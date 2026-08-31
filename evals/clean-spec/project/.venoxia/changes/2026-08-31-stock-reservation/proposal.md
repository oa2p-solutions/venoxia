# Reservar el stock al confirmar el pago

## Por qué

Hoy el stock se descuenta cuando el pago se liquida, y entre la confirmación y la
liquidación pasan hasta doce minutos. En ese hueco dos clientes pueden comprar la misma
unidad y uno de los dos recibe un correo de disculpa. Es el motivo número uno de
incidencias del equipo de atención.

## Qué cambia

La capability `checkout` gana dos requisitos: crear una reserva de stock con TTL al
confirmar el pago, y liberarla cuando el TTL vence sin liquidación.

## Qué no cambia

El cálculo del total del carrito y la idempotencia de la confirmación de pago se quedan
como están. La reserva no toca el precio ni el flujo de cobro.

## Apuestas

Los 15 minutos de TTL salen del percentil 99 del tiempo de liquidación actual más un
margen. Es la única cifra elegida y está declarada como tal en el delta.
