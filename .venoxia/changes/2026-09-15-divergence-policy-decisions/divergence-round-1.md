# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-divergence-policy-decisions/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 40
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 19 divergencias blandas sobre los 40 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 19

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The reader agent asks for both fields

El lector A describe el efecto como «los ficheros declaran los campos requirement_id e input»; el lector B describe el efecto como «agents/reader.md y SKILL.md nombran requirement_id e input como campos». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reader agent asks for both fields» es la correcta?**
- (A) «los ficheros declaran los campos requirement_id e input»
- (B) «agents/reader.md y SKILL.md nombran requirement_id e input como campos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Different requirements stay apart

El lector A describe el efecto como «quedan como dos decisiones separadas»; el lector B describe el efecto como «dos escenarios con requirement_id distintos quedan en dos decisiones». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Different requirements stay apart» es la correcta?**
- (A) «quedan como dos decisiones separadas»
- (B) «dos escenarios con requirement_id distintos quedan en dos decisiones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A reader who changes policy breaks the group

El lector A describe el efecto como «ese escenario se convierte en otra decisión distinta»; el lector B describe el efecto como «el escenario con lectura distinta se separa como decisión propia». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A reader who changes policy breaks the group» es la correcta?**
- (A) «ese escenario se convierte en otra decisión distinta»
- (B) «el escenario con lectura distinta se separa como decisión propia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The equivalent option resolves nothing

El lector A describe el efecto como «reader vale null y answers queda vacío»; el lector B describe el efecto como «la opción equivalente lleva reader nulo y answers vacío». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The equivalent option resolves nothing» es la correcta?**
- (A) «reader vale null y answers queda vacío»
- (B) «la opción equivalente lleva reader nulo y answers vacío»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Members carry their hardness

El lector A describe el efecto como «cada miembro indica su dureza; la decisión toma la mayor»; el lector B describe el efecto como «cada miembro declara su dureza y la decisión la mayor». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Members carry their hardness» es la correcta?**
- (A) «cada miembro indica su dureza; la decisión toma la mayor»
- (B) «cada miembro declara su dureza y la decisión la mayor»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A clarification does not close

El lector A describe el efecto como «la decisión sigue pending y muestra lo contestado antes»; el lector B describe el efecto como «la decisión sigue pending y previous enseña lo contestado». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A clarification does not close» es la correcta?**
- (A) «la decisión sigue pending y muestra lo contestado antes»
- (B) «la decisión sigue pending y previous enseña lo contestado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A legacy hand-written answer is unclassified

El lector A describe el efecto como «la decisión sale unclassified mostrando la respuesta previa»; el lector B describe el efecto como «la decisión sale unclassified con previous.answer visible». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A legacy hand-written answer is unclassified» es la correcta?**
- (A) «la decisión sale unclassified mostrando la respuesta previa»
- (B) «la decisión sale unclassified con previous.answer visible»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Changed options make the earlier answer stale

El lector A describe el efecto como «la decisión sale stale con el motivo del cambio»; el lector B describe el efecto como «la decisión sale stale con stale_reason explicando el cambio». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Changed options make the earlier answer stale» es la correcta?**
- (A) «la decisión sale stale con el motivo del cambio»
- (B) «la decisión sale stale con stale_reason explicando el cambio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict ignores the history

El lector A describe el efecto como «counts, veredicto y código de salida no cambian»; el lector B describe el efecto como «counts, verdict y exit_code son iguales que sin historial». Similitud de contenido 0.09, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict ignores the history» es la correcta?**
- (A) «counts, veredicto y código de salida no cambian»
- (B) «counts, verdict y exit_code son iguales que sin historial»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A clarification gets one more call

El lector A describe el efecto como «declara una llamada extra con la misma pregunta y la información aportada»; el lector B describe el efecto como «SKILL.md declara una llamada adicional con la misma pregunta». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A clarification gets one more call» es la correcta?**
- (A) «declara una llamada extra con la misma pregunta y la información aportada»
- (B) «SKILL.md declara una llamada adicional con la misma pregunta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Answered decisions are not asked again

El lector A describe el efecto como «declara que no repregunta las decisiones ya respondidas»; el lector B describe el efecto como «SKILL.md declara pasar el historial y no repreguntar answered». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Answered decisions are not asked again» es la correcta?**
- (A) «declara que no repregunta las decisiones ya respondidas»
- (B) «SKILL.md declara pasar el historial y no repreguntar answered»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The skill announces the running version

El lector A describe el efecto como «declara que anuncia la versión del plugin al empezar»; el lector B describe el efecto como «SKILL.md declara anunciar la versión leída del manifiesto». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The skill announces the running version» es la correcta?**
- (A) «declara que anuncia la versión del plugin al empezar»
- (B) «SKILL.md declara anunciar la versión leída del manifiesto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every divergence belongs to exactly one decision

El lector A describe el efecto como «cada divergencia aparece en exactamente una decisión»; el lector B describe el efecto como «cada índice de divergences aparece en una sola decisión». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every divergence belongs to exactly one decision» es la correcta?**
- (A) «cada divergencia aparece en exactamente una decisión»
- (B) «cada índice de divergences aparece en una sola decisión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The verdict does not move

El lector A describe el efecto como «counts y veredicto siguen igual con una sola decisión»; el lector B describe el efecto como «counts, veredicto diverged y una sola entrada en decisions se mantienen». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The verdict does not move» es la correcta?**
- (A) «counts y veredicto siguen igual con una sola decisión»
- (B) «counts, veredicto diverged y una sola entrada en decisions se mantienen»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One decision per call

El lector A describe el efecto como «declara que pregunta una decisión por llamada, en orden»; el lector B describe el efecto como «SKILL.md declara una decisión por llamada en el orden del informe». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One decision per call» es la correcta?**
- (A) «declara que pregunta una decisión por llamada, en orden»
- (B) «SKILL.md declara una decisión por llamada en el orden del informe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The root decision is explained once

El lector A describe el efecto como «declara que explica la decisión raíz antes de preguntar»; el lector B describe el efecto como «SKILL.md declara explicar la decisión raíz una sola vez». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The root decision is explained once» es la correcta?**
- (A) «declara que explica la decisión raíz antes de preguntar»
- (B) «SKILL.md declara explicar la decisión raíz una sola vez»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every member is recorded with its own answer

El lector A describe el efecto como «declara que anota cada miembro con su propia respuesta»; el lector B describe el efecto como «SKILL.md declara anotar una entrada por miembro con su answer». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every member is recorded with its own answer» es la correcta?**
- (A) «declara que anota cada miembro con su propia respuesta»
- (B) «SKILL.md declara anotar una entrada por miembro con su answer»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The skill never groups on its own

El lector A describe el efecto como «declara que la skill no agrupa, sólo el script»; el lector B describe el efecto como «SKILL.md declara que la skill no agrupa preguntas por su cuenta». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The skill never groups on its own» es la correcta?**
- (A) «declara que la skill no agrupa, sólo el script»
- (B) «SKILL.md declara que la skill no agrupa preguntas por su cuenta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The text report names the version

El lector A describe el efecto como «el texto muestra Venoxia seguido de la versión»; el lector B describe el efecto como «la salida de texto contiene Venoxia seguido de la versión». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The text report names the version» es la correcta?**
- (A) «el texto muestra Venoxia seguido de la versión»
- (B) «la salida de texto contiene Venoxia seguido de la versión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-019 — Como R-DIV-018 deja `requirement_id` opcional y R-DIV-019 agrupa cuando las divergencias «comparten requirement_id —o ninguna lo trae—», una implementación literal funde en una sola decisión escenarios de requisitos sin relación (facturación y borrado de cuenta) en cuanto los lectores omiten el campo opcional; el usuario recibe una única pregunta con las opciones «lectura del lector A / del lector B / equivalentes», no puede responder distinto por miembro, y el texto elegido se escribe literalmente en el delta de un requisito sobre el que nunca se le preguntó.
- **[high]** R-DIV-022 — R-DIV-022 declara `answered` «cuando una entrada con la misma huella tiene resolution selected, equivalent o custom-resolved», sin exigir que sea la entrada más reciente: si el usuario reabre una decisión y la cierra con `changes-contract` o `needs-clarification`, la entrada anterior con `selected` sigue casando y la decisión sale `answered`, de modo que R-DIV-023 ya no la vuelve a plantear nunca y la respuesta que el usuario retiró queda como respuesta buena en el contrato.
- **[medium]** R-DIV-022 — Elegir la opción «las lecturas dicen lo mismo» produce, por R-DIV-020, `answers` vacío (nada se escribe en el delta), por R-DIV-022 la decisión queda `answered` con huella calculada sobre unas lecturas que ya no cambiarán, y por R-DIV-022 el veredicto ignora el historial: el script sigue devolviendo `diverged` y código 1 en cada pasada mientras R-DIV-023 obliga a no volver a preguntar esa decisión, dejando el change atascado sin poder pasar a `validated` y sin ninguna pregunta visible que lo desbloquee salvo editar `decisions.json` a mano.

## Escenarios que convergen · 21

- A reading without the new fields still parses
- The new fields reach the members
- Three CLP notations are one decision
- The figures are never diluted
- Identical readings keep their old reason
- A reader-backed option resolves every member literally
- Each question appears once
- Members are evidence, not questions
- The old sections are gone
- The rest of the report does not move
- Without a history every decision is pending
- A matching resolved answer is answered
- A legacy chosen option is migrated
- The five resolutions are named
- Only three resolutions close
- A contract change is routed, not closed
- A grouped question names its scenarios and confronts the readings
- A two-field option carries both fields of its reader
- The report lists every decision once
- The three JSON reports name the version
- A missing manifest does not break the report
