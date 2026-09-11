#!/usr/bin/env python3
"""La puerta local: los jobs del CI, en un solo comando, antes de cada `push`.

Tres pasos, con el nombre del job del CI al que corresponden:

    matrix           la suite en cada versión de Python que declara la matriz
                     del workflow, dentro de `python:<versión>-slim`, como
                     usuario sin privilegios y en paralelo
    gate             python3 scripts/gate.py --root .   (acta, validador y
                     oráculo de cada change en «verified», sobre este repo;
                     ahí corre `tools/coverage.py` como runner de R-TEC-004)
    plugin-validate  claude plugin validate . --strict

La cobertura dejó de ser un paso propio en `2026-09-09-technical-contract`:
el gate ya la ejecuta como oráculo de un requisito, y medir dos veces lo
mismo eran dos minutos por push. `evals` se queda fuera a propósito: cuesta
tokens y se lanza a mano.

Códigos de salida, los del resto del núcleo:

    0   los tres pasos en verde
    1   algún paso en rojo
    2   no se pudo comprobar: falta un ejecutable, la matriz del workflow no
        se puede leer, o la invocación es incorrecta

Un paso que no se pudo ejecutar no es verde. La única forma de seguir sin la
matriz es pedirlo a mano con `--no-docker`, que deja el paso como omitido a
la vista en el resumen; el hook de `pre-push` nunca lo pasa.

Lo que `--list` imprime es, argumento por argumento, lo que se ejecuta: no
hay un comando «canónico» para enseñar y otro para correr. La matriz se lanza
en segundo plano y los otros tres pasos corren de uno en uno mientras tanto:
tres suites en contenedor, la suite instrumentada de la cobertura y los
oráculos de la puerta, todos a la vez sobre el mismo árbol, agotarían los
timeouts de los subprocesos y el veredicto dependería del planificador.

Sólo biblioteca estándar. Se ejecuta desde la raíz del repositorio::

    python3 tools/check.py
    python3 tools/check.py --list
    python3 tools/check.py --no-docker
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parent.parent
#: La matriz se lee del workflow, no de una lista propia: dos listas envejecen
#: por separado. La variable de entorno existe para que los tests puedan
#: apuntar a un workflow inventado; en uso normal no se toca.
WORKFLOW = Path(os.environ.get("VENOXIA_CHECK_WORKFLOW") or ROOT / ".forgejo" / "workflows" / "ci.yml")

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2

#: Líneas de la salida de un paso fallido que se enseñan en el resumen.
TAIL_LINES = 40

MATRIX_RE = re.compile(r"python-version:\s*\[([^\]]*)\]")


class UsageError(Exception):
    """No se pudo comprobar. Sale con 2, nunca con verde."""


@dataclass
class Step:
    """Un paso de la puerta: un nombre y uno o más comandos.

    Con varios comandos, el paso corre en paralelo y queda en verde sólo si
    todos terminan en verde. `skipped` lleva el motivo cuando el paso no se
    ejecuta a petición; un paso omitido no cuenta como fallo, y se dice.
    """

    name: str
    commands: list[list[str]]
    skipped: str | None = None


@dataclass
class Verdict:
    ok: bool
    seconds: float
    output: str = ""
    skipped: str | None = None
    commands: list[list[str]] = field(default_factory=list)


# --- Los pasos -----------------------------------------------------------------


def matrix_versions(workflow: Path = WORKFLOW) -> list[str]:
    """Las versiones de Python de la matriz del workflow, o `UsageError`."""
    try:
        text = workflow.read_text(encoding="utf-8")
    except OSError as error:
        raise UsageError(
            f"no se puede leer la matriz del workflow «{workflow}»: {error.strerror or error}"
        ) from None
    match = MATRIX_RE.search(text)
    versions = []
    if match:
        versions = [v.strip().strip("'\"") for v in match.group(1).split(",") if v.strip()]
    if not versions:
        raise UsageError(
            f"el workflow «{workflow}» no declara una matriz «python-version» legible: "
            "cero contenedores no comprueban nada"
        )
    return versions


def docker_command(version: str, root: Path = ROOT) -> list[str]:
    """La suite dentro de `python:<versión>-slim`, sin root y sin dejar contenedor."""
    return [
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", "HOME=/tmp",
        "-v", f"{root}:/w", "-w", "/w",
        f"python:{version}-slim",
        "python3", "-m", "unittest", "discover", "-s", "tests", "-q",
    ]


def build_steps(no_docker: bool) -> list[Step]:
    if no_docker:
        matrix = Step("matrix", [], skipped="omitido a petición (--no-docker)")
    else:
        matrix = Step("matrix", [docker_command(v) for v in matrix_versions()])
    return [
        matrix,
        Step("gate", [[sys.executable, "scripts/gate.py", "--root", "."]]),
        Step("plugin-validate", [["claude", "plugin", "validate", ".", "--strict"]]),
    ]


def matrix_label(command: list[str]) -> str:
    for token in command:
        if token.startswith("python:") and token.endswith("-slim"):
            return token[len("python:"):-len("-slim")]
    return "?"


def ensure_tools(steps: list[Step]) -> None:
    """Todo ejecutable que un paso necesite tiene que estar antes de empezar."""
    for step in steps:
        for command in step.commands:
            executable = command[0]
            if shutil.which(executable) is None:
                hint = ""
                if executable == "docker":
                    hint = " Con «--no-docker» la comprobación sigue sin la matriz, a la vista."
                raise UsageError(
                    f"falta «{executable}» en el PATH y el paso «{step.name}» lo necesita.{hint}"
                )
    if any(command[0] == "docker" for step in steps for command in step.commands):
        probe = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if probe.returncode != 0:
            raise UsageError(
                "el cliente «docker» está, pero el demonio no responde: arráncalo, o pasa "
                "«--no-docker» para seguir sin la matriz, a la vista."
            )


# --- La ejecución --------------------------------------------------------------


def _launch(command: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )


def _tail(text: str) -> str:
    lines = text.rstrip().splitlines()
    return "\n".join(lines[-TAIL_LINES:])


def run_steps(steps: list[Step], out: TextIO = sys.stdout) -> int:
    """Ejecuta los pasos y escribe el resumen. Devuelve el código de salida.

    Los pasos con varios comandos (la matriz) arrancan primero, en paralelo y
    en segundo plano; los demás corren de uno en uno mientras tanto. El
    veredicto de un paso con varios comandos es la agregación de todos: verde
    sólo si todos terminaron en verde.
    """
    verdicts: dict[str, Verdict] = {}
    background: dict[str, list[tuple[list[str], subprocess.Popen, float]]] = {}

    for step in steps:
        if step.skipped is not None:
            verdicts[step.name] = Verdict(ok=True, seconds=0.0, skipped=step.skipped)
        elif len(step.commands) > 1:
            background[step.name] = [(c, _launch(c), time.monotonic()) for c in step.commands]

    for step in steps:
        if step.skipped is not None or step.name in background:
            continue
        started = time.monotonic()
        ok, chunks = True, []
        for command in step.commands:
            done = subprocess.run(
                command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            chunks.append(done.stdout or "")
            ok = ok and done.returncode == 0
        verdicts[step.name] = Verdict(ok, time.monotonic() - started, "\n".join(chunks), commands=step.commands)

    for name, procs in background.items():
        ok, chunks = True, []
        started = min(t for _, _, t in procs)
        for command, proc, _ in procs:
            output, _ = proc.communicate()
            if proc.returncode != 0:
                ok = False
                chunks.append(f"$ {shlex.join(command)}\n{output or ''}")
        verdicts[name] = Verdict(ok, time.monotonic() - started, "\n".join(chunks), commands=[c for c, _, _ in procs])

    code = EXIT_OK
    for step in steps:
        verdict = verdicts[step.name]
        if verdict.skipped is not None:
            out.write(f"– {step.name:<16} {verdict.skipped}\n")
        elif verdict.ok:
            out.write(f"✓ {step.name:<16} {verdict.seconds:6.1f} s\n")
        else:
            code = EXIT_FAIL
            out.write(f"✗ {step.name:<16} {verdict.seconds:6.1f} s\n")
            for line in _tail(verdict.output).splitlines():
                out.write(f"    {line}\n")

    total = len(steps)
    red = sum(1 for v in verdicts.values() if not v.ok)
    skipped = sum(1 for v in verdicts.values() if v.skipped is not None)
    if code == EXIT_OK:
        summary = f"Puerta local en verde · {total - skipped} pasos"
        if skipped:
            summary += f" · {skipped} omitido a petición"
    else:
        summary = f"Puerta local en rojo · {red} de {total} pasos han fallado"
    out.write(summary + "\n")
    return code


# --- CLI ---------------------------------------------------------------------------


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        sys.stderr.write(f"tools/check.py: error de uso: {message}\n")
        sys.exit(EXIT_USAGE)


def build_cli() -> argparse.ArgumentParser:
    cli = _Parser(
        prog="tools/check.py",
        description="La puerta local de Venoxia: los jobs del CI en un solo comando, antes de cada push.",
        epilog="Códigos de salida: 0 todo en verde · 1 algún paso en rojo · 2 no se pudo comprobar.",
    )
    cli.add_argument("--list", action="store_true", help="imprime cada paso con su comando y no ejecuta nada")
    cli.add_argument("--no-docker", action="store_true", help="omite la matriz en contenedores, a la vista en el resumen")
    return cli


def list_steps(steps: list[Step], out: TextIO = sys.stdout) -> None:
    for step in steps:
        if step.skipped is not None:
            out.write(f"{step.name}: {step.skipped}\n")
        elif len(step.commands) > 1:
            for command in step.commands:
                out.write(f"{step.name}[{matrix_label(command)}]: {shlex.join(command)}\n")
        else:
            out.write(f"{step.name}: {shlex.join(step.commands[0])}\n")


def main(argv: list[str] | None = None) -> int:
    args = build_cli().parse_args(argv)
    try:
        steps = build_steps(no_docker=args.no_docker)
        if args.list:
            list_steps(steps)
            return EXIT_OK
        ensure_tools(steps)
    except UsageError as error:
        sys.stderr.write(f"tools/check.py: {error}\n")
        return EXIT_USAGE
    sys.stdout.write(f"Puerta local sobre {ROOT}\n")
    sys.stdout.flush()
    return run_steps(steps)


if __name__ == "__main__":
    sys.exit(main())
