# <change-id> Proposal

<!-- Plantilla de propuesta de Venoxia. Vive en `.venoxia/changes/<id>/proposal.md` y
     responde a una sola pregunta: por qué merece la pena hacer este cambio y qué
     comportamiento observable se compromete a cambiar. El detalle del comportamiento
     va en los deltas de `delta/<capability>.md`, no aquí.

     Encabezados en inglés, prosa en español. Borra los comentarios guía al rellenar. -->

## Why

<!-- La motivación: qué problema resuelve y por qué ahora. Un problema concreto con
     alguien que lo sufre, no una mejora genérica. Si la única respuesta es «para
     modernizarlo», el cambio todavía no está justificado. -->

Hoy el stock se descuenta al completarse el cobro, así que dos clientes pueden
pagar la última unidad y uno de los dos recibe una cancelación posterior.

## What Changes

<!-- Qué cambia de cara a quien usa el sistema, en frases cortas. Comportamiento
     observable: no menciones clases, tablas ni ficheros; eso es implementación y
     cambiará sin que la especificación tenga que enterarse. -->

- Al confirmar el pago se reserva el stock de todas las líneas del pedido.
- Si falta stock en alguna línea, la confirmación se rechaza sin reservar nada.
- La reserva caduca sola si el cobro no se completa a tiempo.

## Capabilities

### New Capabilities

<!-- Capabilities que se crean. Nombre en kebab-case, una línea por capability; cada
     una genera `.venoxia/capabilities/<name>/spec.md`. Si la lista queda vacía,
     bórrala en lugar de dejar un hueco. -->

- `checkout`: reserva de existencias, cobro y confirmación del pedido.

### Modified Capabilities

<!-- Capabilities existentes cuyos REQUISITOS cambian, no sólo su implementación. Cada
     una necesita su fichero de delta. Un cambio puramente interno no aparece aquí: si
     no cambia el comportamiento observable, no cambia la especificación. -->

- `inventory`: el stock pasa a distinguir entre existencias reservadas y libres.

## Impact

<!-- Qué se ve afectado: APIs públicas, contratos con terceros, datos que hay que
     migrar, consumidores que se enteran del cambio. Nombra también lo que se rompe:
     una propuesta que no rompe nada suele ser una propuesta que no ha mirado. -->

- `POST /checkout/confirm` gana la respuesta `409` cuando falta stock.
- El panel de almacén debe distinguir existencias reservadas de disponibles.
- Sin migración de datos: las reservas nacen vacías.

## Confidence

<!-- Sección propia de Venoxia. Aquí se declara, a la vista de todo el mundo, qué
     partes de esta propuesta son apuestas y cuándo se revisan. Es el mismo contrato
     que imponen los metadatos de cada requisito, pero al nivel de la decisión
     completa: `validate.py` exige `expires` a cada requisito en `confidence: low`
     (V10) porque una apuesta sin fecha de revisión es una mentira aplazada, y limita
     al 30 % la proporción de requisitos en `low` (V11).

     Una línea por apuesta, con el mismo vocabulario que los requisitos:
     qué se apuesta · nivel · por qué es una apuesta · cuándo se revisa · qué dato la
     resuelve. Si no sabes qué evidencia la resolvería, no es una apuesta: es una
     preferencia disfrazada. -->

- **Los 15 minutos de la reserva** · `low` · el número sale de una estimación, no de
  datos de conversión · se revisa el `2026-10-30` con la tasa de reservas caducadas
  del primer mes.
- **Rechazar el pedido completo cuando falta una sola línea** · `medium` · asumimos
  que el cliente prefiere el rechazo al envío parcial · se revisa el `2026-12-15` con
  las reclamaciones de pedidos rechazados.
- **El resto de la propuesta** · `high` · comportamiento decidido y contrastado con
  operaciones; no requiere revisión programada.
