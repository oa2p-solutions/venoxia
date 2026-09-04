# El recibo llega y la devolución libera stock

## Por qué

Hoy el cliente confirma el pago y no ve el desglose de lo que pagó, y una devolución no
suelta las unidades que la reserva de esa compra había bloqueado.

## Qué cambia

La capability `checkout` nace con dos requisitos: emitir un recibo al confirmar el pago
y liberar la reserva de existencias cuando el pago se revierte.

## Capabilities

New: `checkout`.

## Impact

Ningún otro sistema cambia de contrato: ambos requisitos son comportamiento nuevo sobre
un flujo que ya existía.

## Confidence

`high` en los dos: el recibo y la liberación de stock son comportamiento decidido, no
una apuesta.
