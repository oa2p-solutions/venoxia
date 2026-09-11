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

### R-VAL-006 · A verified change stands on a green oracle

WHEN el `change.json` de un change declara `state: verified`, el sistema
DEBE rechazar la especificación a menos que exista un `oracle.json` legible
para ese change cuyo último run tenga `all_green: true` y cuyo conjunto de
`requirement_id` cubra todos los IDs del delta del change, nombrando en el
hallazgo el primer requisito que no está en verde.

#### Scenario: Verified with a green run that covers every requirement
- **WHEN** el change está en `verified` y el último run de `oracle.json` es
  `all_green: true` y cubre todos los IDs del delta
- **THEN** `V17` no se dispara

#### Scenario: Verified with no oracle.json at all
- **WHEN** el change está en `verified` y no existe `oracle.json`
- **THEN** `V17` se dispara nombrando el change y el primer requisito de su
  delta

#### Scenario: Verified with a red run
- **WHEN** el último run grabado tiene al menos un requisito en `red`,
  `missing` o `timeout`
- **THEN** `V17` se dispara nombrando el primer requisito que no está en
  verde

#### Scenario: Verified with a green run that forgot a requirement
- **WHEN** el último run está en verde pero no incluye todos los
  `requirement_id` del delta del change
- **THEN** `V17` se dispara nombrando el ID que el run nunca vio

#### Scenario: A corrupt oracle.json does not crash the validator
- **WHEN** `oracle.json` existe y no se puede interpretar como JSON
- **THEN** `V17` se dispara con un mensaje que dice que el fichero no se
  pudo leer, sin ningún «Traceback» en la salida

verifies:   tests/test_rules_oracle.py
confidence: high
from:       README.md#las-18-reglas-del-validador

### R-VAL-007 · Green without red earns a warning

WHERE existe `oracle.json` para un change, el sistema DEBE avisar, por cada
requisito cuyo estado en el último run sea `green`, cuando ningún run
anterior de ese mismo change registre ese requisito en `red`.

#### Scenario: Red preceded the green
- **WHEN** un requisito está en rojo en un run y en verde en el siguiente
- **THEN** `V18` no se dispara para ese requisito

#### Scenario: The only run is already green
- **WHEN** el único run grabado de un requisito lo deja en verde
- **THEN** `V18` se dispara para ese requisito con severidad `warning`

#### Scenario: Every run has always been green
- **WHEN** todos los runs grabados de un requisito están en verde y ninguno
  estuvo nunca en rojo
- **THEN** `V18` se dispara para ese requisito

#### Scenario: One warning per requirement, never one per change
- **WHEN** un change tiene dos requisitos en verde y sólo uno de los dos
  pasó antes por rojo
- **THEN** `V18` se dispara una sola vez, nombrando el requisito que nunca
  estuvo en rojo

verifies:   tests/test_rules_oracle.py
confidence: high
from:       README.md#las-18-reglas-del-validador
