# ci Delta

## ADDED Requirements

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

### R-CI-010 · The Forgejo workflow runs the same commands and safety nets as the GitHub one

WHEN se parsean `.github/workflows/ci.yml` y `.forgejo/workflows/ci.yml`, el
sistema DEBE tener, en cada job del workflow de Forgejo, todos los comandos
`run:` del job homónimo del workflow de GitHub, DEBE declarar
`continue-on-error: true` en `coverage` y en `plugin-validate`, y DEBE
mantener el job `evals` limitado a `workflow_dispatch` con
`secrets.ANTHROPIC_API_KEY`.

#### Scenario: Same commands per job
- **WHEN** se comparan los dos workflows job a job
- **THEN** cada comando `run:` de un job de GitHub aparece en el job
  homónimo de Forgejo

#### Scenario: Same safety nets
- **WHEN** se parsea `.forgejo/workflows/ci.yml`
- **THEN** los jobs `coverage` y `plugin-validate` declaran
  `continue-on-error: true`

#### Scenario: evals only runs by hand
- **WHEN** se parsea el job `evals` de `.forgejo/workflows/ci.yml`
- **THEN** la condición del job es `github.event_name == 'workflow_dispatch'`

#### Scenario: evals needs the API key
- **WHEN** se parsea el job `evals` de `.forgejo/workflows/ci.yml`
- **THEN** el job referencia `secrets.ANTHROPIC_API_KEY`

verifies:   tests/test_forgejo_workflow.py
confidence: high
from:       README.md#verificar-en-ci
