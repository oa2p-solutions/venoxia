#!/usr/bin/env python3
"""CI en Forgejo Actions: el espejo del workflow del plugin sobre el runner interno.

`.github/workflows/ci.yml` es el CI del plugin en GitHub Actions; este
fichero comprueba que `.forgejo/workflows/ci.yml` lo espeja sobre el
`forgejo-runner` interno de la organización, sin tocar la red ni lanzar
ningún workflow de verdad: los mismos disparadores, los mismos cinco jobs,
los mismos comandos `run:` job a job y las mismas redes de seguridad
(`continue-on-error`, `evals` sólo a mano). Lo que cambia respecto a GitHub
es lo que el runner interno impone: `runs-on` sólo con las etiquetas que
ese runner declara (`oa2p-debian`, `oa2p-node`) y, como el host sólo tiene
Python 3.14, cada entrada de la matriz de `tests` corre dentro de una
imagen `python:<versión>-slim` en vez de usar `actions/setup-python`.

Sin PyYAML —la suite es stdlib pura— los dos ficheros se leen con
expresiones regulares sobre su forma canónica: jobs de primer nivel con dos
espacios de indentación, `run:` de una línea o de bloque `|`.

@covers R-CI-008
@covers R-CI-009
@covers R-CI-010

Cómo lanzarlo::

    python3 -m unittest tests.test_forgejo_workflow -v
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

GITHUB_CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
FORGEJO_CI = REPO_ROOT / ".forgejo" / "workflows" / "ci.yml"
README_PATH = REPO_ROOT / "README.md"

JOB_NAMES = ("tests", "self-spec", "coverage", "plugin-validate", "evals")
RUNNER_LABELS = frozenset({"oa2p-debian", "oa2p-node"})


def _read(path: Path, what: str) -> str:
    if not path.is_file():
        raise AssertionError(f"no existe «{path.relative_to(REPO_ROOT)}»: falta {what}.")
    return path.read_text(encoding="utf-8")


def _jobs_section(text: str) -> str:
    match = re.search(r"^jobs:\s*\n(.*)\Z", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise AssertionError("el workflow no declara el bloque «jobs:»")
    return match.group(1)


def _job_block(text: str, job_name: str, where: Path) -> str:
    """El bloque de un job, desde su línea `  <job_name>:` hasta el siguiente job
    de primer nivel (dos espacios de indentación) o el final del fichero."""
    pattern = re.compile(
        rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z][\w-]*:\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(_jobs_section(text))
    if not match:
        raise AssertionError(f"«{where.relative_to(REPO_ROOT)}» no declara el job «{job_name}»")
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


class ForgejoWorkflowTriggersAndJobsTest(unittest.TestCase):
    """R-CI-008 · Disparadores, los cinco jobs y sólo las etiquetas del runner."""

    def test_forgejo_workflow_exists(self):
        self.assertTrue(FORGEJO_CI.is_file(), f"falta «{FORGEJO_CI}»")

    def test_triggers_push_pull_request_and_dispatch_on_main(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
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
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        for job_name in JOB_NAMES:
            _job_block(text, job_name, FORGEJO_CI)  # lanza AssertionError si falta

    def test_every_runs_on_is_a_label_the_internal_runner_declares(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        labels = re.findall(r"^\s*runs-on:\s*(.+?)\s*$", text, re.MULTILINE)
        self.assertTrue(labels, "ningún job declara «runs-on»")
        for label in labels:
            self.assertIn(
                label.strip("\"'"),
                RUNNER_LABELS,
                f"«runs-on: {label}» no es una etiqueta del runner interno "
                f"({', '.join(sorted(RUNNER_LABELS))})",
            )
        self.assertNotIn("ubuntu-latest", text, "el runner interno no conoce «ubuntu-latest»")


class ForgejoTestsMatrixFromImageTest(unittest.TestCase):
    """R-CI-009 · La matriz nombra 3.12/3.13/3.14 y el intérprete viene de la imagen."""

    def test_matrix_names_the_three_supported_python_versions(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        job = _job_block(text, "tests", FORGEJO_CI)
        for version in ("3.12", "3.13", "3.14"):
            self.assertIn(
                f'"{version}"',
                job,
                f"el job «tests» no incluye Python {version} en su matriz",
            )

    def test_tests_job_runs_inside_a_python_slim_image_per_matrix_entry(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        job = _job_block(text, "tests", FORGEJO_CI)
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


class ForgejoMirrorsGithubCommandsTest(unittest.TestCase):
    """R-CI-010 · Mismos comandos job a job, mismas redes de seguridad, evals manual."""

    def test_every_github_run_command_appears_in_the_same_forgejo_job(self):
        github = _read(GITHUB_CI, "el workflow de CI del plugin en GitHub")
        forgejo = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        for job_name in JOB_NAMES:
            expected = _run_commands(_job_block(github, job_name, GITHUB_CI))
            actual = _run_commands(_job_block(forgejo, job_name, FORGEJO_CI))
            self.assertTrue(expected, f"el job «{job_name}» de GitHub no tiene ningún «run:»")
            for command in expected:
                self.assertIn(
                    command,
                    actual,
                    f"el job «{job_name}» de Forgejo no ejecuta «{command}», "
                    f"que sí ejecuta el de GitHub",
                )

    def test_coverage_and_plugin_validate_keep_continue_on_error(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        for job_name in ("coverage", "plugin-validate"):
            job = _job_block(text, job_name, FORGEJO_CI)
            self.assertIn(
                "continue-on-error: true",
                job,
                f"el job «{job_name}» de Forgejo no declara «continue-on-error: true»",
            )

    def test_no_other_job_gets_a_safety_net_the_github_one_lacks(self):
        """Ataque del abogado del diablo: un `continue-on-error` en `tests` o
        `self-spec` (o un `if: false`) dejaría el CI interno en verde
        permanente. «Mismas redes de seguridad» es igualdad, no superconjunto."""
        github = _read(GITHUB_CI, "el workflow de CI del plugin en GitHub")
        forgejo = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        for job_name in JOB_NAMES:
            in_github = "continue-on-error" in _job_block(github, job_name, GITHUB_CI)
            forgejo_job = _job_block(forgejo, job_name, FORGEJO_CI)
            self.assertEqual(
                "continue-on-error" in forgejo_job,
                in_github,
                f"el job «{job_name}» difiere en «continue-on-error» entre los dos workflows",
            )
            self.assertNotRegex(
                forgejo_job,
                r"if:\s*(\$\{\{\s*)?false",
                f"el job «{job_name}» de Forgejo lleva un «if: false» que lo apaga",
            )

    def test_every_job_checks_out_the_commit_under_test(self):
        """Ataque del abogado del diablo: sin `actions/checkout` la suite correría
        sobre el árbol que dejó el run anterior en el runner."""
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        for job_name in JOB_NAMES:
            self.assertIn(
                "uses: actions/checkout@",
                _job_block(text, job_name, FORGEJO_CI),
                f"el job «{job_name}» de Forgejo no hace checkout del commit",
            )

    def test_evals_job_is_manual(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        job = _job_block(text, "evals", FORGEJO_CI)
        self.assertRegex(
            job,
            r"if:\s*\$\{\{\s*github\.event_name\s*==\s*'workflow_dispatch'\s*\}\}",
            "el job «evals» no está restringido a «workflow_dispatch»",
        )

    def test_evals_job_needs_the_api_key(self):
        text = _read(FORGEJO_CI, "el workflow de CI del plugin en Forgejo")
        job = _job_block(text, "evals", FORGEJO_CI)
        self.assertIn(
            "secrets.ANTHROPIC_API_KEY",
            job,
            "el job «evals» no declara «secrets.ANTHROPIC_API_KEY»",
        )


class ReadmeNamesTheForgejoWorkflowTest(unittest.TestCase):
    """Complemento de R-CI-008: el README nombra el segundo workflow y sus etiquetas."""

    def test_ci_section_mentions_the_forgejo_workflow_and_runner_labels(self):
        text = _read(README_PATH, "README.md")
        match = re.search(
            r"^## Verificar en CI\s*$(.*?)(?=^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "no se pudo extraer el cuerpo de «## Verificar en CI»")
        section = match.group(1)
        self.assertIn(".forgejo/workflows/ci.yml", section)
        for label in sorted(RUNNER_LABELS):
            self.assertIn(label, section, f"la sección no nombra la etiqueta «{label}»")


if __name__ == "__main__":
    unittest.main()
