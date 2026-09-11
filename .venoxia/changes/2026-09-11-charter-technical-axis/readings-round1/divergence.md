# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-charter-technical-axis/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 8
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 1 divergencia blanda sobre los 8 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 1

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The technical conventions heading is gone

El lector A describe el efecto como «el encabezado Convenciones técnicas ya no aparece»; el lector B describe el efecto como «el cuerpo no contiene el encabezado indicado». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The technical conventions heading is gone» es la correcta?**
- (A) «el encabezado Convenciones técnicas ya no aparece»
- (B) «el cuerpo no contiene el encabezado indicado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-CHL-007 — La disyunción «requisito de technical-contract con verifies: o apuesta en ## Bets» se puede resolver siempre por el lado barato: una skill que clasifica todo juicio técnico sin principio como apuesta cumple la frase al pie de la letra y pasa los tres escenarios (que sólo exigen que el cuerpo nombre los dos destinos y prohíba la prosa), y el resultado es que ningún juicio técnico llega nunca al contrato con test, que es justo lo que el change existe para evitar.
- **[medium]** R-CHL-006 — «el /venoxia:specify tecleado de la entrega» y el escenario que sólo pide declarar que la entrega termina con ese comando se cumplen imprimiendo la línea del comando al usuario; nada obliga a comprobar que los requisitos se escribieron. Si el usuario no lo teclea, las convenciones técnicas aprobadas quedan como filas de una tabla del acta sin ningún requisito con verifies: detrás, es decir, exactamente la prosa no verificable que el requisito dice erradicar.
- **[medium]** R-CHL-006 — «DEBE escribir principles.md sólo con los tres principios del método y los de dominio» autoriza a reescribir el fichero descartando todo lo que no encaje en esas dos categorías, y la obligación de trasladar sólo alcanza a las convenciones de la tanda en curso; en un proyecto ya adoptado, la skill borra de principles.md convenciones técnicas preexistentes sin llevarlas a technical-contract ni a ## Bets, perdiendo decisiones que eran su único registro.
- **[low]** R-CHL-006 — El único escenario negativo prohíbe la cadena literal «## Convenciones técnicas»; una skill que renombra el encabezado (por ejemplo «## Acuerdos del eje técnico») y sigue volcando ahí la prosa de cada convención, además de llevarla a technical-contract, pasa los cinco escenarios y deja dos fuentes de verdad para la misma decisión técnica, que divergirán en cuanto una de las dos se edite.

## Escenarios que convergen · 7

- An approved convention is a requirement of technical-contract
- An undecided convention is a bet
- The principles file carries no technical conventions
- The delivery hands the approved conventions to specify
- The body names the two destinations
- The body forbids prose
- The inventory includes the technical contract
