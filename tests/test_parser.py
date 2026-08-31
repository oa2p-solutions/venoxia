#!/usr/bin/env python3
"""Suite del parser y del modelo de Venoxia — contrato §2 y §3.

Prueba `scripts/venoxia/parser.py` y `scripts/venoxia/model.py` contra la
gramática del contrato: el requisito canónico entero, los separadores del
encabezado, las viñetas, los metadatos, los bloques de código, los cuatro
hallazgos del parser (`P01`–`P04`), `parse_delta`, `parse_capability`,
`find_covers`, la promesa de que **el parser nunca lanza** y las dataclases del
modelo.

Todo se escribe con `unittest` de la stdlib: el proyecto es de cero dependencias
y aquí no hay `pytest` instalado. Nada de red, nada de `$HOME` real, nada de
escribir dentro del repositorio: los ficheros de prueba viven en
`tempfile.TemporaryDirectory`.

Las cuatro clases del final vigilan las reparaciones del parser, que es la parte
que más veces se ha equivocado:

* `TestContractDivergences`: los dos casos en los que el código no cumplía el
  contrato §3 —la sangría de un metadato y la prosa borrada por una clave
  desconocida—, ya arreglados y aquí como red de seguridad.
* `TestMetadataIndentationGuards`: lo que la sangría libre podría tragarse.
* `TestMetadataBlockRegion`: el bloque de metadatos entendido como **región** y
  no como líneas sueltas, que es lo que arregla las dos regresiones de la ronda
  anterior —el ejemplo alineado a mano que pisaba un metadato de verdad y la
  clave desconocida que se quedaba cruda en la narrativa—.
* `TestIndentedCodeFences`: la valla ``` sangrada cuatro columnas o más, que
  ahora blinda su contenido sin tragarse el resto del documento cuando va suelta.
* `TestOrphanFenceNeverHidesRequirements`: el peor fallo que ha tenido el
  plugin —una valla huérfana borraba los requisitos de detrás y el validador
  daba «✓ cumple el contrato» con exit 0— y las dos decisiones que lo cierran.
* `TestHiddenHeadingSafeguard`: el `P05`, la red que se pone debajo de todo lo
  anterior para que ningún «### » pueda dejar de ser requisito en silencio.
"""

from __future__ import annotations

import sys
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

# --------------------------------------------------------------------------
# sys.path: el mismo ajuste idempotente que hace `tests/conftest.py`, repetido
# aquí porque «python3 -m unittest» no carga conftest.py.
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from venoxia import model, parser  # noqa: E402  (el ajuste de sys.path va antes)


# --------------------------------------------------------------------------
# Andamio local: markdown de prueba y utilidades de fichero temporal
# --------------------------------------------------------------------------


def future_date(days: int = 60) -> str:
    """Fecha ISO futura calculada desde hoy, para que el fixture no caduque."""
    return (date.today() + timedelta(days=days)).isoformat()


#: El requisito canónico del contrato §3, letra por letra, con la única
#: variación de que «expires» se calcula desde hoy en vez de ser una constante.
#: Las líneas están numeradas en el comentario porque los tests las afirman.
CANONICAL_EXPIRES = future_date()
CANONICAL = (
    "### R-CHK-014 · Stock reservation on payment confirmation\n"          # 1
    "\n"                                                                    # 2
    "WHEN el cliente confirma el pago, el sistema SHALL reservar el stock de\n"  # 3
    "todas las líneas del pedido durante 15 minutos.\n"                    # 4
    "\n"                                                                    # 5
    "#### Scenario: Stock available on every line\n"                       # 6
    "- **WHEN** hay stock disponible en todas las líneas\n"                # 7
    "- **THEN** se crea la reserva con TTL de 15 minutos\n"                # 8
    "\n"                                                                    # 9
    "#### Scenario: Insufficient stock on one line\n"                      # 10
    "- **WHEN** falta stock en al menos una línea\n"                       # 11
    "- **THEN** responde 409 y no crea ninguna reserva\n"                  # 12
    "\n"                                                                    # 13
    "verifies:   test/checkout/reservation.spec.ts\n"                      # 14
    "confidence: medium\n"                                                 # 15
    "  why:      los 15 minutos son una apuesta, no un dato\n"             # 16
    "  expires:  " + CANONICAL_EXPIRES + "\n"                              # 17
    "from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar\n"       # 18
)

#: Entradas hostiles que el parser tiene que digerir sin lanzar. El contrato
#: §3 lo dice sin matices: «Nunca lanza excepción».
HOSTILE_INPUTS: tuple[tuple[str, str], ...] = (
    ("vacio", ""),
    ("solo_blancos", "   \n\t\t\n \n"),
    ("hash_suelto", "###"),
    ("hash_con_espacios", "###   \n###\n"),
    ("dos_puntos_suelto", ":"),
    ("dos_puntos_en_requisito", "### R-CHK-001 · Título\n:\n::\n"),
    ("valla_sin_cerrar", "### R-CHK-001 · Título\n```python\nprint('hola')\n"),
    ("valla_solo_cierre", "### R-CHK-001 · Título\ntexto\n```\n"),
    ("vallas_anidadas", "### R-CHK-001 · T\n````md\n```\n~~~\n```\n````\n~~~\n"),
    ("markdown_truncado", "### R-CHK-001 · Título\n\nWHEN el sistema SHA"),
    ("bullet_truncado", "#### Scenario: S\n- **WHE"),
    ("cinco_mil_sin_saltos", "x" * 5000),
    ("cinco_mil_tras_hash", "### " + "y" * 5000),
    ("bytes_nulos", "### R-CHK-001 · T\n\x00\x00\nverifies: a\x00b\n"),
    ("utf16_mal_descodificado", "### R-CHK-001 · T".encode("utf-16").decode("latin-1")),
    ("bom_al_principio", "\ufeff### R-CHK-001 · Título\n"),
    ("regla_horizontal_guiones", "---\n### R-CHK-001 · T\n---\n#### Scenario: S\n---\n"),
    ("regla_horizontal_asteriscos", "***\n*\n**\n### R-CHK-001 · T\n***\n"),
    ("encabezado_con_emoji", "### 🎯 R-CHK-001 · Título con emoji 🚀\n"),
    ("metadato_con_emoji", "### R-CHK-001 · T\n\nverifies: 🚀/a.spec.ts\n"),
    ("solo_metadatos", "verifies: a\nconfidence: low\nwhy: porque sí\n"),
    ("escenario_huerfano", "#### Scenario: sin requisito\n- **WHEN** a\n"),
    ("doscientas_almohadillas", "#" * 200 + " título\n"),
    ("surrogate_suelto", "### R-CHK-001 · T\n\udcff\n"),
    ("caracteres_de_control", "### R-CHK-001 · T\n\x01\x02\x1b[31mrojo\x1b[0m\n"),
    ("crlf", "### R-CHK-001 · T\r\n\r\nWHEN algo.\r\nverifies: a\r\n"),
    ("encabezados_encadenados", "### R-A-001 · ### R-A-002 · ### R-A-003 · x\n"),
)


class TempDirCase(unittest.TestCase):
    """Base para los tests que necesitan ficheros: un directorio temporal propio."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relpath: str, content: str) -> Path:
        """Escribe un fichero UTF-8 bajo el directorio temporal y devuelve su ruta."""
        target = self.root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def write_bytes(self, relpath: str, payload: bytes) -> Path:
        """Escribe bytes crudos bajo el directorio temporal y devuelve su ruta."""
        target = self.root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target


def parse_one(text: str, source_file: str = "delta/checkout.md"):
    """Parsea un markdown que contiene un solo requisito y lo devuelve con sus hallazgos."""
    requirements, findings = parser.parse_requirements(text, source_file=source_file)
    return requirements, findings


# --------------------------------------------------------------------------
# §3 · El requisito canónico, parseado entero
# --------------------------------------------------------------------------


class TestCanonicalRequirement(unittest.TestCase):
    """El ejemplo canónico del contrato §3 se parsea entero y sin hallazgos."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.requirements, cls.findings = parser.parse_requirements(
            CANONICAL, source_file="delta/checkout.md"
        )

    def test_canonical_yields_exactly_one_requirement(self):
        """El documento canónico contiene exactamente un requisito."""
        self.assertEqual(len(self.requirements), 1)

    def test_canonical_produces_no_findings(self):
        """El requisito canónico está bien formado: el parser no tiene nada que decir."""
        self.assertEqual([finding.rule for finding in self.findings], [])

    def test_canonical_header_splits_id_title_and_line(self):
        """El encabezado se reparte en id, título y número de línea 1-indexado."""
        requirement = self.requirements[0]
        self.assertEqual(requirement.id, "R-CHK-014")
        self.assertEqual(requirement.title, "Stock reservation on payment confirmation")
        self.assertEqual(requirement.line, 1)

    def test_canonical_keeps_raw_header(self):
        """`raw_header` conserva la línea del encabezado tal cual se escribió."""
        self.assertEqual(
            self.requirements[0].raw_header,
            "### R-CHK-014 · Stock reservation on payment confirmation",
        )

    def test_canonical_narrative_is_the_exact_prose(self):
        """La narrativa es la prosa entre el encabezado y el primer escenario, sin más."""
        self.assertEqual(
            self.requirements[0].narrative,
            "WHEN el cliente confirma el pago, el sistema SHALL reservar el stock de\n"
            "todas las líneas del pedido durante 15 minutos.",
        )

    def test_canonical_records_source_file(self):
        """El requisito recuerda de qué fichero viene, para los mensajes del informe."""
        self.assertEqual(self.requirements[0].source_file, "delta/checkout.md")

    def test_canonical_has_two_scenarios_with_their_titles_and_lines(self):
        """Los dos escenarios se reconocen con su título y su línea."""
        scenarios = self.requirements[0].scenarios
        self.assertEqual(
            [(scenario.title, scenario.line) for scenario in scenarios],
            [
                ("Stock available on every line", 6),
                ("Insufficient stock on one line", 10),
            ],
        )

    def test_canonical_first_scenario_bullets(self):
        """Las viñetas del primer escenario son pares (palabra clave, texto)."""
        self.assertEqual(
            self.requirements[0].scenarios[0].bullets,
            [
                ("WHEN", "hay stock disponible en todas las líneas"),
                ("THEN", "se crea la reserva con TTL de 15 minutos"),
            ],
        )

    def test_canonical_second_scenario_bullets(self):
        """Las viñetas del segundo escenario también se parean sin perder texto."""
        self.assertEqual(
            self.requirements[0].scenarios[1].bullets,
            [
                ("WHEN", "falta stock en al menos una línea"),
                ("THEN", "responde 409 y no crea ninguna reserva"),
            ],
        )

    def test_canonical_meta_has_the_five_keys(self):
        """Los cinco metadatos del contrato se recogen con su valor recortado."""
        self.assertEqual(
            self.requirements[0].meta,
            {
                "verifies": "test/checkout/reservation.spec.ts",
                "confidence": "medium",
                "why": "los 15 minutos son una apuesta, no un dato",
                "expires": CANONICAL_EXPIRES,
                "from": "prfaq/checkout-express.md#sin-sorpresas-al-pagar",
            },
        )

    def test_canonical_meta_lines_point_at_each_key(self):
        """`meta_lines` da la línea 1-indexada de cada metadato, para señalar el error."""
        self.assertEqual(
            self.requirements[0].meta_lines,
            {"verifies": 14, "confidence": 15, "why": 16, "expires": 17, "from": 18},
        )


# --------------------------------------------------------------------------
# §3 · Encabezado de requisito
# --------------------------------------------------------------------------


class TestRequirementHeader(unittest.TestCase):
    """Reparto del encabezado en id y título con los separadores del contrato."""

    def test_all_three_separators_split_id_and_title(self):
        """Los tres separadores del contrato («·», «-», «—») separan id y título."""
        for separator in ("·", "-", "—"):
            with self.subTest(separator=separator):
                requirements, findings = parse_one(
                    "### R-CHK-014 " + separator + " Reserva de stock\n"
                )
                self.assertEqual(len(requirements), 1)
                self.assertEqual(requirements[0].id, "R-CHK-014")
                self.assertEqual(requirements[0].title, "Reserva de stock")
                self.assertEqual(findings, [])

    def test_middle_dot_without_surrounding_spaces_still_splits(self):
        """El «·» separa aunque no lleve espacios alrededor."""
        requirements, _ = parse_one("### R-CHK-014·Reserva de stock\n")
        self.assertEqual(requirements[0].id, "R-CHK-014")
        self.assertEqual(requirements[0].title, "Reserva de stock")

    def test_header_without_separator_is_all_title(self):
        """Sin separador no hay id: el encabezado entero es el título."""
        requirements, _ = parse_one("### Reserva de stock al confirmar el pago\n")
        self.assertIsNone(requirements[0].id)
        self.assertEqual(requirements[0].title, "Reserva de stock al confirmar el pago")

    def test_bare_id_header_is_not_split_into_id_and_number(self):
        """«### R-CHK-014» sin título no se parte en «R-CHK» + «014»."""
        requirements, _ = parse_one("### R-CHK-014\n")
        self.assertEqual(len(requirements), 1)
        self.assertIsNone(requirements[0].id)
        self.assertEqual(requirements[0].title, "R-CHK-014")

    def test_hyphen_glued_to_title_is_not_a_separator(self):
        """El guion sin espacios no separa: pertenece al propio identificador."""
        requirements, _ = parse_one("### R-CHK-014-Reserva\n")
        self.assertIsNone(requirements[0].id)
        self.assertEqual(requirements[0].title, "R-CHK-014-Reserva")

    def test_id_is_stored_verbatim_even_when_malformed(self):
        """El id se guarda tal cual: juzgar su forma es cosa de V01, no del parser."""
        requirements, _ = parse_one("### R-CHECKOUT-14 · Título\n")
        self.assertEqual(requirements[0].id, "R-CHECKOUT-14")

    def test_scenario_heading_is_not_a_requirement_header(self):
        """«#### Scenario:» no abre un requisito, aunque empiece por almohadillas."""
        requirements, _ = parse_one("#### Scenario: no soy un requisito\n")
        self.assertEqual(requirements, [])

    def test_second_level_heading_closes_the_previous_requirement(self):
        """Un encabezado de nivel 2 cierra el requisito anterior."""
        requirements, _ = parse_one(
            "### R-CHK-001 · Uno\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "## Otra sección\n"
            "\n"
            "Esta prosa ya no es del requisito.\n"
        )
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")


# --------------------------------------------------------------------------
# §2 y §3 · Escenarios y viñetas
# --------------------------------------------------------------------------


class TestScenariosAndBullets(unittest.TestCase):
    """Viñetas de escenario: marcas admitidas, normalización y helpers del modelo."""

    def test_both_bullet_markers_are_accepted(self):
        """La viñeta puede empezar por «-» o por «*»."""
        for marker in ("-", "*"):
            with self.subTest(marker=marker):
                requirements, findings = parse_one(
                    "### R-CHK-001 · T\n"
                    "\n"
                    "WHEN algo.\n"
                    "\n"
                    "#### Scenario: S\n"
                    + marker + " **WHEN** hay stock\n"
                    + marker + " **THEN** se reserva\n"
                )
                self.assertEqual(
                    requirements[0].scenarios[0].bullets,
                    [("WHEN", "hay stock"), ("THEN", "se reserva")],
                )
                self.assertEqual(findings, [])

    def test_indented_bullet_is_accepted(self):
        """La sangría por delante de la viñeta no impide reconocerla."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "#### Scenario: S\n"
            "    - **WHEN** hay stock\n"
            "\t- **THEN** se reserva\n"
        )
        self.assertEqual(
            requirements[0].scenarios[0].bullets,
            [("WHEN", "hay stock"), ("THEN", "se reserva")],
        )
        self.assertEqual(findings, [])

    def test_bullet_without_text_keeps_an_empty_string(self):
        """Una viñeta sin texto sigue siendo viñeta: la palabra clave cuenta."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n\nWHEN algo.\n\n#### Scenario: S\n- **WHEN**\n"
        )
        self.assertEqual(requirements[0].scenarios[0].bullets, [("WHEN", "")])

    def test_keywords_are_normalized_to_uppercase(self):
        """`Scenario.keywords()` devuelve las palabras clave en mayúsculas."""
        scenario = model.Scenario(
            title="S", line=1, bullets=[("when", "a"), ("Then", "b"), ("AND", "c")]
        )
        self.assertEqual(scenario.keywords(), {"WHEN", "THEN", "AND"})

    def test_has_ignores_case_of_the_asked_keyword(self):
        """`Scenario.has()` no distingue mayúsculas ni en la viñeta ni en la pregunta."""
        scenario = model.Scenario(title="S", line=1, bullets=[("WHEN", "a")])
        for asked in ("WHEN", "when", " When "):
            with self.subTest(asked=asked):
                self.assertTrue(scenario.has(asked))

    def test_has_is_false_for_a_missing_keyword(self):
        """`Scenario.has()` dice que no cuando la palabra clave no está."""
        scenario = model.Scenario(title="S", line=1, bullets=[("WHEN", "a")])
        self.assertFalse(scenario.has("THEN"))

    def test_keywords_of_a_scenario_without_bullets_is_empty(self):
        """Un escenario sin viñetas no declara ninguna palabra clave."""
        self.assertEqual(model.Scenario(title="S", line=1).keywords(), set())

    def test_parsed_bullet_keyword_is_uppercase(self):
        """La palabra clave que sale del markdown llega en mayúsculas al modelo."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n\nWHEN algo.\n\n#### Scenario: S\n- **WHEN** a\n"
        )
        self.assertEqual(requirements[0].scenarios[0].keywords(), {"WHEN"})


# --------------------------------------------------------------------------
# §3 · Metadatos
# --------------------------------------------------------------------------


class TestMetadata(unittest.TestCase):
    """Bloque de metadatos: posición, sangría cosmética y falsos positivos."""

    def test_metadata_before_the_scenarios_is_accepted(self):
        """Los metadatos escritos antes de los escenarios se aceptan igual."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "verifies: test/a.spec.ts\n"
            "confidence: high\n"
            "from: prfaq/x.md#sección\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "#### Scenario: S\n"
            "- **WHEN** a\n"
            "- **THEN** b\n"
        )
        self.assertEqual(
            requirements[0].meta,
            {
                "verifies": "test/a.spec.ts",
                "confidence": "high",
                "from": "prfaq/x.md#sección",
            },
        )
        self.assertEqual(findings, [])

    def test_metadata_before_the_scenarios_is_not_narrative(self):
        """Un metadato adelantado no contamina la narrativa."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "verifies: test/a.spec.ts\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "#### Scenario: S\n"
            "- **WHEN** a\n"
        )
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")

    def test_metadata_before_scenarios_records_its_real_line(self):
        """La línea del metadato adelantado es la suya, no la del final del requisito."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\nverifies: test/a.spec.ts\n\nWHEN algo.\n"
        )
        self.assertEqual(requirements[0].meta_lines["verifies"], 2)

    def test_metadata_after_the_scenarios_is_accepted(self):
        """Los metadatos escritos tras los escenarios son la posición canónica."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "#### Scenario: S\n"
            "- **WHEN** a\n"
            "- **THEN** b\n"
            "\n"
            "verifies: test/a.spec.ts\n"
            "confidence: high\n"
        )
        self.assertEqual(
            requirements[0].meta, {"verifies": "test/a.spec.ts", "confidence": "high"}
        )
        self.assertEqual(findings, [])

    def test_cosmetic_indentation_of_why_and_expires_is_ignored(self):
        """La sangría de «why» y «expires» es cosmética: se ignora al leerlas."""
        expires = future_date(90)
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "confidence: low\n"
            "  why:      la cifra es una apuesta\n"
            "  expires:  " + expires + "\n"
        )
        self.assertEqual(
            requirements[0].meta,
            {"confidence": "low", "why": "la cifra es una apuesta", "expires": expires},
        )
        self.assertEqual(findings, [])

    def test_indented_metadata_is_not_left_inside_the_narrative(self):
        """El metadato sangrado sale de la narrativa, no se queda como prosa."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "confidence: low\n"
            "    why: la cifra es una apuesta\n"
        )
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")

    def test_extra_spaces_around_the_value_are_trimmed(self):
        """El valor del metadato llega sin los espacios de alineación."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n\nWHEN algo.\n\nverifies:      test/a.spec.ts   \n"
        )
        self.assertEqual(requirements[0].meta["verifies"], "test/a.spec.ts")

    def test_empty_metadata_value_is_kept_as_empty_string(self):
        """Un «verifies:» sin valor se guarda vacío para que V06 pueda quejarse."""
        requirements, _ = parse_one("### R-CHK-001 · T\n\nWHEN algo.\n\nverifies:\n")
        self.assertEqual(requirements[0].meta["verifies"], "")

    def test_https_url_in_the_narrative_is_not_swallowed_as_metadata(self):
        """Una URL «https://» al principio de línea no es un metadato."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN el cliente paga, el sistema consulta el catálogo.\n"
            "https://example.com/docs/checkout describe el contrato.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(
            requirements[0].narrative,
            "WHEN el cliente paga, el sistema consulta el catálogo.\n"
            "https://example.com/docs/checkout describe el contrato.",
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])

    def test_a_requirement_without_metadata_has_empty_dicts(self):
        """Sin metadatos, `meta` y `meta_lines` quedan vacíos, no a `None`."""
        requirements, _ = parse_one("### R-CHK-001 · T\n\nWHEN algo.\n")
        self.assertEqual(requirements[0].meta, {})
        self.assertEqual(requirements[0].meta_lines, {})


# --------------------------------------------------------------------------
# §3 · Bloques de código en la narrativa
# --------------------------------------------------------------------------


FENCED = (
    "### R-CHK-020 · Requisito con ejemplo de código\n"
    "\n"
    "WHEN el cliente pide el estado, el sistema devuelve este documento:\n"
    "\n"
    "```markdown\n"
    "### R-FAKE-999 · No soy un requisito\n"
    "verifies: mentira.spec.ts\n"
    "- **WHEN** tampoco soy una viñeta\n"
    "```\n"
    "\n"
    "verifies: test/checkout/estado.spec.ts\n"
    "confidence: high\n"
)


class TestCodeFences(unittest.TestCase):
    """Nada de lo que hay dentro de una valla ``` se interpreta como gramática."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.requirements, cls.findings = parser.parse_requirements(
            FENCED, source_file="delta/checkout.md"
        )

    def test_fenced_document_yields_a_single_requirement(self):
        """El «### R-FAKE-999» de dentro de la valla no abre un segundo requisito."""
        self.assertEqual([r.id for r in self.requirements], ["R-CHK-020"])

    def test_fenced_metadata_is_not_read(self):
        """El «verifies:» de dentro de la valla no pisa el metadato real."""
        self.assertEqual(
            self.requirements[0].meta,
            {"verifies": "test/checkout/estado.spec.ts", "confidence": "high"},
        )

    def test_fenced_bullet_creates_no_scenario_and_only_the_heading_warns(self):
        """La viñeta de dentro de la valla ni crea escenario ni genera un P04.

        El único hallazgo es el `P05` de la salvaguarda: el «### R-FAKE-999» del
        ejemplo no se ha convertido en requisito y eso se anuncia siempre. Desde
        fuera, un encabezado de ejemplo y un requisito que una valla se ha
        tragado se escriben igual; callarse el segundo cuesta un falso verde, y
        avisar del primero cuesta un aviso.
        """
        self.assertEqual(self.requirements[0].scenarios, [])
        self.assertEqual([finding.rule for finding in self.findings], ["P05"])
        self.assertEqual(self.findings[0].line, 6)

    def test_fenced_code_is_preserved_verbatim_in_the_narrative(self):
        """El bloque de código se conserva literal dentro de la narrativa."""
        self.assertEqual(
            self.requirements[0].narrative,
            "WHEN el cliente pide el estado, el sistema devuelve este documento:\n"
            "\n"
            "```markdown\n"
            "### R-FAKE-999 · No soy un requisito\n"
            "verifies: mentira.spec.ts\n"
            "- **WHEN** tampoco soy una viñeta\n"
            "```",
        )

    def test_an_unclosed_fence_does_not_swallow_a_requirement_heading(self):
        """Una valla sin cerrar llega hasta el siguiente «### », y ahí se para.

        Antes se tragaba el resto del documento, y con él todos los requisitos
        que vinieran detrás: el parser dejaba de verlos y ninguna regla podía
        quejarse de lo que no veía. Eso es un falso verde. Ahora el descuido
        cuesta la cola del requisito en curso —su `verifies:` se pierde y V06 lo
        canta— pero nunca el requisito siguiente.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "```\n"
            "texto que la valla se traga\n"
            "verifies: mentira.spec.ts\n"
            "\n"
            "### R-CHK-002 · Sobrevivo a la valla huérfana\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "verifies: test/b.spec.ts\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001", "R-CHK-002"])
        self.assertEqual(requirements[0].meta, {})
        self.assertEqual(requirements[1].meta, {"verifies": "test/b.spec.ts"})
        self.assertEqual(requirements[1].narrative, "WHEN algo, el sistema responde.")
        self.assertEqual(findings, [])

    def test_an_unclosed_fence_stops_at_a_block_heading_too(self):
        """El «## ADDED Requirements» de un delta también corta la valla huérfana."""
        requirements, findings = parse_one(
            "## ADDED Requirements\n"
            "\n"
            "### R-CHK-001 · T\n"
            "\n"
            "```\n"
            "sin cerrar\n"
            "\n"
            "## MODIFIED Requirements\n"
            "\n"
            "### R-CHK-002 · Sobrevivo\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001", "R-CHK-002"])
        self.assertEqual(requirements[1].block, "MODIFIED")
        self.assertEqual(findings, [])

    def test_nested_fences_do_not_close_the_outer_one(self):
        """Una valla de tres acentos dentro de otra de cuatro no la cierra."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "````md\n"
            "```\n"
            "### R-FAKE-001 · dentro\n"
            "```\n"
            "````\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001"])
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})


# --------------------------------------------------------------------------
# §3 · Los cuatro hallazgos del parser
# --------------------------------------------------------------------------


class TestReadTextFindings(TempDirCase):
    """`P01`: todo fichero que no se puede leer devuelve texto `None` y un error."""

    def assert_p01(self, finding, path: Path):
        """Comprueba la forma de un hallazgo `P01`."""
        self.assertIsNotNone(finding)
        self.assertEqual(finding.rule, "P01")
        self.assertEqual(finding.severity, model.SEVERITY_ERROR)
        self.assertEqual(finding.severity, "error")
        self.assertIn(str(path), finding.message)
        self.assertTrue(finding.hint)

    def test_p01_when_the_file_does_not_exist(self):
        """Un fichero inexistente devuelve `(None, P01)` en vez de lanzar."""
        missing = self.root / "no-existe.md"
        text, finding = parser.read_text(missing)
        self.assertIsNone(text)
        self.assert_p01(finding, missing)

    def test_p01_when_the_path_is_a_directory(self):
        """Un directorio en lugar de un fichero devuelve `P01`."""
        directory = self.root / "capabilities"
        directory.mkdir()
        text, finding = parser.read_text(directory)
        self.assertIsNone(text)
        self.assert_p01(finding, directory)

    def test_p01_when_the_file_is_binary(self):
        """Un fichero con bytes nulos se rechaza como binario, sin descodificar."""
        binary = self.write_bytes("binario.md", b"### R-CHK-001 \x00\x01\x02 basura")
        text, finding = parser.read_text(binary)
        self.assertIsNone(text)
        self.assert_p01(finding, binary)

    def test_p01_when_the_file_is_not_utf8(self):
        """Un fichero en latin-1 no se descodifica: devuelve `P01`, no una traza."""
        latin = self.write_bytes("latin.md", b"### R-CHK-001 \xb7 T\xedtulo con acento\n")
        text, finding = parser.read_text(latin)
        self.assertIsNone(text)
        self.assert_p01(finding, latin)

    def test_p01_when_the_file_is_utf16(self):
        """Un fichero en UTF-16 tampoco se lee: `P01` y ninguna excepción."""
        utf16 = self.write_bytes("utf16.md", CANONICAL.encode("utf-16"))
        text, finding = parser.read_text(utf16)
        self.assertIsNone(text)
        self.assert_p01(finding, utf16)

    def test_read_text_returns_the_content_and_no_finding_on_success(self):
        """Un fichero UTF-8 correcto devuelve su texto y ningún hallazgo."""
        good = self.write("bien.md", CANONICAL)
        text, finding = parser.read_text(good)
        self.assertEqual(text, CANONICAL)
        self.assertIsNone(finding)

    def test_read_text_drops_the_byte_order_mark(self):
        """La marca de orden de bytes se descarta al leer."""
        good = self.write_bytes("bom.md", "\ufeff### R-CHK-001 · T\n".encode("utf-8"))
        text, finding = parser.read_text(good)
        self.assertEqual(text, "### R-CHK-001 · T\n")
        self.assertIsNone(finding)

    def test_p01_from_parse_delta_uses_the_relative_path(self):
        """El `P01` de un delta ilegible se reporta con la ruta relativa a la raíz."""
        delta, findings = parser.parse_delta(
            self.root / ".venoxia" / "changes" / "c1" / "delta" / "checkout.md",
            root=self.root,
        )
        self.assertEqual([finding.rule for finding in findings], ["P01"])
        self.assertEqual(findings[0].file, ".venoxia/changes/c1/delta/checkout.md")
        self.assertEqual(delta.blocks, {})

    def test_p01_from_parse_capability_returns_an_empty_capability(self):
        """El `P01` de una capability ilegible devuelve la capability vacía."""
        capability, findings = parser.parse_capability(
            self.root / ".venoxia" / "capabilities" / "checkout" / "spec.md",
            root=self.root,
        )
        self.assertEqual([finding.rule for finding in findings], ["P01"])
        self.assertEqual(capability.name, "checkout")
        self.assertEqual(capability.requirements, [])


class TestMetadataFindings(unittest.TestCase):
    """`P02`, `P03` y `P04`: los avisos de forma que emite el parser."""

    def test_p02_for_an_unknown_metadata_key(self):
        """Una clave de metadatos desconocida produce un aviso `P02`."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
            "owner: el equipo de checkout\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P02"])
        finding = findings[0]
        self.assertEqual(finding.severity, model.SEVERITY_WARNING)
        self.assertEqual(finding.line, 6)
        self.assertEqual(finding.file, "delta/checkout.md")
        self.assertEqual(finding.requirement_id, "R-CHK-001")
        self.assertIn("owner", finding.message)
        self.assertNotIn("owner", requirements[0].meta)

    def test_p02_is_not_raised_for_the_five_known_keys(self):
        """Ninguna de las cinco claves del contrato genera un aviso."""
        for key in model.META_KEYS:
            with self.subTest(key=key):
                _, findings = parse_one(
                    "### R-CHK-001 · T\n\nWHEN algo.\n\n" + key + ": valor\n"
                )
                self.assertEqual(findings, [])

    def test_p03_for_a_repeated_metadata_key(self):
        """Una clave repetida produce un aviso `P03`."""
        _, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "verifies: test/primero.spec.ts\n"
            "verifies: test/ultimo.spec.ts\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P03"])
        self.assertEqual(findings[0].severity, model.SEVERITY_WARNING)
        self.assertEqual(findings[0].line, 6)
        self.assertIn("verifies", findings[0].message)

    def test_p03_keeps_the_last_value(self):
        """Con la clave repetida gana la última aparición."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "verifies: test/primero.spec.ts\n"
            "verifies: test/ultimo.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta["verifies"], "test/ultimo.spec.ts")
        self.assertEqual(requirements[0].meta_lines["verifies"], 6)

    def test_p04_for_a_malformed_bullet_inside_a_scenario(self):
        """Una viñeta que no encaja en «- **PALABRA** texto» produce un `P04`."""
        _, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "#### Scenario: Hay stock\n"
            "- **WHEN** hay stock\n"
            "- esto no lleva palabra clave\n"
            "- **THEN** se reserva\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P04"])
        finding = findings[0]
        self.assertEqual(finding.severity, model.SEVERITY_WARNING)
        self.assertEqual(finding.line, 7)
        self.assertEqual(finding.requirement_id, "R-CHK-001")
        self.assertIn("Hay stock", finding.message)

    def test_p04_does_not_lose_the_well_formed_bullets(self):
        """El `P04` avisa de la viñeta rota sin perder las que sí están bien."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo.\n"
            "\n"
            "#### Scenario: S\n"
            "- **WHEN** hay stock\n"
            "- esto no lleva palabra clave\n"
            "- **THEN** se reserva\n"
        )
        self.assertEqual(
            requirements[0].scenarios[0].bullets,
            [("WHEN", "hay stock"), ("THEN", "se reserva")],
        )

    def test_horizontal_rules_inside_a_scenario_are_not_bullets(self):
        """Las reglas horizontales «---» y «***» no se confunden con viñetas."""
        for rule in ("---", "***", "___"):
            with self.subTest(rule=rule):
                _, findings = parse_one(
                    "### R-CHK-001 · T\n"
                    "\n"
                    "WHEN algo.\n"
                    "\n"
                    "#### Scenario: S\n"
                    "- **WHEN** a\n"
                    + rule + "\n"
                )
                self.assertEqual(findings, [])

    def test_a_document_without_requirements_produces_no_findings(self):
        """Un fichero sin ningún «### » da cero requisitos y ningún hallazgo."""
        requirements, findings = parse_one(
            "# Capability de checkout\n\n## Purpose\n\nQue pagar no dé sorpresas.\n"
        )
        self.assertEqual(requirements, [])
        self.assertEqual(findings, [])


# --------------------------------------------------------------------------
# §3 · parse_delta
# --------------------------------------------------------------------------


DELTA_MARKDOWN = (
    "# Delta de checkout\n"
    "\n"
    "## ADDED Requirements\n"
    "\n"
    "### R-CHK-001 · Uno\n"
    "\n"
    "WHEN a, el sistema responde.\n"
    "\n"
    "## MODIFIED requirements\n"
    "\n"
    "### R-CHK-002 · Dos\n"
    "\n"
    "WHEN b, el sistema responde.\n"
    "\n"
    "## REMOVED REQUIREMENTS\n"
    "\n"
    "### R-CHK-003 · Tres\n"
    "\n"
    "WHEN c, el sistema responde.\n"
    "\n"
    "## RENAMED Requirements\n"
)


class TestParseDelta(TempDirCase):
    """Un delta agrupa sus requisitos por bloque y recuerda los bloques vacíos."""

    def setUp(self) -> None:
        super().setUp()
        self.path = self.write(
            ".venoxia/changes/2026-01-01-checkout/delta/checkout.md", DELTA_MARKDOWN
        )
        self.delta, self.findings = parser.parse_delta(self.path, root=self.root)

    def test_delta_declares_the_four_block_names(self):
        """Los cuatro nombres de bloque del contrato se reconocen."""
        self.assertEqual(set(self.delta.blocks), set(model.BLOCK_NAMES))

    def test_requirements_land_in_their_own_block(self):
        """Cada requisito queda en el bloque que lo precede."""
        self.assertEqual(
            {name: [r.id for r in reqs] for name, reqs in self.delta.blocks.items()},
            {
                "ADDED": ["R-CHK-001"],
                "MODIFIED": ["R-CHK-002"],
                "REMOVED": ["R-CHK-003"],
                "RENAMED": [],
            },
        )

    def test_block_word_requirements_is_case_insensitive(self):
        """La palabra «Requirements» del encabezado de bloque no distingue mayúsculas."""
        self.assertIn("MODIFIED", self.delta.blocks)
        self.assertIn("REMOVED", self.delta.blocks)

    def test_each_requirement_remembers_its_block(self):
        """El requisito guarda el nombre de su bloque en mayúsculas."""
        self.assertEqual(
            [r.block for r in self.delta.requirements], ["ADDED", "MODIFIED", "REMOVED"]
        )

    def test_a_declared_but_empty_block_is_kept(self):
        """Un bloque declarado y vacío existe en `blocks` con la lista vacía."""
        self.assertEqual(self.delta.blocks["RENAMED"], [])

    def test_requirements_are_returned_in_document_order(self):
        """`Delta.requirements` devuelve todos los requisitos en orden de aparición."""
        self.assertEqual(
            [(r.id, r.line) for r in self.delta.requirements],
            [("R-CHK-001", 5), ("R-CHK-002", 11), ("R-CHK-003", 17)],
        )

    def test_delta_capability_name_comes_from_the_file_name(self):
        """El nombre de la capability de un delta sale del nombre del fichero."""
        self.assertEqual(self.delta.capability, "checkout")

    def test_delta_path_is_relative_to_the_root(self):
        """La ruta del delta se guarda relativa a la raíz del proyecto."""
        self.assertEqual(
            self.delta.path, ".venoxia/changes/2026-01-01-checkout/delta/checkout.md"
        )

    def test_a_clean_delta_produces_no_findings(self):
        """Un delta bien formado no genera ningún hallazgo."""
        self.assertEqual(self.findings, [])

    def test_a_delta_without_block_headers_declares_no_blocks(self):
        """Un delta sin encabezados de bloque deja `blocks` vacío para que V12 lo diga."""
        path = self.write("suelto.md", "### R-CHK-009 · Sin bloque\n\nWHEN algo.\n")
        delta, findings = parser.parse_delta(path, root=self.root)
        self.assertEqual(delta.blocks, {})
        self.assertEqual(delta.requirements, [])
        self.assertEqual(findings, [])

    def test_requirements_order_is_sorted_by_line_across_blocks(self):
        """El orden de `Delta.requirements` es por línea aunque los bloques se repitan."""
        path = self.write(
            "mezclado.md",
            "## ADDED Requirements\n"
            "\n"
            "### R-CHK-010 · Diez\n"
            "\n"
            "## REMOVED Requirements\n"
            "\n"
            "### R-CHK-011 · Once\n"
            "\n"
            "## ADDED Requirements\n"
            "\n"
            "### R-CHK-012 · Doce\n",
        )
        delta, _ = parser.parse_delta(path, root=self.root)
        self.assertEqual(
            [r.id for r in delta.requirements], ["R-CHK-010", "R-CHK-011", "R-CHK-012"]
        )

    def test_default_block_labels_requirements_written_before_any_block(self):
        """`default_block` marca los requisitos que llegan antes del primer bloque."""
        requirements, _ = parser.parse_requirements(
            "### R-CHK-001 · Uno\n\nWHEN algo.\n", default_block="added"
        )
        self.assertEqual(requirements[0].block, "ADDED")

    def test_without_default_block_the_requirement_has_none(self):
        """Sin bloque declarado ni por defecto, `block` es `None`."""
        requirements, _ = parser.parse_requirements("### R-CHK-001 · Uno\n")
        self.assertIsNone(requirements[0].block)


# --------------------------------------------------------------------------
# §3 · parse_capability
# --------------------------------------------------------------------------


class TestParseCapability(TempDirCase):
    """El nombre de una capability sale de su directorio cuando el fichero es `spec.md`."""

    def test_capability_name_comes_from_the_directory_for_spec_md(self):
        """`capabilities/checkout/spec.md` se llama «checkout», no «spec»."""
        path = self.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Checkout\n\n" + CANONICAL,
        )
        capability, findings = parser.parse_capability(path, root=self.root)
        self.assertEqual(capability.name, "checkout")
        self.assertEqual(findings, [])

    def test_capability_path_is_relative_to_the_root(self):
        """La ruta de la capability se guarda relativa a la raíz del proyecto."""
        path = self.write(".venoxia/capabilities/checkout/spec.md", CANONICAL)
        capability, _ = parser.parse_capability(path, root=self.root)
        self.assertEqual(capability.path, ".venoxia/capabilities/checkout/spec.md")

    def test_capability_name_falls_back_to_the_file_name(self):
        """Si el fichero no se llama `spec.md`, el nombre sale del propio fichero."""
        path = self.write(".venoxia/capabilities/inventory.md", CANONICAL)
        capability, _ = parser.parse_capability(path, root=self.root)
        self.assertEqual(capability.name, "inventory")

    def test_capability_collects_its_requirements(self):
        """La capability trae dentro los requisitos parseados del fichero."""
        path = self.write(".venoxia/capabilities/checkout/spec.md", CANONICAL)
        capability, _ = parser.parse_capability(path, root=self.root)
        self.assertEqual([r.id for r in capability.requirements], ["R-CHK-014"])

    def test_capability_requirements_have_no_block(self):
        """Una capability viva no tiene bloques: sus requisitos llevan `block=None`."""
        path = self.write(".venoxia/capabilities/checkout/spec.md", CANONICAL)
        capability, _ = parser.parse_capability(path, root=self.root)
        self.assertIsNone(capability.requirements[0].block)

    def test_capability_reads_the_purpose_section(self):
        """El propósito sale de la sección «## Purpose» si existe."""
        path = self.write(
            ".venoxia/capabilities/checkout/spec.md",
            "# Checkout\n\n## Purpose\n\nQue pagar no dé sorpresas.\n\n" + CANONICAL,
        )
        capability, _ = parser.parse_capability(path, root=self.root)
        self.assertEqual(capability.purpose, "Que pagar no dé sorpresas.")


# --------------------------------------------------------------------------
# §3 · find_covers
# --------------------------------------------------------------------------


class TestFindCovers(unittest.TestCase):
    """`find_covers` recoge los IDs marcados con «@covers» en un fichero de test."""

    def test_several_covers_in_one_file_and_several_comment_styles(self):
        """Varios «@covers» en el mismo fichero, en comentarios de distinta sintaxis."""
        text = (
            "// @covers R-CHK-014\n"
            "# @covers R-CHK-015\n"
            "/* @covers R-CHK-016 */\n"
            "<!-- @covers R-ORD-001 -->\n"
            "-- @covers R-INV-002\n"
            '""" @covers R-PAY-003 """\n'
        )
        self.assertEqual(
            parser.find_covers(text),
            {
                "R-CHK-014",
                "R-CHK-015",
                "R-CHK-016",
                "R-ORD-001",
                "R-INV-002",
                "R-PAY-003",
            },
        )

    def test_repeated_covers_collapse_into_one_id(self):
        """El mismo ID marcado dos veces aparece una sola vez: es un conjunto."""
        self.assertEqual(
            parser.find_covers("// @covers R-CHK-014\n// @covers R-CHK-014\n"),
            {"R-CHK-014"},
        )

    def test_covers_inside_code_is_found_anywhere_in_the_file(self):
        """El «@covers» vale en cualquier parte del fichero, no sólo al principio."""
        text = (
            "import test from 'node:test';\n"
            "\n"
            "test('reserva el stock', () => {\n"
            "  // @covers R-CHK-014\n"
            "});\n"
        )
        self.assertEqual(parser.find_covers(text), {"R-CHK-014"})

    def test_extra_whitespace_between_covers_and_the_id(self):
        """Da igual cuánto espacio haya entre «@covers» y el ID."""
        self.assertEqual(parser.find_covers("@covers    R-CHK-014"), {"R-CHK-014"})

    def test_no_covers_returns_an_empty_set(self):
        """Un fichero sin marcas devuelve el conjunto vacío, no `None`."""
        self.assertEqual(parser.find_covers("test('algo', () => {});\n"), set())

    def test_empty_text_returns_an_empty_set(self):
        """El texto vacío devuelve el conjunto vacío."""
        self.assertEqual(parser.find_covers(""), set())

    def test_covers_glued_to_the_id_is_not_a_mark(self):
        """«@coversR-CHK-014», sin espacio, no es una marca de cobertura."""
        self.assertEqual(parser.find_covers("@coversR-CHK-014"), set())


# --------------------------------------------------------------------------
# §3 · El parser nunca lanza
# --------------------------------------------------------------------------


class TestParserNeverRaises(TempDirCase):
    """Contrato §3: «Nunca lanza excepción». Ni con la entrada más hostil."""

    def test_parse_requirements_never_raises(self):
        """`parse_requirements` digiere cualquier entrada hostil sin lanzar."""
        for name, text in HOSTILE_INPUTS:
            with self.subTest(entrada=name):
                try:
                    requirements, findings = parser.parse_requirements(
                        text, source_file="hostil.md"
                    )
                except BaseException as error:  # noqa: BLE001 - eso es lo que se prueba
                    self.fail(
                        "parse_requirements lanzó %s con la entrada «%s»: %s"
                        % (type(error).__name__, name, error)
                    )
                self.assertIsInstance(requirements, list)
                self.assertIsInstance(findings, list)

    def test_find_covers_never_raises(self):
        """`find_covers` digiere cualquier entrada hostil sin lanzar."""
        for name, text in HOSTILE_INPUTS:
            with self.subTest(entrada=name):
                try:
                    covers = parser.find_covers(text)
                except BaseException as error:  # noqa: BLE001
                    self.fail(
                        "find_covers lanzó %s con la entrada «%s»: %s"
                        % (type(error).__name__, name, error)
                    )
                self.assertIsInstance(covers, set)

    def test_parse_delta_and_parse_capability_never_raise_on_hostile_files(self):
        """Ni `parse_delta` ni `parse_capability` lanzan con un fichero hostil."""
        for name, text in HOSTILE_INPUTS:
            with self.subTest(entrada=name):
                path = self.root / (name + ".md")
                path.write_bytes(text.encode("utf-8", "surrogatepass"))
                try:
                    delta, delta_findings = parser.parse_delta(path, root=self.root)
                    capability, cap_findings = parser.parse_capability(
                        path, root=self.root
                    )
                except BaseException as error:  # noqa: BLE001
                    self.fail(
                        "el parser lanzó %s con el fichero «%s»: %s"
                        % (type(error).__name__, name, error)
                    )
                self.assertIsInstance(delta, model.Delta)
                self.assertIsInstance(capability, model.Capability)
                self.assertIsInstance(delta_findings, list)
                self.assertIsInstance(cap_findings, list)

    def test_parse_delta_and_parse_capability_never_raise_on_a_bytes_path(self):
        """Una ruta en `bytes` devuelve un hallazgo, no un `TypeError` escapado.

        `_relative_path()` y `_capability_name()` corrían fuera del `try` y
        `_relative_path` sólo atrapaba `(OSError, ValueError)`: con la ruta en
        `bytes` el `TypeError` salía del parser y rompía el contrato §3.
        """
        real = self.write("spec.md", CANONICAL)
        for name, path in (
            ("existente", str(real).encode("utf-8")),
            ("inexistente", b"/no/existe/spec.md"),
        ):
            with self.subTest(ruta=name):
                try:
                    delta, delta_findings = parser.parse_delta(path, root=self.root)
                    capability, cap_findings = parser.parse_capability(
                        path, root=self.root
                    )
                except BaseException as error:  # noqa: BLE001 - eso es lo que se prueba
                    self.fail(
                        "el parser lanzó %s con una ruta en bytes: %s"
                        % (type(error).__name__, error)
                    )
                self.assertIsInstance(delta, model.Delta)
                self.assertIsInstance(capability, model.Capability)
                self.assertTrue(delta_findings)
                self.assertTrue(cap_findings)

    def test_parse_delta_and_parse_capability_never_raise_on_a_hostile_path_object(self):
        """Ni un objeto cuyo `__fspath__` revienta saca una excepción del parser."""

        class Explosive:
            """Una «ruta» que estalla al convertirse en cadena, de las dos formas."""

            def __fspath__(self):
                raise RuntimeError("no soy una ruta")

            def __str__(self):
                raise ValueError("ni siquiera me puedes imprimir")

        for name, path in (("explosiva", Explosive()), ("entero", 42), ("nula", None)):
            with self.subTest(ruta=name):
                try:
                    delta, delta_findings = parser.parse_delta(path, root=self.root)
                    capability, cap_findings = parser.parse_capability(
                        path, root=self.root
                    )
                except BaseException as error:  # noqa: BLE001
                    self.fail(
                        "el parser lanzó %s con la ruta «%s»: %s"
                        % (type(error).__name__, name, error)
                    )
                self.assertIsInstance(delta, model.Delta)
                self.assertIsInstance(capability, model.Capability)
                self.assertTrue(delta_findings)
                self.assertTrue(cap_findings)

    def test_parse_requirements_tolerates_none_as_text(self):
        """Ni siquiera un `None` por texto rompe el parser."""
        requirements, findings = parser.parse_requirements(None)  # type: ignore[arg-type]
        self.assertEqual(requirements, [])
        self.assertEqual(findings, [])

    def test_read_text_never_raises_on_an_unreadable_path(self):
        """`read_text` de una ruta imposible devuelve un hallazgo, no una excepción."""
        try:
            text, finding = parser.read_text(self.root / "a" / "b" / "c" / "d.md")
        except BaseException as error:  # noqa: BLE001
            self.fail("read_text lanzó %s: %s" % (type(error).__name__, error))
        self.assertIsNone(text)
        self.assertEqual(finding.rule, "P01")


# --------------------------------------------------------------------------
# §2 · El modelo
# --------------------------------------------------------------------------


class TestFindingModel(unittest.TestCase):
    """`Finding.to_dict()` es la puerta al esquema JSON estable de §4."""

    def test_to_dict_has_the_seven_schema_keys_in_order(self):
        """Las siete claves del esquema salen en el orden exacto del contrato §4."""
        finding = model.Finding(
            rule="V06",
            severity=model.SEVERITY_ERROR,
            message="Falta «verifies:».",
            file=".venoxia/changes/x/delta/checkout.md",
            line=14,
            requirement_id="R-CHK-014",
            hint="Añade «verifies: ruta/al/test».",
        )
        self.assertEqual(
            list(finding.to_dict().keys()),
            ["rule", "severity", "message", "file", "line", "requirement_id", "hint"],
        )

    def test_to_dict_carries_the_values(self):
        """`to_dict()` copia los valores sin tocarlos."""
        finding = model.Finding(
            rule="V06",
            severity=model.SEVERITY_ERROR,
            message="Falta «verifies:».",
            file="delta/checkout.md",
            line=14,
            requirement_id="R-CHK-014",
            hint="Añade «verifies: ruta/al/test».",
        )
        self.assertEqual(
            finding.to_dict(),
            {
                "rule": "V06",
                "severity": "error",
                "message": "Falta «verifies:».",
                "file": "delta/checkout.md",
                "line": 14,
                "requirement_id": "R-CHK-014",
                "hint": "Añade «verifies: ruta/al/test».",
            },
        )

    def test_to_dict_defaults_are_empty_string_and_none(self):
        """Sin fichero, línea, id ni pista, el hallazgo lleva los valores por defecto."""
        finding = model.Finding(rule="P01", severity="error", message="No se puede leer.")
        self.assertEqual(
            finding.to_dict(),
            {
                "rule": "P01",
                "severity": "error",
                "message": "No se puede leer.",
                "file": "",
                "line": None,
                "requirement_id": None,
                "hint": None,
            },
        )

    def test_severity_constants(self):
        """Las constantes de severidad son las dos cadenas del esquema JSON."""
        self.assertEqual(model.SEVERITY_ERROR, "error")
        self.assertEqual(model.SEVERITY_WARNING, "warning")


class TestRequirementLabel(unittest.TestCase):
    """`Requirement.label` es lo que aparece en los mensajes al usuario."""

    def test_label_is_the_id_when_there_is_one(self):
        """Con id, la etiqueta es el id."""
        requirement = model.Requirement(
            id="R-CHK-014", title="Reserva de stock", line=1, narrative="WHEN algo."
        )
        self.assertEqual(requirement.label, "R-CHK-014")

    def test_label_is_the_quoted_title_without_id(self):
        """Sin id, la etiqueta es el título entre comillas latinas."""
        requirement = model.Requirement(
            id=None, title="Reserva de stock", line=1, narrative="WHEN algo."
        )
        self.assertEqual(requirement.label, "«Reserva de stock»")

    def test_label_of_a_parsed_requirement_without_id(self):
        """La etiqueta del requisito que sale del parser sin id usa su título."""
        requirements, _ = parse_one("### Reserva de stock\n")
        self.assertEqual(requirements[0].label, "«Reserva de stock»")


class TestValidationResult(unittest.TestCase):
    """`ValidationResult`: qué cuenta como error, como aviso y como éxito."""

    def make_result(self, *findings, strict: bool = False) -> model.ValidationResult:
        """Construye un resultado con los hallazgos dados."""
        result = model.ValidationResult(strict=strict)
        for finding in findings:
            result.add(finding)
        return result

    def error(self) -> model.Finding:
        """Un hallazgo de error cualquiera."""
        return model.Finding(rule="V06", severity=model.SEVERITY_ERROR, message="mal")

    def warning(self) -> model.Finding:
        """Un hallazgo de aviso cualquiera."""
        return model.Finding(rule="V14", severity=model.SEVERITY_WARNING, message="ojo")

    def test_empty_result_is_ok(self):
        """Sin hallazgos, la especificación cumple."""
        self.assertTrue(self.make_result().ok)

    def test_a_warning_alone_is_ok_without_strict(self):
        """Un aviso no tumba la validación en modo normal."""
        self.assertTrue(self.make_result(self.warning()).ok)

    def test_a_warning_is_not_ok_with_strict(self):
        """En modo estricto, un aviso cuenta como fallo."""
        self.assertFalse(self.make_result(self.warning(), strict=True).ok)

    def test_an_error_is_never_ok(self):
        """Un error tumba la validación con y sin modo estricto."""
        for strict in (False, True):
            with self.subTest(strict=strict):
                self.assertFalse(self.make_result(self.error(), strict=strict).ok)

    def test_errors_and_warnings_are_split_by_severity(self):
        """`errors` y `warnings` reparten los hallazgos por severidad."""
        result = self.make_result(self.error(), self.warning(), self.error())
        self.assertEqual([f.rule for f in result.errors], ["V06", "V06"])
        self.assertEqual([f.rule for f in result.warnings], ["V14"])

    def test_add_ignores_none(self):
        """`add(None)` no ensucia la lista de hallazgos."""
        result = self.make_result()
        result.add(None)  # type: ignore[arg-type]
        self.assertEqual(result.findings, [])

    def test_counts_has_the_five_schema_keys(self):
        """`counts()` devuelve exactamente las cinco claves del esquema §4."""
        self.assertEqual(
            set(model.ValidationResult().counts()),
            {"error", "warning", "requirements", "capabilities", "deltas"},
        )

    def test_counts_adds_requirements_of_capabilities_and_deltas(self):
        """`counts()` suma los requisitos de las capabilities y de los deltas."""
        def requirement(rid: str, line: int) -> model.Requirement:
            """Un requisito mínimo para poder contarlo."""
            return model.Requirement(id=rid, title="T", line=line, narrative="WHEN algo.")

        capability = model.Capability(
            name="checkout",
            path=".venoxia/capabilities/checkout/spec.md",
            requirements=[requirement("R-CHK-001", 1), requirement("R-CHK-002", 10)],
        )
        delta = model.Delta(
            capability="checkout",
            path=".venoxia/changes/c1/delta/checkout.md",
            blocks={"ADDED": [requirement("R-CHK-003", 5)], "RENAMED": []},
        )
        result = model.ValidationResult(
            capabilities=[capability], deltas=[delta], strict=False
        )
        result.add(self.error())
        result.add(self.warning())
        result.add(self.warning())
        self.assertEqual(
            result.counts(),
            {
                "error": 1,
                "warning": 2,
                "requirements": 3,
                "capabilities": 1,
                "deltas": 1,
            },
        )

    def test_counts_of_an_empty_result_is_all_zeros(self):
        """Un resultado vacío cuenta cero en todo."""
        self.assertEqual(
            model.ValidationResult().counts(),
            {
                "error": 0,
                "warning": 0,
                "requirements": 0,
                "capabilities": 0,
                "deltas": 0,
            },
        )

    def test_default_root_and_strict(self):
        """Los valores por defecto son raíz «.» y modo no estricto."""
        result = model.ValidationResult()
        self.assertEqual(result.root, ".")
        self.assertFalse(result.strict)


class TestModelConstants(unittest.TestCase):
    """Las constantes del contrato §2, tal cual."""

    def test_block_names(self):
        """Los cuatro nombres de bloque, en orden."""
        self.assertEqual(
            model.BLOCK_NAMES, ("ADDED", "MODIFIED", "REMOVED", "RENAMED")
        )

    def test_confidence_levels(self):
        """Los tres niveles de confianza, de más a menos."""
        self.assertEqual(model.CONFIDENCE_LEVELS, ("high", "medium", "low"))

    def test_meta_keys(self):
        """Las cinco claves de metadatos reconocidas."""
        self.assertEqual(
            model.META_KEYS, ("verifies", "confidence", "why", "expires", "from")
        )

    def test_requirement_id_regex_accepts_the_canonical_form(self):
        """El identificador canónico encaja en `REQUIREMENT_ID_RE`."""
        for identifier in ("R-CHK-014", "R-AB-000", "R-ABCD-999"):
            with self.subTest(identifier=identifier):
                self.assertIsNotNone(model.REQUIREMENT_ID_RE.match(identifier))

    def test_requirement_id_regex_rejects_malformed_ids(self):
        """El identificador mal formado no encaja: eso es lo que V01 mira."""
        for identifier in ("R-C-014", "R-CHECKOUT-014", "R-CHK-14", "CHK-014", "r-chk-014"):
            with self.subTest(identifier=identifier):
                self.assertIsNone(model.REQUIREMENT_ID_RE.match(identifier))


# --------------------------------------------------------------------------
# Divergencias entre el código y el contrato
# --------------------------------------------------------------------------


class TestContractDivergences(unittest.TestCase):
    """Las dos divergencias del parser con el contrato §3, ya reparadas.

    Fallaban a propósito mientras el parser topaba la sangría de los metadatos
    en ocho columnas y borraba de la narrativa cualquier línea con forma
    «Palabra: texto». Arreglado eso, la marca de fallo esperado sobra: se
    quedan como tests normales para que la regresión vuelva a saltar.
    """

    def test_metadata_indentation_beyond_eight_spaces_is_still_metadata(self):
        """Contrato §3: la sangría de un metadato es cosmética (`^\\s*`), sin tope."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "confidence: low\n"
            "            why: la cifra es una apuesta\n"
        )
        self.assertEqual(requirements[0].meta.get("why"), "la cifra es una apuesta")

    def test_a_prose_line_with_an_unknown_key_stays_in_the_narrative(self):
        """Contrato §3: sólo las cinco claves son metadatos; la prosa no se borra.

        La versión anterior de este test medía el caso fácil y bendecía el
        difícil: ponía una línea en blanco entre la prosa y el bloque de
        metadatos, que era justo lo único que hacía falta para que la prosa se
        salvara. Pegada al bloque seguía desapareciendo. Aquí van los dos, y el
        segundo es el que de verdad vigila la reparación.
        """
        prosa = "Nota: WHEN el cliente confirma el pago, el sistema reserva el stock."
        for caso, separacion in {"separada del bloque": "\n", "pegada al bloque": ""}.items():
            with self.subTest(caso=caso):
                requirements, findings = parse_one(
                    "### R-CHK-014 · Reserva de stock\n"
                    "\n"
                    + prosa
                    + "\n"
                    + separacion
                    + "verifies: test/a.spec.ts\n"
                )
                # El aviso P02 sí lo manda el contrato; lo que no manda es que la
                # línea desaparezca de la narrativa y la deje vacía.
                self.assertEqual([f.rule for f in findings], ["P02"], caso)
                self.assertEqual(requirements[0].narrative, prosa, caso)
                self.assertEqual(
                    requirements[0].meta, {"verifies": "test/a.spec.ts"}, caso
                )


# --------------------------------------------------------------------------
# Lo que el bloque de metadatos no debe tragarse
# --------------------------------------------------------------------------


class TestMetadataIndentationGuards(unittest.TestCase):
    """Casos límite de la sangría dentro y fuera del bloque de metadatos.

    El contrato §3 dice que la sangría de «why»/«expires» es cosmética, y eso
    vale **dentro del bloque**. Estos tests fijan la frontera: la valla ```
    protege, la clave desconocida suelta se queda como prosa, ni las viñetas ni
    las URL entran por sangrada que esté la línea, y un metadato legítimo se lee
    con veinte columnas de alineación.
    """

    def test_a_fenced_code_block_never_yields_metadata(self):
        """Dentro de una valla ``` no hay metadatos, con la sangría que sea."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN el cliente pide el estado, el sistema devuelve este ejemplo:\n"
            "\n"
            "```yaml\n"
            "            verifies: mentira.spec.ts\n"
            "            confidence: low\n"
            "```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])
        self.assertIn("            verifies: mentira.spec.ts", requirements[0].narrative)

    def test_an_indented_example_never_overrides_the_real_metadata(self):
        """Un ejemplo sangrado no abre bloque: no pisa el metadato en ningún orden.

        La versión anterior de este test elegía el orden en el que el metadato
        de verdad iba el último y, como gana el último, la corrupción quedaba
        disimulada en un simple `P03`. Aquí se comprueban los dos órdenes: en
        los dos el `verifies` bueno sobrevive, no hay ningún hallazgo y el
        ejemplo se queda donde el autor lo escribió, en la narrativa.
        """
        real = "verifies: test/a.spec.ts\n"
        example = "    verifies: ejemplo.spec.ts\n"
        for orden, (primero, segundo) in {
            "ejemplo antes": (example, real),
            "ejemplo después": (real, example),
        }.items():
            with self.subTest(orden=orden):
                requirements, findings = parse_one(
                    "### R-CHK-001 · T\n"
                    "\n"
                    "WHEN el cliente pide el estado, el sistema devuelve este ejemplo:\n"
                    "\n"
                    + primero
                    + "\n"
                    + segundo
                )
                self.assertEqual(
                    requirements[0].meta, {"verifies": "test/a.spec.ts"}, orden
                )
                self.assertEqual(findings, [], orden)
                self.assertIn(
                    "    verifies: ejemplo.spec.ts", requirements[0].narrative, orden
                )

    def test_a_list_item_with_a_colon_stays_in_the_narrative(self):
        """«- algo: otra cosa» es una viñeta de la narrativa, no un metadato."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN el cliente paga, el sistema comprueba dos cosas:\n"
            "- stock: que haya en todas las líneas\n"
            "      - saldo: que la tarjeta responda\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])
        self.assertEqual(
            requirements[0].narrative,
            "WHEN el cliente paga, el sistema comprueba dos cosas:\n"
            "- stock: que haya en todas las líneas\n"
            "      - saldo: que la tarjeta responda",
        )

    def test_an_https_url_is_never_metadata_at_any_indentation(self):
        """Una URL «https://» no es un metadato ni con veinte espacios delante."""
        for indent in ("", "    ", " " * 9, " " * 20):
            with self.subTest(indent=len(indent)):
                requirements, findings = parse_one(
                    "### R-CHK-001 · T\n"
                    "\n"
                    "WHEN el cliente paga, el sistema consulta el catálogo.\n"
                    + indent + "https://example.com/docs/checkout lo describe.\n"
                    "\n"
                    "verifies: test/a.spec.ts\n"
                )
                self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
                self.assertEqual(findings, [])
                self.assertIn("https://example.com/docs/checkout", requirements[0].narrative)

    def test_a_legitimate_metadata_survives_twenty_spaces_of_indentation(self):
        """Con veinte espacios de sangría el metadato se lee igual y sale de la prosa."""
        expires = future_date(45)
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "confidence:         low\n"
            "                    why:     los 15 minutos son una apuesta\n"
            "                    expires: " + expires + "\n"
        )
        self.assertEqual(
            requirements[0].meta,
            {
                "confidence": "low",
                "why": "los 15 minutos son una apuesta",
                "expires": expires,
            },
        )
        self.assertEqual(requirements[0].meta_lines["why"], 6)
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")
        self.assertEqual(findings, [])

    def test_a_deeply_indented_unknown_key_keeps_its_line_in_the_narrative(self):
        """Una clave desconocida alineada a mano avisa con `P02` y sigue siendo prosa."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "                    nota: esto es prosa alineada, no un metadato.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P02"])
        self.assertEqual(findings[0].line, 4)
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(
            requirements[0].narrative,
            "WHEN algo, el sistema responde.\n"
            "                    nota: esto es prosa alineada, no un metadato.",
        )


# --------------------------------------------------------------------------
# El bloque de metadatos como región, no como líneas sueltas
# --------------------------------------------------------------------------


def _document_with_prose(
    narrative: str, line: str, position: str, vicinity: str
) -> str:
    """Un requisito con `line` colocada respecto del bloque de metadatos.

    `position` es «antes» o «después» del bloque; `vicinity`, «pegada» (sin
    línea en blanco de por medio) o «separada». Sirve para recorrer las cuatro
    combinaciones sin escribir cuatro documentos a mano.
    """
    block = "verifies: test/a.spec.ts\nconfidence: high\n"
    gap = "\n" if vicinity == "separada" else ""
    tail = line + "\n" + gap + block if position == "antes" else block + gap + line + "\n"
    return "### R-CHK-001 · T\n\n" + narrative + "\n\n" + tail


class TestMetadataBlockRegion(unittest.TestCase):
    """El contrato §3 habla de **el bloque** de metadatos, no de líneas sueltas.

    Clasificar cada línea por su cuenta costó dos regresiones: un ejemplo
    alineado a mano pisaba un metadato de verdad y una clave desconocida del
    bloque final se quedaba cruda en la narrativa. Estos tests fijan la región:
    una racha contigua de «clave: valor», abierta a ras de margen (tres columnas
    como mucho) y con al menos una de las cinco claves reconocidas.
    """

    def test_an_indented_example_does_not_override_expires(self):
        """Una tabla de ejemplo alineada a mano no toca el `expires:` que gobierna V10."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "verifies:   test/real.spec.ts\n"
            "confidence: high\n"
            "expires:    2030-01-01\n"
            "\n"
            "Tabla de ejemplo, alineada a mano:\n"
            "\n"
            "            confidence: xxxxx\n"
            "            expires:    ayer\n"
        )
        self.assertEqual(
            requirements[0].meta,
            {
                "verifies": "test/real.spec.ts",
                "confidence": "high",
                "expires": "2030-01-01",
            },
        )
        self.assertEqual(findings, [])
        self.assertIn("            expires:    ayer", requirements[0].narrative)

    def test_an_unknown_key_inside_the_final_block_leaves_the_narrative_clean(self):
        """Un «owner:» del bloque final avisa, se pierde y no vuelve a la prosa."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
            "owner: alice\n"
            "from: prfaq/x.md#sección\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P02"])
        self.assertEqual(findings[0].line, 6)
        self.assertEqual(
            requirements[0].meta,
            {"verifies": "test/a.spec.ts", "from": "prfaq/x.md#sección"},
        )
        # Lo que rompía V02 y V14: la narrativa acababa con «owner: alice».
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")

    def test_three_columns_of_indentation_still_open_the_block(self):
        """La frontera está en tres columnas: con tres, el bloque abre."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "   verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")
        self.assertEqual(findings, [])

    def test_four_columns_of_indentation_do_not_open_the_block(self):
        """Con cuatro columnas ya es código sangrado de CommonMark: no abre bloque."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "    verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {})
        self.assertIn("    verifies: test/a.spec.ts", requirements[0].narrative)
        self.assertEqual(findings, [])

    def test_a_run_without_any_known_key_is_prose(self):
        """Una racha sin ninguna de las cinco claves es prosa: avisa y se queda."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "Nota: esto es una aclaración.\n"
            "Aviso: y esto otra.\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P02", "P02"])
        self.assertEqual([finding.line for finding in findings], [5, 6])
        self.assertEqual(requirements[0].meta, {})
        self.assertEqual(
            requirements[0].narrative,
            "WHEN algo, el sistema responde.\n"
            "\n"
            "Nota: esto es una aclaración.\n"
            "Aviso: y esto otra.",
        )

    def test_a_blank_line_closes_the_block(self):
        """Una línea en blanco corta la racha: lo de después es otro bloque."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
            "\n"
            "            nota: alineada a mano, no es del bloque de arriba\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P02"])
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertIn("            nota: alineada", requirements[0].narrative)

    def test_prose_next_to_the_block_survives_in_every_combination(self):
        """La regla es la clave, no la distancia: cuatro posiciones, un resultado.

        Este test no sale del caso que se dio, sale de la regla: una línea con
        forma «Palabra: texto» y clave desconocida es prosa **esté donde esté**
        respecto del bloque de metadatos —delante o detrás, pegada o separada—.
        Medir sólo el caso separado fue lo que dejó pasar dos rondas el borrado
        de la prosa contigua.
        """
        narrativa = "WHEN el cliente confirma el pago, el sistema reserva el stock."
        prosa = "Nota: la reserva dura quince minutos."
        for posicion in ("antes", "después"):
            for vecindad in ("pegada", "separada"):
                with self.subTest(posicion=posicion, vecindad=vecindad):
                    requirements, findings = parse_one(
                        _document_with_prose(narrativa, prosa, posicion, vecindad)
                    )
                    self.assertEqual([f.rule for f in findings], ["P02"])
                    self.assertEqual(findings[0].message.count("«Nota»"), 1)
                    self.assertIn(narrativa, requirements[0].narrative)
                    self.assertIn(prosa, requirements[0].narrative)
                    self.assertNotIn("verifies", requirements[0].narrative)
                    self.assertEqual(
                        requirements[0].meta,
                        {"verifies": "test/a.spec.ts", "confidence": "high"},
                    )

    def test_a_known_key_next_to_the_block_is_metadata_in_every_combination(self):
        """La otra mitad de la regla: con una de las cinco claves no hay duda.

        Un «from: …» pegado o separado del bloque es metadato en los cuatro
        casos. Es la frontera deliberada: lo que decide es la clave, y por eso
        una clave reconocida nunca se queda en la prosa aunque venga suelta.
        """
        narrativa = "WHEN el cliente confirma el pago, el sistema reserva el stock."
        conocida = "from: prfaq/checkout.md#sin-sorpresas"
        for posicion in ("antes", "después"):
            for vecindad in ("pegada", "separada"):
                with self.subTest(posicion=posicion, vecindad=vecindad):
                    requirements, findings = parse_one(
                        _document_with_prose(narrativa, conocida, posicion, vecindad)
                    )
                    self.assertEqual(findings, [])
                    self.assertEqual(requirements[0].narrative, narrativa)
                    self.assertEqual(
                        requirements[0].meta,
                        {
                            "verifies": "test/a.spec.ts",
                            "confidence": "high",
                            "from": "prfaq/checkout.md#sin-sorpresas",
                        },
                    )

    def test_an_indented_known_key_does_not_drag_down_the_flush_one_below_it(self):
        """El bloque abre en la primera clave reconocida **a ras**, no en la primera.

        Con un ejemplo sangrado pegado por encima, abrir en la primera clave
        reconocida a secas descartaba la racha entera y se llevaba por delante un
        «confidence:» de verdad escrito en el margen.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "    verifies: ejemplo.spec.ts\n"
            "confidence: high\n"
        )
        self.assertEqual(requirements[0].meta, {"confidence": "high"})
        self.assertIn("    verifies: ejemplo.spec.ts", requirements[0].narrative)
        self.assertEqual(findings, [])

    def test_an_unknown_key_between_two_known_ones_belongs_to_the_block(self):
        """Y el interior del bloque sigue siendo bloque: ahí sí manda la vecindad.

        Entre «verifies:» y «from:», un «owner: alice» es un metadato mal
        escrito, no prosa: avisa con su P02, no entra en `meta` y no vuelve a la
        narrativa. Es el caso que la ronda anterior arregló y que éste no puede
        romper.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "verifies: test/a.spec.ts\n"
            "owner: alice\n"
            "from: prfaq/x.md\n"
        )
        self.assertEqual([f.rule for f in findings], ["P02"])
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")
        self.assertEqual(
            requirements[0].meta,
            {"verifies": "test/a.spec.ts", "from": "prfaq/x.md"},
        )

    def test_the_metadata_block_right_after_the_header_still_works(self):
        """El bloque adelantado, pegado al encabezado, se sigue leyendo entero."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "verifies: test/a.spec.ts\n"
            "confidence: high\n"
            "  why: alineado bajo la clave larga\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
        )
        self.assertEqual(
            requirements[0].meta,
            {
                "verifies": "test/a.spec.ts",
                "confidence": "high",
                "why": "alineado bajo la clave larga",
            },
        )
        self.assertEqual(requirements[0].narrative, "WHEN algo, el sistema responde.")
        self.assertEqual(findings, [])


# --------------------------------------------------------------------------
# Vallas de código sangradas
# --------------------------------------------------------------------------


class TestIndentedCodeFences(unittest.TestCase):
    """Una valla ``` dentro de una lista anidada también blinda lo que envuelve.

    `FENCE_RE` admitía hasta tres espacios, así que la valla de un ejemplo
    metido en una lista de dos niveles —CommonMark impecable— no protegía nada:
    su contenido desaparecía de la narrativa y sus claves entraban como
    metadatos del requisito.
    """

    NESTED = (
        "### R-CHK-001 · T\n"
        "\n"
        "WHEN el cliente pide el estado, el sistema responde así:\n"
        "\n"
        "- nivel 1\n"
        "  - nivel 2\n"
        "    ```\n"
        "    ### R-FAKE-999 · No soy un requisito\n"
        "    verifies: mentira.spec.ts\n"
        "    - **WHEN** tampoco soy una viñeta\n"
        "    ```\n"
        "\n"
        "verifies: test/a.spec.ts\n"
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.requirements, cls.findings = parser.parse_requirements(
            cls.NESTED, source_file="delta/checkout.md"
        )

    def test_the_fenced_metadata_does_not_reach_the_requirement(self):
        """El «verifies:» de dentro de la valla sangrada no entra en `meta`."""
        self.assertEqual(self.requirements[0].meta, {"verifies": "test/a.spec.ts"})

    def test_the_fenced_header_does_not_open_a_second_requirement(self):
        """El «### R-FAKE-999» de dentro de la valla sangrada no abre requisito."""
        self.assertEqual([r.id for r in self.requirements], ["R-CHK-001"])

    def test_the_fenced_bullet_creates_no_scenario_and_no_finding(self):
        """Ni escenarios ni hallazgos salen de dentro de la valla sangrada."""
        self.assertEqual(self.requirements[0].scenarios, [])
        self.assertEqual([finding.rule for finding in self.findings], [])

    def test_the_indented_block_survives_verbatim_in_the_narrative(self):
        """El ejemplo sangrado se conserva literal, valla incluida."""
        self.assertEqual(
            self.requirements[0].narrative,
            "WHEN el cliente pide el estado, el sistema responde así:\n"
            "\n"
            "- nivel 1\n"
            "  - nivel 2\n"
            "    ```\n"
            "    ### R-FAKE-999 · No soy un requisito\n"
            "    verifies: mentira.spec.ts\n"
            "    - **WHEN** tampoco soy una viñeta\n"
            "    ```",
        )

    def test_a_bullet_inside_an_indented_fence_is_not_a_malformed_bullet(self):
        """Una línea de lista dentro de una valla sangrada no se cobra un `P04`.

        Con la valla topada en tres espacios, esa línea no estaba dentro de
        ninguna valla: era una viñeta rota del escenario abierto justo antes.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "#### Scenario: S\n"
            "- **WHEN** a\n"
            "- **THEN** b\n"
            "\n"
            "    ```\n"
            "    - una línea de ejemplo que no es una viñeta\n"
            "    ```\n"
        )
        self.assertEqual(findings, [])
        self.assertEqual(
            requirements[0].scenarios[0].bullets, [("WHEN", "a"), ("THEN", "b")]
        )

    def test_an_indented_fence_shields_a_line_written_flush_to_the_margin(self):
        """Lo que va dentro de la valla sangrada no es gramática, aunque esté a ras.

        Es la demostración del fallo que arregló la ronda anterior: sin reconocer
        la valla de la lista anidada, el «verifies:» del ejemplo entraba como
        metadato del requisito.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN el cliente pide el estado, el sistema responde así:\n"
            "\n"
            "- nivel 1\n"
            "  - nivel 2\n"
            "    ```\n"
            "verifies: mentira.spec.ts\n"
            "- **WHEN** tampoco soy una viñeta\n"
            "    ```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001"])
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])

    def test_a_bare_fence_does_not_shield_a_heading_written_flush_to_the_margin(self):
        """El precio del arreglo, escrito y con test: la valla anónima no blinda un «### ».

        Una valla **sin etiqueta de lenguaje** no puede envolver un encabezado de
        requisito, porque ésa es exactamente la forma con la que una valla
        huérfana se tragaba los requisitos de detrás y regalaba un falso verde.
        Aquí el ejemplo se rompe y aparece un requisito de mentira: ruidoso,
        visible y con sus hallazgos, que es el lado barato del error.
        """
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "- nivel 1\n"
            "  - nivel 2\n"
            "    ```\n"
            "### R-FAKE-999 · No soy un requisito\n"
            "    ```\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001", "R-FAKE-999"])

    def test_a_labelled_fence_does_shield_a_heading_written_flush_to_the_margin(self):
        """Con etiqueta, el autor declara que es un ejemplo, y entonces sí blinda.

        Es la única señal honesta que da el texto para distinguir un ejemplo de
        una valla mal cerrada, y por eso es la que decide.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "- nivel 1\n"
            "  - nivel 2\n"
            "    ```markdown\n"
            "### R-FAKE-999 · No soy un requisito\n"
            "    ```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001"])
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual([finding.rule for finding in findings], ["P05"])
        self.assertEqual(findings[0].line, 6)

    def test_a_fence_indented_far_beyond_the_opener_does_not_close_it(self):
        """La valla de cierre admite tres columnas más que la de apertura, no más.

        Una valla abierta a ras de margen no la cierra una línea de acentos
        sangrada cuatro columnas: eso es contenido del propio bloque, como manda
        CommonMark. Aquí lo que se juega es que el «verifies:» de en medio siga
        siendo texto y no un metadato.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "```\n"
            "    ```\n"
            "verifies: mentira.spec.ts\n"
            "```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])

    def test_a_lone_indented_fence_does_not_swallow_the_rest(self):
        """Una valla sangrada y sin pareja no abre nada: no esconde los metadatos.

        Abrir la valla con la sangría que sea tiene este filo: un «```» sangrado
        y suelto se tragaría el resto del requisito y su `verifies:` de verdad,
        que es peor que el fallo que se venía a arreglar. Para CommonMark una
        línea sangrada cuatro columnas sólo es valla dentro de una lista, y sin
        cierre esa lectura no se sostiene, así que se lee como texto.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "    ```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual(findings, [])
        self.assertIn("    ```", requirements[0].narrative)

    def test_thousands_of_lone_indented_fences_are_still_fast(self):
        """Buscarle pareja a cada valla sangrada no puede costar un recorrido entero.

        La comprobación de pareja es un barrido del documento; sin cachearla por
        forma de valla, un fichero con miles de vallas sangradas sin cierre
        posible tardaba más de cuatro segundos. El presupuesto de aquí es
        holgado a propósito: lo que se vigila es el salto de orden, no los
        milisegundos.
        """
        texto = "### R-CHK-001 · T\n\nWHEN algo.\n\n" + "    ```py\n" * 5000
        inicio = time.perf_counter()
        requirements, _ = parse_one(texto)
        transcurrido = time.perf_counter() - inicio
        self.assertEqual(len(requirements), 1)
        self.assertLess(transcurrido, 2.0, "el parser tardó %.2f s" % transcurrido)

    def test_a_lone_flush_fence_still_swallows_the_rest(self):
        """La valla sin cerrar escrita a ras de margen se sigue tragando el resto."""
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "```\n"
            "\n"
            "verifies: mentira.spec.ts\n"
        )
        self.assertEqual(requirements[0].meta, {})
        self.assertEqual(findings, [])

    def test_an_indented_fence_closes_with_its_own_indentation(self):
        """Una valla sangrada se cierra con otra igual de sangrada, y ahí acaba."""
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "- nivel 1\n"
            "    ```\n"
            "    verifies: mentira.spec.ts\n"
            "    ```\n"
            "\n"
            "confidence: high\n"
        )
        # Si la valla no se hubiera cerrado, «confidence» seguiría dentro del
        # bloque de código y `meta` estaría vacío.
        self.assertEqual(requirements[0].meta, {"confidence": "high"})


# --------------------------------------------------------------------------
# La valla huérfana que borraba los requisitos de detrás
# --------------------------------------------------------------------------


#: El documento del fallo, letra por letra. Una valla sangrada que el autor se
#: dejó sin cerrar en R-CHK-001 y, mucho más abajo, un bloque ```ts perfectamente
#: cerrado. Buscándole pareja a la valla huérfana **en todo el documento**, el
#: parser daba por buena la valla de cierre de aquel bloque y se tragaba entero
#: lo que había en medio: los dos requisitos siguientes, con sus errores dentro.
ORPHAN_FENCE_SPEC = (
    "### R-CHK-001 · Reserva de stock\n"                     # 1
    "\n"                                                      # 2
    "WHEN el cliente confirma el pago, el sistema reserva.\n"  # 3
    "\n"                                                      # 4
    "- nivel 1\n"                                             # 5
    "  - nivel 2\n"                                           # 6
    "    ```\n"                                               # 7
    "    valla que el autor olvidó cerrar\n"                  # 8
    "\n"                                                      # 9
    "### R-CHK-002 · Requisito sin verifies\n"                # 10
    "\n"                                                      # 11
    "WHEN pasa algo, el sistema hace lo otro.\n"              # 12
    "\n"                                                      # 13
    "### R-CHK-003 · Requisito con un ejemplo bien cerrado\n"  # 14
    "\n"                                                      # 15
    "WHEN pasa otra cosa, el sistema responde.\n"             # 16
    "\n"                                                      # 17
    "```ts\n"                                                 # 18
    "const x = 1;\n"                                          # 19
    "```\n"                                                   # 20
)


class TestOrphanFenceNeverHidesRequirements(unittest.TestCase):
    """Ninguna valla huérfana puede borrar los requisitos que vienen detrás.

    Es el peor fallo posible del plugin: el validador daba «✓ La especificación
    cumple el contrato» con exit 0 sobre una spec con tres errores, porque los
    requisitos que los traían habían dejado de existir para el parser. Ninguna
    regla puede quejarse de un requisito que no ve.

    La reparación son dos decisiones, y cada test de aquí vigila una: la pareja
    de una valla tiene que ser **compatible** —misma sangría o más, mismo
    carácter, al menos tantos acentos— y una valla sin pareja no puede tragarse
    un encabezado de nivel de requisito.
    """

    def test_the_three_requirements_survive_the_orphan_fence(self):
        """Los tres requisitos del documento del fallo llegan enteros al modelo."""
        requirements, _ = parse_one(ORPHAN_FENCE_SPEC)
        self.assertEqual(
            [r.id for r in requirements], ["R-CHK-001", "R-CHK-002", "R-CHK-003"]
        )

    def test_the_swallowed_requirements_keep_the_prose_the_rules_judge(self):
        """Y con su narrativa: sin ella, V02, V03 y V14 no tendrían nada que juzgar."""
        requirements, _ = parse_one(ORPHAN_FENCE_SPEC)
        self.assertEqual(
            requirements[1].narrative, "WHEN pasa algo, el sistema hace lo otro."
        )
        self.assertEqual(
            requirements[2].narrative,
            "WHEN pasa otra cosa, el sistema responde.\n\n```ts\nconst x = 1;\n```",
        )

    def test_the_orphan_indented_fence_stays_in_the_narrative_as_text(self):
        """La valla huérfana no abre nada: se lee como el texto sangrado que es."""
        requirements, _ = parse_one(ORPHAN_FENCE_SPEC)
        self.assertIn("    ```", requirements[0].narrative)
        self.assertIn("    valla que el autor olvidó cerrar", requirements[0].narrative)

    def test_a_flush_fence_does_not_close_an_indented_one(self):
        """La pareja tiene que venir con la sangría de la valla que abre, o más.

        Aquí está la raíz del fallo: la valla de cierre a ras de margen pertenece
        a otro bloque, no a la de la lista anidada. Si se la deja cerrar, se
        traga las once líneas de en medio.
        """
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "  - nivel 2\n"
            "    ```\n"
            "\n"
            "### R-CHK-002 · Sobrevivo\n"
            "\n"
            "WHEN algo, el sistema responde.\n"
            "\n"
            "```\n"
            "un bloque de otro requisito\n"
            "```\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001", "R-CHK-002"])

    def test_an_orphan_fence_does_not_pair_with_a_later_indented_example(self):
        """La otra mitad del fallo: el cierre robado también puede venir sangrado.

        Exigir que la pareja traiga la sangría de la que abre tapaba sólo la
        variante del cierre a ras. Con dos vallas sangradas —una suelta arriba y
        el cierre de un ejemplo legítimo más abajo— la forma es idéntica y el
        emparejamiento volvía a tragarse los requisitos de en medio. Lo que lo
        impide es que una valla sin etiqueta no busque pareja más allá del
        siguiente encabezado de requisito.
        """
        requirements, _ = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "- lista\n"
            "    ```\n"
            "    valla que nadie cerró\n"
            "\n"
            "### R-CHK-002 · Requisito sin verifies\n"
            "\n"
            "WHEN otra cosa, el sistema responde.\n"
            "\n"
            "### R-CHK-003 · Requisito con un ejemplo sangrado legítimo\n"
            "\n"
            "- lista\n"
            "    ```py\n"
            "    x = 1\n"
            "    ```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual(
            [r.id for r in requirements], ["R-CHK-001", "R-CHK-002", "R-CHK-003"]
        )
        self.assertEqual(requirements[2].meta, {"verifies": "test/a.spec.ts"})

    def test_two_orphan_fences_of_different_requirements_do_not_pair(self):
        """Dos vallas sueltas de requisitos distintos no se emparejan entre sí.

        Cada una es huérfana en su requisito; leerlas como un solo bloque borraba
        todos los requisitos que hubiera entre ellas.
        """
        texto = "".join(
            f"### R-CHK-{numero:03d} · T\n\nWHEN algo, el sistema responde.\n\n"
            "- lista\n    ```\n    ejemplo sin cerrar\n\n"
            for numero in range(1, 5)
        )
        requirements, _ = parse_one(texto)
        self.assertEqual(
            [r.id for r in requirements],
            ["R-CHK-001", "R-CHK-002", "R-CHK-003", "R-CHK-004"],
        )

    def test_a_closed_fence_still_shields_a_heading_written_inside_it(self):
        """La contrapartida: la valla bien cerrada sigue blindando lo que envuelve.

        Arreglar la valla huérfana no puede costar el ejemplo legítimo. Con
        pareja compatible, el «### » de dentro sigue siendo texto —y se anuncia
        con el `P05` de la salvaguarda, que es sólo un aviso—.
        """
        requirements, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "```md\n"
            "### R-FAKE-999 · No soy un requisito\n"
            "```\n"
            "\n"
            "verifies: test/a.spec.ts\n"
        )
        self.assertEqual([r.id for r in requirements], ["R-CHK-001"])
        self.assertEqual(requirements[0].meta, {"verifies": "test/a.spec.ts"})
        self.assertEqual([finding.rule for finding in findings], ["P05"])


class TestHiddenHeadingSafeguard(unittest.TestCase):
    """`P05`: la salvaguarda de último recurso contra el requisito invisible.

    Debajo de todas las reglas de vallas hay una red: si alguna vez un «### »
    vuelve a no convertirse en requisito, se anuncia con su línea. Un aviso de
    más es barato; un requisito que desaparece en silencio es un falso verde.
    """

    def test_a_heading_hidden_by_a_fence_raises_the_warning(self):
        """El encabezado escondido sale por su código, su línea y su texto."""
        _, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "```markdown\n"
            "### R-CHK-002 · Escondido por la valla\n"
            "```\n"
        )
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule, "P05")
        self.assertEqual(finding.severity, model.SEVERITY_WARNING)
        self.assertEqual(finding.line, 4)
        self.assertEqual(finding.file, "delta/checkout.md")
        self.assertIn("R-CHK-002 · Escondido por la valla", finding.message)
        self.assertTrue(finding.hint)

    def test_every_hidden_heading_gets_its_own_warning(self):
        """Dos encabezados escondidos, dos avisos, cada uno con su línea."""
        _, findings = parse_one(
            "### R-CHK-001 · T\n"
            "\n"
            "```markdown\n"
            "### R-CHK-002 · Primero\n"
            "### R-CHK-003 · Segundo\n"
            "```\n"
        )
        self.assertEqual([finding.rule for finding in findings], ["P05", "P05"])
        self.assertEqual([finding.line for finding in findings], [4, 5])

    def test_a_document_whose_headings_are_all_requirements_stays_silent(self):
        """Sin encabezados escondidos no hay aviso: la red no se nota."""
        requirements, findings = parse_one(CANONICAL)
        self.assertEqual([r.id for r in requirements], ["R-CHK-014"])
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
