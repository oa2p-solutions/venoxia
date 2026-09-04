#!/usr/bin/env python3
"""Linter determinista del acta de proyecto de Venoxia.

El acta (`.venoxia/charter.md`) es lo que existe **antes** de que exista un
cambio que especificar: dice qué cambia en el mundo, para quién, qué se va a
construir y en qué orden, qué queda fuera y qué se está suponiendo. Aquí viven
las dieciséis reglas que la juzgan. Todas son deterministas: ninguna consulta a
un modelo, ninguna toca la red y sólo `C12` mira el calendario, para saber si
una apuesta con fecha de revisión ya venció. Dos ejecuciones sobre la misma acta
producen el mismo veredicto y el mismo JSON, byte a byte.

Uso:

    python3 scripts/charter_lint.py [PATH]
        --root DIR      raíz del proyecto (por defecto, el directorio actual)
        --strict        los avisos cuentan como fallo
        --json          salida JSON con el esquema estable
        --no-color      sin colores ANSI

Sin `PATH` se juzga `<root>/.venoxia/charter.md`. Códigos de salida: `0` el acta
cumple · `1` no cumple · `2` error de uso. Dos ausencias no son errores y las
dos salen con `0`: un proyecto sin `.venoxia/` no ha adoptado Venoxia, y un
proyecto con `.venoxia/` y sin acta la puede escribir cuando quiera —se usa el
núcleo verificable sin acta, y el plugin no está para estorbar—.

**El corazón de este fichero son `C07` y `C10`**, igual que `V06` lo es del
validador. Un acta sin criterio de terminación es una lista de deseos: nadie
puede afirmar que una capability está hecha, así que ninguna lo estará nunca del
todo. Y un acta sin no-alcance es un proyecto que no ha decidido nada: decir que
sí a todo es la forma más cara de no elegir. Sus mensajes y sus pistas son los
más trabajados del fichero a propósito.

El informe no se reimplementa aquí: los hallazgos se pintan con
`venoxia.report`, que ya sabe agruparlos por severidad y poner el remedio debajo
del problema, y el JSON es el mismo esquema estable versión 1 que emite
`validate.py`, con lo propio del acta colgando de la clave `charter`. Lo único
que este módulo escribe por su cuenta son las dos líneas de cierre: el resumen
de `report` habla de requisitos, capabilities y deltas, y un acta no tiene
ninguna de las tres cosas. Un informe que cuenta lo que no hay es un informe que
miente.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from venoxia import parser, report  # noqa: E402
from venoxia.model import (  # noqa: E402
    FILLER_REVISIT_RE,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    Finding,
    ValidationResult,
)

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

VENOXIA_DIR = ".venoxia"
CAPABILITIES_DIR = "capabilities"
SPEC_FILENAME = "spec.md"
CHARTER_FILENAME = "charter.md"

# Las cinco secciones obligatorias, en el orden en que se escriben. Los
# encabezados son estructurales y por eso van en inglés, como el resto del
# plugin; la prosa de debajo, en español.
SECTION_PURPOSE = "Purpose"
SECTION_USERS = "Users"
SECTION_CAPABILITIES = "Capabilities"
SECTION_OUT_OF_SCOPE = "Out of scope"
SECTION_BETS = "Bets"

REQUIRED_SECTIONS = (
    SECTION_PURPOSE,
    SECTION_USERS,
    SECTION_CAPABILITIES,
    SECTION_OUT_OF_SCOPE,
    SECTION_BETS,
)

#: Encabezado normalizado (minúsculas, sin acentos) → sección canónica. La caja
#: no decide nada: «## out of scope» y «## Out of Scope» son la misma sección.
SECTION_BY_HEADING = {_name.lower(): _name for _name in REQUIRED_SECTIONS}

#: Traducciones que alguien va a escribir tarde o temprano. **No** se aceptan
#: como sección —el encabezado estructural va en inglés—, pero se reconocen para
#: que la pista de `C01` diga «tienes esto y hace falta aquello» en vez de
#: mandar escribir una sección que ya está escrita en el otro idioma.
SPANISH_HEADINGS = {
    "proposito": SECTION_PURPOSE,
    "propósito": SECTION_PURPOSE,
    "usuarios": SECTION_USERS,
    "capacidades": SECTION_CAPABILITIES,
    "fuera de alcance": SECTION_OUT_OF_SCOPE,
    "fuera del alcance": SECTION_OUT_OF_SCOPE,
    "no alcance": SECTION_OUT_OF_SCOPE,
    "apuestas": SECTION_BETS,
}

#: Por qué existe cada sección. Va en el mensaje de `C01`: decir «falta la
#: sección X» sin decir qué se pierde con ella no ayuda a escribirla.
SECTION_PURPOSE_OF = {
    SECTION_PURPOSE: "nadie sabe qué cambia en el mundo cuando el proyecto exista",
    SECTION_USERS: "no se sabe a quién le cambia el día lo que se va a construir",
    SECTION_CAPABILITIES: "no hay nada priorizado que construir ni por dónde empezar",
    SECTION_OUT_OF_SCOPE: "el alcance no tiene frontera y acaba comiéndoselo todo",
    SECTION_BETS: "no hay dónde anotar lo que se está suponiendo sin haberlo comprobado",
}

#: Qué escribir debajo de cada encabezado. Va en la pista de `C01`.
SECTION_SHAPE = {
    SECTION_PURPOSE: (
        "de una a tres frases que digan qué cambia para alguien, no qué se programa"
    ),
    SECTION_USERS: (
        "un «### <slug> · <Nombre del rol>» por usuario, cada uno con «- **hoy:** …» "
        "y «- **con esto:** …»"
    ),
    SECTION_CAPABILITIES: (
        "la tabla de cinco columnas «# | Capability | Qué podrá hacer | Done when | Risk»"
    ),
    SECTION_OUT_OF_SCOPE: (
        "una viñeta «- **<Qué>.** <por qué no>» por cada cosa que la v1 no va a hacer"
    ),
    SECTION_BETS: (
        "un «### B-001 · <título>» por apuesta, con su prosa y las claves "
        "«confidence», «why», «revisit» y «fatal»"
    ),
}

#: Las cinco columnas exactas de la tabla de capabilities, ya normalizadas.
TABLE_COLUMNS = ("#", "capability", "que podra hacer", "done when", "risk")

#: Cómo se escriben de verdad, para los mensajes y las pistas.
TABLE_HEADER_TEXT = "# | Capability | Qué podrá hacer | Done when | Risk"

#: Una fila de ejemplo, la del acta canónica. Se cita en varias pistas.
TABLE_ROW_EXAMPLE = (
    "| 1 | `booking` | reservar una mesa para una fecha y hora | un cliente reserva y "
    "recibe la confirmación con su hora | high |"
)

#: Niveles admitidos en «Risk» y en el «confidence:» de una apuesta, de más a
#: menos. Se comparan literales y en minúsculas, igual que hace `V09` con la
#: confianza de un requisito: si la caja decidiera, la misma acta se leería
#: distinta según quién la teclease.
RISK_LEVELS = ("high", "medium", "low")
CONFIDENCE_LEVELS = ("high", "medium", "low")

#: Valores admitidos en «fatal:».
FATAL_VALUES = ("yes", "no")

#: Claves del bloque de metadatos de una apuesta, en inglés y fijas.
BET_META_KEYS = ("confidence", "why", "revisit", "fatal")

#: Verbos de implementación que no pueden **abrir** un «Done when». La lista es
#: cerrada y se compara sólo contra el arranque de la frase: un «Done when» que
#: menciona uno de paso —«el dueño ve las mesas libres sin configurar nada»—
#: describe un hecho observable y pasa. Esta regla es la que más fácil sería
#: convertir en un falso positivo, y por eso no adivina.
IMPLEMENTATION_VERBS = (
    "implementar",
    "crear la tabla",
    "usar",
    "refactorizar",
    "montar",
    "configurar",
    "integrar",
    "desplegar",
)

#: Los mismos verbos en participio. «Desplegado en producción» es la misma tarea
#: que «desplegar en producción» —y es, literalmente, uno de los tres ejemplos
#: de lo que no vale que trae la plantilla—, así que mirar sólo el infinitivo
#: dejaba pasar la forma en que esto se escribe de verdad. Se compara igual:
#: sólo contra el arranque y con frontera de palabra.
#:
#: Fuera de la lista, a propósito, «usado» y «creado»: los dos abren frases
#: observables legítimas —«usado por los seis comerciales la primera semana»,
#: «creado el pedido, el cliente ve su número»— y meterlos aquí sería el falso
#: positivo que acaba con la regla apagada.
IMPLEMENTATION_PARTICIPLE_STEMS = (
    "implementad",
    "montad",
    "configurad",
    "integrad",
    "desplegad",
    "refactorizad",
)

#: El participio, con sus cuatro terminaciones: «desplegado», «desplegada»,
#: «desplegados», «desplegadas». La frontera de palabra es lo que impide que
#: «integrado» denuncie a «integradora».
IMPLEMENTATION_PARTICIPLE_RE = re.compile(
    r"^(?P<verb>(?:" + "|".join(IMPLEMENTATION_PARTICIPLE_STEMS) + r")[oa]s?)\b"
)

#: Fórmulas que suenan a criterio de terminación y no lo son. No arrancan por
#: ningún verbo de implementación —por eso se les escapaban a la lista de
#: arriba— y aun así se pueden declarar cumplidas sin mirar nada: no dicen quién
#: lo ve ni qué ve. Son las que escribe quien no ha hecho la tanda C.
#:
#: **Cubren la celda entera, y en eso está su seguridad**: en cuanto la frase
#: añade un sujeto y un hecho —«el dueño ve que la lista funciona
#: correctamente»— deja de casar y la regla se calla. Un falso positivo aquí
#: exigiría que alguien hubiera escrito, como criterio completo, «que funcione
#: bien», que es exactamente lo que se persigue.
_EMPTY_DONE_WHEN_ALTERNATIVES = (
    # «que sea rápido», «que quede ágil»: un adjetivo sin sujeto y sin hecho.
    r"(?:que\s+)?(?:sea|es|quede|queda|resulte)\s+"
    r"(?:rapid[oa]|agil|fluid[oa]|intuitiv[oa]|facil|comod[oa]|usable|estable|"
    r"fiable|segur[oa]|robust[oa]|escalable|bonit[oa])",
    # «que funcione bien», «todo funciona correctamente», «va bien».
    r"(?:que\s+)?(?:todo\s+)?(?:funcione|funciona|funcionen|funcionan|va|vaya|rula)"
    r"(?:\s+(?:bien|correctamente|ok|sin\s+problemas|sin\s+errores|sin\s+fallos|"
    r"como\s+se\s+espera|como\s+toca))?",
    # «el sistema funciona correctamente»: el sujeto es la máquina, no nadie.
    r"(?:el\s+sistema|la\s+aplicacion|la\s+app|la\s+herramienta|la\s+plataforma|"
    r"el\s+servicio|la\s+web|la\s+pantalla|el\s+flujo|el\s+proceso)"
    r"\s+(?:funciona|funcione|va|vaya|responde|anda)"
    r"(?:\s+(?:bien|correctamente|ok|sin\s+problemas|sin\s+errores|sin\s+fallos|"
    r"como\s+se\s+espera))?",
    # «la funcionalidad está completa», «está terminado», «ya está listo».
    r"(?:(?:la\s+funcionalidad|la\s+feature|el\s+desarrollo|la\s+capability|"
    r"el\s+modulo|la\s+parte|el\s+trabajo|todo)\s+)?"
    r"(?:ya\s+)?(?:esta|estan|queda|quedan)\s+"
    r"(?:complet[ao]s?|terminad[ao]s?|list[ao]s?|hech[ao]s?|acabad[ao]s?|"
    r"implementad[ao]s?|operativ[ao]s?|funcionando|en\s+marcha|ok)",
    # «sin errores», que dice lo que no pasa y no dice lo que pasa.
    r"sin\s+(?:errores|bugs|fallos|incidencias|problemas)",
    # «cuando esté listo», que es la fecha de terminación de quien tiene prisa.
    r"(?:cuando|si)\s+(?:este|quede)\s+(?:list[ao]|terminad[ao]|hech[ao]|complet[ao])",
)
EMPTY_DONE_WHEN_RE = re.compile(
    "^(?:" + "|".join(_EMPTY_DONE_WHEN_ALTERNATIVES) + ")$"
)

#: Entradas de «## Out of scope» que ocupan una viñeta y no excluyen nada.
#: «Nada por ahora» es, con todas las letras, el proyecto que C10 existe para
#: señalar —uno que no ha dicho que no a nada—, y escrito en una viñeta apagaba
#: la regla entera: bastaba una línea para que el acta pasara diciendo que no
#: había frontera. Se comparan contra la entrada **completa**, ya sin negrita ni
#: puntuación, por el mismo motivo que las fórmulas de arriba: una exclusión de
#: verdad nombra algo, y en cuanto nombra algo deja de casar.
_FILLER_EXCLUSION_ALTERNATIVES = (
    r"(?:de\s+momento\s+|por\s+ahora\s+|todavia\s+|aun\s+)?(?:nada|ningun[ao]?)"
    r"(?:\s+(?:de\s+momento|por\s+ahora|todavia|aun|excluido|fuera|"
    r"que\s+decir|que\s+excluir|en\s+concreto|especial))?",
    r"n\s*/\s*a|na|tbd|tba",
    r"todo\s+(?:entra|cabe|vale)|ya\s+veremos|se\s+vera|esta\s+por\s+ver",
    r"(?:pendiente|por\s+definir|por\s+determinar|por\s+decidir|sin\s+definir|"
    r"sin\s+determinar|sin\s+decidir)(?:\s+de\s+(?:definir|determinar|decidir))?",
    r"[-–—?¿.…]+",
)
FILLER_EXCLUSION_RE = re.compile(
    "^(?:" + "|".join(_FILLER_EXCLUSION_ALTERNATIVES) + ")$"
)

#: Forma canónica del identificador de una apuesta: «B-001».
BET_ID_RE = re.compile(r"^B-\d{3}$")

#: Forma canónica de un slug de capability: kebab-case en minúsculas.
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

#: Delimitadores de un comentario de markdown. La plantilla del acta se reparte
#: llena de ellos, y lo que explican no es lo que el acta dice.
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"

#: Encabezado de sección del acta: «## Purpose». El «(?!#)» lo distingue de los
#: «### …» de usuarios y apuestas.
SECTION_HEADER_RE = re.compile(r"^##(?!#)\s+(?P<title>\S.*?)\s*$")

#: Encabezado de usuario o de apuesta: «### owner · Dueño del restaurante».
ENTRY_HEADER_RE = re.compile(r"^###(?!#)\s+(?P<body>\S.*?)\s*$")

#: Cualquier encabezado de nivel 1 o 2: cierra la sección en curso.
SECTION_BREAK_RE = re.compile(r"^#{1,2}(?!#)\s*\S")

#: Reparto de «### <clave> · <resto>» en sus dos mitades. Los separadores son
#: los mismos que admite el encabezado de un requisito: «·», la raya «—», el
#: semicuadratín «–» y el guion «-» con espacio a los dos lados, que si no
#: partiría por la mitad un «B-001» o un slug con guiones.
ENTRY_SPLIT_RE = re.compile(r"^(?P<key>\S+?)(?:\s*[·—–]\s*|\s+-\s+)(?P<rest>.+)$")

#: El separador suelto, para proponer el arreglo de un encabezado mal partido.
SEPARATOR_RE = re.compile(r"\s*[·—–]\s*|\s+-\s+")

#: Viñeta con clave en negrita: «- **hoy:** apunta las reservas en un cuaderno».
#: Los dos puntos pueden ir dentro o fuera de la negrita; ni una cosa ni la otra
#: cambia lo que la viñeta dice.
BOLD_BULLET_RE = re.compile(
    r"^\s*[-*]\s+\*\*(?P<key>[^*]+?)\s*:?\s*\*\*\s*:?\s*(?P<text>.*?)\s*$"
)

#: Cualquier viñeta, con negrita o sin ella. Sirve para contar entradas de
#: «## Out of scope», donde la negrita es la forma recomendada y no el requisito.
ANY_BULLET_RE = re.compile(r"^\s*[-*]\s+(?P<text>\S.*?)\s*$")

#: Celda de la fila separadora de una tabla: «---», «:--», «--:», «:-:».
TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{1,}:?$")

#: Separador de celdas de una tabla markdown: la barra que **no** va escapada.
#: Un «\|» dentro de una celda es una barra literal y es markdown válido; partir
#: por ella corría todas las columnas un puesto y hacía que el linter acusara a
#: la columna equivocada —un «Risk» que en realidad era media frase—, que es la
#: peor forma de rechazar un acta legítima: por un motivo que no es el suyo.
TABLE_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")

#: Una fila de tabla cuya primera celda es «#», escrita sin las barras
#: exteriores. Es exactamente el encabezado del acta —«# | Capability | …»— y
#: casa también con «^#{1,2}(?!#)\s*\S», así que sin esta excepción se leía
#: como un título de nivel uno, cerraba «## Capabilities» y el linter contestaba
#: que la sección no traía ninguna tabla.
TABLE_HASH_HEADER_RE = re.compile(r"^#\s*\|")

#: Fecha ISO. Ya no se pide en ninguna clave: se usa para **rechazarla** en
#: «revisit:», donde lo que hace falta es el hecho que resuelve la apuesta y no
#: el día en que caduca. Reconocerla es lo que permite dar el remedio bueno en
#: vez de un «valor no válido» que no enseña nada.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")

#: Frontera de frase del propósito. Un punto entre dígitos no la marca: «15.000»
#: es un número, no dos frases. Y tampoco la marca un punto al que no le sigue
#: el arranque de otra frase: «las tiendas de la S.L. dejen de cuadrar a mano»
#: es una frase y contaba como tres, de modo que C02 rechazaba por larga un
#: propósito de dos líneas con una abreviatura dentro. Se exige lo que separa de
#: verdad dos frases en castellano —el final del texto, o un espacio y una
#: mayúscula o un signo de apertura—, y en la duda se cuenta de menos: C02 pone
#: un máximo, así que equivocarse a la baja no rechaza a nadie.
SENTENCE_BOUNDARY_RE = re.compile(
    "(?<!\\d)[.!?…]+(?!\\d)(?=\\s+[«¿¡\"'(\\[A-ZÁÉÍÓÚÜÑ]|\\s*$)"
)

#: Cuántos días se sugieren por delante cuando hay que proponer un «revisit:».
#: El ejemplo que las pistas de C12 usan para enseñar la forma de un «revisit:».
#: Es un suceso del proyecto y no un plazo a propósito: lo que se pide es el
#: hecho que resuelve la apuesta, y un ejemplo con días enseñaría lo contrario.
REVISIT_EXAMPLE = "cuando hayamos cerrado las diez primeras compras"


class UsageError(Exception):
    """Error de uso de la línea de comandos: se responde con el código 2."""


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------


def _strip_accents(text: str) -> str:
    """Quita los acentos de un texto sin tocar nada más."""
    try:
        decomposed = unicodedata.normalize("NFD", text)
    except Exception:  # defensa: normalizar no puede tumbar el linter
        return text
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _normalize(text: str) -> str:
    """Minúsculas, sin acentos y con los espacios colapsados.

    Es la forma en que se comparan los encabezados y las columnas de la tabla:
    lo estructural no puede depender de una tilde ni de una mayúscula.
    """
    collapsed = parser.WHITESPACE_RE.sub(" ", text or "").strip().lower()
    return _strip_accents(collapsed)


def _collapse(text: str) -> str:
    """Colapsa un texto en una sola línea de espacios simples."""
    return parser.WHITESPACE_RE.sub(" ", text or "").strip()


def _display_path(path: Path, root: Path) -> str:
    """Ruta del acta relativa a la raíz, para los mensajes."""
    try:
        relative = os.path.relpath(os.path.abspath(str(path)), os.path.abspath(str(root)))
    except Exception:
        # Cualquier ruta imposible se enseña tal cual: aquí no se lanza por un
        # mensaje.
        return str(path)
    if relative.startswith(".."):
        # Fuera de la raíz: la ruta entera es más útil que un rosario de «..».
        return str(path)
    return relative


# ---------------------------------------------------------------------------
# El modelo del acta
# ---------------------------------------------------------------------------


@dataclass
class Section:
    """Una sección del acta: su encabezado y las líneas que cuelgan de él.

    Un acta con dos «## Bets» no pierde ninguna apuesta: las líneas de todas las
    apariciones se acumulan aquí, bajo el primer encabezado. Tragarse media
    sección en silencio porque el encabezado esté repetido es peor que leer de
    más, y las reglas juzgan igual de bien un montón que dos.
    """

    name: str
    heading: str
    line: int
    lines: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class User:
    """Un usuario del acta: quién es, cómo vive hoy y qué cambia para él."""

    slug: str
    role: str
    line: int
    header: str
    before: str | None = None
    after: str | None = None

    @property
    def label(self) -> str:
        """Etiqueta corta para los mensajes: el slug si lo hay, si no el encabezado."""
        return self.slug or (self.header.strip() or "usuario sin nombre")


@dataclass
class CapabilityRow:
    """Una fila de la tabla de capabilities, tal cual está escrita."""

    line: int
    priority_text: str = ""
    priority: int | None = None
    slug: str = ""
    what: str = ""
    done_when: str = ""
    risk: str = ""
    cells: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        """Cómo se nombra la capability en un mensaje."""
        if self.slug:
            return f"«{self.slug}»"
        if self.priority_text:
            return f"la capability de prioridad «{self.priority_text}»"
        return "la capability sin nombre"


@dataclass
class Exclusion:
    """Una entrada de «## Out of scope»: qué queda fuera y por qué.

    Se guarda la viñeta entera. Que empiece por la negrita de «- **<Qué>.**» es
    la forma recomendada del contrato y no una condición: C10 no juzga la forma
    de la viñeta, sólo si llega a nombrar algo que se queda fuera. Una que no
    nombra nada —«nada por ahora»— no cuenta, y ésa es toda la lectura que la
    regla hace del texto.
    """

    line: int
    text: str


@dataclass
class Bet:
    """Una apuesta del acta: lo que se está suponiendo sin haberlo comprobado."""

    line: int
    id: str | None
    title: str
    header: str
    prose: str = ""
    meta: dict[str, str] = field(default_factory=dict)
    meta_lines: dict[str, int] = field(default_factory=dict)

    @property
    def label(self) -> str:
        """El identificador si lo hay, y si no el título entre comillas."""
        if self.id:
            return self.id
        title = (self.title or self.header or "").strip()
        return f"«{title}»" if title else "«apuesta sin título»"

    def value(self, key: str) -> str | None:
        """Valor de un metadato ya recortado, o `None` si la clave no está."""
        raw = self.meta.get(key)
        return raw if raw is None else raw.strip()

    def line_of(self, key: str) -> int:
        """Línea del metadato, o la del encabezado si el metadato no está."""
        return self.meta_lines.get(key, self.line)


@dataclass
class Charter:
    """El acta ya leída: sus secciones y todo lo que se ha sabido extraer.

    Nada de esto juzga: aquí sólo se guarda lo que el fichero dice. Que falte
    una sección, que un slug no sea kebab-case o que una apuesta no traiga fecha
    lo deciden las reglas, no el parseo.
    """

    path: str
    sections: dict[str, Section] = field(default_factory=dict)
    foreign_headings: list[tuple[int, str, str]] = field(default_factory=list)
    purpose: str = ""
    users: list[User] = field(default_factory=list)
    capabilities: list[CapabilityRow] = field(default_factory=list)
    table_header: list[str] | None = None
    table_header_line: int | None = None
    table_header_ok: bool = False
    exclusions: list[Exclusion] = field(default_factory=list)
    bets: list[Bet] = field(default_factory=list)
    failure: Finding | None = None

    def has(self, name: str) -> bool:
        """¿Está declarada esa sección?"""
        return name in self.sections

    def line_of(self, name: str, default: int | None = None) -> int | None:
        """Línea del encabezado de una sección, o el respaldo que se pase."""
        section = self.sections.get(name)
        return section.line if section is not None else default


# ---------------------------------------------------------------------------
# El parseo · nunca lanza
# ---------------------------------------------------------------------------


def _code_fence_map(lines: list[str]) -> list[bool]:
    """Marca las líneas que caen dentro de un bloque de código.

    Lo que vive dentro de una valla es un ejemplo, no estructura: ni abre
    sección, ni declara un usuario, ni es una fila de la tabla. La valla misma
    cuenta como código, para que no se lea como nada.
    """
    inside = [False] * len(lines)
    opener: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        match = parser.FENCE_RE.match(line)
        if match is not None:
            marker = match.group("marker") or ""
            info = (match.group("info") or "").strip()
            if opener is None:
                opener = (marker[0], len(marker))
                inside[index] = True
                continue
            char, length = opener
            if marker[0] == char and len(marker) >= length and not info:
                opener = None
                inside[index] = True
                continue
        inside[index] = opener is not None
    return inside


def _without_comments(line: str, inside: bool) -> tuple[str, bool]:
    """Borra de la línea lo que cae dentro de un comentario de markdown.

    Devuelve también si el comentario sigue abierto al final de la línea, porque
    los de la plantilla ocupan párrafos enteros.
    """
    kept: list[str] = []
    index = 0
    while index < len(line):
        if inside:
            end = line.find(COMMENT_CLOSE, index)
            if end < 0:
                break
            inside = False
            index = end + len(COMMENT_CLOSE)
            continue
        start = line.find(COMMENT_OPEN, index)
        if start < 0:
            kept.append(line[index:])
            break
        kept.append(line[index:start])
        inside = True
        index = start + len(COMMENT_OPEN)
    return "".join(kept), inside


def _readable_lines(lines: list[str]) -> list[str]:
    """El acta con lo que no es contenido ya en blanco: código y comentarios.

    Las dos cosas se borran por el mismo motivo. La plantilla del acta se
    reparte con comentarios guía largos y con tablas de muestra dentro de
    vallas, y quien la rellena los va borrando a medida que escribe: leer una
    fila de ejemplo como una capability de verdad —o una viñeta explicativa como
    el «**hoy:**» de un usuario— llenaría el informe de hallazgos contra texto
    que nadie ha escrito. Las líneas no se quitan, se vacían: así el número de
    línea de cada hallazgo sigue siendo el del fichero.
    """
    in_code = _code_fence_map(lines)
    readable: list[str] = []
    inside_comment = False
    for index, line in enumerate(lines):
        if in_code[index]:
            # Un «<!--» dentro de una valla es texto de ejemplo y no abre nada.
            readable.append("")
            continue
        cleaned, inside_comment = _without_comments(line, inside_comment)
        readable.append(cleaned)
    return readable


def _table_cells(line: str) -> list[str] | None:
    """Celdas de una fila de tabla markdown, o `None` si la línea no lo es.

    Se admite la fila con las barras exteriores y sin ellas: las dos son
    markdown válido y ninguna de las dos cambia lo que la tabla dice. Y una
    barra escapada —«\\|»— es parte del texto de la celda, no un separador: la
    columna «Done when» de un exportador de CSV la nombra tarde o temprano.
    """
    stripped = line.strip()
    if "|" not in stripped:
        return None
    parts = TABLE_CELL_SPLIT_RE.split(stripped)
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [part.replace("\\|", "|").strip() for part in parts]


def _is_separator_row(cells: list[str]) -> bool:
    """¿Es la fila de guiones que separa el encabezado del cuerpo de la tabla?"""
    return bool(cells) and all(TABLE_SEPARATOR_CELL_RE.match(cell) for cell in cells)


def parse_charter(path: str | Path, root: str | Path = ".") -> Charter:
    """Lee el acta y devuelve su modelo. **Nunca lanza.**

    Un acta ilegible, vacía o deforme produce un modelo a medias y, cuando el
    fichero ni siquiera se deja leer, el `P01` del parser en `failure`. Una traza
    de Python delante de quien está escribiendo su primer acta no explica nada y
    hace desinstalar el plugin.
    """
    display = ""
    charter = Charter(path="")
    try:
        display = _display_path(Path(path), Path(root))
        charter = Charter(path=display)
        text, failure = parser.read_text(path)
        if failure is not None:
            failure.file = display
            charter.failure = failure
            return charter
        _fill_charter(charter, text or "")
        return charter
    except Exception as error:  # defensa: el parseo del acta no propaga
        charter.failure = Finding(
            rule="P01",
            severity=SEVERITY_ERROR,
            message=(
                f"No se ha podido leer el acta «{display or path}»: "
                f"{type(error).__name__}: {error}."
            ),
            file=display,
            hint=(
                "Es un fallo de Venoxia, no del acta: repórtalo indicando el fichero "
                "que lo provoca."
            ),
        )
        return charter


def _fill_charter(charter: Charter, text: str) -> None:
    """Rellena el modelo del acta a partir de su texto."""
    _collect_sections(charter, _readable_lines(text.splitlines()))

    purpose_section = charter.sections.get(SECTION_PURPOSE)
    if purpose_section is not None:
        charter.purpose = _collapse(
            " ".join(content for _number, content in purpose_section.lines)
        )

    users_section = charter.sections.get(SECTION_USERS)
    if users_section is not None:
        charter.users = _parse_users(users_section)

    table_section = charter.sections.get(SECTION_CAPABILITIES)
    if table_section is not None:
        _parse_capabilities(charter, table_section)

    scope_section = charter.sections.get(SECTION_OUT_OF_SCOPE)
    if scope_section is not None:
        charter.exclusions = _parse_exclusions(scope_section)

    bets_section = charter.sections.get(SECTION_BETS)
    if bets_section is not None:
        charter.bets = _parse_bets(bets_section)


def _collect_sections(charter: Charter, lines: list[str]) -> None:
    """Reparte el documento en secciones de nivel dos.

    Las líneas llegan ya limpias de código y de comentarios (`_readable_lines`),
    así que aquí todo lo que se lee es contenido del acta.

    Un encabezado que no es ninguna de las cinco no se pierde: se guarda aparte
    para que `C01` pueda decir «tienes “## Propósito” y hace falta “## Purpose”»
    en vez de mandar escribir lo que ya está escrito en otro idioma.
    """
    current: Section | None = None
    for index, raw in enumerate(lines):
        number = index + 1
        header = SECTION_HEADER_RE.match(raw)
        if header is not None:
            title = header.group("title").strip().rstrip(":").strip()
            name = SECTION_BY_HEADING.get(_normalize(title))
            if name is None:
                current = None
                foreign = SPANISH_HEADINGS.get(_normalize(title))
                if foreign is not None:
                    charter.foreign_headings.append((number, title, foreign))
                continue
            existing = charter.sections.get(name)
            if existing is None:
                current = Section(name=name, heading=title, line=number)
                charter.sections[name] = current
            else:
                current = existing
            continue

        if SECTION_BREAK_RE.match(raw):
            if current is not None and TABLE_HASH_HEADER_RE.match(raw):
                # No es un título: es «# | Capability | …», el encabezado de la
                # tabla escrito sin las barras exteriores. Su primera celda es
                # una almohadilla y por eso se disfraza de nivel uno.
                current.lines.append((number, raw))
                continue
            # Un «# Título» de nivel uno cierra la sección en curso.
            current = None
            continue

        if current is not None:
            current.lines.append((number, raw))


def _split_entry(body: str) -> tuple[str, str]:
    """Parte «### <clave> · <resto>» en sus dos mitades.

    Sin separador, el encabezado entero es la clave y el resto queda vacío: lo
    dirá la regla que corresponda, no el parseo.
    """
    match = ENTRY_SPLIT_RE.match(body.strip())
    if match is None:
        return body.strip(), ""
    return match.group("key").strip(), match.group("rest").strip()


def _parse_users(section: Section) -> list[User]:
    """Lee los «### <slug> · <Nombre del rol>» y sus dos viñetas."""
    users: list[User] = []
    current: User | None = None
    for number, raw in section.lines:
        header = ENTRY_HEADER_RE.match(raw)
        if header is not None:
            slug, role = _split_entry(header.group("body"))
            current = User(slug=slug, role=role, line=number, header=header.group("body"))
            users.append(current)
            continue
        if current is None:
            continue
        bullet = BOLD_BULLET_RE.match(raw)
        if bullet is None:
            continue
        key = _normalize(bullet.group("key"))
        value = bullet.group("text").strip()
        if key == "hoy":
            current.before = value
        elif key in ("con esto", "con esto:"):
            current.after = value
    return users


def _parse_capabilities(charter: Charter, section: Section) -> None:
    """Lee la tabla de capabilities: primero su encabezado, luego sus filas.

    El encabezado manda. Si no está o no declara las cinco columnas exactas, no
    se lee ninguna fila: adivinar qué columna es cuál produciría capabilities
    inventadas, con su prioridad y su riesgo sacados de donde no estaban. `C04`
    lo cuenta como lo que es —no hay ninguna capability legible— y explica por
    qué.
    """
    rows: list[tuple[int, list[str]]] = []
    for number, raw in section.lines:
        cells = _table_cells(raw)
        if cells is None or not any(cells):
            continue
        rows.append((number, cells))

    if not rows:
        return

    header_line, header_cells = rows[0]
    charter.table_header = header_cells
    charter.table_header_line = header_line
    charter.table_header_ok = tuple(_normalize(cell) for cell in header_cells) == TABLE_COLUMNS
    if not charter.table_header_ok:
        return

    for number, cells in rows[1:]:
        if _is_separator_row(cells):
            continue
        padded = list(cells) + [""] * (len(TABLE_COLUMNS) - len(cells))
        priority_text = padded[0].strip()
        row = CapabilityRow(
            line=number,
            priority_text=priority_text,
            priority=_as_priority(priority_text),
            slug=padded[1].strip().strip("`").strip(),
            what=padded[2].strip(),
            done_when=padded[3].strip(),
            risk=padded[4].strip(),
            cells=list(cells),
        )
        charter.capabilities.append(row)


def _as_priority(text: str) -> int | None:
    """Convierte la primera columna en un entero, o `None` si no lo es."""
    candidate = (text or "").strip()
    if not candidate:
        return None
    try:
        return int(candidate)
    except ValueError:
        return None


def _parse_exclusions(section: Section) -> list[Exclusion]:
    """Lee las viñetas de «## Out of scope»."""
    exclusions: list[Exclusion] = []
    for number, raw in section.lines:
        bullet = ANY_BULLET_RE.match(raw)
        if bullet is None:
            continue
        exclusions.append(Exclusion(line=number, text=bullet.group("text").strip()))
    return exclusions


def _parse_bets(section: Section) -> list[Bet]:
    """Lee los «### B-NNN · <título>» con su prosa y su bloque de metadatos.

    El bloque de metadatos es el mismo de un requisito: claves fijas en inglés
    al final de la apuesta, con la sangría que se quiera. Se toma sólo el bloque
    **final** y contiguo, igual que hace el parser con los requisitos: una línea
    de prosa que por casualidad tenga forma de «clave: valor» sigue siendo prosa
    mientras haya prosa debajo.
    """
    bets: list[Bet] = []
    blocks: list[tuple[Bet, list[tuple[int, str]]]] = []
    current: list[tuple[int, str]] | None = None

    for number, raw in section.lines:
        header = ENTRY_HEADER_RE.match(raw)
        if header is not None:
            body = header.group("body")
            key, title = _split_entry(body)
            bet = Bet(
                line=number,
                id=key if BET_ID_RE.match(key) else (key or None),
                title=title,
                header=body,
            )
            bets.append(bet)
            current = []
            blocks.append((bet, current))
            continue
        if current is not None:
            current.append((number, raw))

    for bet, body in blocks:
        _fill_bet(bet, body)
    return bets


def _fill_bet(bet: Bet, body: list[tuple[int, str]]) -> None:
    """Reparte el cuerpo de una apuesta entre prosa y metadatos."""
    start = len(body)
    index = len(body) - 1
    while index >= 0:
        _number, raw = body[index]
        if not raw.strip():
            index -= 1
            continue
        if parser.META_LINE_RE.match(raw) is not None:
            start = index
            index -= 1
            continue
        break

    for number, raw in body[start:]:
        match = parser.META_LINE_RE.match(raw)
        if match is None:
            continue
        key = match.group("key").strip().lower()
        # La última repetición gana, igual que en el bloque de un requisito.
        bet.meta[key] = match.group("value").strip()
        bet.meta_lines[key] = number

    bet.prose = _collapse(" ".join(raw for _number, raw in body[:start]))


# ---------------------------------------------------------------------------
# Contexto y registro de reglas
# ---------------------------------------------------------------------------


@dataclass
class Context:
    """Todo lo que una regla necesita saber, ya leído y ya contado."""

    root: Path
    path: Path
    display: str
    charter: Charter
    today: date = field(default_factory=date.today)
    live_capabilities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    """Una regla del acta: su código, su severidad y la función que la aplica."""

    code: str
    severity: str
    summary: str
    check: Callable[[Context], list[Finding]]


def _finding(
    ctx: Context,
    code: str,
    severity: str,
    message: str,
    hint: str,
    line: int | None = None,
    subject: str | None = None,
) -> Finding:
    """Construye un hallazgo ya situado en el acta.

    `subject` viaja en el campo `requirement_id` del modelo, que es la columna
    con la que el informe encabeza cada hallazgo. En un acta ese sujeto es el
    slug de una capability o el identificador de una apuesta.
    """
    return Finding(
        rule=code,
        severity=severity,
        message=message,
        file=ctx.display,
        line=line,
        requirement_id=subject,
        hint=hint,
    )


# ---------------------------------------------------------------------------
# Las dieciséis reglas
# ---------------------------------------------------------------------------


def rule_c01(ctx: Context) -> list[Finding]:
    """C01 · Están las cinco secciones obligatorias."""
    findings: list[Finding] = []
    translated = {name: (number, title) for number, title, name in ctx.charter.foreign_headings}

    for name in REQUIRED_SECTIONS:
        if ctx.charter.has(name):
            continue
        hint = f"Añade «## {name}» con {SECTION_SHAPE[name]}."
        foreign = translated.get(name)
        if foreign is not None:
            number, title = foreign
            hint = (
                f"El acta ya trae «## {title}» en la línea {number}: renómbralo a "
                f"«## {name}» y deja la prosa como está. Los encabezados del acta van "
                "en inglés porque los lee el linter; lo que se lee en español es lo "
                "que hay debajo."
            )
        findings.append(
            _finding(
                ctx,
                "C01",
                SEVERITY_ERROR,
                (
                    f"El acta no declara la sección «## {name}»: sin ella "
                    f"{SECTION_PURPOSE_OF[name]}."
                ),
                hint,
                line=None,
            )
        )
    return findings


def rule_c02(ctx: Context) -> list[Finding]:
    """C02 · El propósito tiene entre una y tres frases."""
    if not ctx.charter.has(SECTION_PURPOSE):
        # Que la sección no esté lo dice C01. Repetirlo aquí sería cobrar dos
        # veces el mismo error.
        return []

    line = ctx.charter.line_of(SECTION_PURPOSE)
    sentences = [
        piece.strip()
        for piece in SENTENCE_BOUNDARY_RE.split(ctx.charter.purpose)
        if piece.strip()
    ]
    example = (
        "«Que un restaurante pequeño deje de perder mesas por reservas apuntadas en "
        "un cuaderno que sólo entiende quien lo escribió»"
    )

    if not sentences:
        return [
            _finding(
                ctx,
                "C02",
                SEVERITY_ERROR,
                (
                    "La sección «## Purpose» está vacía: el acta no dice qué cambia en "
                    "el mundo cuando el proyecto exista."
                ),
                (
                    f"Escribe de una a tres frases sobre qué cambia para alguien, no "
                    f"sobre qué se programa. Por ejemplo {example}."
                ),
                line=line,
            )
        ]

    if len(sentences) > 3:
        return [
            _finding(
                ctx,
                "C02",
                SEVERITY_ERROR,
                (
                    f"El propósito del acta tiene {len(sentences)} frases y el máximo "
                    "son tres: lo que no cabe en tres frases todavía no es un "
                    "propósito, es un plan."
                ),
                (
                    "Quédate con la frase que dice qué cambia en el mundo y baja el "
                    "resto a «## Capabilities» o a «## Out of scope», que es donde el "
                    "detalle se puede verificar."
                ),
                line=line,
            )
        ]

    return []


def rule_c03(ctx: Context) -> list[Finding]:
    """C03 · Hay al menos un usuario, y cada uno dice cómo vive hoy y qué cambia."""
    if not ctx.charter.has(SECTION_USERS):
        return []

    shape = (
        "«### owner · Dueño del restaurante», y debajo «- **hoy:** apunta las reservas "
        "en un cuaderno» y «- **con esto:** ve la ocupación de la noche desde el móvil»"
    )

    if not ctx.charter.users:
        return [
            _finding(
                ctx,
                "C03",
                SEVERITY_ERROR,
                (
                    "El acta no declara ningún usuario: un proyecto al que no le cambia "
                    "el día a nadie no tiene a quién servir."
                ),
                f"Escribe al menos un usuario con la forma {shape}.",
                line=ctx.charter.line_of(SECTION_USERS),
            )
        ]

    findings: list[Finding] = []
    for user in ctx.charter.users:
        missing = [
            label
            for label, value in (("**hoy:**", user.before), ("**con esto:**", user.after))
            if value is None
        ]
        empty = [
            label
            for label, value in (("**hoy:**", user.before), ("**con esto:**", user.after))
            if value is not None and not value
        ]
        if not missing and not empty:
            continue

        if missing:
            listed = " ni ".join(f"«{label}»" for label in missing)
            if len(missing) == 2:
                message = (
                    f"El usuario «{user.label}» no declara {listed}: el acta lo nombra "
                    "y no dice nada de él."
                )
            elif "**con esto:**" in missing:
                message = (
                    f"El usuario «{user.label}» no declara {listed}: el acta cuenta "
                    "cómo vive hoy y no dice qué cambia para él."
                )
            else:
                message = (
                    f"El usuario «{user.label}» no declara {listed}: sin el hoy, lo que "
                    "el proyecto promete no se compara con nada."
                )
        else:
            listed = " y ".join(f"«{label}»" for label in empty)
            message = (
                f"El {listed} de «{user.label}» está vacío: la viñeta está escrita y no "
                "dice nada."
            )

        findings.append(
            _finding(
                ctx,
                "C03",
                SEVERITY_ERROR,
                message,
                (
                    "Completa las dos viñetas del usuario: «- **hoy:** …» cuenta cómo "
                    "se las apaña ahora y «- **con esto:** …» qué hará cuando el "
                    "proyecto exista. La diferencia entre las dos es el valor que "
                    "estás prometiendo."
                ),
                line=user.line,
                subject=user.slug or None,
            )
        )
    return findings


def rule_c04(ctx: Context) -> list[Finding]:
    """C04 · Hay al menos una capability en la tabla."""
    if not ctx.charter.has(SECTION_CAPABILITIES):
        return []
    if ctx.charter.capabilities:
        return []

    charter = ctx.charter
    hint = (
        f"Escribe la tabla con las cinco columnas exactas «{TABLE_HEADER_TEXT}» y una "
        f"fila por capability, por ejemplo:\n{TABLE_ROW_EXAMPLE}"
    )

    if charter.table_header is None:
        message = (
            "La sección «## Capabilities» no trae ninguna tabla: sin capabilities "
            "priorizadas el acta no dice qué se construye ni por dónde se empieza."
        )
        line = charter.line_of(SECTION_CAPABILITIES)
    elif not charter.table_header_ok:
        written = " | ".join(charter.table_header) or "(ninguna)"
        message = (
            f"La tabla de «## Capabilities» declara las columnas «{written}» y las del "
            f"acta son exactamente cinco: «{TABLE_HEADER_TEXT}». Con otro encabezado no "
            "se puede leer ninguna capability sin inventarse qué columna es cuál."
        )
        line = charter.table_header_line
    else:
        message = (
            "La tabla de «## Capabilities» sólo trae el encabezado: ninguna capability, "
            "ninguna primera línea de código que escribir."
        )
        line = charter.table_header_line

    return [_finding(ctx, "C04", SEVERITY_ERROR, message, hint, line=line)]


def rule_c05(ctx: Context) -> list[Finding]:
    """C05 · Cada slug de capability es kebab-case válido y único."""
    findings: list[Finding] = []
    seen: dict[str, CapabilityRow] = {}

    for row in ctx.charter.capabilities:
        if not row.slug:
            findings.append(
                _finding(
                    ctx,
                    "C05",
                    SEVERITY_ERROR,
                    (
                        f"La fila de prioridad «{row.priority_text or '?'}» no declara "
                        "ningún slug de capability: sin nombre no hay directorio donde "
                        "escribir su especificación."
                    ),
                    (
                        "Escribe el slug entre acentos graves en la segunda columna, en "
                        "kebab-case y en inglés: «`booking`». Es el mismo nombre que "
                        "usará «.venoxia/capabilities/booking/spec.md»."
                    ),
                    line=row.line,
                )
            )
            continue

        if not SLUG_RE.match(row.slug):
            suggestion = _kebab(row.slug)
            hint = (
                "Escríbelo en kebab-case: minúsculas, dígitos y guiones simples, sin "
                "espacios ni acentos."
            )
            if suggestion and suggestion != row.slug:
                hint = f"{hint} Aquí sería «`{suggestion}`»."
            findings.append(
                _finding(
                    ctx,
                    "C05",
                    SEVERITY_ERROR,
                    (
                        f"El slug «{row.slug}» no es kebab-case: es el nombre del "
                        "directorio «.venoxia/capabilities/<slug>/», y ahí no cabe "
                        "cualquier cosa."
                    ),
                    hint,
                    line=row.line,
                    subject=row.slug,
                )
            )
            continue

        previous = seen.get(row.slug)
        if previous is not None:
            findings.append(
                _finding(
                    ctx,
                    "C05",
                    SEVERITY_ERROR,
                    (
                        f"El slug «{row.slug}» ya está declarado en la línea "
                        f"{previous.line}: dos capabilities no pueden compartir nombre, "
                        "porque compartirían también su «spec.md»."
                    ),
                    (
                        "Renombra una de las dos con el nombre que de verdad la "
                        "distingue, o fúndelas en una sola fila si describen el mismo "
                        "comportamiento."
                    ),
                    line=row.line,
                    subject=row.slug,
                )
            )
            continue

        seen[row.slug] = row

    # El slug del usuario se juzga con la misma vara: también nombra algo que se
    # referencia desde fuera del acta, y un «Coordinadora De Turnos» pasando por
    # slug convierte la sección en prosa sin identificadores.
    for user in ctx.charter.users:
        if not user.slug or SLUG_RE.match(user.slug):
            continue
        head = user.header or user.slug
        if user.role:
            # Hay separador: lo que falla es sólo la forma del slug.
            propuesta = _kebab(user.slug) or "owner"
            legible = user.role
            message = (
                f"El slug del usuario «{user.slug}» no es kebab-case: el papel se "
                "nombra con un identificador estable, no con su título escrito a mano."
            )
        else:
            # Sin separador reconocido, el encabezado entero se leyó como slug —el
            # caso típico es un slug con espacios. Si aun así trae un «·», sus dos
            # mitades son la mejor propuesta: la izquierda da el slug, la derecha el
            # nombre legible del papel.
            partes = SEPARATOR_RE.split(head, maxsplit=1)
            propuesta = _kebab(partes[0]) or "owner"
            legible = (partes[1].strip() if len(partes) > 1 else "") or partes[0].strip()
            message = (
                f"El encabezado de usuario «{head}» no separa el slug del nombre del "
                "papel: el slug va antes del «·» y no puede llevar espacios."
            )
        findings.append(
            _finding(
                ctx,
                "C05",
                SEVERITY_ERROR,
                message,
                (
                    f"Escríbelo así: «### {propuesta} · {legible}». El slug va en "
                    "inglés, en minúsculas y con guiones simples, y no lleva espacios; "
                    "el nombre legible del papel va después del «·»."
                ),
                line=user.line,
                subject=user.slug,
            )
        )

    return findings


def _kebab(text: str) -> str:
    """Propone el kebab-case de un texto, para la pista de C05."""
    normalized = _strip_accents(text or "").lower()
    pieces = [piece for piece in re.split(r"[^a-z0-9]+", normalized) if piece]
    return "-".join(pieces)


def rule_c06(ctx: Context) -> list[Finding]:
    """C06 · Las prioridades son enteros, empiezan en 1 y no tienen huecos ni repetidos."""
    rows = ctx.charter.capabilities
    if not rows:
        return []

    findings: list[Finding] = []
    for row in rows:
        if row.priority is not None:
            continue
        written = row.priority_text or "(vacía)"
        findings.append(
            _finding(
                ctx,
                "C06",
                SEVERITY_ERROR,
                (
                    f"La prioridad «{written}» de {row.label} no es un número entero: "
                    "la prioridad es el orden en que se va a construir, y un orden se "
                    "cuenta."
                ),
                (
                    "Numera las filas con enteros desde el 1, sin huecos ni repetidos: "
                    "la 1 es la capability por la que empiezas."
                ),
                line=row.line,
                subject=row.slug or None,
            )
        )

    if findings:
        # Con una prioridad ilegible no se puede juzgar la serie: decir además
        # «faltan la 2 y la 3» sería contar dos veces el mismo desperfecto.
        return findings

    values = [row.priority for row in rows if row.priority is not None]
    expected = list(range(1, len(values) + 1))
    if sorted(values) == expected:
        return []

    problems: list[str] = []
    repeated = sorted({value for value in values if values.count(value) > 1})
    if repeated:
        listed = ", ".join(str(value) for value in repeated)
        if len(repeated) == 1:
            problems.append(f"la prioridad {listed} está repetida")
        else:
            problems.append(f"las prioridades {listed} están repetidas")
    missing = [value for value in expected if value not in values]
    if missing:
        listed = ", ".join(str(value) for value in missing)
        if len(missing) == 1:
            problems.append(f"falta la {listed}")
        else:
            problems.append(f"faltan la {listed}")
    if not problems:
        # Defensa: una serie sin repetidos y sin huecos es la serie completa, así
        # que aquí no se llega. Si algún día se llegara, el mensaje sigue diciendo
        # algo cierto en vez de quedarse a medias.
        problems.append("la serie no empieza en 1")

    written = ", ".join(str(value) for value in values)
    return [
        _finding(
            ctx,
            "C06",
            SEVERITY_ERROR,
            (
                f"Las prioridades del acta son {written} y tienen que ser 1…"
                f"{len(values)}: {' y '.join(problems)}. Dos capabilities no pueden ser "
                "la primera, y una prioridad que falta es una decisión que nadie tomó."
            ),
            (
                "Renumera la columna «#» de 1 en adelante, en el orden en que vas a "
                "construir. Si dos te parecen igual de urgentes, elige: el acta existe "
                "para eso."
            ),
            line=rows[0].line,
        )
    ]


def rule_c07(ctx: Context) -> list[Finding]:
    """C07 · Cada capability declara «Done when». **Es el oráculo del acta.**

    Sin criterio de terminación nadie puede afirmar que una capability está
    hecha, y lo que no se puede dar por terminado no se termina: se abandona
    cuando aburre. Es la misma exigencia que `V06` le hace a un requisito con su
    `verifies:`, una fase antes: allí la apuesta la resuelve un test, y aquí un
    hecho que alguien puede ver.
    """
    findings: list[Finding] = []
    for row in ctx.charter.capabilities:
        if row.done_when:
            continue
        findings.append(
            _finding(
                ctx,
                "C07",
                SEVERITY_ERROR,
                (
                    f"La capability {row.label} no declara «Done when»: sin criterio de "
                    "terminación nadie puede afirmar que está hecha, y lo que no se "
                    "puede dar por terminado no es una capability, es un deseo."
                ),
                (
                    "Escribe en la columna «Done when» el hecho observable que te haría "
                    "decir «ya está»: quién hace qué y qué ve. Por ejemplo «un cliente "
                    "reserva y recibe la confirmación con su hora». Si no sabes "
                    "escribirlo, todavía no sabes qué estás construyendo, y descubrirlo "
                    "hoy es lo más barato que te va a pasar en este proyecto."
                ),
                line=row.line,
                subject=row.slug or None,
            )
        )
    return findings


def rule_c08(ctx: Context) -> list[Finding]:
    """C08 · El «Done when» está en términos observables, no de implementación.

    Dos maneras distintas de no ser observable, y la regla mira las dos porque
    la segunda es la que llega de verdad al acta.

    **La tarea de implementación** se rechaza sólo cuando la frase *empieza* por
    uno de los verbos de la lista, en infinitivo o en participio. Mencionarlo de
    pasada no es un problema: «el dueño ve las mesas libres sin configurar nada»
    describe un hecho observable, y denunciarlo sería el falso positivo que hace
    que la regla se acabe apagando entera.

    **La fórmula vacía** —«el sistema funciona correctamente», «la funcionalidad
    está completa»— no arranca por ningún verbo de implementación y aun así no
    contesta ni quién lo ve ni qué ve. Se rechaza cuando ocupa la celda entera,
    porque así una frase de verdad nunca puede casar con ella: en cuanto hay un
    sujeto y un hecho, el patrón deja de aplicar. Un criterio así lo da por
    cumplido quien tenga prisa, que es justo el escenario contra el que se
    escribe el acta.
    """
    findings: list[Finding] = []
    for row in ctx.charter.capabilities:
        if not row.done_when:
            # La ausencia la denuncia C07, que además explica por qué importa.
            continue

        verb = _leading_implementation_verb(row.done_when)
        if verb is not None:
            message = (
                f"El «Done when» de {row.label} empieza por «{verb}», que es una "
                f"tarea de implementación: «{row.done_when}» dice lo que alguien va "
                "a programar, no lo que alguien va a poder ver."
            )
            hint = (
                "Reescríbelo como quién hace qué y qué ve: en vez de "
                f"«{row.done_when}», algo como «un cliente reserva y recibe la "
                "confirmación con su hora». La prueba es sencilla: si puedes "
                "reescribir el código entero sin que la frase deje de ser cierta, "
                "la frase sirve de criterio; si la frase habla del código, caduca "
                "con él."
            )
        elif _is_empty_formula(row.done_when):
            message = (
                f"El «Done when» de {row.label} es «{row.done_when}»: una fórmula que "
                "se puede dar por cumplida sin mirar nada, porque no dice quién lo ve "
                "ni qué ve."
            )
            hint = (
                "Contéstale a la celda las dos preguntas del acta: ¿quién lo ve? y "
                f"¿qué ve? En vez de «{row.done_when}», algo como «un cliente reserva "
                "y recibe la confirmación con su hora». Y si no sabes escribirlo, no "
                "es una frase que redactar mejor: es una pregunta más para quien pidió "
                "la capability, porque todavía no está decidido qué se está "
                "construyendo."
            )
        else:
            continue

        findings.append(
            _finding(
                ctx,
                "C08",
                SEVERITY_ERROR,
                message,
                hint,
                line=row.line,
                subject=row.slug or None,
            )
        )
    return findings


def _leading_implementation_verb(text: str) -> str | None:
    """El verbo de implementación con el que arranca la frase, si es que arranca.

    Se mira el infinitivo de la lista cerrada y, después, el participio: son la
    misma tarea escrita de las dos maneras en que se escribe.
    """
    normalized = _normalize(text)
    for verb in IMPLEMENTATION_VERBS:
        if normalized == verb or normalized.startswith(f"{verb} "):
            return verb
    participle = IMPLEMENTATION_PARTICIPLE_RE.match(normalized)
    if participle is not None:
        return participle.group("verb")
    return None


def _bare_text(text: str) -> str:
    """El texto normalizado y sin la envoltura que no dice nada.

    Quita la negrita, los acentos graves y la puntuación de los extremos, que es
    lo que separa «**está hecho.**» de «esta hecho» sin cambiar nada de lo que
    la frase afirma. Lo usan las dos comparaciones de celda entera del fichero.
    """
    return re.sub(r"^[*_`\s]+|[*_`\s.,;:…!?]+$", "", _normalize(text))


def _is_empty_formula(text: str) -> bool:
    """¿La celda entera es una fórmula que se declara cumplida sin mirar nada?"""
    bare = _bare_text(text)
    return bool(bare) and EMPTY_DONE_WHEN_RE.match(bare) is not None


def _is_filler_exclusion(text: str) -> bool:
    """¿La viñeta entera es un «ya veremos» en vez de un no?"""
    bare = _bare_text(text)
    return bool(bare) and FILLER_EXCLUSION_RE.match(bare) is not None


def rule_c09(ctx: Context) -> list[Finding]:
    """C09 · «Risk» vale exactamente high, medium o low."""
    findings: list[Finding] = []
    admitted = ", ".join(f"«{level}»" for level in RISK_LEVELS)
    default_hint = (
        "Escribe «high» si esa capability puede tumbar el proyecto, «medium» si te "
        "puede costar semanas y «low» si ya sabes hacerla. En inglés y en minúsculas: "
        "el riesgo alto es el que obliga a declarar una apuesta en «## Bets»."
    )

    for row in ctx.charter.capabilities:
        value = row.risk
        if value in RISK_LEVELS:
            continue

        if not value:
            message = (
                f"La capability {row.label} no declara «Risk»: no dice cuánto de esto "
                "es terreno conocido."
            )
            hint = default_hint
        elif value.lower() in RISK_LEVELS:
            # El nivel es de los tres, pero con la caja cambiada. Es otro error y
            # se arregla de otra manera: se corrige la caja, no se elige otro
            # nivel. Mismo cuidado que tiene V09 con «confidence».
            expected = value.lower()
            message = (
                f"El «Risk» de {row.label} es «{value}» y lleva la caja cambiada: el "
                f"nivel se escribe «{expected}», en minúsculas."
            )
            hint = (
                f"Cámbialo por «{expected}». Los tres niveles se comparan tal cual, así "
                "que mientras la caja no coincida el riesgo no cuenta como declarado y "
                "C15 no te reclamará ninguna apuesta por él."
            )
        else:
            message = (
                f"El «Risk» de {row.label} es «{value}», que no es un nivel del acta; "
                f"los únicos son {admitted}."
            )
            hint = default_hint

        findings.append(
            _finding(
                ctx,
                "C09",
                SEVERITY_ERROR,
                message,
                hint,
                line=row.line,
                subject=row.slug or None,
            )
        )
    return findings


def rule_c10(ctx: Context) -> list[Finding]:
    """C10 · «## Out of scope» trae al menos una entrada. **Sin no-alcance no hay alcance.**

    Un proyecto que no ha dicho que no a nada todavía no ha decidido nada. El
    no-alcance es la única parte del acta que cuesta algo escribir: obliga a
    renunciar delante de testigos, y por eso es la que de verdad fija la
    frontera. Lo que hoy cuesta una línea, dentro de un mes cuesta una discusión.

    Cuenta entradas, pero no cuenta viñetas: «- nada por ahora» es una viñeta y
    no es una entrada. Es exactamente el acta que esta regla existe para
    señalar, y mientras se contaran viñetas bastaba escribirla para apagarla.
    """
    if not ctx.charter.has(SECTION_OUT_OF_SCOPE):
        return []

    filler = [item for item in ctx.charter.exclusions if _is_filler_exclusion(item.text)]
    if len(filler) < len(ctx.charter.exclusions):
        # Queda al menos un no de verdad, y con uno ya hay frontera.
        return []

    hint = (
        "Escribe al menos una viñeta «- **<Qué>.** <por qué no>» con algo que "
        "te han pedido —o que te apetece— y que esta versión no va a hacer. "
        "Por ejemplo «- **Pagos y señales.** No se cobra nada en la v1; el "
        "riesgo regulatorio no compensa hasta que haya reservas de verdad». "
        "Decir que no aquí cuesta una línea; decirlo dentro de un mes cuesta "
        "una discusión."
    )

    if not filler:
        message = (
            "El acta no declara nada fuera de alcance: un proyecto que no ha dicho "
            "que no a nada todavía no ha decidido nada, y un alcance sin frontera "
            "se lo acaba comiendo todo."
        )
        line = ctx.charter.line_of(SECTION_OUT_OF_SCOPE)
    else:
        first = filler[0]
        counted = (
            "la única entrada"
            if len(filler) == 1
            else f"las {len(filler)} entradas"
        )
        message = (
            f"«{first.text}» no excluye nada, y es {counted} de «## Out of scope»: "
            "el acta ocupa la sección sin llegar a decir que no a nada, que es "
            "justo lo que la sección existe para impedir."
        )
        hint = (
            f"{hint} Y ojo a la confusión de siempre: «más adelante» tampoco es un "
            "no-alcance, es una fila con un número alto en la tabla de arriba."
        )
        line = first.line

    return [_finding(ctx, "C10", SEVERITY_ERROR, message, hint, line=line)]


def rule_c11(ctx: Context) -> list[Finding]:
    """C11 · Cada apuesta declara «confidence:» con uno de los tres niveles."""
    findings: list[Finding] = []
    admitted = ", ".join(f"«{level}»" for level in CONFIDENCE_LEVELS)
    default_hint = (
        "Escribe «confidence: high», «medium» o «low», en inglés y en minúsculas. No "
        "hay valor por defecto: si no sabes cuánto confías en la suposición, la "
        "respuesta suele ser «low»."
    )

    for bet in ctx.charter.bets:
        value = bet.value("confidence")
        if value in CONFIDENCE_LEVELS:
            continue

        if value is None:
            message = (
                f"La apuesta {bet.label} no declara «confidence:»: dice lo que se está "
                "suponiendo y no dice cuánto se confía en ello."
            )
            hint = default_hint
        elif not value:
            message = (
                f"El «confidence:» de {bet.label} está vacío: la línea está escrita y "
                "no dice ningún nivel."
            )
            hint = default_hint
        elif value.lower() in CONFIDENCE_LEVELS:
            expected = value.lower()
            message = (
                f"«confidence: {value}» de {bet.label} lleva la caja cambiada: el nivel "
                f"se escribe «{expected}», en minúsculas."
            )
            hint = (
                f"Cámbialo por «confidence: {expected}»: los tres niveles se comparan "
                "tal cual, y mientras la caja no coincida el nivel no cuenta como "
                "declarado —así que C12 tampoco te reclamará la fecha de revisión—."
            )
        else:
            message = (
                f"«confidence: {value}» no es un nivel admitido en {bet.label}; los "
                f"únicos son {admitted}."
            )
            hint = default_hint

        findings.append(
            _finding(
                ctx,
                "C11",
                SEVERITY_ERROR,
                message,
                hint,
                line=bet.line_of("confidence"),
                subject=bet.id,
            )
        )
    return findings


def rule_c12(ctx: Context) -> list[Finding]:
    """C12 · Una apuesta en «low» declara «revisit:»: el hecho que la resuelve.

    No una fecha. Lo que cierra una suposición no es que pase el tiempo, es que
    llegue un dato: «cuando cerremos la primera compra», «cuando hayamos visto
    veinte presupuestos de proveedores nuevos». El hecho dice qué habrá que
    mirar y permite reconocer el momento cuando llega; un día del calendario no
    dice ninguna de las dos cosas, y llega igual esté la respuesta disponible o
    no. Una fecha que se cumple sin que haya nada que mirar sólo se puede
    posponer, y una apuesta pospuesta dos veces ya no la lee nadie.

    Por eso una fecha ISO aquí es un error y no un descuido de forma: es la
    respuesta que este campo dejó de admitir, y dejarla pasar la reintroduciría
    por inercia. El acta la revisa entera cada vez que se retoma —ése es el
    momento en que se pregunta cuáles se han resuelto—, y para eso el hecho
    sirve y la fecha no.
    """
    findings: list[Finding] = []

    for bet in ctx.charter.bets:
        value = bet.value("revisit")
        line = bet.line_of("revisit")
        # La **obligación** de traer «revisit:» es sólo de «low»: una apuesta en
        # «medium» puede no declarar cómo se resuelve y sigue siendo legal. Pero
        # la **forma** del valor vale para todas: un «revisit:» escrito dice qué
        # resuelve la apuesta o no dice nada, y eso no depende de la confianza.
        # Separarlo importa, porque las fechas inventadas se acumulan justo en
        # «medium», que es donde acaba casi todo lo que no es un hecho ni una
        # corazonada.
        if bet.value("confidence") != "low" and value is None:
            # Un «LOW» con la caja cambiada no es un nivel válido —lo dice C11— y
            # no se le puede reclamar el oráculo de una apuesta mal declarada.
            continue

        if value is None:
            message = (
                f"{bet.label} declara «confidence: low» y no trae «revisit:»: una "
                "suposición que no dice qué la resuelve deja de ser una apuesta y se "
                "convierte en «cómo funciona el sistema»."
            )
            hint = (
                f"Añade el hecho que la cierra: «revisit: {REVISIT_EXAMPLE}». No una "
                "fecha: hace falta saber qué habrá que mirar y poder reconocer cuándo "
                "ya se puede mirar. Si no lo sabes tú, es una pregunta más para quien "
                "conoce el negocio; y si ya lo has comprobado con alguien, sube la "
                "confianza."
            )
        elif not value:
            message = (
                f"El «revisit:» de {bet.label} está vacío: promete decir qué resuelve "
                "la apuesta y no lo dice."
            )
            hint = (
                f"Escribe el hecho: «revisit: {REVISIT_EXAMPLE}», o sube la confianza "
                "si ya no es una apuesta."
            )
        elif ISO_DATE_RE.match(value):
            message = (
                f"«revisit: {value}» de {bet.label} es una fecha, y «revisit:» pide el "
                "hecho que resuelve la apuesta, no el día en que caduca."
            )
            hint = (
                "El día llega esté la respuesta o no, y quien llegue a él no sabrá qué "
                "tenía que mirar. Escribe el dato que la cierra: "
                f"«revisit: {REVISIT_EXAMPLE}». Si la fecha salía de algo —el fin de "
                "una campaña, la primera entrega—, nombra ese algo, que es lo que de "
                "verdad la resuelve."
            )
        elif _is_filler_revisit(value):
            message = (
                f"«revisit: {value}» de {bet.label} no nombra ningún hecho: es una "
                "forma de decir «más adelante», y más adelante no llega nunca."
            )
            hint = (
                "Contesta a qué tendría que pasar para poder cerrar esta apuesta: un "
                "número de casos vistos, un cliente usándolo, una conversación que "
                f"todavía no has tenido. Por ejemplo «revisit: {REVISIT_EXAMPLE}». Si "
                "no hay nada que pueda resolverla, no es una apuesta: es una decisión "
                "tomada, y va en «medium» con su «why:»."
            )
        else:
            continue

        findings.append(
            _finding(
                ctx,
                "C12",
                SEVERITY_ERROR,
                message,
                hint,
                line=line,
                subject=bet.id,
            )
        )
    return findings


def _is_filler_revisit(value: str) -> bool:
    """¿El «revisit:» entero es un «ya veremos» en vez de un hecho?"""
    bare = _bare_text(value)
    return bool(bare) and FILLER_REVISIT_RE.match(bare) is not None

def rule_c13(ctx: Context) -> list[Finding]:
    """C13 · El identificador de la apuesta casa «B-NNN» y es único."""
    findings: list[Finding] = []
    seen: dict[str, Bet] = {}
    next_free = len(ctx.charter.bets) + 1

    for bet in ctx.charter.bets:
        identifier = bet.id or ""
        if not BET_ID_RE.match(identifier):
            proposal = f"B-{min(next_free, 999):03d}"
            if not identifier:
                message = (
                    f"El encabezado «### {bet.header}» no declara identificador de "
                    "apuesta: sin él nadie puede citarla cuando llegue el día de "
                    "resolverla."
                )
            else:
                message = (
                    f"El identificador «{identifier}» no tiene la forma «B-NNN»: una "
                    "«B», un guion y tres dígitos."
                )
            findings.append(
                _finding(
                    ctx,
                    "C13",
                    SEVERITY_ERROR,
                    message,
                    (
                        f"Escribe el encabezado como «### {proposal} · "
                        f"{bet.title or 'Título de la apuesta'}»: el identificador, el "
                        "separador «·» y el título."
                    ),
                    line=bet.line,
                    subject=bet.id,
                )
            )
            continue

        previous = seen.get(identifier)
        if previous is not None:
            findings.append(
                _finding(
                    ctx,
                    "C13",
                    SEVERITY_ERROR,
                    (
                        f"El identificador «{identifier}» ya está declarado en la línea "
                        f"{previous.line}: dos apuestas no pueden compartirlo."
                    ),
                    (
                        f"Renumera la segunda apuesta —por ejemplo «B-{min(next_free, 999):03d}»— "
                        "y deja intacta la primera, que es a la que ya apunta todo el "
                        "que la haya citado."
                    ),
                    line=bet.line,
                    subject=identifier,
                )
            )
            continue

        seen[identifier] = bet

    return findings


def rule_c14(ctx: Context) -> list[Finding]:
    """C14 · «fatal:» vale «yes» o «no» cuando está presente."""
    findings: list[Finding] = []
    for bet in ctx.charter.bets:
        value = bet.value("fatal")
        if value is None or value in FATAL_VALUES:
            continue
        findings.append(
            _finding(
                ctx,
                "C14",
                SEVERITY_WARNING,
                (
                    f"«fatal: {value or '(vacío)'}» de {bet.label} no es «yes» ni «no»: "
                    "la pregunta es si el proyecto se cae cuando la apuesta salga mal, "
                    "y sólo admite esas dos respuestas."
                ),
                (
                    "Escribe «fatal: yes» si equivocarte aquí tumba el proyecto y "
                    "«fatal: no» si sólo te cuesta trabajo. Si dudas, escribe «yes» y "
                    "pon la apuesta la primera."
                ),
                line=bet.line_of("fatal"),
                subject=bet.id,
            )
        )
    return findings


def rule_c15(ctx: Context) -> list[Finding]:
    """C15 · Un acta con capabilities de riesgo alto y ninguna apuesta declarada."""
    if not ctx.charter.has(SECTION_BETS):
        # Que la sección no esté ya lo dice C01, y con más razón que aquí.
        return []
    if ctx.charter.bets:
        return []

    risky = [row for row in ctx.charter.capabilities if row.risk == "high"]
    if not risky:
        return []

    listed = ", ".join(f"«{row.slug or row.priority_text}»" for row in risky)
    return [
        _finding(
            ctx,
            "C15",
            SEVERITY_WARNING,
            (
                f"El acta declara riesgo alto en {listed} y no declara ninguna apuesta: "
                "un riesgo alto sin suposición escrita es una suposición que nadie va a "
                "revisar."
            ),
            (
                "Escribe en «## Bets» qué estás dando por hecho en esa capability: "
                "«### B-001 · <título>», la prosa, y «confidence», «why», «revisit» y "
                "«fatal». Si no encuentras ninguna suposición, el riesgo probablemente "
                "no sea alto y lo que toca es bajarlo a «medium»."
            ),
            line=ctx.charter.line_of(SECTION_BETS),
        )
    ]


def rule_c16(ctx: Context) -> list[Finding]:
    """C16 · El orden del acta y el orden en que se ha construido no coinciden.

    Una capability que ya tiene `spec.md` vivo está en marcha. Si el acta la
    coloca detrás de otra que todavía no tiene ninguna, la prioridad escrita no
    es la que se está siguiendo: el acta dice una cosa y el disco otra. Es un
    aviso y no un error porque adelantarse puede estar justificado —lo que no
    puede es quedarse sin decir—.

    La regla mira sólo lo que existe: `.venoxia/capabilities/<slug>/spec.md`. Un
    proyecto que todavía no ha especificado nada no dispara nada.
    """
    if not ctx.live_capabilities:
        return []

    ordered = sorted(
        (row for row in ctx.charter.capabilities if row.priority is not None and row.slug),
        key=lambda row: (row.priority or 0, row.line),
    )
    findings: list[Finding] = []
    pending: list[CapabilityRow] = []

    for row in ordered:
        if row.slug not in ctx.live_capabilities:
            pending.append(row)
            continue
        if not pending:
            continue
        skipped = pending[0]
        findings.append(
            _finding(
                ctx,
                "C16",
                SEVERITY_WARNING,
                (
                    f"La capability «{row.slug}» es la prioridad {row.priority} del acta "
                    f"y ya tiene especificación viva en «{ctx.live_capabilities[row.slug]}», "
                    f"mientras que «{skipped.slug}», que el acta pone antes (prioridad "
                    f"{skipped.priority}), no tiene ninguna: el orden que se está "
                    "siguiendo no es el que el acta declara."
                ),
                (
                    f"Si el orden ha cambiado, renumera la tabla y sube «{row.slug}» al "
                    f"puesto que de verdad ocupa; si «{skipped.slug}» sigue siendo lo "
                    "primero, especifícala con «/venoxia:specify». Un acta que nadie "
                    "corrige cuando el plan cambia deja de ser el plan."
                ),
                line=row.line,
                subject=row.slug,
            )
        )

    return findings


RULES: list[Rule] = [
    Rule("C01", SEVERITY_ERROR, "Están las cinco secciones obligatorias", rule_c01),
    Rule("C02", SEVERITY_ERROR, "El propósito tiene entre una y tres frases", rule_c02),
    Rule("C03", SEVERITY_ERROR, "Hay usuarios, y cada uno dice su hoy y su con esto", rule_c03),
    Rule("C04", SEVERITY_ERROR, "Hay al menos una capability en la tabla", rule_c04),
    Rule("C05", SEVERITY_ERROR, "Cada slug es kebab-case y único", rule_c05),
    Rule("C06", SEVERITY_ERROR, "Las prioridades son 1…N, sin huecos ni repetidos", rule_c06),
    Rule("C07", SEVERITY_ERROR, "Cada capability declara «Done when»", rule_c07),
    Rule("C08", SEVERITY_ERROR, "El «Done when» está en términos observables", rule_c08),
    Rule("C09", SEVERITY_ERROR, "«Risk» vale high, medium o low", rule_c09),
    Rule("C10", SEVERITY_ERROR, "El acta declara algo fuera de alcance", rule_c10),
    Rule("C11", SEVERITY_ERROR, "Cada apuesta declara «confidence:»", rule_c11),
    Rule("C12", SEVERITY_ERROR, "Una apuesta en «low» trae «revisit:» futuro", rule_c12),
    Rule("C13", SEVERITY_ERROR, "El identificador de la apuesta casa «B-NNN» y es único", rule_c13),
    Rule("C14", SEVERITY_WARNING, "«fatal:» vale yes o no cuando está", rule_c14),
    Rule("C15", SEVERITY_WARNING, "Un riesgo alto sin apuestas declaradas", rule_c15),
    Rule("C16", SEVERITY_WARNING, "El orden construido es el que el acta declara", rule_c16),
]


def run_rules(ctx: Context) -> list[Finding]:
    """Aplica las dieciséis reglas en orden y devuelve todos sus hallazgos.

    Una regla que se cayera no puede tumbar el linter entero: el fallo se
    convierte en un hallazgo con su código y el resto sigue. Es la misma defensa
    que tiene `validate.py`, y por el mismo motivo: quien está escribiendo su
    acta merece un veredicto, no una traza.
    """
    findings: list[Finding] = []
    for rule in RULES:
        try:
            produced = rule.check(ctx) or []
        except Exception as error:  # defensa: el linter siempre da un veredicto
            findings.append(
                Finding(
                    rule=rule.code,
                    severity=SEVERITY_ERROR,
                    message=(
                        f"La regla {rule.code} no se pudo aplicar: "
                        f"{type(error).__name__}: {error}."
                    ),
                    file=ctx.display,
                    hint=(
                        "Es un fallo de Venoxia, no del acta: repórtalo indicando el "
                        "fichero que lo provoca."
                    ),
                )
            )
            continue
        findings.extend(produced)
    return findings


# ---------------------------------------------------------------------------
# Localización del acta
# ---------------------------------------------------------------------------


@dataclass
class Target:
    """Qué acta hay que juzgar, o por qué no hay ninguna."""

    path: Path | None = None
    adopted: bool = True
    present: bool = True
    note: str = ""


def locate_charter(root: Path, given: str | None) -> Target:
    """Decide qué fichero se juzga.

    Con una ruta explícita manda la ruta, aunque viva fuera de `.venoxia/`: quien
    la nombra sabe lo que hace, y que no exista es un error de uso. Sin ruta, se
    busca el acta en su sitio canónico y las dos ausencias posibles —el proyecto
    sin `.venoxia/` y el `.venoxia/` sin acta— se responden con un mensaje y un
    cero, no con un fallo.
    """
    if given:
        candidate = Path(os.path.expanduser(given))
        if not candidate.is_absolute() and not candidate.exists():
            candidate = root / candidate
        if candidate.is_dir():
            raise UsageError(
                f"«{given}» es un directorio: nombra el fichero del acta, por ejemplo "
                f"«{Path(given) / CHARTER_FILENAME}», o usa «--root» para cambiar la "
                "raíz del proyecto."
            )
        if not candidate.is_file():
            raise UsageError(
                f"no existe la ruta «{given}»: no está ni en «{Path.cwd()}» ni en "
                f"«{root}»."
            )
        return Target(path=candidate)

    venoxia_dir = root / VENOXIA_DIR
    if not venoxia_dir.is_dir():
        return Target(adopted=False, present=False)

    charter_path = venoxia_dir / CHARTER_FILENAME
    if not charter_path.is_file():
        return Target(present=False)

    return Target(path=charter_path)


def live_capabilities(root: Path) -> dict[str, str]:
    """Las capabilities que ya tienen `spec.md` en disco: slug → ruta relativa."""
    found: dict[str, str] = {}
    directory = root / VENOXIA_DIR / CAPABILITIES_DIR
    try:
        entries = sorted(directory.glob(f"*/{SPEC_FILENAME}"))
    except OSError:
        # Un directorio que no se deja recorrer no acusa a nadie: C16 se calla.
        return found
    for spec in entries:
        found[spec.parent.name] = _display_path(spec, root)
    return found


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------


def lint_charter(root: Path, path: Path, strict: bool = False) -> tuple[ValidationResult, Charter]:
    """Lee el acta, aplica las reglas y devuelve el resultado y el modelo.

    Un acta que no se deja leer produce el `P01` del parser **y nada más**: las
    dieciséis reglas hablan de lo que el acta dice, y de un fichero que no se ha
    podido abrir no se puede decir que le falte la sección «## Purpose». Sería
    culpar al contenido de un problema del continente.
    """
    result = ValidationResult(strict=strict, root=str(root))
    charter = parse_charter(path, root)

    if charter.failure is not None:
        result.add(charter.failure)
        return result, charter

    ctx = Context(
        root=root,
        path=path,
        display=charter.path,
        charter=charter,
        live_capabilities=live_capabilities(root),
    )
    for finding in run_rules(ctx):
        result.add(finding)
    return result, charter


def charter_payload(charter: Charter) -> dict:
    """Lo propio del acta dentro del JSON: sus recuentos y sus prioridades.

    Cuelga de la clave `charter` del esquema estable. Las prioridades van en el
    documento porque son lo único accionable que el acta produce: de ahí sale el
    `/venoxia:specify` de la primera capability.
    """
    return {
        "path": charter.path,
        "counts": {
            "users": len(charter.users),
            "capabilities": len(charter.capabilities),
            "out_of_scope": len(charter.exclusions),
            "bets": len(charter.bets),
        },
        "capabilities": [
            {"priority": row.priority, "slug": row.slug, "risk": row.risk}
            for row in charter.capabilities
        ],
    }


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------


def _plural(count: int, singular: str, plural: str) -> str:
    """«1 apuesta» o «3 apuestas», con la palabra que toque."""
    return f"{count} {singular if count == 1 else plural}"


def summary_lines(result: ValidationResult, charter: Charter, enabled: bool) -> list[str]:
    """Las líneas de cierre: qué trae el acta, qué falla y el veredicto.

    `report.summary_lines` no vale aquí: cuenta requisitos, capabilities y deltas
    del ámbito validado, y un acta no tiene ninguna de las tres cosas. Diría «0
    requisitos · sin ficheros de especificación» al pie de un acta impecable.
    """
    counts = result.counts()
    contents = " · ".join(
        (
            _plural(len(charter.users), "usuario", "usuarios"),
            _plural(len(charter.capabilities), "capability", "capabilities"),
            _plural(len(charter.exclusions), "exclusión", "exclusiones"),
            _plural(len(charter.bets), "apuesta", "apuestas"),
        )
    )
    lines = [f"Acta «{charter.path}»: {contents}"]

    counted = (
        f"{_plural(counts['error'], 'error', 'errores')}, "
        f"{_plural(counts['warning'], 'aviso', 'avisos')}"
    )
    if result.strict:
        counted = f"{counted} · modo estricto: los avisos cuentan"
    lines.append(counted)

    if result.ok:
        lines.append(
            report.paint(
                f"{report.MARK_OK} El acta define el proyecto y se puede verificar.",
                report.ANSI_GREEN,
                enabled,
            )
        )
    else:
        lines.append(
            report.paint(
                f"{report.MARK_ERROR} El acta todavía no define el proyecto: corrige lo "
                "de arriba y vuelve a pasarla.",
                report.ANSI_RED,
                enabled,
            )
        )
    return lines


def render_text(result: ValidationResult, charter: Charter, no_color: bool = False) -> str:
    """Informe completo para una persona, con el remedio pegado al problema.

    Los hallazgos los pinta `report.render_finding_lines`, que es la misma
    máquina que usa `validate.py`: mismo orden, mismos colores, mismo remedio
    debajo del mensaje. Lo único propio de aquí es el cierre.
    """
    enabled = report.color_enabled(no_color)
    findings = report.sort_findings(result.findings)
    lines: list[str] = []

    groups = (
        ("Errores", SEVERITY_ERROR, report.MARK_ERROR, report.ANSI_RED),
        ("Avisos", SEVERITY_WARNING, report.MARK_WARNING, report.ANSI_YELLOW),
    )
    for title, severity, mark, color in groups:
        group = [finding for finding in findings if finding.severity == severity]
        if not group:
            continue
        lines.append(report.paint(f"{title} ({len(group)})", color, enabled))
        lines.append("")
        for finding in group:
            lines.extend(report.render_finding_lines(finding, mark, color, enabled))
            lines.append("")

    # Defensa: una severidad inesperada no puede desaparecer del informe.
    others = [
        finding
        for finding in findings
        if finding.severity not in (SEVERITY_ERROR, SEVERITY_WARNING)
    ]
    if others:
        lines.append(report.paint(f"Otros hallazgos ({len(others)})", report.ANSI_YELLOW, enabled))
        lines.append("")
        for finding in others:
            lines.extend(
                report.render_finding_lines(
                    finding, report.MARK_WARNING, report.ANSI_YELLOW, enabled
                )
            )
            lines.append("")

    lines.extend(summary_lines(result, charter, enabled))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos."""
    cli = argparse.ArgumentParser(
        prog="charter_lint.py",
        description=(
            "Comprueba el acta del proyecto contra las dieciséis reglas del contrato "
            "del acta. Determinista: ninguna regla consulta a un modelo."
        ),
        epilog=(
            "Códigos de salida: 0 el acta cumple · 1 no cumple · 2 error de uso. Ni un "
            "proyecto sin .venoxia/ ni un .venoxia/ sin acta son errores: se avisa y se "
            "sale con 0."
        ),
    )
    cli.add_argument(
        "path",
        nargs="?",
        metavar="PATH",
        help=(
            "el fichero del acta; sin él se juzga «.venoxia/charter.md» bajo la raíz "
            "del proyecto"
        ),
    )
    cli.add_argument(
        "--root",
        metavar="DIR",
        help="raíz del proyecto, la que contiene .venoxia/ (por defecto, el directorio actual)",
    )
    cli.add_argument("--strict", action="store_true", help="los avisos también hacen fallar")
    cli.add_argument(
        "--json",
        action="store_true",
        help="emite el JSON del esquema estable en vez del informe de texto",
    )
    cli.add_argument("--no-color", action="store_true", help="sin colores ANSI")
    return cli


def _absent(args: argparse.Namespace, root: Path, target: Target) -> int:
    """Responde a las dos ausencias que no son un error, y siempre con cero."""
    if not target.adopted:
        message = (
            f"venoxia: este proyecto todavía no ha adoptado Venoxia (no existe "
            f"«{root / VENOXIA_DIR}»). No hay acta que comprobar."
        )
    else:
        message = (
            f"venoxia: este proyecto no tiene acta (no existe "
            f"«{root / VENOXIA_DIR / CHARTER_FILENAME}»). Si vas a empezar de cero, "
            "escríbela con «/venoxia:charter»; si ya sabes qué comportamiento quieres, "
            "el acta no hace falta."
        )

    if args.json:
        # «adopted» y «charter» separan lo que el resto del documento no puede
        # distinguir: sin acta salen los mismos ceros que con un acta impecable.
        empty = ValidationResult(strict=args.strict, root=str(root))
        print(
            report.render_json(
                empty, extra={"adopted": target.adopted, "charter": None}
            )
        )
        print(message, file=sys.stderr)
    else:
        print(message)
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida y nunca lanza por los datos."""
    cli = build_parser()
    args = cli.parse_args(argv)

    root = Path(os.path.expanduser(args.root)) if args.root else Path.cwd()
    if not root.is_dir():
        print(
            f"venoxia: la raíz «{root}» no existe o no es un directorio.",
            file=sys.stderr,
        )
        return EXIT_USAGE
    root = root.resolve()

    try:
        target = locate_charter(root, args.path)
    except UsageError as error:
        print(f"venoxia: {error}", file=sys.stderr)
        return EXIT_USAGE

    if target.path is None:
        return _absent(args, root, target)

    result, charter = lint_charter(root, target.path, strict=args.strict)

    if args.json:
        print(
            report.render_json(
                result, extra={"adopted": True, "charter": charter_payload(charter)}
            )
        )
    else:
        print(render_text(result, charter, no_color=args.no_color))

    return EXIT_OK if result.ok else EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
