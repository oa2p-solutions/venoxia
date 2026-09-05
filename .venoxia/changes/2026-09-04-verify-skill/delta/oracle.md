# oracle Delta

## ADDED Requirements

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
