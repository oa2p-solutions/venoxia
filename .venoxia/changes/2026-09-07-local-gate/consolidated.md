# ci Delta

Consolidado el 2026-09-09, como paso previo a C4 (`technical-contract`, `PLAN.md`):
`V13` exige que lo que un delta modifica exista en una capability viva, y C4 modifica
`R-CI-019`. `R-CI-019`, `R-CI-020` y `R-CI-021` —la puerta local `tools/check.py`, la matriz en contenedores sin root y el hook de pre-push— viven ahora en `.venoxia/capabilities/ci/spec.md`, con su texto tal cual estaba aquí.

El texto original está en el historial de git, y la evidencia de su ciclo rojo→verde
sigue en `oracle.json`, junto a `proposal.md`, `divergence.md` y `readings/`. Límite
conocido (D8): un change `archived` deja de ejecutarse en `gate.py`; sus tests siguen
corriendo en la suite.
