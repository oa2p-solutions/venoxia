# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-15-charter-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 9
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 10 divergencias blandas sobre los 9 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Decisiones agrupadas · 1

Varias divergencias de abajo nacen de la misma ambigüedad y se resuelven con una
sola respuesta. Contesta aquí una vez; la respuesta vale para todos los escenarios
que se listan, y si para alguno no vale, dilo y se pregunta aparte.

### Escenario: The evidence file and its shape are named, The three kinds and the three outcomes are named, The drafted row is confirmed in one call, No row the user has not seen, Dependent questions never share a call, The version is announced first y The version travels with the evidence

D-001 · razón `same-readings-across-scenarios` · 7 divergencias en `side_effects` · escenarios: «The evidence file and its shape are named», «The three kinds and the three outcomes are named», «The drafted row is confirmed in one call», «No row the user has not seen», «Dependent questions never share a call», «The version is announced first» y «The version travels with the evidence».

**¿Qué efectos observables debe producir «The evidence file and its shape are named», «The three kinds and the three outcomes are named», «The drafted row is confirmed in one call», «No row the user has not seen», «Dependent questions never share a call», «The version is announced first» y «The version travels with the evidence»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura
- (C) Las lecturas dicen lo mismo con otras palabras, no hay divergencia real

## Divergencias blandas · 10

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The evidence file and its shape are named

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The evidence file and its shape are named»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The three kinds and the three outcomes are named

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The three kinds and the three outcomes are named»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The three kinds and the three outcomes are named

El lector A describe el efecto como «SKILL.md nombra los tres tipos y los tres desenlaces»; el lector B describe el efecto como «el SKILL.md nombra los tres kinds y los tres outcomes». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The three kinds and the three outcomes are named» es la correcta?**
- (A) «SKILL.md nombra los tres tipos y los tres desenlaces»
- (B) «el SKILL.md nombra los tres kinds y los tres outcomes»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Own decisions go to the log, not only to the delivery

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge; el lector B registra «se registra la decisión propia en el log ademas de en la entrega» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Own decisions go to the log, not only to the delivery»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) «se registra la decisión propia en el log ademas de en la entrega»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The log survives the session

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge; el lector B registra «las entradas nuevas se añaden sin borrar las anteriores» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The log survives the session»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) «las entradas nuevas se añaden sin borrar las anteriores»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The drafted row is confirmed in one call

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The drafted row is confirmed in one call»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: No row the user has not seen

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «No row the user has not seen»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Dependent questions never share a call

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Dependent questions never share a call»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The version is announced first

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The version is announced first»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The version travels with the evidence

El lector A registra «modifica skills/charter/SKILL.md» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The version travels with the evidence»?**
- (A) «modifica skills/charter/SKILL.md»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-018 — R-CHL-018 obliga a presentar la fila marcada como inferida y confirmarla en una sola llamada antes de escribirla, pero no condiciona la escritura al sí del usuario: una implementación que presenta la fila, recibe «no, esa capability sobra» o una prioridad distinta, y escribe igualmente la fila redactada cumple al pie de la letra («se confirmó antes de escribir», «el usuario la vio»), y el acta queda con una capability y una prioridad que el usuario rechazó, registradas además en charter-log.json como parte del proceso de confirmación.
- **[medium]** R-CHL-017 — R-CHL-017 sólo obliga a registrar la casilla inferida que la skill «confirma, corrige o descarta»; una implementación que infiere una casilla y la escribe directamente en el acta sin presentarla nunca dispara la obligación y no deja ninguna entrada, de modo que la entrega puede anunciar «0 inferencias» con un acta llena de contenido inventado y C21 en verde por no llevar la marca `<!-- inferred -->` (R-CHL-018 sólo cubre las filas de la tabla de capabilities).
- **[medium]** R-CHL-017 — R-CHL-017 describe charter-log.json como fichero de versión `1` con la lista `entries` y sólo exige «añadir una entrada»; nada dice qué hacer con un fichero preexistente ilegible o de otra versión, así que una implementación que en ese caso lo reescribe desde cero como {"version":1,"entries":[<la nueva>]} cumple la frase y borra sin aviso toda la evidencia de las sesiones anteriores —la única prueba de qué se infirió y qué dijo el usuario—, mientras la entrega informa tranquilamente de «1 entrada escrita».
- **[low]** R-CHL-019 — R-CHL-019 exige anunciar la versión leída de ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json y escribirla en cada entrada, pero no dice nada del caso en que la variable no esté definida o el fichero no se pueda leer: una implementación que entonces sigue adelante sin anunciar nada y con `plugin_version` vacío cumple, y el registro queda sin atribución de versión justo cuando el plugin corre desde un sitio inesperado, que es el único escenario en el que el hallazgo 6 pedía poder demostrar qué versión corre.
