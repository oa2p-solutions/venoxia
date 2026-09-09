#!/usr/bin/env python3
"""V17 y V18: lo que `change.json` y `oracle.json` dicen del estado del change.

`validate.py` comprueba que cada requisito **declare** su oráculo (`V06`,
`V07`, `V08`); estas dos reglas comprueban lo contrario: que el estado que un
change **afirma** —`verified`— esté acreditado por lo que el oráculo dejó
grabado en disco, y que ningún verde haya llegado sin pasar antes por rojo.
Ninguna de las dos ejecuta ningún test: las dos leen `oracle.json`, que
`Project.oracle_record()` fabrica directamente para no pagar el coste de una
suite de verdad en cada caso.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_rules_oracle -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_rules_oracle.py -q
"""

from __future__ import annotations

import json
import unittest

from tests.venoxia_fixtures import (
    CAPABILITY_NAME,
    CHANGE_ID,
    DEFAULT_REQUIREMENT_ID,
    Project,
    requirement,
)

SECOND_REQUIREMENT_ID = "R-CHK-020"


class TestRuleV17VerifiedNeedsOracle(unittest.TestCase):
    """V17 · un change «verified» tiene su oráculo en verde, en disco."""

    def test_does_not_fire_without_verified(self):
        """Sin «verified» declarado, V17 no se evalúa: ni con oráculo ausente.

        @covers R-VAL-006
        """
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("V17", run.rule_set(), run.describe())
            self.assertNotIn("V18", run.rule_set(), run.describe())

    def test_passes_when_the_last_run_is_green_and_covers_the_delta(self):
        """Rojo y luego verde, cubriendo el único requisito del change: sin V17.

        @covers R-VAL-006
        """
        with Project() as project:
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            project.oracle_record(
                CHANGE_ID,
                runs=[
                    {DEFAULT_REQUIREMENT_ID: "red"},
                    {DEFAULT_REQUIREMENT_ID: "green"},
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_fails_when_verified_has_no_oracle_json(self):
        """(a) «verified» sin ningún oracle.json en disco.

        @covers R-VAL-006
        """
        with Project() as project:
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V17"}, run.describe())
            finding = run.findings_for("V17")[0]
            self.assertEqual(finding["severity"], "error")
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
            self.assertIn("verified", finding["message"])
            self.assertIn("oracle.json", finding["message"])
            self.assertIn("/venoxia:verify", finding["hint"])

    def test_fails_when_the_last_run_has_a_red(self):
        """(b) el último run grabado no está en verde.

        @covers R-VAL-006
        """
        with Project() as project:
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            project.oracle_record(CHANGE_ID, runs=[{DEFAULT_REQUIREMENT_ID: "red"}])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V17"}, run.describe())
            finding = run.findings_for("V17")[0]
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
            self.assertIn("no está en verde", finding["message"])

    def test_fails_when_the_last_run_is_green_but_misses_a_requirement(self):
        """(c) el último run está en verde pero no cubre todos los IDs del delta.

        @covers R-VAL-006
        """
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                added=[
                    requirement(),
                    requirement(
                        id=SECOND_REQUIREMENT_ID,
                        title="Segundo requisito del change",
                        verifies=project.oracle(SECOND_REQUIREMENT_ID),
                    ),
                ],
            )
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            # Los dos runs cubren sólo el primer requisito: el segundo nunca se
            # corrió. El rojo previo del primero evita que V18 se cuele aquí.
            project.oracle_record(
                CHANGE_ID,
                runs=[
                    {DEFAULT_REQUIREMENT_ID: "red"},
                    {DEFAULT_REQUIREMENT_ID: "green"},
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V17"}, run.describe())
            finding = run.findings_for("V17")[0]
            self.assertEqual(finding["requirement_id"], SECOND_REQUIREMENT_ID)
            self.assertIn(SECOND_REQUIREMENT_ID, finding["message"])

    def test_fails_when_oracle_json_is_corrupt(self):
        """(d) oracle.json existe y no se puede interpretar como JSON.

        @covers R-VAL-006
        """
        with Project() as project:
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            project.write(
                f".venoxia/changes/{CHANGE_ID}/oracle.json",
                "{esto no es json",
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V17"}, run.describe())
            finding = run.findings_for("V17")[0]
            self.assertIn("no es JSON válido", finding["message"])
            self.assertNotIn("Traceback", run.stdout)
            self.assertNotIn("Traceback", run.stderr)


class TestRuleV18RedBeforeGreen(unittest.TestCase):
    """V18 · aviso: ningún verde debería llegar sin haber pasado antes por rojo."""

    def test_does_not_fire_without_oracle_json(self):
        """Sin oracle.json, V18 no se evalúa: sea cual sea el «state».

        @covers R-VAL-007
        """
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("V18", run.rule_set(), run.describe())

    def test_passes_when_a_red_run_precedes_the_green_one(self):
        """runs=[red, green]: el requisito sí estuvo en rojo antes. Sin V18.

        @covers R-VAL-007
        """
        with Project() as project:
            project.oracle_record(
                CHANGE_ID,
                runs=[
                    {DEFAULT_REQUIREMENT_ID: "red"},
                    {DEFAULT_REQUIREMENT_ID: "green"},
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("V18", run.rule_set(), run.describe())

    def test_warns_when_the_only_run_is_green(self):
        """Un único run, ya en verde: no hay rojo anterior que lo respalde.

        @covers R-VAL-007
        """
        with Project() as project:
            project.oracle_record(CHANGE_ID, runs=[{DEFAULT_REQUIREMENT_ID: "green"}])
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V18"}, run.describe())
            finding = run.findings_for("V18")[0]
            self.assertEqual(finding["severity"], "warning")
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
            self.assertIn(DEFAULT_REQUIREMENT_ID, finding["message"])

    def test_warns_when_every_run_is_green(self):
        """runs=[green, green]: nunca hubo un rojo, ni siquiera en el primero.

        @covers R-VAL-007
        """
        with Project() as project:
            project.oracle_record(
                CHANGE_ID,
                runs=[
                    {DEFAULT_REQUIREMENT_ID: "green"},
                    {DEFAULT_REQUIREMENT_ID: "green"},
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), {"V18"}, run.describe())

    def test_warns_once_per_requirement_not_once_per_change(self):
        """Dos requisitos en verde, sólo uno con rojo antes: un aviso, del otro.

        @covers R-VAL-007
        """
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                added=[
                    requirement(),
                    requirement(
                        id=SECOND_REQUIREMENT_ID,
                        title="Segundo requisito del change",
                        verifies=project.oracle(SECOND_REQUIREMENT_ID),
                    ),
                ],
            )
            project.oracle_record(
                CHANGE_ID,
                runs=[
                    {DEFAULT_REQUIREMENT_ID: "red", SECOND_REQUIREMENT_ID: "green"},
                    {DEFAULT_REQUIREMENT_ID: "green", SECOND_REQUIREMENT_ID: "green"},
                ],
            )
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), {"V18"}, run.describe())
            findings = run.findings_for("V18")
            self.assertEqual(len(findings), 1, run.describe())
            self.assertEqual(findings[0]["requirement_id"], SECOND_REQUIREMENT_ID)


class TestRulesV17V18JsonSchema(unittest.TestCase):
    """Ambas reglas respetan el esquema v1: sólo se añaden claves, nunca se pisan."""

    def test_v17_and_v18_do_not_disturb_the_json_schema(self):
        """@covers R-VAL-006
        @covers R-VAL-007
        """
        with Project() as project:
            project.delta(
                CHANGE_ID,
                CAPABILITY_NAME,
                added=[
                    requirement(),
                    requirement(
                        id=SECOND_REQUIREMENT_ID,
                        title="Segundo requisito del change",
                        verifies=project.oracle(SECOND_REQUIREMENT_ID),
                    ),
                ],
            )
            project.change(CHANGE_ID, state="verified", capabilities=[CAPABILITY_NAME])
            # DEFAULT llega a verde sin haber pasado por rojo (V18) y SECOND
            # sigue en rojo, así que el run entero no está en verde (V17).
            project.oracle_record(
                CHANGE_ID,
                runs=[{DEFAULT_REQUIREMENT_ID: "green", SECOND_REQUIREMENT_ID: "red"}],
            )
            run = project.validate_json("--strict")
            self.assertEqual(
                set(run.json.keys()),
                {"version", "ok", "strict", "root", "counts", "findings", "budget", "adopted"},
                run.describe(),
            )
            rules = {finding["rule"] for finding in run.findings}
            self.assertEqual(rules, {"V17", "V18"}, run.describe())
            for finding in run.findings:
                self.assertIn(
                    finding["severity"],
                    ("error", "warning"),
                    finding,
                )
                if finding["rule"] == "V17":
                    self.assertEqual(finding["severity"], "error")
                if finding["rule"] == "V18":
                    self.assertEqual(finding["severity"], "warning")


class TestRuleV19RunnerMustBeDeclared(unittest.TestCase):
    """V19 · un «runner:» declarado tiene que existir en venoxia.json.

    Del change `2026-09-09-oracle-named-runners`: `runner:` pasa a ser una
    clave reconocida del bloque de metadatos y el validador comprueba, sin
    ejecutar nada, que `.venoxia/venoxia.json` declare ese nombre bajo
    `runners` con un `command` no vacío. Lo que aquí es un error del
    validador sería, en `oracle.py`, un código `2` sin veredicto.
    """

    def _config(self, project: Project, runners: object) -> None:
        project.write(
            ".venoxia/venoxia.json",
            json.dumps(
                {
                    "version": 1,
                    "test_command": "python3 -m unittest {files}",
                    "cwd": ".",
                    "runners": runners,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )

    def _delta_with_runner(self, project: Project, runner: str) -> None:
        project.delta(
            CHANGE_ID,
            CAPABILITY_NAME,
            added=[requirement(extra_meta=(("runner", runner),))],
        )

    def test_fires_on_an_undeclared_runner_name(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._config(project, {"alt": {"command": "python3 tools/coverage.py"}})
            self._delta_with_runner(project, "nope")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V19"}, run.describe())
            finding = run.findings_for("V19")[0]
            self.assertEqual(finding["severity"], "error")
            self.assertEqual(finding["requirement_id"], DEFAULT_REQUIREMENT_ID)
            self.assertIn("nope", finding["message"])
            self.assertIn("venoxia.json", finding["message"])

    def test_fires_without_venoxia_json(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V19"}, run.describe())
            self.assertEqual(run.findings_for("V19")[0]["requirement_id"], DEFAULT_REQUIREMENT_ID)

    def test_a_declared_runner_is_silent(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._config(project, {"alt": {"command": "python3 tools/coverage.py"}})
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.rule_set(), set(), run.describe())

    def test_no_runner_no_rule(self):
        """@covers R-VAL-008"""
        with Project() as project:
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("V19", run.rule_set(), run.describe())

    def test_fires_on_an_empty_runner(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._config(project, {"alt": {"command": "python3 tools/coverage.py"}})
            self._delta_with_runner(project, "")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertIn("V19", run.rule_set(), run.describe())
            self.assertIn("no nombra", run.findings_for("V19")[0]["message"])

    def test_fires_on_a_declared_runner_without_a_command(self):
        """@covers R-VAL-008"""
        for runners in ({"alt": {}}, {"alt": {"command": ""}}, {"alt": "no-es-un-objeto"}):
            with self.subTest(runners=runners), Project() as project:
                self._config(project, runners)
                self._delta_with_runner(project, "alt")
                run = project.validate_json("--strict")
                self.assertEqual(run.returncode, 1, run.describe())
                self.assertEqual(run.rule_set(), {"V19"}, run.describe())

    def test_fires_on_a_declared_runner_whose_cwd_does_not_exist(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._config(
                project,
                {"alt": {"command": "python3 tools/coverage.py", "cwd": "no-such-directory"}},
            )
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V19"}, run.describe())
            self.assertIn("no-such-directory", run.findings_for("V19")[0]["message"])

    def test_a_corrupt_venoxia_json_does_not_crash_the_validator(self):
        """@covers R-VAL-008"""
        with Project() as project:
            project.write(".venoxia/venoxia.json", "{ esto no es JSON")
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.rule_set(), {"V19"}, run.describe())
            self.assertIn("no se pudo leer", run.findings_for("V19")[0]["message"])
            self.assertNotIn("Traceback", run.stderr)

    def test_the_hint_shows_the_entry_to_add(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._config(project, {"other": {"command": "python3 tools/coverage.py"}})
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            self.assertEqual(run.rule_set(), {"V19"}, run.describe())
            self.assertIn('"alt"', run.findings_for("V19")[0]["hint"])

    def test_v19_does_not_disturb_the_json_schema(self):
        """@covers R-VAL-008"""
        with Project() as project:
            self._delta_with_runner(project, "alt")
            run = project.validate_json("--strict")
            # Las siete del esquema más «adopted», que el CLI añade por contrato.
            self.assertEqual(
                set(run.json.keys()),
                {"version", "ok", "strict", "root", "counts", "findings", "budget", "adopted"},
            )


if __name__ == "__main__":
    unittest.main()
