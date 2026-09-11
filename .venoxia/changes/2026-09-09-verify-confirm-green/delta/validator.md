# validator Delta

## MODIFIED Requirements

### R-VAL-007 · Green without red earns a warning unless it was confirmed

WHERE existe `oracle.json` para un change, el sistema DEBE avisar, por cada
requisito cuyo estado en el último run sea `green`, cuando ningún run
anterior de ese mismo change registre ese requisito en `red` y ningún run del
historial lo traiga en su lista `confirmed_green`.

#### Scenario: Red preceded the green
- **WHEN** un requisito está en rojo en un run y en verde en el siguiente
- **THEN** `V18` no se dispara para ese requisito

#### Scenario: The only run is already green
- **WHEN** el único run grabado de un requisito lo deja en verde
- **THEN** `V18` se dispara para ese requisito con severidad `warning`

#### Scenario: Every run has always been green
- **WHEN** todos los runs grabados de un requisito están en verde y ninguno
  estuvo nunca en rojo
- **THEN** `V18` se dispara para ese requisito con severidad `warning`

#### Scenario: One warning per requirement, never one per change
- **WHEN** un change tiene dos requisitos en verde y sólo uno de los dos
  pasó antes por rojo
- **THEN** `V18` se dispara una sola vez, nombrando el requisito que nunca
  estuvo en rojo

#### Scenario: A confirmed green is silent
- **WHEN** un requisito está en verde en el último run, nunca estuvo en rojo y
  algún run del historial lo trae en `confirmed_green`
- **THEN** `V18` no se dispara para ese requisito

#### Scenario: A confirmation covers only the IDs it names
- **WHEN** dos requisitos están en verde sin rojo previo y sólo uno de los dos
  figura en `confirmed_green`
- **THEN** `V18` se dispara una sola vez, nombrando el que no está confirmado

#### Scenario: The confirmation may live in an earlier run
- **WHEN** el run que trae el requisito en `confirmed_green` no es el último y
  el último lo deja en verde
- **THEN** `V18` no se dispara para ese requisito

verifies:   tests/test_rules_oracle.py
confidence: high
from:       README.md#las-19-reglas-del-validador
