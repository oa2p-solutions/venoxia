# ci Delta

Consolidado el 2026-09-06. `R-CI-011` y `R-CI-012` —que el repositorio no
declare ningún workflow de GitHub Actions, y el contrato completo del CI
interno leído de un solo fichero— viven ahora en
`.venoxia/capabilities/ci/spec.md`.

`R-CI-013`, `R-CI-014` y `R-CI-015` no pasan a la capability. Describían
`templates/ci/venoxia-gate.yml` y la sección del README que la documentaba, y
el change `2026-09-06-portable-gate` retira los dos: la puerta del consumidor
deja de ser un workflow y pasa a ser un comando, `scripts/gate.py`. El motivo
está en su `proposal.md`; en una frase, un fichero de CI obliga a Venoxia a
opinar sobre la forja, el runner y la autenticación de quien lo copia, y esas
tres opiniones son justo lo que no le corresponde.

El texto original de los cinco requisitos está en el historial de git, y la
evidencia de su ciclo rojo→verde sigue en `oracle.json`, junto a
`proposal.md`, `divergence.md` y `readings/`.
