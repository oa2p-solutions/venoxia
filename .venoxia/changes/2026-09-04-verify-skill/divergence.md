# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-04-verify-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 6
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 3 divergencias blandas sobre los 6 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Frontmatter and tool contract read from disk

El lector A describe el efecto como «confirma que el frontmatter cumple name, description y allowed-tools»; el lector B describe el efecto como «el frontmatter tiene name, description y allowed-tools correctos». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Frontmatter and tool contract read from disk» es la correcta?**
- (A) «confirma que el frontmatter cumple name, description y allowed-tools»
- (B) «el frontmatter tiene name, description y allowed-tools correctos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A green run with no red run in the history

El lector A describe el efecto como «la skill pregunta al usuario si vio fallar el test»; el lector B describe el efecto como «la skill pregunta al usuario, no escribe nada». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A green run with no red run in the history» es la correcta?**
- (A) «la skill pregunta al usuario si vio fallar el test»
- (B) «la skill pregunta al usuario, no escribe nada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The user does not confirm

El lector A describe el efecto como «change.json permanece sin cambios»; el lector B describe el efecto como «change.json no cambia de estado». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The user does not confirm» es la correcta?**
- (A) «change.json permanece sin cambios»
- (B) «change.json no cambia de estado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-010 — El requisito acepta como «rojo previo» un run anterior en `missing`; como en el flujo el oráculo se ejecuta ya en `specify`, cuando aún no existe ningún test, todo requisito arrastra siempre un run en `missing` y la precondición queda satisfecha automáticamente. Una implementación literal nunca llega a preguntar al usuario y estampa `verified` sobre tests que jamás se vieron fallar por la razón correcta (incluidos tests vacíos o escritos contra código ya funcionante), que es justo la garantía que este requisito existe para dar.
- **[high]** R-ORC-010 — La obligación y la prohibición sólo se enuncian para «un change en `validated`»: nada regula el caso de un change en `draft` o `specified` con el oráculo en verde. Una implementación que también le escriba `"state": "verified"` cumple cada frase del requisito y permite que un cambio alcance el estado terminal sin haber pasado nunca por el validador ni por la divergencia, rompiendo el único punto del ciclo donde se comprueba que la spec es coherente.
- **[medium]** R-ORC-010 — La confirmación se pide en singular («si vio fallar el test») mientras que el efecto es global (`change.json` pasa a `verified`): si cinco requisitos del delta no tienen run en rojo, preguntar por uno solo y tomar ese «sí» como confirmación de todos cumple el escenario al pie de la letra y marca como verificados cuatro requisitos cuyo test nadie ha visto fallar.

## Escenarios que convergen · 3

- A green run backed by a documented red run
- The user confirms the test was seen failing
- A red run never writes verified
