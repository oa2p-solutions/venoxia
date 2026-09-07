# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 12
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 14 blandas y 2 lagunas declaradas sobre los 12 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: No history, no copy

El lector A registra «crea oracle.json como único fichero nuevo» y ningún otro lector lo recoge; el lector B registra «crea oracle.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice por su alcance («unico» frente a «solo») y su alcance (ninguna marca frente a «unico»).

**¿Qué efectos observables debe producir «No history, no copy»?**
- (A) «crea oracle.json como único fichero nuevo»
- (B) «crea oracle.json»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 14

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Both flags in one invocation

El lector A describe el efecto como «rechaza la ejecución por flags incompatibles»; el lector B describe el efecto como «el proceso termina sin ejecutar nada». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Both flags in one invocation» es la correcta?**
- (A) «rechaza la ejecución por flags incompatibles»
- (B) «el proceso termina sin ejecutar nada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is written under both flags

El lector A describe el efecto como «termina en error sin crear ningún fichero»; el lector B describe el efecto como «el proceso termina y no crea ningún fichero». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Nothing is written under both flags» es la correcta?**
- (A) «termina en error sin crear ningún fichero»
- (B) «el proceso termina y no crea ningún fichero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names both flags

El lector A registra «escribe en stderr un aviso que nombra --dry-run y --record» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The usage error names both flags»?**
- (A) «escribe en stderr un aviso que nombra --dry-run y --record»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An existing history is left intact

El lector A registra «oracle.json conserva su contenido byte a byte» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An existing history is left intact»?**
- (A) «oracle.json conserva su contenido byte a byte»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An existing history is left intact

El lector A describe el efecto como «termina en error sin tocar el historial existente»; el lector B describe el efecto como «el proceso termina y oracle.json queda igual». Similitud de contenido 0.11, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An existing history is left intact» es la correcta?**
- (A) «termina en error sin tocar el historial existente»
- (B) «el proceso termina y oracle.json queda igual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The original bytes survive in the copy

El lector A describe el efecto como «graba el run y preserva el historial corrupto en una copia»; el lector B describe el efecto como «el proceso graba el run y conserva la copia corrupta original». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The original bytes survive in the copy» es la correcta?**
- (A) «graba el run y preserva el historial corrupto en una copia»
- (B) «el proceso graba el run y conserva la copia corrupta original»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The warning names the copy

El lector A registra «escribe en stderr un aviso que nombra la ruta de la copia» y ningún otro lector lo recoge; el lector B registra «crea la copia corrupt-<marca>» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The warning names the copy»?**
- (A) «escribe en stderr un aviso que nombra la ruta de la copia»
- (B) «crea la copia corrupt-<marca>»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The warning names the copy

El lector A describe el efecto como «graba el run y avisa por stderr de la copia creada»; el lector B describe el efecto como «el proceso graba el run y avisa con la ruta de la copia». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The warning names the copy» es la correcta?**
- (A) «graba el run y avisa por stderr de la copia creada»
- (B) «el proceso graba el run y avisa con la ruta de la copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No history, no copy

El lector A describe el efecto como «crea el historial sin generar ninguna copia»; el lector B describe el efecto como «el proceso crea sólo oracle.json, sin copia». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No history, no copy» es la correcta?**
- (A) «crea el historial sin generar ninguna copia»
- (B) «el proceso crea sólo oracle.json, sin copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A copy that cannot be written keeps the original in place

El lector A describe el efecto como «conserva el historial original sin sustituirlo»; el lector B describe el efecto como «oracle.json conserva su contenido original intacto». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A copy that cannot be written keeps the original in place» es la correcta?**
- (A) «conserva el historial original sin sustituirlo»
- (B) «oracle.json conserva su contenido original intacto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A run that could not be recorded is not a verdict

El lector A describe el efecto como «termina en error al no poder grabar el run»; el lector B describe el efecto como «el proceso termina sin registrar el run». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A run that could not be recorded is not a verdict» es la correcta?**
- (A) «termina en error al no poder grabar el run»
- (B) «el proceso termina sin registrar el run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A readable history with extra keys is not corrupt

El lector A registra «conserva los runs anteriores más el actual, con la clave extra intacta» y ningún otro lector lo recoge; el lector B registra «añade el run actual al historial existente» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A readable history with extra keys is not corrupt»?**
- (A) «conserva los runs anteriores más el actual, con la clave extra intacta»
- (B) «añade el run actual al historial existente»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A readable history with extra keys is not corrupt

El lector A describe el efecto como «añade el run al historial sin crear ninguna copia»; el lector B describe el efecto como «el historial conserva runs previos y añade el actual». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A readable history with extra keys is not corrupt» es la correcta?**
- (A) «añade el run al historial sin crear ninguna copia»
- (B) «el historial conserva runs previos y añade el actual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A second corruption never overwrites the first copy

El lector A describe el efecto como «crea una segunda copia sin sobrescribir la primera»; el lector B describe el efecto como «cada invocación graba el run y crea una copia distinta». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A second corruption never overwrites the first copy» es la correcta?**
- (A) «crea una segunda copia sin sobrescribir la primera»
- (B) «cada invocación graba el run y crea una copia distinta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Lagunas declaradas · 2

2 lagunas declaradas sobre 2 escenarios. Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala
un hueco del delta, no un fallo del lector.

### Escenario: A copy that cannot be written keeps the original in place

El lector B declara que el texto no lo resuelve: «el escenario no indica el código de salida, aunque el texto del requisito general para este caso dice 2».

**¿Qué debe ocurrir en «A copy that cannot be written keeps the original in place»?**
- (A) «conserva el historial original sin sustituirlo» (lectura de A)
- (B) «oracle.json conserva su contenido original intacto» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: A failed copy is reported as a run that was not recorded

El lector B declara que el texto no lo resuelve: «el escenario no indica el código de salida en su propio THEN».

**¿Qué debe ocurrir en «A failed copy is reported as a run that was not recorded»?**
- (A) «avisa por stderr que el run no se ha grabado» (lectura de A)
- (B) «stderr avisa que el run no se ha grabado» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-012 — R-ORC-012 obliga a copiar los bytes corruptos aparte y «escribir el historial nuevo», pero no exige que ese historial nuevo conserve rastro alguno de los runs descartados: una implementación literal deja un `oracle.json` con un único run verde, indistinguible de un primer run legítimo. Basta con que un byte deje el fichero inválido (o con que una escritura previa se interrumpa) para que todo el historial rojo que `verify`/V17 exigen desaparezca del disco y un change quede declarable `verified` sin que jamás conste el rojo previo.
- **[medium]** R-ORC-012 — Nada en R-ORC-012 exige comprobar la legibilidad de `oracle.json` antes de invocar el runner ni reparar el fichero cuando la copia falla: una implementación literal ejecuta la suite entera, intenta la copia, falla, tira el resultado verde y sale con 2 dejando el `oracle.json` corrupto intacto. Cada reintento repite la suite completa y vuelve a salir 2, de modo que el change no puede alcanzar `verified` hasta que alguien borre el fichero a mano, y el `2` es además indistinguible de un error de uso para `gate.py`.
