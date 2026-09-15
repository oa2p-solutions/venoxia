# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 21
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0
- **Herramienta:** Venoxia 0.5.0 (`diff_readings.py`)
- **Historial de decisiones:** `/Users/afroxstudio/Developments/ia/venoxia/.venoxia/changes/2026-09-15-charter-evidence/decisions.json`

## Veredicto

**Las lecturas casi convergen.** 24 divergencias blandas sobre los 21 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Decisiones pendientes · 22

Cada decisión se pregunta una sola vez. Su respuesta vale para todos los escenarios de su
matriz; si para alguno no vale, dilo y se pregunta aparte. Las divergencias que la forman
están en «Evidencia por divergencia».

### D-001 · The evidence file and its shape are named

Razón `same-reading-two-fields` · 2 divergencias en `side_effects` y `effect` · dureza blanda.

| Escenario | Entrada | A | B | Dureza |
|---|---|---|---|---|
| The evidence file and its shape are named | — | se documenta el fichero .venoxia/charter-log.json y su forma en SKILL.md | — | blanda |
| The evidence file and its shape are named | — | SKILL.md nombra charter-log.json, entries y sus claves | SKILL.md nombra el fichero, entries y sus claves | blanda |

El lector A registra «se documenta el fichero .venoxia/charter-log.json y su forma en SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Cuál de estas lecturas de «The evidence file and its shape are named» es la correcta, para el efecto y para los efectos observables a la vez?**
- (A) «SKILL.md nombra charter-log.json, entries y sus claves», con «se documenta el fichero .venoxia/charter-log.json y su forma en SKILL.md» (A)
- (B) «SKILL.md nombra el fichero, entries y sus claves» (B)
- (C) Las lecturas dicen lo mismo con otras palabras, no hay divergencia real

### D-002 · The three kinds and the three outcomes are named

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documentan inference, question, own-decision, confirmed, corrected, dropped» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The three kinds and the three outcomes are named»?**
- (A) «se documentan inference, question, own-decision, confirmed, corrected, dropped»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-003 · Own decisions go to the log, not only to the delivery

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que toda decisión propia se anota en charter-log.json además de en la entrega» y ningún otro lector lo recoge; el lector B registra «se escribe una entrada own-decision en charter-log.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Own decisions go to the log, not only to the delivery»?**
- (A) «se documenta que toda decisión propia se anota en charter-log.json además de en la entrega»
- (B) «se escribe una entrada own-decision en charter-log.json»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-004 · The log survives the session

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que las entradas nuevas se añaden sin borrar las anteriores» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The log survives the session»?**
- (A) «se documenta que las entradas nuevas se añaden sin borrar las anteriores»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-005 · The log survives the session

Razón `single` · 1 divergencia en `effect` · dureza blanda.

El lector A describe el efecto como «SKILL.md declara que el registro persiste entre sesiones»; el lector B describe el efecto como «SKILL.md declara que el registro persiste y no borra entradas». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The log survives the session» es la correcta?**
- (A) «SKILL.md declara que el registro persiste entre sesiones»
- (B) «SKILL.md declara que el registro persiste y no borra entradas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### D-006 · An inference is logged when it is written, not when it is confirmed

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta el desenlace pending hasta confirmar, corregir o descartar» y ningún otro lector lo recoge; el lector B registra «se crea entrada inference con desenlace pending» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An inference is logged when it is written, not when it is confirmed»?**
- (A) «se documenta el desenlace pending hasta confirmar, corregir o descartar»
- (B) «se crea entrada inference con desenlace pending»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-007 · An inference is logged when it is written, not when it is confirmed

Razón `single` · 1 divergencia en `effect` · dureza blanda.

El lector A describe el efecto como «SKILL.md declara que la inferencia se registra al escribirla»; el lector B describe el efecto como «SKILL.md declara que la entrada se escribe al rellenar la casilla». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inference is logged when it is written, not when it is confirmed» es la correcta?**
- (A) «SKILL.md declara que la inferencia se registra al escribirla»
- (B) «SKILL.md declara que la entrada se escribe al rellenar la casilla»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### D-008 · An unreadable log is kept, not overwritten

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector B registra «se crea un registro nuevo» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An unreadable log is kept, not overwritten»?**
- (A) «se crea un registro nuevo»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-009 · Pending inferences are counted and keep the mark

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que la casilla conserva <!-- inferred --> mientras esté pending» y «se documenta que la entrega cuenta las pending» y ningún otro lector lo recoge; el lector B registra «la entrega dice cuántas inferencias quedan pending» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Pending inferences are counted and keep the mark»?**
- (A) «se documenta que la casilla conserva <!-- inferred --> mientras esté pending» y «se documenta que la entrega cuenta las pending»
- (B) «la entrega dice cuántas inferencias quedan pending»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-010 · The corrupt copy never replaces an earlier one

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que <marca> es fecha y hora UTC hasta el segundo con sufijo numérico si colisiona» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The corrupt copy never replaces an earlier one»?**
- (A) «se documenta que <marca> es fecha y hora UTC hasta el segundo con sufijo numérico si colisiona»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-011 · Resolving an inference updates its own entry

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que se añade resolved_at sin crear otra entrada» y ningún otro lector lo recoge; el lector B registra «no se crea una entrada nueva» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Resolving an inference updates its own entry»?**
- (A) «se documenta que se añade resolved_at sin crear otra entrada»
- (B) «no se crea una entrada nueva»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-012 · Pending inferences are resumed first

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta el orden de presentación al retomar un acta» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Pending inferences are resumed first»?**
- (A) «se documenta el orden de presentación al retomar un acta»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-013 · An unanswered row is offered again when resuming

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que se presentan junto a las inferencias pending al retomar» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An unanswered row is offered again when resuming»?**
- (A) «se documenta que se presentan junto a las inferencias pending al retomar»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-014 · Dropped rows are named in the delivery

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta la mención de cada fila descartada y su motivo en la entrega» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Dropped rows are named in the delivery»?**
- (A) «se documenta la mención de cada fila descartada y su motivo en la entrega»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-015 · The drafted row is confirmed in one call

Razón `same-reading-two-fields` · 2 divergencias en `side_effects` y `effect` · dureza blanda.

| Escenario | Entrada | A | B | Dureza |
|---|---|---|---|---|
| The drafted row is confirmed in one call | — | se documenta que contenido y prioridad se confirman juntos antes de escribir la fila | — | blanda |
| The drafted row is confirmed in one call | — | SKILL.md declara confirmación en una sola llamada antes de escribir | SKILL.md declara que la fila se confirma en una sola llamada | blanda |

El lector A registra «se documenta que contenido y prioridad se confirman juntos antes de escribir la fila» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Cuál de estas lecturas de «The drafted row is confirmed in one call» es la correcta, para el efecto y para los efectos observables a la vez?**
- (A) «SKILL.md declara confirmación en una sola llamada antes de escribir», con «se documenta que contenido y prioridad se confirman juntos antes de escribir la fila» (A)
- (B) «SKILL.md declara que la fila se confirma en una sola llamada» (B)
- (C) Las lecturas dicen lo mismo con otras palabras, no hay divergencia real

### D-016 · No row the user has not seen

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta la prohibición de escribir filas no vistas» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «No row the user has not seen»?**
- (A) «se documenta la prohibición de escribir filas no vistas»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-017 · A rejected row is never written

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que corregir vuelve a pedir confirmación» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A rejected row is never written»?**
- (A) «se documenta que corregir vuelve a pedir confirmación»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-018 · An unanswered row leaves a trace

Razón `single` · 1 divergencia en `effect` · dureza blanda.

El lector A describe el efecto como «SKILL.md declara que la fila sin respuesta tampoco se escribe»; el lector B describe el efecto como «SKILL.md declara que la fila no contestada se anota dropped sin respuesta». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unanswered row leaves a trace» es la correcta?**
- (A) «SKILL.md declara que la fila sin respuesta tampoco se escribe»
- (B) «SKILL.md declara que la fila no contestada se anota dropped sin respuesta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### D-019 · Dependent questions never share a call

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta el ejemplo del reparto de convenciones y la prioridad de la fila» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Dependent questions never share a call»?**
- (A) «se documenta el ejemplo del reparto de convenciones y la prioridad de la fila»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-020 · The version is announced first

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta la lectura de la versión desde plugin.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The version is announced first»?**
- (A) «se documenta la lectura de la versión desde plugin.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-021 · The version travels with the evidence

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que plugin_version viaja en cada entrada de charter-log.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The version travels with the evidence»?**
- (A) «se documenta que plugin_version viaja en cada entrada de charter-log.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### D-022 · A missing manifest is announced as unknown

Razón `single` · 1 divergencia en `side_effects` · dureza blanda.

El lector A registra «se documenta que unknown se anuncia y se anota igual sin CLAUDE_PLUGIN_ROOT o manifiesto legible» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A missing manifest is announced as unknown»?**
- (A) «se documenta que unknown se anuncia y se anota igual sin CLAUDE_PLUGIN_ROOT o manifiesto legible»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Evidencia por divergencia · 24

Cada desacuerdo que el motor encontró, con su dureza, su señal y su detalle. Aquí no hay
preguntas: cada uno pertenece a una decisión de arriba.

- **D-001** · «The evidence file and its shape are named» · `side_effects` · blanda · El lector A registra «se documenta el fichero .venoxia/charter-log.json y su forma en SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-001** · «The evidence file and its shape are named» · `effect` · blanda · El lector A describe el efecto como «SKILL.md nombra charter-log.json, entries y sus claves»; el lector B describe el efecto como «SKILL.md nombra el fichero, entries y sus claves». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.
- **D-002** · «The three kinds and the three outcomes are named» · `side_effects` · blanda · El lector A registra «se documentan inference, question, own-decision, confirmed, corrected, dropped» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-003** · «Own decisions go to the log, not only to the delivery» · `side_effects` · blanda · El lector A registra «se documenta que toda decisión propia se anota en charter-log.json además de en la entrega» y ningún otro lector lo recoge; el lector B registra «se escribe una entrada own-decision en charter-log.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-004** · «The log survives the session» · `side_effects` · blanda · El lector A registra «se documenta que las entradas nuevas se añaden sin borrar las anteriores» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-005** · «The log survives the session» · `effect` · blanda · El lector A describe el efecto como «SKILL.md declara que el registro persiste entre sesiones»; el lector B describe el efecto como «SKILL.md declara que el registro persiste y no borra entradas». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.
- **D-006** · «An inference is logged when it is written, not when it is confirmed» · `side_effects` · blanda · El lector A registra «se documenta el desenlace pending hasta confirmar, corregir o descartar» y ningún otro lector lo recoge; el lector B registra «se crea entrada inference con desenlace pending» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-007** · «An inference is logged when it is written, not when it is confirmed» · `effect` · blanda · El lector A describe el efecto como «SKILL.md declara que la inferencia se registra al escribirla»; el lector B describe el efecto como «SKILL.md declara que la entrada se escribe al rellenar la casilla». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.
- **D-008** · «An unreadable log is kept, not overwritten» · `side_effects` · blanda · El lector B registra «se crea un registro nuevo» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-009** · «Pending inferences are counted and keep the mark» · `side_effects` · blanda · El lector A registra «se documenta que la casilla conserva <!-- inferred --> mientras esté pending» y «se documenta que la entrega cuenta las pending» y ningún otro lector lo recoge; el lector B registra «la entrega dice cuántas inferencias quedan pending» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-010** · «The corrupt copy never replaces an earlier one» · `side_effects` · blanda · El lector A registra «se documenta que <marca> es fecha y hora UTC hasta el segundo con sufijo numérico si colisiona» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-011** · «Resolving an inference updates its own entry» · `side_effects` · blanda · El lector A registra «se documenta que se añade resolved_at sin crear otra entrada» y ningún otro lector lo recoge; el lector B registra «no se crea una entrada nueva» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-012** · «Pending inferences are resumed first» · `side_effects` · blanda · El lector A registra «se documenta el orden de presentación al retomar un acta» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-013** · «An unanswered row is offered again when resuming» · `side_effects` · blanda · El lector A registra «se documenta que se presentan junto a las inferencias pending al retomar» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-014** · «Dropped rows are named in the delivery» · `side_effects` · blanda · El lector A registra «se documenta la mención de cada fila descartada y su motivo en la entrega» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-015** · «The drafted row is confirmed in one call» · `side_effects` · blanda · El lector A registra «se documenta que contenido y prioridad se confirman juntos antes de escribir la fila» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-015** · «The drafted row is confirmed in one call» · `effect` · blanda · El lector A describe el efecto como «SKILL.md declara confirmación en una sola llamada antes de escribir»; el lector B describe el efecto como «SKILL.md declara que la fila se confirma en una sola llamada». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.
- **D-016** · «No row the user has not seen» · `side_effects` · blanda · El lector A registra «se documenta la prohibición de escribir filas no vistas» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-017** · «A rejected row is never written» · `side_effects` · blanda · El lector A registra «se documenta que corregir vuelve a pedir confirmación» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-018** · «An unanswered row leaves a trace» · `effect` · blanda · El lector A describe el efecto como «SKILL.md declara que la fila sin respuesta tampoco se escribe»; el lector B describe el efecto como «SKILL.md declara que la fila no contestada se anota dropped sin respuesta». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.
- **D-019** · «Dependent questions never share a call» · `side_effects` · blanda · El lector A registra «se documenta el ejemplo del reparto de convenciones y la prioridad de la fila» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-020** · «The version is announced first» · `side_effects` · blanda · El lector A registra «se documenta la lectura de la versión desde plugin.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-021** · «The version travels with the evidence» · `side_effects` · blanda · El lector A registra «se documenta que plugin_version viaja en cada entrada de charter-log.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.
- **D-022** · «A missing manifest is announced as unknown» · `side_effects` · blanda · El lector A registra «se documenta que unknown se anuncia y se anota igual sin CLAUDE_PLUGIN_ROOT o manifiesto legible» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-CHL-017 — Un `charter-log.json` ilegible o de otra versión se aparta y se crea uno nuevo vacío, pero el acta conserva intactas las marcas `<!-- inferred -->` de las casillas que estaban `pending`; como al retomar sólo se presentan «las inferencias `pending` del registro», esas casillas ya no existen para la skill y no se vuelven a ofrecer nunca, así que C21 rechaza el acta indefinidamente y `gate.py` (fail-closed) deja el proyecto bloqueado sin ninguna vía automática de salida.
- **[medium]** R-CHL-017 — Descartar una inferencia quita la línea del acta y ninguna frase obliga a preguntar el valor real; como al retomar sólo se reofrecen las `pending` y las filas `dropped` por «sin respuesta», una inferencia que el usuario rechaza deja esa casilla del acta vacía para siempre y nadie vuelve a plantearla: el acta acaba con menos contenido del que tenía y el usuario no recibe la pregunta que sustituía a la inferencia equivocada.
- **[medium]** R-CHL-017 — El registro guarda «el texto propuesto o preguntado» y «las palabras literales del usuario», se conserva entre sesiones y el requisito prohíbe borrar entradas anteriores: el texto que el usuario mandó corregir o descartar del acta sobrevive verbatim en `.venoxia/charter-log.json` y acaba en el commit, de modo que retirar una línea del acta es sólo cosmético y no hay ningún mecanismo previsto para eliminar un dato confidencial que el usuario acaba de retractar.

## Escenarios que convergen · 1

- A dropped inference leaves the charter
