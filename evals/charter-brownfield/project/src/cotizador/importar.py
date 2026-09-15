"""Lee los presupuestos en Excel y los normaliza a una lista de líneas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Linea:
    proveedor: str
    producto: str
    unidad: str
    precio: float


def importar(rutas: list[Path]) -> list[Linea]:
    """Una línea por producto y proveedor. El nombre del proveedor sale del fichero."""
    lineas: list[Linea] = []
    for ruta in rutas:
        proveedor = ruta.stem.split("-")[0]
        for producto, unidad, precio in _leer_filas(ruta):
            lineas.append(Linea(proveedor, producto.strip().lower(), unidad, float(precio)))
    return lineas


def _leer_filas(ruta: Path):
    import openpyxl

    libro = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    hoja = libro.active
    for fila in hoja.iter_rows(min_row=2, values_only=True):
        if fila and fila[0]:
            yield fila[0], fila[1] or "ud", fila[2] or 0
