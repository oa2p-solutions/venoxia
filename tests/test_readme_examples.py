#!/usr/bin/env python3
"""El README y las plantillas se validan como ficheros reales.

`README.md` afirma que su acta de ejemplo y su requisito de ejemplo «se
extraen a ficheros reales y se pasan por `charter_lint.py` y `validate.py`
antes de publicarlos». Este fichero convierte esa afirmación en un test: si
alguien mete un `SHALL` en la narrativa del ejemplo, o una fecha en un
`revisit:`, o rompe cualquiera de las diecinueve reglas del acta o las
dieciséis del validador, la suite se pone roja en vez de colar el error hasta
que un lector humano lo note (ya pasó una vez con un `SHALL` que `V14`
marcaba).

Las cuatro plantillas de `templates/` reciben el mismo trato: son lo primero
que copia quien empieza un proyecto, así que un error ahí se multiplica por
cada proyecto nuevo.

Los bloques del README se localizan por el encabezado de sección que los
precede, nunca por el número de línea: el README se reescribe con frecuencia
y un test que dependiera de la línea exacta se rompería por razones que no
tienen nada que ver con lo que comprueba.
"""

from __future__ import annotations

import re
import unittest

from tests.venoxia_fixtures import (
    REPO_ROOT,
    Project,
)

README_PATH = REPO_ROOT / "README.md"
TEMPLATES_DIR = REPO_ROOT / "templates"

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE_END_RE = re.compile(r"^```\s*$")


def _fenced_blocks(text: str, lang: str) -> list[tuple[str, str]]:
    """Devuelve `(heading_anterior, cuerpo)` de cada bloque ` ```<lang> ` del texto.

    `heading_anterior` es el texto del último encabezado Markdown (`## …`, de
    cualquier nivel) visto antes de que se abriera la valla; las líneas
    **dentro** de la valla nunca se interpretan como encabezados, así que un
    ejemplo que empieza por `# Título` no confunde al escaneo.
    """
    fence_open_re = re.compile(rf"^```{re.escape(lang)}\s*$")
    blocks: list[tuple[str, str]] = []
    current_heading = ""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            current_heading = heading_match.group(2)
            index += 1
            continue
        if fence_open_re.match(line):
            body_lines: list[str] = []
            index += 1
            while index < len(lines) and not _FENCE_END_RE.match(lines[index]):
                body_lines.append(lines[index])
                index += 1
            blocks.append((current_heading, "\n".join(body_lines)))
        index += 1
    return blocks


def _first_block_after(text: str, heading: str, lang: str = "markdown") -> str:
    """El cuerpo del primer bloque ` ```<lang> ` que sigue al encabezado `heading`.

    Falla con un mensaje que nombra el encabezado buscado si no hay ninguno:
    así, si el README cambia de estructura, el test dice qué esperaba en vez
    de fallar por una `IndexError` opaca.
    """
    for candidate_heading, body in _fenced_blocks(text, lang):
        if candidate_heading == heading:
            return body
    raise AssertionError(
        f"No se encontró ningún bloque ```{lang} bajo el encabezado «## {heading}» "
        f"en «{README_PATH}». ¿Se renombró la sección?"
    )


def _headings(text: str) -> list[str]:
    """Los encabezados `## …` (segundo nivel) de un texto, en orden."""
    found = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.*?)\s*$", line)
        if match:
            found.append(match.group(1))
    return found


class ReadmeExamplesTest(unittest.TestCase):
    """El acta y el requisito de ejemplo del README pasan por los linters de verdad."""

    def setUp(self) -> None:
        self.readme_text = README_PATH.read_text(encoding="utf-8")

    def test_readme_charter_passes_strict_lint(self) -> None:
        """El acta de ejemplo bajo «## El acta del proyecto» pasa `charter_lint.py --strict`."""
        charter_block = _first_block_after(self.readme_text, "El acta del proyecto")
        with Project(scaffold=False) as project:
            project.write(".venoxia/charter.md", charter_block + "\n")
            run = project.lint_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rules(), [])

    def test_readme_requirement_passes_strict_validation(self) -> None:
        """El requisito de ejemplo bajo «## El formato del requisito» pasa `validate.py --strict`.

        Se envuelve en una capability de mentira con `## Purpose` y
        `## Requirements`, y se crea el fichero de test que cita en
        `verifies:` con su `@covers`, tal como manda `V07`/`V08`.
        """
        requirement_block = _first_block_after(self.readme_text, "El formato del requisito")
        verifies_match = re.search(r"^verifies:\s*(\S+)", requirement_block, re.MULTILINE)
        covers_match = re.search(r"^###\s*(\S+)", requirement_block, re.MULTILINE)
        self.assertIsNotNone(verifies_match, "El requisito de ejemplo no declara «verifies:».")
        self.assertIsNotNone(covers_match, "El requisito de ejemplo no tiene un ID en su encabezado.")

        with Project(scaffold=False) as project:
            spec = (
                "# Capability: checkout\n\n"
                "## Purpose\n\n"
                "El paso de «checkout» del sistema, para el ejemplo del README.\n\n"
                "## Requirements\n\n" + requirement_block + "\n"
            )
            project.write(".venoxia/capabilities/checkout/spec.md", spec)
            project.test_file(verifies_match.group(1), covers=[covers_match.group(1)])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rules(), [])


class TemplatesTest(unittest.TestCase):
    """Las cuatro plantillas de `templates/` pasan por los mismos linters, tal cual se copian."""

    def test_template_charter_passes_strict_lint(self) -> None:
        """`templates/charter.md`, comentarios HTML incluidos, pasa `charter_lint.py --strict`."""
        content = (TEMPLATES_DIR / "charter.md").read_text(encoding="utf-8")
        with Project(scaffold=False) as project:
            project.write(".venoxia/charter.md", content)
            run = project.lint_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rules(), [])

    def test_template_capability_passes_strict_validation(self) -> None:
        """`templates/capability.md` pasa `validate.py --strict` con su oráculo stubeado."""
        content = (TEMPLATES_DIR / "capability.md").read_text(encoding="utf-8")
        with Project(scaffold=False) as project:
            project.write(".venoxia/capabilities/checkout/spec.md", content)
            project.test_file("test/checkout/reservation.spec.ts", covers=["R-CHK-014"])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rules(), [])

    def test_template_delta_passes_strict_validation(self) -> None:
        """`templates/delta.md` pasa `validate.py --strict` con su oráculo stubeado."""
        content = (TEMPLATES_DIR / "delta.md").read_text(encoding="utf-8")
        with Project(scaffold=False) as project:
            project.write(".venoxia/changes/c1/delta/checkout.md", content)
            project.test_file("test/checkout/stock-reservation.spec.ts", covers=["R-CHK-021"])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rules(), [])

    def test_template_proposal_has_required_sections(self) -> None:
        """`templates/proposal.md` trae los cinco encabezados que exige el formato.

        No hay linter para `proposal.md`: `validate.py` no lo toca. Lo único
        comprobable es que estén las cinco secciones de segundo nivel que el
        resto del plugin da por escritas.
        """
        content = (TEMPLATES_DIR / "proposal.md").read_text(encoding="utf-8")
        headings = _headings(content)
        for required in ("Why", "What Changes", "Capabilities", "Impact", "Confidence"):
            self.assertIn(
                required,
                headings,
                f"«templates/proposal.md» no trae el encabezado «## {required}».",
            )


if __name__ == "__main__":
    unittest.main()
