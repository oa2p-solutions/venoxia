# Capability: checkout

## Purpose

El paso de pago de la tienda: desde que el cliente revisa el carrito hasta que el pedido
queda confirmado y cobrado.

## Requirements

### R-CHK-001 · Cart total recalculation on line change

WHEN el cliente cambia la cantidad de una línea del carrito, el sistema recalcula el
total del carrito antes de devolver la respuesta.

#### Scenario: Quantity increased on a line with stock
- **WHEN** el cliente sube la cantidad de una línea que tiene stock
- **THEN** el total del carrito refleja la nueva cantidad en la misma respuesta

verifies:   test/checkout/cart-total.spec.ts
confidence: high
from:       prfaq/checkout-express.md#el-carrito-siempre-cuadra

### R-CHK-002 · Payment confirmation is idempotent

WHEN el cliente confirma el pago dos veces con el mismo identificador de intento, el
sistema devuelve el resultado de la primera confirmación y no genera un segundo cargo.

#### Scenario: Same payment intent confirmed twice
- **WHEN** llega una segunda confirmación con un identificador de intento ya usado
- **THEN** responde 200 con el resultado de la primera y no genera un segundo cargo

verifies:   test/checkout/payment-confirmation.spec.ts
confidence: high
from:       prfaq/checkout-express.md#nunca-se-cobra-dos-veces
