# 2026-09-04-ci-gate Proposal

## Why

La frase central del README es «la spec deja de ser prosa y pasa a ser un
contrato que falla en CI cuando miente». Hasta hoy eso es una promesa sin
testigo: nada corre la suite, el validador ni el acta fuera del portátil de
quien los ejecuta a mano, y ningún proyecto que adopte Venoxia tiene una
plantilla de puerta para su propio CI. La tesis necesita un workflow que la
haga cumplible.

## What Changes

- Existe `.github/workflows/ci.yml`, el CI del propio plugin: se dispara en
  `push` y `pull_request` sobre `main`, y también a mano
  (`workflow_dispatch`).
- El job `tests` corre `python3 -m unittest discover -s tests -q` en una
  matriz de Python 3.12, 3.13 y 3.14.
- El job `self-spec` corre `python3 scripts/validate.py --root . --strict
  --json` y `python3 scripts/charter_lint.py --root . --strict --json`: el
  repo se valida contra su propio contrato.
- El job `coverage` corre `tools/coverage.py` (DEF-010); se marca
  `continue-on-error` porque hoy mide dos huecos ya documentados y aceptados
  en `TODO.md` (`scripts/guardian.py` al 0 % por el `os._exit` de su
  fail-open, `scripts/oracle.py` al 81,3 %), y el propio DEF-010 dejó dicho
  que la tabla debe seguir marcando «FALLA» como recordatorio, no
  convertirse en un semáforo rojo permanente del repo entero.
- El job `plugin-validate` instala el CLI de Claude Code con `npm` y corre
  `claude plugin validate . --strict`; se marca `continue-on-error` porque
  no se puede comprobar sin un run real de GitHub Actions si ese comando
  exige credenciales en un runner sin sesión previa.
- El job `evals` sólo corre con `workflow_dispatch`, exige
  `secrets.ANTHROPIC_API_KEY` y ejecuta el comando de `evals/README.md`:
  cuesta tokens y usa un LLM, así que no se dispara en cada `push`.
- Existe `templates/ci/venoxia-gate.yml`, la plantilla para un proyecto
  consumidor: hace checkout de sí mismo y de `oa2p-solutions/venoxia` fijado
  a una referencia (`VENOXIA_REF`) en un directorio auxiliar, con
  `secrets.VENOXIA_TOKEN` porque el repo es privado, y corre
  `charter_lint.py --strict` y `validate.py --strict` sin `pip`. Si el
  proyecto declara `.venoxia/venoxia.json`, además ejecuta `oracle.py
  --change <id>` por cada change en `validated` o `verified`, y cualquier
  código de salida distinto de `0` hace fallar el job.
- README gana la sección «## Verificar en CI» que explica los dos workflows
  y por qué `evals` es manual.

## New Capabilities

- `ci`: el contrato de integración continua del plugin (workflow propio,
  plantilla del consumidor y su documentación), hasta hoy inexistente.

## Modified Capabilities

Ninguna: `validate.py`, `charter_lint.py`, `oracle.py`, `guardian.py` y
`diff_readings.py` no cambian de comportamiento ni de esquema JSON.

## Impact

- Ningún cambio en la lógica de decisión, la latencia ni el fail-open de
  `scripts/guardian.py`.
- Ninguna clave existente del JSON versión 1 de `validate.py` ni de
  `diff_readings.py` cambia de nombre, tipo ni orden.
- Las cifras de los cinco fixtures de `evals/` no cambian: `self-spec` y
  `coverage` sólo leen y ejecutan lo que ya existe, no tocan `evals/`.
- No se crea ningún repositorio remoto, no se hace ningún `git push` desde
  esta sesión y no se publica ninguna release: eso sigue abierto (Fase 6 del
  `TODO.md`) y exige confirmación explícita del usuario.

## Confidence

- **El job `plugin-validate` se marca `continue-on-error`** · `low` · no se
  puede comprobar sin un run real en un runner de GitHub Actions si `claude
  plugin validate` exige credenciales fuera de una sesión interactiva; en
  este repositorio, con una sesión ya autenticada, el comando no las pide ·
  se revisa con el primer run real en GitHub Actions (el enlace queda
  pendiente, ver «## Pendiente»).
- **El job `coverage` se marca `continue-on-error`** · `medium` · los dos
  huecos que le impiden salir en verde (`guardian.py` al 0 %, `oracle.py`
  al 81,3 %) ya están documentados en `TODO.md` como conocidos y no
  atribuibles a este change; convertirlos en un rojo permanente del repo no
  añade información nueva · se revisa cuando `tools/coverage.py --init` se
  vuelva a ejecutar tras cerrar cualquiera de los dos huecos.
- **La matriz cubre 3.12, 3.13 y 3.14 sin haber podido probar 3.12 en esta
  máquina** · `low` · el intérprete 3.12 no está instalado en este entorno
  de desarrollo y no se ha instalado uno nuevo sólo para esta comprobación;
  no se ha encontrado en el código ninguna sintaxis posterior a 3.12 (sin
  `match`, sin `except*`, sin `tomllib`) y la suite sí se ha corrido en 3.13
  y 3.14 · se revisa con el primer run real de la matriz en GitHub Actions.
- **El resto de la propuesta** · `high` · los comandos y disparadores son
  literales del contrato ya escrito en `README.md`, `evals/README.md` y
  `TODO.md`; no hay apuesta de comportamiento nueva.

## Pendiente

Esta sesión no dispone de la herramienta para despachar los lectores de
`/venoxia:diverge`, así que este change se deja en `specified`, con
`oracle.json` grabando primero el rojo (antes de escribir `ci.yml`,
`templates/ci/venoxia-gate.yml` y la sección de `README.md`) y después el
verde, en ese orden. El paso a `validated` con `/venoxia:diverge` y a
`verified` con `/venoxia:verify` lo hace la sesión principal.

Además, dos partes del criterio de aceptación de `DEF-009` exigen un run
real en GitHub Actions que esta sesión tiene prohibido disparar (ninguna
acción remota, sin `git push`): (a) que la matriz de `tests` realmente pase
en 3.12/3.13/3.14 sobre los runners de GitHub, y (b) la prueba negativa de
empujar un `SHALL` en `.venoxia/capabilities/validator/spec.md` a una rama
y comprobar que `self-spec` falla por V14, con el enlace al run fallido
como evidencia. Ambas quedan como «no verificable en local»; la prueba
negativa se hizo en su forma local equivalente
(`python3 scripts/validate.py --root . --strict --json` sobre una copia con
el `SHALL` introducido y revertida a continuación) y confirmó que V14
dispara, pero eso no sustituye al run de GitHub Actions que el criterio
pide.
