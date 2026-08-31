## ADDED Requirements

### R-CHK-010 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema reserva el stock de todas las líneas del
pedido durante 15 minutos y devuelve el identificador de la reserva.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas del pedido
- **THEN** responde 201 y crea una única reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea del pedido
- **THEN** responde 409, no crea ninguna reserva y deja el stock intacto

verifies:   test/checkout/stock-reservation.spec.ts
confidence: high
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar

### R-CHK-011 · Reservation release when the TTL expires

WHEN pasan 15 minutos desde que se creó una reserva sin que el pago se liquide, el
sistema libera el stock reservado y marca la reserva como caducada.

#### Scenario: Reservation reaches its TTL without settlement
- **WHEN** una reserva cumple 15 minutos sin que llegue la liquidación
- **THEN** el stock vuelve a estar disponible y la reserva figura como caducada

verifies:   test/checkout/reservation-expiry.spec.ts
confidence: high
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
