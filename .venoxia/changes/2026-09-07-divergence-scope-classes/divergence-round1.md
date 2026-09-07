# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-scope-classes/readings-round1`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 2
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 2 divergencias blandas sobre los 2 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 2

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Two synonyms of the same class

El lector A describe el efecto como «esa diferencia no hace dura la divergencia»; el lector B describe el efecto como «no marca divergencia dura entre las dos lecturas». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two synonyms of the same class» es la correcta?**
- (A) «esa diferencia no hace dura la divergencia»
- (B) «no marca divergencia dura entre las dos lecturas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Two marks of different classes

El lector A describe el efecto como «esa diferencia hace dura la divergencia»; el lector B describe el efecto como «marca divergencia dura entre las dos lecturas». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two marks of different classes» es la correcta?**
- (A) «esa diferencia hace dura la divergencia»
- (B) «marca divergencia dura entre las dos lecturas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-012 — El requisito habla de «las marcas de alcance» de cada efecto sin decir qué ocurre cuando un efecto contiene más de una: una implementación que clasifica cada efecto por su primera marca declara de la misma clase «sólo actualiza parcialmente oracle.json» y «sólo actualiza oracle.json completo» (ambos empiezan por «sólo», clase 1) y marca la divergencia como blanda, ocultando justo la contradicción parcial/completo que el segundo escenario exige endurecer; el change pasa a `validated` con dos lectores que entendieron comportamientos opuestos.
- **[high]** R-DIV-012 — La tercera clase mete en el mismo saco «completo», «total» y «todo», de modo que la implementación DEBE tratar como iguales «reserva todo el stock disponible» y «reserva el stock completo del pedido»: mismo sujeto («el stock»), misma clase, divergencia blanda. Dos lecturas que describen reservar cosas distintas (lo que hay vs. lo que se pidió) quedan silenciadas por el propio mandato, que es el escenario que la detección de divergencia existe para cazar.
