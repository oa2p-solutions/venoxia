# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-verify-confirm-green/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 22
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 7 blandas y 3 lagunas declaradas sobre los 22 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: The confirmation lands in the recorded run

El lector B registra «oracle.json gana un run con confirmed_green: ["R-ORC-901"]» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice por la cifra (901 frente a ninguna cifra).

**¿Qué efectos observables debe producir «The confirmation lands in the recorded run»?**
- (A) «oracle.json gana un run con confirmed_green: ["R-ORC-901"]»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 7

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The confirmation lands in the recorded run

El lector A describe el efecto como «el último run añade confirmed_green con ese ID»; el lector B describe el efecto como «el run grabado incluye confirmed_green con R-ORC-901». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The confirmation lands in the recorded run» es la correcta?**
- (A) «el último run añade confirmed_green con ese ID»
- (B) «el run grabado incluye confirmed_green con R-ORC-901»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Several IDs separated by commas

El lector A describe el efecto como «el último run trae los dos IDs en confirmed_green»; el lector B describe el efecto como «el run grabado incluye ambos IDs en confirmed_green». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Several IDs separated by commas» es la correcta?**
- (A) «el último run trae los dos IDs en confirmed_green»
- (B) «el run grabado incluye ambos IDs en confirmed_green»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An ID that is not green in this run is a usage error

El lector A describe el efecto como «el proceso termina por error de uso»; el lector B describe el efecto como «el proceso termina con error de uso y no graba el run». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An ID that is not green in this run is a usage error» es la correcta?**
- (A) «el proceso termina por error de uso»
- (B) «el proceso termina con error de uso y no graba el run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A green run backed by a documented red run

El lector A describe el efecto como «change.json pasa a state verified»; el lector B describe el efecto como «el change pasa al estado verified». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A green run backed by a documented red run» es la correcta?**
- (A) «change.json pasa a state verified»
- (B) «el change pasa al estado verified»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The user confirms and the confirmation is recorded

El lector B registra «oracle.json gana un run con --record --confirm-green nombrando ese requisito» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The user confirms and the confirmation is recorded»?**
- (A) «oracle.json gana un run con --record --confirm-green nombrando ese requisito»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The recorded confirmation unlocks verified

El lector A describe el efecto como «change.json pasa a state verified»; el lector B describe el efecto como «el change pasa al estado verified». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The recorded confirmation unlocks verified» es la correcta?**
- (A) «change.json pasa a state verified»
- (B) «el change pasa al estado verified»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A confirmation already in the history is enough

El lector A describe el efecto como «change.json pasa a verified sin volver a preguntar»; el lector B describe el efecto como «el change pasa a verified sin preguntar de nuevo». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A confirmation already in the history is enough» es la correcta?**
- (A) «change.json pasa a verified sin volver a preguntar»
- (B) «el change pasa a verified sin preguntar de nuevo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Lagunas declaradas · 3

3 lagunas declaradas sobre 3 escenarios. Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala
un hueco del delta, no un fallo del lector.

### Escenario: The output keeps its eight top-level keys

El lector B declara que el texto no lo resuelve: «el texto remite a las ocho claves de R-ORC-008 sin listarlas aquí; el suite necesitaría ese requisito para comparar, y este delta no lo incluye.».

**¿Qué debe ocurrir en «The output keeps its eight top-level keys»?**
- (A) «el JSON de salida conserva las ocho claves de primer nivel» (lectura de A)
- (B) «el JSON de salida trae exactamente ocho claves de primer nivel» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: An ID outside the change records nothing

El lector B declara que el texto no lo resuelve: «no se dice el código de salida de este escenario en concreto, aunque es plausible que sea el mismo 2 del escenario anterior; el texto no lo repite aquí.».

**¿Qué debe ocurrir en «An ID outside the change records nothing»?**
- (A) «el directorio del change no gana ningún fichero» (lectura de A)
- (B) «el directorio del change no gana ningún fichero nuevo» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: Every run has always been green

El lector B declara que el texto no lo resuelve: «no se repite la severidad aquí; asumir que es warning como el escenario anterior requeriría inferencia no confirmada en este texto.».

**¿Qué debe ocurrir en «Every run has always been green»?**
- (A) «V18 se dispara para ese requisito» (lectura de A y B)
- (B) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

## Escenarios que convergen · 12

- A run without the flag carries no confirmation
- An ID outside the change is a usage error
- Confirming without recording is a usage error
- A green run with no red run in the history
- The user does not confirm
- A red run never writes verified
- Red preceded the green
- The only run is already green
- One warning per requirement, never one per change
- A confirmed green is silent
- A confirmation covers only the IDs it names
- The confirmation may live in an earlier run
