## ADDED Requirements

### R-CHK-010 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema reserva el stock de todas las líneas del
pedido durante 15 minutos y devuelve el identificador de la reserva.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas del pedido
- **THEN** se crea una única reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea del pedido
- **THEN** la petición se rechaza y no se crea ninguna reserva

verifies:   test/checkout/stock-reservation.spec.ts
confidence: medium
  why:      el PR/FAQ dice «se rechaza» sin fijar con qué respuesta se rechaza
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
