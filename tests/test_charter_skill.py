#!/usr/bin/env python3
"""`skills/charter/SKILL.md` reparte las convenciones técnicas entre el contrato y las apuestas.

No hay comportamiento que ejecutar —la skill la interpreta un modelo—, así
que lo que se comprueba es estructural: que el cuerpo declara que una
convención aprobada es un requisito de `technical-contract`, que una sin
decidir es una apuesta en `## Bets`, que `principles.md` no lleva
convenciones técnicas, que el encabezado `## Convenciones técnicas` ha
desaparecido de la skill y que la entrega termina con el `/venoxia:specify`
de `technical-contract`.

Nace en rojo: la skill de hoy escribe `## Convenciones técnicas` como prosa
en `principles.md`, y ese rojo es el que `oracle.py --record` graba antes de
tocar la skill.

@covers R-CHL-006

Cómo lanzarlo::

    python3 -m unittest tests.test_charter_skill -v
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

SKILL_PATH = REPO_ROOT / "skills" / "charter" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _body() -> str:
    """El cuerpo de la skill, sin el frontmatter."""
    if not SKILL_PATH.is_file():
        raise AssertionError(f"no existe «{SKILL_PATH}»")
    text = SKILL_PATH.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError("skills/charter/SKILL.md no empieza con un frontmatter válido")
    return text[match.end():]


class CharterSkillTechnicalAxisTest(unittest.TestCase):
    """R-CHL-006 · lo aprobado va al contrato, lo abierto a las apuestas, nada a prosa."""

    def test_an_approved_convention_is_a_requirement_of_technical_contract(self):
        """@covers R-CHL-006"""
        self.assertIn(
            "una convención aprobada es un requisito de `technical-contract`",
            _body(),
            "skills/charter/SKILL.md no manda las convenciones aprobadas a technical-contract",
        )

    def test_an_undecided_convention_is_a_bet(self):
        """@covers R-CHL-006"""
        self.assertIn(
            "una convención sin decidir es una apuesta en `## Bets`",
            _body(),
            "skills/charter/SKILL.md no manda las convenciones sin decidir a ## Bets",
        )

    def test_the_principles_file_carries_no_technical_conventions(self):
        """@covers R-CHL-006"""
        self.assertIn(
            "`principles.md` no lleva convenciones técnicas",
            _body(),
            "skills/charter/SKILL.md no dice que principles.md va sin convenciones técnicas",
        )

    def test_the_technical_conventions_heading_is_gone(self):
        """@covers R-CHL-006"""
        self.assertNotIn(
            "## Convenciones técnicas",
            _body(),
            "skills/charter/SKILL.md sigue escribiendo el encabezado «## Convenciones técnicas»",
        )

    def test_existing_conventions_are_moved_not_dropped(self):
        """@covers R-CHL-006"""
        self.assertIn(
            "las convenciones técnicas que ya estén en `principles.md` se reparten igual",
            _body(),
            "skills/charter/SKILL.md no protege las convenciones técnicas ya escritas",
        )

    def test_the_delivery_hands_the_approved_conventions_to_specify(self):
        """@covers R-CHL-006"""
        self.assertIn(
            "`/venoxia:specify` de `technical-contract`",
            _body(),
            "skills/charter/SKILL.md no termina la entrega con el specify de technical-contract",
        )


if __name__ == "__main__":
    unittest.main()
