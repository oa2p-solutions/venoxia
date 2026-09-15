# divergence Delta

Consolidado el 2026-09-15, para que `2026-09-15-divergence-policy-decisions`
pueda modificar `R-DIV-015` y `R-DIV-016` (V13 exige que lo modificado viva en
una capability). `R-DIV-013` a `R-DIV-017` —la agrupación por decisión raíz y la
entrevista por decisión— viven ahora en `.venoxia/capabilities/divergence/spec.md`,
con el texto vigente de cada ID tal cual estaba en este delta.

El texto original está en el historial de git, y la evidencia de su ciclo
rojo→verde sigue en `oracle.json`, junto a `proposal.md`, `divergence.md`,
`readings/` y `decisions.json`. Límite conocido (D8): un change `archived` deja
de ejecutarse en `gate.py`; los tests siguen corriendo en la suite.
