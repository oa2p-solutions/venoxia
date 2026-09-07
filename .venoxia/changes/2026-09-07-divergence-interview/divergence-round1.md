# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 9
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 5 blandas y 0 lagunas declaradas sobre los 9 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: A different number makes it hard

El lector B registra «elemento de divergences lleva la clave signal con valor numeric» y «el informe nombra los dos números (15 y 30)» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Además, lo que registra el otro lector lo contradice.

**¿Qué efectos observables debe producir «A different number makes it hard»?**
- (A) «elemento de divergences lleva la clave signal con valor numeric» y «el informe nombra los dos números (15 y 30)»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 5

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A negation makes it hard

El lector A describe el efecto como «el elemento de divergences lleva signal con valor polarity»; el lector B describe el efecto como «el JSON marca la divergencia con signal polarity». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negation makes it hard» es la correcta?**
- (A) «el elemento de divergences lleva signal con valor polarity»
- (B) «el JSON marca la divergencia con signal polarity»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A different number makes it hard

El lector A describe el efecto como «signal vale numeric y el informe nombra ambos números»; el lector B describe el efecto como «el JSON marca signal numeric y el informe cita ambos números». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A different number makes it hard» es la correcta?**
- (A) «signal vale numeric y el informe nombra ambos números»
- (B) «el JSON marca signal numeric y el informe cita ambos números»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A soft divergence carries no signal

El lector A describe el efecto como «el elemento de divergences lleva signal con valor null»; el lector B describe el efecto como «el JSON marca la divergencia sin señal (signal null)». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A soft divergence carries no signal» es la correcta?**
- (A) «el elemento de divergences lleva signal con valor null»
- (B) «el JSON marca la divergencia sin señal (signal null)»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The tool is declared

El lector A describe el efecto como «el frontmatter de la skill incluye AskUserQuestion en allowed-tools»; el lector B describe el efecto como «el frontmatter de la skill declara AskUserQuestion». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The tool is declared» es la correcta?**
- (A) «el frontmatter de la skill incluye AskUserQuestion en allowed-tools»
- (B) «el frontmatter de la skill declara AskUserQuestion»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body forbids grouping and rewording

El lector A describe el efecto como «el cuerpo exige una pregunta por llamada, orden y texto literal»; el lector B describe el efecto como «el cuerpo de la skill prohíbe agrupar o reformular preguntas». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body forbids grouping and rewording» es la correcta?**
- (A) «el cuerpo exige una pregunta por llamada, orden y texto literal»
- (B) «el cuerpo de la skill prohíbe agrupar o reformular preguntas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-008 — El requisito sólo se activa «cuando marca como dura una divergencia de side_effects» y exige que la señal sea una de cuatro; una implementación literal garantiza el consecuente estrechando el antecedente: marca dura únicamente lo que encaja en `polarity`, `scope`, `numeric` o `empty-repertoire`, y degrada a blanda cualquier otra contradicción entre lectores (p. ej. un lector dice que se escribe en `drift/` y el otro que se escribe en `oracle.json`). Así `diff_readings.py` sale con 0, la skill escribe `validated` y el guardián abre la puerta al código con dos lecturas incompatibles del mismo delta.
- **[medium]** R-DIV-008 — «Emitir esa misma señal ... con uno de los valores» permite emitir una sola señal por divergencia aunque concurran varias: ante «no se crea el presupuesto de 15 minutos» frente a «se crea el presupuesto de 30 minutos», la implementación reporta `polarity` y el informe nombra sólo la marca «no»; la discrepancia numérica queda invisible, sin pregunta y sin decisión, y llega al código como 15 o 30 minutos al azar.
- **[medium]** R-DIV-010 — «Anotar la respuesta tal cual en decisions.json» no exige acumular ni conservar lo ya anotado: escribir el fichero entero con la última respuesta en cada iteración cumple la frase literalmente y borra las anteriores, de modo que tras una entrevista de ocho preguntas sólo sobrevive una decisión y el resto hay que volver a preguntárselas al usuario. Los dos escenarios sólo inspeccionan el texto de `SKILL.md`, así que la pérdida no se observa.

## Escenarios que convergen · 4

- The report names the negation
- The body still refuses to edit deltas
- The body names the decisions file and its shape
- A hand-written answer is kept verbatim
