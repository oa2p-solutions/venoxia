# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-04-oracle/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 13
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 6 divergencias duras, 11 blandas y 0 lagunas declaradas sobre los 13 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 6

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: verifies points to a file that was never written

El lector A registra «no invoca test_command para el requisito faltante» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «verifies points to a file that was never written»?**
- (A) «no invoca test_command para el requisito faltante»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A runner that sleeps past the limit

El lector A registra «termina la ejecución del test_command en marcha» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «A runner that sleeps past the limit»?**
- (A) «termina la ejecución del test_command en marcha»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The project never wrote venoxia.json

El lector A registra «no ejecuta ningún runner» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «The project never wrote venoxia.json»?**
- (A) «no ejecuta ningún runner»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: test_command forgot the placeholder

El lector A registra «no ejecuta ningún runner» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «test_command forgot the placeholder»?**
- (A) «no ejecuta ningún runner»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Two runs in a row

El lector B registra «se escribe/actualiza oracle.json con el historial de runs» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «Two runs in a row»?**
- (A) «se escribe/actualiza oracle.json con el historial de runs»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The history file is corrupt

El lector A registra «oracle.json queda con un único run, el actual» y ningún otro lector lo recoge; el lector B registra «oracle.json se sobrescribe con un historial nuevo» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto.

**¿Qué efectos observables debe producir «The history file is corrupt»?**
- (A) «oracle.json queda con un único run, el actual»
- (B) «oracle.json se sobrescribe con un historial nuevo»
- (C) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

## Divergencias blandas · 11

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Three requirements, three green tests

El lector A describe el efecto como «confirma que todos los requisitos están en verde»; el lector B describe el efecto como «termina en verde con el total correcto de requisitos». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Three requirements, three green tests» es la correcta?**
- (A) «confirma que todos los requisitos están en verde»
- (B) «termina en verde con el total correcto de requisitos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One red among three

El lector A describe el efecto como «señala qué requisito falló con su código de salida»; el lector B describe el efecto como «identifica el requisito rojo con su exit_code, deja los demás en verde». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One red among three» es la correcta?**
- (A) «señala qué requisito falló con su código de salida»
- (B) «identifica el requisito rojo con su exit_code, deja los demás en verde»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: verifies points to a file that was never written

El lector A describe el efecto como «marca el requisito como missing sin ejecutar su test»; el lector B describe el efecto como «marca el requisito como missing sin invocar el runner». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «verifies points to a file that was never written» es la correcta?**
- (A) «marca el requisito como missing sin ejecutar su test»
- (B) «marca el requisito como missing sin invocar el runner»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No traceback after a timeout

El lector A describe el efecto como «no imprime ningún Traceback en stderr tras el timeout»; el lector B describe el efecto como «stderr no contiene ningún rastro de traceback». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No traceback after a timeout» es la correcta?**
- (A) «no imprime ningún Traceback en stderr tras el timeout»
- (B) «stderr no contiene ningún rastro de traceback»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The project never wrote venoxia.json

El lector A describe el efecto como «indica qué fichero de configuración falta con un ejemplo»; el lector B describe el efecto como «termina con error nombrando venoxia.json y un ejemplo». Similitud de contenido 0.10, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The project never wrote venoxia.json» es la correcta?**
- (A) «indica qué fichero de configuración falta con un ejemplo»
- (B) «termina con error nombrando venoxia.json y un ejemplo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: test_command forgot the placeholder

El lector A describe el efecto como «indica que falta el marcador {files} en test_command»; el lector B describe el efecto como «termina con error nombrando el marcador {files} ausente». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «test_command forgot the placeholder» es la correcta?**
- (A) «indica que falta el marcador {files} en test_command»
- (B) «termina con error nombrando el marcador {files} ausente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dry run over a change with two requirements

El lector A describe el efecto como «muestra el comando de cada requisito sin ejecutarlo»; el lector B describe el efecto como «imprime un comando por requisito sin invocar ningún runner». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Dry run over a change with two requirements» es la correcta?**
- (A) «muestra el comando de cada requisito sin ejecutarlo»
- (B) «imprime un comando por requisito sin invocar ningún runner»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Two runs in a row

El lector A describe el efecto como «acumula la nueva ejecución en el historial»; el lector B describe el efecto como «oracle.json acumula las dos ejecuciones registradas». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two runs in a row» es la correcta?**
- (A) «acumula la nueva ejecución en el historial»
- (B) «oracle.json acumula las dos ejecuciones registradas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The history file is corrupt

El lector A describe el efecto como «descarta el historial corrupto y guarda solo el run actual»; el lector B describe el efecto como «el historial corrupto se reemplaza por uno con solo la ejecución actual». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The history file is corrupt» es la correcta?**
- (A) «descarta el historial corrupto y guarda solo el run actual»
- (B) «el historial corrupto se reemplaza por uno con solo la ejecución actual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The top-level keys never change

El lector A describe el efecto como «las claves del JSON coinciden exactamente con el esquema»; el lector B describe el efecto como «el JSON expone exactamente las claves de primer nivel del esquema». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The top-level keys never change» es la correcta?**
- (A) «las claves del JSON coinciden exactamente con el esquema»
- (B) «el JSON expone exactamente las claves de primer nivel del esquema»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Two paths, one invocation

El lector A describe el efecto como «invoca el runner una vez con las dos rutas»; el lector B describe el efecto como «el runner se invoca una sola vez recibiendo ambas rutas». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Two paths, one invocation» es la correcta?**
- (A) «invoca el runner una vez con las dos rutas»
- (B) «el runner se invoca una sola vez recibiendo ambas rutas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-001 — R-ORC-001 sólo exige exit 0 y `all_green: true` cuando «todos» los requisitos están verdes: en un change con cero requisitos la condición es vacíamente cierta, así que una implementación literal responde `all_green: true`, `counts.total: 0` y código `0` sin haber ejecutado un solo test, y el estado `verified` se concede sobre un oráculo que no verificó nada.
- **[high]** R-ORC-007 — Nada prohíbe combinar `--dry-run` (R-ORC-006: no se invoca el runner, código 0) con `--record` (R-ORC-007: DEBE añadir «la ejecución» al historial): `oracle.py --change X --dry-run --record` escribe en `oracle.json` un run en el que ningún test corrió, y como R-ORC-006 no fija qué estado llevan los requisitos en dry-run, ese run puede quedar registrado como verde y falsear la única traza que sostiene el veredicto del oráculo.
- **[medium]** R-ORC-002 — R-ORC-002 pide marcar el rojo y «dejar los demás requisitos con el estado que les corresponda», sin exigir que se ejecuten: una implementación que aborta en el primer rojo y marca como `green` todos los requisitos aún no ejecutados pasa el escenario (los otros dos aparecen `green`) y publica en el JSON y en el historial requisitos verdes cuyo test nunca se invocó.
- **[medium]** R-ORC-007 — R-ORC-007 sólo pone cota superior («como mucho los últimos 50 runs») y el escenario sólo obliga a conservar dos: una implementación que trunca el historial a los 2 últimos runs cumple ambas cosas y destruye en cada ejecución el registro histórico acumulado, que es precisamente lo que este requisito dice acumular.

## Escenarios que convergen · 1

- A corrupt history warns without a traceback
