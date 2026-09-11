# validator Delta

Consolidado el 2026-09-09, como paso previo a `verify-confirm-green`: `V13`
exige que lo que un delta modifica exista en una capability viva, y ese change
modifica `R-VAL-007`. `R-VAL-006` (`V17`) y `R-VAL-007` (`V18`) viven ahora en
`.venoxia/capabilities/validator/spec.md`, con su texto tal cual estaba aquí.

El texto original está en el historial de git, y la evidencia de su ciclo
rojo→verde sigue en `oracle.json`, junto a `proposal.md`, `divergence.md` y
`readings/`. Límite conocido (D8): un change `archived` deja de ejecutarse en
`gate.py`; sus tests siguen corriendo en la suite.
