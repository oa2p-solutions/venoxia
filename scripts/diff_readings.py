#!/usr/bin/env python3
"""Motor de divergencia de Venoxia.

Compara las lecturas independientes que varios lectores aislados han hecho del
mismo delta y decide si convergen. La aritmética del veredicto la hace este
código, nunca un modelo: normaliza, empareja escenario con escenario, compara
campo a campo y convierte cada desacuerdo en una pregunta cerrada con las
lecturas enfrentadas y sus opciones.

Contrato de la salida (§7 del contrato de interfaces):

* Códigos de salida: 0 ni divergencia dura ni laguna · 1 hay divergencia dura o
  laguna declarada · 2 error de uso, lectura ilegible o **ejecución incompleta**
  (menos de dos lectores, o ningún escenario que comparar: no se comparó nada,
  así que no hay convergencia que afirmar).
* Las divergencias blandas por sí solas no hacen fallar salvo con ``--strict``.
* ``converged`` **no** es el código de salida: dice si las lecturas coinciden
  (cero divergencias de cualquier dureza, cero lagunas y una comparación que de
  verdad ocurrió), mientras que el código de salida dice si la ejecución falla.
  Con sólo blandas: ``converged`` falso y salida 0. El detalle, en ``Verdict``.
* Ningún JSON malformado produce una traza de Python: se reporta en español.

**Un solo veredicto para los tres canales.** El markdown, el JSON y el resumen de
``--out`` no calculan nada por su cuenta: los tres reciben el mismo ``Verdict``
—código, ``strict`` y código de salida— y lo escriben en su formato. Cualquier
sitio donde los tres pudieran contar historias distintas del mismo hecho es un
fallo del producto, y la única forma de que no ocurra es que sólo haya una
historia. El JSON extiende el ejemplo de §7 con ``verdict``, ``strict``,
``exit_code`` y ``advocate`` justamente para poder decir por escrito lo que el
markdown dice en prosa.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_THRESHOLD = 0.6
READER_PATTERN = "reader-*.json"
ADVOCATE_FILENAME = "devils-advocate.json"

#: Las dos señales de que un fichero **pretendía** ser una lectura aunque su nombre
#: no sea el canónico. Se comparan siempre en minúsculas: la caja de las letras no
#: puede decidir si algo se mira o no se mira.
READER_PREFIX = "reader-"
JSON_SUFFIX = ".json"

#: Qué se esperaba encontrar detrás de cada nombre, para que el mensaje de error no
#: le atribuya al abogado del diablo el papel de lector ni al revés.
EXPECTED_READER = "el «reader-<nombre>.json» que escribió el lector"
EXPECTED_ADVOCATE = f"el «{ADVOCATE_FILENAME}» que escribió el abogado del diablo"

#: Con menos de dos lecturas no hay nada que cotejar: lo que salga no es una
#: convergencia, es una ejecución incompleta.
MINIMUM_READERS = 2

EXIT_OK = 0
EXIT_DIVERGENCE = 1
EXIT_USAGE = 2

HARDNESS_HARD = "hard"
HARDNESS_SOFT = "soft"

FIELD_MISSING_SCENARIO = "missing_scenario"
FIELD_STATUS_CODE = "status_code"
FIELD_STATUS_CODE_ABSENT = "status_code_absent"
FIELD_SIDE_EFFECTS = "side_effects"
FIELD_EFFECT = "effect"

SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
DEFAULT_SEVERITY = "medium"

# Estado del abogado del diablo. «No hay fichero», «hay fichero y está vacío» y
# «hay fichero y no se pudo leer» son tres cosas distintas, y confundir las dos
# últimas hace que el informe afirme que no encontró nada cuando lo cierto es
# que no se sabe qué encontró.
ADVOCATE_ABSENT = "absent"
ADVOCATE_EMPTY = "empty"
ADVOCATE_LISTED = "listed"
ADVOCATE_UNREADABLE = "unreadable"

# Los seis veredictos posibles. Son la **única** fuente del texto del informe,
# del resumen de `--out`, del color y del código de salida: si los tres canales
# leen del mismo código, no pueden contradecirse.
VERDICT_ERRORS = "errors"
VERDICT_TOO_FEW_READERS = "too_few_readers"
VERDICT_DIVERGED = "diverged"
VERDICT_SOFT_ONLY = "soft_only"
VERDICT_NO_SCENARIOS = "no_scenarios"
VERDICT_CONVERGED = "converged"

#: Titular de cada veredicto: lo escriben igual el markdown y el resumen.
VERDICT_HEADLINES = {
    VERDICT_ERRORS: "Lectura incompleta",
    VERDICT_TOO_FEW_READERS: "Lectura sin contraste",
    VERDICT_DIVERGED: "Las lecturas no convergen",
    VERDICT_SOFT_ONLY: "Las lecturas casi convergen",
    VERDICT_NO_SCENARIOS: "Sin escenarios que comparar",
    VERDICT_CONVERGED: "Las lecturas convergen",
}

#: Opciones de reserva de una pregunta cerrada. Nunca deberían hacer falta: son
#: la red por si dos opciones se renderizaran iguales y la pregunta se quedara
#: sin respuesta posible.
FALLBACK_OPTIONS = (
    "Las dos lecturas dicen lo mismo una vez normalizadas: no hay divergencia real",
    "El delta no lo dice, hay que escribirlo antes de implementar nada",
)

# Frases canónicas de los códigos HTTP más frecuentes: hacen que la opción de
# la pregunta se lea sola («409 Conflict») en vez de obligar a recordar el número.
HTTP_REASONS = {
    "200": "OK",
    "201": "Created",
    "202": "Accepted",
    "204": "No Content",
    "301": "Moved Permanently",
    "302": "Found",
    "303": "See Other",
    "304": "Not Modified",
    "307": "Temporary Redirect",
    "308": "Permanent Redirect",
    "400": "Bad Request",
    "401": "Unauthorized",
    "402": "Payment Required",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "406": "Not Acceptable",
    "408": "Request Timeout",
    "409": "Conflict",
    "410": "Gone",
    "412": "Precondition Failed",
    "413": "Content Too Large",
    "415": "Unsupported Media Type",
    "418": "I'm a teapot",
    "422": "Unprocessable Entity",
    "423": "Locked",
    "424": "Failed Dependency",
    "425": "Too Early",
    "428": "Precondition Required",
    "429": "Too Many Requests",
    "500": "Internal Server Error",
    "501": "Not Implemented",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
    "504": "Gateway Timeout",
}

ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"

TRUTHY = {"true", "yes", "si", "1"}
NULLISH = {"null", "none", "nil", "n a", "na", "ninguno", "ninguna", "sin codigo"}


# ---------------------------------------------------------------------------
# Normalización y similitud
# ---------------------------------------------------------------------------


def normalize(s: object) -> str:
    """Devuelve el texto en minúsculas, sin acentos, sin puntuación y con los espacios colapsados."""
    if s is None:
        return ""
    text = s if isinstance(s, str) else str(s)
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    # La puntuación, los símbolos, los controles y el guion bajo pasan a ser
    # separadores: «409/422» y «409 422» deben normalizarse igual.
    cleaned = "".join(
        " " if ch == "_" or unicodedata.category(ch)[0] in {"P", "S", "C"} else ch
        for ch in without_marks
    )
    return " ".join(cleaned.lower().split())


def tokens(s: object) -> set[str]:
    """Conjunto de tokens normalizados de un texto."""
    return set(normalize(s).split())


def jaccard(left: set[str], right: set[str]) -> float:
    """Índice de Jaccard entre dos conjuntos de tokens; dos vacíos son idénticos."""
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def similarity(left: object, right: object) -> float:
    """Similitud de tokens entre dos textos, en el rango [0.0, 1.0]."""
    return jaccard(tokens(left), tokens(right))


# ---------------------------------------------------------------------------
# Presentación en español
# ---------------------------------------------------------------------------


def join_es(items: list[str], conjunction: str = "y") -> str:
    """Enumera en español: «a», «a y b», «a, b y c»."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"


def option_letter(index: int) -> str:
    """Letra de la opción número «index» (0 → A, 25 → Z, 26 → AA)."""
    letters = ""
    position = index + 1
    while position > 0:
        position, remainder = divmod(position - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def reader_label(name: str) -> str:
    """Etiqueta corta de un lector: «reader-a» → «A», «reader-implementer» → «implementer»."""
    label = name[len("reader-"):] if name.startswith("reader-") else name
    label = label.strip() or name
    return label.upper() if len(label) <= 3 else label


def labels_of(names: list[str]) -> list[str]:
    """Etiquetas de una lista de lectores, en el mismo orden."""
    return [reader_label(name) for name in names]


def who(names: list[str]) -> str:
    """«El lector A» o «Los lectores A y C», según cuántos sean."""
    prefix = "Los lectores" if len(names) > 1 else "El lector"
    return f"{prefix} {join_es(labels_of(names))}"


def lower_first(text: str) -> str:
    """Pasa a minúscula la primera letra, para encadenar cláusulas con punto y coma."""
    return text[:1].lower() + text[1:] if text else text


def count_es(number: int, singular: str, plural: str) -> str:
    """Concuerda el sustantivo con el número: «1 divergencia dura», «2 divergencias duras»."""
    return f"{number} {singular if number == 1 else plural}"


def quote_list(items: list[str]) -> str:
    """Enumera elementos entrecomillados a la española."""
    return join_es([f"«{item}»" for item in items])


def describe_status(value: str | None) -> str:
    """Texto de la opción para un código de estado, con su frase canónica si la conocemos."""
    if value is None:
        return "Ninguno, el escenario no devuelve código de estado"
    reason = HTTP_REASONS.get(normalize(value))
    return f"{value} {reason}" if reason else str(value)


def status_key(value: object) -> object:
    """Clave de equivalencia de un código de estado: «409» y «409 Conflict» son la misma respuesta.

    El criterio, que es el que decide si hay divergencia dura o no la hay:

    * Un lector que escribe **«409»** y otro que escribe **«409 Conflict»** están
      diciendo lo mismo. Lo que la pregunta cerrada compara es el código, y la
      frase canónica es la que este mismo módulo le añadiría al imprimirlo
      (`describe_status`). Tratarlos como dos respuestas producía una pregunta con
      las dos opciones idénticas —«(A) 409 Conflict» y «(B) 409 Conflict»— bajo un
      titular que afirmaba que no pueden ser las dos correctas a la vez. Se
      unifican, y entonces no hay divergencia que preguntar.
    * Con **cualquier otro texto detrás del número** («409 Gone», «409 porque el
      stock ya está reservado») la clave se queda con el texto entero y las
      lecturas siguen enfrentadas. Unificar por el número a secas callaría un
      desacuerdo que puede ser real, y este módulo existe para no callar ninguno.
    """
    if value is None:
        return None
    text = normalize(value)
    if not text:
        return None
    parts = text.split()
    reason = HTTP_REASONS.get(parts[0])
    if reason is not None:
        rest = " ".join(parts[1:])
        if not rest or rest == normalize(reason):
            return parts[0]
    return text


def distinct_options(options: list[str]) -> list[str]:
    """Opciones de una pregunta cerrada, sin repetidas y nunca menos de dos.

    Una pregunta cerrada con dos opciones iguales es peor que no preguntar: quien
    la lee no tiene forma de contestarla y el informe, encima, afirma que las
    lecturas no pueden ser todas correctas. La red vive aquí y no en cada
    comparador porque debe cubrir **cualquier** pregunta, venga de donde venga.
    """
    seen: set[str] = set()
    result: list[str] = []
    for option in options:
        if option in seen:
            continue
        seen.add(option)
        result.append(option)
    for fallback in FALLBACK_OPTIONS:
        if len(result) >= 2:
            break
        if fallback not in seen:
            seen.add(fallback)
            result.append(fallback)
    return result


def describe_side_effects(items: list[str]) -> str:
    """Texto de la opción para un conjunto de efectos colaterales."""
    if not items:
        return "Ninguno, el escenario no produce efectos observables"
    return quote_list(items)


def describe_effect(text: str) -> str:
    """Texto de la opción para la descripción del efecto."""
    return f"«{text}»" if text else "Sin descripción del efecto"


# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------


@dataclass
class Reading:
    """Lectura de un escenario concreto por parte de un lector."""

    scenario: str
    effect: str
    status_code: str | None
    side_effects: list[str]
    unclear: bool
    unclear_why: str | None


@dataclass
class ReaderFile:
    """Fichero «reader-*.json» ya interpretado."""

    name: str
    path: Path
    readings: list[Reading]


@dataclass
class Divergence:
    """Desacuerdo entre lecturas, con la pregunta cerrada que lo resuelve."""

    scenario: str
    field: str
    hardness: str
    readings: dict[str, object]
    question: str
    options: list[str]
    detail: str = ""

    def __post_init__(self) -> None:
        # Ninguna pregunta sale con dos opciones iguales, la construya quien la construya.
        self.options = distinct_options(list(self.options))

    def to_dict(self) -> dict:
        """Proyección al esquema JSON estable del contrato."""
        return {
            "scenario": self.scenario,
            "field": self.field,
            "hardness": self.hardness,
            "readings": self.readings,
            "question": self.question,
            "options": list(self.options),
        }


@dataclass
class Gap:
    """Laguna declarada por un lector con «unclear: true»."""

    scenario: str
    reader: str
    why: str

    def to_dict(self) -> dict:
        return {"scenario": self.scenario, "reader": self.reader, "why": self.why}


@dataclass
class GapQuestion:
    """Pregunta cerrada derivada de una o varias lagunas sobre el mismo escenario."""

    scenario: str
    detail: str
    question: str
    options: list[str]

    def __post_init__(self) -> None:
        # La misma red que en `Divergence`: la laguna también se cierra preguntando.
        self.options = distinct_options(list(self.options))


@dataclass
class ScenarioGroup:
    """Un escenario y las lecturas que cada lector hizo de él."""

    key: str
    title: str
    by_reader: dict[str, Reading]


@dataclass
class Analysis:
    """Resultado completo de la comparación, listo para renderizar."""

    directory: Path
    threshold: float
    reader_names: list[str]
    scenarios: list[ScenarioGroup]
    divergences: list[Divergence]
    gaps: list[Gap]
    gap_questions: list[GapQuestion]
    attacks: list[dict]
    advocate_status: str
    errors: list[str]

    @property
    def hard(self) -> list[Divergence]:
        return [d for d in self.divergences if d.hardness == HARDNESS_HARD]

    @property
    def soft(self) -> list[Divergence]:
        return [d for d in self.divergences if d.hardness == HARDNESS_SOFT]

    @property
    def advocate_present(self) -> bool:
        """¿Había un «devils-advocate.json» en el directorio? (Legible o no.)"""
        return self.advocate_status != ADVOCATE_ABSENT

    @property
    def contrasted(self) -> bool:
        """¿Se ha cotejado de verdad algo? Dos lecturas legibles como mínimo.

        Con un solo lector nadie contrastó nada: ni se pueden detectar divergencias
        —todos los comparadores necesitan dos votantes— ni se puede llamar
        «escenario que converge» a un escenario que una sola persona leyó.
        """
        return not self.errors and len(self.reader_names) >= MINIMUM_READERS

    @property
    def verdict_code(self) -> str:
        """El veredicto, en un código estable. Es lo único que deciden los datos.

        El orden de precedencia dice qué es lo más grave de esta ejecución:

        1. `errors`: hay ficheros que no se pudieron interpretar, la comparación
           está incompleta y no se afirma nada.
        2. `too_few_readers`: menos de dos lectores. Un despacho que perdió un
           lector no es una convergencia, es una ejecución incompleta, y lo es
           **independientemente** de lo que declarase el que sí llegó. Por eso va
           por delante de las lagunas: la laguna se sigue imprimiendo debajo, pero
           el titular no puede ser otro.
        3. `diverged`: hay divergencia dura o laguna declarada.
        4. `soft_only`: sólo desacuerdos blandos.
        5. `no_scenarios`: nadie trajo ningún escenario, así que no se comparó nada.
        6. `converged`: dos lecturas o más, escenarios que cotejar y ni un desacuerdo.
        """
        if self.errors:
            return VERDICT_ERRORS
        if len(self.reader_names) < MINIMUM_READERS:
            return VERDICT_TOO_FEW_READERS
        if self.hard or self.gaps:
            return VERDICT_DIVERGED
        if self.soft:
            return VERDICT_SOFT_ONLY
        if not self.scenarios:
            return VERDICT_NO_SCENARIOS
        return VERDICT_CONVERGED

    @property
    def converged(self) -> bool:
        """¿Coinciden las lecturas? Sólo el veredicto `converged` lo afirma.

        `converged` y el código de salida contestan **dos preguntas distintas** y no
        pueden fundirse en un solo booleano:

        * `converged` describe las lecturas: ¿leyeron lo mismo dos lectores o más?
        * `Verdict.exit_code` describe la ejecución: ¿debe fallar el comando? El §7
          del contrato lo fija en las duras, las lagunas y, con `--strict`, las
          blandas.

        Un caso con una sola divergencia blanda tiene `converged` a falso —hay
        desacuerdo y el informe lo imprime— y sale con 0, porque una blanda sola no
        tumba la ejecución. Derivar el booleano del código de salida hacía que el
        veredicto afirmase la convergencia tres líneas antes de listar el desacuerdo.

        Y `converged` tampoco es cierto **por vacuidad**: con errores de lectura, con
        un solo lector o sin ningún escenario no se comparó nada, y de no comparar
        nada no sale una convergencia. Ésos son veredictos propios, no éste.
        """
        return self.verdict_code == VERDICT_CONVERGED

    @property
    def divergent_keys(self) -> set[str]:
        """Claves normalizadas de los escenarios con algún desacuerdo o laguna."""
        titles = {normalize(d.scenario) for d in self.divergences}
        titles |= {normalize(g.scenario) for g in self.gaps}
        return titles

    def counts(self) -> dict:
        return {
            "hard": len(self.hard),
            "soft": len(self.soft),
            "gaps": len(self.gaps),
            "scenarios": len(self.scenarios),
            "readers": len(self.reader_names),
        }


@dataclass
class Verdict:
    """El veredicto de una ejecución concreta, que es lo que leen los tres canales.

    Existe para que el markdown, el JSON y el resumen de `--out` no puedan
    contarse historias distintas: se calcula una vez, con `strict` incluido, y los
    tres lo escriben en su formato. `strict` forma parte del veredicto porque
    cambia el resultado de **esta** invocación, y un informe que dijera «con
    `--strict`, sí» estaría contando lo que pasaría en otra.
    """

    code: str
    strict: bool
    exit_code: int

    @property
    def headline(self) -> str:
        """El titular que escriben igual el informe y el resumen."""
        return VERDICT_HEADLINES[self.code]

    @property
    def converged(self) -> bool:
        return self.code == VERDICT_CONVERGED

    @property
    def marker(self) -> str:
        """✓ convergen · ⚠ hay desacuerdo pero la ejecución no falla · ✗ la ejecución falla."""
        if self.converged:
            return "✓"
        return "⚠" if self.exit_code == EXIT_OK else "✗"


def exit_code_for(code: str, strict: bool) -> int:
    """Código de salida de cada veredicto. La tabla entera, en un solo sitio.

    `errors`, `too_few_readers` y `no_scenarios` salen con 2 —el código que §7
    reserva a la ejecución que no produjo un veredicto utilizable— y no con 1: un
    1 diría «las lecturas se contradicen», que es falso; lo que ocurre es que no
    se comparó nada. Con 2, además, el caso de un solo lector queda pegado al de
    cero lectores, que ya salía con 2, y ninguna de las dos ejecuciones puede
    confundirse con una convergencia.
    """
    if code in (VERDICT_ERRORS, VERDICT_TOO_FEW_READERS, VERDICT_NO_SCENARIOS):
        return EXIT_USAGE
    if code == VERDICT_DIVERGED:
        return EXIT_DIVERGENCE
    if code == VERDICT_SOFT_ONLY:
        return EXIT_DIVERGENCE if strict else EXIT_OK
    return EXIT_OK


def build_verdict(analysis: Analysis, strict: bool) -> Verdict:
    """El veredicto de esta ejecución: código, modo estricto y código de salida."""
    code = analysis.verdict_code
    return Verdict(code=code, strict=strict, exit_code=exit_code_for(code, strict))


# ---------------------------------------------------------------------------
# Carga de las lecturas
# ---------------------------------------------------------------------------


def read_json(path: Path) -> tuple[object, str | None]:
    """Lee un JSON del disco y devuelve (dato, None) o (None, error legible en español)."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, f"«{path.name}» no está en UTF-8; el lector debe escribir su JSON en UTF-8."
    except OSError as exc:
        reason = exc.strerror or exc.__class__.__name__
        return None, f"No se pudo leer «{path.name}»: {reason}."
    if not text.strip():
        # Un fichero vacío es la forma más silenciosa de estar: el JSON diría
        # «Expecting value en la línea 1», que suena a JSON roto cuando lo que pasa
        # es que el lector no llegó a escribir nada.
        return None, (
            f"«{path.name}» está vacío: el lector no llegó a escribir nada. "
            "Vuelve a despacharlo; debe devolver un array JSON con una lectura por escenario."
        )
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, (
            f"«{path.name}» no es JSON válido: {exc.msg} (línea {exc.lineno}, columna {exc.colno}). "
            "El lector debe devolver un array JSON y nada más, sin preámbulo y sin vallas de markdown."
        )


def coerce_status_code(value: object) -> str | None:
    """Convierte el código de estado a texto, o a None si el lector no dio ninguno."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        text = str(int(value)) if float(value).is_integer() else str(value)
    else:
        text = str(value)
    text = text.strip()
    if not text or normalize(text) in NULLISH:
        return None
    return text


def coerce_side_effects(value: object) -> list[str]:
    """Normaliza el campo «side_effects» a una lista de textos no vacíos."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple)):
        items = []
        for item in value:
            text = item.strip() if isinstance(item, str) else str(item).strip()
            if text:
                items.append(text)
        return items
    text = str(value).strip()
    return [text] if text else []


def coerce_flag(value: object) -> bool:
    """Interpreta «unclear» de forma tolerante: booleano, número o texto."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return normalize(value) in TRUTHY
    return False


def coerce_text(value: object) -> str:
    """Convierte un campo textual opcional a texto limpio."""
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def parse_reading(entry: object, path: Path, position: int) -> tuple[Reading | None, str | None]:
    """Interpreta un objeto de lectura; devuelve (Reading, None) o (None, error)."""
    if not isinstance(entry, dict):
        return None, (
            f"«{path.name}»: el elemento nº {position} no es un objeto JSON. "
            "Cada elemento del array debe ser un objeto con «scenario», «effect», «status_code», "
            "«side_effects», «unclear» y «unclear_why»."
        )
    scenario = entry.get("scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        return None, (
            f"«{path.name}»: el elemento nº {position} no trae un «scenario» con el título literal del "
            "escenario; sin él no se puede emparejar con las demás lecturas."
        )
    unclear_why = coerce_text(entry.get("unclear_why")) or None
    reading = Reading(
        scenario=scenario.strip(),
        effect=coerce_text(entry.get("effect")),
        status_code=coerce_status_code(entry.get("status_code")),
        side_effects=coerce_side_effects(entry.get("side_effects")),
        unclear=coerce_flag(entry.get("unclear")),
        unclear_why=unclear_why,
    )
    return reading, None


def extract_entries(raw: object, path: Path) -> tuple[list, str | None]:
    """Acepta un array, el envoltorio {"readings": [...]} o un objeto suelto."""
    if isinstance(raw, list):
        return raw, None
    if isinstance(raw, dict):
        if "readings" in raw:
            inner = raw["readings"]
            if isinstance(inner, list):
                return inner, None
            return [], f"«{path.name}»: la clave «readings» debe contener un array de lecturas."
        if "scenario" in raw:
            return [raw], None
        return [], (
            f"«{path.name}»: se esperaba un array de lecturas y llegó un objeto sin «readings» ni «scenario»."
        )
    return [], f"«{path.name}»: se esperaba un array JSON de lecturas y llegó {type(raw).__name__}."


def load_reader_file(path: Path) -> tuple[ReaderFile | None, list[str]]:
    """Carga un «reader-*.json» completo; los problemas vuelven como errores en español."""
    raw, error = read_json(path)
    if error is not None:
        return None, [error]
    entries, error = extract_entries(raw, path)
    if error is not None:
        return None, [error]

    errors: list[str] = []
    readings: list[Reading] = []
    seen: dict[str, str] = {}
    for position, entry in enumerate(entries, start=1):
        reading, entry_error = parse_reading(entry, path, position)
        if entry_error is not None:
            errors.append(entry_error)
            continue
        assert reading is not None
        key = normalize(reading.scenario)
        if key in seen:
            errors.append(
                f"«{path.name}»: el escenario «{reading.scenario}» aparece dos veces "
                f"(la primera como «{seen[key]}»); cada escenario debe leerse una sola vez."
            )
            continue
        seen[key] = reading.scenario
        readings.append(reading)

    if errors:
        return None, errors
    return ReaderFile(name=path.stem, path=path, readings=readings), []


def load_attacks(path: Path) -> tuple[list[dict], list[str]]:
    """Carga «devils-advocate.json»; un array vacío es una respuesta legítima."""
    raw, error = read_json(path)
    if error is not None:
        return [], [error]
    if isinstance(raw, dict):
        entries = raw.get("attacks") if isinstance(raw.get("attacks"), list) else [raw]
    elif isinstance(raw, list):
        entries = raw
    else:
        return [], [f"«{path.name}»: se esperaba un objeto o un array de ataques."]

    attacks: list[dict] = []
    errors: list[str] = []
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"«{path.name}»: el elemento nº {position} no es un objeto JSON.")
            continue
        attack = coerce_text(entry.get("attack"))
        if not attack:
            errors.append(
                f"«{path.name}»: el elemento nº {position} no describe ningún ataque en la clave «attack»."
            )
            continue
        # Una «severity» que no es high, medium ni low se sigue tratando como
        # «medium» —el JSON del contrato sólo admite esas tres, y romper el
        # informe entero por una palabra sería desproporcionado cuando el ataque
        # en sí está intacto—, pero **se dice**: imprimirla degradada sin más era
        # atribuirle a la fuente algo que la fuente no dijo. Un ataque sin texto,
        # en cambio, sí es un error de lectura: ahí no queda nada que reportar.
        declared = coerce_text(entry.get("severity"))
        severity = normalize(declared) or DEFAULT_SEVERITY
        record: dict = {
            "attack": attack,
            "requirement_id": coerce_text(entry.get("requirement_id")) or None,
            "severity": severity if severity in SEVERITY_RANK else DEFAULT_SEVERITY,
        }
        if severity not in SEVERITY_RANK:
            record["severity_declared"] = declared
        attacks.append(record)
    if errors:
        return [], errors
    attacks.sort(key=lambda item: SEVERITY_RANK[item["severity"]])
    return attacks, []


def looks_like_reading(name: str) -> bool:
    """¿Este nombre pretendía ser una lectura, aunque no esté escrito como toca?

    El criterio es ancho a propósito y **no mira la caja de las letras**: cuenta todo
    lo que empieza por «reader-» y todo lo que acaba en «.json», en mayúsculas o en
    minúsculas. Entran `reader-c.JSON`, `readerb.json`, `notes.json`, `Reader-C.Json`
    y `reader-a.json.bak`; se quedan fuera `notas.md` y los directorios de trabajo
    que no llevan ninguna de las dos señales.

    Dejar fuera a un candidato lo devuelve al silencio, que es exactamente el fallo
    que este módulo existe para no cometer; meter a uno de más sólo cuesta una
    pregunta al usuario. Por eso la red se tiende del lado ancho.
    """
    lowered = name.lower()
    return lowered.startswith(READER_PREFIX) or lowered.endswith(JSON_SUFFIX)


def unusable_reason(path: Path, directory: Path, expected: str = EXPECTED_READER) -> str | None:
    """Por qué esta ruta no se puede abrir como lectura, o `None` si sí se puede.

    Son las formas de «está ahí y nadie la mira» que no llegan a ser un error de
    JSON, y ninguna se descarta en silencio:

    * **El enlace simbólico colgante.** Lo deja una copia parcial, un `rsync`
      interrumpido o un checkout con enlaces. A diferencia de un directorio, éste
      aparece justo cuando alguien creía estar poniendo ahí un fichero.
    * **Lo que no resuelve a un fichero regular:** un directorio llamado
      `reader-c.json`, un FIFO, un socket, un dispositivo. Se leen mal, se cuelgan o
      no se leen, y las tres cosas son peores calladas.

    Un fichero regular sin permiso de lectura **no** sale por aquí: sale al abrirlo,
    en `read_json`, que ya lo cuenta con el motivo del sistema operativo.
    """
    if path.is_symlink() and not path.exists():
        try:
            target = str(path.readlink())
        except OSError:
            target = ""
        destination = f" a «{target}»" if target else ""
        return (
            f"«{path.name}» es un enlace simbólico roto: apunta{destination}, que no existe, "
            f"así que no hay nada detrás del nombre y nadie lo ha leído. Restaura el destino del "
            f"enlace o escribe ahí {expected}."
        )
    if not path.is_file():
        kind = "un directorio" if path.is_dir() else "algo que no es un fichero regular"
        return (
            f"«{path.name}» está en el directorio de lecturas pero es {kind}, así que nadie lo ha "
            f"leído. Sácalo de «{directory.name}/» y deja ahí {expected}."
        )
    return None


def misnamed_reason(path: Path, directory: Path) -> str:
    """Por qué este fichero, que parecía una lectura, no cuenta como tal.

    El patrón `reader-*.json` se compara **respetando la caja**, así que se separan
    dos errores que se arreglan de forma distinta: el que sólo falla en las
    mayúsculas —`reader-c.JSON`— y el que falla en el nombre entero —`readerb.json`,
    la errata de un guion—. Al primero se le dice el nombre exacto al que renombrar.
    """
    if fnmatch.fnmatchcase(path.name.lower(), READER_PATTERN):
        return (
            f"«{path.name}» sólo se diferencia de «{READER_PATTERN}» en la caja de las letras, y "
            f"el patrón distingue mayúsculas: nadie lo ha leído. Renómbralo a "
            f"«{path.name.lower()}» para que cuente como lectura."
        )
    return (
        f"«{path.name}» está en el directorio de lecturas pero no encaja en el patrón "
        f"«{READER_PATTERN}» ni es «{ADVOCATE_FILENAME}», así que nadie lo ha leído. "
        f"Renómbralo a «reader-<nombre>.json» o sácalo de «{directory.name}/»."
    )


def load_readings_dir(directory: Path) -> tuple[list[ReaderFile], list[dict], str, list[str]]:
    """Carga todas las lecturas del directorio; devuelve lectores, ataques, estado del abogado y errores.

    Lo que hace, exactamente —y el docstring dice sólo esto porque una promesa que
    el código no cumple convierte un hueco en una trampa—:

    * Se enumera **todo** el contenido del directorio, no lo que encaje en un
      patrón. La enumeración es la única fuente: hasta el abogado del diablo sale de
      aquí, para que no haya dos versiones de qué hay en la carpeta.
    * Se lee como lectura lo que se llama exactamente `reader-*.json` (`fnmatchcase`,
      con la extensión en minúsculas) **y** resuelve a un fichero regular con JSON
      dentro.
    * Todo lo demás que `looks_like_reading` reconoce como candidato —otra caja de
      letras, un guion de menos, un enlace roto, un directorio con nombre de
      fichero— vuelve como **error de lectura**, con su nombre y con qué hacer. De
      ahí sale el veredicto `errors` y el código 2.
    * Lo que no parece una lectura (`notas.md`, un `__pycache__`) se ignora sin ruido.

    Un fichero que alguien puso ahí y que nadie lee es una trampa, no una comodidad:
    un solo lector descartado en silencio deja al informe afirmando que las lecturas
    convergen, que es la única cosa que este componente no se puede permitir decir
    en falso.
    """
    errors: list[str] = []
    readers: list[ReaderFile] = []
    advocate_path: Path | None = None

    try:
        entries = sorted(directory.iterdir())
    except OSError as exc:
        reason = exc.strerror or exc.__class__.__name__
        return (
            [],
            [],
            ADVOCATE_ABSENT,
            [
                f"No se pudo listar el directorio de lecturas «{directory}»: {reason}. "
                "Sin poder enumerarlo no se sabe qué lecturas hay, así que no se compara nada."
            ],
        )

    for path in entries:
        if path.name == ADVOCATE_FILENAME:
            advocate_path = path
            continue
        if not looks_like_reading(path.name):
            continue
        # El orden importa: primero si la ruta se puede abrir, y sólo después si el
        # nombre es el canónico. Al revés, a un directorio «reader-viejo/» se le
        # pediría renombrarlo a «reader-<nombre>.json», que no es lo que le pasa.
        reason = unusable_reason(path, directory)
        if reason is not None:
            errors.append(reason)
            continue
        if not fnmatch.fnmatchcase(path.name, READER_PATTERN):
            errors.append(misnamed_reason(path, directory))
            continue
        reader, file_errors = load_reader_file(path)
        if reader is not None:
            readers.append(reader)
        errors.extend(file_errors)

    attacks: list[dict] = []
    advocate_status = ADVOCATE_ABSENT
    if advocate_path is not None:
        # El abogado también puede «estar y no mirarse»: un enlace colgante con su
        # nombre dejaba el informe sin sección ninguna, como si nadie lo hubiera
        # despachado. Está, no se pudo leer, y eso es lo que se dice.
        reason = unusable_reason(advocate_path, directory, EXPECTED_ADVOCATE)
        if reason is not None:
            errors.append(reason)
            advocate_status = ADVOCATE_UNREADABLE
        else:
            attacks, advocate_errors = load_attacks(advocate_path)
            errors.extend(advocate_errors)
            if advocate_errors:
                advocate_status = ADVOCATE_UNREADABLE
            elif attacks:
                advocate_status = ADVOCATE_LISTED
            else:
                advocate_status = ADVOCATE_EMPTY
    return readers, attacks, advocate_status, errors


# ---------------------------------------------------------------------------
# Aritmética de la divergencia
# ---------------------------------------------------------------------------


def index_scenarios(readers: list[ReaderFile]) -> list[ScenarioGroup]:
    """Empareja los escenarios de todos los lectores por su título normalizado."""
    groups: dict[str, ScenarioGroup] = {}
    for reader in readers:
        for reading in reader.readings:
            key = normalize(reading.scenario)
            group = groups.get(key)
            if group is None:
                group = ScenarioGroup(key=key, title=reading.scenario, by_reader={})
                groups[key] = group
            group.by_reader[reader.name] = reading
    return list(groups.values())


def group_readings(values: dict[str, object], key_of) -> list[tuple[object, list[str]]]:
    """Agrupa lectores por el valor equivalente que dieron, conservando el orden de aparición."""
    order: list[object] = []
    buckets: dict[object, list[str]] = {}
    display: dict[object, object] = {}
    for name, value in values.items():
        key = key_of(value)
        if key not in buckets:
            buckets[key] = []
            display[key] = value
            order.append(key)
        buckets[key].append(name)
    return [(display[key], buckets[key]) for key in order]


def voters(group: ScenarioGroup, reader_names: list[str], is_empty) -> list[str]:
    """Lectores cuyo valor cuenta en un campo.

    Al lector que declaró «unclear: true» y dejó ese campo vacío no se le cuenta el
    hueco como desacuerdo: su laguna ya se reporta aparte y contarla dos veces sólo
    añade ruido al informe.
    """
    voting: list[str] = []
    for name in reader_names:
        reading = group.by_reader.get(name)
        if reading is None:
            continue
        if reading.unclear and is_empty(reading):
            continue
        voting.append(name)
    return voting


def compare_missing(group: ScenarioGroup, reader_names: list[str]) -> Divergence | None:
    """Un escenario que unos lectores ven y otros no es una divergencia dura."""
    present = [name for name in reader_names if name in group.by_reader]
    absent = [name for name in reader_names if name not in group.by_reader]
    if not absent or not present:
        return None

    effects = {name: group.by_reader[name].effect for name in present}
    options: list[str] = []
    for effect, names in group_readings(effects, normalize):
        text = str(effect)
        if text:
            options.append(f"Sí, y su efecto es «{text}» (lectura de {join_es(labels_of(names))})")
        else:
            options.append(f"Sí, tal como lo lee {join_es(labels_of(names))}")
    options.append("No, el delta no describe ese escenario y sobra en las lecturas que lo traen")

    readings: dict[str, object] = {}
    for name in reader_names:
        reading = group.by_reader.get(name)
        readings[name] = reading.effect if reading is not None else None

    detail = (
        f"{who(present)} lee este escenario en el delta; "
        f"{lower_first(who(absent))} no lo encuentra."
    )
    return Divergence(
        scenario=group.title,
        field=FIELD_MISSING_SCENARIO,
        hardness=HARDNESS_HARD,
        readings=readings,
        question=f"¿Forma parte «{group.title}» de este delta?",
        options=options,
        detail=detail,
    )


def compare_status_code(group: ScenarioGroup, reader_names: list[str]) -> Divergence | None:
    """Compara el código de estado; distinto o ausente en unos y no en otros es divergencia dura."""
    present = voters(group, reader_names, lambda reading: reading.status_code is None)
    if len(present) < 2:
        return None
    codes: dict[str, object] = {name: group.by_reader[name].status_code for name in present}
    # `status_key` decide qué es «la misma respuesta»: «409» y «409 Conflict» lo son.
    buckets = group_readings(codes, status_key)
    if len(buckets) < 2:
        return None

    has_absent = any(value is None for value, _ in buckets)
    clauses: list[str] = []
    options: list[str] = []
    for value, names in buckets:
        code = value if value is None else str(value)
        if code is None:
            clauses.append(f"{who(names)} no da ningún código")
        else:
            clauses.append(f"{who(names)} responde **{code}**")
        options.append(describe_status(code))
    detail = "; ".join([clauses[0]] + [lower_first(clause) for clause in clauses[1:]]) + "."

    return Divergence(
        scenario=group.title,
        field=FIELD_STATUS_CODE_ABSENT if has_absent else FIELD_STATUS_CODE,
        hardness=HARDNESS_HARD,
        readings={name: codes[name] for name in present},
        question=f"¿Qué código de estado debe devolver el sistema en «{group.title}»?",
        options=options,
        detail=detail,
    )


def compare_side_effects(group: ScenarioGroup, reader_names: list[str]) -> Divergence | None:
    """Compara el conjunto de efectos colaterales; cualquier diferencia de conjunto es dura."""
    present = voters(group, reader_names, lambda reading: not reading.side_effects)
    if len(present) < 2:
        return None
    effects: dict[str, object] = {name: group.by_reader[name].side_effects for name in present}

    def key_of(items: object) -> tuple:
        return tuple(sorted({normalize(item) for item in items if normalize(item)}))

    buckets = group_readings(effects, key_of)
    if len(buckets) < 2:
        return None

    # Los efectos que no aparecen en todas las lecturas son los que están en discusión.
    normalized_sets = [set(key_of(items)) for items, _ in buckets]
    shared = set.intersection(*normalized_sets) if normalized_sets else set()
    contested_display: dict[str, str] = {}
    for items, _ in buckets:
        for item in items:
            key = normalize(item)
            if key and key not in shared and key not in contested_display:
                contested_display[key] = item

    clauses: list[str] = []
    options: list[str] = []
    for items, names in buckets:
        listed = list(items)
        if listed:
            clauses.append(f"{who(names)} registra {quote_list(listed)}")
        else:
            clauses.append(f"{who(names)} no registra ningún efecto")
        options.append(describe_side_effects(listed))
    detail = "; ".join([clauses[0]] + [lower_first(clause) for clause in clauses[1:]]) + "."
    if shared and contested_display:
        detail += f" En discusión: {quote_list(list(contested_display.values()))}."

    return Divergence(
        scenario=group.title,
        field=FIELD_SIDE_EFFECTS,
        hardness=HARDNESS_HARD,
        readings={name: list(group.by_reader[name].side_effects) for name in present},
        question=f"¿Qué efectos observables debe producir «{group.title}»?",
        options=options,
        detail=detail,
    )


def compare_effect(group: ScenarioGroup, reader_names: list[str], threshold: float) -> Divergence | None:
    """Compara la descripción del efecto por similitud de tokens; bajo el umbral es divergencia blanda."""
    present = voters(group, reader_names, lambda reading: not reading.effect)
    if len(present) < 2:
        return None
    texts: dict[str, object] = {name: group.by_reader[name].effect for name in present}
    buckets = group_readings(texts, normalize)
    if len(buckets) < 2:
        return None

    token_sets = {name: tokens(text) for name, text in texts.items()}
    worst = 1.0
    for index, left in enumerate(present):
        for right in present[index + 1:]:
            worst = min(worst, jaccard(token_sets[left], token_sets[right]))
    if worst >= threshold:
        return None

    clauses: list[str] = []
    options: list[str] = []
    for text, names in buckets:
        rendered = str(text)
        if rendered:
            clauses.append(f"{who(names)} describe el efecto como «{rendered}»")
        else:
            clauses.append(f"{who(names)} no describe ningún efecto")
        options.append(describe_effect(rendered))
    same = "Ambas lecturas describen" if len(buckets) == 2 else "Todas las lecturas describen"
    options.append(f"{same} lo mismo con otras palabras, no hay divergencia real")

    detail = "; ".join([clauses[0]] + [lower_first(clause) for clause in clauses[1:]]) + "."
    detail += f" Similitud de tokens {worst:.2f}, por debajo del umbral {threshold:.2f}."

    return Divergence(
        scenario=group.title,
        field=FIELD_EFFECT,
        hardness=HARDNESS_SOFT,
        readings={name: group.by_reader[name].effect for name in present},
        question=f"¿Cuál de estas lecturas del efecto de «{group.title}» es la correcta?",
        options=options,
        detail=detail,
    )


def collect_gaps(group: ScenarioGroup, reader_names: list[str]) -> tuple[list[Gap], GapQuestion | None]:
    """Recoge las lagunas declaradas del escenario y arma la pregunta cerrada que las cierra."""
    flagged = [name for name in reader_names if name in group.by_reader and group.by_reader[name].unclear]
    if not flagged:
        return [], None

    gaps = [
        Gap(
            scenario=group.title,
            reader=name,
            why=group.by_reader[name].unclear_why or "el lector declaró la laguna sin explicarla",
        )
        for name in flagged
    ]

    clauses = []
    for gap in gaps:
        clauses.append(f"{who([gap.reader])} declara que el texto no lo resuelve: «{gap.why}»")
    detail = "; ".join([clauses[0]] + [lower_first(clause) for clause in clauses[1:]]) + "."

    present = [name for name in reader_names if name in group.by_reader]
    texts: dict[str, object] = {
        name: group.by_reader[name].effect for name in present if group.by_reader[name].effect
    }
    options: list[str] = []
    if texts:
        for text, names in group_readings(texts, normalize):
            options.append(f"«{text}» (lectura de {join_es(labels_of(names))})")
        options.append("Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre")
    else:
        options.append("El delta ya lo dice y la duda es infundada, hay que señalar dónde lo dice")
        options.append("El delta no lo dice, hay que escribirlo antes de implementar nada")

    question = GapQuestion(
        scenario=group.title,
        detail=detail,
        question=f"¿Qué debe ocurrir en «{group.title}»?",
        options=options,
    )
    return gaps, question


def analyse(
    directory: Path,
    readers: list[ReaderFile],
    attacks: list[dict],
    advocate_status: str,
    threshold: float,
    errors: list[str],
) -> Analysis:
    """Ejecuta toda la comparación y devuelve el análisis listo para renderizar."""
    reader_names = [reader.name for reader in readers]
    scenarios = index_scenarios(readers)

    divergences: list[Divergence] = []
    gaps: list[Gap] = []
    gap_questions: list[GapQuestion] = []
    for group in scenarios:
        for candidate in (
            compare_missing(group, reader_names),
            compare_status_code(group, reader_names),
            compare_side_effects(group, reader_names),
            compare_effect(group, reader_names, threshold),
        ):
            if candidate is not None:
                divergences.append(candidate)
        scenario_gaps, gap_question = collect_gaps(group, reader_names)
        gaps.extend(scenario_gaps)
        if gap_question is not None:
            gap_questions.append(gap_question)

    return Analysis(
        directory=directory,
        threshold=threshold,
        reader_names=reader_names,
        scenarios=scenarios,
        divergences=divergences,
        gaps=gaps,
        gap_questions=gap_questions,
        attacks=attacks,
        advocate_status=advocate_status,
        errors=list(errors),
    )


def decide_exit_code(analysis: Analysis, strict: bool) -> int:
    """Código de salida de un análisis. Lo decide el veredicto, y sólo el veredicto.

    Ojo: esto **no** es `analysis.converged`. Un caso con sólo divergencias blandas
    sale con 0 y aun así no converge; el porqué está en `Analysis.converged`.
    """
    return build_verdict(analysis, strict).exit_code


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------


def build_payload(analysis: Analysis, verdict: Verdict) -> dict:
    """Construye el JSON estable versión 1 del contrato.

    Sobre el ejemplo de §7 añade cuatro claves, todas para que el canal máquina
    pueda decir lo mismo que el canal prosa: `verdict` (cuál de los seis
    veredictos), `strict` (el modo de **esta** invocación), `exit_code` (el código
    con el que sale el proceso, calculado por la misma función que lo devuelve) y
    `advocate` (si el abogado del diablo faltaba, estaba vacío o no se pudo leer).
    """
    payload: dict = {
        "version": SCHEMA_VERSION,
        "converged": verdict.converged,
        "verdict": verdict.code,
        "strict": verdict.strict,
        "exit_code": verdict.exit_code,
        "counts": analysis.counts(),
        "divergences": [divergence.to_dict() for divergence in analysis.divergences],
        "gaps": [gap.to_dict() for gap in analysis.gaps],
        "attacks": [dict(attack) for attack in analysis.attacks],
        "advocate": analysis.advocate_status,
    }
    if analysis.errors:
        payload["errors"] = list(analysis.errors)
    return payload


def render_question(scenario: str, detail: str, question: str, options: list[str]) -> list[str]:
    """Bloque markdown de una pregunta cerrada."""
    lines = [f"### Escenario: {scenario}", ""]
    if detail:
        lines.extend([detail, ""])
    lines.append(f"**{question}**")
    lines.extend(f"- ({option_letter(index)}) {option}" for index, option in enumerate(options))
    lines.append("")
    return lines


def verdict_sentence(analysis: Analysis, verdict: Verdict) -> str:
    """Frase de veredicto, sin color. Empieza por el titular del veredicto y acaba por el código de salida.

    Todas las frases cierran con lo que ha pasado **en esta invocación**, nunca con
    lo que pasaría en otra: un informe que dijera «con `--strict`, sí» obliga a
    quien lo lee a averiguar por su cuenta si esta ejecución llevaba `--strict`.
    """
    counts = analysis.counts()
    scenarios = "el único escenario" if counts["scenarios"] == 1 else f"los {counts['scenarios']} escenarios"
    readers = "el único lector" if counts["readers"] == 1 else f"los {counts['readers']} lectores"
    headline = f"**{verdict.headline}.**"

    if verdict.code == VERDICT_ERRORS:
        body = (
            f"{count_es(len(analysis.errors), 'problema', 'problemas')} al interpretar los ficheros "
            "de `readings/`: el veredicto no es concluyente hasta que se corrijan."
        )
    elif verdict.code == VERDICT_TOO_FEW_READERS:
        body = (
            f"Sólo hay {count_es(counts['readers'], 'lectura legible', 'lecturas legibles')}, y con "
            f"menos de {MINIMUM_READERS} no hay nada que cotejar: no se puede afirmar que las lecturas "
            "convergen porque no se ha comparado ninguna con ninguna. Despacha al menos dos lectores "
            "con consignas distintas y vuelve a ejecutar."
        )
    elif verdict.code == VERDICT_DIVERGED:
        body = (
            f"{count_es(counts['hard'], 'divergencia dura', 'divergencias duras')}, "
            f"{count_es(counts['soft'], 'blanda', 'blandas')} y "
            f"{count_es(counts['gaps'], 'laguna declarada', 'lagunas declaradas')} sobre {scenarios}."
        )
    elif verdict.code == VERDICT_SOFT_ONLY:
        body = (
            f"{count_es(counts['soft'], 'divergencia blanda', 'divergencias blandas')} sobre "
            f"{scenarios}: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de "
            "implementar."
        )
        body += (
            " Esta ejecución lleva `--strict`, así que las blandas también la tumban."
            if verdict.strict
            else " Las blandas por sí solas no hacen fallar la ejecución."
        )
    elif verdict.code == VERDICT_NO_SCENARIOS:
        body = (
            f"{readers.capitalize()} no traen ningún escenario: no se ha comparado nada, así que aquí "
            "no hay convergencia que afirmar."
        )
    else:
        body = f"No hay desacuerdo en {scenarios} entre {readers}."

    return f"{headline} {body} Esta ejecución sale con código {verdict.exit_code}."


def paint(text: str, color: str, enabled: bool) -> str:
    """Envuelve el texto en color ANSI si está habilitado."""
    return f"{color}{text}{ANSI_RESET}" if enabled else text


def verdict_color(verdict: Verdict) -> str:
    """Verde si convergen, amarillo si hay desacuerdo que no tumba, rojo si la ejecución falla.

    Se deriva del mismo marcador que usa el resumen, así que el color y el símbolo
    no pueden discrepar: con `--strict` y sólo blandas la ejecución falla, y por eso
    ese caso ya no se pinta de amarillo.
    """
    if verdict.marker == "✓":
        return ANSI_GREEN
    return ANSI_YELLOW if verdict.marker == "⚠" else ANSI_RED


def summary_line(analysis: Analysis, verdict: Verdict, color: bool = False) -> str:
    """Resumen de una línea para cuando el informe va a un fichero.

    Lleva el mismo titular que el informe, más los hechos que decidieron el
    veredicto: los recuentos, si iba `--strict` y el código de salida.
    """
    counts = analysis.counts()
    parts = [f"{verdict.marker} {verdict.headline}"]
    if analysis.errors:
        parts.append(count_es(len(analysis.errors), "problema de lectura", "problemas de lectura"))
    if counts["hard"] or counts["soft"] or counts["gaps"]:
        parts.append(
            f"{count_es(counts['hard'], 'dura', 'duras')}, "
            f"{count_es(counts['soft'], 'blanda', 'blandas')}, "
            f"{count_es(counts['gaps'], 'laguna', 'lagunas')}"
        )
    parts.append(count_es(counts["scenarios"], "escenario", "escenarios"))
    parts.append(count_es(counts["readers"], "lector", "lectores"))
    if verdict.strict:
        parts.append("`--strict`")
    parts.append(f"salida {verdict.exit_code}")
    return paint(" · ".join(parts), verdict_color(verdict), color)


def render_markdown(analysis: Analysis, verdict: Verdict, color: bool = False) -> str:
    """Informe markdown completo: el producto real de esta herramienta."""
    counts = analysis.counts()
    readers = ", ".join(f"`{name}`" for name in analysis.reader_names) or "ninguno"
    lines: list[str] = [
        "# Informe de divergencia",
        "",
        f"- **Lecturas:** `{analysis.directory}`",
        f"- **Lectores:** {counts['readers']} ({readers})",
        f"- **Escenarios comparados:** {counts['scenarios']}",
        f"- **Umbral de similitud de `effect`:** {analysis.threshold:.2f}",
        f"- **Modo estricto (`--strict`):** {'sí' if verdict.strict else 'no'}",
        f"- **Código de salida:** {verdict.exit_code}",
        "",
        "## Veredicto",
        "",
        paint(verdict_sentence(analysis, verdict), verdict_color(verdict), color),
        "",
    ]

    if analysis.errors:
        lines.extend(["## Errores de lectura", ""])
        lines.extend(f"- {error}" for error in analysis.errors)
        lines.extend(
            [
                "",
                "Corrige o vuelve a despachar los lectores afectados y ejecuta de nuevo la divergencia.",
                "",
            ]
        )

    if 0 < counts["readers"] < MINIMUM_READERS:
        lines.extend(
            [
                "> Con un solo lector no hay contraste posible: sólo se detectan las lagunas que él mismo",
                "> declara, y nada de lo que dice queda cotejado con nadie. Despacha al menos dos lectores",
                "> con consignas distintas.",
                "",
            ]
        )

    if analysis.hard:
        lines.extend([f"## Divergencias duras · {len(analysis.hard)}", ""])
        lines.extend(
            [
                "Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su",
                "letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.",
                "",
            ]
        )
        for divergence in analysis.hard:
            lines.extend(
                render_question(
                    divergence.scenario, divergence.detail, divergence.question, divergence.options
                )
            )

    if analysis.soft:
        lines.extend([f"## Divergencias blandas · {len(analysis.soft)}", ""])
        lines.extend(
            [
                "Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.",
                "",
            ]
        )
        for divergence in analysis.soft:
            lines.extend(
                render_question(
                    divergence.scenario, divergence.detail, divergence.question, divergence.options
                )
            )

    if analysis.gap_questions:
        # El «· N» de las cuatro secciones cuenta lo mismo en todas: bloques debajo.
        # Aquí hay un bloque por escenario, aunque las lagunas —una por lector— sean
        # más; el total va en la prosa, que es donde no engaña a nadie.
        lines.extend([f"## Lagunas declaradas · {len(analysis.gap_questions)}", ""])
        declared = count_es(len(analysis.gaps), "laguna declarada", "lagunas declaradas")
        over = count_es(len(analysis.gap_questions), "escenario", "escenarios")
        lines.extend(
            [
                f"{declared} sobre {over}. "
                "Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala",
                "un hueco del delta, no un fallo del lector.",
                "",
            ]
        )
        for gap_question in analysis.gap_questions:
            lines.extend(
                render_question(
                    gap_question.scenario, gap_question.detail, gap_question.question, gap_question.options
                )
            )

    if analysis.advocate_present or analysis.attacks:
        lines.extend([f"## Abogado del diablo · {len(analysis.attacks)}", ""])
        if analysis.attacks:
            lines.extend(
                [
                    "Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.",
                    "",
                ]
            )
            for attack in analysis.attacks:
                target = attack["requirement_id"] or "sin requisito concreto"
                line = f"- **[{attack['severity']}]** {target} — {attack['attack']}"
                declared = attack.get("severity_declared")
                if declared:
                    line += (
                        f" · La fuente declaró la severidad «{declared}», que no es `high`, `medium` "
                        f"ni `low`: se trata como `{attack['severity']}`."
                    )
                lines.append(line)
        elif analysis.advocate_status == ADVOCATE_UNREADABLE:
            # No es lo mismo «no encontró nada» que «no se sabe qué encontró».
            lines.append(
                f"El fichero «{ADVOCATE_FILENAME}» está pero no se ha podido interpretar: **no se sabe "
                "qué encontró el abogado del diablo**. El detalle está en «Errores de lectura», y hasta "
                "que se corrija este informe no dice nada sobre los ataques."
            )
        else:
            lines.append(
                f"El fichero «{ADVOCATE_FILENAME}» está y se ha leído entero: el abogado del diablo no "
                "encontró ningún ataque que mereciera reportarse."
            )
        lines.append("")

    # Sólo se llama «escenario que converge» a lo que dos lectores cotejaron de
    # verdad: con errores de lectura o con un solo lector, esta sección listaría
    # escenarios que nadie comparó con nadie, que es la peor forma de dar luz verde.
    converged_titles = [
        group.title for group in analysis.scenarios if group.key not in analysis.divergent_keys
    ] if analysis.contrasted else []
    if converged_titles:
        lines.extend([f"## Escenarios que convergen · {len(converged_titles)}", ""])
        lines.extend(f"- {title}" for title in converged_titles)
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="diff_readings.py",
        description=(
            "Compara las lecturas aisladas de un delta y convierte cada desacuerdo en una pregunta "
            "cerrada. La aritmética del veredicto la hace este código, no un modelo."
        ),
        epilog=(
            "Códigos de salida: 0 las lecturas convergen · 1 hay divergencia dura o laguna declarada "
            "(o blanda con --strict) · 2 error de uso, fichero de lectura ilegible o ejecución "
            "incompleta (menos de dos lectores, o ningún escenario que comparar)."
        ),
    )
    parser.add_argument(
        "--readings",
        required=True,
        metavar="DIR",
        help="directorio readings/ del change, con los ficheros reader-*.json y devils-advocate.json",
    )
    parser.add_argument(
        "--out",
        metavar="FILE",
        help="escribe el informe en este fichero (por convención, .venoxia/changes/<id>/divergence.md)",
    )
    parser.add_argument("--json", action="store_true", help="emite el JSON estable en vez del informe markdown")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        metavar="N",
        help=f"umbral de similitud de tokens para el campo effect (por defecto {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="las divergencias blandas también hacen fallar",
    )
    parser.add_argument("--no-color", action="store_true", help="sin colores ANSI")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida, nunca lanza por culpa de los datos."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not 0.0 <= args.threshold <= 1.0:
        print(
            f"venoxia: --threshold debe estar entre 0.0 y 1.0; llegó {args.threshold}.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    directory = Path(args.readings).expanduser()
    if not directory.exists():
        print(f"venoxia: no existe el directorio de lecturas «{directory}».", file=sys.stderr)
        return EXIT_USAGE
    if not directory.is_dir():
        print(
            f"venoxia: «{directory}» no es un directorio; --readings espera la carpeta readings/ del change.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    readers, attacks, advocate_status, errors = load_readings_dir(directory)
    if not readers and not errors:
        print(
            f"venoxia: no hay ningún fichero «{READER_PATTERN}» en «{directory}»; "
            "despacha primero los lectores con /venoxia:diverge.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    analysis = analyse(directory, readers, attacks, advocate_status, args.threshold, errors)
    # Un solo veredicto para los tres canales: el markdown, el JSON y el resumen de
    # `--out` lo reciben ya calculado y ninguno vuelve a decidir nada por su cuenta.
    verdict = build_verdict(analysis, args.strict)

    use_color = not args.no_color and sys.stdout.isatty()
    if args.json:
        text = json.dumps(build_payload(analysis, verdict), ensure_ascii=False, indent=2) + "\n"
    else:
        text = render_markdown(analysis, verdict, color=use_color and args.out is None)

    if args.out:
        out_path = Path(args.out).expanduser()
        try:
            if out_path.parent and not out_path.parent.exists():
                out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
        except OSError as exc:
            reason = exc.strerror or exc.__class__.__name__
            print(f"venoxia: no se pudo escribir «{out_path}»: {reason}.", file=sys.stderr)
            return EXIT_USAGE
        print(summary_line(analysis, verdict, color=use_color))
        print(f"Informe escrito en {out_path}")
    else:
        sys.stdout.write(text)

    return verdict.exit_code


if __name__ == "__main__":
    sys.exit(main())
