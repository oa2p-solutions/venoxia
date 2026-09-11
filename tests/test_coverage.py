#!/usr/bin/env python3
"""El umbral de cobertura como contrato: `tools/coverage.py` no se baja el listón solo.

`tools/coverage.py` es el runner con nombre «coverage» de `R-TEC-004` y el
oráculo lo ejecuta entero, sin `{files}`: su código de salida es el veredicto.
Lo que aquí se prueba es la aritmética del umbral que ese run aplica, sin
lanzar la suite bajo `trace` (del orden de dos minutos): un fichero que
aparece sin entrada en `tools/coverage-threshold.json` se exige al suelo del
núcleo, `85`, y no a su propia medida menos dos —que es como un script nuevo
sin un solo test pasaría con un 0 %—.

El módulo se carga por ruta porque `tools/` no está en `sys.path` y no es un
paquete: es el mismo camino que usa `tests/test_check.py` con `tools/check.py`.

@covers R-TEC-004
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from tests.venoxia_fixtures import REPO_ROOT

COVERAGE_PY = REPO_ROOT / "tools" / "coverage.py"


def load_coverage_module():
    spec = importlib.util.spec_from_file_location("venoxia_tools_coverage", COVERAGE_PY)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ThresholdForNewFilesTest(unittest.TestCase):
    """R-TEC-004 · un fichero sin entrada en el fichero de umbrales se exige al suelo del núcleo."""

    @classmethod
    def setUpClass(cls):
        cls.coverage = load_coverage_module()

    def test_a_new_file_with_no_tests_is_held_to_the_core_floor(self):
        """@covers R-TEC-004"""
        threshold = self.coverage.threshold_for_new_file("scripts/nuevo.py", 0.0)
        self.assertEqual(threshold, self.coverage.CORE_FLOOR)
        self.assertEqual(self.coverage.CORE_FLOOR, 85)

    def test_a_new_file_well_covered_keeps_the_measured_minus_two_rule(self):
        """@covers R-TEC-004"""
        threshold = self.coverage.threshold_for_new_file("scripts/nuevo.py", 96.4)
        self.assertEqual(threshold, 94)

    def test_a_new_file_without_any_data_is_held_to_the_core_floor(self):
        """@covers R-TEC-004"""
        threshold = self.coverage.threshold_for_new_file("scripts/nuevo.py", None)
        self.assertEqual(threshold, self.coverage.CORE_FLOOR)

    def test_the_init_rule_for_core_scripts_is_unchanged(self):
        """@covers R-TEC-004"""
        core = sorted(self.coverage.CORE_SCRIPTS)[0]
        self.assertEqual(self.coverage.compute_threshold(core, 10.0), self.coverage.CORE_FLOOR)
        self.assertEqual(self.coverage.compute_threshold(core, 97.5), 95)

    def test_a_file_below_its_threshold_turns_the_table_red(self):
        """@covers R-TEC-004"""
        FileCoverage = self.coverage.FileCoverage
        coverage = {
            "scripts/a.py": FileCoverage("scripts/a.py", 100, 90, Path("a.cover")),
            "scripts/b.py": FileCoverage("scripts/b.py", 100, 70, Path("b.cover")),
        }
        table, ok = self.coverage.render_table(coverage, {"scripts/a.py": 85, "scripts/b.py": 85})
        self.assertFalse(ok)
        self.assertIn("scripts/b.py", table)
        self.assertIn("FALLA", table)

    def test_every_file_at_or_above_its_threshold_turns_the_table_green(self):
        """@covers R-TEC-004"""
        FileCoverage = self.coverage.FileCoverage
        coverage = {"scripts/a.py": FileCoverage("scripts/a.py", 100, 90, Path("a.cover"))}
        table, ok = self.coverage.render_table(coverage, {"scripts/a.py": 85})
        self.assertTrue(ok)
        self.assertIn("90.0", table)
        self.assertIn("85", table)


if __name__ == "__main__":
    unittest.main()
