# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 16
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 15 divergencias blandas sobre los 16 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 15

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The three kinds and the three outcomes are named

El lector A describe el efecto como «el test confirma que SKILL.md nombra tipos y desenlaces»; el lector B describe el efecto como «el cuerpo de SKILL.md nombra los tres tipos y desenlaces». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The three kinds and the three outcomes are named» es la correcta?**
- (A) «el test confirma que SKILL.md nombra tipos y desenlaces»
- (B) «el cuerpo de SKILL.md nombra los tres tipos y desenlaces»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Own decisions go to the log, not only to the delivery

El lector A describe el efecto como «el test confirma que SKILL.md declara registrar own-decision»; el lector B describe el efecto como «el cuerpo declara que own-decision también se anota en el registro». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Own decisions go to the log, not only to the delivery» es la correcta?**
- (A) «el test confirma que SKILL.md declara registrar own-decision»
- (B) «el cuerpo declara que own-decision también se anota en el registro»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The log survives the session

El lector A describe el efecto como «el test confirma que SKILL.md declara persistencia entre sesiones»; el lector B describe el efecto como «el cuerpo declara que el registro persiste y se añade sin borrar». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The log survives the session» es la correcta?**
- (A) «el test confirma que SKILL.md declara persistencia entre sesiones»
- (B) «el cuerpo declara que el registro persiste y se añade sin borrar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An inference is logged when it is written, not when it is confirmed

El lector A describe el efecto como «el test confirma que SKILL.md declara el momento de registro»; el lector B describe el efecto como «el cuerpo declara que la entrada se escribe al rellenar, pending». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An inference is logged when it is written, not when it is confirmed» es la correcta?**
- (A) «el test confirma que SKILL.md declara el momento de registro»
- (B) «el cuerpo declara que la entrada se escribe al rellenar, pending»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unreadable log is kept, not overwritten

El lector A describe el efecto como «el test confirma que SKILL.md declara renombrar el registro corrupto»; el lector B describe el efecto como «el cuerpo declara que un registro ilegible se renombra, nunca se sobrescribe». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unreadable log is kept, not overwritten» es la correcta?**
- (A) «el test confirma que SKILL.md declara renombrar el registro corrupto»
- (B) «el cuerpo declara que un registro ilegible se renombra, nunca se sobrescribe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Pending inferences are counted and keep the mark

El lector A describe el efecto como «el test confirma que SKILL.md declara marca y conteo de pendientes»; el lector B describe el efecto como «el cuerpo declara que pending conserva la marca y se cuenta en la entrega». Similitud de contenido 0.15, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Pending inferences are counted and keep the mark» es la correcta?**
- (A) «el test confirma que SKILL.md declara marca y conteo de pendientes»
- (B) «el cuerpo declara que pending conserva la marca y se cuenta en la entrega»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The corrupt copy never replaces an earlier one

El lector A describe el efecto como «el test confirma que SKILL.md declara el formato de la marca temporal»; el lector B describe el efecto como «el cuerpo declara el formato de la marca y el sufijo numérico». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The corrupt copy never replaces an earlier one» es la correcta?**
- (A) «el test confirma que SKILL.md declara el formato de la marca temporal»
- (B) «el cuerpo declara el formato de la marca y el sufijo numérico»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The drafted row is confirmed in one call

El lector A describe el efecto como «el test confirma que SKILL.md declara confirmación en una sola llamada»; el lector B describe el efecto como «el cuerpo declara que la fila redactada se confirma en una llamada». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The drafted row is confirmed in one call» es la correcta?**
- (A) «el test confirma que SKILL.md declara confirmación en una sola llamada»
- (B) «el cuerpo declara que la fila redactada se confirma en una llamada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No row the user has not seen

El lector A describe el efecto como «el test confirma que SKILL.md declara no escribir filas no vistas»; el lector B describe el efecto como «el cuerpo declara que no se escribe fila que el usuario no vio». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No row the user has not seen» es la correcta?**
- (A) «el test confirma que SKILL.md declara no escribir filas no vistas»
- (B) «el cuerpo declara que no se escribe fila que el usuario no vio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A rejected row is never written

El lector A describe el efecto como «el test confirma que SKILL.md declara el flujo de confirmación y rechazo»; el lector B describe el efecto como «el cuerpo declara que la fila rechazada no se escribe y se anota dropped». Similitud de contenido 0.14, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A rejected row is never written» es la correcta?**
- (A) «el test confirma que SKILL.md declara el flujo de confirmación y rechazo»
- (B) «el cuerpo declara que la fila rechazada no se escribe y se anota dropped»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unanswered row leaves a trace

El lector A describe el efecto como «el test confirma que SKILL.md declara anotar dropped sin respuesta»; el lector B describe el efecto como «el cuerpo declara que fila sin respuesta se anota dropped sin respuesta». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unanswered row leaves a trace» es la correcta?**
- (A) «el test confirma que SKILL.md declara anotar dropped sin respuesta»
- (B) «el cuerpo declara que fila sin respuesta se anota dropped sin respuesta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dependent questions never share a call

El lector A describe el efecto como «el test confirma que SKILL.md declara separar preguntas dependientes»; el lector B describe el efecto como «el cuerpo declara que preguntas dependientes van en llamadas separadas». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dependent questions never share a call» es la correcta?**
- (A) «el test confirma que SKILL.md declara separar preguntas dependientes»
- (B) «el cuerpo declara que preguntas dependientes van en llamadas separadas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The version is announced first

El lector A describe el efecto como «el test confirma que SKILL.md declara anunciar versión al iniciar»; el lector B describe el efecto como «el cuerpo declara que al empezar se anuncia la versión del plugin». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The version is announced first» es la correcta?**
- (A) «el test confirma que SKILL.md declara anunciar versión al iniciar»
- (B) «el cuerpo declara que al empezar se anuncia la versión del plugin»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The version travels with the evidence

El lector A describe el efecto como «el test confirma que SKILL.md declara plugin_version en cada entrada»; el lector B describe el efecto como «el cuerpo declara que cada entrada lleva plugin_version». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The version travels with the evidence» es la correcta?**
- (A) «el test confirma que SKILL.md declara plugin_version en cada entrada»
- (B) «el cuerpo declara que cada entrada lleva plugin_version»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A missing manifest is announced as unknown

El lector A describe el efecto como «el test confirma que SKILL.md declara unknown sin manifiesto»; el lector B describe el efecto como «el cuerpo declara que sin manifiesto legible la versión es unknown». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A missing manifest is announced as unknown» es la correcta?**
- (A) «el test confirma que SKILL.md declara unknown sin manifiesto»
- (B) «el cuerpo declara que sin manifiesto legible la versión es unknown»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-017 — R-CHL-017 exige que «las entradas nuevas se añaden sin borrar las anteriores» y que «una casilla cuya entrada sigue pending conserva la marca <!-- inferred -->»; una implementación que al confirmar añade una entrada nueva con desenlace `confirmed` en lugar de resolver la entrada `pending` cumple ambas frases al pie de la letra, y entonces toda casilla confirmada conserva la marca, C21 rechaza el acta indefinidamente (charter_lint rojo y gate.py fail-closed) y la entrega sigue anunciando inferencias `pending` que el usuario ya confirmó.
- **[medium]** R-CHL-017 — R-CHL-017 obliga a escribir la entrada `inference` y la marca <!-- inferred --> al rellenar la casilla, pero ninguna frase obliga a retomar las inferencias `pending` en una sesión posterior; una skill que infiere, marca el acta y termina la sesión sin presentar la inferencia deja en disco un charter.md que C21 rechaza y un registro que crece con `pending` nuevos en cada ejecución, sin ninguna vía prevista para desbloquearlo salvo editar el acta a mano.
- **[medium]** R-CHL-018 — R-CHL-018 manda no escribir la fila si el usuario la rechaza o no la contesta, y R-CHL-017 sólo obliga a que la entrega diga cuántas entradas de cada clase (`inference`, `question`, `own-decision`) escribió y cuántas inferencias quedan `pending`: una implementación que trata cualquier respuesta no afirmativa como «sin respuesta», descarta la fila, la anota como `dropped` y no vuelve a proponerla cumple ambos requisitos, y el usuario recibe un acta a la que le falta una capability que él mismo describió —incluida `technical-contract`— sin que la entrega lo mencione en ninguna cifra.

## Escenarios que convergen · 1

- The evidence file and its shape are named
