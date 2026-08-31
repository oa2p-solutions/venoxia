#!/usr/bin/env python3
"""Informe de Venoxia: del resultado de la validación al texto y al JSON.

Este módulo no juzga nada. Recibe un `ValidationResult` ya cerrado y lo cuenta
de dos maneras:

* `render_text` para la persona que tiene el terminal delante: los hallazgos
  agrupados por severidad y el remedio pegado justo debajo del problema.
* `render_json` y `build_payload` para el resto del sistema —la skill, el
  guardián y el futuro panel de salud— con el esquema estable versión 1.

Dos ejecuciones sobre el mismo árbol producen el mismo texto y el mismo JSON,
byte a byte: los hallazgos se ordenan siempre por fichero, línea y código de
regla, y el color sólo aparece cuando la salida es de verdad un terminal.
"""

from __future__ import annotations

import json
import sys

from .model import (
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    Finding,
    Requirement,
    ValidationResult,
)

# Versión del esquema JSON. Sube sólo si cambia la forma del documento, nunca
# por añadir un valor: hay consumidores que dependen de estas claves.
SCHEMA_VERSION = 1

# Presupuesto de incertidumbre: como mucho el 30 % de los requisitos del ámbito
# puede declarar «confidence: low». El límite se guarda también como fracción
# entera para decidir el borde con aritmética exacta —0.30 pasa, 0.31 falla—,
# sin depender de cómo redondee el punto flotante.
UNCERTAINTY_LIMIT = 0.30
_LIMIT_NUMERATOR = 3
_LIMIT_DENOMINATOR = 10

ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"

MARK_ERROR = "✗"
MARK_WARNING = "⚠"
MARK_OK = "✓"

# Sangría del mensaje y del remedio bajo la línea de cabecera del hallazgo.
INDENT = "      "

# Ubicación de los hallazgos que no pertenecen a un fichero concreto, como el
# presupuesto de incertidumbre, que se mide sobre el ámbito entero.
SCOPE_LOCATION = "(ámbito validado)"


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------


def color_enabled(no_color: bool = False) -> bool:
    """Decide si se puede pintar en color.

    Sólo si nadie ha pedido lo contrario **y** la salida estándar es un
    terminal: en CI, en un fichero o en una tubería la respuesta es que no.
    """
    if no_color:
        return False
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        # Un stdout sustituido que no sabe responder no es un terminal.
        return False


def paint(text: str, color: str, enabled: bool) -> str:
    """Envuelve el texto en color ANSI si está habilitado."""
    return f"{color}{text}{ANSI_RESET}" if enabled else text


# ---------------------------------------------------------------------------
# Orden y recuentos
# ---------------------------------------------------------------------------


def _sort_key(finding: Finding) -> tuple[str, int, str]:
    """Clave de orden de un hallazgo: fichero, línea y código de regla."""
    line = finding.line if isinstance(finding.line, int) and finding.line > 0 else 0
    return (finding.file or "", line, finding.rule or "")


def sort_findings(findings: list[Finding]) -> list[Finding]:
    """Ordena los hallazgos de forma determinista y estable."""
    return sorted(findings, key=_sort_key)


def requirements_of(result: ValidationResult) -> list[Requirement]:
    """Todos los requisitos del ámbito: primero las capabilities, luego los deltas."""
    collected: list[Requirement] = []
    for capability in result.capabilities:
        collected.extend(capability.requirements)
    for delta in result.deltas:
        collected.extend(delta.requirements)
    return collected


def uncertainty_budget(requirements: list[Requirement]) -> dict:
    """Mide el presupuesto de incertidumbre de un conjunto de requisitos.

    Devuelve cuántos declaran «confidence: low», sobre cuántos, la proporción
    redondeada a tres decimales, el límite y si se respeta. Con cero requisitos
    el presupuesto se cumple: no hay apuesta que medir.

    **Ésta es la única cuenta del presupuesto que hay en el sistema.** De ella
    salen el campo `budget` del JSON, la línea de cierre del informe de texto y
    el veredicto de la regla `V11`, que llama aquí en vez de contar por su
    cuenta. Cuando había dos cuentas, el informe podía decir «presupuesto
    excedido» sin ningún `V11` que lo respaldase.

    El nivel se compara **tal cual**, sin bajar la caja: una apuesta sólo está
    declarada si pone exactamente «low», que es el mismo literal que exige `V09`
    y el único que hace a `V10` reclamar la fecha de revisión. Un «LOW» no es un
    nivel válido —lo denuncia `V09`— y contarlo además contra el presupuesto
    sería cobrar dos veces el mismo error, con la regla que no toca.
    """
    total = len(requirements)
    low = sum(
        1
        for requirement in requirements
        if (requirement.meta.get("confidence") or "").strip() == "low"
    )
    ratio = round(low / total, 3) if total else 0.0
    # Comparación exacta con enteros: low/total <= 3/10.
    within = low * _LIMIT_DENOMINATOR <= total * _LIMIT_NUMERATOR
    return {
        "low": low,
        "total": total,
        "ratio": ratio,
        "limit": UNCERTAINTY_LIMIT,
        "ok": within,
    }


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


def build_payload(result: ValidationResult, extra: dict | None = None) -> dict:
    """Construye el documento del esquema estable versión 1.

    `extra` añade claves al primer nivel para quien necesite llevar contexto
    propio; las claves del esquema se calculan siempre desde el resultado.
    """
    payload = {
        "version": SCHEMA_VERSION,
        "ok": bool(result.ok),
        "strict": bool(result.strict),
        "root": result.root,
        "counts": result.counts(),
        "findings": [finding.to_dict() for finding in sort_findings(result.findings)],
        "budget": uncertainty_budget(requirements_of(result)),
    }
    if extra:
        payload.update(extra)
    return payload


def render_json(result: ValidationResult, extra: dict | None = None) -> str:
    """Serializa el resultado con el esquema estable, en UTF-8 legible."""
    return json.dumps(
        build_payload(result, extra), ensure_ascii=False, indent=2, sort_keys=False
    )


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------


def location_of(finding: Finding) -> str:
    """Ubicación legible de un hallazgo: «fichero:línea», «fichero» o el ámbito."""
    if not finding.file:
        return SCOPE_LOCATION
    if isinstance(finding.line, int) and finding.line > 0:
        return f"{finding.file}:{finding.line}"
    return finding.file


def render_finding_lines(
    finding: Finding, mark: str, color: str, enabled: bool
) -> list[str]:
    """Un hallazgo en tres líneas: dónde, qué pasa y qué hacer."""
    header = f"{mark} {finding.rule}  {location_of(finding)}"
    if finding.requirement_id:
        header = f"{header}  {finding.requirement_id}"
    lines = [paint(header, color, enabled), f"{INDENT}{finding.message}"]
    if finding.hint:
        lines.append(f"{INDENT}→ {finding.hint}")
    return lines


def _plural(count: int, singular: str, plural: str) -> str:
    """«1 error» o «3 errores», con la palabra que toque."""
    return f"{count} {singular if count == 1 else plural}"


def _scope_sentence(counts: dict) -> str:
    """«12 requisitos en 2 capabilities, 1 delta», con lo que de verdad hay."""
    pieces: list[str] = []
    if counts["capabilities"]:
        pieces.append(_plural(counts["capabilities"], "capability", "capabilities"))
    if counts["deltas"]:
        pieces.append(_plural(counts["deltas"], "delta", "deltas"))
    requirements = _plural(counts["requirements"], "requisito", "requisitos")
    if not pieces:
        return f"{requirements} · sin ficheros de especificación"
    return f"{requirements} en {', '.join(pieces)}"


def summary_lines(result: ValidationResult, enabled: bool) -> list[str]:
    """Las líneas de cierre: presupuesto, recuento y veredicto."""
    counts = result.counts()
    lines: list[str] = []

    budget = uncertainty_budget(requirements_of(result))
    if budget["total"]:
        percent = f"{budget['ratio'] * 100:.1f}".replace(".", ",")
        limit = f"{UNCERTAINTY_LIMIT * 100:.0f}"
        verdict = "dentro" if budget["ok"] else "excedido"
        # «1 de 1 requisito», no «1 de 1 requisitos»: la línea de al lado ya
        # concuerda el singular y dos líneas seguidas no pueden decir cada una
        # una cosa sobre el mismo número.
        counted_requirements = _plural(budget["total"], "requisito", "requisitos")
        lines.append(
            f"Presupuesto de incertidumbre: {budget['low']} de "
            f"{counted_requirements} en «low» ({percent} % · límite {limit} %) "
            f"— {verdict}"
        )

    counted = (
        f"{_plural(counts['error'], 'error', 'errores')}, "
        f"{_plural(counts['warning'], 'aviso', 'avisos')} · {_scope_sentence(counts)}"
    )
    if result.strict:
        counted = f"{counted} · modo estricto: los avisos cuentan"
    lines.append(counted)

    if result.ok:
        lines.append(paint(f"{MARK_OK} La especificación cumple el contrato.", ANSI_GREEN, enabled))
    else:
        lines.append(
            paint(
                f"{MARK_ERROR} La especificación incumple el contrato: "
                "corrige lo de arriba y vuelve a validar.",
                ANSI_RED,
                enabled,
            )
        )
    return lines


def render_summary(result: ValidationResult, no_color: bool = False) -> str:
    """Sólo el cierre: presupuesto, recuento y veredicto. Es lo que imprime «-q»."""
    return "\n".join(summary_lines(result, color_enabled(no_color)))


def render_text(result: ValidationResult, no_color: bool = False) -> str:
    """Informe completo para una persona, en español y con el remedio a la vista."""
    enabled = color_enabled(no_color)
    findings = sort_findings(result.findings)
    lines: list[str] = []

    groups = (
        ("Errores", SEVERITY_ERROR, MARK_ERROR, ANSI_RED),
        ("Avisos", SEVERITY_WARNING, MARK_WARNING, ANSI_YELLOW),
    )
    for title, severity, mark, color in groups:
        group = [finding for finding in findings if finding.severity == severity]
        if not group:
            continue
        lines.append(paint(f"{title} ({len(group)})", color, enabled))
        lines.append("")
        for finding in group:
            lines.extend(render_finding_lines(finding, mark, color, enabled))
            lines.append("")

    # Defensa: una severidad inesperada no puede desaparecer del informe.
    others = [
        finding
        for finding in findings
        if finding.severity not in (SEVERITY_ERROR, SEVERITY_WARNING)
    ]
    if others:
        lines.append(paint(f"Otros hallazgos ({len(others)})", ANSI_YELLOW, enabled))
        lines.append("")
        for finding in others:
            lines.extend(render_finding_lines(finding, MARK_WARNING, ANSI_YELLOW, enabled))
            lines.append("")

    lines.extend(summary_lines(result, enabled))
    return "\n".join(lines)
