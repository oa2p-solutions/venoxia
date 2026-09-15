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

#### Scenario: Product discontinued on one line
- **WHEN** alguna línea del pedido es de un producto descatalogado
- **THEN** la petición se rechaza y no se crea ninguna reserva

#### Scenario: Line quantity above the reservable limit
- **WHEN** alguna línea pide más unidades de las que se pueden reservar de una vez
- **THEN** la petición se rechaza y no se crea ninguna reserva

verifies:   test/checkout/stock-reservation.spec.ts
confidence: medium
  why:      el PR/FAQ dice «se rechaza» sin fijar con qué respuesta se rechaza
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
