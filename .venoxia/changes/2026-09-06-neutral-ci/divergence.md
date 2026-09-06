# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-06-neutral-ci/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 6
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 3 divergencias blandas sobre los 6 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The workflow is scanned like everything else

El lector A describe el efecto como «el workflow de CI entra en el barrido de documentación publicada»; el lector B describe el efecto como «el workflow de CI aparece incluido en el barrido de documentación». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The workflow is scanned like everything else» es la correcta?**
- (A) «el workflow de CI entra en el barrido de documentación publicada»
- (B) «el workflow de CI aparece incluido en el barrido de documentación»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The workflow does not name the internal forge

El lector A describe el efecto como «el nombre de la forja interna no aparece en ninguna capitalización»; el lector B describe el efecto como «el texto del workflow, con comentarios, no nombra la forja». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The workflow does not name the internal forge» es la correcta?**
- (A) «el nombre de la forja interna no aparece en ninguna capitalización»
- (B) «el texto del workflow, con comentarios, no nombra la forja»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The workflow does not name the internal runner labels

El lector A describe el efecto como «ninguna de las dos etiquetas del runner interno aparece»; el lector B describe el efecto como «el texto del workflow, con comentarios, no nombra las etiquetas del runner». Similitud de contenido 0.18, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The workflow does not name the internal runner labels» es la correcta?**
- (A) «ninguna de las dos etiquetas del runner interno aparece»
- (B) «el texto del workflow, con comentarios, no nombra las etiquetas del runner»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-CI-008 — R-CI-008 exige que cada `runs-on` lea una variable del repositorio, pero nada obliga a que esa variable esté declarada ni a que el workflow falle de forma visible si está vacía, y sus tres escenarios sólo parsean el YAML. Un workflow con `runs-on: ${{ vars.RUNNER }}` sobre una variable inexistente deja los cinco jobs sin máquina (encolados para siempre o abortando en el arranque): la puerta de CI deja de ejecutarse en cada push y el test del requisito sigue verde porque nunca observa una ejecución real.
- **[medium]** R-CI-018 — R-CI-018 sólo instrumenta la ausencia de tres literales (nombre de la forja y dos etiquetas de runner) en el texto del workflow; una implementación que borra esas tres cadenas y deja en un comentario `# runner interno del rack de la oficina, arm64, host 10.x.x.x, SSH 2222` pasa los tres escenarios y publica en un repositorio público exactamente el mapa de infraestructura que R-CI-008 dice querer ocultar.
- **[medium]** R-CI-018 — El barrido de R-CI-018 se limita a una lista cerrada de rutas publicadas (README, docs, skills, templates, scripts, hooks, .claude-plugin y el workflow) y deja fuera `tests/**` y `.venoxia/**`, que en un repositorio público se clonan igual; la implementación literal guarda los tres términos prohibidos en `tests/test_gate.py` —como el propio delta describe— y cualquiera que haga `git clone` sigue obteniendo el nombre de la forja interna, las dos etiquetas del runner y el espejo de respaldo. El requisito reubica la filtración en lugar de eliminarla, y una vez publicada es irreversible.

## Escenarios que convergen · 3

- Triggers read from disk
- The five jobs by name
- No runner label is written down
