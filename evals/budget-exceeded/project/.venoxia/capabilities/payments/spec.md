# Capability: payments

## Purpose

El cobro de un pedido: qué medios de pago se aceptan, cómo se reparte el importe y qué
ocurre cuando una parte del cobro falla.

## Requirements

### R-PAY-001 · Single charge per confirmed order

WHEN un pedido se confirma, el sistema genera un único cargo por el importe total del
pedido y lo asocia al identificador del pedido.

#### Scenario: Order confirmed once
- **WHEN** un pedido pasa a confirmado por primera vez
- **THEN** existe exactamente un cargo asociado a ese pedido por el importe total

verifies:   test/payments/single-charge.spec.ts
confidence: high
from:       prfaq/pago-repartido.md#un-pedido-un-cargo
