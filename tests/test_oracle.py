#!/usr/bin/env python3
"""Tests de `scripts/oracle.py`: atribución de rojo/verde por requisito.

Cada test monta un `Project()`, le pone `.venoxia/venoxia.json` apuntando al
runner falso de `tests/fake_runner.py` (vía `project.oracle_config`) y escribe
los ficheros de test con `project.test_file(..., result=…)`, que es lo que el
runner falso lee para decidir su código de salida. `FAKE_RUNNER_LOG` deja
constancia de cada invocación, para comprobar que un requisito «missing» no
llega a invocar nada.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.venoxia_fixtures import (
    CHANGE_ID,
    FAKE_RUNNER_PY,
    Project,
    requirement,
)

FAKE_RUNNER_COMMAND = f"python3 {FAKE_RUNNER_PY} {{files}}"


def _log_lines(log_path: Path) -> list[str]:
    """Las líneas del log del runner falso, o una lista vacía si no se creó."""
    if not log_path.is_file():
        return []
    return [line for line in log_path.read_text(encoding="utf-8").splitlines() if line]


class OracleAllGreenTest(unittest.TestCase):
    """R-ORC-001 · un change con todos los requisitos en verde."""

    def test_three_requirements_all_green(self):
        """@covers R-ORC-001"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [
                requirement(id="R-ORC-101", title="Uno", verifies=project.oracle("R-ORC-101")),
                requirement(id="R-ORC-102", title="Dos", verifies=project.oracle("R-ORC-102")),
                requirement(id="R-ORC-103", title="Tres", verifies=project.oracle("R-ORC-103")),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            payload = run.json
            self.assertTrue(payload["all_green"])
            self.assertFalse(payload["all_red"])
            self.assertEqual(payload["counts"]["total"], 3)
            self.assertEqual(payload["counts"]["green"], 3)
            statuses = {result["status"] for result in payload["results"]}
            self.assertEqual(statuses, {"green"})


class OracleRedAttributionTest(unittest.TestCase):
    """R-ORC-002 · un requisito rojo se nombra, no sólo se cuenta."""

    def test_one_red_among_three_is_named(self):
        """@covers R-ORC-002"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [
                requirement(id="R-ORC-201", title="Uno", verifies=project.oracle("R-ORC-201")),
                requirement(
                    id="R-ORC-202",
                    title="Dos",
                    verifies=project.oracle("R-ORC-202", result="red"),
                ),
                requirement(id="R-ORC-203", title="Tres", verifies=project.oracle("R-ORC-203")),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            payload = run.json
            self.assertFalse(payload["all_green"])
            by_id = {result["requirement_id"]: result for result in payload["results"]}
            self.assertEqual(by_id["R-ORC-202"]["status"], "red")
            self.assertEqual(by_id["R-ORC-202"]["exit_code"], 1)
            self.assertEqual(by_id["R-ORC-201"]["status"], "green")
            self.assertEqual(by_id["R-ORC-203"]["status"], "green")


class OracleMissingTest(unittest.TestCase):
    """R-ORC-003 · un oráculo que no existe no se invoca."""

    def test_missing_verifies_is_not_invoked(self):
        """@covers R-ORC-003"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            log_path = project.path("runner.log")
            missing_path = "test/generated/r-orc-301-missing.spec.ts"
            reqs = [
                requirement(id="R-ORC-301", title="Falta", verifies=missing_path),
                requirement(id="R-ORC-302", title="Existe", verifies=project.oracle("R-ORC-302")),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 1, run.describe())
            payload = run.json
            by_id = {result["requirement_id"]: result for result in payload["results"]}
            self.assertEqual(by_id["R-ORC-301"]["status"], "missing")
            self.assertIsNone(by_id["R-ORC-301"]["exit_code"])
            self.assertEqual(by_id["R-ORC-302"]["status"], "green")

            invoked = "\n".join(_log_lines(log_path))
            self.assertNotIn(missing_path, invoked)


class OracleTimeoutTest(unittest.TestCase):
    """R-ORC-004 · un runner que duerme más que el presupuesto."""

    def test_runner_sleeping_past_timeout(self):
        """@covers R-ORC-004"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [
                requirement(
                    id="R-ORC-401",
                    title="Lento",
                    verifies=project.oracle("R-ORC-401", result="sleep 3"),
                ),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID, "--timeout", "1")

            self.assertEqual(run.returncode, 1, run.describe())
            self.assertNotIn("Traceback", run.stderr)
            payload = run.json
            by_id = {result["requirement_id"]: result for result in payload["results"]}
            self.assertEqual(by_id["R-ORC-401"]["status"], "timeout")


class OracleUsageErrorsTest(unittest.TestCase):
    """R-ORC-005 · sin configuración, o sin el marcador, no hay adivinanza."""

    def test_missing_venoxia_json(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.remove(".venoxia/venoxia.json")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("venoxia.json", run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_test_command_without_placeholder(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.oracle_config("python3 -m unittest")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("{files}", run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_nonexistent_change(self):
        """El change no existe: error de uso, no un rojo silencioso."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            run = project.run_oracle("--change", "no-such-change")
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertNotIn("Traceback", run.stderr)


class OracleDryRunTest(unittest.TestCase):
    """R-ORC-006 · «--dry-run» enseña el comando y no toca el runner."""

    def test_dry_run_prints_and_does_not_invoke(self):
        """@covers R-ORC-006"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            log_path = project.path("runner.log")
            reqs = [
                requirement(id="R-ORC-601", title="Uno", verifies=project.oracle("R-ORC-601")),
                requirement(id="R-ORC-602", title="Dos", verifies=project.oracle("R-ORC-602")),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle(
                "--change", CHANGE_ID, "--dry-run", env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertIn("R-ORC-601", run.stdout)
            self.assertIn("R-ORC-602", run.stdout)
            self.assertEqual(_log_lines(log_path), [])

    def test_dry_run_with_zero_requirements_explains_why(self):
        """Un change sin requisitos (p. ej. sin «delta/») no se queda mudo en --dry-run."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            project.delta(CHANGE_ID, project.capability_name, raw="")

            run = project.run_oracle("--change", CHANGE_ID, "--dry-run")

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("Traceback", run.stderr)
            self.assertIn("0 requisitos", run.stdout)
            self.assertTrue(run.stdout.strip())


class OracleRecordTest(unittest.TestCase):
    """R-ORC-007 · el historial se acumula y sobrevive a un fichero corrupto."""

    def _oracle_json(self, project: Project) -> dict:
        return json.loads(project.read(f".venoxia/changes/{CHANGE_ID}/oracle.json"))

    def test_two_records_in_a_row(self):
        """@covers R-ORC-007"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-701", title="Uno", verifies=project.oracle("R-ORC-701"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            first = project.run_oracle_json("--change", CHANGE_ID, "--record")
            second = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(first.returncode, 0, first.describe())
            self.assertEqual(second.returncode, 0, second.describe())
            history = self._oracle_json(project)
            self.assertEqual(history["version"], 1)
            self.assertEqual(history["change"], CHANGE_ID)
            self.assertEqual(len(history["runs"]), 2)
            self.assertNotIn("change", history["runs"][0])

    def test_corrupt_history_is_replaced_without_traceback(self):
        """@covers R-ORC-007"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-702", title="Uno", verifies=project.oracle("R-ORC-702"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            project.write(f".venoxia/changes/{CHANGE_ID}/oracle.json", "{ esto no es JSON")

            run = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertNotIn("Traceback", run.stderr)
            history = self._oracle_json(project)
            self.assertEqual(len(history["runs"]), 1)

    def test_keeps_only_the_last_fifty_runs(self):
        """--record no deja crecer el historial sin límite."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-703", title="Uno", verifies=project.oracle("R-ORC-703"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            record_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            padded_runs = [{"ran_at": f"run-{index}"} for index in range(55)]
            record_path.write_text(
                json.dumps({"version": 1, "change": CHANGE_ID, "runs": padded_runs}),
                encoding="utf-8",
            )

            run = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            history = self._oracle_json(project)
            self.assertEqual(len(history["runs"]), 50)
            # El run nuevo es el único con «counts»: los 55 de relleno no lo
            # traían. Y de los viejos sólo sobreviven los últimos 49.
            self.assertIn("counts", history["runs"][-1])
            self.assertEqual(history["runs"][0]["ran_at"], "run-6")


class OracleSchemaAndMultiplePathsTest(unittest.TestCase):
    """R-ORC-008 · el esquema es estable y varias rutas van en una invocación."""

    def test_top_level_keys_are_exactly_the_schema(self):
        """@covers R-ORC-008"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-801", title="Uno", verifies=project.oracle("R-ORC-801"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(
                set(run.json.keys()),
                {
                    "version",
                    "change",
                    "ran_at",
                    "runner",
                    "results",
                    "counts",
                    "all_green",
                    "all_red",
                },
            )

    def test_two_paths_one_invocation(self):
        """@covers R-ORC-008"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            log_path = project.path("runner.log")
            path_a = project.oracle("R-ORC-802", path="test/generated/r-orc-802-a.spec.ts")
            path_b_relpath = "test/generated/r-orc-802-b.spec.ts"
            project.test_file(path_b_relpath, covers=["R-ORC-802"])
            combined = f"{path_a}, {path_b_relpath}"
            reqs = [requirement(id="R-ORC-802", title="Dos rutas", verifies=combined)]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            lines = _log_lines(log_path)
            self.assertEqual(len(lines), 1)
            self.assertIn(path_a, lines[0])
            self.assertIn(path_b_relpath, lines[0])
            result = run.json["results"][0]
            self.assertEqual(set(result["verifies"]), {path_a, path_b_relpath})


class OracleHostileInputsTest(unittest.TestCase):
    """Barrido de entradas hostiles: ninguna produce un «Traceback»."""

    def test_venoxia_json_is_a_directory(self):
        with Project() as project:
            project.remove(".venoxia/venoxia.json")
            project.path(".venoxia/venoxia.json").mkdir()
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertNotIn("Traceback", run.stderr)
            self.assertEqual(run.returncode, 2, run.describe())

    def test_change_json_is_unreadable(self):
        """`change.json` roto no impide leer el `delta/`: oracle.py no lo necesita."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            project.change(CHANGE_ID, raw="{ esto tampoco es JSON")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertNotIn("Traceback", run.stderr)
            self.assertEqual(run.returncode, 0, run.describe())

    def test_delta_without_requirements(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            project.delta(CHANGE_ID, project.capability_name, raw="")
            run = project.run_oracle_json("--change", CHANGE_ID)
            self.assertNotIn("Traceback", run.stderr)
            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.json["counts"]["total"], 0)
            self.assertFalse(run.json["all_green"])
            self.assertFalse(run.json["all_red"])


if __name__ == "__main__":
    unittest.main()
