# Pago repartido entre varios medios

## Por qué

El ticket medio ha subido y los clientes piden partir el importe entre tarjeta y saldo
de la tienda. Hoy solo aceptamos un medio por pedido.

## Qué cambia

La capability `payments` gana cuatro requisitos: repartir el importe entre varios medios,
deshacer el reparto entero si una parte falla, decidir el orden en que se consumen los
medios y limitar cuántos medios caben en un pedido.

## Apuestas

Dos de los cuatro requisitos son conjeturas sin dato detrás: el orden de consumo de los
medios y el tope de medios por pedido. Van declarados con `confidence: low` y su fecha
de caducidad, a la espera de la prueba con clientes reales.
