"""Paquete interno de Venoxia: modelo, parser e informe.

No ejecuta lógica ni toca el disco al importarse. Los scripts de entrada lo
usan así, tras añadir `scripts/` al `sys.path`:

    from venoxia import model, parser, report
"""

from __future__ import annotations

__all__ = ["model", "parser", "report"]
