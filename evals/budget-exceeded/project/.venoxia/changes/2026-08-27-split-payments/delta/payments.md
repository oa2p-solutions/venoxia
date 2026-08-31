## ADDED Requirements

### R-PAY-010 · Consumption order across payment methods

WHEN un pedido se paga con varios medios, el sistema consume primero el saldo de la
tienda y deja la tarjeta para el importe restante.

#### Scenario: Store credit covers part of the order
- **WHEN** el saldo de la tienda cubre una parte del importe del pedido
- **THEN** el saldo se consume entero y la tarjeta paga solo el resto

verifies:   test/payments/consumption-order.spec.ts
confidence: low
  why:      nadie ha medido si el cliente prefiere gastar antes el saldo o la tarjeta
  expires:  2030-06-30
from:       prfaq/pago-repartido.md#el-cliente-elige-como-paga

### R-PAY-011 · Maximum number of payment methods per order

WHEN un cliente añade un cuarto medio de pago a un pedido, el sistema rechaza la adición
y deja el reparto anterior intacto.

#### Scenario: Fourth payment method added to an order
- **WHEN** el pedido ya tiene tres medios de pago y se añade un cuarto
- **THEN** la adición se rechaza y el reparto de los tres medios anteriores no cambia

verifies:   test/payments/method-limit.spec.ts
confidence: low
  why:      el tope de tres medios es una conjetura de producto, no un dato de uso
  expires:  2030-06-30
from:       prfaq/pago-repartido.md#el-cliente-elige-como-paga

### R-PAY-012 · Split amounts add up to the order total

WHEN el sistema reparte el importe de un pedido entre varios medios, la suma de las
partes coincide al céntimo con el importe total del pedido.

#### Scenario: Order split between store credit and card
- **WHEN** un pedido se reparte entre saldo de la tienda y tarjeta
- **THEN** la suma de las dos partes es igual al importe total del pedido

verifies:   test/payments/split-amounts.spec.ts
confidence: medium
  why:      el redondeo con tres medios y descuentos todavía no está probado en producción
from:       prfaq/pago-repartido.md#un-pedido-un-cargo

### R-PAY-013 · Every part of a split payment is rolled back on failure

WHEN una de las partes de un pago repartido falla, el sistema deshace las partes ya
cobradas y deja el pedido sin ningún cargo.

#### Scenario: Card declined after store credit was consumed
- **WHEN** la tarjeta rechaza su parte después de haberse consumido el saldo
- **THEN** el saldo vuelve al cliente y el pedido queda sin ningún cargo

verifies:   test/payments/rollback.spec.ts
confidence: high
from:       prfaq/pago-repartido.md#un-pedido-un-cargo
