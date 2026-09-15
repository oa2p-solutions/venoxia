# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 13
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 10 divergencias blandas sobre los 13 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 10

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The evidence file and its shape are named

El lector A describe el efecto como «el SKILL.md nombra el fichero, la lista y las claves»; el lector B describe el efecto como «el test lee SKILL.md y encuentra el nombre del fichero y claves». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The evidence file and its shape are named» es la correcta?**
- (A) «el SKILL.md nombra el fichero, la lista y las claves»
- (B) «el test lee SKILL.md y encuentra el nombre del fichero y claves»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The three kinds and the three outcomes are named

El lector A describe el efecto como «el SKILL.md nombra los tres tipos y los tres desenlaces»; el lector B describe el efecto como «el test confirma que SKILL.md nombra los tres kinds y los tres outcomes». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The three kinds and the three outcomes are named» es la correcta?**
- (A) «el SKILL.md nombra los tres tipos y los tres desenlaces»
- (B) «el test confirma que SKILL.md nombra los tres kinds y los tres outcomes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Own decisions go to the log, not only to the delivery

El lector A describe el efecto como «el SKILL.md declara que las decisiones propias también se registran»; el lector B describe el efecto como «el test confirma que SKILL.md declara el doble registro de own-decision». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Own decisions go to the log, not only to the delivery» es la correcta?**
- (A) «el SKILL.md declara que las decisiones propias también se registran»
- (B) «el test confirma que SKILL.md declara el doble registro de own-decision»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The log survives the session

El lector A describe el efecto como «el SKILL.md declara que el registro persiste y sólo se añade»; el lector B describe el efecto como «el test confirma que SKILL.md declara persistencia entre sesiones». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The log survives the session» es la correcta?**
- (A) «el SKILL.md declara que el registro persiste y sólo se añade»
- (B) «el test confirma que SKILL.md declara persistencia entre sesiones»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An inference is logged when it is written, not when it is confirmed

El lector A describe el efecto como «el SKILL.md declara que se registra al rellenar, no al confirmar»; el lector B describe el efecto como «el test confirma que SKILL.md fija el momento de escritura y el pending». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inference is logged when it is written, not when it is confirmed» es la correcta?**
- (A) «el SKILL.md declara que se registra al rellenar, no al confirmar»
- (B) «el test confirma que SKILL.md fija el momento de escritura y el pending»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unreadable log is kept, not overwritten

El lector A describe el efecto como «el SKILL.md declara que un registro ilegible se renombra, no se sobrescribe»; el lector B describe el efecto como «el test confirma que SKILL.md declara el renombrado a corrupt-<marca>». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unreadable log is kept, not overwritten» es la correcta?**
- (A) «el SKILL.md declara que un registro ilegible se renombra, no se sobrescribe»
- (B) «el test confirma que SKILL.md declara el renombrado a corrupt-<marca>»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No row the user has not seen

El lector A describe el efecto como «el SKILL.md declara que nunca se escribe una fila no vista»; el lector B describe el efecto como «el test confirma que SKILL.md prohíbe escribir filas no vistas». Similitud de contenido 0.55, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No row the user has not seen» es la correcta?**
- (A) «el SKILL.md declara que nunca se escribe una fila no vista»
- (B) «el test confirma que SKILL.md prohíbe escribir filas no vistas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A rejected row is never written

El lector A describe el efecto como «el SKILL.md declara que lo rechazado no se escribe y queda dropped»; el lector B describe el efecto como «el test confirma que SKILL.md declara el flujo sí/corrección/dropped». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A rejected row is never written» es la correcta?**
- (A) «el SKILL.md declara que lo rechazado no se escribe y queda dropped»
- (B) «el test confirma que SKILL.md declara el flujo sí/corrección/dropped»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dependent questions never share a call

El lector A describe el efecto como «el SKILL.md declara que preguntas dependientes van en llamadas separadas»; el lector B describe el efecto como «el test confirma que SKILL.md separa preguntas dependientes con ejemplo». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dependent questions never share a call» es la correcta?**
- (A) «el SKILL.md declara que preguntas dependientes van en llamadas separadas»
- (B) «el test confirma que SKILL.md separa preguntas dependientes con ejemplo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The version is announced first

El lector A describe el efecto como «el SKILL.md declara que la versión se anuncia en la primera línea»; el lector B describe el efecto como «el test confirma que SKILL.md declara anuncio inicial de la versión». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The version is announced first» es la correcta?**
- (A) «el SKILL.md declara que la versión se anuncia en la primera línea»
- (B) «el test confirma que SKILL.md declara anuncio inicial de la versión»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-017 — El requisito obliga a registrar la inferencia al rellenar la casilla con desenlace `pending` «mientras no se ha presentado», pero ninguna frase obliga a presentarla nunca; una implementación que infiere todas las casillas, las escribe en el acta, deja todas las entradas en `pending` y en la entrega dice sólo «5 entradas inference» (el recuento es por `kind`, no por desenlace) cumple al pie de la letra y entrega un acta inventada indistinguible de una confirmada.
- **[medium]** R-CHL-017 — Nada exige que `<marca>` sea única: renombrar siempre a `charter-log.json.corrupt-1` cumple la frase «renombrarse antes de crear uno nuevo y nunca sobrescribirse», y en la segunda ejecución el renombrado destruye la copia anterior; con un registro de versión superior (que el requisito manda apartar igual que uno ilegible) se pierde evidencia válida y no recuperable.
- **[medium]** R-CHL-018 — El requisito ata el `dropped` sólo al rechazo: si el usuario no contesta la llamada de confirmación (la cierra o responde algo que no es sí, corrección ni rechazo), una implementación literal no escribe la fila y tampoco anota nada, con lo que una capability que el usuario había descrito desaparece del acta sin dejar rastro en el registro de evidencia.

## Escenarios que convergen · 3

- The drafted row is confirmed in one call
- The version travels with the evidence
- A missing manifest is announced as unknown
