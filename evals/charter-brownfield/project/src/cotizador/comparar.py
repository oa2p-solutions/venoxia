"""Elige el proveedor más barato por producto."""

from __future__ import annotations

from collections import defaultdict

from .importar import Linea


def comparar(lineas: list[Linea]) -> dict[str, Linea]:
    """Para cada producto, la línea de menor precio. A igual precio gana el primero leído."""
    por_producto: dict[str, list[Linea]] = defaultdict(list)
    for linea in lineas:
        por_producto[linea.producto].append(linea)
    return {producto: min(candidatas, key=lambda l: l.precio) for producto, candidatas in por_producto.items()}
