# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-local-gate/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 14
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 0 divergencias duras, 2 blandas y 2 lagunas declaradas sobre los 14 escenarios. Esta ejecución sale con código 1.

## Divergencias blandas · 2

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The four steps by name

El lector A describe el efecto como «lista los cuatro pasos con su comando, sin ejecutar nada»; el lector B describe el efecto como «lista los cuatro pasos con su comando sin ejecutarlos». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The four steps by name» es la correcta?**
- (A) «lista los cuatro pasos con su comando, sin ejecutar nada»
- (B) «lista los cuatro pasos con su comando sin ejecutarlos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Never as root

El lector A describe el efecto como «cada comando lleva --user con uid y gid del invocador»; el lector B describe el efecto como «cada comando docker run lleva --user con uid y gid del invocante». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Never as root» es la correcta?**
- (A) «cada comando lleva --user con uid y gid del invocador»
- (B) «cada comando docker run lleva --user con uid y gid del invocante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Lagunas declaradas · 2

2 lagunas declaradas sobre 2 escenarios. Un lector ha dicho que el texto no lo resuelve. Esa respuesta es correcta y señala
un hueco del delta, no un fallo del lector.

### Escenario: The matrix is skipped on purpose

El lector B declara que el texto no lo resuelve: «el código 0 está condicionado a que los otros tres pasos terminen en verde, y el texto no dice qué código se observa si alguno de esos tres falla en este mismo escenario».

**¿Qué debe ocurrir en «The matrix is skipped on purpose»?**
- (A) «el paso matrix aparece omitido a petición en el resumen» (lectura de A y B)
- (B) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

### Escenario: The hook propagates the verdict

El lector B declara que el texto no lo resuelve: «el texto dice que el código no es 0 pero no fija cuál es el valor concreto que se observa».

**¿Qué debe ocurrir en «The hook propagates the verdict»?**
- (A) «el hook termina con el mismo código y git aborta el push» (lectura de A y B)
- (B) Ninguna de las anteriores, el delta debe decir explícitamente qué ocurre

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-020 — R-CI-020 sólo exige lanzar un contenedor por versión «las tres en paralelo»; nada dice que el veredicto del paso `matrix` sea la agregación de los códigos de salida de los tres contenedores. Una implementación que los lanza en segundo plano (o con `docker run -d`) y da el paso por verde en cuanto los tres arrancan cumple los dos escenarios (que sólo inspeccionan los comandos listados con `--list`) y hace que `tools/check.py` —y por tanto el hook de pre-push— apruebe pushes con la suite en rojo en alguna versión de Python, que es justo lo que el change existe para impedir.
- **[medium]** R-CI-021 — R-CI-021 exige que el hook invoque `tools/check.py` de la raíz sin opciones, y nada lo obliga a mirar las refs que git le entrega por stdin: el hook comprueba el árbol de trabajo actual, no los commits que se envían. Empujar una rama distinta de la que está checked out, o con cambios sin commitear, da verde a commits que nadie ha comprobado (y bloquea pushes limpios por ediciones locales sucias), dejando el hook como una garantía vacía.
- **[medium]** R-CI-020 — R-CI-020 fija imagen, `--user` y paralelismo de los `docker run`, pero ninguna frase obliga a `--rm` ni a borrar los contenedores después; una implementación literal deja tres contenedores parados por ejecución y, con el hook de pre-push activo (R-CI-021), cada push acumula tres más hasta llenar el disco del desarrollador, que tendrá que limpiarlos a mano.

## Escenarios que convergen · 10

- One step fails
- Every step passes
- A required executable is missing
- An unknown option
- One container per version of the matrix
- The matrix cannot be read from the workflow
- Docker is not usable
- The hook is an executable that runs the local check
- The hook passes no options
- The README says how to enable it
