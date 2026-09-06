#!/usr/bin/env python3
"""La plantilla de CI del proyecto consumidor, y lo que el README promete de ella.

`templates/ci/venoxia-gate.yml` no se ejecuta en este repositorio: se copia a
`.forgejo/workflows/venoxia-gate.yml` en un proyecto que ha adoptado Venoxia.
Este fichero comprueba, sin tocar la red ni lanzar ningún workflow, que la
plantilla declara la forma que promete —checkout de un Venoxia fijado por
tag, la etiqueta del runner interno, el intérprete desde la imagen, los dos
linters en `--strict`, ningún `pip`, y el oráculo por cada change activo— y
que la sección «## Verificar en CI» del README describe un único CI.

Lo que este fichero **no** puede comprobar es que la plantilla funcione tal
cual en un proyecto consumidor real: eso exige ese proyecto, su secret y un
run de verdad. Por eso no es un requisito del delta sino una suposición
declarada en su `proposal.md`, por la misma razón por la que `R-CI-006` y
`R-CI-007` salieron del delta anterior en la divergencia del 2026-09-05.

@covers R-CI-013
@covers R-CI-014
@covers R-CI-015

Cómo lanzarlo::

    python3 -m unittest tests.test_ci_template -v
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

GATE_PATH = REPO_ROOT / "templates" / "ci" / "venoxia-gate.yml"
README_PATH = REPO_ROOT / "README.md"

#: La única etiqueta que la plantilla puede pedir: el job corre Python, no Node.
RUNNER_LABEL = "oa2p-debian"


def _read(path: Path, what: str) -> str:
    if not path.is_file():
        raise AssertionError(f"no existe «{path.relative_to(REPO_ROOT)}»: falta {what}.")
    return path.read_text(encoding="utf-8")


def _template() -> str:
    return _read(GATE_PATH, "la plantilla templates/ci/venoxia-gate.yml")


def _run_commands(text: str) -> list[str]:
    """Los comandos `run:` del YAML, con los bloques `run: |` aplanados.

    Sin PyYAML —la suite es stdlib pura—, sobre la forma canónica del fichero:
    `run:` de una línea, o de bloque con el cuerpo más indentado.
    """
    commands: list[str] = []
    lines = text.splitlines()
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
            commands.append(re.sub(r"\s+", " ", " ".join(body)).strip())
            continue
        commands.append(re.sub(r"\s+", " ", rest))
        i += 1
    return commands


def _readme_ci_section() -> str:
    text = _read(README_PATH, "README.md")
    match = re.search(
        r"^## Verificar en CI\s*$(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError("README.md no tiene la sección «## Verificar en CI»")
    return match.group(1)


class GateTemplateTargetsForgejoTest(unittest.TestCase):
    """R-CI-013 · La plantilla apunta a Forgejo: repo, etiqueta, imagen, sin pip."""

    def test_template_exists(self):
        self.assertTrue(GATE_PATH.is_file(), f"falta «{GATE_PATH}»")

    def test_checks_out_a_pinned_venoxia_from_the_forgejo_repository(self):
        text = _template()
        self.assertIn(
            "repository: OA2P/venoxia",
            text,
            "la plantilla no hace checkout de «OA2P/venoxia», el repo de Forgejo",
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

    def test_does_not_name_the_retired_github_repository(self):
        text = _template()
        self.assertNotIn(
            "oa2p-solutions/venoxia",
            text,
            "la plantilla sigue apuntando al repo de GitHub, que ya no es la fuente",
        )
        self.assertNotIn(
            "github.com",
            text,
            "la plantilla nombra github.com: el proyecto ha dejado de usar GitHub",
        )

    def test_every_runs_on_is_the_internal_runner_label(self):
        text = _template()
        labels = re.findall(r"^\s*runs-on:\s*(.+?)\s*$", text, re.MULTILINE)
        self.assertTrue(labels, "la plantilla no declara ningún «runs-on»")
        for label in labels:
            self.assertEqual(
                label.strip("\"'"),
                RUNNER_LABEL,
                f"«runs-on: {label}» no es la etiqueta del runner interno "
                f"«{RUNNER_LABEL}»",
            )
        self.assertNotIn(
            "ubuntu-latest",
            text,
            "el runner interno no conoce «ubuntu-latest»",
        )

    def test_interpreter_comes_from_a_python_image_not_setup_python(self):
        text = _template()
        self.assertRegex(
            text,
            r"container:\s*\n\s*image:\s*\S*python:3\.14-slim",
            "la plantilla no declara «container» con la imagen «python:3.14-slim»",
        )
        self.assertNotIn(
            "actions/setup-python",
            text,
            "la plantilla no debe usar setup-python: el intérprete viene de la imagen",
        )

    def test_runs_both_linters_in_strict_mode(self):
        text = _template()
        self.assertIn("charter_lint.py", text, "la plantilla no corre charter_lint.py")
        self.assertIn("validate.py", text, "la plantilla no corre validate.py")
        self.assertIn("--strict", text, "la plantilla no corre los linters en «--strict»")

    def test_no_dependency_installer(self):
        """Ningún **paso** instala dependencias; nombrarlo en un comentario sí vale.

        El requisito prohíbe el paso, no la palabra: la cabecera de la
        plantilla tiene que poder explicar por qué no lo hay y qué añadir si
        tu suite tiene dependencias. Mirar el fichero entero convertía esa
        explicación en un fallo.
        """
        for command in _run_commands(_template()):
            self.assertNotIn(
                "pip install",
                command,
                f"la plantilla del consumidor no puede depender de pip: {command}",
            )


class GateTemplateRunsTheOracleTest(unittest.TestCase):
    """R-CI-014 · El oráculo por cada change validated o verified, y su rojo cuenta."""

    def test_oracle_step_is_conditional_on_the_project_config(self):
        text = _template()
        self.assertIn(
            "venoxia.json",
            text,
            "el paso del oráculo no está condicionado a «.venoxia/venoxia.json»",
        )

    def test_one_invocation_per_gated_change(self):
        text = _template()
        self.assertIn("oracle.py", text, "la plantilla no invoca oracle.py")
        self.assertIn("--change", text, "la plantilla no invoca oracle.py por change")
        for state in ("validated", "verified"):
            self.assertIn(
                state,
                text,
                f"la plantilla no menciona el estado «{state}» al filtrar los changes",
            )

    def test_the_pinned_reference_has_no_fallback(self):
        """`${{ vars.VENOXIA_REF || 'main' }}` cumpliría «fijado» y seguiría una rama."""
        text = _template()
        ref = re.search(r"^\s*ref:\s*(.+)$", text, re.MULTILINE)
        self.assertIsNotNone(ref, "la plantilla no declara «ref» en el checkout de Venoxia")
        self.assertNotIn(
            "||",
            ref.group(1),
            "el «ref» declara un valor de reserva: con VENOXIA_REF sin definir "
            "acabaría siguiendo una rama en movimiento",
        )

    def test_an_undefined_reference_fails_before_the_checkout(self):
        """Una `ref` vacía toma la rama por defecto: hay que fallar antes."""
        commands = _run_commands(_template())
        guard = [c for c in commands if "VENOXIA_REF" in c]
        self.assertTrue(guard, "ningún paso comprueba que VENOXIA_REF esté definida")
        joined = " ".join(guard)
        self.assertIn("SystemExit(1)", joined, "la comprobación no hace fallar el job")

    def test_the_documentation_asks_for_a_tag_not_a_branch(self):
        text = _template()
        self.assertIn("tag", text, "la plantilla no pide un tag para VENOXIA_REF")
        self.assertIn(
            "rama",
            text,
            "la plantilla no advierte de lo que pasa con una rama en movimiento",
        )

    def test_every_checkout_refuses_to_persist_credentials(self):
        """Un checkout con `token:` deja la credencial en el `.git/config`.

        El paso siguiente ejecuta el `test_command` del repositorio bajo
        prueba, que podría leerla de ahí aunque no esté en su entorno. Vale
        para los dos checkouts: el del consumidor lleva además permiso de
        escritura.
        """
        text = _template()
        checkouts = text.count("uses: actions/checkout@")
        self.assertGreaterEqual(checkouts, 2, "faltan pasos de checkout en la plantilla")
        self.assertEqual(
            text.count("persist-credentials: false"),
            checkouts,
            "algún checkout no declara «persist-credentials: false» y dejaría "
            "su credencial escrita en el workspace",
        )

    def test_the_oracle_step_carries_no_secret(self):
        """El paso que ejecuta código del repositorio bajo prueba no ve secretos."""
        text = _template()
        oracle_step = text[text.index("- name: oracle.py") :]
        self.assertNotIn(
            "secrets.",
            oracle_step,
            "el paso del oráculo declara un secreto: ejecuta el test_command "
            "que declara el repositorio bajo prueba",
        )

    def test_the_token_appears_only_in_the_venoxia_checkout(self):
        text = _template()
        occurrences = re.findall(r"secrets\.VENOXIA_TOKEN", text)
        self.assertEqual(len(occurrences), 1, "el token aparece fuera del checkout de Venoxia")

    def test_the_gate_runs_on_the_events_that_gate_a_merge(self):
        """`on: workflow_dispatch` a secas no bloquearía ninguna fusión."""
        text = _template()
        header = text[: text.index("jobs:")]
        self.assertIn("push:", header)
        self.assertIn("pull_request:", header)

    def test_no_job_or_step_discards_its_failure(self):
        self.assertNotIn(
            "continue-on-error",
            _template(),
            "la plantilla descarta el fallo de algún job o paso: un oráculo en "
            "rojo dejaría el workflow del consumidor en verde",
        )

    def test_a_missing_project_config_fails_the_job(self):
        joined = " ".join(_run_commands(_template()))
        self.assertIn("venoxia.json", joined)
        self.assertIn(
            "sys.exit(1)",
            joined,
            "la plantilla no falla cuando falta la configuración del oráculo",
        )

    def test_an_unreadable_change_is_not_skipped_in_silence(self):
        """Corromper un `change.json` no puede ser la forma de saltarse la puerta."""
        joined = " ".join(_run_commands(_template()))
        self.assertIn("unreadable", joined, "la plantilla no recoge los changes ilegibles")

    def test_the_state_is_normalised_before_comparing(self):
        """`"Verified"` o `"validated "` son el estado que nombran, no otro."""
        joined = " ".join(_run_commands(_template()))
        self.assertIn(
            ".strip().lower()",
            joined,
            "la plantilla compara el «state» en crudo: una mayúscula o un "
            "espacio bastarían para saltarse el oráculo",
        )

    def test_a_red_oracle_fails_the_job(self):
        """Sin una salida distinta de 0, un change «verified» con el oráculo
        caído pasaría la puerta en silencio: exactamente la mentira que el
        guardián no puede ver desde el editor de nadie."""
        self.assertRegex(
            _template(),
            r"sys\.exit\(1\)",
            "la plantilla no hace fallar el job cuando algún oráculo queda en rojo",
        )


class ReadmeDescribesOneCiTest(unittest.TestCase):
    """R-CI-015 · El README describe un único CI y la plantilla del consumidor."""

    def test_section_names_the_only_workflow_and_the_runner_labels(self):
        section = _readme_ci_section()
        self.assertIn(".forgejo/workflows/ci.yml", section)
        for label in ("oa2p-debian", "oa2p-node"):
            self.assertIn(label, section, f"la sección no nombra la etiqueta «{label}»")

    def test_section_names_the_consumer_template(self):
        self.assertIn("templates/ci/venoxia-gate.yml", _readme_ci_section())

    def test_section_explains_that_evals_is_manual(self):
        self.assertIn("workflow_dispatch", _readme_ci_section())

    def test_section_no_longer_names_a_github_workflow(self):
        self.assertNotIn(
            ".github/workflows/ci.yml",
            _readme_ci_section(),
            "la sección sigue nombrando el workflow de GitHub, que ya no existe",
        )


if __name__ == "__main__":
    unittest.main()
