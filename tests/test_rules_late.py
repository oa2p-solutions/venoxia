#!/usr/bin/env python3
"""Las reglas V09–V16 y la interfaz de línea de comandos de `validate.py`.

Cada regla trae su caso en positivo y su caso en negativo, y todos se ejecutan
igual: se monta el proyecto limpio de `Project()`, se rompe **una** cosa y se
comprueba que el conjunto de reglas disparadas es **exactamente** el esperado.
Si al romper `revisit:` saltara además `V11`, el test lo diría: por eso se
compara el conjunto entero y no sólo la pertenencia.

`validate.py` se invoca siempre por subproceso y con `--json`, que es el
contrato del que dependen la skill y el guardián. Lo que no se puede leer del
JSON —el código de salida, el mensaje del proyecto no adoptado, lo que `-q`
recorta— se lee de la salida de texto.

Ninguna fecha está escrita a mano: todas salen de `future_date()`,
`past_date()` o del año en curso, así que la suite sigue en verde dentro de
tres años. Todo ocurre bajo `tempfile.TemporaryDirectory` (lo monta `Project`):
ni el repositorio ni el `$HOME` real se tocan, y no hay red.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_rules_late -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_rules_late.py -q
"""

from __future__ import annotations

import json
import unittest

from tests.venoxia_fixtures import (
    REVISIT_FACT,
    BLOCK_NAMES,
    CAPABILITY_NAME,
    CHANGE_ID,
    DEFAULT_REQUIREMENT_ID,
    DEFAULT_VERIFIES,
    LIVE_REQUIREMENT_ID,
    LIVE_VERIFIES,
    Project,
    future_date,
    live_requirement,
    past_date,
    requirement,
    today,
)

#: Un ID bien formado que no vive en ninguna capability del proyecto limpio.
GHOST_ID = "R-CHK-777"

#: El ID huérfano que un test declara con «@covers» sin especificarlo (V16).
ORPHAN_ID = "R-XXX-999"


def non_iso_date() -> str:
    """Una fecha futura escrita «DD/MM/YYYY»: el día es bueno, el formato no.

    Se deriva de `future_date()` en vez de escribirse a mano para que el caso
    siga siendo «formato equivocado» y nunca se convierta en «fecha caducada».
    """
    year, month, day = future_date().split("-")
    return f"{day}/{month}/{year}"


def impossible_date() -> str:
    """Un «AAAA-02-31» del año que viene: forma ISO correcta, día inexistente.

    El año es relativo a hoy por la misma razón que el resto de fechas de la
    suite; el 31 de febrero no existe en ningún calendario, así que el caso no
    caduca jamás.
    """
    return f"{today().year + 1}-02-31"


class TestRuleV09Confidence(unittest.TestCase):
    """V09 · «confidence:» está y vale high, medium o low."""

    def test_v09_accepts_the_three_documented_levels(self):
        """Los tres niveles del contrato pasan sin un solo hallazgo."""
        for level in ("high", "medium", "low"):
            with self.subTest(confidence=level):
                with Project() as project:
                    # Los rellenos dejan el presupuesto de V11 en el 20 % para
                    # que «low» no arrastre otra regla al informe.
                    project.capability(
                        CAPABILITY_NAME, [live_requirement(), *project.filler(3)]
                    )
                    project.delta(
                        CHANGE_ID,
                        CAPABILITY_NAME,
                        added=[
                            requirement(
                                confidence=level,
                                revisit=REVISIT_FACT if level == "low" else None,
                            )
                        ],
                    )
                    run = project.validate_json("--strict")
                    self.assertEqual(run.returncode, 0, run.describe())
                    self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v09_fails_when_confidence_is_absent(self):
        """Un requisito sin «confidence:» dispara V09 y sólo V09."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("confidence",))]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V09"}, run.describe())
            finding = run.findings_for("V09")[0]
            self.assertEqual(finding["severity"], "error")
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)

    def test_v09_fails_when_the_value_is_not_one_of_the_three_levels(self):
        """«confidence: alto» no es un nivel admitido y el mensaje repite el valor."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(confidence="alto")]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V09"}, run.describe())
            message = run.findings_for("V09")[0]["message"]
            self.assertIn("alto", message)
            self.assertIn("high, medium, low", message)

    def test_v09_rejects_the_levels_written_in_other_letter_cases(self):
        """«High» y «MEDIUM» no son niveles: el contrato §5 los quiere en minúsculas.

        La pertenencia al conjunto {high, medium, low} es literal, y la propia
        pista de la regla ya lo decía. El mensaje separa este caso —la caja
        equivocada— del valor inventado, porque el remedio no es el mismo: aquí
        no hay que elegir otro nivel, sólo escribirlo en minúsculas.
        """
        for level in ("High", "MEDIUM"):
            with self.subTest(confidence=level):
                with Project() as project:
                    project.delta(
                        CHANGE_ID,
                        CAPABILITY_NAME,
                        added=[requirement(confidence=level)],
                    )
                    run = project.validate_json("--strict")
                    self.assertEqual(run.returncode, 1, run.describe())
                    self.assertEqual(run.rule_set(), {"V09"}, run.describe())
                    finding = run.findings_for("V09")[0]
                    self.assertEqual(finding["severity"], "error")
                    self.assertIn(level, finding["message"])
                    self.assertIn(f"«{level.lower()}»", finding["message"])
                    self.assertIn("minúsculas", finding["message"])
                    # No es el mensaje del valor inventado: ése recita los tres
                    # niveles porque no se sabe cuál se quería.
                    self.assertNotIn("high, medium, low", finding["message"])
                    self.assertIn(
                        f"confidence: {level.lower()}", finding["hint"] or ""
                    )

    def test_v09_with_the_wrong_letter_case_does_not_drag_v10_or_v11(self):
        """«LOW» dispara V09 y nada más: sin nivel válido no hay apuesta que contar.

        Es el efecto colateral que el endurecimiento tenía que dejar fijado. Si
        V10 le reclamara «revisit:» o V11 lo metiera en el presupuesto, dos
        reglas estarían apoyándose en un valor que una tercera acaba de
        rechazar, y el informe cobraría tres veces el mismo error.
        """
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(confidence="LOW")]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V09"}, run.describe())
            self.assertIn("LOW", run.findings_for("V09")[0]["message"])

    def test_v09_separates_the_empty_declaration_from_the_absent_one(self):
        """«confidence:» escrita y vacía no es «confidence:» ausente.

        El mensaje señalaba la línea donde el usuario sí había declarado el
        metadato y le decía que no lo declaraba. V06 ya distinguía los dos casos
        —«El “verifies:” de R-… está vacío»— y aquí se hace igual: quien tiene la
        línea escrita necesita saber que le falta el **valor**, no la línea.
        """
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(confidence="")]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V09"}, run.describe())
            finding = run.findings_for("V09")[0]
            self.assertIn("está vacío", finding["message"])
            self.assertNotIn("no declara «confidence:»", finding["message"])
            # Y la línea señalada es la del metadato, no la del encabezado.
            self.assertEqual(
                finding["line"],
                self._line_of(project, "confidence:"),
                run.describe(),
            )

    def test_v09_still_says_no_declara_when_the_line_is_absent(self):
        """El arreglo no puede borrar el otro caso: sin línea, «no declara»."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("confidence",))]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), {"V09"}, run.describe())
            message = run.findings_for("V09")[0]["message"]
            self.assertIn("no declara «confidence:»", message)
            self.assertNotIn("está vacío", message)

    @staticmethod
    def _line_of(project: Project, needle: str) -> int:
        """Número de línea (1-indexado) de la primera línea que empieza por `needle`."""
        relpath = f".venoxia/changes/{CHANGE_ID}/delta/{CAPABILITY_NAME}.md"
        for number, line in enumerate(project.read(relpath).splitlines(), start=1):
            if line.strip().startswith(needle):
                return number
        raise AssertionError(f"no se encontró «{needle}» en «{relpath}».")


class TestRuleV10Revisit(unittest.TestCase):
    """V10 · una apuesta en «low» dice qué hecho la resuelve, y no cuándo caduca."""

    def _low_bet(self, **meta) -> Project:
        """Proyecto con una única apuesta «low» y presupuesto de V11 holgado.

        Cuatro requisitos intachables acompañan a la apuesta, así que el «low»
        es 1 de 5 —el 20 %— y V11 no se cuela en el informe de V10.
        """
        project = Project()
        self.addCleanup(project.cleanup)
        project.capability(CAPABILITY_NAME, [live_requirement(), *project.filler(3)])
        project.delta(
            CHANGE_ID,
            CAPABILITY_NAME,
            added=[requirement(confidence="low", **meta)],
        )
        return project

    def test_v10_accepts_a_low_confidence_bet_that_names_the_fact(self):
        """Una apuesta «low» que dice qué la resuelve cumple el contrato."""
        project = self._low_bet(revisit=REVISIT_FACT)
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v10_does_not_demand_a_revisit_when_the_confidence_is_not_low(self):
        """Un requisito que no es «low» puede no declarar cómo se resuelve su duda.

        Lo que sí se le exige, si lo declara, es que lo declare bien: eso lo
        comprueba `test_v10_judges_the_shape_at_every_confidence_level`.
        """
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                added=[requirement(confidence="medium", revisit=None)],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v10_fails_when_a_low_confidence_bet_has_no_revisit(self):
        """Una apuesta «low» sin «revisit:» dispara V10 y sólo V10."""
        project = self._low_bet()
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertEqual(run.rule_set(), {"V10"}, run.describe())
        finding = run.findings_for("V10")[0]
        self.assertEqual(finding["severity"], "error")
        self.assertIn("revisit", finding["message"])

    def test_v10_separates_the_empty_revisit_from_the_absent_one(self):
        """«revisit:» escrita y vacía no es «revisit:» ausente.

        Decirle «no trae revisit:» a quien tiene la línea escrita —y señalarle
        esa misma línea— es contradecirle con su propio fichero delante.
        """
        project = self._low_bet(revisit="")
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertEqual(run.rule_set(), {"V10"}, run.describe())
        message = run.findings_for("V10")[0]["message"]
        self.assertIn("está vacío", message)
        self.assertNotIn("no trae «revisit:»", message)

    def test_v10_still_says_no_trae_when_the_line_is_absent(self):
        """Y sin la línea, el mensaje sigue siendo el de la ausencia."""
        project = self._low_bet()
        run = project.validate_json("--strict")
        self.assertEqual(run.rule_set(), {"V10"}, run.describe())
        message = run.findings_for("V10")[0]["message"]
        self.assertIn("no trae «revisit:»", message)
        self.assertNotIn("está vacío", message)

    def test_v10_rejects_a_future_date(self):
        """Una fecha es la respuesta que este campo dejó de admitir."""
        written = future_date()
        project = self._low_bet(revisit=written)
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertEqual(run.rule_set(), {"V10"}, run.describe())
        message = run.findings_for("V10")[0]["message"]
        self.assertIn(written, message)
        self.assertIn("es una fecha", message)

    def test_v10_rejects_a_past_date_for_the_same_reason(self):
        """Hacia atrás tampoco: el problema no es que venza, es que no dice qué mirar."""
        project = self._low_bet(revisit=past_date())
        run = project.validate_json("--strict")
        self.assertEqual(run.rule_set(), {"V10"}, run.describe())
        self.assertIn("es una fecha", run.findings_for("V10")[0]["message"])

    def test_v10_rejects_filler_that_means_later(self):
        """«Ya veremos» ocupa la línea sin nombrar nada, que es no tener apuesta."""
        for filler in ("ya veremos", "más adelante", "TBD", "3 meses"):
            with self.subTest(revisit=filler):
                project = self._low_bet(revisit=filler)
                run = project.validate_json("--strict")
                self.assertEqual(run.rule_set(), {"V10"}, run.describe())
                self.assertIn(
                    "no nombra ningún hecho", run.findings_for("V10")[0]["message"]
                )

    def test_v10_judges_the_shape_at_every_confidence_level(self):
        """Sólo «low» está obligada a traer «revisit:»; escribirlo mal lo puede cualquiera."""
        for level in ("high", "medium"):
            with self.subTest(confidence=level):
                with Project() as project:
                    project.delta(
                        CHANGE_ID,
                        CAPABILITY_NAME,
                        added=[requirement(confidence=level, revisit=future_date())],
                    )
                    run = project.validate_json("--strict")
                    self.assertEqual(run.rule_set(), {"V10"}, run.describe())
                    self.assertIn(
                        "es una fecha", run.findings_for("V10")[0]["message"]
                    )

    def test_v10_hint_shows_the_shape_it_wants(self):
        """El remedio enseña la forma que se pide, no la que se acaba de rechazar."""
        project = self._low_bet(revisit=future_date())
        run = project.validate_json("--strict")
        hint = run.findings_for("V10")[0]["hint"]
        self.assertIn("hecho", hint)
        self.assertNotIn("YYYY-MM-DD", hint)


class TestRuleV11UncertaintyBudget(unittest.TestCase):
    """V11 · como mucho el 30 % de los requisitos del ámbito declara «low»."""

    def _budget(self, fillers: int, low_bets: int) -> Project:
        """Proyecto con `1 + fillers` requisitos intachables y `low_bets` apuestas vivas.

        Las apuestas llevan siempre su `revisit:` con un hecho, así que lo
        único que puede saltar es el presupuesto.
        """
        project = Project()
        self.addCleanup(project.cleanup)
        project.capability(CAPABILITY_NAME, [live_requirement(), *project.filler(fillers)])
        bets = []
        for offset in range(low_bets):
            identifier = f"R-LOW-{200 + offset:03d}"
            bets.append(
                requirement(
                    id=identifier,
                    title=f"Uncertain bet {offset}",
                    verifies=project.oracle(identifier),
                    confidence="low",
                    revisit=REVISIT_FACT,
                )
            )
        project.delta(CHANGE_ID, CAPABILITY_NAME, added=bets)
        return project

    def test_v11_passes_below_the_limit(self):
        """Una apuesta de cada diez requisitos —el 10 %— cabe de sobra."""
        project = self._budget(fillers=8, low_bets=1)
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.rule_set(), set(), run.describe())
        self.assertEqual(
            run.json["budget"],
            {"low": 1, "total": 10, "ratio": 0.1, "limit": 0.3, "ok": True},
        )

    def test_v11_passes_at_exactly_thirty_percent(self):
        """Tres apuestas de diez requisitos es el borde exacto del contrato: pasa."""
        project = self._budget(fillers=6, low_bets=3)
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.rule_set(), set(), run.describe())
        self.assertEqual(
            run.json["budget"],
            {"low": 3, "total": 10, "ratio": 0.3, "limit": 0.3, "ok": True},
        )

    def test_v11_fails_above_the_limit(self):
        """Cuatro apuestas de diez —el 40 %— pasan del listón y V11 lo dice con cifras."""
        project = self._budget(fillers=5, low_bets=4)
        run = project.validate_json("--strict")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertEqual(run.rule_set(), {"V11"}, run.describe())
        self.assertEqual(
            run.json["budget"],
            {"low": 4, "total": 10, "ratio": 0.4, "limit": 0.3, "ok": False},
        )
        message = run.findings_for("V11")[0]["message"]
        self.assertIn("40,0 %", message)
        self.assertIn("4 de 10", message)
        self.assertIn("30 %", message)

    def test_v11_passes_when_there_is_no_requirement_at_all(self):
        """Un `.venoxia/` vacío no tiene apuestas que medir: el presupuesto se cumple."""
        with Project(scaffold=False) as project:
            project.adopt()
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())
            self.assertEqual(
                run.json["budget"],
                {"low": 0, "total": 0, "ratio": 0.0, "limit": 0.3, "ok": True},
            )


class TestBudgetHasASingleSourceOfTruth(unittest.TestCase):
    """V11, el campo `budget` del JSON y la línea de cierre cuentan lo mismo.

    Había dos cuentas: V11 medía descartando los niveles mal escritos y el
    informe minusculaba por su cuenta. Con cuatro «LOW» de diez, el texto cerraba
    con «presupuesto excedido» y el JSON con `ok: false` mientras no existía
    ningún V11 que lo respaldase: el veredicto del informe contradecía al de las
    reglas, en la única cifra que el plugin publica sobre cuánta incertidumbre se
    permite.
    """

    def _project(self, fillers: int, bets: int, confidence: str = "low") -> Project:
        """`1 + fillers` requisitos intachables y `bets` apuestas con ese nivel."""
        project = Project()
        self.addCleanup(project.cleanup)
        project.capability(CAPABILITY_NAME, [live_requirement(), *project.filler(fillers)])
        blocks = []
        for offset in range(bets):
            identifier = f"R-LOW-{200 + offset:03d}"
            blocks.append(
                requirement(
                    id=identifier,
                    title=f"Uncertain bet {offset}",
                    verifies=project.oracle(identifier),
                    confidence=confidence,
                    revisit=REVISIT_FACT,
                )
            )
        project.delta(CHANGE_ID, CAPABILITY_NAME, added=blocks)
        return project

    def assert_one_truth(self, project: Project) -> dict:
        """El JSON, el texto y V11 dicen el mismo número y el mismo veredicto."""
        run = project.validate_json()
        budget = run.json["budget"]

        text = project.validate("--no-color").stdout
        lines = [line for line in text.splitlines() if line.startswith("Presupuesto")]
        self.assertEqual(len(lines), 1, text)
        line = lines[0]
        self.assertIn(f"{budget['low']} de {budget['total']} requisito", line)
        self.assertTrue(
            line.endswith("dentro" if budget["ok"] else "excedido"), line
        )

        findings = run.findings_for("V11")
        # La equivalencia, en las dos direcciones: si el presupuesto se excede
        # hay V11, y si hay V11 el presupuesto se excede.
        self.assertEqual(bool(findings), not budget["ok"], run.describe())
        if findings:
            self.assertIn(
                f"{budget['low']} de {budget['total']}", findings[0]["message"]
            )
        return budget

    def test_the_three_numbers_agree_below_the_limit(self):
        """Una apuesta de diez: dentro, y nadie dice lo contrario."""
        budget = self.assert_one_truth(self._project(fillers=8, bets=1))
        self.assertEqual(budget, {"low": 1, "total": 10, "ratio": 0.1, "limit": 0.3, "ok": True})

    def test_the_three_numbers_agree_at_the_exact_border(self):
        """Tres de diez es el borde exacto del contrato: pasa, y sin V11."""
        budget = self.assert_one_truth(self._project(fillers=6, bets=3))
        self.assertEqual(budget, {"low": 3, "total": 10, "ratio": 0.3, "limit": 0.3, "ok": True})

    def test_the_three_numbers_agree_above_the_limit(self):
        """Cuatro de diez: excedido en el JSON, en el texto y en V11."""
        budget = self.assert_one_truth(self._project(fillers=5, bets=4))
        self.assertEqual(budget, {"low": 4, "total": 10, "ratio": 0.4, "limit": 0.3, "ok": False})

    def test_the_three_numbers_agree_when_the_letter_case_is_invalid(self):
        """Cuatro «LOW» de diez: la caja mal escrita no es una apuesta declarada.

        Es el escenario que delataba las dos cuentas. «LOW» no es un nivel —lo
        dice V09— así que no cuenta como apuesta en ninguna de las tres cifras:
        ni el JSON, ni el texto, ni V11.
        """
        project = self._project(fillers=5, bets=4, confidence="LOW")
        budget = self.assert_one_truth(project)
        self.assertEqual(budget, {"low": 0, "total": 10, "ratio": 0.0, "limit": 0.3, "ok": True})
        run = project.validate_json()
        self.assertEqual(run.rule_set(), {"V09"}, run.describe())

    def test_an_empty_scope_agrees_too(self):
        """Sin requisitos no hay presupuesto que imprimir ni V11 que emitir."""
        with Project(scaffold=False) as project:
            project.adopt()
            run = project.validate_json()
            self.assertEqual(
                run.json["budget"],
                {"low": 0, "total": 0, "ratio": 0.0, "limit": 0.3, "ok": True},
            )
            self.assertEqual(run.findings_for("V11"), [])
            text = project.validate("--no-color").stdout
            self.assertNotIn("Presupuesto de incertidumbre", text)


class TestRuleV12DeltaBlocks(unittest.TestCase):
    """V12 · cada delta declara al menos un bloque de requisitos."""

    def test_v12_accepts_each_of_the_four_block_headers(self):
        """Los cuatro nombres de bloque del contrato cuentan como declaración."""
        for name in BLOCK_NAMES:
            with self.subTest(block=name):
                with Project() as project:
                    project.delta(CHANGE_ID, CAPABILITY_NAME, declare=(name,))
                    run = project.validate_json("--strict")
                    self.assertEqual(run.returncode, 0, run.describe())
                    self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v12_fails_when_the_delta_declares_no_block(self):
        """Un delta con requisitos pero sin encabezado de bloque dispara V12 y sólo V12."""
        with Project() as project:
            relpath = f".venoxia/changes/{CHANGE_ID}/delta/{CAPABILITY_NAME}.md"
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                raw="# Delta de checkout\n\n" + requirement() + "\n",
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V12"}, run.describe())
            finding = run.findings_for("V12")[0]
            self.assertEqual(finding["severity"], "error")
            self.assertEqual(finding["file"], relpath)
            self.assertIn(relpath, finding["message"])


class TestRuleV13LiveReferences(unittest.TestCase):
    """V13 · lo que un delta cambia, retira o renombra existe en una capability viva."""

    def test_v13_accepts_a_modified_requirement_that_exists_live(self):
        """Un MODIFIED que cita el ID vivo de la capability es exactamente lo esperado."""
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                modified=[
                    requirement(
                        id=LIVE_REQUIREMENT_ID,
                        title="Cart total recalculation, revisited",
                        verifies=LIVE_VERIFIES,
                    )
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v13_fails_when_modified_names_an_unknown_id(self):
        """Un MODIFIED sobre un ID que no vive en ninguna capability dispara V13."""
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                modified=[
                    requirement(
                        id=GHOST_ID,
                        title="Requisito fantasma",
                        verifies=project.oracle(GHOST_ID),
                    )
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V13"}, run.describe())
            finding = run.findings_for("V13")[0]
            self.assertEqual(finding["severity"], "error")
            self.assertEqual(finding["requirement_id"], GHOST_ID)
            self.assertIn("MODIFIED", finding["message"])
            self.assertIn(GHOST_ID, finding["message"])

    def test_v13_fails_when_removed_names_an_unknown_id(self):
        """Retirar un requisito que nunca existió también dispara V13."""
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                removed=[
                    requirement(
                        id=GHOST_ID,
                        title="Requisito fantasma",
                        verifies=project.oracle(GHOST_ID),
                    )
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V13"}, run.describe())
            self.assertIn("REMOVED", run.findings_for("V13")[0]["message"])

    def test_v13_is_not_evaluated_without_live_capabilities(self):
        """Sin capabilities vivas en disco no hay base contra la que comparar: V13 calla."""
        with Project() as project:
            project.remove(f".venoxia/capabilities/{CAPABILITY_NAME}/spec.md")
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                modified=[
                    requirement(
                        id=GHOST_ID,
                        title="Requisito fantasma",
                        verifies=project.oracle(GHOST_ID),
                    )
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())


class TestRuleV14EnglishModals(unittest.TestCase):
    """V14 · la prosa va en español: sin «SHALL» ni «MUST» en la narrativa."""

    def _with_modal(self, project: Project, modal: str) -> None:
        """Sustituye el requisito del delta por uno con el modal inglés en la narrativa."""
        project.delta(
            CHANGE_ID,
            CAPABILITY_NAME,
            added=[
                requirement(
                    narrative=(
                        f"WHEN el cliente confirma el pago, el sistema {modal} reservar "
                        "el stock de todas las líneas del pedido durante 15 minutos."
                    )
                )
            ],
        )

    def test_v14_passes_when_the_narrative_uses_the_spanish_modal(self):
        """La narrativa canónica dice «DEBE» y no produce ningún aviso."""
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v14_warns_when_the_narrative_uses_shall(self):
        """«SHALL» en la narrativa es aviso, no error: exit 0 sin «--strict»."""
        with Project() as project:
            self._with_modal(project, "SHALL")
            run = project.validate_json()
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), {"V14"}, run.describe())
            finding = run.findings_for("V14")[0]
            self.assertEqual(finding["severity"], "warning")
            self.assertIn("SHALL", finding["message"])

    def test_v14_warns_when_the_narrative_uses_must(self):
        """«MUST» se denuncia igual que «SHALL», y también como aviso."""
        with Project() as project:
            self._with_modal(project, "MUST")
            run = project.validate_json()
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), {"V14"}, run.describe())
            self.assertIn("MUST", run.findings_for("V14")[0]["message"])

    def test_v14_warning_becomes_a_failure_under_strict(self):
        """Con «--strict» el mismo aviso de V14 tumba la validación."""
        with Project() as project:
            self._with_modal(project, "SHALL")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V14"}, run.describe())


class TestRuleV15Provenance(unittest.TestCase):
    """V15 · el comportamiento nuevo dice de dónde viene."""

    def test_v15_passes_when_the_added_requirement_declares_from(self):
        """El requisito canónico del bloque ADDED trae «from:» y no genera aviso."""
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v15_warns_when_from_is_absent_in_an_added_block(self):
        """Un requisito ADDED sin «from:» es aviso: exit 0 sin «--strict»."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("from",))]
            )
            run = project.validate_json()
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), {"V15"}, run.describe())
            finding = run.findings_for("V15")[0]
            self.assertEqual(finding["severity"], "warning")
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
            self.assertIn("from", finding["message"])

    def test_v15_warning_becomes_a_failure_under_strict(self):
        """Con «--strict» la falta de «from:» deja de ser un detalle."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("from",))]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V15"}, run.describe())


class TestRuleV15CanActuallyFire(unittest.TestCase):
    """V15 · la regla tiene que poder saltar, y por el motivo que dice.

    El aviso se decidía consultando los requisitos vivos de la capability, que
    salen de releer **el mismo fichero** que se está validando: la evidencia era
    siempre el propio texto y «capability sin requisitos previos» resultaba
    inobservable. Estos tests fijan las dos vías por las que V15 sí puede saltar
    —cada una con su redacción— y se ponen en rojo si alguna vuelve a quedarse
    muda.
    """

    #: El requisito que inaugura una capability suelta, fuera de `capabilities/`.
    NEW_CAPABILITY_ID = "R-SHP-001"

    def test_an_added_requirement_without_from_always_warns(self):
        """La vía clara: el delta lo declara nuevo y eso no depende de nada vivo."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("from",))]
            )
            run = project.validate_json()
            self.assertEqual(run.rule_set(), {"V15"}, run.describe())
            message = run.findings_for("V15")[0]["message"]
            self.assertIn("nuevo", message)
            self.assertIn(DEFAULT_REQUIREMENT_ID, message)

    def test_a_requirement_that_opens_a_capability_warns_and_says_so(self):
        """La segunda vía: un fichero de capability del que no hay nada vivo."""
        with Project() as project:
            loose = "docs/spec-shipping.md"
            project.write(
                loose,
                "# Capability: shipping\n\n"
                + requirement(
                    id=self.NEW_CAPABILITY_ID,
                    title="Shipping estimate on checkout",
                    verifies=project.oracle(self.NEW_CAPABILITY_ID),
                    omit=("from",),
                )
                + "\n",
            )
            run = project.validate_json(loose)
            self.assertEqual(run.rule_set(), {"V15"}, run.describe())
            message = run.findings_for("V15")[0]["message"]
            self.assertIn(self.NEW_CAPABILITY_ID, message)
            self.assertIn("inaugura la capability", message)

    def test_a_removed_requirement_is_never_called_new(self):
        """Un requisito de un bloque REMOVED es una baja, no un estreno.

        El delta se llama «payments.md» a propósito: es el caso en el que la
        capability del fichero no tiene requisitos vivos y la regla, midiendo la
        novedad por ahí, acababa pidiéndole su procedencia a una baja y
        llamándola «El requisito nuevo». Describir como alta lo que el delta
        declara como baja es decir lo contrario de lo que pasa.
        """
        with Project() as project:
            project.delta(
                CHANGE_ID, "payments", removed=[live_requirement(omit=("from",))]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), set(), run.describe())
            self.assertEqual(run.returncode, 0, run.describe())

    def test_a_modified_requirement_is_not_asked_for_its_provenance_either(self):
        """Un MODIFIED cita un ID que ya vivía: tampoco estrena nada."""
        with Project() as project:
            project.delta(
                CHANGE_ID, "payments", modified=[live_requirement(omit=("from",))]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), set(), run.describe())


class TestRuleV16OrphanCovers(unittest.TestCase):
    """V16 · ningún test declara «@covers» de un ID que no existe."""

    def test_v16_passes_when_every_covers_names_a_known_requirement(self):
        """Los oráculos del proyecto limpio sólo cubren IDs especificados."""
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_v16_warns_when_a_test_covers_an_unknown_id(self):
        """Un «@covers R-XXX-999» sin requisito detrás es aviso: exit 0 sin «--strict»."""
        with Project() as project:
            # El mismo oráculo sigue cubriendo R-CHK-014, así que V08 calla y el
            # único hallazgo posible es el «@covers» huérfano.
            project.test_file(
                DEFAULT_VERIFIES, covers=[DEFAULT_REQUIREMENT_ID, ORPHAN_ID]
            )
            run = project.validate_json()
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), {"V16"}, run.describe())
            finding = run.findings_for("V16")[0]
            self.assertEqual(finding["severity"], "warning")
            self.assertEqual(finding["requirement_id"], ORPHAN_ID)
            self.assertEqual(finding["file"], DEFAULT_VERIFIES)
            self.assertIn(ORPHAN_ID, finding["message"])
            self.assertIn(DEFAULT_VERIFIES, finding["message"])

    def test_v16_warning_becomes_a_failure_under_strict(self):
        """Con «--strict» el «@covers» huérfano tumba la validación."""
        with Project() as project:
            project.test_file(
                DEFAULT_VERIFIES, covers=[DEFAULT_REQUIREMENT_ID, ORPHAN_ID]
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V16"}, run.describe())


class TestCommandLineInterface(unittest.TestCase):
    """El CLI de §5: códigos de salida, ámbito, formato y verbosidad."""

    def test_cli_exits_zero_when_the_specification_conforms(self):
        """El proyecto limpio sale con 0 y lo dice en español."""
        with Project() as project:
            run = project.validate("--no-color")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertIn("La especificación cumple el contrato.", run.stdout)

    def test_cli_exits_one_when_the_specification_does_not_conform(self):
        """Un requisito sin oráculo hace salir con 1."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("verifies",))]
            )
            run = project.validate("--no-color")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertIn("incumple el contrato", run.stdout)

    def test_cli_exits_two_when_the_path_does_not_exist(self):
        """Una ruta que no existe es error de uso: código 2 y aviso por stderr."""
        with Project() as project:
            run = project.validate("no/existe.md")
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("no existe la ruta", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_cli_exits_two_on_an_unknown_flag(self):
        """Un flag que el CLI no conoce también es error de uso."""
        with Project() as project:
            run = project.validate("--vuela-bajo")
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertEqual(run.stdout, "")

    def test_cli_exits_two_when_change_is_combined_with_paths(self):
        """«--change» ya acota el ámbito: mezclarlo con rutas sueltas es error de uso."""
        with Project() as project:
            run = project.validate("--change", CHANGE_ID, ".venoxia")
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("--change", run.stderr)

    def test_cli_exits_two_when_the_change_does_not_exist(self):
        """Pedir un change que no está en disco es error de uso, no incumplimiento."""
        with Project() as project:
            run = project.validate("--change", "no-existe")
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("no existe el change", run.stderr)

    def test_cli_says_in_spanish_that_the_project_has_not_adopted_venoxia(self):
        """Sin `.venoxia/` el plugin no estorba: mensaje en español y exit 0."""
        with Project(scaffold=False) as project:
            run = project.validate()
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertIn("todavía no ha adoptado Venoxia", run.stdout)
            self.assertIn("No hay especificación que validar", run.stdout)

    def test_strict_turns_a_warning_into_a_failure(self):
        """El mismo proyecto con un solo aviso sale 0 sin «--strict» y 1 con él."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("from",))]
            )
            lenient = project.validate_json()
            strict = project.validate_json("--strict")
            self.assertEqual(lenient.returncode, 0, lenient.describe())
            self.assertEqual(strict.returncode, 1, strict.describe())
            self.assertEqual(lenient.json["counts"], strict.json["counts"])
            self.assertTrue(lenient.json["ok"])
            self.assertFalse(strict.json["ok"])

    def test_strict_changes_nothing_when_there_are_only_errors(self):
        """Con errores y ningún aviso, «--strict» no cambia ni el código ni el informe."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("verifies",))]
            )
            lenient = project.validate_json()
            strict = project.validate_json("--strict")
            self.assertEqual(lenient.returncode, 1, lenient.describe())
            self.assertEqual(strict.returncode, 1, strict.describe())
            self.assertEqual(lenient.rules(), strict.rules())
            self.assertEqual(lenient.json["counts"], strict.json["counts"])

    def test_change_narrows_the_scope_to_a_single_change(self):
        """Con dos changes, validar sólo el limpio da 0 y validar el roto da 1."""
        with Project() as project:
            project.change("c2", capabilities=[CAPABILITY_NAME])
            project.delta(
                "c2",
                CAPABILITY_NAME,
                added=[
                    requirement(
                        id="R-CHK-020", title="Requisito roto", omit=("verifies",)
                    )
                ],
            )

            clean = project.validate_json("--change", CHANGE_ID)
            self.assertEqual(clean.returncode, 0, clean.describe())
            self.assertEqual(clean.rule_set(), set(), clean.describe())
            self.assertEqual(clean.json["counts"]["deltas"], 1)

            broken = project.validate_json("--change", "c2")
            self.assertEqual(broken.returncode, 1, broken.describe())
            self.assertEqual(broken.rule_set(), {"V06"}, broken.describe())

            everything = project.validate_json()
            self.assertEqual(everything.returncode, 1, everything.describe())
            self.assertEqual(everything.json["counts"]["deltas"], 2)

    def test_json_output_contains_nothing_but_json(self):
        """Con «--json» todo el stdout se parsea de una vez con `json.loads`."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("verifies",))]
            )
            run = project.validate("--json")
            self.assertEqual(run.returncode, 1, run.describe())
            payload = json.loads(run.stdout)
            self.assertEqual(payload["version"], 1)
            self.assertFalse(payload["ok"])

    def test_json_output_stays_json_on_a_project_without_venoxia(self):
        """El aviso de «proyecto no adoptado» va por stderr y no ensucia el JSON."""
        with Project(scaffold=False) as project:
            run = project.validate("--json")
            self.assertEqual(run.returncode, 0, run.describe())
            payload = json.loads(run.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["counts"]["requirements"], 0)
            self.assertIn("todavía no ha adoptado Venoxia", run.stderr)

    def test_quiet_reduces_the_output_to_the_summary(self):
        """«-q» deja el resumen y se lleva el detalle de cada hallazgo."""
        with Project() as project:
            project.delta(
                CHANGE_ID, CAPABILITY_NAME, added=[requirement(omit=("verifies",))]
            )
            full = project.validate("--no-color")
            quiet = project.validate("--no-color", "-q")
            self.assertEqual(quiet.returncode, full.returncode)
            self.assertLess(len(quiet.stdout), len(full.stdout))
            self.assertIn("Presupuesto de incertidumbre", quiet.stdout)
            self.assertIn("incumple el contrato", quiet.stdout)
            self.assertNotIn("V06", quiet.stdout)
            self.assertIn("V06", full.stdout)

    def test_an_explicit_path_to_a_loose_delta_file_is_validated(self):
        """Un PATH a un delta fuera de `.venoxia/` se valida como delta."""
        with Project() as project:
            identifier = "R-LOO-001"
            project.write(
                "specs/loose-delta.md",
                "## ADDED Requirements\n\n"
                + requirement(
                    id=identifier,
                    title="Loose delta requirement",
                    verifies=project.oracle(identifier),
                )
                + "\n",
            )
            run = project.validate_json("--strict", "specs/loose-delta.md")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())
            self.assertEqual(run.json["counts"]["deltas"], 1)
            self.assertEqual(run.json["counts"]["capabilities"], 0)
            self.assertEqual(run.json["counts"]["requirements"], 1)


if __name__ == "__main__":
    unittest.main()
