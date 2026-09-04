#!/usr/bin/env python3
"""Modelo de datos de Venoxia.

Aquí sólo viven estructuras: el parser las rellena y el validador las juzga.
Ninguna dataclase de este módulo aplica reglas de negocio, toca el disco ni
imprime nada al importarse.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# La severidad viaja como texto plano para que llegue al JSON del esquema
# estable sin traducción intermedia: «error» o «warning».
Severity = str

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"

# Nombres de bloque que puede declarar un delta.
BLOCK_NAMES = ("ADDED", "MODIFIED", "REMOVED", "RENAMED")

# Valores admitidos en «confidence:», de más a menos certeza.
CONFIDENCE_LEVELS = ("high", "medium", "low")

# Claves reconocidas del bloque de metadatos de un requisito.
META_KEYS = ("verifies", "confidence", "why", "revisit", "from")

# «expires:» era el nombre de «revisit:» cuando la revisión de una apuesta se
# declaraba con una fecha. Se conserva aquí, y sólo aquí, para poder dar un
# aviso que diga cómo se llama ahora: un «clave desconocida» genérico dejaría a
# quien tenga specs escritas adivinando.
RETIRED_META_KEYS = {"expires": "revisit"}

#: Fórmulas que ocupan el «revisit:» sin decir qué lo resuelve. Se comparan
#: contra el valor **entero**, ya normalizado: en cuanto la frase nombra un
#: suceso concreto deja de casar, y ahí está su seguridad.
#:
#: Una fecha ISO suelta entra en la lista a propósito. Es lo que se escribía
#: antes y lo que un modelo escribe por inercia, y no es lo que ahora se pide:
#: un día del calendario no dice qué habrá que mirar cuando llegue, y quien
#: llegue a él no sabrá si la apuesta se puede resolver ya o no.
_FILLER_REVISIT_ALTERNATIVES = (
    r"\d{4}-\d{1,2}-\d{1,2}",
    r"(?:mas\s+adelante|mas\s+tarde|ya\s+veremos|se\s+vera|esta\s+por\s+ver|"
    r"proximamente|en\s+su\s+momento|cuando\s+(?:toque|proceda|sea|haya\s+tiempo)|"
    r"algun\s+dia|en\s+el\s+futuro|a\s+futuro)",
    r"(?:pendiente|por\s+definir|por\s+determinar|por\s+decidir|por\s+ver|"
    r"sin\s+definir|sin\s+determinar|tbd|tba|n\s*/\s*a|na)",
    r"(?:en\s+)?(?:unos?\s+)?(?:\d+\s+)?"
    r"(?:dias|semanas|meses|trimestres|anos|sprints)(?:\s+(?:vista|despues))?",
    r"(?:el\s+)?(?:proximo|siguiente)\s+(?:mes|trimestre|ano|sprint|release|version)",
    r"(?:periodicamente|regularmente|de\s+vez\s+en\s+cuando)",
    r"[-–—?¿.…]+",
)
FILLER_REVISIT_RE = re.compile(
    "^(?:" + "|".join(_FILLER_REVISIT_ALTERNATIVES) + ")$"
)

# Forma canónica del identificador de un requisito: «R-CHK-014».
REQUIREMENT_ID_RE = re.compile(r"^R-[A-Z]{2,4}-\d{3}$")

# Estados del ciclo de vida de un change, en el orden en que se alcanzan:
# draft (specify aún no ha corrido) → specified (specify) → validated
# (diverge, con validador y divergencia en 0) → verified (verify, con el
# oráculo en verde) → archived. Vive aquí, y sólo aquí, para que `validate.py`
# (V17 compara contra «verified») y las skills que escriben cada estado no
# repitan la lista cada una a su manera.
CHANGE_STATES = ("draft", "specified", "validated", "verified", "archived")


@dataclass
class Finding:
    """Un problema detectado en la especificación.

    Es la única moneda de cambio entre el parser, el validador y el informe:
    nada se comunica lanzando excepciones, todo se comunica con hallazgos.

    `message` dice qué está mal; `hint` dice qué hacer para arreglarlo. Los dos
    en español, porque los lee una persona con prisa.
    """

    rule: str
    severity: str
    message: str
    file: str = ""
    line: int | None = None
    requirement_id: str | None = None
    hint: str | None = None

    def to_dict(self) -> dict:
        """Devuelve el hallazgo con las claves exactas del esquema JSON."""
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "requirement_id": self.requirement_id,
            "hint": self.hint,
        }


@dataclass
class Scenario:
    """Un escenario de un requisito: «#### Scenario: …» y sus viñetas.

    Cada viñeta es un par (palabra clave, texto), por ejemplo
    `("WHEN", "hay stock disponible en todas las líneas")`.
    """

    title: str
    line: int
    bullets: list[tuple[str, str]] = field(default_factory=list)

    def keywords(self) -> set[str]:
        """Palabras clave presentes en el escenario, en mayúsculas."""
        return {
            keyword.strip().upper()
            for keyword, _ in self.bullets
            if keyword and keyword.strip()
        }

    def has(self, keyword: str) -> bool:
        """Indica si el escenario declara esa palabra clave (sin distinguir mayúsculas)."""
        if not keyword:
            return False
        return keyword.strip().upper() in self.keywords()


@dataclass
class Requirement:
    """Un requisito: encabezado, narrativa EARS, escenarios y metadatos.

    El parser guarda el `id` tal cual lo encuentra en el encabezado; juzgar si
    está bien formado es cosa de las reglas del validador, no del parser.
    """

    id: str | None
    title: str
    line: int
    narrative: str
    scenarios: list[Scenario] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)
    meta_lines: dict[str, int] = field(default_factory=dict)
    source_file: str = ""
    block: str | None = None
    raw_header: str = ""

    @property
    def label(self) -> str:
        """Etiqueta corta para los mensajes: el ID si lo hay, si no el título."""
        if self.id:
            return self.id
        title = (self.title or "").strip()
        return f"«{title}»" if title else "«requisito sin título»"


@dataclass
class Capability:
    """Una capability viva: el estado actual de un trozo del sistema."""

    name: str
    path: str
    purpose: str = ""
    requirements: list[Requirement] = field(default_factory=list)


@dataclass
class Delta:
    """El cambio propuesto sobre una capability, agrupado por bloques.

    Las claves de `blocks` son los bloques realmente declarados en el fichero
    («ADDED», «MODIFIED», «REMOVED», «RENAMED»), incluso si un bloque queda sin
    requisitos: así V12 distingue «no declara bloques» de «el bloque está vacío».
    """

    capability: str
    path: str
    blocks: dict[str, list[Requirement]] = field(default_factory=dict)

    @property
    def requirements(self) -> list[Requirement]:
        """Todos los requisitos del delta, en orden de aparición en el fichero."""
        collected: list[Requirement] = []
        for block_requirements in self.blocks.values():
            collected.extend(block_requirements)
        # El número de línea reconstruye el orden del documento aunque los
        # bloques se hayan recorrido por separado; `sorted` es estable.
        return sorted(collected, key=lambda requirement: requirement.line or 0)


@dataclass
class ValidationResult:
    """El resultado completo de una validación: qué se leyó y qué falló."""

    findings: list[Finding] = field(default_factory=list)
    capabilities: list[Capability] = field(default_factory=list)
    deltas: list[Delta] = field(default_factory=list)
    strict: bool = False
    root: str = "."

    def add(self, finding: Finding) -> None:
        """Añade un hallazgo al resultado."""
        if finding is not None:
            self.findings.append(finding)

    @property
    def errors(self) -> list[Finding]:
        """Hallazgos con severidad de error."""
        return [finding for finding in self.findings if finding.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[Finding]:
        """Hallazgos con severidad de aviso."""
        return [finding for finding in self.findings if finding.severity == SEVERITY_WARNING]

    @property
    def ok(self) -> bool:
        """La especificación cumple: sin errores y, en modo estricto, sin avisos."""
        if self.errors:
            return False
        if self.strict and self.warnings:
            return False
        return True

    def counts(self) -> dict:
        """Recuento para el resumen y para el JSON del informe."""
        requirements = sum(len(capability.requirements) for capability in self.capabilities)
        requirements += sum(len(delta.requirements) for delta in self.deltas)
        return {
            "error": len(self.errors),
            "warning": len(self.warnings),
            "requirements": requirements,
            "capabilities": len(self.capabilities),
            "deltas": len(self.deltas),
        }
