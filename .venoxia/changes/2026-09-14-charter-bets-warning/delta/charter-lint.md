# charter-lint Delta

## ADDED Requirements

### R-CHL-008 · C20 warns about a charter that declares no bet

WHEN un acta declara su sección de apuestas y no escribe ninguna dentro, el sistema
DEBE marcar el hallazgo `C20` sobre esa sección, salvo que alguna capability declare
riesgo alto.

#### Scenario: A charter without a single bet
- **WHEN** ninguna capability declara riesgo alto y la sección de apuestas está vacía
- **THEN** salta `C20` sobre la línea de la sección de apuestas

#### Scenario: A high risk row keeps its own warning
- **WHEN** alguna capability declara riesgo alto y la sección de apuestas está vacía
- **THEN** no salta `C20`

#### Scenario: One bet is enough
- **WHEN** la sección de apuestas declara al menos una apuesta
- **THEN** no salta `C20`

verifies:   tests/test_charter_lint.py
confidence: medium
  why:      que el aviso ceda ante «C15» es una decisión de ruido, no un hecho
  revisit:  cuando alguien reciba el aviso sobre un acta suya y diga si le sobró o le faltó información
from:       .venoxia/changes/2026-09-14-charter-bets-warning/proposal.md
