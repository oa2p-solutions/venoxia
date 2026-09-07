# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 9
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 3 divergencias duras, 5 blandas y 2 lagunas declaradas sobre los 9 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 3

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: Nothing is written under both flags

El lector A responde **2**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «Nothing is written under both flags»?**
- (A) 2
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: The usage error names both flags

El lector A responde **2**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The usage error names both flags»?**
- (A) 2
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: An existing history is left intact

El lector A responde **2**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «An existing history is left intact»?**
- (A) 2
- (B) Ninguno, el escenario no devuelve código de estado

## Divergencias blandas · 5

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: An existing history is left intact

El lector A describe el efecto como «oracle.json conserva su contenido original»; el lector B describe el efecto como «el oracle.json existente queda sin modificar byte a byte». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An existing history is left intact» es la correcta?**
- (A) «oracle.json conserva su contenido original»
- (B) «el oracle.json existente queda sin modificar byte a byte»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The warning names the copy

El lector A describe el efecto como «stderr nombra la ruta de la copia creada»; el lector B describe el efecto como «stderr muestra aviso con la ruta de la copia». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The warning names the copy» es la correcta?**
- (A) «stderr nombra la ruta de la copia creada»
- (B) «stderr muestra aviso con la ruta de la copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No history, no copy

El lector A describe el efecto como «no se crea ninguna copia porque no había historial»; el lector B describe el efecto como «no se crea ningún fichero de copia corrupta». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No history, no copy» es la correcta?**
- (A) «no se crea ninguna copia porque no había historial»
- (B) «no se crea ningún fichero de copia corrupta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A copy that cannot be written keeps the original in place

El lector A describe el efecto como «oracle.json original permanece intacto»; el lector B describe el efecto como «oracle.json conserva su contenido original byte a byte». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A copy that cannot be written keeps the original in place» es la correcta?**
- (A) «oracle.json original permanece intacto»
- (B) «oracle.json conserva su contenido original byte a byte»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A second corruption never overwrites the first copy

El lector A registra «se escribe una segunda copia oracle.json.corrupt-<marca> distinta de la primera» y ningún otro lector lo recoge; el lector B registra «se escriben dos ficheros oracle.json.corrupt-<marca> con nombres diferentes» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A second corruption never overwrites the first copy»?**
- (A) «se escribe una segunda copia oracle.json.corrupt-<marca> distinta de la primera»
- (B) «se escriben dos ficheros oracle.json.corrupt-<marca> con nombres diferentes»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Lagunas declaradas · 2

2 lagunas declaradas sobre 2 escenarios. Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala
un hueco del delta, no un fallo del lector.

### Escenario: A copy that cannot be written keeps the original in place

El lector B declara que el texto no lo resuelve: «el delta no dice qué código de salida ni qué aviso produce este fallo de escritura de la copia».

**¿Qué debe ocurrir en «A copy that cannot be written keeps the original in place»?**
- (A) «oracle.json original permanece intacto» (lectura de A)
- (B) «oracle.json conserva su contenido original byte a byte» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: A second corruption never overwrites the first copy

El lector B declara que el texto no lo resuelve: «el delta no explica cómo se genera un nombre distinto cuando la marca es la misma en ambas ejecuciones».

**¿Qué debe ocurrir en «A second corruption never overwrites the first copy»?**
- (A) «se crean dos copias con nombres distintos» (lectura de A)
- (B) «quedan dos copias corruptas con nombres distintos» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-012 — El requisito sólo exige que la copia «exista» antes de escribir el historial nuevo, no que esté completa: una implementación crea `oracle.json.corrupt-<marca>` vacío, sobrescribe `oracle.json` con el historial nuevo y sólo entonces vuelca en la copia los bytes originales. Pasa los cuatro escenarios, que únicamente observan el estado final; si el proceso muere entre medias, el único rastro de los runs anteriores (incluido el rojo previo que `verify` exige) queda destruido de forma irreversible en un fichero vacío.
- **[medium]** R-ORC-012 — El escenario «A copy that cannot be written keeps the original in place» sólo obliga a conservar `oracle.json` byte a byte, y nada exige código de salida distinto de 0 ni aviso: una implementación que, al fallar la copia, se salta silenciosamente el registro y termina con éxito cumple la letra, y el usuario cree haber registrado un run del oráculo que no está en disco en ninguna parte.
- **[low]** R-ORC-011 — R-ORC-011 prohíbe invocar el runner y escribir `oracle.json`, pero no prohíbe otras escrituras: una implementación que aplique primero R-ORC-012 (detecta `oracle.json` corrupto, crea la copia `oracle.json.corrupt-<marca>`) y sólo después detecte el conflicto de flags y salga con 2 pasa los cuatro escenarios, y cada errata de invocación con `--dry-run --record` deja un fichero basura nuevo en el change que nadie borra ni contabiliza.

## Escenarios que convergen · 2

- Both flags in one invocation
- The original bytes survive in the copy
