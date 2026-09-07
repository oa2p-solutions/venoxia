# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-false-positives/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 6
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 6 divergencias blandas sobre los 6 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 6

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Gender variants of the same quantifier

El lector A describe el efecto como «no clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Gender variants of the same quantifier» es la correcta?**
- (A) «no clasifica la diferencia como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A negation deep inside a subordinate clause

El lector A describe el efecto como «no clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negation deep inside a subordinate clause» es la correcta?**
- (A) «no clasifica la diferencia como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A condition dragged into one effect only

El lector A describe el efecto como «no clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A condition dragged into one effect only» es la correcta?**
- (A) «no clasifica la diferencia como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A negation against a different verb

El lector A describe el efecto como «no clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negation against a different verb» es la correcta?**
- (A) «no clasifica la diferencia como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A negated condition against an affirmed one

El lector A describe el efecto como «clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia se marca como dura». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negated condition against an affirmed one» es la correcta?**
- (A) «clasifica la diferencia como divergencia dura»
- (B) «la divergencia se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A plain negation still contradicts

El lector A describe el efecto como «clasifica la diferencia como divergencia dura»; el lector B describe el efecto como «la divergencia se marca como dura». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A plain negation still contradicts» es la correcta?**
- (A) «clasifica la diferencia como divergencia dura»
- (B) «la divergencia se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-011 — La exclusión de «la negación de un predicado que el otro efecto no repite» es puramente léxica: con «oracle.json no se modifica» frente a «oracle.json se reescribe entero», el verbo negado (modifica) no aparece en el otro efecto, así que la contradicción real queda fuera de la señal de polaridad y la divergencia sale blanda; /venoxia:diverge escribe `validated` y el guardián abre la puerta al código sobre dos lecturas que discrepan en si un artefacto se destruye o se conserva.
- **[high]** R-DIV-011 — Los únicos dos escenarios que exigen dureza son negaciones textuales exactas («se crea el presupuesto» / «no se crea el presupuesto» y «está validado» / «no está validado»), así que una implementación que marque dura la polaridad sólo cuando los dos efectos son idénticos salvo por el token «no» cumple los seis escenarios y deja pasar como blanda cualquier contradicción reformulada («se crea el presupuesto» vs «el presupuesto nunca llega a crearse»), vaciando la señal de polaridad justo del «caso flagrante» por el que la nota de confianza dice conservarla.
- **[medium]** R-DIV-011 — La exclusión de «la negación que va dentro de una subordinada cuando sólo uno de los dos efectos trae esa subordinada» borra también el alcance del efecto: «deniega la edición cuando el change no está validado» y «deniega la edición» se tratan como no divergentes, aunque un lector entiende una denegación condicional y el otro una denegación universal que bloquearía toda escritura de código.
