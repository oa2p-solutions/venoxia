#!/usr/bin/env python3
"""El CI de este repositorio, y que sea el único que hay.

Este fichero es el contrato entero del workflow: se lee del disco y se
comprueba solo, sin compararlo con ningún otro. Antes existían dos —uno por
forja— y el segundo se medía **contra** el primero, comando a comando; un
espejo sin original no comprueba nada, así que ahora el contrato se enuncia
aquí y el fichero se mide contra él.

Lo que no puede nombrar, y por eso también se comprueba: el repositorio es
público, así que una etiqueta de runner escrita a mano publicaría a cada
persona que lo clone el mapa de una infraestructura que no es suya. Los
`runs-on` leen una variable del repositorio.

@covers R-CI-008
@covers R-CI-009
@covers R-CI-011
@covers R-CI-012

Cómo lanzarlo::

    python3 -m unittest tests.test_ci_workflow -v
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import REPO_ROOT  # noqa: E402

WORKFLOW = REPO_ROOT / ".forgejo" / "workflows" / "ci.yml"
GITHUB_WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

JOB_NAMES = ("tests", "self-spec", "coverage", "plugin-validate", "evals")
#: Un `runs-on` conforme es una expresión que lee una variable del
#: repositorio: `${{ vars.LO_QUE_SEA }}`. Cualquier otra cosa es una
#: etiqueta escrita a mano, que es lo que este repositorio no publica.
RUNS_ON_FROM_VARS = re.compile(r"^\$\{\{\s*vars\.[A-Za-z_][A-Za-z0-9_]*\s*\}\}$")

#: Los jobs que pueden fallar sin tumbar el workflow, y sólo ellos. `coverage`
#: mide huecos ya documentados en TODO.md; `plugin-validate` depende de la
#: apuesta B-004. Un `continue-on-error` en `tests` o en `self-spec` dejaría el
#: CI en verde permanente, que es exactamente la mentira que este CI existe
#: para impedir.
JOBS_WITH_SAFETY_NET = frozenset({"coverage", "plugin-validate"})

#: El comando que cada job tiene que ejecutar. Es el contrato entero de
#: `R-CI-012`: lo que antes se deducía comparando con el workflow de GitHub,
#: escrito aquí una sola vez.
EXPECTED_COMMANDS = {
    "tests": ("python3 -m unittest discover -s tests -q",),
    "self-spec": (
        "python3 scripts/validate.py --root . --strict --json",
        "python3 scripts/charter_lint.py --root . --strict --json",
    ),
    "coverage": ("python3 tools/coverage.py",),
    "plugin-validate": ("claude plugin validate . --strict",),
    "evals": ("claude plugin eval venoxia",),
}


def _read(path: Path, what: str) -> str:
    if not path.is_file():
        raise AssertionError(f"no existe «{path.relative_to(REPO_ROOT)}»: falta {what}.")
    return path.read_text(encoding="utf-8")


def _workflow() -> str:
    return _read(WORKFLOW, "el workflow de CI de este repositorio")


def _jobs_section(text: str) -> str:
    match = re.search(r"^jobs:\s*\n(.*)\Z", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise AssertionError("el workflow no declara el bloque «jobs:»")
    return match.group(1)


def _job_block(text: str, job_name: str) -> str:
    """El bloque de un job, desde su línea `  <job_name>:` hasta el siguiente job
    de primer nivel (dos espacios de indentación) o el final del fichero."""
    pattern = re.compile(
        rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z][\w-]*:\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(_jobs_section(text))
    if not match:
        raise AssertionError(
            f"«{WORKFLOW.relative_to(REPO_ROOT)}» no declara el job «{job_name}»"
        )
    return match.group(0)


def _run_commands(job: str) -> list[str]:
    """Los comandos `run:` de un job, normalizados: una línea por comando,
    con los bloques `run: |` aplanados quitando indentación y
    continuaciones de línea (`\\`)."""
    commands: list[str] = []
    lines = job.splitlines()
    i = 0
    while i < len(lines):
        match = re.match(r"^(\s*)(?:-\s+)?run:\s*(.*)$", lines[i])
        if not match:
            i += 1
            continue
        indent, rest = len(match.group(1)), match.group(2).strip()
        if rest in ("|", "|-", ">", ">-"):
            body: list[str] = []
            i += 1
            while i < len(lines) and (
                not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent
            ):
                body.append(lines[i].strip())
                i += 1
            joined = " ".join(part.rstrip("\\").strip() for part in body if part)
            commands.append(re.sub(r"\s+", " ", joined).strip())
            continue
        commands.append(re.sub(r"\s+", " ", rest))
        i += 1
    return commands


class TheWorkflowIsTheOnlyCiTest(unittest.TestCase):
    """R-CI-011 · No queda ningún workflow de GitHub Actions en el repositorio."""

    def test_the_workflow_exists(self):
        self.assertTrue(WORKFLOW.is_file(), f"falta «{WORKFLOW}»")

    def test_no_github_actions_workflow_directory(self):
        self.assertFalse(
            GITHUB_WORKFLOWS_DIR.exists(),
            f"«{GITHUB_WORKFLOWS_DIR.relative_to(REPO_ROOT)}» sigue existiendo: el "
            "proyecto ha dejado de usar GitHub, y un workflow que nadie ejecuta "
            "promete una puerta que no existe",
        )

    def test_no_workflow_file_anywhere_under_dot_github(self):
        """No basta con que falte `workflows/`: GitHub Actions también recoge lo
        que cuelgue de `.github/` por otras vías, y dejar un `ci.yml` suelto ahí
        sería la misma promesa sin cumplir con otro nombre."""
        github_dir = REPO_ROOT / ".github"
        if not github_dir.exists():
            return
        strays = sorted(
            path.relative_to(REPO_ROOT).as_posix()
            for path in github_dir.rglob("*")
            if path.is_file() and path.suffix in (".yml", ".yaml")
        )
        self.assertEqual(
            strays,
            [],
            f"quedan ficheros de workflow bajo «.github/»: {', '.join(strays)}",
        )


class WorkflowTriggersAndJobsTest(unittest.TestCase):
    """R-CI-008 · Disparadores, los cinco jobs y sólo las etiquetas del runner."""

    def test_triggers_push_pull_request_and_dispatch_on_main(self):
        text = _workflow()
        self.assertRegex(
            text,
            re.compile(r"^on:\s*$", re.MULTILINE),
            "no declara el bloque «on:» de disparadores",
        )
        self.assertRegex(
            text,
            r"push:\s*\n\s*branches:\s*\[?\s*main",
            "«push» no está acotado a la rama «main»",
        )
        self.assertRegex(
            text,
            r"pull_request:\s*\n\s*branches:\s*\[?\s*main",
            "«pull_request» no está acotado a la rama «main»",
        )
        self.assertIn(
            "workflow_dispatch:",
            text,
            "falta el disparador manual «workflow_dispatch»",
        )

    def test_five_jobs_are_declared(self):
        text = _workflow()
        for job_name in JOB_NAMES:
            _job_block(text, job_name)  # lanza AssertionError si falta

    def test_no_runner_label_is_written_down(self):
        """El repositorio es público: una etiqueta escrita a mano publicaría el
        mapa de una infraestructura que no es de quien clona el plugin."""
        text = _workflow()
        valores = re.findall(r"^\s*runs-on:\s*(.+?)\s*$", text, re.MULTILINE)
        self.assertTrue(valores, "ningún job declara «runs-on»")
        for valor in valores:
            self.assertRegex(
                valor.strip("\"'"),
                RUNS_ON_FROM_VARS,
                f"«runs-on: {valor}» escribe el runner en vez de leerlo de una "
                "variable del repositorio",
            )

    def test_the_workflow_names_no_internal_infrastructure(self):
        """Los comentarios cuentan: son lo primero que lee quien abre el fichero."""
        text = _workflow().lower()
        for termino in ("oa2p-debian", "oa2p-node", "forgejo"):
            self.assertNotIn(
                termino,
                text,
                f"el workflow nombra «{termino}»: el repositorio es público y eso "
                "no le sirve a quien instala el plugin",
            )


class TestsMatrixFromImageTest(unittest.TestCase):
    """R-CI-009 · La matriz nombra 3.12/3.13/3.14 y el intérprete viene de la imagen."""

    def test_matrix_names_the_three_supported_python_versions(self):
        job = _job_block(_workflow(), "tests")
        for version in ("3.12", "3.13", "3.14"):
            self.assertIn(
                f'"{version}"',
                job,
                f"el job «tests» no incluye Python {version} en su matriz",
            )

    def test_tests_job_runs_inside_a_python_slim_image_per_matrix_entry(self):
        job = _job_block(_workflow(), "tests")
        self.assertRegex(
            job,
            r"container:\s*\n\s*image:\s*\S*python:\$\{\{\s*matrix\.python-version\s*\}\}-slim",
            "el job «tests» no declara «container» con la imagen "
            "«python:${{ matrix.python-version }}-slim»",
        )
        self.assertNotIn(
            "actions/setup-python",
            job,
            "el job «tests» no debe usar setup-python: el intérprete viene de la imagen",
        )

    def test_local_interpreter_is_one_of_the_declared_matrix_versions(self):
        """B-003 · Que la matriz pase de verdad en el runner exige un run real.
        Lo único que se puede aportar aquí es la evidencia local parcial: que
        el intérprete que corre esta suite es uno de los tres declarados."""
        self.assertIn(
            sys.version_info[:2],
            {(3, 12), (3, 13), (3, 14)},
            "el intérprete que corre esta suite no es ninguno de los declarados "
            "en la matriz de «tests»; incluso esa evidencia local parcial se pierde",
        )


class WorkflowCommandsTest(unittest.TestCase):
    """R-CI-012 · Los comandos exactos de cada job, leídos de un solo fichero."""

    def test_every_job_runs_the_commands_its_contract_declares(self):
        text = _workflow()
        for job_name, expected in EXPECTED_COMMANDS.items():
            actual = _run_commands(_job_block(text, job_name))
            for command in expected:
                # «Ejecuta» el comando: literal, tal cual o envuelto. `tests` y
                # `coverage` lo envuelven en `su ci -c "…"` porque el job corre
                # como root en el contenedor y root se salta los tests de
                # permisos.
                self.assertTrue(
                    any(command in step for step in actual),
                    f"el job «{job_name}» no ejecuta «{command}»; sus pasos: {actual}",
                )


class WorkflowSafetyNetsTest(unittest.TestCase):
    """R-CI-012 · Las redes de seguridad están donde tienen que estar, y sólo ahí."""

    def test_exactly_two_jobs_carry_a_continue_on_error(self):
        text = _workflow()
        with_net = {
            job_name
            for job_name in JOB_NAMES
            if "continue-on-error: true" in _job_block(text, job_name)
        }
        self.assertEqual(
            with_net,
            set(JOBS_WITH_SAFETY_NET),
            "los jobs con «continue-on-error» no son exactamente «coverage» y "
            "«plugin-validate»: una red de más en «tests» o en «self-spec» deja "
            "el CI en verde permanente",
        )

    def test_only_the_manual_job_declares_a_condition(self):
        """Un `if:` en cualquier otro job lo apaga sin que se note.

        No basta con prohibir `if: false`: un `if: github.repository == '…'`
        que nunca se cumple deja el CI en verde permanente sin ejecutar la
        suite, y no es una constante. El único `if:` legítimo es el que
        limita `evals` a `workflow_dispatch`.
        """
        text = _workflow()
        with_condition = {
            job_name
            for job_name in JOB_NAMES
            if re.search(r"^    if:", _job_block(text, job_name), re.MULTILINE)
        }
        self.assertEqual(
            with_condition,
            {"evals"},
            "sólo «evals» puede declarar «if:»; en cualquier otro job es un "
            "interruptor para apagarlo sin que el informe lo diga",
        )

    def test_no_job_depends_on_the_manual_one(self):
        """`needs: evals` saltaría los cuatro jobs en cada push y pull request.

        `evals` sólo corre con `workflow_dispatch`; un job que dependa de él
        se salta siempre que no se lance a mano, y un job saltado no pone el
        run en rojo.
        """
        text = _workflow()
        for job_name in ("tests", "self-spec", "coverage", "plugin-validate"):
            needs = re.search(r"^    needs:.*$", _job_block(text, job_name), re.MULTILINE)
            if needs is None:
                continue
            self.assertNotIn(
                "evals",
                needs.group(0),
                f"el job «{job_name}» depende de «evals», que sólo corre a mano: "
                "en cada push se saltaría sin dejar el run en rojo",
            )

    def test_no_step_of_the_gate_jobs_is_conditional(self):
        """Un `if:` a nivel de paso apaga la suite dejando el job encendido."""
        text = _workflow()
        for job_name in ("tests", "self-spec", "coverage", "plugin-validate"):
            self.assertNotRegex(
                _job_block(text, job_name),
                r"^\s+if:",
                f"un paso del job «{job_name}» declara «if:»: se puede apagar "
                "lo que ejecuta sin apagar el job",
            )

    def test_no_command_hides_its_own_exit_code(self):
        """`|| echo …` y `if ! …` dejan un comando en rojo con el job en verde.

        Prohibir sólo `|| true` era una lista que se esquiva cambiando lo que
        va detrás del `||`.
        """
        text = _workflow()
        for job_name in JOB_NAMES:
            for command in _run_commands(_job_block(text, job_name)):
                self.assertNotIn(
                    "||",
                    command,
                    f"el job «{job_name}» enmascara un fallo con «||»: {command}",
                )
                self.assertNotIn(
                    "if !",
                    command,
                    f"el job «{job_name}» enmascara un fallo con «if !»: {command}",
                )

    def test_the_suite_command_is_not_narrowed_by_extra_arguments(self):
        """Un `-p 'no_such_*.py'` detrás contiene la cadena y descubre cero tests."""
        job = _job_block(_workflow(), "tests")
        canonical = "python3 -m unittest discover -s tests -q"
        self.assertTrue(
            any(command.rstrip('"').endswith(canonical) for command in _run_commands(job)),
            f"ningún comando del job «tests» termina en «{canonical}»: un "
            "argumento añadido detrás puede reducir lo que la suite descubre",
        )

    def test_the_api_key_appears_only_inside_the_evals_job(self):
        """En un `env:` de workflow la heredaría `tests`, que corre código de PR."""
        text = _workflow()
        evals = _job_block(text, "evals")
        self.assertIn("secrets.ANTHROPIC_API_KEY", evals)
        outside = text.replace(evals, "")
        self.assertNotIn(
            "ANTHROPIC_API_KEY",
            outside,
            "la clave aparece fuera del job «evals»: el job «tests» ejecuta el "
            "código de cada pull request y la heredaría",
        )

    def test_no_checkout_pins_a_reference(self):
        """Un checkout con `ref:` correría sobre otro commit que el del run."""
        text = _workflow()
        for job_name in JOB_NAMES:
            self.assertNotRegex(
                _job_block(text, job_name),
                r"^\s+ref:",
                f"el checkout del job «{job_name}» fija «ref»: el job no correría "
                "sobre el commit que disparó el run",
            )

    def test_every_job_checks_out_the_commit_under_test(self):
        """Sin `actions/checkout` la suite correría sobre el árbol que dejó el
        run anterior en el runner."""
        text = _workflow()
        for job_name in JOB_NAMES:
            self.assertIn(
                "uses: actions/checkout@",
                _job_block(text, job_name),
                f"el job «{job_name}» no hace checkout del commit",
            )

    def test_evals_job_is_manual(self):
        job = _job_block(_workflow(), "evals")
        self.assertRegex(
            job,
            r"if:\s*\$\{\{\s*\w+\.event_name\s*==\s*'workflow_dispatch'\s*\}\}",
            "el job «evals» no está restringido a «workflow_dispatch»",
        )

    def test_evals_job_needs_the_api_key(self):
        job = _job_block(_workflow(), "evals")
        self.assertIn(
            "secrets.ANTHROPIC_API_KEY",
            job,
            "el job «evals» no declara «secrets.ANTHROPIC_API_KEY»",
        )

    def test_plugin_validate_keeps_its_safety_net_while_b004_is_open(self):
        """B-004 · Mientras no se sepa si el CLI exige credenciales en un runner
        limpio, quitar esta red bloquearía el workflow entero."""
        job = _job_block(_workflow(), "plugin-validate")
        self.assertIn(
            "continue-on-error: true",
            job,
            "el job «plugin-validate» no declara «continue-on-error: true»",
        )


if __name__ == "__main__":
    unittest.main()
