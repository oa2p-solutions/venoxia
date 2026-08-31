## ADDED Requirements

### R-INV-002 · Low stock alert on threshold crossing

WHEN las existencias de una referencia bajan del punto de pedido, el sistema emite un
aviso de reposición dirigido al responsable de compras de esa familia de producto.

#### Scenario: Stock falls below the reorder point
- **WHEN** una salida deja las existencias por debajo del punto de pedido
- **THEN** se emite un aviso de reposición para el responsable de compras

#### Scenario: Stock stays above the reorder point
- **WHEN** una salida deja las existencias por encima del punto de pedido
- **THEN** no se emite ningún aviso de reposición

confidence: high
from:       prfaq/almacen-sin-sorpresas.md#nadie-se-entera-tarde

### R-INV-003 · Reorder point derived from recent consumption

WHEN el sistema recalcula el punto de pedido de una referencia, lo fija en el consumo
medio diario de las últimas cuatro semanas multiplicado por el plazo de entrega en días.

#### Scenario: Reference with four full weeks of consumption
- **WHEN** una referencia acumula cuatro semanas completas de consumo
- **THEN** su punto de pedido es el consumo medio diario por el plazo de entrega

verifies:   test/inventory/reorder-point.spec.ts
confidence: high
from:       prfaq/almacen-sin-sorpresas.md#nadie-se-entera-tarde
