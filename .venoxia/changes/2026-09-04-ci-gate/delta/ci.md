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
plugin validate . --strict`; y WHEN el job `evals` se ejecuta, el sistema
DEBE limitarse a `workflow_dispatch`, exigir `secrets.ANTHROPIC_API_KEY` y
correr el comando de `evals/README.md`.

#### Scenario: plugin-validate installs before validating
- **WHEN** se parsea el job `plugin-validate`
- **THEN** un paso instala el paquete del CLI con `npm install` antes de
  correr `claude plugin validate . --strict`

#### Scenario: evals only runs by hand and needs the API key
- **WHEN** se parsea el job `evals`
- **THEN** su condición es `github.event_name == 'workflow_dispatch'`,
  declara `secrets.ANTHROPIC_API_KEY` y ejecuta `claude plugin eval venoxia`

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-004 · The consumer gate template pins Venoxia and skips pip

WHEN un proyecto consumidor usa `templates/ci/venoxia-gate.yml`, el sistema
DEBE hacer checkout del proyecto y de `oa2p-solutions/venoxia` a una
referencia fija (`VENOXIA_REF`) en un directorio auxiliar, usando
`secrets.VENOXIA_TOKEN` porque el repositorio es privado, y correr
`charter_lint.py --strict` y `validate.py --strict` sobre el proyecto
consumidor sin invocar `pip` en ningún paso.

#### Scenario: Pinned checkout and the two strict gates
- **WHEN** se parsea `templates/ci/venoxia-gate.yml`
- **THEN** declara el checkout fijado por referencia con el token de
  secrets, y sus pasos corren `charter_lint.py` y `validate.py` en
  `--strict` sin ningún `pip install`

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
  termina con código distinto de `0` y el job se marca en rojo

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-en-ci

### R-CI-006 · The declared Python matrix actually passes on real GitHub Actions runners

WHEN el job `tests` corre de verdad sobre los runners de GitHub Actions, el
sistema DEBE completar en verde la suite en las tres versiones declaradas
(3.12, 3.13 y 3.14), no sólo declararlas en la matriz.

#### Scenario: The three matrix legs go green on a real run
- **WHEN** se dispara un run real de `ci.yml` en GitHub Actions
- **THEN** los tres trabajos de la matriz de `tests` (3.12, 3.13 y 3.14)
  terminan en verde

verifies:   tests/test_ci_workflow.py
confidence: low
  why:      esta sesión no puede disparar un run real de GitHub Actions
            (ninguna acción remota) ni tiene instalado Python 3.12 en esta
            máquina; sólo se ha confirmado que la suite pasa aquí con 3.13
            y 3.14, y que el intérprete que corre esta comprobación es uno
            de los tres declarados
  revisit:  cuando exista el primer run real de la matriz en GitHub Actions
from:       README.md#verificar-en-ci

### R-CI-007 · plugin-validate's continue-on-error is confirmed necessary on a clean runner

WHEN el job `plugin-validate` corre en un runner de GitHub Actions sin
ninguna sesión de Claude Code autenticada de antemano, el sistema DEBE
completar `claude plugin validate . --strict` sin credenciales
adicionales; y si el CLI las exige, el `continue-on-error: true` del job
DEBE seguir evitando que ese fallo bloquee el resto del workflow.

#### Scenario: The safety net exists while the credential question is open
- **WHEN** se parsea el job `plugin-validate`
- **THEN** declara `continue-on-error: true`, así que aunque el CLI exija
  credenciales en un runner limpio, el resto de `ci.yml` no se bloquea

verifies:   tests/test_ci_workflow.py
confidence: low
  why:      esta máquina ya tiene una sesión de Claude Code autenticada, así
            que no se puede comprobar aquí si `claude plugin validate`
            exige credenciales en un runner limpio de GitHub Actions; el
            `continue-on-error` es la mitigación mientras esa pregunta siga
            abierta
  revisit:  cuando exista un run real de este job en un runner limpio de
            GitHub Actions
from:       README.md#verificar-en-ci
