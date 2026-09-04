# <capability> Delta

<!-- Plantilla de delta de Venoxia. Un delta describe el cambio de comportamiento que
     propone un change concreto, nunca el estado completo de la capability. Vive en
     `.venoxia/changes/<id>/delta/<capability>.md` y el nombre del fichero determina a
     qué capability se aplica.

     Un delta declara al menos uno de los cuatro bloques de abajo (V12). Deja los
     bloques que no uses vacíos o bórralos, pero no inventes requisitos para rellenar:
     un requisito de adorno es peor que un bloque vacío, porque pasa la validación y
     miente igual.

     Los encabezados y las claves de metadatos van en inglés; la prosa, en español.
     Borra los comentarios guía al rellenar la plantilla. -->

## ADDED Requirements

<!-- Comportamiento que hoy no existe en la capability viva. El ID es nuevo y no puede
     repetir ninguno ya usado (V01). Si la capability es nueva, indica el origen de la
     decisión en `from` para no perder la trazabilidad (V15 avisa cuando falta).

     El requisito de ejemplo está completo a propósito: el bloque de metadatos con
     `verifies` y `confidence` forma parte del requisito desde el primer borrador, no
     es un trámite que se despacha al final. Sin oráculo, el requisito no compila. -->

### R-CHK-021 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de
todas las líneas del pedido durante 15 minutos.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas
- **THEN** se crea la reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea
- **THEN** responde 409 y no crea ninguna reserva

verifies:   test/checkout/stock-reservation.spec.ts
confidence: medium
  why:      los 15 minutos son una apuesta, no un dato
  revisit:  cuando hayamos medido un mes de reservas caducadas
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar

## MODIFIED Requirements

<!-- Requisitos que ya existen en la capability viva y cambian de comportamiento. El
     encabezado repite el ID existente —eso no es un duplicado, es lo esperado— y V13
     comprueba que ese ID exista de verdad en `.venoxia/capabilities/`.

     Copia el requisito entero con el texto nuevo, no sólo la parte que cambia: el
     delta debe poder leerse sin tener la spec viva delante. Revisa también los
     metadatos, porque un cambio de comportamiento casi siempre invalida el oráculo
     anterior y suele bajar la confianza que tenías. -->

## REMOVED Requirements

<!-- Comportamiento que deja de existir. Basta el encabezado con el ID vivo y una
     narrativa que explique por qué se retira y qué pasa con lo que dependía de él.
     Retirar un requisito es una decisión de producto: si nadie sabe decir a quién
     afecta, todavía no está tomada. -->

## RENAMED Requirements

<!-- El comportamiento se conserva pero cambia su identidad: el título, el ID, o la
     capability a la que pertenece. El encabezado lleva el ID vivo para que V13 lo
     encuentre, y la narrativa declara el nombre o el ID nuevo. Úsalo en lugar de un
     REMOVED más un ADDED: así el historial no pierde el rastro de la decisión. -->
