# 2026-09-15-divergence-root-decisions Proposal

## Why

Cuando un delta admite dos lecturas, la ambigüedad suele ser **una** —«¿se
rechaza con 409 o con 422?», «¿se reserva el pedido completo o sólo las
unidades con stock?»— y el informe de `diff_readings.py` la enseña **varias
veces**: una vez por escenario que la hereda, o una vez por campo en el que los
lectores la escribieron (`effect` y `side_effects` del mismo escenario). La
skill `/venoxia:diverge` plantea entonces la misma pregunta tres o cuatro veces
seguidas, y la cuarta se contesta sin mirar, que es exactamente lo que la
entrevista de divergencia existe para evitar. El análisis está en
`2026-09-15-charter-rediseno.md`, sección 5.

## What Changes

- El script agrupa las divergencias que proceden de la misma decisión raíz,
  con dos criterios deterministas y sin constantes nuevas: dos campos del
  mismo escenario cuyas lecturas comparten tokens distintivos en cada lector,
  y el mismo campo en escenarios distintos con el mismo conjunto de lecturas.
- El JSON gana la clave `decisions`, que cubre todas las divergencias (las no
  agrupadas como `single`) y dice por qué se agrupó cada una. `divergences`,
  `counts` y el código de salida no cambian.
- El informe markdown gana la sección «Decisiones agrupadas» cuando hay
  alguna con más de un miembro.
- La skill plantea una decisión por llamada, explica la raíz una sola vez,
  lista los escenarios afectados y anota en `decisions.json` una entrada por
  divergencia miembro con el mismo `answer`, para no perder la trazabilidad
  individual.
- Con varios changes activos y sin id, la skill pregunta cuál en vez de
  elegir el `change.json` más reciente.

## Capabilities

### Modified Capabilities

- `divergence`: el motor agrupa por decisión raíz y la skill pregunta por
  decisión.

## Impact

- El esquema JSON versión 1 sólo crece (`R-TEC-006`): los graders de los evals
  existentes siguen leyendo lo mismo.
- Las cifras de `evals/README.md` no se mueven: `counts` y `exit_code` son
  los de siempre. `ambiguous-partial-effect` pasa a traer una sola decisión con
  dos miembros.
- `R-DIV-009` («una pregunta por llamada, en el orden del informe, con la
  pregunta y las opciones literales del script») se sigue cumpliendo
  literalmente: la agrupación la hace el script, no la skill; el informe es
  ahora el que trae la pregunta agrupada.
- Un eval nuevo, `diverge-root-decision`, con el mismo par de códigos en tres
  escenarios, puntúa la agrupación con regex sobre el JSON.

## Confidence

- **Que compartir un token distintivo en cada lector baste para reconocer la
  misma lectura en dos campos** · `medium` · es un criterio de conjuntos, no de
  significado · se revisa cuando la agrupación se use sobre tres deltas reales
  y se cuente cuántas decisiones agrupadas mezclaban lecturas distintas.
- **El resto de la propuesta** · `high` · igualdad de conjuntos y forma del
  JSON, comprobables sobre fixtures.
