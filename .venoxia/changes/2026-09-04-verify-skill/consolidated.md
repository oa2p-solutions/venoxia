# oracle Delta

Consolidado el 2026-09-09 (paso C4.0 de `PLAN.md`, decisión D11). `R-ORC-009` y `R-ORC-010` —la skill `/venoxia:verify`: su contrato de herramientas y la regla de que `verified` sólo sigue a un rojo previo o a una confirmación explícita—
viven ahora en `.venoxia/capabilities/oracle/spec.md`, con el texto vigente de
cada ID tal cual estaba en este delta: ninguno de los tres changes de `oracle`
modificó un requisito de otro.

El texto original está en el historial de git, y la evidencia de su ciclo
rojo→verde sigue en `oracle.json`, junto a `proposal.md`, `divergence.md` y
`readings/`. Límite conocido (D8): un change `archived` deja de ejecutarse en
`gate.py`; los tests siguen corriendo en la suite y `R-ORC-013` a `R-ORC-016`
siguen en su change `verified`, que el gate sí ejecuta.
