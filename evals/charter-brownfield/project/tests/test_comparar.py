from cotizador.comparar import comparar
from cotizador.importar import Linea


def test_gana_el_mas_barato_por_producto():
    lineas = [Linea("norte", "tomate", "kg", 1.9), Linea("sur", "tomate", "kg", 1.7)]
    assert comparar(lineas)["tomate"].proveedor == "sur"


def test_a_igual_precio_gana_el_primero():
    lineas = [Linea("norte", "aceite", "l", 4.0), Linea("sur", "aceite", "l", 4.0)]
    assert comparar(lineas)["aceite"].proveedor == "norte"
