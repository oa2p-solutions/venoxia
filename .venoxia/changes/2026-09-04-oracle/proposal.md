# 2026-09-04-oracle Proposal

## Why

Hoy `validate.py` comprueba que cada requisito **declare** su oráculo con
`verifies:` y que el fichero exista, pero nadie ejecuta ese test ni atribuye
su resultado al requisito. Un requisito puede llevar semanas con `verifies:`
apuntando a un test que lleva el mismo tiempo en rojo, y nada en el sistema lo
dice: la disciplina de SDD se queda a medias si la mitad de TDD —correr el
test y anotar si pasa— sigue siendo manual y de memoria.

## What Changes

- Un nuevo comando, `scripts/oracle.py`, ejecuta el `test_command` que declara
  `.venoxia/venoxia.json` una vez por requisito de un change, sustituyendo el
  marcador `{files}` por las rutas de su `verifies:`.
- Cada requisito queda atribuido a exactamente un estado: `green`, `red`,
  `missing` (el fichero de `verifies:` no existe) o `timeout`.
- `--record` añade el resultado de la ejecución a
  `.venoxia/changes/<id>/oracle.json`, conservando como máximo los últimos 50
  runs en orden cronológico.
- `--dry-run` enseña el comando exacto que se ejecutaría por requisito sin
  invocar nada.
- Sin `.venoxia/venoxia.json`, o con un `test_command` que no trae `{files}`,
  el comando termina con un error de uso que dice qué falta y un ejemplo.

## Capabilities

### New Capabilities

- `oracle`: ejecución del `test_command` declarado por el proyecto y
  atribución de rojo/verde por requisito, con su historial en `oracle.json`.

### Modified Capabilities

Ninguna: `validate.py`, `charter_lint.py`, `diff_readings.py` y `guardian.py`
no cambian de comportamiento.

## Impact

- Los proyectos que adopten esta capability necesitan
  `.venoxia/venoxia.json` con su `test_command`; sin él, `oracle.py` es un
  error de uso y no un fallo silencioso.
- Ningún cambio en el esquema JSON versión 1 de `validate.py` ni de
  `diff_readings.py`: `oracle.py` estrena su propio esquema, también versión 1
  y también estable.
- El guardián no cambia: sigue sin ejecutar tests ni importar este módulo.
- `templates/venoxia.json` da a quien adopta Venoxia un punto de partida para
  su propio `test_command`.

## Confidence

- **El formato de `.venoxia/venoxia.json` (una clave `test_command` con un
  único marcador `{files}`, y `cwd` relativo a la raíz)** · `medium` · es la
  forma más simple que cubre un test runner por proyecto, pero no se ha
  probado todavía con un runner que necesite invocarse de otra manera; se
  revisa cuando el primer proyecto con un `test_command` distinto de
  `python3 -m unittest {files}` lo adopte.
- **Una invocación por requisito, nunca una sola invocación con todos los
  ficheros de `verifies:` del change** · `high` · es la única forma de poder
  atribuir el resultado a un requisito concreto en vez de a un lote; no hay
  otra manera de que `V07`/`V16` y `oracle.py` hablen del mismo requisito.
- **El resto de la propuesta** · `high` · comportamiento decidido y
  contrastado con el mismo criterio que ya usa `validate.py`: determinista,
  sin modelo, códigos 0/1/2.
