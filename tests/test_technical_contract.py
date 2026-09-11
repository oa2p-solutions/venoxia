#!/usr/bin/env python3
"""El contrato técnico del repositorio como suite: imports, red y códigos de salida.

Es el oráculo de la capability `technical-contract`: las decisiones técnicas
que antes vivían como prosa en `.venoxia/principles.md` —sólo biblioteca
estándar, ningún script toca la red ni consulta a un modelo, los cinco CLI
comparten los códigos `0`/`1`/`2`— escritas como tests que fallan si dejan de
ser verdad. El análisis de imports se hace con `ast` sobre el fuente, sin
importar nada: importar un módulo para saber qué importa ejecutaría justo lo
que se quiere prohibir.

`sys.stdlib_module_names` existe desde Python 3.10; la matriz del proyecto
empieza en 3.12.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_technical_contract -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_technical_contract.py -q

@covers R-TEC-001
@covers R-TEC-002
@covers R-TEC-005
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.venoxia_fixtures import REPO_ROOT

SCRIPTS_DIR = REPO_ROOT / "scripts"
TOOLS_DIR = REPO_ROOT / "tools"
TESTS_DIR = REPO_ROOT / "tests"

#: Módulos de la stdlib que abren conexiones. Un script que los importa puede
#: hablar con fuera, y el veredicto dejaría de depender sólo del árbol.
NETWORK_MODULES = ("urllib", "http", "socket", "ssl", "smtplib", "ftplib", "xmlrpc")

#: Clientes de modelo. Caen también bajo R-TEC-001 por no ser stdlib; se
#: nombran aparte porque son la premisa que se protege.
MODEL_CLIENTS = ("anthropic", "openai")

#: Los cinco CLI que comparten el contrato de códigos de salida.
CLIS = ("validate.py", "charter_lint.py", "diff_readings.py", "oracle.py", "gate.py")


def python_files(*directories: Path) -> list[Path]:
    """Todos los `.py` bajo los directorios dados, recursivamente y ordenados."""
    return sorted(path for directory in directories for path in directory.rglob("*.py"))


def imported_modules(source: str) -> set[str]:
    """Los módulos que un fuente importa, tal como los escribe («urllib.request»).

    Los imports relativos (`from .model import …`) no cuentan: nombran el
    propio paquete, no un módulo externo.
    """
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            modules.add(node.module)
    return modules


def top_level(module: str) -> str:
    return module.split(".", 1)[0]


def repository_modules() -> set[str]:
    """Los nombres importables que son del propio repositorio.

    `scripts/` y `tests/` van al `sys.path`, así que sus ficheros y paquetes
    se importan por su nombre (`validate`, `venoxia`, `venoxia_fixtures`); y
    `tests` es a su vez un paquete importable desde la raíz.
    """
    names = {"tests", "tools", "scripts"}
    for directory in (SCRIPTS_DIR, TOOLS_DIR, TESTS_DIR):
        for path in directory.iterdir():
            if path.suffix == ".py":
                names.add(path.stem)
            elif path.is_dir() and (path / "__init__.py").is_file():
                names.add(path.name)
    return names


def _label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def foreign_imports(path: Path, source: str, allowed: set[str]) -> list[tuple[str, str]]:
    """Los imports de `source` que no son stdlib ni están en `allowed`, como (fichero, módulo)."""
    return [
        (_label(path), module)
        for module in sorted(imported_modules(source))
        if top_level(module) not in sys.stdlib_module_names
        and top_level(module) not in allowed
    ]


def forbidden_imports(path: Path, source: str, forbidden: tuple[str, ...]) -> list[tuple[str, str]]:
    """Los imports de `source` cuyo módulo de primer nivel está en `forbidden`."""
    return [
        (_label(path), module)
        for module in sorted(imported_modules(source))
        if top_level(module) in forbidden
    ]


def dynamic_imports(path: Path, source: str) -> list[tuple[str, str]]:
    """Las llamadas a `importlib.import_module` o `__import__` de `source`, como (fichero, llamada).

    Un import dinámico no produce ningún nodo `Import`, así que un fuente que
    trajera su dependencia por esta vía esquivaría `foreign_imports` y el
    plugin reventaría igual en la máquina de quien no tenga el paquete.
    """
    found: list[tuple[str, str]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("__import__", "import_module"):
            found.append((_label(path), func.id))
        elif isinstance(func, ast.Attribute) and func.attr == "import_module":
            found.append((_label(path), "importlib.import_module"))
    return found


#: Formas de lanzar un proceso sin importar `subprocess`. Un script que las
#: usara podría hablar con fuera o con un modelo sin que el análisis de
#: imports lo viera.
OS_SPAWN_PREFIXES = ("system", "popen", "exec", "spawn", "posix_spawn")


def os_shell_calls(path: Path, source: str) -> list[tuple[str, str]]:
    """Las llamadas `os.system`, `os.popen`, `os.exec*`, `os.spawn*` y `os.posix_spawn*` de `source`."""
    found: list[tuple[str, str]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "os"
            and func.attr.startswith(OS_SPAWN_PREFIXES)
        ):
            found.append((_label(path), f"os.{func.attr}"))
    return found


def _scan(files: list[Path], scanner, *args) -> list[tuple[str, str]]:
    offenders: list[tuple[str, str]] = []
    for path in files:
        offenders.extend(scanner(path, path.read_text(encoding="utf-8"), *args))
    return offenders


class StandardLibraryOnlyTest(unittest.TestCase):
    """R-TEC-001 · scripts/, tools/ y tests/ importan sólo stdlib o módulos del repo."""

    def test_every_import_resolves_to_the_standard_library_or_to_the_repository(self):
        """@covers R-TEC-001"""
        files = python_files(SCRIPTS_DIR, TOOLS_DIR, TESTS_DIR)
        self.assertGreater(len(files), 10, "el escaneo no ha encontrado ficheros")
        offenders = _scan(files, foreign_imports, repository_modules())
        self.assertEqual([], offenders, f"imports ajenos a la stdlib y al repo: {offenders}")

    def test_a_third_party_import_is_named_by_the_test(self):
        """@covers R-TEC-001"""
        source = "import json\nimport requests\nfrom pathlib import Path\n"
        offenders = foreign_imports(Path("x/fake.py"), source, repository_modules())
        self.assertEqual([("x/fake.py", "requests")], offenders)

    def test_pytest_is_never_a_requirement(self):
        """@covers R-TEC-001"""
        offenders = _scan(python_files(TESTS_DIR), forbidden_imports, ("pytest",))
        self.assertEqual([], offenders, f"tests/ importa pytest: {offenders}")

    def test_a_dynamic_import_counts_as_an_import(self):
        """@covers R-TEC-001"""
        offenders = _scan(python_files(SCRIPTS_DIR, TOOLS_DIR), dynamic_imports)
        self.assertEqual([], offenders, f"imports dinámicos en scripts/ o tools/: {offenders}")

        source = "import importlib\nmod = importlib.import_module('requests')\nother = __import__('yaml')\n"
        flagged = dynamic_imports(Path("x/fake.py"), source)
        self.assertEqual(
            [("x/fake.py", "importlib.import_module"), ("x/fake.py", "__import__")], flagged
        )


class NoNetworkNoModelTest(unittest.TestCase):
    """R-TEC-002 · ningún script abre red ni llama a un modelo."""

    def test_no_network_module_in_any_script(self):
        """@covers R-TEC-002"""
        offenders = _scan(python_files(SCRIPTS_DIR), forbidden_imports, NETWORK_MODULES)
        self.assertEqual([], offenders, f"módulos de red en scripts/: {offenders}")

    def test_no_model_client_in_any_script(self):
        """@covers R-TEC-002"""
        offenders = _scan(python_files(SCRIPTS_DIR), forbidden_imports, MODEL_CLIENTS)
        self.assertEqual([], offenders, f"clientes de modelo en scripts/: {offenders}")

    def test_a_network_import_is_named_by_the_test(self):
        """@covers R-TEC-002"""
        source = "import json\nimport urllib.request\n"
        offenders = forbidden_imports(Path("x/fake.py"), source, NETWORK_MODULES)
        self.assertEqual([("x/fake.py", "urllib.request")], offenders)

    def test_only_the_oracle_and_the_gate_spawn_subprocesses(self):
        """@covers R-TEC-002"""
        offenders = _scan(python_files(SCRIPTS_DIR), forbidden_imports, ("subprocess",))
        spawning = sorted({path for path, _module in offenders})
        self.assertEqual(["scripts/gate.py", "scripts/oracle.py"], spawning)

    def test_no_script_shells_out_through_os(self):
        """@covers R-TEC-002"""
        offenders = _scan(python_files(SCRIPTS_DIR), os_shell_calls)
        self.assertEqual([], offenders, f"llamadas a os.* que lanzan procesos: {offenders}")

        source = "import os\nos.system('curl x')\nos.popen('claude')\nos.execv('/bin/sh', [])\nos._exit(0)\n"
        flagged = os_shell_calls(Path("x/fake.py"), source)
        self.assertEqual(
            [("x/fake.py", "os.system"), ("x/fake.py", "os.popen"), ("x/fake.py", "os.execv")],
            flagged,
        )


class SharedExitCodesTest(unittest.TestCase):
    """R-TEC-005 · los cinco CLI comparten 0 cumple / 1 no cumple / 2 sin veredicto."""

    def _run(self, script: str, *args: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
            env.pop("PYTHONPATH", None)
            return subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / script), *args],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

    def test_an_unknown_option_is_2_in_all_five(self):
        """@covers R-TEC-005"""
        for script in CLIS:
            with self.subTest(script=script):
                run = self._run(script, "--no-such-flag")
                self.assertEqual(run.returncode, 2, run.stderr)

    def test_a_root_that_does_not_exist_is_2_in_all_five(self):
        """@covers R-TEC-005"""
        missing = str(REPO_ROOT / "no-such-root-for-venoxia")
        invocations = {
            "validate.py": ("--root", missing),
            "charter_lint.py": ("--root", missing),
            "diff_readings.py": ("--readings", missing),
            "oracle.py": ("--root", missing, "--change", "x"),
            "gate.py": ("--root", missing),
        }
        for script in CLIS:
            with self.subTest(script=script):
                run = self._run(script, *invocations[script])
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertNotIn("Traceback", run.stderr)

    def test_in_the_gate_2_means_it_could_not_look(self):
        """@covers R-TEC-005"""
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / ".venoxia").mkdir()
            run = self._run("gate.py", "--root", root)
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
