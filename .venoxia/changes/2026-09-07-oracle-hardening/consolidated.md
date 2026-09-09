# oracle Delta

Consolidado el 2026-09-09 (paso C4.0 de `PLAN.md`, decisión D11). `R-ORC-011` y `R-ORC-012` —`--dry-run` y `--record` excluyentes, y la copia del historial corrupto antes de sustituirlo—
viven ahora en `.venoxia/capabilities/oracle/spec.md`, con el texto vigente de
cada ID tal cual estaba en este delta: ninguno de los tres changes de `oracle`
modificó un requisito de otro.

El texto original está en el historial de git, y la evidencia de su ciclo
rojo→verde sigue en `oracle.json`, junto a `proposal.md`, `divergence.md` y
`readings/`. Límite conocido (D8): un change `archived` deja de ejecutarse en
`gate.py`; los tests siguen corriendo en la suite y `R-ORC-013` a `R-ORC-016`
siguen en su change `verified`, que el gate sí ejecuta.
