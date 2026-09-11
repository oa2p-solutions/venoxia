# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-technical-contract/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 29
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 14 divergencias blandas sobre los 29 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 14

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Every import resolves to the standard library or to the repository

El lector A describe el efecto como «el test pasa: todos los imports son stdlib o del repo»; el lector B describe el efecto como «el test pasa: todos los imports son válidos». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every import resolves to the standard library or to the repository» es la correcta?**
- (A) «el test pasa: todos los imports son stdlib o del repo»
- (B) «el test pasa: todos los imports son válidos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No script shells out through os

El lector A describe el efecto como «el test pasa: ningún script llama a funciones os shell»; el lector B describe el efecto como «el test pasa: ninguna llamada usa os.system/popen/exec/spawn». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No script shells out through os» es la correcta?**
- (A) «el test pasa: ningún script llama a funciones os shell»
- (B) «el test pasa: ninguna llamada usa os.system/popen/exec/spawn»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every file at or above its threshold

El lector A describe el efecto como «coverage.py termina con código 0»; el lector B describe el efecto como «el proceso termina en verde, todos los ficheros cumplen su umbral». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Every file at or above its threshold» es la correcta?**
- (A) «coverage.py termina con código 0»
- (B) «el proceso termina en verde, todos los ficheros cumplen su umbral»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One file below its threshold

El lector A describe el efecto como «coverage.py termina con código 1»; el lector B describe el efecto como «el proceso termina en rojo por un fichero bajo umbral». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «One file below its threshold» es la correcta?**
- (A) «coverage.py termina con código 1»
- (B) «el proceso termina en rojo por un fichero bajo umbral»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A script the suite never runs is below its threshold

El lector A describe el efecto como «cuenta como por debajo del umbral, código 1»; el lector B describe el efecto como «cuenta como por debajo de umbral y falla el proceso». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A script the suite never runs is below its threshold» es la correcta?**
- (A) «cuenta como por debajo del umbral, código 1»
- (B) «cuenta como por debajo de umbral y falla el proceso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A file without an entry is held to the core floor

El lector A describe el efecto como «se le aplica el umbral suelo del núcleo, 85»; el lector B describe el efecto como «el fichero se mide contra el suelo del núcleo, 85». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A file without an entry is held to the core floor» es la correcta?**
- (A) «se le aplica el umbral suelo del núcleo, 85»
- (B) «el fichero se mide contra el suelo del núcleo, 85»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unknown option is 2 in all five

El lector A describe el efecto como «los cinco scripts terminan con código 2»; el lector B describe el efecto como «los cinco scripts terminan con código de error de uso». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «An unknown option is 2 in all five» es la correcta?**
- (A) «los cinco scripts terminan con código 2»
- (B) «los cinco scripts terminan con código de error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A root that does not exist is 2 in all five

El lector A describe el efecto como «los cinco scripts terminan con código 2»; el lector B describe el efecto como «los cinco scripts terminan con código de error de uso». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A root that does not exist is 2 in all five» es la correcta?**
- (A) «los cinco scripts terminan con código 2»
- (B) «los cinco scripts terminan con código de error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: In the gate, 2 means it could not look

El lector A describe el efecto como «gate.py termina con código 2 si falta venoxia.json»; el lector B describe el efecto como «gate.py termina sin veredicto al faltar venoxia.json». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «In the gate, 2 means it could not look» es la correcta?**
- (A) «gate.py termina con código 2 si falta venoxia.json»
- (B) «gate.py termina sin veredicto al faltar venoxia.json»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Extra keys never remove the schema ones

El lector A describe el efecto como «build_payload conserva las siete claves del esquema»; el lector B describe el efecto como «el informe conserva las siete claves junto a las añadidas». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Extra keys never remove the schema ones» es la correcta?**
- (A) «build_payload conserva las siete claves del esquema»
- (B) «el informe conserva las siete claves junto a las añadidas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The three steps by name

El lector A describe el efecto como «lista matrix, gate y plugin-validate con su comando, sin ejecutar»; el lector B describe el efecto como «la salida nombra matrix, gate y plugin-validate sin ejecutarlos». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The three steps by name» es la correcta?**
- (A) «lista matrix, gate y plugin-validate con su comando, sin ejecutar»
- (B) «la salida nombra matrix, gate y plugin-validate sin ejecutarlos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every step passes

El lector A describe el efecto como «la comprobación termina con código 0»; el lector B describe el efecto como «la comprobación termina en verde». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Every step passes» es la correcta?**
- (A) «la comprobación termina con código 0»
- (B) «la comprobación termina en verde»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A required executable is missing

El lector A describe el efecto como «termina con código 2 y nombra el ejecutable que falta»; el lector B describe el efecto como «termina sin veredicto y el mensaje nombra el ejecutable ausente». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A required executable is missing» es la correcta?**
- (A) «termina con código 2 y nombra el ejecutable que falta»
- (B) «termina sin veredicto y el mensaje nombra el ejecutable ausente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unknown option

El lector A describe el efecto como «termina con código 2 y muestra el mensaje de uso»; el lector B describe el efecto como «termina sin veredicto con un mensaje de uso». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «An unknown option» es la correcta?**
- (A) «termina con código 2 y muestra el mensaje de uso»
- (B) «termina sin veredicto con un mensaje de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-TEC-002 — Las dos listas de R-TEC-002 son cerradas: un script puede abrir conexiones TCP con `asyncio.open_connection` o `selectors` (ninguno figura entre `urllib`/`http`/`socket`/`ssl`/`smtplib`/`ftplib`/`xmlrpc`) y lanzar procesos con `pty.spawn`, `multiprocessing` u `os.fork` (ninguno figura entre `os.system`/`os.popen`/`os.exec*`/`os.spawn*`/`os.posix_spawn*`), pasando los cinco escenarios en verde mientras consulta a un modelo para decidir un veredicto; se pierde la garantía central de que la aritmética de los veredictos está en código y es determinista.
- **[medium]** R-TEC-004 — El suelo de 85 sólo protege a los ficheros sin entrada en `tools/coverage-threshold.json`; añadir a `guardian.py` una entrada con umbral `0` deja `tools/coverage.py` en código `0` con cero líneas cubiertas y cumple los cinco escenarios, de modo que la puerta de cobertura se desactiva editando un fichero de datos y sin tocar una línea de código ni de test.
- **[medium]** R-TEC-006 — Un `build_payload` implementado como `{**esquema, **extra}` deja que una clave añadida con el nombre de una del esquema (`compliant`, `findings`, `adopted`) sobrescriba su valor: las siete claves siguen presentes y los tres escenarios pasan, pero el JSON versión 1 publica un veredicto falso que los graders de evals y cualquier consumidor leen como bueno.
- **[medium]** R-TEC-001 — El escenario acepta como válido todo módulo que sea «un fichero o paquete del propio repositorio»: copiar un paquete de terceros dentro de `scripts/` o `tools/` (un `vendor/requests.py`) hace que su import pase el test, con lo que el repositorio incorpora código ajeno sin versión ni auditoría mientras el contrato de cero dependencias sigue en verde.

## Escenarios que convergen · 15

- A third-party import fails the test
- pytest is never a requirement
- A dynamic import fails the test
- No network module in any script
- No model client in any script
- A network import fails the test
- Only the oracle and the gate spawn subprocesses
- Only the standard library
- No shared package
- No subprocess and no dynamic import
- The report names each file with its figures
- The version is the integer one
- Serialisation keeps every key
- Coverage is not a step of its own
- One step fails
