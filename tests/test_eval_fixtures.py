#!/usr/bin/env python3
"""Los cinco fixtures de evals no se mueven cuando cambia una regla.

`evals/README.md` («Cifras que los graders dan por buenas») es parte del
contrato de la batería: sus graders son expresiones regulares sobre el JSON
exacto que `validate.py` y `diff_readings.py` producen para cada fixture. Este
fichero convierte esa tabla en un test: si una regla nueva mueve una sola
cifra, la suite se pone roja aquí, en vez de dejar que lo note primero un
`claude plugin eval` que cuesta tokens. Si el número tiene que cambiar de
verdad, se cambia aquí **a conciencia**, a la vez que la fila de
`evals/README.md`, nunca por separado.

Corre los scripts por subproceso, contra los fixtures reales de `evals/`
—no un `Project()` de andamio—, porque lo que hay que proteger es justo el
comportamiento sobre esos ficheros concretos.

Se ejecuta con cualquiera de las tres formas::

    python3 -m unittest tests.test_eval_fixtures -v
    python3 -m unittest discover -s tests -v
    python3 -m pytest tests/test_eval_fixtures.py -q
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.venoxia_fixtures import DIFF_READINGS_PY, REPO_ROOT, VALIDATE_PY

EVALS_DIR = REPO_ROOT / "evals"
RUN_TIMEOUT = 30

# Las cifras de `validate.py --json --no-color`, calcadas de la columna
# homónima de `evals/README.md` § «Cifras que los graders dan por buenas».
VALIDATE_CIFRAS = {
    "clean-spec": {"ok": True, "error": 0, "warning": 0, "requirements": 4, "low": 0},
    "missing-oracle": {"ok": False, "error": 1, "warning": 0, "requirements": 3, "low": 0},
    "budget-exceeded": {"ok": False, "error": 1, "warning": 0, "requirements": 5, "low": 2},
    "ambiguous-status-code": {"ok": True, "error": 0, "warning": 0, "requirements": 3, "low": 0},
    "ambiguous-partial-effect": {"ok": True, "error": 0, "warning": 0, "requirements": 3, "low": 0},
}

# Las cifras de `diff_readings.py --json`. Sólo los tres fixtures con
# `readings/` las tienen: `missing-oracle` y `budget-exceeded` no comparan
# lecturas porque el validador ya rechaza la spec antes de llegar ahí.
DIFF_READINGS_CIFRAS = {
    "clean-spec": {"converged": True, "hard": 0, "soft": 0, "gaps": 0},
    "ambiguous-status-code": {"converged": False, "hard": 1, "soft": 0, "gaps": 0},
    "ambiguous-partial-effect": {"converged": False, "hard": 1, "soft": 1, "gaps": 0},
}


def _run_json(script: Path, *args: str) -> dict:
    """Ejecuta un script de `scripts/` por subproceso y parsea su stdout como JSON."""
    argv = [sys.executable, str(script), *args]
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=RUN_TIMEOUT,
    )
    try:
        return json.loads(completed.stdout)
    except ValueError as error:
        raise AssertionError(
            f"stdout no es JSON ({error}).\n"
            f"  comando   : {' '.join(argv)}\n"
            f"  returncode: {completed.returncode}\n"
            f"  stdout    : {completed.stdout[:800]}\n"
            f"  stderr    : {completed.stderr[:800]}"
        ) from None


def _readings_dir(case: str) -> Path:
    """El único `readings/` del fixture, o falla nombrando lo que encontró."""
    project = EVALS_DIR / case / "project"
    candidates = sorted((project / ".venoxia" / "changes").glob("*/readings"))
    if len(candidates) != 1:
        raise AssertionError(
            f"«{case}» debería tener exactamente un directorio «readings/»; "
            f"encontrados: {candidates}"
        )
    return candidates[0]


class EvalFixturesValidateTest(unittest.TestCase):
    """`validate.py --json --no-color` sobre cada `evals/<caso>/project`."""

    def test_each_case_matches_its_documented_figures(self):
        for case, expected in VALIDATE_CIFRAS.items():
            with self.subTest(case=case):
                payload = _run_json(
                    VALIDATE_PY,
                    "--root",
                    str(EVALS_DIR / case / "project"),
                    "--json",
                    "--no-color",
                )
                self.assertEqual(payload.get("ok"), expected["ok"], payload)
                self.assertEqual(
                    payload.get("counts", {}).get("error"), expected["error"], payload
                )
                self.assertEqual(
                    payload.get("counts", {}).get("warning"), expected["warning"], payload
                )
                self.assertEqual(
                    payload.get("counts", {}).get("requirements"),
                    expected["requirements"],
                    payload,
                )
                self.assertEqual(payload.get("budget", {}).get("low"), expected["low"], payload)

    def test_clean_spec_also_passes_in_strict_mode(self):
        """`clean-spec` es el caso que más importa: mide el falso positivo."""
        payload = _run_json(
            VALIDATE_PY,
            "--root",
            str(EVALS_DIR / "clean-spec" / "project"),
            "--json",
            "--no-color",
            "--strict",
        )
        self.assertTrue(payload.get("ok"), payload)
        self.assertEqual(payload.get("findings"), [], payload)


class EvalFixturesDiffReadingsTest(unittest.TestCase):
    """`diff_readings.py --json` sobre los tres fixtures que traen `readings/`."""

    def test_each_case_matches_its_documented_figures(self):
        for case, expected in DIFF_READINGS_CIFRAS.items():
            with self.subTest(case=case):
                payload = _run_json(
                    DIFF_READINGS_PY,
                    "--readings",
                    str(_readings_dir(case)),
                    "--json",
                )
                self.assertEqual(payload.get("converged"), expected["converged"], payload)
                self.assertEqual(
                    payload.get("counts", {}).get("hard"), expected["hard"], payload
                )
                self.assertEqual(
                    payload.get("counts", {}).get("soft"), expected["soft"], payload
                )
                self.assertEqual(
                    payload.get("counts", {}).get("gaps"), expected["gaps"], payload
                )


if __name__ == "__main__":
    unittest.main()
