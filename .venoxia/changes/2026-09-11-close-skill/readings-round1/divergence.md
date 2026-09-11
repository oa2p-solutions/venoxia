# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-close-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 25
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 3 blandas y 0 lagunas declaradas sobre los 25 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: History is never rewritten nor hooks skipped

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «History is never rewritten nor hooks skipped» de este delta?**
- (A) Sí, y su efecto es «cuerpo declara que nunca pasa --no-verify --force --amend» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The body requires the verified state

El lector A describe el efecto como «el cuerpo declara que sólo trabaja en verified»; el lector B describe el efecto como «cuerpo declara que sólo actúa sobre change verified». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body requires the verified state» es la correcta?**
- (A) «el cuerpo declara que sólo trabaja en verified»
- (B) «cuerpo declara que sólo actúa sobre change verified»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A red gate stops the skill

El lector A describe el efecto como «el cuerpo declara detenerse sin commit si la puerta falla»; el lector B describe el efecto como «cuerpo declara que puerta no-0 detiene sin commit». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A red gate stops the skill» es la correcta?**
- (A) «el cuerpo declara detenerse sin commit si la puerta falla»
- (B) «cuerpo declara que puerta no-0 detiene sin commit»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The files to commit are shown before asking

El lector A describe el efecto como «el cuerpo declara mostrar los ficheros antes de pedir autorización»; el lector B describe el efecto como «cuerpo declara mostrar ficheros a commitear antes de preguntar». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The files to commit are shown before asking» es la correcta?**
- (A) «el cuerpo declara mostrar los ficheros antes de pedir autorización»
- (B) «cuerpo declara mostrar ficheros a commitear antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CLS-002 — R-CLS-002 obliga a «enseñar los ficheros que irían al commit» pero no acota cuáles son ni los liga al change: una implementación que hace `git add -A`, lista el árbol entero sucio y pide el sí empaqueta y empuja ficheros ajenos al change y nunca examinados por `gate.py` (restos de otros changes, ficheros temporales, credenciales locales), y como R-CLS-002 prohíbe `--amend` y `--force`, lo publicado ya no se puede deshacer.
- **[high]** R-CLS-002 — R-CLS-002 sólo prohíbe tres banderas (`--no-verify`, `--force`, `--amend`); un `git push -c core.hooksPath=/dev/null` —o con `GIT_CONFIG` apuntando a otro lado— cumple la letra y salta el hook `pre-push`, que es la única puerta que corre la matriz de Python, la cobertura y `plugin validate`. El resultado es un push público que nadie verificó, con la spec prohibiendo además reescribir la historia para arreglarlo.
- **[medium]** R-CLS-004 — R-CLS-004 fija `allowed-tools` a doce entradas que incluyen `git add` pero ningún `git reset`/`git restore`: si la skill hace el `add` para enseñar los ficheros y el usuario responde que no, cumple R-CLS-002 (no hay commit ni push) pero deja todo el árbol en el índice y literalmente no dispone de ninguna herramienta para deshacerlo, de modo que el siguiente commit del usuario se lleva por sorpresa todo lo que la skill preparó.
- **[medium]** R-CLS-004 — R-CLS-004 prohíbe a la skill de cierre escribir «ningún estado del change», así que el change se queda en `verified` para siempre y nadie lo pasa nunca a `archived`; como `gate.py` ejecuta el oráculo de todos los changes en `verified`, cada cierre re-ejecuta la historia completa y un test antiguo que se rompa por causas ajenas deja la puerta en rojo y bloquea el cierre de cualquier change nuevo, sin que la propia skill pueda tocar nada para desatascarlo.

## Escenarios que convergen · 21

- The skill is named close and takes a change id
- The body runs the gate before proposing the commit
- The gate output is shown literally
- The proposed message is shown before asking
- Authorization goes through AskUserQuestion
- No commit nor push without an explicit yes
- A failed push is delivered as it is
- The subject names the change
- The body lists the requirement IDs
- No co-author trailer
- No generated-with footer
- No mention of the model nor the tool
- The tools are exactly the twelve declared
- No generic Bash
- No Write nor Edit
- The body says it writes no file
- The body says it writes no state
- The delivery names the commit hash
- The delivery names the branch and the remote
- The delivery names the push result
- The next step is specify
