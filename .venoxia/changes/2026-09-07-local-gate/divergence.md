# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-local-gate/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 16
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 4 divergencias blandas sobre los 16 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 4

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The four steps by name

El lector A describe el efecto como «lista los cuatro pasos con su comando, sin ejecutar nada»; el lector B describe el efecto como «lista los cuatro pasos con su comando, sin ejecutarlos». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The four steps by name» es la correcta?**
- (A) «lista los cuatro pasos con su comando, sin ejecutar nada»
- (B) «lista los cuatro pasos con su comando, sin ejecutarlos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The matrix is skipped on purpose

El lector A describe el efecto como «matrix aparece omitido a petición y el resto pasa»; el lector B describe el efecto como «matrix aparece omitido a petición en el resumen». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The matrix is skipped on purpose» es la correcta?**
- (A) «matrix aparece omitido a petición y el resto pasa»
- (B) «matrix aparece omitido a petición en el resumen»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The hook propagates a failed check

El lector A describe el efecto como «git aborta el push con el mismo código de la comprobación»; el lector B describe el efecto como «el hook termina en fallo y git aborta el push». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The hook propagates a failed check» es la correcta?**
- (A) «git aborta el push con el mismo código de la comprobación»
- (B) «el hook termina en fallo y git aborta el push»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The hook propagates a check that could not run

El lector A describe el efecto como «git aborta el push con el mismo código de la comprobación»; el lector B describe el efecto como «el hook termina sin poder ejecutar y git aborta el push». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The hook propagates a check that could not run» es la correcta?**
- (A) «git aborta el push con el mismo código de la comprobación»
- (B) «el hook termina sin poder ejecutar y git aborta el push»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-CI-020 — La obligación de `--rm` sólo aparece en el escenario que observa la salida de `--list`; la prosa del requisito no la menciona. Una implementación que imprime en `--list` el comando canónico con `--rm` pero ejecuta la matriz por otra vía (o sin `--rm`) pasa los seis escenarios y deja tres contenedores detenidos por cada ejecución: con el hook de `pre-push` activo eso son tres contenedores y sus capas de escritura por cada `git push`, que nadie borra y que llenan el disco hasta que alguien hace `docker container prune` a mano.
- **[medium]** R-CI-019 — R-CI-019 enumera los cuatro pasos sin fijar orden ni exigir que se ejecuten de uno en uno, y R-CI-020 exige paralelismo dentro de `matrix`: una implementación que lanza los cuatro pasos a la vez cumple ambas frases y pone en marcha simultáneamente tres suites en contenedores, la suite instrumentada de `tools/coverage.py` y las ejecuciones de `verifies:` que dispara el oráculo dentro de `gate`, todas sobre el mismo árbol de trabajo. Bajo esa carga los subprocesos de la suite agotan su timeout y el resultado (rojo/verde, y la atribución `timeout` del oráculo) pasa a depender del planificador: `push` bloqueados al azar y veredictos no reproducibles.
- **[medium]** R-CI-021 — R-CI-021 obliga a que el hook viva en el repositorio y a que el README pida `git config core.hooksPath .githooks` en cada clon, sin exigir ninguna comprobación de procedencia de lo que se ejecuta. A partir de esa línea, hacer `push` con una rama ajena revisada en local ejecuta el `tools/check.py` y el `test_command` de esa rama —vía `gate`/oráculo— en el host, con los privilegios de quien empuja y fuera de todo contenedor: revisar y reenviar la rama de un contribuidor se convierte en ejecución de su código sin que ninguna frase del delta lo advierta ni lo limite (el aislamiento en contenedor sólo cubre el paso `matrix`).

## Escenarios que convergen · 12

- One step fails
- Every step passes
- A required executable is missing
- An unknown option
- One container per version of the matrix
- The suite fails in one version
- Never as root
- The matrix cannot be read from the workflow
- Docker is not usable
- The hook is an executable that runs the local check
- The hook passes no options
- The README says how to enable it
