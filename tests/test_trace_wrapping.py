#!/usr/bin/env python3
"""`Project.run` bajo `VENOXIA_TRACE_DIR`: el prefijo de `trace` y su ausencia.

`tools/coverage.py` mide la cobertura de `scripts/**/*.py` incluyendo los
subprocesos que la suite lanza (`Project.run`), no sólo el proceso principal
de `unittest`. Para eso, `Project.run` antepone `python3 -m trace --count …`
al argv del subproceso cuando `VENOXIA_TRACE_DIR` está en el entorno efectivo
—el real de `os.environ`, o el que llega por el parámetro `env=`— y no toca
el argv en absoluto cuando no lo está. Este fichero comprueba las dos ramas;
no repite la cobertura de comportamiento de `guardian.py`/`validate.py`, que
vive en sus propios ficheros de test.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_trace_wrapping -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_trace_wrapping.py -q
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from tests.venoxia_fixtures import GUARDIAN_PY, VALIDATE_PY, Project


class ProjectRunWithoutTraceTest(unittest.TestCase):
    """Sin `VENOXIA_TRACE_DIR`, el argv no cambia: es el caso de siempre."""

    def test_argv_is_plain_python_and_script_when_the_variable_is_absent(self) -> None:
        with Project() as project:
            run = project.run(GUARDIAN_PY, stdin="{}")
            self.assertEqual(run.argv, (sys.executable, str(GUARDIAN_PY)))

    def test_extra_env_that_is_not_the_trace_variable_leaves_argv_alone(self) -> None:
        with Project() as project:
            run = project.run(GUARDIAN_PY, stdin="{}", env={"ALGO_MAS": "x"})
            self.assertEqual(run.argv, (sys.executable, str(GUARDIAN_PY)))


class ProjectRunUnderTraceTest(unittest.TestCase):
    """Con `VENOXIA_TRACE_DIR`, el subproceso se lanza bajo `trace --count`."""

    def test_argv_gains_the_exact_trace_prefix_the_contract_names(self) -> None:
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    GUARDIAN_PY, stdin="{}", env={"VENOXIA_TRACE_DIR": trace_dir}
                )
                self.assertEqual(
                    run.argv,
                    (
                        sys.executable,
                        "-m",
                        "trace",
                        "--count",
                        "--file",
                        str(Path(trace_dir) / "counts"),
                        "--coverdir",
                        trace_dir,
                        "--missing",
                        "--ignore-dir",
                        sys.prefix,
                        str(GUARDIAN_PY),
                    ),
                )

    def test_arguments_after_the_script_still_travel_after_it_under_trace(self) -> None:
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    VALIDATE_PY,
                    "--root",
                    str(project.root),
                    "--json",
                    env={"VENOXIA_TRACE_DIR": trace_dir},
                )
                self.assertEqual(
                    run.argv[-4:],
                    (str(VALIDATE_PY), "--root", str(project.root), "--json"),
                )

    def test_the_wrapped_subprocess_still_runs_and_writes_shared_coverage_files(self) -> None:
        # `validate.py` sale por `sys.exit`, no por `os._exit`: es uno de los
        # scripts para los que `trace` sí llega a volcar sus resultados —la
        # salvedad de `guardian.py` está documentada en `tools/coverage.py`.
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    VALIDATE_PY,
                    "--root",
                    str(project.root),
                    "--json",
                    env={"VENOXIA_TRACE_DIR": trace_dir},
                )
                self.assertEqual(run.returncode, 0, run.describe())
                self.assertTrue(run.json["adopted"])
                self.assertTrue((Path(trace_dir) / "counts").exists())
                self.assertTrue((Path(trace_dir) / "validate.cover").exists())

    def test_the_trace_variable_is_read_from_the_merged_environment(self) -> None:
        """`full_env` mezcla `os.environ` con `env=`: por ahí puede llegar la variable."""
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    GUARDIAN_PY,
                    stdin="{}",
                    env={"VENOXIA_TRACE_DIR": trace_dir, "OTRA": "y"},
                )
                self.assertIn("trace", run.argv)


if __name__ == "__main__":
    unittest.main()
