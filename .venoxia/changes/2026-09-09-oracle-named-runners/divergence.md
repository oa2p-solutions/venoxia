# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-oracle-named-runners/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 38
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 14 divergencias blandas sobre los 38 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 14

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The command runs character for character

El lector A describe el efecto como «ejecuta el command del runner sin sustituir nada»; el lector B describe el efecto como «ejecuta el command del runner coverage tal cual». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The command runs character for character» es la correcta?**
- (A) «ejecuta el command del runner sin sustituir nada»
- (B) «ejecuta el command del runner coverage tal cual»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A missing anchor does not run the verbatim command

El lector A describe el efecto como «no se ejecuta el comando de ese runner»; el lector B describe el efecto como «no ejecuta el comando cuando falta el fichero de verifies». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A missing anchor does not run the verbatim command» es la correcta?**
- (A) «no se ejecuta el comando de ese runner»
- (B) «no ejecuta el comando cuando falta el fichero de verifies»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The default runner still demands the placeholder

El lector A describe el efecto como «el proceso termina por falta del placeholder»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The default runner still demands the placeholder» es la correcta?**
- (A) «el proceso termina por falta del placeholder»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An undeclared name is a usage error

El lector A describe el efecto como «el proceso termina como error de uso»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «An undeclared name is a usage error» es la correcta?**
- (A) «el proceso termina como error de uso»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing runs, not even the other requirements

El lector A describe el efecto como «el proceso termina y no ejecuta ningún comando»; el lector B describe el efecto como «el proceso termina con código 2, ningún comando corre». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Nothing runs, not even the other requirements» es la correcta?**
- (A) «el proceso termina y no ejecuta ningún comando»
- (B) «el proceso termina con código 2, ningún comando corre»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The message names the runner and the file

El lector A describe el efecto como «el proceso termina y stderr avisa nombrando el runner y el fichero»; el lector B describe el efecto como «termina con código 2 y stderr nombra runner y fichero». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The message names the runner and the file» es la correcta?**
- (A) «el proceso termina y stderr avisa nombrando el runner y el fichero»
- (B) «termina con código 2 y stderr nombra runner y fichero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is recorded

El lector A describe el efecto como «el proceso termina sin escribir ningún fichero nuevo»; el lector B describe el efecto como «el proceso termina con código 2 y no crea ningún fichero». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Nothing is recorded» es la correcta?**
- (A) «el proceso termina sin escribir ningún fichero nuevo»
- (B) «el proceso termina con código 2 y no crea ningún fichero»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Dry run is a usage error too

El lector A describe el efecto como «el proceso termina como error de uso»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «Dry run is a usage error too» es la correcta?**
- (A) «el proceso termina como error de uso»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A runner without a command

El lector A describe el efecto como «el proceso termina como error de uso»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A runner without a command» es la correcta?**
- (A) «el proceso termina como error de uso»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A runners key that is not an object

El lector A describe el efecto como «el proceso termina como error de uso»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A runners key that is not an object» es la correcta?**
- (A) «el proceso termina como error de uso»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A runner whose cwd does not exist

El lector A describe el efecto como «el proceso termina como error de uso»; el lector B describe el efecto como «el proceso termina con código 2». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «A runner whose cwd does not exist» es la correcta?**
- (A) «el proceso termina como error de uso»
- (B) «el proceso termina con código 2»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A named runner is named in its result

El lector A describe el efecto como «el resultado del requisito incluye runner.name igual a alt»; el lector B describe el efecto como «el elemento de results trae runner.name igual a alt». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A named runner is named in its result» es la correcta?**
- (A) «el resultado del requisito incluye runner.name igual a alt»
- (B) «el elemento de results trae runner.name igual a alt»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The top level keeps its eight keys

El lector A describe el efecto como «el documento mantiene exactamente ocho claves de primer nivel»; el lector B describe el efecto como «las claves de primer nivel son las ocho de R-ORC-008». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The top level keeps its eight keys» es la correcta?**
- (A) «el documento mantiene exactamente ocho claves de primer nivel»
- (B) «las claves de primer nivel son las ocho de R-ORC-008»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An undeclared runner name

El lector A describe el efecto como «salta V19 sobre el requisito y es la única regla que salta»; el lector B describe el efecto como «salta V19 sobre el requisito y ninguna otra regla». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An undeclared runner name» es la correcta?**
- (A) «salta V19 sobre el requisito y es la única regla que salta»
- (B) «salta V19 sobre el requisito y ninguna otra regla»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-014 — R-ORC-014 obliga a poner `status: green` cuando el `command` del runner con nombre termina en 0, y lo único que exige de la parte del requisito es que el fichero de `verifies:` exista: un runner declarado como `command: "true"` (o incluso un solo espacio, que pasa el «command no vacío» de R-ORC-015 y de V19) da verde a todos los requisitos que lo nombren sin que su fichero de test llegue a ejecutarse nunca, rompiendo el único vínculo del sistema entre requisito y test y permitiendo que un change llegue a `verified` con pruebas que no corrieron.
- **[medium]** R-ORC-015 — R-ORC-015 sólo exige código 2 cuando el `cwd` del runner «no existe en disco»: un `cwd` que apunta a un fichero regular (o a un enlace roto hacia un fichero) supera esa comprobación previa, así que la ejecución arranca, otros requisitos ya han corrido sus comandos y el fallo al lanzar el proceso aparece a mitad de camino; una implementación literal lo atribuye como `red` de ese requisito, justo lo que el título del requisito promete que nunca pasará, y deja un run grabado que culpa al test de un error de configuración.

## Escenarios que convergen · 24

- The named runner replaces the default for that requirement
- A requirement without runner keeps the default
- The placeholder of a named runner is substituted
- A runner with its own cwd runs there
- The paths follow the runner into its cwd
- A runner without cwd inherits the project's
- A failing named runner is a red requirement
- A verbatim runner that passes is a green requirement
- The verifies path is still the anchor
- Dry run prints the verbatim command
- The command recorded is the one that ran
- The default runner has no name
- The default runner still records its command
- The working directory is recorded
- A missing requirement carries its runner too
- The recorded history carries it
- No venoxia.json at all
- A declared runner is silent
- No runner, no rule
- An empty runner
- A declared runner without a command
- A declared runner whose cwd does not exist
- A corrupt venoxia.json does not crash the validator
- The hint shows the entry to add
