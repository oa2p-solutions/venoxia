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


# ---------------------------------------------------------------------------
# La entrevista adaptativa (2026-09-15-charter-adaptive-interview)
# ---------------------------------------------------------------------------

_SLOTS = (
    "purpose",
    "primary_user",
    "current_workaround",
    "first_capability",
    "done_when",
    "out_of_scope",
    "evidence",
    "bets",
    "domain_decisions",
)

_STATES = ("known", "inferred", "missing", "optional", "conflicting")

_LAST_REAL_CASE_QUESTION = (
    "Cuéntame la última vez que ocurrió el problema: quién estaba intentando hacer "
    "qué, qué pasos siguió y dónde perdió más tiempo o cometió errores."
)

_REMOVE_FIRST_QUESTION = (
    "¿Qué parte de ese proceso eliminarías primero y qué tendría que ver esa persona "
    "para considerar que ya funciona?"
)


def _headings(body: str) -> list[tuple[int, str]]:
    """Los encabezados de segundo nivel del cuerpo, con su posición en el texto."""
    return [(match.start(), match.group(1)) for match in re.finditer(r"^## (.+)$", body, re.MULTILINE)]


class CharterSkillCoverageMapTest(unittest.TestCase):
    """R-CHL-009 · una pregunta sólo se hace por una casilla en «missing» o «conflicting»."""

    def test_the_nine_slots_are_named(self):
        """@covers R-CHL-009"""
        body = _body()
        for slot in _SLOTS:
            self.assertIn(f"`{slot}`", body, f"skills/charter/SKILL.md no nombra la casilla «{slot}»")

    def test_the_five_states_are_named(self):
        """@covers R-CHL-009"""
        body = _body()
        for state in _STATES:
            self.assertIn(f"`{state}`", body, f"skills/charter/SKILL.md no nombra el estado «{state}»")

    def test_only_a_missing_or_conflicting_slot_is_asked(self):
        """@covers R-CHL-009"""
        self.assertIn(
            "una pregunta sólo se hace cuando su casilla está en `missing` o en `conflicting`",
            _body(),
            "skills/charter/SKILL.md no limita las preguntas a las casillas missing o conflicting",
        )

    def test_the_slot_is_named_before_the_question(self):
        """@covers R-CHL-009"""
        self.assertIn(
            "antes de cada pregunta se nombra la casilla que va a escribir",
            _body(),
            "skills/charter/SKILL.md no nombra la casilla antes de preguntar",
        )

    def test_one_answer_refreshes_the_whole_map(self):
        """@covers R-CHL-009"""
        self.assertIn(
            "tras cada respuesta se re-evalúa el mapa entero",
            _body(),
            "skills/charter/SKILL.md no re-evalúa el mapa entero tras cada respuesta",
        )

    def test_a_correction_invalidates_only_its_dependants(self):
        """@covers R-CHL-009"""
        self.assertIn(
            "una corrección invalida sólo las casillas que dependen de la corregida",
            _body(),
            "skills/charter/SKILL.md no acota lo que invalida una corrección",
        )

    def test_an_inferred_slot_needs_the_users_confirmation(self):
        """@covers R-CHL-009"""
        body = _body()
        self.assertIn("una casilla `inferred` sólo pasa a `known` cuando el usuario la confirma", body)
        self.assertIn("la confirmación general del borrador se hace siempre", body)


class CharterSkillEntryModesTest(unittest.TestCase):
    """R-CHL-010 · tres modos de entrada más retomar, y el borrador antes de preguntar."""

    def test_the_modes_are_named(self):
        """@covers R-CHL-010"""
        body = _body()
        for mode in ("producto ya explicado", "proyecto existente", "idea difusa", "retomar un acta"):
            self.assertIn(mode, body, f"skills/charter/SKILL.md no nombra el modo «{mode}»")

    def test_an_explained_product_is_drafted_first(self):
        """@covers R-CHL-010"""
        self.assertIn(
            "el acta se redacta antes de la primera pregunta",
            _body(),
            "skills/charter/SKILL.md no redacta el acta antes de la primera pregunta",
        )

    def test_inferences_are_marked_in_the_draft(self):
        """@covers R-CHL-010"""
        self.assertIn(
            "las inferencias van marcadas en el borrador",
            _body(),
            "skills/charter/SKILL.md no marca las inferencias en el borrador",
        )

    def test_the_inference_mark_is_the_literal_comment(self):
        """@covers R-CHL-010"""
        self.assertIn(
            "la marca de inferencia es `<!-- inferred -->`",
            _body(),
            "skills/charter/SKILL.md no fija la marca literal que C21 busca",
        )

    def test_resuming_wins_over_an_existing_project(self):
        """@covers R-CHL-010"""
        self.assertIn(
            "con `.venoxia/charter.md` en el disco el modo es retomar un acta aunque haya código",
            _body(),
            "skills/charter/SKILL.md deja que un proyecto existente pise un acta ya escrita",
        )

    def test_the_draft_lives_in_the_conversation_until_approved(self):
        """@covers R-CHL-010"""
        self.assertIn(
            "el borrador se enseña en la conversación y no se escribe en `.venoxia/charter.md` hasta la aprobación",
            _body(),
            "skills/charter/SKILL.md escribe el borrador en disco antes de la aprobación",
        )

    def test_the_explained_mode_needs_three_slots_said_by_the_user(self):
        """@covers R-CHL-010"""
        body = _body()
        self.assertIn(
            "el modo producto ya explicado exige `purpose`, `primary_user` y `first_capability` dichos por el usuario",
            body,
        )
        self.assertIn("un `Done when` nunca se infiere", body)

    def test_the_vague_mode_opens_with_the_last_real_case(self):
        """@covers R-CHL-010"""
        self.assertIn(
            _LAST_REAL_CASE_QUESTION,
            _body(),
            "skills/charter/SKILL.md no abre la idea difusa con la última vez que ocurrió el problema",
        )

    def test_the_vague_mode_continues_with_what_to_remove_first(self):
        """@covers R-CHL-010"""
        self.assertIn(
            _REMOVE_FIRST_QUESTION,
            _body(),
            "skills/charter/SKILL.md no sigue con qué parte del proceso eliminaría primero",
        )

    def test_the_fixed_rounds_are_gone(self):
        """@covers R-CHL-010"""
        self.assertIsNone(
            re.search(r"^### Tanda", _body(), re.MULTILINE),
            "skills/charter/SKILL.md sigue organizando la entrevista en tandas fijas",
        )


class CharterSkillExistingProjectTest(unittest.TestCase):
    """R-CHL-011 · lo que el disco ya dice no se pregunta."""

    def test_the_reading_is_reconstructed_from_disk(self):
        """@covers R-CHL-011"""
        self.assertIn(
            "se reconstruyen desde el repositorio y se presentan para corregirlos",
            _body(),
            "skills/charter/SKILL.md no reconstruye la lectura desde el repositorio",
        )

    def test_the_next_change_is_asked(self):
        """@covers R-CHL-011"""
        self.assertIn(
            "se pregunta qué cambio quiere hacer ahora",
            _body(),
            "skills/charter/SKILL.md no pregunta qué cambio quiere hacer ahora",
        )

    def test_disk_facts_are_not_asked(self):
        """@covers R-CHL-011"""
        self.assertIn(
            "no se pregunta por el stack, el comando de pruebas ni un comportamiento que el disco ya demuestra",
            _body(),
            "skills/charter/SKILL.md sigue preguntando lo que el disco ya demuestra",
        )

    def test_priority_is_adoption_order_said_once(self):
        """@covers R-CHL-011"""
        body = _body()
        self.assertIn("la prioridad es el orden de adopción de Venoxia", body)
        self.assertIn("se explica una sola vez", body)


class CharterSkillFactsAndBetsTest(unittest.TestCase):
    """R-CHL-012 · una síntesis, una corrección, y ninguna apuesta fabricada."""

    def test_one_synthesis_and_one_correction(self):
        """@covers R-CHL-012"""
        body = _body()
        self.assertIn("se presentan en una síntesis con la razón de cada clasificación", body)
        self.assertIn("una sola corrección general", body)

    def test_the_per_section_question_is_gone(self):
        """@covers R-CHL-012"""
        self.assertIn(
            "no se vuelve a preguntar «¿lo has visto o lo supones?» por cada sección",
            _body(),
            "skills/charter/SKILL.md sigue preguntando «¿lo has visto o lo supones?» por sección",
        )

    def test_revisit_and_fatal_only_for_open_bets(self):
        """@covers R-CHL-012"""
        self.assertIn(
            "`revisit` y `fatal` se preguntan sólo por las apuestas que sigan abiertas",
            _body(),
            "skills/charter/SKILL.md pregunta revisit y fatal por apuestas que no quedan abiertas",
        )

    def test_no_bet_is_fabricated(self):
        """@covers R-CHL-012"""
        body = _body()
        self.assertIn("no se escribe ninguna apuesta", body)
        self.assertIn("el aviso `C20` se conserva", body)
        self.assertIn("la afirmación queda registrada", body)

    def test_the_claim_is_recorded_inside_the_charter(self):
        """@covers R-CHL-012"""
        self.assertIn(
            "la afirmación se registra como comentario bajo `## Bets` del propio acta, con la fecha",
            _body(),
            "skills/charter/SKILL.md no dice dónde queda registrada la afirmación",
        )


class CharterSkillMinimumTest(unittest.TestCase):
    """R-CHL-013 · alcanzado el mínimo, se ofrece cerrar."""

    def test_the_minimum_is_listed(self):
        """@covers R-CHL-013"""
        body = _body()
        for item in (
            "un `Done when` observable",
            "un no-alcance razonado",
            "la clasificación de hechos y apuestas confirmada",
            "sólo si la fila 1 arbitra",
        ):
            self.assertIn(item, body, f"skills/charter/SKILL.md no enumera «{item}» en el mínimo")

    def test_the_draft_is_offered_for_approval(self):
        """@covers R-CHL-013"""
        self.assertIn(
            "se presenta el borrador completo y se pregunta si aprobarlo o profundizar en una sección concreta",
            _body(),
            "skills/charter/SKILL.md no ofrece aprobar o profundizar al alcanzar el mínimo",
        )

    def test_no_interview_on_its_own_initiative(self):
        """@covers R-CHL-013"""
        self.assertIn(
            "no se sigue entrevistando por iniciativa propia",
            _body(),
            "skills/charter/SKILL.md sigue entrevistando por iniciativa propia",
        )


class CharterSkillPreparationTest(unittest.TestCase):
    """R-CHL-014 · lo técnico va después del acta, detectado antes que preguntado."""

    def test_preparation_comes_after_writing_the_charter(self):
        """@covers R-CHL-014"""
        headings = _headings(_body())
        linter = [pos for pos, title in headings if "linter" in title.lower()]
        preparation = [pos for pos, title in headings if "preparación" in title.lower()]
        self.assertTrue(linter, "skills/charter/SKILL.md no tiene una sección que pase el linter")
        self.assertTrue(preparation, "skills/charter/SKILL.md no tiene una sección de preparación")
        self.assertGreater(preparation[0], linter[0], "la preparación no va después del linter")

    def test_the_test_command_is_detected_before_it_is_asked(self):
        """@covers R-CHL-014"""
        self.assertIn(
            "el comando de pruebas se detecta en el repositorio antes de preguntarlo",
            _body(),
            "skills/charter/SKILL.md pregunta el comando de pruebas sin detectarlo antes",
        )

    def test_ambiguity_is_the_only_reason_to_ask(self):
        """@covers R-CHL-014"""
        self.assertIn(
            "sólo se pregunta ante una ambigüedad que impida ejecutar el paso siguiente",
            _body(),
            "skills/charter/SKILL.md pregunta en la preparación sin una ambigüedad que bloquee",
        )

    def test_no_generic_list_of_conventions(self):
        """@covers R-CHL-014"""
        body = _body()
        self.assertIn(
            "una convención sólo se propone cuando es relevante para el proyecto o para el cambio inmediato",
            body,
        )
        self.assertIn("no se presenta una lista genérica de convenciones", body)

    def test_the_generic_table_is_gone(self):
        """@covers R-CHL-014"""
        self.assertNotIn(
            "Errores de una API",
            _body(),
            "skills/charter/SKILL.md sigue ofreciendo la tabla genérica de convenciones",
        )

    def test_the_detected_command_is_not_trusted_blindly(self):
        """@covers R-CHL-014"""
        body = _body()
        self.assertIn("la preparación no ejecuta el comando detectado", body)
        self.assertIn("el rojo del primer `/venoxia:verify` es quien comprueba que prueba algo", body)

    def test_the_npm_placeholder_is_not_a_candidate(self):
        """@covers R-CHL-014"""
        self.assertIn(
            "el marcador de `npm init` («no test specified») no cuenta como candidato",
            _body(),
            "skills/charter/SKILL.md adoptaría el marcador de npm init como comando de pruebas",
        )


class CharterSkillResumeTest(unittest.TestCase):
    """R-CHL-015 · retomar empieza por el estado del acta, no por sus apuestas."""

    def test_the_state_is_summarised_first(self):
        """@covers R-CHL-015"""
        self.assertIn(
            "al retomar se resume el propósito, la primera capability, el estado y los bloqueos",
            _body(),
            "skills/charter/SKILL.md no resume el estado del acta al retomar",
        )

    def test_bets_are_grouped_in_one_view(self):
        """@covers R-CHL-015"""
        self.assertIn(
            "las apuestas abiertas se agrupan en una sola vista",
            _body(),
            "skills/charter/SKILL.md no agrupa las apuestas abiertas",
        )

    def test_one_question_with_three_intentions(self):
        """@covers R-CHL-015"""
        self.assertIn(
            "continuar con la siguiente capability, revisar una sección o resolver una apuesta cuyo hecho ya ocurrió",
            _body(),
            "skills/charter/SKILL.md no pregunta qué quiere hacer el usuario al retomar",
        )

    def test_never_bet_by_bet_first(self):
        """@covers R-CHL-015"""
        self.assertIn(
            "no se pregunta apuesta por apuesta antes de saber qué quiere hacer el usuario",
            _body(),
            "skills/charter/SKILL.md interroga apuesta por apuesta al retomar",
        )

    def test_no_mtime(self):
        """@covers R-CHL-015"""
        self.assertNotIn("mtime", _body(), "skills/charter/SKILL.md usa mtime para adivinar el objetivo")

    def test_a_charter_that_fails_the_linter_is_shown_with_its_blockers(self):
        """@covers R-CHL-015"""
        body = _body()
        self.assertIn("un acta que no pasa el linter se enseña con sus bloqueos antes de la pregunta", body)
        self.assertIn("empezar de cero sigue disponible como respuesta escrita", body)

    def test_starting_over_never_overwrites_without_a_warning(self):
        """@covers R-CHL-015"""
        self.assertIn(
            "antes de pisar el acta anterior se avisa de que la skill no guarda copias y se espera la confirmación explícita del usuario",
            _body(),
            "skills/charter/SKILL.md pisaría el acta anterior sin aviso",
        )


if __name__ == "__main__":
    unittest.main()
