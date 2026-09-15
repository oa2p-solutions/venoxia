# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-divergence-policy-decisions/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 44
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 31 divergencias blandas sobre los 44 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 31

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A reading without the new fields still parses

El lector A registra «miembros de la decisión llevan requirement_id e input a null» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A reading without the new fields still parses»?**
- (A) «miembros de la decisión llevan requirement_id e input a null»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The new fields reach the members

El lector A describe el efecto como «el miembro de la decisión lleva los valores literales»; el lector B describe el efecto como «el miembro conserva requirement_id e input literales». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The new fields reach the members» es la correcta?**
- (A) «el miembro de la decisión lleva los valores literales»
- (B) «el miembro conserva requirement_id e input literales»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The reader agent asks for both fields

El lector A describe el efecto como «los dos documentos nombran requirement_id e input»; el lector B describe el efecto como «ambos ficheros nombran requirement_id e input como campos». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reader agent asks for both fields» es la correcta?**
- (A) «los dos documentos nombran requirement_id e input»
- (B) «ambos ficheros nombran requirement_id e input como campos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Three CLP notations are one decision

El lector A registra «JSON trae una decisión con tres divergencias miembro y razón same-policy-across-scenarios» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Three CLP notations are one decision»?**
- (A) «JSON trae una decisión con tres divergencias miembro y razón same-policy-across-scenarios»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The figures are never diluted

El lector A describe el efecto como «cada miembro conserva su lectura literal con cifras»; el lector B describe el efecto como «el informe muestra cada cifra literal en su fila». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The figures are never diluted» es la correcta?**
- (A) «cada miembro conserva su lectura literal con cifras»
- (B) «el informe muestra cada cifra literal en su fila»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Without a requirement the rest of the scenario must match

El lector A describe el efecto como «quedan separados si side_effects difieren, juntos si comparten requirement_id»; el lector B describe el efecto como «con side_effects distintos son dos decisiones, no una». Similitud de contenido 0.17, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Without a requirement the rest of the scenario must match» es la correcta?**
- (A) «quedan separados si side_effects difieren, juntos si comparten requirement_id»
- (B) «con side_effects distintos son dos decisiones, no una»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A reader-backed option resolves every member literally

El lector A registra «resolutions.answers se rellena por cada miembro» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A reader-backed option resolves every member literally»?**
- (A) «resolutions.answers se rellena por cada miembro»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Each question appears once

El lector A describe el efecto como «la pregunta de la decisión sale una sola vez»; el lector B describe el efecto como «la pregunta aparece una sola vez en el informe». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Each question appears once» es la correcta?**
- (A) «la pregunta de la decisión sale una sola vez»
- (B) «la pregunta aparece una sola vez en el informe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Members are evidence, not questions

El lector A describe el efecto como «evidencia lista dureza y detalle sin preguntas ni opciones»; el lector B describe el efecto como «cada divergencia muestra dureza y detalle, sin opciones». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Members are evidence, not questions» es la correcta?**
- (A) «evidencia lista dureza y detalle sin preguntas ni opciones»
- (B) «cada divergencia muestra dureza y detalle, sin opciones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The old sections are gone

El lector A registra «el informe deja de emitir Divergencias duras, blandas y Decisiones agrupadas» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The old sections are gone»?**
- (A) «el informe deja de emitir Divergencias duras, blandas y Decisiones agrupadas»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Without a history every decision is pending

El lector A describe el efecto como «todas las decisiones salen pending sin fuente de historial»; el lector B describe el efecto como «todas las decisiones salen pending, decisions_source es null». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Without a history every decision is pending» es la correcta?**
- (A) «todas las decisiones salen pending sin fuente de historial»
- (B) «todas las decisiones salen pending, decisions_source es null»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A matching resolved answer is answered

El lector A registra «se añade previous con at, answer y resolution» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A matching resolved answer is answered»?**
- (A) «se añade previous con at, answer y resolution»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A matching resolved answer is answered

El lector A describe el efecto como «la decisión sale answered y deja de contar como pendiente»; el lector B describe el efecto como «sale answered con previous y no cuenta en pendientes». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A matching resolved answer is answered» es la correcta?**
- (A) «la decisión sale answered y deja de contar como pendiente»
- (B) «sale answered con previous y no cuenta en pendientes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A clarification does not close

El lector A registra «se añade previous con la aclaración anterior» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A clarification does not close»?**
- (A) «se añade previous con la aclaración anterior»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A clarification does not close

El lector A describe el efecto como «la decisión sigue pending mostrando lo ya contestado»; el lector B describe el efecto como «sigue pending y previous muestra lo contestado antes». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A clarification does not close» es la correcta?**
- (A) «la decisión sigue pending mostrando lo ya contestado»
- (B) «sigue pending y previous muestra lo contestado antes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The latest entry with the fingerprint wins

El lector A registra «previous refleja la entrada posterior, no la selected anterior» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The latest entry with the fingerprint wins»?**
- (A) «previous refleja la entrada posterior, no la selected anterior»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An equivalence that left the divergence hard is stale

El lector A registra «se añade stale_reason explicando el motivo» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An equivalence that left the divergence hard is stale»?**
- (A) «se añade stale_reason explicando el motivo»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A legacy chosen option is migrated

El lector A describe el efecto como «la decisión sale answered marcando la migración»; el lector B describe el efecto como «sale answered con previous.migrated en true». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A legacy chosen option is migrated» es la correcta?**
- (A) «la decisión sale answered marcando la migración»
- (B) «sale answered con previous.migrated en true»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A legacy hand-written answer is unclassified

El lector A describe el efecto como «la decisión sale unclassified mostrando la respuesta antigua»; el lector B describe el efecto como «sale unclassified mostrando previous.answer». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A legacy hand-written answer is unclassified» es la correcta?**
- (A) «la decisión sale unclassified mostrando la respuesta antigua»
- (B) «sale unclassified mostrando previous.answer»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Changed options make the earlier answer stale

El lector A describe el efecto como «la decisión sale stale indicando qué cambió»; el lector B describe el efecto como «sale stale y stale_reason dice qué opción cambió». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Changed options make the earlier answer stale» es la correcta?**
- (A) «la decisión sale stale indicando qué cambió»
- (B) «sale stale y stale_reason dice qué opción cambió»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Only three resolutions close

El lector A describe el efecto como «el texto declara que sólo tres resoluciones cierran la decisión»; el lector B describe el efecto como «declara que sólo selected, equivalent y custom-resolved cierran». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only three resolutions close» es la correcta?**
- (A) «el texto declara que sólo tres resoluciones cierran la decisión»
- (B) «declara que sólo selected, equivalent y custom-resolved cierran»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A clarification gets one more call

El lector A describe el efecto como «el texto declara una llamada extra con la misma pregunta»; el lector B describe el efecto como «declara una llamada adicional con la misma pregunta». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A clarification gets one more call» es la correcta?**
- (A) «el texto declara una llamada extra con la misma pregunta»
- (B) «declara una llamada adicional con la misma pregunta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An answer that does not fit every member is asked per member

El lector A describe el efecto como «el texto declara preguntar por miembro con su propio answer»; el lector B describe el efecto como «declara preguntar por miembro, cada uno con su answer». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An answer that does not fit every member is asked per member» es la correcta?**
- (A) «el texto declara preguntar por miembro con su propio answer»
- (B) «declara preguntar por miembro, cada uno con su answer»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Answered decisions are not asked again

El lector A describe el efecto como «el texto declara pasar el historial y no repreguntar lo answered»; el lector B describe el efecto como «declara no repreguntar answered y mostrar previous en stale». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Answered decisions are not asked again» es la correcta?**
- (A) «el texto declara pasar el historial y no repreguntar lo answered»
- (B) «declara no repreguntar answered y mostrar previous en stale»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every divergence belongs to exactly one decision

El lector A describe el efecto como «cada índice de divergences pertenece a una sola decisión»; el lector B describe el efecto como «cada divergencia figura en exactamente una decisión». Similitud de contenido 0.12, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every divergence belongs to exactly one decision» es la correcta?**
- (A) «cada índice de divergences pertenece a una sola decisión»
- (B) «cada divergencia figura en exactamente una decisión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict does not move

El lector A describe el efecto como «counts y veredicto no cambian, decisions trae una entrada»; el lector B describe el efecto como «counts, veredicto diverged y una sola decisión, sin cambios». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict does not move» es la correcta?**
- (A) «counts y veredicto no cambian, decisions trae una entrada»
- (B) «counts, veredicto diverged y una sola decisión, sin cambios»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A grouped question names its scenarios and confronts the readings

El lector A registra «options incluye la opción de que no hay divergencia real» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A grouped question names its scenarios and confronts the readings»?**
- (A) «options incluye la opción de que no hay divergencia real»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A two-field option carries both fields of its reader

El lector A describe el efecto como «la opción enlaza efecto y efectos colaterales del mismo lector»; el lector B describe el efecto como «la opción combina efecto y efectos colaterales del lector». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A two-field option carries both fields of its reader» es la correcta?**
- (A) «la opción enlaza efecto y efectos colaterales del mismo lector»
- (B) «la opción combina efecto y efectos colaterales del lector»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The report lists every decision once

El lector A describe el efecto como «el informe trae la decisión una vez con razón y escenarios»; el lector B describe el efecto como «aparece una sola vez con su razón y escenarios». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The report lists every decision once» es la correcta?**
- (A) «el informe trae la decisión una vez con razón y escenarios»
- (B) «aparece una sola vez con su razón y escenarios»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One decision per call

El lector A describe el efecto como «el texto declara preguntar una decisión por llamada en orden»; el lector B describe el efecto como «declara una decisión por llamada, en el orden del informe». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One decision per call» es la correcta?**
- (A) «el texto declara preguntar una decisión por llamada en orden»
- (B) «declara una decisión por llamada, en el orden del informe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every member is recorded with its own answer

El lector A describe el efecto como «el texto declara anotar decisions.json por miembro con su answer»; el lector B describe el efecto como «declara anotar una entrada por miembro con su answer». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every member is recorded with its own answer» es la correcta?**
- (A) «el texto declara anotar decisions.json por miembro con su answer»
- (B) «declara anotar una entrada por miembro con su answer»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-022 — R-DIV-016 y R-DIV-023 obligan a escribir una entrada por divergencia miembro y todas llevan la misma `fingerprint` de la decisión, mientras R-DIV-022 decide el `status` con «la entrada más reciente con esa huella —la última de la lista—»: si tras un `needs-clarification` se pregunta por miembro y uno se cierra con `custom-resolved` mientras otro queda en `changes-contract`, basta con que la entrada cerrada quede después en el fichero para que toda la decisión salga `answered`; la skill no vuelve a preguntar (R-DIV-023) y el miembro que contradecía el acta o el delta desaparece de la entrevista para siempre, sin que nadie lo remita a /venoxia:specify.
- **[medium]** R-DIV-023 — R-DIV-023 sólo prohíbe preguntar las decisiones `answered` y para las `stale` exige «enseñar `previous`», sin exigir volver a preguntarlas: una skill que imprime la respuesta anterior y sigue adelante cumple la frase, de modo que una decisión que el propio script marcó obsoleta —porque la pregunta o las opciones cambiaron, o porque el `equivalent` anterior dejó viva una divergencia dura— nunca se re-plantea; con divergencias blandas el cambio se sella como `validated` arrastrando en el delta una respuesta a una pregunta que ya no existe, y sólo se arregla editando `decisions.json` a mano.

## Escenarios que convergen · 15

- Different requirements stay apart
- A reader who changes policy breaks the group
- Identical readings keep their old reason
- The equivalent option resolves nothing
- Members carry their hardness
- The rest of the report does not move
- The verdict ignores the history
- The five resolutions are named
- A contract change is routed, not closed
- The skill announces the running version
- The root decision is explained once
- The skill never groups on its own
- The three JSON reports name the version
- The text report names the version
- A missing manifest does not break the report
