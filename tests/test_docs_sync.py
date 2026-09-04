#!/usr/bin/env python3
"""La spec no puede mentir, y el README tampoco: sincronía entre el README y
el registro de reglas de cada linter.

Este fichero no comprueba comportamiento del validador ni del linter del
acta —eso lo hacen `test_rules_early.py`, `test_rules_late.py` y
`test_charter_lint.py`—, comprueba que la tabla que el README enseña de cada
uno coincide, código a código y severidad a severidad, con `RULES` en el
script correspondiente, y que el número que anuncia cada encabezado es el
número real de reglas. Una regla nueva sin fila en el README, o una fila que
se queda con la severidad de ayer, hace fallar este test en vez de esperar a
que alguien lo note leyendo.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_docs_sync -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_docs_sync.py -q
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

# `venoxia_fixtures` ya ha puesto `scripts/` en `sys.path`.
import charter_lint  # noqa: E402
import validate  # noqa: E402

README_PATH = REPO_ROOT / "README.md"

#: Encabezado de una sección de reglas: «## Las 16 reglas del validador» o
#: «### Las 19 reglas del linter del acta», con el número capturado.
_HEADING_RE = re.compile(r"^#{2,3}\s+Las\s+(\d+)\s+reglas del (.+?)\s*$", re.MULTILINE)

#: Una fila de la tabla de reglas: `| `C01` | descripción... | error |`.
#: El código va entre backticks en la primera celda; la severidad es la
#: última celda, sin adornos.
_ROW_RE = re.compile(r"^\|\s*`([A-Z]\d{2})`\s*\|.*\|\s*(error|warning)\s*\|\s*$", re.MULTILINE)


def _section_after(heading_match: re.Match[str], text: str) -> str:
    """El bloque de texto entre este encabezado y el siguiente (o el final)."""
    start = heading_match.end()
    next_heading = re.search(r"^#{1,3}\s", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _find_section(text: str, label_substring: str) -> re.Match[str]:
    """El encabezado «Las N reglas del <label_substring>», o falla el test."""
    for match in _HEADING_RE.finditer(text):
        if label_substring in match.group(2):
            return match
    raise AssertionError(
        f"README.md no tiene ningún encabezado «Las N reglas del "
        f"{label_substring}»"
    )


def _rules_from_readme(label_substring: str) -> tuple[int, dict[str, str]]:
    """Encabezado + tabla de una sección de reglas.

    Devuelve `(N declarado en el encabezado, {código: severidad})` leyendo la
    primera tabla markdown que aparece después del encabezado que menciona
    `label_substring` (p. ej. «validador» o «linter del acta»).
    """
    text = README_PATH.read_text(encoding="utf-8")
    heading = _find_section(text, label_substring)
    declared_count = int(heading.group(1))
    section = _section_after(heading, text)
    rules = {code: severity for code, severity in _ROW_RE.findall(section)}
    return declared_count, rules


class DocsSyncTest(unittest.TestCase):
    """El README no puede describir reglas que el código no tiene, ni al revés."""

    def test_validator_table_matches_rules(self):
        """La tabla de `## Las 16 reglas del validador` == `validate.RULES`."""
        _declared, table = _rules_from_readme("validador")
        expected = {rule.code: rule.severity for rule in validate.RULES}
        self.assertEqual(
            table,
            expected,
            "La tabla de reglas del validador en README.md no coincide con "
            "validate.RULES (código o severidad distintos)",
        )

    def test_charter_table_matches_rules(self):
        """La tabla de `### Las 19 reglas del linter del acta` == `charter_lint.RULES`."""
        _declared, table = _rules_from_readme("linter del acta")
        expected = {rule.code: rule.severity for rule in charter_lint.RULES}
        self.assertEqual(
            table,
            expected,
            "La tabla de reglas del linter del acta en README.md no coincide "
            "con charter_lint.RULES (código o severidad distintos)",
        )

    def test_headline_counts_match(self):
        """El «N» de cada encabezado es `len(RULES)`, ni más ni menos."""
        validator_count, _ = _rules_from_readme("validador")
        charter_count, _ = _rules_from_readme("linter del acta")
        self.assertEqual(
            validator_count,
            len(validate.RULES),
            "El encabezado «Las N reglas del validador» no coincide con "
            "len(validate.RULES)",
        )
        self.assertEqual(
            charter_count,
            len(charter_lint.RULES),
            "El encabezado «Las N reglas del linter del acta» no coincide "
            "con len(charter_lint.RULES)",
        )


if __name__ == "__main__":
    unittest.main()
