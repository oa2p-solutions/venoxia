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

- **Que `claude plugin validate` no exija credenciales en un runner limpio
  de GitHub Actions** · apuesta `B-004` del acta, no un requisito: ningún
  test puede comprobarlo, así que tras la divergencia salió del delta y
  vive en `## Bets` de `.venoxia/charter.md` con su `revisit` · mitigado con
  `continue-on-error: true` mientras tanto, y ese `continue-on-error` sí es
  parte del requisito `R-CI-003`.
- **El job `coverage` se marca `continue-on-error`** · `medium` · los dos
  huecos que le impiden salir en verde (`guardian.py` al 0 %, `oracle.py`
  al 81,3 %) ya están documentados en `TODO.md` como conocidos y no
  atribuibles a este change; convertirlos en un rojo permanente del repo no
  añade información nueva · se revisa cuando `tools/coverage.py --init` se
  vuelva a ejecutar tras cerrar cualquiera de los dos huecos.
- **Que la matriz declarada (3.12, 3.13, 3.14) pase de verdad en GitHub
  Actions** · apuesta `B-003` del acta, no un requisito, por la misma razón:
  el intérprete 3.12 no está instalado en este entorno y ningún test local
  puede sustituir al run real; no se ha encontrado en el código ninguna
  sintaxis posterior a 3.12 y la suite sí se ha corrido en 3.13 y 3.14 · se
  revisa con el primer run real de la matriz en GitHub Actions.
- **El resto de la propuesta, incluida la forma estructural que declaran
  `ci.yml` y `venoxia-gate.yml`** (`R-CI-001`…`R-CI-005`) · `high` · los
  comandos, disparadores y nombres de job son literales del contrato ya
  escrito en `README.md`, `evals/README.md` y `TODO.md`, y se comprueban
  íntegramente por parseo estático (`tests/test_ci_workflow.py`); la única
  incertidumbre real —si lo declarado se sostiene en un run real— se movió
  primero a dos requisitos `low` (`R-CI-006`, `R-CI-007`) y, tras la
  divergencia, a las apuestas `B-003` y `B-004` del acta: lo que no puede
  comprobar ningún test no es un requisito, es una suposición.

## Cierre

Divergencia pasada el 2026-09-05 desde la sesión principal, en tres rondas.
Las dos primeras no convergieron por escenarios que juntaban varios hechos en
un mismo THEN (cada lector los repartía distinto entre `effect` y
`side_effects`) y por dos requisitos, `R-CI-006` y `R-CI-007`, que ningún
test puede comprobar: los dos lectores los declararon laguna. Salieron del
delta y son ahora las apuestas `B-003` y `B-004` del acta; los escenarios se
reescribieron con un hecho por escenario. La tercera ronda dio 0 duras, 2
blandas y 0 lagunas: `validated`, y con el rojo del 2026-09-04 en
`oracle.json` y el verde de hoy, `verified`.

Sigue sin poder comprobarse en local lo que exige un run real de GitHub
Actions: la matriz en 3.12 y la prueba negativa del `SHALL`. Son `B-003` y
la casilla abierta de la Fase 10 del `TODO.md`.
