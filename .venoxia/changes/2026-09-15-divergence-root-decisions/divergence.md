# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-divergence-root-decisions/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 20
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 12 divergencias blandas sobre los 20 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 12

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Disjoint distinguishing tokens stay apart

El lector A describe el efecto como «cada divergencia queda como decisión separada, razón single»; el lector B describe el efecto como «el JSON trae dos decisiones separadas con razón single». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Disjoint distinguishing tokens stay apart» es la correcta?**
- (A) «cada divergencia queda como decisión separada, razón single»
- (B) «el JSON trae dos decisiones separadas con razón single»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A shared particle groups nothing

El lector A describe el efecto como «las divergencias no se agrupan por compartir sólo una partícula vacía»; el lector B describe el efecto como «cada divergencia queda como decisión propia, razón single». Similitud de contenido 0.09, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A shared particle groups nothing» es la correcta?**
- (A) «las divergencias no se agrupan por compartir sólo una partícula vacía»
- (B) «cada divergencia queda como decisión propia, razón single»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The same two status codes in three scenarios

El lector A describe el efecto como «una decisión agrupa las tres divergencias de código de estado»; el lector B describe el efecto como «una sola decisión agrupa los tres escenarios como miembros». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The same two status codes in three scenarios» es la correcta?**
- (A) «una decisión agrupa las tres divergencias de código de estado»
- (B) «una sola decisión agrupa los tres escenarios como miembros»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Different code pairs stay apart

El lector A describe el efecto como «quedan dos decisiones separadas, cada una con un miembro»; el lector B describe el efecto como «el JSON trae dos decisiones, cada una con un solo miembro». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Different code pairs stay apart» es la correcta?**
- (A) «quedan dos decisiones separadas, cada una con un miembro»
- (B) «el JSON trae dos decisiones, cada una con un solo miembro»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A missing scenario is never grouped

El lector A describe el efecto como «la divergencia del escenario visto por un solo lector queda sola»; el lector B describe el efecto como «la divergencia del escenario ausente queda sola, razón single». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A missing scenario is never grouped» es la correcta?**
- (A) «la divergencia del escenario visto por un solo lector queda sola»
- (B) «la divergencia del escenario ausente queda sola, razón single»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict does not move

El lector A describe el efecto como «counts y el veredicto diverged no cambian, decisions trae una entrada»; el lector B describe el efecto como «counts, veredicto diverged y decisions con una entrada quedan igual». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict does not move» es la correcta?**
- (A) «counts y el veredicto diverged no cambian, decisions trae una entrada»
- (B) «counts, veredicto diverged y decisions con una entrada quedan igual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A two-field option carries both fields of its reader

El lector A describe el efecto como «la opción de cada lector une su efecto y sus efectos colaterales»; el lector B describe el efecto como «cada opción enlaza el efecto y los efectos colaterales del mismo lector». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A two-field option carries both fields of its reader» es la correcta?**
- (A) «la opción de cada lector une su efecto y sus efectos colaterales»
- (B) «cada opción enlaza el efecto y los efectos colaterales del mismo lector»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No grouped decision, no section

El lector A describe el efecto como «el informe omite la sección Decisiones agrupadas»; el lector B describe el efecto como «el informe no incluye la sección Decisiones agrupadas». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No grouped decision, no section» es la correcta?**
- (A) «el informe omite la sección Decisiones agrupadas»
- (B) «el informe no incluye la sección Decisiones agrupadas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One decision per call

El lector A describe el efecto como «el SKILL.md declara preguntar una decisión por llamada, en orden del informe»; el lector B describe el efecto como «el cuerpo de la skill declara una decisión por llamada, orden y textos literales». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One decision per call» es la correcta?**
- (A) «el SKILL.md declara preguntar una decisión por llamada, en orden del informe»
- (B) «el cuerpo de la skill declara una decisión por llamada, orden y textos literales»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every member is recorded

El lector A describe el efecto como «el SKILL.md declara anotar en decisions.json una entrada por miembro»; el lector B describe el efecto como «el cuerpo de la skill declara anotar una entrada por miembro con mismo answer y clave decision». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every member is recorded» es la correcta?**
- (A) «el SKILL.md declara anotar en decisions.json una entrada por miembro»
- (B) «el cuerpo de la skill declara anotar una entrada por miembro con mismo answer y clave decision»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The skill never groups on its own

El lector A describe el efecto como «el SKILL.md declara que la agrupación la hace el script, no la skill»; el lector B describe el efecto como «el cuerpo de la skill declara que no agrupa y que el script decide». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The skill never groups on its own» es la correcta?**
- (A) «el SKILL.md declara que la agrupación la hace el script, no la skill»
- (B) «el cuerpo de la skill declara que no agrupa y que el script decide»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The date of the files decides nothing

El lector A describe el efecto como «el SKILL.md declara no elegir el change por la fecha de sus ficheros»; el lector B describe el efecto como «el cuerpo de la skill no elige el change por fecha del change.json». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The date of the files decides nothing» es la correcta?**
- (A) «el SKILL.md declara no elegir el change por la fecha de sus ficheros»
- (B) «el cuerpo de la skill no elige el change por fecha del change.json»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-017 — R-DIV-017 permite examinar un change en `verified` cuando su id viene en `$ARGUMENTS` y a la vez prohíbe que vuelva a `validated`: la entrevista escribe las respuestas en el delta y deja el change declarándose `verified` con un texto que ningún run del oráculo respalda, de modo que `gate.py` y `/venoxia:close` lo dan por verificado y se publica como contrato verificado un delta que nadie ha vuelto a ejecutar.
- **[medium]** R-DIV-013 — R-DIV-013 agrupa en cuanto los tokens distintivos «comparten al menos uno» y sólo excluye palabras vacías: dos divergencias sin relación (efecto «el pedido se crea» vs «el pedido se rechaza» y side_effects «se notifica al dueño del pedido» vs «no se notifica a nadie») comparten el token de contenido «pedido» y se funden en una sola decisión; el usuario contesta una pregunta y R-DIV-016 obliga a anotar ese mismo `answer` como decisión de las dos divergencias, con lo que el delta recoge una decisión que el usuario nunca tomó sobre el segundo campo.
- **[medium]** R-DIV-014 — R-DIV-014 obliga («DEBE agruparlas») a fundir en una sola decisión todas las divergencias del mismo campo que enfrentan el mismo par de lecturas, sin tope de miembros y sin ninguna vía para que el usuario responda distinto en un escenario concreto: el par «200» vs «409» repetido en doce escenarios (crear, borrar, reintentar) se contesta una vez y esa respuesta se escribe literal como decisión de los doce, incluidos aquellos en los que la respuesta correcta era la contraria.

## Escenarios que convergen · 8

- The partial reservation fixture is one decision
- A two-field decision is not chained across scenarios
- Every divergence belongs to exactly one decision
- A grouped question names its scenarios and confronts the readings
- The report lists grouped decisions
- The root decision is explained once
- Several active changes are asked about
- A verified change is never taken by default
