# Capability: oracle

## Purpose

Ejecuta el oráculo que cada requisito de un change declara en `verifies:`
—con el `test_command` del proyecto o con el runner con nombre que el
requisito elija— y atribuye el resultado, `green`, `red`, `missing` o
`timeout`, al requisito exacto que lo declaró, dejando en `oracle.json` el
historial que acredita el ciclo rojo→verde. Determinista y sin modelo: lo que
`/venoxia:verify` presenta es lo que este script calcula, y `V17`/`V18` lo
auditan después leyendo el disco.

## Requirements

### R-ORC-001 · A change with every requirement green passes

WHEN se ejecuta `oracle.py --change <ID>` sobre un change cuyos requisitos
tienen todos su `verifies:` en verde, el sistema DEBE terminar con código `0`
y responder con `all_green: true` y `counts.total` igual al número de
requisitos del change.

#### Scenario: Three requirements, three green tests
- **WHEN** un change tiene tres requisitos y el `test_command` sale con
  código `0` para los tres
- **THEN** el proceso termina con código `0`, `all_green` es `true` y
  `counts.total` vale `3`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-002 · A red requirement is named, not just counted

WHEN el `test_command` de un requisito termina con código distinto de `0`,
el sistema DEBE marcar ese requisito como `red` con su `exit_code`, dejar los
demás requisitos con el estado que les corresponda y terminar con código `1`,
sin que el JSON deje de decir **cuál** de los requisitos falló.

#### Scenario: One red among three
- **WHEN** un requisito de tres sale con código `1` y los otros dos con
  código `0`
- **THEN** el proceso termina con código `1`, `all_green` es `false`, el
  requisito que falló aparece con `status: red` y `exit_code: 1`, y los otros
  dos aparecen con `status: green`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-003 · A missing oracle file is not invoked

WHEN el fichero que declara `verifies:` de un requisito no existe en disco,
el sistema DEBE marcar ese requisito como `missing`, no debe invocar el
`test_command` para él, y el proceso DEBE terminar con código `1`.

#### Scenario: verifies points to a file that was never written
- **WHEN** la ruta de `verifies:` de un requisito no existe
- **THEN** ese requisito queda con `status: missing`, el runner no se llama
  para él y el proceso termina con código `1`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-004 · A runner that outlives the timeout does not hang the oracle

WHILE el `test_command` de un requisito sigue en marcha más allá de
`--timeout`, el sistema DEBE terminar esa ejecución, marcar el requisito como
`timeout`, seguir con el resto de requisitos y responder sin ningún
«Traceback» en la salida de error.

#### Scenario: A runner that sleeps past the limit
- **WHEN** el `test_command` de un requisito tarda más que `--timeout 1`
- **THEN** ese requisito queda con `status: timeout` y el proceso termina con
  código `1`

#### Scenario: No traceback after a timeout
- **WHEN** el `test_command` de un requisito tarda más que `--timeout 1`
- **THEN** `stderr` no contiene «Traceback»

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-005 · No config, no {files}, no guessing

WHEN falta `.venoxia/venoxia.json`, o su `test_command` no contiene el
marcador `{files}`, el sistema DEBE terminar con código `2` y un mensaje en
español que nombra el fichero o el marcador que falta y enseña un ejemplo de
contenido válido, sin ejecutar ningún runner.

#### Scenario: The project never wrote venoxia.json
- **WHEN** no existe `.venoxia/venoxia.json`
- **THEN** el proceso termina con código `2` y el mensaje nombra ese fichero
  y enseña un ejemplo de su contenido

#### Scenario: test_command forgot the placeholder
- **WHEN** `test_command` no contiene `{files}`
- **THEN** el proceso termina con código `2` y el mensaje nombra el marcador
  `{files}`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-006 · Dry run shows the command and touches nothing

WHERE se invoca con `--dry-run`, el sistema DEBE imprimir, para cada
requisito, el `test_command` ya sustituido por sus rutas de `verifies:`, y no
DEBE invocar el runner para ninguno.

#### Scenario: Dry run over a change with two requirements
- **WHEN** se ejecuta `oracle.py --change <ID> --dry-run`
- **THEN** se imprime un comando por requisito y el proceso termina con
  código `0` sin que el runner se haya invocado ni una vez

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-007 · The history accumulates and survives a corrupt file

WHEN se invoca con `--record`, el sistema DEBE añadir la ejecución a
`.venoxia/changes/<ID>/oracle.json` conservando como mucho los últimos 50
runs en orden cronológico, y WHEN ese fichero ya existe pero su contenido no
es JSON válido, el sistema DEBE sustituirlo por un historial nuevo avisando
por `stderr`, sin ningún «Traceback».

#### Scenario: Two runs in a row
- **WHEN** se ejecuta `--record` dos veces seguidas
- **THEN** `oracle.json` contiene dos runs

#### Scenario: The history file is corrupt
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON y se
  ejecuta `--record`
- **THEN** `oracle.json` queda con un único run, el actual

#### Scenario: A corrupt history warns without a traceback
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON y se
  ejecuta `--record`
- **THEN** `stderr` recibe un aviso y ningún «Traceback»

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-008 · The JSON schema is stable and one call covers every path

WHEN `oracle.py` responde con `--json`, el sistema DEBE mantener exactamente
las claves de primer nivel `version`, `change`, `ran_at`, `runner`,
`results`, `counts`, `all_green` y `all_red`, y WHEN un requisito declara más
de una ruta en `verifies:`, el sistema DEBE pasarlas todas al mismo
`test_command` en una sola invocación.

#### Scenario: The top-level keys never change
- **WHEN** se pide `--json` sobre cualquier change
- **THEN** el conjunto de claves de primer nivel del documento es exactamente
  el del esquema, ni una de más ni una de menos

#### Scenario: Two paths, one invocation
- **WHEN** un requisito declara dos rutas separadas por coma en `verifies:`
- **THEN** el runner se invoca una sola vez para ese requisito y recibe las
  dos rutas

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-009 · The verify skill exists with its tool contract

WHEN se busca `skills/verify/SKILL.md` en el plugin, el sistema DEBE tener un
fichero con frontmatter `name: verify`, una `description` que dispara con
«verifica el cambio», «graba el rojo», «pasa el oráculo», «¿está en verde?»
y «corre los tests de la spec», y un `allowed-tools` que declara `Read`,
`Glob`, `Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" *)` y `Write`,
sin ningún `Bash` genérico.

#### Scenario: Frontmatter and tool contract read from disk
- **WHEN** se parsea el frontmatter de `skills/verify/SKILL.md`
- **THEN** `name` vale `verify`, la `description` contiene las cinco frases
  disparadoras y `allowed-tools` es exactamente esas cuatro entradas

verifies:   tests/test_verify_skill.py
confidence: high
from:       README.md#el-ciclo-de-vida-de-un-change-y-quien-escribe-cada-estado

### R-ORC-010 · Verified only follows a prior red run or an explicit confirmation

WHEN el oráculo de un change en `validated` queda todo en verde, el sistema
DEBE escribir `"state": "verified"` en `change.json`, sin tocar ninguna otra
clave, sólo si el historial de `oracle.json` trae, para cada requisito del
delta, un run anterior en `red` o `missing`; y WHEN algún requisito no tiene
ningún run anterior en rojo, el sistema NO DEBE escribir `verified` sin
preguntar antes al usuario si vio fallar el test y recibir su confirmación
explícita.

#### Scenario: A green run backed by a documented red run
- **WHEN** el oráculo queda todo en verde y, para cada requisito del delta,
  algún run anterior de `oracle.json` lo trae en `red` o `missing`
- **THEN** `change.json` pasa a `"state": "verified"`

#### Scenario: A green run with no red run in the history
- **WHEN** el oráculo queda todo en verde y algún requisito del delta no
  tiene ningún run anterior en `red` ni en `missing`
- **THEN** la skill pregunta al usuario si vio fallar el test de ese
  requisito, sin escribir nada en `change.json`

#### Scenario: The user confirms the test was seen failing
- **WHEN** el usuario contesta que sí vio fallar el test
- **THEN** `change.json` pasa a `"state": "verified"`

#### Scenario: The user does not confirm
- **WHEN** el usuario contesta que no vio fallar el test, o no contesta
- **THEN** `change.json` no cambia

#### Scenario: A red run never writes verified
- **WHEN** el oráculo deja algún requisito en `red`, `missing` o `timeout`
- **THEN** `change.json` no cambia, sea cual sea su `state`

verifies:   tests/test_verify_skill.py
confidence: high
from:       README.md#el-ciclo-de-vida-de-un-change-y-quien-escribe-cada-estado

### R-ORC-011 · Dry run and record are mutually exclusive

IF se invoca `oracle.py` con `--dry-run` y `--record` a la vez, THEN el
sistema DEBE terminar con código `2` antes de invocar el runner y antes de
escribir o crear ningún fichero bajo el directorio del change.

#### Scenario: Both flags in one invocation
- **WHEN** se ejecuta `oracle.py --change <ID> --dry-run --record`
- **THEN** el proceso termina con código `2`

#### Scenario: Nothing is written under both flags
- **WHEN** se ejecuta `oracle.py --change <ID> --dry-run --record` sobre un
  change sin `oracle.json`
- **THEN** el proceso termina con código `2` y el directorio del change no
  gana ningún fichero

#### Scenario: The usage error names both flags
- **WHEN** se ejecuta `oracle.py --change <ID> --dry-run --record`
- **THEN** el proceso termina con código `2` y `stderr` recibe un aviso que
  nombra `--dry-run` y `--record`

#### Scenario: An existing history is left intact
- **WHEN** se ejecuta `oracle.py --change <ID> --dry-run --record` sobre un
  change cuyo `oracle.json` ya existe
- **THEN** el proceso termina con código `2` y `oracle.json` conserva su
  contenido byte a byte

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-012 · A corrupt history is copied aside before it is replaced

WHEN se invoca con `--record` y `oracle.json` existe pero no es JSON válido
o no trae una lista `runs`, el sistema DEBE escribir los bytes originales
completos en una copia `oracle.json.corrupt-<marca>` junto a él —con un sufijo
numérico tras la marca si ese nombre ya existe— y sólo después de que la copia
contenga esos bytes escribir el historial nuevo; cuando la copia no se puede
escribir, el historial no se sustituye, `stderr` recibe un aviso que dice que
el run no se ha grabado y el proceso termina con código `2`.

#### Scenario: The original bytes survive in the copy
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON y se
  ejecuta `--record` con el `test_command` en verde
- **THEN** el proceso termina con código `0` y existe un fichero
  `oracle.json.corrupt-<marca>` con el contenido original byte a byte

#### Scenario: The warning names the copy
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON y se
  ejecuta `--record` con el `test_command` en verde
- **THEN** el proceso termina con código `0` y el aviso de `stderr` nombra la
  ruta de la copia

#### Scenario: No history, no copy
- **WHEN** `oracle.json` no existe y se ejecuta `--record` con el
  `test_command` en verde
- **THEN** el proceso termina con código `0` y el directorio del change gana
  sólo `oracle.json`

#### Scenario: A copy that cannot be written keeps the original in place
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON, se ejecuta
  `--record` y la copia no se puede escribir
- **THEN** el proceso termina con código `2` y `oracle.json` conserva su
  contenido original byte a byte

#### Scenario: A failed copy is reported as a run that was not recorded
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON, se ejecuta
  `--record` y la copia no se puede escribir
- **THEN** el proceso termina con código `2` y `stderr` recibe un aviso que
  dice que el run no se ha grabado

#### Scenario: A run that could not be recorded is not a verdict
- **WHEN** `oracle.json` existe, no se puede interpretar como JSON, se ejecuta
  `--record` y la copia no se puede escribir
- **THEN** el proceso termina con código `2`

#### Scenario: A readable history with extra keys is not corrupt
- **WHEN** `oracle.json` es JSON válido, trae una lista `runs` y además una
  clave que el esquema no declara, y se ejecuta `--record` con el
  `test_command` en verde
- **THEN** el proceso termina con código `0` y el historial conserva sus runs
  anteriores más el actual, sin ninguna copia nueva

#### Scenario: A second corruption never overwrites the first copy
- **WHEN** `oracle.json` está corrupto, se ejecuta `--record` dos veces con la
  misma `<marca>` y el `test_command` en verde, y el fichero vuelve a estar
  corrupto entre las dos
- **THEN** cada invocación termina con código `0` y existen dos copias, la
  segunda con un sufijo numérico tras la marca

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo
