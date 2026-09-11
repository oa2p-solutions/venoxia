#!/usr/bin/env python3
"""`skills/specify/SKILL.md` lleva un juicio técnico sin principio al contrato o a una apuesta.

Estructural, como los demás tests de skills: el cuerpo tiene que nombrar los
dos destinos de un juicio técnico que ningún principio gobierna
—`technical-contract` o `## Bets`—, prohibir la prosa con todas las letras y
mandar leer la capability `technical-contract` en el inventario del Paso 1.

Nace en rojo: la skill de hoy sólo conoce «preguntar» o «confidence: low»
como salidas, y ninguna nombra el contrato técnico.

@covers R-CHL-007

Cómo lanzarlo::

    python3 -m unittest tests.test_specify_skill -v
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

SKILL_PATH = REPO_ROOT / "skills" / "specify" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _body() -> str:
    """El cuerpo de la skill, sin el frontmatter."""
    if not SKILL_PATH.is_file():
        raise AssertionError(f"no existe «{SKILL_PATH}»")
    text = SKILL_PATH.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError("skills/specify/SKILL.md no empieza con un frontmatter válido")
    return text[match.end():]


class SpecifySkillTechnicalJudgementTest(unittest.TestCase):
    """R-CHL-007 · un juicio técnico sin principio va al contrato o a una apuesta, nunca a prosa."""

    def test_the_body_names_the_two_destinations(self):
        """@covers R-CHL-007"""
        self.assertIn(
            "un juicio técnico sin principio que lo gobierne va a `technical-contract`",
            _body(),
            "skills/specify/SKILL.md no manda el juicio técnico a technical-contract",
        )
        self.assertIn(
            "o a `## Bets` con el hecho que lo cierra",
            _body(),
            "skills/specify/SKILL.md no ofrece ## Bets como destino del juicio técnico",
        )

    def test_the_body_forbids_prose(self):
        """@covers R-CHL-007"""
        self.assertIn(
            "nunca a prosa",
            _body(),
            "skills/specify/SKILL.md no prohíbe con todas las letras la prosa para el juicio técnico",
        )

    def test_a_bet_only_when_no_test_could_check_it(self):
        """@covers R-CHL-007"""
        self.assertIn(
            "sólo es apuesta cuando ningún test podría comprobarlo aunque se escribiera",
            _body(),
            "skills/specify/SKILL.md deja que todo juicio técnico acabe como apuesta",
        )

    def test_the_inventory_includes_the_technical_contract(self):
        """@covers R-CHL-007"""
        self.assertIn(
            ".venoxia/capabilities/technical-contract/spec.md",
            _body(),
            "skills/specify/SKILL.md no manda leer la capability technical-contract en el inventario",
        )


if __name__ == "__main__":
    unittest.main()
