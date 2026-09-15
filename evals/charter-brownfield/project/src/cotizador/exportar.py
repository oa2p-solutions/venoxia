"""Escribe el pedido ganador como CSV, un bloque por proveedor."""

from __future__ import annotations

import csv
from pathlib import Path

from .importar import Linea


def exportar(ganadoras: dict[str, Linea], destino: Path) -> None:
    with destino.open("w", newline="", encoding="utf-8") as fh:
        escritor = csv.writer(fh)
        escritor.writerow(["proveedor", "producto", "unidad", "precio"])
        for linea in sorted(ganadoras.values(), key=lambda l: (l.proveedor, l.producto)):
            escritor.writerow([linea.proveedor, linea.producto, linea.unidad, f"{linea.precio:.2f}"])
