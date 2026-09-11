# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-close-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 33
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 6 divergencias blandas sobre los 33 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 6

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A red gate stops the skill

El lector A describe el efecto como «el cuerpo declara que con puerta distinta de 0 se detiene sin commit»; el lector B describe el efecto como «el cuerpo declara que se detiene sin commit si la puerta falla». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A red gate stops the skill» es la correcta?**
- (A) «el cuerpo declara que con puerta distinta de 0 se detiene sin commit»
- (B) «el cuerpo declara que se detiene sin commit si la puerta falla»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A non-empty index stops the skill

El lector A describe el efecto como «el cuerpo declara que un índice no vacío detiene la skill sin commit»; el lector B describe el efecto como «el cuerpo declara que se detiene sin commit si el índice ya tiene cambios». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A non-empty index stops the skill» es la correcta?**
- (A) «el cuerpo declara que un índice no vacío detiene la skill sin commit»
- (B) «el cuerpo declara que se detiene sin commit si el índice ya tiene cambios»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Only the listed files are staged

El lector A describe el efecto como «el cuerpo declara que añade por ruta sólo lo enseñado, nunca -A ni .»; el lector B describe el efecto como «el cuerpo declara que añade por ruta sólo los ficheros mostrados». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Only the listed files are staged» es la correcta?**
- (A) «el cuerpo declara que añade por ruta sólo lo enseñado, nunca -A ni .»
- (B) «el cuerpo declara que añade por ruta sólo los ficheros mostrados»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The user excludes a file by naming it

El lector A describe el efecto como «el cuerpo declara que un fichero nombrado por el usuario queda excluido»; el lector B describe el efecto como «el cuerpo declara que el usuario excluye un fichero al nombrarlo». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The user excludes a file by naming it» es la correcta?**
- (A) «el cuerpo declara que un fichero nombrado por el usuario queda excluido»
- (B) «el cuerpo declara que el usuario excluye un fichero al nombrarlo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The tools are exactly the twelve declared

El lector A describe el efecto como «el frontmatter lista exactamente los doce allowed-tools indicados»; el lector B describe el efecto como «el frontmatter declara exactamente las doce herramientas permitidas». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The tools are exactly the twelve declared» es la correcta?**
- (A) «el frontmatter lista exactamente los doce allowed-tools indicados»
- (B) «el frontmatter declara exactamente las doce herramientas permitidas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No generic Bash

El lector A describe el efecto como «el frontmatter no incluye ningún Bash sin acotar»; el lector B describe el efecto como «el frontmatter declara que ningún Bash queda sin acotar». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic Bash» es la correcta?**
- (A) «el frontmatter no incluye ningún Bash sin acotar»
- (B) «el frontmatter declara que ningún Bash queda sin acotar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CLS-002 — La lista propuesta es «todo lo que `git status` enumera», lo que incluye los ficheros sin seguimiento del árbol: un `.env`, un volcado de credenciales, un `oracle.json.corrupt-*` o un scratch local entran en el grupo «el resto» y, con un único sí en el `AskUserQuestion`, se añaden por ruta, se comitean y se empujan al remoto; la fuga al historial público es irreversible y el único modo de evitarla es que el usuario enumere uno a uno cada fichero a excluir.
- **[medium]** R-CLS-002 — El texto sólo describe qué hacer si el índice está vacío al empezar y si el push sale en rojo: si el `git commit` falla (un hook de pre-commit lo rechaza, y `--no-verify` está prohibido), los ficheros quedan preparados en el índice y ninguna frase obliga a deshacerlo; en la siguiente invocación la skill se detiene por «índice no vacío» y, como su `allowed-tools` no incluye ningún `git reset` ni `git restore` (R-CLS-004), el flujo queda bloqueado hasta que alguien limpie el índice a mano.
- **[medium]** R-CLS-004 — La skill que cierra el change tiene prohibido escribir cualquier estado, así que ningún paso del ciclo lleva nunca un change a `archived`: todos se quedan en `verified` para siempre y `gate.py` —que valida el oráculo de cada change en `verified`— reejecuta el conjunto completo en cada cierre; en cuanto un requisito antiguo queda obsoleto y su test se pone en rojo, la puerta sale distinta de `0` y R-CLS-001 impide cerrar ningún change nuevo, sin ningún remedio dentro del flujo.
- **[low]** R-CLS-003 — El asunto debe nombrar el change y a la vez ninguna línea del mensaje puede contener «Claude»: en un repositorio que es un plugin de Claude Code, un change cuyo id incluya esa palabra obliga a una implementación literal a mutilar el id en el asunto —dejando un commit que nombra un change inexistente— o a negarse a cerrar el change.

## Escenarios que convergen · 27

- The skill is named close and takes a change id
- The body requires the verified state
- The body runs the gate before proposing the commit
- The gate output is shown literally
- Nothing is staged before the yes
- Every changed file is proposed, grouped
- The change's own files cannot be excluded
- The branch and the remote are shown before asking
- No git configuration override
- The files to commit are shown before asking
- The proposed message is shown before asking
- Authorization goes through AskUserQuestion
- No commit nor push without an explicit yes
- History is never rewritten nor hooks skipped
- A failed push is delivered as it is
- The subject names the change
- The body lists the requirement IDs
- No co-author trailer
- No generated-with footer
- No mention of the model nor the tool
- No Write nor Edit
- The body says it writes no file
- The body says it writes no state
- The delivery names the commit hash
- The delivery names the branch and the remote
- The delivery names the push result
- The next step is specify
