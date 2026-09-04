#!/usr/bin/env python3
"""`Project.run` bajo `VENOXIA_TRACE_DIR` y el envoltorio `tools/trace_run.py`.

`tools/coverage.py` mide la cobertura de `scripts/**/*.py` incluyendo los
subprocesos que la suite lanza (`Project.run`), no sólo el proceso principal
de `unittest`. Para eso, `Project.run` antepone `[sys.executable,
tools/trace_run.py]` al argv del subproceso cuando `VENOXIA_TRACE_DIR` está en
el entorno efectivo —el real de `os.environ`, o el que llega por el parámetro
`env=`— y no toca el argv en absoluto cuando no lo está.

`tools/trace_run.py` existe por dos motivos que este fichero comprueba por
separado:

1. Bajo `python3 -m trace`, `trace.main()` atrapa el `SystemExit` de lo que
   ejecuta y nunca lo relanza: cualquier script que salga con `sys.exit(N)`
   para `N != 0` devolvía `0` al proceso que lo lanzó. `ProjectRunUnderTraceTest`
   y `TraceRunScriptTest` comprueban que el código de salida real sobrevive.
2. `scripts/guardian.py` termina siempre con `os._exit(0)`, que se salta el
   volcado de `trace`. `test_guardian_cover_survives_its_own_os_exit`
   comprueba que ya no mide 0 % para siempre.

No repite la cobertura de comportamiento de `guardian.py`/`validate.py`, que
vive en sus propios ficheros de test.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_trace_wrapping -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_trace_wrapping.py -q
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.venoxia_fixtures import GUARDIAN_PY, TRACE_RUN_PY, VALIDATE_PY, Project


class ProjectRunWithoutTraceTest(unittest.TestCase):
    """Sin `VENOXIA_TRACE_DIR`, el argv no cambia: es el caso de siempre.

    Las dos pruebas fuerzan `VENOXIA_TRACE_DIR=""` explícitamente en vez de
    confiar en que la variable esté ausente del entorno ambiente: si este
    fichero se ejecuta **dentro** de `python3 tools/coverage.py` —que la
    define para medirse a sí mismo—, `full_env` la heredaría igual que
    cualquier otra variable de `os.environ`, y el argv sí llevaría el
    envoltorio. Una cadena vacía es, para `Project.run`, lo mismo que no
    tenerla puesta en absoluto (`if trace_dir:` es falso para `""`).
    """

    def test_argv_is_plain_python_and_script_when_the_variable_is_absent(self) -> None:
        with Project() as project:
            run = project.run(GUARDIAN_PY, stdin="{}", env={"VENOXIA_TRACE_DIR": ""})
            self.assertEqual(run.argv, (sys.executable, str(GUARDIAN_PY)))

    def test_extra_env_that_is_not_the_trace_variable_leaves_argv_alone(self) -> None:
        with Project() as project:
            run = project.run(
                GUARDIAN_PY, stdin="{}", env={"ALGO_MAS": "x", "VENOXIA_TRACE_DIR": ""}
            )
            self.assertEqual(run.argv, (sys.executable, str(GUARDIAN_PY)))


class ProjectRunUnderTraceTest(unittest.TestCase):
    """Con `VENOXIA_TRACE_DIR`, el subproceso se lanza bajo `tools/trace_run.py`."""

    def test_argv_gains_the_exact_wrapper_prefix_the_contract_names(self) -> None:
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    GUARDIAN_PY, stdin="{}", env={"VENOXIA_TRACE_DIR": trace_dir}
                )
                self.assertEqual(
                    run.argv,
                    (sys.executable, str(TRACE_RUN_PY), str(GUARDIAN_PY)),
                )

    def test_arguments_after_the_script_still_travel_after_it_under_the_wrapper(self) -> None:
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
                    run.argv,
                    (
                        sys.executable,
                        str(TRACE_RUN_PY),
                        str(VALIDATE_PY),
                        "--root",
                        str(project.root),
                        "--json",
                    ),
                )

    def test_the_wrapped_subprocess_still_runs_and_writes_shared_coverage_files(self) -> None:
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

    def test_guardian_cover_survives_its_own_os_exit(self) -> None:
        """El hueco que documentaba `tools/coverage.py`: ya no mide 0 % para siempre."""
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    GUARDIAN_PY, stdin="{}", env={"VENOXIA_TRACE_DIR": trace_dir}
                )
                self.assertEqual(run.returncode, 0, run.describe())
                cover_path = Path(trace_dir) / "guardian.cover"
                self.assertTrue(cover_path.exists(), "guardian.cover no se escribió")
                executed_lines = sum(
                    1
                    for line in cover_path.read_text(encoding="utf-8").splitlines()
                    if line.lstrip()[:1].isdigit()
                )
                self.assertGreater(executed_lines, 0)

    def test_the_trace_variable_is_read_from_the_merged_environment(self) -> None:
        """`full_env` mezcla `os.environ` con `env=`: por ahí puede llegar la variable."""
        with Project() as project:
            with tempfile.TemporaryDirectory() as trace_dir:
                run = project.run(
                    GUARDIAN_PY,
                    stdin="{}",
                    env={"VENOXIA_TRACE_DIR": trace_dir, "OTRA": "y"},
                )
                self.assertIn(str(TRACE_RUN_PY), run.argv)


class TraceRunScriptTest(unittest.TestCase):
    """`tools/trace_run.py` en sí mismo, sin pasar por `Project.run`."""

    def _write_exit_script(self, directory: Path, code: int) -> Path:
        script = directory / "exit_with_code.py"
        script.write_text(f"import sys\nsys.exit({code})\n", encoding="utf-8")
        return script

    def test_preserves_the_exact_exit_code_without_trace(self) -> None:
        # `env=` se construye a mano, sin `VENOXIA_TRACE_DIR`, en vez de dejar
        # que el subproceso herede `os.environ` tal cual: si este fichero
        # corre dentro de `python3 tools/coverage.py` (que sí la define, para
        # medirse a sí mismo), heredarla activaría `trace` sin que este test
        # lo pidiera, escribiendo cuentas de un fichero que este mismo test
        # borra al salir del `with` — justo el ruido que «sin trace» quiere
        # descartar.
        env = {key: value for key, value in os.environ.items() if key != "VENOXIA_TRACE_DIR"}
        with tempfile.TemporaryDirectory() as workdir:
            script = self._write_exit_script(Path(workdir), 3)
            result = subprocess.run(
                [sys.executable, str(TRACE_RUN_PY), str(script)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            self.assertEqual(result.returncode, 3, result.stderr)

    def test_preserves_the_exact_exit_code_under_trace(self) -> None:
        with tempfile.TemporaryDirectory() as workdir:
            script = self._write_exit_script(Path(workdir), 3)
            with tempfile.TemporaryDirectory() as trace_dir:
                env = dict(os.environ, VENOXIA_TRACE_DIR=trace_dir)
                result = subprocess.run(
                    [sys.executable, str(TRACE_RUN_PY), str(script)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=env,
                )
                self.assertEqual(result.returncode, 3, result.stderr)

    def test_with_no_arguments_fails_with_usage_error(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TRACE_RUN_PY)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("uso:", result.stderr)


if __name__ == "__main__":
    unittest.main()
