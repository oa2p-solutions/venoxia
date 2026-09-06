# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-06-portable-gate/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 45
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 32 divergencias blandas sobre los 45 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 32

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A project that passes the gate

El lector A describe el efecto como «termina con éxito tras pasar acta, specs y oráculos»; el lector B describe el efecto como «el proceso termina con éxito». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project that passes the gate» es la correcta?**
- (A) «termina con éxito tras pasar acta, specs y oráculos»
- (B) «el proceso termina con éxito»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A specification that does not conform

El lector A describe el efecto como «rechaza el proyecto por una spec inválida»; el lector B describe el efecto como «el proceso falla porque un requisito omite verifies». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A specification that does not conform» es la correcta?**
- (A) «rechaza el proyecto por una spec inválida»
- (B) «el proceso falla porque un requisito omite verifies»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A charter that does not conform

El lector A describe el efecto como «rechaza el proyecto por un acta que incumple»; el lector B describe el efecto como «el proceso falla porque el acta incumple sus reglas». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A charter that does not conform» es la correcta?**
- (A) «rechaza el proyecto por un acta que incumple»
- (B) «el proceso falla porque el acta incumple sus reglas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A verified change with a red oracle

El lector A describe el efecto como «rechaza porque el oráculo de un change verified no está verde»; el lector B describe el efecto como «el proceso falla porque el oráculo de un verified está rojo». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A verified change with a red oracle» es la correcta?**
- (A) «rechaza porque el oráculo de un change verified no está verde»
- (B) «el proceso falla porque el oráculo de un verified está rojo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The oracle runs for real

El lector A describe el efecto como «rechaza porque el oráculo se ejecuta sin --dry-run»; el lector B describe el efecto como «el proceso falla porque el oráculo corre sin --dry-run». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The oracle runs for real» es la correcta?**
- (A) «rechaza porque el oráculo se ejecuta sin --dry-run»
- (B) «el proceso falla porque el oráculo corre sin --dry-run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The gate writes no evidence

El lector A describe el efecto como «pasa sin modificar el historial grabado del oráculo»; el lector B describe el efecto como «el proceso pasa sin modificar el oracle.json existente». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The gate writes no evidence» es la correcta?**
- (A) «pasa sin modificar el historial grabado del oráculo»
- (B) «el proceso pasa sin modificar el oracle.json existente»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A specified change whose test does not exist yet passes

El lector A describe el efecto como «pasa aunque el verifies: de un change specified no exista aún»; el lector B describe el efecto como «el proceso pasa porque el delta de specified aún no se valida». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A specified change whose test does not exist yet passes» es la correcta?**
- (A) «pasa aunque el verifies: de un change specified no exista aún»
- (B) «el proceso pasa porque el delta de specified aún no se valida»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The gate runs its own scripts, not the inspected project's

El lector A describe el efecto como «ejecuta sus propios scripts, ignora los del proyecto y rechaza»; el lector B describe el efecto como «el proceso ejecuta sus propios scripts y falla por el acta real». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The gate runs its own scripts, not the inspected project's» es la correcta?**
- (A) «ejecuta sus propios scripts, ignora los del proyecto y rechaza»
- (B) «el proceso ejecuta sus propios scripts y falla por el acta real»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A check that cannot be carried out does not pass

El lector A describe el efecto como «rechaza por no poder completar una de las tres comprobaciones»; el lector B describe el efecto como «el proceso termina en error de uso, nunca en verde». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A check that cannot be carried out does not pass» es la correcta?**
- (A) «rechaza por no poder completar una de las tres comprobaciones»
- (B) «el proceso termina en error de uso, nunca en verde»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An active change with no requirement does not pass

El lector A describe el efecto como «rechaza un change validated o verified sin requisitos en su delta»; el lector B describe el efecto como «el proceso falla porque el change activo no declara requisitos». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An active change with no requirement does not pass» es la correcta?**
- (A) «rechaza un change validated o verified sin requisitos en su delta»
- (B) «el proceso falla porque el change activo no declara requisitos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A project with no charter cannot be gated

El lector A describe el efecto como «rechaza y nombra en stderr .venoxia/charter.md ausente o ilegible»; el lector B describe el efecto como «el proceso termina en error de uso y nombra el acta». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project with no charter cannot be gated» es la correcta?**
- (A) «rechaza y nombra en stderr .venoxia/charter.md ausente o ilegible»
- (B) «el proceso termina en error de uso y nombra el acta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A capability spec with no requirement does not pass

El lector A describe el efecto como «rechaza y nombra en stderr el spec.md vacío de requisitos»; el lector B describe el efecto como «el proceso falla y nombra en stderr la capability vacía». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A capability spec with no requirement does not pass» es la correcta?**
- (A) «rechaza y nombra en stderr el spec.md vacío de requisitos»
- (B) «el proceso falla y nombra en stderr la capability vacía»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A capability directory without a spec does not pass

El lector A describe el efecto como «rechaza y nombra en stderr el directorio sin spec.md»; el lector B describe el efecto como «el proceso falla y nombra en stderr el directorio sin spec». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A capability directory without a spec does not pass» es la correcta?**
- (A) «rechaza y nombra en stderr el directorio sin spec.md»
- (B) «el proceso falla y nombra en stderr el directorio sin spec»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Every verified change's oracle runs

El lector A describe el efecto como «rechaza y nombra en la salida los dos changes en rojo»; el lector B describe el efecto como «el proceso falla y nombra los dos changes en rojo». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Every verified change's oracle runs» es la correcta?**
- (A) «rechaza y nombra en la salida los dos changes en rojo»
- (B) «el proceso falla y nombra los dos changes en rojo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The summary comes last, after every subprocess

El lector A describe el efecto como «el resumen real de la puerta queda al final de la salida»; el lector B describe el efecto como «el resumen real de la puerta aparece al final, tras el falso». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The summary comes last, after every subprocess» es la correcta?**
- (A) «el resumen real de la puerta queda al final de la salida»
- (B) «el resumen real de la puerta aparece al final, tras el falso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A passing gate says how much it looked at

El lector A describe el efecto como «pasa e informa cuántos spec.md, changes y oráculos miró»; el lector B describe el efecto como «el proceso pasa y reporta cuántos ficheros ha mirado». Similitud de contenido 0.17, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A passing gate says how much it looked at» es la correcta?**
- (A) «pasa e informa cuántos spec.md, changes y oráculos miró»
- (B) «el proceso pasa y reporta cuántos ficheros ha mirado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A failing gate says how much it looked at too

El lector A describe el efecto como «rechaza e informa el mismo recuento de lo mirado»; el lector B describe el efecto como «el proceso falla y también reporta cuántos ficheros ha mirado». Similitud de contenido 0.09, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A failing gate says how much it looked at too» es la correcta?**
- (A) «rechaza e informa el mismo recuento de lo mirado»
- (B) «el proceso falla y también reporta cuántos ficheros ha mirado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The state is read without regard to case or spacing

El lector A describe el efecto como «normaliza "Verified" a verified y rechaza por oráculo rojo»; el lector B describe el efecto como «el proceso falla tratando 'Verified' igual que 'verified'». Similitud de contenido 0.11, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The state is read without regard to case or spacing» es la correcta?**
- (A) «normaliza "Verified" a verified y rechaza por oráculo rojo»
- (B) «el proceso falla tratando 'Verified' igual que 'verified'»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unreadable change does not pass

El lector A describe el efecto como «rechaza por change.json ilegible, inválido o con state desconocido»; el lector B describe el efecto como «el proceso falla por un change.json ilegible o inválido». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unreadable change does not pass» es la correcta?**
- (A) «rechaza por change.json ilegible, inválido o con state desconocido»
- (B) «el proceso falla por un change.json ilegible o inválido»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The unreadable change is named

El lector A describe el efecto como «rechaza y nombra en stderr el change con change.json ilegible»; el lector B describe el efecto como «el proceso falla y nombra en stderr el change ilegible». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The unreadable change is named» es la correcta?**
- (A) «rechaza y nombra en stderr el change con change.json ilegible»
- (B) «el proceso falla y nombra en stderr el change ilegible»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A project with no active change passes

El lector A describe el efecto como «pasa sin changes en verified y con el resto correcto»; el lector B describe el efecto como «el proceso pasa sin ningún change en verified». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project with no active change passes» es la correcta?**
- (A) «pasa sin changes en verified y con el resto correcto»
- (B) «el proceso pasa sin ningún change en verified»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A project with no active change is still checked

El lector A describe el efecto como «rechaza por acta inválida aunque no haya changes activos»; el lector B describe el efecto como «el proceso falla igual, sin changes activos, por el acta». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project with no active change is still checked» es la correcta?**
- (A) «rechaza por acta inválida aunque no haya changes activos»
- (B) «el proceso falla igual, sin changes activos, por el acta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A project without Venoxia cannot be gated

El lector A describe el efecto como «rechaza y nombra en su mensaje la raíz sin .venoxia/»; el lector B describe el efecto como «el proceso termina en error y nombra la raíz inspeccionada». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project without Venoxia cannot be gated» es la correcta?**
- (A) «rechaza y nombra en su mensaje la raíz sin .venoxia/»
- (B) «el proceso termina en error y nombra la raíz inspeccionada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unusable oracle config is a usage error

El lector A describe el efecto como «rechaza por venoxia.json ausente, ilegible o sin test_command usable»; el lector B describe el efecto como «el proceso termina en error por configuración de oráculo inutilizable». Similitud de contenido 0.00, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unusable oracle config is a usage error» es la correcta?**
- (A) «rechaza por venoxia.json ausente, ilegible o sin test_command usable»
- (B) «el proceso termina en error por configuración de oráculo inutilizable»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names the unusable file

El lector A describe el efecto como «rechaza y nombra en stderr .venoxia/venoxia.json»; el lector B describe el efecto como «el proceso falla y nombra en stderr venoxia.json». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The usage error names the unusable file» es la correcta?**
- (A) «rechaza y nombra en stderr .venoxia/venoxia.json»
- (B) «el proceso falla y nombra en stderr venoxia.json»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No checkout or secret of a workflow ships in the repository

El lector A describe el efecto como «fuera de las exclusiones no aparece actions/checkout ni secrets. en ${{ }}»; el lector B describe el efecto como «ningún fichero del repositorio contiene actions/checkout ni secrets. en {{ }}». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No checkout or secret of a workflow ships in the repository» es la correcta?**
- (A) «fuera de las exclusiones no aparece actions/checkout ni secrets. en ${{ }}»
- (B) «ningún fichero del repositorio contiene actions/checkout ni secrets. en {{ }}»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No workflow pinned to a runner ships in the repository

El lector A describe el efecto como «fuera de las exclusiones no aparece la clave runs-on seguida de dos puntos»; el lector B describe el efecto como «ningún fichero del repositorio contiene la clave runs-on seguida de dos puntos». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No workflow pinned to a runner ships in the repository» es la correcta?**
- (A) «fuera de las exclusiones no aparece la clave runs-on seguida de dos puntos»
- (B) «ningún fichero del repositorio contiene la clave runs-on seguida de dos puntos»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The README warns that the gate runs the project's tests

El lector A describe el efecto como «la sección advierte que ejecuta el test_command sin secretos»; el lector B describe el efecto como «README advierte que el comando ejecuta el test_command del proyecto». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The README warns that the gate runs the project's tests» es la correcta?**
- (A) «la sección advierte que ejecuta el test_command sin secretos»
- (B) «README advierte que el comando ejecuta el test_command del proyecto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The README says what the gate does not run

El lector A describe el efecto como «la sección aclara que sólo cubre changes verified, no lo archivado»; el lector B describe el efecto como «README aclara que archivados los ejecuta la suite del proyecto». Similitud de contenido 0.17, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The README says what the gate does not run» es la correcta?**
- (A) «la sección aclara que sólo cubre changes verified, no lo archivado»
- (B) «README aclara que archivados los ejecuta la suite del proyecto»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The published documentation does not name the internal forge

El lector A describe el efecto como «ningún fichero publicado menciona "forgejo" en ninguna forma»; el lector B describe el efecto como «la documentación publicada no menciona 'forgejo' en ningún caso». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The published documentation does not name the internal forge» es la correcta?**
- (A) «ningún fichero publicado menciona "forgejo" en ninguna forma»
- (B) «la documentación publicada no menciona 'forgejo' en ningún caso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The published documentation does not name the internal runner labels

El lector A describe el efecto como «ningún fichero publicado menciona etiquetas, dominio ni puerto internos»; el lector B describe el efecto como «la documentación publicada no menciona etiquetas de runner ni el puerto 2222». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «The published documentation does not name the internal runner labels» es la correcta?**
- (A) «ningún fichero publicado menciona etiquetas, dominio ni puerto internos»
- (B) «la documentación publicada no menciona etiquetas de runner ni el puerto 2222»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The published documentation does not name the backup mirror

El lector A describe el efecto como «ningún fichero publicado menciona expresiones de respaldo o espejo»; el lector B describe el efecto como «la documentación publicada no menciona el espejo de respaldo». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The published documentation does not name the backup mirror» es la correcta?**
- (A) «ningún fichero publicado menciona expresiones de respaldo o espejo»
- (B) «la documentación publicada no menciona el espejo de respaldo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-016 — El escenario «A project without Venoxia is not an error» obliga a terminar con `0` cuando no hay directorio `.venoxia/`, así que una puerta que se invoca con un `--root` mal escrito, antes de que termine el checkout, o sobre un repositorio al que alguien le ha borrado `.venoxia/` en el mismo commit, sale verde sin haber corrido ni el acta, ni el validador, ni un solo test: el borrado completo sale gratis justo donde el requisito cierra esa misma asimetría para `change.json` («borrar el fichero saldría más barato que corromperlo»), y contradice su propio principio de que un `0` debe ser imposible de obtener por accidente. El aviso exigido no cambia nada, porque un job en verde no lo lee nadie.
- **[low]** R-CI-017 — Los tres escenarios de R-CI-017 sólo inspeccionan `templates/`, así que mover `templates/ci/venoxia-gate.yml` a `examples/ci/venoxia-gate.yml` (o a `docs/`) los cumple los tres al pie de la letra —`templates/ci/` no existe, no hay `.yml` bajo `templates/`, no hay `runs-on:` bajo `templates/`— mientras el plugin sigue publicando exactamente la plantilla de workflow con el runner fijado que este requisito existe para eliminar, y de paso queda fuera del alcance de R-CI-018, que tampoco mira ahí.

## Escenarios que convergen · 13

- A validated change with a red oracle does not close the gate
- The output of the three checks reaches whoever runs the gate
- The three checks all run even when the first one fails
- A change directory without change.json does not pass
- The gate names the validated changes it did not run
- A mature project reports zero oracles
- Changes in other states are left alone
- The template directory is gone
- No workflow file under templates
- No file under templates pins a runner
- The README names the gate command
- The README explains the exit codes
- The gate warns about it in its own help
