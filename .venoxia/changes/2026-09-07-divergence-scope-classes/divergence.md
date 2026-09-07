# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-scope-classes/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 3
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas convergen.** No hay desacuerdo en los 3 escenarios entre los 2 lectores. Esta ejecución sale con código 0.

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-012 — El texto clasifica por presencia de marca, no por polaridad: «crea sólo oracle.json» y «no crea sólo oracle.json» (o «reserva todo el pedido» vs «no reserva todo el pedido») llevan marcas de la misma clase, así que la implementación literal está obligada a NO contar contradicción. Dos lectores que se contradicen frontalmente producen divergencia blanda, /venoxia:diverge escribe `validated` y se escribe código sobre una lectura equivocada del delta.
- **[medium]** R-DIV-012 — Las tres clases son listas cerradas de diez palabras, y el requisito ordena no contar contradicción «cuando sólo uno de los dos lleva marca»: «crea exclusivamente oracle.json» (sin marca reconocida) frente a «crea todos los ficheros del change» (clase completo) queda como divergencia blanda pese a ser el par opuesto exacto; basta que un lector use un sinónimo fuera de la lista para desactivar el chequeo.
- **[medium]** R-DIV-012 — Nada define «el mismo sujeto», así que una implementación que lo calcule como los dos primeros tokens del efecto pasa los tres escenarios (todos comparten prefijo literal) y no detecta nada en cuanto los lectores parafrasean: «se crea la reserva para el pedido completo» vs «reserva creada sólo para lo disponible» no comparten sujeto y la contradicción de alcance nunca se cuenta, dejando la regla inerte en el caso normal de dos lectores independientes.

## Escenarios que convergen · 3

- Two synonyms of the same class
- A mark against no mark
- Two marks of different classes
