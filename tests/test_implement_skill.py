#!/usr/bin/env python3
"""`skills/implement/SKILL.md` existe y trae el contrato que `/venoxia:implement` promete.

No hay comportamiento que ejecutar —la skill la interpreta un modelo—, así
que lo que se comprueba es estructural: el frontmatter declara `name:
implement` y un `argument-hint` con el id del change; `allowed-tools` es
exactamente la lista acotada (sin ningún `Bash` genérico); y el cuerpo
declara las fronteras con todas las letras: sólo sobre un change en
`validated` con un rojo grabado, inventario antes de editar, nunca `.venoxia/`
ni los ficheros de `verifies:`, nunca `--record`, parada con el oráculo en
`0`, una decisión no escrita se pregunta y se anota, y la entrega nombra cada
requisito con su estado, los ficheros tocados y `/venoxia:verify`.

Nace en rojo: `skills/implement/SKILL.md` no existe todavía.

@covers R-IMP-001
@covers R-IMP-002
@covers R-IMP-003
@covers R-IMP-004

Cómo lanzarlo::

    python3 -m unittest tests.test_implement_skill -v
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

SKILL_PATH = REPO_ROOT / "skills" / "implement" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

#: El contrato de herramientas exacto: ni una entrada de más, ni un `Bash` sin acotar.
_EXPECTED_TOOLS = frozenset(
    {
        "Read",
        "Glob",
        "Grep",
        "Edit",
        "Write",
        "AskUserQuestion",
        'Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" *)',
    }
)


def _read_skill() -> str:
    if not SKILL_PATH.is_file():
        raise AssertionError(
            f"no existe «{SKILL_PATH}»: falta la skill /venoxia:implement que escribe el "
            "código de un change validado."
        )
    return SKILL_PATH.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError(
            "skills/implement/SKILL.md no empieza con un frontmatter «---\\n...\\n---\\n» válido"
        )
    return match.group(1)


def _body(text: str) -> str:
    return text[_FRONTMATTER_RE.match(text).end():]


def _field(frontmatter: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(f"el frontmatter de skills/implement/SKILL.md no declara «{name}:»")
    return match.group(1).strip()


def _allowed_tools(frontmatter: str) -> list[str]:
    match = re.search(r"^allowed-tools:\s*\n((?:^ {2}-.*\n?)+)", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(
            "el frontmatter de skills/implement/SKILL.md no declara «allowed-tools:» como una lista"
        )
    items: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


class ImplementSkillPreconditionsTest(unittest.TestCase):
    """R-IMP-001 · sólo desde un change validated con un rojo grabado, y leyendo antes de editar."""

    def test_the_skill_is_named_implement_and_takes_a_change_id(self):
        """@covers R-IMP-001"""
        frontmatter = _frontmatter(_read_skill())
        self.assertEqual(_field(frontmatter, "name"), "implement")
        self.assertIn("change", _field(frontmatter, "argument-hint"))

    def test_the_body_requires_the_validated_state(self):
        """@covers R-IMP-001"""
        self.assertIn(
            "sólo trabaja sobre un change en `validated`",
            _body(_read_skill()),
            "skills/implement/SKILL.md no exige el estado validated",
        )

    def test_the_body_requires_a_recorded_red_run(self):
        """@covers R-IMP-001"""
        self.assertIn(
            "algún requisito en `red`",
            _body(_read_skill()),
            "skills/implement/SKILL.md no exige un run con algún requisito en red antes de escribir código",
        )

    def test_the_body_refuses_a_missing_test(self):
        """@covers R-IMP-001"""
        self.assertIn(
            "algún requisito del change en `missing`",
            _body(_read_skill()),
            "skills/implement/SKILL.md no se detiene ante un requisito en missing",
        )

    def test_the_inventory_precedes_any_edit(self):
        """@covers R-IMP-001"""
        body = _body(_read_skill())
        for token in ("delta/", "decisions.json", "principles.md", "capabilities/", "verifies:"):
            self.assertIn(token, body, f"skills/implement/SKILL.md no manda leer «{token}» antes de editar")
        self.assertIn(
            "antes de editar nada",
            body,
            "skills/implement/SKILL.md no dice que el inventario va antes de editar nada",
        )


class ImplementSkillBoundariesTest(unittest.TestCase):
    """R-IMP-002 · nunca la spec ni los oráculos; el guardián sigue vigilando."""

    def test_the_body_forbids_editing_venoxia(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "nunca edita `.venoxia/`",
            _body(_read_skill()),
            "skills/implement/SKILL.md no prohíbe editar .venoxia/",
        )

    def test_the_body_forbids_editing_the_oracle_files(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "ni ningún fichero que un `verifies:` nombre",
            _body(_read_skill()),
            "skills/implement/SKILL.md no prohíbe editar los ficheros de verifies:",
        )

    def test_the_body_forbids_editing_the_test_directories(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "ni ningún otro fichero del directorio que contiene a cada uno de ellos, subdirectorios incluidos",
            _body(_read_skill()),
            "skills/implement/SKILL.md no protege el directorio de los ficheros de verifies:",
        )

    def test_decisions_json_is_the_one_exception(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "el único fichero de `.venoxia/` que escribe",
            _body(_read_skill()),
            "skills/implement/SKILL.md no acota la excepción de decisions.json",
        )

    def test_decisions_json_only_grows(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "añade sin borrar lo que ya hay",
            _body(_read_skill()),
            "skills/implement/SKILL.md no protege las decisiones ya anotadas",
        )

    def test_the_body_says_the_guardian_keeps_watching(self):
        """@covers R-IMP-002"""
        self.assertIn(
            "el guardián intercepta también las ediciones hechas desde la skill",
            _body(_read_skill()),
            "skills/implement/SKILL.md no dice que el guardián sigue vigilando dentro de la skill",
        )


class ImplementSkillOracleTest(unittest.TestCase):
    """R-IMP-003 · el oráculo sin --record es el criterio de parada; sin Bash genérico."""

    def test_the_tools_are_exactly_the_seven_declared(self):
        """@covers R-IMP-003"""
        tools = _allowed_tools(_frontmatter(_read_skill()))
        self.assertEqual(set(tools), set(_EXPECTED_TOOLS))
        self.assertEqual(len(tools), len(_EXPECTED_TOOLS), "allowed-tools trae entradas repetidas")

    def test_no_generic_bash(self):
        """@covers R-IMP-003"""
        for tool in _allowed_tools(_frontmatter(_read_skill())):
            self.assertFalse(
                tool == "Bash" or tool.strip() == "Bash(python3 *)",
                f"«{tool}» es un Bash genérico: la skill sólo puede invocar oracle.py",
            )

    def test_the_body_forbids_recording(self):
        """@covers R-IMP-003"""
        self.assertIn(
            "nunca pasa `--record`",
            _body(_read_skill()),
            "skills/implement/SKILL.md no prohíbe --record",
        )

    def test_the_body_stops_on_a_green_oracle(self):
        """@covers R-IMP-003"""
        self.assertIn(
            "termina en cuanto el oráculo queda todo en verde",
            _body(_read_skill()),
            "skills/implement/SKILL.md no fija el 0 del oráculo como criterio de parada",
        )

    def test_an_unwritten_decision_is_asked_not_chosen(self):
        """@covers R-IMP-003"""
        body = _body(_read_skill())
        self.assertIn("AskUserQuestion", body)
        self.assertIn(
            "se anota en `decisions.json`",
            body,
            "skills/implement/SKILL.md no anota la respuesta en decisions.json",
        )


class ImplementSkillStopRulesTest(unittest.TestCase):
    """R-IMP-003 · las otras dos paradas: sin progreso, o una respuesta que cambia comportamiento."""

    def test_an_answer_that_changes_behaviour_goes_back_to_specify(self):
        """@covers R-IMP-003"""
        self.assertIn(
            "cambia el comportamiento observable",
            _body(_read_skill()),
            "skills/implement/SKILL.md no remite a specify cuando la respuesta cambia comportamiento",
        )
        self.assertIn("/venoxia:specify", _body(_read_skill()))

    def test_no_progress_stops_the_loop(self):
        """@covers R-IMP-003"""
        self.assertIn(
            "no cambia el estado de ningún requisito",
            _body(_read_skill()),
            "skills/implement/SKILL.md no se detiene cuando un intento no cambia nada",
        )


class ImplementSkillDeliveryTest(unittest.TestCase):
    """R-IMP-004 · la entrega nombra cada requisito, los ficheros y el siguiente paso."""

    def test_the_delivery_lists_every_requirement_with_its_state(self):
        """@covers R-IMP-004"""
        self.assertIn(
            "cada requisito del change con su estado",
            _body(_read_skill()),
            "skills/implement/SKILL.md no lista cada requisito con su estado en la entrega",
        )

    def test_the_delivery_lists_the_files_touched(self):
        """@covers R-IMP-004"""
        self.assertIn(
            "los ficheros tocados",
            _body(_read_skill()),
            "skills/implement/SKILL.md no nombra los ficheros tocados en la entrega",
        )

    def test_the_next_step_is_verify(self):
        """@covers R-IMP-004"""
        self.assertIn(
            "/venoxia:verify",
            _body(_read_skill()),
            "skills/implement/SKILL.md no remite a /venoxia:verify",
        )


if __name__ == "__main__":
    unittest.main()
