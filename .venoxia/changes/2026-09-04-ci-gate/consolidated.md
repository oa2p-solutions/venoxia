# ci Delta

Consolidado el 2026-09-06. Los requisitos que este change introdujo
(`R-CI-001`…`R-CI-005`) describían `.github/workflows/ci.yml` y la plantilla
de consumidor para GitHub Actions. El change `2026-09-06-single-ci`
retira GitHub del proyecto entero, así que ese comportamiento deja de
existir y no pasa a `.venoxia/capabilities/ci/spec.md`: lo sustituye
`R-CI-011`, que exige que el repositorio no declare ningún workflow de
GitHub Actions.

El texto original de los cinco requisitos está en el historial de git y la
evidencia de su ciclo rojo→verde sigue en `oracle.json`, junto a
`proposal.md` y `readings/`.
