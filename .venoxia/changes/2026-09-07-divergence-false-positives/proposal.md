# 2026-09-07-divergence-false-positives Proposal

## Why

El cuaderno de construcción dejó escrito el criterio: la señal de polaridad de
`diff_readings.py` había dado dos falsos positivos sobre prosa real, los dos
corregidos con test de regresión, y «si un tercer delta trae un tercero, la
pregunta deja de ser cómo refinar la gramática y pasa a ser si la señal
compensa». El tercero llegó el 2026-09-07, y trajo dos más: sobre los deltas
de `2026-09-07-oracle-hardening` y `2026-09-07-divergence-interview` el motor
declaró incompatibles «stderr nombra ambas flags» y «stderr nombra ambos
flags» (dos géneros de la misma palabra, contados como marcas de alcance
distintas), «mensaje en stderr indicando que no se grabó el run» y «stderr
avisa de que el run no se ha grabado» (la negación va dentro de la subordinada
en las dos, pero en la segunda no está pegada al «que»), y «el informe nombra
ambos números» frente a «el informe nombra los dos números (15 y 30)».

La cuenta a día de hoy, sobre las diez lecturas reales que conserva el repo y
las tres rondas de hoy: la señal de polaridad no ha cazado ningún desacuerdo
real y ha producido cinco falsos positivos. Lo que sí caza es el caso
flagrante —«se crea el presupuesto» contra «no se crea el presupuesto»—, que
sin ella `coverage` daba por convergencia, y ése es el motivo de no retirarla.

## What Changes

- «ambos» y «ambas» dejan de ser marcas de alcance: son cuantificadores de
  estilo, como «cada» o «cualquier», que ya estaban fuera por la misma razón.
- Una negación que aparece **después** de una palabra que abre subordinada
  —«que», «si», «cuando», «porque»…— no cuenta como polaridad del efecto,
  esté o no pegada a ella. Antes sólo se ignoraba la inmediatamente posterior.
- Una negación sólo contradice al efecto que niega **el mismo predicado**:
  «oracle.json no se modifica» frente a «oracle.json conserva su contenido»
  comparten el sujeto y difieren en el verbo, y eso es la frontera de
  antónimos que `R-DIV-005` ya dejó del lado blando; emparejarlos por el nombre
  del fichero y contarlos como contradicción era el sexto falso positivo.
- El caso flagrante sigue siendo duro: una negación sin subordinada delante
  niega el efecto, y las dos frases dicen lo mismo salvo por ella.

## Capabilities

### Modified Capabilities

- `divergence`: un requisito nuevo, `R-DIV-011`. `R-DIV-005` no cambia de
  redacción: sigue diciendo que un colateral huérfano es duro sólo si
  contradice; lo que se afina es qué cuenta como contradicción.

## Impact

- El fixture `ambiguous-partial-effect` de los evals sigue dando su dura
  («completo» contra «sólo» no tocan ni «ambos» ni la subordinada).
- Una negación de la cláusula principal que vaya detrás de una subordinada
  —«cuando falta stock no se crea la reserva»— pasa al lado blando. Se declara
  como coste: se sigue presentando con su pregunta, y `--strict` la devuelve a
  hacer fallar la ejecución.
- La medición que decide si la señal compensa se hace con la clave `signal`
  que introduce `2026-09-07-divergence-interview`.

## Pendiente

Tres rondas de divergencia, la última con seis blandas y ninguna dura. Ataques
del abogado que quedan como coste declarado, no como cambio:

- Una negación frente a un antónimo verbal («no se modifica» frente a «se
  reescribe entero») cae del lado blando: es la frontera de `R-DIV-005`, se
  sigue presentando con su pregunta y `--strict` la devuelve a hacer fallar.
- Una condición negada que sólo un lector se trae al efecto («cuando el
  change no está validado» frente a nada) no cuenta como contradicción; el
  desacuerdo sobre si la denegación es condicional o universal se presenta
  como blanda por la cobertura, no como dura.
- La negación exige el mismo predicado, así que «se crea el presupuesto»
  frente a «el presupuesto nunca llega a crearse» es blanda. Es el precio de
  no volver a llamar contradicción a lo que sólo comparte el nombre de un
  fichero; la cuenta con `signal` dirá si compensa.

## Confidence

- **Conservar la señal de polaridad en vez de retirarla** · `medium` · cinco
  falsos positivos y cero aciertos sobre prosa real pesan en contra; el caso
  flagrante pesa a favor; se revisa cuando la clave `signal` acumule veinte
  duras de polaridad sobre deltas reales y se pueda contar cuántas fueron
  desacuerdos de verdad.
- **Ignorar toda negación posterior a una palabra subordinante** · `medium` ·
  es más gramática de la que el motor quería tener, pero la alternativa
  (mirar sólo la palabra anterior) acaba de fallar sobre prosa real; se revisa
  con la misma cuenta de arriba.
- **El resto de la propuesta** · `high` · determinista, sin modelo, y con los
  dos casos reales como tests de regresión.
