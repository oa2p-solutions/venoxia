# 2026-09-07-divergence-scope-classes Proposal

## Why

El mismo día en que `2026-09-07-divergence-false-positives` cerró tres falsos
positivos de la señal de polaridad, la ronda 5 del panel de
`2026-09-07-oracle-hardening` trajo el siguiente, esta vez de la señal de
alcance: «crea oracle.json como único fichero nuevo» frente a «crea sólo
oracle.json» salieron como contradicción porque `diff_readings.py` compara las
marcas de alcance como conjunto de **palabras**, y «único» y «sólo» son
palabras distintas. Dicen lo mismo: las dos acotan al eje «únicamente esto».
Lo que el motor quería distinguir era «el pedido completo» de «sólo las
unidades con stock» —parcial contra total—, y eso no depende de qué sinónimo
elija cada lector.

## What Changes

- Las marcas de alcance se comparan por **clase**, no por palabra: «sólo»,
  «solamente», «únicamente», «único» y «única» son una clase; «parcial» y sus
  formas, otra; «completo», «total», «todo» y sus formas, la tercera.
- Dos efectos con marcas de la misma clase no se contradicen por el alcance;
  dos con marcas de clases distintas, sí, como hasta ahora.
- Una marca frente a ninguna tampoco contradice: «crea sólo oracle.json» es
  una precisión de «crea oracle.json», no lo niega. La ronda 6 del panel de
  `oracle-hardening` lo dio como dura y era el mismo hecho dicho dos veces.
- El informe sigue nombrando las palabras literales de cada lector cuando la
  señal de alcance dispara.

## Capabilities

### Modified Capabilities

- `divergence`: un requisito nuevo, `R-DIV-012`. `R-DIV-005` y `R-DIV-011` no
  cambian de redacción.

## Impact

- El fixture `ambiguous-partial-effect` de los evals sigue dando su dura:
  «completo» y «sólo» son clases distintas.
- El esquema JSON no cambia.

## Pendiente

Ataques del abogado que se resuelven en la implementación, sin cambiar el
contrato:

- Un efecto con varias marcas se compara por el **conjunto** de sus clases, no
  por la primera: «sólo actualiza parcialmente» y «sólo actualiza completo»
  difieren en una clase y siguen siendo contradicción.
- «Todo el stock disponible» y «el stock completo del pedido» comparten clase
  y no se contradicen por el alcance; si difieren, es por el resto de sus
  palabras, y eso lo mide la cobertura, no esta señal.

- Una negación delante de la misma marca («crea sólo X» frente a «no crea sólo
  X») la caza la señal de polaridad, no la de alcance: las dos señales se
  evalúan por separado y basta una.
- Un sinónimo fuera de la lista («exclusivamente») no se reconoce: la lista es
  cerrada por diseño (`R-DIV-005`) y ampliarla es una decisión aparte.
- «El mismo sujeto» es lo que ya mide `same_subject`: los tokens de contenido
  sin marcas ni cifras, con el umbral general.

## Confidence

- **Tres clases y ninguna más** · `high` · son los tres puntos del eje
  parcial/total que la lista cerrada de marcas ya cubría; agrupar por clase no
  añade palabras, sólo deja de castigar el sinónimo.
- **El resto de la propuesta** · `high` · determinista y con el caso real como
  test de regresión.
