#!/usr/bin/env python3
"""El oráculo de Venoxia: ejecuta el test que cada requisito declara y anota el veredicto.

`validate.py` comprueba que un requisito **declare** su oráculo con
`verifies:` y que el fichero exista; no lo ejecuta. Este script es la otra
mitad: corre el `test_command` que el proyecto declara en
`.venoxia/venoxia.json`, una vez por requisito, y atribuye el resultado —
`green`, `red`, `missing` o `timeout`— al requisito exacto que lo declaró.
Determinista, sin red y sin modelo: dos ejecuciones sobre el mismo árbol y el
mismo estado del test producen el mismo JSON, byte a byte salvo `ran_at` y
las duraciones.

Uso:

    python3 scripts/oracle.py --change ID [PATH]
        --root DIR      raíz del proyecto (por defecto, el directorio actual)
        --change ID     el change .venoxia/changes/<ID>/ cuyos requisitos se ejecutan
        --timeout SECS  presupuesto por requisito, en segundos (por defecto 600)
        --record        añade la ejecución a .venoxia/changes/<ID>/oracle.json
        --dry-run       imprime el comando de cada requisito y no ejecuta nada
        --json          salida JSON con el esquema estable
        --no-color      sin colores ANSI

Configuración del proyecto, en `.venoxia/venoxia.json`:

    {"version": 1, "test_command": "python3 -m unittest {files}", "cwd": "."}

`{files}` se sustituye por las rutas de `verifies:` del requisito, separadas
por un espacio y entrecomilladas con `shlex.quote`. `cwd` es relativo a la
raíz del proyecto.

Códigos de salida: `0` todos los requisitos en `green` (o `--dry-run`) · `1`
alguno en `red`, `missing` o `timeout` · `2` error de uso: no existe
`.venoxia/`, el change no existe, falta `venoxia.json` o está mal escrito, o
`test_command` no trae `{files}`.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from venoxia import parser  # noqa: E402
from venoxia.model import Requirement  # noqa: E402

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

VENOXIA_DIR = ".venoxia"
CHANGES_DIR = "changes"
DELTA_DIR = "delta"
CONFIG_FILENAME = "venoxia.json"
RECORD_FILENAME = "oracle.json"

STATUS_GREEN = "green"
STATUS_RED = "red"
STATUS_MISSING = "missing"
STATUS_TIMEOUT = "timeout"

SCHEMA_VERSION = 1
FILES_PLACEHOLDER = "{files}"
DEFAULT_TIMEOUT = 600.0
MAX_RUNS = 50
OUTPUT_TAIL_LINES = 20

# El ejemplo que enseñan los errores de uso cuando falta o está mal escrito
# `.venoxia/venoxia.json`. Es texto, nunca se ejecuta.
CONFIG_EXAMPLE = (
    '{\n  "version": 1,\n  "test_command": "python3 -m unittest {files}",\n'
    '  "cwd": "."\n}'
)

ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"

MARK_OK = "✓"
MARK_FAIL = "✗"

# Separador de varias rutas en un mismo «verifies:», igual que validate.py.
_VERIFIES_SPLIT_CHARS = (",", " ", "\t", "\n")


class UsageError(Exception):
    """Error de uso: se responde con el código 2 y un mensaje en español."""


# ---------------------------------------------------------------------------
# Color (mismo criterio que venoxia.report)
# ---------------------------------------------------------------------------


def color_enabled(no_color: bool = False) -> bool:
    """Sólo se pinta si nadie lo ha pedido en contra y stdout es un terminal."""
    if no_color:
        return False
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


def paint(text: str, color: str, enabled: bool) -> str:
    """Envuelve el texto en color ANSI si está habilitado."""
    return f"{color}{text}{ANSI_RESET}" if enabled else text


# ---------------------------------------------------------------------------
# Configuración del proyecto
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OracleConfig:
    """El contenido ya validado de `.venoxia/venoxia.json`."""

    test_command: str
    cwd: Path


def load_config(root: Path) -> OracleConfig:
    """Lee y valida `.venoxia/venoxia.json`. Lanza `UsageError` si algo falta.

    Las tres formas de fallar tienen su propio mensaje, con un ejemplo de
    contenido válido delante: sin esto, quien lo lee tiene que adivinar el
    formato en vez de copiarlo.
    """
    config_path = root / VENOXIA_DIR / CONFIG_FILENAME
    try:
        exists = config_path.is_file()
    except OSError:
        exists = False
    if not exists:
        raise UsageError(
            f"falta «{VENOXIA_DIR}/{CONFIG_FILENAME}»: el oráculo necesita saber cómo "
            f"correr los tests de este proyecto. Créalo con, por ejemplo:\n\n{CONFIG_EXAMPLE}"
        )

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as error:
        raise UsageError(
            f"no se pudo leer «{VENOXIA_DIR}/{CONFIG_FILENAME}»: {error}."
        ) from error

    try:
        data = json.loads(text)
    except ValueError as error:
        raise UsageError(
            f"«{VENOXIA_DIR}/{CONFIG_FILENAME}» no es JSON válido: {error}. Ejemplo de "
            f"contenido válido:\n\n{CONFIG_EXAMPLE}"
        ) from error

    if not isinstance(data, dict):
        raise UsageError(
            f"«{VENOXIA_DIR}/{CONFIG_FILENAME}» debe ser un objeto JSON, no "
            f"«{type(data).__name__}». Ejemplo:\n\n{CONFIG_EXAMPLE}"
        )

    test_command = data.get("test_command")
    if not isinstance(test_command, str) or not test_command.strip():
        raise UsageError(
            f"«{VENOXIA_DIR}/{CONFIG_FILENAME}» no declara «test_command»: el comando "
            f"con el que correr los tests. Ejemplo:\n\n{CONFIG_EXAMPLE}"
        )
    if FILES_PLACEHOLDER not in test_command:
        raise UsageError(
            f"«test_command» de «{VENOXIA_DIR}/{CONFIG_FILENAME}» no contiene el "
            f"marcador «{FILES_PLACEHOLDER}»: sin él no hay dónde poner las rutas de "
            f"«verifies:». Ejemplo:\n\n{CONFIG_EXAMPLE}"
        )

    raw_cwd = data.get("cwd", ".")
    if not isinstance(raw_cwd, str) or not raw_cwd:
        raw_cwd = "."
    cwd = (root / raw_cwd) if not Path(raw_cwd).is_absolute() else Path(raw_cwd)
    try:
        cwd_is_dir = cwd.is_dir()
    except OSError:
        cwd_is_dir = False
    if not cwd_is_dir:
        raise UsageError(
            f"el «cwd» de «{VENOXIA_DIR}/{CONFIG_FILENAME}» («{raw_cwd}») no existe: "
            f"buscado en «{cwd}»."
        )

    return OracleConfig(test_command=test_command, cwd=cwd)


# ---------------------------------------------------------------------------
# Requisitos del change
# ---------------------------------------------------------------------------


def _verifies_paths(requirement: Requirement) -> list[str]:
    """Rutas declaradas en «verifies:», admitiendo varias separadas por coma o espacio."""
    value = (requirement.meta.get("verifies") or "").strip()
    if not value:
        return []
    chunk = value
    for char in _VERIFIES_SPLIT_CHARS[1:]:
        chunk = chunk.replace(char, ",")
    return [piece.strip() for piece in chunk.split(",") if piece.strip()]


def collect_requirements(root: Path, change: str) -> list[Requirement]:
    """Los requisitos de un change, en el orden en que aparecen en sus deltas.

    Lanza `UsageError` sólo si el change no existe: un `delta/` ausente o
    vacío no es un error de uso, es un change sin requisitos que ejecutar.
    """
    change_dir = root / VENOXIA_DIR / CHANGES_DIR / change
    try:
        change_exists = change_dir.is_dir()
    except OSError:
        change_exists = False
    if not change_exists:
        raise UsageError(
            f"no existe el change «{change}»: se buscaba «{change_dir}». Mira los "
            f"disponibles en «{root / VENOXIA_DIR / CHANGES_DIR}»."
        )

    delta_dir = change_dir / DELTA_DIR
    try:
        delta_files = sorted(delta_dir.glob("*.md")) if delta_dir.is_dir() else []
    except OSError:
        delta_files = []

    requirements: list[Requirement] = []
    for path in delta_files:
        delta, _findings = parser.parse_delta(path, root)
        requirements.extend(delta.requirements)
    return requirements


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------


@dataclass
class Result:
    """El veredicto de un requisito: su estado, cuánto tardó y qué dijo."""

    requirement_id: str
    verifies: list[str] = field(default_factory=list)
    status: str = STATUS_MISSING
    exit_code: int | None = None
    duration_ms: int = 0
    output_tail: str = ""

    def to_dict(self) -> dict:
        return {
            "requirement_id": self.requirement_id,
            "verifies": self.verifies,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "output_tail": self.output_tail,
        }


def build_command(template: str, files: list[str]) -> str:
    """Sustituye «{files}» por las rutas, entrecomilladas con `shlex.quote`."""
    joined = " ".join(shlex.quote(path) for path in files)
    return template.replace(FILES_PLACEHOLDER, joined)


def _tail(text: str, lines: int = OUTPUT_TAIL_LINES) -> str:
    """Las últimas `lines` líneas de un texto, o el texto entero si es más corto."""
    if not text:
        return ""
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


def run_one(requirement: Requirement, root: Path, cfg: OracleConfig, timeout: float) -> Result:
    """Ejecuta el oráculo de un requisito y devuelve su veredicto.

    Ficheros inexistentes no se invocan: el requisito queda «missing» sin
    tocar el runner. Con todos los ficheros en disco, se hace **una sola**
    invocación con todas sus rutas.
    """
    written = _verifies_paths(requirement)
    result = Result(requirement_id=requirement.id or "", verifies=written)

    if not written:
        result.status = STATUS_MISSING
        return result

    missing = [path for path in written if not _resolve(root, path).is_file()]
    if missing:
        result.status = STATUS_MISSING
        return result

    command = build_command(cfg.test_command, written)
    try:
        argv = shlex.split(command)
    except ValueError as error:
        # Comillas desparejadas en un test_command escrito a mano: no es un
        # fallo del requisito, es la configuración del proyecto. Se cuenta
        # como «red» porque el oráculo no se pudo correr, y se explica en la
        # cola de salida en vez de reventar.
        result.status = STATUS_RED
        result.output_tail = f"«test_command» no se pudo interpretar: {error}."
        return result

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cfg.cwd),
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout if timeout > 0 else None,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        result.status = STATUS_GREEN if completed.returncode == 0 else STATUS_RED
        result.exit_code = completed.returncode
        result.duration_ms = elapsed_ms
        result.output_tail = _tail(completed.stdout or "")
    except subprocess.TimeoutExpired as timeout_error:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        result.status = STATUS_TIMEOUT
        result.duration_ms = elapsed_ms
        output = timeout_error.output
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        result.output_tail = _tail(
            output or f"excedió el presupuesto de {timeout:g} s."
        )
    except OSError as os_error:
        # El runner no se pudo ni lanzar (comando inexistente, sin permisos).
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        result.status = STATUS_RED
        result.duration_ms = elapsed_ms
        result.output_tail = f"no se pudo lanzar «{cfg.test_command}»: {os_error}."

    return result


def _resolve(root: Path, path: str) -> Path:
    """Resuelve una ruta de `verifies:` contra la raíz del proyecto."""
    candidate = Path(os.path.expanduser(path))
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate


def run_all(
    requirements: list[Requirement], root: Path, cfg: OracleConfig, timeout: float
) -> list[Result]:
    """Ejecuta el oráculo de cada requisito, en el orden en que se recibieron."""
    return [run_one(requirement, root, cfg, timeout) for requirement in requirements]


def dry_run_lines(requirements: list[Requirement], root: Path, cfg: OracleConfig) -> list[str]:
    """El comando que se ejecutaría por requisito, sin ejecutar nada."""
    lines: list[str] = []
    for requirement in requirements:
        written = _verifies_paths(requirement)
        label = requirement.id or "«sin identificador»"
        if not written:
            lines.append(f"{label}: (sin «verifies:», no hay comando que construir)")
            continue
        missing = [path for path in written if not _resolve(root, path).is_file()]
        if missing:
            listed = ", ".join(f"«{path}»" for path in missing)
            lines.append(f"{label}: (no existe {listed}, no se invocaría el runner)")
            continue
        lines.append(f"{label}: {build_command(cfg.test_command, written)}")
    return lines


# ---------------------------------------------------------------------------
# Análisis y esquema JSON
# ---------------------------------------------------------------------------


def analyse(results: list[Result]) -> dict:
    """Cuenta los estados y decide `all_green`/`all_red`.

    `all_green`/`all_red` son literales: **todos** los requisitos, no la
    mayoría. Con cero requisitos ninguno de los dos es verdad — no hay nada
    que verificar, así que no hay nada que llamar «verde» ni «rojo».
    """
    counts = {
        STATUS_GREEN: 0,
        STATUS_RED: 0,
        STATUS_MISSING: 0,
        STATUS_TIMEOUT: 0,
        "total": len(results),
    }
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    total = counts["total"]
    all_green = total > 0 and counts[STATUS_GREEN] == total
    all_red = total > 0 and counts[STATUS_RED] == total
    return {"counts": counts, "all_green": all_green, "all_red": all_red}


def build_payload(change: str, cfg: OracleConfig, results: list[Result]) -> dict:
    """Construye el documento del esquema estable versión 1."""
    analysis = analyse(results)
    return {
        "version": SCHEMA_VERSION,
        "change": change,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "runner": {"command": cfg.test_command, "cwd": str(cfg.cwd)},
        "results": [result.to_dict() for result in results],
        "counts": analysis["counts"],
        "all_green": analysis["all_green"],
        "all_red": analysis["all_red"],
    }


def render_json(payload: dict) -> str:
    """Serializa el payload con el esquema estable, en UTF-8 legible."""
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False)


# ---------------------------------------------------------------------------
# Historial: .venoxia/changes/<id>/oracle.json
# ---------------------------------------------------------------------------


def _load_history(path: Path) -> list[dict]:
    """Los runs ya grabados, o una lista vacía si el fichero no existe o está roto.

    Un `oracle.json` que no se deja interpretar no detiene el registro: se
    avisa por stderr y se empieza un historial nuevo. Es lo mismo que hace
    `find_active_change` del guardián con un `change.json` corrupto: el
    fichero del usuario está mal, y eso no es un fallo del oráculo.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except OSError as error:
        print(
            f"venoxia: no se pudo leer «{path}» ({error}); se empieza un historial nuevo.",
            file=sys.stderr,
        )
        return []

    try:
        data = json.loads(text)
    except ValueError as error:
        print(
            f"venoxia: «{path}» no es JSON válido ({error}); se sustituye por un "
            "historial nuevo.",
            file=sys.stderr,
        )
        return []

    if not isinstance(data, dict) or not isinstance(data.get("runs"), list):
        print(
            f"venoxia: «{path}» no tiene la forma esperada; se sustituye por un "
            "historial nuevo.",
            file=sys.stderr,
        )
        return []

    return [run for run in data["runs"] if isinstance(run, dict)]


def record(path: Path, change: str, payload: dict, keep: int = MAX_RUNS) -> None:
    """Añade `payload` (sin «change») al historial y conserva como mucho `keep` runs."""
    entry = {key: value for key, value in payload.items() if key != "change"}
    runs = _load_history(path)
    runs.append(entry)
    if len(runs) > keep:
        runs = runs[-keep:]

    document = {"version": SCHEMA_VERSION, "change": change, "runs": runs}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"venoxia: no se pudo escribir «{path}»: {error}.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Informe de texto
# ---------------------------------------------------------------------------


def _status_color(status: str) -> str:
    if status == STATUS_GREEN:
        return ANSI_GREEN
    if status == STATUS_MISSING:
        return ANSI_YELLOW
    return ANSI_RED


def render_text(payload: dict, no_color: bool = False) -> str:
    """Una línea por requisito, y un cierre con los recuentos y el veredicto."""
    enabled = color_enabled(no_color)
    lines: list[str] = []

    for result in payload["results"]:
        status = result["status"]
        mark = MARK_OK if status == STATUS_GREEN else MARK_FAIL
        color = _status_color(status)
        header = (
            f"{mark} {result['requirement_id'] or '(sin identificador)'}  {status}  "
            f"{result['duration_ms']} ms"
        )
        lines.append(paint(header, color, enabled))

    counts = payload["counts"]
    lines.append(
        f"{counts[STATUS_GREEN]} green, {counts[STATUS_RED]} red, "
        f"{counts[STATUS_MISSING]} missing, {counts[STATUS_TIMEOUT]} timeout · "
        f"{counts['total']} requisitos"
    )

    if counts[STATUS_MISSING]:
        verdict = f"Oráculo incompleto: {counts[STATUS_MISSING]} ficheros no existen"
        color = ANSI_YELLOW
    elif counts[STATUS_RED] or counts[STATUS_TIMEOUT]:
        verdict = f"Oráculo en rojo: {counts[STATUS_RED] + counts[STATUS_TIMEOUT]} requisitos"
        color = ANSI_RED
    else:
        verdict = "Oráculo en verde"
        color = ANSI_GREEN
    lines.append(paint(verdict, color, enabled))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos."""
    cli = argparse.ArgumentParser(
        prog="oracle.py",
        description=(
            "Ejecuta el test_command de .venoxia/venoxia.json por cada requisito de un "
            "change y atribuye rojo o verde a cada uno. Determinista: nada consulta a "
            "un modelo."
        ),
        epilog=(
            "Códigos de salida: 0 todos en green (o --dry-run) · 1 alguno en red, "
            "missing o timeout · 2 error de uso."
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
        required=True,
        help="el change .venoxia/changes/<ID>/ cuyos requisitos se ejecutan",
    )
    cli.add_argument(
        "--timeout",
        metavar="SECONDS",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"presupuesto por requisito, en segundos (por defecto {DEFAULT_TIMEOUT:g})",
    )
    cli.add_argument(
        "--record",
        action="store_true",
        help="añade la ejecución a .venoxia/changes/<ID>/oracle.json",
    )
    cli.add_argument(
        "--dry-run",
        action="store_true",
        help="imprime el comando de cada requisito y no ejecuta nada",
    )
    cli.add_argument(
        "--json",
        action="store_true",
        help="emite el JSON del esquema estable en vez del informe de texto",
    )
    cli.add_argument("--no-color", action="store_true", help="sin colores ANSI")
    return cli


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida y nunca lanza por los datos."""
    cli = build_parser()
    args = cli.parse_args(argv)

    root = Path(os.path.expanduser(args.root)) if args.root else Path.cwd()
    if not root.is_dir():
        print(f"venoxia: la raíz «{root}» no existe o no es un directorio.", file=sys.stderr)
        return EXIT_USAGE
    root = root.resolve()

    if not (root / VENOXIA_DIR).is_dir():
        print(
            f"venoxia: este proyecto todavía no ha adoptado Venoxia (no existe "
            f"«{root / VENOXIA_DIR}»). No hay oráculo que ejecutar.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    try:
        cfg = load_config(root)
        requirements = collect_requirements(root, args.change)
    except UsageError as error:
        print(f"venoxia: {error}", file=sys.stderr)
        return EXIT_USAGE

    if args.dry_run:
        for line in dry_run_lines(requirements, root, cfg):
            print(line)
        return EXIT_OK

    results = run_all(requirements, root, cfg, args.timeout)
    payload = build_payload(args.change, cfg, results)

    if args.record:
        record_path = root / VENOXIA_DIR / CHANGES_DIR / args.change / RECORD_FILENAME
        record(record_path, args.change, payload)

    if args.json:
        print(render_json(payload))
    else:
        print(render_text(payload, no_color=args.no_color))

    counts = payload["counts"]
    failed = counts[STATUS_RED] or counts[STATUS_MISSING] or counts[STATUS_TIMEOUT]
    return EXIT_FAILED if failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
