# oracle Delta

## ADDED Requirements

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
