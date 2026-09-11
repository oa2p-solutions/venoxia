#!/usr/bin/env python3
"""La puerta local: `tools/check.py` y el hook de `pre-push` que la invoca.

Los jobs del CI, encadenados en un solo comando que corre antes de cada
`push`: la suite en la matriz de Python dentro de contenedores, la cobertura,
la puerta de `scripts/gate.py` sobre este mismo repositorio y la validación
del plugin. Un veredicto único con los códigos del núcleo: `0` cumple, `1`
no cumple, `2` no se pudo comprobar.

Nada de esto ejecuta la puerta de verdad —tardaría minutos—: se comprueba lo
que lista, cómo falla y cómo propaga el veredicto, con pasos falsos donde hace
falta.

@covers R-CI-019
@covers R-CI-020
@covers R-CI-021

Cómo lanzarlo::

    python3 -m unittest tests.test_check -v
"""

from __future__ import annotations

import importlib.util
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import REPO_ROOT  # noqa: E402

CHECK = REPO_ROOT / "tools" / "check.py"
HOOK = REPO_ROOT / ".githooks" / "pre-push"
WORKFLOW = REPO_ROOT / ".forgejo" / "workflows" / "ci.yml"
README = REPO_ROOT / "README.md"

# Tres pasos desde 2026-09-09-technical-contract: la cobertura corre dentro del
# gate como runner de R-TEC-004, no como paso propio (R-CI-019).
STEP_NAMES = ("matrix", "gate", "plugin-validate")


def run_check(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Lanza `tools/check.py` por subproceso desde la raíz del repositorio."""
    return subprocess.run(
        [sys.executable, str(CHECK), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def workflow_matrix_versions() -> list[str]:
    """Las versiones de Python que declara la matriz del workflow."""
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r"python-version:\s*\[([^\]]+)\]", text)
    assert match, "el workflow no declara «python-version: [...]»"
    return [v.strip().strip("'\"") for v in match.group(1).split(",")]


def load_check_module():
    """Importa `tools/check.py` como módulo para probar su aritmética sin lanzarla."""
    spec = importlib.util.spec_from_file_location("venoxia_check", CHECK)
    module = importlib.util.module_from_spec(spec)
    # `dataclass` busca el módulo en `sys.modules` al construir la clase.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def path_with_only(*executables: str) -> str:
    """Un `PATH` con un solo directorio que contiene únicamente los ejecutables dados.

    `python3` siempre está, porque los pasos lo invocan; el resto se enlaza al
    binario real si existe, y si no, se crea un stub que sale con 0.
    """
    tmp = tempfile.mkdtemp(prefix="venoxia-path-")
    os.symlink(sys.executable, os.path.join(tmp, "python3"))
    for name in executables:
        real = shutil.which(name)
        target = os.path.join(tmp, name)
        if real:
            os.symlink(real, target)
        else:
            Path(target).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(target, 0o755)
    return tmp


class TestTheThreeSteps(unittest.TestCase):
    """R-CI-019 · Tres pasos con nombre, un veredicto único."""

    def test_list_names_the_three_steps_with_their_commands_and_runs_nothing(self):
        run = run_check("--list")
        self.assertEqual(run.returncode, 0, run.stderr)
        for name in STEP_NAMES:
            self.assertRegex(run.stdout, rf"(?m)^{re.escape(name)}\b", f"falta el paso «{name}»")
        self.assertNotRegex(
            run.stdout, r"(?m)^coverage\b", "coverage ya no es un paso propio: corre dentro del gate"
        )
        self.assertIn("scripts/gate.py --root", run.stdout)
        self.assertIn("claude plugin validate", run.stdout)
        # No se ha ejecutado nada: ni un resumen de resultados ni tiempos.
        self.assertNotIn("✓", run.stdout)
        self.assertNotIn("✗", run.stdout)

    def test_an_unknown_option_is_a_usage_error(self):
        run = run_check("--no-such-flag")
        self.assertEqual(run.returncode, 2)
        self.assertIn("--no-such-flag", run.stderr)

    def test_one_failing_step_turns_the_verdict_red_and_shows_its_output(self):
        check = load_check_module()
        out = io.StringIO()
        steps = [
            check.Step("uno", [[sys.executable, "-c", "print('todo bien')"]]),
            check.Step("dos", [[sys.executable, "-c", "import sys; print('aquí está el fallo'); sys.exit(1)"]]),
        ]
        code = check.run_steps(steps, out=out)
        self.assertEqual(code, 1)
        text = out.getvalue()
        self.assertIn("aquí está el fallo", text, "el final de la salida del paso fallido no aparece")
        self.assertRegex(text, r"✗\s+dos")
        self.assertRegex(text, r"✓\s+uno")

    def test_every_step_green_is_exit_zero(self):
        check = load_check_module()
        out = io.StringIO()
        steps = [
            check.Step(name, [[sys.executable, "-c", "pass"]]) for name in STEP_NAMES
        ]
        self.assertEqual(check.run_steps(steps, out=out), 0)
        self.assertNotIn("✗", out.getvalue())

    def test_a_missing_executable_is_exit_two_and_names_it(self):
        env = dict(os.environ, PATH=path_with_only("docker"))
        # Con docker presente y `claude` ausente, la comprobación no puede
        # validar el plugin: no aprueba lo que no ha mirado.
        run = run_check(env=env)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("claude", run.stderr)


class TestTheMatrixInContainers(unittest.TestCase):
    """R-CI-020 · Un contenedor por versión, nunca como root, o se omite a la vista."""

    def test_one_docker_run_per_version_of_the_workflow_matrix(self):
        run = run_check("--list")
        self.assertEqual(run.returncode, 0, run.stderr)
        versions = workflow_matrix_versions()
        docker_lines = [l for l in run.stdout.splitlines() if "docker run" in l]
        self.assertEqual(len(docker_lines), len(versions), run.stdout)
        for version in versions:
            self.assertTrue(
                any(f"python:{version}-slim" in l for l in docker_lines),
                f"ningún comando usa la imagen python:{version}-slim",
            )

    def test_containers_are_removed_when_they_finish(self):
        run = run_check("--list")
        for line in (l for l in run.stdout.splitlines() if "docker run" in l):
            self.assertIn("--rm", line)

    def test_the_suite_failing_in_one_version_turns_the_matrix_red(self):
        check = load_check_module()
        out = io.StringIO()
        green = [sys.executable, "-c", "print('verde')"]
        red = [sys.executable, "-c", "import sys; print('rojo en 3.13'); sys.exit(1)"]
        steps = [check.Step("matrix", [green, red, green])]
        self.assertEqual(check.run_steps(steps, out=out), 1)
        text = out.getvalue()
        self.assertRegex(text, r"✗\s+matrix")
        self.assertIn("rojo en 3.13", text)

    def test_never_as_root(self):
        run = run_check("--list")
        expected = f"--user {os.getuid()}:{os.getgid()}"
        for line in (l for l in run.stdout.splitlines() if "docker run" in l):
            self.assertIn(expected, line)

    def test_docker_unusable_is_exit_two_and_points_to_no_docker(self):
        env = dict(os.environ, PATH=path_with_only("claude"))
        run = run_check(env=env)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("docker", run.stderr)
        self.assertIn("--no-docker", run.stderr)

    def test_no_docker_lists_the_matrix_as_skipped_on_purpose(self):
        run = run_check("--list", "--no-docker")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn("docker run", run.stdout)
        self.assertRegex(run.stdout, r"(?m)^matrix\b.*omitid")

    def test_an_unreadable_matrix_is_exit_two_and_names_the_workflow(self):
        with tempfile.TemporaryDirectory(prefix="venoxia-wf-") as tmp:
            bogus = Path(tmp) / "ci.yml"
            bogus.write_text("jobs:\n  tests:\n    steps: []\n", encoding="utf-8")
            env = dict(os.environ, VENOXIA_CHECK_WORKFLOW=str(bogus))
            run = run_check("--list", env=env)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("ci.yml", run.stderr)

    def test_a_skipped_step_does_not_count_as_failure(self):
        check = load_check_module()
        out = io.StringIO()
        steps = [
            check.Step("matrix", [], skipped="omitido a petición (--no-docker)"),
            check.Step("coverage", [[sys.executable, "-c", "pass"]]),
        ]
        self.assertEqual(check.run_steps(steps, out=out), 0)
        self.assertIn("omitido", out.getvalue())


class TestThePrePushHook(unittest.TestCase):
    """R-CI-021 · El hook vive en el repo, invoca la comprobación y propaga su código."""

    def test_the_hook_is_executable_and_invokes_the_local_check(self):
        self.assertTrue(HOOK.is_file(), f"falta {HOOK}")
        self.assertTrue(HOOK.stat().st_mode & stat.S_IXUSR, "el hook no es ejecutable")
        text = HOOK.read_text(encoding="utf-8")
        self.assertIn("tools/check.py", text)

    def test_the_hook_passes_no_options(self):
        text = HOOK.read_text(encoding="utf-8")
        self.assertNotIn("--no-docker", text)
        self.assertNotIn("--list", text)

    def _run_hook_with_a_fake_check_exiting(self, code: int) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory(prefix="venoxia-hook-") as tmp:
            root = Path(tmp)
            (root / ".githooks").mkdir()
            (root / "tools").mkdir()
            hook = root / ".githooks" / "pre-push"
            shutil.copy(HOOK, hook)
            hook.chmod(0o755)
            (root / "tools" / "check.py").write_text(
                f"import sys\nprint('comprobación falsa con código {code}')\nsys.exit({code})\n",
                encoding="utf-8",
            )
            # git ejecuta los hooks desde la raíz del árbol de trabajo, con la
            # ruta del hook como `$0`.
            return subprocess.run(
                [".githooks/pre-push", "origin", "git@example:repo.git"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
            )

    def test_the_hook_propagates_a_failed_check(self):
        run = self._run_hook_with_a_fake_check_exiting(1)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("comprobación falsa con código 1", run.stdout)

    def test_the_hook_propagates_a_check_that_could_not_run(self):
        run = self._run_hook_with_a_fake_check_exiting(2)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("comprobación falsa con código 2", run.stdout)

    def test_the_readme_says_how_to_enable_it(self):
        text = README.read_text(encoding="utf-8")
        match = re.search(r"## Verificar regresiones\n(.*?)\n## ", text, re.DOTALL)
        self.assertIsNotNone(match, "falta la sección «## Verificar regresiones»")
        section = match.group(1)
        self.assertIn("tools/check.py", section)
        self.assertIn("git config core.hooksPath .githooks", section)


if __name__ == "__main__":
    unittest.main()
