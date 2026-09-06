# Capability: ci

## Purpose

Hacer cumplible la tesis del plugin —«la spec falla en CI cuando miente»—
ejecutando en cada `push` la misma puerta que un desarrollador corre en
local: la suite, el validador y el acta en estricto, la cobertura y la
estructura del plugin. El CI del repositorio vive en Forgejo Actions sobre
el runner interno de la organización; `templates/ci/venoxia-gate.yml` es la
misma puerta empaquetada para un proyecto que adopta Venoxia.

## Requirements

### R-CI-008 · The Forgejo workflow declares the same triggers and jobs on the internal runner

WHEN se busca `.forgejo/workflows/ci.yml` en el repositorio, el sistema DEBE
tener un workflow que se dispare en `push` y `pull_request` sobre la rama
`main`, y también en `workflow_dispatch`, que declare los cinco jobs
`tests`, `self-spec`, `coverage`, `plugin-validate` y `evals`, y cuyos jobs
corran sólo sobre las etiquetas `oa2p-debian` u `oa2p-node` del runner
interno.

#### Scenario: Triggers read from disk
- **WHEN** se parsea `.forgejo/workflows/ci.yml`
- **THEN** declara `push` y `pull_request` acotados a `main`, y
  `workflow_dispatch`

#### Scenario: The five jobs by name
- **WHEN** se parsea `.forgejo/workflows/ci.yml`
- **THEN** declara los cinco jobs `tests`, `self-spec`, `coverage`,
  `plugin-validate` y `evals`

#### Scenario: Only the internal runner labels
- **WHEN** se parsea `.forgejo/workflows/ci.yml`
- **THEN** cada `runs-on` vale `oa2p-debian` u `oa2p-node`

verifies:   tests/test_forgejo_workflow.py
confidence: high
from:       README.md#verificar-en-ci

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

verifies:   tests/test_forgejo_workflow.py
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
