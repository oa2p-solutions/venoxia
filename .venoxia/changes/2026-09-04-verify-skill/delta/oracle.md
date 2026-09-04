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

WHEN `oracle.py --record` termina con código `0` sobre un change en
`validated`, el sistema DEBE escribir `"state": "verified"` sólo si el
historial de `oracle.json` trae, para cada requisito del delta, un run
anterior en `red` o `missing`; y WHEN no hay ningún run anterior en rojo, el
sistema NO DEBE escribir `verified` sin que el usuario confirme
explícitamente haber visto fallar el test, presentando antes el aviso de
«verde sin rojo».

#### Scenario: A green run backed by a documented red run
- **WHEN** el último run está en verde y un run anterior del mismo
  requisito quedó en `red` o `missing`
- **THEN** la skill cambia únicamente la clave `state` a `verified` y lo dice

#### Scenario: A green run with no red run in the history
- **WHEN** el único run que existe está en verde
- **THEN** la skill no escribe `verified`, presenta el aviso de «verde sin
  rojo» y pregunta si el test se ha visto fallar; sólo escribe `verified`
  tras una confirmación explícita, y lo deja dicho en la entrega

verifies:   tests/test_verify_skill.py
confidence: high
from:       README.md#el-ciclo-de-vida-de-un-change-y-quien-escribe-cada-estado
