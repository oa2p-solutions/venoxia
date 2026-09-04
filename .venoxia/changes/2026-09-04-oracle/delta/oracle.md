# oracle Delta

## ADDED Requirements

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
- **THEN** ese requisito queda con `status: timeout`, el proceso termina con
  código `1` y `stderr` no contiene «Traceback»

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
- **THEN** `oracle.json` tiene `version: 1` y dos runs, en el orden en que se
  ejecutaron

#### Scenario: The history file is corrupt
- **WHEN** `oracle.json` existe y no se puede interpretar como JSON
- **THEN** el tercer `--record` lo sustituye por un historial nuevo, avisa
  por `stderr` y no produce ningún «Traceback»

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
