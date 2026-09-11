#!/usr/bin/env python3
"""`skills/close/SKILL.md` existe y trae el contrato que `/venoxia:close` promete.

No hay comportamiento que ejecutar —la skill la interpreta un modelo—, así
que lo que se comprueba es estructural, como en `test_implement_skill.py`:
el frontmatter declara `name: close` y un `argument-hint` con el id del
change; `allowed-tools` es exactamente la lista acotada (la puerta y los
subcomandos de git que el cierre necesita, sin ningún `Bash` genérico y sin
`Write` ni `Edit`); y el cuerpo declara las fronteras con todas las letras:
sólo sobre un change en `verified`, la puerta antes de proponer el commit y
parada si sale distinto de `0`, autorización explícita por `AskUserQuestion`
antes de `git commit` y `git push`, nunca `--no-verify`/`--force`/`--amend`,
un mensaje que nombra el change y sus IDs y no menciona al modelo ni a la
herramienta, ningún fichero escrito, y una entrega con hash, rama, remoto,
resultado del push y `/venoxia:specify`.

Nace en rojo: `skills/close/SKILL.md` no existe todavía.

@covers R-CLS-001
@covers R-CLS-002
@covers R-CLS-003
@covers R-CLS-004

Cómo lanzarlo::

    python3 -m unittest tests.test_close_skill -v
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

SKILL_PATH = REPO_ROOT / "skills" / "close" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

#: El contrato de herramientas exacto: la puerta, ocho subcomandos de git, y nada más.
_EXPECTED_TOOLS = frozenset(
    {
        "Read",
        "Glob",
        "AskUserQuestion",
        'Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate.py" *)',
        "Bash(git status *)",
        "Bash(git diff *)",
        "Bash(git log *)",
        "Bash(git rev-parse *)",
        "Bash(git branch *)",
        "Bash(git add *)",
        "Bash(git commit *)",
        "Bash(git push *)",
    }
)


def _read_skill() -> str:
    if not SKILL_PATH.is_file():
        raise AssertionError(
            f"no existe «{SKILL_PATH}»: falta la skill /venoxia:close que cierra un change "
            "verificado con la puerta, la autorización y el commit."
        )
    return SKILL_PATH.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError(
            "skills/close/SKILL.md no empieza con un frontmatter «---\\n...\\n---\\n» válido"
        )
    return match.group(1)


def _body(text: str) -> str:
    return text[_FRONTMATTER_RE.match(text).end():]


def _field(frontmatter: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(f"el frontmatter de skills/close/SKILL.md no declara «{name}:»")
    return match.group(1).strip()


def _allowed_tools(frontmatter: str) -> list[str]:
    match = re.search(r"^allowed-tools:\s*\n((?:^ {2}-.*\n?)+)", frontmatter, re.MULTILINE)
    if not match:
        raise AssertionError(
            "el frontmatter de skills/close/SKILL.md no declara «allowed-tools:» como una lista"
        )
    items: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


class CloseSkillPreconditionsTest(unittest.TestCase):
    """R-CLS-001 · sólo desde un change verified, y la puerta antes de proponer nada."""

    def test_the_skill_is_named_close_and_takes_a_change_id(self):
        """@covers R-CLS-001"""
        frontmatter = _frontmatter(_read_skill())
        self.assertEqual(_field(frontmatter, "name"), "close")
        self.assertIn("change", _field(frontmatter, "argument-hint"))

    def test_the_body_requires_the_verified_state(self):
        """@covers R-CLS-001"""
        self.assertIn(
            "sólo trabaja sobre un change en `verified`",
            _body(_read_skill()),
            "skills/close/SKILL.md no exige el estado verified",
        )

    def test_the_body_runs_the_gate_before_proposing_the_commit(self):
        """@covers R-CLS-001"""
        self.assertIn(
            "ejecuta `gate.py` antes de proponer el commit",
            _body(_read_skill()),
            "skills/close/SKILL.md no manda pasar la puerta antes de proponer el commit",
        )

    def test_a_red_gate_stops_the_skill(self):
        """@covers R-CLS-001"""
        self.assertIn(
            "con la puerta en un código distinto de `0` se detiene y no hay commit",
            _body(_read_skill()),
            "skills/close/SKILL.md no se detiene con la puerta en rojo",
        )

    def test_the_gate_output_is_shown_literally(self):
        """@covers R-CLS-001"""
        self.assertIn(
            "enseña la salida literal de la puerta",
            _body(_read_skill()),
            "skills/close/SKILL.md no enseña la salida literal de gate.py",
        )


class CloseSkillAuthorizationTest(unittest.TestCase):
    """R-CLS-002 · ficheros y mensaje a la vista, autorización explícita, sin rodeos."""

    def test_the_files_to_commit_are_shown_before_asking(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "enseña los ficheros que irían al commit antes de pedir la autorización",
            _body(_read_skill()),
            "skills/close/SKILL.md no enseña los ficheros del commit antes de preguntar",
        )

    def test_the_proposed_message_is_shown_before_asking(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "enseña el mensaje de commit propuesto antes de pedir la autorización",
            _body(_read_skill()),
            "skills/close/SKILL.md no enseña el mensaje propuesto antes de preguntar",
        )

    def test_authorization_goes_through_ask_user_question(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "pide la autorización con `AskUserQuestion`",
            _body(_read_skill()),
            "skills/close/SKILL.md no pide la autorización con AskUserQuestion",
        )

    def test_no_commit_nor_push_without_an_explicit_yes(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "sin un sí explícito del usuario no ejecuta ni `git commit` ni `git push`",
            _body(_read_skill()),
            "skills/close/SKILL.md no condiciona commit y push al sí explícito",
        )

    def test_history_is_never_rewritten_nor_hooks_skipped(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "nunca pasa `--no-verify`, `--force` ni `--amend`",
            _body(_read_skill()),
            "skills/close/SKILL.md no prohíbe --no-verify, --force y --amend",
        )

    def test_nothing_is_staged_before_the_yes(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "`git add` se ejecuta sólo después de la autorización",
            _body(_read_skill()),
            "skills/close/SKILL.md pone ficheros en el índice antes del sí",
        )

    def test_only_the_listed_files_are_staged(self):
        """@covers R-CLS-002"""
        body = _body(_read_skill())
        self.assertIn(
            "añade por ruta exactamente los ficheros que enseñó",
            body,
            "skills/close/SKILL.md no acota el git add a los ficheros enseñados",
        )
        self.assertIn(
            "nunca con `git add -A` ni `git add .`",
            body,
            "skills/close/SKILL.md no prohíbe git add -A ni git add .",
        )

    def test_every_changed_file_is_proposed_grouped(self):
        """@covers R-CLS-002"""
        body = _body(_read_skill())
        self.assertIn(
            "todo lo que `git status` enumera",
            body,
            "skills/close/SKILL.md no propone todo lo que git status enumera",
        )
        self.assertIn(
            "tres grupos",
            body,
            "skills/close/SKILL.md no agrupa la lista en tres grupos",
        )

    def test_a_non_empty_index_stops_the_skill(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "si el índice ya tiene cambios preparados antes de empezar, se detiene sin commit",
            _body(_read_skill()),
            "skills/close/SKILL.md no se detiene con un índice ya cargado",
        )

    def test_the_changes_own_files_cannot_be_excluded(self):
        """@covers R-CLS-002"""
        body = _body(_read_skill())
        self.assertIn(
            "no se puede excluir",
            body,
            "skills/close/SKILL.md deja excluir los ficheros del propio change",
        )
        self.assertIn(
            "si el usuario lo nombra se detiene sin commit",
            body,
            "skills/close/SKILL.md no se detiene cuando el usuario excluye un fichero del propio change",
        )

    def test_the_user_excludes_a_file_by_naming_it(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "queda fuera del commit cuando el usuario lo nombra en su respuesta",
            _body(_read_skill()),
            "skills/close/SKILL.md no deja excluir un fichero nombrándolo",
        )

    def test_the_branch_and_the_remote_are_shown_before_asking(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "enseña la rama y el remoto del push antes de pedir la autorización",
            _body(_read_skill()),
            "skills/close/SKILL.md no enseña rama y remoto antes de preguntar",
        )

    def test_no_git_configuration_override(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "nunca pasa una opción `-c` ni cambia una variable de entorno de git",
            _body(_read_skill()),
            "skills/close/SKILL.md no cierra la puerta a -c core.hooksPath ni a GIT_CONFIG",
        )

    def test_a_failed_push_is_delivered_as_it_is(self):
        """@covers R-CLS-002"""
        self.assertIn(
            "un push en rojo se entrega tal cual y no se rodea",
            _body(_read_skill()),
            "skills/close/SKILL.md no entrega el push en rojo tal cual",
        )


class CloseSkillCommitMessageTest(unittest.TestCase):
    """R-CLS-003 · el mensaje nombra el change y sus IDs, y nunca al modelo ni a la herramienta."""

    def test_the_subject_names_the_change(self):
        """@covers R-CLS-003"""
        self.assertIn(
            "el asunto del mensaje nombra el change",
            _body(_read_skill()),
            "skills/close/SKILL.md no manda nombrar el change en el asunto",
        )

    def test_the_body_lists_the_requirement_ids(self):
        """@covers R-CLS-003"""
        self.assertIn(
            "el cuerpo del mensaje lista los IDs de los requisitos del change",
            _body(_read_skill()),
            "skills/close/SKILL.md no manda listar los IDs en el cuerpo del mensaje",
        )

    def test_no_co_author_trailer(self):
        """@covers R-CLS-003"""
        self.assertIn(
            "no lleva ninguna línea `Co-Authored-By`",
            _body(_read_skill()),
            "skills/close/SKILL.md no prohíbe la línea Co-Authored-By",
        )

    def test_no_generated_with_footer(self):
        """@covers R-CLS-003"""
        self.assertIn(
            "no lleva ningún pie «Generated with»",
            _body(_read_skill()),
            "skills/close/SKILL.md no prohíbe el pie «Generated with»",
        )

    def test_no_mention_of_the_model_nor_the_tool(self):
        """@covers R-CLS-003"""
        self.assertIn(
            "no menciona a Claude ni a Claude Code",
            _body(_read_skill()),
            "skills/close/SKILL.md no prohíbe mencionar a Claude ni a Claude Code en el mensaje",
        )


class CloseSkillToolsTest(unittest.TestCase):
    """R-CLS-004 · herramientas acotadas, sin escritura."""

    def test_the_tools_are_exactly_the_twelve_declared(self):
        """@covers R-CLS-004"""
        tools = _allowed_tools(_frontmatter(_read_skill()))
        self.assertEqual(set(tools), set(_EXPECTED_TOOLS))
        self.assertEqual(len(tools), len(_EXPECTED_TOOLS), "allowed-tools trae entradas repetidas")

    def test_no_generic_bash(self):
        """@covers R-CLS-004"""
        for tool in _allowed_tools(_frontmatter(_read_skill())):
            self.assertFalse(
                tool == "Bash" or tool.strip() in {"Bash(*)", "Bash(python3 *)", "Bash(git *)"},
                f"«{tool}» es un Bash genérico: la skill sólo puede invocar gate.py y ocho subcomandos de git",
            )

    def test_no_write_nor_edit(self):
        """@covers R-CLS-004"""
        tools = set(_allowed_tools(_frontmatter(_read_skill())))
        self.assertNotIn("Write", tools, "la skill /venoxia:close no puede escribir ficheros")
        self.assertNotIn("Edit", tools, "la skill /venoxia:close no puede editar ficheros")

    def test_the_body_says_it_writes_no_file(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "no escribe ningún fichero",
            _body(_read_skill()),
            "skills/close/SKILL.md no declara que no escribe ningún fichero",
        )

    def test_the_body_says_it_writes_no_state(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "no escribe ningún estado del change",
            _body(_read_skill()),
            "skills/close/SKILL.md no declara que no escribe ningún estado",
        )


class CloseSkillDeliveryTest(unittest.TestCase):
    """R-CLS-004 · la entrega nombra hash, rama y remoto, resultado del push y el siguiente paso."""

    def test_the_delivery_names_the_commit_hash(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "el hash del commit",
            _body(_read_skill()),
            "skills/close/SKILL.md no nombra el hash del commit en la entrega",
        )

    def test_the_delivery_names_the_branch_and_the_remote(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "la rama y el remoto",
            _body(_read_skill()),
            "skills/close/SKILL.md no nombra la rama y el remoto en la entrega",
        )

    def test_the_delivery_names_the_push_result(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "el resultado del push",
            _body(_read_skill()),
            "skills/close/SKILL.md no nombra el resultado del push en la entrega",
        )

    def test_the_next_step_is_specify(self):
        """@covers R-CLS-004"""
        self.assertIn(
            "/venoxia:specify",
            _body(_read_skill()),
            "skills/close/SKILL.md no remite a /venoxia:specify",
        )


if __name__ == "__main__":
    unittest.main()
