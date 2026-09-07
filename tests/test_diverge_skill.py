#!/usr/bin/env python3
"""`skills/diverge/SKILL.md` conduce la divergencia como entrevista y anota lo elegido.

No hay comportamiento que ejecutar —la skill la interpreta un modelo—, así
que lo que se comprueba es estructural: que `allowed-tools` incluye
`AskUserQuestion` sin perder ninguna de las herramientas que ya tenía, y que
el cuerpo declara el contrato con todas las letras: una pregunta por llamada,
en el orden del informe, con la pregunta y las opciones literales del script;
las respuestas anotadas tal cual en `decisions.json`, con sus claves; una
respuesta escrita a mano copiada con las palabras del usuario; y la frontera de
siempre, que la skill no edita deltas.

Nace en rojo: la skill de hoy no declara `AskUserQuestion` ni nombra
`decisions.json`, y ese rojo es el que `oracle.py --record` graba antes de
tocar la skill.

@covers R-DIV-009
@covers R-DIV-010

Cómo lanzarlo::

    python3 -m unittest tests.test_diverge_skill -v
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

SKILL_PATH = REPO_ROOT / "skills" / "diverge" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

#: Las herramientas que la skill ya tenía y no puede perder, más la entrevista.
_EXPECTED_TOOLS = frozenset(
    {
        "Read",
        "Write",
        "Glob",
        "AskUserQuestion",
        "Agent(venoxia:reader, venoxia:devils-advocate)",
        "Bash(mkdir -p *)",
        'Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/diff_readings.py" *)',
        'Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" *)',
        "Bash(python3 *)",
    }
)

#: Las claves de cada entrada de `decisions.json` que el cuerpo tiene que nombrar.
_DECISION_KEYS = ("scenario", "question", "options", "chosen", "answer")


def _read_skill() -> str:
    if not SKILL_PATH.is_file():
        raise AssertionError(f"no existe «{SKILL_PATH}»")
    return SKILL_PATH.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError("skills/diverge/SKILL.md no empieza con un frontmatter válido")
    return match.group(1)


def _allowed_tools(frontmatter: str) -> list[str]:
    match = re.search(r"^allowed-tools:\s*\n((?:^ {2}-.*\n?)+)", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError("el frontmatter de skills/diverge/SKILL.md no declara «allowed-tools:»")
    return [line.strip()[2:].strip() for line in match.group(1).splitlines() if line.strip().startswith("- ")]


class DivergeSkillInterviewTest(unittest.TestCase):
    """R-DIV-009 · las preguntas del script se plantean una por llamada, literales."""

    def test_allowed_tools_declare_ask_user_question_and_keep_the_rest(self):
        """@covers R-DIV-009"""
        tools = _allowed_tools(_frontmatter(_read_skill()))
        self.assertEqual(set(tools), set(_EXPECTED_TOOLS), tools)
        self.assertEqual(len(tools), len(_EXPECTED_TOOLS), "allowed-tools trae entradas repetidas")

    def test_body_asks_one_question_per_call_in_report_order_verbatim(self):
        """@covers R-DIV-009"""
        text = _read_skill()
        for phrase in ("una pregunta por llamada", "en el orden del informe", "literales"):
            self.assertIn(phrase, text, f"skills/diverge/SKILL.md no declara «{phrase}»")

    def test_body_still_refuses_to_edit_deltas(self):
        """@covers R-DIV-009"""
        self.assertIn("no edita deltas", _read_skill())


class DivergeSkillDecisionsTest(unittest.TestCase):
    """R-DIV-010 · lo elegido se anota tal cual en decisions.json."""

    def test_body_names_the_decisions_file_and_its_keys(self):
        """@covers R-DIV-010"""
        text = _read_skill()
        self.assertIn("decisions.json", text)
        for key in _DECISION_KEYS:
            self.assertIn(f"`{key}`", text, f"skills/diverge/SKILL.md no nombra la clave «{key}»")

    def test_body_keeps_a_hand_written_answer_verbatim(self):
        """@covers R-DIV-010"""
        self.assertIn("con las palabras del usuario", _read_skill())

    def test_body_keeps_earlier_decisions(self):
        """@covers R-DIV-010"""
        self.assertIn("sin borrar las anteriores", _read_skill())


if __name__ == "__main__":
    unittest.main()
