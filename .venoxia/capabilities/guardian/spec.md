# Capability: guardian

## Purpose

Decide, sobre el payload de un hook `PreToolUse`, si una edición de código de
producción se permite o se deniega, con una única garantía que ningún otro
script del proyecto tiene: siempre exactamente una decisión JSON por stdout y
código de salida `0`, pase lo que pase.

## Requirements

### R-GRD-001 · Exactly one decision, always exit zero

WHEN el guardián recibe cualquier payload, el sistema DEBE escribir por
stdout exactamente un documento `hookSpecificOutput` con `permissionDecision`
en `allow` o `deny`, y DEBE terminar siempre con código de salida `0`, sin
importar si el payload es válido, hostil o si el propio `change.json` está
corrupto.

#### Scenario: A well-formed decision
- **WHEN** se juzga una edición de código con un cambio validado al lado
- **THEN** stdout trae un único `hookSpecificOutput` con `hookEventName: PreToolUse` y una decisión válida

#### Scenario: A corrupt change still yields one decision
- **WHEN** el `change.json` del cambio activo es basura binaria
- **THEN** el proceso sale con `0`, imprime exactamente una línea de decisión y deja rastro en stderr

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián

### R-GRD-002 · No .venoxia/ never blocks

WHEN el proyecto no tiene ningún directorio `.venoxia/`, el sistema DEBE
permitir la edición: sin adopción de Venoxia, el guardián no tiene nada que
vigilar.

#### Scenario: The project has not adopted Venoxia
- **WHEN** se juzga una edición de código sin que exista `.venoxia/`
- **THEN** la decisión es «allow»

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián

### R-GRD-003 · Validated with a real delta allows; validated alone does not

WHEN el cambio activo declara `"state": "validated"`, el sistema DEBE
permitir la edición de código sólo si su `delta/` tiene al menos un fichero
`.md` no vacío que lo acredite, y denegarla en cualquier otro caso.

#### Scenario: Validated with its delta backs the edit
- **WHEN** el cambio activo está en «validated» y trae el delta de la capability
- **THEN** la decisión es «allow» y la razón menciona «validated»

#### Scenario: Validated without a delta does not back the edit
- **WHEN** el cambio activo dice «validated» pero no hay ningún delta que lo acredite
- **THEN** la decisión es «deny»

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián

### R-GRD-004 · Via direct allows and is logged

WHEN el cambio activo declara `"via": "direct"`, el sistema DEBE permitir la
edición y DEBE añadir una línea JSONL a `.venoxia/drift/direct.log` con
exactamente los campos `ts`, `change`, `tool` y `path`.

#### Scenario: Direct escape hatch allows
- **WHEN** el cambio activo declara «via: direct»
- **THEN** la decisión es «allow» y la razón menciona «direct»

#### Scenario: The drift log line carries the four contract fields
- **WHEN** una edición pasa por la vía «direct»
- **THEN** se añade una línea JSON con «ts», «change», «tool» y «path», y ninguna clave más

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián

### R-GRD-005 · A corrupt change.json denies; an I/O failure allows

WHEN el `change.json` del cambio activo no se puede usar tal cual está, el
sistema DEBE denegar la edición cuando el problema es que su contenido está
mal escrito, y DEBE permitirla y anotar `"note": "change-no-legible"` en el
diario de deriva cuando el problema fue no poder leerlo por un fallo de
entrada o salida.

#### Scenario: Corrupt content does not grant the edit
- **WHEN** el único `change.json` es basura binaria
- **THEN** la decisión es «deny»

#### Scenario: An I/O failure allows instead
- **WHEN** el `change.json` no se puede leer por un fallo de entrada/salida
- **THEN** la decisión es «allow» y sale con código `0`

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián
