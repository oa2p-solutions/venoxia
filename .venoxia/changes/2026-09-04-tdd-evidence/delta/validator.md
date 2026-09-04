# validator Delta

## ADDED Requirements

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
