# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-05-forgejo-ci/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 9
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 1 divergencia blanda sobre los 9 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 1

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: evals only runs by hand

El lector A describe el efecto como «el job evals sólo corre por workflow_dispatch»; el lector B describe el efecto como «el job evals condiciona su ejecución a workflow_dispatch». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «evals only runs by hand» es la correcta?**
- (A) «el job evals sólo corre por workflow_dispatch»
- (B) «el job evals condiciona su ejecución a workflow_dispatch»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-010 — El requisito sólo obliga a que cada comando `run:` de GitHub «aparezca» en el job homónimo de Forgejo y sólo exige `continue-on-error: true` en `coverage` y `plugin-validate`; nada prohíbe declararlo también en `tests` y `self-spec` (o poner `if: false` en sus steps). Un workflow así pasa los cuatro escenarios —que sólo parsean el YAML— y deja el CI interno en verde permanente aunque la suite y el validador estén en rojo, que es exactamente lo contrario de la puerta que este change pretende montar.
- **[medium]** R-CI-010 — La paridad se define únicamente sobre los comandos `run:`, así que el workflow de Forgejo puede omitir los pasos `uses:` del de GitHub, empezando por `actions/checkout`, y seguir cumpliendo «cada comando `run:` aparece en el job homónimo». Sobre el runner interno, cuyo workspace persiste entre ejecuciones, la suite se ejecutaría sobre el árbol que dejó el run anterior: el workflow reporta verde para un commit cuyo código nunca se ha traído ni probado.

## Escenarios que convergen · 8

- Triggers read from disk
- The five jobs by name
- Only the internal runner labels
- The matrix names the three versions
- The interpreter comes from the image
- Same commands per job
- Same safety nets
- evals needs the API key
