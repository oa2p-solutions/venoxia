# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-06-single-ci/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 47
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 10 divergencias blandas sobre los 47 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 10

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The API key never reaches the job that runs pull request code

El lector A describe el efecto como «secrets.ANTHROPIC_API_KEY sólo aparece dentro del job evals»; el lector B describe el efecto como «la clave sólo aparece dentro del job evals, no a nivel de workflow». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The API key never reaches the job that runs pull request code» es la correcta?**
- (A) «secrets.ANTHROPIC_API_KEY sólo aparece dentro del job evals»
- (B) «la clave sólo aparece dentro del job evals, no a nivel de workflow»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Checkout of a pinned Venoxia

El lector A describe el efecto como «el paso hace checkout de OA2P/venoxia con ref y token»; el lector B describe el efecto como «el checkout de Venoxia usa ref de VENOXIA_REF y token de VENOXIA_TOKEN». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Checkout of a pinned Venoxia» es la correcta?**
- (A) «el paso hace checkout de OA2P/venoxia con ref y token»
- (B) «el checkout de Venoxia usa ref de VENOXIA_REF y token de VENOXIA_TOKEN»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An undefined reference fails the job

El lector A describe el efecto como «la plantilla deja el job en fallo»; el lector B describe el efecto como «si el consumidor no define VENOXIA_REF, el job falla». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An undefined reference fails the job» es la correcta?**
- (A) «la plantilla deja el job en fallo»
- (B) «si el consumidor no define VENOXIA_REF, el job falla»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One oracle invocation per gated change

El lector B registra «se ejecuta el test_command del proyecto consumidor» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «One oracle invocation per gated change»?**
- (A) «se ejecuta el test_command del proyecto consumidor»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The oracle actually runs the tests

El lector B registra «se ejecutan los tests reales del change» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The oracle actually runs the tests»?**
- (A) «se ejecutan los tests reales del change»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: Changes in other states are left alone

El lector A describe el efecto como «el paso no invoca el oráculo para ese change»; el lector B describe el efecto como «changes en draft o specified no se invocan con el oráculo». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Changes in other states are left alone» es la correcta?**
- (A) «el paso no invoca el oráculo para ese change»
- (B) «changes en draft o specified no se invocan con el oráculo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The state is read without regard to case or spacing

El lector A describe el efecto como «el paso trata el estado normalizado, ignorando mayúsculas y espacios»; el lector B describe el efecto como «el paso trata Verified o validated con espacios como el estado nombrado». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The state is read without regard to case or spacing» es la correcta?**
- (A) «el paso trata el estado normalizado, ignorando mayúsculas y espacios»
- (B) «el paso trata Verified o validated con espacios como el estado nombrado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A red oracle fails the job

El lector A describe el efecto como «el paso deja el job en fallo»; el lector B describe el efecto como «si un oráculo no termina en verde, el job falla». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A red oracle fails the job» es la correcta?**
- (A) «el paso deja el job en fallo»
- (B) «si un oráculo no termina en verde, el job falla»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unreadable change fails the job

El lector A describe el efecto como «el paso deja el job en fallo y nombra ese change»; el lector B describe el efecto como «change.json ilegible, inválido o sin state hace fallar el job nombrando el change». Similitud de contenido 0.36, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unreadable change fails the job» es la correcta?**
- (A) «el paso deja el job en fallo y nombra ese change»
- (B) «change.json ilegible, inválido o sin state hace fallar el job nombrando el change»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A project with no active change passes

El lector A describe el efecto como «el paso termina sin fallo»; el lector B describe el efecto como «sin changes validated ni verified y todos legibles, el paso pasa sin fallo». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A project with no active change passes» es la correcta?**
- (A) «el paso termina sin fallo»
- (B) «sin changes validated ni verified y todos legibles, el paso pasa sin fallo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-012 — La prohibición es una lista cerrada (`||` y `if !`) y ningún escenario mira el código de salida real: un paso `run: |` con `set +e` delante, o con una segunda línea `exit 0` detrás de `python3 -m unittest discover -s tests -q` (uno de sus comandos sigue *terminando* en el comando canónico, no hay `if:` ni `continue-on-error`), cumple los quince escenarios y deja el job `tests` en verde con la suite en rojo.
- **[high]** R-CI-014 — El escenario «Changes in other states are left alone» obliga a no invocar el oráculo salvo en `validated`/`verified`, y sólo se exige fallar cuando el `change.json` es ilegible o no trae `state`: cambiar `"state": "verified"` por `"specified"` o `"archived"` —o borrar el directorio del change— hace que la puerta no ejecute ningún oráculo y termine en verde, de modo que una palabra en un fichero de metadatos desactiva exactamente la puerta que debía bloquear la fusión.
- **[medium]** R-CI-013 — La plantilla fija el intérprete a un contenedor `python:3.14-slim` y prohíbe todo `pip install`, mientras R-CI-014 obliga a ejecutar de verdad (sin `--dry-run`) el `test_command` del consumidor: para cualquier proyecto consumidor cuya suite tenga una sola dependencia, el oráculo falla siempre por `ModuleNotFoundError`, la puerta queda permanentemente roja sin poder fusionar nada y la propia plantilla prohíbe el único remedio.
- **[medium]** R-CI-013 — El único control exigido sobre `VENOXIA_REF` es que no tenga valor de reserva y que el job falle cuando *no está definida*; una implementación que sólo comprueba que la variable no está vacía acepta `VENOXIA_REF=main`, y el consumidor queda anclado a la rama en movimiento de Venoxia —justo el fallo que el requisito dice querer evitar— porque el escenario del tag sólo obliga a que la documentación lo «pida y advierta», no a rechazarlo.

## Escenarios que convergen · 37

- No workflow directory for GitHub Actions
- The la forja interna workflow is the one on disk
- The tests job runs the canonical suite command
- The self-spec job runs the validator in strict mode
- The self-spec job runs the charter linter in strict mode
- The coverage job runs the coverage tool
- The plugin-validate job validates the plugin structure
- The workflow starts without anyone asking
- Only two jobs carry a safety net
- No job is switched off
- No job depends on the manual one
- No step is switched off by a condition
- No step discards its own failure
- The evals job is manual
- The evals job declares the API key
- Every job checks out the commit under test
- No command hides its own failure
- No checkout pins a moving reference
- The pinned reference has no fallback
- The pinned reference is a tag, not a branch
- The failure names the missing variable
- The gate never falls back to the default branch
- The internal runner label
- The interpreter comes from the image
- The two linters in strict mode
- No dependency installer
- A missing project config fails the job
- The oracle step runs without the checkout token
- The token belongs to the checkout step alone
- No checkout leaves a credential on disk
- The gate runs on the events that gate a merge
- No job or step discards its own failure
- The section names the only workflow
- The section names the runner labels
- The section names the consumer template
- The section explains the manual evals
- The section no longer names a GitHub workflow
