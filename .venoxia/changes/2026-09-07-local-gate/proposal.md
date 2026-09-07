# 2026-09-07-local-gate Proposal

## Why

Quien escribe el código de este repositorio son sesiones de Claude, y una
sesión puede commitear y empujar sin haber corrido la suite. Hoy nada lo
impide: los comandos existen —la suite, la cobertura, la puerta, la
validación del plugin—, pero nadie los encadena antes del `push`, y Python
3.12 ni siquiera está instalado en la máquina de desarrollo.

El CI remoto tampoco lo cubre. El de GitHub Actions se quedó en cola sin
runner en sus tres intentos, y el que sí corre vive en el respaldo, así que
sólo se ejecuta cuando alguien espeja a mano. Mientras tanto, tres regresiones
reales se cazaron en un CI y no en local: los tests que sólo tienen sentido en
un sistema de ficheros de macOS y que en Linux se comportan distinto; los
quince tests de permisos que root se salta y que hunden la cobertura; y el
fallo de la instrumentación de cobertura que se hacía pasar por el código de
salida del programa medido.

La puerta que la Fase 13 convirtió en comando prometía correr «igual en
cualquier CI, en un hook local o a mano». Falta el hook local.

## What Changes

- Existe una comprobación local, un solo comando, que encadena lo mismo que
  los jobs del CI: la suite en las tres versiones de Python dentro de
  contenedores, la cobertura, la puerta sobre este mismo repositorio y la
  validación de la estructura del plugin. Termina con un veredicto único.
- La matriz de Python corre en contenedores `python:<versión>-slim` como
  usuario sin privilegios, en paralelo, y toma las versiones de la misma
  matriz que declara el workflow de CI.
- Un hook de `pre-push` ejecuta la comprobación local y aborta el `push` si no
  queda en verde. Se activa por clon con `git config core.hooksPath
  .githooks`, y el README lo documenta junto al resto de la verificación.

## Capabilities

### Modified Capabilities

- `ci`: la puerta que el CI ejecuta en cada `push` pasa a ejecutarse también
  antes de cada `push`, desde la máquina de quien empuja.

## Impact

- Un `git push` con el hook activado tarda unos tres minutos más: la
  cobertura bajo `trace` y los tres contenedores en paralelo dominan el
  tiempo. Es el coste de no empujar código roto.
- Hace falta un cliente `docker` con el demonio en marcha. Sin él, la
  comprobación no aprueba lo que no ha comprobado: termina con error de uso,
  y `--no-docker` es la única forma de saltarse la matriz, a la vista y a
  propósito.
- `claude` tiene que estar en el `PATH` para la validación del plugin; si
  falta, el mismo error de uso.
- Ningún cambio en los scripts del núcleo, en el guardián ni en el esquema
  JSON versión 1. `tools/` gana un fichero y el repositorio un directorio
  `.githooks/`.

## Confidence

- **Que la matriz en contenedores reproduzca lo que el CI mide** · `high` ·
  medido hoy en esta máquina: 794 tests en verde en 3.12, 3.13 y 3.14 dentro
  de `python:<versión>-slim`; los seis tests que se saltan son los que sólo
  tienen sentido en APFS y que la ejecución nativa en macOS sí corre.
- **Que tres minutos por `push` sean asumibles** · `medium` · es una apuesta
  sobre la paciencia de quien empuja, no sobre el código · se revisa cuando
  alguien empiece a empujar con `--no-verify` para saltarse el hook.
- **El resto de la propuesta** · `high` · la comprobación encadena comandos
  que ya existen y ya tienen tests.

## Pendiente

Cerrado el 2026-09-07 en el día. Divergencia en **tres rondas** con lectores
nuevos cada vez: la ronda 1 dio 0 duras, 4 blandas y 5 lagunas, todas por
códigos de salida que el delta no decía (`--list`, la lista de la matriz,
`--no-docker`); la ronda 2 bajó a 2 lagunas (el código con `--no-docker` si
otro paso falla, y el valor concreto que propaga el hook); la ronda 3 cerró
con 0 duras, 4 blandas y 0 lagunas sobre 16 escenarios. Las 4 blandas son
paráfrasis con los mismos códigos en los dos lectores.

El abogado del diablo dejó nueve ataques en tres rondas y cinco cambiaron el
contrato: la matriz vacía o ilegible es un `2` y no un verde vacío; el paso
`matrix` agrega los tres contenedores y es rojo si uno falla; `--rm` en cada
`docker run`; el hook no pasa opciones; y los dos códigos que propaga el hook
son concretos. Los otros cuatro son fronteras que se declaran y no se
persiguen: con `--no-docker` el código es el mismo que con la matriz en verde
(la opción se escribe a mano y el hook no la pasa); el hook comprueba el
árbol de trabajo, no las referencias que git le entrega; `--list` imprime
exactamente el argv que se ejecuta, así que no hay un comando para enseñar y
otro para correr; y los cuatro pasos no corren todos a la vez: la matriz va
en segundo plano y los otros tres de uno en uno, porque tres suites en
contenedor más la cobertura instrumentada más los oráculos de la puerta
sobre el mismo árbol agotarían los timeouts y el veredicto dependería del
planificador. El último ataque —el paso `gate` ejecuta el `test_command` del
repositorio en la máquina, fuera de contenedor, así que empujar desde una
rama ajena es ejecutar su código— va al README como advertencia.

Oráculo: rojo grabado con `tools/check.py` y `.githooks/pre-push` aún sin
existir (3 `red`), verde después con los 18 tests de `tests/test_check.py`.
El hook queda activado en este clon con `git config core.hooksPath .githooks`.
