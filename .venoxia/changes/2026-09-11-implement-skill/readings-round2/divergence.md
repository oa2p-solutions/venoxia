# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-implement-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 18
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 4 divergencias blandas sobre los 18 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 4

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The body requires the validated state

El lector A describe el efecto como «el cuerpo exige que el change esté en validated»; el lector B describe el efecto como «el cuerpo declara que sólo trabaja sobre un change validated». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body requires the validated state» es la correcta?**
- (A) «el cuerpo exige que el change esté en validated»
- (B) «el cuerpo declara que sólo trabaja sobre un change validated»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body requires a recorded red run

El lector A describe el efecto como «el cuerpo exige un run de oracle.json con algún requisito red»; el lector B describe el efecto como «el cuerpo declara que exige un run con algún requisito en red antes de escribir código». Similitud de contenido 0.45, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body requires a recorded red run» es la correcta?**
- (A) «el cuerpo exige un run de oracle.json con algún requisito red»
- (B) «el cuerpo declara que exige un run con algún requisito en red antes de escribir código»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: decisions.json is the one exception

El lector A registra «escribe decisions.json del change» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «decisions.json is the one exception»?**
- (A) «escribe decisions.json del change»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: No generic Bash

El lector A describe el efecto como «el frontmatter no incluye ningún Bash sin acotar»; el lector B describe el efecto como «ninguna entrada de allowed-tools es un Bash sin acotar». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic Bash» es la correcta?**
- (A) «el frontmatter no incluye ningún Bash sin acotar»
- (B) «ninguna entrada de allowed-tools es un Bash sin acotar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-IMP-002 — R-IMP-002 sólo blinda el fichero que nombra `verifies:` y «los demás ficheros del directorio que lo contiene»: un helper o fixture que viva en un subdirectorio (`tests/support/`, `tests/fixtures/`) o cualquier módulo que el test importe desde fuera de esa carpeta queda editable, así que la skill puede pasar un requisito de rojo a verde debilitando el oráculo en vez de implementar nada, y `/venoxia:verify` graba ese verde como prueba del comportamiento.
- **[medium]** R-IMP-002 — R-IMP-002 autoriza escribir el `decisions.json` del change sin exigir que conserve lo ya escrito: una implementación que lo reescribe entero al anotar su primera respuesta borra las decisiones literales que `/venoxia:diverge` recogió del usuario, que son el único registro de por qué el change llegó a `validated`.
- **[medium]** R-IMP-003 — R-IMP-003 manda anotar en `decisions.json` la decisión no escrita que deja un requisito en rojo, y R-IMP-002 prohíbe tocar el delta: el comportamiento decidido se implementa en código y ningún requisito lo describe jamás, de modo que el change puede llegar a `verified` con conducta pactada fuera de la especificación, que es exactamente lo que Venoxia existe para impedir.
- **[medium]** R-IMP-003 — R-IMP-003 sólo fija el fin del trabajo para el caso verde («DEBE terminar cuando el oráculo sale con código 0») y nada acota los intentos ni define rendirse: si el rojo no se puede arreglar, una implementación literal sigue editando y reescribiendo código de producción en bucle indefinidamente, sin salida ni entrega, dejando el árbol lleno de cambios a medias.

## Escenarios que convergen · 14

- The skill is named implement and takes a change id
- The body refuses a missing test
- The inventory precedes any edit
- The body forbids editing .venoxia
- The body forbids editing the oracle files
- The body forbids editing the test directories
- The body says the guardian keeps watching
- The tools are exactly the seven declared
- The body forbids recording
- The body stops on a green oracle
- An unwritten decision is asked, not chosen
- The delivery lists every requirement with its state
- The delivery lists the files touched
- The next step is verify
