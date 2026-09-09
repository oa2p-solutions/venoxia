# ci Delta

Consolidado el 2026-09-09, como paso previo a C4 (`technical-contract`, `PLAN.md`):
`V13` exige que lo que un delta modifica exista en una capability viva, y C4 modifica
`R-CI-019`. La versión vigente de `R-CI-008` y `R-CI-018` —el workflow que no nombra su runner y la documentación pública que no describe el CI interno— sustituye en `.venoxia/capabilities/ci/spec.md` a la que vivía allí desde la consolidación anterior.

El texto original está en el historial de git, y la evidencia de su ciclo rojo→verde
sigue en `oracle.json`, junto a `proposal.md`, `divergence.md` y `readings/`. Límite
conocido (D8): un change `archived` deja de ejecutarse en `gate.py`; sus tests siguen
corriendo en la suite.
