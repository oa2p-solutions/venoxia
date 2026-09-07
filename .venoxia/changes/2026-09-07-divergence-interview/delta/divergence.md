# divergence Delta

## ADDED Requirements

### R-DIV-008 · A hard side-effect divergence names the signal that made it hard

WHEN `diff_readings.py` marca como dura una divergencia de `side_effects`, el
sistema DEBE nombrar en el informe la señal que la hizo dura y emitir esa misma
señal en la clave `signal` del elemento de `divergences` del JSON, con uno de
los valores `polarity`, `scope`, `numeric` o `empty-repertoire`.

#### Scenario: A negation makes it hard
- **WHEN** un lector registra «no se crea el presupuesto» y el otro «se crea
  el presupuesto» sobre el mismo escenario
- **THEN** el elemento de `divergences` lleva la clave `signal` con el valor
  `polarity`

#### Scenario: The report names the negation
- **WHEN** un lector registra «no se crea el presupuesto» y el otro «se crea
  el presupuesto» sobre el mismo escenario
- **THEN** el informe nombra la marca «no» como lo que hizo dura la divergencia

#### Scenario: A different number makes it hard
- **WHEN** un lector registra «la reserva dura 15 minutos» y el otro «la
  reserva dura 30 minutos» sobre el mismo escenario
- **THEN** el elemento de `divergences` lleva la clave `signal` con el valor
  `numeric` y el informe nombra los dos números

#### Scenario: A soft divergence carries no signal
- **WHEN** una divergencia de `side_effects` es blanda
- **THEN** el elemento de `divergences` lleva la clave `signal` con el valor
  `null`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#cómo-se-usa

### R-DIV-009 · The diverge skill asks the script's questions one at a time

WHEN el informe de `diff_readings.py` trae preguntas cerradas, la skill
`/venoxia:diverge` DEBE plantearlas al usuario con `AskUserQuestion`, una
pregunta por llamada, en el orden del informe, con el texto de la pregunta y
las opciones literales del script.

#### Scenario: The tool is declared
- **WHEN** se lee el frontmatter de `skills/diverge/SKILL.md`
- **THEN** `allowed-tools` incluye `AskUserQuestion`

#### Scenario: The body forbids grouping and rewording
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que las preguntas van una por llamada, en el orden del
  informe, con la pregunta y las opciones literales del script

#### Scenario: The body still refuses to edit deltas
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que la skill no edita deltas

verifies:   tests/test_diverge_skill.py
confidence: medium
  why:      una pregunta por llamada es más lento que agrupar cuatro; se elige porque agrupar es el «contestar en bloque» que motiva el cambio
from:       README.md#cómo-se-usa

### R-DIV-010 · The chosen reading is recorded literally for the delta

WHEN el usuario contesta una pregunta de la entrevista, la skill
`/venoxia:diverge` DEBE añadir la respuesta tal cual a
`.venoxia/changes/<id>/decisions.json` —con el escenario, la pregunta, las
opciones y el texto elegido o escrito a mano— sin borrar las respuestas ya
anotadas, para que el siguiente paso copie ese texto al escenario del delta sin
reformularlo.

#### Scenario: The body names the decisions file and its shape
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** nombra `decisions.json` y las claves `scenario`, `question`,
  `options`, `chosen` y `answer`

#### Scenario: A hand-written answer is kept verbatim
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que una respuesta escrita a mano se anota con las palabras
  del usuario

#### Scenario: Earlier decisions are kept
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que cada respuesta se añade sin borrar las anteriores

verifies:   tests/test_diverge_skill.py
confidence: high
from:       README.md#cómo-se-usa
