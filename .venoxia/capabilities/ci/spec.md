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
