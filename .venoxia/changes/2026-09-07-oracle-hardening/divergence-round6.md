# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 12
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 15 blandas y 0 lagunas declaradas sobre los 12 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: No history, no copy

El lector A registra «crea oracle.json» y ningún otro lector lo recoge; el lector B registra «el directorio del change gana únicamente oracle.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice por su alcance (ninguna marca frente a «solo»).

**¿Qué efectos observables debe producir «No history, no copy»?**
- (A) «crea oracle.json»
- (B) «el directorio del change gana únicamente oracle.json»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 15

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Both flags in one invocation

El lector A describe el efecto como «el proceso termina sin ejecutar el runner»; el lector B describe el efecto como «rechaza la invocación con error de uso». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Both flags in one invocation» es la correcta?**
- (A) «el proceso termina sin ejecutar el runner»
- (B) «rechaza la invocación con error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is written under both flags

El lector B registra «no crea ningún fichero nuevo bajo el directorio del change» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Nothing is written under both flags»?**
- (A) «no crea ningún fichero nuevo bajo el directorio del change»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Nothing is written under both flags

El lector A describe el efecto como «el proceso termina y no crea ningún fichero»; el lector B describe el efecto como «rechaza la invocación sin escribir ningún fichero». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Nothing is written under both flags» es la correcta?**
- (A) «el proceso termina y no crea ningún fichero»
- (B) «rechaza la invocación sin escribir ningún fichero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names both flags

El lector A describe el efecto como «stderr muestra un aviso que nombra ambos flags»; el lector B describe el efecto como «rechaza la invocación y stderr nombra ambos flags». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The usage error names both flags» es la correcta?**
- (A) «stderr muestra un aviso que nombra ambos flags»
- (B) «rechaza la invocación y stderr nombra ambos flags»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An existing history is left intact

El lector A describe el efecto como «oracle.json queda sin modificar, byte a byte»; el lector B describe el efecto como «rechaza la invocación y no toca el historial existente». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An existing history is left intact» es la correcta?**
- (A) «oracle.json queda sin modificar, byte a byte»
- (B) «rechaza la invocación y no toca el historial existente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The original bytes survive in the copy

El lector A describe el efecto como «se crea una copia con los bytes originales del historial corrupto»; el lector B describe el efecto como «acepta el run y guarda copia del historial corrupto». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The original bytes survive in the copy» es la correcta?**
- (A) «se crea una copia con los bytes originales del historial corrupto»
- (B) «acepta el run y guarda copia del historial corrupto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The warning names the copy

El lector A describe el efecto como «stderr muestra un aviso que nombra la ruta de la copia»; el lector B describe el efecto como «acepta el run y stderr nombra la ruta de la copia». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The warning names the copy» es la correcta?**
- (A) «stderr muestra un aviso que nombra la ruta de la copia»
- (B) «acepta el run y stderr nombra la ruta de la copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No history, no copy

El lector A describe el efecto como «se crea únicamente el fichero oracle.json»; el lector B describe el efecto como «acepta el run y crea sólo oracle.json». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No history, no copy» es la correcta?**
- (A) «se crea únicamente el fichero oracle.json»
- (B) «acepta el run y crea sólo oracle.json»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A copy that cannot be written keeps the original in place

El lector B registra «oracle.json conserva su contenido original byte a byte» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A copy that cannot be written keeps the original in place»?**
- (A) «oracle.json conserva su contenido original byte a byte»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A copy that cannot be written keeps the original in place

El lector A describe el efecto como «el historial corrupto original no se sustituye»; el lector B describe el efecto como «rechaza el run y conserva el historial original». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A copy that cannot be written keeps the original in place» es la correcta?**
- (A) «el historial corrupto original no se sustituye»
- (B) «rechaza el run y conserva el historial original»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A run that could not be recorded is not a verdict

El lector A describe el efecto como «el proceso termina sin registrar el run como verdicto»; el lector B describe el efecto como «el proceso termina con error sin registrar veredicto». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A run that could not be recorded is not a verdict» es la correcta?**
- (A) «el proceso termina sin registrar el run como verdicto»
- (B) «el proceso termina con error sin registrar veredicto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A readable history with extra keys is not corrupt

El lector A registra «añade el run actual a la lista runs existente» y ningún otro lector lo recoge; el lector B registra «el historial conserva los runs anteriores y añade el actual» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A readable history with extra keys is not corrupt»?**
- (A) «añade el run actual a la lista runs existente»
- (B) «el historial conserva los runs anteriores y añade el actual»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A readable history with extra keys is not corrupt

El lector A describe el efecto como «el historial suma el run actual a los anteriores»; el lector B describe el efecto como «acepta el run y conserva runs anteriores más el actual». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A readable history with extra keys is not corrupt» es la correcta?**
- (A) «el historial suma el run actual a los anteriores»
- (B) «acepta el run y conserva runs anteriores más el actual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A second corruption never overwrites the first copy

El lector A registra «no sobrescribe la primera copia» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A second corruption never overwrites the first copy»?**
- (A) «no sobrescribe la primera copia»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A second corruption never overwrites the first copy

El lector A describe el efecto como «quedan dos copias distintas del historial corrupto»; el lector B describe el efecto como «cada invocación acepta el run y quedan dos copias distintas». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A second corruption never overwrites the first copy» es la correcta?**
- (A) «quedan dos copias distintas del historial corrupto»
- (B) «cada invocación acepta el run y quedan dos copias distintas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-ORC-012 — R-ORC-012 define «corrupto» incluyendo «no trae una lista `runs`»: un `oracle.json` perfectamente legible cuyos runs vengan como objeto en vez de lista (o bajo una clave heredada) se copia aparte y se sustituye por «el historial nuevo», que la frase permite que contenga sólo el run actual; todo el historial previo —incluido el run rojo que `/venoxia:verify` exige— desaparece del fichero que lee el validador, y el proceso sale con `0` avisando únicamente por `stderr`, invisible para cualquier caller que consuma el JSON de stdout.
- **[medium]** R-ORC-011 — R-ORC-011 sólo prohíbe «escribir o crear» ficheros bajo el directorio del change, y el único fichero protegido byte a byte por un escenario es `oracle.json`: una implementación que, antes de detectar el conflicto de flags, «limpie» las copias `oracle.json.corrupt-<marca>` (o cualquier otro fichero del change) y luego salga con `2` cumple los cuatro escenarios, y destruye de forma irreversible las únicas copias que R-ORC-012 dejó del historial original.

## Escenarios que convergen · 1

- A failed copy is reported as a run that was not recorded
