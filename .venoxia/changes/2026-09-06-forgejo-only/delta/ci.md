# ci Delta

## ADDED Requirements

### R-CI-011 · The repository declares no GitHub Actions workflow

WHEN se recorre el árbol del repositorio, el sistema DEBE no contener
ningún fichero de workflow bajo `.github/workflows/`, porque el proyecto ha
dejado de usar GitHub y un workflow que nadie ejecuta promete una puerta que
no existe.

#### Scenario: No workflow directory for GitHub Actions
- **WHEN** se busca el directorio `.github/workflows/` en la raíz del
  repositorio
- **THEN** el directorio no existe

#### Scenario: The Forgejo workflow is the one on disk
- **WHEN** se busca `.forgejo/workflows/ci.yml` en la raíz del repositorio
- **THEN** el fichero existe

verifies:   tests/test_forgejo_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-012 · The Forgejo workflow states its commands and safety nets on its own

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

verifies:   tests/test_forgejo_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-013 · The consumer gate template targets Forgejo Actions

WHEN se parsea `templates/ci/venoxia-gate.yml`, el sistema DEBE hacer
checkout del repositorio `OA2P/venoxia` con `ref` tomado de la variable
`VENOXIA_REF` y sin ningún valor de reserva, DEBE dejar el job en fallo
cuando esa variable no está definida —una `ref` vacía toma la rama por
defecto, que es justo la rama en movimiento que se quiere evitar—, con
`secrets.VENOXIA_TOKEN`,
DEBE correr sobre la etiqueta `oa2p-debian` del runner interno, DEBE tomar
el intérprete de una imagen `python:3.14-slim` en vez de
`actions/setup-python`, DEBE ejecutar `charter_lint.py` y `validate.py` en
`--strict`, y DEBE no contener ningún paso de `pip install`.

#### Scenario: Checkout of a pinned Venoxia
- **WHEN** se parsea el paso de checkout de Venoxia de
  `templates/ci/venoxia-gate.yml`
- **THEN** hace checkout de `OA2P/venoxia` con `ref` tomado de
  `VENOXIA_REF` y `token` tomado de `secrets.VENOXIA_TOKEN`

#### Scenario: The pinned reference has no fallback
- **WHEN** se parsea el paso de checkout de Venoxia de
  `templates/ci/venoxia-gate.yml`
- **THEN** su `ref` no declara ningún valor de reserva

#### Scenario: The pinned reference is a tag, not a branch
- **WHEN** se lee el valor de ejemplo y la documentación de `VENOXIA_REF` en
  `templates/ci/venoxia-gate.yml`
- **THEN** piden un tag de Venoxia y advierten de que una rama deja la
  puerta del consumidor a merced de lo que cambie en Venoxia

#### Scenario: An undefined reference fails the job
- **WHEN** el proyecto consumidor no define `VENOXIA_REF`
- **THEN** la plantilla deja el job en fallo

#### Scenario: The failure names the missing variable
- **WHEN** la plantilla falla porque `VENOXIA_REF` no está definida
- **THEN** el mensaje nombra `VENOXIA_REF`

#### Scenario: The gate never falls back to the default branch
- **WHEN** `VENOXIA_REF` no está definida
- **THEN** el paso de checkout de Venoxia no llega a ejecutarse

#### Scenario: The internal runner label
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** cada `runs-on` vale `oa2p-debian`

#### Scenario: The interpreter comes from the image
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** declara `container` con la imagen `python:3.14-slim` y no usa
  `actions/setup-python`

#### Scenario: The two linters in strict mode
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** ejecuta `charter_lint.py` y `validate.py`, los dos con `--strict`

#### Scenario: No dependency installer
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** no aparece ningún `pip install`

verifies:   tests/test_ci_template.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-014 · The consumer gate template demands the oracle, never skips it

WHEN el proyecto consumidor pasa por la puerta, el sistema DEBE ejecutar una
invocación de `oracle.py --change <id>` por cada change cuyo `state` sea
`validated` o `verified`, DEBE dejar el job en fallo cuando alguno de esos
oráculos no termina en verde, DEBE dejar el job en fallo cuando
`.venoxia/venoxia.json` no existe, DEBE dejar el job en fallo cuando el
`change.json` de un change no se puede leer o no trae un `state`, DEBE
invocar el oráculo sin `--dry-run` para que el `test_command` se ejecute de
verdad, y DEBE no declarar `continue-on-error` en ningún job ni en ningún
paso, y DEBE ejecutar el oráculo sin `secrets.VENOXIA_TOKEN` en el entorno
de ese paso y sin que el checkout lo haya dejado escrito en el `.git/config`
del workspace de ninguno de sus checkouts, DEBE dispararse en `push` y en
`pull_request`, porque cualquier paso que se salta, que no ejecuta nada, que
sólo arranca a mano o cuyo fallo se descarta convierte borrar un fichero o
añadir una bandera en la forma de esquivar la puerta, y porque el `test_command` que ese paso ejecuta
lo declara el repositorio bajo prueba: dejarle el token al alcance convierte
un cambio de una línea en una fuga del secreto.

#### Scenario: One oracle invocation per gated change
- **WHEN** el paso recorre un change en `validated` o en `verified`
- **THEN** invoca `oracle.py --change <id>` para ese change

#### Scenario: The oracle actually runs the tests
- **WHEN** el paso invoca `oracle.py` para un change
- **THEN** lo hace sin `--dry-run`, de modo que el `test_command` se ejecuta
  de verdad en vez de sólo listarse

#### Scenario: Changes in other states are left alone
- **WHEN** el proyecto tiene un change en `draft` o en `specified`
- **THEN** el paso no lo invoca

#### Scenario: The state is read without regard to case or spacing
- **WHEN** el `state` de un change es `Verified` o `validated ` con espacios
- **THEN** el paso lo trata como el estado que nombra, porque cambiar una
  letra en un fichero de metadatos no puede ser la forma de esquivar la
  puerta

#### Scenario: A red oracle fails the job
- **WHEN** el oráculo de alguno de esos changes no termina en verde
- **THEN** el paso deja el job en fallo

#### Scenario: A missing project config fails the job
- **WHEN** el proyecto no tiene `.venoxia/venoxia.json`
- **THEN** el paso deja el job en fallo y nombra el fichero que falta

#### Scenario: An unreadable change fails the job
- **WHEN** el `change.json` de un change no se puede leer, no es JSON válido
  o no trae un `state`
- **THEN** el paso deja el job en fallo y nombra ese change, en vez de
  omitirlo en silencio

#### Scenario: A project with no active change passes
- **WHEN** el proyecto no tiene ningún change en `validated` ni en
  `verified`, y todos sus `change.json` se leen bien
- **THEN** el paso termina sin fallo

#### Scenario: The oracle step runs without the checkout token
- **WHEN** se parsea el paso que ejecuta el oráculo en
  `templates/ci/venoxia-gate.yml`
- **THEN** `secrets.VENOXIA_TOKEN` no aparece en su entorno, porque ese paso
  ejecuta el `test_command` que declara el repositorio bajo prueba y un
  cambio en esa línea bastaría para leerlo

#### Scenario: The token belongs to the checkout step alone
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** `secrets.VENOXIA_TOKEN` sólo aparece en el paso de checkout de
  Venoxia

#### Scenario: No checkout leaves a credential on disk
- **WHEN** se parsean **todos** los pasos `actions/checkout` de
  `templates/ci/venoxia-gate.yml`
- **THEN** cada uno declara `persist-credentials: false`, porque un checkout
  escribe la credencial en el `.git/config` del workspace y el paso que
  ejecuta el `test_command` del repositorio bajo prueba podría leerla de ahí
  aunque no esté en su entorno — vale tanto para el token de Venoxia como
  para el del propio consumidor, que además da permiso de escritura

#### Scenario: The gate runs on the events that gate a merge
- **WHEN** se parsea el bloque `on:` de `templates/ci/venoxia-gate.yml`
- **THEN** declara `push` y `pull_request`, porque una puerta que sólo
  arranca a mano no bloquea ninguna fusión

#### Scenario: No job or step discards its own failure
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** no aparece `continue-on-error` en ningún job ni en ningún paso,
  de modo que un oráculo en rojo deja el workflow del consumidor en rojo

verifies:   tests/test_ci_template.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-015 · The README describes one CI and one template

WHEN se lee la sección `## Verificar en CI` de `README.md`, el sistema DEBE
nombrar `.forgejo/workflows/ci.yml` como el único CI del repositorio, DEBE
nombrar las dos etiquetas `oa2p-debian` y `oa2p-node` del runner interno,
DEBE nombrar `templates/ci/venoxia-gate.yml` como la plantilla del
consumidor, DEBE explicar que `evals` sólo corre con `workflow_dispatch`, y
DEBE no nombrar `.github/workflows/ci.yml`.

#### Scenario: The section names the only workflow
- **WHEN** se lee la sección `## Verificar en CI` de `README.md`
- **THEN** nombra `.forgejo/workflows/ci.yml`

#### Scenario: The section names the runner labels
- **WHEN** se lee la sección `## Verificar en CI` de `README.md`
- **THEN** nombra `oa2p-debian` y `oa2p-node`

#### Scenario: The section names the consumer template
- **WHEN** se lee la sección `## Verificar en CI` de `README.md`
- **THEN** nombra `templates/ci/venoxia-gate.yml`

#### Scenario: The section explains the manual evals
- **WHEN** se lee la sección `## Verificar en CI` de `README.md`
- **THEN** nombra `workflow_dispatch`

#### Scenario: The section no longer names a GitHub workflow
- **WHEN** se lee la sección `## Verificar en CI` de `README.md`
- **THEN** no aparece `.github/workflows/ci.yml`

verifies:   tests/test_ci_template.py
confidence: high
from:       README.md#verificar-en-ci
