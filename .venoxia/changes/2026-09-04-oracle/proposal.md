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

## Pendiente

Resuelto el 2026-09-07. La divergencia del 2026-09-05 (cuatro rondas, 6 duras
en la última, ninguna un desacuerdo de comportamiento) no convergía por un
defecto del motor, no del delta: `diff_readings.py` contaba como dura cada
colateral que el otro lector no recogía aunque no lo contradijera. El change
`2026-09-06-divergence-additive` lo arregló. Con el motor corregido, las
lecturas de aquella ronda ya daban 0 duras; se despachó un panel nuevo (dos
lectores y abogado) sobre el mismo delta y salió con **0 duras, 17 blandas y
0 lagunas** sobre 13 escenarios. Las 17 blandas son paráfrasis del mismo
efecto con los mismos códigos de salida en los dos lectores; el validador y
la divergencia salieron los dos con `0` y el change pasó a `validated`.

El oráculo se volvió a grabar el mismo día (`ran_at` 2026-09-07T14:13:45Z):
8 en verde, y el historial acredita el rojo previo de cada requisito, así que
el change pasa a `verified`.

El abogado del diablo dejó seis ataques, cinco `high`. Contrastados con el
código que ya existe: `R-ORC-008` (inyección por `verifies:`) está cerrado
porque `oracle.py` entrecomilla con `shlex.quote` y ejecuta con
`shell=False`; `R-ORC-001` (delta vacío como verde) está cerrado porque
`all_green` exige `total > 0`. Quedan abiertos, y anotados en la Fase 13 del
cuaderno: `--dry-run` combinado con `--record` graba un run sin ejecutar
nada; el historial corrupto se sustituye sin copia previa; el `test_command`
sólo se comprueba por la presencia de `{files}`; y el timeout por requisito
no tiene cota agregada. Ninguno bloquea el estado: el abogado no cuenta para
el código de salida.
