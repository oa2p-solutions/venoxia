#!/usr/bin/env python3
"""La puerta portátil: `scripts/gate.py`, y que el plugin no traiga workflows.

Lo que un proyecto consumidor necesita de Venoxia son tres cosas —el acta, el
validador y el oráculo por cada change activo— y un veredicto único. Eso es un
comando, no un fichero de CI: un workflow obliga a declarar un runner, un
checkout y una forma de autenticarse, y esas tres decisiones son de quien lo
copia. `gate.py` no tiene ninguna de las tres, así que corre igual en
cualquier CI, en un hook local o a mano.

Este fichero comprueba su contrato de punta a punta sobre proyectos de
juguete, con la lógica que antes vivía en un heredoc de YAML —qué changes
están activos, cómo se normaliza su `state`, cuándo se falla— ejecutada de
verdad en vez de buscada como cadenas dentro de un fichero.

@covers R-CI-016
@covers R-CI-017
@covers R-CI-018

Cómo lanzarlo::

    python3 -m unittest tests.test_gate -v
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import (  # noqa: E402
    REPO_ROOT,
    SCRIPTS_DIR,
    CompletedRun,
    Project,
    requirement,
)

#: La clave que fija el runner, entre comillas o no y con o sin espacios antes
#: de los dos puntos: `runs-on : x` es YAML válido y esquiva la cadena literal.
RUNS_ON = re.compile(r"""["']?runs-on["']?\s*:""")

#: La otra mitad de un workflow: de dónde saca el código y con qué credencial.
SECRETS_EXPR = re.compile(r"\$\{\{[^}]*\bsecrets\.")

GATE_PY = SCRIPTS_DIR / "gate.py"
CHARTER_TEMPLATE = REPO_ROOT / "templates" / "charter.md"


def with_charter(project: Project) -> Project:
    """Le pone al proyecto un acta que pasa `charter_lint.py --strict`.

    `Project()` no monta ninguna: su andamio cubre capabilities y changes, no el
    acta. La puerta la exige —un `.venoxia/` sin acta deja una de las tres
    comprobaciones vacía—, así que la suite se la da.
    """
    project.write(".venoxia/charter.md", CHARTER_TEMPLATE.read_text(encoding="utf-8"))
    return project
README_PATH = REPO_ROOT / "README.md"
TEMPLATES_DIR = REPO_ROOT / "templates"


#: Lo que **tiene** que nombrar un runner: el CI de este repositorio, los tests
#: que comprueban su contenido y la capability que lo especifica. Y detrás, el
#: ruido del árbol de trabajo que nadie versiona: sin excluirlo, un fichero de
#: una dependencia instalada dejaría la suite en rojo para siempre.
WORKFLOW_SCAN_EXCLUDED = (
    ".forgejo/workflows",
    "tests",
    ".venoxia",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "htmlcov",
    "coverage",
    "TODO.md",
    "CLAUDE.md",
)


def repository_files() -> list[Path]:
    """Los ficheros del repositorio que sí pueden delatar un workflow."""
    excluidos = {REPO_ROOT / parte for parte in WORKFLOW_SCAN_EXCLUDED}
    salida = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(x == path or x in path.parents for x in excluidos):
            continue
        salida.append(path)
    return salida


def published_docs() -> list[Path]:
    """Lo que el plugin publica a quien lo instala.

    Acotar la prohibición a `README.md` la esquiva quien mueve el párrafo a una
    skill. El repositorio entero tampoco vale: el CI de verdad **tiene** que
    nombrar sus etiquetas de runner, o no arranca.
    """
    paths = [README_PATH, REPO_ROOT / "CONTRIBUTING.md"]
    paths += sorted((REPO_ROOT / "docs").rglob("*"))
    paths += sorted((REPO_ROOT / "skills").rglob("*"))
    paths += sorted((REPO_ROOT / "agents").rglob("*"))
    for extra in ("templates", "scripts", "hooks", ".claude-plugin"):
        paths += sorted((REPO_ROOT / extra).rglob("*"))
    return [path for path in paths if path.is_file()]

#: Lo que el README no puede nombrar: cómo se ejecutan el respaldo y las
#: pruebas internas de la organización no le sirve a quien instala el plugin, y
#: publicarlo es publicar infraestructura ajena al producto.
INTERNAL_TERMS = (
    "forgejo",
    "oa2p-debian",
    "oa2p-node",
    "oa2p-solutions.com",
    ":2222",
)


class GateCase(unittest.TestCase):
    """Base: un proyecto temporal que ya pasa la puerta, y el atajo para correrla."""

    def setUp(self) -> None:
        self.project = with_charter(Project())
        self.addCleanup(self.project.cleanup)

    def gate(self, *args: str) -> CompletedRun:
        return self.project.run(GATE_PY, "--root", str(self.project.root), *args)

    def change(self, change_id: str, state: str, *, raw_state: object = None) -> Path:
        """Escribe un `change.json` con el estado dado, crudo si hace falta."""
        data = {
            "id": change_id,
            "state": state if raw_state is None else raw_state,
            "via": "spec",
            "capabilities": [],
        }
        return self.project.write(
            f".venoxia/changes/{change_id}/change.json",
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        )


class GateVerdictTest(GateCase):
    """R-CI-016 · El veredicto y sus tres códigos de salida."""

    def test_a_clean_project_passes(self):
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())

    def test_a_specification_that_does_not_conform_fails(self):
        """Un requisito sin «verifies:» tumba la puerta: es el corazón del sistema."""
        self.project.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Capability: checkout\n\n## Purpose\n\nProbar.\n\n## Requirements\n\n"
            + requirement("R-CHK-001", omit=("verifies",)),
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_charter_that_does_not_conform_fails(self):
        """El acta entra en la puerta con su propio código de salida.

        Correr `charter_lint.py` y no mirar en qué termina es no correrlo: un
        proyecto con el acta rota pasaría igual.
        """
        self.project.write(".venoxia/charter.md", "# Acta\n\nNada de lo que pide C01.\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_project_without_venoxia_cannot_be_gated(self):
        """Excepción declarada a la convención del núcleo.

        Los otros scripts tratan «este proyecto no ha adoptado Venoxia» como un
        aviso y salen con 0: son herramientas que uno lanza sobre cualquier
        árbol. A la puerta se la invoca sobre un proyecto del que se afirma que
        cumple, así que un `.venoxia/` ausente es una comprobación que no se ha
        podido hacer, no un permiso. Con 0, un `--root` mal escrito daría verde
        sin correr ni el acta, ni el validador, ni un solo test.
        """
        empty = Project(scaffold=False)
        self.addCleanup(empty.cleanup)
        run = empty.run(GATE_PY, "--root", str(empty.root))
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertIn(str(empty.root), run.stdout + run.stderr, run.describe())

    def test_the_gate_runs_its_own_scripts_not_the_inspected_project_ones(self):
        """Resolverlos contra la raíz inspeccionada convertiría tres ficheros de
        tres líneas en un verde permanente, y además ejecutaría código del
        proyecto fuera del `test_command`, que es lo único que la advertencia
        cubre.
        """
        for nombre in ("charter_lint.py", "validate.py", "oracle.py"):
            self.project.write(f"scripts/{nombre}", "import sys\nsys.exit(0)\n")
        self.project.write(".venoxia/charter.md", "# Acta\n\nNada de lo que pide C01.\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_check_that_cannot_be_carried_out_does_not_pass(self):
        """La puerta es fail-closed, al revés que el guardián.

        Aquél es fail-open a propósito: un guardián que se cae no puede impedir
        trabajar. Ésta no puede aprobar lo que no ha llegado a comprobar, o su
        verde no significa nada.
        """
        charter = self.project.path(".venoxia/charter.md")
        charter.chmod(0o000)
        self.addCleanup(charter.chmod, 0o644)
        run = self.gate()
        self.assertEqual(run.returncode, 2, run.describe())

    def test_an_active_change_with_no_requirement_does_not_pass(self):
        """Sin requisitos no hay nada que validar ni nada que ejecutar.

        Aprobarlo por vacuidad da por verificado un change que no ha corrido
        una sola prueba, y ese agujero no es ninguna de las dos fronteras que
        el requisito declara indefendibles. Un `delta/notas.md` sin un solo
        requisito está tan vacío como no tener delta.
        """
        for state in ("validated", "verified"):
            for delta in (None, "# checkout Delta\n\nNotas sueltas, ni un requisito.\n"):
                with self.subTest(state=state, delta=bool(delta)):
                    project = with_charter(Project())
                    self.addCleanup(project.cleanup)
                    project.oracle_config(f'{sys.executable} -c "pass" {{files}}')
                    project.write(
                        ".venoxia/changes/vacio/change.json",
                        json.dumps({"id": "vacio", "state": state, "via": "spec"}) + "\n",
                    )
                    if delta:
                        project.write(".venoxia/changes/vacio/delta/notas.md", delta)
                    run = project.run(GATE_PY, "--root", str(project.root))
                    self.assertEqual(run.returncode, 1, run.describe())
                    self.assertIn("vacio", run.stdout + run.stderr, run.describe())

    def test_a_project_with_no_charter_cannot_be_gated(self):
        """El acta entra en la misma familia que el resto.

        Si sólo se reenviara el veredicto de `charter_lint.py`, un acta ausente
        dejaría una de las tres comprobaciones vacía y el verde resultante
        sería indistinguible de uno de verdad.
        """
        self.project.remove(".venoxia/charter.md")
        run = self.gate()
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertIn("charter.md", run.stderr, run.describe())

    def test_a_capability_spec_with_no_requirement_does_not_pass(self):
        """Vaciar un `spec.md` saca de la verificación todos los requisitos de
        esa capability sin mover el recuento. Para los changes esa misma
        asimetría ya está cerrada; ésta es su espejo."""
        self.project.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Capability: checkout\n\n## Purpose\n\nProbar.\n\n## Requirements\n\n",
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("checkout", run.stderr, run.describe())

    def test_a_capability_directory_without_a_spec_does_not_pass(self):
        """Si sólo se validara lo que se encuentra, borrar un `spec.md` sacaría
        de la puerta todos los requisitos de esa capability mientras que
        corromperlo la tumbaría."""
        self.project.write(".venoxia/capabilities/reservas/notas.md", "# Sin spec\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("reservas", run.stderr, run.describe())

    def test_a_change_directory_without_change_json_does_not_pass(self):
        """Si saltárselo fuera gratis, borrar el fichero saldría más barato que
        corromperlo — justo la asimetría que este requisito cierra."""
        self.project.write(".venoxia/changes/huerfano/proposal.md", "# Sin change.json\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("huerfano", run.stderr, run.describe())

    def test_the_three_checks_all_run_even_when_the_first_one_fails(self):
        """Descubrir un fallo por pasada obliga a reejecutar la suite cada vez."""
        self.project.write(".venoxia/charter.md", "# Acta\n\nNada de lo que pide C01.\n")
        self.project.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Capability: checkout\n\n## Purpose\n\nProbar.\n\n## Requirements\n\n"
            + requirement("R-CHK-001", omit=("verifies",)),
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("C01", run.stdout, "no se ve el fallo del acta")
        self.assertIn("V06", run.stdout, "no se ve el fallo del validador")

    def test_the_output_of_the_three_checks_reaches_the_caller(self):
        """Un `1` mudo bloquea la rama sin decir qué falló ni en qué requisito."""
        self.project.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Capability: checkout\n\n## Purpose\n\nProbar.\n\n## Requirements\n\n"
            + requirement("R-CHK-001", omit=("verifies",)),
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("V06", run.stdout, run.describe())

    def test_an_unknown_root_is_a_usage_error(self):
        run = self.project.run(GATE_PY, "--root", str(self.project.root / "no-existe"))
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertEqual(run.stdout.strip(), "", "un error de uso no escribe en stdout")


class GateActiveChangesTest(GateCase):
    """R-CI-016 · Qué changes entran en la puerta y qué pasa con los que no."""

    def test_a_project_with_no_active_change_passes(self):
        self.change("c-draft", "draft")
        self.change("c-spec", "specified")
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())

    def test_a_project_with_no_active_change_is_still_checked(self):
        """No tener changes activos no exime de las otras dos comprobaciones.

        Con el atajo «sin verified → salir 0», la puerta sería un no-op verde
        para la inmensa mayoría de los proyectos.
        """
        self.project.write(".venoxia/charter.md", "# Acta\n\nNada de lo que pide C01.\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_specified_change_whose_test_does_not_exist_yet_passes(self):
        """`specified` tiene V07/V08 en rojo por diseño: el test aún no existe.

        `validate.py` sin acotar mete todos los deltas, así que la puerta que
        lo invoque tal cual bloquea la rama principal en cuanto alguien empieza
        a especificar — el mismo bloqueo que se evita en «validated», un
        escalón más arriba.
        """
        self.change("c-spec", "specified")
        self.project.write(
            ".venoxia/changes/c-spec/delta/checkout.md",
            "# checkout Delta\n\n## ADDED Requirements\n\n"
            + requirement("R-CHK-901", verifies="tests/todavia_no_existe.py"),
        )
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())

    def test_a_validated_delta_is_validated(self):
        """El delta entra en el validador al llegar a «validated»: si no, un
        change puede pasar de «specified» a «validated» y la puerta nunca mira
        lo que declara."""
        self.change("c-val", "validated")
        self.project.write(
            ".venoxia/changes/c-val/delta/checkout.md",
            "# checkout Delta\n\n## ADDED Requirements\n\n"
            + requirement("R-CHK-001", omit=("verifies",)),
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_changes_in_other_states_are_left_alone(self):
        """Un change en «draft» o «specified» no entra en la puerta aunque su
        oráculo fuera a fallar: todavía no afirma nada que se pueda desmentir."""
        self.project.oracle_config(
            f'{sys.executable} -c "import sys; sys.exit(1)" {{files}}'
        )
        for state in ("draft", "specified"):
            with self.subTest(state=state):
                project = with_charter(Project())
                self.addCleanup(project.cleanup)
                project.oracle_config(
                    f'{sys.executable} -c "import sys; sys.exit(1)" {{files}}'
                )
                project.write(
                    ".venoxia/changes/c1/change.json",
                    json.dumps({"id": "c1", "state": state, "via": "spec"}) + "\n",
                )
                project.write(
                    ".venoxia/changes/c1/delta/checkout.md",
                    "# checkout Delta\n\n## ADDED Requirements\n\n"
                    + requirement("R-CHK-901", verifies="tests/oraculo.py"),
                )
                project.test_file("tests/oraculo.py", covers=("R-CHK-901",))
                run = project.run(GATE_PY, "--root", str(project.root))
                self.assertEqual(run.returncode, 0, run.describe())

    def test_an_unreadable_change_does_not_pass(self):
        """Corromper un change.json no puede ser la forma de esquivar la puerta."""
        self.project.write(".venoxia/changes/roto/change.json", "{ esto no es json")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("roto", run.stderr, run.describe())

    def test_a_change_without_state_does_not_pass(self):
        self.project.write(
            ".venoxia/changes/sin-estado/change.json",
            json.dumps({"id": "sin-estado", "via": "spec"}) + "\n",
        )
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("sin-estado", run.stderr, run.describe())

    def test_an_unknown_state_does_not_pass(self):
        """Corromper el valor del estado no puede salir más barato que borrarlo.

        Con una comparación contra la cadena «verified» a secas, un `state` de
        `"verifed"` o `"verified (pending)"` se lee como un estado más y su
        oráculo no se ejecuta nunca.
        """
        for raw in ("verifed", "verified (pending)", None, ["verified"], 7):
            with self.subTest(state=raw):
                project = with_charter(Project())
                self.addCleanup(project.cleanup)
                project.write(
                    ".venoxia/changes/raro/change.json",
                    json.dumps({"id": "raro", "state": raw, "via": "spec"}) + "\n",
                )
                run = project.run(GATE_PY, "--root", str(project.root))
                self.assertEqual(run.returncode, 1, run.describe())
                self.assertIn("raro", run.stderr, run.describe())

    def test_the_state_is_read_without_regard_to_case_or_spacing(self):
        """«Verified» y « verified » son el estado que nombran, no uno desconocido.

        Sin normalizar, cambiar una letra en un fichero de metadatos bastaría
        para que el change dejara de entrar en la puerta.
        """
        for raw in ("Verified", "  verified  "):
            with self.subTest(state=raw):
                project = with_charter(Project())
                self.addCleanup(project.cleanup)
                project.write(
                    ".venoxia/changes/c1/change.json",
                    json.dumps({"id": "c1", "state": raw, "via": "spec"}) + "\n",
                )
                run = project.run(GATE_PY, "--root", str(project.root))
                # Entra en la puerta: sin venoxia.json eso es un error de uso,
                # que es precisamente la prueba de que no se ignoró.
                self.assertEqual(run.returncode, 2, run.describe())

    def test_an_unusable_oracle_config_is_a_usage_error(self):
        """Si sólo se detectara la ausencia, corromperlo saldría más barato que
        borrarlo: la puerta correría el oráculo con un comando vacío, no
        obtendría ningún rojo y daría verde informando de N oráculos mirados.

        Es la asimetría que ya se cierra para `change.json` y `spec.md`,
        invertida: ahí se detecta lo corrupto, aquí sólo lo ausente.
        """
        casos = {
            "ausente": None,
            "ilegible": "{ esto no es json",
            "sin test_command": '{"version": 1, "cwd": "."}',
            "test_command vacío": '{"version": 1, "test_command": "  ", "cwd": "."}',
        }
        for nombre, contenido in casos.items():
            with self.subTest(config=nombre):
                project = with_charter(Project())
                self.addCleanup(project.cleanup)
                project.write(
                    ".venoxia/changes/c1/change.json",
                    json.dumps({"id": "c1", "state": "verified", "via": "spec"}) + "\n",
                )
                project.write(
                    ".venoxia/changes/c1/delta/checkout.md",
                    "# checkout Delta\n\n## ADDED Requirements\n\n"
                    + requirement("R-CHK-901", verifies="tests/oraculo.py"),
                )
                project.test_file("tests/oraculo.py", covers=("R-CHK-901",))
                if contenido is not None:
                    project.write(".venoxia/venoxia.json", contenido)
                run = project.run(GATE_PY, "--root", str(project.root))
                self.assertEqual(run.returncode, 2, run.describe())
                self.assertIn("venoxia.json", run.stderr, run.describe())


class GateOracleTest(GateCase):
    """R-CI-016 · El oráculo se ejecuta de verdad, sin grabar, y sólo gatea «verified»."""

    def with_change(self, state: str, *, exit_code: int) -> None:
        """Un change en `state` con un requisito cuyo oráculo termina como se pida."""
        self.project.oracle_config(
            f'{sys.executable} -c "import sys; sys.exit({exit_code})" {{files}}'
        )
        self.change("c1", state)
        self.project.write(
            ".venoxia/changes/c1/delta/checkout.md",
            "# checkout Delta\n\n## ADDED Requirements\n\n"
            + requirement("R-CHK-901", verifies="tests/oraculo.py"),
        )
        self.project.test_file("tests/oraculo.py", covers=("R-CHK-901",))
        if state == "verified":
            self.project.oracle_record(
                "c1", [{"R-CHK-901": "red"}, {"R-CHK-901": "green"}]
            )

    def test_a_verified_change_with_a_red_oracle_does_not_pass(self):
        """Un «verified» en rojo es una mentira en el disco: ahí la puerta cierra."""
        self.with_change("verified", exit_code=1)
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_green_oracle_passes(self):
        self.with_change("verified", exit_code=0)
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())

    def test_a_validated_change_with_a_red_oracle_does_not_close_the_gate(self):
        """Un change en «validated» está rojo por diseño: el test existe y el
        código todavía no. Hacerlo gatear bloquearía la rama principal durante
        el flujo normal de Venoxia, que es justo lo que la puerta protege."""
        self.with_change("validated", exit_code=1)
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())

    def test_every_verified_change_oracle_runs(self):
        """Descubrir un change rojo por pasada reejecuta la suite de todos los
        anteriores cada vez."""
        self.project.oracle_config(
            f'{sys.executable} -c "import sys; sys.exit(1)" {{files}}'
        )
        for change_id, req in (("c1", "R-CHK-901"), ("c2", "R-CHK-902")):
            self.change(change_id, "verified")
            self.project.write(
                f".venoxia/changes/{change_id}/delta/checkout.md",
                "# checkout Delta\n\n## ADDED Requirements\n\n"
                + requirement(req, verifies=f"tests/oraculo_{change_id}.py"),
            )
            self.project.test_file(f"tests/oraculo_{change_id}.py", covers=(req,))
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        salida = run.stdout + run.stderr
        for change_id in ("c1", "c2"):
            self.assertIn(change_id, salida, f"no se ve «{change_id}» en la salida")

    def test_the_gate_names_the_validated_changes_it_did_not_run(self):
        """Quien nunca promueve a «verified» deja sus requisitos en tierra de
        nadie: el guardián ya abrió la puerta al código en «validated», el test
        existe y está en rojo, y no llegan a ninguna capability.

        La puerta no puede distinguir «todavía no lo he escrito» de «no pienso
        promoverlo» —son el mismo estado en el disco—, pero sí dejar de
        callarlo.
        """
        self.change("c-parado", "validated")
        self.project.write(
            ".venoxia/changes/c-parado/delta/checkout.md",
            "# checkout Delta\n\n## ADDED Requirements\n\n"
            + requirement("R-CHK-901", verifies="tests/oraculo.py"),
        )
        self.project.test_file("tests/oraculo.py", covers=("R-CHK-901",))
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("c-parado", run.stdout, run.describe())

    def test_a_mature_project_reports_zero_oracles(self):
        """`archived` es el estado final normal, así que un proyecto maduro no
        tiene ningún change activo y la puerta no ejecuta ninguna prueba.

        Es el resultado correcto —los requisitos archivados viven en la
        capability, donde V06/V07/V08 siguen exigiendo su test, y los ejecuta la
        suite del propio proyecto—, pero tiene que verse.
        """
        self.change("c-viejo", "archived")
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertRegex(run.stdout, r"0 or[áa]culos", run.describe())

    def test_a_failing_gate_says_how_much_it_looked_at_too(self):
        """Exigirlo sólo en la pasada verde es exigirlo en la única que nadie lee."""
        self.project.write(".venoxia/charter.md", "# Acta\n\nNada de lo que pide C01.\n")
        run = self.gate()
        self.assertEqual(run.returncode, 1, run.describe())
        for palabra in ("acta", "spec.md", "change", "oráculo"):
            self.assertIn(palabra, run.stdout.lower(), f"el resumen no dice «{palabra}»")

    def test_the_summary_comes_last_after_every_subprocess(self):
        """El resumen se escribe cuando los tres han terminado, así que es lo
        último de la salida.

        El ataque que motivó este escenario suponía que el `test_command` del
        proyecto hereda stdout y podría imprimir un resumen falsificado. No lo
        hereda: `oracle.py` captura su salida y sólo guarda un `output_tail` en
        el historial. La propiedad se mantiene igualmente, y es la que hace
        legible el log: quien lo lea mira el último bloque.
        """
        self.with_change("verified", exit_code=0)
        self.project.oracle_record("c1", [{"R-CHK-901": "red"}, {"R-CHK-901": "green"}])
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())
        lineas = [linea for linea in run.stdout.splitlines() if linea.strip()]
        self.assertTrue(lineas, run.describe())
        self.assertTrue(
            lineas[-1].startswith("venoxia-gate:"),
            f"el resumen no es lo último de la salida: {lineas[-1]!r}",
        )

    def test_the_gate_says_how_much_it_looked_at(self):
        """Un verde sobre un checkout a medias no puede confundirse con uno de
        verdad: la puerta lee el árbol, así que no ve lo que se quitó de él."""
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())
        for palabra in ("acta", "spec.md", "change", "oráculo"):
            self.assertIn(palabra, run.stdout.lower(), f"el resumen no dice «{palabra}»")

    def test_the_gate_writes_no_evidence(self):
        """`--record` inyectaría runs en el historial que V17 y /venoxia:verify
        creen para decidir si un change está verificado. La puerta lee esa
        evidencia; fabricarla la convierte en juez y parte."""
        self.with_change("verified", exit_code=0)
        self.project.oracle_record("c1", [{"R-CHK-901": "red"}, {"R-CHK-901": "green"}])
        antes = self.project.path(".venoxia/changes/c1/oracle.json").read_bytes()
        run = self.gate()
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(
            self.project.path(".venoxia/changes/c1/oracle.json").read_bytes(),
            antes,
            "la puerta ha escrito en oracle.json: invoca el oráculo con --record",
        )

    def test_the_gate_never_passes_record(self):
        source = GATE_PY.read_text(encoding="utf-8")
        self.assertNotIn(
            "--record",
            source,
            "gate.py invoca el oráculo con --record: fabricaría la evidencia que audita",
        )

    def test_the_oracle_runs_for_real(self):
        """`--dry-run` sólo lista comandos y siempre sale en verde: sería una
        puerta que aprueba cualquier cosa."""
        source = GATE_PY.read_text(encoding="utf-8")
        self.assertNotIn(
            "--dry-run",
            source,
            "gate.py invoca el oráculo con --dry-run: no ejecutaría ningún test",
        )


class NoWorkflowTemplateTest(unittest.TestCase):
    """R-CI-017 · El plugin no trae plantillas de workflow."""

    def test_the_ci_template_directory_is_gone(self):
        self.assertFalse(
            (TEMPLATES_DIR / "ci").exists(),
            "«templates/ci/» sigue existiendo: una plantilla de workflow obliga "
            "a declarar un runner, un checkout y una autenticación que son de "
            "quien la copia, no de Venoxia",
        )

    def test_no_workflow_file_under_templates(self):
        if not TEMPLATES_DIR.is_dir():
            return
        strays = sorted(
            path.relative_to(REPO_ROOT).as_posix()
            for path in TEMPLATES_DIR.rglob("*")
            if path.is_file() and path.suffix in (".yml", ".yaml")
        )
        self.assertEqual(strays, [], f"quedan workflows bajo «templates/»: {strays}")


    def test_no_file_under_templates_pins_a_runner(self):
        """Renombrar la plantilla a `.md` o a `.yml.example` no la salva: lo que
        no puede viajar en el plugin es la decisión de qué runner usar."""
        if not TEMPLATES_DIR.is_dir():
            return
        culprits = sorted(
            path.relative_to(REPO_ROOT).as_posix()
            for path in TEMPLATES_DIR.rglob("*")
            if path.is_file()
            and RUNS_ON.search(path.read_text(encoding="utf-8", errors="replace"))
        )
        self.assertEqual(culprits, [], f"plantillas que fijan un runner: {culprits}")


    def test_no_checkout_or_secret_of_a_workflow_ships_in_the_repository(self):
        """Un workflow obliga a decidir runner, checkout y autenticación.

        Prohibir sólo el runner deja publicar la mitad peligrosa —la que hace
        que la puerta ejecute el `test_command` del autor de un pull request
        con las credenciales del runner— a quien se limite a omitir la línea
        `runs-on:` que la otra regla le empuja a quitar.
        """
        culprits = []
        for path in repository_files():
            texto = path.read_text(encoding="utf-8", errors="replace")
            for aguja in ("actions/checkout", SECRETS_EXPR):
                if isinstance(aguja, str):
                    encontrado = aguja in texto
                else:
                    encontrado = bool(aguja.search(texto))
                if encontrado:
                    culprits.append(path.relative_to(REPO_ROOT).as_posix())
                    break
        self.assertEqual(culprits, [], f"mitad peligrosa de un workflow publicada: {culprits}")

    def test_no_workflow_pinned_to_a_runner_ships_in_the_repository(self):
        """Lo que el requisito prohíbe es **publicar** una plantilla de workflow.

        Por eso el barrido es el conjunto publicado y no el árbol entero: las
        tres cosas que tienen que nombrar el runner —el CI de este repositorio,
        los tests que comprueban su contenido y la capability que lo
        especifica— no se instalan como documentación de producto, y recorrer
        todo metería `.git/`, entornos virtuales y `node_modules`, donde un
        fichero ajeno con la clave dejaría la suite en rojo para siempre.
        """
        culprits = sorted(
            path.relative_to(REPO_ROOT).as_posix()
            for path in repository_files()
            if RUNS_ON.search(path.read_text(encoding="utf-8", errors="replace"))
        )
        self.assertEqual(culprits, [], f"workflows publicados con el plugin: {culprits}")


class PublishedDocsTest(unittest.TestCase):
    """R-CI-018 · Lo publicado documenta la puerta, no la infraestructura interna."""

    def setUp(self) -> None:
        self.readme = README_PATH.read_text(encoding="utf-8")

    def test_the_readme_names_the_gate_command(self):
        self.assertIn("scripts/gate.py", self.readme)

    def test_the_readme_explains_the_exit_codes(self):
        """Sin los códigos, quien lo mete en su CI no sabe qué mira su CI."""
        section = re.search(
            r"^## Verificar un proyecto\s*$(.*?)(?=^## |\Z)",
            self.readme,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(section, "falta la sección «## Verificar un proyecto»")
        body = section.group(1)
        for code in ("`0`", "`1`", "`2`"):
            self.assertIn(code, body, f"la sección no explica el código de salida {code}")
        self.assertRegex(
            body,
            r"(?i)bloquea|no ha podido comprobar|no pudo comprobar",
            "la sección no dice que un «2» bloquea igual que un «1»: leerlo como "
            "«error mío de invocación» deja pasar el --root mal escrito y el "
            "checkout a medias que el diseño fail-closed existe para detener",
        )

    def test_the_gate_warns_about_it_in_its_own_help(self):
        """Quien pega el comando en un job disparado por pull requests de un
        fork lee el `--help`, no el README."""
        salida = subprocess.run(
            [sys.executable, str(GATE_PY), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
        self.assertIn("test_command", salida, "el --help no dice qué ejecuta la puerta")
        self.assertRegex(
            salida,
            r"(?i)secreto",
            "el --help no advierte de correr la puerta con secretos en el entorno",
        )

    def test_the_readme_warns_that_the_gate_runs_the_project_tests(self):
        """Al dejar de ser un workflow, la puerta ya no trae «persist-credentials:
        false» ni un paso sin secretos: quien la meta en su CI sobre código de un
        fork ejecuta comandos del autor del pull request con las credenciales del
        runner, y sólo puede evitarlo si el README se lo dice."""
        section = re.search(
            r"^## Verificar un proyecto\s*$(.*?)(?=^## |\Z)",
            self.readme,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(section, "falta la sección «## Verificar un proyecto»")
        body = section.group(1)
        self.assertIn("test_command", body, "la sección no dice qué ejecuta la puerta")
        self.assertRegex(
            body,
            r"(?i)secreto",
            "la sección no advierte de correr la puerta con secretos en el entorno",
        )

    def test_the_readme_says_what_the_gate_does_not_run(self):
        """«Verificar un proyecto» no puede entenderse por más de lo que la
        puerta hace: el oráculo cubre los changes en «verified», y lo archivado
        lo ejecuta la suite del propio proyecto."""
        section = re.search(
            r"^## Verificar un proyecto\s*$(.*?)(?=^## |\Z)",
            self.readme,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(section, "falta la sección «## Verificar un proyecto»")
        body = section.group(1)
        self.assertIn("verified", body, "la sección no dice qué changes cubre el oráculo")
        self.assertRegex(
            body,
            r"(?i)archivad|capabilit",
            "la sección no dice quién ejecuta los requisitos ya archivados",
        )

    def test_the_published_docs_do_not_describe_the_internal_ci(self):
        for path in published_docs():
            lowered = path.read_text(encoding="utf-8", errors="replace").lower()
            for term in INTERNAL_TERMS:
                with self.subTest(path=path.name, term=term):
                    self.assertNotIn(
                        term,
                        lowered,
                        f"«{path.relative_to(REPO_ROOT)}» nombra «{term}»: cómo se "
                        "ejecutan el respaldo y las pruebas internas de la "
                        "organización no le sirve a quien instala el plugin",
                    )

    def test_the_published_docs_do_not_describe_a_backup_mirror(self):
        for path in published_docs():
            with self.subTest(path=path.name):
                self.assertNotRegex(
                    path.read_text(encoding="utf-8", errors="replace"),
                    r"(?i)repositorio de respaldo|espejo de respaldo|respaldo interno"
            r"|copia de seguridad",
                    f"«{path.relative_to(REPO_ROOT)}» describe el espejo de respaldo interno",
                )


if __name__ == "__main__":
    unittest.main()
