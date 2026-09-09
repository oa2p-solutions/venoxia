# guardian Delta

## ADDED Requirements

### R-GRD-006 · A specified change backs writing the oracle it declares

WHEN el cambio activo declara `"state": "specified"`, el sistema DEBE
permitir la edición si la ruta editada es una de las que algún `verifies:`
de su `delta/` nombra, y denegarla en cualquier otro caso.

#### Scenario: The path the delta declares as its oracle
- **WHEN** el cambio activo está en «specified» y su delta declara «verifies: tests/test_x.py»
- **THEN** la decisión sobre «tests/test_x.py» es «allow» y la razón menciona «specified» y «verifies»

#### Scenario: A test-shaped path that nobody declared
- **WHEN** el cambio activo está en «specified» y ningún «verifies:» de su delta nombra «tests/test_otro.py»
- **THEN** la decisión sobre «tests/test_otro.py» es «deny»

#### Scenario: Production code with that same change
- **WHEN** el cambio activo está en «specified» y ningún «verifies:» de su delta nombra «src/a.py»
- **THEN** la decisión sobre «src/a.py» es «deny»

verifies:   tests/test_guardian.py
confidence: medium
  why:      se abre la puerta por el vínculo que el delta declara y no por la forma de la ruta; la alternativa de reconocer lo que parezca un test es más barata y no tiene nada en la spec que la respalde
from:       2026-09-08-vision-conversacion.md#cierre

### R-GRD-007 · The deny of a specified change names the file to write

WHEN el guardián deniega una edición y el cambio activo está en
`"state": "specified"`, el sistema DEBE nombrar en la razón las rutas que los
`verifies:` de su `delta/` declaran, como lo siguiente que hay que escribir, y
ofrecer «/venoxia:validate» y «/venoxia:diverge» como los comandos que
desbloquean, en lugar de «/venoxia:specify».

#### Scenario: The deny names the declared oracle
- **WHEN** se deniega «src/a.py» con el cambio activo en «specified» y su delta declarando «verifies: tests/test_x.py»
- **THEN** la razón nombra «tests/test_x.py», ofrece «/venoxia:validate» y «/venoxia:diverge», y no nombra «/venoxia:specify»

#### Scenario: Nothing declared, the generic remedy stands
- **WHEN** se deniega «src/a.py» con el cambio activo en «specified» y ningún «verifies:» en su delta
- **THEN** la razón mantiene el remedio genérico con «/venoxia:specify»

verifies:   tests/test_guardian.py
confidence: high
from:       2026-09-08-vision-conversacion.md#cierre
