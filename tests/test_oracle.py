#!/usr/bin/env python3
"""Tests de `scripts/oracle.py`: atribución de rojo/verde por requisito.

Cada test monta un `Project()`, le pone `.venoxia/venoxia.json` apuntando al
runner falso de `tests/fake_runner.py` (vía `project.oracle_config`) y escribe
los ficheros de test con `project.test_file(..., result=…)`, que es lo que el
runner falso lee para decidir su código de salida. `FAKE_RUNNER_LOG` deja
constancia de cada invocación, para comprobar que un requisito «missing» no
llega a invocar nada.

Las clases a partir de `OracleConfigDetailErrorsTest` cierran el hueco de
cobertura documentado en `TODO.md` (Fase 9, DEF-013): ramas de error poco
frecuentes de `load_config`, `run_one`, `main`, `_load_history` y `record`
que ni el CLI en su uso normal ni las pruebas de arriba llegan a ejercitar.
Las que necesitan forzar un `OSError` en un método concreto de `Path` (un
disco que falla, no un fichero mal escrito) importan `scripts/oracle.py`
directamente y parchean ese método sólo durante la llamada — no hay forma de
provocar esas condiciones por subproceso sin depender de permisos de SO.

`OracleFlagConflictTest` y los dos tests de copia de `OracleRecordTest` son
del change `2026-09-07-oracle-hardening`: dos ataques del abogado del diablo
que el código no cerraba. Nacen en rojo, que es lo que `oracle.py --record`
graba antes de tocar `scripts/oracle.py`.

@covers R-ORC-011
@covers R-ORC-012
"""

from __future__ import annotations

import json
import pathlib
import shlex
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from tests.venoxia_fixtures import (
    CHANGE_ID,
    FAKE_RUNNER_PY,
    ORACLE_PY,
    Project,
    ensure_import_paths,
    requirement,
)

ensure_import_paths()
import oracle  # noqa: E402 — necesita que sys.path ya traiga scripts/

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


class OracleFlagConflictTest(unittest.TestCase):
    """R-ORC-011 · «--dry-run» y «--record» se excluyen: no se graba lo que no se ejecutó."""

    def _project(self, project: Project) -> Path:
        project.oracle_config(FAKE_RUNNER_COMMAND)
        reqs = [requirement(id="R-ORC-711", title="Uno", verifies=project.oracle("R-ORC-711"))]
        project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
        return project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")

    def test_both_flags_are_a_usage_error_that_writes_nothing(self):
        """@covers R-ORC-011"""
        with Project() as project:
            record_path = self._project(project)
            log_path = project.path("runner.log")
            before = sorted(p.name for p in record_path.parent.iterdir())

            run = project.run_oracle(
                "--change", CHANGE_ID, "--dry-run", "--record",
                env={"FAKE_RUNNER_LOG": str(log_path)},
            )

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertFalse(record_path.exists(), run.describe())
            self.assertEqual(sorted(p.name for p in record_path.parent.iterdir()), before)
            self.assertEqual(_log_lines(log_path), [])
            self.assertNotIn("Traceback", run.stderr)

    def test_an_existing_history_is_left_intact(self):
        """@covers R-ORC-011"""
        with Project() as project:
            record_path = self._project(project)
            before = '{"version": 1, "change": "c1", "runs": [{"ran_at": "antes"}]}\n'
            record_path.write_text(before, encoding="utf-8")

            run = project.run_oracle("--change", CHANGE_ID, "--dry-run", "--record")

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertEqual(record_path.read_text(encoding="utf-8"), before)

    def test_the_usage_error_names_both_flags(self):
        """@covers R-ORC-011"""
        with Project() as project:
            self._project(project)

            run = project.run_oracle("--change", CHANGE_ID, "--dry-run", "--record")

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("--dry-run", run.stderr, run.describe())
            self.assertIn("--record", run.stderr, run.describe())


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

    def _corrupt_copies(self, project: Project) -> list[Path]:
        change_dir = project.path(f".venoxia/changes/{CHANGE_ID}")
        return sorted(change_dir.glob("oracle.json.corrupt-*"))

    def test_corrupt_history_is_copied_aside_byte_for_byte(self):
        """@covers R-ORC-012"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-712", title="Uno", verifies=project.oracle("R-ORC-712"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            garbage = "{ esto no es JSON · ni lo será\n"
            project.write(f".venoxia/changes/{CHANGE_ID}/oracle.json", garbage)

            run = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            copies = self._corrupt_copies(project)
            self.assertEqual(len(copies), 1, run.describe())
            self.assertEqual(copies[0].read_text(encoding="utf-8"), garbage)
            self.assertIn(copies[0].name, run.stderr, run.describe())
            self.assertEqual(len(self._oracle_json(project)["runs"]), 1)

    def test_a_missing_history_leaves_no_copy_behind(self):
        """@covers R-ORC-012"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-713", title="Uno", verifies=project.oracle("R-ORC-713"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(self._corrupt_copies(project), [])

    def test_a_copy_that_cannot_be_written_keeps_the_original_in_place(self):
        """@covers R-ORC-012 · sin copia no hay sustitución: los bytes originales se quedan."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oracle.json"
            garbage = "{ roto"
            path.write_text(garbage, encoding="utf-8")
            payload = {"version": 1, "change": CHANGE_ID, "ran_at": "2026-09-07T17:00:00Z", "results": []}
            real_write_text = pathlib.Path.write_text

            def failing_copy(self, *args, **kwargs):
                if ".corrupt-" in self.name:
                    raise OSError(28, "No space left on device")
                return real_write_text(self, *args, **kwargs)

            stderr = __import__("io").StringIO()
            with unittest.mock.patch.object(pathlib.Path, "write_text", failing_copy), \
                    unittest.mock.patch("sys.stderr", stderr):
                oracle.record(path, CHANGE_ID, payload)

            self.assertEqual(path.read_text(encoding="utf-8"), garbage)
            self.assertEqual(sorted(Path(tmp).glob("oracle.json.corrupt-*")), [])
            self.assertIn("no se ha grabado", stderr.getvalue())

    def test_a_run_that_could_not_be_recorded_exits_with_two(self):
        """@covers R-ORC-012 · si --record no pudo grabar, no hay veredicto: código 2."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-714", title="Uno", verifies=project.oracle("R-ORC-714"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            record_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            record_path.write_text("{ roto", encoding="utf-8")
            real_write_text = pathlib.Path.write_text

            def failing_copy(self, *args, **kwargs):
                if ".corrupt-" in self.name:
                    raise OSError(28, "No space left on device")
                return real_write_text(self, *args, **kwargs)

            stderr, stdout = __import__("io").StringIO(), __import__("io").StringIO()
            with unittest.mock.patch.object(pathlib.Path, "write_text", failing_copy), \
                    unittest.mock.patch("sys.stderr", stderr), unittest.mock.patch("sys.stdout", stdout):
                code = oracle.main(["--root", str(project.root), "--change", CHANGE_ID, "--record", "--json"])

            self.assertEqual(code, 2, stderr.getvalue())
            self.assertEqual(record_path.read_text(encoding="utf-8"), "{ roto")

    def test_a_readable_history_with_extra_keys_is_not_corrupt(self):
        """@covers R-ORC-012 · una clave de más no convierte un historial válido en basura."""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-715", title="Uno", verifies=project.oracle("R-ORC-715"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            record_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            record_path.write_text(
                json.dumps({"version": 1, "change": CHANGE_ID, "runs": [{"ran_at": "antes"}], "extra": True}),
                encoding="utf-8",
            )

            run = project.run_oracle_json("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(self._corrupt_copies(project), [])
            self.assertEqual(len(self._oracle_json(project)["runs"]), 2)

    def test_a_second_corruption_never_overwrites_the_first_copy(self):
        """@covers R-ORC-012 · dos corrupciones con la misma marca dejan dos copias."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oracle.json"
            payload = {"version": 1, "change": CHANGE_ID, "ran_at": "2026-09-07T17:00:00Z", "results": []}
            stderr = __import__("io").StringIO()
            with unittest.mock.patch("sys.stderr", stderr):
                path.write_text("{ primera", encoding="utf-8")
                oracle.record(path, CHANGE_ID, payload)
                path.write_text("{ segunda", encoding="utf-8")
                oracle.record(path, CHANGE_ID, payload)

            copies = sorted(Path(tmp).glob("oracle.json.corrupt-*"))
            self.assertEqual(len(copies), 2, [c.name for c in copies])
            self.assertRegex(copies[1].name, r"^oracle\.json\.corrupt-\w+-2$")
            self.assertEqual(
                sorted(c.read_text(encoding="utf-8") for c in copies), ["{ primera", "{ segunda"]
            )

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


class OracleConfigDetailErrorsTest(unittest.TestCase):
    """R-ORC-005 · más formas de una configuración que no se adivina."""

    def test_invalid_json_in_venoxia_json(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.write(".venoxia/venoxia.json", "{ esto no es JSON")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("JSON válido", run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_venoxia_json_is_not_an_object(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.write(".venoxia/venoxia.json", "[]")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("objeto JSON", run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_test_command_key_is_absent(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.write(".venoxia/venoxia.json", json.dumps({"version": 1, "cwd": "."}))
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("test_command", run.stderr)

    def test_test_command_is_an_empty_string(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.oracle_config("")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("test_command", run.stderr)

    def test_cwd_that_does_not_exist_is_rejected(self):
        """@covers R-ORC-005"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND, cwd="no-such-directory")
            run = project.run_oracle("--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("no existe", run.stderr)

    def test_cwd_that_is_not_a_string_falls_back_to_the_default(self):
        """Un `cwd` de tipo raro no revienta: se trata como si no estuviera escrito."""
        with Project() as project:
            project.write(
                ".venoxia/venoxia.json",
                json.dumps({"version": 1, "test_command": FAKE_RUNNER_COMMAND, "cwd": 5}),
            )
            reqs = [requirement(id="R-ORC-051", title="Uno", verifies=project.oracle("R-ORC-051"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.json["runner"]["cwd"], str(project.root))


class OracleRunOneDetailBranchesTest(unittest.TestCase):
    """Ramas de `run_one` fuera de las ya cubiertas por R-ORC-002/003/004."""

    def test_requirement_without_any_verifies_is_missing_outside_dry_run(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [
                requirement(id="R-ORC-052", title="Sin oráculo", omit=("verifies",)),
                requirement(
                    id="R-ORC-053", title="Con oráculo", verifies=project.oracle("R-ORC-053")
                ),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            by_id = {result["requirement_id"]: result for result in run.json["results"]}
            self.assertEqual(by_id["R-ORC-052"]["status"], "missing")
            self.assertIsNone(by_id["R-ORC-052"]["exit_code"])
            self.assertEqual(by_id["R-ORC-053"]["status"], "green")

    def test_unbalanced_quotes_in_test_command_are_reported_as_red(self):
        """@covers R-ORC-002"""
        with Project() as project:
            project.oracle_config('python3 -m unittest {files} "sin cerrar')
            reqs = [requirement(id="R-ORC-054", title="Uno", verifies=project.oracle("R-ORC-054"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            result = run.json["results"][0]
            self.assertEqual(result["status"], "red")
            self.assertIn("no se pudo interpretar", result["output_tail"])

    def test_a_runner_binary_that_does_not_exist_is_reported_as_red(self):
        """@covers R-ORC-002"""
        with Project() as project:
            project.oracle_config("/no/existe/en-absoluto-xyz {files}")
            reqs = [requirement(id="R-ORC-055", title="Uno", verifies=project.oracle("R-ORC-055"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            result = run.json["results"][0]
            self.assertEqual(result["status"], "red")
            self.assertIn("no se pudo lanzar", result["output_tail"])


class OracleDryRunDetailBranchesTest(unittest.TestCase):
    """Ramas de `dry_run_lines` con requisitos de verdad en la lista."""

    def test_requirement_without_verifies_in_a_nonempty_dry_run(self):
        """@covers R-ORC-006"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [
                requirement(id="R-ORC-056", title="Sin oráculo", omit=("verifies",)),
                requirement(
                    id="R-ORC-057", title="Con oráculo", verifies=project.oracle("R-ORC-057")
                ),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle("--change", CHANGE_ID, "--dry-run")

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertIn("R-ORC-056: (sin «verifies:»", run.stdout)
            self.assertIn("R-ORC-057", run.stdout)


class OracleMainCliBranchesTest(unittest.TestCase):
    """Ramas de `main` que ni `run_oracle` ni el resto de la suite ejercitan."""

    def test_root_that_is_not_a_directory(self):
        """@covers R-ORC-005"""
        with Project() as project:
            missing_root = str(project.path("no-existe-en-absoluto"))
            run = project.run(ORACLE_PY, "--root", missing_root, "--change", CHANGE_ID)
            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("no existe", run.stderr)
            self.assertNotIn("Traceback", run.stderr)

    def test_root_without_venoxia_adoption(self):
        """@covers R-ORC-005"""
        with Project() as project:
            with tempfile.TemporaryDirectory() as bare:
                run = project.run(ORACLE_PY, "--root", bare, "--change", CHANGE_ID)
                self.assertEqual(run.returncode, 2, run.describe())
                self.assertIn(".venoxia", run.stderr)
                self.assertNotIn("Traceback", run.stderr)


class OracleTextReportMissingVerdictTest(unittest.TestCase):
    """`render_text`/`_status_color`: el veredicto «incompleto» en modo texto."""

    def test_missing_requirement_renders_the_incomplete_verdict(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-058", title="Sin oráculo", omit=("verifies",))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle("--change", CHANGE_ID, "--no-color")

            self.assertEqual(run.returncode, 1, run.describe())
            self.assertIn("Oráculo incompleto", run.stdout)
            self.assertIn("missing", run.stdout)


class OracleInternalErrorPathsTest(unittest.TestCase):
    """Ramas que ni el CLI ni `Project` alcanzan sin forzar un fallo de E/S.

    Llaman a las funciones de `scripts/oracle.py` directamente, parcheando
    durante la llamada un único método de `pathlib.Path` para la ruta exacta
    que interesa —el resto del sistema de ficheros sigue funcionando con
    normalidad—, igual que `tests/test_report.py` parchea `sys.stdout` para
    simular un terminal que falla.
    """

    def test_color_enabled_returns_false_when_isatty_raises(self):
        class FlakyStdout:
            def isatty(self):
                raise RuntimeError("sin terminal de verdad")

        with unittest.mock.patch("sys.stdout", FlakyStdout()):
            self.assertFalse(oracle.color_enabled(no_color=False))

    def test_load_config_treats_is_file_oserror_as_missing_config(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            root = project.root
            config_path = root / oracle.VENOXIA_DIR / oracle.CONFIG_FILENAME
            original_is_file = pathlib.Path.is_file

            def flaky_is_file(self):
                if self == config_path:
                    raise OSError("disco caído")
                return original_is_file(self)

            with unittest.mock.patch.object(pathlib.Path, "is_file", flaky_is_file):
                with self.assertRaises(oracle.UsageError) as ctx:
                    oracle.load_config(root)
            self.assertIn("venoxia.json", str(ctx.exception))

    def test_load_config_reports_read_text_oserror(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            root = project.root
            config_path = root / oracle.VENOXIA_DIR / oracle.CONFIG_FILENAME
            original_read_text = pathlib.Path.read_text

            def flaky_read_text(self, *args, **kwargs):
                if self == config_path:
                    raise OSError("no se pudo leer")
                return original_read_text(self, *args, **kwargs)

            with unittest.mock.patch.object(pathlib.Path, "read_text", flaky_read_text):
                with self.assertRaises(oracle.UsageError) as ctx:
                    oracle.load_config(root)
            self.assertIn("no se pudo leer", str(ctx.exception))

    def test_load_config_reports_cwd_is_dir_oserror(self):
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND, cwd=".")
            root = project.root
            original_is_dir = pathlib.Path.is_dir

            def flaky_is_dir(self):
                if self == root:
                    raise OSError("no se puede comprobar")
                return original_is_dir(self)

            with unittest.mock.patch.object(pathlib.Path, "is_dir", flaky_is_dir):
                with self.assertRaises(oracle.UsageError):
                    oracle.load_config(root)

    def test_collect_requirements_survives_change_dir_is_dir_oserror(self):
        with Project() as project:
            reqs = [requirement(id="R-ORC-059", verifies=project.oracle("R-ORC-059"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            root = project.root
            change_dir = root / oracle.VENOXIA_DIR / oracle.CHANGES_DIR / CHANGE_ID
            original_is_dir = pathlib.Path.is_dir

            def flaky_is_dir(self):
                if self == change_dir:
                    raise OSError("boom")
                return original_is_dir(self)

            with unittest.mock.patch.object(pathlib.Path, "is_dir", flaky_is_dir):
                with self.assertRaises(oracle.UsageError):
                    oracle.collect_requirements(root, CHANGE_ID)

    def test_collect_requirements_survives_delta_glob_oserror(self):
        with Project() as project:
            reqs = [requirement(id="R-ORC-060", verifies=project.oracle("R-ORC-060"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
            root = project.root
            delta_dir = (
                root / oracle.VENOXIA_DIR / oracle.CHANGES_DIR / CHANGE_ID / oracle.DELTA_DIR
            )
            original_glob = pathlib.Path.glob

            def flaky_glob(self, *args, **kwargs):
                if self == delta_dir:
                    raise OSError("boom")
                return original_glob(self, *args, **kwargs)

            with unittest.mock.patch.object(pathlib.Path, "glob", flaky_glob):
                result = oracle.collect_requirements(root, CHANGE_ID)
            self.assertEqual(result, [])

    def test_load_history_reports_unreadable_file_without_raising(self):
        """@covers R-ORC-007"""
        with Project() as project:
            history_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text('{"version": 1, "runs": []}', encoding="utf-8")
            original_read_text = pathlib.Path.read_text

            def flaky_read_text(self, *args, **kwargs):
                if self == history_path:
                    raise OSError("boom")
                return original_read_text(self, *args, **kwargs)

            with unittest.mock.patch.object(pathlib.Path, "read_text", flaky_read_text):
                result = oracle._load_history(history_path)
            self.assertEqual(result, [])

    def test_load_history_reports_wrong_shape_without_raising(self):
        with Project() as project:
            history_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(
                json.dumps({"version": 1, "runs": "no-es-una-lista"}), encoding="utf-8"
            )
            result = oracle._load_history(history_path)
            self.assertEqual(result, [])

    def test_record_reports_write_text_oserror_without_raising(self):
        with Project() as project:
            history_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            original_write_text = pathlib.Path.write_text

            def flaky_write_text(self, *args, **kwargs):
                if self == history_path:
                    raise OSError("disco lleno")
                return original_write_text(self, *args, **kwargs)

            with unittest.mock.patch.object(pathlib.Path, "write_text", flaky_write_text):
                # No debe reventar: llegar a la siguiente línea ya lo demuestra.
                oracle.record(history_path, CHANGE_ID, {"version": 1, "results": []})
            self.assertFalse(history_path.exists())


# ---------------------------------------------------------------------------
# Runners con nombre · change 2026-09-09-oracle-named-runners
# ---------------------------------------------------------------------------

# Un runner con nombre que también recibe las rutas. El runner falso anota
# «--alt» como si fuera una ruta más, y eso es lo que distingue en el log una
# invocación suya de una del «test_command».
ALT_RUNNER_COMMAND = f"python3 {FAKE_RUNNER_PY} --alt {{files}}"

# Un runner con nombre sin «{files}»: corre tal cual y el log recibe
# exactamente «--verbatim», sin ninguna ruta detrás.
VERBATIM_RUNNER_COMMAND = f"python3 {FAKE_RUNNER_PY} --verbatim"

# Un runner que anota su directorio de trabajo en el fichero que se le pasa.
_CWD_PROBE = (
    "import os, sys; "
    "open(sys.argv[1], 'a', encoding='utf-8').write(os.getcwd() + '\\n')"
)


def _cwd_probe_command(log_path: Path) -> str:
    """El comando del runner sonda: escribe su `cwd` en `log_path`, una línea por invocación."""
    return f"python3 -c {shlex.quote(_CWD_PROBE)} {shlex.quote(str(log_path))}"


def _runners_config(
    project: Project,
    runners: object,
    *,
    test_command: str = FAKE_RUNNER_COMMAND,
    cwd: str = ".",
) -> Path:
    """Escribe `.venoxia/venoxia.json` con `runners` además del `test_command`.

    `Project.oracle_config` no conoce `runners`: este fichero es el único que
    los necesita, y el andamio no forma parte del oráculo de estos requisitos.
    `runners` se serializa tal cual, también cuando no es un objeto: así se
    fabrica el caso negativo de `R-ORC-015`.
    """
    return project.write(
        ".venoxia/venoxia.json",
        json.dumps(
            {"version": 1, "test_command": test_command, "cwd": cwd, "runners": runners},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )


def _with_runner(
    project: Project,
    identifier: str,
    runner: str,
    *,
    result: str | None = None,
    verifies: str | None = None,
) -> str:
    """Un requisito canónico con `runner: <name>` en su bloque de metadatos.

    Sin `verifies` explícito se crea el fichero de test con `project.oracle`,
    igual que en el resto de la suite; con él se escribe la ruta tal cual, que
    es como se fabrica un ancla que no existe en disco.
    """
    path = verifies if verifies is not None else project.oracle(identifier, result=result)
    return requirement(
        id=identifier,
        title=f"Requisito {identifier}",
        verifies=path,
        extra_meta=(("runner", runner),),
    )


class OracleNamedRunnerTest(unittest.TestCase):
    """R-ORC-013 · un requisito elige su runner por nombre."""

    def test_the_named_runner_replaces_the_default_for_that_requirement(self):
        """@covers R-ORC-013"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            log_path = project.path("runner.log")
            reqs = [_with_runner(project, "R-ORC-131", "alt")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            lines = _log_lines(log_path)
            self.assertEqual(len(lines), 1, lines)
            self.assertTrue(lines[0].startswith("--alt\t"), lines)

    def test_a_requirement_without_runner_keeps_the_default(self):
        """@covers R-ORC-013"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            log_path = project.path("runner.log")
            default_path = project.oracle("R-ORC-133")
            reqs = [
                _with_runner(project, "R-ORC-132", "alt"),
                requirement(id="R-ORC-133", title="Por defecto", verifies=default_path),
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            lines = _log_lines(log_path)
            self.assertEqual(len(lines), 2, lines)
            self.assertIn(default_path, lines, lines)
            self.assertEqual(sum(1 for line in lines if line.startswith("--alt\t")), 1, lines)

    def test_the_placeholder_of_a_named_runner_is_substituted(self):
        """@covers R-ORC-013"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            log_path = project.path("runner.log")
            path = project.oracle("R-ORC-134")
            reqs = [_with_runner(project, "R-ORC-134", "alt", verifies=path)]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(_log_lines(log_path), [f"--alt\t{path}"])

    def test_a_runner_with_its_own_cwd_runs_there(self):
        """@covers R-ORC-013"""
        with Project() as project:
            sub = project.path("sub")
            sub.mkdir()
            probe_log = project.path("cwd.log")
            _runners_config(
                project, {"probe": {"command": _cwd_probe_command(probe_log), "cwd": "sub"}}
            )
            reqs = [_with_runner(project, "R-ORC-135", "probe")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            lines = _log_lines(probe_log)
            self.assertEqual(len(lines), 1, lines)
            self.assertEqual(Path(lines[0]).resolve(), sub.resolve())

    def test_the_paths_follow_the_runner_into_its_cwd(self):
        """@covers R-ORC-013"""
        with Project() as project:
            project.path("sub").mkdir()
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND, "cwd": "sub"}})
            log_path = project.path("runner.log")
            path = project.oracle("R-ORC-138", result="red")
            reqs = [_with_runner(project, "R-ORC-138", "alt", verifies=path)]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            # La ruta llega reescrita respecto a «sub» («../test/…»), y la
            # prueba de que apunta al mismo fichero es que el runner falso,
            # que la abre desde «sub», encuentra su marcador y sale en rojo.
            self.assertEqual(_log_lines(log_path), [f"--alt\t../{path}"])
            self.assertEqual(run.json["results"][0]["status"], "red", run.describe())

    def test_a_runner_without_cwd_inherits_the_project_cwd(self):
        """@covers R-ORC-013"""
        with Project() as project:
            base = project.path("base")
            base.mkdir()
            probe_log = project.path("cwd.log")
            _runners_config(
                project, {"probe": {"command": _cwd_probe_command(probe_log)}}, cwd="base"
            )
            reqs = [_with_runner(project, "R-ORC-136", "probe")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            lines = _log_lines(probe_log)
            self.assertEqual(len(lines), 1, lines)
            self.assertEqual(Path(lines[0]).resolve(), base.resolve())

    def test_a_failing_named_runner_is_a_red_requirement(self):
        """@covers R-ORC-013"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            reqs = [_with_runner(project, "R-ORC-137", "alt", result="red")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            result = run.json["results"][0]
            self.assertEqual(result["status"], "red")
            self.assertEqual(result["exit_code"], 1)


class OracleVerbatimRunnerTest(unittest.TestCase):
    """R-ORC-014 · un runner con nombre sin «{files}» corre tal cual."""

    REQUIREMENT_ID = "R-ORC-141"

    def _project(self, project: Project, *, verifies: str | None = None) -> Path:
        _runners_config(project, {"coverage": {"command": VERBATIM_RUNNER_COMMAND}})
        reqs = [_with_runner(project, self.REQUIREMENT_ID, "coverage", verifies=verifies)]
        project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
        return project.path("runner.log")

    def test_the_command_runs_character_for_character(self):
        """@covers R-ORC-014"""
        with Project() as project:
            log_path = self._project(project)

            run = project.run_oracle_json(
                "--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(_log_lines(log_path), ["--verbatim"])

    def test_a_verbatim_runner_that_passes_is_a_green_requirement(self):
        """@covers R-ORC-014"""
        with Project() as project:
            self._project(project)

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(run.json["results"][0]["status"], "green")

    def test_the_verifies_path_is_still_the_anchor(self):
        """@covers R-ORC-014"""
        with Project() as project:
            self._project(project, verifies="test/generated/never-written.spec.ts")

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            self.assertEqual(run.json["results"][0]["status"], "missing")

    def test_a_missing_anchor_does_not_run_the_verbatim_command(self):
        """@covers R-ORC-014"""
        with Project() as project:
            log_path = self._project(project, verifies="test/generated/never-written.spec.ts")

            project.run_oracle_json("--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)})

            self.assertEqual(_log_lines(log_path), [])

    def test_dry_run_prints_the_verbatim_command(self):
        """@covers R-ORC-014"""
        with Project() as project:
            log_path = self._project(project)

            run = project.run_oracle(
                "--change", CHANGE_ID, "--dry-run", env={"FAKE_RUNNER_LOG": str(log_path)}
            )

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertIn(f"{self.REQUIREMENT_ID}: {VERBATIM_RUNNER_COMMAND}", run.stdout)
            self.assertEqual(_log_lines(log_path), [])

    def test_the_default_runner_still_demands_the_placeholder(self):
        """@covers R-ORC-014"""
        with Project() as project:
            _runners_config(
                project,
                {"coverage": {"command": VERBATIM_RUNNER_COMMAND}},
                test_command=f"python3 {FAKE_RUNNER_PY}",
            )
            reqs = [_with_runner(project, self.REQUIREMENT_ID, "coverage")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("{files}", run.stderr)


class OracleUndeclaredRunnerTest(unittest.TestCase):
    """R-ORC-015 · un runner no declarado o mal formado es error de uso, nunca un rojo."""

    DECLARED = {"alt": {"command": ALT_RUNNER_COMMAND}}

    def _project(
        self,
        project: Project,
        runners: object = None,
        *,
        runner: str = "nope",
        with_default: bool = False,
    ) -> Path:
        _runners_config(project, self.DECLARED if runners is None else runners)
        reqs = []
        if with_default:
            reqs.append(
                requirement(id="R-ORC-150", title="Por defecto", verifies=project.oracle("R-ORC-150"))
            )
        reqs.append(_with_runner(project, "R-ORC-151", runner))
        project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))
        return project.path("runner.log")

    def test_an_undeclared_name_is_a_usage_error(self):
        """@covers R-ORC-015"""
        with Project() as project:
            self._project(project)

            run = project.run_oracle("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertNotIn("Traceback", run.stderr)

    def test_nothing_runs_not_even_the_other_requirements(self):
        """@covers R-ORC-015"""
        with Project() as project:
            log_path = self._project(project, with_default=True)

            run = project.run_oracle("--change", CHANGE_ID, env={"FAKE_RUNNER_LOG": str(log_path)})

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertEqual(_log_lines(log_path), [])

    def test_the_message_names_the_runner_and_the_file(self):
        """@covers R-ORC-015"""
        with Project() as project:
            self._project(project)

            run = project.run_oracle("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("nope", run.stderr)
            self.assertIn("venoxia.json", run.stderr)

    def test_nothing_is_recorded(self):
        """@covers R-ORC-015"""
        with Project() as project:
            self._project(project)
            change_dir = project.path(f".venoxia/changes/{CHANGE_ID}")
            before = sorted(path.name for path in change_dir.iterdir())

            run = project.run_oracle("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertEqual(sorted(path.name for path in change_dir.iterdir()), before)
            self.assertFalse((change_dir / "oracle.json").exists())

    def test_dry_run_is_a_usage_error_too(self):
        """@covers R-ORC-015"""
        with Project() as project:
            self._project(project)

            run = project.run_oracle("--change", CHANGE_ID, "--dry-run")

            self.assertEqual(run.returncode, 2, run.describe())

    def test_a_runner_without_a_command(self):
        """@covers R-ORC-015"""
        for runners in ({"alt": {}}, {"alt": {"command": ""}}, {"alt": "no-es-un-objeto"}):
            with self.subTest(runners=runners), Project() as project:
                self._project(project, runners, runner="alt")

                run = project.run_oracle("--change", CHANGE_ID)

                self.assertEqual(run.returncode, 2, run.describe())
                self.assertNotIn("Traceback", run.stderr)

    def test_a_runners_key_that_is_not_an_object(self):
        """@covers R-ORC-015"""
        with Project() as project:
            _runners_config(project, ["alt"])
            reqs = [requirement(id="R-ORC-152", title="Sin runner", verifies=project.oracle("R-ORC-152"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertNotIn("Traceback", run.stderr)

    def test_a_runner_whose_cwd_does_not_exist(self):
        """@covers R-ORC-015"""
        with Project() as project:
            self._project(
                project,
                {"alt": {"command": ALT_RUNNER_COMMAND, "cwd": "no-such-directory"}},
                runner="alt",
            )

            run = project.run_oracle("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 2, run.describe())
            self.assertIn("no-such-directory", run.stderr)


class OracleResultRunnerTest(unittest.TestCase):
    """R-ORC-016 · cada elemento de «results» dice qué runner lo produjo."""

    RUNNER_KEYS = {"name", "command", "cwd"}

    def test_a_named_runner_is_named_in_its_result(self):
        """@covers R-ORC-016"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            reqs = [_with_runner(project, "R-ORC-161", "alt")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            runner = run.json["results"][0]["runner"]
            self.assertEqual(set(runner.keys()), self.RUNNER_KEYS)
            self.assertEqual(runner["name"], "alt")

    def test_the_command_recorded_is_the_one_that_ran(self):
        """@covers R-ORC-016"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            path = project.oracle("R-ORC-162")
            reqs = [_with_runner(project, "R-ORC-162", "alt", verifies=path)]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            command = run.json["results"][0]["runner"]["command"]
            self.assertEqual(command, f"python3 {FAKE_RUNNER_PY} --alt {shlex.quote(path)}")
            self.assertNotIn("{files}", command)

    def test_the_default_runner_has_no_name(self):
        """@covers R-ORC-016"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            reqs = [requirement(id="R-ORC-163", title="Por defecto", verifies=project.oracle("R-ORC-163"))]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            runner = run.json["results"][0]["runner"]
            self.assertEqual(set(runner.keys()), self.RUNNER_KEYS)
            self.assertIsNone(runner["name"])

    def test_the_default_runner_still_records_its_command(self):
        """@covers R-ORC-016"""
        with Project() as project:
            project.oracle_config(FAKE_RUNNER_COMMAND)
            path = project.oracle("R-ORC-164")
            reqs = [requirement(id="R-ORC-164", title="Por defecto", verifies=path)]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            command = run.json["results"][0]["runner"]["command"]
            self.assertEqual(command, f"python3 {FAKE_RUNNER_PY} {shlex.quote(path)}")

    def test_the_working_directory_is_recorded(self):
        """@covers R-ORC-016"""
        with Project() as project:
            sub = project.path("sub")
            sub.mkdir()
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND, "cwd": "sub"}})
            # La ruta de «verifies:» es relativa a la raíz y el runner corre
            # en «sub»: al runner falso le da igual (no abre ficheros que no
            # existen), lo que se mira aquí es el «cwd» que queda grabado.
            reqs = [_with_runner(project, "R-ORC-165", "alt")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            recorded = run.json["results"][0]["runner"]["cwd"]
            self.assertEqual(Path(recorded).resolve(), sub.resolve())

    def test_a_missing_requirement_carries_its_runner_too(self):
        """@covers R-ORC-016"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            reqs = [
                _with_runner(
                    project, "R-ORC-166", "alt", verifies="test/generated/never-written.spec.ts"
                )
            ]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 1, run.describe())
            result = run.json["results"][0]
            self.assertEqual(result["status"], "missing")
            self.assertEqual(set(result["runner"].keys()), self.RUNNER_KEYS)
            self.assertEqual(result["runner"]["name"], "alt")

    def test_the_recorded_history_carries_it(self):
        """@covers R-ORC-016"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            reqs = [_with_runner(project, "R-ORC-167", "alt")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle("--change", CHANGE_ID, "--record")

            self.assertEqual(run.returncode, 0, run.describe())
            history_path = project.path(f".venoxia/changes/{CHANGE_ID}/oracle.json")
            history = json.loads(history_path.read_text(encoding="utf-8"))
            recorded = history["runs"][-1]["results"][0]["runner"]
            self.assertEqual(recorded["name"], "alt")

    def test_the_top_level_keeps_its_eight_keys(self):
        """@covers R-ORC-016"""
        with Project() as project:
            _runners_config(project, {"alt": {"command": ALT_RUNNER_COMMAND}})
            reqs = [_with_runner(project, "R-ORC-168", "alt")]
            project.delta(CHANGE_ID, project.capability_name, added=reqs, declare=("ADDED",))

            run = project.run_oracle_json("--change", CHANGE_ID)

            self.assertEqual(run.returncode, 0, run.describe())
            self.assertEqual(
                set(run.json.keys()),
                {"version", "change", "ran_at", "runner", "results", "counts", "all_green", "all_red"},
            )


if __name__ == "__main__":
    unittest.main()
