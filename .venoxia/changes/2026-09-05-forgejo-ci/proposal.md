# 2026-09-05-forgejo-ci Proposal

## Why

El CI del plugin vive en `.github/workflows/ci.yml`, pero el primer run real
en GitHub Actions (`oa2p-solutions/venoxia`, 2026-09-05) se quedó en cola
más de veinte minutos sin que ningún runner lo recogiera y terminó
cancelado. Las apuestas `B-003` y `B-004` del acta siguen sin resolver
porque nunca llegó a ejecutarse nada. La organización tiene un Forgejo
interno (`forgejo.int.oa2p-solutions.com`) con Forgejo Actions activado y un
`forgejo-runner` registrado en `oa2p-server`, y el repo ya está espejado en
`OA2P/venoxia`. Un workflow allí es la forma de que el contrato «falla en CI
cuando miente» tenga por fin un testigo que corre.

## What Changes

- Existe `.forgejo/workflows/ci.yml`, con los mismos disparadores (`push` y
  `pull_request` sobre `main`, `workflow_dispatch`) y los mismos cinco jobs
  que el workflow de GitHub: `tests`, `self-spec`, `coverage`,
  `plugin-validate` y `evals`.
- Cada job corre sobre una de las dos etiquetas que el runner interno
  declara: `oa2p-debian` (Debian 13 slim) u `oa2p-node` (Node 22). No hay
  `ubuntu-latest` ni ninguna etiqueta que ese runner no conozca.
- El host del runner sólo tiene Python 3.14, así que el job `tests` no usa
  `actions/setup-python`: cada entrada de la matriz corre dentro de la
  imagen `python:<versión>-slim`, para 3.12, 3.13 y 3.14. Las imágenes
  `slim` no traen `git`, que `actions/checkout` necesita, y el job lo
  instala con `apt-get` antes del checkout.
- Los comandos `run:` de cada job son los mismos que en GitHub, y
  `coverage` y `plugin-validate` conservan su `continue-on-error: true` por
  las mismas razones que allí.
- Un test nuevo, `tests/test_forgejo_workflow.py`, parsea los dos workflows
  y comprueba que el de Forgejo declara lo anterior y que no se desvía del
  de GitHub en comandos ni en redes de seguridad.
- README gana un párrafo en «## Verificar en CI» que nombra el workflow de
  Forgejo y las dos etiquetas del runner.

## New Capabilities

Ninguna.

## Modified Capabilities

- `ci`: gana un segundo workflow, el de Forgejo Actions, que espeja al de
  GitHub sobre el runner interno.

## Impact

- Ningún cambio en scripts, en el guardián ni en el esquema JSON versión 1.
- El workflow de GitHub no cambia: si algún día su cola se mueve, los dos
  corren lo mismo.
- Las cifras de los cinco fixtures de `evals/` no cambian.

## Confidence

- **Que `actions/checkout@v4` funcione dentro de `python:*-slim` una vez
  instalado `git`, y que el runner inyecte `node` en ese contenedor** ·
  `medium` · es el comportamiento documentado de `forgejo-runner` (hereda
  la inyección de `node` de `act`), pero no se ha visto correr en este
  runner concreto · se revisa con el primer run real en Forgejo.
- **Que `npm install -g @anthropic-ai/claude-code` y `claude plugin
  validate` funcionen en `node:22-bookworm` sin sesión** · apuesta `B-004`
  del acta, que este workflow por fin puede resolver · mitigado con
  `continue-on-error: true`.
- **La forma estructural del workflow y su paridad con el de GitHub**
  (`R-CI-008`…`R-CI-010`) · `high` · se comprueba íntegramente por parseo
  estático en `tests/test_forgejo_workflow.py`.

## Cierre

Divergencia pasada el 2026-09-05 desde la sesión principal, a la primera:
0 duras, 1 blanda, 0 lagunas sobre 9 escenarios. La blanda («sólo corre
por workflow_dispatch» frente a «condiciona su ejecución a
workflow_dispatch») es vocabulario, no lectura distinta. El abogado del
diablo dejó dos ataques sobre `R-CI-010` y los dos entraron en el test:
«mismas redes de seguridad» se comprueba como igualdad del conjunto de jobs
con `continue-on-error` entre los dos workflows (no como superconjunto), y
cada job de Forgejo tiene que hacer `actions/checkout` para no correr sobre
el árbol que dejó el run anterior. `validate.py` en verde y `oracle.json`
con el rojo (los tres requisitos, antes de que existiera el fichero) y el
verde del mismo día: `verified`.

Lo que sigue sin comprobarse en local es el run real en Forgejo Actions:
que el runner inyecte `node` en `python:*-slim`, que `actions/checkout@v4`
funcione con el `git` instalado por `apt-get`, y `B-003`/`B-004`.
