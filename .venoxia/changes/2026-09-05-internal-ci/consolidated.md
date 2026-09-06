# ci Delta

Consolidado el 2026-09-06. `R-CI-008` y `R-CI-009`, que este change
introdujo, viven ahora en `.venoxia/capabilities/ci/spec.md`: son el
contrato vivo del único CI del repositorio.

`R-CI-010` no pasa a la capability. Medía el workflow de la forja interna **contra**
el de GitHub, y el change `2026-09-06-single-ci` retira el segundo: un
espejo sin original no comprueba nada. Lo que garantizaba —los comandos de
cada job, las redes de seguridad, el `evals` manual y el checkout— lo
enuncia `R-CI-012` leyendo un solo fichero.

El texto original de los tres requisitos está en el historial de git y la
evidencia de su ciclo rojo→verde sigue en `oracle.json`, junto a
`proposal.md`, `divergence.md` y `readings/`.
