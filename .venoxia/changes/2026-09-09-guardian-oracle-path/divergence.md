# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-guardian-oracle-path/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 5
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas convergen.** No hay desacuerdo en los 5 escenarios entre los 2 lectores. Esta ejecución sale con código 0.

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-GRD-006 — El requisito abre la puerta por «la ruta que algún `verifies:` nombra» y su propio `why:` descarta mirar la forma de la ruta; una implementación literal permite, con el change sólo en `specified`, escribir cualquier fichero que el delta haya declarado en un `verifies:` —`scripts/guardian.py`, `src/pagos.py`, `.venoxia/venoxia.json`—, de modo que basta una línea en un delta que nadie ha validado ni sometido a divergencia para saltarse por completo la puerta de `validated` y editar código de producción o el propio guardián.
- **[medium]** R-GRD-006 — «Denegarla en cualquier otro caso» no exceptúa que otro change acreditado esté abierto: en un proyecto con un change en `validated` y otro recién puesto en `specified`, una implementación que resuelve «el cambio activo» al segundo deniega todas las escrituras de código que el primero sí acredita, y el usuario queda bloqueado para implementar un change ya validado hasta que archive o retroceda el otro.
- **[medium]** R-GRD-006 — «Denegarla en cualquier otro caso» incluye el caso de no poder leer `delta/` por un fallo de E/S: la implementación literal responde `deny` ante un error de lectura propio, invirtiendo la garantía fail-open del guardián, y el mensaje que R-GRD-007 impone («ejecuta /venoxia:validate y /venoxia:diverge») no resuelve nada, dejando al usuario sin salida por un fallo que no es suyo.
- **[medium]** R-GRD-006 — Nada fija cómo se compara la ruta editada (absoluta, del payload del hook) con el valor relativo del `verifies:`; comparar por sufijo o por nombre de fichero cumple «esa ruta es una de las que algún verifies: nombra» y permite escribir `/cualquier/sitio/fuera/del/proyecto/tests/test_x.py`, es decir, autorizar escrituras fuera de la raíz inspeccionada con la sola excusa de coincidir de nombre.

## Escenarios que convergen · 5

- The path the delta declares as its oracle
- A test-shaped path that nobody declared
- Production code with that same change
- The deny names the declared oracle
- Nothing declared, the generic remedy stands
