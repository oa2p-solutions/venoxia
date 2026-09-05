# ci Delta

## ADDED Requirements

### R-CI-001 · The plugin workflow declares its triggers and its five jobs

WHEN se busca `.github/workflows/ci.yml` en el repositorio, el sistema DEBE
tener un workflow que se dispare en `push` y `pull_request` sobre la rama
`main`, y también en `workflow_dispatch`, y que declare los cinco jobs
`tests`, `self-spec`, `coverage`, `plugin-validate` y `evals`, con el job
`tests` cubriendo Python 3.12, 3.13 y 3.14.

#### Scenario: Triggers and job names read from disk
- **WHEN** se parsea `.github/workflows/ci.yml`
- **THEN** declara los tres disparadores acotados a `main` (salvo el manual)
  y los cinco jobs por su nombre, con la matriz de `tests` nombrando las
  tres versiones de Python

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-002 · The self-spec job proves the repo obeys its own validator and charter

WHEN el job `self-spec` de `.github/workflows/ci.yml` se ejecuta, el sistema
DEBE correr `python3 scripts/validate.py --root . --strict --json` y
`python3 scripts/charter_lint.py --root . --strict --json`, exigiendo código
de salida `0` en los dos.

#### Scenario: Both strict commands read from the job
- **WHEN** se parsea el job `self-spec`
- **THEN** sus pasos ejecutan exactamente esos dos comandos, con `--strict`
  y `--json` en ambos

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-003 · plugin-validate installs the CLI and evals stays manual

WHEN el job `plugin-validate` de `.github/workflows/ci.yml` se ejecuta, el
sistema DEBE instalar el CLI de Claude Code con `npm` y correr `claude
plugin validate . --strict`, con `continue-on-error: true` en el job porque
la apuesta `B-004` del acta (si el CLI exige credenciales en un runner
limpio) sigue abierta; y WHEN el job `evals` se ejecuta, el sistema DEBE
limitarse a `workflow_dispatch`, exigir `secrets.ANTHROPIC_API_KEY` y
correr el comando de `evals/README.md`.

#### Scenario: plugin-validate installs before validating
- **WHEN** se parsea el job `plugin-validate`
- **THEN** el paso que ejecuta `npm install` del CLI va antes del paso que
  ejecuta `claude plugin validate . --strict`

#### Scenario: plugin-validate does not block the workflow
- **WHEN** se parsea el job `plugin-validate`
- **THEN** el job declara `continue-on-error: true`

#### Scenario: evals only runs by hand
- **WHEN** se parsea el job `evals`
- **THEN** la condición del job es `github.event_name == 'workflow_dispatch'`

#### Scenario: evals needs the API key
- **WHEN** se parsea el job `evals`
- **THEN** el job referencia `secrets.ANTHROPIC_API_KEY`

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-004 · The consumer gate template pins Venoxia and skips pip

WHEN un proyecto consumidor usa `templates/ci/venoxia-gate.yml`, el sistema
DEBE hacer checkout del proyecto y de `oa2p-solutions/venoxia` a una
referencia fija (`VENOXIA_REF`) en un directorio auxiliar, usando
`secrets.VENOXIA_TOKEN` porque el repositorio es privado, y correr
`charter_lint.py --strict` y `validate.py --strict` sobre el proyecto
consumidor exigiendo código de salida `0` en los dos, sin invocar `pip` en
ningún paso.

#### Scenario: Pinned checkout of Venoxia
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** el checkout de `oa2p-solutions/venoxia` usa la referencia
  `VENOXIA_REF` y el token `secrets.VENOXIA_TOKEN`

#### Scenario: Two strict gates that can fail
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** los pasos que ejecutan `charter_lint.py --strict` y
  `validate.py --strict` no llevan `|| true` ni `continue-on-error`

#### Scenario: No pip anywhere
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** ningún paso ejecuta `pip`

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-005 · The consumer gate template runs the oracle over active changes

WHILE el proyecto consumidor declara `.venoxia/venoxia.json`, el sistema
DEBE ejecutar `oracle.py --change <id>` para cada change en estado
`validated` o `verified`, y el job DEBE fallar si alguna de esas ejecuciones
termina con código distinto de `0`.

#### Scenario: One change in verified with a red requirement fails the job
- **WHEN** existe `.venoxia/venoxia.json` y un change en `verified` cuyo
  oráculo ya no está todo en verde
- **THEN** el paso que corre `oracle.py --change <id>` sobre ese change
  termina con código `1`, el que `oracle.py` devuelve cuando algún requisito
  no está en verde, y el job se marca en rojo

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci
