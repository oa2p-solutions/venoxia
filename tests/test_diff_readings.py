#!/usr/bin/env python3
"""Suite del motor de divergencia: `scripts/diff_readings.py` contra §7 del contrato.

La tesis del componente es que **la aritmética la hace el código, no un modelo**.
Esta suite es lo que lo demuestra: normaliza, empareja, compara campo a campo y
comprueba que cada desacuerdo sale convertido en una **pregunta cerrada**.

Todo se ejecuta por subproceso sobre un proyecto en un directorio temporal, salvo
`normalize`/`similarity`, que se importan directamente porque son funciones puras.

@covers R-DIV-005
@covers R-DIV-006
@covers R-DIV-007
"""

from __future__ import annotations

import json
import os
import re
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

# El bytecode se queda en memoria: la suite no escribe nada dentro del repositorio.
sys.dont_write_bytecode = True

from tests.venoxia_fixtures import (  # noqa: E402  (ajusta sys.path al importarse)
    DIFF_READINGS_PY,
    REPO_ROOT,
    CompletedRun,
    Project,
    reading,
)

import diff_readings  # noqa: E402  (vive en scripts/, que el import de arriba pone en sys.path)

#: Las claves de primer nivel de `--json`: las seis de §7 más las cuatro que hacen
#: falta para que el canal máquina pueda decir lo mismo que el canal prosa.
#: `verdict` nombra cuál de los seis veredictos es, `strict` y `exit_code` cuentan
#: qué pasó **en esta invocación** y `advocate` distingue «no hay abogado» de «hay
#: abogado y no se pudo leer». Sin ellas, el JSON sólo sabía decir `converged: false`
#: para seis situaciones que se arreglan de seis maneras distintas.
TOP_LEVEL_KEYS = [
    "version",
    "converged",
    "verdict",
    "strict",
    "exit_code",
    "counts",
    "divergences",
    "gaps",
    "attacks",
    "advocate",
]

#: Las subclaves exactas de `counts`.
COUNT_KEYS = ["hard", "soft", "gaps", "scenarios", "readers"]

#: Las claves de una divergencia y de una laguna en el JSON del contrato.
DIVERGENCE_KEYS = ["scenario", "field", "hardness", "readings", "question", "options"]
GAP_KEYS = ["scenario", "reader", "why"]

#: El par de lecturas que diverge de forma **blanda**: dicen dos cosas
#: distintas —si al caducar el stock vuelve a estar libre o no— sin que ninguna
#: pieza estructurada (código, efectos) las separe.
#:
#: Antes este par era «reserva creada» contra «reserva creada con TTL», y dejó
#: de servir cuando la similitud pasó a comparar contenido: dos redacciones de
#: lo mismo tienen que converger, y ésa era la avería que se estaba arreglando.
#: Un fixture blando tiene que discrepar de verdad, o el test aprueba porque el
#: motor es ruidoso.
SOFT_A = "la reserva caduca y el stock vuelve a estar libre"
SOFT_B = "la reserva se marca vencida sin tocar el stock"

#: Las preguntas abiertas que este componente existe para no cometer.
OPEN_QUESTIONS = ("hay algo ambiguo", "algo que aclarar")

#: La traza que jamás debe llegar al usuario.
TRACEBACK = "Traceback (most recent call last)"

#: Los dos agentes que despacha /venoxia:diverge.
AGENT_FILES = ("agents/reader.md", "agents/devils-advocate.md")

#: Frontmatter plano: `clave: valor`, sin indentación, sin listas, sin anidamiento.
FLAT_KEY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):(?P<value>.*)$")


def rich_readings() -> dict:
    """Dos lectores que disparan a la vez las cuatro divergencias y una laguna.

    Escenario a escenario: código distinto (dura), un efecto que sólo ve un
    lector (dura), efecto bajo el umbral de similitud (blanda), escenario que
    sólo ve un lector (dura) y un `unclear: true` (laguna).

    El par blando dice dos cosas distintas de verdad —si al caducar se libera el
    stock o no—, no la misma con otras palabras. Desde que la similitud compara
    contenido y no palabras sueltas, un par que sólo cambiaba de redacción
    converge, que es justo lo que se quería.
    """
    return {
        "reader-a": [
            reading("Insufficient stock on one line", "rechaza la peticion", "409"),
            reading(
                "Stock available on every line",
                "crea la reserva",
                "201",
                ["stock reservado", "evento emitido"],
            ),
            reading("Reservation expires", SOFT_A, "200"),
            reading("Payment retried after expiry", "vuelve a reservar", "200"),
            reading("Partial reservation", "reserva parcial", "207"),
        ],
        "reader-b": [
            reading("Insufficient stock on one line", "rechaza la peticion", "422"),
            reading("Stock available on every line", "crea la reserva", "201", ["stock reservado"]),
            reading("Reservation expires", SOFT_B, "200"),
            # «Payment retried after expiry» no está: divergencia missing_scenario.
            reading(
                "Partial reservation",
                "",
                None,
                unclear=True,
                unclear_why="el delta no dice si se reserva lo que hay",
            ),
        ],
    }


def coherence_cases() -> tuple[tuple[str, dict, bool, int], ...]:
    """Los tres veredictos posibles: convergencia real, sólo blandas, y duras o lagunas.

    Cada caso es `(nombre, lectores, converged esperado, exit esperado)`. La pareja
    «sólo blandas» es la que separa las dos preguntas: no convergen —hay desacuerdo—
    y aun así la ejecución no falla.
    """
    return (
        (
            "convergen",
            {
                "a": [reading("Stock available", "crea la reserva", "201", ["stock reservado"])],
                "b": [reading("Stock available", "crea la reserva", "201", ["stock reservado"])],
            },
            True,
            0,
        ),
        (
            "solo-blandas",
            {
                "a": [reading("Reservation created", SOFT_A, "201")],
                "b": [reading("Reservation created", SOFT_B, "201")],
            },
            False,
            0,
        ),
        (
            "dura",
            {
                "a": [reading("Insufficient stock", "rechaza", "409")],
                "b": [reading("Insufficient stock", "rechaza", "422")],
            },
            False,
            1,
        ),
        (
            "laguna",
            {
                "a": [reading("Payment retried after expiry", "vuelve a reservar", "200")],
                "b": [
                    reading(
                        "Payment retried after expiry",
                        "",
                        None,
                        unclear=True,
                        unclear_why="el delta no dice si el reintento vuelve a reservar",
                    )
                ],
            },
            False,
            1,
        ),
    )


def verdict_of(markdown: str) -> str:
    """El párrafo de veredicto del informe: la primera línea con texto tras «## Veredicto»."""
    lines = markdown.splitlines()
    if "## Veredicto" not in lines:
        return ""
    for line in lines[lines.index("## Veredicto") + 1 :]:
        if line.strip():
            return line.strip()
    return ""


def summary_of(stdout: str) -> str:
    """El resumen de una línea que `--out` escribe por stdout antes de «Informe escrito en»."""
    lines = [line for line in stdout.splitlines() if line.strip()]
    return lines[0].strip() if lines else ""


def question_blocks(markdown: str) -> list[tuple[str, list[str]]]:
    """Cada pregunta del informe: su encabezado «### Escenario: …» y sus opciones «- (X) …».

    Es la vista que tiene quien lee el informe, que es donde de verdad importa que
    no haya dos opciones iguales.
    """
    blocks: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    for line in markdown.splitlines():
        if line.startswith("### Escenario: "):
            current = (line[len("### Escenario: "):], [])
            blocks.append(current)
        elif line.startswith("## "):
            current = None
        elif current is not None and line.startswith("- ("):
            # «- (A) texto» → «texto», que es lo que compara quien lo lee.
            current[1].append(line.split(") ", 1)[-1])
    return blocks


def counted_sections(markdown: str) -> dict[str, tuple[int, int]]:
    """Las secciones «## Título · N» con (N anunciado, bloques que traen debajo).

    Un bloque es una pregunta «### Escenario: …» si la sección las trae; si no, cada
    punto de su lista. Las cuatro secciones con recuento deben contar lo mismo: lo
    que hay debajo.
    """
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            heading = line[len("## "):]
            current = None
            if " · " in heading:
                sections[heading] = current = []
            continue
        if current is not None:
            current.append(line)
    counted: dict[str, tuple[int, int]] = {}
    for heading, body in sections.items():
        title, _, announced = heading.rpartition(" · ")
        questions = [line for line in body if line.startswith("### Escenario: ")]
        bullets = [line for line in body if line.startswith("- ")]
        counted[title] = (int(announced), len(questions) if questions else len(bullets))
    return counted


@dataclass
class ChannelCase:
    """Un caso del barrido de coherencia: qué se le da al motor y qué debe contestar.

    `verdict`, `exit_code` y `converged` son la **misma** respuesta escrita tres
    veces; el test comprueba que los tres canales del programa la escriben igual.
    """

    name: str
    readers: dict
    verdict: str
    exit_code: int
    converged: bool
    strict: bool = False
    advocate: object | None = None
    extra_files: dict = field(default_factory=dict)


def channel_cases() -> tuple[ChannelCase, ...]:
    """Los seis veredictos, con las variantes que antes hacían discrepar a los canales."""
    agreed = [reading("Stock available", "crea la reserva", "201", ["stock reservado"])]
    soft = {
        "a": [reading("Reservation created", SOFT_A, "201")],
        "b": [reading("Reservation created", SOFT_B, "201")],
    }
    return (
        ChannelCase("convergen", {"a": list(agreed), "b": list(agreed)}, "converged", 0, True),
        ChannelCase("solo-blandas", soft, "soft_only", 0, False),
        ChannelCase("blandas-estrictas", soft, "soft_only", 1, False, strict=True),
        ChannelCase(
            "dura",
            {
                "a": [reading("Insufficient stock", "rechaza", "409")],
                "b": [reading("Insufficient stock", "rechaza", "422")],
            },
            "diverged",
            1,
            False,
        ),
        ChannelCase(
            "laguna",
            {
                "a": [reading("Payment retried", "vuelve a reservar", "200")],
                "b": [
                    reading(
                        "Payment retried",
                        "",
                        None,
                        unclear=True,
                        unclear_why="el delta no dice si el reintento vuelve a reservar",
                    )
                ],
            },
            "diverged",
            1,
            False,
        ),
        ChannelCase("un-solo-lector", {"a": list(agreed)}, "too_few_readers", 2, False),
        ChannelCase("sin-escenarios", {"a": [], "b": []}, "no_scenarios", 2, False),
        ChannelCase(
            "lector-mal-nombrado",
            {"a": list(agreed), "b": list(agreed)},
            "errors",
            2,
            False,
            extra_files={"readerb.json": "[]"},
        ),
        ChannelCase(
            "json-malformado",
            {"a": list(agreed), "b": "{ esto no es JSON"},
            "errors",
            2,
            False,
        ),
        ChannelCase(
            "abogado-ilegible",
            {"a": list(agreed), "b": list(agreed)},
            "errors",
            2,
            False,
            advocate="{ esto tampoco es JSON",
        ),
    )


def evidence_of(value: object) -> list[str]:
    """Los textos de una lectura que deben poder reconocerse en las opciones."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def read_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Parsea un frontmatter YAML **plano**; devuelve (claves, líneas que no lo son)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["el fichero no abre con «---» en la primera línea"]
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return {}, ["el frontmatter no cierra con «---»"]
    data: dict[str, str] = {}
    offenders: list[str] = []
    for line in lines[1:closing]:
        if not line.strip():
            continue
        match = FLAT_KEY_RE.match(line)
        if match is None:
            offenders.append(line)
            continue
        data[match.group("key")] = match.group("value").strip()
    return data, offenders


class DiffCase(unittest.TestCase):
    """Base común: un proyecto temporal y un atajo para correr el motor."""

    def setUp(self) -> None:
        # Sin andamio: este componente sólo necesita el directorio readings/.
        self.project = Project(scaffold=False)
        self.addCleanup(self.project.cleanup)

    def diff(self, readers: dict, *args: str, advocate: object | None = None) -> CompletedRun:
        """Escribe las lecturas en un change de usar y tirar y ejecuta el motor."""
        self.project.readings("d", readers, devils_advocate=advocate)
        return self.project.diff("d", *args)

    def assertNoTraceback(self, run: CompletedRun) -> None:
        """Ninguna traza de Python cruda llega al usuario."""
        self.assertNotIn(TRACEBACK, run.stderr, run.describe())
        self.assertNotIn(TRACEBACK, run.stdout, run.describe())


# ---------------------------------------------------------------------------
# Normalización: la base de todo lo demás
# ---------------------------------------------------------------------------


class TestNormalize(unittest.TestCase):
    """`normalize` es lo que decide si dos lecturas dicen lo mismo."""

    def test_normalize_folds_case(self):
        """Las mayúsculas no distinguen dos lecturas."""
        for left, right in (("reserva creada", "RESERVA CREADA"), ("409 Conflict", "409 conflict")):
            with self.subTest(left=left, right=right):
                self.assertEqual(diff_readings.normalize(left), diff_readings.normalize(right))

    def test_normalize_folds_accents(self):
        """Los acentos no distinguen dos lecturas: «reserva creada» = «RESERVA CREÁDA»."""
        for left, right in (
            ("reserva creada", "RESERVA CREÁDA"),
            ("peticion rechazada", "petición rechazada"),
        ):
            with self.subTest(left=left, right=right):
                self.assertEqual(diff_readings.normalize(left), diff_readings.normalize(right))

    def test_normalize_folds_punctuation(self):
        """La puntuación no distingue dos lecturas: «409.» = «409»."""
        for left, right in (("409.", "409"), ("«201»", "201"), ("409/422", "409 422")):
            with self.subTest(left=left, right=right):
                self.assertEqual(diff_readings.normalize(left), diff_readings.normalize(right))

    def test_normalize_collapses_whitespace(self):
        """Los espacios de más y los de los extremos no distinguen dos lecturas."""
        for left, right in (("a  b", "a b"), ("  reserva   creada  ", "reserva creada")):
            with self.subTest(left=left, right=right):
                self.assertEqual(diff_readings.normalize(left), diff_readings.normalize(right))

    def test_normalize_keeps_different_texts_apart(self):
        """Lo que de verdad es distinto sigue siéndolo después de normalizar."""
        for left, right in (
            ("409", "422"),
            ("reserva creada", "reserva cancelada"),
            ("stock reservado", "stock liberado"),
            ("", "201"),
        ):
            with self.subTest(left=left, right=right):
                self.assertNotEqual(diff_readings.normalize(left), diff_readings.normalize(right))

    def test_similarity_is_the_jaccard_index_of_the_content_tokens(self):
        """Jaccard exacto, pero sobre los tokens que dicen algo: 2/3 y 3/4."""
        # {reserv, cre} vs {reserv, cre, ttl}: «con» es palabra vacía.
        self.assertAlmostEqual(
            diff_readings.similarity("reserva creada", "reserva creada con TTL"), 2 / 3
        )
        # {reserv, marc, venc} vs {reserv, marc, venc, stock}.
        self.assertAlmostEqual(
            diff_readings.similarity(
                "la reserva se marca vencida", "la reserva se marca vencida sin stock"
            ),
            3 / 4,
        )

    def test_similarity_ignores_voice_and_conjugation(self):
        """La misma frase en activa y en pasiva converge: era el ruido que había que quitar."""
        for left, right in (
            ("registra el plazo como 21 dias naturales",
             "el plazo de entrega queda registrado como 21 dias naturales"),
            ("marca el plazo de entrega como ausente",
             "el plazo de entrega queda marcado como ausente"),
            ("el valor extraido original sigue siendo consultable",
             "el valor extraido originalmente sigue siendo consultable"),
        ):
            with self.subTest(left=left):
                self.assertGreaterEqual(
                    diff_readings.similarity(left, right), diff_readings.DEFAULT_THRESHOLD
                )

    # @covers R-DIV-004
    def test_similarity_never_dilutes_a_different_number(self):
        """Dos cifras distintas no describen el mismo efecto, compartan las palabras que compartan."""
        for left, right in (
            ("registra el plazo como 21 dias naturales",
             "registra el plazo como 14 dias naturales"),
            ("responde 409 y no crea la reserva", "responde 422 y no crea la reserva"),
            ("el plazo se registra en 21 dias", "el plazo se registra en tres semanas"),
        ):
            with self.subTest(left=left):
                self.assertEqual(diff_readings.similarity(left, right), 0.0)

    def test_similarity_still_matches_the_same_number_written_alike(self):
        """Blindar las cifras no puede romper el caso en que las dos lecturas coinciden."""
        self.assertGreaterEqual(
            diff_readings.similarity(
                "registra 123456 unidades minimas con moneda EUR",
                "el importe queda registrado como 123456 unidades minimas en EUR",
            ),
            diff_readings.DEFAULT_THRESHOLD,
        )

    def test_coverage_is_asymmetric_and_absorbs_a_grouped_effect(self):
        """Un lector que agrupa varios efectos en una frase recoge el que el otro separó."""
        grouped = "rechaza el fichero, indica los formatos validos y no crea presupuesto"
        self.assertGreaterEqual(
            diff_readings.coverage("no se crea ningun presupuesto", grouped),
            diff_readings.DEFAULT_THRESHOLD,
        )
        # Al revés no: la frase larga dice cosas que la corta no recoge.
        self.assertLess(
            diff_readings.coverage(grouped, "no se crea ningun presupuesto"),
            diff_readings.DEFAULT_THRESHOLD,
        )

    def test_coverage_does_not_absorb_an_effect_nobody_else_mentions(self):
        """Lo que un lector ve de más sigue quedando fuera: es la divergencia que importa."""
        self.assertLess(
            diff_readings.coverage("evento emitido al bus", "crea la reserva y reserva el stock"),
            diff_readings.DEFAULT_THRESHOLD,
        )


# ---------------------------------------------------------------------------
# La tabla de comparación de §7, una fila por test
# ---------------------------------------------------------------------------


class TestComparisonTable(DiffCase):
    """Cada fila de la tabla campo a campo del contrato §7."""

    # @covers R-DIV-001
    def test_different_status_codes_are_a_hard_divergence(self):
        """409 contra 422 en el mismo escenario es divergencia dura y exit 1."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock on one line", "rechaza", "409")],
                "b": [reading("Insufficient stock on one line", "rechaza", "422")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        payload = run.json
        self.assertEqual(payload["counts"]["hard"], 1, run.describe())
        self.assertFalse(payload["converged"])
        divergence = payload["divergences"][0]
        self.assertEqual(divergence["field"], "status_code")
        self.assertEqual(divergence["hardness"], "hard")
        self.assertEqual(divergence["readings"], {"reader-a": "409", "reader-b": "422"})

    def test_a_null_status_code_against_a_present_one_is_status_code_absent(self):
        """Uno da código y el otro no: dura, y de tipo distinto al desacuerdo de códigos."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock on one line", "rechaza", "409")],
                "b": [reading("Insufficient stock on one line", "rechaza", None)],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        divergence = run.json["divergences"][0]
        self.assertEqual(divergence["field"], "status_code_absent")
        self.assertNotEqual(divergence["field"], "status_code")
        self.assertEqual(divergence["hardness"], "hard")
        self.assertEqual(divergence["readings"], {"reader-a": "409", "reader-b": None})

    def test_a_side_effects_set_difference_is_a_soft_divergence(self):
        """Un efecto colateral que sólo ve un lector, y nadie niega, es blando.

        Antes esto era duro. Dejó de serlo con `R-DIV-005`: la categoría dura
        afirma que las dos lecturas no pueden ser correctas a la vez, y eso no
        es cierto de un lector que dedujo una consecuencia más del contexto sin
        que el otro la contradiga.
        """
        run = self.diff(
            {
                "a": [reading("Stock available", "ok", "201", ["stock reservado", "evento emitido"])],
                "b": [reading("Stock available", "ok", "201", ["stock reservado"])],
            },
            "--json",
        )
        divergence = run.json["divergences"][0]
        self.assertEqual(divergence["field"], "side_effects")
        self.assertEqual(divergence["hardness"], "soft", run.describe())

    def test_the_same_side_effects_in_a_different_order_do_not_diverge(self):
        """`side_effects` es un conjunto, no una lista: el orden no es un desacuerdo."""
        run = self.diff(
            {
                "a": [reading("Stock available", "ok", "201", ["stock reservado", "evento emitido"])],
                "b": [reading("Stock available", "ok", "201", ["evento emitido", "stock reservado"])],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.json["divergences"], [], run.describe())
        self.assertTrue(run.json["converged"])

    def test_the_same_effects_split_between_fields_converge(self):
        """El reparto entre «effect» y «side_effects» no es una divergencia.

        Los dos lectores leen lo mismo y lo colocan distinto: uno escribe los
        tres efectos seguidos en «effect» y el otro deja el tercero como efecto
        colateral. Ninguno se ha equivocado. Cuando esto se comparaba campo
        contra campo salía como divergencia **dura** —la categoría que afirma
        que las lecturas no pueden ser todas correctas—, y era el ruido que
        vaciaba de sentido el informe.
        """
        run = self.diff(
            {
                "a": [
                    reading(
                        "Unsupported format",
                        "rechaza el fichero, indica los formatos validos y no crea presupuesto",
                        "415",
                    )
                ],
                "b": [
                    reading(
                        "Unsupported format",
                        "rechaza el fichero e indica los formatos validos",
                        "415",
                        ["no se crea ningun presupuesto"],
                    )
                ],
            },
            "--json",
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertEqual(hard, [], run.describe())

    def test_an_effect_that_nobody_else_mentions_is_reported_as_soft(self):
        """Lo que un lector ve y el otro no ve en ningún campo se sigue denunciando.

        Es el contrapunto del test de arriba: aflojar el emparejamiento no puede
        tragarse el caso que esta comparación existe para encontrar. Lo que
        cambia con `R-DIV-005` es la **categoría**, no que se denuncie: nadie
        niega el evento, así que la divergencia es blanda y sigue apareciendo
        en el informe con su pregunta y sus opciones.
        """
        run = self.diff(
            {
                "a": [
                    reading(
                        "Stock available",
                        "crea la reserva",
                        "201",
                        ["stock reservado", "evento emitido al bus"],
                    )
                ],
                "b": [reading("Stock available", "crea la reserva", "201", ["stock reservado"])],
            },
            "--json",
        )
        side = [d for d in run.json["divergences"] if d["field"] == "side_effects"]
        self.assertEqual(len(side), 1, run.describe())
        self.assertEqual(side[0]["hardness"], "soft", run.describe())
        joined = " | ".join(side[0]["options"])
        self.assertIn("evento emitido al bus", joined, run.describe())
        self.assertNotIn("stock reservado", joined, run.describe())

    def test_an_opposite_polarity_side_effect_is_hard(self):
        """R-DIV-005 · La misma frase con la polaridad cambiada sí es contradicción.

        «no se crea el presupuesto» y «se crea el presupuesto» hablan de lo
        mismo y no pueden ser las dos verdad. Es lo que distingue contradecir
        de añadir, y lo que la categoría dura tiene que seguir cazando.
        """
        run = self.diff(
            {
                "a": [reading("Budget", "procesa la solicitud", "200", ["no se crea el presupuesto"])],
                "b": [reading("Budget", "procesa la solicitud", "200", ["se crea el presupuesto"])],
            },
            "--json",
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertEqual(len(hard), 1, run.describe())
        self.assertEqual(hard[0]["field"], "side_effects", run.describe())
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_different_number_in_a_side_effect_is_hard(self):
        """R-DIV-005 · La misma frase con otra cifra es contradicción, no añadido."""
        run = self.diff(
            {
                "a": [reading("Hold", "reserva el stock", "201", ["la reserva dura 15 minutos"])],
                "b": [reading("Hold", "reserva el stock", "201", ["la reserva dura 30 minutos"])],
            },
            "--json",
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertEqual(len(hard), 1, run.describe())
        self.assertEqual(hard[0]["field"], "side_effects", run.describe())

    def test_a_scope_marker_difference_is_hard(self):
        """R-DIV-005 · «completo» frente a «solo …» es una contradicción de alcance.

        Es el caso del fixture `ambiguous-partial-effect`: ninguna de las dos
        frases lleva negación ni cifra, y aun así no pueden ser las dos
        ciertas. Sin esta señal la regla nueva convertiría el falso positivo en
        un falso negativo.
        """
        run = self.diff(
            {
                "a": [reading("Partial", "reserva", "201", ["reserva creada para el pedido completo"])],
                "b": [
                    reading(
                        "Partial",
                        "reserva",
                        "201",
                        ["reserva creada solo para las unidades con stock"],
                    )
                ],
            },
            "--json",
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertEqual(len(hard), 1, run.describe())
        self.assertEqual(hard[0]["field"], "side_effects", run.describe())

    def test_a_detail_added_to_the_same_effect_is_not_a_contradiction(self):
        """R-DIV-005 · El techo del detector: compartir palabras no es contradecir.

        Ataque del abogado del diablo: un detector que declare contradicción en
        cuanto dos efectos comparten palabras significativas cumpliría el
        fixture y los escenarios de polaridad, y devolvería duras todas las
        diferencias de detalle — reinstaurando el falso positivo que este
        cambio existe para quitar.
        """
        run = self.diff(
            {
                "a": [reading("Hold", "reserva", "201", ["se reserva el stock y se anota la reserva"])],
                "b": [reading("Hold", "reserva", "201", ["se reserva el stock"])],
            },
            "--json",
        )
        # El detalle de más queda **recogido** por la frase que lo agrupa, así
        # que aquí ni siquiera hay divergencia: es el mejor resultado posible, y
        # lo que el contrato prohíbe es que salga dura.
        self.assertEqual(
            [d for d in run.json["divergences"] if d["hardness"] == "hard"],
            [],
            run.describe(),
        )
        self.assertEqual(run.returncode, 0, run.describe())

    def test_a_reinforced_negation_is_the_same_polarity(self):
        """R-DIV-005 · Negar con dos partículas es negar lo mismo, no discrepar.

        «no se crea ningún presupuesto» y «no crea presupuesto» dicen lo mismo:
        la negación se mira como interruptor, no como conjunto de partículas, o
        el refuerzo se convertiría en un desacuerdo inventado.
        """
        run = self.diff(
            {
                "a": [reading("Budget", "rechaza", "422", ["no se crea ningun presupuesto"])],
                "b": [reading("Budget", "rechaza", "422", ["no crea presupuesto"])],
            },
            "--json",
        )
        self.assertEqual(
            [d for d in run.json["divergences"] if d["hardness"] == "hard"],
            [],
            run.describe(),
        )

    def test_sin_as_a_preposition_is_not_a_negation(self):
        """R-DIV-005 · «sin» introduce un complemento mucho más veces que niega.

        Caso real, cazado al pasar el motor nuevo sobre el delta de
        `2026-09-06-forgejo-only`: «el job termina en fallo sin llegar al
        checkout» y «el job falla antes del checkout» dicen lo mismo, y la
        primera versión de las marcas las declaraba incompatibles porque una
        llevaba «sin». En prosa técnica española «sin tocar», «sin llegar a» y
        «sin que» son preposición, no negación del predicado, y contarlas
        reinstauraba el falso positivo justo donde este cambio lo quitaba.
        """
        run = self.diff(
            {
                "a": [
                    reading(
                        "Ref",
                        "el job falla",
                        None,
                        ["el job falla antes del checkout"],
                    )
                ],
                "b": [
                    reading(
                        "Ref",
                        "el job falla",
                        None,
                        ["el job termina en fallo sin llegar al checkout"],
                    )
                ],
            },
            "--json",
        )
        self.assertEqual(
            [d for d in run.json["divergences"] if d["hardness"] == "hard"],
            [],
            run.describe(),
        )

    def test_a_negation_inside_a_subordinate_clause_is_not_a_contradiction(self):
        """R-DIV-005 · Una negación tras «que» califica la condición, no el efecto.

        Segundo caso real cazado al pasar el motor nuevo sobre el delta de
        `2026-09-06-forgejo-only`: un lector escribe el efecto a secas («el job
        queda en fallo») y el otro se trae la condición dentro («un oráculo
        **que no** termina en verde deja el job en fallo»). Dicen lo mismo, y
        contar ese «no» como polaridad del efecto los declaraba incompatibles.
        """
        run = self.diff(
            {
                "a": [reading("Oracle", "el paso falla", None, ["el job del consumidor queda en fallo"])],
                "b": [
                    reading(
                        "Oracle",
                        "un oraculo que no termina en verde deja el job en fallo",
                        None,
                        [],
                    )
                ],
            },
            "--json",
        )
        self.assertEqual(
            [d for d in run.json["divergences"] if d["hardness"] == "hard"],
            [],
            run.describe(),
        )

    def test_a_negation_that_opens_the_clause_still_contradicts(self):
        """R-DIV-005 · La excepción es sólo para la subordinada, no para todo.

        Sin este contrapunto, ignorar las negaciones tras «que» podría
        extenderse hasta desactivar la señal entera.
        """
        run = self.diff(
            {
                "a": [reading("Budget", "procesa", "200", ["no se crea el presupuesto"])],
                "b": [reading("Budget", "procesa", "200", ["se crea el presupuesto"])],
            },
            "--json",
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertEqual(len(hard), 1, run.describe())

    def test_an_unrelated_added_side_effect_stays_soft(self):
        """R-DIV-005 · Un efecto que no se parece a nada del otro repertorio sólo añade."""
        run = self.diff(
            {
                "a": [reading("Mail", "responde al cliente", "200", ["se envia un correo al cliente"])],
                "b": [reading("Mail", "responde al cliente", "200", [])],
            },
            "--json",
        )
        self.assertEqual(
            [d["hardness"] for d in run.json["divergences"] if d["field"] == "side_effects"],
            ["soft"],
            run.describe(),
        )

    def test_a_granularity_difference_does_not_block_the_run(self):
        """R-DIV-005 · El caso que bloqueaba `2026-09-04-oracle`, de punta a punta.

        Los dos lectores dicen lo mismo con otras palabras y reparten distinto
        entre `effect` y `side_effects`. Antes salía con código 1 y cuatro
        rondas no lo arreglaban; ahora no hay ninguna dura y la ejecución no
        falla.
        """
        run = self.diff(
            {
                "a": [
                    reading(
                        "Oracle",
                        "invoca el oraculo por cada change",
                        None,
                        ["se ejecutan los tests reales del change"],
                    )
                ],
                "b": [
                    reading(
                        "Oracle",
                        "invoca el oraculo por cada change",
                        None,
                        ["ejecucion real del test command"],
                    )
                ],
            },
            "--json",
        )
        self.assertEqual(
            [d for d in run.json["divergences"] if d["hardness"] == "hard"],
            [],
            run.describe(),
        )
        self.assertEqual(run.returncode, 0, run.describe())

    def test_the_report_says_that_a_hard_one_contradicts(self):
        """R-DIV-006 · Una dura de colaterales dice que el otro lector la contradice."""
        run = self.diff(
            {
                "a": [reading("Budget", "procesa", "200", ["no se crea el presupuesto"])],
                "b": [reading("Budget", "procesa", "200", ["se crea el presupuesto"])],
            },
        )
        self.assertIn("lo contradice", run.stdout, run.describe())

    def test_the_report_says_that_a_soft_one_only_adds(self):
        """R-DIV-006 · Una blanda de colaterales dice que nadie la contradice."""
        run = self.diff(
            {
                "a": [reading("Mail", "responde", "200", ["se envia un correo al cliente"])],
                "b": [reading("Mail", "responde", "200", [])],
            },
        )
        self.assertIn("nadie lo contradice", run.stdout, run.describe())

    def test_the_known_hard_eval_fixture_keeps_its_hard_divergence(self):
        """R-DIV-007 · `ambiguous-partial-effect` sigue dando su dura en side_effects.

        Es el criterio de aceptación de `R-DIV-005`, no un efecto colateral: si
        aflojar la regla se lleva por delante esta cifra, se ha cambiado el
        falso positivo por un falso negativo y la regla está mal.
        """
        fixture = (
            REPO_ROOT
            / "evals"
            / "ambiguous-partial-effect"
            / "project"
            / ".venoxia"
            / "changes"
            / "2026-08-31-partial-reservation"
            / "readings"
        )
        self.assertTrue(fixture.is_dir(), f"falta el fixture «{fixture}»")
        run = self.project.run(
            DIFF_READINGS_PY, "--readings", str(fixture), "--json", "--no-color"
        )
        hard = [d for d in run.json["divergences"] if d["hardness"] == "hard"]
        self.assertTrue(hard, run.describe())
        self.assertIn("side_effects", [d["field"] for d in hard], run.describe())

    def test_an_effect_below_the_threshold_is_a_soft_divergence(self):
        """Dos lecturas que discrepan sin que ninguna pieza estructurada las separe: blanda."""
        run = self.diff(
            {
                "a": [reading("Reservation created", SOFT_A, "201")],
                "b": [reading("Reservation created", SOFT_B, "201")],
            },
            "--json",
        )
        payload = run.json
        self.assertEqual(payload["counts"]["soft"], 1, run.describe())
        self.assertEqual(payload["counts"]["hard"], 0, run.describe())
        self.assertEqual(payload["divergences"][0]["field"], "effect")
        self.assertEqual(payload["divergences"][0]["hardness"], "soft")

    def test_an_effect_above_the_threshold_does_not_diverge(self):
        """«…de 15 minutos» vs «…de 15 min»: Jaccard 6/8 = 0.75 ≥ 0.6, no salta nada."""
        run = self.diff(
            {
                "a": [reading("Reservation created", "reserva creada con TTL de 15 minutos", "201")],
                "b": [reading("Reservation created", "reserva creada con TTL de 15 min", "201")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.json["counts"]["soft"], 0, run.describe())
        self.assertEqual(run.json["divergences"], [])

    def test_an_unclear_reading_is_reported_as_a_gap(self):
        """`unclear: true` en cualquier lector es una laguna y hace fallar con exit 1."""
        run = self.diff(
            {
                "a": [reading("Payment retried after expiry", "vuelve a reservar", "200")],
                "b": [
                    reading(
                        "Payment retried after expiry",
                        "",
                        None,
                        unclear=True,
                        unclear_why="el delta no dice si el reintento vuelve a reservar",
                    )
                ],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        payload = run.json
        self.assertEqual(payload["counts"]["gaps"], 1, run.describe())
        self.assertEqual(payload["gaps"][0]["reader"], "reader-b")
        self.assertEqual(payload["gaps"][0]["scenario"], "Payment retried after expiry")
        self.assertIn("reintento", payload["gaps"][0]["why"])

    def test_a_scenario_only_one_reader_sees_is_a_missing_scenario(self):
        """Un escenario presente en un lector y ausente en otro es dura, tipo missing_scenario."""
        run = self.diff(
            {
                "a": [
                    reading("Stock available", "ok", "201"),
                    reading("Reservation expires", "libera el stock", "200"),
                ],
                "b": [reading("Stock available", "ok", "201")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        divergence = run.json["divergences"][0]
        self.assertEqual(divergence["field"], "missing_scenario")
        self.assertEqual(divergence["hardness"], "hard")
        self.assertEqual(divergence["scenario"], "Reservation expires")

    def test_total_convergence_exits_zero_with_no_divergences(self):
        """Dos lecturas idénticas: exit 0, `converged: true` y cero divergencias."""
        agreed = [
            reading("Stock available", "crea la reserva", "201", ["stock reservado"]),
            reading("Insufficient stock", "rechaza la peticion", "409", []),
        ]
        run = self.diff({"a": list(agreed), "b": list(agreed)}, "--json")
        self.assertEqual(run.returncode, 0, run.describe())
        payload = run.json
        self.assertTrue(payload["converged"], run.describe())
        self.assertEqual(payload["divergences"], [])
        self.assertEqual(payload["gaps"], [])
        self.assertEqual(
            payload["counts"], {"hard": 0, "soft": 0, "gaps": 0, "scenarios": 2, "readers": 2}
        )


# ---------------------------------------------------------------------------
# La salida es el producto: preguntas cerradas, nunca abiertas
# ---------------------------------------------------------------------------


class TestClosedQuestions(DiffCase):
    """Cada desacuerdo sale como una pregunta cerrada con las lecturas enfrentadas."""

    def test_every_divergence_carries_a_closed_question(self):
        """Toda divergencia trae una pregunta que acaba en «?» y al menos dos opciones."""
        run = self.diff(rich_readings(), "--json")
        divergences = run.json["divergences"]
        self.assertGreaterEqual(len(divergences), 4, run.describe())
        for divergence in divergences:
            with self.subTest(scenario=divergence["scenario"], field=divergence["field"]):
                self.assertTrue(divergence["question"].endswith("?"), divergence["question"])
                self.assertTrue(divergence["question"].startswith("¿"), divergence["question"])
                self.assertGreaterEqual(len(divergence["options"]), 2, divergence["options"])

    def test_the_options_of_every_divergence_echo_the_readings_they_confront(self):
        """Cada lectura enfrentada se reconoce literalmente en alguna opción."""
        run = self.diff(rich_readings(), "--json")
        for divergence in run.json["divergences"]:
            joined = " | ".join(divergence["options"])
            for reader, value in divergence["readings"].items():
                for fragment in evidence_of(value):
                    with self.subTest(field=divergence["field"], reader=reader, text=fragment):
                        self.assertIn(fragment, joined)

    def test_the_status_code_question_confronts_both_codes(self):
        """La pregunta de 409 contra 422 ofrece las dos respuestas, no una abierta."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock on one line", "rechaza", "409")],
                "b": [reading("Insufficient stock on one line", "rechaza", "422")],
            },
            "--json",
        )
        divergence = run.json["divergences"][0]
        self.assertIn("Insufficient stock on one line", divergence["question"])
        self.assertEqual(len(divergence["options"]), 2, divergence["options"])
        self.assertIn("409", divergence["options"][0])
        self.assertIn("422", divergence["options"][1])

    def test_the_markdown_report_asks_the_question_with_lettered_options(self):
        """El informe markdown imprime la pregunta en negrita y sus opciones con letra."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock on one line", "rechaza", "409")],
                "b": [reading("Insufficient stock on one line", "rechaza", "422")],
            },
        )
        self.assertIn("### Escenario: Insufficient stock on one line", run.stdout)
        self.assertIn("**¿Qué código de estado", run.stdout)
        self.assertIn("- (A) 409", run.stdout)
        self.assertIn("- (B) 422", run.stdout)

    def test_the_report_never_asks_an_open_question(self):
        """Ni «¿hay algo ambiguo?» ni «¿algo que aclarar?» aparecen en ninguna parte."""
        advocate = {
            "attack": "Reservar sólo la primera línea cumple el delta y deja al cliente sin stock.",
            "requirement_id": "R-CHK-014",
            "severity": "high",
        }
        markdown = self.diff(rich_readings(), advocate=advocate)
        payload = self.diff(rich_readings(), "--json", advocate=advocate)
        for label, text in (("markdown", markdown.stdout), ("json", payload.stdout)):
            lowered = text.lower()
            for open_question in OPEN_QUESTIONS:
                with self.subTest(salida=label, pregunta=open_question):
                    self.assertNotIn(open_question, lowered)

    def test_the_gap_question_is_closed_too(self):
        """Una laguna también se cierra con una pregunta y opciones, no con un «¿qué opinas?»."""
        run = self.diff(
            {
                "a": [reading("Payment retried after expiry", "vuelve a reservar", "200")],
                "b": [
                    reading(
                        "Payment retried after expiry",
                        "",
                        None,
                        unclear=True,
                        unclear_why="el delta no dice si el reintento vuelve a reservar",
                    )
                ],
            },
        )
        self.assertIn("**¿Qué debe ocurrir en «Payment retried after expiry»?**", run.stdout)
        self.assertIn("- (A) ", run.stdout)
        self.assertIn("- (B) ", run.stdout)


class TestThreeReaders(DiffCase):
    """Tres lectores no son dos: la pregunta debe enfrentar las tres lecturas."""

    def test_three_readers_produce_a_three_way_question(self):
        """Con 409, 422 y 400 la pregunta ofrece las tres opciones y nombra a los tres."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock", "rechaza", "409")],
                "b": [reading("Insufficient stock", "rechaza", "422")],
                "c": [reading("Insufficient stock", "rechaza", "400")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        payload = run.json
        self.assertEqual(payload["counts"]["readers"], 3)
        divergence = payload["divergences"][0]
        self.assertEqual(
            divergence["readings"], {"reader-a": "409", "reader-b": "422", "reader-c": "400"}
        )
        self.assertEqual(len(divergence["options"]), 3, divergence["options"])
        for code in ("409", "422", "400"):
            with self.subTest(code=code):
                self.assertTrue(
                    any(code in option for option in divergence["options"]), divergence["options"]
                )


# ---------------------------------------------------------------------------
# El esquema JSON estable del contrato §7
# ---------------------------------------------------------------------------


class TestJsonSchema(DiffCase):
    """`--json` es el contrato con el resto del sistema: sus claves no se mueven."""

    def test_json_has_exactly_the_top_level_keys_of_the_contract(self):
        """Ni una clave de más ni una de menos en el primer nivel, y en su orden."""
        run = self.diff(rich_readings(), "--json")
        self.assertEqual(list(run.json.keys()), TOP_LEVEL_KEYS, run.describe())

    def test_json_counts_has_exactly_the_contract_subkeys(self):
        """`counts` trae hard, soft, gaps, scenarios y readers, y nada más."""
        run = self.diff(rich_readings(), "--json")
        self.assertEqual(list(run.json["counts"].keys()), COUNT_KEYS, run.describe())

    def test_json_version_is_one(self):
        """El esquema es la versión 1 del contrato."""
        run = self.diff(rich_readings(), "--json")
        self.assertEqual(run.json["version"], 1)

    def test_every_divergence_entry_has_the_contract_keys(self):
        """Cada divergencia trae scenario, field, hardness, readings, question y options."""
        run = self.diff(rich_readings(), "--json")
        for divergence in run.json["divergences"]:
            with self.subTest(field=divergence["field"]):
                self.assertEqual(list(divergence.keys()), DIVERGENCE_KEYS)

    def test_every_gap_entry_has_the_contract_keys(self):
        """Cada laguna trae scenario, reader y why."""
        run = self.diff(rich_readings(), "--json")
        self.assertTrue(run.json["gaps"], run.describe())
        for gap in run.json["gaps"]:
            with self.subTest(reader=gap.get("reader")):
                self.assertEqual(list(gap.keys()), GAP_KEYS)

    def test_the_counts_add_up_to_the_divergences_reported(self):
        """`counts` no es prosa: cuenta exactamente lo que trae la lista de divergencias."""
        run = self.diff(rich_readings(), "--json")
        payload = run.json
        hard = [d for d in payload["divergences"] if d["hardness"] == "hard"]
        soft = [d for d in payload["divergences"] if d["hardness"] == "soft"]
        self.assertEqual(payload["counts"]["hard"], len(hard), run.describe())
        self.assertEqual(payload["counts"]["soft"], len(soft), run.describe())
        self.assertEqual(payload["counts"]["gaps"], len(payload["gaps"]), run.describe())
        self.assertEqual(payload["counts"]["scenarios"], 5, run.describe())


# ---------------------------------------------------------------------------
# El veredicto no se contradice a sí mismo
# ---------------------------------------------------------------------------


class TestVerdictCoherence(DiffCase):
    """`converged`, `counts` y el texto del veredicto cuentan siempre lo mismo.

    `converged` contesta «¿coinciden las lecturas?» y el código de salida contesta
    «¿falla la ejecución?»: son dos preguntas distintas. Derivar la primera de la
    segunda hacía que el informe afirmase la convergencia tres líneas antes de
    listar la divergencia blanda que acababa de encontrar.
    """

    def test_converged_is_zero_disagreements_not_a_zero_exit_code(self):
        """`converged` es «cero duras, cero blandas y cero lagunas», en los tres casos."""
        for name, readers, expected_converged, expected_exit in coherence_cases():
            with self.subTest(caso=name):
                self.project.readings(name, readers)
                run = self.project.diff(name, "--json")
                payload = run.json
                counts = payload["counts"]
                self.assertEqual(run.returncode, expected_exit, run.describe())
                self.assertIs(payload["converged"], expected_converged, run.describe())
                self.assertEqual(
                    payload["converged"],
                    counts["hard"] == 0 and counts["soft"] == 0 and counts["gaps"] == 0,
                    run.describe(),
                )
                self.assertEqual(
                    len(payload["divergences"]),
                    counts["hard"] + counts["soft"],
                    run.describe(),
                )
                self.assertEqual(bool(payload["divergences"]) or bool(payload["gaps"]),
                                 not payload["converged"], run.describe())

    def test_the_verdict_sentence_never_contradicts_the_sections_below_it(self):
        """Si el informe lista algún desacuerdo, el veredicto no afirma que convergen."""
        for name, readers, expected_converged, _ in coherence_cases():
            with self.subTest(caso=name):
                self.project.readings(name, readers)
                run = self.project.diff(name)
                verdict = verdict_of(run.stdout)
                self.assertTrue(verdict, run.describe())
                if expected_converged:
                    self.assertIn("**Las lecturas convergen.**", verdict, run.describe())
                    self.assertNotIn("## Divergencias", run.stdout, run.describe())
                    self.assertNotIn("## Lagunas", run.stdout, run.describe())
                else:
                    self.assertNotIn("**Las lecturas convergen.**", verdict, run.describe())
                    self.assertTrue(
                        "## Divergencias" in run.stdout or "## Lagunas" in run.stdout,
                        run.describe(),
                    )

    def test_a_soft_only_verdict_names_the_vocabulary_and_says_it_does_not_fail(self):
        """Con sólo blandas el veredicto avisa de que puede ser vocabulario y que no tumba nada."""
        self.project.readings(
            "blandas",
            {
                "a": [reading("Reservation created", SOFT_A, "201")],
                "b": [reading("Reservation created", SOFT_B, "201")],
            },
        )
        run = self.project.diff("blandas")
        self.assertEqual(run.returncode, 0, run.describe())
        verdict = verdict_of(run.stdout).lower()
        self.assertNotIn("las lecturas convergen.", verdict, run.describe())
        self.assertIn("vocabulario", verdict, run.describe())
        self.assertIn("no hacen fallar", verdict, run.describe())
        self.assertIn("## Divergencias blandas · 1", run.stdout, run.describe())

    def test_a_scenario_with_a_soft_divergence_is_not_listed_as_converging(self):
        """«Escenarios que convergen» lista sólo los escenarios sin ningún desacuerdo."""
        self.project.readings(
            "mixto",
            {
                "a": [
                    reading("Stock available", "crea la reserva", "201"),
                    reading("Reservation created", SOFT_A, "201"),
                ],
                "b": [
                    reading("Stock available", "crea la reserva", "201"),
                    reading("Reservation created", SOFT_B, "201"),
                ],
            },
        )
        run = self.project.diff("mixto")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("## Escenarios que convergen · 1", run.stdout, run.describe())
        converging = run.stdout.split("## Escenarios que convergen · 1", 1)[1]
        self.assertIn("- Stock available", converging, run.describe())
        self.assertNotIn("- Reservation created", converging, run.describe())


class TestVerdictArithmetic(unittest.TestCase):
    """El veredicto, su marcador, su color y su código de salida son funciones puras.

    Se prueban aquí a pelo porque hay cosas que el subproceso no puede enseñar: el
    color ANSI sólo sale si stdout es un terminal, y una suite que corre por tubería
    no lo ve nunca. Que `--strict` con sólo blandas se pintase de amarillo mientras
    la ejecución fallaba era exactamente eso: un fallo invisible desde fuera.
    """

    def test_every_verdict_has_a_headline_and_an_exit_code(self):
        """Los seis veredictos, con su código de salida con y sin `--strict`."""
        expected = {
            ("errors", False): 2,
            ("errors", True): 2,
            ("too_few_readers", False): 2,
            ("too_few_readers", True): 2,
            ("no_scenarios", False): 2,
            ("no_scenarios", True): 2,
            ("diverged", False): 1,
            ("diverged", True): 1,
            ("soft_only", False): 0,
            ("soft_only", True): 1,
            ("converged", False): 0,
            ("converged", True): 0,
        }
        self.assertEqual({code for code, _ in expected}, set(diff_readings.VERDICT_HEADLINES))
        for (code, strict), exit_code in expected.items():
            with self.subTest(veredicto=code, strict=strict):
                self.assertEqual(diff_readings.exit_code_for(code, strict), exit_code)
                self.assertTrue(diff_readings.VERDICT_HEADLINES[code].strip())

    def test_the_marker_and_the_colour_follow_the_execution_not_the_hardness(self):
        """✓ sólo si convergen, ⚠ sólo si no falla, ✗ siempre que falle. Con `--strict` también."""
        cases = (
            ("converged", False, "✓", diff_readings.ANSI_GREEN),
            ("soft_only", False, "⚠", diff_readings.ANSI_YELLOW),
            ("soft_only", True, "✗", diff_readings.ANSI_RED),
            ("diverged", False, "✗", diff_readings.ANSI_RED),
            ("too_few_readers", False, "✗", diff_readings.ANSI_RED),
            ("no_scenarios", False, "✗", diff_readings.ANSI_RED),
            ("errors", False, "✗", diff_readings.ANSI_RED),
        )
        for code, strict, marker, colour in cases:
            with self.subTest(veredicto=code, strict=strict):
                verdict = diff_readings.Verdict(
                    code=code, strict=strict, exit_code=diff_readings.exit_code_for(code, strict)
                )
                self.assertEqual(verdict.marker, marker)
                self.assertEqual(diff_readings.verdict_color(verdict), colour)
                self.assertIs(verdict.converged, code == "converged")

    def test_status_key_unifies_a_code_with_its_canonical_reason(self):
        """«409» y «409 Conflict» son la misma respuesta, aquí y en la pregunta."""
        for left, right in (
            ("409", "409 Conflict"),
            ("201", "201 created"),
            ("422", "422 Unprocessable Entity"),
            ("418", "418 I'm a teapot"),
        ):
            with self.subTest(izquierda=left, derecha=right):
                self.assertEqual(diff_readings.status_key(left), diff_readings.status_key(right))

    def test_status_key_keeps_anything_else_apart(self):
        """Unificar por el número a secas callaría un desacuerdo real: «409 Gone» no es «409»."""
        for left, right in (
            ("409", "409 Gone"),
            ("409", "422"),
            ("409 Conflict", "410 Gone"),
            ("409", None),
            ("200", "200 porque el stock ya estaba reservado"),
        ):
            with self.subTest(izquierda=left, derecha=right):
                self.assertNotEqual(diff_readings.status_key(left), diff_readings.status_key(right))

    def test_distinct_options_never_leaves_a_question_unanswerable(self):
        """Ni dos opciones iguales ni menos de dos, venga la pregunta de donde venga."""
        for options in ([], ["a"], ["a", "a"], ["a", "a", "a"], ["a", "b", "a"]):
            with self.subTest(opciones=options):
                result = diff_readings.distinct_options(list(options))
                self.assertGreaterEqual(len(result), 2, result)
                self.assertEqual(len(set(result)), len(result), result)
        # Lo que ya era correcto no se toca: mismo orden y mismas opciones.
        self.assertEqual(diff_readings.distinct_options(["b", "a", "c"]), ["b", "a", "c"])


class TestChannelCoherence(DiffCase):
    """El barrido: los tres canales cuentan la misma historia del mismo hecho.

    El producto de esta herramienta es un informe que una persona lee y responde,
    y hay tres sitios donde puede leerlo: el markdown, el JSON y el resumen que
    `--out` deja por stdout. Cualquier hecho que los tres puedan contar distinto
    —si converge, si iba `--strict`, con qué código sale— es un fallo del
    producto, así que se comprueban **a la vez**, caso por caso, en vez de uno a
    uno y a mano.
    """

    def channels(self, case: ChannelCase):
        """Escribe el caso y lo ejecuta por los tres canales; devuelve las tres salidas."""
        self.project.readings(case.name, case.readers, devils_advocate=case.advocate)
        for filename, content in case.extra_files.items():
            self.project.write(f".venoxia/changes/{case.name}/readings/{filename}", content)
        flags = ("--strict",) if case.strict else ()
        target = self.project.path(f"informes/{case.name}.md")
        return (
            self.project.diff(case.name, "--json", *flags),
            self.project.diff(case.name, *flags),
            self.project.diff(case.name, "--out", str(target), *flags),
            target,
        )

    def test_the_three_channels_agree_on_the_verdict_of_every_case(self):
        """Mismo veredicto, mismo `strict` y mismo código de salida por los tres canales."""
        for case in channel_cases():
            with self.subTest(caso=case.name):
                json_run, markdown_run, out_run, target = self.channels(case)
                for run in (json_run, markdown_run, out_run):
                    self.assertNoTraceback(run)
                    self.assertEqual(run.returncode, case.exit_code, run.describe())

                payload = json_run.json
                self.assertEqual(payload["verdict"], case.verdict, json_run.describe())
                self.assertIs(payload["converged"], case.converged, json_run.describe())
                self.assertIs(payload["strict"], case.strict, json_run.describe())
                self.assertEqual(payload["exit_code"], json_run.returncode, json_run.describe())

                headline = diff_readings.VERDICT_HEADLINES[case.verdict]
                marker = "✓" if case.converged else ("⚠" if case.exit_code == 0 else "✗")

                verdict = verdict_of(markdown_run.stdout)
                self.assertTrue(
                    verdict.startswith(f"**{headline}.**"), f"{verdict}\n{markdown_run.describe()}"
                )
                self.assertIn(
                    f"Esta ejecución sale con código {case.exit_code}.", verdict, markdown_run.describe()
                )
                for code, other in diff_readings.VERDICT_HEADLINES.items():
                    if code != case.verdict:
                        with self.subTest(caso=case.name, titular=code):
                            self.assertNotIn(f"**{other}.**", markdown_run.stdout, markdown_run.describe())

                summary = summary_of(out_run.stdout)
                self.assertTrue(
                    summary.startswith(f"{marker} {headline} ·"), f"{summary}\n{out_run.describe()}"
                )
                self.assertIn(f"salida {case.exit_code}", summary, out_run.describe())

    def test_the_report_says_what_this_invocation_did_by_the_three_channels(self):
        """`--strict` y el código de salida están en el informe, no sólo en el código de retorno."""
        for case in channel_cases():
            with self.subTest(caso=case.name):
                json_run, markdown_run, out_run, target = self.channels(case)
                declared = "sí" if case.strict else "no"
                self.assertIn(
                    f"- **Modo estricto (`--strict`):** {declared}",
                    markdown_run.stdout,
                    markdown_run.describe(),
                )
                self.assertIn(
                    f"- **Código de salida:** {case.exit_code}",
                    markdown_run.stdout,
                    markdown_run.describe(),
                )
                if case.strict:
                    self.assertIn("`--strict`", summary_of(out_run.stdout), out_run.describe())
                # El informe es el mismo por fichero que por stdout: `--out` no es otra versión.
                self.assertEqual(
                    target.read_text(encoding="utf-8"), markdown_run.stdout, out_run.describe()
                )

    def test_no_channel_claims_convergence_without_having_contrasted_anything(self):
        """Sin dos lecturas legibles no hay «convergen» ni «Escenarios que convergen» en ninguna parte."""
        for case in channel_cases():
            if case.verdict not in ("errors", "too_few_readers", "no_scenarios"):
                continue
            with self.subTest(caso=case.name):
                json_run, markdown_run, out_run, _ = self.channels(case)
                self.assertFalse(json_run.json["converged"], json_run.describe())
                self.assertNotIn("**Las lecturas convergen.**", markdown_run.stdout, markdown_run.describe())
                self.assertNotIn("✓", summary_of(out_run.stdout), out_run.describe())
                if case.verdict != "no_scenarios":
                    # Listar como convergentes escenarios que nadie cotejó es la peor
                    # forma de dar luz verde: se prefiere no listar ninguno.
                    self.assertNotIn(
                        "## Escenarios que convergen", markdown_run.stdout, markdown_run.describe()
                    )

    def test_every_section_header_counts_the_blocks_it_renders(self):
        """El «· N» de cada sección es el número de bloques que hay debajo, en las cuatro."""
        self.project.readings(
            "secciones",
            {
                "a": [
                    reading("Insufficient stock", "rechaza", "409"),
                    reading("Reservation created", SOFT_A, "201"),
                    reading("Stock available", "crea la reserva", "201"),
                    reading("Partial reservation", "", None, unclear=True, unclear_why="no lo dice"),
                ],
                "b": [
                    reading("Insufficient stock", "rechaza", "422"),
                    reading("Reservation created", SOFT_B, "201"),
                    reading("Stock available", "crea la reserva", "201"),
                    reading("Partial reservation", "", None, unclear=True, unclear_why="tampoco lo veo"),
                ],
            },
            devils_advocate=[
                {"attack": "Reserva sólo la primera línea del pedido.", "severity": "high"},
                {"attack": "Libera la reserva al minuto 16 sin avisar.", "severity": "low"},
            ],
        )
        run = self.project.diff("secciones")
        sections = counted_sections(run.stdout)
        self.assertEqual(
            sorted(sections),
            [
                "Abogado del diablo",
                "Divergencias blandas",
                "Divergencias duras",
                "Escenarios que convergen",
                "Lagunas declaradas",
            ],
            run.describe(),
        )
        for title, (announced, rendered) in sections.items():
            with self.subTest(seccion=title):
                self.assertEqual(announced, rendered, f"«{title}»\n{run.describe()}")
        # Las dos lagunas son de la misma pregunta: la sección anuncia un bloque y
        # el total de lagunas se dice en la prosa, no en el titular.
        self.assertEqual(sections["Lagunas declaradas"], (1, 1), run.describe())
        self.assertIn("2 lagunas declaradas sobre 1 escenario", run.stdout, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())


class TestMisnamedReadings(DiffCase):
    """Un fichero que nadie lee no se ignora: se dice, con su nombre y con el patrón."""

    def test_a_misnamed_json_does_not_turn_into_a_green_light(self):
        """`notes.json` entre dos lecturas convergentes deja de salir con «convergen» y exit 0."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        self.project.readings("d", {"a": list(agreed), "b": list(agreed)})
        self.project.write(
            ".venoxia/changes/d/readings/notes.json",
            '[{"scenario": "Stock available", "effect": "otra cosa", "status_code": "500"}]',
        )
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertFalse(run.json["converged"], run.describe())
        self.assertEqual(run.json["verdict"], "errors", run.describe())
        joined = " ".join(run.json["errors"])
        self.assertIn("notes.json", joined)
        self.assertIn("reader-*.json", joined)

    def test_a_missing_hyphen_costs_a_reader_and_the_report_says_so(self):
        """`readerb.json` —la errata de un guion— se reporta en vez de dejar un solo lector callando."""
        self.project.readings("d", {"a": [reading("Insufficient stock", "rechaza", "409")]})
        self.project.write(
            ".venoxia/changes/d/readings/readerb.json",
            '[{"scenario": "Insufficient stock", "effect": "rechaza", "status_code": "422"}]',
        )
        run = self.project.diff("d")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("readerb.json", run.stdout, run.describe())
        self.assertIn("reader-*.json", run.stdout, run.describe())
        self.assertNotIn("**Las lecturas convergen.**", run.stdout, run.describe())
        self.assertNotIn("## Escenarios que convergen", run.stdout, run.describe())

    def test_a_file_that_is_not_json_is_not_a_misnamed_reading(self):
        """El aviso es para los `.json` que nadie lee, no para las notas que hay al lado."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        self.project.readings("d", {"a": list(agreed), "b": list(agreed)})
        self.project.write(".venoxia/changes/d/readings/notas.md", "apuntes del despacho\n")
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertTrue(run.json["converged"], run.describe())
        self.assertNotIn("errors", run.json, run.describe())

    def test_the_devils_advocate_is_never_reported_as_misnamed(self):
        """`devils-advocate.json` no encaja en `reader-*.json` y aun así es un fichero esperado."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        run = self.diff(
            {"a": list(agreed), "b": list(agreed)},
            "--json",
            advocate=[{"attack": "Reserva sólo la primera línea.", "severity": "high"}],
        )
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertNotIn("errors", run.json, run.describe())
        self.assertEqual(run.json["advocate"], "listed", run.describe())


#: Los tres nombres canónicos que sí se leen: el patrón fija «reader-» y «.json» en
#: minúsculas, y deja libre la caja de lo que va en medio.
CANONICAL_NAMES = ("reader-c.json", "reader-C.json", "reader-TERCERO.json")

#: Las escrituras del nombre que **no** son canónicas y que antes desaparecían sin
#: dejar rastro: la extensión en otra caja, el prefijo en otra caja, el guion que
#: falta y el abogado del diablo mal escrito (que en un sistema de ficheros
#: insensible a mayúsculas llegaba incluso a cargarse como abogado sin decirlo).
MISNAMED_NAMES = (
    "reader-c.JSON",
    "reader-c.Json",
    "READER-c.json",
    "readerc.json",
    "notes.json",
    "Devils-Advocate.json",
)


def running_as_root() -> bool:
    """¿Corre la suite como root? Para él no existen los ficheros sin permiso de lectura."""
    return getattr(os, "geteuid", lambda: 1)() == 0


class TestFilesNobodyReads(DiffCase):
    """Un fichero que está en `readings/` y que nadie mira es la peor forma de dar luz verde.

    El motor sólo tiene valor si un desacuerdo real nunca puede parecer un acuerdo.
    Un tercer lector que discrepa de frente y se descarta en silencio convierte el
    informe en un `converged: true` con salida 0 —el falso negativo que cuesta la
    razón de ser del componente— mientras el fichero sigue ahí, visible en un `ls`.

    Aquí están todas las formas conocidas de «estar ahí y no mirarse»: la caja de la
    extensión, el prefijo, el guion, el enlace roto, lo que no es un fichero regular,
    el fichero vacío, el ilegible y el directorio que no se puede ni enumerar.
    """

    def agreed(self) -> dict:
        """Dos lectores que coinciden: el suelo verde sobre el que se ve el falso verde."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        return {"a": list(agreed), "b": list(agreed)}

    def dissenting_json(self) -> str:
        """La lectura del tercero, que responde **409** al mismo escenario."""
        return json.dumps(
            [reading("Stock available", "crea la reserva", "409")], ensure_ascii=False
        )

    def with_third(self, name: str) -> Path:
        """Dos lectores de acuerdo más un tercero llamado `name`; devuelve `readings/`."""
        self.project.readings("d", self.agreed())
        directory = self.project.readings_dir("d")
        (directory / name).write_text(self.dissenting_json(), encoding="utf-8")
        return directory

    def case_dir(self, name: str) -> Path:
        """Un `readings/` de usar y tirar, con los dos lectores de acuerdo ya escritos.

        Va aparte del change porque en un sistema de ficheros insensible a mayúsculas
        `reader-c.JSON` y `reader-c.json` no caben en la misma carpeta, y el barrido
        necesita probar las dos escrituras.
        """
        directory = self.project.path(f"casos/{name}")
        directory.mkdir(parents=True, exist_ok=True)
        for reader in ("reader-a.json", "reader-b.json"):
            (directory / reader).write_text(
                json.dumps([reading("Stock available", "crea la reserva", "201")]),
                encoding="utf-8",
            )
        return directory

    # -- Hallazgo A · la extensión en mayúsculas ----------------------------

    def test_an_uppercase_extension_is_not_a_silent_third_opinion(self):
        """`reader-c.JSON` que responde 409 no puede salir como «convergen» con exit 0."""
        self.with_third("reader-c.JSON")
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertFalse(run.json["converged"], run.describe())
        self.assertEqual(run.json["verdict"], "errors", run.describe())
        joined = " ".join(run.json.get("errors", []))
        self.assertIn("reader-c.JSON", joined, run.describe())
        self.assertIn("reader-*.json", joined, run.describe())

    def test_the_uppercase_extension_gets_its_own_section_in_the_report(self):
        """El informe en prosa lo dice también: «Errores de lectura», y no «convergen»."""
        self.with_third("reader-c.Json")
        run = self.project.diff("d")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("## Errores de lectura", run.stdout, run.describe())
        self.assertIn("reader-c.Json", run.stdout, run.describe())
        self.assertNotIn("**Las lecturas convergen.**", run.stdout, run.describe())
        self.assertNotIn("## Escenarios que convergen", run.stdout, run.describe())

    def test_the_pattern_still_accepts_any_case_in_the_middle_of_the_name(self):
        """`reader-C.json` es un nombre legítimo: el patrón sólo fija «reader-» y «.json»."""
        for name in CANONICAL_NAMES:
            with self.subTest(name=name):
                directory = self.case_dir(f"canonico-{name}")
                (directory / name).write_text(self.dissenting_json(), encoding="utf-8")
                readers, _, _, errors = diff_readings.load_readings_dir(directory)
                self.assertEqual(errors, [], f"«{name}» debería leerse, no reportarse")
                self.assertEqual(len(readers), 3, f"«{name}» debería contar como lector")

    # -- Hallazgo B · el enlace simbólico roto ------------------------------

    def test_a_dangling_symlink_is_a_read_error_not_a_reader_less(self):
        """Un `reader-c.json` colgante —copia parcial, rsync a medias— se dice, no se calla."""
        self.project.readings("d", self.agreed())
        directory = self.project.readings_dir("d")
        (directory / "reader-c.json").symlink_to(directory / "no-existe.json")
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertFalse(run.json["converged"], run.describe())
        self.assertEqual(run.json["verdict"], "errors", run.describe())
        joined = " ".join(run.json.get("errors", []))
        self.assertIn("reader-c.json", joined, run.describe())
        self.assertIn("enlace simbólico roto", joined, run.describe())

    def test_a_symlink_to_a_real_reading_is_still_a_reader(self):
        """El vecino que no se puede romper: un enlace que sí resuelve cuenta como lector."""
        directory = self.case_dir("enlace-bueno")
        real = self.project.write("lecturas/tercero.json", self.dissenting_json())
        (directory / "reader-c.json").symlink_to(real)
        readers, _, _, errors = diff_readings.load_readings_dir(directory)
        self.assertEqual(errors, [])
        self.assertEqual(sorted(reader.name for reader in readers), ["reader-a", "reader-b", "reader-c"])

    # -- Todas las formas a la vez ------------------------------------------

    def test_no_file_that_looks_like_a_reading_is_ever_skipped_in_silence(self):
        """El barrido: cada forma de no poder leerse acaba nombrada en «errors», nunca callada.

        Es la propiedad que el docstring de `load_readings_dir` promete, comprobada
        una por una en vez de creída: si alguna vuelve al silencio, el informe vuelve
        a poder decir que las lecturas convergen cuando una de ellas discrepaba.
        """
        cases: dict[str, str] = {}
        for index, name in enumerate(MISNAMED_NAMES):
            directory = self.case_dir(f"nombre-{index}")
            (directory / name).write_text(self.dissenting_json(), encoding="utf-8")
            cases[f"nombre-{index}"] = name

        colgante = self.case_dir("colgante")
        (colgante / "reader-c.json").symlink_to(colgante / "no-existe.json")
        cases["colgante"] = "reader-c.json"

        carpeta = self.case_dir("carpeta")
        (carpeta / "reader-c.json").mkdir()
        cases["carpeta"] = "reader-c.json"

        vacio = self.case_dir("vacio")
        (vacio / "reader-c.json").write_text("", encoding="utf-8")
        cases["vacio"] = "reader-c.json"

        if hasattr(os, "mkfifo"):
            fifo = self.case_dir("fifo")
            os.mkfifo(fifo / "reader-c.json")
            cases["fifo"] = "reader-c.json"

        if not running_as_root():
            ilegible = self.case_dir("ilegible")
            target = ilegible / "reader-c.json"
            target.write_text(self.dissenting_json(), encoding="utf-8")
            os.chmod(target, 0)
            self.addCleanup(os.chmod, target, 0o644)
            cases["ilegible"] = "reader-c.json"

        for case, name in cases.items():
            with self.subTest(case=case):
                directory = self.project.path(f"casos/{case}")
                readers, _, _, errors = diff_readings.load_readings_dir(directory)
                self.assertEqual(
                    [reader.name for reader in readers],
                    ["reader-a", "reader-b"],
                    f"«{name}» no debería contar como lector en el caso «{case}»",
                )
                self.assertTrue(errors, f"«{name}» se descartó en silencio en el caso «{case}»")
                self.assertIn(name, " ".join(errors), f"el error no nombra «{name}»")

    def test_what_does_not_look_like_a_reading_is_still_ignored_without_noise(self):
        """El otro lado de la red: los apuntes y las carpetas de trabajo no son errores."""
        directory = self.case_dir("vecinos")
        (directory / "notas.md").write_text("apuntes del despacho\n", encoding="utf-8")
        (directory / "__pycache__").mkdir()
        (directory / "borradores").mkdir()
        readers, _, _, errors = diff_readings.load_readings_dir(directory)
        self.assertEqual(errors, [])
        self.assertEqual(len(readers), 2)

    def test_the_docstring_does_not_promise_a_sweep_the_code_does_not_do(self):
        """La promesa falsa que convirtió el hueco en trampa no vuelve al docstring.

        El docstring decía «Todo `.json` del directorio se mira» mientras el `glob`
        dejaba fuera `reader-c.JSON`. Antes del arreglo el usuario no esperaba que se
        comprobara nada; con esa frase, el informe se lo prometía.
        """
        doc = diff_readings.load_readings_dir.__doc__ or ""
        self.assertNotIn("Todo `.json` del directorio se mira", doc)
        self.assertIn("Se enumera **todo** el contenido del directorio", doc)

    # -- El abogado del diablo, que también puede estar y no mirarse --------

    def test_a_dangling_advocate_is_not_reported_as_a_missing_advocate(self):
        """Un `devils-advocate.json` colgante no es «no lo despacharon»: es «no se sabe»."""
        self.project.readings("d", self.agreed())
        directory = self.project.readings_dir("d")
        (directory / "devils-advocate.json").symlink_to(directory / "no-existe.json")
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertEqual(run.json["advocate"], "unreadable", run.describe())
        joined = " ".join(run.json.get("errors", []))
        self.assertIn("devils-advocate.json", joined, run.describe())
        self.assertIn("abogado del diablo", joined, run.describe())

    # -- Los mensajes que dicen qué pasa, no qué se parece a lo que pasa ----

    def test_an_empty_reading_says_it_is_empty_not_that_the_json_is_broken(self):
        """Un fichero vacío es un lector que no escribió nada, no un JSON mal formado."""
        directory = self.case_dir("vacio-mensaje")
        (directory / "reader-c.json").write_text("   \n", encoding="utf-8")
        _, _, _, errors = diff_readings.load_readings_dir(directory)
        joined = " ".join(errors)
        self.assertIn("está vacío", joined)
        self.assertNotIn("no es JSON válido", joined)

    @unittest.skipIf(running_as_root(), "root lee cualquier cosa: el caso no existe para él")
    def test_a_readings_directory_that_cannot_be_listed_says_so_without_a_traceback(self):
        """Sin poder enumerar el directorio no se sabe qué lecturas hay: se dice, y sale 2."""
        self.project.readings("d", self.agreed())
        directory = self.project.readings_dir("d")
        os.chmod(directory, 0)
        self.addCleanup(os.chmod, directory, 0o755)
        run = self.project.diff("d", "--json")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertEqual(run.json["verdict"], "errors", run.describe())
        self.assertIn("No se pudo listar", " ".join(run.json.get("errors", [])), run.describe())


class TestIncompleteRuns(DiffCase):
    """Lo que no se comparó no converge: ni con un lector, ni sin escenarios."""

    # @covers R-DIV-002
    def test_a_single_reader_cannot_claim_convergence(self):
        """Con un solo lector el JSON no dice `converged: true` y la ejecución no sale con 0."""
        run = self.diff(
            {
                "a": [
                    reading("Stock available", "crea la reserva", "201"),
                    reading("Insufficient stock", "rechaza", "409"),
                ]
            },
            "--json",
        )
        self.assertEqual(run.returncode, 2, run.describe())
        payload = run.json
        self.assertFalse(payload["converged"], run.describe())
        self.assertEqual(payload["verdict"], "too_few_readers", run.describe())
        self.assertEqual(payload["counts"]["readers"], 1, run.describe())

    def test_a_single_reader_report_says_it_in_prose_and_lists_nothing_as_converging(self):
        """El informe de un solo lector no lista «Escenarios que convergen»: nadie los cotejó."""
        target = self.project.path("informe.md")
        run = self.diff(
            {"a": [reading("Stock available", "crea la reserva", "201")]}, "--out", str(target)
        )
        self.assertEqual(run.returncode, 2, run.describe())
        written = target.read_text(encoding="utf-8")
        self.assertIn("**Lectura sin contraste.**", written)
        self.assertNotIn("## Escenarios que convergen", written)
        self.assertIn("Con un solo lector no hay contraste posible", written)
        self.assertTrue(summary_of(run.stdout).startswith("✗ Lectura sin contraste ·"), run.describe())

    def test_zero_scenarios_is_not_a_convergence_in_any_channel(self):
        """Dos lecturas vacías no convergen: no se comparó nada, y los tres canales lo dicen igual."""
        target = self.project.path("informe.md")
        self.project.readings("vacias", {"a": [], "b": []})
        payload = self.project.diff("vacias", "--json")
        report = self.project.diff("vacias")
        summary = self.project.diff("vacias", "--out", str(target))
        self.assertEqual(payload.returncode, 2, payload.describe())
        self.assertFalse(payload.json["converged"], payload.describe())
        self.assertEqual(payload.json["verdict"], "no_scenarios", payload.describe())
        self.assertIn("**Sin escenarios que comparar.**", verdict_of(report.stdout), report.describe())
        self.assertTrue(
            summary_of(summary.stdout).startswith("✗ Sin escenarios que comparar ·"), summary.describe()
        )


class TestStrictInEveryChannel(DiffCase):
    """`--strict` cambia esta ejecución, así que esta ejecución tiene que decirlo."""

    def soft_pair(self) -> dict:
        """Dos lecturas con una única divergencia blanda (Jaccard 0.5)."""
        return {
            "a": [reading("Reservation created", SOFT_A, "201")],
            "b": [reading("Reservation created", SOFT_B, "201")],
        }

    # @covers R-DIV-003
    def test_strict_with_only_soft_divergences_reports_a_failure_not_a_warning(self):
        """Con `--strict` y sólo blandas: exit 1, ✗ en el resumen y un veredicto en pasado."""
        target = self.project.path("informe.md")
        self.project.readings("estricto", self.soft_pair())
        payload = self.project.diff("estricto", "--strict", "--json")
        report = self.project.diff("estricto", "--strict")
        summary = self.project.diff("estricto", "--strict", "--out", str(target))

        self.assertEqual(payload.returncode, 1, payload.describe())
        self.assertTrue(payload.json["strict"], payload.describe())
        self.assertEqual(payload.json["exit_code"], 1, payload.describe())

        verdict = verdict_of(report.stdout)
        self.assertIn("Esta ejecución lleva `--strict`", verdict)
        self.assertIn("Esta ejecución sale con código 1.", verdict)
        # La condicional «con --strict, sí» no dice qué pasó aquí; la afirmación en
        # negativo, además, era directamente falsa en esta invocación.
        self.assertNotIn("no hacen fallar", verdict)

        line = summary_of(summary.stdout)
        self.assertTrue(line.startswith("✗ "), f"{line}\n{summary.describe()}")
        self.assertIn("`--strict`", line)
        self.assertIn("salida 1", line)

    # @covers R-DIV-003
    def test_without_strict_the_same_pair_is_a_warning_and_says_so(self):
        """Sin `--strict` el mismo par sale con 0, ⚠ en el resumen y `strict: false` en el JSON."""
        target = self.project.path("informe.md")
        self.project.readings("laxo", self.soft_pair())
        payload = self.project.diff("laxo", "--json")
        report = self.project.diff("laxo")
        summary = self.project.diff("laxo", "--out", str(target))

        self.assertEqual(payload.returncode, 0, payload.describe())
        self.assertFalse(payload.json["strict"], payload.describe())
        self.assertEqual(payload.json["exit_code"], 0, payload.describe())

        verdict = verdict_of(report.stdout)
        self.assertIn("no hacen fallar", verdict)
        self.assertIn("Esta ejecución sale con código 0.", verdict)

        line = summary_of(summary.stdout)
        self.assertTrue(line.startswith("⚠ "), f"{line}\n{summary.describe()}")
        self.assertIn("salida 0", line)


class TestDevilsAdvocateStates(DiffCase):
    """«No hay fichero», «está vacío» y «no se pudo leer» son tres cosas distintas."""

    def agreed(self) -> dict:
        """Dos lecturas idénticas, para que lo único en juego sea el abogado."""
        entry = [reading("Stock available", "crea la reserva", "201")]
        return {"a": list(entry), "b": list(entry)}

    def test_an_unreadable_advocate_is_not_reported_as_one_without_findings(self):
        """Un `devils-advocate.json` ilegible no se cuenta como «no encontró nada»."""
        run = self.diff(self.agreed(), advocate="{ esto no es JSON")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertNotIn("no encontró ningún ataque", run.stdout, run.describe())
        self.assertIn("no se sabe qué encontró el abogado del diablo", run.stdout, run.describe())

    def test_an_unreadable_advocate_is_visible_in_the_json_too(self):
        """El JSON distingue el abogado ilegible del que no está: `advocate: unreadable`."""
        run = self.diff(self.agreed(), "--json", advocate="{ esto no es JSON")
        self.assertEqual(run.json["advocate"], "unreadable", run.describe())
        self.assertEqual(run.json["attacks"], [], run.describe())
        self.assertTrue(run.json["errors"], run.describe())

    def test_an_empty_advocate_may_say_it_found_nothing(self):
        """Un fichero legible y vacío sí autoriza a decir que no encontró nada."""
        run = self.diff(self.agreed(), advocate=[])
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("no encontró ningún ataque", run.stdout, run.describe())
        payload = self.diff(self.agreed(), "--json", advocate=[])
        self.assertEqual(payload.json["advocate"], "empty", payload.describe())

    def test_a_missing_advocate_renders_no_section_at_all(self):
        """Sin fichero no hay sección de abogado, y el JSON lo dice con `advocate: absent`."""
        run = self.diff(self.agreed(), "--json")
        self.assertEqual(run.json["advocate"], "absent", run.describe())
        report = self.diff(self.agreed())
        self.assertNotIn("## Abogado del diablo", report.stdout, report.describe())


class TestAttackSeverity(DiffCase):
    """Una severidad que la fuente no dijo no se imprime como si la hubiera dicho."""

    def agreed(self) -> dict:
        entry = [reading("Stock available", "crea la reserva", "201")]
        return {"a": list(entry), "b": list(entry)}

    def test_an_unknown_severity_is_degraded_but_declared(self):
        """`critical` se trata como `medium` y el informe dice que la fuente puso otra cosa."""
        advocate = [{"attack": "Reserva sólo la primera línea.", "severity": "critical"}]
        payload = self.diff(self.agreed(), "--json", advocate=advocate)
        self.assertEqual(payload.returncode, 0, payload.describe())
        attack = payload.json["attacks"][0]
        self.assertEqual(attack["severity"], "medium", payload.describe())
        self.assertEqual(attack["severity_declared"], "critical", payload.describe())
        report = self.diff(self.agreed(), advocate=advocate)
        self.assertIn("critical", report.stdout, report.describe())
        self.assertIn("no es `high`, `medium` ni `low`", report.stdout, report.describe())

    def test_a_known_severity_carries_no_disclaimer(self):
        """Lo que la fuente sí dijo se imprime sin coletilla y sin clave de más."""
        advocate = [{"attack": "Libera la reserva al minuto 16.", "severity": "HIGH"}]
        payload = self.diff(self.agreed(), "--json", advocate=advocate)
        attack = payload.json["attacks"][0]
        self.assertEqual(attack["severity"], "high", payload.describe())
        self.assertNotIn("severity_declared", attack, payload.describe())
        report = self.diff(self.agreed(), advocate=advocate)
        self.assertNotIn("no es `high`, `medium` ni `low`", report.stdout, report.describe())

    def test_an_attack_without_text_is_still_a_read_error(self):
        """Sin `attack` no queda nada que reportar: eso sí es un error de lectura."""
        run = self.diff(self.agreed(), advocate=[{"severity": "high"}])
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("no describe ningún ataque", run.stdout, run.describe())


class TestAnswerableQuestions(DiffCase):
    """Una pregunta cerrada con las dos opciones iguales es peor que no preguntar."""

    def test_a_status_code_and_its_canonical_reason_are_the_same_answer(self):
        """«409» y «409 Conflict» son la misma respuesta: no hay divergencia que preguntar."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock", "rechaza la peticion", "409")],
                "b": [reading("Insufficient stock", "rechaza la peticion", "409 Conflict")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.json["counts"]["hard"], 0, run.describe())
        self.assertEqual(run.json["divergences"], [], run.describe())
        self.assertTrue(run.json["converged"], run.describe())

    def test_a_status_code_with_another_reason_is_still_a_divergence(self):
        """«409» contra «409 Gone» no se unifica: el desacuerdo puede ser real y se pregunta."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock", "rechaza la peticion", "409")],
                "b": [reading("Insufficient stock", "rechaza la peticion", "409 Gone")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        divergence = run.json["divergences"][0]
        self.assertEqual(divergence["field"], "status_code", run.describe())
        self.assertEqual(len(set(divergence["options"])), len(divergence["options"]), divergence)

    def test_the_canonical_reason_does_not_hide_a_third_reader(self):
        """Unificar «409» y «409 Conflict» no borra al lector que responde 422."""
        run = self.diff(
            {
                "a": [reading("Insufficient stock", "rechaza", "409")],
                "b": [reading("Insufficient stock", "rechaza", "409 Conflict")],
                "c": [reading("Insufficient stock", "rechaza", "422")],
            },
            "--json",
        )
        self.assertEqual(run.returncode, 1, run.describe())
        divergence = run.json["divergences"][0]
        self.assertEqual(len(divergence["options"]), 2, divergence["options"])
        self.assertEqual(len(set(divergence["options"])), 2, divergence["options"])
        self.assertEqual(
            divergence["readings"],
            {"reader-a": "409", "reader-b": "409 Conflict", "reader-c": "422"},
            run.describe(),
        )

    def test_no_question_ever_offers_the_same_option_twice(self):
        """Ninguna pregunta, ni en el JSON ni en el informe, repite una opción."""
        cases = {
            "rico": rich_readings(),
            "codigos": {
                "a": [reading("Insufficient stock", "rechaza", "409")],
                "b": [reading("Insufficient stock", "rechaza", "409 Conflict")],
                "c": [reading("Insufficient stock", "rechaza", "422")],
            },
            "efectos": {
                "a": [reading("Stock available", "ok", "201", ["stock reservado", "evento"])],
                "b": [reading("Stock available", "ok", "201", ["stock reservado"])],
                "c": [reading("Stock available", "ok", "201", [])],
            },
            "lagunas": {
                "a": [reading("Partial", "reserva lo que hay", "207")],
                "b": [reading("Partial", "", None, unclear=True, unclear_why="no lo dice")],
            },
        }
        for name, readers in cases.items():
            with self.subTest(caso=name):
                self.project.readings(name, readers)
                payload = self.project.diff(name, "--json")
                for divergence in payload.json["divergences"]:
                    options = divergence["options"]
                    self.assertGreaterEqual(len(options), 2, divergence)
                    self.assertEqual(len(set(options)), len(options), divergence)
                report = self.project.diff(name)
                blocks = question_blocks(report.stdout)
                self.assertTrue(blocks, report.describe())
                for scenario, options in blocks:
                    with self.subTest(caso=name, escenario=scenario):
                        self.assertGreaterEqual(len(options), 2, options)
                        self.assertEqual(len(set(options)), len(options), options)


# ---------------------------------------------------------------------------
# Las banderas de la CLI
# ---------------------------------------------------------------------------


class TestCliFlags(DiffCase):
    """`--out`, `--threshold` y `--strict` cambian el resultado de verdad."""

    def test_out_writes_the_markdown_report_to_the_file(self):
        """`--out` deja el informe en el fichero, con su pregunta dentro, y avisa por stdout."""
        target = self.project.path("informe/divergence.md")
        run = self.diff(
            {
                "a": [reading("Insufficient stock on one line", "rechaza", "409")],
                "b": [reading("Insufficient stock on one line", "rechaza", "422")],
            },
            "--out",
            str(target),
        )
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertTrue(target.is_file(), run.describe())
        written = target.read_text(encoding="utf-8")
        self.assertIn("# Informe de divergencia", written)
        self.assertIn("**¿Qué código de estado debe devolver el sistema en «Insufficient stock on one line»?**", written)
        self.assertIn("- (A) 409 Conflict", written)
        self.assertIn("Informe escrito en", run.stdout)

    def test_the_threshold_decides_whether_the_same_pair_diverges(self):
        """El mismo par (Jaccard 0.75) converge con --threshold 0.1 y diverge con 0.9."""
        readers = {
            "a": [reading("Reservation created", "reserva creada con TTL de 15 minutos", "201")],
            "b": [reading("Reservation created", "reserva creada con TTL de 15 min", "201")],
        }
        self.project.readings("d", readers)
        for threshold, expected_soft in (("0.1", 0), ("0.9", 1)):
            with self.subTest(threshold=threshold):
                run = self.project.diff("d", "--json", "--threshold", threshold)
                self.assertEqual(run.json["counts"]["soft"], expected_soft, run.describe())

    def test_strict_turns_a_soft_divergence_into_a_failure(self):
        """Con `--strict` una blanda sola ya hace fallar con exit 1, y sigue sin converger."""
        run = self.diff(
            {
                "a": [reading("Reservation created", SOFT_A, "201")],
                "b": [reading("Reservation created", SOFT_B, "201")],
            },
            "--strict",
            "--json",
        )
        self.assertEqual(run.json["counts"]["soft"], 1, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertFalse(run.json["converged"], run.describe())

    def test_a_soft_divergence_alone_exits_zero_without_strict(self):
        """Sin `--strict` una blanda sola no tumba la ejecución: exit 0 pero `converged: false`.

        Las dos afirmaciones conviven: hay desacuerdo —así que las lecturas no
        convergen— y §7 sólo hace fallar por duras, lagunas o `--strict`.
        """
        run = self.diff(
            {
                "a": [reading("Reservation created", SOFT_A, "201")],
                "b": [reading("Reservation created", SOFT_B, "201")],
            },
            "--json",
        )
        self.assertEqual(run.json["counts"]["soft"], 1, run.describe())
        self.assertEqual(run.json["counts"]["hard"], 0, run.describe())
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertFalse(run.json["converged"], run.describe())


# ---------------------------------------------------------------------------
# Las formas de entrada que hay que tolerar
# ---------------------------------------------------------------------------


class TestInputShapes(DiffCase):
    """El envoltorio, el abogado del diablo y su ausencia."""

    def test_the_readings_wrapper_is_accepted_like_a_bare_array(self):
        """`{"readings": [...]}` se lee igual que el array desnudo y empareja con él."""
        entry = reading("Stock available", "crea la reserva", "201", ["stock reservado"])
        run = self.diff({"a": {"readings": [entry]}, "b": [entry]}, "--json")
        self.assertEqual(run.returncode, 0, run.describe())
        payload = run.json
        self.assertEqual(payload["counts"], {"hard": 0, "soft": 0, "gaps": 0, "scenarios": 1, "readers": 2})

    def test_devils_advocate_as_a_single_object_is_accepted(self):
        """Un `devils-advocate.json` que es un objeto suelto produce un ataque."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        run = self.diff(
            {"a": list(agreed), "b": list(agreed)},
            "--json",
            advocate={
                "attack": "Reservar sólo la primera línea cumple el delta al pie de la letra.",
                "requirement_id": "R-CHK-014",
                "severity": "high",
            },
        )
        self.assertEqual(run.returncode, 0, run.describe())
        attacks = run.json["attacks"]
        self.assertEqual(len(attacks), 1, run.describe())
        self.assertEqual(attacks[0]["requirement_id"], "R-CHK-014")
        self.assertEqual(attacks[0]["severity"], "high")
        self.assertIn("primera línea", attacks[0]["attack"])

    def test_devils_advocate_as_an_array_is_accepted(self):
        """Un array de ataques se lee entero, sin perder ninguno."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        run = self.diff(
            {"a": list(agreed), "b": list(agreed)},
            "--json",
            advocate=[
                {"attack": "Libera la reserva al minuto 16 sin avisar.", "requirement_id": "R-CHK-014", "severity": "medium"},
                {"attack": "Reserva una sola línea del pedido.", "requirement_id": "R-CHK-014", "severity": "high"},
            ],
        )
        self.assertEqual(run.returncode, 0, run.describe())
        attacks = run.json["attacks"]
        self.assertEqual(len(attacks), 2, run.describe())
        self.assertEqual({attack["severity"] for attack in attacks}, {"high", "medium"})

    def test_a_missing_devils_advocate_breaks_nothing(self):
        """Sin `devils-advocate.json` el informe sale igual, con la lista de ataques vacía."""
        agreed = [reading("Stock available", "crea la reserva", "201")]
        run = self.diff({"a": list(agreed), "b": list(agreed)}, "--json")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.json["attacks"], [], run.describe())
        self.assertFalse(self.project.readings_dir("d").joinpath("devils-advocate.json").exists())


# ---------------------------------------------------------------------------
# Errores legibles: exit 2 y ni una traza
# ---------------------------------------------------------------------------


class TestReadableErrors(DiffCase):
    """Lo que se rompe se cuenta en español; la traza de Python no sale nunca."""

    def test_a_malformed_reader_json_exits_two_without_a_traceback(self):
        """Un `reader-x.json` que no es JSON se reporta en el informe y sale con 2."""
        run = self.diff(
            {
                "a": [reading("Stock available", "crea la reserva", "201")],
                "x": "{ esto no es JSON",
            },
        )
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        combined = run.stdout + run.stderr
        self.assertIn("reader-x.json", combined)
        self.assertIn("no es JSON válido", combined)

    def test_an_empty_readings_directory_exits_two_without_a_traceback(self):
        """Un `readings/` sin ningún `reader-*.json` sale con 2 y dice qué hacer."""
        empty = self.project.path(".venoxia/changes/vacio/readings")
        empty.mkdir(parents=True)
        run = self.project.run(DIFF_READINGS_PY, "--readings", str(empty))
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("no hay ningún fichero", run.stderr)
        self.assertIn("/venoxia:diverge", run.stderr)

    def test_a_nonexistent_readings_directory_exits_two_without_a_traceback(self):
        """Un `--readings` que no existe sale con 2 y lo dice en español."""
        run = self.project.run(
            DIFF_READINGS_PY, "--readings", str(self.project.path("no/existe/readings"))
        )
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("no existe el directorio de lecturas", run.stderr)

    def test_a_readings_path_that_is_a_file_exits_two_without_a_traceback(self):
        """Un `--readings` que apunta a un fichero sale con 2 y explica qué se esperaba."""
        target = self.project.write("readings.json", "[]")
        run = self.project.run(DIFF_READINGS_PY, "--readings", str(target))
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertNoTraceback(run)
        self.assertIn("no es un directorio", run.stderr)


# ---------------------------------------------------------------------------
# Los dos agentes que despacha /venoxia:diverge
# ---------------------------------------------------------------------------


class TestAgentFrontmatter(unittest.TestCase):
    """El aislamiento del lector es una propiedad de seguridad, y se prueba."""

    def frontmatter(self, relpath: str) -> tuple[dict[str, str], list[str]]:
        """Frontmatter del agente, leído del repositorio."""
        path = REPO_ROOT / relpath
        self.assertTrue(path.is_file(), f"falta el agente «{relpath}»")
        return read_frontmatter(path.read_text(encoding="utf-8"))

    def test_agent_frontmatter_is_flat_and_parseable(self):
        """El frontmatter de cada agente es YAML plano: sólo líneas «clave: valor»."""
        for relpath in AGENT_FILES:
            with self.subTest(agente=relpath):
                data, offenders = self.frontmatter(relpath)
                self.assertEqual(offenders, [], f"{relpath}: líneas que no son «clave: valor»")
                self.assertTrue(data, f"{relpath}: el frontmatter está vacío")

    def test_agent_frontmatter_declares_the_required_keys(self):
        """Cada agente declara name, description, model y tools, y ninguno vacío."""
        for relpath in AGENT_FILES:
            data, _ = self.frontmatter(relpath)
            for key in ("name", "description", "model", "tools"):
                with self.subTest(agente=relpath, clave=key):
                    self.assertIn(key, data)
                    self.assertTrue(data[key].strip(), f"{relpath}: «{key}» está vacío")

    def test_agent_tools_are_limited_to_read(self):
        """`tools` es sólo `Read`: añadirle Bash o Grep rompe el aislamiento del lector."""
        for relpath in AGENT_FILES:
            with self.subTest(agente=relpath):
                data, _ = self.frontmatter(relpath)
                self.assertEqual(data.get("tools"), "Read", f"{relpath}: tools debe ser sólo «Read»")

    def test_agent_names_match_their_file(self):
        """El `name` del frontmatter es el del fichero: así lo despacha /venoxia:diverge."""
        for relpath in AGENT_FILES:
            with self.subTest(agente=relpath):
                data, _ = self.frontmatter(relpath)
                self.assertEqual(data.get("name"), (REPO_ROOT / relpath).stem)


if __name__ == "__main__":
    unittest.main()
