# Capability: validator

## Purpose

Decide si una especificación de Venoxia (capabilities y deltas) cumple su
propio contrato, regla a regla, sin consultar a ningún modelo y con el mismo
veredicto en cada ejecución sobre el mismo árbol.

## Requirements

### R-VAL-001 · Exit code contract

WHEN alguien ejecuta `scripts/validate.py` sobre un proyecto con `.venoxia/`,
el sistema DEBE terminar con el código de salida que corresponde, siendo
`0` si la especificación cumple, `1` si no cumple y `2` si el uso del
propio CLI es incorrecto.

#### Scenario: Specification conforms
- **WHEN** el proyecto validado no dispara ningún hallazgo de error
- **THEN** el proceso termina con código `0` y dice en español que cumple el contrato

#### Scenario: Specification does not conform
- **WHEN** un requisito omite «verifies:»
- **THEN** el proceso termina con código `1` y dice en español que incumple el contrato

#### Scenario: Usage error
- **WHEN** la ruta que se pide validar no existe en disco
- **THEN** el proceso termina con código `2` y avisa por stderr, sin nada en stdout

verifies:   tests/test_rules_late.py
confidence: high
from:       README.md#las-16-reglas-del-validador

### R-VAL-002 · Stable JSON schema

WHEN se pide `--json`, el sistema DEBE responder con el documento de esquema
versión 1: `version`, `ok`, `strict`, `root`, `counts`, `findings` y
`budget`, y ninguna clave más en el primer nivel salvo las que añada
explícitamente quien invoque `build_payload`.

#### Scenario: The seven schema keys and no others
- **WHEN** se pide el JSON de un proyecto validado
- **THEN** las claves del primer nivel del documento son exactamente esas siete

verifies:   tests/test_report.py
confidence: high
from:       README.md#las-16-reglas-del-validador

### R-VAL-003 · A project without .venoxia/ does not block

WHEN se ejecuta `validate.py` sobre un proyecto que no tiene `.venoxia/`, el
sistema DEBE terminar con código `0` y decir en español que el proyecto
todavía no ha adoptado Venoxia, en vez de tratar la ausencia como un
incumplimiento.

#### Scenario: No .venoxia/ at all
- **WHEN** la raíz del proyecto no contiene ningún directorio `.venoxia/`
- **THEN** el proceso sale con `0` y el mensaje dice que no hay especificación que validar

verifies:   tests/test_rules_late.py
confidence: high
from:       README.md#las-16-reglas-del-validador

### R-VAL-004 · V06 requires a non-empty oracle

WHEN un requisito no declara «verifies:», o lo declara vacío, el sistema DEBE
marcar el hallazgo `V06` con un hint que enseñe la línea que falta y el
`@covers <ID>` que le corresponde.

#### Scenario: verifies is absent
- **WHEN** el requisito no trae la línea «verifies:»
- **THEN** salta `V06` sobre ese requisito con un hint accionable

#### Scenario: verifies is empty
- **WHEN** la línea «verifies:» está pero sin valor
- **THEN** salta `V06` y el mensaje dice que está vacío

verifies:   tests/test_rules_early.py
confidence: high
from:       README.md#las-16-reglas-del-validador

### R-VAL-005 · A clean project triggers no early rule

WHEN el proyecto canónico de Venoxia se valida sin tocar nada, el sistema
DEBE no disparar ninguna de las ocho reglas tempranas (`V01`–`V08`), ni
siquiera en modo `--strict`: es la base sobre la que se mide todo falso
positivo.

#### Scenario: The canonical project passes V01–V08 even under strict
- **WHEN** se valida el proyecto canónico con `--strict`
- **THEN** el conjunto de reglas disparadas está vacío y el proceso sale con `0`

verifies:   tests/test_rules_early.py
confidence: high
from:       README.md#las-16-reglas-del-validador
