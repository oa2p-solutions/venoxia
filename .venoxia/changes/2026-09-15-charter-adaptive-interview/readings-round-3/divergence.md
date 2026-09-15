# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-adaptive-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 43
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 8 divergencias blandas sobre los 43 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 8

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Only a missing or conflicting slot is asked

El lector A describe el efecto como «SKILL.md declara que sólo pregunta missing o conflicting»; el lector B describe el efecto como «SKILL.md declara que sólo se pregunta si falta o hay conflicto». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only a missing or conflicting slot is asked» es la correcta?**
- (A) «SKILL.md declara que sólo pregunta missing o conflicting»
- (B) «SKILL.md declara que sólo se pregunta si falta o hay conflicto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Resuming wins over an existing project

El lector A describe el efecto como «SKILL.md declara que retomar gana sobre proyecto existente»; el lector B describe el efecto como «SKILL.md declara que con charter.md en disco se retoma el acta». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Resuming wins over an existing project» es la correcta?**
- (A) «SKILL.md declara que retomar gana sobre proyecto existente»
- (B) «SKILL.md declara que con charter.md en disco se retoma el acta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The explained mode needs three slots said by the user

El lector A describe el efecto como «SKILL.md declara que exige tres casillas dichas por usuario»; el lector B describe el efecto como «SKILL.md declara que tres casillas las dice el usuario, no se infieren». Similitud de contenido 0.55, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The explained mode needs three slots said by the user» es la correcta?**
- (A) «SKILL.md declara que exige tres casillas dichas por usuario»
- (B) «SKILL.md declara que tres casillas las dice el usuario, no se infieren»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The per-section question is gone

El lector A describe el efecto como «SKILL.md declara que no repite la pregunta por sección»; el lector B describe el efecto como «SKILL.md declara que ya no pregunta lo has visto o supuesto por sección». Similitud de contenido 0.55, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The per-section question is gone» es la correcta?**
- (A) «SKILL.md declara que no repite la pregunta por sección»
- (B) «SKILL.md declara que ya no pregunta lo has visto o supuesto por sección»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The minimum is listed

El lector A describe el efecto como «SKILL.md enumera el mínimo de casillas para cerrar»; el lector B describe el efecto como «SKILL.md enumera los elementos mínimos del mapa de cobertura». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The minimum is listed» es la correcta?**
- (A) «SKILL.md enumera el mínimo de casillas para cerrar»
- (B) «SKILL.md enumera los elementos mínimos del mapa de cobertura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Preparation comes after writing the charter

El lector A describe el efecto como «la sección de preparación aparece tras escribir el acta»; el lector B describe el efecto como «la sección de preparación aparece después de la del acta y linter». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Preparation comes after writing the charter» es la correcta?**
- (A) «la sección de preparación aparece tras escribir el acta»
- (B) «la sección de preparación aparece después de la del acta y linter»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No generic list of conventions

El lector A describe el efecto como «SKILL.md declara que no presenta lista genérica de convenciones»; el lector B describe el efecto como «SKILL.md declara que una convención se propone sólo si es relevante». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic list of conventions» es la correcta?**
- (A) «SKILL.md declara que no presenta lista genérica de convenciones»
- (B) «SKILL.md declara que una convención se propone sólo si es relevante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A marked line is an error

El lector A registra «genera hallazgo C21 con mensaje sobre inferencia sin confirmar» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A marked line is an error»?**
- (A) «genera hallazgo C21 con mensaje sobre inferencia sin confirmar»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-009 — R-CHL-009 hace pasar una casilla `inferred` a `known` con «la confirmación general del borrador», es decir un único sí a un acta completa: una implementación literal redacta con el modelo el propósito, el usuario principal, el no-alcance y las apuestas, las marca todas `<!-- inferred -->`, y con ese único sí las convierte en acuerdos y borra las marcas (C21 obliga a que ninguna sobreviva), de modo que el acta en disco no distingue lo que dijo el usuario de lo que inventó el modelo y no queda registro de ello en ninguna parte.
- **[medium]** R-CHL-010 — R-CHL-010 obliga a que el modo sea «retomar un acta» por la sola existencia de `.venoxia/charter.md`, sin exigir que tenga contenido útil: con un fichero vacío o un esqueleto copiado, la skill entra en R-CHL-015 y sólo ofrece continuar con la siguiente capability, revisar una sección o resolver una apuesta, ninguna de las cuales escribe un acta desde cero, y el usuario queda bloqueado sin ninguna vía declarada para volver a los tres modos de entrada.
- **[medium]** R-CHL-014 — R-CHL-014 manda detectar el comando de pruebas en el repositorio, prohíbe ejecutarlo en la preparación, sólo permite preguntar «ante una ambigüedad que impida ejecutar el paso siguiente» y excluye un único candidato falso (el marcador de `npm init`): una implementación literal escribe como oráculo del proyecto el primer comando que encuentre —un `make test` obsoleto o un script que sale 0 sin ejecutar nada— sin confirmarlo con el usuario, y todo el contrato de verificación pasa a apoyarse en un comando que no prueba nada.
- **[medium]** R-CHL-012 — R-CHL-012 exige, cuando el usuario afirma que todo está observado, dejar `## Bets` sin apuestas y «dejar registrada la afirmación» sin decir dónde: una línea en la conversación cumple la frase, así que el acta en disco queda con cero apuestas y sin rastro ni de los supuestos que la propia síntesis había clasificado ni de quién decidió descartarlos, y el aviso C20 pasa a ser un ruido permanente sin explicación.

## Escenarios que convergen · 35

- The nine slots are named
- The five states are named
- The slot is named before the question
- One answer refreshes the whole map
- A correction invalidates only its dependants
- An inferred slot needs the user's confirmation
- The modes are named
- An explained product is drafted first
- Inferences are marked in the draft
- The inference mark is the literal comment
- The draft lives in the conversation until it is approved
- The vague mode opens with the last real case
- The vague mode continues with what to remove first
- The fixed rounds are gone
- The reading is reconstructed from disk
- The next change is asked
- Disk facts are not asked
- Priority is adoption order, said once
- One synthesis and one correction
- Revisit and fatal only for open bets
- No bet is fabricated
- The draft is offered for approval
- No interview on its own initiative
- The test command is detected before it is asked
- Ambiguity is the only reason to ask
- The generic table is gone
- The detected command is not trusted blindly
- The npm placeholder is not a candidate
- The state is summarised first
- Bets are grouped in one view
- One question with three intentions
- Never bet by bet first
- No mtime
- Each marked line has its own finding
- A charter without marks is untouched
