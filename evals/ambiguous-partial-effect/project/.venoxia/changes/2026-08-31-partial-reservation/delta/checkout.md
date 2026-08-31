## ADDED Requirements

### R-CHK-012 · Reservation when some lines are short of stock

WHEN el cliente confirma el pago y alguna línea del pedido no tiene stock suficiente, el
sistema reserva lo que puede y le comunica al cliente el resultado de la reserva.

#### Scenario: Every line has stock
- **WHEN** las tres líneas del pedido tienen stock suficiente
- **THEN** responde 200 y comunica el resultado de la reserva

#### Scenario: One line short of stock
- **WHEN** una de las tres líneas del pedido no tiene stock suficiente
- **THEN** responde 200 y comunica el resultado de la reserva

verifies:   test/checkout/partial-reservation.spec.ts
confidence: medium
  why:      «lo que puede» no está decidido: puede ser todo el pedido o solo las líneas con stock
from:       prfaq/checkout-express.md#nadie-se-queda-a-medias
