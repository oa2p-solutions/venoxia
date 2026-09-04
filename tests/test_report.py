#!/usr/bin/env python3
"""Suite del informe de Venoxia: `scripts/venoxia/report.py` contra §4 del contrato.

El esquema JSON versión 1 es **contrato público**: el guardián y el futuro panel
de salud leen esas claves. Un cambio silencioso ahí rompe a terceros sin que
nadie se entere, así que esta suite compara **conjuntos de claves** —no simple
presencia— en el primer nivel, en `counts`, en `budget` y en cada hallazgo.

Lo demás que se defiende aquí:

* determinismo byte a byte de `render_json` sobre el mismo resultado;
* el orden de los hallazgos (fichero, línea, código de regla) incluido el sitio
  de los de ámbito global, que no tienen ni fichero ni línea;
* `ensure_ascii=False`, para que «ó», «ñ» y las comillas angulares salgan
  legibles y no como escapes;
* que no hay ANSI cuando se pide `no_color=True` **ni** cuando la salida no es
  un terminal, que es el caso de CI —comprobado por subproceso con la salida
  redirigida a una tubería—;
* el borde del presupuesto de incertidumbre: 0,30 pasa y 0,4 no.

Todo se construye con objetos del modelo en memoria: ni red, ni `$HOME` real,
ni escrituras dentro del repositorio.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

# Los tres modos del contrato (`python3 -m pytest tests/ -q`,
# `python3 -m unittest discover -s tests` y `python3 -m unittest tests.test_report`)
# ya traen la raíz del repositorio en `sys.path`. Ejecutar el fichero a pelo
# —`python3 tests/test_report.py`— no, así que la añadimos aquí. Es idempotente.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import RUN_TIMEOUT, SCRIPTS_DIR

from venoxia import model, report

# ---------------------------------------------------------------------------
# El esquema, escrito aquí a mano a propósito
# ---------------------------------------------------------------------------
# Estas constantes NO se importan de `report.py`: si se dedujeran del código de
# producción, el test aprobaría cualquier cambio de esquema en lugar de
# detenerlo. Son la copia del contrato §4, y sólo se tocan cuando suba
# `version`.

SCHEMA_TOP_LEVEL_KEYS = frozenset(
    {"version", "ok", "strict", "root", "counts", "findings", "budget"}
)
SCHEMA_COUNTS_KEYS = frozenset(
    {"error", "warning", "requirements", "capabilities", "deltas"}
)
SCHEMA_BUDGET_KEYS = frozenset({"low", "total", "ratio", "limit", "ok"})
SCHEMA_FINDING_KEYS = frozenset(
    {"rule", "severity", "message", "file", "line", "requirement_id", "hint"}
)

#: Prefijo de cualquier secuencia de escape ANSI de color.
ANSI_MARKER = "\x1b["

#: Mensaje y remedio con acentos y comillas angulares, para probar `ensure_ascii=False`.
ACCENTED_MESSAGE = "El «revisit:» no señala ningún hecho: la apuesta quedó sin comprobación."
ACCENTED_HINT = "Añade «verifies: ruta/al/test» y señala el test con su «@covers»."


# ---------------------------------------------------------------------------
# Andamio local: objetos del modelo, sin tocar el disco
# ---------------------------------------------------------------------------


def make_finding(
    rule: str = "V06",
    severity: str = model.SEVERITY_ERROR,
    message: str = "Algo va mal.",
    file: str = "",
    line: int | None = None,
    requirement_id: str | None = None,
    hint: str | None = None,
) -> model.Finding:
    """Un hallazgo suelto con los valores que pida cada test."""
    return model.Finding(
        rule=rule,
        severity=severity,
        message=message,
        file=file,
        line=line,
        requirement_id=requirement_id,
        hint=hint,
    )


def make_requirement(number: int, confidence: str = "medium") -> model.Requirement:
    """Un requisito mínimo con el nivel de confianza que se le pida."""
    return model.Requirement(
        id=f"R-CHK-{number:03d}",
        title=f"Requisito {number}",
        line=number,
        narrative="WHEN pasa algo, el sistema responde.",
        meta={"confidence": confidence},
    )


def make_capability(name: str, requirements: list[model.Requirement]) -> model.Capability:
    """Una capability viva con los requisitos dados."""
    return model.Capability(
        name=name, path=f".venoxia/capabilities/{name}/spec.md", requirements=requirements
    )


def result_with_confidence(low: int, total: int) -> model.ValidationResult:
    """Un resultado con `total` requisitos, de los cuales `low` declaran «low»."""
    requirements = [make_requirement(index, "low") for index in range(1, low + 1)]
    requirements += [
        make_requirement(index, "high") for index in range(low + 1, total + 1)
    ]
    capabilities = [make_capability("checkout", requirements)] if total else []
    return model.ValidationResult(capabilities=capabilities, root="/abs/path")


class FakeTTY(io.StringIO):
    """Un `sys.stdout` de mentira que asegura ser un terminal."""

    def isatty(self) -> bool:
        return True


# El guion que ejecuta el subproceso del test de CI: imprime el informe con el
# color habilitado por defecto (`no_color=False`) y deja que sea `isatty()`
# quien decida. Con la salida en una tubería, la decisión debe ser «sin color».
_PIPE_PROBE = '''\
import sys

sys.path.insert(0, {scripts!r})

from venoxia import model, report

result = model.ValidationResult(root=".")
result.add(model.Finding("V06", "error", "Mensaje de error.",
                         file="d/checkout.md", line=14,
                         requirement_id="R-CHK-014", hint="Arregla esto."))
result.add(model.Finding("V14", "warning", "Mensaje de aviso.",
                         file="d/checkout.md", line=9))
sys.stdout.write(report.render_text(result))
'''


# ---------------------------------------------------------------------------
# Claves del esquema
# ---------------------------------------------------------------------------


class TestJsonSchemaKeys(unittest.TestCase):
    """§4 · el documento JSON tiene exactamente las claves del contrato."""

    def setUp(self) -> None:
        self.result = result_with_confidence(low=1, total=12)
        self.result.add(
            make_finding(
                rule="V06",
                message=ACCENTED_MESSAGE,
                file=".venoxia/changes/c1/delta/checkout.md",
                line=14,
                requirement_id="R-CHK-014",
                hint=ACCENTED_HINT,
            )
        )
        self.result.add(
            make_finding(
                rule="V14",
                severity=model.SEVERITY_WARNING,
                message="La narrativa usa «SHALL».",
                file=".venoxia/changes/c1/delta/checkout.md",
                line=9,
            )
        )
        self.payload = report.build_payload(self.result)

    # @covers R-VAL-002
    def test_payload_top_level_keys_are_exactly_the_schema(self):
        """El primer nivel trae las siete claves del esquema, ni una más ni una menos."""
        self.assertEqual(set(self.payload), set(SCHEMA_TOP_LEVEL_KEYS))

    def test_payload_version_is_one(self):
        """La versión del esquema publicado es 1, el entero, no la cadena."""
        self.assertEqual(self.payload["version"], 1)
        self.assertIs(type(self.payload["version"]), int)

    def test_counts_keys_are_exactly_the_schema(self):
        """«counts» trae exactamente error, warning, requirements, capabilities y deltas."""
        self.assertEqual(set(self.payload["counts"]), set(SCHEMA_COUNTS_KEYS))

    def test_budget_keys_are_exactly_the_schema(self):
        """«budget» trae exactamente low, total, ratio, limit y ok."""
        self.assertEqual(set(self.payload["budget"]), set(SCHEMA_BUDGET_KEYS))

    def test_every_finding_has_exactly_the_seven_schema_keys(self):
        """Cada hallazgo del JSON trae las siete claves del contrato, ni una más."""
        self.assertEqual(len(self.payload["findings"]), 2)
        for entry in self.payload["findings"]:
            with self.subTest(rule=entry.get("rule")):
                self.assertEqual(set(entry), set(SCHEMA_FINDING_KEYS))

    def test_render_json_keys_survive_the_serialisation(self):
        """Las claves del esquema siguen intactas después de serializar y reparsear."""
        reparsed = json.loads(report.render_json(self.result))
        self.assertEqual(set(reparsed), set(SCHEMA_TOP_LEVEL_KEYS))
        self.assertEqual(set(reparsed["counts"]), set(SCHEMA_COUNTS_KEYS))
        self.assertEqual(set(reparsed["budget"]), set(SCHEMA_BUDGET_KEYS))
        for entry in reparsed["findings"]:
            with self.subTest(rule=entry.get("rule")):
                self.assertEqual(set(entry), set(SCHEMA_FINDING_KEYS))

    def test_extra_adds_keys_without_removing_the_schema_ones(self):
        """El «extra» del contrato añade contexto propio sin borrar el esquema."""
        payload = report.build_payload(self.result, {"change": "c1"})
        self.assertEqual(payload["change"], "c1")
        self.assertTrue(SCHEMA_TOP_LEVEL_KEYS.issubset(set(payload)))


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


class TestJsonSchemaTypes(unittest.TestCase):
    """§4 · los tipos del documento JSON son los que espera quien lo consume."""

    def test_ok_and_strict_are_real_booleans(self):
        """«ok» y «strict» son booleanos de verdad, nunca 0 ni 1."""
        for strict, has_error in ((False, False), (True, True)):
            with self.subTest(strict=strict, has_error=has_error):
                result = model.ValidationResult(strict=strict)
                if has_error:
                    result.add(make_finding(file="a.md", line=1))
                payload = report.build_payload(result)
                self.assertIs(type(payload["ok"]), bool)
                self.assertIs(type(payload["strict"]), bool)

    def test_booleans_are_serialised_as_json_true_and_false(self):
        """En el texto JSON los booleanos salen como true/false, no como 1/0."""
        result = model.ValidationResult(strict=True)
        rendered = report.render_json(result)
        self.assertIn('"ok": true', rendered)
        self.assertIn('"strict": true', rendered)
        self.assertNotIn('"ok": 1', rendered)
        self.assertNotIn('"strict": 1', rendered)

    def test_line_is_an_integer_or_none(self):
        """«line» viaja como entero cuando lo hay y como null cuando no."""
        result = model.ValidationResult()
        result.add(make_finding(rule="V06", file="a.md", line=14))
        result.add(make_finding(rule="V11", file="", line=None))
        payload = report.build_payload(result)
        lines = {entry["rule"]: entry["line"] for entry in payload["findings"]}
        self.assertIs(type(lines["V06"]), int)
        self.assertEqual(lines["V06"], 14)
        self.assertIsNone(lines["V11"])

    def test_ratio_and_limit_are_numbers(self):
        """«ratio» y «limit» son números, no cadenas ni booleanos disfrazados."""
        budget = report.build_payload(result_with_confidence(low=1, total=12))["budget"]
        for key in ("ratio", "limit"):
            with self.subTest(key=key):
                self.assertIsInstance(budget[key], (int, float))
                self.assertNotIsInstance(budget[key], bool)

    def test_findings_is_a_list_even_when_empty(self):
        """«findings» es siempre una lista, también en el caso conforme."""
        payload = report.build_payload(model.ValidationResult())
        self.assertIsInstance(payload["findings"], list)
        self.assertEqual(payload["findings"], [])

    def test_counts_values_are_integers(self):
        """Todos los recuentos de «counts» son enteros."""
        payload = report.build_payload(result_with_confidence(low=1, total=12))
        for key, value in payload["counts"].items():
            with self.subTest(key=key):
                self.assertIs(type(value), int)


# ---------------------------------------------------------------------------
# Determinismo
# ---------------------------------------------------------------------------


class TestJsonDeterminism(unittest.TestCase):
    """§4 · el mismo resultado produce siempre el mismo documento."""

    def test_render_json_is_byte_identical_across_calls(self):
        """Dos llamadas sobre el mismo ValidationResult dan la misma cadena, byte a byte."""
        result = result_with_confidence(low=2, total=8)
        result.add(make_finding(rule="V06", file="b.md", line=3))
        result.add(make_finding(rule="V01", file="a.md", line=10))
        result.add(make_finding(rule="V11", file="", line=None))
        first = report.render_json(result)
        second = report.render_json(result)
        self.assertEqual(first, second)
        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))

    def test_render_json_is_reparseable(self):
        """La cadena que emite render_json la vuelve a leer json.loads sin quejarse."""
        result = result_with_confidence(low=1, total=4)
        result.add(
            make_finding(
                rule="V06",
                message=ACCENTED_MESSAGE,
                file="a.md",
                line=1,
                hint=ACCENTED_HINT,
            )
        )
        reparsed = json.loads(report.render_json(result))
        self.assertEqual(reparsed["findings"][0]["message"], ACCENTED_MESSAGE)
        self.assertEqual(reparsed["findings"][0]["hint"], ACCENTED_HINT)

    def test_scrambled_input_order_does_not_change_the_output(self):
        """Añadir los mismos hallazgos en otro orden produce el mismo JSON."""
        specs = [
            ("V06", "b.md", 3),
            ("V01", "a.md", 10),
            ("V04", "a.md", 2),
            ("V11", "", None),
        ]
        straight = model.ValidationResult()
        for rule, path, line in specs:
            straight.add(make_finding(rule=rule, file=path, line=line))
        reversed_result = model.ValidationResult()
        for rule, path, line in reversed(specs):
            reversed_result.add(make_finding(rule=rule, file=path, line=line))
        self.assertEqual(
            report.render_json(straight), report.render_json(reversed_result)
        )


# ---------------------------------------------------------------------------
# Orden de los hallazgos
# ---------------------------------------------------------------------------


class TestFindingOrder(unittest.TestCase):
    """§4 · los hallazgos salen ordenados por fichero, luego línea, luego regla."""

    #: Lista desordenada a propósito: ninguna de las tres claves de orden está
    #: ya colocada al construirla.
    SCRAMBLED = (
        ("V06", "b.md", 3),
        ("V02", "a.md", 10),
        ("V11", "", None),
        ("V04", "a.md", 2),
        ("V12", "a.md", None),
        ("V01", "a.md", 10),
        ("P01", "", None),
    )

    #: El orden que exige el contrato para SCRAMBLED.
    #:
    #: Dos decisiones quedan fijadas aquí, porque §4 no las deletrea y alguien
    #: tiene que dejarlas por escrito:
    #:
    #: 1. Los hallazgos de **ámbito global** —sin fichero, como V11, que mide el
    #:    presupuesto de incertidumbre sobre el ámbito entero— van **los
    #:    primeros**: su fichero vacío ordena antes que cualquier nombre.
    #: 2. Un hallazgo **con fichero pero sin línea** (V12, que habla del fichero
    #:    de delta completo) va **el primero de su fichero**, antes de la línea 1.
    EXPECTED = ("P01", "V11", "V12", "V04", "V01", "V02", "V06")

    def build(self) -> model.ValidationResult:
        """Un resultado con los hallazgos de SCRAMBLED, en su orden desordenado."""
        result = model.ValidationResult()
        for rule, path, line in self.SCRAMBLED:
            result.add(make_finding(rule=rule, file=path, line=line))
        return result

    def rules_in_payload(self) -> list[str]:
        """Los códigos de regla del payload, en el orden en que salen."""
        payload = report.build_payload(self.build())
        return [entry["rule"] for entry in payload["findings"]]

    def test_findings_are_sorted_by_file_then_line_then_rule(self):
        """El orden completo es fichero, luego línea, luego código de regla."""
        self.assertEqual(self.rules_in_payload(), list(self.EXPECTED))

    def test_global_findings_without_file_come_first(self):
        """Los hallazgos de ámbito global (sin fichero, como V11) abren la lista."""
        rules = self.rules_in_payload()
        self.assertEqual(rules[:2], ["P01", "V11"])
        self.assertNotIn("a.md", "".join(rules[:2]))

    def test_a_finding_without_line_opens_its_own_file(self):
        """Sin línea, el hallazgo va el primero de su fichero, antes de la línea 1."""
        rules = self.rules_in_payload()
        self.assertLess(rules.index("V12"), rules.index("V04"))

    def test_rule_code_breaks_the_tie_on_the_same_file_and_line(self):
        """Con mismo fichero y misma línea, decide el código de regla."""
        rules = self.rules_in_payload()
        self.assertLess(rules.index("V01"), rules.index("V02"))

    def test_the_input_order_is_really_scrambled(self):
        """Guardián del propio test: la entrada no viene ya ordenada por casualidad."""
        self.assertNotEqual(
            [rule for rule, _, _ in self.SCRAMBLED], list(self.EXPECTED)
        )

    def test_text_report_follows_the_same_order_inside_each_group(self):
        """El informe de texto respeta el mismo orden dentro de cada severidad."""
        result = model.ValidationResult()
        result.add(make_finding(rule="V06", file="b.md", line=3))
        result.add(make_finding(rule="V04", file="a.md", line=2))
        result.add(make_finding(rule="V11", file="", line=None))
        text = report.render_text(result, no_color=True)
        self.assertLess(text.index("V11"), text.index("V04"))
        self.assertLess(text.index("V04"), text.index("V06"))


# ---------------------------------------------------------------------------
# ensure_ascii=False
# ---------------------------------------------------------------------------


class TestJsonUnicode(unittest.TestCase):
    """§4 · el JSON sale en UTF-8 legible, no en escapes \\uXXXX."""

    def setUp(self) -> None:
        self.result = model.ValidationResult()
        self.result.add(
            make_finding(
                rule="V10",
                message=ACCENTED_MESSAGE,
                file=".venoxia/changes/c1/delta/checkout.md",
                line=14,
                requirement_id="R-CHK-014",
                hint=ACCENTED_HINT,
            )
        )
        self.rendered = report.render_json(self.result)

    def test_accented_characters_stay_literal(self):
        """Las letras acentuadas y la eñe aparecen tal cual en la cadena JSON."""
        for character in ("ó", "ñ", "«", "»"):
            with self.subTest(character=character):
                self.assertIn(character, self.rendered)

    def test_no_unicode_escapes_leak_into_the_output(self):
        """Ni «ó» ni «ñ» ni las comillas angulares salen escapadas como \\uXXXX."""
        for escape in ("\\u00f3", "\\u00F3", "\\u00f1", "\\u00ab", "\\u00bb"):
            with self.subTest(escape=escape):
                self.assertNotIn(escape, self.rendered)

    def test_the_message_survives_the_round_trip(self):
        """El mensaje reparseado es idéntico, carácter a carácter, al original."""
        reparsed = json.loads(self.rendered)
        self.assertEqual(reparsed["findings"][0]["message"], ACCENTED_MESSAGE)


# ---------------------------------------------------------------------------
# Presupuesto de incertidumbre
# ---------------------------------------------------------------------------


class TestUncertaintyBudget(unittest.TestCase):
    """§4 y §5 · el presupuesto que viaja en el payload y su frontera."""

    def test_zero_requirements_gives_ratio_zero_and_passes(self):
        """Sin requisitos no hay apuesta que medir: ratio 0 y presupuesto cumplido."""
        budget = report.build_payload(result_with_confidence(low=0, total=0))["budget"]
        self.assertEqual(budget["total"], 0)
        self.assertEqual(budget["low"], 0)
        self.assertEqual(budget["ratio"], 0.0)
        self.assertIs(budget["ok"], True)

    def test_exactly_thirty_percent_is_within_the_budget(self):
        """La frontera del contrato: con ratio exactamente 0.30, el presupuesto pasa."""
        budget = report.build_payload(result_with_confidence(low=3, total=10))["budget"]
        self.assertEqual(budget["ratio"], 0.30)
        self.assertEqual(budget["limit"], 0.30)
        self.assertIs(budget["ok"], True)

    def test_forty_percent_exceeds_the_budget(self):
        """Con ratio 0.4 el presupuesto se excede y «ok» es falso."""
        budget = report.build_payload(result_with_confidence(low=4, total=10))["budget"]
        self.assertEqual(budget["ratio"], 0.4)
        self.assertIs(budget["ok"], False)

    def test_just_over_the_limit_already_fails(self):
        """Un solo «low» de más sobre el límite ya rompe el presupuesto."""
        budget = report.build_payload(result_with_confidence(low=4, total=13))["budget"]
        self.assertIs(budget["ok"], False)

    def test_budget_ok_is_a_real_boolean(self):
        """«budget.ok» es un booleano de verdad, no un 1 ni un 0."""
        budget = report.build_payload(result_with_confidence(low=3, total=10))["budget"]
        self.assertIs(type(budget["ok"]), bool)

    def test_the_letter_case_of_the_level_is_literal(self):
        """«LOW» no es una apuesta declarada: el nivel se compara tal cual.

        Es el criterio que `V09` exige y el que `V11` aplica. Cuando el informe
        minusculaba por su cuenta, el mismo «LOW» contaba como apuesta aquí y no
        contaba en la regla, y el cierre podía anunciar un presupuesto excedido
        que ninguna regla respaldaba.
        """
        for level in ("LOW", "Low", " low "):
            with self.subTest(confidence=level):
                requirement = make_requirement(1, level)
                budget = report.uncertainty_budget([requirement])
                expected = 1 if level.strip() == "low" else 0
                self.assertEqual(budget["low"], expected, level)
                self.assertEqual(budget["total"], 1)

    def test_the_payload_budget_comes_from_the_shared_function(self):
        """El campo `budget` del JSON es literalmente lo que devuelve la función.

        Aquí se comprueba el lado del informe; que `V11` consuma esta misma
        cuenta —y que el texto, el JSON y la regla no puedan discrepar— lo fija
        `TestBudgetHasASingleSourceOfTruth` en `tests/test_rules_late.py`.
        """
        requirements = [
            make_requirement(1, "low"),
            make_requirement(2, "LOW"),
            make_requirement(3, "high"),
            make_requirement(4, "low"),
        ]
        result = model.ValidationResult(
            capabilities=[make_capability("checkout", requirements)]
        )
        payload = report.build_payload(result)["budget"]
        self.assertEqual(payload, report.uncertainty_budget(requirements))
        self.assertEqual(payload["low"], 2)

    def test_budget_counts_requirements_from_capabilities_and_deltas(self):
        """El presupuesto suma los requisitos de las capabilities y los de los deltas."""
        capability = make_capability("checkout", [make_requirement(1, "low")])
        delta = model.Delta(
            capability="checkout",
            path=".venoxia/changes/c1/delta/checkout.md",
            blocks={"ADDED": [make_requirement(2, "high"), make_requirement(3, "high")]},
        )
        result = model.ValidationResult(capabilities=[capability], deltas=[delta])
        budget = report.build_payload(result)["budget"]
        self.assertEqual(budget["total"], 3)
        self.assertEqual(budget["low"], 1)


# ---------------------------------------------------------------------------
# Texto: color
# ---------------------------------------------------------------------------


class TestRenderTextColor(unittest.TestCase):
    """§4 · color sólo si nadie lo prohíbe y la salida es de verdad un terminal."""

    def build(self) -> model.ValidationResult:
        """Un resultado con un error y un aviso, para que haya algo que pintar."""
        result = model.ValidationResult()
        result.add(make_finding(rule="V06", file="a.md", line=1, hint="Arregla esto."))
        result.add(
            make_finding(
                rule="V14", severity=model.SEVERITY_WARNING, file="a.md", line=2
            )
        )
        return result

    def test_no_color_true_removes_every_ansi_sequence(self):
        """Con no_color=True no queda ni una secuencia ANSI, aunque haya terminal."""
        with unittest.mock.patch.object(sys, "stdout", FakeTTY()):
            text = report.render_text(self.build(), no_color=True)
        self.assertNotIn(ANSI_MARKER, text)

    def test_color_appears_when_stdout_really_is_a_tty(self):
        """Contraprueba: con un stdout que dice ser terminal, sí se pinta en color."""
        with unittest.mock.patch.object(sys, "stdout", FakeTTY()):
            text = report.render_text(self.build())
        self.assertIn(ANSI_MARKER, text)

    def test_no_color_when_stdout_is_not_a_tty_in_process(self):
        """Con un stdout que no es terminal, tampoco hay color aunque no se pida."""
        with unittest.mock.patch.object(sys, "stdout", io.StringIO()):
            text = report.render_text(self.build())
        self.assertNotIn(ANSI_MARKER, text)

    def test_no_ansi_when_the_output_is_a_pipe(self):
        """El caso de CI: informe por subproceso con la salida en tubería, sin ANSI."""
        with tempfile.TemporaryDirectory() as workdir:
            script = Path(workdir) / "print_report.py"
            script.write_text(
                _PIPE_PROBE.format(scripts=str(SCRIPTS_DIR)), encoding="utf-8"
            )
            environment = {
                "PATH": os.environ.get("PATH", ""),
                # Un $HOME de mentira: la suite no toca el del usuario.
                "HOME": workdir,
                # Sin .pyc dentro del repositorio durante la ejecución.
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8",
                # A propósito hostil: un entorno que invita a colorear. Aun así,
                # como la salida es una tubería, no debe salir ni un escape.
                "TERM": "xterm-256color",
                "CLICOLOR_FORCE": "1",
                "FORCE_COLOR": "1",
            }
            run = subprocess.run(
                [sys.executable, str(script)],
                cwd=workdir,
                env=environment,
                capture_output=True,
                text=True,
                timeout=RUN_TIMEOUT,
            )
        detail = f"salida={run.stdout!r} error={run.stderr!r}"
        self.assertEqual(run.returncode, 0, detail)
        self.assertIn("V06", run.stdout, detail)
        self.assertNotIn(ANSI_MARKER, run.stdout, detail)


# ---------------------------------------------------------------------------
# Texto: contenido
# ---------------------------------------------------------------------------


class TestRenderTextContent(unittest.TestCase):
    """§4 · el informe de texto agrupa, explica y cierra con el recuento."""

    def build(self) -> model.ValidationResult:
        """Dos errores y un aviso sobre doce requisitos en dos capabilities."""
        first = make_capability("checkout", [make_requirement(i) for i in range(1, 8)])
        second = make_capability("billing", [make_requirement(i) for i in range(8, 13)])
        result = model.ValidationResult(
            capabilities=[first, second], root="/abs/path"
        )
        result.add(
            make_finding(
                rule="V06",
                message=ACCENTED_MESSAGE,
                file=".venoxia/changes/c1/delta/checkout.md",
                line=14,
                requirement_id="R-CHK-014",
                hint=ACCENTED_HINT,
            )
        )
        result.add(
            make_finding(
                rule="V01",
                message="El identificador está duplicado.",
                file=".venoxia/changes/c1/delta/checkout.md",
                line=2,
            )
        )
        result.add(
            make_finding(
                rule="V14",
                severity=model.SEVERITY_WARNING,
                message="La narrativa usa «SHALL».",
                file=".venoxia/changes/c1/delta/checkout.md",
                line=9,
            )
        )
        return result

    def test_findings_are_grouped_by_severity(self):
        """Primero el bloque de errores con su recuento, después el de avisos."""
        text = report.render_text(self.build(), no_color=True)
        self.assertIn("Errores (2)", text)
        self.assertIn("Avisos (1)", text)
        self.assertLess(text.index("Errores (2)"), text.index("Avisos (1)"))

    def test_every_error_is_listed_before_any_warning(self):
        """Ningún aviso se cuela entre los errores."""
        text = report.render_text(self.build(), no_color=True)
        self.assertLess(text.index("V06"), text.index("V14"))
        self.assertLess(text.index("V01"), text.index("V14"))

    def test_the_header_line_names_rule_location_and_requirement(self):
        """La cabecera del hallazgo dice regla, fichero:línea y el ID del requisito."""
        text = report.render_text(self.build(), no_color=True)
        self.assertIn(
            "✗ V06  .venoxia/changes/c1/delta/checkout.md:14  R-CHK-014", text
        )

    def test_the_hint_is_shown_under_the_message(self):
        """El remedio va justo debajo del mensaje, con la flecha y la sangría."""
        text = report.render_text(self.build(), no_color=True)
        lines = text.splitlines()
        message_index = lines.index(f"      {ACCENTED_MESSAGE}")
        self.assertEqual(lines[message_index + 1], f"      → {ACCENTED_HINT}")

    def test_a_finding_without_hint_shows_no_arrow(self):
        """Sin remedio no se inventa una flecha vacía."""
        result = model.ValidationResult()
        result.add(make_finding(rule="V01", message="Sin remedio.", file="a.md", line=1))
        text = report.render_text(result, no_color=True)
        self.assertIn("Sin remedio.", text)
        self.assertNotIn("→", text)

    def test_the_summary_reads_exactly_as_the_contract_example(self):
        """El resumen es el del contrato: «2 errores, 1 aviso · 12 requisitos en 2 capabilities»."""
        text = report.render_text(self.build(), no_color=True)
        self.assertIn("2 errores, 1 aviso · 12 requisitos en 2 capabilities", text)

    def test_the_summary_pluralises_errors_and_warnings_in_spanish(self):
        """El recuento usa singular con uno y plural con cero o más de uno."""
        cases = (
            (0, 0, "0 errores, 0 avisos"),
            (1, 1, "1 error, 1 aviso"),
            (2, 3, "2 errores, 3 avisos"),
        )
        for errors, warnings, expected in cases:
            with self.subTest(errors=errors, warnings=warnings):
                result = model.ValidationResult()
                for index in range(errors):
                    result.add(make_finding(rule="V01", file="a.md", line=index + 1))
                for index in range(warnings):
                    result.add(
                        make_finding(
                            rule="V14",
                            severity=model.SEVERITY_WARNING,
                            file="b.md",
                            line=index + 1,
                        )
                    )
                self.assertIn(expected, report.render_text(result, no_color=True))

    def test_the_failure_verdict_closes_a_non_conforming_report(self):
        """Cuando no cumple, la última línea lo dice y manda volver a validar."""
        text = report.render_text(self.build(), no_color=True)
        self.assertTrue(
            text.splitlines()[-1].startswith("✗ La especificación incumple el contrato"),
            text.splitlines()[-1],
        )

    def test_the_budget_line_reports_the_limit_in_spanish(self):
        """El cierre incluye el presupuesto de incertidumbre con su límite del 30 %."""
        result = result_with_confidence(low=1, total=12)
        text = report.render_text(result, no_color=True)
        self.assertIn("Presupuesto de incertidumbre: 1 de 12 requisitos", text)
        self.assertIn("límite 30 %", text)

    def test_the_budget_line_agrees_with_itself_on_the_singular(self):
        """Con un solo requisito, la línea del presupuesto también dice «requisito».

        Interpolaba «requisitos» fijo mientras la línea de al lado concuerda con
        `_plural`, así que el mismo informe escribía «1 de 1 requisitos» y, justo
        debajo, «1 requisito». Probarlo sólo con doce era no mirar donde duele.
        """
        text = report.render_text(result_with_confidence(low=1, total=1), no_color=True)
        self.assertIn("Presupuesto de incertidumbre: 1 de 1 requisito en «low»", text)
        self.assertNotIn("1 de 1 requisitos", text)
        # Y la línea del recuento sigue diciendo lo mismo del mismo número.
        self.assertIn("1 requisito en 1 capability", text)

    def test_the_budget_line_keeps_the_plural_when_there_is_more_than_one(self):
        """Con más de uno, plural: el arreglo del singular no se lleva por delante."""
        text = report.render_text(result_with_confidence(low=1, total=2), no_color=True)
        self.assertIn("Presupuesto de incertidumbre: 1 de 2 requisitos en «low»", text)


# ---------------------------------------------------------------------------
# El caso conforme
# ---------------------------------------------------------------------------


class TestConformingResult(unittest.TestCase):
    """§4 · qué dice el informe cuando la especificación cumple."""

    def build(self) -> model.ValidationResult:
        """Un resultado sin hallazgos sobre doce requisitos sanos."""
        return result_with_confidence(low=1, total=12)

    def test_render_text_includes_the_success_line(self):
        """El informe conforme cierra con la línea verde de éxito."""
        text = report.render_text(self.build(), no_color=True)
        self.assertIn("✓ La especificación cumple el contrato.", text)

    def test_the_success_line_is_the_last_one(self):
        """La línea de éxito es la última: nada la tapa por debajo."""
        text = report.render_text(self.build(), no_color=True)
        self.assertEqual(
            text.splitlines()[-1], "✓ La especificación cumple el contrato."
        )

    def test_the_conforming_payload_is_ok(self):
        """En el caso conforme «ok» es verdadero y no hay hallazgos."""
        payload = report.build_payload(self.build())
        self.assertIs(payload["ok"], True)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["counts"]["error"], 0)

    def test_no_severity_headings_when_there_is_nothing_to_report(self):
        """Sin hallazgos no se imprimen encabezados de severidad vacíos."""
        text = report.render_text(self.build(), no_color=True)
        self.assertNotIn("Errores", text)
        self.assertNotIn("Avisos", text)

    def test_strict_mode_turns_a_warning_into_a_failure(self):
        """En modo estricto un solo aviso basta para que «ok» sea falso."""
        result = self.build()
        result.strict = True
        result.add(
            make_finding(
                rule="V14", severity=model.SEVERITY_WARNING, file="a.md", line=1
            )
        )
        payload = report.build_payload(result)
        self.assertIs(payload["ok"], False)
        self.assertIs(payload["strict"], True)
        self.assertIn(
            "modo estricto: los avisos cuentan", report.render_text(result, no_color=True)
        )


if __name__ == "__main__":
    unittest.main()
