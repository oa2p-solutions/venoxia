#!/usr/bin/env python3
"""CI en GitHub Actions: el workflow del propio plugin y la plantilla del consumidor.

La tesis del README es «la spec deja de ser prosa y pasa a ser un contrato que
falla en CI cuando miente». Este fichero comprueba, sin tocar la red ni
lanzar ningún workflow de verdad —GitHub Actions no se puede invocar desde
`unittest`—, que los ficheros que hacen esa promesa cumplible existen y
declaran la forma que prometen: disparadores, jobs, comandos exactos y, para
el proyecto consumidor, la plantilla que hace checkout de un Venoxia fijado
por versión y corre la puerta sin `pip`.

Lo que este fichero **no** puede comprobar —porque exige un run real de
GitHub Actions, no disponible aquí— son las dos mitades dinámicas del
criterio de aceptación: que la matriz efectivamente pasa en 3.12/3.13/3.14
sobre los runners de GitHub (R-CI-006), y que un `SHALL` introducido a
propósito hace fallar el job `self-spec` en un run real. Tampoco puede
comprobar si `claude plugin validate` exige credenciales en un runner
limpio sin sesión previa (R-CI-007); para esas dos apuestas, este fichero
sólo aporta la evidencia local parcial que su «why» declara. Todo queda
documentado como huecos en `README.md` y en la entrega de este change.

@covers R-CI-001
@covers R-CI-002
@covers R-CI-003
@covers R-CI-004
@covers R-CI-005
@covers R-CI-006
@covers R-CI-007

Cómo lanzarlo::

    python3 -m unittest tests.test_ci_workflow -v
    python3 -m unittest discover -s tests -v
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

CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
GATE_PATH = REPO_ROOT / "templates" / "ci" / "venoxia-gate.yml"
README_PATH = REPO_ROOT / "README.md"


def _read(path: Path, what: str) -> str:
    if not path.is_file():
        raise AssertionError(f"no existe «{path.relative_to(REPO_ROOT)}»: falta {what}.")
    return path.read_text(encoding="utf-8")


def _job_block(text: str, job_name: str) -> str:
    """El bloque de un job, desde su línea `  <job_name>:` hasta el siguiente job
    de primer nivel (dos espacios de indentación) o el final del fichero."""
    pattern = re.compile(
        rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z][\w-]*:\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise AssertionError(f"«{CI_PATH.name}» no declara el job «{job_name}»")
    return match.group(0)


class CiWorkflowTriggersAndJobsTest(unittest.TestCase):
    """R-CI-001 · Disparadores y los cinco jobs, todos nombrados y presentes."""

    def test_ci_file_exists(self):
        self.assertTrue(CI_PATH.is_file(), f"falta «{CI_PATH}»")

    def test_triggers_push_pull_request_and_dispatch_on_main(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        self.assertRegex(
            text, re.compile(r"^on:\s*$", re.MULTILINE), "no declara el bloque «on:» de disparadores"
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
        text = _read(CI_PATH, "el workflow de CI del plugin")
        for job_name in ("tests", "self-spec", "coverage", "plugin-validate", "evals"):
            _job_block(text, job_name)  # lanza AssertionError si falta

    def test_tests_job_covers_the_three_supported_python_versions(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        job = _job_block(text, "tests")
        for version in ("3.12", "3.13", "3.14"):
            self.assertIn(
                f'"{version}"',
                job,
                f"el job «tests» no incluye Python {version} en su matriz",
            )
        self.assertIn(
            "python3 -m unittest discover -s tests -q",
            job,
            "el job «tests» no ejecuta la suite con el comando canónico",
        )


class CiSelfSpecCommandsTest(unittest.TestCase):
    """R-CI-002 · El job self-spec ejecuta los comandos exactos, en estricto."""

    def test_self_spec_runs_validate_and_charter_lint_in_strict_json(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        job = _job_block(text, "self-spec")
        self.assertIn(
            "python3 scripts/validate.py --root . --strict --json",
            job,
            "el job «self-spec» no corre validate.py --root . --strict --json",
        )
        self.assertIn(
            "python3 scripts/charter_lint.py --root . --strict --json",
            job,
            "el job «self-spec» no corre charter_lint.py --root . --strict --json",
        )


class CiPluginValidateAndEvalsTest(unittest.TestCase):
    """R-CI-003 · plugin-validate instala el CLI y valida; evals es manual."""

    def test_plugin_validate_installs_cli_and_runs_strict_validate(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        job = _job_block(text, "plugin-validate")
        self.assertIn("npm install", job, "el job «plugin-validate» no instala nada con npm")
        self.assertIn(
            "claude-code",
            job,
            "el job «plugin-validate» no instala el paquete del CLI de Claude Code",
        )
        self.assertIn(
            "claude plugin validate . --strict",
            job,
            "el job «plugin-validate» no ejecuta «claude plugin validate . --strict»",
        )

    def test_evals_job_is_manual_and_needs_the_api_key(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        job = _job_block(text, "evals")
        self.assertRegex(
            job,
            r"if:\s*\$\{\{\s*github\.event_name\s*==\s*'workflow_dispatch'\s*\}\}",
            "el job «evals» no está restringido a «workflow_dispatch»",
        )
        self.assertIn(
            "secrets.ANTHROPIC_API_KEY",
            job,
            "el job «evals» no declara «secrets.ANTHROPIC_API_KEY»",
        )
        self.assertIn(
            "claude plugin eval venoxia",
            job,
            "el job «evals» no ejecuta el comando de evals/README.md",
        )


class CiMatrixRealRunGapTest(unittest.TestCase):
    """R-CI-006 · Apuesta: que la matriz pase de verdad en GitHub Actions.

    Esto no se puede confirmar aquí (exige un run real, prohibido en esta
    sesión, y esta máquina no tiene Python 3.12 instalado). Lo único que
    esta clase aporta es la evidencia local parcial que el «why» del
    requisito declara: que el intérprete que corre esta comprobación es
    uno de los tres que la matriz declara.
    """

    def test_local_interpreter_is_one_of_the_declared_matrix_versions(self):
        declared = {(3, 12), (3, 13), (3, 14)}
        self.assertIn(
            sys.version_info[:2],
            declared,
            "el intérprete que corre esta suite no es ninguno de los "
            "declarados en la matriz de «tests»; incluso esa evidencia "
            "local parcial se pierde",
        )


class CiPluginValidateSafetyNetTest(unittest.TestCase):
    """R-CI-007 · Apuesta: si el CLI exige credenciales en un runner limpio.

    No se puede confirmar aquí porque esta máquina ya tiene una sesión de
    Claude Code autenticada. Lo que sí se puede comprobar localmente es que
    la mitigación (`continue-on-error: true`) sigue declarada mientras esa
    pregunta no tenga respuesta.
    """

    def test_plugin_validate_job_has_a_continue_on_error_safety_net(self):
        text = _read(CI_PATH, "el workflow de CI del plugin")
        job = _job_block(text, "plugin-validate")
        self.assertIn(
            "continue-on-error: true",
            job,
            "el job «plugin-validate» no declara «continue-on-error: "
            "true»: si «claude plugin validate» exige credenciales en un "
            "runner limpio, bloquearía todo el workflow",
        )


class VenoxiaGateTemplateTest(unittest.TestCase):
    """R-CI-004 · La plantilla del consumidor hace checkout fijado y sin pip."""

    def test_gate_template_exists(self):
        self.assertTrue(GATE_PATH.is_file(), f"falta «{GATE_PATH}»")

    def test_checks_out_project_and_a_pinned_venoxia_with_a_token(self):
        text = _read(GATE_PATH, "la plantilla templates/ci/venoxia-gate.yml")
        self.assertIn(
            "oa2p-solutions/venoxia",
            text,
            "la plantilla no hace checkout de oa2p-solutions/venoxia",
        )
        self.assertIn(
            "VENOXIA_REF",
            text,
            "la plantilla no fija el checkout de Venoxia a una referencia (tag)",
        )
        self.assertIn(
            "secrets.VENOXIA_TOKEN",
            text,
            "la plantilla no usa un token de secrets para el checkout privado",
        )

    def test_runs_charter_lint_and_validate_in_strict_without_pip(self):
        text = _read(GATE_PATH, "la plantilla templates/ci/venoxia-gate.yml")
        self.assertIn("charter_lint.py", text)
        self.assertIn("validate.py", text)
        self.assertIn("--strict", text)
        self.assertNotIn(
            "pip install",
            text,
            "la plantilla del consumidor no puede depender de pip",
        )

    def test_runs_oracle_per_validated_or_verified_change_when_venoxia_json_exists(self):
        text = _read(GATE_PATH, "la plantilla templates/ci/venoxia-gate.yml")
        self.assertIn("venoxia.json", text)
        self.assertIn("oracle.py", text)
        self.assertIn("--change", text)
        for state in ("validated", "verified"):
            self.assertIn(
                state,
                text,
                f"la plantilla no menciona el estado «{state}» al filtrar los changes",
            )


class ReadmeCiSectionTest(unittest.TestCase):
    """R-CI-005 · README explica los dos workflows y por qué evals es manual."""

    def test_readme_has_the_ci_section(self):
        text = _read(README_PATH, "README.md")
        self.assertRegex(
            text,
            re.compile(r"^## Verificar en CI\s*$", re.MULTILINE),
            "README.md no tiene la sección «## Verificar en CI»",
        )

    def test_section_names_both_workflows_and_the_manual_evals_reason(self):
        text = _read(README_PATH, "README.md")
        match = re.search(
            r"^## Verificar en CI\s*$(.*?)(?=^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "no se pudo extraer el cuerpo de «## Verificar en CI»")
        section = match.group(1)
        self.assertIn(".github/workflows/ci.yml", section)
        self.assertIn("templates/ci/venoxia-gate.yml", section)
        self.assertIn("workflow_dispatch", section)


if __name__ == "__main__":
    unittest.main()
