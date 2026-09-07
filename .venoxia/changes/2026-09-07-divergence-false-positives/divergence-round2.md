# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-divergence-false-positives/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 5
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 5 divergencias blandas sobre los 5 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 5

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Gender variants of the same quantifier

El lector A describe el efecto como «la diferencia de género del cuantificador no cuenta como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Gender variants of the same quantifier» es la correcta?**
- (A) «la diferencia de género del cuantificador no cuenta como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A negation deep inside a subordinate clause

El lector A describe el efecto como «la negación dentro de la subordinada no cuenta como divergencia dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negation deep inside a subordinate clause» es la correcta?**
- (A) «la negación dentro de la subordinada no cuenta como divergencia dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A condition dragged into one effect only

El lector A describe el efecto como «la condición que aparece en un solo efecto no cuenta como dura»; el lector B describe el efecto como «la divergencia no se marca como dura». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A condition dragged into one effect only» es la correcta?**
- (A) «la condición que aparece en un solo efecto no cuenta como dura»
- (B) «la divergencia no se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A negated condition against an affirmed one

El lector A describe el efecto como «la condición negada frente a la afirmada sí cuenta como divergencia dura»; el lector B describe el efecto como «la divergencia se marca como dura». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A negated condition against an affirmed one» es la correcta?**
- (A) «la condición negada frente a la afirmada sí cuenta como divergencia dura»
- (B) «la divergencia se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A plain negation still contradicts

El lector A describe el efecto como «la negación simple del efecto cuenta como divergencia dura»; el lector B describe el efecto como «la divergencia se marca como dura». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A plain negation still contradicts» es la correcta?**
- (A) «la negación simple del efecto cuenta como divergencia dura»
- (B) «la divergencia se marca como dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-DIV-011 — El requisito manda «dejar fuera de la señal de polaridad» esa diferencia, pero no obliga a conservar el resto: una implementación que, al detectar una diferencia «ambos»/«ambas» o una negación subordinada presente en un solo efecto, descarta el par de efectos completo del cómputo de polaridad pasa los cinco escenarios y, a la vez, oculta la contradicción real que viaje en la misma frase (lector A: «stderr nombra ambas flags y el exit code es 0»; lector B: «stderr nombra ambos flags y el exit code no es 0»): la divergencia sale blanda, /venoxia:diverge escribe state validated y el guardián abre la puerta al código sobre dos lecturas opuestas.
- **[medium]** R-DIV-011 — Los THEN sólo exigen «no hace dura la divergencia», así que una implementación puede normalizar los dos efectos a idénticos y no registrar divergencia alguna, ni blanda: el par «se borra el directorio del change cuando el change no está archivado» / «se borra el directorio del change» se reporta como acuerdo total y el revisor nunca ve que un lector leyó una condición de guarda sobre un borrado irreversible y el otro un borrado incondicional.
