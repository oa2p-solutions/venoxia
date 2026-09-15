# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-adaptive-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 45
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 31 divergencias blandas sobre los 45 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 31

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Only a missing or conflicting slot is asked

El lector A describe el efecto como «declara que sólo se pregunta si la casilla está missing o conflicting»; el lector B describe el efecto como «El SKILL.md declara que sólo se pregunta si falta o hay conflicto». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only a missing or conflicting slot is asked» es la correcta?**
- (A) «declara que sólo se pregunta si la casilla está missing o conflicting»
- (B) «El SKILL.md declara que sólo se pregunta si falta o hay conflicto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An inferred slot needs the user's confirmation

El lector A describe el efecto como «declara que inferred pasa a known sólo si el usuario confirma»; el lector B describe el efecto como «El SKILL.md declara que inferred pasa a known sólo con confirmación». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inferred slot needs the user's confirmation» es la correcta?**
- (A) «declara que inferred pasa a known sólo si el usuario confirma»
- (B) «El SKILL.md declara que inferred pasa a known sólo con confirmación»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The modes are named

El lector A describe el efecto como «nombra los tres modos de entrada y el de retomar acta»; el lector B describe el efecto como «El SKILL.md nombra los tres modos y el de retomar». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The modes are named» es la correcta?**
- (A) «nombra los tres modos de entrada y el de retomar acta»
- (B) «El SKILL.md nombra los tres modos y el de retomar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The inference mark is the literal comment

El lector A describe el efecto como «declara que la marca de inferencia es <!-- inferred -->»; el lector B describe el efecto como «El SKILL.md declara que la marca es <!-- inferred -->». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The inference mark is the literal comment» es la correcta?**
- (A) «declara que la marca de inferencia es <!-- inferred -->»
- (B) «El SKILL.md declara que la marca es <!-- inferred -->»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Resuming wins over an existing project

El lector A describe el efecto como «declara que con charter.md en disco el modo es retomar»; el lector B describe el efecto como «El SKILL.md declara que retomar el acta gana sobre proyecto existente». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Resuming wins over an existing project» es la correcta?**
- (A) «declara que con charter.md en disco el modo es retomar»
- (B) «El SKILL.md declara que retomar el acta gana sobre proyecto existente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The draft lives in the conversation until it is approved

El lector A describe el efecto como «declara que el borrador se enseña sin escribirse hasta aprobar»; el lector B describe el efecto como «El SKILL.md declara que el borrador no se escribe hasta aprobarse». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The draft lives in the conversation until it is approved» es la correcta?**
- (A) «declara que el borrador se enseña sin escribirse hasta aprobar»
- (B) «El SKILL.md declara que el borrador no se escribe hasta aprobarse»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The explained mode needs three slots said by the user

El lector A describe el efecto como «declara que exige purpose, primary_user y first_capability del usuario»; el lector B describe el efecto como «El SKILL.md declara que exige tres casillas dichas por el usuario». Similitud de contenido 0.23, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The explained mode needs three slots said by the user» es la correcta?**
- (A) «declara que exige purpose, primary_user y first_capability del usuario»
- (B) «El SKILL.md declara que exige tres casillas dichas por el usuario»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The vague mode continues with what to remove first

El lector A describe el efecto como «contiene literalmente la pregunta de qué eliminaría primero»; el lector B describe el efecto como «El SKILL.md contiene literalmente la pregunta por qué eliminar primero». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The vague mode continues with what to remove first» es la correcta?**
- (A) «contiene literalmente la pregunta de qué eliminaría primero»
- (B) «El SKILL.md contiene literalmente la pregunta por qué eliminar primero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The fixed rounds are gone

El lector A describe el efecto como «no contiene ningún encabezado que empiece por Tanda»; el lector B describe el efecto como «El SKILL.md ya no contiene encabezados «### Tanda»». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The fixed rounds are gone» es la correcta?**
- (A) «no contiene ningún encabezado que empiece por Tanda»
- (B) «El SKILL.md ya no contiene encabezados «### Tanda»»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The reading is reconstructed from disk

El lector A describe el efecto como «declara que reconstruye propósito, usuarios y capabilities del repo»; el lector B describe el efecto como «El SKILL.md declara que la lectura se reconstruye desde el repositorio». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reading is reconstructed from disk» es la correcta?**
- (A) «declara que reconstruye propósito, usuarios y capabilities del repo»
- (B) «El SKILL.md declara que la lectura se reconstruye desde el repositorio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Priority is adoption order, said once

El lector A describe el efecto como «declara que la prioridad es orden de adopción, explicado una vez»; el lector B describe el efecto como «El SKILL.md declara que la prioridad se explica una sola vez». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Priority is adoption order, said once» es la correcta?**
- (A) «declara que la prioridad es orden de adopción, explicado una vez»
- (B) «El SKILL.md declara que la prioridad se explica una sola vez»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One synthesis and one correction

El lector A describe el efecto como «declara síntesis única de hechos y apuestas con una corrección»; el lector B describe el efecto como «El SKILL.md declara una síntesis única con una corrección general». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One synthesis and one correction» es la correcta?**
- (A) «declara síntesis única de hechos y apuestas con una corrección»
- (B) «El SKILL.md declara una síntesis única con una corrección general»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The per-section question is gone

El lector A describe el efecto como «no repite la pregunta de observado o supuesto por sección»; el lector B describe el efecto como «El SKILL.md declara que ya no se pregunta por sección». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The per-section question is gone» es la correcta?**
- (A) «no repite la pregunta de observado o supuesto por sección»
- (B) «El SKILL.md declara que ya no se pregunta por sección»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No bet is fabricated

El lector A registra «se conserva el aviso C20» y «queda registrada la afirmación del usuario» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «No bet is fabricated»?**
- (A) «se conserva el aviso C20» y «queda registrada la afirmación del usuario»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: No bet is fabricated

El lector A describe el efecto como «declara que si todo es observado no se escribe ninguna apuesta»; el lector B describe el efecto como «El SKILL.md declara que no se fabrica ninguna apuesta si todo es observado». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No bet is fabricated» es la correcta?**
- (A) «declara que si todo es observado no se escribe ninguna apuesta»
- (B) «El SKILL.md declara que no se fabrica ninguna apuesta si todo es observado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The claim is recorded inside the charter

El lector A registra «comentario añadido bajo ## Bets del acta» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The claim is recorded inside the charter»?**
- (A) «comentario añadido bajo ## Bets del acta»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The claim is recorded inside the charter

El lector A describe el efecto como «declara que la afirmación se registra como comentario con fecha»; el lector B describe el efecto como «El SKILL.md declara que la afirmación se registra bajo ## Bets con fecha». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The claim is recorded inside the charter» es la correcta?**
- (A) «declara que la afirmación se registra como comentario con fecha»
- (B) «El SKILL.md declara que la afirmación se registra bajo ## Bets con fecha»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The minimum is listed

El lector A describe el efecto como «enumera el mínimo de casillas necesarias para cerrar el acta»; el lector B describe el efecto como «El SKILL.md enumera los elementos mínimos para ofrecer el cierre». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The minimum is listed» es la correcta?**
- (A) «enumera el mínimo de casillas necesarias para cerrar el acta»
- (B) «El SKILL.md enumera los elementos mínimos para ofrecer el cierre»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The draft is offered for approval

El lector A describe el efecto como «declara que al llegar al mínimo se ofrece aprobar o profundizar»; el lector B describe el efecto como «El SKILL.md declara que al llegar al mínimo se ofrece el borrador». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The draft is offered for approval» es la correcta?**
- (A) «declara que al llegar al mínimo se ofrece aprobar o profundizar»
- (B) «El SKILL.md declara que al llegar al mínimo se ofrece el borrador»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Ambiguity is the only reason to ask

El lector A describe el efecto como «declara que sólo pregunta ante ambigüedad que bloquea el paso»; el lector B describe el efecto como «El SKILL.md declara que sólo una ambigüedad justifica preguntar en preparación». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Ambiguity is the only reason to ask» es la correcta?**
- (A) «declara que sólo pregunta ante ambigüedad que bloquea el paso»
- (B) «El SKILL.md declara que sólo una ambigüedad justifica preguntar en preparación»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No generic list of conventions

El lector A describe el efecto como «declara que propone convenciones sólo si son relevantes»; el lector B describe el efecto como «El SKILL.md declara que no se presenta una lista genérica de convenciones». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic list of conventions» es la correcta?**
- (A) «declara que propone convenciones sólo si son relevantes»
- (B) «El SKILL.md declara que no se presenta una lista genérica de convenciones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The npm placeholder is not a candidate

El lector A describe el efecto como «declara que el marcador no test specified no es candidato»; el lector B describe el efecto como «El SKILL.md declara que el marcador de npm init no es candidato». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The npm placeholder is not a candidate» es la correcta?**
- (A) «declara que el marcador no test specified no es candidato»
- (B) «El SKILL.md declara que el marcador de npm init no es candidato»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One question with three intentions

El lector A describe el efecto como «declara que pregunta continuar, revisar o resolver una apuesta»; el lector B describe el efecto como «El SKILL.md declara una pregunta con tres opciones posibles». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One question with three intentions» es la correcta?**
- (A) «declara que pregunta continuar, revisar o resolver una apuesta»
- (B) «El SKILL.md declara una pregunta con tres opciones posibles»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Never bet by bet first

El lector A describe el efecto como «declara que no pregunta apuesta por apuesta antes de decidir»; el lector B describe el efecto como «El SKILL.md declara que no se pregunta apuesta por apuesta primero». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Never bet by bet first» es la correcta?**
- (A) «declara que no pregunta apuesta por apuesta antes de decidir»
- (B) «El SKILL.md declara que no se pregunta apuesta por apuesta primero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No mtime

El lector A describe el efecto como «no contiene la palabra mtime»; el lector B describe el efecto como «El SKILL.md ya no contiene la palabra mtime». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No mtime» es la correcta?**
- (A) «no contiene la palabra mtime»
- (B) «El SKILL.md ya no contiene la palabra mtime»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A charter that fails the linter is shown with its blockers

El lector A describe el efecto como «declara que un acta que falla el linter se muestra con bloqueos»; el lector B describe el efecto como «El SKILL.md declara que un acta con bloqueos se enseña antes de preguntar». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A charter that fails the linter is shown with its blockers» es la correcta?**
- (A) «declara que un acta que falla el linter se muestra con bloqueos»
- (B) «El SKILL.md declara que un acta con bloqueos se enseña antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A marked line is an error

El lector A registra «se genera un hallazgo C21» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A marked line is an error»?**
- (A) «se genera un hallazgo C21»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A marked line is an error

El lector A describe el efecto como «salta C21 como error sobre la línea con la marca sin confirmar»; el lector B describe el efecto como «El linter marca C21 como error sobre esa línea». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A marked line is an error» es la correcta?**
- (A) «salta C21 como error sobre la línea con la marca sin confirmar»
- (B) «El linter marca C21 como error sobre esa línea»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Each marked line has its own finding

El lector A registra «se genera un hallazgo C21 por línea» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Each marked line has its own finding»?**
- (A) «se genera un hallazgo C21 por línea»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Each marked line has its own finding

El lector A describe el efecto como «salta un C21 distinto por cada línea marcada»; el lector B describe el efecto como «El linter marca un C21 por cada línea marcada». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Each marked line has its own finding» es la correcta?**
- (A) «salta un C21 distinto por cada línea marcada»
- (B) «El linter marca un C21 por cada línea marcada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A charter without marks is untouched

El lector A describe el efecto como «no salta ningún hallazgo C21»; el lector B describe el efecto como «El linter no genera ningún hallazgo C21». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A charter without marks is untouched» es la correcta?**
- (A) «no salta ningún hallazgo C21»
- (B) «El linter no genera ningún hallazgo C21»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-009 — Nada en el delta dice cuándo una casilla puede etiquetarse `inferred` en vez de `missing`, y las preguntas sólo se plantean sobre `missing` o `conflicting`: una skill que marca las nueve casillas como `inferred` a partir de la primera frase del usuario cumple el requisito y no formula ni una sola pregunta, produciendo un acta —propósito, usuario, `Done when`, no-alcance— escrita íntegramente por el modelo y presentada como el contrato del proyecto.
- **[high]** R-CHL-014 — La preparación sólo puede preguntar «ante una ambigüedad que impida ejecutar el paso siguiente» y sólo excluye como candidato el marcador de `npm init`: con un único candidato en el manifiesto (`"test": "exit 0"`, un target de Make vacío, un script que borra la base de datos de desarrollo) la skill lo graba como `test_command` del oráculo sin confirmación del usuario y sin ejecutarlo, de modo que todos los requisitos salen verdes para siempre —o se ejecuta un comando destructivo en cada `/venoxia:verify`— sin que nadie lo haya aprobado.
- **[high]** R-CHL-015 — El requisito obliga a mantener «empezar de cero» como respuesta escrita al retomar, pero ninguna frase gobierna qué pasa con el acta existente: una implementación que, ante ese texto libre, sobrescribe `.venoxia/charter.md` en el acto cumple al pie de la letra y destruye sin confirmación ni copia el propósito, las apuestas y las decisiones acumuladas del proyecto.
- **[medium]** R-CHL-016 — La única comprobación sobre las inferencias es que el acta escrita no conserve la marca `<!-- inferred -->`, así que la vía más barata y plenamente conforme es borrar las marcas al volcar el borrador aprobado: el acta en disco no distingue ninguna línea inferida de una dicha por el usuario, C21 nunca puede saltar sobre un acta escrita por la skill y sólo castiga a quien anote a mano lo que supuso.

## Escenarios que convergen · 18

- The nine slots are named
- The five states are named
- The slot is named before the question
- One answer refreshes the whole map
- A correction invalidates only its dependants
- An explained product is drafted first
- Inferences are marked in the draft
- The vague mode opens with the last real case
- The next change is asked
- Disk facts are not asked
- Revisit and fatal only for open bets
- No interview on its own initiative
- Preparation comes after writing the charter
- The test command is detected before it is asked
- The generic table is gone
- The detected command is not trusted blindly
- The state is summarised first
- Bets are grouped in one view
