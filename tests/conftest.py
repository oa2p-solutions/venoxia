#!/usr/bin/env python3
"""Arranque de la suite de tests de Venoxia.

Su único trabajo es que estos dos imports funcionen desde cualquier fichero de
`tests/`, tanto si la suite la lanza `pytest` como si la lanza `unittest`::

    from venoxia import model, parser, report
    import validate

Para eso mete `<repo>/scripts` al principio de `sys.path` —y de paso `tests/`,
para que los ficheros de test se encuentren entre ellos—, de forma idempotente:
si ya están, no los duplica.

`pytest` importa este fichero solo, antes que ningún test. `unittest`, en
cambio, **no sabe nada de `conftest.py`**: por eso `tests/venoxia_fixtures.py`
repite el mismo ajuste en su propio import. Los dos ajustes son idempotentes,
así que ejecutarlos los dos no hace daño.

Cómo importar el andamio desde un fichero de test
-------------------------------------------------
El import que funciona con **las tres** formas de lanzar la suite es el
cualificado::

    from tests.venoxia_fixtures import Project, requirement, future_date

    python3 -m pytest tests/ -q            # el del contrato
    python3 -m unittest discover -s tests -v
    python3 -m unittest tests.test_lo_que_sea -v

El import corto `from venoxia_fixtures import …` también funciona con `pytest`
y con `unittest discover`, pero **no** con `python3 -m unittest tests.test_x`,
porque ahí `tests/` no entra en `sys.path` antes de importar el módulo de test.
Si dudas, usa el cualificado.

Aquí no hay fixtures de `pytest`: este proyecto es de cero dependencias y la
suite se escribe con `unittest.TestCase` de la stdlib. El equivalente al
fixture `project` del contrato §9 es la clase `Project` del andamio::

    import unittest

    from tests.venoxia_fixtures import Project


    class TestAlgo(unittest.TestCase):
        def test_algo(self):
            \"\"\"El proyecto limpio cumple el contrato en modo estricto.\"\"\"
            with Project() as project:
                run = project.validate_json("--strict")
                self.assertEqual(run.returncode, 0, run.describe())
"""

from __future__ import annotations

import sys
from pathlib import Path

#: Directorio de esta suite.
TESTS_DIR = Path(__file__).resolve().parent

#: Raíz del repositorio: el directorio que contiene `scripts/` y `tests/`.
REPO_ROOT = TESTS_DIR.parent

#: Directorio de los scripts de producción, el que hay que poner en `sys.path`.
SCRIPTS_DIR = REPO_ROOT / "scripts"


def ensure_import_paths() -> None:
    """Pone `<repo>/scripts` y `<repo>/tests` al principio de `sys.path`.

    Idempotente a propósito: se llama al importar este módulo y también al
    importar `venoxia_fixtures`, y llamarla dos veces no duplica las entradas.
    """
    for directory in (TESTS_DIR, SCRIPTS_DIR):
        entry = str(directory)
        if entry not in sys.path:
            sys.path.insert(0, entry)


ensure_import_paths()
