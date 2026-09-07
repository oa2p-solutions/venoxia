# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 12
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 7 divergencias duras, 14 blandas y 0 lagunas declaradas sobre los 12 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 7

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: An existing history is left intact

El lector A registra «oracle.json no se modifica» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice.

**¿Qué efectos observables debe producir «An existing history is left intact»?**
- (A) «oracle.json no se modifica»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The original bytes survive in the copy

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The original bytes survive in the copy»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: The warning names the copy

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The warning names the copy»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: No history, no copy

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «No history, no copy»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: No history, no copy

El lector A registra «se crea oracle.json con el nuevo run» y ningún otro lector lo recoge; el lector B registra «no se crea ningún fichero oracle.json.corrupt-<marca>» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice.

**¿Qué efectos observables debe producir «No history, no copy»?**
- (A) «se crea oracle.json con el nuevo run»
- (B) «no se crea ningún fichero oracle.json.corrupt-<marca>»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A readable history with extra keys is not corrupt

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «A readable history with extra keys is not corrupt»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: A second corruption never overwrites the first copy

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «A second corruption never overwrites the first copy»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

## Divergencias blandas · 14

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Both flags in one invocation

El lector A describe el efecto como «el proceso termina antes de ejecutar el runner»; el lector B describe el efecto como «el proceso termina con error de uso». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Both flags in one invocation» es la correcta?**
- (A) «el proceso termina antes de ejecutar el runner»
- (B) «el proceso termina con error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is written under both flags

El lector A describe el efecto como «el directorio del change no gana ningún fichero»; el lector B describe el efecto como «el proceso termina con error y no crea ficheros». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Nothing is written under both flags» es la correcta?**
- (A) «el directorio del change no gana ningún fichero»
- (B) «el proceso termina con error y no crea ficheros»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names both flags

El lector B registra «stderr recibe un aviso que nombra --dry-run y --record» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The usage error names both flags»?**
- (A) «stderr recibe un aviso que nombra --dry-run y --record»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The usage error names both flags

El lector A describe el efecto como «stderr muestra un aviso citando ambas banderas»; el lector B describe el efecto como «el proceso termina y stderr nombra ambas banderas». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The usage error names both flags» es la correcta?**
- (A) «stderr muestra un aviso citando ambas banderas»
- (B) «el proceso termina y stderr nombra ambas banderas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An existing history is left intact

El lector A describe el efecto como «oracle.json queda igual, sin cambios de bytes»; el lector B describe el efecto como «el proceso termina sin tocar el historial existente». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An existing history is left intact» es la correcta?**
- (A) «oracle.json queda igual, sin cambios de bytes»
- (B) «el proceso termina sin tocar el historial existente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The warning names the copy

El lector A registra «se crea oracle.json.corrupt-<marca>» y ningún otro lector lo recoge; el lector B registra «stderr recibe un aviso que nombra la ruta de la copia» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The warning names the copy»?**
- (A) «se crea oracle.json.corrupt-<marca>»
- (B) «stderr recibe un aviso que nombra la ruta de la copia»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The warning names the copy

El lector A describe el efecto como «stderr informa la ruta de la copia creada»; el lector B describe el efecto como «stderr avisa nombrando la ruta de la copia creada». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The warning names the copy» es la correcta?**
- (A) «stderr informa la ruta de la copia creada»
- (B) «stderr avisa nombrando la ruta de la copia creada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No history, no copy

El lector A describe el efecto como «se graba el run sin crear ninguna copia»; el lector B describe el efecto como «se graba el historial nuevo sin crear ninguna copia». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No history, no copy» es la correcta?**
- (A) «se graba el run sin crear ninguna copia»
- (B) «se graba el historial nuevo sin crear ninguna copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A copy that cannot be written keeps the original in place

El lector A describe el efecto como «oracle.json conserva su contenido original sin cambios»; el lector B describe el efecto como «el historial original queda intacto sin sustituir». Similitud de contenido 0.11, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A copy that cannot be written keeps the original in place» es la correcta?**
- (A) «oracle.json conserva su contenido original sin cambios»
- (B) «el historial original queda intacto sin sustituir»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A run that could not be recorded is not a verdict

El lector A describe el efecto como «el proceso termina en error, sin veredicto grabado»; el lector B describe el efecto como «el proceso termina sin grabar ningún run». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A run that could not be recorded is not a verdict» es la correcta?**
- (A) «el proceso termina en error, sin veredicto grabado»
- (B) «el proceso termina sin grabar ningún run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A readable history with extra keys is not corrupt

El lector B registra «no se crea ninguna copia» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A readable history with extra keys is not corrupt»?**
- (A) «no se crea ninguna copia»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A readable history with extra keys is not corrupt

El lector A describe el efecto como «el historial se actualiza sin crear ninguna copia»; el lector B describe el efecto como «el historial se actualiza con los runs previos más el actual». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A readable history with extra keys is not corrupt» es la correcta?**
- (A) «el historial se actualiza sin crear ninguna copia»
- (B) «el historial se actualiza con los runs previos más el actual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A second corruption never overwrites the first copy

El lector B registra «existen dos ficheros oracle.json.corrupt-<marca>» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A second corruption never overwrites the first copy»?**
- (A) «existen dos ficheros oracle.json.corrupt-<marca>»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A second corruption never overwrites the first copy

El lector A describe el efecto como «quedan dos copias distintas, sin sobrescribir la primera»; el lector B describe el efecto como «quedan dos copias distintas, ninguna sobrescrita». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A second corruption never overwrites the first copy» es la correcta?**
- (A) «quedan dos copias distintas, sin sobrescribir la primera»
- (B) «quedan dos copias distintas, ninguna sobrescrita»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-ORC-012 — El requisito sólo exige «un sufijo numérico tras la marca si ese nombre ya existe» y el único escenario que lo prueba usa dos corrupciones; una implementación que, al ver ocupado `oracle.json.corrupt-<marca>`, escriba siempre `oracle.json.corrupt-<marca>-1` cumple el texto y los escenarios, pero en la tercera corrupción con la misma marca sobrescribe la copia anterior y destruye para siempre los bytes que el requisito promete conservar.
- **[medium]** R-ORC-012 — En la vía corrupta el delta sólo exige «escribir el historial nuevo» sin decir qué contiene (el escenario que obliga a «sus runs anteriores más el actual» es únicamente el del historial legible); una implementación que copie aparte el fichero corrupto y deje `oracle.json` como `{"runs": []}` pasa los siete escenarios, sale con código 0 y sin el aviso de «no se ha grabado», de modo que el usuario cree registrada una ejecución completa de la suite que en realidad no consta en ninguna parte y bloquea después la verificación.

## Escenarios que convergen · 1

- A failed copy is reported as a run that was not recorded
