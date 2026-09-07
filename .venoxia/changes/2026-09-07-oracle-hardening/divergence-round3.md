# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 10
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 2 divergencias duras, 6 blandas y 0 lagunas declaradas sobre los 10 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 2

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: The usage error names both flags

El lector A registra «mensaje en stderr nombrando ambas flags» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice.

**¿Qué efectos observables debe producir «The usage error names both flags»?**
- (A) «mensaje en stderr nombrando ambas flags»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A failed copy is reported as a run that was not recorded

El lector A registra «mensaje en stderr indicando que no se grabó el run» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice.

**¿Qué efectos observables debe producir «A failed copy is reported as a run that was not recorded»?**
- (A) «mensaje en stderr indicando que no se grabó el run»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 6

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Both flags in one invocation

El lector A describe el efecto como «el proceso termina en error de uso sin ejecutar el runner»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Both flags in one invocation» es la correcta?**
- (A) «el proceso termina en error de uso sin ejecutar el runner»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is written under both flags

El lector A describe el efecto como «el proceso termina en error y no crea ficheros»; el lector B describe el efecto como «termina con código 2 y no crea ningún fichero». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Nothing is written under both flags» es la correcta?**
- (A) «el proceso termina en error y no crea ficheros»
- (B) «termina con código 2 y no crea ningún fichero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names both flags

El lector A describe el efecto como «stderr muestra un aviso citando --dry-run y --record»; el lector B describe el efecto como «termina con código 2, stderr nombra ambos flags». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The usage error names both flags» es la correcta?**
- (A) «stderr muestra un aviso citando --dry-run y --record»
- (B) «termina con código 2, stderr nombra ambos flags»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An existing history is left intact

El lector A describe el efecto como «oracle.json permanece exactamente igual»; el lector B describe el efecto como «termina con código 2, oracle.json queda intacto». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «An existing history is left intact» es la correcta?**
- (A) «oracle.json permanece exactamente igual»
- (B) «termina con código 2, oracle.json queda intacto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The original bytes survive in the copy

El lector A describe el efecto como «se crea una copia con los bytes originales intactos»; el lector B describe el efecto como «se crea copia con el contenido original íntegro». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The original bytes survive in the copy» es la correcta?**
- (A) «se crea una copia con los bytes originales intactos»
- (B) «se crea copia con el contenido original íntegro»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A second corruption never overwrites the first copy

El lector A registra «crea segunda copia oracle.json.corrupt-<marca>-<n> sin tocar la primera» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A second corruption never overwrites the first copy»?**
- (A) «crea segunda copia oracle.json.corrupt-<marca>-<n> sin tocar la primera»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-012 — El requisito fija, para la copia fallida, sólo dos efectos observables (no sustituir el historial y avisar por stderr) pero no el código de salida ni el resto de la salida: una implementación que avisa por stderr y aun así termina con código 0 emitiendo el veredicto normal por stdout cumple ambos escenarios literalmente, mientras `/venoxia:verify` y `gate.py` —que deciden por código de salida— dan por bueno un run que no está en disco y hay que volver a ejecutar la suite entera para recuperarlo.
- **[medium]** R-ORC-012 — «No se puede interpretar como historial» lo decide la implementación y los escenarios sólo prueban el caso «no es JSON»: una implementación que declare no interpretable todo `oracle.json` que no coincida exactamente con su esquema (un historial válido de una versión anterior, o con una clave extra) aparta un historial correcto a un fichero `.corrupt-<marca>` que ninguna herramienta lee y arranca el historial vivo desde cero, destruyendo la evidencia del rojo previo que V17 exige para acreditar `verified`.

## Escenarios que convergen · 3

- The warning names the copy
- No history, no copy
- A copy that cannot be written keeps the original in place
