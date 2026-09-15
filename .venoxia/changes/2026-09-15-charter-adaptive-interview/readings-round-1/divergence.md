# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-adaptive-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 36
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 15 divergencias blandas sobre los 36 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 15

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The nine slots are named

El lector A describe el efecto como «el SKILL.md nombra las nueve casillas del mapa»; el lector B describe el efecto como «el skill nombra las nueve casillas de cobertura». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The nine slots are named» es la correcta?**
- (A) «el SKILL.md nombra las nueve casillas del mapa»
- (B) «el skill nombra las nueve casillas de cobertura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Only a missing or conflicting slot is asked

El lector A describe el efecto como «declara que sólo se pregunta si falta o hay conflicto»; el lector B describe el efecto como «el skill declara preguntar sólo si missing o conflicting». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only a missing or conflicting slot is asked» es la correcta?**
- (A) «declara que sólo se pregunta si falta o hay conflicto»
- (B) «el skill declara preguntar sólo si missing o conflicting»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A correction invalidates only its dependants

El lector A describe el efecto como «declara que la corrección invalida sólo sus dependientes»; el lector B describe el efecto como «el skill declara invalidar sólo casillas dependientes». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A correction invalidates only its dependants» es la correcta?**
- (A) «declara que la corrección invalida sólo sus dependientes»
- (B) «el skill declara invalidar sólo casillas dependientes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The modes are named

El lector A describe el efecto como «nombra los tres modos de entrada y retomar acta»; el lector B describe el efecto como «el skill nombra los tres modos y el de retomar». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The modes are named» es la correcta?**
- (A) «nombra los tres modos de entrada y retomar acta»
- (B) «el skill nombra los tres modos y el de retomar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The vague mode opens with the last real case

El lector A describe el efecto como «contiene literalmente la pregunta sobre la última vez»; el lector B describe el efecto como «el skill contiene literalmente la pregunta sobre el último caso». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The vague mode opens with the last real case» es la correcta?**
- (A) «contiene literalmente la pregunta sobre la última vez»
- (B) «el skill contiene literalmente la pregunta sobre el último caso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The reading is reconstructed from disk

El lector A describe el efecto como «declara que reconstruye la lectura del repositorio y la presenta»; el lector B describe el efecto como «el skill declara reconstruir la lectura desde el repositorio». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reading is reconstructed from disk» es la correcta?**
- (A) «declara que reconstruye la lectura del repositorio y la presenta»
- (B) «el skill declara reconstruir la lectura desde el repositorio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One synthesis and one correction

El lector A describe el efecto como «declara una síntesis de hechos y apuestas con una corrección»; el lector B describe el efecto como «el skill declara una síntesis única con razón y una corrección». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One synthesis and one correction» es la correcta?**
- (A) «declara una síntesis de hechos y apuestas con una corrección»
- (B) «el skill declara una síntesis única con razón y una corrección»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The per-section question is gone

El lector A describe el efecto como «ya no repite la pregunta de observado o supuesto por sección»; el lector B describe el efecto como «el skill declara no repetir la pregunta por sección». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The per-section question is gone» es la correcta?**
- (A) «ya no repite la pregunta de observado o supuesto por sección»
- (B) «el skill declara no repetir la pregunta por sección»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No bet is fabricated

El lector A describe el efecto como «declara que si todo es observado no inventa ninguna apuesta»; el lector B describe el efecto como «el skill declara no escribir apuesta, conservar C20 y registrar la afirmación». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No bet is fabricated» es la correcta?**
- (A) «declara que si todo es observado no inventa ninguna apuesta»
- (B) «el skill declara no escribir apuesta, conservar C20 y registrar la afirmación»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The minimum is listed

El lector A describe el efecto como «enumera los elementos mínimos que exige el borrador»; el lector B describe el efecto como «el skill enumera los elementos mínimos del acta». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The minimum is listed» es la correcta?**
- (A) «enumera los elementos mínimos que exige el borrador»
- (B) «el skill enumera los elementos mínimos del acta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The draft is offered for approval

El lector A describe el efecto como «declara que al alcanzar el mínimo ofrece aprobar o profundizar»; el lector B describe el efecto como «el skill declara presentar el borrador y preguntar si aprobarlo». Similitud de contenido 0.09, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The draft is offered for approval» es la correcta?**
- (A) «declara que al alcanzar el mínimo ofrece aprobar o profundizar»
- (B) «el skill declara presentar el borrador y preguntar si aprobarlo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Ambiguity is the only reason to ask

El lector A describe el efecto como «declara que sólo pregunta ante ambigüedad que bloquea el paso»; el lector B describe el efecto como «el skill declara preguntar sólo ante ambigüedad bloqueante». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Ambiguity is the only reason to ask» es la correcta?**
- (A) «declara que sólo pregunta ante ambigüedad que bloquea el paso»
- (B) «el skill declara preguntar sólo ante ambigüedad bloqueante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One question with three intentions

El lector A describe el efecto como «declara una pregunta con tres opciones al retomar el acta»; el lector B describe el efecto como «el skill declara una pregunta única con tres opciones». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One question with three intentions» es la correcta?**
- (A) «declara una pregunta con tres opciones al retomar el acta»
- (B) «el skill declara una pregunta única con tres opciones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A marked line is an error

El lector B registra «se registra un hallazgo C21» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A marked line is an error»?**
- (A) «se registra un hallazgo C21»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A marked line is an error

El lector A describe el efecto como «marca la línea con inferencia sin confirmar como error C21»; el lector B describe el efecto como «salta el hallazgo C21 como error sobre esa línea». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A marked line is an error» es la correcta?**
- (A) «marca la línea con inferencia sin confirmar como error C21»
- (B) «salta el hallazgo C21 como error sobre esa línea»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-010 — R-CHL-010 obliga a «redactar el acta completa» antes de la primera pregunta con un proyecto existente, y nada ordena ese modo frente al de retomar acta de R-CHL-015: una implementación que, ante un repositorio que ya tiene código y `.venoxia/charter.md`, clasifica «proyecto existente» y reescribe el acta entera desde el disco cumple la frase y destruye las apuestas ya acordadas con su `revisit` y su `fatal`, que nadie puede reconstruir.
- **[high]** R-CHL-010 — R-CHL-010 exige «inferencias marcadas» sin fijar la sintaxis de la marca, mientras que C21 (R-CHL-016) sólo salta ante el literal `<!-- inferred -->`: una implementación que marque las inferencias como «(inferido)» en la prosa cumple los dos escenarios y anula por completo la única red que impide que una inferencia sin confirmar quede en el acta como acuerdo y pase el linter en verde.
- **[high]** R-CHL-014 — R-CHL-014 manda detectar el comando de pruebas en el repositorio y preguntar «sólo ante una ambigüedad que impida ejecutar el paso siguiente»: una implementación que toma el primer candidato del manifiesto (por ejemplo un `npm test` que sale 0 sin ejecutar nada) y lo escribe en `venoxia.json` sin ejecutarlo ni confirmarlo cumple la frase —no hay ambigüedad, hay un único candidato— y deja todos los veredictos del oráculo apoyados en un comando que no prueba nada.
- **[medium]** R-CHL-009 — R-CHL-009 prohíbe plantear una pregunta cuando la casilla no está en `missing` o `conflicting`, y nada acota con qué evidencia se puede declarar una casilla `inferred`: una implementación que infiera las nueve casillas de las primeras frases del usuario no formula ni una sola pregunta y produce un acta íntegramente inventada; la entrevista adaptativa se convierte en ninguna entrevista.

## Escenarios que convergen · 22

- The five states are named
- The slot is named before the question
- One answer refreshes the whole map
- An explained product is drafted first
- Inferences are marked in the draft
- The vague mode continues with what to remove first
- The fixed rounds are gone
- The next change is asked
- Disk facts are not asked
- Priority is adoption order, said once
- Revisit and fatal only for open bets
- No interview on its own initiative
- Preparation comes after writing the charter
- The test command is detected before it is asked
- No generic list of conventions
- The generic table is gone
- The state is summarised first
- Bets are grouped in one view
- Never bet by bet first
- No mtime
- Each marked line has its own finding
- A charter without marks is untouched
