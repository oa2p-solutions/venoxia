# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 19
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 17 divergencias blandas sobre los 19 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 17

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The three kinds and the three outcomes are named

El lector A describe el efecto como «el SKILL.md nombra los tres tipos y los tres desenlaces»; el lector B describe el efecto como «el texto nombra los tres tipos y los tres desenlaces». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The three kinds and the three outcomes are named» es la correcta?**
- (A) «el SKILL.md nombra los tres tipos y los tres desenlaces»
- (B) «el texto nombra los tres tipos y los tres desenlaces»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Own decisions go to the log, not only to the delivery

El lector A describe el efecto como «el SKILL.md declara que la decisión propia también se registra»; el lector B describe el efecto como «el texto declara que las decisiones propias se registran». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Own decisions go to the log, not only to the delivery» es la correcta?**
- (A) «el SKILL.md declara que la decisión propia también se registra»
- (B) «el texto declara que las decisiones propias se registran»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The log survives the session

El lector A describe el efecto como «el SKILL.md declara que el registro persiste entre sesiones»; el lector B describe el efecto como «el texto declara que el registro persiste entre sesiones». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The log survives the session» es la correcta?**
- (A) «el SKILL.md declara que el registro persiste entre sesiones»
- (B) «el texto declara que el registro persiste entre sesiones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An inference is logged when it is written, not when it is confirmed

El lector A describe el efecto como «el SKILL.md declara que se registra al rellenar, no al confirmar»; el lector B describe el efecto como «el texto declara que la inferencia se registra al escribirse». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inference is logged when it is written, not when it is confirmed» es la correcta?**
- (A) «el SKILL.md declara que se registra al rellenar, no al confirmar»
- (B) «el texto declara que la inferencia se registra al escribirse»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unreadable log is kept, not overwritten

El lector A describe el efecto como «el SKILL.md declara que un registro ilegible se renombra, nunca se sobrescribe»; el lector B describe el efecto como «el texto declara el renombrado del registro corrupto». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unreadable log is kept, not overwritten» es la correcta?**
- (A) «el SKILL.md declara que un registro ilegible se renombra, nunca se sobrescribe»
- (B) «el texto declara el renombrado del registro corrupto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Pending inferences are counted and keep the mark

El lector A describe el efecto como «el SKILL.md declara que lo pendiente conserva la marca y se cuenta»; el lector B describe el efecto como «el texto declara marca conservada y conteo de pendientes». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Pending inferences are counted and keep the mark» es la correcta?**
- (A) «el SKILL.md declara que lo pendiente conserva la marca y se cuenta»
- (B) «el texto declara marca conservada y conteo de pendientes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The corrupt copy never replaces an earlier one

El lector A describe el efecto como «el SKILL.md declara el formato de la marca temporal y su sufijo»; el lector B describe el efecto como «el texto declara el sufijo numérico si el nombre existe». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The corrupt copy never replaces an earlier one» es la correcta?**
- (A) «el SKILL.md declara el formato de la marca temporal y su sufijo»
- (B) «el texto declara el sufijo numérico si el nombre existe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Resolving an inference updates its own entry

El lector A describe el efecto como «el SKILL.md declara que resolver actualiza la misma entrada, no crea otra»; el lector B describe el efecto como «el texto declara que resolver actualiza la misma entrada». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Resolving an inference updates its own entry» es la correcta?**
- (A) «el SKILL.md declara que resolver actualiza la misma entrada, no crea otra»
- (B) «el texto declara que resolver actualiza la misma entrada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Pending inferences are resumed first

El lector A describe el efecto como «el SKILL.md declara que lo pendiente se presenta antes de preguntas nuevas»; el lector B describe el efecto como «el texto declara que lo pendiente se presenta primero». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Pending inferences are resumed first» es la correcta?**
- (A) «el SKILL.md declara que lo pendiente se presenta antes de preguntas nuevas»
- (B) «el texto declara que lo pendiente se presenta primero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dropped rows are named in the delivery

El lector A describe el efecto como «el SKILL.md declara que la entrega nombra cada fila descartada con motivo»; el lector B describe el efecto como «el texto declara que la entrega nombra las filas descartadas». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dropped rows are named in the delivery» es la correcta?**
- (A) «el SKILL.md declara que la entrega nombra cada fila descartada con motivo»
- (B) «el texto declara que la entrega nombra las filas descartadas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No row the user has not seen

El lector A describe el efecto como «el SKILL.md declara que no se escribe fila no vista por el usuario»; el lector B describe el efecto como «el texto declara que no se escribe fila no vista». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No row the user has not seen» es la correcta?**
- (A) «el SKILL.md declara que no se escribe fila no vista por el usuario»
- (B) «el texto declara que no se escribe fila no vista»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A rejected row is never written

El lector A describe el efecto como «el SKILL.md declara que sólo con el sí se escribe la fila»; el lector B describe el efecto como «el texto declara que la fila rechazada no se escribe». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A rejected row is never written» es la correcta?**
- (A) «el SKILL.md declara que sólo con el sí se escribe la fila»
- (B) «el texto declara que la fila rechazada no se escribe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unanswered row leaves a trace

El lector A describe el efecto como «el SKILL.md declara que lo no contestado se anota como descartado»; el lector B describe el efecto como «el texto declara que la fila sin respuesta se anota descartada». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unanswered row leaves a trace» es la correcta?**
- (A) «el SKILL.md declara que lo no contestado se anota como descartado»
- (B) «el texto declara que la fila sin respuesta se anota descartada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dependent questions never share a call

El lector A describe el efecto como «el SKILL.md declara que preguntas dependientes no comparten llamada»; el lector B describe el efecto como «el texto declara que preguntas dependientes van en llamadas separadas». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dependent questions never share a call» es la correcta?**
- (A) «el SKILL.md declara que preguntas dependientes no comparten llamada»
- (B) «el texto declara que preguntas dependientes van en llamadas separadas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The version is announced first

El lector A describe el efecto como «el SKILL.md declara que anuncia la versión del plugin al empezar»; el lector B describe el efecto como «el texto declara el anuncio de la versión al empezar». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The version is announced first» es la correcta?**
- (A) «el SKILL.md declara que anuncia la versión del plugin al empezar»
- (B) «el texto declara el anuncio de la versión al empezar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The version travels with the evidence

El lector A describe el efecto como «el SKILL.md declara que cada entrada lleva la versión del plugin»; el lector B describe el efecto como «el texto declara que cada entrada lleva la versión». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The version travels with the evidence» es la correcta?**
- (A) «el SKILL.md declara que cada entrada lleva la versión del plugin»
- (B) «el texto declara que cada entrada lleva la versión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A missing manifest is announced as unknown

El lector A describe el efecto como «el SKILL.md declara que sin manifiesto legible la versión es desconocida»; el lector B describe el efecto como «el texto declara que sin manifiesto la versión es unknown». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A missing manifest is announced as unknown» es la correcta?**
- (A) «el SKILL.md declara que sin manifiesto legible la versión es desconocida»
- (B) «el texto declara que sin manifiesto la versión es unknown»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-017 — El sujeto de «rellena una casilla por inferencia, la confirma, corrige o descarta» es la propia skill, y `pending` se define como «mientras la inferencia no se ha presentado»: una implementación que imprime la inferencia en un mensaje, la marca acto seguido `confirmed` sin ninguna pregunta (las palabras del usuario son opcionales, «cuando las hubo») y quita el `<!-- inferred -->` porque ya no está `pending`, cumple la letra; el acta pasa C21 y el registro certifica como confirmado por el usuario un texto que el usuario nunca respondió, que es justo lo que el requisito venía a impedir.
- **[high]** R-CHL-017 — El delta sólo ata la marca `<!-- inferred -->` a la entrada `pending`, y nada obliga a borrar del acta el texto de una inferencia descartada: una implementación que pone el desenlace en `dropped`, quita la marca (ya no está `pending`) y deja la casilla con el texto inferido cumple todos los escenarios; el acta conserva, indistinguible del contenido acordado, justo la frase que el usuario rechazó, y C21 deja de rechazarla precisamente por haberla descartado.
- **[medium]** R-CHL-017 — Al renombrar un `charter-log.json` ilegible o de otra versión y crear uno nuevo vacío, las inferencias `pending` desaparecen del registro mientras sus marcas `<!-- inferred -->` siguen en el acta: como la única vía de resolución descrita es «presentar las inferencias `pending` del registro» y la entrega sólo está obligada a nombrar el fichero y sus cuentas, el usuario queda con un acta que C21 rechaza indefinidamente, sin nada que se le presente para resolverla y sin aviso de que el registro anterior se apartó.
- **[medium]** R-CHL-018 — «No contestar» se equipara a rechazar: una implementación que, ante una entrevista interrumpida o un «sigue tú», anota todas las filas redactadas como `dropped` con «sin respuesta» y no escribe ninguna, cumple la letra; como `dropped` es un desenlace resuelto, la regla de retomar (que sólo repesca las `pending`) no las vuelve a presentar nunca, y el acta queda entregada con la tabla de capabilities mutilada sin que nada obligue a preguntarlas de nuevo.

## Escenarios que convergen · 2

- The evidence file and its shape are named
- The drafted row is confirmed in one call
