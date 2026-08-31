#!/usr/bin/env python3
"""Reglas V01–V08 del validador: identidad, forma y oráculo del requisito.

Cada regla trae un caso en positivo —el proyecto limpio no la dispara— y al
menos uno en negativo. La disciplina de todos los negativos es la misma y no
admite atajos: se rompe **una** cosa del proyecto canónico y se comprueba que
el conjunto de reglas disparadas es **exactamente** el esperado, nunca que «lo
contiene». Un fixture que dispara la regla que se prueba y de propina otra por
estar mal escrito es un test que aprueba por el motivo equivocado.

Todo se ejecuta contra `scripts/validate.py` por subproceso y con `--json`, que
es la superficie que el resto del plugin consume. El andamio
(`tests/venoxia_fixtures.py`) monta el proyecto dentro de un
`tempfile.TemporaryDirectory` con un `$HOME` falso: ni el repositorio ni el
`$HOME` real se tocan, y no hay red por ninguna parte.

Cómo lanzarlo::

    python3 -m unittest tests.test_rules_early -v
    python3 -m pytest tests/test_rules_early.py -q
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

# La raíz del repositorio en `sys.path`, para que el import cualificado de abajo
# funcione también cuando este fichero se ejecuta directamente
# (`python3 tests/test_rules_early.py`). Con `pytest` o con
# «python3 -m unittest tests.test_rules_early» ya está puesta; esto no la duplica.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import (  # noqa: E402
    CAPABILITY_NAME,
    CHANGE_ID,
    DEFAULT_REQUIREMENT_ID,
    DEFAULT_REQUIREMENT_TITLE,
    LIVE_REQUIREMENT_ID,
    Project,
    live_requirement,
    requirement,
)

# `venoxia_fixtures` ya ha puesto `scripts/` en `sys.path`, así que el validador
# se puede importar como módulo. Se hace para poder examinar `analyse_ears` en
# corto: los casos EARS que sólo se distinguen por un signo de puntuación son
# más claros —y más difíciles de aprobar por accidente— cuando se le preguntan a
# la función directamente, sin un fichero markdown de por medio.
import validate  # noqa: E402

# ---------------------------------------------------------------------------
# Narrativas EARS · una por patrón del contrato §5
#
# Todas dicen «DEBE» y no «SHALL»/«MUST», que dispararía V14 y ensuciaría el
# conjunto de reglas que el test compara.
# ---------------------------------------------------------------------------

EARS_NARRATIVES: dict[str, str] = {
    "event-driven": (
        "WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de "
        "todas las líneas del pedido durante 15 minutos."
    ),
    "state-driven": (
        "WHILE el carrito está bloqueado por otra sesión, el sistema DEBE rechazar "
        "cualquier cambio de línea."
    ),
    "optional-feature": (
        "WHERE el pago repartido está habilitado, el sistema DEBE admitir dos "
        "métodos de pago por pedido."
    ),
    "unwanted-behaviour": (
        "IF el proveedor de pago rechaza el cargo, THEN el sistema DEBE liberar la "
        "reserva de stock del pedido."
    ),
    "ubicuo": (
        "El sistema DEBE registrar cada intento de pago en el diario de auditoría."
    ),
    "complejo": (
        "WHILE el carrito está bloqueado por otra sesión, WHEN el cliente confirma "
        "el pago, el sistema DEBE rechazar la confirmación."
    ),
}

#: Dos cláusulas de arranque: el requisito esconde dos comportamientos.
AMBIGUOUS_NARRATIVE = (
    "WHEN el cliente confirma el pago, el sistema DEBE reservar el stock. WHEN el "
    "cliente cancela el pedido, el sistema DEBE liberar la reserva."
)

#: Una palabra clave que abre una cláusula que no dice nada.
EMPTY_CLAUSE_NARRATIVE = (
    "WHEN, el sistema DEBE reservar el stock del pedido durante 15 minutos."
)


# ---------------------------------------------------------------------------
# Base común
# ---------------------------------------------------------------------------


class EarlyRuleCase(unittest.TestCase):
    """Andamio común: un proyecto limpio nuevo por test y dos aserciones de cabecera."""

    def setUp(self) -> None:
        self.project = Project()
        self.addCleanup(self.project.cleanup)

    # -- Construcción del ámbito --------------------------------------------

    def delta_with(self, *requirements: str) -> None:
        """Reescribe el delta canónico con los requisitos dados en su bloque ADDED."""
        self.project.delta(CHANGE_ID, CAPABILITY_NAME, added=list(requirements))

    # -- Aserciones ----------------------------------------------------------

    def assert_conforms(self) -> None:
        """Exige conformidad total en modo estricto: exit 0 y ni un solo hallazgo."""
        run = self.project.validate_json("--strict")
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.returncode, 0, run.describe())

    def assert_only_rule(self, rule: str) -> list[dict]:
        """Exige que salte esa regla y **sólo** ésa, con exit 1 y severidad de error.

        Se valida sin `--strict` a propósito: así el `1` demuestra que la regla es
        un error, y la comparación de conjuntos —no de pertenencia— demuestra que
        el fixture no ha ensuciado el veredicto con avisos de propina.
        """
        run = self.project.validate_json()
        self.assertEqual(run.rule_set(), {rule}, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())
        findings = run.findings_for(rule)
        for finding in findings:
            self.assertEqual(finding["severity"], "error", run.describe())
        return findings


# ---------------------------------------------------------------------------
# V01 · el identificador está, tiene forma y es único
# ---------------------------------------------------------------------------


class TestRuleV01Identifier(EarlyRuleCase):
    """V01 · el ID está, casa «R-XXX-000» y no lo repite nadie en el ámbito."""

    #: Los cuatro moldes que el contrato rechaza, con por qué fallan.
    MALFORMED_IDS = {
        "R-C-014": "una sola letra de capability, y el mínimo son dos",
        "R-CHECKOUT-014": "ocho letras de capability, y el máximo son cuatro",
        "R-CHK-14": "dos dígitos, y el contrato pide tres",
        "r-chk-014": "en minúsculas, y el molde es en mayúsculas",
    }

    def test_v01_accepts_well_formed_unique_identifiers(self) -> None:
        """Dos requisitos con IDs bien formados y distintos no disparan nada."""
        second = requirement(
            id="R-CHK-015",
            title="Reservation expiry after fifteen minutes",
            verifies=self.project.oracle("R-CHK-015"),
        )
        self.delta_with(requirement(), second)
        self.assert_conforms()

    def test_v01_fails_on_malformed_identifiers(self) -> None:
        """Cada molde de ID inválido dispara V01 y nombra el identificador ofensivo."""
        for bad_id, reason in self.MALFORMED_IDS.items():
            with self.subTest(identifier=bad_id, reason=reason):
                project = Project()
                self.addCleanup(project.cleanup)
                # El oráculo apunta al ID tal cual está escrito: así V08 y V16
                # quedan satisfechas y el único fallo posible es el de V01.
                project.delta(
                    CHANGE_ID,
                    CAPABILITY_NAME,
                    added=[requirement(id=bad_id, verifies=project.oracle(bad_id))],
                )
                run = project.validate_json()
                self.assertEqual(run.rule_set(), {"V01"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                # El ID en minúsculas ni siquiera lo reconoce el encabezado, así
                # que V01 lo denuncia como ausente; el texto ofensivo sale igual.
                self.assertIn(bad_id, run.findings_for("V01")[0]["message"])

    def test_v01_fails_when_the_header_declares_no_identifier(self) -> None:
        """Un encabezado sólo con título deja el requisito sin ID y dispara V01."""
        self.project.test_file("test/checkout/anonimo.spec.ts", covers=[])
        self.delta_with(
            requirement(omit=("id",), verifies="test/checkout/anonimo.spec.ts")
        )
        findings = self.assert_only_rule("V01")
        self.assertIn("no declara identificador", findings[0]["message"])
        # El encabezado no traía nada que pareciera un ID, así que el ejemplo de
        # la pista se escribe una sola vez y con el título entero detrás.
        hint = findings[0]["hint"] or ""
        self.assertEqual(
            hint.count(f"### R-CHK-014 · {DEFAULT_REQUIREMENT_TITLE}"), 1, hint
        )

    def test_v01_fails_when_two_files_declare_the_same_identifier(self) -> None:
        """Un ID repetido en dos deltas dispara V01 nombrando el otro fichero y su línea."""
        original = f".venoxia/changes/{CHANGE_ID}/delta/{CAPABILITY_NAME}.md"
        self.project.delta(CHANGE_ID, "payments", added=[requirement()])

        findings = self.assert_only_rule("V01")
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
        self.assertEqual(finding["file"], f".venoxia/changes/{CHANGE_ID}/delta/payments.md")
        self.assertIn(
            f"{original}:{self._header_line(original, DEFAULT_REQUIREMENT_ID)}",
            finding["message"],
        )

    def test_v01_allows_a_modified_block_to_repeat_a_live_identifier(self) -> None:
        """Un bloque MODIFIED que repite el ID de la capability viva es lo esperado."""
        self.project.delta(
            CHANGE_ID, CAPABILITY_NAME, modified=[live_requirement()]
        )
        # Que el ID vivo aparezca dos veces —en la spec y en el delta— no es un
        # duplicado: es exactamente lo que un MODIFIED significa.
        self.assert_conforms()

    def _header_line(self, relpath: str, requirement_id: str) -> int:
        """Número de línea (1-indexado) del «### <ID>» dentro de ese fichero."""
        for number, line in enumerate(self.project.read(relpath).splitlines(), start=1):
            if line.startswith(f"### {requirement_id}"):
                return number
        self.fail(f"no se encontró el encabezado de «{requirement_id}» en «{relpath}».")
        return 0  # pragma: no cover - self.fail ya cortó


class TestRuleV01MalformedHeader(EarlyRuleCase):
    """V01 · un encabezado que trae el ID mal escrito no es un encabezado sin ID.

    Son dos problemas con dos remedios, y confundirlos hacía que la pista
    produjera markdown roto: interpolaba el encabezado entero —identificador
    incluido— detrás del ID de ejemplo de la documentación, y así proponía
    «### R-CHK-014 · r-chk-999 · Stock reservation…», que duplica el ID y
    sustituye el del proyecto por el del manual.
    """

    #: El ID que el proyecto quiere de verdad; en el fichero va en minúsculas.
    WRITTEN_ID = "R-CHK-999"

    def proposed_header(self, hint: str) -> str:
        """El encabezado que la pista propone entre comillas angulares."""
        match = re.search(r"«(###[^»]+)»", hint or "")
        if match is None:
            self.fail(f"la pista de V01 no propone ningún encabezado: {hint!r}")
        return match.group(1)

    def test_v01_keeps_the_written_identifier_in_the_hint(self) -> None:
        """La pista conserva el ID del proyecto —en mayúsculas— y no lo duplica."""
        self.project.test_file("test/checkout/anonimo.spec.ts", covers=[])
        self.delta_with(
            requirement(
                id=self.WRITTEN_ID.lower(), verifies="test/checkout/anonimo.spec.ts"
            )
        )
        findings = self.assert_only_rule("V01")
        hint = findings[0]["hint"] or ""
        self.assertEqual(
            self.proposed_header(hint),
            f"### {self.WRITTEN_ID} · {DEFAULT_REQUIREMENT_TITLE}",
            hint,
        )
        # Ni el ID de ejemplo de la documentación ni el ID repetido dos veces.
        self.assertNotIn("R-CHK-014", hint)
        self.assertEqual(hint.count(self.WRITTEN_ID), 1, hint)

    def test_v01_does_not_claim_the_header_declares_no_identifier(self) -> None:
        """El mensaje nombra el ID mal escrito en vez de negar que exista."""
        self.project.test_file("test/checkout/anonimo.spec.ts", covers=[])
        self.delta_with(
            requirement(
                id=self.WRITTEN_ID.lower(), verifies="test/checkout/anonimo.spec.ts"
            )
        )
        message = self.assert_only_rule("V01")[0]["message"]
        self.assertIn(self.WRITTEN_ID.lower(), message)
        self.assertNotIn("no declara identificador", message)

    def test_v01_separates_a_missing_separator_from_a_missing_identifier(self) -> None:
        """«### R-CHK-999: Título» trae el ID bien escrito y sin «·»: eso dice."""
        self.project.test_file("test/checkout/anonimo.spec.ts", covers=[])
        self.delta_with(
            requirement(
                id=self.WRITTEN_ID,
                verifies="test/checkout/anonimo.spec.ts",
                separator=":",
            )
        )
        findings = self.assert_only_rule("V01")
        message = findings[0]["message"]
        self.assertIn(self.WRITTEN_ID, message)
        self.assertNotIn("no declara identificador", message)
        self.assertIn("no lo separa del título", message)
        self.assertEqual(
            self.proposed_header(findings[0]["hint"] or ""),
            f"### {self.WRITTEN_ID} · {DEFAULT_REQUIREMENT_TITLE}",
        )

    def test_a_title_with_hyphens_or_digits_is_not_mistaken_for_an_identifier(
        self,
    ) -> None:
        """Distinguir es lo difícil: un título con guiones sigue siendo un título.

        Si el reconocimiento se afloja, estos encabezados —que no traen ningún ID—
        empezarían a recibir el mensaje del ID mal escrito y una pista que les
        parte el título por la primera palabra.
        """
        titles = (
            "Multi-factor authentication on checkout",
            "15-minute reservation window",
            "Check-in flow for guest users",
        )
        for title in titles:
            with self.subTest(title=title):
                project = Project()
                self.addCleanup(project.cleanup)
                project.test_file("test/checkout/anonimo.spec.ts", covers=[])
                project.delta(
                    CHANGE_ID,
                    CAPABILITY_NAME,
                    added=[
                        requirement(
                            omit=("id",),
                            title=title,
                            verifies="test/checkout/anonimo.spec.ts",
                        )
                    ],
                )
                run = project.validate_json()
                self.assertEqual(run.rule_set(), {"V01"}, run.describe())
                finding = run.findings_for("V01")[0]
                self.assertIn("no declara identificador", finding["message"])
                self.assertIn(f"### R-CHK-014 · {title}", finding["hint"] or "")

    def test_v01_hint_repairs_the_requirement_when_pasted_verbatim(self) -> None:
        """Pegar el encabezado de la pista deja la especificación conforme.

        Es la prueba de fuego de una pista: se copia tal cual, se sustituye el
        encabezado y el proyecto pasa las dieciséis reglas en modo estricto. Con
        la pista rota de antes, el encabezado pegado traía dos identificadores y
        la validación seguía en rojo.
        """
        oracle = self.project.oracle(self.WRITTEN_ID)
        markdown = requirement(id=self.WRITTEN_ID.lower(), verifies=oracle)
        self.delta_with(markdown)

        run = self.project.validate_json()
        # El requisito se queda sin ID, así que el «@covers» de su oráculo se
        # queda huérfano: V16 acompaña a V01 mientras el encabezado esté roto.
        self.assertEqual(run.rule_set(), {"V01", "V16"}, run.describe())

        header = self.proposed_header(run.findings_for("V01")[0]["hint"] or "")
        self.delta_with("\n".join([header, *markdown.splitlines()[1:]]))
        self.assert_conforms()


# ---------------------------------------------------------------------------
# V02 · la narrativa encaja en exactamente un patrón EARS
# ---------------------------------------------------------------------------


class TestRuleV02Ears(EarlyRuleCase):
    """V02 · la narrativa encaja en un patrón EARS y en uno solo."""

    def test_v02_accepts_every_ears_pattern(self) -> None:
        """Los cinco patrones EARS del contrato, más el complejo, pasan sin hallazgos."""
        for pattern, narrative in EARS_NARRATIVES.items():
            with self.subTest(pattern=pattern):
                project = Project()
                self.addCleanup(project.cleanup)
                project.delta(
                    CHANGE_ID, CAPABILITY_NAME, added=[requirement(narrative=narrative)]
                )
                run = project.validate_json("--strict")
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    def test_v02_fails_when_two_clauses_open_the_narrative(self) -> None:
        """Dos cláusulas de arranque esconden dos comportamientos en un requisito."""
        self.delta_with(requirement(narrative=AMBIGUOUS_NARRATIVE))
        findings = self.assert_only_rule("V02")
        self.assertIn("«WHEN»", findings[0]["message"])

    def test_v02_fails_when_a_keyword_opens_an_empty_clause(self) -> None:
        """Una palabra clave EARS cuya cláusula queda vacía deja el patrón a medias."""
        self.delta_with(requirement(narrative=EMPTY_CLAUSE_NARRATIVE))
        findings = self.assert_only_rule("V02")
        self.assertIn("«WHEN»", findings[0]["message"])
        self.assertIn("vacía", findings[0]["message"])


class TestRuleV02EmptyClauseIsReallyEmpty(EarlyRuleCase):
    """V02 · cuándo una cláusula está vacía de verdad y cuándo es sólo puntuación.

    Las dos mentiras que este grupo vigila:

    * los dos puntos de «WHEN: el cliente confirma…» cortaban la cláusula y
      dejaban «WHEN» sin resto, así que V02 llamaba vacía a una narrativa llena;
    * una palabra clave que no abre la narrativa es prosa —lo dice el propio
      código—, pero se emitía igual el error, y encima diciendo que el patrón
      «ubicuo» quedaba «a medias». El patrón ubicuo no tiene cláusula que pueda
      quedarse a medias: la frase era imposible.
    """

    COLON_NARRATIVE = (
        "WHEN: el cliente confirma el pago, el sistema DEBE reservar el stock de "
        "todas las líneas del pedido."
    )
    PROSE_KEYWORD_NARRATIVE = (
        "El sistema DEBE registrar cada intento de pago en el diario. WHEN,"
    )

    def test_a_colon_after_the_keyword_does_not_empty_the_clause(self) -> None:
        """«WHEN: …» es event-driven bien escrito, no una cláusula vacía."""
        analysis = validate.analyse_ears(self.COLON_NARRATIVE)
        self.assertEqual(analysis.pattern, "event-driven")
        self.assertIsNone(analysis.problem, analysis)

    def test_a_keyword_that_does_not_open_the_narrative_is_prose(self) -> None:
        """La palabra clave de en medio no fija patrón, así que no puede vaciarlo."""
        analysis = validate.analyse_ears(self.PROSE_KEYWORD_NARRATIVE)
        self.assertEqual(analysis.pattern, "ubicuo")
        self.assertIsNone(analysis.problem, analysis)

    def test_the_ubiquitous_pattern_never_reports_an_empty_clause(self) -> None:
        """Invariante: si hay cláusula vacía, hay un patrón con cláusulas que llenar."""
        narratives = [
            self.COLON_NARRATIVE,
            self.PROSE_KEYWORD_NARRATIVE,
            EMPTY_CLAUSE_NARRATIVE,
            *EARS_NARRATIVES.values(),
            "WHEN:",
            "El sistema DEBE avisar: WHERE, el cliente lo pide.",
        ]
        for narrative in narratives:
            with self.subTest(narrative=narrative):
                analysis = validate.analyse_ears(narrative)
                if analysis.problem == "empty_clause":
                    self.assertNotEqual(analysis.pattern, "ubicuo", analysis)

    def test_an_empty_clause_is_still_an_error(self) -> None:
        """El arreglo no puede pasarse de frenada: «WHEN,» sigue siendo un error."""
        analysis = validate.analyse_ears(EMPTY_CLAUSE_NARRATIVE)
        self.assertEqual(analysis.problem, "empty_clause")
        self.assertEqual(analysis.detail, "WHEN")
        self.assertEqual(validate.analyse_ears("WHEN:").problem, "empty_clause")

    def test_two_clauses_separated_by_a_colon_are_still_ambiguous(self) -> None:
        """Los dos puntos sólo se perdonan pegados a la keyword, no en general."""
        analysis = validate.analyse_ears(
            "WHEN el cliente paga: WHEN el cliente cancela, el sistema DEBE avisar."
        )
        self.assertEqual(analysis.problem, "ambiguous")

    def test_v02_stays_silent_on_a_narrative_written_with_a_colon(self) -> None:
        """De punta a punta: la narrativa con «WHEN:» no produce ni un error.

        Queda el aviso `P02` del parser, que ve una línea con forma de metadato
        («WHEN: …») y avisa de la clave desconocida. Es su trabajo y es un aviso,
        no el error contra una narrativa correcta que emitía V02.
        """
        self.delta_with(requirement(narrative=self.COLON_NARRATIVE))
        run = self.project.validate_json()
        self.assertEqual(run.rule_set(), {"P02"}, run.describe())
        self.assertEqual(run.returncode, 0, run.describe())


# ---------------------------------------------------------------------------
# V03 · hay narrativa antes del primer escenario
# ---------------------------------------------------------------------------


class TestRuleV03Narrative(EarlyRuleCase):
    """V03 · entre el encabezado y el primer escenario hay prosa que dice qué hacer."""

    def test_v03_accepts_a_requirement_with_narrative(self) -> None:
        """Con narrativa entre el encabezado y el primer escenario no salta nada."""
        self.delta_with(requirement(narrative=EARS_NARRATIVES["event-driven"]))
        self.assert_conforms()

    def test_v03_fails_when_the_narrative_is_empty(self) -> None:
        """Sin una línea de prosa antes del primer escenario, salta V03."""
        self.delta_with(requirement(narrative=""))
        findings = self.assert_only_rule("V03")
        self.assertEqual(findings[0]["requirement_id"], DEFAULT_REQUIREMENT_ID)
        self.assertIn(DEFAULT_REQUIREMENT_ID, findings[0]["message"])


# ---------------------------------------------------------------------------
# V04 · al menos un escenario por requisito
# ---------------------------------------------------------------------------


class TestRuleV04Scenarios(EarlyRuleCase):
    """V04 · un requisito sin escenarios no se puede dar por cumplido."""

    def test_v04_accepts_a_requirement_with_one_scenario(self) -> None:
        """Un único escenario bien formado basta para satisfacer V04."""
        self.delta_with(
            requirement(
                scenarios=[
                    (
                        "Stock available on every line",
                        "hay stock disponible en todas las líneas",
                        "se crea la reserva con TTL de 15 minutos",
                    )
                ]
            )
        )
        self.assert_conforms()

    def test_v04_fails_when_the_requirement_has_no_scenario(self) -> None:
        """Cero escenarios dispara V04 y nombra el requisito."""
        self.delta_with(requirement(scenarios=[]))
        findings = self.assert_only_rule("V04")
        self.assertEqual(findings[0]["requirement_id"], DEFAULT_REQUIREMENT_ID)
        self.assertIn(DEFAULT_REQUIREMENT_ID, findings[0]["message"])


# ---------------------------------------------------------------------------
# V05 · cada escenario declara «**WHEN**» y «**THEN**»
# ---------------------------------------------------------------------------


class TestRuleV05ScenarioKeywords(EarlyRuleCase):
    """V05 · todo escenario dice su condición y su efecto observable."""

    SCENARIO_TITLE = "Insufficient stock on one line"

    def test_v05_accepts_a_scenario_with_both_keywords(self) -> None:
        """Un escenario con «**WHEN**» y «**THEN**» no dispara V05."""
        self.delta_with(
            requirement(
                scenarios=[
                    (
                        self.SCENARIO_TITLE,
                        "falta stock en al menos una línea",
                        "responde 409 y no crea ninguna reserva",
                    )
                ]
            )
        )
        self.assert_conforms()

    def test_v05_fails_when_the_scenario_has_no_when(self) -> None:
        """Sin «**WHEN**», el mensaje nombra el escenario y la keyword que falta."""
        self.delta_with(
            requirement(
                scenarios=[
                    (self.SCENARIO_TITLE, None, "responde 409 y no crea ninguna reserva")
                ]
            )
        )
        findings = self.assert_only_rule("V05")
        self.assertIn(self.SCENARIO_TITLE, findings[0]["message"])
        self.assertIn("**WHEN**", findings[0]["message"])
        self.assertNotIn("**THEN**", findings[0]["message"])

    def test_v05_fails_when_the_scenario_has_no_then(self) -> None:
        """Sin «**THEN**», el mensaje nombra el escenario y la keyword que falta."""
        self.delta_with(
            requirement(
                scenarios=[
                    (self.SCENARIO_TITLE, "falta stock en al menos una línea", None)
                ]
            )
        )
        findings = self.assert_only_rule("V05")
        self.assertIn(self.SCENARIO_TITLE, findings[0]["message"])
        self.assertIn("**THEN**", findings[0]["message"])
        self.assertNotIn("**WHEN**", findings[0]["message"])


# ---------------------------------------------------------------------------
# V06 · el requisito declara su oráculo · el corazón del sistema
# ---------------------------------------------------------------------------


class TestRuleV06Oracle(EarlyRuleCase):
    """V06 · «verifies:» está y trae valor. Sin oráculo, el requisito es una opinión."""

    def test_v06_accepts_a_declared_oracle(self) -> None:
        """Con «verifies:» apuntando a un test real, V06 calla."""
        self.delta_with(requirement(verifies=self.project.oracle(DEFAULT_REQUIREMENT_ID)))
        self.assert_conforms()

    def test_v06_fails_when_verifies_is_absent(self) -> None:
        """Sin la línea «verifies:», salta V06 con un hint accionable."""
        self.delta_with(requirement(omit=("verifies",)))
        findings = self.assert_only_rule("V06")
        self.assertEqual(findings[0]["requirement_id"], DEFAULT_REQUIREMENT_ID)
        self.assert_actionable_hint(findings[0])

    def test_v06_fails_when_verifies_is_empty(self) -> None:
        """Una línea «verifies:» sin valor promete un oráculo y no dice cuál."""
        self.delta_with(requirement(verifies=""))
        findings = self.assert_only_rule("V06")
        self.assertIn("vacío", findings[0]["message"])
        self.assert_actionable_hint(findings[0])

    def assert_actionable_hint(self, finding: dict) -> None:
        """El hint de V06 dice qué escribir: «verifies:» y el «@covers» con su ID."""
        hint = finding["hint"] or ""
        self.assertIn("verifies:", hint)
        self.assertIn(f"@covers {DEFAULT_REQUIREMENT_ID}", hint)


# ---------------------------------------------------------------------------
# V07 · el fichero del oráculo existe en disco
# ---------------------------------------------------------------------------


class TestRuleV07OracleExists(EarlyRuleCase):
    """V07 · la ruta de «verifies:», resuelta desde «--root», existe de verdad."""

    def test_v07_accepts_several_existing_paths(self) -> None:
        """Un «verifies:» con varias rutas pasa si todas existen en disco."""
        first = "test/checkout/reserva-feliz.spec.ts"
        second = "test/checkout/reserva-sin-stock.spec.ts"
        self.project.test_file(first, covers=[DEFAULT_REQUIREMENT_ID])
        self.project.test_file(second, covers=[DEFAULT_REQUIREMENT_ID])
        self.delta_with(requirement(verifies=f"{first}, {second}"))
        self.assert_conforms()

    def test_v07_fails_when_the_oracle_file_is_missing(self) -> None:
        """Una ruta de «verifies:» que no existe dispara V07 y nombra dónde se buscó."""
        missing = "test/checkout/todavia-no-existe.spec.ts"
        self.delta_with(requirement(verifies=missing))
        findings = self.assert_only_rule("V07")
        message = findings[0]["message"]
        self.assertIn(missing, message)
        self.assertIn(str(self.project.path(missing)), message)

    def test_v07_says_that_a_directory_is_a_directory(self) -> None:
        """Una ruta que existe pero es un directorio no «no existe»: es otra cosa.

        Decirle «no existe» a quien tiene la carpeta delante le manda crear lo
        que ya está, y esconde el error de verdad: la ruta se quedó a medio
        escribir, sin el nombre del fichero.
        """
        folder = "test/checkout/reservas"
        self.project.path(folder).mkdir(parents=True, exist_ok=True)
        self.delta_with(requirement(verifies=folder))
        findings = self.assert_only_rule("V07")
        message = findings[0]["message"]
        self.assertIn(folder, message)
        self.assertIn("es un directorio, no un fichero", message)
        self.assertNotIn("que no existe", message)
        self.assertIn(folder, findings[0]["hint"] or "")


# ---------------------------------------------------------------------------
# V08 · el fichero del oráculo devuelve el vínculo con «@covers <ID>»
# ---------------------------------------------------------------------------


class TestRuleV08Covers(EarlyRuleCase):
    """V08 · el test nombrado por «verifies:» declara «@covers <ID>». El vínculo es doble."""

    def test_v08_accepts_when_only_one_of_the_paths_covers_the_requirement(self) -> None:
        """Con varias rutas basta que una traiga el «@covers», como fija el contrato §5."""
        without = "test/checkout/sin-covers.spec.ts"
        with_covers = "test/checkout/con-covers.spec.ts"
        self.project.test_file(without, covers=[])
        self.project.test_file(with_covers, covers=[DEFAULT_REQUIREMENT_ID])
        self.delta_with(requirement(verifies=f"{without}, {with_covers}"))
        self.assert_conforms()

    def test_v08_fails_when_the_oracle_file_has_no_covers(self) -> None:
        """Un oráculo que existe pero no cita el ID deja el vínculo en un solo sentido."""
        orphan = "test/checkout/sin-covers.spec.ts"
        self.project.test_file(orphan, covers=[])
        self.delta_with(requirement(verifies=orphan))
        findings = self.assert_only_rule("V08")
        message = findings[0]["message"]
        # El contrato §5 exige que el mensaje nombre el ID y la ruta. Y con una
        # sola ruta el sujeto es singular, así que la negación tiene que ir en
        # el verbo: «El fichero … NO contiene». Un mensaje afirmativo diría lo
        # contrario de lo que pasa, y justo en la regla que cierra el vínculo
        # doble entre requisito y test.
        self.assertIn(DEFAULT_REQUIREMENT_ID, message)
        self.assertIn(orphan, message)
        self.assertIn(f"no contiene «@covers {DEFAULT_REQUIREMENT_ID}»", message)
        self.assertIn(f"@covers {DEFAULT_REQUIREMENT_ID}", findings[0]["hint"] or "")

    def test_v08_fails_when_none_of_the_several_paths_covers_the_requirement(self) -> None:
        """Con varias rutas sin «@covers», el sujeto es plural y el verbo, afirmativo."""
        first = "test/checkout/sin-covers-uno.spec.ts"
        second = "test/checkout/sin-covers-dos.spec.ts"
        self.project.test_file(first, covers=[])
        self.project.test_file(second, covers=[])
        self.delta_with(requirement(verifies=f"{first}, {second}"))
        findings = self.assert_only_rule("V08")
        message = findings[0]["message"]
        self.assertIn(first, message)
        self.assertIn(second, message)
        self.assertIn(
            f"Ninguno de los ficheros de «verifies:» («{first}», «{second}») "
            f"contiene «@covers {DEFAULT_REQUIREMENT_ID}»",
            message,
        )
        # La negación va en el sujeto, no en el verbo: «Ninguno … no contiene»
        # afirmaría lo contrario de lo que se quiere decir.
        self.assertNotIn("no contiene", message)


class TestUnreadableOracle(EarlyRuleCase):
    """Un oráculo que no se deja leer se denuncia como tal, no como «sin @covers».

    Son dos problemas distintos con dos remedios distintos. El validador leía el
    fichero, se tragaba el `P01` del parser, se quedaba con la cadena vacía y
    concluía que faltaba el «@covers»: mandaba escribir una línea que el fichero
    ya traía escrita, y de paso dejaba sin explicar por qué V16 no veía nada
    dentro. Un validador que acusa de lo que no es, no vale para nada.
    """

    LATIN1_ORACLE = "test/checkout/latin1.spec.ts"
    BINARY_ORACLE = "test/checkout/binario.spec.ts"

    def write_latin1(self, relpath: str, covers: str = DEFAULT_REQUIREMENT_ID) -> str:
        """Escribe un test con el «@covers» dentro, pero en latin-1: no es UTF-8."""
        target = self.project.path(relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            f"// @covers {covers}\n// reserva de acentuación: sí, señor\n".encode(
                "latin-1"
            )
        )
        return relpath

    def write_binary(self, relpath: str, covers: str = DEFAULT_REQUIREMENT_ID) -> str:
        """Escribe un fichero binario que **sí** contiene el «@covers»."""
        target = self.project.path(relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f"// @covers {covers}\n".encode() + b"\x00\x01\x02binario")
        return relpath

    def test_an_unreadable_oracle_is_reported_as_unreadable(self) -> None:
        """El hallazgo dice que no se puede leer y por qué, y lo ancla al requisito."""
        path = self.write_latin1(self.LATIN1_ORACLE)
        self.delta_with(requirement(verifies=path))
        run = self.project.validate_json()

        self.assertEqual(run.rule_set(), {"P01"}, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())
        finding = run.findings_for("P01")[0]
        self.assertEqual(finding["severity"], "error", run.describe())
        self.assertIn("No se puede leer", finding["message"])
        self.assertIn("no está codificado en UTF-8", finding["message"])
        # Nombra la ruta tal y como está escrita en «verifies:» y el requisito
        # que la declara: sin eso, el hallazgo no dice a quién le toca arreglarlo.
        self.assertIn(path, finding["message"])
        self.assertIn(DEFAULT_REQUIREMENT_ID, finding["message"])
        self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
        self.assertEqual(
            finding["file"], f".venoxia/changes/{CHANGE_ID}/delta/{CAPABILITY_NAME}.md"
        )

    def test_the_hint_does_not_ask_for_a_line_the_file_already_has(self) -> None:
        """La pista habla de la codificación, no de añadir el «@covers»."""
        path = self.write_latin1(self.LATIN1_ORACLE)
        self.delta_with(requirement(verifies=path))
        run = self.project.validate_json()
        hint = run.findings_for("P01")[0]["hint"] or ""
        self.assertIn(path, hint)
        self.assertIn("UTF-8", hint)
        self.assertNotIn(f"Añade el comentario «@covers {DEFAULT_REQUIREMENT_ID}»", hint)

    def test_a_binary_oracle_carrying_the_covers_is_not_accused_of_missing_it(
        self,
    ) -> None:
        """El fichero trae el «@covers» escrito: acusarle de no traerlo es mentir."""
        path = self.write_binary(self.BINARY_ORACLE)
        self.delta_with(requirement(verifies=path))
        run = self.project.validate_json()

        self.assertNotIn("V08", run.rule_set(), run.describe())
        self.assertEqual(run.rule_set(), {"P01"}, run.describe())
        self.assertIn("bytes nulos", run.findings_for("P01")[0]["message"])

    def test_a_readable_sibling_with_the_covers_still_satisfies_v08(self) -> None:
        """Con dos rutas, la legible con «@covers» cierra V08; la otra se reporta.

        El contrato §5 dice que basta con que **una** de las rutas traiga el
        «@covers», así que V08 calla. Que la otra no se deje leer sigue siendo un
        problema, y se cuenta aparte en vez de disfrazarse de V08.
        """
        unreadable = self.write_latin1(self.LATIN1_ORACLE)
        readable = "test/checkout/con-covers.spec.ts"
        self.project.test_file(readable, covers=[DEFAULT_REQUIREMENT_ID])
        self.delta_with(requirement(verifies=f"{unreadable}, {readable}"))
        run = self.project.validate_json()

        self.assertEqual(run.rule_set(), {"P01"}, run.describe())
        self.assertIn(unreadable, run.findings_for("P01")[0]["hint"] or "")

    def test_v08_still_fires_when_the_readable_oracle_has_no_covers(self) -> None:
        """El arreglo no puede callar V08 donde de verdad falta el «@covers»."""
        orphan = "test/checkout/sin-covers.spec.ts"
        self.project.test_file(orphan, covers=[])
        self.delta_with(requirement(verifies=orphan))
        findings = self.assert_only_rule("V08")
        self.assertIn(
            f"no contiene «@covers {DEFAULT_REQUIREMENT_ID}»", findings[0]["message"]
        )


# ---------------------------------------------------------------------------
# Todas son errores: exit 1
# ---------------------------------------------------------------------------


def _break_v01(project: Project) -> None:
    """Rompe V01: un ID con dos dígitos en vez de tres."""
    project.delta(
        CHANGE_ID,
        CAPABILITY_NAME,
        added=[requirement(id="R-CHK-14", verifies=project.oracle("R-CHK-14"))],
    )


def _break_v02(project: Project) -> None:
    """Rompe V02: dos cláusulas de arranque en la misma narrativa."""
    project.delta(CHANGE_ID, CAPABILITY_NAME, added=[requirement(narrative=AMBIGUOUS_NARRATIVE)])


def _break_v03(project: Project) -> None:
    """Rompe V03: requisito sin narrativa."""
    project.delta(CHANGE_ID, CAPABILITY_NAME, added=[requirement(narrative="")])


def _break_v04(project: Project) -> None:
    """Rompe V04: requisito sin escenarios."""
    project.delta(CHANGE_ID, CAPABILITY_NAME, added=[requirement(scenarios=[])])


def _break_v05(project: Project) -> None:
    """Rompe V05: un escenario sin «**THEN**»."""
    project.delta(
        CHANGE_ID,
        CAPABILITY_NAME,
        added=[requirement(scenarios=[("Sólo la condición", "falta stock", None)])],
    )


def _break_v06(project: Project) -> None:
    """Rompe V06: requisito sin «verifies:»."""
    project.delta(CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("verifies",))])


def _break_v07(project: Project) -> None:
    """Rompe V07: «verifies:» a una ruta que no existe."""
    project.delta(
        CHANGE_ID,
        CAPABILITY_NAME,
        added=[requirement(verifies="test/checkout/todavia-no-existe.spec.ts")],
    )


def _break_v08(project: Project) -> None:
    """Rompe V08: el oráculo existe pero no cita el ID."""
    project.test_file("test/checkout/sin-covers.spec.ts", covers=[])
    project.delta(
        CHANGE_ID,
        CAPABILITY_NAME,
        added=[requirement(verifies="test/checkout/sin-covers.spec.ts")],
    )


#: Una rotura mínima por regla, cada una pensada para disparar sólo la suya.
BREAKERS = {
    "V01": _break_v01,
    "V02": _break_v02,
    "V03": _break_v03,
    "V04": _break_v04,
    "V05": _break_v05,
    "V06": _break_v06,
    "V07": _break_v07,
    "V08": _break_v08,
}


class TestEarlyRulesAreErrors(unittest.TestCase):
    """V01–V08 son errores: tumban la validación aunque no se pida «--strict»."""

    def test_v01_to_v08_are_errors_that_exit_1(self) -> None:
        """Cada una de las ocho reglas sale con severidad «error» y código 1."""
        self.assertEqual(sorted(BREAKERS), [f"V0{n}" for n in range(1, 9)])
        for rule, break_it in BREAKERS.items():
            with self.subTest(rule=rule):
                project = Project()
                self.addCleanup(project.cleanup)
                break_it(project)
                run = project.validate_json()
                self.assertEqual(run.rule_set(), {rule}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                self.assertEqual(run.json["ok"], False, run.describe())
                self.assertGreaterEqual(run.json["counts"]["error"], 1, run.describe())
                for finding in run.findings_for(rule):
                    self.assertEqual(finding["severity"], "error", run.describe())


class TestCleanProjectIsTheBaseline(unittest.TestCase):
    """El punto de partida: el proyecto canónico no dispara ninguna de las ocho."""

    def test_the_clean_project_triggers_no_early_rule(self) -> None:
        """Sin tocar nada, el proyecto canónico pasa V01–V08 incluso en modo estricto."""
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.rules(), [], run.describe())
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.json["counts"]["requirements"], 2, run.describe())
            self.assertIn(
                LIVE_REQUIREMENT_ID,
                project.read(f".venoxia/capabilities/{CAPABILITY_NAME}/spec.md"),
            )


if __name__ == "__main__":
    unittest.main()
