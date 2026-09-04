## ADDED Requirements

### R-CHK-001 · Receipt on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE mostrarle un recibo con el desglose
exacto de lo cobrado.

#### Scenario: Payment confirmed with a single line
- **WHEN** se confirma el pago de un pedido de una sola línea
- **THEN** el recibo muestra esa línea con su importe exacto

verifies:   test/checkout/receipt.spec.ts
confidence: high
from:       prfaq/checkout-sin-sorpresas.md#el-cliente-ve-el-recibo-de-lo-que-pago

### R-CHK-002 · Reservation release on refund

WHEN un pago se revierte, el sistema DEBE liberar la reserva de existencias que ese
pedido había tomado.

#### Scenario: Refund of a paid order with an active reservation
- **WHEN** se revierte el pago de un pedido con una reserva activa
- **THEN** la reserva de existencias de ese pedido queda liberada

verifies:   test/checkout/refund.spec.ts
confidence: high
from:       prfaq/checkout-sin-sorpresas.md#una-devolucion-libera-lo-que-habia-reservado
