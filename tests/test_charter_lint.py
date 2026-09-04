#!/usr/bin/env python3
"""Reglas C01–C16 del linter del acta: qué proyecto se va a construir y para quién.

Cada regla trae un caso en positivo —el acta canónica no la dispara— y al menos
uno en negativo. La disciplina de todos los negativos es la misma que en el
resto de la suite y no admite atajos: se rompe **una** cosa del acta canónica y
se comprueba que el conjunto de reglas disparadas es **exactamente** el
esperado, nunca que «lo contiene». Un fixture que dispara la regla que se prueba
y de propina otra por estar mal escrito es un test que aprueba por el motivo
equivocado.

Todo se ejecuta contra `scripts/charter_lint.py` por subproceso y con `--json`,
que es la superficie que la skill consume. El andamio compartido
(`tests/venoxia_fixtures.py`) monta el proyecto dentro de un
`tempfile.TemporaryDirectory` con un `$HOME` falso; el constructor de actas vive
**aquí**, porque el acta es de este fichero y el andamio es de todos.

Ninguna fecha se escribe a mano: las de `revisit:` salen de `future_date()` y
`past_date()`, que cuentan desde `datetime.date.today()`. Una constante escrita
a mano convierte la suite en verde-hasta-que-un-día-no.

Cómo lanzarlo::

    python3 -m unittest tests.test_charter_lint -v
    python3 -m pytest tests/test_charter_lint.py -q
"""

from __future__ import annotations

import sys
import unittest
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

# La raíz del repositorio en `sys.path`, para que el import cualificado de abajo
# funcione también cuando este fichero se ejecuta directamente. Con `pytest` o
# con «python3 -m unittest tests.test_charter_lint» ya está puesta; esto no la
# duplica.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.venoxia_fixtures import (  # noqa: E402
    SCRIPTS_DIR,
    CompletedRun,
    Project,
    future_date,
    past_date,
)

# `venoxia_fixtures` ya ha puesto `scripts/` en `sys.path`, así que el linter se
# puede importar como módulo. Se hace para poder examinar el registro de reglas
# y `_leading_implementation_verb` en corto: los casos de C08 que sólo se
# distinguen por dónde cae el verbo son más claros —y más difíciles de aprobar
# por accidente— preguntándole a la función directamente.
import charter_lint  # noqa: E402

#: El script bajo prueba y el sitio donde vive el acta dentro del proyecto.
CHARTER_LINT_PY = SCRIPTS_DIR / "charter_lint.py"
CHARTER_RELPATH = ".venoxia/charter.md"


# ---------------------------------------------------------------------------
# El constructor del acta
#
# Todo caso negativo se escribe tocándole **un** parámetro a `charter()`. Los
# valores por omisión reproducen el acta canónica del contrato, con una sola
# diferencia: la fecha de `revisit:` se calcula desde hoy en vez de estar
# escrita a mano.
# ---------------------------------------------------------------------------

DEFAULT_TITLE = "Reservas Bistró · Acta del proyecto"

DEFAULT_PURPOSE = (
    "Que un restaurante pequeño deje de perder mesas por reservas apuntadas en un\n"
    "cuaderno que sólo entiende quien lo escribió."
)

#: El hecho con el que el acta canónica declara qué resuelve su apuesta.
#: `revisit:` ya no admite fechas: pide el suceso que cierra la suposición.
REVISIT_FACT = "cuando hayamos servido las cincuenta primeras reservas"


@dataclass
class User:
    """Un usuario del acta: quién es, cómo vive hoy y qué cambia para él.

    `before` y `after` a `None` **quitan** la viñeta; a `""` la escriben vacía.
    Son dos fallos distintos y C03 los cuenta de forma distinta.
    """

    slug: str = "owner"
    role: str = "Dueño del restaurante"
    before: str | None = "apunta las reservas en un cuaderno y las repasa cada mañana."
    after: str | None = "ve la ocupación de la noche desde el móvil sin llamar a nadie."

    def render(self) -> str:
        """El markdown del usuario."""
        header = f"### {self.slug} · {self.role}" if self.role else f"### {self.slug}"
        lines = [header]
        if self.before is not None:
            lines.append(f"- **hoy:** {self.before}".rstrip())
        if self.after is not None:
            lines.append(f"- **con esto:** {self.after}".rstrip())
        return "\n".join(lines)


DEFAULT_USERS: tuple[User, ...] = (
    User(),
    User(
        slug="diner",
        role="Cliente que reserva",
        before="llama por teléfono y espera a que alguien coja.",
        after="reserva desde el enlace del perfil, a cualquier hora.",
    ),
)


@dataclass
class Cap:
    """Una fila de la tabla de capabilities."""

    priority: object = 1
    slug: str = "booking"
    what: str = "reservar una mesa para una fecha y hora"
    done_when: str = "un cliente reserva y recibe la confirmación con su hora"
    risk: str = "high"
    quoted: bool = True

    def render(self) -> str:
        """La fila, con el slug entre acentos graves como manda el contrato."""
        slug = f"`{self.slug}`" if self.quoted and self.slug else self.slug
        return f"| {self.priority} | {slug} | {self.what} | {self.done_when} | {self.risk} |"


DEFAULT_CAPABILITIES: tuple[Cap, ...] = (
    Cap(),
    Cap(
        priority=2,
        slug="availability",
        what="ver qué queda libre esta noche",
        done_when="el dueño abre el móvil y ve las mesas libres de hoy",
        risk="medium",
    ),
)

DEFAULT_OUT_OF_SCOPE: tuple[str, ...] = (
    "**Pagos y señales.** No se cobra nada en la v1; el riesgo regulatorio no compensa\n"
    "  hasta que haya reservas de verdad.",
    "**App nativa.** La web basta para lo que promete el propósito.",
)

#: Marca de «pon tú el valor bueno»: el hecho canónico si la apuesta va en
#: «low», y ninguna línea si no, porque sólo «low» lo exige.
AUTO = "auto"


@dataclass
class Bet:
    """Una apuesta del acta, con su prosa y su bloque de metadatos.

    Cualquier clave a `None` **no se escribe**; a `""` se escribe vacía. Las dos
    cosas son fallos distintos y las reglas las distinguen.
    """

    id: str = "B-001"
    title: str = "Nadie anula por WhatsApp"
    prose: str = (
        "Damos por hecho que un cliente que quiere anular usará el enlace y no el\n"
        "teléfono del restaurante."
    )
    confidence: str | None = "low"
    why: str | None = "no lo hemos comprobado con ningún restaurante real"
    revisit: str | None = AUTO
    fatal: str | None = "no"

    def render(self) -> str:
        """El markdown de la apuesta."""
        header = f"### {self.id} · {self.title}" if self.title else f"### {self.id}"
        revisit = self.revisit
        if revisit == AUTO:
            revisit = REVISIT_FACT if self.confidence == "low" else None

        meta: list[str] = []
        if self.confidence is not None:
            meta.append(f"confidence: {self.confidence}".rstrip())
        for key, value in (("why", self.why), ("revisit", revisit), ("fatal", self.fatal)):
            if value is not None:
                meta.append(f"  {key + ':':<9} {value}".rstrip())

        blocks = [header]
        if self.prose:
            blocks.append(self.prose)
        if meta:
            blocks.append("\n".join(meta))
        return "\n\n".join(blocks)


DEFAULT_BETS: tuple[Bet, ...] = (Bet(),)


def _section_body(value: object, default: Sequence, render) -> str:
    """El cuerpo de una sección: crudo si es una cadena, renderizado si es una lista."""
    if isinstance(value, str):
        return value
    items = default if value is None else value
    return render(list(items))


def _users_body(items: list) -> str:
    """Los usuarios, separados por una línea en blanco."""
    return "\n\n".join(item if isinstance(item, str) else item.render() for item in items)


def _capabilities_body(items: list) -> str:
    """La tabla entera: encabezado, separador y una fila por capability."""
    rows = [
        "| # | Capability | Qué podrá hacer | Done when | Risk |",
        "|---|---|---|---|---|",
    ]
    rows.extend(item if isinstance(item, str) else item.render() for item in items)
    return "\n".join(rows)


def _out_of_scope_body(items: list) -> str:
    """Las exclusiones, una viñeta por línea."""
    return "\n".join(f"- {item}" for item in items)


def _bets_body(items: list) -> str:
    """Las apuestas, separadas por una línea en blanco."""
    return "\n\n".join(item if isinstance(item, str) else item.render() for item in items)


def charter(
    *,
    title: str = DEFAULT_TITLE,
    purpose: str = DEFAULT_PURPOSE,
    users: object = None,
    capabilities: object = None,
    out_of_scope: object = None,
    bets: object = None,
    omit: Sequence[str] = (),
) -> str:
    """Devuelve el markdown de un acta. Por omisión, la canónica del contrato.

    Cada sección admite dos formas: una lista de `User`, `Cap`, `Bet` o cadenas
    —que se renderiza— o una cadena, que se escribe **tal cual** como cuerpo de
    la sección. La segunda es la que permite probar una tabla sin separador o una
    sección vacía sin pelearse con el constructor.

    `omit=("Bets",)` deja el acta sin esa sección, que es como se prueba C01.
    """
    omitted = set(omit)
    bodies = [
        (charter_lint.SECTION_PURPOSE, purpose),
        (charter_lint.SECTION_USERS, _section_body(users, DEFAULT_USERS, _users_body)),
        (
            charter_lint.SECTION_CAPABILITIES,
            _section_body(capabilities, DEFAULT_CAPABILITIES, _capabilities_body),
        ),
        (
            charter_lint.SECTION_OUT_OF_SCOPE,
            _section_body(out_of_scope, DEFAULT_OUT_OF_SCOPE, _out_of_scope_body),
        ),
        (charter_lint.SECTION_BETS, _section_body(bets, DEFAULT_BETS, _bets_body)),
    ]

    parts = [f"# {title}"] if title else []
    for name, body in bodies:
        if name in omitted:
            continue
        parts.append(f"## {name}")
        if body:
            parts.append(body)
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Base común
# ---------------------------------------------------------------------------


class CharterCase(unittest.TestCase):
    """Andamio común: un proyecto nuevo por test y tres aserciones de cabecera."""

    def setUp(self) -> None:
        self.project = Project()
        self.addCleanup(self.project.cleanup)

    # -- Ficheros ------------------------------------------------------------

    def write(self, text: str) -> Path:
        """Escribe el acta del proyecto."""
        return self.project.write(CHARTER_RELPATH, text)

    def write_spec(self, slug: str) -> Path:
        """Crea una capability viva en disco, que es lo único que C16 mira."""
        return self.project.write(
            f".venoxia/capabilities/{slug}/spec.md",
            f"# Capability: {slug}\n\n## Purpose\n\nLo que ya se está especificando.\n",
        )

    # -- Ejecución -----------------------------------------------------------

    def lint(self, *args: str) -> CompletedRun:
        """Ejecuta `charter_lint.py --root <root>` con los argumentos que se le pasen."""
        return self.project.run(CHARTER_LINT_PY, "--root", str(self.project.root), *args)

    def lint_json(self, *args: str) -> CompletedRun:
        """Atajo de `lint("--json", …)`, que es lo que necesitan `.rules()` y `.json`."""
        return self.lint("--json", *args)

    # -- Aserciones ----------------------------------------------------------

    def assert_conforms(self, text: str | None = None) -> CompletedRun:
        """Exige conformidad total en modo estricto: exit 0 y ni un solo hallazgo."""
        if text is not None:
            self.write(text)
        run = self.lint_json("--strict")
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.returncode, 0, run.describe())
        return run

    def assert_only_error(self, rule: str, text: str | None = None) -> list[dict]:
        """Exige que salte esa regla y **sólo** ésa, con exit 1 y severidad de error.

        Se valida sin `--strict` a propósito: así el `1` demuestra que la regla es
        un error, y la comparación de conjuntos —no de pertenencia— demuestra que
        el fixture no ha ensuciado el veredicto con avisos de propina.
        """
        if text is not None:
            self.write(text)
        run = self.lint_json()
        self.assertEqual(run.rule_set(), {rule}, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())
        findings = run.findings_for(rule)
        self.assertTrue(findings, run.describe())
        for finding in findings:
            self.assertEqual(finding["severity"], "error", run.describe())
            self.assertTrue((finding["hint"] or "").strip(), run.describe())
            self.assertEqual(finding["file"], CHARTER_RELPATH, run.describe())
        return findings

    def assert_only_warning(self, rule: str, text: str | None = None) -> list[dict]:
        """Exige que salte ese aviso y sólo ése: exit 0 sin `--strict` y 1 con él."""
        if text is not None:
            self.write(text)
        run = self.lint_json()
        self.assertEqual(run.rule_set(), {rule}, run.describe())
        self.assertEqual(run.returncode, 0, run.describe())
        findings = run.findings_for(rule)
        self.assertTrue(findings, run.describe())
        for finding in findings:
            self.assertEqual(finding["severity"], "warning", run.describe())
            self.assertTrue((finding["hint"] or "").strip(), run.describe())
        strict = self.lint_json("--strict")
        self.assertEqual(strict.returncode, 1, strict.describe())
        return findings


# ---------------------------------------------------------------------------
# El acta canónica
# ---------------------------------------------------------------------------


class TestCanonicalCharterIsTheBaseline(CharterCase):
    """El punto de partida: el acta del contrato pasa las dieciséis reglas."""

    def test_the_canonical_charter_conforms_in_strict_mode(self) -> None:
        """Sin tocar nada, el acta canónica pasa con «--strict» y cero avisos."""
        run = self.assert_conforms(charter())
        self.assertEqual(run.json["ok"], True, run.describe())
        self.assertEqual(run.json["adopted"], True, run.describe())

    def test_the_canonical_charter_reports_what_it_declares(self) -> None:
        """El JSON cuenta lo que el acta trae: usuarios, capabilities, exclusiones y apuestas."""
        self.write(charter())
        run = self.lint_json()
        block = run.json["charter"]
        self.assertEqual(block["path"], CHARTER_RELPATH, run.describe())
        self.assertEqual(
            block["counts"],
            {"users": 2, "capabilities": 2, "out_of_scope": 2, "bets": 1},
            run.describe(),
        )
        self.assertEqual(
            block["capabilities"],
            [
                {"priority": 1, "slug": "booking", "risk": "high"},
                {"priority": 2, "slug": "availability", "risk": "medium"},
            ],
            run.describe(),
        )

    def test_the_text_report_closes_with_the_charter_verdict(self) -> None:
        """El informe de texto cierra hablando del acta, no de requisitos que no hay."""
        self.write(charter())
        run = self.lint("--no-color")
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("El acta define el proyecto", run.stdout)
        self.assertIn("2 usuarios · 2 capabilities · 2 exclusiones · 1 apuesta", run.stdout)
        # El resumen de `report` habla de requisitos y deltas, y un acta no tiene
        # ninguna de las dos cosas: contarlas aquí sería contar lo que no hay.
        self.assertNotIn("requisito", run.stdout)
        self.assertNotIn("delta", run.stdout)


# ---------------------------------------------------------------------------
# C01 · las cinco secciones obligatorias
# ---------------------------------------------------------------------------


class TestRuleC01Sections(CharterCase):
    """C01 · Purpose, Users, Capabilities, Out of scope y Bets, las cinco."""

    def test_c01_accepts_the_five_sections(self) -> None:
        """El acta canónica declara las cinco y no dispara nada."""
        self.assert_conforms(charter())

    def test_c01_fails_when_any_required_section_is_missing(self) -> None:
        """Quitar cualquiera de las cinco dispara C01 y sólo C01."""
        for name in charter_lint.REQUIRED_SECTIONS:
            with self.subTest(section=name):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(CHARTER_RELPATH, charter(omit=(name,)))
                run = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
                self.assertEqual(run.rule_set(), {"C01"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                self.assertEqual(len(run.findings_for("C01")), 1, run.describe())
                self.assertIn(f"«## {name}»", run.findings_for("C01")[0]["message"])

    def test_c01_counts_every_missing_section_separately(self) -> None:
        """Un acta vacía dispara los cinco C01, uno por sección, y nada más."""
        findings = self.assert_only_error("C01", "")
        self.assertEqual(len(findings), 5)
        for name in charter_lint.REQUIRED_SECTIONS:
            self.assertTrue(
                any(f"«## {name}»" in finding["message"] for finding in findings),
                findings,
            )

    def test_c01_points_at_the_spanish_heading_instead_of_asking_for_a_new_one(self) -> None:
        """Con «## Propósito» escrito, la pista dice que se renombre, no que se escriba."""
        text = charter(omit=(charter_lint.SECTION_PURPOSE,)).replace(
            "## Users", "## Propósito\n\n" + DEFAULT_PURPOSE + "\n\n## Users", 1
        )
        findings = self.assert_only_error("C01", text)
        hint = findings[0]["hint"] or ""
        self.assertIn("«## Propósito»", hint)
        self.assertIn("«## Purpose»", hint)
        self.assertIn("renómbralo", hint.lower())


# ---------------------------------------------------------------------------
# C02 · el propósito, de una a tres frases
# ---------------------------------------------------------------------------


class TestRuleC02Purpose(CharterCase):
    """C02 · el propósito dice qué cambia en el mundo, en una a tres frases."""

    def test_c02_accepts_one_to_three_sentences(self) -> None:
        """Una frase, dos y tres pasan; el número de frases es un rango, no un dogma."""
        purposes = {
            "una": DEFAULT_PURPOSE,
            "dos": (
                "Que un restaurante pequeño deje de perder mesas. Que el dueño sepa "
                "cuántas quedan sin llamar a nadie."
            ),
            "tres": (
                "Que un restaurante pequeño deje de perder mesas. Que el dueño sepa "
                "cuántas quedan. Que el cliente reserve a las tres de la mañana si le "
                "apetece."
            ),
        }
        for label, purpose in purposes.items():
            with self.subTest(sentences=label):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(CHARTER_RELPATH, charter(purpose=purpose))
                run = project.run(
                    CHARTER_LINT_PY, "--root", str(project.root), "--json", "--strict"
                )
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    def test_c02_fails_on_an_empty_purpose(self) -> None:
        """Un «## Purpose» sin nada debajo dispara C02."""
        findings = self.assert_only_error("C02", charter(purpose=""))
        self.assertIn("está vacía", findings[0]["message"])
        self.assertIn("qué cambia", findings[0]["hint"] or "")

    def test_c02_fails_when_the_purpose_runs_past_three_sentences(self) -> None:
        """Cuatro frases dispara C02 y el mensaje dice cuántas hay."""
        purpose = (
            "Que un restaurante pequeño deje de perder mesas. Que el dueño sepa "
            "cuántas quedan. Que el cliente reserve cuando quiera. Y que nadie tenga "
            "que descifrar la letra del cuaderno."
        )
        findings = self.assert_only_error("C02", charter(purpose=purpose))
        self.assertIn("4 frases", findings[0]["message"])

    def test_c02_does_not_split_a_purpose_on_a_thousands_separator(self) -> None:
        """«15.000» es un número, no dos frases: el propósito sigue siendo uno."""
        purpose = (
            "Que las 15.000 reservas al año de un restaurante pequeño dejen de vivir en "
            "un cuaderno."
        )
        self.assert_conforms(charter(purpose=purpose))

    def test_c02_does_not_split_a_purpose_on_an_abbreviation(self) -> None:
        """«S.L.» no abre una frase nueva: detrás no hay ni un espacio ni una mayúscula.

        Contando el punto de la abreviatura, este propósito de dos frases salía
        con cuatro y C02 lo rechazaba por largo. Una regla que rechaza prosa
        correcta se acaba desactivando entera.
        """
        purpose = (
            "Que las tiendas de la S.L. dejen de cuadrar a mano el cierre de caja. "
            "Que el gerente lo vea cerrado a las 22:00 sin llamar a ninguna."
        )
        self.assert_conforms(charter(purpose=purpose))

    def test_c02_still_counts_the_sentences_that_are_sentences(self) -> None:
        """El guardia de la abreviatura no puede dejar pasar un propósito largo.

        Es la otra mitad del cambio anterior: cinco frases de verdad —cada una
        detrás de un punto y un espacio— siguen contando cinco, y el signo de
        apertura de la interrogativa abre frase igual que una mayúscula.
        """
        purpose = (
            "Que el bar deje de perder mesas. ¿Y las cenas de empresa? También. "
            "Que el dueño lo vea desde el móvil. Que nadie descifre el cuaderno."
        )
        findings = self.assert_only_error("C02", charter(purpose=purpose))
        self.assertIn("5 frases", findings[0]["message"])


# ---------------------------------------------------------------------------
# C03 · los usuarios
# ---------------------------------------------------------------------------


class TestRuleC03Users(CharterCase):
    """C03 · al menos un usuario, y cada uno con su hoy y su con esto."""

    def test_c03_accepts_users_that_declare_both_bullets(self) -> None:
        """Dos usuarios completos, y también uno solo, pasan sin decir nada."""
        self.assert_conforms(charter())
        self.assert_conforms(charter(users=[User()]))

    def test_c03_fails_when_the_charter_declares_no_user(self) -> None:
        """Un «## Users» sin ningún «###» dispara C03."""
        findings = self.assert_only_error("C03", charter(users=""))
        self.assertIn("ningún usuario", findings[0]["message"])

    def test_c03_fails_when_a_user_omits_what_changes_for_them(self) -> None:
        """Sin «**con esto:**» el acta cuenta el hoy y no promete nada."""
        findings = self.assert_only_error(
            "C03", charter(users=[User(after=None), DEFAULT_USERS[1]])
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["requirement_id"], "owner")
        self.assertIn("«**con esto:**»", findings[0]["message"])

    def test_c03_tells_an_empty_bullet_apart_from_a_missing_one(self) -> None:
        """Una viñeta escrita y vacía no es una viñeta ausente: el mensaje lo dice."""
        findings = self.assert_only_error(
            "C03", charter(users=[User(before=""), DEFAULT_USERS[1]])
        )
        self.assertIn("está vacío", findings[0]["message"])
        self.assertNotIn("no declara", findings[0]["message"])


# ---------------------------------------------------------------------------
# C04 · la tabla trae capabilities
# ---------------------------------------------------------------------------


class TestRuleC04Capabilities(CharterCase):
    """C04 · hay al menos una capability priorizada."""

    def test_c04_accepts_a_table_with_one_capability(self) -> None:
        """Con una sola fila ya hay por dónde empezar."""
        self.assert_conforms(charter(capabilities=[Cap(risk="medium")]))

    def test_c04_fails_when_the_section_has_no_table(self) -> None:
        """Un «## Capabilities» sin tabla dispara C04."""
        findings = self.assert_only_error("C04", charter(capabilities=""))
        self.assertIn("no trae ninguna tabla", findings[0]["message"])

    def test_c04_fails_when_the_table_has_only_its_header(self) -> None:
        """Encabezado y separador sin filas: la tabla no declara ninguna capability."""
        findings = self.assert_only_error("C04", charter(capabilities=[]))
        self.assertIn("sólo trae el encabezado", findings[0]["message"])

    def test_c04_fails_when_the_table_declares_the_wrong_columns(self) -> None:
        """Con cuatro columnas no se puede saber cuál es cuál: no se lee ninguna fila."""
        table = (
            "| # | Capability | Done when | Risk |\n"
            "|---|---|---|---|\n"
            "| 1 | `booking` | un cliente reserva y ve su hora | high |"
        )
        findings = self.assert_only_error("C04", charter(capabilities=table))
        self.assertIn("exactamente cinco", findings[0]["message"])
        self.assertIn(charter_lint.TABLE_HEADER_TEXT, findings[0]["hint"] or "")

    def test_c04_reads_a_table_written_without_its_outer_pipes(self) -> None:
        """Sin barras exteriores es markdown válido, y su cabecera empieza por «#».

        Un «# | Capability | …» casa también con la forma de un título de nivel
        uno, así que cerraba «## Capabilities» y el linter contestaba que la
        sección no traía ninguna tabla: un acta legítima rechazada por un motivo
        que no era el suyo.
        """
        table = (
            "# | Capability | Qué podrá hacer | Done when | Risk\n"
            "--- | --- | --- | --- | ---\n"
            "1 | `booking` | reservar una mesa | un cliente reserva y ve su hora | medium"
        )
        self.assert_conforms(charter(capabilities=table))

    def test_c04_keeps_an_escaped_pipe_inside_the_cell(self) -> None:
        """«\\|» es una barra literal, no un separador: las columnas no se corren."""
        done_when = (
            "el contable abre el fichero y ve las columnas separadas por \\| "
            "sin ninguna fila partida"
        )
        self.assert_conforms(
            charter(capabilities=[Cap(slug="csv-export", done_when=done_when, risk="medium")])
        )
        self.assertEqual(
            charter_lint._table_cells("| a \\| b | c |"),
            ["a | b", "c"],
        )


# ---------------------------------------------------------------------------
# C05 · el slug de la capability
# ---------------------------------------------------------------------------


class TestRuleC05Slugs(CharterCase):
    """C05 · cada slug es kebab-case válido y no lo repite nadie."""

    def test_c05_accepts_distinct_kebab_case_slugs(self) -> None:
        """Dos slugs bien escritos y distintos no disparan nada."""
        self.assert_conforms(
            charter(
                capabilities=[
                    Cap(slug="table-booking"),
                    Cap(priority=2, slug="availability", risk="low"),
                ]
            )
        )

    def test_c05_fails_on_a_slug_that_is_not_kebab_case(self) -> None:
        """«Booking Table» no puede ser el nombre de un directorio de capability."""
        findings = self.assert_only_error(
            "C05",
            charter(capabilities=[Cap(slug="Booking Table"), DEFAULT_CAPABILITIES[1]]),
        )
        self.assertIn("no es kebab-case", findings[0]["message"])
        self.assertIn("«`booking-table`»", findings[0]["hint"] or "")

    def test_c05_fails_when_two_capabilities_share_a_slug(self) -> None:
        """Dos filas con el mismo slug compartirían también su «spec.md»."""
        findings = self.assert_only_error(
            "C05",
            charter(capabilities=[Cap(), Cap(priority=2, risk="medium")]),
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["requirement_id"], "booking")
        self.assertIn("ya está declarado", findings[0]["message"])

    def test_c05_accepts_a_kebab_case_user_slug(self) -> None:
        """Un papel bien nombrado no dispara nada."""
        self.assert_conforms(charter(users=[User(slug="shift-lead", role="Coordinadora")]))

    def test_c05_fails_on_a_user_slug_that_is_not_kebab_case(self) -> None:
        """El papel se nombra con un identificador, no con su título."""
        findings = self.assert_only_error(
            "C05", charter(users=[User(slug="Coordinadora", role="Coordinadora de turnos")])
        )
        self.assertIn("no es kebab-case", findings[0]["message"])
        self.assertIn("### coordinadora · Coordinadora de turnos", findings[0]["hint"] or "")

    def test_c05_fails_when_the_user_header_has_no_separator(self) -> None:
        """Un slug con espacios se traga el encabezado entero y deja el papel sin id."""
        findings = self.assert_only_error(
            "C05", charter(users=[User(slug="Coordinadora De Turnos", role="")])
        )
        self.assertIn("no separa el slug del nombre del papel", findings[0]["message"])
        self.assertIn("### coordinadora-de-turnos ·", findings[0]["hint"] or "")

    def test_c05_proposes_both_halves_when_the_header_does_carry_a_separator(self) -> None:
        """Con «·» pero el slug con espacios, la pista parte por donde el autor quiso."""
        self.write(charter(users=[User(slug="Coordinadora De Turnos · Coordinadora", role="")]))
        hint = self.assert_only_error("C05")[0]["hint"] or ""
        self.assertIn("### coordinadora-de-turnos · Coordinadora", hint)
        # La pista no repite el título entero a los dos lados del separador.
        self.assertNotIn("Coordinadora De Turnos · Coordinadora De Turnos", hint)


# ---------------------------------------------------------------------------
# C06 · las prioridades
# ---------------------------------------------------------------------------


class TestRuleC06Priorities(CharterCase):
    """C06 · las prioridades son 1…N, sin huecos ni repetidos."""

    def test_c06_accepts_a_complete_series_from_one(self) -> None:
        """1, 2 y 3 en cualquier orden de escritura es una serie completa."""
        self.assert_conforms(
            charter(
                capabilities=[
                    Cap(),
                    Cap(priority=3, slug="reminders", risk="low"),
                    Cap(priority=2, slug="availability", risk="medium"),
                ]
            )
        )

    def test_c06_fails_on_a_gap_in_the_series(self) -> None:
        """1 y 3 deja la 2 sin decidir por nadie."""
        findings = self.assert_only_error(
            "C06",
            charter(
                capabilities=[Cap(), Cap(priority=3, slug="availability", risk="medium")]
            ),
        )
        self.assertIn("falta la 2", findings[0]["message"])

    def test_c06_fails_on_a_repeated_priority(self) -> None:
        """Dos capabilities no pueden ser la primera."""
        findings = self.assert_only_error(
            "C06",
            charter(
                capabilities=[Cap(), Cap(priority=1, slug="availability", risk="medium")]
            ),
        )
        self.assertIn("repetida", findings[0]["message"])

    def test_c06_fails_when_a_priority_is_not_an_integer(self) -> None:
        """Un orden se cuenta: «uno» no es una prioridad."""
        findings = self.assert_only_error(
            "C06",
            charter(
                capabilities=[Cap(priority="uno"), Cap(priority=2, slug="availability", risk="medium")]
            ),
        )
        self.assertEqual(len(findings), 1)
        self.assertIn("«uno»", findings[0]["message"])


# ---------------------------------------------------------------------------
# C07 · el oráculo del acta
# ---------------------------------------------------------------------------


class TestRuleC07DoneWhen(CharterCase):
    """C07 · sin «Done when» una capability es un deseo. **El corazón del acta.**"""

    def test_c07_accepts_a_capability_with_a_done_when(self) -> None:
        """Con criterio de terminación escrito, la regla se calla."""
        self.assert_conforms(charter())

    def test_c07_fails_when_a_capability_has_no_done_when(self) -> None:
        """Sin «Done when» nadie puede afirmar que la capability está hecha."""
        findings = self.assert_only_error(
            "C07", charter(capabilities=[Cap(done_when=""), DEFAULT_CAPABILITIES[1]])
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["requirement_id"], "booking")
        # El mensaje tiene que explicar **por qué** importa, no sólo qué falta.
        self.assertIn("no es una capability, es un deseo", findings[0]["message"])
        hint = findings[0]["hint"] or ""
        self.assertIn("quién hace qué y qué ve", hint)
        self.assertIn("un cliente reserva y recibe la confirmación con su hora", hint)

    def test_c07_speaks_once_per_capability(self) -> None:
        """Dos capabilities sin criterio son dos hallazgos, no uno resumido."""
        findings = self.assert_only_error(
            "C07",
            charter(
                capabilities=[
                    Cap(done_when=""),
                    Cap(priority=2, slug="availability", done_when="", risk="medium"),
                ]
            ),
        )
        self.assertEqual(len(findings), 2)
        self.assertEqual(
            {finding["requirement_id"] for finding in findings}, {"booking", "availability"}
        )

    def test_c07_reaches_the_text_report_with_its_remedy(self) -> None:
        """El informe de texto trae el mensaje y el remedio, no sólo el código."""
        self.write(charter(capabilities=[Cap(done_when=""), DEFAULT_CAPABILITIES[1]]))
        run = self.lint("--no-color")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("C07", run.stdout)
        self.assertIn("es un deseo", run.stdout)
        self.assertIn("→ Escribe en la columna «Done when»", run.stdout)


# ---------------------------------------------------------------------------
# C08 · el «Done when» es observable
# ---------------------------------------------------------------------------


class TestRuleC08ObservableDoneWhen(CharterCase):
    """C08 · el criterio de terminación describe lo que se ve, no lo que se programa."""

    #: Frases que **mencionan** un verbo de implementación sin arrancar por él.
    #: Son las que convertirían la regla en ruido si se buscara la palabra suelta.
    MENTIONS = (
        "un cliente reserva y ve su hora confirmada sin configurar nada",
        "el dueño ve las mesas libres de hoy tras integrar el TPV",
        "el cliente recibe el recordatorio sin que nadie tenga que desplegar nada",
        "cualquiera puede usar el enlace del perfil y acabar con una mesa reservada",
    )

    def test_c08_accepts_a_done_when_that_only_mentions_an_implementation_verb(self) -> None:
        """Mencionar «configurar» de pasada no convierte el criterio en una tarea."""
        for done_when in self.MENTIONS:
            with self.subTest(done_when=done_when):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(
                    CHARTER_RELPATH,
                    charter(capabilities=[Cap(done_when=done_when), DEFAULT_CAPABILITIES[1]]),
                )
                run = project.run(
                    CHARTER_LINT_PY, "--root", str(project.root), "--json", "--strict"
                )
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    #: Un «Done when» plausible por cada verbo de la lista. Es un diccionario y
    #: no una plantilla para que el fixture se lea como algo que alguien
    #: escribiría de verdad, y porque así la suite se rompe el día en que se
    #: añada un verbo sin su caso.
    TASKS = {
        "implementar": "implementar el endpoint de reservas",
        "crear la tabla": "crear la tabla de reservas en la base de datos",
        "usar": "usar una cola para las confirmaciones",
        "refactorizar": "refactorizar el módulo de disponibilidad",
        "montar": "montar el formulario de reserva",
        "configurar": "configurar el envío de correos",
        "integrar": "integrar el calendario del restaurante",
        "desplegar": "desplegar la web en producción",
    }

    def test_c08_covers_every_verb_of_the_contract(self) -> None:
        """El fixture cubre la lista entera: añadir un verbo obliga a añadir su caso."""
        self.assertEqual(set(self.TASKS), set(charter_lint.IMPLEMENTATION_VERBS))

    def test_c08_fails_when_the_done_when_opens_with_an_implementation_verb(self) -> None:
        """Cada verbo de la lista, al principio de la frase, dispara C08 y sólo C08."""
        for verb, done_when in self.TASKS.items():
            with self.subTest(verb=verb):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(
                    CHARTER_RELPATH,
                    charter(
                        capabilities=[
                            Cap(done_when=done_when),
                            DEFAULT_CAPABILITIES[1],
                        ]
                    ),
                )
                run = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
                self.assertEqual(run.rule_set(), {"C08"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                finding = run.findings_for("C08")[0]
                self.assertIn(f"«{verb}»", finding["message"])
                # La pista tiene que enseñar la reescritura, no sólo prohibir.
                self.assertIn("quién hace qué y qué ve", finding["hint"] or "")

    def test_c08_ignores_accents_and_case_at_the_start(self) -> None:
        """«Implementar» con mayúscula es el mismo verbo que «implementar»."""
        findings = self.assert_only_error(
            "C08",
            charter(
                capabilities=[
                    Cap(done_when="Implementar la tabla de reservas"),
                    DEFAULT_CAPABILITIES[1],
                ]
            ),
        )
        self.assertIn("«implementar»", findings[0]["message"])

    def test_c08_is_decided_by_the_start_of_the_sentence(self) -> None:
        """La función que decide mira el arranque; en corto y sin fichero de por medio."""
        self.assertEqual(
            charter_lint._leading_implementation_verb("implementar el endpoint"),
            "implementar",
        )
        self.assertEqual(
            charter_lint._leading_implementation_verb("Crear la tabla de reservas"),
            "crear la tabla",
        )
        self.assertIsNone(
            charter_lint._leading_implementation_verb("un cliente reserva sin usar el teléfono")
        )
        # «usar» es prefijo de «usaría», y una regla que no mira la frontera de
        # palabra denuncia lo que no debe.
        self.assertIsNone(
            charter_lint._leading_implementation_verb("usaría el enlace del perfil")
        )

    #: El mismo verbo en participio, que es como se escribe de verdad. El tercer
    #: caso es, con estas palabras, uno de los tres ejemplos de lo que no vale
    #: que trae la plantilla del acta.
    PARTICIPLES = {
        "implementad": "implementado el endpoint de reservas",
        "montad": "montada la pantalla de disponibilidad",
        "configurad": "configurados los recordatorios por correo",
        "integrad": "integrado el calendario del restaurante",
        "desplegad": "desplegado en producción",
        "refactorizad": "refactorizado el módulo de reservas",
    }

    def test_c08_covers_every_participle_of_the_contract(self) -> None:
        """El fixture cubre la lista entera: añadir un participio obliga a su caso."""
        self.assertEqual(
            set(self.PARTICIPLES), set(charter_lint.IMPLEMENTATION_PARTICIPLE_STEMS)
        )

    def test_c08_fails_when_the_done_when_opens_with_a_participle(self) -> None:
        """«Desplegado en producción» es la misma tarea que «desplegar en producción»."""
        for stem, done_when in self.PARTICIPLES.items():
            with self.subTest(participle=stem):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(
                    CHARTER_RELPATH,
                    charter(capabilities=[Cap(done_when=done_when), DEFAULT_CAPABILITIES[1]]),
                )
                run = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
                self.assertEqual(run.rule_set(), {"C08"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                self.assertIn("quién hace qué y qué ve", run.findings_for("C08")[0]["hint"])

    #: Fórmulas que suenan a criterio y no lo son: ninguna arranca por un verbo
    #: de implementación, y ninguna contesta quién lo ve ni qué ve. Las dos
    #: primeras y la cuarta son las que la plantilla nombra como ejemplo de lo
    #: que no vale.
    EMPTY_FORMULAS = (
        "que sea rápido",
        "que funcione bien",
        "el sistema funciona correctamente",
        "la funcionalidad está completa",
        "está terminado",
        "ya está listo",
        "todo funciona",
        "sin errores",
        "cuando esté listo",
        "**está hecho.**",
    )

    def test_c08_fails_on_a_formula_that_can_be_declared_done_without_looking(self) -> None:
        """Una celda que es sólo la fórmula dispara C08 y explica qué falta."""
        for done_when in self.EMPTY_FORMULAS:
            with self.subTest(done_when=done_when):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(
                    CHARTER_RELPATH,
                    charter(capabilities=[Cap(done_when=done_when), DEFAULT_CAPABILITIES[1]]),
                )
                run = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
                self.assertEqual(run.rule_set(), {"C08"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                finding = run.findings_for("C08")[0]
                self.assertIn("sin mirar nada", finding["message"])
                # El remedio manda preguntar, no redactar mejor: rellenar el
                # fondo no es trabajo del linter ni de quien lo ejecuta.
                self.assertIn("una pregunta más", finding["hint"] or "")

    #: Las mismas palabras dentro de un criterio que sí dice quién ve qué. Son
    #: las que convertirían la regla en ruido si el patrón no cubriera la celda
    #: entera, y por eso valen más que los casos que fallan.
    FORMULAS_INSIDE_A_REAL_CRITERION = (
        "el dueño ve que la lista funciona correctamente después de un corte de luz",
        "el cliente completa la reserva sin errores en el primer intento",
        "la cocinera dice que ya está listo el pedido y el camarero lo ve en su pantalla",
        "el comercial encuentra el pedido y le parece rápido, por debajo de dos segundos",
    )

    def test_c08_accepts_a_criterion_that_merely_contains_the_formula(self) -> None:
        """Con sujeto y hecho delante, «funciona correctamente» deja de ser una fórmula."""
        for done_when in self.FORMULAS_INSIDE_A_REAL_CRITERION:
            with self.subTest(done_when=done_when):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(
                    CHARTER_RELPATH,
                    charter(capabilities=[Cap(done_when=done_when), DEFAULT_CAPABILITIES[1]]),
                )
                run = project.run(
                    CHARTER_LINT_PY, "--root", str(project.root), "--json", "--strict"
                )
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    def test_c08_decides_the_empty_formula_on_the_whole_cell(self) -> None:
        """La función que decide, en corto: la fórmula sola sí, la fórmula dentro no."""
        self.assertTrue(charter_lint._is_empty_formula("El sistema funciona correctamente."))
        self.assertTrue(charter_lint._is_empty_formula("**Que sea rápido**"))
        self.assertFalse(
            charter_lint._is_empty_formula("el dueño ve que funciona correctamente")
        )
        self.assertFalse(charter_lint._is_empty_formula(""))


# ---------------------------------------------------------------------------
# C09 · el riesgo
# ---------------------------------------------------------------------------


class TestRuleC09Risk(CharterCase):
    """C09 · «Risk» vale exactamente high, medium o low."""

    def test_c09_accepts_the_three_levels(self) -> None:
        """Los tres niveles del contrato pasan."""
        self.assert_conforms(
            charter(
                capabilities=[
                    Cap(risk="high"),
                    Cap(priority=2, slug="availability", risk="medium"),
                    Cap(priority=3, slug="reminders", risk="low"),
                ]
            )
        )

    def test_c09_fails_on_a_level_that_is_not_one_of_the_three(self) -> None:
        """«crítico» no es un nivel del acta."""
        findings = self.assert_only_error(
            "C09",
            charter(capabilities=[Cap(risk="crítico"), DEFAULT_CAPABILITIES[1]]),
        )
        self.assertIn("«crítico»", findings[0]["message"])

    def test_c09_tells_a_wrong_case_apart_from_a_wrong_level(self) -> None:
        """«High» es el nivel correcto mal escrito, y el remedio es otro."""
        findings = self.assert_only_error(
            "C09",
            charter(capabilities=[Cap(risk="High"), DEFAULT_CAPABILITIES[1]]),
        )
        self.assertIn("caja cambiada", findings[0]["message"])
        self.assertIn("«high»", findings[0]["hint"] or "")

    def test_c09_fails_when_the_column_is_empty(self) -> None:
        """Una capability sin riesgo declarado no dice cuánto es terreno conocido."""
        findings = self.assert_only_error(
            "C09",
            charter(capabilities=[Cap(risk=""), DEFAULT_CAPABILITIES[1]]),
        )
        self.assertIn("no declara «Risk»", findings[0]["message"])


# ---------------------------------------------------------------------------
# C10 · el no-alcance
# ---------------------------------------------------------------------------


class TestRuleC10OutOfScope(CharterCase):
    """C10 · un proyecto sin no-alcance no ha decidido nada. **El otro corazón.**"""

    def test_c10_accepts_a_charter_that_says_no_to_something(self) -> None:
        """Con una sola exclusión ya hay frontera."""
        self.assert_conforms(
            charter(out_of_scope=["**Pagos.** No se cobra nada en la v1."])
        )

    def test_c10_fails_when_nothing_is_left_out(self) -> None:
        """Un «## Out of scope» vacío dispara C10 y explica por qué importa."""
        findings = self.assert_only_error("C10", charter(out_of_scope=""))
        self.assertEqual(len(findings), 1)
        self.assertIn("todavía no ha decidido nada", findings[0]["message"])
        hint = findings[0]["hint"] or ""
        self.assertIn("- **<Qué>.** <por qué no>", hint)
        self.assertIn("cuesta una discusión", hint)

    def test_c10_reaches_the_text_report_with_its_remedy(self) -> None:
        """El informe de texto trae el remedio del no-alcance, no sólo el código."""
        self.write(charter(out_of_scope=""))
        run = self.lint("--no-color")
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("C10", run.stdout)
        self.assertIn("no ha dicho que no a nada", run.stdout)

    #: Viñetas que ocupan la sección sin excluir nada. Escribir una era, hasta
    #: que la regla las contó aparte, la forma de apagar C10 con una línea.
    FILLER = (
        "nada por ahora",
        "Nada.",
        "ninguno",
        "de momento nada",
        "TBD",
        "por definir",
        "ya veremos",
        "todo entra",
        "—",
    )

    def test_c10_fails_when_the_only_entry_excludes_nothing(self) -> None:
        """Una viñeta de relleno no es un no: C10 salta igual que si no hubiera nada."""
        for text in self.FILLER:
            with self.subTest(entry=text):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(CHARTER_RELPATH, charter(out_of_scope=[text]))
                run = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
                self.assertEqual(run.rule_set(), {"C10"}, run.describe())
                self.assertEqual(run.returncode, 1, run.describe())
                finding = run.findings_for("C10")[0]
                # El mensaje cita la viñeta: quien la escribió tiene que
                # reconocerla, o buscará una sección vacía que no está vacía.
                self.assertIn("no excluye nada", finding["message"])
                self.assertIn("más adelante", finding["hint"] or "")

    def test_c10_accepts_a_real_exclusion_among_the_filler(self) -> None:
        """Con un no de verdad ya hay frontera, aunque le acompañe un «ya veremos»."""
        self.assert_conforms(
            charter(
                out_of_scope=[
                    "nada por ahora",
                    "**Pagos.** No se cobra nada en la v1; no compensa todavía.",
                ]
            )
        )

    def test_c10_does_not_mistake_a_real_exclusion_for_filler(self) -> None:
        """Nombrar algo basta: en cuanto la viñeta nombra algo, deja de ser relleno."""
        for text in (
            "**Pagos.** No se cobra nada en la v1.",
            "Nada de pagos en la v1: el riesgo regulatorio no compensa.",
            "Ninguna integración con portales de reservas, que no es el problema.",
        ):
            with self.subTest(entry=text):
                self.assertFalse(charter_lint._is_filler_exclusion(text))


# ---------------------------------------------------------------------------
# C11 · la confianza de la apuesta
# ---------------------------------------------------------------------------


class TestRuleC11BetConfidence(CharterCase):
    """C11 · cada apuesta declara cuánto se confía en lo que supone."""

    def test_c11_accepts_the_three_levels(self) -> None:
        """high, medium y low pasan; sólo «low» arrastra fecha de revisión."""
        for level in ("high", "medium", "low"):
            with self.subTest(confidence=level):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(CHARTER_RELPATH, charter(bets=[Bet(confidence=level)]))
                run = project.run(
                    CHARTER_LINT_PY, "--root", str(project.root), "--json", "--strict"
                )
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    def test_c11_fails_when_a_bet_declares_no_confidence(self) -> None:
        """Una apuesta que no dice cuánto se confía en ella no es una apuesta."""
        findings = self.assert_only_error(
            "C11", charter(bets=[Bet(confidence=None, revisit=None)])
        )
        self.assertEqual(findings[0]["requirement_id"], "B-001")
        self.assertIn("no declara «confidence:»", findings[0]["message"])

    def test_c11_tells_a_wrong_case_apart_from_a_wrong_level(self) -> None:
        """«LOW» es el nivel correcto mal escrito, y mientras tanto no cuenta."""
        findings = self.assert_only_error(
            "C11", charter(bets=[Bet(confidence="LOW", revisit=None)])
        )
        self.assertIn("caja cambiada", findings[0]["message"])

    def test_c11_fails_on_an_invented_level(self) -> None:
        """«segurísimo» no es ninguno de los tres."""
        findings = self.assert_only_error(
            "C11", charter(bets=[Bet(confidence="segurísimo", revisit=None)])
        )
        self.assertIn("«confidence: segurísimo»", findings[0]["message"])


# ---------------------------------------------------------------------------
# C12 · la fecha de revisión
# ---------------------------------------------------------------------------


class TestRuleC12Revisit(CharterCase):
    """C12 · una apuesta en «low» dice qué hecho la resuelve, y no cuándo caduca."""

    def test_c12_accepts_a_fact_and_ignores_the_other_levels(self) -> None:
        """En «low» con el hecho escrito pasa; en «medium» no se le reclama ninguno."""
        self.assert_conforms(charter(bets=[Bet(revisit="cuando entre el primer cliente")]))
        self.assert_conforms(charter(bets=[Bet(confidence="medium", revisit=None)]))

    def test_c12_fails_when_a_low_bet_has_no_revisit(self) -> None:
        """Sin nada que la resuelva, la suposición deja de ser apuesta y pasa a ser el sistema."""
        findings = self.assert_only_error("C12", charter(bets=[Bet(revisit=None)]))
        self.assertIn("no trae «revisit:»", findings[0]["message"])
        self.assertIn("cómo funciona el sistema", findings[0]["message"])

    def test_c12_fails_when_the_revisit_is_empty(self) -> None:
        """La línea escrita y vacía promete decir qué resuelve la apuesta y no lo dice."""
        findings = self.assert_only_error("C12", charter(bets=[Bet(revisit="")]))
        self.assertIn("está vacío", findings[0]["message"])

    def test_c12_rejects_a_future_date(self) -> None:
        """Una fecha es lo que este campo dejó de admitir, apunte hacia donde apunte."""
        future = future_date(30)
        findings = self.assert_only_error("C12", charter(bets=[Bet(revisit=future)]))
        self.assertIn(future, findings[0]["message"])
        self.assertIn("es una fecha", findings[0]["message"])
        self.assertIn("hecho que resuelve la apuesta", findings[0]["message"])

    def test_c12_rejects_a_past_date_for_the_same_reason(self) -> None:
        """Hacia atrás tampoco: el problema no es que venza, es que no dice qué mirar."""
        findings = self.assert_only_error("C12", charter(bets=[Bet(revisit=past_date(30))]))
        self.assertIn("es una fecha", findings[0]["message"])

    def test_c12_rejects_filler_that_means_later(self) -> None:
        """«Ya veremos» ocupa la línea sin nombrar nada, que es no tener apuesta."""
        for filler in ("ya veremos", "más adelante", "TBD", "el próximo trimestre", "3 meses"):
            with self.subTest(revisit=filler):
                findings = self.assert_only_error("C12", charter(bets=[Bet(revisit=filler)]))
                self.assertIn("no nombra ningún hecho", findings[0]["message"])

    def test_c12_accepts_a_fact_that_merely_mentions_a_period(self) -> None:
        """«Tras las tres primeras semanas de uso real» nombra un hecho, no un plazo vacío."""
        self.assert_conforms(
            charter(bets=[Bet(revisit="tras las tres primeras semanas de uso real")])
        )

    def test_c12_judges_the_shape_at_every_confidence_level(self) -> None:
        """Sólo «low» está obligada a traer «revisit:»; escribirlo mal lo puede cualquiera.

        Las fechas inventadas se acumulan justo en «medium», que es donde acaba
        casi todo lo que no es un hecho comprobado ni una corazonada. Una regla
        que sólo mirase «low» las dejaría pasar todas.
        """
        for level in ("high", "medium"):
            with self.subTest(confidence=level):
                findings = self.assert_only_error(
                    "C12", charter(bets=[Bet(confidence=level, revisit=future_date(30))])
                )
                self.assertIn("es una fecha", findings[0]["message"])

    def test_c12_lets_a_non_low_bet_omit_the_revisit(self) -> None:
        """Lo que sigue siendo exclusivo de «low» es la obligación de traerlo."""
        self.assert_conforms(charter(bets=[Bet(confidence="medium", revisit=None)]))
        self.assert_conforms(charter(bets=[Bet(confidence="high", revisit=None)]))

    def test_c12_points_at_the_fact_in_its_hint(self) -> None:
        """El remedio enseña la forma que se pide, no la que se acaba de rechazar."""
        findings = self.assert_only_error("C12", charter(bets=[Bet(revisit=future_date(30))]))
        self.assertIn(charter_lint.REVISIT_EXAMPLE, findings[0]["hint"])


# ---------------------------------------------------------------------------
# C13 · el identificador de la apuesta
# ---------------------------------------------------------------------------


class TestRuleC13BetIdentifier(CharterCase):
    """C13 · el identificador casa «B-NNN» y no lo repite nadie."""

    def test_c13_accepts_well_formed_unique_identifiers(self) -> None:
        """Dos apuestas con identificadores distintos y bien formados pasan."""
        self.assert_conforms(
            charter(
                bets=[
                    Bet(),
                    Bet(
                        id="B-002",
                        title="El dueño mira el móvil en la cocina",
                        prose="Damos por hecho que el móvil está a mano durante el servicio.",
                        confidence="medium",
                        why="lo hemos visto en dos restaurantes, no en veinte",
                        revisit=None,
                    ),
                ]
            )
        )

    def test_c13_fails_on_a_malformed_identifier(self) -> None:
        """«B-1» no es «B-001»: el molde son tres dígitos."""
        findings = self.assert_only_error("C13", charter(bets=[Bet(id="B-1")]))
        self.assertIn("«B-1»", findings[0]["message"])
        self.assertIn("«B-NNN»", findings[0]["message"])

    def test_c13_fails_when_two_bets_share_an_identifier(self) -> None:
        """Dos apuestas con el mismo identificador no se pueden citar por separado."""
        findings = self.assert_only_error(
            "C13",
            charter(
                bets=[
                    Bet(),
                    Bet(
                        title="Nadie llama para cambiar la hora",
                        prose="Damos por hecho que el cambio de hora se hace por el enlace.",
                        confidence="medium",
                        revisit=None,
                    ),
                ]
            ),
        )
        self.assertEqual(len(findings), 1)
        self.assertIn("ya está declarado", findings[0]["message"])


# ---------------------------------------------------------------------------
# C14 · «fatal:» (aviso)
# ---------------------------------------------------------------------------


class TestRuleC14Fatal(CharterCase):
    """C14 · «fatal:» vale «yes» o «no» cuando está escrito."""

    def test_c14_accepts_yes_no_and_its_absence(self) -> None:
        """Los dos valores pasan, y no escribir la clave también."""
        for value in ("yes", "no", None):
            with self.subTest(fatal=value):
                project = Project()
                self.addCleanup(project.cleanup)
                project.write(CHARTER_RELPATH, charter(bets=[Bet(fatal=value)]))
                run = project.run(
                    CHARTER_LINT_PY, "--root", str(project.root), "--json", "--strict"
                )
                self.assertEqual(run.rules(), [], run.describe())
                self.assertEqual(run.returncode, 0, run.describe())

    def test_c14_warns_on_any_other_answer(self) -> None:
        """«quizá» no responde a si el proyecto se cae: es un aviso, no un error."""
        findings = self.assert_only_warning("C14", charter(bets=[Bet(fatal="quizá")]))
        self.assertIn("«fatal: quizá»", findings[0]["message"])
        self.assertIn("«fatal: yes»", findings[0]["hint"] or "")


# ---------------------------------------------------------------------------
# C15 · riesgo alto sin apuestas (aviso)
# ---------------------------------------------------------------------------


class TestRuleC15RiskWithoutBets(CharterCase):
    """C15 · un riesgo alto sin ninguna suposición escrita."""

    def test_c15_stays_quiet_when_the_risk_is_backed_by_a_bet(self) -> None:
        """Con una apuesta declarada, el riesgo alto no dispara nada."""
        self.assert_conforms(charter())

    def test_c15_stays_quiet_without_high_risk_capabilities(self) -> None:
        """Sin riesgo alto, un acta sin apuestas es perfectamente legítima."""
        self.assert_conforms(
            charter(
                capabilities=[
                    Cap(risk="medium"),
                    Cap(priority=2, slug="availability", risk="low"),
                ],
                bets="",
            )
        )

    def test_c15_warns_on_high_risk_with_no_bets_declared(self) -> None:
        """Riesgo alto y cero apuestas: nadie va a revisar lo que se está suponiendo."""
        findings = self.assert_only_warning("C15", charter(bets=""))
        self.assertIn("«booking»", findings[0]["message"])
        self.assertIn("ninguna apuesta", findings[0]["message"])


# ---------------------------------------------------------------------------
# C16 · el orden del acta y el orden real (aviso)
# ---------------------------------------------------------------------------


class TestRuleC16LivePriority(CharterCase):
    """C16 · lo que ya se está especificando y lo que el acta pone primero."""

    def test_c16_stays_quiet_when_nothing_is_specified_yet(self) -> None:
        """Un acta recién escrita, sin ninguna capability viva, no dispara nada."""
        self.assert_conforms(charter())

    def test_c16_stays_quiet_when_the_order_is_respected(self) -> None:
        """La prioridad 1 viva y la 2 pendiente es exactamente el plan del acta."""
        self.write_spec("booking")
        self.assert_conforms(charter())

    def test_c16_stays_quiet_when_everything_is_already_specified(self) -> None:
        """Con las dos vivas no hay ningún adelantamiento que señalar."""
        self.write_spec("booking")
        self.write_spec("availability")
        self.assert_conforms(charter())

    def test_c16_warns_when_a_later_capability_is_specified_first(self) -> None:
        """La 2 viva y la 1 sin nada: el orden que se sigue no es el que el acta declara."""
        self.write_spec("availability")
        findings = self.assert_only_warning("C16", charter())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["requirement_id"], "availability")
        self.assertIn(".venoxia/capabilities/availability/spec.md", findings[0]["message"])
        self.assertIn("«booking»", findings[0]["message"])
        self.assertIn("/venoxia:specify", findings[0]["hint"] or "")


# ---------------------------------------------------------------------------
# El parseo no lanza
# ---------------------------------------------------------------------------


class TestMalformedCharterNeverRaises(CharterCase):
    """Un acta deforme produce hallazgos, nunca una traza de Python.

    Quien está escribiendo su primer acta se merece un veredicto en español, y
    una traza delante no explica nada: hace desinstalar el plugin.
    """

    def assert_no_traceback(self, run: CompletedRun) -> None:
        """Ni traza ni código de salida inesperado."""
        self.assertNotIn("Traceback", run.stderr, run.describe())
        self.assertNotIn("Traceback", run.stdout, run.describe())
        self.assertIn(run.returncode, (0, 1), run.describe())

    def test_an_empty_file_reports_the_missing_sections(self) -> None:
        """Un fichero vacío son cinco secciones que faltan, no un fallo."""
        self.write("")
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.rule_set(), {"C01"}, run.describe())

    def test_a_charter_with_only_headings_reports_every_empty_section(self) -> None:
        """Las cinco secciones vacías disparan las cuatro reglas de contenido."""
        self.write(
            charter(purpose="", users="", capabilities="", out_of_scope="", bets="")
        )
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.rule_set(), {"C02", "C03", "C04", "C10"}, run.describe())

    def test_a_table_with_missing_columns_reports_no_readable_capability(self) -> None:
        """Tres columnas no se pueden repartir en cinco sin inventarse cuál es cuál."""
        table = "| # | Capability | Risk |\n|---|---|---|\n| 1 | `booking` | high |"
        self.write(charter(capabilities=table))
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.rule_set(), {"C04"}, run.describe())

    def test_a_table_without_a_separator_row_is_still_read(self) -> None:
        """El separador es cosmética de markdown: sin él, las filas se leen igual.

        El linter juzga lo que el acta dice, no cómo se ve renderizada. Tumbar un
        acta por una fila de guiones sería castigar la forma y no el contenido.
        """
        table = (
            "| # | Capability | Qué podrá hacer | Done when | Risk |\n"
            + DEFAULT_CAPABILITIES[0].render()
            + "\n"
            + DEFAULT_CAPABILITIES[1].render()
        )
        self.write(charter(capabilities=table))
        run = self.lint_json("--strict")
        self.assert_no_traceback(run)
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.json["charter"]["counts"]["capabilities"], 2, run.describe())

    def test_the_guide_comments_of_the_template_are_not_read_as_content(self) -> None:
        """Los comentarios guía de la plantilla no son lo que el acta dice.

        La plantilla se reparte llena de ellos y quien la rellena los va
        borrando a medida que escribe. Un comentario que explica la tabla —con
        sus barras y sus viñetas de ejemplo dentro— no puede convertirse en una
        capability ni en un usuario que nadie ha declarado.
        """
        comment = (
            "<!-- La tabla lleva cinco columnas exactas:\n"
            "     | # | Capability | Qué podrá hacer | Done when | Risk |\n"
            "     y una fila por capability, como\n"
            "     | 9 | `ejemplo` | lo que sea | Implementar lo que sea | altísimo |\n"
            "     Bórrame al rellenar. -->\n"
        )
        self.write(
            charter(
                capabilities=comment + "\n" + _capabilities_body(list(DEFAULT_CAPABILITIES)),
                out_of_scope="<!-- una viñeta por cada no -->\n"
                + _out_of_scope_body(list(DEFAULT_OUT_OF_SCOPE)),
            )
        )
        run = self.lint_json("--strict")
        self.assert_no_traceback(run)
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(
            run.json["charter"]["counts"],
            {"users": 2, "capabilities": 2, "out_of_scope": 2, "bets": 1},
            run.describe(),
        )

    def test_an_example_table_inside_a_code_fence_is_not_read_as_capabilities(self) -> None:
        """Una tabla de muestra entre vallas es un ejemplo, no dos capabilities más.

        La skill que escribe el acta enseña la forma de la tabla; leer esa
        muestra como contenido llenaría el informe de slugs duplicados que nadie
        ha escrito.
        """
        example = (
            "Así se escribe la tabla:\n\n"
            "```markdown\n"
            "| # | Capability | Qué podrá hacer | Done when | Risk |\n"
            "|---|---|---|---|---|\n"
            "| 1 | `booking` | reservar | Implementar el endpoint | alto |\n"
            "```\n"
        )
        self.write(charter(capabilities=example + "\n" + _capabilities_body(list(DEFAULT_CAPABILITIES))))
        run = self.lint_json("--strict")
        self.assert_no_traceback(run)
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.json["charter"]["counts"]["capabilities"], 2, run.describe())

    def test_a_repeated_section_does_not_lose_half_the_document(self) -> None:
        """Dos «## Bets» son dos apuestas leídas, no una perdida en silencio."""
        second = Bet(
            id="B-002",
            title="El servicio de mesas no cambia en temporada alta",
            prose="Damos por hecho que la sala se organiza igual en agosto que en enero.",
            confidence="medium",
            why="no hemos visto un agosto todavía",
            revisit=None,
        )
        text = charter() + "\n## Bets\n\n" + second.render() + "\n"
        self.write(text)
        run = self.lint_json("--strict")
        self.assert_no_traceback(run)
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.json["charter"]["counts"]["bets"], 2, run.describe())

    def test_truncated_markdown_reports_what_is_missing(self) -> None:
        """Un acta cortada por la mitad se juzga por lo que le queda."""
        text = charter()
        self.write(text[: len(text) // 2])
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("C01", run.rule_set(), run.describe())

    def test_an_unclosed_code_fence_swallows_the_rest_without_crashing(self) -> None:
        """Una valla sin cerrar deja el resto en código: se dice, no se revienta."""
        text = charter().replace("## Capabilities", "```\n## Capabilities", 1)
        self.write(text)
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.returncode, 1, run.describe())

    def test_a_binary_charter_reports_that_it_cannot_be_read(self) -> None:
        """Un fichero con bytes nulos no es un acta sin secciones: es un acta ilegible."""
        self.project.path(CHARTER_RELPATH).parent.mkdir(parents=True, exist_ok=True)
        self.project.path(CHARTER_RELPATH).write_bytes(b"# Acta\x00\x01\x02 binaria")
        run = self.lint_json()
        self.assert_no_traceback(run)
        self.assertEqual(run.rule_set(), {"P01"}, run.describe())
        self.assertEqual(run.returncode, 1, run.describe())
        self.assertIn("No se puede leer", run.findings_for("P01")[0]["message"])


# ---------------------------------------------------------------------------
# La línea de comandos
# ---------------------------------------------------------------------------


class TestCommandLine(CharterCase):
    """El CLI: las dos ausencias que no son error, los dos que sí, y las banderas."""

    def test_a_project_without_venoxia_is_not_an_error(self) -> None:
        """Un proyecto que no ha adoptado Venoxia no falla por no haberlo adoptado."""
        project = Project(scaffold=False)
        self.addCleanup(project.cleanup)
        run = project.run(CHARTER_LINT_PY, "--root", str(project.root))
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("todavía no ha adoptado Venoxia", run.stdout)

    def test_a_project_without_a_charter_is_invited_to_write_one(self) -> None:
        """Con `.venoxia/` y sin acta se invita a escribirla, y se sale con cero."""
        run = self.lint()
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIn("/venoxia:charter", run.stdout)
        self.assertIn("el acta no hace falta", run.stdout)

    def test_the_absence_of_a_charter_is_visible_in_the_json(self) -> None:
        """El JSON distingue «no hay acta» de «el acta está impecable»."""
        run = self.lint_json()
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertIsNone(run.json["charter"], run.describe())
        self.assertEqual(run.json["adopted"], True, run.describe())

        project = Project(scaffold=False)
        self.addCleanup(project.cleanup)
        other = project.run(CHARTER_LINT_PY, "--root", str(project.root), "--json")
        self.assertEqual(other.json["adopted"], False, other.describe())
        self.assertIsNone(other.json["charter"], other.describe())

    def test_an_explicit_path_is_judged_wherever_it_lives(self) -> None:
        """Una ruta suelta manda, aunque el acta no esté en su sitio canónico."""
        self.project.write("borradores/acta.md", charter())
        run = self.project.run(
            CHARTER_LINT_PY,
            "--root",
            str(self.project.root),
            "--json",
            "--strict",
            "borradores/acta.md",
        )
        self.assertEqual(run.rules(), [], run.describe())
        self.assertEqual(run.returncode, 0, run.describe())
        self.assertEqual(run.json["charter"]["path"], "borradores/acta.md", run.describe())

    def test_a_missing_explicit_path_is_a_usage_error(self) -> None:
        """Nombrar un acta que no existe es un error de uso, no un acta que incumple."""
        run = self.lint("no-existe.md")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertIn("no existe la ruta", run.stderr)

    def test_a_directory_as_path_is_a_usage_error(self) -> None:
        """Un directorio no es un acta: se dice qué fichero nombrar."""
        run = self.lint(".venoxia")
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertIn("es un directorio", run.stderr)

    def test_a_root_that_is_not_a_directory_is_a_usage_error(self) -> None:
        """Una raíz inexistente no produce veredicto sobre ninguna acta."""
        run = self.project.run(CHARTER_LINT_PY, "--root", str(self.project.root / "nada"))
        self.assertEqual(run.returncode, 2, run.describe())
        self.assertIn("no existe o no es un directorio", run.stderr)

    def test_strict_turns_warnings_into_a_failure(self) -> None:
        """El mismo acta: con avisos sale 0, y con «--strict» sale 1."""
        self.write(charter(bets=""))
        relaxed = self.lint_json()
        self.assertEqual(relaxed.rule_set(), {"C15"}, relaxed.describe())
        self.assertEqual(relaxed.returncode, 0, relaxed.describe())
        strict = self.lint_json("--strict")
        self.assertEqual(strict.returncode, 1, strict.describe())
        self.assertEqual(strict.json["ok"], False, strict.describe())
        self.assertEqual(strict.json["strict"], True, strict.describe())

    def test_the_json_carries_the_stable_schema(self) -> None:
        """El documento es el esquema versión 1, con lo del acta colgando de «charter»."""
        self.write(charter())
        run = self.lint_json()
        payload = run.json
        self.assertEqual(payload["version"], 1, run.describe())
        for key in ("ok", "strict", "root", "counts", "findings", "budget", "adopted", "charter"):
            self.assertIn(key, payload, run.describe())
        self.assertEqual(payload["root"], str(self.project.root), run.describe())

    def test_no_color_leaves_no_ansi_behind(self) -> None:
        """Ni con hallazgos ni sin ellos se cuela una secuencia ANSI en la salida."""
        self.write(charter(out_of_scope=""))
        run = self.lint("--no-color")
        self.assertNotIn("\033[", run.stdout, run.describe())
        self.write(charter())
        clean = self.lint("--no-color")
        self.assertNotIn("\033[", clean.stdout, clean.describe())

    def test_two_runs_over_the_same_charter_produce_the_same_bytes(self) -> None:
        """Determinismo: mismo acta, mismo informe, byte a byte."""
        self.write(charter(capabilities=[Cap(done_when=""), DEFAULT_CAPABILITIES[1]]))
        first = self.lint("--no-color")
        second = self.lint("--no-color")
        self.assertEqual(first.stdout, second.stdout, first.describe())
        self.assertEqual(first.returncode, second.returncode, first.describe())


# ---------------------------------------------------------------------------
# El registro de reglas
# ---------------------------------------------------------------------------


class TestRuleRegistry(unittest.TestCase):
    """`RULES` es el contrato del fichero: dieciséis códigos, en orden y con severidad."""

    #: La severidad que el contrato del acta le asigna a cada regla.
    SEVERITIES = {
        "C01": "error",
        "C02": "error",
        "C03": "error",
        "C04": "error",
        "C05": "error",
        "C06": "error",
        "C07": "error",
        "C08": "error",
        "C09": "error",
        "C10": "error",
        "C11": "error",
        "C12": "error",
        "C13": "error",
        "C14": "warning",
        "C15": "warning",
        "C16": "warning",
    }

    def test_the_sixteen_rules_are_registered_in_order(self) -> None:
        """Los códigos son C01…C16, sin saltos ni repetidos."""
        codes = [rule.code for rule in charter_lint.RULES]
        self.assertEqual(codes, [f"C{number:02d}" for number in range(1, 17)])

    def test_every_rule_declares_its_severity_and_its_function(self) -> None:
        """Cada regla trae la severidad del contrato, un resumen y una función."""
        for rule in charter_lint.RULES:
            with self.subTest(rule=rule.code):
                self.assertEqual(rule.severity, self.SEVERITIES[rule.code])
                self.assertTrue(rule.summary.strip())
                self.assertTrue(callable(rule.check))
                self.assertEqual(rule.check.__name__, f"rule_{rule.code.lower()}")

    def test_a_rule_that_breaks_does_not_take_the_verdict_with_it(self) -> None:
        """Si una regla lanza, el linter la convierte en hallazgo y sigue con las demás."""

        def exploding(_ctx):
            raise RuntimeError("bum")

        ctx = charter_lint.Context(
            root=Path("."),
            path=Path("charter.md"),
            display="charter.md",
            charter=charter_lint.Charter(path="charter.md"),
        )
        # Se sabotea C10 y no C01: así el veredicto conserva los cinco C01 del
        # acta vacía y se puede comprobar que las otras quince reglas se han
        # aplicado igualmente, que es lo que la defensa promete.
        index = next(
            position for position, rule in enumerate(charter_lint.RULES) if rule.code == "C10"
        )
        original = charter_lint.RULES[:]
        try:
            charter_lint.RULES[index] = charter_lint.Rule("C10", "error", "explota", exploding)
            findings = charter_lint.run_rules(ctx)
        finally:
            charter_lint.RULES[:] = original

        broken = [finding for finding in findings if finding.rule == "C10"]
        self.assertEqual(len(broken), 1, findings)
        self.assertIn("no se pudo aplicar", broken[0].message)
        self.assertIn("RuntimeError", broken[0].message)
        self.assertEqual(len([f for f in findings if f.rule == "C01"]), 5, findings)


if __name__ == "__main__":
    unittest.main()
