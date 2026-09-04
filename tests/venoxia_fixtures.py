#!/usr/bin/env python3
"""Andamio compartido de la suite de tests de Venoxia.

Aquí vive el constructor de proyectos de prueba: un `.venoxia/` completo en un
directorio temporal, los scripts invocados por subproceso y unas cuantas ayudas
para leer su salida. Todos los ficheros de test de `tests/` se apoyan en esto.

Las tres piezas que hay que conocer:

* `requirement(...)` devuelve el markdown de **un** requisito canónico. Todos
  los casos negativos de las reglas V01–V16 se construyen tocándole un
  parámetro (o quitándole un metadato con `omit=`).
* `Project()` monta un proyecto **limpio**: pasa las dieciséis reglas con
  `--strict` y cero avisos. Es el punto de partida: se rompe una sola cosa y se
  comprueba que salta una sola regla.
* `CompletedRun` envuelve la salida del subproceso: `returncode`, `stdout`,
  `stderr`, `.json`, `.rules()`, `.rule_set()` y `.findings_for("V06")`.

Todo ocurre bajo `tempfile.TemporaryDirectory`: ni el repositorio ni el `$HOME`
real se tocan. Los subprocesos reciben un `HOME` falso, `PYTHONDONTWRITEBYTECODE=1`
y un `timeout` de 30 segundos.

Cómo importarlo
---------------
El import que funciona con **las tres** formas de lanzar la suite es el
cualificado::

    from tests.venoxia_fixtures import Project, requirement, future_date

    python3 -m pytest tests/ -q            # el del contrato
    python3 -m unittest discover -s tests -v
    python3 -m unittest tests.test_lo_que_sea -v

El import corto `from venoxia_fixtures import …` también funciona con `pytest`
y con `unittest discover`, pero **no** con `python3 -m unittest tests.test_x`,
porque ahí `tests/` no entra en `sys.path` antes de importar el módulo de test.
Si dudas, usa el cualificado.

Al final del fichero hay un ejemplo de uso completo, listo para copiar.
"""

from __future__ import annotations

import json as _json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path: el mismo ajuste que hace conftest.py, repetido aquí porque
# «python3 -m unittest» no carga conftest.py. Es idempotente.
# ---------------------------------------------------------------------------

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def ensure_import_paths() -> None:
    """Pone `<repo>/scripts` y `<repo>/tests` al principio de `sys.path`.

    Es el mismo ajuste de `conftest.py`, repetido aquí porque
    «python3 -m unittest» no carga `conftest.py`. Idempotente: llamarla dos
    veces no duplica las entradas.
    """
    for directory in (TESTS_DIR, SCRIPTS_DIR):
        entry = str(directory)
        if entry not in sys.path:
            sys.path.insert(0, entry)


ensure_import_paths()

# Los scripts de entrada, por si un test quiere invocarlos a mano.
VALIDATE_PY = SCRIPTS_DIR / "validate.py"
CHARTER_LINT_PY = SCRIPTS_DIR / "charter_lint.py"
GUARDIAN_PY = SCRIPTS_DIR / "guardian.py"
DIFF_READINGS_PY = SCRIPTS_DIR / "diff_readings.py"

# Segundos que se le conceden a cualquier subproceso antes de darlo por colgado.
RUN_TIMEOUT = 30


# ---------------------------------------------------------------------------
# Constantes del proyecto canónico
#
# Los seis ficheros de test comparten estos nombres: si un test necesita
# nombrar «la capability», «el change» o «el requisito del delta», que use
# estas constantes en vez de repetir la cadena.
# ---------------------------------------------------------------------------

CAPABILITY_NAME = "checkout"
CHANGE_ID = "c1"

#: El requisito que vive en la capability (`.venoxia/capabilities/checkout/spec.md`).
LIVE_REQUIREMENT_ID = "R-CHK-001"
LIVE_REQUIREMENT_TITLE = "Cart total recalculation on line change"
LIVE_NARRATIVE = (
    "WHEN el cliente cambia la cantidad de una línea del carrito, el sistema DEBE "
    "recalcular el total del carrito antes de responder."
)
LIVE_SCENARIOS: tuple[tuple[str, str, str], ...] = (
    (
        "Quantity increased on a line with stock",
        "el cliente sube la cantidad de una línea que tiene stock",
        "el total del carrito refleja la nueva cantidad en la misma respuesta",
    ),
)
LIVE_VERIFIES = "test/checkout/cart-total.spec.ts"
LIVE_FROM = "prfaq/checkout-express.md#el-carrito-siempre-cuadra"

#: El requisito que propone el delta (`.venoxia/changes/c1/delta/checkout.md`).
DEFAULT_REQUIREMENT_ID = "R-CHK-014"
DEFAULT_REQUIREMENT_TITLE = "Stock reservation on payment confirmation"
DEFAULT_NARRATIVE = (
    "WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de todas "
    "las líneas del pedido durante 15 minutos."
)
DEFAULT_SCENARIOS: tuple[tuple[str, str, str], ...] = (
    (
        "Stock available on every line",
        "hay stock disponible en todas las líneas",
        "se crea la reserva con TTL de 15 minutos",
    ),
    (
        "Insufficient stock on one line",
        "falta stock en al menos una línea",
        "responde 409 y no crea ninguna reserva",
    ),
)
DEFAULT_VERIFIES = "test/checkout/reservation.spec.ts"
DEFAULT_CONFIDENCE = "medium"
DEFAULT_FROM = "prfaq/checkout-express.md#sin-sorpresas-al-pagar"

#: Nombres de bloque de un delta, en el orden en que se escriben en el fichero.
BLOCK_NAMES = ("ADDED", "MODIFIED", "REMOVED", "RENAMED")

#: Claves que admite el parámetro `omit` de `requirement()`.
OMITTABLE = frozenset(
    {"id", "title", "narrative", "scenarios", "verifies", "confidence", "why", "revisit", "from"}
)


# ---------------------------------------------------------------------------
# Fechas: siempre relativas a hoy, nunca constantes que caducan
# ---------------------------------------------------------------------------


def today() -> date:
    """El día de hoy. Existe para que ningún test escriba `date.today()` a mano."""
    return date.today()


def future_date(days: int = 90) -> str:
    """Fecha ISO «YYYY-MM-DD» de dentro de `days` días.

    Ya no hay ningún campo de Venoxia que pida una fecha: `revisit:` declara el
    hecho que resuelve la apuesta, no el día en que caduca. Esto se conserva
    para los casos que prueban que **una fecha se rechaza**, y se calcula desde
    hoy por el mismo motivo de siempre: una constante escrita a mano deja de ser
    futura algún día y convierte la suite en verde-hasta-que-un-día-no.
    """
    return (date.today() + timedelta(days=days)).isoformat()


def past_date(days: int = 30) -> str:
    """Fecha ISO «YYYY-MM-DD» de hace `days` días.

    Igual que `future_date()`: sirve para comprobar que a `revisit:` le da lo
    mismo hacia qué lado apunte una fecha, porque ninguna fecha vale.
    """
    return (date.today() - timedelta(days=days)).isoformat()


#: El hecho que resuelve una apuesta, en la forma que `revisit:` pide ahora.
#: Nombra un suceso reconocible del proyecto de ejemplo: cuando ocurra, quien
#: mire sabrá que ya puede cerrar la apuesta.
REVISIT_FACT = "cuando hayamos servido las cincuenta primeras reservas"


# ---------------------------------------------------------------------------
# El markdown de un requisito
# ---------------------------------------------------------------------------


def requirement(
    id: str | None = DEFAULT_REQUIREMENT_ID,
    title: str | None = DEFAULT_REQUIREMENT_TITLE,
    narrative: str | None = None,
    scenarios: Sequence[object] | None = None,
    verifies: str | None = DEFAULT_VERIFIES,
    confidence: str | None = DEFAULT_CONFIDENCE,
    why: str | None = None,
    revisit: str | None = None,
    source: str | None = None,
    omit: Sequence[str] | str = (),
    *,
    separator: str = "·",
    extra_meta: Sequence[tuple[str, str]] = (),
) -> str:
    """Devuelve el markdown de UN requisito canónico, sin salto de línea final.

    Por defecto sale un requisito impecable: ID bien formado, narrativa EARS
    event-driven **sin `SHALL` ni `MUST`** (V14), dos escenarios con `WHEN` y
    `THEN` (V04/V05), `verifies:` a un fichero que `Project` crea de verdad y
    con su `@covers` (V06/V07/V08), `confidence: medium` (V09/V10/V11) y `from:`
    (V15).

    Parámetros
    ----------
    id, title
        Encabezado. Con los dos se escribe `### <id> <separator> <title>`. Si
        uno es `None` (o está en `omit`) se escribe solo el otro, sin separador,
        y entonces el parser deja el requisito **sin ID** — que es el caso
        negativo de V01. Para un ID mal formado, pásalo tal cual:
        `requirement(id="R-CHECKOUT-14")`.
    narrative
        `None` → la narrativa canónica. `""` → sin narrativa (negativo de V03).
        Cualquier otra cadena se escribe literal, multilínea incluida.
    scenarios
        `None` → los dos escenarios canónicos del contrato. `[]` → ninguno
        (negativo de V04). Si es una lista, cada elemento puede ser:

        * una tupla `(título, when, then)`; un `when` o un `then` a `None` no
          emite esa viñeta (negativo de V05);
        * una cadena, que se escribe literal como bloque de escenario (para
          viñetas raras, `AND`, o viñetas mal formadas que disparan `P04`).
    verifies, confidence, why, revisit, source
        Los metadatos. `source` es el valor de `from:` (`from` es palabra
        reservada de Python). Reglas comunes:

        * `None` en `verifies`/`confidence`/`why`/`revisit` → la línea no se
          escribe. `source=None` es la excepción: significa «el valor por
          defecto», porque su valor por defecto no es `None`.
        * `""` → la línea se escribe **vacía** (`verifies:`), que es un caso
          negativo distinto de no escribirla.
    omit
        Tupla de claves que no se emiten. Admite `'verifies'`, `'confidence'`,
        `'why'`, `'revisit'`, `'from'` y además `'id'`, `'title'`,
        `'narrative'` y `'scenarios'`. Una clave desconocida es un `ValueError`:
        vale más un error ruidoso que un `omit` que no omite nada.
    separator
        Separador entre ID y título. El parser admite `·`, `—`, `–` y ` - `.
    extra_meta
        Pares `(clave, valor)` que se añaden al final del bloque de metadatos,
        tal cual. Para los hallazgos del parser: una clave desconocida (`P02`)
        o una clave repetida (`P03`).

    Ejemplos
    --------
    ::

        requirement()                               # impecable
        requirement(omit=("verifies",))             # negativo de V06
        requirement(confidence="low", revisit=past_date())   # negativo de V10
        requirement(scenarios=[("Sólo condición", "falta stock", None)])  # V05
    """
    if isinstance(omit, str):
        omit = (omit,)
    omitted = frozenset(omit)
    unknown = sorted(omitted - OMITTABLE)
    if unknown:
        raise ValueError(
            f"requirement(omit=…) no conoce {unknown}; las claves válidas son "
            f"{sorted(OMITTABLE)}."
        )

    parts: list[str] = [_header(id, title, separator, omitted)]

    body = DEFAULT_NARRATIVE if narrative is None else narrative
    if "narrative" not in omitted and body.strip():
        parts.append(body.strip("\n"))

    if "scenarios" not in omitted:
        blocks = DEFAULT_SCENARIOS if scenarios is None else scenarios
        for block in blocks:
            parts.append(_scenario_block(block))

    meta = _meta_block(verifies, confidence, why, revisit, source, omitted, extra_meta)
    if meta:
        parts.append(meta)

    return "\n\n".join(parts)


def live_requirement(**overrides) -> str:
    """El requisito de la capability viva (`R-CHK-001`), con sus propios valores.

    Acepta los mismos parámetros que `requirement()` para sobrescribir lo que
    haga falta: `live_requirement(confidence="low", revisit=past_date())`.
    """
    defaults = {
        "id": LIVE_REQUIREMENT_ID,
        "title": LIVE_REQUIREMENT_TITLE,
        "narrative": LIVE_NARRATIVE,
        "scenarios": list(LIVE_SCENARIOS),
        "verifies": LIVE_VERIFIES,
        "confidence": "high",
        "source": LIVE_FROM,
    }
    defaults.update(overrides)
    return requirement(**defaults)


def _header(id: str | None, title: str | None, separator: str, omitted: frozenset[str]) -> str:
    """El «### …» del requisito, con ID, con título o con los dos."""
    has_id = id is not None and "id" not in omitted
    has_title = title is not None and "title" not in omitted
    if has_id and has_title:
        return f"### {id} {separator} {title}"
    if has_id:
        return f"### {id}"
    if has_title:
        return f"### {title}"
    return "###"


def _scenario_block(block: object) -> str:
    """Un «#### Scenario: …» con sus viñetas, desde una tupla o desde markdown crudo."""
    if isinstance(block, str):
        return block.strip("\n")
    if not isinstance(block, (tuple, list)) or len(block) != 3:
        raise ValueError(
            "Cada escenario es una tupla (título, when, then) o una cadena de markdown "
            f"crudo; llegó {block!r}."
        )
    title, when, then = block
    lines = [f"#### Scenario: {title}"]
    if when is not None:
        lines.append(f"- **WHEN** {when}")
    if then is not None:
        lines.append(f"- **THEN** {then}")
    return "\n".join(lines)


def _meta_block(
    verifies: str | None,
    confidence: str | None,
    why: str | None,
    revisit: str | None,
    source: str | None,
    omitted: frozenset[str],
    extra_meta: Sequence[tuple[str, str]],
) -> str:
    """El bloque de metadatos del requisito, con la sangría cosmética del contrato."""
    lines: list[str] = []
    if "verifies" not in omitted and verifies is not None:
        lines.append(f"verifies:   {verifies}".rstrip())
    if "confidence" not in omitted and confidence is not None:
        lines.append(f"confidence: {confidence}".rstrip())
    if "why" not in omitted and why is not None:
        lines.append(f"  why:      {why}".rstrip())
    if "revisit" not in omitted and revisit is not None:
        lines.append(f"  revisit:  {revisit}".rstrip())
    from_value = DEFAULT_FROM if source is None else source
    if "from" not in omitted:
        lines.append(f"from:       {from_value}".rstrip())
    for key, value in extra_meta:
        lines.append(f"{key}: {value}".rstrip())
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Las lecturas canónicas de diff_readings.py
# ---------------------------------------------------------------------------


def reading(
    scenario: str,
    effect: str,
    status_code: str | None = None,
    side_effects: Sequence[str] = (),
    unclear: bool = False,
    unclear_why: str | None = None,
) -> dict:
    """Una lectura suelta de un lector, con la forma exacta del contrato §7."""
    return {
        "scenario": scenario,
        "effect": effect,
        "status_code": status_code,
        "side_effects": list(side_effects),
        "unclear": unclear,
        "unclear_why": unclear_why,
    }


def default_readings() -> dict[str, list[dict]]:
    """Dos lectores que **convergen** sobre los dos escenarios del delta canónico.

    Devuelve un diccionario nuevo en cada llamada: modifícalo sin miedo para
    fabricar la divergencia que necesite el test.
    """
    agreed = [
        reading(
            scenario="Stock available on every line",
            effect="crea la reserva con TTL de 15 minutos",
            status_code="201",
            side_effects=["reserva creada", "stock comprometido"],
        ),
        reading(
            scenario="Insufficient stock on one line",
            effect="rechaza la petición y no crea ninguna reserva",
            status_code="409",
            side_effects=["ninguna reserva creada", "stock intacto"],
        ),
    ]
    return {
        "reader-a": [dict(item) for item in agreed],
        "reader-b": [dict(item) for item in agreed],
    }


# ---------------------------------------------------------------------------
# La salida de un subproceso
# ---------------------------------------------------------------------------


@dataclass
class CompletedRun:
    """Lo que devolvió un script: código de salida, stdout y stderr.

    Los métodos que hablan de reglas (`rules`, `rule_set`, `findings_for`)
    necesitan el JSON del informe: ejecuta `project.validate("--json", …)` o el
    atajo `project.validate_json(…)`. Si stdout no es JSON, la propiedad `.json`
    falla con un mensaje que dice exactamente eso.
    """

    returncode: int
    stdout: str
    stderr: str
    argv: tuple[str, ...] = ()

    @property
    def json(self) -> dict:
        """El stdout parseado como JSON.

        Falla con `AssertionError` y el comando entero en el mensaje si no lo es
        —casi siempre porque faltó `--json`—.
        """
        text = self.stdout.strip()
        if not text:
            raise AssertionError(
                "Se esperaba JSON en stdout y stdout está vacío.\n"
                f"  comando : {' '.join(self.argv)}\n"
                f"  returncode: {self.returncode}\n"
                f"  stderr  : {self.stderr.strip()[:800]}"
            )
        try:
            return _json.loads(text)
        except ValueError as error:
            raise AssertionError(
                f"stdout no es JSON ({error}). ¿Faltó «--json» en la invocación?\n"
                f"  comando : {' '.join(self.argv)}\n"
                f"  returncode: {self.returncode}\n"
                f"  stdout  : {text[:800]}\n"
                f"  stderr  : {self.stderr.strip()[:800]}"
            ) from None

    @property
    def findings(self) -> list[dict]:
        """La lista de hallazgos del informe JSON, en el orden en que vienen."""
        return list(self.json.get("findings", []))

    def rules(self) -> list[str]:
        """Códigos de regla de los hallazgos, en orden y con repeticiones."""
        return [finding.get("rule") for finding in self.findings]

    def rule_set(self) -> set[str]:
        """Conjunto de códigos de regla de los hallazgos."""
        return set(self.rules())

    def findings_for(self, rule: str) -> list[dict]:
        """Los hallazgos de una regla concreta, p. ej. `run.findings_for("V06")`."""
        return [finding for finding in self.findings if finding.get("rule") == rule]

    # -- Atajos del guardián -------------------------------------------------

    @property
    def decision(self) -> str:
        """`"allow"` o `"deny"`: la decisión que emitió `guardian.py`."""
        block = self.json.get("hookSpecificOutput", {})
        return block.get("permissionDecision", "")

    @property
    def reason(self) -> str:
        """El texto en español con que el guardián justifica su decisión."""
        block = self.json.get("hookSpecificOutput", {})
        return block.get("permissionDecisionReason", "")

    def describe(self) -> str:
        """Resumen de la ejecución, para meterlo en el mensaje de un assert."""
        return (
            f"comando: {' '.join(self.argv)}\n"
            f"returncode: {self.returncode}\n"
            f"stdout:\n{self.stdout}\n"
            f"stderr:\n{self.stderr}"
        )


# ---------------------------------------------------------------------------
# El proyecto de prueba
# ---------------------------------------------------------------------------


@dataclass
class Project:
    """Un proyecto de usuario completo dentro de un directorio temporal.

    Recién construido, `Project()` monta un proyecto **limpio**: pasa las
    dieciséis reglas con `--strict` y no produce ni un aviso. Ése es el punto de
    partida de todo caso negativo: se rompe **una** cosa y se comprueba que salta
    **una** regla.

    Lo que monta el andamio por defecto::

        <root>/
        ├── prfaq/checkout-express.md
        ├── test/checkout/cart-total.spec.ts       # @covers R-CHK-001
        ├── test/checkout/reservation.spec.ts      # @covers R-CHK-014
        └── .venoxia/
            ├── principles.md
            ├── capabilities/checkout/spec.md      # R-CHK-001 (confidence: high)
            └── changes/c1/
                ├── change.json                    # state draft · via spec
                ├── delta/checkout.md              # ## ADDED → R-CHK-014
                └── readings/reader-a.json, reader-b.json   # convergen

    Se usa como gestor de contexto y se limpia solo::

        with Project() as project:
            ...

    o, si el test prefiere el estilo de `unittest`::

        project = Project()
        self.addCleanup(project.cleanup)

    `Project(scaffold=False)` devuelve un directorio vacío, sin `.venoxia/`: es
    el proyecto «no adoptado» que `validate.py` salda con exit 0 y que el
    guardián deja pasar en su paso 1.

    Trampas conocidas, para no escribir tests ambiguos
    --------------------------------------------------
    * Un requisito nuevo necesita su oráculo en disco: si le cambias el
      `verifies:`, crea el fichero con `project.test_file(ruta, covers=[ID])` o
      pide la ruta ya hecha con `project.oracle(ID)`, o saltarán V07 y V08 además
      de lo que querías probar.
    * Todo requisito de un bloque `ADDED` necesita `from:` o salta V15 (aviso, y
      con `--strict` tumba la validación).
    * `SHALL` y `MUST` en la narrativa disparan V14. La narrativa canónica usa
      «DEBE».
    * Todo `revisit:` que deba ser válido usa `REVISIT_FACT`: un hecho, no una fecha.

    Acoplamientos reales entre reglas, que no son un fallo del andamio
    ---------------------------------------------------------------------
    Hay reglas que se disparan juntas porque el contrato dice que se disparen
    juntas. Cuando el test quiera **una sola** regla, hay que desactivar la otra
    a propósito:

    * `confidence: low` en el proyecto por defecto es 1 de 2 requisitos, el 50 %,
      así que V10 y V11 saltan a la vez. Añade rellenos intachables para que la
      aritmética vuelva a caber: `project.capability("checkout",
      [live_requirement(), *project.filler(3)])` deja el `low` en el 20 %.
    * Un requisito sin ID (o con el ID mal formado) deja huérfano el `@covers`
      de su oráculo, y a V01 se le suman V08 y V16. Apunta el `verifies:` a un
      oráculo que cubra exactamente ese ID:
      `requirement(id="R-CHECKOUT-14", verifies=project.oracle("R-CHECKOUT-14"))`.
    """

    scaffold: bool = True
    capability_name: str = CAPABILITY_NAME
    change_id: str = CHANGE_ID

    root: Path = field(init=False)
    home: Path = field(init=False)

    def __post_init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="venoxia-test-")
        base = Path(self._tmp.name).resolve()
        # El proyecto y el HOME falso viven separados: así ningún script
        # confunde el uno con el otro y el `$HOME` real nunca se toca.
        self.root = base / "project"
        self.home = base / "home"
        self.root.mkdir(parents=True, exist_ok=True)
        self.home.mkdir(parents=True, exist_ok=True)
        # Reloj propio para los mtime de los change.json: cada `change()` que se
        # escribe es estrictamente más reciente que el anterior, y así el
        # «cambio activo» del guardián no depende de la resolución del disco.
        self._clock = time.time() - 3600.0
        if self.scaffold:
            self._build_scaffold()

    # -- Ciclo de vida -------------------------------------------------------

    def __enter__(self) -> Project:
        return self

    def __exit__(self, *exc_info) -> bool:
        self.cleanup()
        return False

    def cleanup(self) -> None:
        """Borra el directorio temporal. Se puede llamar más de una vez."""
        self._tmp.cleanup()

    # -- Ficheros ------------------------------------------------------------

    def path(self, relpath: str | Path) -> Path:
        """Ruta absoluta de algo dentro del proyecto."""
        return self.root / Path(relpath)

    def write(self, relpath: str | Path, content: str) -> Path:
        """Escribe un fichero de texto (creando sus directorios) y devuelve su ruta."""
        target = self.path(relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read(self, relpath: str | Path) -> str:
        """Lee un fichero de texto del proyecto."""
        return self.path(relpath).read_text(encoding="utf-8")

    def exists(self, relpath: str | Path) -> bool:
        """¿Existe esa ruta dentro del proyecto?"""
        return self.path(relpath).exists()

    def remove(self, relpath: str | Path) -> None:
        """Borra un fichero del proyecto si está; si no está, no hace nada."""
        target = self.path(relpath)
        if target.is_file():
            target.unlink()

    # -- Especificación ------------------------------------------------------

    def adopt(self) -> Path:
        """Crea `.venoxia/` vacío y devuelve su ruta. Marca el proyecto como adoptado."""
        directory = self.path(".venoxia")
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def capability(
        self,
        name: str,
        requirements: Sequence[str] | str,
        purpose: str | None = None,
    ) -> Path:
        """Escribe `.venoxia/capabilities/<name>/spec.md` y devuelve su ruta.

        `requirements` es el markdown que devuelve `requirement()`: una cadena o
        una lista de cadenas. Escribir la misma capability dos veces la
        sobrescribe, que es como se rompe el proyecto limpio.
        """
        blocks = [requirements] if isinstance(requirements, str) else list(requirements)
        text = purpose if purpose is not None else (
            f"El paso de «{name}» del sistema: lo que el usuario ve y lo que el "
            "sistema garantiza."
        )
        body = "\n".join(
            [
                f"# Capability: {name}",
                "",
                "## Purpose",
                "",
                text,
                "",
                "## Requirements",
                "",
            ]
        )
        return self.write(
            f".venoxia/capabilities/{name}/spec.md",
            body + "\n\n".join(blocks) + "\n",
        )

    def change(
        self,
        id: str = CHANGE_ID,
        state: str = "draft",
        via: str = "spec",
        capabilities: Sequence[str] | None = None,
        *,
        created: str | None = None,
        extra: Mapping[str, object] | None = None,
        raw: str | None = None,
        mtime: float | None = None,
    ) -> Path:
        """Escribe `.venoxia/changes/<id>/change.json` y devuelve su ruta.

        `state ∈ {draft, specified, validated, archived}` y `via ∈ {spec, direct}`.
        `extra` añade o pisa claves del JSON; `raw` escribe el fichero literal
        (para probar un `change.json` corrupto).

        Cada llamada deja el fichero con un `mtime` estrictamente más reciente
        que el de la llamada anterior, así que **el último `change()` escrito es
        siempre el cambio activo** para el guardián. Pásale `mtime=` si el test
        necesita otro orden.
        """
        target = self.path(f".venoxia/changes/{id}/change.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            target.write_text(raw, encoding="utf-8")
        else:
            payload: dict[str, object] = {
                "id": id,
                "state": state,
                "via": via,
                "capabilities": list(capabilities or []),
                "created": created or f"{date.today().isoformat()}T09:14:00Z",
            }
            if extra:
                payload.update(extra)
            target.write_text(
                _json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

        self._clock += 2.0
        stamp = self._clock if mtime is None else mtime
        os.utime(target, (stamp, stamp))
        return target

    def delta(
        self,
        change_id: str,
        capability: str,
        added: Sequence[str] = (),
        modified: Sequence[str] = (),
        removed: Sequence[str] = (),
        renamed: Sequence[str] = (),
        raw: str | None = None,
        *,
        declare: Sequence[str] = (),
    ) -> Path:
        """Escribe `.venoxia/changes/<change_id>/delta/<capability>.md`.

        Cada bloque recibe la lista de markdowns de `requirement()`. Un bloque
        con requisitos se declara solo; para declarar un bloque **vacío** —o
        para forzar el orden— nómbralo en `declare=("ADDED",)`. Con `raw` se
        escribe el fichero literal: es la forma de fabricar un delta sin ningún
        bloque, que es el caso negativo de V12.

        Cuidado: los requisitos de `MODIFIED`, `REMOVED` y `RENAMED` también
        pasan por las dieciséis reglas, así que necesitan su `verifies:` con
        fichero y `@covers` como cualquier otro.
        """
        relpath = f".venoxia/changes/{change_id}/delta/{capability}.md"
        if raw is not None:
            return self.write(relpath, raw)

        contents = {
            "ADDED": list(added),
            "MODIFIED": list(modified),
            "REMOVED": list(removed),
            "RENAMED": list(renamed),
        }
        wanted = {name.upper() for name in declare}
        chunks: list[str] = []
        for name in BLOCK_NAMES:
            blocks = contents[name]
            if not blocks and name not in wanted:
                continue
            chunks.append(f"## {name} Requirements")
            chunks.extend(blocks)
        return self.write(relpath, "\n\n".join(chunks) + "\n" if chunks else "")

    def test_file(self, relpath: str | Path, covers: Sequence[str] | str = ()) -> Path:
        """Escribe un fichero de test de mentira con sus comentarios «@covers <ID>».

        `covers` admite un ID suelto o una lista. Con la lista vacía el fichero
        existe pero no cubre nada: es el caso negativo de V08.
        """
        ids = [covers] if isinstance(covers, str) else list(covers)
        lines = [
            "// Fichero de test de mentira, escrito por la suite de Venoxia.",
            "// No ejecuta nada: sólo existe para que el oráculo del requisito",
            "// tenga un fichero al que apuntar.",
        ]
        lines.extend(f"// @covers {identifier}" for identifier in ids)
        lines.extend(
            [
                "",
                'describe("caso de prueba", () => {',
                '  it("cumple lo que el requisito promete", () => {});',
                "});",
                "",
            ]
        )
        return self.write(relpath, "\n".join(lines))

    def oracle(self, requirement_id: str, path: str | None = None) -> str:
        """Crea el fichero de test que cubre `requirement_id` y devuelve su ruta relativa.

        Pensado para usarse dentro de la propia llamada a `requirement()`::

            req = requirement(id="R-CHK-999", verifies=project.oracle("R-CHK-999"))

        Así V07 y V08 quedan satisfechas y el test rompe sólo lo que quería
        romper.
        """
        relpath = path or f"test/generated/{requirement_id.lower()}.spec.ts"
        self.test_file(relpath, covers=[requirement_id])
        return relpath

    def filler(
        self,
        count: int,
        *,
        prefix: str = "R-FIL",
        start: int = 100,
        **overrides,
    ) -> list[str]:
        """Devuelve `count` requisitos intachables, cada uno con su oráculo en disco.

        Sirve para mover la aritmética de V11 sin tocar nada más: con tres
        rellenos, un solo «confidence: low» pasa del 50 % al 20 % y V11 deja de
        saltar encima del test de V10. Los IDs son `R-FIL-100`, `R-FIL-101`, …

        `**overrides` se pasa tal cual a `requirement()`::

            project.capability("checkout", [live_requirement(), *project.filler(3)])
        """
        blocks: list[str] = []
        for offset in range(count):
            identifier = f"{prefix}-{start + offset:03d}"
            defaults: dict[str, object] = {
                "id": identifier,
                "title": f"Filler requirement {start + offset}",
            }
            if "verifies" not in overrides:
                defaults["verifies"] = self.oracle(identifier)
            defaults.update(overrides)
            blocks.append(requirement(**defaults))
        return blocks

    def readings(
        self,
        change_id: str,
        readers: Mapping[str, object],
        devils_advocate: object | None = None,
    ) -> Path:
        """Escribe `.venoxia/changes/<change_id>/readings/` y devuelve el directorio.

        `readers` va de nombre a contenido. El nombre puede ser `"reader-a"` o
        simplemente `"a"`: el prefijo `reader-` se añade si falta, y la extensión
        `.json` también. El contenido puede ser:

        * una lista de lecturas (usa `reading(...)` o `default_readings()`), o un
          diccionario `{"readings": [...]}`, que se serializan a JSON;
        * una **cadena**, que se escribe literal — es como se fabrica el JSON
          malformado que el contrato manda saldar con exit 2.

        `devils_advocate` escribe `devils-advocate.json` con las mismas reglas.
        """
        directory = self.path(f".venoxia/changes/{change_id}/readings")
        directory.mkdir(parents=True, exist_ok=True)
        for name, content in readers.items():
            filename = name if name.startswith("reader-") else f"reader-{name}"
            if not filename.endswith(".json"):
                filename = f"{filename}.json"
            (directory / filename).write_text(_dump(content), encoding="utf-8")
        if devils_advocate is not None:
            (directory / "devils-advocate.json").write_text(
                _dump(devils_advocate), encoding="utf-8"
            )
        return directory

    def readings_dir(self, change_id: str = CHANGE_ID) -> Path:
        """Ruta absoluta del `readings/` de un change."""
        return self.path(f".venoxia/changes/{change_id}/readings")

    # -- Ejecución de los scripts -------------------------------------------

    def run(
        self,
        script: str | Path,
        *args: str,
        stdin: str | None = None,
        cwd: str | Path | None = None,
        timeout: int = RUN_TIMEOUT,
    ) -> CompletedRun:
        """Ejecuta un script de `scripts/` en un subproceso y devuelve su salida.

        Es el escape hatch: `validate`, `guardian` y `diff` son atajos sobre
        esto. El subproceso corre con `sys.executable`, con `cwd` dentro del
        temporal, con un `HOME` falso y con `PYTHONDONTWRITEBYTECODE=1` para no
        dejar `__pycache__` en el repositorio.
        """
        argv = [sys.executable, str(script), *[str(arg) for arg in args]]
        completed = subprocess.run(
            argv,
            input=stdin if stdin is not None else "",
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd is not None else str(self.root),
            env=self._env(),
        )
        return CompletedRun(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            argv=tuple(argv),
        )

    def validate(self, *args: str, cwd: str | Path | None = None) -> CompletedRun:
        """Ejecuta `validate.py --root <root>` con los argumentos que se le pasen.

        Los argumentos van tal cual: si quieres el JSON (y con él `.rules()`),
        pásale `"--json"` o usa `validate_json()`.
        """
        return self.run(VALIDATE_PY, "--root", str(self.root), *args, cwd=cwd)

    def validate_json(self, *args: str, cwd: str | Path | None = None) -> CompletedRun:
        """Atajo de `validate("--json", …)`, que es lo que necesitan `.rules()` y `.json`."""
        return self.validate("--json", *args, cwd=cwd)

    def lint(self, *args: str, cwd: str | Path | None = None) -> CompletedRun:
        """Ejecuta `charter_lint.py --root <root>` con los argumentos que se le pasen.

        Hermano de `validate()`: mismos argumentos, mismo `CompletedRun`, sólo que
        sobre `.venoxia/charter.md` en vez de sobre capabilities y deltas.
        """
        return self.run(CHARTER_LINT_PY, "--root", str(self.root), *args, cwd=cwd)

    def lint_json(self, *args: str, cwd: str | Path | None = None) -> CompletedRun:
        """Atajo de `lint("--json", …)`, que es lo que necesitan `.rules()` y `.json`."""
        return self.lint("--json", *args, cwd=cwd)

    def guardian(
        self,
        tool_name: str = "Write",
        file_path: str | None = None,
        cwd: str | Path | None = None,
        raw_stdin: str | None = None,
        *,
        tool_input: Mapping[str, object] | None = None,
        path_key: str | None = None,
        extra_payload: Mapping[str, object] | None = None,
    ) -> CompletedRun:
        """Ejecuta `guardian.py` con un payload de hook por la entrada estándar.

        Por defecto edita `src/checkout.ts`, que **no** es especificación: es la
        ruta con la que el guardián de verdad decide. El `cwd` del payload es la
        raíz del proyecto salvo que se diga otra cosa.

        * `tool_name="NotebookEdit"` mete la ruta en `notebook_path`, como manda
          el contrato; `path_key=` fuerza la clave a mano.
        * `tool_input={}` sustituye el bloque entero: así se prueba el payload
          sin ninguna ruta.
        * `raw_stdin="…"` manda esa cadena literal por stdin e ignora todo lo
          demás: es la forma de probar el JSON malformado y el stdin vacío.
        """
        if raw_stdin is not None:
            payload_text = raw_stdin
        else:
            if tool_input is None:
                key = path_key or (
                    "notebook_path" if tool_name == "NotebookEdit" else "file_path"
                )
                tool_input = {key: file_path if file_path is not None else "src/checkout.ts"}
            payload: dict[str, object] = {
                "hook_event_name": "PreToolUse",
                "cwd": str(cwd) if cwd is not None else str(self.root),
                "tool_name": tool_name,
                "tool_input": dict(tool_input),
            }
            if extra_payload:
                payload.update(extra_payload)
            payload_text = _json.dumps(payload, ensure_ascii=False)
        return self.run(GUARDIAN_PY, stdin=payload_text)

    def diff(self, change_id: str = CHANGE_ID, *args: str) -> CompletedRun:
        """Ejecuta `diff_readings.py --readings .venoxia/changes/<change_id>/readings/`."""
        return self.run(DIFF_READINGS_PY, "--readings", str(self.readings_dir(change_id)), *args)

    # -- Interior ------------------------------------------------------------

    def _env(self) -> dict[str, str]:
        """El entorno de los subprocesos: determinista y sin tocar el `$HOME` real."""
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["HOME"] = str(self.home)
        env.pop("PYTHONPATH", None)
        return env

    def _build_scaffold(self) -> None:
        """Monta el proyecto limpio: el que pasa todas las reglas con `--strict`."""
        self.write(
            ".venoxia/principles.md",
            "# Principios\n\n"
            "El comportamiento se escribe antes que el código, y todo requisito "
            "declara qué test lo desmiente.\n",
        )
        self.write(
            "prfaq/checkout-express.md",
            "# Checkout express\n\n"
            "## El carrito siempre cuadra\n\n"
            "El total del carrito no sorprende a nadie al pagar.\n\n"
            "## Sin sorpresas al pagar\n\n"
            "Al confirmar el pago el stock queda reservado el tiempo necesario para "
            "liquidar.\n",
        )
        self.test_file(LIVE_VERIFIES, covers=[LIVE_REQUIREMENT_ID])
        self.test_file(DEFAULT_VERIFIES, covers=[DEFAULT_REQUIREMENT_ID])
        self.capability(self.capability_name, [live_requirement()])
        self.change(
            self.change_id,
            state="draft",
            via="spec",
            capabilities=[self.capability_name],
        )
        self.delta(self.change_id, self.capability_name, added=[requirement()])
        self.readings(self.change_id, default_readings())


def _dump(content: object) -> str:
    """Serializa a JSON, o devuelve la cadena tal cual si ya viene escrita."""
    if isinstance(content, str):
        return content
    return _json.dumps(content, ensure_ascii=False, indent=2) + "\n"


__all__ = [
    "BLOCK_NAMES",
    "CAPABILITY_NAME",
    "CHANGE_ID",
    "CHARTER_LINT_PY",
    "CompletedRun",
    "DEFAULT_CONFIDENCE",
    "DEFAULT_FROM",
    "DEFAULT_NARRATIVE",
    "DEFAULT_REQUIREMENT_ID",
    "DEFAULT_REQUIREMENT_TITLE",
    "DEFAULT_SCENARIOS",
    "DEFAULT_VERIFIES",
    "DIFF_READINGS_PY",
    "GUARDIAN_PY",
    "LIVE_FROM",
    "LIVE_NARRATIVE",
    "LIVE_REQUIREMENT_ID",
    "LIVE_REQUIREMENT_TITLE",
    "LIVE_SCENARIOS",
    "LIVE_VERIFIES",
    "OMITTABLE",
    "Project",
    "REPO_ROOT",
    "RUN_TIMEOUT",
    "SCRIPTS_DIR",
    "TESTS_DIR",
    "VALIDATE_PY",
    "default_readings",
    "ensure_import_paths",
    "future_date",
    "REVISIT_FACT",
    "live_requirement",
    "past_date",
    "reading",
    "requirement",
    "today",
]


# ---------------------------------------------------------------------------
# Ejemplo de uso · cópialo y cámbiale lo que necesites
# ---------------------------------------------------------------------------
#
# import unittest
#
# from tests.venoxia_fixtures import Project, requirement, future_date, past_date
#
#
# class TestReglaV06(unittest.TestCase):
#     """V06 · el requisito declara su oráculo en «verifies:»."""
#
#     def test_v06_passes_on_the_clean_project(self):
#         """El proyecto limpio no produce ningún hallazgo de V06."""
#         with Project() as project:
#             run = project.validate_json("--strict")
#             self.assertEqual(run.returncode, 0, run.describe())
#             self.assertEqual(run.rules(), [])
#
#     def test_v06_fails_when_verifies_is_absent(self):
#         """Quitar «verifies:» del requisito del delta dispara V06 y sólo V06."""
#         with Project() as project:
#             project.delta("c1", "checkout", added=[requirement(omit=("verifies",))])
#             run = project.validate_json("--strict")
#             self.assertEqual(run.returncode, 1, run.describe())
#             self.assertEqual(run.rule_set(), {"V06"})
#             self.assertEqual(run.findings_for("V06")[0]["requirement_id"], "R-CHK-014")
#
#     def test_guardian_denies_a_source_edit_without_a_validated_change(self):
#         """Con el change en «draft», editar código fuera de la spec se deniega."""
#         with Project() as project:
#             run = project.guardian(tool_name="Write", file_path="src/checkout.ts")
#             self.assertEqual(run.returncode, 0)
#             self.assertEqual(run.decision, "deny")
#             self.assertIn("/venoxia:specify", run.reason)
#
#     def test_diff_converges_on_the_clean_project(self):
#         """Las dos lecturas por defecto convergen: exit 0."""
#         with Project() as project:
#             run = project.diff("c1", "--json")
#             self.assertEqual(run.returncode, 0, run.describe())
#             self.assertTrue(run.json["converged"])
#
#
# if __name__ == "__main__":
#     unittest.main()
