# ci Delta

## ADDED Requirements

### R-CI-019 · The local check runs the CI gate as one command

WHEN se ejecuta `tools/check.py` desde la raíz del repositorio, el sistema
DEBE ejecutar cuatro pasos —`matrix`, `coverage`, `gate` y `plugin-validate`—
y DEBE terminar con código `0` sólo si los cuatro terminan en verde, con `1`
si alguno falla y con `2` si un paso no se pudo ejecutar o la invocación es
incorrecta.

Los cuatro pasos son los jobs del CI, en local: `matrix` es la suite en cada
versión de Python soportada, `coverage` es `tools/coverage.py`, `gate` es
`scripts/gate.py --root .` sobre este mismo repositorio —que ya incluye el
acta y el validador en estricto y el oráculo de cada change en `verified`—, y
`plugin-validate` es `claude plugin validate . --strict`. El job `evals` se
queda fuera a propósito: cuesta tokens y se lanza a mano.

Un paso que no se pudo ejecutar no es un paso en rojo ni en verde: es una
comprobación que no ocurrió, y aprobarla sería aprobar lo que no se ha
mirado. Por eso el código es `2`, el mismo que el resto del núcleo reserva
para el error de uso.

#### Scenario: The four steps by name
- **WHEN** se pide la lista de pasos con `--list`
- **THEN** la salida nombra `matrix`, `coverage`, `gate` y `plugin-validate`
  con el comando de cada uno, no se ejecuta ninguno y la comprobación termina
  con código `0`

#### Scenario: One step fails
- **WHEN** un paso termina en fallo
- **THEN** el resumen lo marca en rojo, muestra el final de su salida y la
  comprobación termina con código `1`

#### Scenario: Every step passes
- **WHEN** los cuatro pasos terminan en verde
- **THEN** la comprobación termina con código `0`

#### Scenario: A required executable is missing
- **WHEN** falta en el `PATH` un ejecutable que un paso necesita
- **THEN** la comprobación termina con código `2` y el mensaje nombra el
  ejecutable que falta

#### Scenario: An unknown option
- **WHEN** se invoca con una opción que no existe
- **THEN** la comprobación termina con código `2` y el mensaje de uso

verifies:   tests/test_check.py
confidence: high
from:       README.md#verificar-regresiones

### R-CI-020 · The Python matrix runs in containers as an unprivileged user

WHEN la comprobación local ejecuta el paso `matrix`, el sistema DEBE lanzar la
suite una vez por cada versión de Python que declara la matriz del workflow de
CI, cada una dentro de un contenedor con la imagen `python:<versión>-slim`,
con el usuario y el grupo de quien invoca en vez de root, y las tres en
paralelo; el paso queda en verde sólo cuando los tres contenedores han
terminado en verde.

Las versiones se toman de la misma matriz que el workflow y no de una lista
aparte, porque dos listas envejecen por separado. El usuario sin privilegios
no es un detalle: como root, quince tests de permisos se saltan y la cobertura
del guardián cae por debajo de su umbral, y eso ya pasó una vez en el CI.

Un cliente `docker` sin demonio en marcha, o ausente, impide comprobar; la
única forma de seguir sin la matriz es pedirlo con `--no-docker`, que deja el
paso como omitido a petición y a la vista en el resumen. Es una frontera que
se declara aquí: con `--no-docker` el código de salida es el que dicten los
otros tres pasos, igual que si la matriz hubiera pasado, y la diferencia está
sólo en el resumen. Se acepta porque la opción se escribe a mano cada vez y el hook
de `pre-push` nunca la pasa (`R-CI-021`). Una matriz que no se puede leer del
workflow, o que está vacía, tampoco es un verde: cero contenedores no
comprueban nada, y el código es `2`.

#### Scenario: One container per version of the matrix
- **WHEN** se listan los comandos del paso `matrix`
- **THEN** hay un comando `docker run` por cada versión de la matriz del
  workflow, cada uno usa la imagen `python:<versión>-slim` de su versión y
  lleva `--rm` para que el contenedor se borre al terminar, y la lista termina
  con código `0`

#### Scenario: The suite fails in one version
- **WHEN** la suite termina en fallo en al menos uno de los contenedores de la
  matriz
- **THEN** el paso `matrix` se marca en rojo, muestra el final de la salida
  del contenedor que falló y la comprobación termina con código `1`

#### Scenario: Never as root
- **WHEN** se listan los comandos del paso `matrix`
- **THEN** cada comando lleva `--user` con el uid y el gid de quien invoca, y
  la lista termina con código `0`

#### Scenario: The matrix cannot be read from the workflow
- **WHEN** el workflow no declara una matriz de versiones legible, o la declara
  vacía
- **THEN** la comprobación termina con código `2` y el mensaje nombra el
  fichero del workflow

#### Scenario: Docker is not usable
- **WHEN** no hay un cliente `docker` utilizable y no se ha pedido `--no-docker`
- **THEN** la comprobación termina con código `2` y el mensaje nombra
  `--no-docker`

#### Scenario: The matrix is skipped on purpose
- **WHEN** se pasa `--no-docker` y los otros tres pasos terminan en verde
- **THEN** el paso `matrix` aparece como omitido a petición en el resumen y la
  comprobación termina con código `0`

verifies:   tests/test_check.py
confidence: high
from:       README.md#verificar-regresiones

### R-CI-021 · A pre-push hook runs the local check

WHEN se hace `git push` con `core.hooksPath` apuntando a `.githooks/`, el
sistema DEBE ejecutar la comprobación local antes de enviar nada y DEBE
terminar el hook con el mismo código que la comprobación, de modo que git
aborte el `push` cuando no queda en verde.

El hook vive en el repositorio y no en `.git/hooks/`, que no se versiona:
activarlo es una línea por clon, y el README la da en el mismo sitio donde
explica el resto de la verificación. Quien de verdad necesite empujar sin
comprobar tiene `git push --no-verify`, que deja rastro en la orden y no en
el silencio. Por lo mismo, el hook invoca la comprobación sin opciones: un
hook que pasara `--no-docker` o `--list` cumpliría la forma y vaciaría el
fondo. Frontera declarada: el hook comprueba el árbol de trabajo de quien
empuja, no las referencias que git le entrega, así que empujar una rama que no
es la que está desplegada, o con cambios sin commitear, comprueba otra cosa que
lo que se envía. Es el límite de un hook de una sola línea, y se acepta porque
en este repositorio se empuja la rama en la que se trabaja.

#### Scenario: The hook is an executable that runs the local check
- **WHEN** se lee `.githooks/pre-push`
- **THEN** es un fichero ejecutable que invoca `tools/check.py` de la raíz del
  repositorio

#### Scenario: The hook propagates a failed check
- **WHEN** la comprobación local termina en fallo
- **THEN** el hook termina con código `1`, el mismo de la comprobación, y git
  aborta el `push`

#### Scenario: The hook propagates a check that could not run
- **WHEN** la comprobación local no se pudo ejecutar
- **THEN** el hook termina con código `2`, el mismo de la comprobación, y git
  aborta el `push`

#### Scenario: The hook passes no options
- **WHEN** se lee `.githooks/pre-push`
- **THEN** la invocación de `tools/check.py` no lleva `--no-docker` ni `--list`

#### Scenario: The README says how to enable it
- **WHEN** se lee la sección «## Verificar regresiones» de `README.md`
- **THEN** nombra `tools/check.py` y `git config core.hooksPath .githooks`

verifies:   tests/test_check.py
confidence: high
from:       README.md#verificar-regresiones
