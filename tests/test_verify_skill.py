#!/usr/bin/env python3
"""`skills/verify/SKILL.md` existe y trae el contrato que `/venoxia:verify` promete.

No hay comportamiento que ejecutar aquí —la skill la interpreta un modelo, no
un intérprete—, así que lo que este fichero comprueba es estructural: que el
frontmatter declara `name: verify`, que `description` dispara con las cinco
frases que el usuario diría, que `allowed-tools` es exactamente la lista
acotada (sin ningún `Bash` genérico) y que el cuerpo nombra el contrato de
`oracle.py` (`--dry-run`, `--record`, `verified`, «verde sin rojo») y declara
con todas las letras que nunca edita tests ni código de producción.

Es, a propósito, el primer test que se ejecuta contra este change: falla en
rojo porque `skills/verify/SKILL.md` todavía no existe, y ese rojo es el que
`oracle.py --record` deja grabado antes de escribir la skill.

@covers R-ORC-009
@covers R-ORC-010

Cómo lanzarlo::

    python3 -m unittest tests.test_verify_skill -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_verify_skill.py -q
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

SKILL_PATH = REPO_ROOT / "skills" / "verify" / "SKILL.md"

#: El bloque de frontmatter entre las dos vallas `---`.
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

#: Las cinco frases que la descripción tiene que disparar, literales del
#: `implementation_plan` de la definición: «verifica el cambio», «graba el
#: rojo», «pasa el oráculo», «¿está en verde?», «corre los tests de la spec».
_TRIGGERS = (
    "verifica el cambio",
    "graba el rojo",
    "pasa el oráculo",
    "¿está en verde?",
    "corre los tests de la spec",
)

#: El contrato de herramientas exacto: ni una entrada de más, ni un `Bash`
#: sin acotar. `oracle.py` es el único script que esta skill puede invocar.
_EXPECTED_TOOLS = frozenset(
    {
        "Read",
        "Glob",
        'Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" *)',
        "Write",
    }
)


def _read_skill() -> str:
    """El texto de `skills/verify/SKILL.md`, o un fallo que dice qué falta."""
    if not SKILL_PATH.is_file():
        raise AssertionError(
            f"no existe «{SKILL_PATH}»: falta la skill /venoxia:verify que envuelve "
            "oracle.py y escribe «verified»."
        )
    return SKILL_PATH.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    """El contenido entre las dos vallas `---` del frontmatter."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError(
            "skills/verify/SKILL.md no empieza con un frontmatter «---\\n...\\n---\\n» válido"
        )
    return match.group(1)


def _field(frontmatter: str, name: str) -> str:
    """El valor de una clave de una sola línea del frontmatter (`name:`, …)."""
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(f"el frontmatter de skills/verify/SKILL.md no declara «{name}:»")
    return match.group(1).strip()


def _allowed_tools(frontmatter: str) -> list[str]:
    """Las entradas de la lista `allowed-tools:`, en el orden en que aparecen."""
    match = re.search(r"^allowed-tools:\s*\n((?:^ {2}-.*\n?)+)", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(
            "el frontmatter de skills/verify/SKILL.md no declara «allowed-tools:» "
            "como una lista"
        )
    items: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


class VerifySkillFrontmatterTest(unittest.TestCase):
    """El frontmatter declara el nombre, los disparadores y el contrato de herramientas."""

    def test_skill_file_exists(self):
        self.assertTrue(SKILL_PATH.is_file(), f"falta «{SKILL_PATH}»")

    def test_name_is_verify(self):
        frontmatter = _frontmatter(_read_skill())
        self.assertEqual(_field(frontmatter, "name"), "verify")

    def test_description_has_the_five_triggers(self):
        frontmatter = _frontmatter(_read_skill())
        description = _field(frontmatter, "description")
        for trigger in _TRIGGERS:
            self.assertIn(
                trigger,
                description,
                f"la description de skills/verify/SKILL.md no dispara con «{trigger}»",
            )

    def test_allowed_tools_are_exactly_the_declared_four(self):
        frontmatter = _frontmatter(_read_skill())
        tools = _allowed_tools(frontmatter)
        self.assertEqual(
            set(tools),
            set(_EXPECTED_TOOLS),
            "allowed-tools de skills/verify/SKILL.md no es exactamente "
            "{Read, Glob, Bash(oracle.py), Write}",
        )
        self.assertEqual(
            len(tools),
            len(_EXPECTED_TOOLS),
            "allowed-tools de skills/verify/SKILL.md trae entradas repetidas",
        )

    def test_allowed_tools_has_no_generic_bash(self):
        frontmatter = _frontmatter(_read_skill())
        for tool in _allowed_tools(frontmatter):
            self.assertFalse(
                tool == "Bash" or tool.strip() == "Bash(python3 *)",
                f"«{tool}» es un Bash genérico: la skill sólo puede invocar oracle.py",
            )


class VerifySkillBodyTest(unittest.TestCase):
    """El cuerpo nombra el contrato de `oracle.py` y su propia frontera."""

    def test_mentions_the_oracle_invocation(self):
        text = _read_skill()
        for token in ("oracle.py", "--dry-run", "--record"):
            self.assertIn(token, text, f"skills/verify/SKILL.md no menciona «{token}»")

    def test_mentions_verified_and_green_without_red(self):
        text = _read_skill()
        self.assertIn(
            "verified",
            text,
            "skills/verify/SKILL.md no menciona el estado «verified» que escribe",
        )
        self.assertIn(
            "verde sin rojo",
            text,
            "skills/verify/SKILL.md no nombra el caso «verde sin rojo»",
        )

    def test_records_the_confirmation_with_confirm_green_before_verified(self):
        """R-ORC-010 · la confirmación del usuario se graba con --confirm-green, no sólo se dice.

        @covers R-ORC-010
        """
        text = _read_skill()
        self.assertIn(
            "--confirm-green",
            text,
            "skills/verify/SKILL.md no manda grabar la confirmación con «--confirm-green»",
        )
        self.assertIn(
            "confirmed_green",
            text,
            "skills/verify/SKILL.md no nombra la lista «confirmed_green» que V18 lee",
        )

    def test_records_the_confirmation_only_after_asking_and_only_for_confirmed_ids(self):
        """R-ORC-010 · --confirm-green nunca precede a la pregunta ni nombra IDs sin confirmar.

        @covers R-ORC-010
        """
        text = _read_skill()
        self.assertIn(
            "sólo después de haber preguntado",
            text,
            "skills/verify/SKILL.md no dice que --confirm-green va sólo después de preguntar",
        )
        self.assertIn(
            "únicamente con los IDs que el usuario confirmó",
            text,
            "skills/verify/SKILL.md no acota --confirm-green a los IDs confirmados",
        )
        self.assertIn(
            "nunca como primera grabación",
            text,
            "skills/verify/SKILL.md no prohíbe que la confirmación sea la primera grabación",
        )

    def test_only_a_prior_red_run_counts_as_red(self):
        """R-ORC-010 · un run anterior en «missing» no acredita el rojo previo.

        @covers R-ORC-010
        """
        text = _read_skill()
        self.assertNotIn(
            "`requirement_id` en `red` o `missing`",
            text,
            "skills/verify/SKILL.md sigue tratando «missing» como rojo previo",
        )
        self.assertIn(
            "`missing` y `timeout` no acreditan",
            text,
            "skills/verify/SKILL.md no dice que missing y timeout no acreditan el rojo",
        )

    def test_declares_it_never_edits_tests_or_production_code(self):
        text = _read_skill()
        self.assertRegex(
            text,
            r"[Nn]unca edit[a-záéíóúñ]*\s+tests\s+ni\s+c[oó]digo",
            "skills/verify/SKILL.md no declara con todas las letras que nunca "
            "edita tests ni código de producción",
        )


if __name__ == "__main__":
    unittest.main()
