# Capability: ci

## Purpose

Hacer cumplible la tesis del plugin —«la spec falla en CI cuando miente»—
ejecutando en cada `push` la misma puerta que un desarrollador corre en
local: la suite, el validador y el acta en estricto, la cobertura y la
estructura del plugin. El CI del repositorio vive en la forja interna sobre
el runner interno de la organización; `scripts/gate.py` es la misma puerta
como comando para un proyecto que adopta Venoxia, y `tools/check.py` la
ejecuta en local antes de cada `push`.

## Requirements

### R-CI-008 · The workflow declares its triggers, its jobs and a runner it does not name

WHEN se busca el workflow del repositorio, el sistema DEBE tener uno que se
dispare en `push` y `pull_request` sobre la rama `main`, y también en
`workflow_dispatch`, que declare los cinco jobs `tests`, `self-spec`,
`coverage`, `plugin-validate` y `evals`, y cuyos `runs-on` tomen el nombre del
runner de una variable del repositorio en vez de escribirlo.

El repositorio es público, así que una etiqueta literal publica a cada persona
que lo clona el mapa de una infraestructura que no es suya y que no le sirve
para nada. Un workflow tiene que decir en qué runner corre; no tiene que
decirlo **aquí**, y quien administre la forja declara esas variables una vez.

La frontera, declarada: el directorio `.forgejo/workflows/` se queda. Es la
ruta que la forja exige, y moverlo a `.github/` quitaría la palabra a cambio de
un problema peor, porque GitHub Actions ejecutaría el workflow en el
repositorio público y fallaría por runners que allí no existen.

#### Scenario: Triggers read from disk
- **WHEN** se parsea el workflow del repositorio
- **THEN** declara `push` y `pull_request` acotados a `main`, y
  `workflow_dispatch`

#### Scenario: The five jobs by name
- **WHEN** se parsea el workflow del repositorio
- **THEN** declara los cinco jobs `tests`, `self-spec`, `coverage`,
  `plugin-validate` y `evals`

#### Scenario: No runner label is written down
- **WHEN** se parsea el workflow del repositorio
- **THEN** cada `runs-on` es una expresión que lee una variable del
  repositorio, y ninguno contiene una etiqueta escrita a mano

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-un-proyecto

### R-CI-009 · The tests job takes each Python from a container image

WHEN el job `tests` de `.forgejo/workflows/ci.yml` se ejecuta, el sistema
DEBE correr la suite dentro de la imagen `python:<versión>-slim` de cada
entrada de la matriz, con la matriz nombrando Python 3.12, 3.13 y 3.14,
porque el host del runner sólo tiene Python 3.14 instalado.

#### Scenario: The matrix names the three versions
- **WHEN** se parsea el job `tests` de `.forgejo/workflows/ci.yml`
- **THEN** su matriz nombra `3.12`, `3.13` y `3.14`

#### Scenario: The interpreter comes from the image
- **WHEN** se parsea el job `tests` de `.forgejo/workflows/ci.yml`
- **THEN** el job declara `container` con la imagen
  `python:${{ matrix.python-version }}-slim`

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-011 · The repository declares no GitHub Actions workflow

WHEN se recorre el árbol del repositorio, el sistema DEBE no contener
ningún fichero de workflow bajo `.github/workflows/`, porque el proyecto ha
dejado de usar GitHub y un workflow que nadie ejecuta promete una puerta que
no existe.

#### Scenario: No workflow directory for GitHub Actions
- **WHEN** se busca el directorio `.github/workflows/` en la raíz del
  repositorio
- **THEN** el directorio no existe

#### Scenario: The internal forge workflow is the one on disk
- **WHEN** se busca `.forgejo/workflows/ci.yml` en la raíz del repositorio
- **THEN** el fichero existe

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-012 · The internal forge workflow states its commands and safety nets on its own

WHEN se parsea `.forgejo/workflows/ci.yml`, el sistema DEBE declarar el
comando de la suite en el job `tests`, los dos comandos del validador y del
acta en `self-spec`, el comando de cobertura en `coverage`, la instalación
del CLI y `claude plugin validate . --strict` en `plugin-validate`, y
`claude plugin eval venoxia` en `evals`, DEBE arrancar solo ante un `push` y
un `pull_request` sobre `main`, DEBE llevar `continue-on-error: true` en
`coverage` y en `plugin-validate` y en ningún otro job ni en ningún paso,
DEBE limitar `evals`
a `workflow_dispatch` con `secrets.ANTHROPIC_API_KEY`, DEBE hacer, en cada
uno de los cinco jobs, un `actions/checkout` del commit que ha disparado el
run, DEBE no declarar `if:` en ningún job ni en ninguno de los pasos que
ejecutan esos comandos, y DEBE no contener `||` ni `if !` en ningún comando,
porque tanto una condición que no se cumple como un `|| echo` dejan la suite
y los linters de adorno sin que ningún `continue-on-error` lo delate.

#### Scenario: The tests job runs the canonical suite command
- **WHEN** se parsea el job `tests` de `.forgejo/workflows/ci.yml`
- **THEN** uno de sus comandos **termina** en
  `python3 -m unittest discover -s tests -q`, sin argumentos añadidos detrás
  que puedan reducir lo que descubre

#### Scenario: The self-spec job runs the validator in strict mode
- **WHEN** se parsea el job `self-spec` de `.forgejo/workflows/ci.yml`
- **THEN** entre sus comandos figura
  `python3 scripts/validate.py --root . --strict --json`

#### Scenario: The self-spec job runs the charter linter in strict mode
- **WHEN** se parsea el job `self-spec` de `.forgejo/workflows/ci.yml`
- **THEN** entre sus comandos figura
  `python3 scripts/charter_lint.py --root . --strict --json`

#### Scenario: The coverage job runs the coverage tool
- **WHEN** se parsea el job `coverage` de `.forgejo/workflows/ci.yml`
- **THEN** entre sus comandos figura `python3 tools/coverage.py`

#### Scenario: The plugin-validate job validates the plugin structure
- **WHEN** se parsea el job `plugin-validate` de `.forgejo/workflows/ci.yml`
- **THEN** entre sus comandos figura `claude plugin validate . --strict`

#### Scenario: The workflow starts without anyone asking
- **WHEN** se parsea el bloque `on:` de `.forgejo/workflows/ci.yml`
- **THEN** declara `push` y `pull_request` sobre `main`, además de
  `workflow_dispatch`

#### Scenario: Only two jobs carry a safety net
- **WHEN** se parsean los cinco jobs de `.forgejo/workflows/ci.yml`
- **THEN** los jobs que declaran `continue-on-error: true` son exactamente
  `coverage` y `plugin-validate`

#### Scenario: No job is switched off
- **WHEN** se parsean los cinco jobs de `.forgejo/workflows/ci.yml`
- **THEN** ninguno declara `if:`, salvo `evals`, cuyo `if:` es justo lo que
  lo limita a `workflow_dispatch`

#### Scenario: No job depends on the manual one
- **WHEN** se parsean las dependencias de `tests`, `self-spec`, `coverage` y
  `plugin-validate`
- **THEN** ninguno declara `needs` sobre `evals`, que al estar limitado a
  `workflow_dispatch` los saltaría a todos en cada `push` y cada
  `pull_request`

#### Scenario: No step is switched off by a condition
- **WHEN** se parsean los pasos que ejecutan los comandos de `tests`,
  `self-spec`, `coverage` y `plugin-validate`
- **THEN** ninguno declara `if:`, de modo que no se puede apagar la suite
  dejando el job encendido

#### Scenario: No step discards its own failure
- **WHEN** se parsean los pasos de los cinco jobs de
  `.forgejo/workflows/ci.yml`
- **THEN** ninguno declara `continue-on-error`, que a nivel de paso dejaría
  la suite en rojo con el job en verde

#### Scenario: The evals job is manual
- **WHEN** se parsea el job `evals` de `.forgejo/workflows/ci.yml`
- **THEN** declara una condición que lo limita a `workflow_dispatch`

#### Scenario: The evals job declares the API key
- **WHEN** se parsea el job `evals` de `.forgejo/workflows/ci.yml`
- **THEN** declara `secrets.ANTHROPIC_API_KEY`

#### Scenario: The API key never reaches the job that runs pull request code
- **WHEN** se busca `secrets.ANTHROPIC_API_KEY` en
  `.forgejo/workflows/ci.yml`
- **THEN** aparece sólo dentro del job `evals`, y nunca en un `env:` de
  nivel de workflow que heredaría `tests`, que ejecuta el código de cada
  pull request

#### Scenario: Every job checks out the commit under test
- **WHEN** se parsean los cinco jobs de `.forgejo/workflows/ci.yml`
- **THEN** cada uno declara un paso `uses: actions/checkout@`

#### Scenario: No command hides its own failure
- **WHEN** se parsean los comandos `run:` de los cinco jobs de
  `.forgejo/workflows/ci.yml`
- **THEN** ninguno contiene `||` ni `if !`, las dos construcciones con las
  que un comando en rojo puede dejar su job en verde

#### Scenario: No checkout pins a moving reference
- **WHEN** se parsean los pasos `actions/checkout` de
  `.forgejo/workflows/ci.yml`
- **THEN** ninguno declara `ref`, de modo que cada job toma el commit que
  disparó el run

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-016 · The gate is a command, not a workflow

WHEN alguien ejecuta `scripts/gate.py` sobre un proyecto que ha adoptado
Venoxia, el sistema DEBE correr **los scripts que viajan junto a `gate.py`**
—nunca los que encuentre bajo la raíz inspeccionada—: el acta en estricto, el
validador en estricto
sobre las specs de las capabilities y sobre los deltas de los changes en
`validated` o `verified`, y el oráculo de cada change en `verified`; DEBE
hacer las tres siempre, sin pararse en la primera que falle ni en el primer
change cuyo oráculo salga rojo, dejar que los tres escriban su propia salida,
y decir, **una vez terminados los tres y como última cosa que escribe**, si ha
mirado el acta, cuántos `spec.md`, cuántos changes y cuántos oráculos, y qué
changes en `validated` ha dejado sin ejecutar; DEBE terminar con `1` si cualquiera de los tres no pasa, con `2` si el
uso es incorrecto, si la configuración del oráculo no sirve, o si alguna de
las tres comprobaciones no se puede llevar a cabo, y con `0` sólo cuando las
tres se han hecho y las tres pasan; y DEBE invocar el oráculo sin `--dry-run`
y sin `--record`.

La puerta es **fail-closed**, y en eso es lo contrario del guardián: aquél es
fail-open a propósito, porque un guardián que se cae no puede impedir
trabajar; ésta no puede aprobar lo que no ha llegado a comprobar. Un `0` sólo
significa algo si es imposible obtenerlo por accidente.

De ahí una **excepción declarada a la convención del núcleo**. Los otros
scripts tratan «este proyecto no ha adoptado Venoxia» como un aviso y salen
con `0`: son herramientas que uno puede lanzar sobre cualquier árbol. La
puerta no. A la puerta se la invoca sobre un proyecto del que se afirma que
cumple, así que un `.venoxia/` ausente es una comprobación que no se ha
podido hacer —`2`—, no un permiso. Con `0`, un `--root` mal escrito o un
checkout a medias darían verde sin correr ni el acta, ni el validador, ni un
solo test, y el aviso no lo salva: nadie lee la salida de un job en verde.

Cada cosa entra en la puerta cuando deja de estar roja por diseño. Un change
en `specified` tiene `V07`/`V08` en rojo porque el test todavía no existe, y
uno en `validated` tiene el oráculo en rojo porque el código todavía no está:
las dos son etapas normales del flujo, y hacerlas gatear bloquearía la rama
principal justo mientras se trabaja. Por eso el delta entra al llegar a
`validated` y el oráculo al llegar a `verified`.

La frontera, declarada: la puerta **lee el árbol de trabajo, así que no puede
ver lo que se ha quitado de él, ni desconfiar de los ficheros por los que se
guía**. `change.json` dice qué estado tiene cada change y `venoxia.json` con
qué comando se ejecutan los tests: pasar un change a `archived` saca su
oráculo de la puerta, poner `true` como `test_command` la deja en verde sin
ejecutar una prueba, y borrar el directorio entero de un change —o
`.venoxia/capabilities/`— la deja sin nada que mirar ahí. Nada de eso lo
detecta un programa que sólo ve el árbol resultante; lo que sostiene esas
transiciones es la revisión del commit que las introduce, y por eso la puerta
dice al terminar cuánto ha mirado: un verde sobre cero capabilities y cero
changes se distingue a simple vista de un verde de verdad. Lo que sí cierra,
y por eso se enuncia con ese alcance, es la asimetría **dentro de un
directorio que existe**: ahí borrar un fichero no sale más barato que
corromperlo.

Y la otra frontera, la que más conviene no disimular: el oráculo se ejecuta
por change, porque `oracle.py` sólo sabe apuntar a uno, y sólo gatean los que
están en `verified`. Un proyecto que nunca promueve deja sus requisitos en
tierra de nadie: el guardián ya abrió la puerta al código en `validated`, el
test
existe y está en rojo, y esos requisitos no pasan a ninguna capability, así
que nada los ejecuta. La puerta no puede distinguir «todavía no he escrito el
código» de «no pienso promoverlo nunca» —son el mismo estado en el disco—,
pero sí puede dejar de callarlo: por eso nombra en su resumen los changes en
`validated` que no ha ejecutado, en la pasada verde y en la roja.

Sobre ese resumen, una precisión que importa: el `test_command` del proyecto
hereda la salida estándar, así que puede imprimir un texto idéntico al del
resumen. Por eso el resumen se escribe **al final**, cuando los tres han
terminado. Lo que lo identifica es esa posición, no su redacción; quien lea el
log tiene que mirar el último bloque, no buscar una frase. En un proyecto maduro
todos los changes acaban en `archived` —es el estado final normal—, así que la
puerta corre el acta, el validador y **cero oráculos**. Eso no deja los
requisitos sin comprobar: al archivarse pasan a la capability, donde `V06`,
`V07` y `V08` siguen exigiendo que cada uno declare su test, que el fichero
exista y que devuelva el `@covers`; quien los ejecuta es la suite del propio
proyecto. Pero la puerta no es el corredor de tests del proyecto, y el README
tiene que decirlo en vez de dejar que «verificar un proyecto» se entienda por
más de lo que es. Por lo mismo, el
coste crece con el número de changes en `verified`: quien no archive nunca
reejecutará su suite una vez por requisito acumulado, y la respuesta es
archivar, no que la puerta invente una caché o un límite que nadie ha
declarado.

#### Scenario: A project that passes the gate
- **WHEN** el acta y las specs cumplen y el oráculo de cada change `verified`
  termina en verde
- **THEN** el proceso termina con código `0`

#### Scenario: A specification that does not conform
- **WHEN** un requisito del proyecto omite `verifies:`
- **THEN** el proceso termina con código `1`

#### Scenario: A charter that does not conform
- **WHEN** el acta del proyecto incumple una de sus reglas
- **THEN** el proceso termina con código `1`

#### Scenario: A verified change with a red oracle
- **WHEN** el oráculo de un change en `verified` no termina en verde
- **THEN** el proceso termina con código `1`

#### Scenario: A validated change with a red oracle does not close the gate
- **WHEN** el oráculo de un change en `validated` no termina en verde, y todo
  lo demás pasa
- **THEN** el proceso termina con código `0`

#### Scenario: The oracle runs for real
- **WHEN** el oráculo de un change en `verified` termina en rojo
- **THEN** el proceso termina con `1`, porque la invocación no lleva
  `--dry-run`: con esa bandera el oráculo sólo lista comandos y siempre sale
  en verde

#### Scenario: The gate writes no evidence
- **WHEN** el oráculo de un change en `verified` con historial grabado termina
  en verde
- **THEN** el proceso termina con `0` y el `oracle.json` de ese change queda
  byte a byte como estaba, porque la invocación no lleva `--record`

#### Scenario: A specified change whose test does not exist yet passes
- **WHEN** un change en `specified` tiene un requisito cuyo `verifies:` apunta
  a un fichero que todavía no existe, y todo lo demás pasa
- **THEN** el proceso termina con `0`, porque su delta no entra en el
  validador hasta que el change llega a `validated`

#### Scenario: The gate runs its own scripts, not the inspected project's
- **WHEN** el proyecto inspeccionado versiona sus propios
  `scripts/charter_lint.py`, `scripts/validate.py` y `scripts/oracle.py`, que
  terminan con `0` sin comprobar nada
- **THEN** el proceso ejecuta los que están junto a `gate.py` y termina con
  `1` porque el acta del proyecto no cumple: resolverlos contra la raíz
  inspeccionada convertiría tres ficheros de tres líneas en un verde
  permanente, y además ejecutaría código del proyecto fuera del
  `test_command`, que es lo único que la advertencia cubre

#### Scenario: A check that cannot be carried out does not pass
- **WHEN** una de las tres comprobaciones no se puede llevar a cabo —el acta
  no se puede leer, falta uno de los scripts de Venoxia, o recorrer
  `.venoxia/changes/` lanza un error de E/S
- **THEN** el proceso termina con `2`, nunca con `0`: la puerta no aprueba lo
  que no ha llegado a comprobar

#### Scenario: The output of the three checks reaches whoever runs the gate
- **WHEN** el validador no pasa porque un requisito omite `verifies:`
- **THEN** el proceso termina con `1` y el código de la regla que ha saltado
  aparece en la salida estándar del comando, porque cada script escribe la
  suya sin que la puerta la capture ni la filtre, y un `1` mudo bloquea la
  rama sin decir qué falló

#### Scenario: The three checks all run even when the first one fails
- **WHEN** el acta no cumple y además un requisito omite `verifies:`
- **THEN** el proceso termina con `1` y en su salida aparecen los dos fallos,
  no sólo el primero: descubrir uno por pasada obliga a reejecutar la suite
  entera cada vez

#### Scenario: An active change with no requirement does not pass
- **WHEN** un change en `validated` o `verified` no tiene ningún fichero en su
  `delta/`, o los que tiene no declaran ni un requisito
- **THEN** el proceso termina con `1`: sin requisitos no hay nada que validar
  ni nada que ejecutar, y aprobarlo por vacuidad daría por verificado un
  change que no ha corrido una sola prueba

#### Scenario: A project with no charter cannot be gated
- **WHEN** el proyecto tiene `.venoxia/` pero no `.venoxia/charter.md`, o el
  acta no se puede leer
- **THEN** el proceso termina con `2` y escribe en la salida de error un
  mensaje que nombra `.venoxia/charter.md`: si sólo se reenviara el veredicto
  de `charter_lint.py`, un acta ausente dejaría una de las tres comprobaciones
  vacía y el verde resultante sería indistinguible de uno de verdad

#### Scenario: A capability spec with no requirement does not pass
- **WHEN** un `spec.md` de `.venoxia/capabilities/` no declara ni un requisito
- **THEN** el proceso termina con `1` y escribe en la salida de error un
  mensaje que lo nombra: vaciarlo saca de la verificación todos los requisitos
  de esa capability sin mover el recuento, y para los changes esa misma
  asimetría ya está cerrada

#### Scenario: A capability directory without a spec does not pass
- **WHEN** un directorio de `.venoxia/capabilities/` no contiene `spec.md`
- **THEN** el proceso termina con `1` y escribe en la salida de error un
  mensaje que nombra ese directorio: si sólo se validara lo que se encuentra,
  borrar un `spec.md` sacaría de la puerta todos los requisitos de esa
  capability mientras que corromperlo la tumbaría

#### Scenario: A change directory without change.json does not pass
- **WHEN** un directorio de `.venoxia/changes/` no contiene `change.json`
- **THEN** el proceso termina con `1` y escribe en la salida de error un
  mensaje que nombra ese directorio: dentro de un directorio que existe,
  borrar el fichero no puede salir más barato que corromperlo

#### Scenario: Every verified change's oracle runs
- **WHEN** dos changes en `verified` tienen el oráculo en rojo
- **THEN** el proceso termina con `1` y su salida nombra los dos, no sólo uno
  de ellos, porque descubrir un change rojo por pasada obliga a reejecutar la
  suite de todos los anteriores cada vez

#### Scenario: The summary comes last, after every subprocess
- **WHEN** el `test_command` del proyecto inspeccionado imprime por su cuenta
  un resumen falsificado
- **THEN** el resumen de la puerta sigue siendo el último de la salida, porque
  se escribe cuando los tres han terminado: compartiendo `stdout` con un
  comando ajeno, lo que identifica al resumen de verdad es su posición y no su
  redacción, que cualquiera puede copiar

#### Scenario: A passing gate says how much it looked at
- **WHEN** el proceso no encuentra ningún incumplimiento
- **THEN** termina con `0` y su salida dice que ha mirado el acta, y cuántos
  ficheros `spec.md`, cuántos changes y cuántos oráculos —ficheros, no
  directorios, o el recuento diría lo mismo antes y después de borrar uno—,
  para que un verde sobre un checkout a medias no se confunda con uno de
  verdad

#### Scenario: A failing gate says how much it looked at too
- **WHEN** el proceso encuentra un incumplimiento en el acta
- **THEN** termina con `1` y su salida trae ese mismo recuento: exigirlo sólo
  en la pasada verde es exigirlo en la única que nadie lee

#### Scenario: The gate names the validated changes it did not run
- **WHEN** el proyecto tiene un change en `validated` y todo lo demás pasa
- **THEN** el proceso termina con `0` y su resumen nombra ese change entre los
  que no ha ejecutado, porque quien nunca promueve a `verified` fusiona el
  código que el
  guardián le deja escribir en ese estado, sus requisitos no llegan nunca a
  una capability, y ninguna otra comprobación los ejecuta

#### Scenario: A mature project reports zero oracles
- **WHEN** todos los changes del proyecto están en `archived` y el acta y las
  specs pasan
- **THEN** el proceso termina con `0` y su resumen dice «0 oráculos»: es el
  resultado correcto y también el aviso de que ahí la puerta no ha ejecutado
  ninguna prueba

#### Scenario: Changes in other states are left alone
- **WHEN** el proyecto tiene un change en `draft` o en `specified` cuyo
  oráculo fallaría
- **THEN** el proceso termina con código `0`

#### Scenario: The state is read without regard to case or spacing
- **WHEN** el `state` de un change con el oráculo en rojo es `Verified` en vez
  de `verified`
- **THEN** el proceso termina con código `1`

#### Scenario: An unreadable change does not pass
- **WHEN** el `change.json` de un change no se puede leer, no es JSON válido,
  no trae `state`, o su `state` no es una cadena con uno de los cinco estados
  del ciclo de vida —`draft`, `specified`, `validated`, `verified`,
  `archived`— una vez normalizado
- **THEN** el proceso termina con código `1`, porque corromper el valor del
  estado no puede salir más barato que borrarlo

#### Scenario: The unreadable change is named
- **WHEN** el proceso falla por un `change.json` que no se puede leer
- **THEN** termina con `1` y escribe en la salida de error un mensaje que
  nombra ese change

#### Scenario: A project with no active change passes
- **WHEN** el proyecto no tiene ningún change en `verified`, todos sus
  `change.json` se leen bien, y el acta y las specs pasan
- **THEN** el proceso termina con código `0`

#### Scenario: A project with no active change is still checked
- **WHEN** el proyecto no tiene ningún change en `verified` y su acta no
  cumple
- **THEN** el proceso termina con `1`: no tener changes activos no exime de
  las otras dos comprobaciones, o la puerta sería un no-op verde para la
  mayoría de los proyectos

#### Scenario: A project without Venoxia cannot be gated
- **WHEN** el proyecto no tiene directorio `.venoxia/`
- **THEN** el proceso termina con código `2`, nombrando en su mensaje la raíz
  sobre la que ha mirado, porque un `--root` mal escrito, un checkout a medias
  o un borrado en el mismo commit no pueden dar verde

#### Scenario: An unusable oracle config is a usage error
- **WHEN** hay changes en `verified` y `.venoxia/venoxia.json` falta, no se
  puede leer, no es JSON válido, o no declara un `test_command` utilizable
- **THEN** el proceso termina con código `2`, porque si sólo se detectara la
  ausencia, corromper ese fichero saldría más barato que borrarlo: la puerta
  ejecutaría el oráculo con un comando vacío, no obtendría ningún rojo, y
  daría verde informando de N oráculos mirados

#### Scenario: The usage error names the unusable file
- **WHEN** el proceso falla porque la configuración del oráculo no sirve
- **THEN** termina con `2` y escribe en la salida de error un mensaje que
  nombra `.venoxia/venoxia.json`

verifies:   tests/test_gate.py
confidence: high
from:       README.md#verificar-un-proyecto

### R-CI-017 · No workflow template ships with the plugin

WHEN se recorre el árbol del repositorio, el sistema DEBE no contener ninguna
plantilla de workflow de CI, porque un fichero de workflow obliga a declarar
un runner, un checkout y una autenticación que son de quien lo copia y no de
Venoxia.

#### Scenario: The template directory is gone
- **WHEN** se busca el directorio `templates/ci/` en el repositorio
- **THEN** el directorio no existe

#### Scenario: No workflow file under templates
- **WHEN** se recorren recursivamente los ficheros de `templates/`
- **THEN** ninguno tiene extensión `.yml` ni `.yaml`

#### Scenario: No file under templates pins a runner
- **WHEN** se recorren recursivamente los ficheros de `templates/`
- **THEN** ninguno contiene `runs-on:`, se llame como se llame y esté o no
  dentro de un bloque de código: fijar un runner es justo la decisión que la
  plantilla no puede tomar por quien la copia

#### Scenario: No checkout or secret of a workflow ships in the repository
- **WHEN** se recorren los ficheros del repositorio fuera de las exclusiones
  declaradas más abajo
- **THEN** en ninguno aparece `actions/checkout` ni la expresión `secrets.`
  dentro de `${{ }}`: un workflow obliga a decidir el runner, el checkout y la
  autenticación, y prohibir sólo el primero deja publicar la mitad peligrosa
  —la que hace que la puerta ejecute el `test_command` del autor de un pull
  request con las credenciales del runner— a quien se limite a omitir la línea
  `runs-on:` que esta misma regla le empuja a quitar

#### Scenario: No workflow pinned to a runner ships in the repository
- **WHEN** se recorren los ficheros del repositorio fuera de las exclusiones
  declaradas más abajo
- **THEN** al leer el texto de cada uno de esos ficheros, en ninguno aparece
  la clave `runs-on` seguida de dos puntos —opcionalmente entre comillas
  simples o dobles, y con o sin espacios en blanco antes de los dos puntos—,
  sea cual sea la extensión del fichero y esté o no dentro de un bloque de
  código: acotarlo a `templates/`, a `.yml` o a la cadena literal lo esquiva
  quien mueve el contenido a `examples/venoxia-gate.workflow` o escribe
  `runs-on : …`

Los dos barridos son el repositorio entero menos una lista **cerrada** de
exclusiones, y no el conjunto publicado de `R-CI-018`. Acotarlo a lo publicado
reabriría la evasión que estas reglas existen para cerrar: `examples/` y la
raíz no están en esa lista, y ahí cabe el workflow completo.

Las exclusiones son de dos clases, y conviene no mezclarlas. Tres son las
cosas que **tienen** que nombrar un runner: `.forgejo/workflows/` —el CI de
este repositorio—, `tests/` —que comprueba su contenido— y `.venoxia/` —la
capability que lo especifica—. Las demás son ruido del árbol de trabajo que
nadie versiona ni publica: `.git/`, `.venv/`, `venv/`, `node_modules/`,
`__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `htmlcov/`, `coverage/` —lo
que deja `tools/coverage.py`— y los dos ficheros con los que se trabaja en
este repositorio, `TODO.md` y `CLAUDE.md`, que citan el workflow porque
documentan cómo se construye Venoxia. Sin esa segunda lista, un
fichero de una dependencia instalada con `runs-on:` dentro dejaría la suite en
rojo de forma permanente por algo que el repositorio ni siquiera contiene.

Y el límite, dicho: esto es una comprobación de texto, no un análisis de YAML.
Detecta el descuido y la copia, no al que quiera colar un workflow a
propósito; contra eso lo que hay es la revisión del commit.

verifies:   tests/test_gate.py
confidence: high
from:       README.md#verificar-un-proyecto

### R-CI-018 · The published documentation does not describe the internal CI

WHEN se lee la documentación que el plugin publica a quien lo instala —
`README.md`, `CONTRIBUTING.md`, `docs/**`, `skills/**`, `agents/**`,
`templates/**`, `scripts/**`, `hooks/**`, `.claude-plugin/**` **y el workflow
de CI**—, el sistema DEBE explicar cómo verificar un proyecto nombrando
`scripts/gate.py` y sus códigos de salida, DEBE advertir de que la puerta
ejecuta el `test_command` que declara el proyecto inspeccionado, y DEBE no
nombrar la forja interna de la organización, sus etiquetas de runner ni el
espejo de respaldo.

El workflow entra ahora en el barrido, y ésa es toda la diferencia con la
versión anterior de este requisito. Antes quedaba fuera con un argumento que
era cierto: un workflow **tiene** que decir en qué runner corre. Desde
`R-CI-008` lo dice leyendo una variable del repositorio, así que la excepción
ya no se sostiene y el fichero se mide como cualquier otro: comentarios
incluidos, que son lo primero que lee quien lo abre.

Lo que sigue fuera, y por qué: la capability que especifica el CI y el acta
que apuesta por él viven bajo `.venoxia/`, que es el registro de cómo se
construye Venoxia y no lo que Venoxia hace. Y una precisión incómoda que
conviene no tapar: **una lista de términos prohibidos publica lo que
prohíbe**. Los tres que quedan viven en un solo sitio, el test que los mantiene
fuera de todo lo demás; quitarlos de ahí es quitar el cable trampa.

#### Scenario: The workflow is scanned like everything else
- **WHEN** se leen los ficheros de documentación publicada
- **THEN** el workflow de CI está entre ellos

#### Scenario: The workflow does not name the internal forge
- **WHEN** se lee el texto del workflow, comentarios incluidos
- **THEN** no aparece el nombre de la forja interna en ninguna combinación de
  mayúsculas y minúsculas

#### Scenario: The workflow does not name the internal runner labels
- **WHEN** se lee el texto del workflow, comentarios incluidos
- **THEN** no aparece ninguna de las dos etiquetas del runner interno

verifies:   tests/test_gate.py
confidence: high
from:       README.md#verificar-un-proyecto

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
