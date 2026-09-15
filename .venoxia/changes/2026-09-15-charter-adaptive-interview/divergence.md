# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-adaptive-interview/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 46
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 43 divergencias blandas sobre los 46 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 43

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The nine slots are named

El lector A describe el efecto como «la skill nombra las nueve casillas del mapa de cobertura»; el lector B describe el efecto como «el fichero nombra las nueve casillas del mapa». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The nine slots are named» es la correcta?**
- (A) «la skill nombra las nueve casillas del mapa de cobertura»
- (B) «el fichero nombra las nueve casillas del mapa»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Only a missing or conflicting slot is asked

El lector A describe el efecto como «la skill sólo pregunta si la casilla está missing o conflicting»; el lector B describe el efecto como «el fichero declara que sólo se pregunta si falta o hay conflicto». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only a missing or conflicting slot is asked» es la correcta?**
- (A) «la skill sólo pregunta si la casilla está missing o conflicting»
- (B) «el fichero declara que sólo se pregunta si falta o hay conflicto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The slot is named before the question

El lector A describe el efecto como «la skill nombra la casilla antes de preguntarla»; el lector B describe el efecto como «el fichero declara que se nombra la casilla antes de preguntar». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The slot is named before the question» es la correcta?**
- (A) «la skill nombra la casilla antes de preguntarla»
- (B) «el fichero declara que se nombra la casilla antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One answer refreshes the whole map

El lector A registra «re-evaluación del mapa de cobertura» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «One answer refreshes the whole map»?**
- (A) «re-evaluación del mapa de cobertura»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: One answer refreshes the whole map

El lector A describe el efecto como «tras cada respuesta se re-evalúa el mapa entero»; el lector B describe el efecto como «el fichero declara que cada respuesta re-evalúa todo el mapa». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One answer refreshes the whole map» es la correcta?**
- (A) «tras cada respuesta se re-evalúa el mapa entero»
- (B) «el fichero declara que cada respuesta re-evalúa todo el mapa»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A correction invalidates only its dependants

El lector A registra «invalidación de casillas dependientes» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A correction invalidates only its dependants»?**
- (A) «invalidación de casillas dependientes»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A correction invalidates only its dependants

El lector A describe el efecto como «una corrección invalida sólo las casillas dependientes»; el lector B describe el efecto como «el fichero declara que una corrección invalida sólo sus dependientes». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A correction invalidates only its dependants» es la correcta?**
- (A) «una corrección invalida sólo las casillas dependientes»
- (B) «el fichero declara que una corrección invalida sólo sus dependientes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An inferred slot needs the user's confirmation

El lector A registra «confirmación general del borrador siempre se hace» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An inferred slot needs the user's confirmation»?**
- (A) «confirmación general del borrador siempre se hace»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An inferred slot needs the user's confirmation

El lector A describe el efecto como «una casilla inferida pasa a known sólo si el usuario confirma»; el lector B describe el efecto como «el fichero declara que inferred pasa a known sólo con confirmación». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inferred slot needs the user's confirmation» es la correcta?**
- (A) «una casilla inferida pasa a known sólo si el usuario confirma»
- (B) «el fichero declara que inferred pasa a known sólo con confirmación»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An explained product is drafted first

El lector A registra «redacción del acta completa antes de la primera pregunta» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An explained product is drafted first»?**
- (A) «redacción del acta completa antes de la primera pregunta»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An explained product is drafted first

El lector A describe el efecto como «con producto explicado el acta se redacta antes de preguntar»; el lector B describe el efecto como «el fichero declara que el acta se redacta antes de preguntar». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An explained product is drafted first» es la correcta?**
- (A) «con producto explicado el acta se redacta antes de preguntar»
- (B) «el fichero declara que el acta se redacta antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Inferences are marked in the draft

El lector A describe el efecto como «las inferencias quedan marcadas en el borrador»; el lector B describe el efecto como «el fichero declara que las inferencias van marcadas en el borrador». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Inferences are marked in the draft» es la correcta?**
- (A) «las inferencias quedan marcadas en el borrador»
- (B) «el fichero declara que las inferencias van marcadas en el borrador»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The inference mark is the literal comment

El lector A describe el efecto como «la marca de inferencia es el comentario literal indicado»; el lector B describe el efecto como «el fichero declara que la marca es el comentario literal inferred». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The inference mark is the literal comment» es la correcta?**
- (A) «la marca de inferencia es el comentario literal indicado»
- (B) «el fichero declara que la marca es el comentario literal inferred»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Resuming wins over an existing project

El lector A describe el efecto como «con charter.md en disco el modo es retomar acta aunque haya código»; el lector B describe el efecto como «el fichero declara que con charter.md en disco gana retomar». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Resuming wins over an existing project» es la correcta?**
- (A) «con charter.md en disco el modo es retomar acta aunque haya código»
- (B) «el fichero declara que con charter.md en disco gana retomar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The draft lives in the conversation until it is approved

El lector A registra «ninguna escritura en charter.md antes de la aprobación» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The draft lives in the conversation until it is approved»?**
- (A) «ninguna escritura en charter.md antes de la aprobación»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The draft lives in the conversation until it is approved

El lector A describe el efecto como «el borrador se muestra en conversación y no se escribe hasta aprobar»; el lector B describe el efecto como «el fichero declara que el borrador no se escribe hasta aprobarse». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The draft lives in the conversation until it is approved» es la correcta?**
- (A) «el borrador se muestra en conversación y no se escribe hasta aprobar»
- (B) «el fichero declara que el borrador no se escribe hasta aprobarse»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The explained mode needs three slots said by the user

El lector A describe el efecto como «exige purpose, primary_user y first_capability dichos por el usuario»; el lector B describe el efecto como «el fichero declara que ese modo exige tres casillas dichas por el usuario». Similitud de contenido 0.23, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The explained mode needs three slots said by the user» es la correcta?**
- (A) «exige purpose, primary_user y first_capability dichos por el usuario»
- (B) «el fichero declara que ese modo exige tres casillas dichas por el usuario»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The vague mode opens with the last real case

El lector A describe el efecto como «el modo idea difusa abre con la pregunta literal indicada»; el lector B describe el efecto como «el fichero contiene literalmente la pregunta por la última vez». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The vague mode opens with the last real case» es la correcta?**
- (A) «el modo idea difusa abre con la pregunta literal indicada»
- (B) «el fichero contiene literalmente la pregunta por la última vez»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The vague mode continues with what to remove first

El lector A describe el efecto como «el modo idea difusa continúa con la pregunta literal indicada»; el lector B describe el efecto como «el fichero contiene literalmente la pregunta sobre qué eliminar primero». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The vague mode continues with what to remove first» es la correcta?**
- (A) «el modo idea difusa continúa con la pregunta literal indicada»
- (B) «el fichero contiene literalmente la pregunta sobre qué eliminar primero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The fixed rounds are gone

El lector A registra «eliminación de los encabezados de tanda» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The fixed rounds are gone»?**
- (A) «eliminación de los encabezados de tanda»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The reading is reconstructed from disk

El lector A registra «reconstrucción y presentación de la lectura desde disco» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The reading is reconstructed from disk»?**
- (A) «reconstrucción y presentación de la lectura desde disco»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The reading is reconstructed from disk

El lector A describe el efecto como «propósito, usuarios, capabilities y restricciones se leen del repositorio»; el lector B describe el efecto como «el fichero declara que la lectura se reconstruye desde el repositorio». Similitud de contenido 0.10, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The reading is reconstructed from disk» es la correcta?**
- (A) «propósito, usuarios, capabilities y restricciones se leen del repositorio»
- (B) «el fichero declara que la lectura se reconstruye desde el repositorio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The next change is asked

El lector A describe el efecto como «la skill pregunta qué cambio quiere hacer ahora el usuario»; el lector B describe el efecto como «el fichero declara que se pregunta qué cambio quiere hacer ahora». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The next change is asked» es la correcta?**
- (A) «la skill pregunta qué cambio quiere hacer ahora el usuario»
- (B) «el fichero declara que se pregunta qué cambio quiere hacer ahora»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Disk facts are not asked

El lector A describe el efecto como «no pregunta por stack, comando de pruebas ni lo ya demostrado»; el lector B describe el efecto como «el fichero declara que no se pregunta lo que el disco ya demuestra». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Disk facts are not asked» es la correcta?**
- (A) «no pregunta por stack, comando de pruebas ni lo ya demostrado»
- (B) «el fichero declara que no se pregunta lo que el disco ya demuestra»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Priority is adoption order, said once

El lector A describe el efecto como «explica una sola vez que la prioridad es orden de adopción»; el lector B describe el efecto como «el fichero declara la prioridad como orden de adopción, dicha una vez». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Priority is adoption order, said once» es la correcta?**
- (A) «explica una sola vez que la prioridad es orden de adopción»
- (B) «el fichero declara la prioridad como orden de adopción, dicha una vez»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One synthesis and one correction

El lector A describe el efecto como «presenta hechos y apuestas en una síntesis y pide una corrección»; el lector B describe el efecto como «el fichero declara una síntesis única con una sola corrección general». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One synthesis and one correction» es la correcta?**
- (A) «presenta hechos y apuestas en una síntesis y pide una corrección»
- (B) «el fichero declara una síntesis única con una sola corrección general»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No bet is fabricated

El lector A describe el efecto como «si todo es observado no escribe ninguna apuesta y conserva C20»; el lector B describe el efecto como «el fichero declara que no se escribe ninguna apuesta si todo es observado». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No bet is fabricated» es la correcta?**
- (A) «si todo es observado no escribe ninguna apuesta y conserva C20»
- (B) «el fichero declara que no se escribe ninguna apuesta si todo es observado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The claim is recorded inside the charter

El lector A describe el efecto como «la afirmación queda registrada como comentario bajo Bets con fecha»; el lector B describe el efecto como «el fichero declara que la afirmación se registra como comentario con fecha». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The claim is recorded inside the charter» es la correcta?**
- (A) «la afirmación queda registrada como comentario bajo Bets con fecha»
- (B) «el fichero declara que la afirmación se registra como comentario con fecha»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The minimum is listed

El lector A describe el efecto como «enumera los elementos mínimos exigidos para cerrar el acta»; el lector B describe el efecto como «el fichero enumera los elementos mínimos del mapa de cobertura». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The minimum is listed» es la correcta?**
- (A) «enumera los elementos mínimos exigidos para cerrar el acta»
- (B) «el fichero enumera los elementos mínimos del mapa de cobertura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The draft is offered for approval

El lector A describe el efecto como «al llegar al mínimo presenta el borrador y pregunta aprobar o profundizar»; el lector B describe el efecto como «el fichero declara que se presenta el borrador y se pregunta aprobar o profundizar». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The draft is offered for approval» es la correcta?**
- (A) «al llegar al mínimo presenta el borrador y pregunta aprobar o profundizar»
- (B) «el fichero declara que se presenta el borrador y se pregunta aprobar o profundizar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The test command is detected before it is asked

El lector A registra «detección del comando de pruebas en el repositorio» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The test command is detected before it is asked»?**
- (A) «detección del comando de pruebas en el repositorio»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The test command is detected before it is asked

El lector A describe el efecto como «detecta el comando de pruebas en el repositorio antes de preguntar»; el lector B describe el efecto como «el fichero declara que el comando se detecta antes de preguntarlo». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The test command is detected before it is asked» es la correcta?**
- (A) «detecta el comando de pruebas en el repositorio antes de preguntar»
- (B) «el fichero declara que el comando se detecta antes de preguntarlo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Ambiguity is the only reason to ask

El lector A describe el efecto como «sólo pregunta ante ambigüedad que impida el siguiente paso»; el lector B describe el efecto como «el fichero declara que sólo se pregunta ante ambigüedad bloqueante». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Ambiguity is the only reason to ask» es la correcta?**
- (A) «sólo pregunta ante ambigüedad que impida el siguiente paso»
- (B) «el fichero declara que sólo se pregunta ante ambigüedad bloqueante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No generic list of conventions

El lector A describe el efecto como «propone convención sólo si es relevante, sin lista genérica»; el lector B describe el efecto como «el fichero declara que una convención se propone sólo si es relevante». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic list of conventions» es la correcta?**
- (A) «propone convención sólo si es relevante, sin lista genérica»
- (B) «el fichero declara que una convención se propone sólo si es relevante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The generic table is gone

El lector A registra «eliminación de la fila de la tabla genérica» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The generic table is gone»?**
- (A) «eliminación de la fila de la tabla genérica»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The detected command is not trusted blindly

El lector A describe el efecto como «la preparación no ejecuta el comando detectado, lo verifica el primer verify»; el lector B describe el efecto como «el fichero declara que la preparación no ejecuta el comando detectado». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The detected command is not trusted blindly» es la correcta?**
- (A) «la preparación no ejecuta el comando detectado, lo verifica el primer verify»
- (B) «el fichero declara que la preparación no ejecuta el comando detectado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Bets are grouped in one view

El lector A describe el efecto como «las apuestas abiertas se agrupan en una sola vista»; el lector B describe el efecto como «el fichero declara que las apuestas abiertas se agrupan en una vista». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Bets are grouped in one view» es la correcta?**
- (A) «las apuestas abiertas se agrupan en una sola vista»
- (B) «el fichero declara que las apuestas abiertas se agrupan en una vista»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One question with three intentions

El lector A describe el efecto como «pregunta si continuar, revisar sección o resolver apuesta cumplida»; el lector B describe el efecto como «el fichero declara una pregunta con tres opciones posibles». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One question with three intentions» es la correcta?**
- (A) «pregunta si continuar, revisar sección o resolver apuesta cumplida»
- (B) «el fichero declara una pregunta con tres opciones posibles»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Never bet by bet first

El lector A describe el efecto como «no pregunta apuesta por apuesta antes de saber qué quiere el usuario»; el lector B describe el efecto como «el fichero declara que no se pregunta apuesta por apuesta primero». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Never bet by bet first» es la correcta?**
- (A) «no pregunta apuesta por apuesta antes de saber qué quiere el usuario»
- (B) «el fichero declara que no se pregunta apuesta por apuesta primero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No mtime

El lector A describe el efecto como «el fichero no usa mtime para inferir el objetivo de sesión»; el lector B describe el efecto como «el fichero no contiene la palabra mtime». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No mtime» es la correcta?**
- (A) «el fichero no usa mtime para inferir el objetivo de sesión»
- (B) «el fichero no contiene la palabra mtime»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A charter that fails the linter is shown with its blockers

El lector A describe el efecto como «muestra el acta con sus bloqueos antes de preguntar, con opción de empezar de cero»; el lector B describe el efecto como «el fichero declara que un acta con bloqueos se enseña antes de preguntar». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A charter that fails the linter is shown with its blockers» es la correcta?**
- (A) «muestra el acta con sus bloqueos antes de preguntar, con opción de empezar de cero»
- (B) «el fichero declara que un acta con bloqueos se enseña antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Starting over never overwrites without a warning

El lector A describe el efecto como «avisa que no guarda copias y espera confirmación antes de pisar el acta»; el lector B describe el efecto como «el fichero declara que se avisa y se espera confirmación antes de pisar el acta». Similitud de contenido 0.55, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Starting over never overwrites without a warning» es la correcta?**
- (A) «avisa que no guarda copias y espera confirmación antes de pisar el acta»
- (B) «el fichero declara que se avisa y se espera confirmación antes de pisar el acta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A marked line is an error

El lector A registra «emisión de un finding C21 de tipo error» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A marked line is an error»?**
- (A) «emisión de un finding C21 de tipo error»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-009 — En el modo «proyecto existente» la skill reconstruye desde el repositorio el propósito, los usuarios, las capabilities y las restricciones, así que las nueve casillas quedan en `inferred` y ninguna en `missing`; como R-CHL-009 prohíbe plantear una pregunta cuya casilla no esté en `missing` o `conflicting`, una implementación literal no pregunta absolutamente nada y promueve las nueve casillas a `known` con la única confirmación general del borrador. El acta —raíz del contrato de la que cuelgan todas las capabilities y requisitos— queda certificada como acordada sin que el usuario haya aportado un solo hecho.
- **[medium]** R-CHL-009 — «Ante una corrección DEBE invalidar sólo las casillas que dependen de la corregida» es un techo sin grafo de dependencias definido: declarar que ninguna casilla depende de otra cumple la frase al pie de la letra. El usuario corrige `purpose`, y `first_capability`, `done_when` y `out_of_scope` derivados del propósito anterior siguen en `known`, por lo que la misma regla prohíbe volver a preguntarlos: el acta se aprueba con una capability deducida de un propósito que el usuario ya rechazó.
- **[medium]** R-CHL-016 — C21 sólo dispara sobre una línea que «conserva» la marca literal `<!-- inferred -->`, y ningún requisito obliga a que el acta escrita en disco lleve esa marca; como la regla rechaza cualquier línea que la lleve, la implementación obediente escribe el acta aprobada ya sin marcas y C21 no salta nunca (el escenario «A charter without marks is untouched» sale en verde). El único control mecánico contra una inferencia sin confirmar queda vacío: una línea inventada por el modelo es indistinguible en disco de un acuerdo del usuario.
- **[medium]** R-CHL-011 — «No DEBE preguntar por un comportamiento que el disco ya demuestra» es una prohibición absoluta: con un repositorio heredado, la skill escribe en el acta como propósito, restricción o `Done when` lo que el código hace hoy —incluidos bugs y comportamientos obsoletos— y tiene vedado preguntar si eso es lo querido. El contrato del proyecto pasa a consagrar el comportamiento actual como intencionado, y los deltas posteriores se validarán contra él.

## Escenarios que convergen · 10

- The five states are named
- The modes are named
- The per-section question is gone
- Revisit and fatal only for open bets
- No interview on its own initiative
- Preparation comes after writing the charter
- The npm placeholder is not a candidate
- The state is summarised first
- Each marked line has its own finding
- A charter without marks is untouched
