# 2026-09-06-neutral-ci Proposal

## Por qué

El repositorio es público y el CI lo delata. `.forgejo/workflows/ci.yml` fija
`runs-on: CI_RUNNER` y `CI_RUNNER_NODE`, la capability `ci` los enuncia como
contrato, y `tests/test_ci_workflow.py` los comprueba: entre los tres,
quien clona el plugin se lleva el mapa de una infraestructura que no le sirve
para nada y que no es suya.

`R-CI-018` ya prohíbe nombrarlos en lo que el plugin publica como producto, y
dejó fuera el CI con un argumento defendible: un workflow **tiene** que decir
en qué runner corre. Ese argumento sigue siendo cierto para el fichero, no
para las etiquetas literales: un workflow puede pedirle el nombre del runner a
una variable del repositorio y funcionar igual.

## Qué se construye

- El workflow deja de nombrar etiquetas: `runs-on: ${{ vars.CI_RUNNER }}` y
  `${{ vars.CI_RUNNER_NODE }}`. Quien administre la forja las declara una vez.
- La capability `ci` enuncia el contrato sin nombrarlas: los jobs corren en las
  dos variables, no en dos cadenas concretas.
- `tests/test_ci_workflow.py` pasa a `tests/test_ci_workflow.py`, y con él
  los `verifies:` de los requisitos que lo nombran.

## Qué no

- **El directorio `.forgejo/workflows/` se queda.** Es la ruta que la forja
  exige; moverlo a `.github/` quitaría la palabra y traería un problema peor,
  porque GitHub Actions lo ejecutaría en el repositorio público y fallaría por
  runners que allí no existen. Queda como frontera declarada.
- El resto del contrato del CI —los cinco jobs, sus comandos, las redes de
  seguridad, la matriz desde la imagen— no cambia.

## Apuestas

- **Que la forja interna resuelva `vars` en `runs-on`.** `medium`: el contexto
  `vars` está implementado y `runs-on` se evalúa antes de asignar el job, que
  es el orden que hace falta. `revisit:` el primer run real tras el cambio, que
  dirá si el job arranca o queda en `queued` sin runner que lo tome.
