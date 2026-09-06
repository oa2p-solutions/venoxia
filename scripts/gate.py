#!/usr/bin/env python3
"""La puerta de Venoxia: un comando, no un fichero de CI.

Lo que un proyecto necesita para afirmar que cumple son tres cosas —el acta, el
validador y el oráculo de cada change en `verified`— y un veredicto único. Eso
es un comando: un workflow obligaría a declarar un runner, un checkout y una
forma de autenticarse, y esas tres decisiones son de quien lo copia, no de
Venoxia. Sin ninguna de las tres, esto corre igual en cualquier CI, en un hook
local o a mano.

Dos propiedades que gobiernan todo lo demás:

**Fail-closed**, al revés que el guardián. Aquél es fail-open a propósito,
porque un guardián que se cae no puede impedir trabajar; ésta no puede aprobar
lo que no ha llegado a comprobar. Un `0` sólo significa algo si es imposible
obtenerlo por accidente, así que todo lo que impida comprobar sale con `2`.

**Ejecuta sus propios scripts**, los que viajan junto a este fichero, nunca los
que encuentre bajo la raíz inspeccionada: resolverlos contra el proyecto
convertiría tres stubs de tres líneas en un verde permanente.

Códigos de salida, los mismos que el resto del núcleo:

    0   el proyecto pasa la puerta
    1   no la pasa
    2   el uso es incorrecto, o algo impidió comprobar

Cómo lanzarlo::

    python3 scripts/gate.py --root <proyecto>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

#: Los cinco estados del ciclo de vida. Un `state` que no sea uno de éstos no
#: se salta: corromper el valor no puede salir más barato que borrarlo.
LIFECYCLE_STATES = frozenset(
    {"draft", "specified", "validated", "verified", "archived"}
)

#: El delta de un change entra en el validador al llegar aquí. Antes —en
#: `specified`— V07/V08 están en rojo por diseño, porque el test aún no existe.
VALIDATED_STATES = frozenset({"validated", "verified"})

#: El oráculo sólo gatea aquí. Un change en `validated` está rojo por diseño
#: —el test existe y el código todavía no—, así que hacerlo gatear bloquearía
#: la rama principal durante el flujo normal.
GATED_STATES = frozenset({"verified"})

VENOXIA_DIR = ".venoxia"
CHARTER = "charter.md"
CAPABILITIES_DIR = "capabilities"
CHANGES_DIR = "changes"
DELTA_DIR = "delta"
SPEC_FILENAME = "spec.md"
CHANGE_FILENAME = "change.json"
ORACLE_CONFIG = "venoxia.json"

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2

SCRIPTS_DIR = Path(__file__).resolve().parent
CHARTER_LINT = SCRIPTS_DIR / "charter_lint.py"
VALIDATE = SCRIPTS_DIR / "validate.py"
ORACLE = SCRIPTS_DIR / "oracle.py"


class CannotCheck(Exception):
    """Una comprobación que no se ha podido llevar a cabo. Nunca es un `0`."""


def run(argv: list[str], cwd: Path) -> int:
    """Lanza un script de Venoxia dejando que escriba su propia salida.

    Sin capturarla ni filtrarla: un `1` mudo bloquea la rama sin decir qué
    falló ni en qué requisito.
    """
    try:
        completed = subprocess.run([sys.executable, *argv], cwd=str(cwd))
    except OSError as error:
        raise CannotCheck(f"no se pudo ejecutar «{argv[0]}»: {error}") from error
    return completed.returncode


def require_script(path: Path) -> None:
    if not path.is_file():
        raise CannotCheck(
            f"falta «{path}», que es parte de Venoxia: sin él no hay comprobación "
            "que hacer, y una puerta que no comprueba no puede aprobar."
        )


def read_change(change_dir: Path) -> str:
    """El `state` normalizado de un change, o un `CannotCheck` con el motivo.

    «Verified» y « verified » son el estado que nombran; un valor que no esté
    en el ciclo de vida, o un fichero ilegible, no se salta.
    """
    change_file = change_dir / CHANGE_FILENAME
    if not change_file.is_file():
        raise CannotCheck(f"«{change_dir.name}» no tiene {CHANGE_FILENAME}")
    try:
        data = json.loads(change_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise CannotCheck(f"«{change_dir.name}»: {error}") from error
    if not isinstance(data, dict):
        raise CannotCheck(f"«{change_dir.name}»: change.json no es un objeto")
    raw = data.get("state")
    if not isinstance(raw, str) or not raw.strip():
        raise CannotCheck(f"«{change_dir.name}»: sin «state»")
    state = raw.strip().lower()
    if state not in LIFECYCLE_STATES:
        raise CannotCheck(f"«{change_dir.name}»: estado desconocido «{raw}»")
    return state


def delta_files(change_dir: Path) -> list[Path]:
    delta_dir = change_dir / DELTA_DIR
    return sorted(delta_dir.glob("*.md")) if delta_dir.is_dir() else []


def declares_requirement(path: Path) -> bool:
    """Si un markdown declara al menos un requisito.

    Un `spec.md` vaciado, o un `delta/notas.md` sin un solo requisito, están tan
    vacíos como no existir: aprobarlos por vacuidad sacaría de la verificación
    todo lo que declaraban sin mover el recuento.
    """
    try:
        texto = path.read_text(encoding="utf-8")
    except OSError as error:
        raise CannotCheck(f"no se pudo leer «{path}»: {error}") from error
    return any(
        linea.startswith("### ") and "·" in linea for linea in texto.splitlines()
    )


def oracle_command(root: Path) -> None:
    """Comprueba que la configuración del oráculo sirva para algo.

    Detectar sólo la ausencia haría que corromper este fichero saliera más
    barato que borrarlo: la puerta correría el oráculo con un comando vacío, no
    obtendría ningún rojo y daría verde informando de N oráculos mirados.
    """
    config = root / VENOXIA_DIR / ORACLE_CONFIG
    if not config.is_file():
        raise CannotCheck(f"falta «{VENOXIA_DIR}/{ORACLE_CONFIG}»")
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise CannotCheck(f"«{VENOXIA_DIR}/{ORACLE_CONFIG}»: {error}") from error
    command = data.get("test_command") if isinstance(data, dict) else None
    if not isinstance(command, str) or not command.strip():
        raise CannotCheck(
            f"«{VENOXIA_DIR}/{ORACLE_CONFIG}» no declara un «test_command» utilizable"
        )


def gate(root: Path) -> int:
    """El veredicto. Las tres comprobaciones se hacen siempre, sin pararse."""
    venoxia = root / VENOXIA_DIR
    if not venoxia.is_dir():
        raise CannotCheck(
            f"«{root}» no tiene {VENOXIA_DIR}/: no hay nada que comprobar ahí. "
            "Los otros scripts de Venoxia tratan esto como un aviso; la puerta "
            "no, porque a ella se la invoca sobre un proyecto del que se afirma "
            "que cumple, y un --root mal escrito no puede dar verde."
        )

    problemas: list[str] = []
    fallos = 0

    # --- El acta ---------------------------------------------------------
    require_script(CHARTER_LINT)
    charter = venoxia / CHARTER
    if not charter.is_file():
        raise CannotCheck(f"falta «{VENOXIA_DIR}/{CHARTER}»")
    try:
        # Que exista no basta: si no se deja leer, `charter_lint.py` la
        # rechazaría como un incumplimiento del proyecto cuando en realidad es
        # una comprobación que no se ha podido hacer.
        charter.read_text(encoding="utf-8")
    except OSError as error:
        raise CannotCheck(f"no se puede leer «{VENOXIA_DIR}/{CHARTER}»: {error}") from error
    if run([str(CHARTER_LINT), "--root", str(root), "--strict"], root) != 0:
        fallos += 1

    # --- Las specs y los deltas de los changes ya acordados ---------------
    require_script(VALIDATE)
    specs: list[Path] = []
    caps_dir = venoxia / CAPABILITIES_DIR
    if caps_dir.is_dir():
        for capability in sorted(x for x in caps_dir.iterdir() if x.is_dir()):
            spec = capability / SPEC_FILENAME
            if not spec.is_file():
                problemas.append(f"«{capability.name}» no tiene {SPEC_FILENAME}")
                continue
            if not declares_requirement(spec):
                problemas.append(f"«{capability.name}» no declara ni un requisito")
                continue
            specs.append(spec)

    deltas: list[Path] = []
    gated: list[str] = []
    sin_ejecutar: list[str] = []
    total_changes = 0
    changes_dir = venoxia / CHANGES_DIR
    if changes_dir.is_dir():
        for change_dir in sorted(x for x in changes_dir.iterdir() if x.is_dir()):
            total_changes += 1
            try:
                state = read_change(change_dir)
            except CannotCheck as error:
                problemas.append(str(error))
                continue
            if state not in VALIDATED_STATES:
                continue
            propios = [x for x in delta_files(change_dir) if declares_requirement(x)]
            if not propios:
                problemas.append(f"«{change_dir.name}» está en «{state}» sin requisitos")
                continue
            deltas.extend(propios)
            if state in GATED_STATES:
                gated.append(change_dir.name)
            else:
                sin_ejecutar.append(change_dir.name)

    objetivos = [str(x) for x in specs + deltas]
    if objetivos and run([str(VALIDATE), "--root", str(root), "--strict", *objetivos], root):
        fallos += 1

    # --- El oráculo de cada change en «verified» --------------------------
    if gated:
        require_script(ORACLE)
        oracle_command(root)
        for change_id in gated:
            print(f"== oracle.py --change {change_id} ==", flush=True)
            if run([str(ORACLE), "--root", str(root), "--change", change_id], root):
                problemas.append(f"«{change_id}» tiene el oráculo en rojo")

    # --- El resumen, al final y sólo cuando los tres han terminado --------
    for problema in problemas:
        print(f"venoxia-gate: {problema}", file=sys.stderr)
    print(
        f"venoxia-gate: mirado el acta, {len(specs)} spec.md, "
        f"{total_changes} changes y {len(gated)} oráculos"
        + (
            f"; sin ejecutar en «validated»: {', '.join(sin_ejecutar)}"
            if sin_ejecutar
            else ""
        ),
        flush=True,
    )
    return EXIT_FAIL if fallos or problemas else EXIT_OK


def build_cli() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(
        prog="gate.py",
        description=(
            "La puerta de Venoxia: corre el acta, el validador y el oráculo de "
            "cada change en «verified», y da un veredicto único. "
            "AVISO: ejecuta el «test_command» que declara el proyecto "
            "inspeccionado, así que no la lances con secretos en su entorno "
            "sobre código que no es de fiar —el de un pull request de un fork, "
            "por ejemplo—: correría comandos de quien lo escribió con las "
            "credenciales de tu runner."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Códigos de salida: 0 cumple · 1 no cumple · 2 no se pudo comprobar.",
    )
    cli.add_argument(
        "--root",
        metavar="DIR",
        help="raíz del proyecto, la que contiene .venoxia/ (por defecto, el actual)",
    )
    return cli


def main(argv: list[str] | None = None) -> int:
    args = build_cli().parse_args(argv)
    root = Path(os.path.expanduser(args.root)) if args.root else Path.cwd()
    if not root.is_dir():
        print(f"venoxia-gate: «{root}» no es un directorio.", file=sys.stderr)
        return EXIT_USAGE
    try:
        return gate(root.resolve())
    except CannotCheck as error:
        print(f"venoxia-gate: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
