# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-divergence-policy-decisions/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 45
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 18 divergencias blandas sobre los 45 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 18

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The new fields reach the members

El lector A describe el efecto como «el miembro de la decisión lleva los campos literales»; el lector B describe el efecto como «el miembro lleva requirement_id e input literales». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The new fields reach the members» es la correcta?**
- (A) «el miembro de la decisión lleva los campos literales»
- (B) «el miembro lleva requirement_id e input literales»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The reader agent asks for both fields

El lector A describe el efecto como «los dos ficheros nombran requirement_id e input como campos»; el lector B describe el efecto como «ambos documentos nombran requirement_id e input como campos». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reader agent asks for both fields» es la correcta?**
- (A) «los dos ficheros nombran requirement_id e input como campos»
- (B) «ambos documentos nombran requirement_id e input como campos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Three CLP notations are one decision

El lector A registra «crea una decisión con razón same-policy-across-scenarios» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Three CLP notations are one decision»?**
- (A) «crea una decisión con razón same-policy-across-scenarios»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Three CLP notations are one decision

El lector A describe el efecto como «agrupa los tres escenarios en una sola decisión por política»; el lector B describe el efecto como «el JSON agrupa las tres notaciones en una decisión». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Three CLP notations are one decision» es la correcta?**
- (A) «agrupa los tres escenarios en una sola decisión por política»
- (B) «el JSON agrupa las tres notaciones en una decisión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The figures are never diluted

El lector A describe el efecto como «cada miembro conserva sus cifras literales y la matriz las muestra»; el lector B describe el efecto como «cada miembro conserva sus lecturas literales con cifras». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The figures are never diluted» es la correcta?**
- (A) «cada miembro conserva sus cifras literales y la matriz las muestra»
- (B) «cada miembro conserva sus lecturas literales con cifras»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Without a requirement the rest of the scenario must match

El lector A describe el efecto como «quedan dos decisiones si side_effects difieren, una si comparten requirement_id»; el lector B describe el efecto como «sin requirement_id son dos decisiones; con el mismo, una». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Without a requirement the rest of the scenario must match» es la correcta?**
- (A) «quedan dos decisiones si side_effects difieren, una si comparten requirement_id»
- (B) «sin requirement_id son dos decisiones; con el mismo, una»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Members carry their hardness

El lector A describe el efecto como «cada miembro indica su dureza y la decisión toma la mayor»; el lector B describe el efecto como «cada miembro dice su dureza; la decisión, la mayor». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Members carry their hardness» es la correcta?**
- (A) «cada miembro indica su dureza y la decisión toma la mayor»
- (B) «cada miembro dice su dureza; la decisión, la mayor»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Members are evidence, not questions

El lector A describe el efecto como «cada divergencia muestra dureza y detalle sin pregunta ni opciones»; el lector B describe el efecto como «cada divergencia trae dureza y detalle, sin opciones». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Members are evidence, not questions» es la correcta?**
- (A) «cada divergencia muestra dureza y detalle sin pregunta ni opciones»
- (B) «cada divergencia trae dureza y detalle, sin opciones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The old sections are gone

El lector A describe el efecto como «desaparecen las secciones antiguas y queda Decisiones pendientes con recuento»; el lector B describe el efecto como «el informe omite las secciones antiguas, sí muestra decisiones pendientes». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The old sections are gone» es la correcta?**
- (A) «desaparecen las secciones antiguas y queda Decisiones pendientes con recuento»
- (B) «el informe omite las secciones antiguas, sí muestra decisiones pendientes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Changed options make the earlier answer stale

El lector A describe el efecto como «la decisión sale stale con stale_reason indicando qué cambió»; el lector B describe el efecto como «la decisión sale stale y dice qué opción cambió». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Changed options make the earlier answer stale» es la correcta?**
- (A) «la decisión sale stale con stale_reason indicando qué cambió»
- (B) «la decisión sale stale y dice qué opción cambió»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict ignores the history

El lector A describe el efecto como «counts, verdict y exit_code no cambian por el historial»; el lector B describe el efecto como «counts, veredicto y exit_code son iguales que sin historial». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict ignores the history» es la correcta?**
- (A) «counts, verdict y exit_code no cambian por el historial»
- (B) «counts, veredicto y exit_code son iguales que sin historial»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A clarification gets one more call

El lector A describe el efecto como «declara una llamada adicional con la misma pregunta e información»; el lector B describe el efecto como «el texto describe una llamada más con la misma pregunta». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A clarification gets one more call» es la correcta?**
- (A) «declara una llamada adicional con la misma pregunta e información»
- (B) «el texto describe una llamada más con la misma pregunta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An answer that does not fit every member is asked per member

El lector A describe el efecto como «declara preguntar por miembro, cada uno con su propio answer»; el lector B describe el efecto como «el texto describe preguntar por miembro con su propia respuesta». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An answer that does not fit every member is asked per member» es la correcta?**
- (A) «declara preguntar por miembro, cada uno con su propio answer»
- (B) «el texto describe preguntar por miembro con su propia respuesta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Answered decisions are not asked again

El lector A describe el efecto como «declara pasar el historial y no repreguntar las respondidas»; el lector B describe el efecto como «el texto describe pasar el historial y no repreguntar lo answered». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Answered decisions are not asked again» es la correcta?**
- (A) «declara pasar el historial y no repreguntar las respondidas»
- (B) «el texto describe pasar el historial y no repreguntar lo answered»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict does not move

El lector A describe el efecto como «counts y veredicto no cambian y decisions trae una sola entrada»; el lector B describe el efecto como «el veredicto sigue diverged y decisions trae una entrada». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict does not move» es la correcta?**
- (A) «counts y veredicto no cambian y decisions trae una sola entrada»
- (B) «el veredicto sigue diverged y decisions trae una entrada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A two-field option carries both fields of its reader

El lector A describe el efecto como «la opción combina el efecto y los side_effects del mismo lector»; el lector B describe el efecto como «la opción enlaza efecto y efectos colaterales del lector». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A two-field option carries both fields of its reader» es la correcta?**
- (A) «la opción combina el efecto y los side_effects del mismo lector»
- (B) «la opción enlaza efecto y efectos colaterales del lector»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One decision per call

El lector A describe el efecto como «declara plantear una decisión por llamada con pregunta y opciones literales»; el lector B describe el efecto como «se pregunta una decisión por llamada, en orden del informe». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One decision per call» es la correcta?**
- (A) «declara plantear una decisión por llamada con pregunta y opciones literales»
- (B) «se pregunta una decisión por llamada, en orden del informe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The root decision is explained once

El lector A describe el efecto como «declara explicar la decisión raíz una vez y listar escenarios»; el lector B describe el efecto como «se explica la decisión raíz una vez antes de preguntar». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The root decision is explained once» es la correcta?**
- (A) «declara explicar la decisión raíz una vez y listar escenarios»
- (B) «se explica la decisión raíz una vez antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-DIV-023 — Nada en el delta obliga a que la respuesta llegue al texto del delta, y una decisión cerrada como `custom-resolved` o `selected` en una sesión que no llegó a editarlo sale `answered` en la siguiente pasada: la skill no la pregunta (R-DIV-023), R-DIV-021 sólo lleva a «Decisiones pendientes» las decisiones no respondidas y R-DIV-022 impide que el historial mueva el código de salida, así que `diff_readings.py` devuelve 1 para siempre sin ninguna pregunta que contestar y el change no puede llegar nunca a `validated` salvo editando a mano `decisions.json`.
- **[medium]** R-DIV-019 — El THEN de «Without a requirement the rest of the scenario must match» dice literalmente que con el mismo `requirement_id` dos escenarios siguen siendo una sola decisión aunque un lector les dé `side_effects` distintos, y la matriz que R-DIV-021 obliga a enseñar sólo trae escenario, entrada, lectura del campo en disputa y dureza: el usuario cierra de una sola respuesta escenarios cuyos efectos colaterales divergen sin llegar a verlos en la pregunta.

## Escenarios que convergen · 28

- A reading without the new fields still parses
- Different requirements stay apart
- A reader who changes policy breaks the group
- Identical readings keep their old reason
- A reader-backed option resolves every member literally
- The equivalent option resolves nothing
- Each question appears once
- The rest of the report does not move
- Without a history every decision is pending
- A matching resolved answer is answered
- A clarification does not close
- The latest entry with the fingerprint wins
- A member left open keeps the decision pending
- An equivalence that left the divergence hard is stale
- A legacy chosen option is migrated
- A legacy hand-written answer is unclassified
- The five resolutions are named
- Only three resolutions close
- A contract change is routed, not closed
- The skill announces the running version
- Every divergence belongs to exactly one decision
- A grouped question names its scenarios and confronts the readings
- The report lists every decision once
- Every member is recorded with its own answer
- The skill never groups on its own
- The three JSON reports name the version
- The text report names the version
- A missing manifest does not break the report
