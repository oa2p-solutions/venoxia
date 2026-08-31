# Capability: inventory

## Purpose

El registro de existencias del almacén: cuántas unidades hay de cada referencia, quién
las ha movido y cuándo hay que reponer.

## Requirements

### R-INV-001 · Stock ledger entry for every movement

WHEN una referencia entra o sale del almacén, el sistema anota el movimiento en el libro
de existencias con la cantidad, el motivo y el instante en que ocurrió.

#### Scenario: Outbound movement of an existing reference
- **WHEN** salen tres unidades de una referencia con existencias
- **THEN** el libro de existencias recoge una anotación de salida de tres unidades

verifies:   test/inventory/stock-ledger.spec.ts
confidence: high
from:       prfaq/almacen-sin-sorpresas.md#todo-movimiento-deja-rastro
