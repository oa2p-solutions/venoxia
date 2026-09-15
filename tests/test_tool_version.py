"""R-TEC-007 · cada informe dice qué Venoxia lo produjo.

Los tres scripts con informe —`validate.py`, `charter_lint.py` y
`diff_readings.py`— escriben en su JSON la clave `tool` con la versión del
manifiesto `.claude-plugin/plugin.json` que acompaña a los scripts, y la nombran
en el informe de texto. Es lo que permite demostrar, desde lo que una skill
escribe en disco, que corrió la versión instalada y no una copia antigua.

@covers R-TEC-007
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import (  # noqa: E402
    CHARTER_LINT_PY,
    DIFF_READINGS_PY,
    REPO_ROOT,
    VALIDATE_PY,
    Project,
    default_readings,
)

MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"


def manifest_version() -> str:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]


class ToolVersionTest(unittest.TestCase):
    """@covers R-TEC-007"""

    def setUp(self) -> None:
        self.project = Project()
        self.addCleanup(self.project.cleanup)
        self.project.readings("d", default_readings())

    def runs(self, json_flag: bool):
        flag = ("--json",) if json_flag else ()
        return {
            "validate.py": self.project.run(VALIDATE_PY, "--root", str(self.project.root), "--no-color", *flag),
            "charter_lint.py": self.project.run(
                CHARTER_LINT_PY, "--root", str(self.project.root), "--no-color", *flag
            ),
            "diff_readings.py": self.project.diff("d", "--no-color", *flag),
        }

    def test_the_three_json_reports_name_the_version(self):
        """@covers R-TEC-007"""
        version = manifest_version()
        for script, run in self.runs(True).items():
            with self.subTest(script=script):
                tool = run.json.get("tool")
                self.assertIsNotNone(tool, run.describe())
                self.assertEqual(tool["name"], "venoxia", run.describe())
                self.assertEqual(tool["version"], version, run.describe())
                self.assertEqual(tool["script"], script, run.describe())

    def test_the_text_report_names_the_version(self):
        """@covers R-TEC-007"""
        version = manifest_version()
        for script, run in self.runs(False).items():
            with self.subTest(script=script):
                self.assertIn(f"Venoxia {version}", run.stdout, run.describe())

    def test_a_missing_manifest_does_not_break_the_report(self):
        """@covers R-TEC-007"""
        with tempfile.TemporaryDirectory() as tmp:
            scripts = Path(tmp) / "scripts"
            shutil.copytree(REPO_ROOT / "scripts", scripts, ignore=shutil.ignore_patterns("__pycache__"))
            readings = self.project.readings_dir("d")
            completed = subprocess.run(
                [sys.executable, str(scripts / "diff_readings.py"), "--readings", str(readings), "--json", "--no-color"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotIn("Traceback", completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["tool"]["version"], "unknown", completed.stdout[:500])
            self.assertEqual(completed.returncode, payload["exit_code"], completed.stdout[:500])
            baseline = self.project.diff("d", "--json", "--no-color").json
            self.assertEqual(payload["verdict"], baseline["verdict"])


if __name__ == "__main__":
    unittest.main()
