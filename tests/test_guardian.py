#!/usr/bin/env python3
"""Tests del guardián de Venoxia (`scripts/guardian.py`) contra §6 del contrato.

Todo se invoca **por subproceso, con el payload JSON por la entrada estándar**,
que es exactamente como lo llama Claude Code. Nada de importar el módulo y
llamar a sus funciones: si el guardián sólo funcionase importado, no funcionaría.

Lo que defiende esta suite, por orden de importancia:

1. **Por stdout sale siempre exactamente una decisión válida.** Un hook
   `PreToolUse` que no escribe nada no ha decidido nada y la edición sigue
   adelante: un `deny` que no se imprime es una escritura consentida. Se
   comprueba con la salida en bytes y con el entorno en contra
   (`PYTHONIOENCODING=ascii`, `latin-1`, `LC_ALL=C`) y con una ruta que ni
   siquiera es Unicode legal.
2. **Fail-open absoluto ante los fallos del guardián.** Diez entradas
   hostiles —stdin vacío, JSON roto, un `drift/` sin permiso de escritura— y
   ninguna puede devolver `deny` ni un código de salida distinto de 0. Un
   guardián que rompe el flujo por un fallo propio se desinstala el primer día.
   El `change.json` corrupto **no** está en esa lista: es un fichero del
   usuario que está mal, no un fallo nuestro, y tiene su propia clase.
3. **El mensaje de `deny` es el producto.** Tiene que nombrar el fichero,
   ofrecer `/venoxia:specify` y `/venoxia:validate`, y decir cómo saltárselo.
   Denegar sin decir qué teclear es peor que no denegar.
4. Los cinco caminos de decisión, su precedencia y el diario de deriva.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import unittest
from datetime import datetime
from pathlib import Path

from tests.venoxia_fixtures import GUARDIAN_PY, REPO_ROOT, Project

#: El manifiesto del hook que Claude Code lee para instalar el guardián.
HOOKS_JSON = REPO_ROOT / "hooks" / "hooks.json"

#: Ruta de código corriente: no es especificación, así que es la que hace decidir.
CODE_PATH = "src/checkout.ts"

#: El diario de deriva, relativo a la raíz del proyecto.
DRIFT_LOG = ".venoxia/drift/direct.log"

#: Un delta con contenido: lo que acredita que la spec de un cambio existe.
DELTA_MARKDOWN = "## ADDED Requirements\n\n### R-CHK-014 · Algo que el sistema hará\n"

#: Presupuesto de latencia que afirma el test. El objetivo de diseño es 100 ms
#: (contrato §6); aquí se afloja a 500 ms para que el arranque del intérprete en
#: una máquina cargada no vuelva inestable la suite.
LATENCY_BUDGET_SECONDS = 0.5


class GuardianTestCase(unittest.TestCase):
    """Base común: proyectos temporales que se limpian solos y dos asertos."""

    def make_project(self, **kwargs) -> Project:
        """Devuelve un `Project` en un temporal, ya registrado para su limpieza."""
        project = Project(**kwargs)
        self.addCleanup(project.cleanup)
        return project

    def assert_allow(self, run, context: str = "") -> None:
        """Afirma que el guardián permitió la edición y salió con 0."""
        self.assertEqual(0, run.returncode, f"{context}\n{run.describe()}")
        self.assertEqual("allow", run.decision, f"{context}\n{run.describe()}")

    def assert_deny(self, run, context: str = "") -> None:
        """Afirma que el guardián denegó la edición y aun así salió con 0."""
        self.assertEqual(0, run.returncode, f"{context}\n{run.describe()}")
        self.assertEqual("deny", run.decision, f"{context}\n{run.describe()}")

    def drift_lines(self, project: Project) -> list[str]:
        """Las líneas no vacías del diario de deriva del proyecto."""
        return [line for line in project.read(DRIFT_LOG).splitlines() if line.strip()]

    def give_delta(self, project: Project, change_id: str, content: str = DELTA_MARKDOWN) -> Path:
        """Escribe un delta no vacío al cambio: la prueba de que su spec existe.

        Desde la segunda ronda, el paso 3 sólo se cree un «state»: «validated»
        si el cambio trae además su «delta/*.md» con contenido. Los tests que
        quieran probar **otra** cosa con un cambio validado tienen que dárselo.
        """
        return project.write(f".venoxia/changes/{change_id}/delta/checkout.md", content)


# ---------------------------------------------------------------------------
# Los cinco caminos de decisión (§6)
# ---------------------------------------------------------------------------


class GuardianDecisionPathsTest(GuardianTestCase):
    """Los cinco pasos del orden de decisión, uno por test."""

    def test_step1_allows_when_the_project_has_no_venoxia_directory(self):
        """Paso 1: sin «.venoxia/» el proyecto no ha adoptado Venoxia y todo pasa."""
        project = self.make_project(scaffold=False)
        self.assertFalse(project.exists(".venoxia"), "el proyecto no debía estar adoptado")

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)

    def test_step2_allows_every_specification_path(self):
        """Paso 2: «.venoxia/», «prfaq/» y el markdown de spec siempre se pueden escribir."""
        project = self.make_project()
        spec_paths = (
            ".venoxia/capabilities/checkout/spec.md",
            ".venoxia/changes/c1/delta/checkout.md",
            "prfaq/checkout-express.md",
            "docs/specs/x.md",
            "spec.md",
            "proposal.md",
        )
        for relative in spec_paths:
            with self.subTest(path=relative):
                run = project.guardian(file_path=relative)
                self.assert_allow(run, f"«{relative}» es especificación y debía permitirse")

    def test_step3_allows_when_the_active_change_is_validated(self):
        """Paso 3: un cambio activo en «state»: «validated» respalda la edición de código."""
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        # El andamio ya trae el «delta/checkout.md» del cambio, que es lo que
        # acredita el «validated»; se afirma aquí para que la dependencia sea
        # visible y no un accidente del fixture.
        self.assertTrue(project.exists(".venoxia/changes/c1/delta/checkout.md"))

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)
        self.assertIn("validated", run.reason)

    def test_step4_allows_when_the_active_change_declares_via_direct(self):
        """Paso 4: «via»: «direct» es la salida de emergencia y permite la edición."""
        project = self.make_project()
        project.change("c1", state="draft", via="direct")

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)
        self.assertIn("direct", run.reason)

    def test_step5_denies_when_nothing_backs_the_edit(self):
        """Paso 5: sin cambio validado ni «via»: «direct», editar código se deniega."""
        project = self.make_project()
        project.change("c1", state="draft", via="spec")

        run = project.guardian(file_path=CODE_PATH)

        self.assert_deny(run)


# ---------------------------------------------------------------------------
# El anclaje de las rutas de especificación (paso 2)
# ---------------------------------------------------------------------------


class GuardianSpecPathAnchoringTest(GuardianTestCase):
    """El paso 2 no puede convertirse en un rodeo al guardián.

    El contrato (§6, paso 2, y §8) escribe «.venoxia/», «prfaq/», «docs/spec*» y
    «specs/» **ancladas a la raíz del proyecto**. Reconocerlas a cualquier
    profundidad haría que un simple «mkdir src/prfaq/» dejara fuera del alcance
    del guardián todo lo que se metiera dentro: el producto entero anulado por
    un directorio con el nombre adecuado.

    El proyecto de estos tests trae el andamio por defecto, cuyo cambio activo
    está en «state»: «draft» y «via»: «spec»: cualquier ruta que **no** sea
    especificación se deniega, así que un «allow» aquí sólo puede venir del
    paso 2.
    """

    def setUp(self) -> None:
        self.project = self.make_project()

    def test_code_under_a_nested_spec_directory_is_denied(self):
        """Un «prfaq/» o un «.venoxia/» que no cuelgan de la raíz no eximen de nada."""
        bypass_paths = (
            "src/prfaq/checkout.ts",
            "src/.venoxia/checkout.ts",
            "a/b/prfaq/checkout.ts",
            "a/b/.venoxia/changes/c1/change.json",
            "src/prfaq/nested/deep/todavia-codigo.py",
            "src/prfaq/notas.md",
        )
        for relative in bypass_paths:
            with self.subTest(path=relative):
                run = self.project.guardian(file_path=relative)
                self.assert_deny(
                    run,
                    f"«{relative}» no está en la raíz: no puede pasar por especificación",
                )

    def test_nested_specs_and_docs_directories_do_not_launder_markdown(self):
        """«specs/» y «docs/spec*» sólo valen en la raíz: anidados, el markdown se deniega."""
        bypass_paths = (
            "lib/specs/x.md",
            "src/vendor/specs/notas.md",
            "src/docs/specs/x.md",
            "a/b/docs/spec/x.md",
        )
        for relative in bypass_paths:
            with self.subTest(path=relative):
                run = self.project.guardian(file_path=relative)
                self.assert_deny(
                    run,
                    f"«{relative}» no cuelga de la raíz: no puede pasar por especificación",
                )

    def test_root_anchored_specification_paths_are_still_allowed(self):
        """El anclaje no cierra ningún camino legítimo: la raíz sigue siendo escribible."""
        spec_paths = (
            ".venoxia/principles.md",
            ".venoxia/capabilities/checkout/spec.md",
            ".venoxia/changes/c1/change.json",
            "prfaq/checkout-express.md",
            "prfaq/borradores/idea.md",
            "docs/specs/x.md",
            "docs/spec/checkout.md",
            "docs/specs/checkout/detalle.md",
            "specs/x.md",
        )
        for relative in spec_paths:
            with self.subTest(path=relative):
                run = self.project.guardian(file_path=relative)
                self.assert_allow(run, f"«{relative}» es especificación y debía permitirse")

    def test_spec_filenames_travel_anywhere_but_only_as_markdown(self):
        """«spec.md», «proposal.md» y «delta*.md» valen a cualquier profundidad; sus homónimos en código, no."""
        for relative in ("src/checkout/spec.md", "src/proposal.md", "a/b/delta-checkout.md"):
            with self.subTest(path=relative, expected="allow"):
                self.assert_allow(
                    self.project.guardian(file_path=relative),
                    f"«{relative}» es markdown de spec y debía permitirse",
                )
        for relative in ("src/spec.ts", "src/proposal.py", "src/delta.js", "src/spec/x.ts"):
            with self.subTest(path=relative, expected="deny"):
                self.assert_deny(
                    self.project.guardian(file_path=relative),
                    f"«{relative}» es código, por mucho que se llame como una spec",
                )

    def test_paths_outside_the_project_still_fail_open(self):
        """El anclaje no toca el fail-open: lo raro o lo de fuera se sigue permitiendo."""
        for relative in ("../../etc/passwd", "../prfaq/x.ts", "/etc/hosts"):
            with self.subTest(path=relative):
                run = self.project.guardian(file_path=relative)
                self.assert_allow(run, f"«{relative}» queda fuera del proyecto: fail-open")


# ---------------------------------------------------------------------------
# El diario de deriva (paso 4)
# ---------------------------------------------------------------------------


class GuardianDriftLogTest(GuardianTestCase):
    """Lo que el paso 4 deja escrito en «.venoxia/drift/direct.log»."""

    def setUp(self) -> None:
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="direct")

    def test_direct_edit_writes_one_line_to_the_drift_log(self):
        """Una edición «direct» crea el diario con exactamente una línea."""
        self.assert_allow(self.project.guardian(file_path=CODE_PATH))

        self.assertTrue(
            self.project.exists(DRIFT_LOG),
            f"el guardián debía crear «{DRIFT_LOG}»",
        )
        self.assertEqual(1, len(self.drift_lines(self.project)))

    def test_drift_log_line_is_valid_json_with_the_four_contract_fields(self):
        """La línea del diario es JSON válido y trae «ts», «change», «tool» y «path»."""
        self.assert_allow(self.project.guardian(tool_name="Write", file_path=CODE_PATH))

        line = self.drift_lines(self.project)[0]
        entry = json.loads(line)

        self.assertEqual({"ts", "change", "tool", "path"}, set(entry))
        self.assertEqual("c1", entry["change"])
        self.assertEqual("Write", entry["tool"])
        self.assertEqual(CODE_PATH, entry["path"])

    def test_drift_log_timestamp_is_iso8601_in_utc(self):
        """El «ts» del diario es un ISO 8601 en UTC, parseable y con zona horaria."""
        self.assert_allow(self.project.guardian(file_path=CODE_PATH))

        stamp = json.loads(self.drift_lines(self.project)[0])["ts"]
        self.assertTrue(stamp.endswith("Z"), f"«{stamp}» debía terminar en «Z» (UTC)")
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        self.assertIsNotNone(moment.tzinfo, f"«{stamp}» debía llevar zona horaria")
        self.assertEqual(0, moment.utcoffset().total_seconds())

    def test_drift_log_accumulates_one_line_per_direct_edit(self):
        """El diario es un JSONL que se acumula: dos ediciones, dos líneas distintas."""
        self.assert_allow(self.project.guardian(tool_name="Write", file_path=CODE_PATH))
        self.assert_allow(self.project.guardian(tool_name="Edit", file_path="src/otro.ts"))

        entries = [json.loads(line) for line in self.drift_lines(self.project)]

        self.assertEqual(2, len(entries), "el segundo apunte pisó al primero")
        self.assertEqual(["Write", "Edit"], [entry["tool"] for entry in entries])
        self.assertEqual([CODE_PATH, "src/otro.ts"], [entry["path"] for entry in entries])


# ---------------------------------------------------------------------------
# El mensaje de denegación: el producto
# ---------------------------------------------------------------------------


class GuardianDenyMessageTest(GuardianTestCase):
    """El texto del «deny». Un guardián que deniega sin decir qué teclear se desinstala."""

    def setUp(self) -> None:
        project = self.make_project()
        project.change("c1", state="draft", via="spec")
        self.run_result = project.guardian(file_path=CODE_PATH)
        self.assert_deny(self.run_result)
        self.reason = self.run_result.reason

    def test_deny_reason_names_the_file_that_was_blocked(self):
        """La razón nombra el fichero concreto que se intentó editar."""
        self.assertIn(CODE_PATH, self.reason)

    def test_deny_reason_offers_the_specify_and_validate_commands(self):
        """La razón trae los dos comandos exactos que desbloquean la edición."""
        for command in ("/venoxia:specify", "/venoxia:validate"):
            with self.subTest(command=command):
                self.assertIn(command, self.reason)

    def test_deny_reason_offers_the_direct_escape_hatch(self):
        """La razón explica la salida de emergencia: «via»: «direct» en el change.json."""
        self.assertIn("via", self.reason)
        self.assertIn("direct", self.reason)

    def test_deny_output_repeats_the_reason_in_system_message(self):
        """Al denegar se añade «systemMessage» con el mismo texto que la razón."""
        payload = self.run_result.json
        self.assertIn("systemMessage", payload)
        self.assertEqual(self.reason, payload["systemMessage"])


# ---------------------------------------------------------------------------
# Forma de la salida
# ---------------------------------------------------------------------------


class GuardianOutputShapeTest(GuardianTestCase):
    """El sobre JSON que Claude Code espera de un hook «PreToolUse»."""

    def test_output_is_a_pretooluse_hook_specific_output(self):
        """La salida es «hookSpecificOutput» con el evento y una decisión válida."""
        project = self.make_project()
        project.change("c1", state="validated", via="spec")

        payload = project.guardian(file_path=CODE_PATH).json

        self.assertIn("hookSpecificOutput", payload)
        block = payload["hookSpecificOutput"]
        self.assertEqual("PreToolUse", block.get("hookEventName"))
        self.assertIn(block.get("permissionDecision"), {"allow", "deny"})
        self.assertTrue(block.get("permissionDecisionReason", "").strip())

    def test_allow_output_carries_no_system_message(self):
        """«systemMessage» es exclusivo del «deny»: al permitir no aparece."""
        project = self.make_project()
        project.change("c1", state="validated", via="spec")

        payload = project.guardian(file_path=CODE_PATH).json

        self.assertNotIn("systemMessage", payload)

    def test_notebook_edit_takes_its_path_from_notebook_path(self):
        """Con «NotebookEdit» la ruta llega en «notebook_path» y el guardián la usa."""
        project = self.make_project()
        project.change("c1", state="draft", via="spec")

        run = project.guardian(tool_name="NotebookEdit", file_path="src/analysis.ipynb")

        self.assert_deny(run, "la ruta de «notebook_path» debía llegar a la decisión")
        self.assertIn("src/analysis.ipynb", run.reason)


# ---------------------------------------------------------------------------
# Precedencia entre pasos y elección del cambio activo
# ---------------------------------------------------------------------------


class GuardianPrecedenceTest(GuardianTestCase):
    """Quién gana cuando dos condiciones se cumplen a la vez."""

    def test_validated_beats_direct_and_records_no_drift(self):
        """Con «validated» y «direct» juntos gana el paso 3: no se anota deriva."""
        project = self.make_project()
        project.change("c1", state="validated", via="direct")

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)
        self.assertIn("validated", run.reason)
        self.assertFalse(
            project.exists(DRIFT_LOG),
            "el paso 3 no debe anotar deriva: la edición sí tenía spec validada",
        )

    def test_most_recent_change_wins_when_it_is_validated(self):
        """Con varios changes manda el de «mtime» más reciente: si está validado, permite."""
        project = self.make_project()
        old = project.change("older", state="draft", via="spec")
        new = project.change("newer", state="validated", via="spec")
        self.give_delta(project, "newer")
        self.assertLess(
            old.stat().st_mtime,
            new.stat().st_mtime,
            "el andamio debía dejar «newer» estrictamente más reciente",
        )

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)
        self.assertIn("newer", run.reason)

    def test_most_recent_change_wins_when_it_is_not_validated(self):
        """El mismo criterio en negativo: un «validated» más viejo no salva la edición."""
        project = self.make_project()
        old = project.change("older", state="validated", via="spec")
        new = project.change("newer", state="draft", via="spec")
        self.assertLess(
            old.stat().st_mtime,
            new.stat().st_mtime,
            "el andamio debía dejar «newer» estrictamente más reciente",
        )

        run = project.guardian(file_path=CODE_PATH)

        self.assert_deny(run)
        self.assertIn("newer", run.reason)


# ---------------------------------------------------------------------------
# Fail-open: donde se juega la confianza
# ---------------------------------------------------------------------------


class GuardianFailOpenTest(GuardianTestCase):
    """Entradas hostiles. Ninguna puede denegar ni salir con un código distinto de 0.

    Aquí sólo entran los **fallos del guardián**: lo que no supo leer, lo que no
    supo escribir, lo que no venía en el payload. Un `change.json` corrupto no
    es un fallo del guardián sino un fichero del usuario que está mal, y
    confundir las dos cosas era media puerta trasera: bastaba dejar el
    `change.json` ilegible para que todo pasara. Ese caso vive ahora en
    `GuardianCorruptChangeTest`, y deniega.
    """

    # -- Constructores de cada caso hostil -----------------------------------

    def case_empty_stdin(self):
        """Entrada estándar vacía."""
        return self.make_project().guardian(raw_stdin="")

    def case_stdin_is_not_json(self):
        """Entrada estándar con texto que no es JSON."""
        return self.make_project().guardian(raw_stdin="esto no es JSON ni lo pretende")

    def case_truncated_json(self):
        """JSON cortado a la mitad."""
        return self.make_project().guardian(raw_stdin='{"cwd": "/tmp", "tool_input": {')

    def case_json_is_an_array(self):
        """El payload es un array en vez de un objeto."""
        return self.make_project().guardian(raw_stdin='[1, 2, 3]')

    def case_missing_tool_input(self):
        """Payload sin la clave «tool_input»."""
        project = self.make_project()
        payload = {
            "hook_event_name": "PreToolUse",
            "cwd": str(project.root),
            "tool_name": "Write",
        }
        return project.guardian(raw_stdin=json.dumps(payload))

    def case_tool_input_without_file_path(self):
        """«tool_input» sin ninguna clave de ruta."""
        return self.make_project().guardian(tool_input={"content": "hola"})

    def case_empty_file_path(self):
        """«file_path» presente pero vacío."""
        return self.make_project().guardian(tool_input={"file_path": ""})

    def case_nonexistent_cwd(self):
        """El «cwd» del payload apunta a un directorio que no existe."""
        project = self.make_project()
        return project.guardian(cwd=str(project.path("no-existe-este-directorio")))

    def case_unwritable_drift_directory(self):
        """El «drift/» existe sin permiso de escritura y el apunte no se puede hacer."""
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("como root, «chmod 000» no impide escribir")
        project = self.make_project()
        project.change("c1", state="draft", via="direct")
        drift = project.path(".venoxia/drift")
        drift.mkdir(parents=True, exist_ok=True)
        os.chmod(drift, 0o000)
        try:
            return project.guardian(file_path=CODE_PATH)
        finally:
            os.chmod(drift, 0o755)

    def case_path_escaping_the_project(self):
        """Una ruta con «..» que se sale del proyecto."""
        return self.make_project().guardian(file_path="../../etc/passwd")

    HOSTILE_CASES = (
        "case_empty_stdin",
        "case_stdin_is_not_json",
        "case_truncated_json",
        "case_json_is_an_array",
        "case_missing_tool_input",
        "case_tool_input_without_file_path",
        "case_empty_file_path",
        "case_nonexistent_cwd",
        "case_unwritable_drift_directory",
        "case_path_escaping_the_project",
    )

    def test_every_hostile_input_allows_and_exits_zero(self):
        """Ninguna entrada hostil puede denegar ni salir con un código distinto de 0."""
        for name in self.HOSTILE_CASES:
            builder = getattr(self, name)
            with self.subTest(case=name, what=builder.__doc__):
                run = builder()
                self.assertEqual(
                    0, run.returncode, f"{name} salió con código != 0\n{run.describe()}"
                )
                self.assertEqual(
                    "allow", run.decision, f"{name} no permitió\n{run.describe()}"
                )

    def test_hostile_input_still_emits_exactly_one_decision(self):
        """Aun fallando, el guardián escribe una sola decisión bien formada en stdout."""
        run = self.make_project().guardian(raw_stdin="{{{ roto")

        payload = run.json  # falla con AssertionError si stdout no es un JSON único
        self.assertEqual(
            "PreToolUse", payload["hookSpecificOutput"]["hookEventName"]
        )
        self.assertEqual("allow", payload["hookSpecificOutput"]["permissionDecision"])


# ---------------------------------------------------------------------------
# Presupuesto de latencia
# ---------------------------------------------------------------------------


class GuardianLatencyTest(GuardianTestCase):
    """El guardián corre en cada edición: lo que tarda es parte del contrato."""

    def test_one_invocation_stays_within_the_latency_budget(self):
        """Una invocación completa tarda menos de 500 ms (objetivo de diseño: 100 ms)."""
        project = self.make_project()
        project.change("c1", state="draft", via="spec")
        project.guardian(file_path=CODE_PATH)  # calentamiento: caché del intérprete

        start = time.perf_counter()
        run = project.guardian(file_path=CODE_PATH)
        elapsed = time.perf_counter() - start

        self.assert_deny(run)
        self.assertLess(
            elapsed,
            LATENCY_BUDGET_SECONDS,
            f"la invocación tardó {elapsed * 1000:.0f} ms; el objetivo de diseño son 100 ms "
            f"y el techo de este test {LATENCY_BUDGET_SECONDS * 1000:.0f} ms",
        )

    def test_the_validated_path_with_its_delta_check_stays_within_the_budget(self):
        """El camino más caro —el que además mira el «delta/»— también cabe."""
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        project.guardian(file_path=CODE_PATH)  # calentamiento

        start = time.perf_counter()
        run = project.guardian(file_path=CODE_PATH)
        elapsed = time.perf_counter() - start

        self.assert_allow(run)
        self.assertLess(
            elapsed,
            LATENCY_BUDGET_SECONDS,
            f"la invocación tardó {elapsed * 1000:.0f} ms; el objetivo de diseño son 100 ms",
        )

    def test_checking_the_delta_costs_microseconds_not_milliseconds(self):
        """El precio del arreglo del paso 3, medido: un «scandir» y un «stat»."""
        project = self.make_project()
        delta_dir = project.path(".venoxia/changes/c1/delta")
        iterations = 200

        start = time.perf_counter()
        for _ in range(iterations):
            with os.scandir(delta_dir) as entries:
                for entry in entries:
                    if entry.name.endswith(".md") and entry.is_file():
                        entry.stat()
                        break
        per_decision = (time.perf_counter() - start) / iterations

        self.assertLess(
            per_decision,
            0.002,
            f"comprobar el delta cuesta {per_decision * 1000:.3f} ms por decisión; "
            "el presupuesto entero del guardián son 100 ms",
        )

    def test_guardian_imports_no_venoxia_module_and_never_runs_the_validator(self):
        """El presupuesto de latencia como test: ni módulos de Venoxia ni subprocesos."""
        source = Path(GUARDIAN_PY).read_text(encoding="utf-8")
        imported: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)

        for forbidden in ("venoxia", "validate", "subprocess", "runpy", "importlib"):
            with self.subTest(module=forbidden):
                offenders = [
                    name
                    for name in imported
                    if name == forbidden or name.startswith(f"{forbidden}.")
                ]
                self.assertEqual([], offenders, f"guardian.py importa «{forbidden}»")

        self.assertNotIn("validate.py", source, "guardian.py no debe ejecutar el validador")


# ---------------------------------------------------------------------------
# La emisión: por stdout sale siempre exactamente una decisión válida
# ---------------------------------------------------------------------------


def guardian_bytes(
    project: Project,
    payload: dict | None = None,
    env_overrides: dict[str, str | None] | None = None,
) -> subprocess.CompletedProcess:
    """Invoca el guardián en un subproceso **sin decodificar su salida**.

    El atajo `project.guardian(...)` fija `PYTHONIOENCODING=utf-8` y devuelve
    texto ya decodificado, que es justo lo que aquí hay que poder torcer: estos
    tests miran los **bytes** que salen y con el entorno en contra. Un valor
    `None` en `env_overrides` borra esa variable del entorno del hijo.
    """
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["HOME"] = str(project.home)
    env.pop("PYTHONPATH", None)
    for name, value in (env_overrides or {}).items():
        if value is None:
            env.pop(name, None)
        else:
            env[name] = value
    body = {
        "hook_event_name": "PreToolUse",
        "cwd": str(project.root),
        "tool_name": "Write",
        "tool_input": {"file_path": CODE_PATH},
    }
    if payload:
        body.update(payload)
    # `ensure_ascii=True` para que el propio payload viaje en ASCII: así el
    # caso del surrogate suelto llega intacto sea cual sea la codificación.
    return subprocess.run(
        [sys.executable, str(GUARDIAN_PY)],
        input=json.dumps(body, ensure_ascii=True).encode("ascii"),
        capture_output=True,
        cwd=str(project.root),
        env=env,
        timeout=30,
    )


class _NameInliner(ast.NodeTransformer):
    """Sustituye los nombres ya conocidos por su valor, para poder evaluar el resto."""

    def __init__(self, namespace: dict) -> None:
        self.namespace = namespace

    def visit_Name(self, node: ast.Name):  # noqa: N802 — nombre impuesto por ast
        if node.id in self.namespace:
            return ast.copy_location(ast.Constant(self.namespace[node.id]), node)
        return node


def source_constant(name: str):
    """Evalúa una constante literal de `guardian.py` leyendo su fuente.

    Sin importar el módulo: la suite invoca al guardián por subproceso, y esto
    es análisis estático del fichero, como el test que vigila sus imports. Las
    asignaciones que no son literales (f-strings, `frozenset(...)`, llamadas) se
    saltan; las que se apoyan en otra constante ya vista, se resuelven.
    """
    tree = ast.parse(Path(GUARDIAN_PY).read_text(encoding="utf-8"))
    namespace: dict = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = ast.literal_eval(_NameInliner(namespace).visit(node.value))
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                namespace[target.id] = value
    if name not in namespace:
        raise AssertionError(f"guardian.py no define «{name}» como constante literal")
    return namespace[name]


class GuardianEmissionTest(GuardianTestCase):
    """Lo peor que le puede pasar al plugin: denegar y que no salga nada.

    Un hook `PreToolUse` que escribe cero bytes y sale con 0 no ha decidido
    nada, así que la edición sigue adelante. Antes bastaba con que la salida
    estándar no fuese UTF-8 —o con que la ruta editada llevase un surrogate
    suelto— para que el `deny` se evaporase sin dejar más rastro que un
    `stderr` que nadie lee: un `deny` convertido en escritura efectiva.
    """

    #: Entornos en los que el envoltorio de texto de stdout **no** es UTF-8.
    HOSTILE_ENVIRONMENTS = (
        {"PYTHONIOENCODING": "ascii"},
        {"PYTHONIOENCODING": "latin-1"},
        {"PYTHONIOENCODING": "ascii:strict"},
        {"PYTHONIOENCODING": None, "PYTHONUTF8": "0", "LC_ALL": "C", "LANG": "C"},
    )

    def setUp(self) -> None:
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="spec")

    def assert_one_valid_decision(self, completed, expected: str, context: str) -> dict:
        """El stdout es exactamente un JSON, en ASCII, con la decisión esperada."""
        detail = (
            f"{context}\n"
            f"returncode: {completed.returncode}\n"
            f"stdout ({len(completed.stdout)} bytes): {completed.stdout[:400]!r}\n"
            f"stderr: {completed.stderr[:400]!r}"
        )
        self.assertEqual(0, completed.returncode, detail)
        self.assertTrue(completed.stdout, f"el guardián no escribió nada.\n{detail}")
        self.assertTrue(
            completed.stdout.isascii(),
            f"la decisión debía salir en ASCII puro.\n{detail}",
        )
        # Que sea ASCII implica que también es UTF-8 válido: cualquier cliente
        # la puede parsear, tenga la codificación que tenga.
        text = completed.stdout.decode("utf-8")
        self.assertEqual(1, len([line for line in text.splitlines() if line.strip()]), detail)
        payload = json.loads(text)
        block = payload["hookSpecificOutput"]
        self.assertEqual("PreToolUse", block["hookEventName"], detail)
        self.assertEqual(expected, block["permissionDecision"], detail)
        self.assertTrue(block["permissionDecisionReason"].strip(), detail)
        return payload

    def test_a_non_utf8_stdout_still_carries_the_deny(self):
        """Con stdout en ascii o latin-1 el «deny» sale igual, y parseable."""
        for overrides in self.HOSTILE_ENVIRONMENTS:
            with self.subTest(env=overrides):
                completed = guardian_bytes(self.project, env_overrides=overrides)
                payload = self.assert_one_valid_decision(
                    completed, "deny", f"entorno {overrides}"
                )
                reason = payload["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn(CODE_PATH, reason)
                self.assertIn("/venoxia:specify", reason)

    def test_a_non_utf8_stdout_still_carries_the_allow(self):
        """El mismo entorno hostil tampoco puede tragarse un «allow»."""
        self.project.change("c2", state="validated", via="spec")
        self.give_delta(self.project, "c2")
        for overrides in self.HOSTILE_ENVIRONMENTS:
            with self.subTest(env=overrides):
                completed = guardian_bytes(self.project, env_overrides=overrides)
                self.assert_one_valid_decision(completed, "allow", f"entorno {overrides}")

    def test_an_accented_payload_is_read_whatever_the_environment_says(self):
        """El payload viene en UTF-8 y se lee como UTF-8, diga lo que diga el entorno.

        Leerlo por el envoltorio de texto lo hacía depender de la codificación
        del entorno: con `PYTHONIOENCODING=ascii`, un solo acento en la ruta
        —«src/año/checkout.ts»— tumbaba la lectura, el guardián caía en su
        fail-open y el `deny` se convertía en `allow`. La decisión se invertía
        sola, en silencio, en cualquier terminal con `LC_ALL=C`.
        """
        payload = json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.project.root),
                "tool_name": "Write",
                "tool_input": {"file_path": "src/año/checkout.ts"},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        for overrides in self.HOSTILE_ENVIRONMENTS:
            with self.subTest(env=overrides):
                env = {**os.environ, "HOME": str(self.project.home)}
                for name, value in overrides.items():
                    env.pop(name, None) if value is None else env.update({name: value})
                completed = subprocess.run(
                    [sys.executable, str(GUARDIAN_PY)],
                    input=payload,
                    capture_output=True,
                    cwd=str(self.project.root),
                    env=env,
                    timeout=30,
                )
                decision = self.assert_one_valid_decision(
                    completed, "deny", f"entorno {overrides}"
                )
                self.assertIn(
                    "src/año/checkout.ts",
                    decision["hookSpecificOutput"]["permissionDecisionReason"],
                )

    def test_a_file_path_that_is_not_legal_unicode_still_denies(self):
        """Un surrogate suelto en «file_path» no puede tumbar la emisión.

        Node sustituye el surrogate por U+FFFD y escribe el fichero igualmente,
        así que si el guardián se queda mudo aquí, la edición pasa.
        """
        completed = guardian_bytes(
            self.project, payload={"tool_input": {"file_path": "src/evil\ud800.ts"}}
        )
        payload = self.assert_one_valid_decision(completed, "deny", "surrogate suelto")
        self.assertIn(
            "src/evil", payload["hookSpecificOutput"]["permissionDecisionReason"]
        )

    def test_a_file_path_with_accents_and_quotes_round_trips(self):
        """Los escapes ASCII no deforman el mensaje: el cliente lo recompone entero."""
        weird = 'src/año/«edición»/precio€.ts'
        completed = guardian_bytes(self.project, payload={"tool_input": {"file_path": weird}})
        payload = self.assert_one_valid_decision(completed, "deny", "ruta con acentos")
        reason = payload["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn(weird, reason)
        self.assertIn("«", reason, "los escapes «\\uXXXX» deben volver a ser texto")

    def test_the_decision_is_pure_ascii_even_in_the_ordinary_environment(self):
        """Siempre ASCII: la salida no depende de la codificación de nadie."""
        completed = guardian_bytes(self.project)
        self.assertTrue(completed.stdout.isascii(), repr(completed.stdout[:200]))

    def test_stdout_is_exactly_one_document_even_when_the_payload_is_garbage(self):
        """Con el payload roto sale un «allow» y **uno solo**, no dos pegados."""
        env = dict(os.environ)
        env["HOME"] = str(self.project.home)
        completed = subprocess.run(
            [sys.executable, str(GUARDIAN_PY)],
            input=b"{{{ roto",
            capture_output=True,
            cwd=str(self.project.root),
            env=env,
            timeout=30,
        )
        self.assert_one_valid_decision(completed, "allow", "payload roto")

    def test_a_broken_stderr_cannot_swallow_the_decision(self):
        """Con el otro extremo de stderr cerrado, la decisión sale igual y el rc sigue siendo 0.

        El guardián escribe la traza de cualquier tropiezo en stderr. Si ese
        stderr está roto, escribir en él lanza dentro del propio manejador de
        errores —y el hook se queda sin decidir— o deja bytes sin vaciar que
        hacen terminar al intérprete con código 120, que para el cliente es un
        «error del hook» aunque la decisión esté escrita. Las dos formas
        acaban en lo mismo: la edición pasa.
        """
        self.corrupt_the_change()
        read_end, write_end = os.pipe()
        os.close(read_end)  # nadie leerá: escribir en ese stderr fallará
        try:
            process = subprocess.Popen(
                [sys.executable, str(GUARDIAN_PY)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=write_end,
                cwd=str(self.project.root),
                env={**os.environ, "HOME": str(self.project.home)},
            )
        finally:
            os.close(write_end)
        stdout, _ = process.communicate(
            json.dumps(
                {
                    "hook_event_name": "PreToolUse",
                    "cwd": str(self.project.root),
                    "tool_name": "Write",
                    "tool_input": {"file_path": CODE_PATH},
                }
            ).encode("ascii"),
            timeout=30,
        )
        completed = subprocess.CompletedProcess(
            args=(), returncode=process.returncode, stdout=stdout, stderr=b""
        )

        self.assert_one_valid_decision(completed, "deny", "stderr roto")

    def corrupt_the_change(self) -> None:
        """Deja el «change.json» del proyecto ilegible: así el guardián tiene qué trazar."""
        self.project.path(".venoxia/changes/c1/change.json").write_bytes(
            b"\x00\x01\xff\xfe\x80 basura binaria"
        )

    def test_the_last_resort_bytes_are_valid_decisions(self):
        """El último escalón de la emisión son bytes ya escritos: tienen que valer."""
        constants = source_constant("LAST_RESORT_BYTES")
        self.assertEqual({"allow", "deny"}, set(constants))
        for decision, data in constants.items():
            with self.subTest(decision=decision):
                self.assertIsInstance(data, bytes)
                self.assertTrue(data.endswith(b"\n"))
                payload = json.loads(data.decode("ascii"))
                block = payload["hookSpecificOutput"]
                self.assertEqual("PreToolUse", block["hookEventName"])
                self.assertEqual(decision, block["permissionDecision"])
                self.assertTrue(block["permissionDecisionReason"].strip())
                self.assertEqual(decision == "deny", "systemMessage" in payload)

    def test_the_reserve_reasons_are_ascii_only(self):
        """Las razones de reserva van sin acentos a propósito: son el último recurso."""
        for name in ("REASON_ASCII_ALLOW", "REASON_ASCII_DENY"):
            with self.subTest(constant=name):
                value = source_constant(name)
                self.assertTrue(value.isascii(), f"«{name}» debía ser ASCII puro")
                self.assertTrue(value.strip())

    def test_the_serialization_escapes_instead_of_trusting_the_encoding(self):
        """`ensure_ascii=False` al emitir es exactamente lo que rompía la emisión."""
        source = Path(GUARDIAN_PY).read_text(encoding="utf-8")
        self.assertIn("ensure_ascii=True", source)
        self.assertIn("sys.stdout.buffer", source)


# ---------------------------------------------------------------------------
# La garantía de terminación
# ---------------------------------------------------------------------------


class GuardianExitGuaranteeTest(GuardianTestCase):
    """*Pase lo que pase, el guardián termina con código 0 y por su stdout ha
    salido exactamente un documento JSON parseable con una decisión válida.*

    Las dos mitades se comprueban por separado porque se sostienen por separado:
    contra un stdout que no admite escritura no hay documento posible, pero el
    código de salida se cumple igual.

    Y el código de salida importa tanto como el JSON. Para Claude Code, un
    código distinto de 0 y de 2 es «error no bloqueante del hook»: **la edición
    sigue**. Con la decisión en el `BufferedWriter` y el `flush` reventado, el
    que reintentaba vaciar era `Py_FinalizeEx` al terminar el intérprete, ya
    fuera de todo `except`, y el proceso salía con 120: un `deny` escrito que el
    cliente descarta. Era el mismo fallo ya cerrado para stderr —`write_stderr`
    y su sumidero— sin aplicar a stdout.
    """

    def setUp(self) -> None:
        if os.name != "posix":
            self.skipTest("los stdout hostiles de estos tests son POSIX")
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="spec")

    def payload(self, file_path: str = CODE_PATH) -> bytes:
        """El payload del hook, en ASCII, para mandárselo al proceso por stdin."""
        return json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(self.project.root),
                "tool_name": "Write",
                "tool_input": {"file_path": file_path},
            },
            ensure_ascii=True,
        ).encode("ascii")

    def child_env(self, overrides: dict[str, str | None] | None = None) -> dict[str, str]:
        """El entorno del hijo, con el `HOME` falso y lo que el caso quiera torcer."""
        env = dict(os.environ)
        env["HOME"] = str(self.project.home)
        for name, value in (overrides or {}).items():
            env.pop(name, None) if value is None else env.update({name: value})
        return env

    def run_with_stdout(self, stdout, close_after: str | None = None) -> int:
        """Lanza el guardián con ese stdout y devuelve su código de salida."""
        process = subprocess.Popen(
            [sys.executable, str(GUARDIAN_PY)],
            stdin=subprocess.PIPE,
            stdout=stdout,
            stderr=subprocess.PIPE,
            cwd=str(self.project.root),
            env=self.child_env(),
            preexec_fn=(lambda: os.close(1)) if close_after == "fd1" else None,
        )
        process.communicate(self.payload(), timeout=30)
        return process.returncode

    # -- Los stdout hostiles -------------------------------------------------

    def case_pipe_without_a_reader(self) -> int:
        """stdout es un pipe cuyo lector ya se cerró: el `flush` revienta."""
        read_end, write_end = os.pipe()
        os.close(read_end)
        try:
            return self.run_with_stdout(write_end)
        finally:
            os.close(write_end)

    def case_read_only_descriptor(self) -> int:
        """stdout es un descriptor abierto en sólo lectura: escribir da EBADF."""
        descriptor = os.open(os.devnull, os.O_RDONLY)
        try:
            return self.run_with_stdout(descriptor)
        finally:
            os.close(descriptor)

    def case_closed_stdout(self) -> int:
        """El descriptor 1 llega cerrado: ni siquiera hay `sys.stdout`."""
        return self.run_with_stdout(subprocess.DEVNULL, close_after="fd1")

    def case_dev_full(self) -> int:
        """stdout apunta a `/dev/full`: cada escritura da ENOSPC. Sólo en Linux."""
        if not os.path.exists("/dev/full"):
            self.skipTest("esta máquina no tiene «/dev/full» (macOS no lo trae)")
        with open("/dev/full", "wb") as handle:
            return self.run_with_stdout(handle.fileno())

    HOSTILE_STDOUTS = (
        "case_pipe_without_a_reader",
        "case_read_only_descriptor",
        "case_closed_stdout",
        "case_dev_full",
    )

    def test_every_hostile_stdout_still_exits_zero(self):
        """Ningún stdout roto puede colar un código de salida distinto de 0.

        El 120 no es un detalle de higiene: es la diferencia entre un `deny`
        que el cliente obedece y un `deny` que descarta como error del hook.
        """
        for name in self.HOSTILE_STDOUTS:
            builder = getattr(self, name)
            with self.subTest(case=name, what=builder.__doc__):
                returncode = builder()

                self.assertEqual(
                    0,
                    returncode,
                    f"{name}: salió con {returncode} "
                    "(120 = quedaron bytes sin vaciar al finalizar el intérprete)",
                )

    # -- Los bytes crudos, donde sí se pueden mirar ---------------------------

    def decision_written_to_a_file(self, overrides=None, file_path: str = CODE_PATH) -> bytes:
        """Corre el guardián con stdout redirigido a un fichero y devuelve sus bytes."""
        target = self.project.root.parent / "salida-del-guardian"
        with open(target, "wb") as handle:
            process = subprocess.Popen(
                [sys.executable, str(GUARDIAN_PY)],
                stdin=subprocess.PIPE,
                stdout=handle,
                stderr=subprocess.PIPE,
                cwd=str(self.project.root),
                env=self.child_env(overrides),
            )
            process.communicate(self.payload(file_path), timeout=30)
        self.assertEqual(0, process.returncode, "el guardián no terminó con 0")
        return target.read_bytes()

    def assert_exactly_one_decision(self, raw: bytes, expected: str, context: str) -> None:
        """Los bytes son **un** documento JSON, en ASCII, con una decisión válida."""
        detail = f"{context}\nstdout ({len(raw)} bytes): {raw[:400]!r}"
        self.assertTrue(raw, f"stdout quedó vacío.\n{detail}")
        self.assertTrue(raw.isascii(), f"la decisión debía salir en ASCII puro.\n{detail}")
        text = raw.decode("utf-8")
        self.assertEqual(
            1, len([line for line in text.splitlines() if line.strip()]), detail
        )
        block = json.loads(text)["hookSpecificOutput"]
        self.assertEqual("PreToolUse", block["hookEventName"], detail)
        self.assertEqual(expected, block["permissionDecision"], detail)
        self.assertTrue(block["permissionDecisionReason"].strip(), detail)

    def test_the_raw_bytes_are_one_document_in_every_hostile_environment(self):
        """Con stdout a un fichero de verdad, la decisión sale entera y sale una sola vez."""
        environments = ({},) + GuardianEmissionTest.HOSTILE_ENVIRONMENTS
        for overrides in environments:
            with self.subTest(env=overrides or "entorno normal"):
                raw = self.decision_written_to_a_file(overrides)

                self.assert_exactly_one_decision(raw, "deny", f"entorno {overrides}")

    def test_the_guarantee_holds_for_an_allow_as_well(self):
        """La garantía no es del `deny`: es de la decisión, sea la que sea."""
        raw = self.decision_written_to_a_file(file_path=".venoxia/principles.md")

        self.assert_exactly_one_decision(raw, "allow", "ruta de especificación")


# ---------------------------------------------------------------------------
# La raíz del proyecto tiene más de un nombre absoluto
# ---------------------------------------------------------------------------


class GuardianRootAliasTest(GuardianTestCase):
    """`/tmp/p/src/x.ts` y `/private/tmp/p/src/x.ts` son el mismo fichero.

    Comparar cadenas contra el `cwd` dejaba fuera del proyecto —y por tanto
    permitida— la mitad de las rutas absolutas de cualquier Mac: `/tmp`, `/var`
    y `/etc` son enlaces, y nadie tiene que prepararlos.

    Aquí el alias se fabrica **con un symlink**, y eso es exactamente lo que
    esta clase cubre y nada más: la familia que `os.path.realpath` sí resuelve.
    Durante una ronda entera este docstring afirmó cubrir también los firmlinks
    de `/System/Volumes/Data/…`, que `realpath` **no** resuelve: el caso pasaba
    en verde porque el alias se fabricaba con un symlink, no con un firmlink. Un
    test que dice cubrir un caso que no cubre es peor que no tenerlo. Los tres
    alias que no son symlinks —firmlink, caja y NFC/NFD— viven en
    `GuardianRootIdentityTest`, que los fabrica de verdad.
    """

    def setUp(self) -> None:
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="spec")
        self.alias = self.project.root.parent / "otro-nombre-de-la-raiz"
        try:
            self.alias.symlink_to(self.project.root, target_is_directory=True)
        except (OSError, NotImplementedError) as error:  # pragma: no cover
            self.skipTest(f"este sistema no deja crear symlinks: {error}")

    def test_code_reached_through_another_name_of_the_root_is_still_judged(self):
        """El mismo fichero por otro nombre de la raíz se sigue denegando."""
        run = self.project.guardian(file_path=str(self.alias / "src" / "checkout.ts"))

        self.assert_deny(run, "el alias de la raíz no puede sacar el fichero del proyecto")
        self.assertIn("src/checkout.ts", run.reason)

    def test_specification_reached_through_the_alias_is_recognised(self):
        """Resolver la ruta no sólo deniega más: también reconoce la spec por el alias."""
        run = self.project.guardian(file_path=str(self.alias / ".venoxia" / "principles.md"))

        self.assert_allow(run)
        self.assertIn(
            "es especificación",
            run.reason,
            "debía reconocerla como spec, no darla por fuera del proyecto",
        )
        self.assertIn("«.venoxia/principles.md»", run.reason)

    def test_a_path_genuinely_outside_the_project_is_still_allowed(self):
        """Lo de fuera sigue fuera: resolver no puede convertir el guardián en un muro."""
        outside = self.project.root.parent / "otro-proyecto" / "src" / "x.ts"

        run = self.project.guardian(file_path=str(outside))

        self.assert_allow(run, "un fichero de otro proyecto no es asunto del guardián")

    def test_a_symlink_out_of_the_project_does_not_launder_the_edit(self):
        """El rodeo contrario, que resolver **sólo** con realpath abriría.

        `src/fuera/` es un enlace a un directorio de fuera: por cadena la ruta
        está dentro del proyecto y eso basta para juzgarla. Entre un «deny» de
        más y un «allow» de más, aquí se elige siempre el primero.
        """
        target = self.project.root.parent / "destino-fuera"
        target.mkdir(parents=True, exist_ok=True)
        link = self.project.path("src/fuera")
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target, target_is_directory=True)

        run = self.project.guardian(file_path="src/fuera/checkout.ts")

        self.assert_deny(run, "por cadena está dentro del proyecto: se juzga")

    def test_an_impossible_path_falls_back_instead_of_raising(self):
        """Un «realpath» que no se puede calcular vuelve al comportamiento anterior."""
        loop_a = self.project.path("bucle-a")
        loop_b = self.project.path("bucle-b")
        loop_a.symlink_to(loop_b)
        loop_b.symlink_to(loop_a)

        run = self.project.guardian(file_path="bucle-a/checkout.ts")

        self.assert_deny(run, "un bucle de symlinks dentro del proyecto no exime de nada")

    def test_resolving_the_root_costs_microseconds_not_milliseconds(self):
        """El precio del arreglo, medido: dos «realpath» sobre las rutas reales del caso."""
        root = str(self.project.root)
        candidate = str(self.alias / "src" / "checkout.ts")
        iterations = 200

        start = time.perf_counter()
        for _ in range(iterations):
            os.path.realpath(root)
            os.path.realpath(candidate)
        per_decision = (time.perf_counter() - start) / iterations

        self.assertLess(
            per_decision,
            0.002,
            f"las dos llamadas a realpath cuestan {per_decision * 1000:.3f} ms por decisión; "
            "el presupuesto entero del guardián son 100 ms",
        )

    def test_the_alias_path_stays_within_the_latency_budget(self):
        """Y la invocación entera por el camino que sí resuelve, también."""
        target = str(self.alias / "src" / "checkout.ts")
        self.project.guardian(file_path=target)  # calentamiento

        start = time.perf_counter()
        run = self.project.guardian(file_path=target)
        elapsed = time.perf_counter() - start

        self.assert_deny(run)
        self.assertLess(elapsed, LATENCY_BUDGET_SECONDS, f"tardó {elapsed * 1000:.0f} ms")


# ---------------------------------------------------------------------------
# La raíz se compara por identidad de fichero, no por cómo se escriba
# ---------------------------------------------------------------------------


def same_file(left, right) -> bool:
    """¿Las dos rutas llevan al mismo fichero? El par `(st_dev, st_ino)` lo dice."""
    try:
        one, other = os.stat(left), os.stat(right)
    except OSError:
        return False
    return (one.st_dev, one.st_ino) == (other.st_dev, other.st_ino)


def callable_name(node: ast.expr) -> str:
    """El último nombre de lo que se llama: `os.stat(...)` → `"stat"`."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


#: Lo que en `relative_to_root` cuesta una llamada al sistema.
DISK_CALLS = frozenset({"resolve", "realpath", "stat", "file_identity", "relative_by_identity"})


class GuardianRootIdentityTest(GuardianTestCase):
    """Los alias de la raíz que `realpath` **no** deshace, fabricados de verdad.

    Tres formas de escribir la misma raíz siguen siendo el mismo inodo después
    de pasar por `os.path.realpath`, y ninguna hay que prepararla:

    * **firmlink**: `/System/Volumes/Data/<ruta>` es el mismo directorio que
      `<ruta>` en cualquier Mac desde Catalina, y `realpath` lo deja tal cual.
    * **caja**: APFS es insensible a mayúsculas por defecto.
    * **NFC frente a NFD**: es lo que pasa al copiar del Finder una ruta con
      acentos.

    Con la comparación por cadenas, las tres sacaban del proyecto —y por tanto
    permitían— cualquier fichero de código. La medida que las cierra es la
    única que no depende de cómo se escriba la ruta: `os.stat` y el par
    `(st_dev, st_ino)`.

    Cada test se salta a sí mismo si su alias no existe en la máquina que corre
    la suite: en Linux ni la caja ni la normalización Unicode dan el mismo
    inodo, y ahí no hay nada que cerrar.
    """

    def setUp(self) -> None:
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="spec")

    def alias_or_skip(self, alias: str, what: str) -> str:
        """Devuelve el alias si de verdad es el mismo directorio; si no, salta el test."""
        if not same_file(alias, self.project.root):
            self.skipTest(f"esta máquina no da un alias de la raíz por {what}")
        return alias

    def firmlink(self) -> str:
        """El alias de firmlink de la raíz: `/System/Volumes/Data/<ruta de la raíz>`."""
        return self.alias_or_skip("/System/Volumes/Data" + str(self.project.root), "firmlink")

    def test_a_firmlink_alias_of_the_root_does_not_launder_the_edit(self):
        """Por el firmlink, `src/checkout.ts` sigue siendo código del proyecto: se deniega."""
        run = self.project.guardian(file_path=self.firmlink() + "/src/checkout.ts")

        self.assert_deny(run, "el firmlink de la raíz no puede sacar el fichero del proyecto")
        self.assertIn("src/checkout.ts", run.reason, "y la ruta se enseña ya relativa")

    def test_realpath_alone_does_not_close_the_firmlink_alias(self):
        """La razón de que haga falta el `stat`: `realpath` deja el firmlink tal cual.

        Si algún día macOS resolviera los firmlinks en `realpath`, este test se
        pondría rojo y podría borrarse: el paso 2 de `relative_to_root` bastaría
        para este alias. Mientras tanto, es lo que sostiene el paso 3.
        """
        alias = self.firmlink()

        self.assertNotEqual(
            os.path.realpath(alias),
            os.path.realpath(str(self.project.root)),
            "«realpath» ya deshace el firmlink: revisa si el paso 3 sigue haciendo falta",
        )

    def test_a_case_variant_of_the_root_does_not_launder_the_edit(self):
        """En un APFS insensible a la caja, la raíz en mayúsculas es la misma raíz."""
        alias = self.alias_or_skip(str(self.project.root).upper(), "caja")

        run = self.project.guardian(file_path=alias + "/src/checkout.ts")

        self.assert_deny(run, "la caja de la raíz no puede sacar el fichero del proyecto")

    def test_an_nfd_variant_of_the_root_does_not_launder_the_edit(self):
        """NFC frente a NFD: la ruta con acentos copiada del Finder es la misma ruta."""
        nfc = self.project.root.parent / unicodedata.normalize("NFC", "proyecto-año")
        nfd = self.project.root.parent / unicodedata.normalize("NFD", "proyecto-año")
        self.assertNotEqual(str(nfc), str(nfd), "las dos formas debían escribirse distinto")
        change = nfc / ".venoxia" / "changes" / "c1"
        change.mkdir(parents=True, exist_ok=True)
        (change / "change.json").write_text(
            json.dumps({"id": "c1", "state": "draft", "via": "spec"}), encoding="utf-8"
        )
        if not same_file(nfc, nfd):
            self.skipTest("este sistema de ficheros distingue NFC de NFD")

        run = self.project.guardian(cwd=str(nfc), file_path=str(nfd / "src" / "checkout.ts"))

        self.assert_deny(run, "la normalización Unicode no puede sacar el fichero del proyecto")
        self.assertIn("src/checkout.ts", run.reason)

    def test_specification_reached_through_the_firmlink_is_recognised(self):
        """El arreglo no deniega de más: por el firmlink, la spec se sigue reconociendo."""
        run = self.project.guardian(file_path=self.firmlink() + "/.venoxia/principles.md")

        self.assert_allow(run)
        self.assertIn("es especificación", run.reason)
        self.assertIn("«.venoxia/principles.md»", run.reason)

    def test_a_path_genuinely_outside_the_project_is_still_allowed(self):
        """Comparar inodos no convierte al guardián en un muro: lo de fuera sigue fuera."""
        outside = self.project.root.parent / "otro-proyecto" / "src" / "x.ts"
        outside.parent.mkdir(parents=True, exist_ok=True)
        for target in (str(outside), "/etc/hosts", str(self.project.root.parent)):
            with self.subTest(path=target):
                self.assert_allow(
                    self.project.guardian(file_path=target),
                    f"«{target}» no es del proyecto: el guardián no interviene",
                )

    def test_an_absurdly_deep_path_neither_hangs_nor_denies(self):
        """El tope del ascenso: una ruta imposible se abandona, no se persigue."""
        absurd = "/" + "/".join(["tramo"] * 300) + "/x.ts"

        run = self.project.guardian(file_path=absurd)

        self.assert_allow(run, "una ruta absurda queda fuera; el ascenso está acotado")

    def test_the_frequent_path_is_decided_without_touching_the_disk(self):
        """El `stat` sólo se paga cuando la aritmética de cadenas ya ha dicho «fuera».

        La estructura de `relative_to_root` es lo que lo garantiza: devuelve el
        resultado de las cadenas **antes** de llamar a nada que toque el disco.
        Mover la comparación por identidad delante pondría este test rojo, que
        es justo lo que se quiere: le costaría un `stat` a cada edición.
        """
        tree = ast.parse(Path(GUARDIAN_PY).read_text(encoding="utf-8"))
        function = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "relative_to_root"
        )
        early = [
            node.lineno
            for node in ast.walk(function)
            if isinstance(node, ast.Return)
            and isinstance(node.value, ast.Name)
            and node.value.id == "relative"
        ]
        disk = [
            node.lineno
            for node in ast.walk(function)
            if isinstance(node, ast.Call) and callable_name(node.func) in DISK_CALLS
        ]

        self.assertTrue(early, "«relative_to_root» ya no devuelve pronto lo que dicen las cadenas")
        self.assertTrue(disk, "«relative_to_root» ya no compara por identidad ni resuelve")
        self.assertLess(
            min(early),
            min(disk),
            "el camino frecuente pasó a pagar una llamada al sistema por edición",
        )

    def test_the_identity_ascent_costs_microseconds_not_milliseconds(self):
        """El precio del arreglo, medido: un `stat` de la raíz y unos pocos del ascenso."""
        root = str(self.project.root)
        cases = {
            "el alias de firmlink": "/System/Volumes/Data" + root + "/src/checkout.ts",
            "el peor caso": "/" + "/".join(["tramo-que-no-existe"] * 130) + "/x.ts",
        }
        iterations = 200
        for label, candidate in cases.items():
            with self.subTest(case=label):
                start = time.perf_counter()
                for _ in range(iterations):
                    target = os.stat(root)
                    current = candidate
                    for _hop in range(128):
                        try:
                            status = os.stat(current)
                        except OSError:
                            status = None
                        if status is not None and (
                            (status.st_dev, status.st_ino) == (target.st_dev, target.st_ino)
                        ):
                            break
                        parent = os.path.dirname(current)
                        if parent == current:
                            break
                        current = parent
                per_decision = (time.perf_counter() - start) / iterations

                self.assertLess(
                    per_decision,
                    0.005,
                    f"el ascenso por identidad cuesta {per_decision * 1000:.3f} ms por "
                    "decisión; el presupuesto entero del guardián son 100 ms",
                )

    def test_the_firmlink_path_stays_within_the_latency_budget(self):
        """Y la invocación entera por el camino que compara inodos, también."""
        target = self.firmlink() + "/src/checkout.ts"
        self.project.guardian(file_path=target)  # calentamiento

        start = time.perf_counter()
        run = self.project.guardian(file_path=target)
        elapsed = time.perf_counter() - start

        self.assert_deny(run)
        self.assertLess(elapsed, LATENCY_BUDGET_SECONDS, f"tardó {elapsed * 1000:.0f} ms")


# ---------------------------------------------------------------------------
# Qué ruta juzga cada herramienta
# ---------------------------------------------------------------------------


class GuardianToolPathPreferenceTest(GuardianTestCase):
    """`NotebookEdit` trae la ruta en `notebook_path` (contrato §6); el resto, en `file_path`.

    Mirar siempre `file_path` primero hacía que un `NotebookEdit` con los dos
    campos juzgase el equivocado: un `file_path` de adorno que pareciera
    especificación bastaba para editar cualquier cuaderno.
    """

    def setUp(self) -> None:
        self.project = self.make_project()
        self.project.change("c1", state="draft", via="spec")

    def test_notebook_edit_prefers_notebook_path_when_both_are_present(self):
        """Con los dos campos, «NotebookEdit» juzga el cuaderno, no el señuelo."""
        run = self.project.guardian(
            tool_name="NotebookEdit",
            tool_input={"file_path": "spec.md", "notebook_path": "src/analysis.ipynb"},
        )

        self.assert_deny(run, "el señuelo «spec.md» no puede decidir por el cuaderno")
        self.assertIn("src/analysis.ipynb", run.reason)

    def test_the_editing_tools_prefer_file_path_when_both_are_present(self):
        """Y al revés: «Write» y «Edit» juzgan «file_path» aunque venga un «notebook_path»."""
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                run = self.project.guardian(
                    tool_name=tool,
                    tool_input={"file_path": CODE_PATH, "notebook_path": "spec.md"},
                )
                self.assert_deny(run, "el señuelo «spec.md» no puede decidir por el código")
                self.assertIn(CODE_PATH, run.reason)

    def test_each_tool_falls_back_to_the_other_key(self):
        """La clave que falta no deja al guardián sin ruta: la otra queda de reserva."""
        cases = (
            ("NotebookEdit", {"file_path": "src/analysis.ipynb"}, "src/analysis.ipynb"),
            ("Write", {"notebook_path": "src/analysis.ipynb"}, "src/analysis.ipynb"),
        )
        for tool, tool_input, expected in cases:
            with self.subTest(tool=tool, tool_input=tool_input):
                run = self.project.guardian(tool_name=tool, tool_input=tool_input)
                self.assert_deny(run)
                self.assertIn(expected, run.reason)


# ---------------------------------------------------------------------------
# Un «change.json» fabricado a mano no desactiva el guardián
# ---------------------------------------------------------------------------


class GuardianForgedChangeTest(GuardianTestCase):
    """El paso 3 pide algo más que una palabra en un fichero.

    Con sólo la herramienta `Write` y sin escribir una línea de especificación
    se podía desarmar el guardián en dos pasos: `.venoxia/` es especificación y
    se puede escribir (paso 2), así que bastaba fabricar allí un `change.json`
    con `"state": "validated"` para que todo el código pasara después. Ahora el
    paso 3 exige además el `delta/*.md` del cambio: sigue siendo falsificable
    por quien pueda escribir bajo `.venoxia/` —está documentado en el README—,
    pero ya no es gratis ni accidental.
    """

    def setUp(self) -> None:
        self.project = self.make_project()

    def test_the_two_step_bypass_no_longer_disarms_the_guardian(self):
        """La secuencia exacta del rodeo, paso a paso, terminando en «deny»."""
        self.assert_deny(
            self.project.guardian(file_path=CODE_PATH), "a) código sin spec: se deniega"
        )
        self.assert_allow(
            self.project.guardian(file_path=".venoxia/changes/zzz/change.json"),
            "b) escribir bajo «.venoxia/» sigue permitido: es el paso 2",
        )
        self.project.change("zzz", state="validated", via="spec")

        self.assert_deny(
            self.project.guardian(file_path=CODE_PATH),
            "c) un «change.json» sin delta no acredita ninguna especificación",
        )

    def test_the_deny_explains_that_the_delta_is_missing(self):
        """El mensaje dice qué falta: el delta del cambio, con su ruta."""
        self.project.change("zzz", state="validated", via="spec")

        reason = self.project.guardian(file_path=CODE_PATH).reason

        self.assertIn("delta", reason)
        self.assertIn("zzz", reason)
        self.assertIn("/venoxia:validate", reason)

    def test_an_empty_or_non_markdown_delta_does_not_count(self):
        """Un «delta/» de mentira tampoco vale: hace falta markdown con algo dentro."""
        cases = {
            "delta/checkout.md vacío": ("delta/checkout.md", ""),
            "delta/checkout.md en blanco": ("delta/checkout.md", ""),
            "delta/notas.txt con texto": ("delta/notas.txt", "no soy markdown"),
        }
        for label, (relative, content) in cases.items():
            with self.subTest(case=label):
                project = self.make_project()
                project.change("zzz", state="validated", via="spec")
                project.write(f".venoxia/changes/zzz/{relative}", content)

                self.assert_deny(project.guardian(file_path=CODE_PATH), label)

    def test_a_validated_change_with_a_real_delta_still_allows(self):
        """El arreglo no cierra el camino legítimo: con su delta, el cambio vale."""
        self.project.change("zzz", state="validated", via="spec")
        self.give_delta(self.project, "zzz")

        run = self.project.guardian(file_path=CODE_PATH)

        self.assert_allow(run, "un cambio validado con su delta respalda la edición")
        self.assertIn("validated", run.reason)
        self.assertFalse(
            self.project.exists(DRIFT_LOG),
            "un «validated» respaldado no es deriva: no se anota nada",
        )

    def test_an_unbacked_validated_change_that_passes_via_direct_is_recorded(self):
        """Si el «validated» sin delta pasa por la puerta de «direct», queda marcado."""
        self.project.change("zzz", state="validated", via="direct")

        self.assert_allow(self.project.guardian(file_path=CODE_PATH))

        entry = json.loads(self.drift_lines(self.project)[0])
        self.assertEqual(
            {"ts", "change", "tool", "path", "note"},
            set(entry),
            "el apunte debe traer los cuatro campos del contrato y la marca del porqué",
        )
        self.assertEqual("validated-sin-delta", entry["note"])
        self.assertEqual("zzz", entry["change"])
        self.assertEqual(CODE_PATH, entry["path"])

    def test_an_unreadable_delta_directory_allows_and_says_why(self):
        """No poder mirar el «delta/» sí es un fallo nuestro: se permite, y se anota."""
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("como root, «chmod 000» no impide leer")
        self.project.change("zzz", state="validated", via="spec")
        delta_dir = self.project.path(".venoxia/changes/zzz/delta")
        delta_dir.mkdir(parents=True, exist_ok=True)
        (delta_dir / "checkout.md").write_text(DELTA_MARKDOWN, encoding="utf-8")
        os.chmod(delta_dir, 0o000)
        self.addCleanup(os.chmod, delta_dir, 0o755)

        run = self.project.guardian(file_path=CODE_PATH)

        self.assert_allow(run, "un directorio ilegible es un fallo del guardián: fail-open")
        entry = json.loads(self.drift_lines(self.project)[0])
        self.assertEqual("delta-no-comprobable", entry["note"])

    def test_the_change_id_from_the_file_never_builds_a_path(self):
        """El «id» del «change.json» es del usuario: vale para el mensaje, no para la ruta."""
        self.project.change("zzz", state="validated", via="spec", extra={"id": "../../c1"})
        self.give_delta(self.project, "zzz")

        run = self.project.guardian(file_path=CODE_PATH)

        # El delta que cuenta es el del directorio «zzz», no el que insinúa el «id».
        self.assert_allow(run)
        self.assertNotIn("../../c1", run.reason, "un «id» con barras no se enseña tal cual")

    def test_the_deny_points_at_the_change_directory_that_exists(self):
        """La ruta que ofrece el «deny» es la del directorio, no la del «id» declarado.

        Mandar al usuario a un fichero que no está en el disco es peor que no
        decirle nada, y el «id» del `change.json` puede no coincidir con el
        nombre del directorio que lo contiene.
        """
        self.project.change("zzz", state="draft", via="spec", extra={"id": "otro-nombre"})

        reason = self.project.guardian(file_path=CODE_PATH).reason

        self.assertIn(".venoxia/changes/zzz/change.json", reason)
        self.assertNotIn(".venoxia/changes/otro-nombre/change.json", reason)
        self.assertIn("otro-nombre", reason, "el «id» declarado sí vale para nombrar el cambio")


# ---------------------------------------------------------------------------
# Un «change.json» corrupto no es el fail-open
# ---------------------------------------------------------------------------


class GuardianCorruptChangeTest(GuardianTestCase):
    """Un fichero del usuario que está mal no da derecho a pasar.

    El fail-open cubre los fallos **del guardián**: lo que él no supo hacer.
    Un `change.json` ilegible es otra cosa: es una respuesta que no acredita
    nada. Tratarlo como fail-open abría la segunda mitad del rodeo —dejar el
    `change.json` corrupto a propósito desactivaba el guardián entero—, así que
    ahora se salta y la búsqueda sigue; si no queda ningún cambio bueno, se
    deniega.
    """

    def corrupt(self, project: Project, change_id: str = "c1") -> None:
        """Deja el «change.json» de un cambio como basura binaria."""
        project.path(f".venoxia/changes/{change_id}/change.json").write_bytes(
            b"\x00\x01\xff\xfe\x80 basura binaria"
        )

    def test_a_binary_change_json_does_not_grant_the_edit(self):
        """El «change.json» binario del único cambio: se deniega, no se permite."""
        project = self.make_project()
        self.corrupt(project)

        run = project.guardian(file_path=CODE_PATH)

        self.assert_deny(run, "un «change.json» ilegible no acredita nada")
        self.assertEqual(0, run.returncode)

    def test_a_change_json_that_is_not_an_object_does_not_grant_the_edit(self):
        """Un array —o cualquier JSON que no sea un objeto— tampoco es un cambio."""
        for raw in ('[{"state": "validated"}]\n', '"validated"\n', "null\n"):
            with self.subTest(raw=raw):
                project = self.make_project()
                project.change("c1", raw=raw)

                self.assert_deny(project.guardian(file_path=CODE_PATH), raw)

    def test_an_oversized_change_json_does_not_grant_the_edit(self):
        """Un «change.json» de más de 1 MiB no es nuestro: no se lee y no acredita."""
        project = self.make_project()
        project.change("c1", raw='{"state": "validated"}\n' + " " * (1 << 20))
        self.give_delta(project, "c1")

        self.assert_deny(project.guardian(file_path=CODE_PATH))

    def test_the_deny_names_the_change_that_could_not_be_read(self):
        """El mensaje dice cuál es el fichero roto y sigue diciendo qué teclear."""
        project = self.make_project()
        self.corrupt(project)

        reason = project.guardian(file_path=CODE_PATH).reason

        self.assertIn("c1", reason)
        self.assertIn("change.json", reason)
        self.assertIn("/venoxia:specify", reason)

    def test_a_corrupt_change_does_not_hide_an_older_valid_one(self):
        """«Sigue evaluando»: el cambio roto se salta y manda el siguiente legible."""
        project = self.make_project()
        project.change("older", state="validated", via="spec")
        self.give_delta(project, "older")
        project.change("newer", raw="{{{ esto no es JSON\n")

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run, "el cambio válido de debajo sigue valiendo")
        self.assertIn("older", run.reason)

    def test_a_corrupt_change_still_exits_zero_with_one_decision_and_a_trace(self):
        """Denegar no es romperse: exit 0, una sola decisión y la traza en stderr."""
        project = self.make_project()
        self.corrupt(project)

        run = project.guardian(file_path=CODE_PATH)

        self.assertEqual(0, run.returncode, run.describe())
        self.assertEqual(1, len([line for line in run.stdout.splitlines() if line.strip()]))
        self.assertIn("Traceback", run.stderr, "el fichero roto debe dejar rastro en stderr")


# ---------------------------------------------------------------------------
# No poder leer el «change.json» es un fallo nuestro, no del usuario
# ---------------------------------------------------------------------------


class GuardianIoFailOpenTest(GuardianTestCase):
    """La otra mitad de la distinción, la que se confundió en sentido contrario.

    `GuardianCorruptChangeTest` defiende que un `change.json` **mal escrito**
    no acredita nada y se deniega. Endurecer eso metió el `OSError` en el mismo
    `except` que el JSON corrupto, y con él un EACCES o un EISDIR pasaron a
    contar como «fichero del usuario que está mal»: un `.venoxia/` que quedó de
    root tras un `sudo`, o un montaje de red que va y viene, bloqueaban **todas**
    las ediciones con un mensaje que manda ejecutar `/venoxia:specify`, que no lo
    arregla. Es el escenario exacto por el que un guardián se desinstala.

    No poder **leer** no dice nada del proyecto: dice que no hemos podido
    preguntar. Eso es un fallo nuestro y manda el fail-open, igual que en
    `has_delta_evidence`, que ya lo hacía bien diez líneas más abajo.
    """

    def skip_if_root(self) -> None:
        """Como root, `chmod 000` no impide nada y el caso no se puede montar."""
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("como root, «chmod 000» no impide leer")

    def case_change_json_without_read_permission(self):
        """El `change.json` del cambio activo, sin permiso de lectura (EACCES)."""
        self.skip_if_root()
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        target = project.path(".venoxia/changes/c1/change.json")
        os.chmod(target, 0o000)
        self.addCleanup(os.chmod, target, 0o644)
        return project

    def case_change_json_is_a_directory(self):
        """El `change.json` resultó ser un directorio (EISDIR)."""
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        target = project.path(".venoxia/changes/c1/change.json")
        target.unlink()
        target.mkdir()
        return project

    def case_change_directory_without_permissions(self):
        """El directorio del cambio no se deja mirar: ni siquiera hay `stat`."""
        self.skip_if_root()
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        target = project.path(".venoxia/changes/c1")
        os.chmod(target, 0o000)
        self.addCleanup(os.chmod, target, 0o755)
        return project

    def case_changes_directory_without_permissions(self):
        """El propio `.venoxia/changes/` no se deja recorrer."""
        self.skip_if_root()
        project = self.make_project()
        project.change("c1", state="validated", via="spec")
        target = project.path(".venoxia/changes")
        os.chmod(target, 0o000)
        self.addCleanup(os.chmod, target, 0o755)
        return project

    IO_CASES = (
        "case_change_json_without_read_permission",
        "case_change_json_is_a_directory",
        "case_change_directory_without_permissions",
        "case_changes_directory_without_permissions",
    )

    def test_every_io_failure_allows_and_exits_zero(self):
        """Ningún fallo de entrada/salida puede convertirse en un `deny`."""
        for name in self.IO_CASES:
            builder = getattr(self, name)
            with self.subTest(case=name, what=builder.__doc__):
                project = builder()

                run = project.guardian(file_path=CODE_PATH)

                self.assertEqual(0, run.returncode, f"{name}\n{run.describe()}")
                self.assertEqual(
                    "allow",
                    run.decision,
                    f"{name}: un fallo de E/S es nuestro, no del usuario\n{run.describe()}",
                )

    def test_the_io_failure_is_recorded_in_the_drift_log(self):
        """Un `allow` concedido sin haber podido comprobar nada queda anotado."""
        project = self.case_change_json_without_read_permission()

        self.assert_allow(project.guardian(file_path=CODE_PATH))

        entry = json.loads(self.drift_lines(project)[0])
        self.assertEqual("change-no-legible", entry["note"])
        self.assertEqual("c1", entry["change"])
        self.assertEqual(CODE_PATH, entry["path"])

    def test_the_reason_says_it_is_our_failure_and_where_the_trace_is(self):
        """El texto del `allow` distingue el fallo de E/S de un fichero mal escrito."""
        project = self.case_change_json_is_a_directory()

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run)
        self.assertIn("no se pudo leer", run.reason)
        self.assertIn("fail-open", run.reason)
        self.assertIn(DRIFT_LOG, run.reason)
        self.assertIn("Traceback", run.stderr, "el tropiezo debe dejar rastro en stderr")

    def test_the_distinction_holds_in_both_directions(self):
        """La frontera entera en un solo test: E/S permite, JSON corrupto deniega.

        Es la comprobación que impide arreglar uno de los dos lados rompiendo el
        otro, que es exactamente lo que ha pasado dos veces.
        """
        unreadable = self.case_change_json_without_read_permission()
        self.assert_allow(
            unreadable.guardian(file_path=CODE_PATH),
            "no poder leer el fichero es un fallo del guardián: fail-open",
        )

        corrupt = self.make_project()
        corrupt.path(".venoxia/changes/c1/change.json").write_bytes(b"\x00\xff basura")
        self.assert_deny(
            corrupt.guardian(file_path=CODE_PATH),
            "un fichero del usuario mal escrito no acredita nada: deny",
        )

    def test_an_unreadable_newer_change_does_not_fall_back_to_an_older_one(self):
        """Si el cambio que mandaba no se pudo leer, no se decide con el de debajo.

        Con el JSON corrupto sí se sigue evaluando: el fichero se leyó y dice
        algo que no vale. Aquí no se ha podido leer nada, así que decidir con un
        cambio más viejo sería decidir con la certeza de no saber.
        """
        self.skip_if_root()
        project = self.make_project()
        project.change("older", state="draft", via="spec")
        project.change("newer", state="validated", via="spec")
        target = project.path(".venoxia/changes/newer/change.json")
        os.chmod(target, 0o000)
        self.addCleanup(os.chmod, target, 0o644)

        run = project.guardian(file_path=CODE_PATH)

        self.assert_allow(run, "el cambio que decidía no se pudo leer: fail-open")
        self.assertIn("newer", run.reason)


# ---------------------------------------------------------------------------
# El manifiesto del hook
# ---------------------------------------------------------------------------


class HooksManifestTest(unittest.TestCase):
    """`hooks/hooks.json`: lo que Claude Code lee para instalar el guardián."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = HOOKS_JSON.read_text(encoding="utf-8")

    def entry(self) -> dict:
        """La única entrada de «PreToolUse» del manifiesto."""
        manifest = json.loads(self.raw)
        entries = manifest["hooks"]["PreToolUse"]
        self.assertEqual(1, len(entries), "se esperaba una sola entrada «PreToolUse»")
        return entries[0]

    def test_manifest_is_valid_json_with_a_pretooluse_event(self):
        """El manifiesto es JSON válido y declara el evento «PreToolUse»."""
        manifest = json.loads(self.raw)
        self.assertIn("hooks", manifest)
        self.assertIn("PreToolUse", manifest["hooks"])
        self.assertIsInstance(manifest["hooks"]["PreToolUse"], list)

    def test_matcher_is_exactly_the_three_editing_tools(self):
        """El matcher es exactamente «Edit|Write|NotebookEdit»."""
        self.assertEqual("Edit|Write|NotebookEdit", self.entry()["matcher"])

    def test_hook_declares_a_five_second_timeout(self):
        """El hook declara «timeout»: 5, como manda el contrato."""
        hook = self.entry()["hooks"][0]
        self.assertEqual("command", hook["type"])
        self.assertEqual(5, hook["timeout"])

    def test_command_points_through_plugin_root_at_a_script_that_exists(self):
        """El comando usa «${CLAUDE_PLUGIN_ROOT}» y apunta a un script real del repo."""
        command = self.entry()["hooks"][0]["command"]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", command)

        match = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"']+)", command)
        self.assertIsNotNone(match, f"no se pudo extraer la ruta del script de «{command}»")
        script = REPO_ROOT / match.group(1)
        self.assertTrue(script.is_file(), f"el comando apunta a «{script}», que no existe")


if __name__ == "__main__":
    unittest.main()
