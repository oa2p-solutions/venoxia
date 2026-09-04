# <name> Specification

<!-- Plantilla de capability de Venoxia. Una capability describe el estado actual del
     comportamiento observable de una parte del sistema, y vive para siempre en
     `.venoxia/capabilities/<name>/spec.md`. No describe la implementación: si algo
     puede cambiar sin que cambie el comportamiento observable, no pertenece aquí.

     Sustituye `<name>` por el nombre del directorio de la capability, en kebab-case
     (por ejemplo `checkout`). Los encabezados estructurales y las claves de metadatos
     van en inglés porque los parsea `validate.py`; la prosa va en español.

     Borra los comentarios guía y el requisito de ejemplo al rellenar la plantilla. -->

## Purpose

<!-- Una o dos frases: para qué existe esta capability y de qué responde ante el resto
     del sistema. Escribe el propósito, no el catálogo de requisitos: eso viene abajo.
     Si no sabes decir en dos frases para qué sirve, todavía no tienes una capability,
     tienes un cajón de sastre. -->

Gestiona el proceso de pago del carrito: reserva de existencias, cobro y
confirmación del pedido frente al cliente.

## Requirements

<!-- LA FORMA CANÓNICA DEL REQUISITO

     1. Encabezado `### R-XXX-000 · Título en inglés`. El ID vive en el encabezado
        (`^R-[A-Z]{2,4}-\d{3}$`): estable, enlazable y parseable. El prefijo de dos a cuatro
        letras identifica la capability (CHK = checkout). El separador es `·`.
     2. Narrativa EARS en español, arrancando con la palabra clave en inglés (`WHEN`,
        `WHILE`, `WHERE`, `IF … THEN`, o ninguna para un requisito ubicuo). Usa `DEBE`
        para la obligación: la regla V14 avisa si escribes `SHALL` o `MUST` en una
        prosa que por lo demás está en español.
     3. Uno o más escenarios `#### Scenario:`, cada uno con al menos un bullet
        `- **WHEN**` y otro `- **THEN**` (V05). Si te faltan palabras para el `THEN`,
        el comportamiento no está decidido y lo estás delegando en quien implemente.
     4. Bloque de metadatos al final. No es opcional ni un paso posterior: un
        requisito sin oráculo no compila.

     LOS METADATOS, CLAVE A CLAVE

     · `verifies` — ruta (o varias, separadas por coma o espacio) del test que resuelve la
       apuesta. `validate.py` falla con V06 si falta, con V07 si el fichero no existe
       y con V08 si ese fichero no contiene `@covers <ID>`. El doble vínculo
       spec ↔ test es el corazón del sistema: sin él la spec puede mentir sin coste.
     · `confidence` — `high`, `medium` o `low` (V09). Es una declaración honesta, no
       una nota de autoestima: `high` es comportamiento decidido y contrastado;
       `medium` es que hay una elección discutible detrás.
     · `why` — qué parte concreta es la apuesta. Imprescindible en `medium` y `low`:
       sin el porqué, quien revise dentro de tres meses no sabrá qué reconsiderar.
     · `revisit` — **el hecho que resuelve la apuesta**, no una fecha. Con
       `confidence: low` lo exige V10. Lo que cierra una suposición no es que pase el
       tiempo, es que llegue un dato: «cuando hayamos medido un mes de reservas
       caducadas» dice qué habrá que mirar y permite reconocer el momento cuando
       llega. Un día del calendario no dice ninguna de las dos cosas y llega igual
       esté la respuesta disponible o no, así que sólo se puede posponer; V10 rechaza
       las fechas por eso.
     · `from` — origen de la decisión, como `documento#sección`. V15 avisa si falta
       en un requisito nuevo, para que se sepa de dónde salió el comportamiento.

     Presupuesto de incertidumbre (V11): como mucho el 30 % de los requisitos del
     ámbito validado puede estar en `confidence: low`. Si lo superas, no tienes una
     especificación, tienes una lista de deseos. -->

### R-CHK-014 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de
todas las líneas del pedido durante 15 minutos.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas
- **THEN** se crea la reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea
- **THEN** responde 409 y no crea ninguna reserva

verifies:   test/checkout/reservation.spec.ts
confidence: medium
  why:      los 15 minutos son una apuesta, no un dato
  revisit:  cuando hayamos medido un mes de reservas caducadas
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
