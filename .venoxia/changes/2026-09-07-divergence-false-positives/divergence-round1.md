# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-false-positives/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 3
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas convergen.** No hay desacuerdo en los 3 escenarios entre los 2 lectores. Esta ejecución sale con código 0.

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-011 — El escenario 2 obliga a clasificar como blanda una pareja cuyos textos difieren en mucho más que la negación («mensaje en stderr indicando que no se grabó el run» vs «stderr avisa de que el run no se ha grabado»), así que la única implementación que lo pasa es la laxa: «hay una negación después de que/cuando/porque/si → blanda». Con esa regla, «el guardián deniega cuando el change está validado» frente a «el guardián deniega cuando el change no está validado» sale blanda, diff_readings.py cierra con 0, /venoxia:diverge escribe state: validated y se abre el guardián al código sobre una contradicción de polaridad sin resolver.
- **[medium]** R-DIV-011 — El requisito manda clasificar «la divergencia» como blanda, no la señal de polaridad, y no acota el efecto a la señal que la disparó: una implementación literal marca blanda toda la divergencia del escenario en cuanto detecta la variante ambos/ambas o la negación subordinada, silenciando de paso las señales duras que ese mismo escenario tuviera por otros motivos (efecto ausente en un lector, verbos opuestos como «se borra» vs «se conserva»), que quedan sin bloquear y sin arreglo salvo revisión manual.

## Escenarios que convergen · 3

- Gender variants of the same quantifier
- A negation deep inside a subordinate clause
- A plain negation still contradicts
