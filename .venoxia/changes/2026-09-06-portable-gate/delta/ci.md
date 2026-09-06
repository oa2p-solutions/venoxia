# ci Delta

## ADDED Requirements

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
`templates/**`, `scripts/**`, `hooks/**` y `.claude-plugin/**`—, el
sistema DEBE explicar cómo verificar un proyecto nombrando `scripts/gate.py` y
sus códigos de salida, DEBE advertir de que la puerta ejecuta el
`test_command` que declara el proyecto inspeccionado, y DEBE no nombrar la
forja interna de la organización, sus etiquetas de runner ni el espejo de
respaldo, porque cómo se ejecutan el respaldo y las pruebas internas no es de
interés para quien instala el plugin.

Y como toda comprobación por lista, ésta es un cable trampa contra el
descuido —el párrafo que se queda pegado de una sesión anterior—, y no una
censura. Quien quiera describir la infraestructura interna con otras palabras
puede hacerlo, y lo que lo impide es la revisión del commit. Añadir un término a la
lista cuando aparezca un escape real es el mantenimiento previsto, no un
parche.

El alcance es ese conjunto y no «el repositorio entero», y conviene no
venderlo por más: `.forgejo/workflows/ci.yml` **tiene** que nombrar sus
etiquetas de runner —es el CI de verdad, y sin ellas no arranca—, igual que
la capability que lo especifica, el acta que apuesta por él y los ficheros con
los que se trabaja en este repositorio, `CLAUDE.md` y `TODO.md`. Ésos
describen cómo se construye Venoxia, no qué hace Venoxia, y quien los abre ya
está mirando el taller y no el producto. Lo que la regla impide es que esa
información viaje dentro del plugin como si fuera documentación de producto,
y que baste mover un párrafo del README a otro fichero **de ese conjunto**
para esquivarla. Por eso el alcance son las skills y los agentes **enteros**,
no sólo sus `SKILL.md`, y por eso incluye `scripts/`, `hooks/` y
`.claude-plugin/`: un fichero hermano dentro de la misma skill se instala
exactamente igual, y el `--help` o el docstring de `gate.py` —el comando que
el README manda ejecutar— llega a cada instalador tal cual. Dejar la regla a
un directorio de distancia es no ponerla.

La advertencia no es adorno: al dejar de ser un workflow, la puerta ya no
trae `persist-credentials: false` ni un paso sin secretos: quien la meta en su
CI sobre código de un fork estará ejecutando comandos del autor del pull
request con las credenciales del runner, y sólo puede evitarlo si lo sabe.

#### Scenario: The README names the gate command
- **WHEN** se lee `README.md`
- **THEN** nombra `scripts/gate.py`

#### Scenario: The README explains the exit codes
- **WHEN** se lee `README.md`
- **THEN** explica los tres códigos con los que termina el comando: `0` si el
   proyecto pasa la puerta, `1` si no la pasa, y `2` si el uso es incorrecto o
   si la puerta no ha podido comprobar —diciendo que `2` bloquea igual que
   `1`, porque leerlo como «error mío de invocación» deja pasar justo el
   `--root` mal escrito y el checkout a medias que el diseño fail-closed
   existe para detener

#### Scenario: The gate warns about it in its own help
- **WHEN** se ejecuta `scripts/gate.py --help`
- **THEN** su texto dice que el comando ejecuta el `test_command` del proyecto
  inspeccionado y que no debe correr con secretos en su entorno sobre código
  que no es de fiar: quien pega el comando en un job disparado por pull
  requests de un fork lee el `--help`, no el README

#### Scenario: The README warns that the gate runs the project's tests
- **WHEN** se lee la sección «## Verificar un proyecto» de `README.md`
- **THEN** dice que el comando ejecuta el `test_command` del proyecto y que no
  debe correr con secretos en su entorno sobre código que no es de fiar

#### Scenario: The README says what the gate does not run
- **WHEN** se lee la sección «## Verificar un proyecto» de `README.md`
- **THEN** dice que el oráculo cubre los changes en `verified` y que los
  requisitos ya archivados en las capabilities los ejecuta la suite del propio
  proyecto, para que «verificar un proyecto» no se entienda por más de lo que
  la puerta hace

#### Scenario: The published documentation does not name the internal forge
- **WHEN** se leen los ficheros de documentación publicada
- **THEN** en ninguno aparece `forgejo` en ninguna combinación de mayúsculas y
  minúsculas

#### Scenario: The published documentation does not name the internal runner labels
- **WHEN** se leen los ficheros de documentación publicada
- **THEN** en ninguno aparece `oa2p-debian`, `oa2p-node`, el dominio interno
  `oa2p-solutions.com` —a secas, no sólo con un subdominio delante— ni el
  puerto `2222` de su acceso por SSH, en ninguna combinación de mayúsculas y
  minúsculas

#### Scenario: The published documentation does not name the backup mirror
- **WHEN** se leen los ficheros de documentación publicada
- **THEN** en ninguno aparece ninguna de las expresiones «repositorio de
  respaldo», «espejo de respaldo», «respaldo interno» ni «copia de seguridad»,
  en cualquier combinación de mayúsculas y minúsculas

verifies:   tests/test_gate.py
confidence: high
from:       README.md#verificar-un-proyecto
