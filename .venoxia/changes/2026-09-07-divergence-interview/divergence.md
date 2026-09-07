# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 10
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 4 divergencias blandas sobre los 10 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 4

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A negation makes it hard

El lector A describe el efecto como «el elemento de divergences lleva signal con valor polarity»; el lector B describe el efecto como «el elemento de divergences lleva la señal polarity». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negation makes it hard» es la correcta?**
- (A) «el elemento de divergences lleva signal con valor polarity»
- (B) «el elemento de divergences lleva la señal polarity»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The report names the negation

El lector A describe el efecto como «el informe nombra la marca «no» como causa de la divergencia»; el lector B describe el efecto como «el informe nombra la marca «no» como causante». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The report names the negation» es la correcta?**
- (A) «el informe nombra la marca «no» como causa de la divergencia»
- (B) «el informe nombra la marca «no» como causante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A different number makes it hard

El lector A describe el efecto como «signal vale numeric y el informe nombra los dos números»; el lector B describe el efecto como «el elemento lleva signal numeric y el informe cita ambos números». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A different number makes it hard» es la correcta?**
- (A) «signal vale numeric y el informe nombra los dos números»
- (B) «el elemento lleva signal numeric y el informe cita ambos números»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Earlier decisions are kept

El lector A registra «se añade la respuesta a decisions.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Earlier decisions are kept»?**
- (A) «se añade la respuesta a decisions.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-DIV-008 — La clave `signal` es única y el delta no fija precedencia cuando concurren dos señales: ante «no se crea el presupuesto en 15 minutos» frente a «se crea el presupuesto en 30 minutos», una implementación que emite `signal: "numeric"` y nombra sólo el 15 y el 30 cumple los cuatro escenarios (el escenario de la negación sólo aplica a su propio caso), pero el informe y la entrevista posterior nunca mencionan que un lector dice que el efecto no ocurre: el usuario resuelve la duración y la contradicción de fondo sobre si el presupuesto se crea sigue viva en el delta.
- **[medium]** R-DIV-008 — «Nombrar en el informe la señal que la hizo dura» se satisface imprimiendo la palabra `scope` o `empty-repertoire`, porque sólo los escenarios de `polarity` y `numeric` exigen contenido (la marca «no», los dos números); para las otras dos señales el informe puede no decir qué difiere entre las lecturas, y el usuario tiene que contestar la pregunta cerrada a ciegas y esa respuesta se copia literal al delta por R-DIV-010.
- **[medium]** R-DIV-010 — «Sin borrar las respuestas ya anotadas» convierte `decisions.json` en un fichero que nadie limpia ni acota al informe en curso: una segunda pasada de `/venoxia:diverge` sobre el delta ya corregido deja dos entradas con el mismo `scenario` y la misma `question` y `chosen` contradictorios, y como ninguna frase dice cuál gana, el paso que copia el texto al escenario puede pegar la decisión obsoleta —o la que el usuario ya rectificó— en el requisito.

## Escenarios que convergen · 6

- A soft divergence carries no signal
- The tool is declared
- The body forbids grouping and rewording
- The body still refuses to edit deltas
- The body names the decisions file and its shape
- A hand-written answer is kept verbatim
