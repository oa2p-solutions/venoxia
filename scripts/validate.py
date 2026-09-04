#!/usr/bin/env python3
"""Validador determinista de Venoxia: el contrato que la especificación cumple o no.

Aquí viven las dieciséis reglas del formato. Todas son deterministas: ninguna
consulta a un modelo ni toca la red, y `V10` rechaza tanto una fecha como una
fórmula vacía en `revisit:`: la apuesta debe declarar el hecho que la
resuelve, no un plazo. Dos ejecuciones sobre el mismo árbol producen el mismo
veredicto y el mismo JSON, byte a byte.

Uso:

    python3 scripts/validate.py [PATH ...]
        --root DIR      raíz del proyecto (por defecto, el directorio actual)
        --change ID     valida sólo el change .venoxia/changes/<ID>/
        --strict        los avisos cuentan como fallo
        --json          salida JSON con el esquema estable
        --no-color      sin colores ANSI
        -q, --quiet     sólo el resumen

Códigos de salida: `0` la especificación cumple · `1` no cumple · `2` error de
uso. Un proyecto que todavía no ha adoptado Venoxia —sin `.venoxia/`— no es un
error: se dice y se sale con `0`.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from venoxia import model, parser, report  # noqa: E402
from venoxia.model import (  # noqa: E402
    CONFIDENCE_LEVELS,
    FILLER_REVISIT_RE,
    REQUIREMENT_ID_RE,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    Capability,
    Delta,
    Finding,
    Requirement,
    ValidationResult,
)

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

VENOXIA_DIR = ".venoxia"
CAPABILITIES_DIR = "capabilities"
CHANGES_DIR = "changes"
DELTA_DIR = "delta"
SPEC_FILENAME = "spec.md"

# Bloques cuyos requisitos *declaran* comportamiento: son los únicos que pueden
# duplicar un ID. Los demás bloques citan un ID que ya vive en una capability,
# y repetirlo es exactamente lo que se espera de ellos.
DECLARING_BLOCKS = (None, "ADDED")
REFERENCING_BLOCKS = ("MODIFIED", "REMOVED", "RENAMED")

# Palabras clave que abren un patrón EARS. `THEN` no está: no arranca un
# patrón, cierra el de `IF`.
EARS_START_KEYWORDS = ("WHEN", "WHILE", "WHERE", "IF")

# Patrón EARS de cada combinación admitida de palabras clave de arranque.
EARS_PATTERNS = {
    ("WHEN",): "event-driven",
    ("WHILE",): "state-driven",
    ("WHERE",): "optional-feature",
    ("IF",): "unwanted-behaviour",
    ("WHILE", "WHEN"): "complejo",
}
EARS_UBIQUITOUS = "ubicuo"

# Frontera de cláusula dentro de la narrativa ya colapsada en una línea.
# Los dos puntos **no** cierran cláusula cuando van pegados a una palabra clave
# EARS: «WHEN: el cliente confirma el pago, …» es una forma legítima de escribir
# la condición, y tratarla como frontera dejaba la cláusula «WHEN» sin resto y
# hacía que V02 denunciara como vacía una narrativa que no lo estaba.
CLAUSE_BOUNDARY_RE = re.compile(
    r"(?:(?<!\bWHEN)(?<!\bWHILE)(?<!\bWHERE)(?<!\bIF):|[,;.!?])+\s*|\s+[—–]\s+"
)

# Primera palabra de una cláusula, si viene en mayúsculas.
CLAUSE_KEYWORD_RE = re.compile(r"([A-ZÁÉÍÓÚÜÑ]{2,})\b")

# Primer trozo del encabezado de un requisito, hasta el primer espacio o
# separador. Es el candidato a identificador cuando el parser no ha sabido leer
# ninguno: sirve para distinguir «no hay nada que parezca un ID» de «hay algo
# que lo parece pero está mal escrito».
HEADER_CANDIDATE_RE = re.compile(r"^(?P<candidate>[^\s·—–:]+)")

# Puntuación que puede separar el identificador del título del encabezado.
HEADER_SEPARATORS = " \t·—–:-"

# Un candidato «parece un identificador» si arranca como el molde («R-») o si
# tiene su silueta: empieza por letra, lleva un separador y acaba en dígitos
# —«RCHK_014», «REQ-14»—. Los títulos de verdad no la tienen: ni «Stock
# reservation on payment confirmation», ni «Multi-factor authentication» (no
# acaba en dígitos), ni «15-minute reservation window» (no empieza por letra).
ID_PREFIX_RE = re.compile(r"^[Rr][-_]")
ID_SHAPE_RE = re.compile(r"^[A-Za-z][\w.]*[-_][\w.-]*\d$")

# Modales que delatan una traducción a medias: la prosa va en español.
ENGLISH_MODAL_RE = re.compile(r"\b(SHALL|MUST)\b")

#: Fecha ISO. Ya no se pide en ninguna clave: se usa para **rechazarla** en
#: «revisit:», donde lo que hace falta es el hecho que resuelve la apuesta y no
#: el día en que caduca. Reconocerla es lo que permite dar el remedio bueno en
#: vez de un «valor no válido» que no enseña nada.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")

# Separadores admitidos entre varias rutas de un mismo «verifies:».
VERIFIES_SPLIT_RE = re.compile(r"[,\s]+")

# Colapsa cualquier racha de espacios en blanco en uno solo.
WHITESPACE_RE = re.compile(r"\s+")

# El ejemplo de «revisit:» que usan las pistas de V10.
#: El ejemplo que las pistas de V10 usan para enseñar la forma de un «revisit:».
#: Es deliberadamente un suceso del proyecto y no un plazo: lo que se pide es el
#: hecho que resuelve la apuesta, y un ejemplo con un número de días enseñaría
#: justo lo contrario.
REVISIT_EXAMPLE = "cuando hayamos procesado los primeros veinte pedidos reales"


class UsageError(Exception):
    """Error de uso de la línea de comandos: se responde con el código 2."""


# ---------------------------------------------------------------------------
# Contexto
# ---------------------------------------------------------------------------


@dataclass
class Context:
    """Todo lo que una regla necesita saber, ya leído y ya contado.

    El caché de lectura es parte del contrato interno: varias reglas miran los
    mismos ficheros de test —`V08` comprueba el `@covers` y `V16` busca los
    `@covers` huérfanos— y ninguno se lee dos veces del disco.
    """

    root: Path
    capabilities: list[Capability] = field(default_factory=list)
    deltas: list[Delta] = field(default_factory=list)
    all_requirements: list[Requirement] = field(default_factory=list)
    live_ids: set[str] = field(default_factory=set)
    live_requirements: dict[str, Requirement] = field(default_factory=dict)
    live_by_capability: dict[str, set[str]] = field(default_factory=dict)
    owners: dict[str, str] = field(default_factory=dict)
    disk_reads: int = 0
    _texts: dict[str, str | None] = field(default_factory=dict, repr=False)
    _failures: dict[str, Finding | None] = field(default_factory=dict, repr=False)
    _files: dict[str, bool] = field(default_factory=dict, repr=False)
    _dirs: dict[str, bool] = field(default_factory=dict, repr=False)

    def resolve(self, path: str | Path) -> Path:
        """Resuelve una ruta de la especificación contra la raíz del proyecto."""
        candidate = Path(os.path.expanduser(str(path)))
        if not candidate.is_absolute():
            candidate = self.root / candidate
        return candidate

    def is_file(self, path: str | Path) -> bool:
        """¿Existe ese fichero en disco? El resultado se recuerda."""
        key = str(self.resolve(path))
        if key not in self._files:
            try:
                self._files[key] = Path(key).is_file()
            except OSError:
                self._files[key] = False
        return self._files[key]

    def is_dir(self, path: str | Path) -> bool:
        """¿Esa ruta es un directorio? El resultado se recuerda.

        V07 lo necesita para no acusar de «no existe» a una ruta que existe pero
        no es un fichero: el remedio de una y otra no se parecen en nada.
        """
        key = str(self.resolve(path))
        if key not in self._dirs:
            try:
                self._dirs[key] = Path(key).is_dir()
            except OSError:
                self._dirs[key] = False
        return self._dirs[key]

    def read_with_failure(self, path: str | Path) -> tuple[str | None, Finding | None]:
        """Lee un fichero una sola vez y devuelve también **por qué** no se pudo.

        El `P01` del parser es la única prueba de que un fichero existe y aun así
        no se deja leer —bytes nulos, latin-1, permisos—. Perderlo convierte un
        problema en otro: una regla que no puede mirar dentro del oráculo acaba
        acusándolo de no traer el «@covers» que sí tiene escrito. Por eso el
        fallo se guarda junto al texto y se recuerda igual que el acierto.
        """
        key = str(self.resolve(path))
        if key not in self._texts:
            text, failure = parser.read_text(key)
            self._texts[key] = text
            self._failures[key] = failure
            self.disk_reads += 1
        return self._texts[key], self._failures[key]

    def read(self, path: str | Path) -> str | None:
        """El texto de un fichero, o `None` si no se pudo leer.

        Atajo de `read_with_failure` para quien sólo necesita el contenido; quien
        tenga que explicar la ausencia usa la otra.
        """
        return self.read_with_failure(path)[0]

    def known_ids(self) -> set[str]:
        """IDs que existen: los del ámbito validado más los de las capabilities vivas."""
        known = {
            requirement.id for requirement in self.all_requirements if requirement.id
        }
        known.update(self.live_ids)
        return known


@dataclass(frozen=True)
class Rule:
    """Una regla del contrato: su código, su severidad y la función que la aplica."""

    code: str
    severity: str
    summary: str
    check: Callable[[Context], list[Finding]]


# ---------------------------------------------------------------------------
# Ayudas comunes a las reglas
# ---------------------------------------------------------------------------


def _meta(requirement: Requirement, key: str) -> str | None:
    """Valor de un metadato tal cual, o `None` si la clave no está declarada."""
    value = requirement.meta.get(key)
    return value if value is None else value.strip()


def _meta_line(requirement: Requirement, key: str) -> int | None:
    """Línea del metadato, o la del encabezado si el metadato no existe."""
    return requirement.meta_lines.get(key, requirement.line)


def _verifies_paths(requirement: Requirement) -> list[str]:
    """Rutas declaradas en «verifies:», que admite varias separadas por coma o espacio."""
    value = _meta(requirement, "verifies") or ""
    return [chunk for chunk in VERIFIES_SPLIT_RE.split(value) if chunk]


def _capability_hint(requirement: Requirement) -> str:
    """Nombre de la capability del requisito, para redactar ejemplos útiles."""
    source = Path(requirement.source_file or "")
    if source.stem.lower() == "spec" and source.parent.name:
        return source.parent.name
    return source.stem or "capability"


def _example_id(requirement: Requirement) -> str:
    """El ID del requisito si lo tiene, o el molde que debería seguir."""
    return requirement.id or "R-XXX-000"


def _header_parts(requirement: Requirement) -> tuple[str, str]:
    """Parte el encabezado sin ID en «lo que podría ser el ID» y «el resto».

    Cuando el parser no encuentra separador, el encabezado entero se guarda como
    título. Aquí se vuelve a mirar para saber qué tiene delante: si es un
    identificador mal escrito, el mensaje y la pista de `V01` tienen que hablar
    de él y no fingir que el encabezado no traía ninguno.
    """
    body = (requirement.title or "").strip()
    match = HEADER_CANDIDATE_RE.match(body)
    if match is None:
        return "", body
    candidate = match.group("candidate")
    rest = body[match.end() :].lstrip(HEADER_SEPARATORS).strip()
    return candidate, rest


def _looks_like_identifier(candidate: str) -> bool:
    """¿Ese trozo de encabezado pretende ser un identificador?

    Lo pretende si arranca como el molde («R-…») o si mezcla dígitos con guiones
    o subrayados —«RCHK_014»—. Un título de verdad, «Stock reservation on
    payment confirmation», no cumple ninguna de las dos, y por eso no se le
    acusa de traer un ID mal escrito.
    """
    if not candidate:
        return False
    return bool(ID_PREFIX_RE.match(candidate) or ID_SHAPE_RE.match(candidate))


def _declared_confidence(requirement: Requirement) -> str | None:
    """El nivel de confianza si está bien escrito; `None` si no lo está.

    Sólo cuentan los tres literales en minúsculas del contrato §5. Un valor con
    la caja cambiada —«LOW»— o inventado no es un nivel: lo denuncia `V09` y,
    para el resto de reglas, es como si el requisito no declarase confianza.
    """
    value = _meta(requirement, "confidence")
    return value if value in CONFIDENCE_LEVELS else None


def _collapse(text: str) -> str:
    """Colapsa la narrativa en una sola línea de espacios simples."""
    return WHITESPACE_RE.sub(" ", text or "").strip()


@dataclass(frozen=True)
class EarsAnalysis:
    """Cómo encaja una narrativa en los patrones EARS."""

    pattern: str | None
    keywords: tuple[str, ...]
    problem: str | None
    detail: str


def analyse_ears(narrative: str) -> EarsAnalysis:
    """Clasifica la narrativa en un patrón EARS y detecta la ambigüedad.

    La narrativa se colapsa en una línea y se parte en cláusulas por sus signos
    de puntuación. De cada cláusula interesa la primera palabra si viene en
    mayúsculas: son ésas las que abren un patrón.

    * ninguna palabra clave → ubicuo
    * `WHEN` → event-driven · `WHILE` → state-driven · `WHERE` → optional-feature
    * `IF … THEN …` → unwanted-behaviour · `WHILE … WHEN …` → complejo

    Falla en dos casos y sólo en dos: cuando aparece más de una palabra clave de
    arranque sin formar el patrón complejo —dos comportamientos disfrazados de
    uno—, y cuando una palabra clave **que sostiene el patrón** abre una cláusula
    que no dice nada. La distinción importa: una palabra clave que no abre la
    narrativa es prosa, el patrón sigue siendo ubicuo y una cláusula corta detrás
    de ella no deja «a medias» ningún patrón. Denunciarla era emitir un error
    contra una narrativa correcta.
    """
    text = _collapse(narrative)
    if not text:
        return EarsAnalysis(None, (), "empty", "")

    spans = _clause_spans(text)
    starts: list[tuple[str, int, str]] = []
    for index, (start, end) in enumerate(spans):
        fragment = text[start:end].strip()
        match = CLAUSE_KEYWORD_RE.match(fragment)
        if match is None:
            continue
        keyword = match.group(1)
        if keyword not in EARS_START_KEYWORDS:
            continue
        # Los dos puntos pegados a la palabra clave son puntuación, no
        # contenido: «WHEN: el cliente confirma…» dice tanto como «WHEN el
        # cliente confirma…», así que no cuentan para decidir si la cláusula
        # está vacía.
        rest = fragment[match.end() :].lstrip(" \t:").strip()
        starts.append((keyword, index, rest))

    keywords = tuple(keyword for keyword, _index, _rest in starts)

    # `bearing` son las palabras clave que de verdad sostienen el patrón. Sólo
    # de ésas puede decirse que dejan el patrón a medias.
    bearing: list[tuple[str, int, str]]
    if len(keywords) > 1:
        if keywords == ("WHILE", "WHEN") and starts[0][1] == 0:
            pattern: str | None = EARS_PATTERNS[keywords]
            bearing = starts
        else:
            return EarsAnalysis(None, keywords, "ambiguous", "")
    elif len(keywords) == 1 and starts[0][1] == 0:
        pattern = EARS_PATTERNS[(keywords[0],)]
        bearing = starts
    else:
        # Ninguna palabra clave, o una que no abre la narrativa: la frase es
        # ubicua y la palabra, prosa. El patrón ubicuo no tiene cláusula que
        # pueda quedarse vacía.
        pattern = EARS_UBIQUITOUS
        bearing = []

    for keyword, _index, rest in bearing:
        if not rest:
            return EarsAnalysis(pattern, keywords, "empty_clause", keyword)

    return EarsAnalysis(pattern, keywords, None, "")


def _clause_spans(text: str) -> list[tuple[int, int]]:
    """Posiciones de cada cláusula de la narrativa, ya colapsada en una línea."""
    spans: list[tuple[int, int]] = []
    start = 0
    for boundary in CLAUSE_BOUNDARY_RE.finditer(text):
        if boundary.start() > start:
            spans.append((start, boundary.start()))
        start = boundary.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def _is_declaration(requirement: Requirement) -> bool:
    """¿El requisito declara comportamiento nuevo, o cita uno que ya existe?"""
    return requirement.block in DECLARING_BLOCKS


#: Por qué un requisito estrena comportamiento. Cada motivo tiene su redacción:
#: llamar «nuevo» a lo que el delta declara como baja es describir al revés.
NOVELTY_ADDED = "added"
NOVELTY_CAPABILITY = "capability"


def _novelty(ctx: Context, requirement: Requirement) -> str | None:
    """Por qué el requisito estrena comportamiento, o `None` si no lo estrena.

    Dos motivos, y el orden importa:

    * `NOVELTY_ADDED` — el delta lo escribe bajo `## ADDED Requirements`. Es el
      caso claro y **no depende de qué haya vivo en disco**: el delta lo declara
      nuevo y con eso basta. Que dependiera era lo que dejaba la regla muda.
    * `NOVELTY_CAPABILITY` — el requisito vive en una capability de la que no
      hay ni un requisito vivo en disco, así que la inaugura.

    Un `MODIFIED`, un `REMOVED` o un `RENAMED` no estrenan nada: citan un ID que
    ya vivía. Preguntarles por su procedencia —y encima llamarlos «nuevos»—
    describía como alta lo que el delta declara como baja.

    Cuidado con la segunda vía: en la ubicación canónica el `spec.md` que se
    valida **es** la evidencia viva de su propia capability, así que una
    capability recién creada allí no se distingue de una de siempre. Su novedad
    la declara el bloque `ADDED` de su delta, que es la primera vía.
    """
    if requirement.block == "ADDED":
        return NOVELTY_ADDED
    if requirement.block in REFERENCING_BLOCKS:
        return None
    owner = ctx.owners.get(requirement.source_file, "")
    if ctx.live_by_capability.get(owner):
        return None
    return NOVELTY_CAPABILITY


# ---------------------------------------------------------------------------
# Las dieciséis reglas
# ---------------------------------------------------------------------------


def _missing_identifier_texts(requirement: Requirement) -> tuple[str, str]:
    """Mensaje y pista para un encabezado al que el parser no le lee ningún ID.

    Son dos problemas distintos y cada uno tiene su remedio:

    * el encabezado no trae **nada** que parezca un identificador —sólo título—;
    * el encabezado trae uno, pero mal escrito o sin separar del título.

    Confundirlos tenía dos consecuencias, y las dos mentían. El mensaje decía
    «no declara identificador» de un encabezado que sí lo declaraba, y la pista
    interpolaba el encabezado entero detrás del ID de ejemplo de la
    documentación —«### R-CHK-014 · r-chk-014 · Stock reservation…»—: markdown
    roto que, copiado tal cual, borraba el ID real de quien escribía.
    """
    candidate, rest = _header_parts(requirement)
    raw = (requirement.raw_header or "").strip() or f"### {requirement.title}".strip()

    if not _looks_like_identifier(candidate):
        # No hay ID a la vista: el remedio es escribir uno, y el título del
        # ejemplo es el encabezado entero, que aquí es sólo título.
        title = (requirement.title or "").strip() or "Título del requisito"
        return (
            f"El requisito {requirement.label} no declara identificador en su "
            "encabezado.",
            f"Escribe el encabezado como «### R-CHK-014 · {title}»: el ID delante "
            "del separador «·».",
        )

    # Hay algo que pretende ser un ID. Se conserva tal cual —sólo se sube de caja
    # si con eso ya cumple el molde—, porque el identificador es del proyecto,
    # no de la documentación.
    upper = candidate.upper()
    if REQUIREMENT_ID_RE.match(candidate):
        suggested, well_formed = candidate, True
    elif REQUIREMENT_ID_RE.match(upper):
        suggested, well_formed = upper, True
    else:
        suggested, well_formed = candidate, False

    title = rest or "Título del requisito"
    hint = (
        f"Escribe el encabezado como «### {suggested} · {title}»: el "
        "identificador, el separador «·» y el título."
    )
    if not well_formed:
        hint = (
            f"{hint} Y renombra «{candidate}» al molde «R-XXX-000» —R, de dos a "
            "cuatro letras mayúsculas y tres dígitos, como «R-CHK-014»—, que "
            "tampoco lo cumple."
        )

    if suggested == candidate and well_formed:
        # El ID está bien escrito: lo que falta es el separador.
        if rest:
            message = (
                f"El encabezado «{raw}» trae «{candidate}» pero no lo separa del "
                "título: sin «·» delante del título, el requisito se queda sin "
                "identificador."
            )
        else:
            message = (
                f"El encabezado «{raw}» trae «{candidate}» y nada más: sin «·» y "
                "un título detrás, el parser no lo lee como identificador."
            )
    else:
        message = (
            f"El encabezado «{raw}» empieza por «{candidate}», que se parece a un "
            "identificador pero no está escrito como tal: el molde es «R-XXX-000», "
            "en mayúsculas y separado del título por «·»."
        )
    return message, hint


def rule_v01(ctx: Context) -> list[Finding]:
    """V01 · El ID está, tiene la forma «R-XXX-000» y es único en el ámbito."""
    findings: list[Finding] = []
    declared: dict[str, Requirement] = {}

    for requirement in ctx.all_requirements:
        if not requirement.id:
            message, hint = _missing_identifier_texts(requirement)
            findings.append(
                Finding(
                    rule="V01",
                    severity=SEVERITY_ERROR,
                    message=message,
                    file=requirement.source_file,
                    line=requirement.line,
                    hint=hint,
                )
            )
            continue

        if not REQUIREMENT_ID_RE.match(requirement.id):
            findings.append(
                Finding(
                    rule="V01",
                    severity=SEVERITY_ERROR,
                    message=(
                        f"El identificador «{requirement.id}» no tiene la forma "
                        "«R-XXX-000»: R, de dos a cuatro letras mayúsculas y tres dígitos."
                    ),
                    file=requirement.source_file,
                    line=requirement.line,
                    requirement_id=requirement.id,
                    hint=(
                        "Renómbralo a algo como «R-CHK-014»: la abreviatura de la "
                        "capability en mayúsculas y un número de tres cifras."
                    ),
                )
            )
            continue

        if not _is_declaration(requirement):
            # Un MODIFIED, REMOVED o RENAMED repite a propósito un ID vivo.
            continue

        previous = declared.get(requirement.id)
        if previous is None and requirement.block == "ADDED":
            previous = ctx.live_requirements.get(requirement.id)

        if previous is not None and previous is not requirement:
            where = previous.source_file or "otro fichero"
            if previous.line:
                where = f"{where}:{previous.line}"
            findings.append(
                Finding(
                    rule="V01",
                    severity=SEVERITY_ERROR,
                    message=(
                        f"El identificador «{requirement.id}» ya está declarado en "
                        f"«{where}»: dos requisitos no pueden compartir ID."
                    ),
                    file=requirement.source_file,
                    line=requirement.line,
                    requirement_id=requirement.id,
                    hint=(
                        "Renumera el requisito nuevo (por ejemplo «R-CHK-015») y deja "
                        "intacto el que ya vivía; si lo que querías era cambiarlo, "
                        "muévelo al bloque «## MODIFIED Requirements»."
                    ),
                )
            )
            continue

        declared[requirement.id] = requirement

    return findings


def rule_v02(ctx: Context) -> list[Finding]:
    """V02 · La narrativa encaja en exactamente un patrón EARS."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        analysis = analyse_ears(requirement.narrative)
        if analysis.problem is None or analysis.problem == "empty":
            # La narrativa vacía la denuncia V03; aquí no se repite.
            continue

        if analysis.problem == "ambiguous":
            listed = ", ".join(f"«{keyword}»" for keyword in analysis.keywords)
            message = (
                f"La narrativa de {requirement.label} abre {len(analysis.keywords)} "
                f"cláusulas EARS ({listed}): no encaja en un solo patrón."
            )
            hint = (
                "Parte el requisito en uno por comportamiento, o deja una sola "
                "cláusula de arranque: «WHEN …» (event-driven), «WHILE …» "
                "(state-driven), «WHERE …» (optional-feature), «IF … THEN …» "
                "(unwanted-behaviour) o ninguna (ubicuo). La única combinación "
                "admitida es «WHILE … WHEN …» (complejo)."
            )
        else:
            message = (
                f"La cláusula «{analysis.detail}» de {requirement.label} está vacía: "
                f"el patrón EARS «{analysis.pattern}» queda a medias."
            )
            hint = (
                f"Completa la cláusula: «{analysis.detail} <la condición>, el sistema "
                "DEBE <la respuesta observable>»."
            )

        findings.append(
            Finding(
                rule="V02",
                severity=SEVERITY_ERROR,
                message=message,
                file=requirement.source_file,
                line=requirement.line,
                requirement_id=requirement.id,
                hint=hint,
            )
        )
    return findings


def rule_v03(ctx: Context) -> list[Finding]:
    """V03 · Hay narrativa antes del primer escenario."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        if requirement.narrative.strip():
            continue
        findings.append(
            Finding(
                rule="V03",
                severity=SEVERITY_ERROR,
                message=(
                    f"El requisito {requirement.label} no tiene narrativa: entre el "
                    "encabezado y lo que sigue no dice qué debe hacer el sistema."
                ),
                file=requirement.source_file,
                line=requirement.line,
                requirement_id=requirement.id,
                hint=(
                    "Escribe la frase EARS justo debajo del encabezado, por ejemplo "
                    "«WHEN el cliente confirma el pago, el sistema DEBE reservar el "
                    "stock durante 15 minutos»."
                ),
            )
        )
    return findings


def rule_v04(ctx: Context) -> list[Finding]:
    """V04 · Cada requisito trae al menos un escenario."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        if requirement.scenarios:
            continue
        findings.append(
            Finding(
                rule="V04",
                severity=SEVERITY_ERROR,
                message=(
                    f"El requisito {requirement.label} no declara ningún escenario: "
                    "nadie sabe qué observar para darlo por cumplido."
                ),
                file=requirement.source_file,
                line=requirement.line,
                requirement_id=requirement.id,
                hint=(
                    "Añade al menos un «#### Scenario: …» con sus dos viñetas: "
                    "«- **WHEN** …» y «- **THEN** …»."
                ),
            )
        )
    return findings


def rule_v05(ctx: Context) -> list[Finding]:
    """V05 · Cada escenario declara «**WHEN**» y «**THEN**»."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        for scenario in requirement.scenarios:
            missing = [keyword for keyword in ("WHEN", "THEN") if not scenario.has(keyword)]
            if not missing:
                continue
            listed = " ni ".join(f"«**{keyword}**»" for keyword in missing)
            findings.append(
                Finding(
                    rule="V05",
                    severity=SEVERITY_ERROR,
                    message=(
                        f"El escenario «{scenario.title}» de {requirement.label} no "
                        f"declara {listed}."
                    ),
                    file=requirement.source_file,
                    line=scenario.line,
                    requirement_id=requirement.id,
                    hint=(
                        "Completa el escenario con "
                        + " y ".join(f"«- **{keyword}** …»" for keyword in missing)
                        + ": la condición y el efecto observable son obligatorios."
                    ),
                )
            )
    return findings


def rule_v06(ctx: Context) -> list[Finding]:
    """V06 · El requisito declara su oráculo. Es el corazón del sistema."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        value = _meta(requirement, "verifies")
        if value:
            continue

        example = f"test/{_capability_hint(requirement)}/<caso>.spec.ts"
        covers = f"@covers {_example_id(requirement)}"
        hint = (
            f"Añade al final del requisito la línea «verifies: {example}» —la ruta del "
            f"test que falla cuando el sistema deja de cumplirlo— y marca ese test con "
            f"el comentario «{covers}»."
        )

        if value is None:
            message = (
                f"El requisito {requirement.label} no declara «verifies:»: sin oráculo "
                "no es verificable, y un requisito que nada puede desmentir es una "
                "opinión, no un contrato."
            )
        else:
            message = (
                f"El «verifies:» de {requirement.label} está vacío: promete un oráculo "
                "y no dice cuál, así que el requisito sigue sin ser verificable."
            )

        findings.append(
            Finding(
                rule="V06",
                severity=SEVERITY_ERROR,
                message=message,
                file=requirement.source_file,
                line=_meta_line(requirement, "verifies"),
                requirement_id=requirement.id,
                hint=hint,
            )
        )
    return findings


def rule_v07(ctx: Context) -> list[Finding]:
    """V07 · El fichero del oráculo existe en disco."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        for written in _verifies_paths(requirement):
            if ctx.is_file(written):
                continue

            if ctx.is_dir(written):
                # Existe, pero no es un fichero. Decir «no existe» mandaría a
                # crear lo que ya está y escondería el error de verdad: la ruta
                # se quedó a mitad de camino.
                message = (
                    f"El oráculo de {requirement.label} apunta a «{written}», que es "
                    f"un directorio, no un fichero: encontrado en "
                    f"«{ctx.resolve(written)}»."
                )
                hint = (
                    f"Apunta «verifies:» al fichero de test concreto que hay dentro "
                    f"de «{written}» y márcalo con «@covers {_example_id(requirement)}»; "
                    "un directorio no puede desmentir un requisito."
                )
            else:
                message = (
                    f"El oráculo de {requirement.label} apunta a «{written}», que no "
                    f"existe: buscado en «{ctx.resolve(written)}»."
                )
                hint = (
                    f"Crea ese test y márcalo con «@covers {_example_id(requirement)}», "
                    "o corrige la ruta de «verifies:» si está mal escrita. Que el test "
                    "todavía no exista no es un fallo del validador: es el orden "
                    "correcto, primero el oráculo y luego el código."
                )

            findings.append(
                Finding(
                    rule="V07",
                    severity=SEVERITY_ERROR,
                    message=message,
                    file=requirement.source_file,
                    line=_meta_line(requirement, "verifies"),
                    requirement_id=requirement.id,
                    hint=hint,
                )
            )
    return findings


def rule_v08(ctx: Context) -> list[Finding]:
    """V08 · El fichero del oráculo contiene «@covers <ID>». El vínculo es doble.

    Aquí se relaya además el `P01` del parser: un oráculo que existe y no se deja
    leer —binario, latin-1, sin permisos— no es un oráculo sin «@covers», es un
    oráculo ilegible. Acusarlo de lo primero mandaba escribir una línea que ya
    estaba escrita, y dejaba sin explicar por qué `V16` no ve nada dentro.
    """
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        written_paths = _verifies_paths(requirement)
        existing = [written for written in written_paths if ctx.is_file(written)]

        readable: list[str] = []
        for written in existing:
            _text, failure = ctx.read_with_failure(written)
            if failure is None:
                readable.append(written)
                continue
            findings.append(
                Finding(
                    rule=failure.rule,
                    severity=failure.severity,
                    message=(
                        f"{failure.message} Es el oráculo que «verifies:» declara "
                        f"para {requirement.label} («{written}»), así que nadie puede "
                        "comprobar qué «@covers» trae dentro."
                    ),
                    file=requirement.source_file,
                    line=_meta_line(requirement, "verifies"),
                    requirement_id=requirement.id,
                    hint=(
                        f"Guarda «{written}» como texto UTF-8, o apunta «verifies:» al "
                        "fichero de test de verdad. Mientras no se pueda leer, ni V08 "
                        "puede confirmar el vínculo ni V16 ve los «@covers» que declare."
                    ),
                )
            )

        if not requirement.id:
            # Sin ID no hay «@covers» que buscar; lo denuncia V01.
            continue
        if not readable:
            # Sin fichero legible no hay nada que comprobar: lo dice V06, V07 o
            # el P01 de aquí arriba.
            continue
        if any(
            requirement.id in parser.find_covers(ctx.read(written) or "")
            for written in readable
        ):
            continue

        # Sólo se acusa a los ficheros que de verdad se han podido mirar: de los
        # ilegibles ya se ha dicho lo suyo, y afirmar que «no contienen» algo que
        # nadie ha leído sería inventarse el hallazgo.
        listed = ", ".join(f"«{written}»" for written in readable)
        if len(readable) > 1:
            claim = f"Ninguno de los ficheros de «verifies:» ({listed}) contiene"
        else:
            claim = f"El fichero de «verifies:» ({listed}) no contiene"
        findings.append(
            Finding(
                rule="V08",
                severity=SEVERITY_ERROR,
                message=(
                    f"{claim} «@covers {requirement.id}»: el vínculo entre requisito "
                    "y test sólo va en un sentido."
                ),
                file=requirement.source_file,
                line=_meta_line(requirement, "verifies"),
                requirement_id=requirement.id,
                hint=(
                    f"Añade el comentario «@covers {requirement.id}» dentro de "
                    f"«{readable[0]}»; basta una línea, en el comentario que use ese "
                    "lenguaje."
                ),
            )
        )
    return findings


def rule_v09(ctx: Context) -> list[Finding]:
    """V09 · «confidence:» está y vale exactamente high, medium o low.

    La pertenencia al conjunto del contrato §5 es literal: «LOW» no es «low».
    Admitir cualquier caja dejaría que el mismo requisito se leyera distinto
    según quién lo teclease, y de ese valor cuelgan la caducidad de `V10` y el
    presupuesto de `V11`.
    """
    findings: list[Finding] = []
    admitted = ", ".join(CONFIDENCE_LEVELS)
    lowercase_hint = (
        "Escribe «confidence: high», «medium» o «low», en inglés y en minúsculas. "
        "No hay valor por defecto: la confianza forma parte del requisito."
    )

    for requirement in ctx.all_requirements:
        value = _meta(requirement, "confidence")
        if value in CONFIDENCE_LEVELS:
            continue

        if value is None:
            message = (
                f"El requisito {requirement.label} no declara «confidence:»: no dice "
                "cuánto se confía en lo que afirma."
            )
            hint = lowercase_hint
        elif not value:
            # Declarada y vacía. Decirle «no declara» a quien tiene la línea
            # escrita —y señalarle esa misma línea— es mandarle escribir lo que
            # ya escribió. Es el mismo cuidado que se tiene en V06.
            message = (
                f"El «confidence:» de {requirement.label} está vacío: la línea está "
                "escrita y no dice ningún nivel."
            )
            hint = lowercase_hint
        elif value.lower() in CONFIDENCE_LEVELS:
            # El nivel es de los tres, pero mal escrito. Es un error distinto
            # del valor inventado y se arregla de otra manera: se corrige la
            # caja, no se elige otro nivel.
            expected = value.lower()
            message = (
                f"«confidence: {value}» de {requirement.label} lleva la caja cambiada: "
                f"el nivel se escribe «{expected}», en minúsculas."
            )
            hint = (
                f"Cámbialo por «confidence: {expected}»: los tres niveles se comparan "
                "tal cual. Mientras la caja no coincida el nivel no cuenta como "
                "declarado, así que ni V10 le reclama «revisit:» ni V11 lo cuenta "
                "como apuesta."
            )
        else:
            message = (
                f"«confidence: {value}» no es un valor admitido en {requirement.label}; "
                f"los únicos son {admitted}."
            )
            hint = lowercase_hint

        findings.append(
            Finding(
                rule="V09",
                severity=SEVERITY_ERROR,
                message=message,
                file=requirement.source_file,
                line=_meta_line(requirement, "confidence"),
                requirement_id=requirement.id,
                hint=hint,
            )
        )
    return findings


def rule_v10(ctx: Context) -> list[Finding]:
    """V10 · Una apuesta en «low» declara «revisit:»: el hecho que la resuelve.

    No una fecha. Un requisito en `low` es una decisión que se tomó porque
    había que tomar alguna, y lo que la cierra no es que pase el tiempo: es que
    llegue un dato. «Cuando hayamos procesado los primeros veinte pedidos» dice
    qué habrá que mirar y permite reconocer el momento cuando llega; un día del
    calendario no dice ninguna de las dos cosas, y quien llegue a él tendrá que
    reconstruir de memoria qué se estaba esperando.

    Por eso una fecha ISO en «revisit:» es un error y no un descuido de forma:
    es la respuesta que este campo dejó de admitir, y dejarla pasar la
    reintroduciría por inercia.

    Lo que la regla puede comprobar es que el hecho **esté y diga algo**. Que
    vaya a ocurrir, y cuándo, no lo sabe nadie todavía; que «ya veremos» no es
    un hecho, sí.
    """
    findings: list[Finding] = []

    for requirement in ctx.all_requirements:
        value = _meta(requirement, "revisit")
        line = _meta_line(requirement, "revisit")
        # La **obligación** de traer «revisit:» es sólo de «low»; la **forma**
        # del valor vale para todos. Un requisito en «medium» puede no declarar
        # cómo se resuelve su duda, pero si la declara, la declara bien: una
        # fecha ahí es igual de inútil el día que llegue.
        if _declared_confidence(requirement) != "low" and value is None:
            # Un «LOW» con la caja cambiada no es un nivel válido —lo denuncia
            # V09— y no se le puede reclamar el oráculo de una apuesta que aún
            # no está bien declarada.
            continue

        if value is None:
            message = (
                f"{requirement.label} declara «confidence: low» y no trae «revisit:»: "
                "una apuesta que no dice qué la resuelve no la resuelve nadie."
            )
            hint = (
                f"Añade el hecho que la cierra: «revisit: {REVISIT_EXAMPLE}». No una "
                "fecha: lo que hace falta es saber qué habrá que mirar y poder "
                "reconocer el momento en que ya se puede mirar. Si no lo sabes, es "
                "una pregunta para quien pidió el cambio. Y si ya no hay nada que "
                "resolver, sube la confianza."
            )
        elif not value:
            # La línea está escrita y vacía: no es lo mismo que no traerla, y
            # señalar «no trae» justo en la línea donde pone «revisit:» es
            # contradecir al usuario con su propio fichero delante.
            message = (
                f"El «revisit:» de {requirement.label} está vacío: promete decir qué "
                "resuelve la apuesta y no lo dice."
            )
            hint = (
                f"Escribe el hecho: «revisit: {REVISIT_EXAMPLE}», o sube la confianza "
                "si ya no es una apuesta."
            )
        elif ISO_DATE_RE.match(value):
            message = (
                f"«revisit: {value}» de {requirement.label} es una fecha, y «revisit:» "
                "pide el hecho que resuelve la apuesta, no el día en que caduca."
            )
            hint = (
                "Una fecha no dice qué habrá que mirar cuando llegue, y el día que "
                "llegue nadie sabrá si la apuesta ya se puede cerrar. Escribe el dato "
                f"que la cierra: «revisit: {REVISIT_EXAMPLE}». Si la fecha salía de un "
                "hecho —el fin de una campaña, una migración—, nombra el hecho."
            )
        elif _is_filler_revisit(value):
            message = (
                f"«revisit: {value}» de {requirement.label} no nombra ningún hecho: es "
                "una forma de decir «más adelante», y más adelante no llega nunca."
            )
            hint = (
                "Contesta a qué tendría que pasar para poder cerrar esta apuesta: un "
                "volumen alcanzado, un cliente en producción, una medición hecha. "
                f"Por ejemplo «revisit: {REVISIT_EXAMPLE}». Si de verdad no hay nada "
                "que pueda resolverla, entonces no es una apuesta: es una decisión "
                "tomada, y va en «medium» con su «why:»."
            )
        else:
            continue

        findings.append(
            Finding(
                rule="V10",
                severity=SEVERITY_ERROR,
                message=message,
                file=requirement.source_file,
                line=line,
                requirement_id=requirement.id,
                hint=hint,
            )
        )
    return findings


def _is_filler_revisit(value: str) -> bool:
    """¿El «revisit:» entero es un «ya veremos» en vez de un hecho?"""
    bare = re.sub(
        r"^[*_`\s]+|[*_`\s.,;:…!?]+$",
        "",
        _strip_accents(WHITESPACE_RE.sub(" ", value or "").strip().lower()),
    )
    return bool(bare) and FILLER_REVISIT_RE.match(bare) is not None


def _strip_accents(text: str) -> str:
    """Quita los acentos sin tocar nada más, para comparar «vera» con «verá»."""
    try:
        decomposed = unicodedata.normalize("NFD", text)
    except Exception:  # defensa: normalizar no puede tumbar el validador
        return text
    return "".join(char for char in decomposed if not unicodedata.combining(char))

def rule_v11(ctx: Context) -> list[Finding]:
    """V11 · Presupuesto de incertidumbre: como mucho el 30 % en «low».

    La cuenta la hace `report.uncertainty_budget` y **sólo** ella: es la misma
    función que llena el campo `budget` del JSON y la línea de cierre del informe
    de texto. Que la regla contara por su cuenta permitía que el informe dijera
    «presupuesto excedido» sin ningún V11 que lo respaldase, y que la misma
    salida diera dos números distintos para lo mismo.
    """
    budget = report.uncertainty_budget(ctx.all_requirements)
    if budget["ok"]:
        return []

    percent = f"{budget['ratio'] * 100:.1f}".replace(".", ",")
    limit = f"{report.UNCERTAINTY_LIMIT * 100:.0f}"
    return [
        Finding(
            rule="V11",
            severity=SEVERITY_ERROR,
            message=(
                f"El {percent} % de los requisitos del ámbito declara «confidence: low» "
                f"({budget['low']} de {budget['total']}) y el límite es el {limit} %."
            ),
            hint=(
                "Resuelve las apuestas más caras antes de seguir: investiga y sube a "
                "«medium» las que ya puedas responder. Se baja el número de «low», "
                "nunca el listón."
            ),
        )
    ]


def rule_v12(ctx: Context) -> list[Finding]:
    """V12 · Cada delta declara al menos un bloque de requisitos."""
    names = [f"«## {name} Requirements»" for name in model.BLOCK_NAMES]
    blocks = f"{', '.join(names[:-1])} o {names[-1]}"

    findings: list[Finding] = []
    for delta in ctx.deltas:
        if delta.blocks:
            continue
        findings.append(
            Finding(
                rule="V12",
                severity=SEVERITY_ERROR,
                message=(
                    f"El delta «{delta.path}» no declara ningún bloque de requisitos: "
                    "no se sabe si añade, cambia, retira o renombra comportamiento."
                ),
                file=delta.path,
                hint=(
                    f"Abre al menos un bloque —{blocks}— y coloca debajo los requisitos "
                    "que le correspondan."
                ),
            )
        )
    return findings


def rule_v13(ctx: Context) -> list[Finding]:
    """V13 · Lo que un delta cambia, retira o renombra tiene que existir vivo."""
    if not ctx.live_ids:
        # Sin capabilities vivas en disco no hay base contra la que comparar.
        return []

    findings: list[Finding] = []
    for delta in ctx.deltas:
        for block in REFERENCING_BLOCKS:
            for requirement in delta.blocks.get(block, []):
                if not requirement.id or requirement.id in ctx.live_ids:
                    continue
                findings.append(
                    Finding(
                        rule="V13",
                        severity=SEVERITY_ERROR,
                        message=(
                            f"El bloque {block} de «{delta.path}» toca "
                            f"«{requirement.id}», que no existe en ninguna capability "
                            "viva."
                        ),
                        file=requirement.source_file or delta.path,
                        line=requirement.line,
                        requirement_id=requirement.id,
                        hint=(
                            "Corrige el ID —los vivos están en "
                            f"{VENOXIA_DIR}/{CAPABILITIES_DIR}/*/{SPEC_FILENAME}— o "
                            "mueve el requisito al bloque «## ADDED Requirements» si de "
                            "verdad es comportamiento nuevo."
                        ),
                    )
                )
    return findings


def rule_v14(ctx: Context) -> list[Finding]:
    """V14 · La prosa va en español: sin «SHALL» ni «MUST» en la narrativa."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        found = sorted(set(ENGLISH_MODAL_RE.findall(requirement.narrative or "")))
        if not found:
            continue
        listed = " y ".join(f"«{modal}»" for modal in found)
        # Mismo cuidado que en V08: con dos modales el sujeto va en plural, así
        # que cada rama trae su sintagma completo en vez de un número fijo.
        if len(found) > 1:
            phrase = f"los modales en inglés {listed}"
        else:
            phrase = f"el modal en inglés {listed}"
        findings.append(
            Finding(
                rule="V14",
                severity=SEVERITY_WARNING,
                message=f"La narrativa de {requirement.label} usa {phrase}.",
                file=requirement.source_file,
                line=requirement.line,
                requirement_id=requirement.id,
                hint=(
                    "Escribe el modal en español: «el sistema DEBE …». Las palabras "
                    "clave estructurales (WHEN, WHILE, WHERE, IF, THEN) sí van en inglés."
                ),
            )
        )
    return findings


def rule_v15(ctx: Context) -> list[Finding]:
    """V15 · El comportamiento nuevo dice de dónde viene."""
    findings: list[Finding] = []
    for requirement in ctx.all_requirements:
        if _meta(requirement, "from"):
            continue
        novelty = _novelty(ctx, requirement)
        if novelty is None:
            continue
        if novelty == NOVELTY_ADDED:
            message = (
                f"El requisito nuevo {requirement.label} no declara «from:»: no "
                "queda rastro de qué decisión lo justifica."
            )
        else:
            owner = ctx.owners.get(requirement.source_file, "") or "esa capability"
            message = (
                f"El requisito {requirement.label} inaugura la capability "
                f"«{owner}» y no declara «from:»: no queda rastro de qué decisión "
                "la justifica."
            )
        findings.append(
            Finding(
                rule="V15",
                severity=SEVERITY_WARNING,
                message=message,
                file=requirement.source_file,
                line=requirement.line,
                requirement_id=requirement.id,
                hint=(
                    "Añade «from: prfaq/<documento>.md#<sección>» apuntando al "
                    "documento donde se tomó la decisión."
                ),
            )
        )
    return findings


def rule_v16(ctx: Context) -> list[Finding]:
    """V16 · Un test que cubre un ID inexistente comprueba algo sin especificar."""
    known = ctx.known_ids()
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()

    for requirement in ctx.all_requirements:
        for written in _verifies_paths(requirement):
            if not ctx.is_file(written):
                continue
            text = ctx.read(written)
            if not text:
                # Fichero vacío o ilegible: aquí no se puede ver ningún
                # «@covers». Si es ilegible, V08 ya lo ha dicho relayando el P01
                # del parser, así que esta ceguera queda explicada en el informe.
                continue
            for covered in sorted(parser.find_covers(text)):
                if covered in known:
                    continue
                key = (str(ctx.resolve(written)), covered)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    Finding(
                        rule="V16",
                        severity=SEVERITY_WARNING,
                        message=(
                            f"El test «{written}» declara «@covers {covered}», y ningún "
                            "requisito lleva ese ID: comprueba comportamiento que no "
                            "está especificado."
                        ),
                        file=written,
                        requirement_id=covered,
                        hint=(
                            f"Corrige el ID del «@covers» en «{written}», o especifica "
                            "ese comportamiento con un requisito que lo declare."
                        ),
                    )
                )
    return findings


RULES: list[Rule] = [
    Rule("V01", SEVERITY_ERROR, "El ID está, tiene la forma «R-XXX-000» y es único", rule_v01),
    Rule("V02", SEVERITY_ERROR, "La narrativa encaja en exactamente un patrón EARS", rule_v02),
    Rule("V03", SEVERITY_ERROR, "Hay narrativa antes del primer escenario", rule_v03),
    Rule("V04", SEVERITY_ERROR, "El requisito trae al menos un escenario", rule_v04),
    Rule("V05", SEVERITY_ERROR, "Cada escenario declara «**WHEN**» y «**THEN**»", rule_v05),
    Rule("V06", SEVERITY_ERROR, "El requisito declara su oráculo en «verifies:»", rule_v06),
    Rule("V07", SEVERITY_ERROR, "El fichero del oráculo existe en disco", rule_v07),
    Rule("V08", SEVERITY_ERROR, "El fichero del oráculo contiene «@covers <ID>»", rule_v08),
    Rule("V09", SEVERITY_ERROR, "«confidence:» vale high, medium o low", rule_v09),
    Rule("V10", SEVERITY_ERROR, "Una apuesta en «low» dice qué hecho la resuelve", rule_v10),
    Rule("V11", SEVERITY_ERROR, "Como mucho el 30 % de los requisitos está en «low»", rule_v11),
    Rule("V12", SEVERITY_ERROR, "Cada delta declara al menos un bloque", rule_v12),
    Rule("V13", SEVERITY_ERROR, "Lo que el delta cambia o retira existe vivo", rule_v13),
    Rule("V14", SEVERITY_WARNING, "La narrativa no usa «SHALL» ni «MUST»", rule_v14),
    Rule("V15", SEVERITY_WARNING, "El comportamiento nuevo declara «from:»", rule_v15),
    Rule("V16", SEVERITY_WARNING, "Ningún test cubre un ID inexistente", rule_v16),
]


def run_rules(ctx: Context) -> list[Finding]:
    """Aplica las dieciséis reglas en orden y devuelve todos sus hallazgos.

    Una regla que se cayera no puede tumbar la validación entera: el fallo se
    convierte en un hallazgo con su código y el resto sigue.
    """
    findings: list[Finding] = []
    for rule in RULES:
        try:
            produced = rule.check(ctx) or []
        except Exception as error:  # defensa: el validador siempre da un veredicto
            findings.append(
                Finding(
                    rule=rule.code,
                    severity=SEVERITY_ERROR,
                    message=(
                        f"La regla {rule.code} no se pudo aplicar: "
                        f"{type(error).__name__}: {error}."
                    ),
                    hint=(
                        "Es un fallo de Venoxia, no de la especificación: repórtalo "
                        "indicando el fichero que lo provoca."
                    ),
                )
            )
            continue
        findings.extend(produced)
    return findings


# ---------------------------------------------------------------------------
# Descubrimiento del ámbito
# ---------------------------------------------------------------------------


@dataclass
class Targets:
    """Los ficheros que se van a validar, ya clasificados."""

    capabilities: list[Path] = field(default_factory=list)
    deltas: list[Path] = field(default_factory=list)
    adopted: bool = True
    note: str = ""


def _unique(paths: list[Path]) -> list[Path]:
    """Quita repetidos conservando el orden, comparando por ruta resuelta."""
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _classify(path: Path) -> str:
    """Decide si un fichero markdown suelto es una capability o un delta.

    Manda la ubicación: bajo `capabilities/` es una capability y bajo
    `changes/<id>/delta/` es un delta. Fuera de la estructura conocida decide el
    contenido: si declara un bloque de requisitos, es un delta.
    """
    try:
        parts = [part.lower() for part in path.resolve().parts]
    except OSError:
        parts = [part.lower() for part in path.parts]

    if CAPABILITIES_DIR in parts:
        return "capability"
    if CHANGES_DIR in parts and DELTA_DIR in parts:
        return "delta"

    text, _failure = parser.read_text(path)
    if text:
        for line in text.splitlines():
            if parser.BLOCK_HEADER_RE.match(line):
                return "delta"
    return "capability"


def _markdown_under(directory: Path) -> list[Path]:
    """Todos los markdown de un directorio, en orden estable."""
    return sorted(directory.rglob("*.md"))


def collect_targets(root: Path, paths: list[str], change: str | None) -> Targets:
    """Decide qué ficheros entran en el ámbito de esta validación."""
    if change and paths:
        raise UsageError(
            "no se pueden combinar «--change» y rutas sueltas: «--change» ya acota el "
            "ámbito al change entero."
        )

    if change:
        return _targets_from_change(root, change)
    if paths:
        return _targets_from_paths(root, paths)
    return _targets_from_discovery(root)


def _targets_from_change(root: Path, change: str) -> Targets:
    """Ámbito de un único change: los deltas de `.venoxia/changes/<id>/delta/`."""
    change_dir = root / VENOXIA_DIR / CHANGES_DIR / change
    if not change_dir.is_dir():
        raise UsageError(
            f"no existe el change «{change}»: se buscaba «{change_dir}». Mira los "
            f"disponibles en «{root / VENOXIA_DIR / CHANGES_DIR}»."
        )

    delta_dir = change_dir / DELTA_DIR
    deltas = sorted(delta_dir.glob("*.md")) if delta_dir.is_dir() else []
    note = ""
    if not deltas:
        note = (
            f"el change «{change}» no tiene ningún delta en «{delta_dir}»: no hay "
            "requisitos que validar."
        )
    return Targets(capabilities=[], deltas=deltas, note=note)


def _targets_from_paths(root: Path, paths: list[str]) -> Targets:
    """Ámbito explícito: los ficheros y directorios que ha nombrado quien llama."""
    collected: list[Path] = []
    for raw in paths:
        candidate = Path(os.path.expanduser(raw))
        # Una ruta relativa se busca primero desde donde se invoca el comando y,
        # si allí no hay nada, desde la raíz del proyecto.
        if not candidate.is_absolute() and not candidate.exists():
            candidate = root / candidate
        if candidate.is_dir():
            found = _markdown_under(candidate)
            if not found:
                raise UsageError(f"«{raw}» no contiene ningún fichero markdown.")
            collected.extend(found)
        elif candidate.is_file():
            collected.append(candidate)
        else:
            raise UsageError(
                f"no existe la ruta «{raw}»: no está ni en «{Path.cwd()}» ni en «{root}»."
            )

    targets = Targets()
    for path in _unique(collected):
        if _classify(path) == "delta":
            targets.deltas.append(path)
        else:
            targets.capabilities.append(path)
    return targets


def _targets_from_discovery(root: Path) -> Targets:
    """Ámbito completo: todo lo que hay bajo `.venoxia/`."""
    venoxia_dir = root / VENOXIA_DIR
    if not venoxia_dir.is_dir():
        return Targets(adopted=False)

    capabilities = sorted((venoxia_dir / CAPABILITIES_DIR).glob(f"*/{SPEC_FILENAME}"))

    deltas: list[Path] = []
    changes_dir = venoxia_dir / CHANGES_DIR
    if changes_dir.is_dir():
        for change_dir in sorted(entry for entry in changes_dir.iterdir() if entry.is_dir()):
            delta_dir = change_dir / DELTA_DIR
            if delta_dir.is_dir():
                deltas.extend(sorted(delta_dir.glob("*.md")))

    return Targets(capabilities=capabilities, deltas=deltas)


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------


def _parse_capability_cached(
    path: Path, root: Path, cache: dict[str, tuple[Capability, list[Finding]]]
) -> tuple[Capability, list[Finding]]:
    """Parsea una capability una sola vez, aunque esté viva y además en el ámbito."""
    key = str(Path(path).resolve())
    if key not in cache:
        cache[key] = parser.parse_capability(path, root)
    return cache[key]


def _live_capabilities(
    root: Path, cache: dict[str, tuple[Capability, list[Finding]]]
) -> list[Capability]:
    """Las capabilities vivas del proyecto, la base contra la que compara V13.

    Sus hallazgos de forma no se acumulan aquí: se cuentan cuando la capability
    entra de verdad en el ámbito validado.
    """
    directory = root / VENOXIA_DIR / CAPABILITIES_DIR
    if not directory.is_dir():
        return []
    capabilities: list[Capability] = []
    for spec in sorted(directory.glob(f"*/{SPEC_FILENAME}")):
        capability, _findings = _parse_capability_cached(spec, root, cache)
        capabilities.append(capability)
    return capabilities


def build_context(
    root: Path,
    result: ValidationResult,
    live_capabilities: list[Capability],
) -> Context:
    """Reúne en un solo objeto todo lo que las reglas van a mirar."""
    all_requirements: list[Requirement] = []
    owners: dict[str, str] = {}

    for capability in result.capabilities:
        all_requirements.extend(capability.requirements)
        owners[capability.path] = capability.name
    for delta in result.deltas:
        all_requirements.extend(delta.requirements)
        owners[delta.path] = delta.capability

    live_requirements: dict[str, Requirement] = {}
    live_by_capability: dict[str, set[str]] = {}
    for capability in live_capabilities:
        ids: set[str] = set()
        for requirement in capability.requirements:
            if not requirement.id:
                continue
            ids.add(requirement.id)
            live_requirements.setdefault(requirement.id, requirement)
        live_by_capability[capability.name] = ids

    return Context(
        root=root,
        capabilities=result.capabilities,
        deltas=result.deltas,
        all_requirements=all_requirements,
        live_ids=set(live_requirements),
        live_requirements=live_requirements,
        live_by_capability=live_by_capability,
        owners=owners,
    )


def validate_targets(
    root: str | Path,
    capability_paths: list[Path] | None = None,
    delta_paths: list[Path] | None = None,
    strict: bool = False,
) -> ValidationResult:
    """Valida un ámbito ya resuelto y devuelve el resultado completo."""
    root_path = Path(root).expanduser().resolve()
    result = ValidationResult(strict=strict, root=str(root_path))
    cache: dict[str, tuple[Capability, list[Finding]]] = {}

    live_capabilities = _live_capabilities(root_path, cache)

    for path in capability_paths or []:
        capability, findings = _parse_capability_cached(path, root_path, cache)
        result.capabilities.append(capability)
        for finding in findings:
            result.add(finding)

    for path in delta_paths or []:
        delta, findings = parser.parse_delta(path, root_path)
        result.deltas.append(delta)
        for finding in findings:
            result.add(finding)

    ctx = build_context(root_path, result, live_capabilities)
    for finding in run_rules(ctx):
        result.add(finding)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos."""
    cli = argparse.ArgumentParser(
        prog="validate.py",
        description=(
            "Valida la especificación de Venoxia contra las dieciséis reglas del "
            "contrato. Determinista: ninguna regla consulta a un modelo."
        ),
        epilog=(
            "Códigos de salida: 0 la especificación cumple · 1 no cumple · 2 error de "
            "uso. Un proyecto sin .venoxia/ no es un error: se avisa y se sale con 0."
        ),
    )
    cli.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help=(
            "ficheros .md o directorios que validar; sin ninguno se descubre todo lo "
            "que hay bajo .venoxia/"
        ),
    )
    cli.add_argument(
        "--root",
        metavar="DIR",
        help="raíz del proyecto, la que contiene .venoxia/ (por defecto, el directorio actual)",
    )
    cli.add_argument(
        "--change",
        metavar="ID",
        help="valida sólo los deltas de .venoxia/changes/<ID>/",
    )
    cli.add_argument(
        "--strict",
        action="store_true",
        help="los avisos también hacen fallar",
    )
    cli.add_argument(
        "--json",
        action="store_true",
        help="emite el JSON del esquema estable en vez del informe de texto",
    )
    cli.add_argument("--no-color", action="store_true", help="sin colores ANSI")
    cli.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="sólo el resumen, sin el detalle de cada hallazgo",
    )
    return cli


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
        targets = collect_targets(root, list(args.paths), args.change)
    except UsageError as error:
        print(f"venoxia: {error}", file=sys.stderr)
        return EXIT_USAGE

    if not targets.adopted:
        message = (
            f"venoxia: este proyecto todavía no ha adoptado Venoxia (no existe "
            f"«{root / VENOXIA_DIR}»). No hay especificación que validar."
        )
        if args.json:
            # «adopted» separa las dos cosas que el resto del documento no puede
            # distinguir: un proyecto sin «.venoxia/» produce los mismos ceros que
            # una especificación conforme. Sin esta clave, una verja de CI o el panel
            # de salud leerían «verde» donde no hay nada que validar.
            empty = ValidationResult(strict=args.strict, root=str(root))
            print(report.render_json(empty, extra={"adopted": False}))
            print(message, file=sys.stderr)
        else:
            print(message)
        return EXIT_OK

    if targets.note:
        print(f"venoxia: {targets.note}", file=sys.stderr)

    result = validate_targets(
        root,
        capability_paths=targets.capabilities,
        delta_paths=targets.deltas,
        strict=args.strict,
    )

    if args.json:
        print(report.render_json(result, extra={"adopted": True}))
    elif args.quiet:
        print(report.render_summary(result, no_color=args.no_color))
    else:
        print(report.render_text(result, no_color=args.no_color))

    return EXIT_OK if result.ok else EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
