# 2026-09-06-single-ci Proposal

## Why

La organización ha decidido llevar todo a la forja interna: GitHub deja de usarse
para este proyecto. Hoy el repo mantiene dos CI que dicen lo mismo
(`.github/workflows/ci.yml` y `.forgejo/workflows/ci.yml`), y el segundo
está escrito **como espejo del primero**: `tests/test_ci_workflow.py`
compara comando a comando los dos ficheros. Esa forma de comprobar deja de
tener sentido en cuanto uno de los dos desaparece, porque la referencia
contra la que se mide es justamente lo que se retira. Y el único CI que ha
llegado a ejecutarse de verdad es el de la forja interna: el de GitHub nunca pasó de
`queued`.

Mantener el de GitHub sin ejecutarlo sería peor que no tenerlo: un fichero
que promete una puerta que nadie abre. Y la plantilla del consumidor
(`templates/ci/venoxia-gate.yml`) apunta a `oa2p-solutions/venoxia` con un
token de GitHub, así que un proyecto que la copiara hoy haría checkout de un
repositorio que ya no es la fuente.

## What Changes

- `.github/workflows/ci.yml` deja de existir. `.forgejo/workflows/ci.yml` es
  el único CI del repositorio, y el repo no declara ningún workflow de
  GitHub Actions.
- El contrato del workflow de la forja interna pasa a enunciarse **en absoluto**, no
  por paridad: los comandos exactos de cada job, `continue-on-error` sólo en
  `coverage` y `plugin-validate`, `evals` limitado a `workflow_dispatch` con
  `secrets.ANTHROPIC_API_KEY`, y `actions/checkout` en todos los jobs. Lo que
  antes se comprobaba comparando dos ficheros se comprueba ahora leyendo uno.
- `templates/ci/venoxia-gate.yml` pasa a la forja interna: se copia a
  `.forgejo/workflows/venoxia-gate.yml` en el proyecto consumidor, hace
  checkout de `OA2P/venoxia` fijado a un tag, corre sobre la etiqueta
  `CI_RUNNER` dentro de la imagen `python:3.14-slim`, y sigue sin `pip` en
  ningún paso. No queda ninguna plantilla para GitHub Actions.
- `tests/test_ci_workflow.py` se retira y su contenido vivo se reparte:
  `tests/test_ci_workflow.py` pasa a ser el contrato completo del CI
  del repo, y `tests/test_ci_template.py` (nuevo) el de la plantilla del
  consumidor y el de la sección del README.
- `README.md`, `CLAUDE.md` y los manifiestos del plugin
  (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) dejan de
  nombrar GitHub como origen o como CI.
- Las apuestas `B-003` y `B-004` del acta cambian de testigo: el run real
  que las resuelve es el de la forja interna, no el de GitHub Actions.

## New Capabilities

Ninguna.

## Modified Capabilities

- `ci`: pierde el workflow de GitHub Actions y la plantilla de consumidor
  para GitHub. Queda un único CI, el de la forja interna, con su contrato enunciado
  sin depender de ningún fichero espejo.

## Impact

- Ningún cambio en `scripts/`, en el guardián, en el oráculo ni en el
  esquema JSON versión 1.
- Las cifras de los cinco fixtures de `evals/` no cambian: ninguno tiene
  workflows.
- `R-CI-006` y `R-CI-007` ya no existían (salieron del delta en la
  divergencia del 2026-09-05 y viven como apuestas `B-003`/`B-004`), así que
  este change no los toca.
- Un proyecto consumidor que ya hubiera copiado la plantilla de GitHub
  seguirá funcionando mientras el espejo de GitHub exista, pero deja de
  estar soportada: la plantilla que se mantiene es la de la forja interna.
- El expresión `github.event_name` del job `evals` **se conserva**: es el
  nombre del contexto de expresión que la forja interna implementa por
  compatibilidad, no una dependencia de GitHub, y es el que han usado los
  runs reales que sí han corrido.

## Confidence

- **Que retirar `.github/workflows/ci.yml` no deje ningún hueco de
  cobertura** · `high` · lo que comprobaba `test_ci_workflow.py` sobre los
  jobs (`self-spec` con sus dos comandos exactos, `plugin-validate` con la
  instalación del CLI, `evals` manual con la API key) pasa entero a
  `test_ci_workflow.py` contra el fichero que sí se ejecuta.
- **La forma estructural del workflow y de la plantilla**
  (`R-CI-011`…`R-CI-015`) · `high` · se comprueba por parseo estático, sin
  red y sin lanzar ningún workflow.
- **Que la plantilla de la forja interna funcione tal cual en un proyecto
  consumidor** · no es un requisito de este delta: ningún test puede
  comprobarlo sin un proyecto consumidor real con su secret. Se declara
  aquí y no se convierte en requisito, por la misma razón por la que
  `R-CI-006` y `R-CI-007` salieron del delta anterior: lo que no puede
  comprobar un test no es un requisito, es una suposición.

## Pendiente

Divergencia pasada en **ocho rondas** con lectores nuevos cada vez. Las
rondas 3 y 4 no convergían por un defecto del motor, no del delta: los dos
lectores coincidían en el comportamiento y `diff_readings.py` contaba como
dura cada diferencia de granularidad en `side_effects`. Eso se arregló en
`2026-09-06-divergence-additive`, y la ronda 5 salió con 0 duras sobre el
mismo delta con más escenarios que nunca. La ronda 8 cierra con 0 duras, 10
blandas y 0 lagunas sobre 47 escenarios.

El abogado del diablo dejó **23 ataques en ocho rondas y ninguno fue ruido**.
Los que cambiaron el contrato están en el delta; éstos se quedan fuera y se
anotan aquí:

- **La puerta del consumidor se desactiva editando metadatos.** Un proyecto
  que cambie el `state` de sus changes a `specified`, o que borre
  `.venoxia/changes/`, pasa la puerta sin ejecutar ningún oráculo. Se cerró
  lo que se podía —un `change.json` ilegible o sin `state` sí falla, y el
  estado se compara normalizado, así que `"Verified"` no cuela—, pero un
  repositorio que decide no declarar ningún change no se distingue de uno que
  todavía no tiene ninguno. Cerrarlo del todo exige que la puerta sepa qué
  debería haber, y eso es otro problema.
- **`set +e` o un `exit 0` detrás del comando.** El delta prohíbe `||` e
  `if !`, que es lo que se puede comprobar parseando el YAML. Un bloque
  `run: |` con varias líneas puede seguir enmascarando el fallo. Comprobarlo
  de verdad exige ejecutar el workflow, no leerlo.
- **La plantilla no instala dependencias.** Para un consumidor cuya suite las
  tenga, el oráculo falla por `ModuleNotFoundError` hasta que añada su propio
  paso. Documentado en la cabecera de la plantilla y en el README, con el
  sitio exacto donde va y la advertencia de no pasarle secretos.
- **`VENOXIA_REF=main` sigue siendo posible.** La plantilla exige que la
  variable esté definida y que no tenga valor de reserva, y pide un tag en su
  documentación, pero no rechaza un nombre de rama: distinguir un tag de una
  rama sin consultar al servidor no se puede.

Los cuatro comparten forma: son evasiones de un autor que **quiere** saltarse
su propia puerta, no errores de alguien que la escribe de buena fe. Contra el
primero, un contrato que se comprueba parseando YAML siempre tiene una
evasión más.

