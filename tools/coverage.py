#!/usr/bin/env python3
"""Cobertura de `scripts/**/*.py` con la stdlib, subprocesos incluidos.

`tests/venoxia_fixtures.py` (`Project.run`) ejecuta `validate.py`,
`charter_lint.py`, `guardian.py`, `diff_readings.py` y `oracle.py` **por
subprocess**, nunca importados. Una medida de cobertura ingenua —correr
`trace` sólo sobre el proceso de `unittest`— vería una fracción: todo lo que
pasa dentro de esos subprocesos quedaría sin contar. Este script resuelve eso
en dos mitades que se buscan la una a la otra:

1. Aquí abajo se lanza la suite entera bajo `tools/trace_run.py`, el
   envoltorio de `trace` de este mismo repositorio (no `python3 -m trace`
   directamente — véase por qué en su docstring), con `VENOXIA_TRACE_DIR=<dir>`
   en el entorno del proceso de `unittest`.

2. `Project.run` (en `tests/venoxia_fixtures.py`) mira esa misma variable: si
   está puesta, antepone `[sys.executable, tools/trace_run.py]` a cada
   subproceso que lanza. Como hereda el entorno del proceso de `unittest`
   (que ya la tiene), esto ocurre sin que ningún test declare nada.

`tools/trace_run.py` existe porque `python3 -m trace` tiene dos huecos que
rompían esta medición:

* `trace.main()` atrapa el `SystemExit` de lo que ejecuta con un
  `except SystemExit: pass` explícito y nunca lo relanza: bajo esa medición,
  cualquier script que sale con `sys.exit(N)` para `N != 0` devuelve `0` al
  proceso que lo lanzó, así que un test que comprueba `returncode == 1` de
  `validate.py` fallaba sólo por estar bajo `trace`, no por una regresión.
* `scripts/guardian.py` termina siempre con `os._exit(0)` en su `finally`
  fail-open — algo que ningún ajuste de este proyecto toca —, y `os._exit`
  salta el volcado de resultados de `trace`, que sólo ocurre al retornar de
  la ejecución que envuelve. `guardian.py` medía 0 % para siempre por esta
  vía.

`tools/trace_run.py` ejecuta el script en el mismo proceso con
`runpy.run_path` dentro de `Trace.runctx`, captura el `SystemExit` real y
sustituye `os._exit` por una función que vuelca las cuentas acumuladas antes
de llamar al `os._exit` original — así los dos huecos se cierran sin tocar
ni `guardian.py` ni ningún otro script medido.

El fichero de cuentas (`<dir>/counts`) es uno solo: `trace` lo usa a la vez
como `infile` y como `outfile`, así que cada proceso —el principal y cada
subproceso— carga lo acumulado hasta ese momento, le suma lo suyo, y vuelve a
escribir el conjunto completo en `<dir>/*.cover`. La suite es secuencial (no
hay dos scripts corriendo en paralelo), así que no hay carrera en ese
fichero: quien escribe último dentro de un mismo run dejó ya fusionado todo lo
anterior.

Umbral
------
La primera vez que se ejecuta (no existe todavía `tools/coverage-threshold.json`,
o se pide explícitamente con `--init`), este script fija el umbral de cada
fichero en el valor medido menos 2 puntos, redondeado hacia abajo — y nunca
por debajo de 85 para los cinco scripts del núcleo determinista
(`validate.py`, `charter_lint.py`, `guardian.py`, `diff_readings.py`,
`oracle.py`). Las siguientes ejecuciones comparan contra ese fichero y fallan
(código 1) si algún fichero baja de su umbral.

Con el envoltorio de `tools/trace_run.py`, `scripts/guardian.py` ya deja
`.cover` como cualquier otro script: el hueco que documentaba esta sección
(medía 0 % por el `os._exit` sin volcar) está cerrado, y su umbral se trata
igual que el de los otros cuatro scripts del núcleo.

Uso
---
    python3 tools/coverage.py                    # mide y compara con el umbral
    python3 tools/coverage.py --init             # (re)fija el umbral desde lo medido ahora
    python3 tools/coverage.py --out DIR          # dónde deja counts/ y los .cover
    python3 tools/coverage.py --threshold-file P # umbral en otro fichero
    python3 tools/coverage.py --fail-under 90    # ignora el fichero de umbral: exige 90 a todos

Tiempo medido en esta máquina: la suite completa bajo esta doble traza tarda
del orden de dos minutos (frente a ~25 s sin trace) — muy por debajo del
límite de 15 minutos que impondría paralelizar por fichero de test. Por eso
este script no implementa esa paralelización: es una simplificación
deliberada, no un olvido, y queda dicha aquí por si algún día el tiempo
medido en CI la hace necesaria.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
TESTS_DIR = REPO_ROOT / "tests"
TRACE_RUN_PY = TOOLS_DIR / "trace_run.py"

DEFAULT_OUT_DIR = REPO_ROOT / "coverage"
DEFAULT_THRESHOLD_FILE = TOOLS_DIR / "coverage-threshold.json"

#: Los cinco scripts del núcleo determinista: su umbral nunca baja de 85,
#: pase lo que pase con la resta de 2 puntos sobre lo medido en el `--init`.
CORE_SCRIPTS = frozenset(
    {
        "scripts/validate.py",
        "scripts/charter_lint.py",
        "scripts/guardian.py",
        "scripts/diff_readings.py",
        "scripts/oracle.py",
    }
)

CORE_FLOOR = 85

#: Formato de una línea de `.cover`: `"%5d: "` para las ejecutadas (el
#: recuento siempre es >=1 — si nunca se ejecutó no lleva número, lleva la
#: marca de abajo), `">>>>>> "` para las ejecutables que nunca se ejecutaron
#: (sólo aparece con `--missing`, que este script siempre pide), y siete
#: espacios para todo lo que no es una línea ejecutable (comentarios, blancos,
#: continuaciones). Verificado contra la salida real de `trace` en 3.14.
_EXECUTED_RE = re.compile(r"^\s*\d+:")
_MISSING_PREFIX = ">>>>>>"


class CoverageError(Exception):
    """Un error de uso: umbral corrupto, fichero de umbral con claves ajenas, etc."""


def discover_scripts() -> list[Path]:
    """Todos los `.py` de `scripts/`, recursivo, en orden estable."""
    return sorted(SCRIPTS_DIR.rglob("*.py"))


def script_key(path: Path) -> str:
    """La clave con la que este script nombra un fichero: `scripts/venoxia/model.py`."""
    return path.relative_to(REPO_ROOT).as_posix()


def cover_filename_for(path: Path) -> str:
    """El nombre de `.cover` que `trace` le da a este fichero.

    Un script de primer nivel (`scripts/validate.py`) corre como `__main__`
    de un fichero suelto: `trace` lo nombra por su nombre base, sin paquete
    (`validate.cover`). Un módulo del paquete `venoxia` se importa con su
    nombre punteado (`venoxia.model`), y así es como `trace` lo anota
    (`venoxia.model.cover`) — comprobado corriendo la suite real bajo
    `VENOXIA_TRACE_DIR` y mirando qué apareció.
    """
    relative = path.relative_to(SCRIPTS_DIR).with_suffix("")
    dotted = ".".join(relative.parts)
    return f"{dotted}.cover"


def parse_cover_file(path: Path) -> tuple[int, int]:
    """`(líneas ejecutables, líneas ejecutadas)` a partir de un `.cover`."""
    executable = 0
    executed = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if _EXECUTED_RE.match(line):
                executable += 1
                executed += 1
            elif line.startswith(_MISSING_PREFIX):
                executable += 1
    return executable, executed


def missing_lines(path: Path, limit: int = 20) -> list[str]:
    """Las líneas fuente marcadas `>>>>>>` (ejecutables, nunca ejecutadas)."""
    found: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, start=1):
            if line.startswith(_MISSING_PREFIX):
                found.append(f"L{lineno}: {line[len(_MISSING_PREFIX):].strip()}")
                if len(found) >= limit:
                    break
    return found


class FileCoverage:
    """Lo medido para un fichero: puede no haber datos en absoluto (`executable=0`)."""

    __slots__ = ("key", "executable", "executed", "cover_path")

    def __init__(self, key: str, executable: int, executed: int, cover_path: Path | None):
        self.key = key
        self.executable = executable
        self.executed = executed
        self.cover_path = cover_path

    @property
    def percentage(self) -> float | None:
        if self.executable == 0:
            return None
        return round(100.0 * self.executed / self.executable, 1)

    @property
    def has_data(self) -> bool:
        return self.cover_path is not None


def run_suite_under_trace(out_dir: Path) -> int:
    """Lanza la suite bajo `tools/trace_run.py -m unittest`, con `VENOXIA_TRACE_DIR=out_dir`.

    Devuelve el código de salida real de `unittest` (0 si `OK`, 1 si `FAILED`)
    — a diferencia de `python3 -m trace`, que lo enmascaraba siempre a `0`
    (véase el docstring de `tools/trace_run.py`). Ese código ya no es sólo
    informativo: `main()` lo usa para hacer fallar la ejecución si la suite no
    terminó en `OK` bajo medición, porque ahora un `FAILED` aquí es la suite
    de verdad fallando, no un artefacto de la instrumentación.

    `Project.run` (en `tests/venoxia_fixtures.py`) hereda `VENOXIA_TRACE_DIR`
    de este entorno para todos los subprocesos que la suite lanza, así que
    también ellos pasan por `tools/trace_run.py`.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    argv = [
        sys.executable,
        str(TRACE_RUN_PY),
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-q",
    ]
    env = dict(os.environ)
    env["VENOXIA_TRACE_DIR"] = str(out_dir)
    completed = subprocess.run(argv, cwd=str(REPO_ROOT), env=env)
    return completed.returncode


def measure(out_dir: Path) -> dict[str, FileCoverage]:
    """Cobertura por fichero de `scripts/**/*.py`, leyendo los `.cover` de `out_dir`."""
    results: dict[str, FileCoverage] = {}
    for script_path in discover_scripts():
        key = script_key(script_path)
        cover_path = out_dir / cover_filename_for(script_path)
        if cover_path.exists():
            executable, executed = parse_cover_file(cover_path)
            results[key] = FileCoverage(key, executable, executed, cover_path)
        else:
            results[key] = FileCoverage(key, 0, 0, None)
    return results


def compute_threshold(key: str, measured: float | None) -> int:
    """El umbral del `--init`: medido menos 2, hacia abajo; suelo de 85 en el núcleo."""
    base = measured if measured is not None else 0.0
    floor_value = math.floor(base - 2)
    if key in CORE_SCRIPTS:
        floor_value = max(floor_value, CORE_FLOOR)
    return floor_value


def build_thresholds(coverage: dict[str, FileCoverage]) -> dict[str, int]:
    return {key: compute_threshold(key, fc.percentage) for key, fc in coverage.items()}


def load_thresholds(path: Path) -> dict[str, int]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise CoverageError(
            f"No se pudo leer el fichero de umbral {path}: {err}. "
            "Bórralo o corrígelo, o vuelve a fijarlo con --init."
        ) from err
    if not isinstance(raw, dict):
        raise CoverageError(f"{path} no es un objeto JSON de {{fichero: umbral}}.")
    return {str(k): int(v) for k, v in raw.items()}


def write_thresholds(path: Path, thresholds: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = dict(sorted(thresholds.items()))
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_table(coverage: dict[str, FileCoverage], thresholds: dict[str, int]) -> tuple[str, bool]:
    """La tabla que se imprime, y si todo el mundo pasó su umbral."""
    header = f"{'fichero':<32} {'ejecutables':>11} {'ejecutadas':>10} {'%':>6} {'umbral':>6}  estado"
    lines = [header, "-" * len(header)]
    ok = True
    for key in sorted(coverage):
        fc = coverage[key]
        threshold = thresholds.get(key)
        pct = fc.percentage
        pct_text = f"{pct:.1f}" if pct is not None else "n/d"
        threshold_text = str(threshold) if threshold is not None else "-"
        if not fc.has_data:
            status = "SIN DATOS"
        elif pct is None:
            status = "SIN DATOS"
        else:
            status = None  # se decide abajo
        failing = threshold is not None and (pct is None or pct < threshold)
        if failing:
            ok = False
            status = "FALLA" if status is None else f"{status} (FALLA)"
        elif status is None:
            status = "ok"
        lines.append(
            f"{key:<32} {fc.executable:>11} {fc.executed:>10} {pct_text:>6} "
            f"{threshold_text:>6}  {status}"
        )
    return "\n".join(lines), ok


def print_gap_notes(coverage: dict[str, FileCoverage], thresholds: dict[str, int]) -> None:
    for key in sorted(coverage):
        fc = coverage[key]
        threshold = thresholds.get(key)
        if fc.has_data or threshold is None:
            continue
        print(f"\n{key}: sin `.cover` en {DEFAULT_OUT_DIR} — ¿algún test lo ejercita?")


def print_missing_for_failures(coverage: dict[str, FileCoverage], thresholds: dict[str, int]) -> None:
    for key in sorted(coverage):
        fc = coverage[key]
        threshold = thresholds.get(key)
        pct = fc.percentage
        if threshold is None or pct is None or pct >= threshold or not fc.has_data:
            continue
        gaps = missing_lines(fc.cover_path)
        if gaps:
            print(f"\n{key}: líneas ejecutables nunca ejecutadas (hasta 20):")
            for gap in gaps:
                print(f"  {gap}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cobertura de scripts/**/*.py con trace de la stdlib, subprocesos incluidos.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT_DIR),
        help=f"Directorio de counts/.cover (por defecto {DEFAULT_OUT_DIR}).",
    )
    parser.add_argument(
        "--threshold-file",
        default=str(DEFAULT_THRESHOLD_FILE),
        help=f"Fichero de umbrales (por defecto {DEFAULT_THRESHOLD_FILE}).",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Ignora el fichero de umbral: exige este porcentaje a todos los ficheros.",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="(Re)fija tools/coverage-threshold.json desde lo medido en esta ejecución.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    out_dir = Path(args.out)
    threshold_file = Path(args.threshold_file)

    suite_returncode = run_suite_under_trace(out_dir)
    if suite_returncode != 0:
        print(
            f"\nLa suite no terminó en OK bajo medición (código {suite_returncode}): "
            "esto ya no es un artefacto de la instrumentación — con tools/trace_run.py "
            "el código de salida es el real de unittest. Corrige la suite antes de fiarte "
            "de la tabla de abajo."
        )
    else:
        print("\nLa suite terminó en OK bajo medición.")

    coverage = measure(out_dir)

    bootstrapping = args.init or not threshold_file.exists()
    if bootstrapping:
        thresholds = build_thresholds(coverage)
        write_thresholds(threshold_file, thresholds)
        if not args.init:
            print(f"\nNo existía {threshold_file}: se ha creado con lo medido ahora como línea base.")
        else:
            print(f"\n{threshold_file} fijado de nuevo con lo medido ahora.")
    else:
        thresholds = load_thresholds(threshold_file)
        missing_keys = sorted(set(coverage) - set(thresholds))
        if missing_keys:
            for key in missing_keys:
                thresholds[key] = compute_threshold(key, coverage[key].percentage)
            write_thresholds(threshold_file, thresholds)
            print(
                f"\nFicheros nuevos sin umbral: {', '.join(missing_keys)}. "
                f"Añadidos a {threshold_file} con lo medido ahora."
            )

    if args.fail_under is not None:
        thresholds = {key: math.floor(args.fail_under) for key in coverage}

    table, ok = render_table(coverage, thresholds)
    print()
    print(table)
    print_gap_notes(coverage, thresholds)
    print_missing_for_failures(coverage, thresholds)

    return 0 if ok and suite_returncode == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CoverageError as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(2)
