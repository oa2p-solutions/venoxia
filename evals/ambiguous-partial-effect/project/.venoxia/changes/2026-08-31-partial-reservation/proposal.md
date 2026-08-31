# Reservar el stock cuando alguna línea se queda corta

## Por qué

Un pedido de cinco líneas con una sola línea sin existencias se cae entero. El cliente
pierde también las cuatro líneas que sí estaban disponibles.

## Qué cambia

La capability `checkout` gana un requisito sobre qué se reserva cuando una línea no llega:
el pedido deja de caerse entero.

## Apuestas

El texto del PR/FAQ dice «con lo que hay». Nadie ha escrito todavía si eso significa
reservar solo las líneas disponibles o no reservar nada hasta que el cliente decida.
