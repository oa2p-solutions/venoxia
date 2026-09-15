# 2026-09-15-charter-adaptive-interview Proposal

## Why

La entrevista de `/venoxia:charter` se contesta hoy en catorce a veintidós preguntas
en un proyecto nuevo, y en ocho a diez incluso cuando el usuario llega con el
producto explicado: el «camino corto» del Paso 1 redacta primero, pero el mínimo
del Paso 5 le exige después la tanda de hechos y apuestas entera, las
convenciones técnicas, el comando de pruebas y el aviso del guardián. Dos tandas
preguntan lo mismo (qué podrá hacer alguien que hoy no puede), el usuario, su
apaño, el problema y la primera capability se preguntan por separado cuando salen
de una sola historia, y la tanda de evidencia vuelve a entrevistar sobre casillas
ya contestadas. Quien retoma un acta recibe una pregunta por apuesta antes de que
nadie le pregunte qué quiere hacer. El análisis completo está en
`2026-09-15-charter-rediseno.md`.

## What Changes

- La entrevista se conduce con un mapa de cobertura de nueve casillas y cinco
  estados; una pregunta sólo se hace cuando su casilla está en `missing` o en
  `conflicting`, y la skill nombra la casilla antes de preguntar.
- La conversación se clasifica en tres modos de entrada más «retomar»: con el
  producto explicado o con un proyecto existente, el acta se redacta antes de la
  primera pregunta; con una idea difusa, la primera pregunta pide el último caso
  real y la segunda, qué parte eliminaría primero y qué tendría que ver esa persona.
- Los hechos y las apuestas se separan con una síntesis y una sola corrección
  general; `revisit` y `fatal` sólo se preguntan por las apuestas que queden
  abiertas, y ninguna apuesta se fabrica cuando el usuario afirma que todo está
  observado.
- Alcanzado el mínimo, la skill presenta el borrador completo y ofrece aprobarlo o
  profundizar; no sigue entrevistando por iniciativa propia.
- Comando de pruebas, convenciones técnicas, oráculo, guardián y esqueleto salen de
  la entrevista a una preparación posterior, detectada en el repositorio y
  preguntada sólo ante una ambigüedad que bloquee el paso siguiente.
- Al retomar un acta se resume el estado, se agrupan las apuestas abiertas y se
  pregunta qué quiere hacer el usuario antes de tocar ninguna apuesta.
- El linter gana `C21`: una marca de inferencia sin confirmar dentro del acta es un
  error, para que ninguna inferencia del borrador llegue al disco como acuerdo.
- De paso, la `description` del frontmatter deja de decir «apuestas con fecha de
  revisión», que contradice a `C12`.

## Capabilities

### Modified Capabilities

- `charter-lint`: la skill charter gana el mapa, los modos, la síntesis, la
  frontera mínima, la preparación y el retomar; el linter gana una regla.

## Impact

- `skills/charter/SKILL.md` se reescribe; las frases que `tests/test_charter_skill.py`
  exige para `R-CHL-006` se conservan literalmente y el destino de cada convención
  técnica no cambia.
- `charter_lint.py --strict` pasa a salir con `1` sobre un acta que conserve
  `<!-- inferred -->`; ningún acta existente lleva esa marca, así que ninguna se ve
  afectada. La tabla de reglas del README pasa de veinte filas a veintiuna.
- Ningún formato del acta ni de la plantilla cambia: los proyectos Venoxia
  existentes siguen pasando el linter tal cual.
- Los evals ganan seis casos conversacionales de charter; llegan en un commit
  aparte, con su protocolo de persona descrito en `evals/README.md`.

## Confidence

- **Que la reconstrucción desde el disco baste para no preguntar nada que el disco
  ya diga** · `medium` · depende de cuánto documente cada repositorio · se revisa
  cuando tres entrevistas reales hayan pasado por el modo de proyecto existente y se
  cuente cuántas preguntas sobraron o faltaron.
- **Que una síntesis con una corrección general separe hechos y apuestas tan bien
  como la pregunta por sección** · `medium` · es la apuesta central del rediseño ·
  se revisa cuando tres actas reales hayan salido de la síntesis y alguien compare
  sus apuestas con lo que después resultó supuesto.
- **Que la preparación detecte el comando de pruebas sin preguntar** · `medium` ·
  los manifiestos no siempre declaran uno · se revisa cuando tres proyectos reales
  hayan pasado por la preparación y se cuente en cuántos hubo que preguntar.
- **El resto de la propuesta** · `high` · son afirmaciones sobre el texto de la
  skill y sobre una marca literal en el fichero.
