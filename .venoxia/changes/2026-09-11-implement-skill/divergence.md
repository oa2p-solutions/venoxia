# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-implement-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 21
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 6 divergencias blandas sobre los 21 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 6

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: decisions.json is the one exception

El lector A describe el efecto como «el cuerpo declara que decisions.json es la única excepción escribible»; el lector B describe el efecto como «el cuerpo declara que decisions.json es el único fichero de .venoxia que escribe». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «decisions.json is the one exception» es la correcta?**
- (A) «el cuerpo declara que decisions.json es la única excepción escribible»
- (B) «el cuerpo declara que decisions.json es el único fichero de .venoxia que escribe»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: decisions.json only grows

El lector B registra «se añaden entradas a decisions.json sin eliminar las previas» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «decisions.json only grows»?**
- (A) «se añaden entradas a decisions.json sin eliminar las previas»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The tools are exactly the seven declared

El lector A describe el efecto como «allowed-tools lista exactamente los siete herramientas indicadas»; el lector B describe el efecto como «allowed-tools lista exactamente Read, Glob, Grep, Edit, Write, AskUserQuestion y Bash acotado a oracle.py». Similitud de contenido 0.24, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The tools are exactly the seven declared» es la correcta?**
- (A) «allowed-tools lista exactamente los siete herramientas indicadas»
- (B) «allowed-tools lista exactamente Read, Glob, Grep, Edit, Write, AskUserQuestion y Bash acotado a oracle.py»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The delivery lists every requirement with its state

El lector A describe el efecto como «la entrega nombra cada requisito con su estado del oráculo»; el lector B describe el efecto como «el cuerpo declara que la entrega nombra cada requisito con su estado». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The delivery lists every requirement with its state» es la correcta?**
- (A) «la entrega nombra cada requisito con su estado del oráculo»
- (B) «el cuerpo declara que la entrega nombra cada requisito con su estado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The delivery lists the files touched

El lector A describe el efecto como «la entrega nombra los ficheros que la skill tocó»; el lector B describe el efecto como «el cuerpo declara que la entrega nombra los ficheros tocados». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The delivery lists the files touched» es la correcta?**
- (A) «la entrega nombra los ficheros que la skill tocó»
- (B) «el cuerpo declara que la entrega nombra los ficheros tocados»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The next step is verify

El lector A describe el efecto como «la entrega indica /venoxia:verify como siguiente paso»; el lector B describe el efecto como «el cuerpo declara que el siguiente paso es /venoxia:verify». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The next step is verify» es la correcta?**
- (A) «la entrega indica /venoxia:verify como siguiente paso»
- (B) «el cuerpo declara que el siguiente paso es /venoxia:verify»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 5

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-IMP-003 — R-IMP-003 manda ejecutar `oracle.py` «sin --record» y terminar cuando el oráculo sale con código 0; el `Bash` acotado a `oracle.py` permite cualquier flag, así que la skill puede lanzar `oracle.py --change <id> --dry-run`, que sólo lista los comandos y sale 0, darse por terminada sin haber ejecutado un solo test y entregar el change a `/venoxia:verify` con el código sin escribir.
- **[high]** R-IMP-002 — R-IMP-002 sólo prohíbe editar los ficheros que nombra un `verifies:` **del delta** y sus directorios; los tests de las demás capabilities, si viven en otro directorio, quedan fuera de la prohibición, así que la skill puede reescribir o vaciar el oráculo de otra capability para que la suite quede verde y destruir en silencio la verificación de un comportamiento ya contratado.
- **[medium]** R-IMP-002 — R-IMP-002 prohíbe editar «ningún otro fichero del directorio que contiene» a un fichero de `verifies:`, subdirectorios incluidos; en un proyecto con test colocado junto al código (`src/checkout/total.test.ts`) o con el test en la raíz, esa regla cubre el propio código de producción y la skill que la cumple al pie de la letra se niega a escribir nada, dejando el change implementable sólo a mano.
- **[medium]** R-IMP-003 — R-IMP-003 sólo obliga a parar cuando «un intento no cambia el estado de ningún requisito»; una skill que en cada iteración pone R1 de rojo a verde rompiendo R2 (y a la inversa en la siguiente) siempre cambia algún estado, así que el bucle no termina nunca y sigue reescribiendo código de producción sin límite de intentos.
- **[medium]** R-IMP-001 — R-IMP-001 exige que el último run no tenga «ningún requisito del change en `missing`», pero `missing` es una atribución del oráculo, no la ausencia: un último run que sólo evaluó un requisito (rojo) y ni siquiera menciona a los demás cumple la condición, y la skill arranca a escribir código sobre un change cuyos otros requisitos no tienen ningún test comprobado.

## Escenarios que convergen · 15

- The skill is named implement and takes a change id
- The body requires the validated state
- The body requires a recorded red run
- The body refuses a missing test
- The inventory precedes any edit
- The body forbids editing .venoxia
- The body forbids editing the oracle files
- The body forbids editing the test directories
- The body says the guardian keeps watching
- No generic Bash
- The body forbids recording
- The body stops on a green oracle
- An unwritten decision is asked, not chosen
- An answer that changes behaviour goes back to specify
- No progress stops the loop
