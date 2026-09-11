# oracle Delta

## ADDED Requirements

### R-ORC-017 · A confirmed green is recorded next to the run

WHEN se invoca `oracle.py --record --confirm-green <IDs>`, el sistema DEBE
anotar en el run que graba en `oracle.json` la lista `confirmed_green` con
esos IDs, sólo si cada uno de esos IDs pertenece al change y sale en `green`
en ese mismo run —cualquier otro estado (`red`, `missing` o `timeout`) es un
error de uso, código `2`, que no graba nada—, conservando las ocho claves de
primer nivel del documento JSON de salida.

#### Scenario: The confirmation lands in the recorded run
- **WHEN** se ejecuta `--record --confirm-green R-ORC-901` y `R-ORC-901` sale
  en verde en ese run
- **THEN** el último run de `oracle.json` trae `confirmed_green` igual a
  `["R-ORC-901"]`

#### Scenario: Several IDs separated by commas
- **WHEN** se ejecuta `--record --confirm-green R-ORC-901,R-ORC-902` y los dos
  salen en verde
- **THEN** el último run de `oracle.json` trae los dos IDs en `confirmed_green`

#### Scenario: The output keeps its eight top-level keys
- **WHEN** se ejecuta `--record --confirm-green R-ORC-901 --json`
- **THEN** las claves de primer nivel del documento son exactamente
  `version`, `change`, `ran_at`, `runner`, `results`, `counts`, `all_green` y
  `all_red`

#### Scenario: A run without the flag carries no confirmation
- **WHEN** se ejecuta `--record` sin `--confirm-green`
- **THEN** el último run de `oracle.json` no trae la clave `confirmed_green`

#### Scenario: An ID outside the change is a usage error
- **WHEN** se ejecuta `--record --confirm-green R-ORC-999` y ningún requisito
  del change tiene ese ID
- **THEN** el proceso termina con código `2`

#### Scenario: An ID outside the change records nothing
- **WHEN** se ejecuta `--record --confirm-green R-ORC-999` sobre un change sin
  `oracle.json` y ningún requisito del change tiene ese ID
- **THEN** el proceso termina con código `2` y el directorio del change no
  gana ningún fichero

#### Scenario: An ID that is not green in this run is a usage error
- **WHEN** se ejecuta `--record --confirm-green R-ORC-901` y `R-ORC-901` sale
  en `red`, `missing` o `timeout` en ese run
- **THEN** el proceso termina con código `2` y `oracle.json` no gana ningún run

#### Scenario: Confirming without recording is a usage error
- **WHEN** se ejecuta `--confirm-green R-ORC-901` sin `--record`
- **THEN** el proceso termina con código `2` y no se ejecuta ningún comando

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

## MODIFIED Requirements

### R-ORC-010 · Verified only follows a prior red run or a recorded confirmation

WHEN el oráculo de un change en `validated` queda todo en verde, el sistema
DEBE escribir `"state": "verified"` en `change.json`, sin tocar ninguna otra
clave, sólo si el historial de `oracle.json` trae, para cada requisito del
delta, un run anterior en `red` —`missing` y `timeout` no acreditan nada— o
una confirmación grabada con `--confirm-green`; y WHEN algún requisito no tiene ni lo uno ni lo otro, el
sistema NO DEBE escribir `verified` sin preguntar antes al usuario si vio
fallar el test, y con su confirmación explícita DEBE grabarla con
`--confirm-green` antes de escribir `verified`; la skill graba
`--confirm-green` sólo después de haber preguntado y únicamente con los IDs
que el usuario confirmó uno a uno, nunca como primera grabación del change.

#### Scenario: A green run backed by a documented red run
- **WHEN** el oráculo queda todo en verde y, para cada requisito del delta,
  algún run anterior de `oracle.json` lo trae en `red`
- **THEN** `change.json` pasa a `"state": "verified"`

#### Scenario: A prior missing run is not a prior red run
- **WHEN** el oráculo queda todo en verde y el único run anterior de un
  requisito lo trae en `missing`
- **THEN** la skill pregunta al usuario si vio fallar el test de ese
  requisito, sin escribir nada en `change.json`

#### Scenario: A green run with no red run in the history
- **WHEN** el oráculo queda todo en verde y algún requisito del delta no
  tiene ningún run anterior en `red` ni figura en `confirmed_green` de ningún
  run
- **THEN** la skill pregunta al usuario si vio fallar el test de ese
  requisito, sin escribir nada en `change.json`

#### Scenario: The user confirms and the confirmation is recorded
- **WHEN** el usuario contesta que sí vio fallar el test
- **THEN** la skill vuelve a grabar el oráculo con `--record --confirm-green`
  nombrando ese requisito

#### Scenario: The confirmation names only the IDs the user confirmed
- **WHEN** cinco requisitos están en verde sin rojo previo y el usuario
  confirma sólo uno de ellos
- **THEN** `--confirm-green` nombra únicamente ese requisito

#### Scenario: No confirmation is recorded before asking
- **WHEN** el oráculo queda todo en verde y la skill todavía no ha preguntado
  al usuario por ningún requisito
- **THEN** la skill no pasa `--confirm-green` en ninguna grabación

#### Scenario: The recorded confirmation unlocks verified
- **WHEN** el run grabado trae ese requisito en `confirmed_green` y todo sigue
  en verde
- **THEN** `change.json` pasa a `"state": "verified"`

#### Scenario: A confirmation already in the history is enough
- **WHEN** el oráculo queda todo en verde y el requisito sin rojo previo
  figura en `confirmed_green` de algún run anterior
- **THEN** `change.json` pasa a `"state": "verified"` sin volver a preguntar

#### Scenario: The user does not confirm
- **WHEN** el usuario contesta que no vio fallar el test, o no contesta
- **THEN** `change.json` no cambia

#### Scenario: A red run never writes verified
- **WHEN** el oráculo deja algún requisito en `red`, `missing` o `timeout`
- **THEN** `change.json` no cambia, sea cual sea su `state`

verifies:   tests/test_verify_skill.py
confidence: high
from:       README.md#el-ciclo-de-vida-de-un-change-y-quien-escribe-cada-estado
