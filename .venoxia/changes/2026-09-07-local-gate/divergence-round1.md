# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-local-gate/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 12
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 0 divergencias duras, 4 blandas y 5 lagunas declaradas sobre los 12 escenarios. Esta ejecución sale con código 1.

## Divergencias blandas · 4

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The four steps by name

El lector A describe el efecto como «muestra los cuatro pasos con su comando, sin ejecutar nada»; el lector B describe el efecto como «lista los cuatro pasos con su comando sin ejecutarlos». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The four steps by name» es la correcta?**
- (A) «muestra los cuatro pasos con su comando, sin ejecutar nada»
- (B) «lista los cuatro pasos con su comando sin ejecutarlos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Never as root

El lector A describe el efecto como «cada comando docker lleva --user con uid y gid del invocador»; el lector B describe el efecto como «cada comando listado lleva --user con uid y gid de quien invoca». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Never as root» es la correcta?**
- (A) «cada comando docker lleva --user con uid y gid del invocador»
- (B) «cada comando listado lleva --user con uid y gid de quien invoca»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The matrix is skipped on purpose

El lector A describe el efecto como «el paso matrix aparece omitido a petición en el resumen»; el lector B describe el efecto como «el paso matrix aparece omitido a petición y no cuenta como fallo». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The matrix is skipped on purpose» es la correcta?**
- (A) «el paso matrix aparece omitido a petición en el resumen»
- (B) «el paso matrix aparece omitido a petición y no cuenta como fallo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The hook propagates the verdict

El lector A registra «git aborta el push si el código no es 0» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The hook propagates the verdict»?**
- (A) «git aborta el push si el código no es 0»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Lagunas declaradas · 5

5 lagunas declaradas sobre 5 escenarios. Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala
un hueco del delta, no un fallo del lector.

### Escenario: The four steps by name

El lector B declara que el texto no lo resuelve: «no dice el código de salida de invocar --list».

**¿Qué debe ocurrir en «The four steps by name»?**
- (A) «muestra los cuatro pasos con su comando, sin ejecutar nada» (lectura de A)
- (B) «lista los cuatro pasos con su comando sin ejecutarlos» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: One container per version of the matrix

El lector B declara que el texto no lo resuelve: «no dice el código de salida al listar los comandos del paso matrix».

**¿Qué debe ocurrir en «One container per version of the matrix»?**
- (A) «lista un comando docker run por versión de la matriz» (lectura de A y B)
- (B) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: Never as root

El lector B declara que el texto no lo resuelve: «no dice el código de salida al listar los comandos del paso matrix».

**¿Qué debe ocurrir en «Never as root»?**
- (A) «cada comando docker lleva --user con uid y gid del invocador» (lectura de A)
- (B) «cada comando listado lleva --user con uid y gid de quien invoca» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: The matrix is skipped on purpose

El lector B declara que el texto no lo resuelve: «no dice el código de salida final cuando se pasa --no-docker».

**¿Qué debe ocurrir en «The matrix is skipped on purpose»?**
- (A) «el paso matrix aparece omitido a petición en el resumen» (lectura de A)
- (B) «el paso matrix aparece omitido a petición y no cuenta como fallo» (lectura de B)
- (C) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: The hook propagates the verdict

El lector B declara que el texto no lo resuelve: «el código exacto depende del resultado de la comprobación, no se fija un valor concreto».

**¿Qué debe ocurrir en «The hook propagates the verdict»?**
- (A) «el hook termina con el mismo código que la comprobación» (lectura de A y B)
- (B) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-020 — «un comando `docker run` por cada versión de la matriz del workflow» se cumple de forma vacía: si el fichero del workflow no está, cambia de formato o su matriz se lee como lista vacía, el paso `matrix` lanza cero contenedores, ningún comando falla y el paso termina «en verde», con lo que `tools/check.py` sale con `0` sin haber ejecutado la suite en ninguna versión de Python y el pre-push aprueba el envío.
- **[medium]** R-CI-020 — Con `--no-docker` el paso omitido «no cuenta como fallo», así que la comprobación termina con código `0`, exactamente el mismo que un verde completo; la única diferencia está en una línea de prosa del resumen, de modo que el hook de pre-push —y cualquier script que lea sólo el código de salida— aprueba un push cuya suite no se ha ejecutado en ninguna versión de la matriz ni con usuario sin privilegios.
- **[medium]** R-CI-021 — El delta sólo exige que `.githooks/pre-push` sea ejecutable, invoque `tools/check.py` y propague su código; un hook que invoque siempre `tools/check.py --no-docker` (o incluso `--list`, que por contrato no ejecuta nada y no puede terminar en fallo) cumple los tres escenarios al pie de la letra mientras deja la verificación local reducida a nada, y el desarrollador cree estar protegido porque activó `core.hooksPath`.

## Escenarios que convergen · 7

- One step fails
- Every step passes
- A required executable is missing
- An unknown option
- Docker is not usable
- The hook is an executable that runs the local check
- The README says how to enable it
