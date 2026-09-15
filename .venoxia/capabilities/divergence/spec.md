# Capability: divergence

## Purpose

Coteja dos o más lecturas aisladas del mismo delta y convierte cada
desacuerdo detectable en una divergencia dura o blanda, sin que ningún
modelo participe en la aritmética de la comparación.

## Requirements

### R-DIV-001 · A different status code is a hard divergence

WHEN dos lecturas del mismo escenario declaran un `status_code` distinto,
el sistema DEBE marcar el campo `status_code` como divergencia dura y hacer
que la ejecución termine con código `1`.

#### Scenario: 409 against 422 on the same scenario
- **WHEN** una lectura dice `409` y la otra `422` para el mismo escenario
- **THEN** la divergencia queda marcada como dura sobre el campo `status_code` y el proceso sale con `1`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-002 · Fewer than two readers cannot claim convergence

WHEN se ejecuta `diff_readings.py` con menos de dos ficheros de lectura en
`readings/`, el sistema DEBE terminar con código `2` y responder con
`"converged": false` y `"verdict": "too_few_readers"`, sin afirmar ningún
acuerdo que no se pudo contrastar.

#### Scenario: A single reader
- **WHEN** `readings/` contiene un único fichero de lectura
- **THEN** el JSON dice `converged: false`, `verdict: too_few_readers` y el proceso sale con `2`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-003 · Only soft divergences pass unless strict

WHEN la única divergencia entre dos lecturas es blanda, el sistema DEBE
terminar con código `0` por omisión, y DEBE terminar con código `1` cuando
se pide `--strict`, dejando claro en el informe qué modo decidió el
resultado.

#### Scenario: Without strict, a soft divergence is a warning
- **WHEN** dos lecturas sólo divergen de forma blanda y no se pide `--strict`
- **THEN** el proceso sale con `0` y el resumen se marca con «⚠»

#### Scenario: With strict, the same pair fails
- **WHEN** el mismo par se compara con `--strict`
- **THEN** el proceso sale con `1` y el resumen se marca con «✗»

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-004 · A different number is never diluted

WHEN dos lecturas describen la misma acción con una cifra distinta, el
sistema DEBE devolver una similitud de `0.0` entre ellas, aunque compartan
casi todas las demás palabras del texto.

#### Scenario: Same words, different number
- **WHEN** una lectura dice «21 días» y la otra «14 días» sobre el mismo hecho
- **THEN** la similitud calculada es exactamente `0.0`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-013 · Two fields of one scenario that read the same way are one decision

WHEN `effect` y `side_effects` del mismo escenario divergen y, en cada lector,
los tokens distintivos de las dos lecturas —los tokens de contenido que sólo
tiene ese lector, contados como los compara `effect`: sin palabras vacías ni
conjugación— comparten al menos uno, el sistema DEBE agrupar las dos
divergencias en una sola decisión con razón `same-reading-two-fields`; sin
ese token compartido en alguno de los lectores DEBE mantenerlas como
decisiones separadas.

#### Scenario: The partial reservation fixture is one decision
- **WHEN** las lecturas del efecto y de los efectos colaterales de «One line
  short of stock» enfrentan «pedido completo» a «unidades con stock» en los
  dos campos
- **THEN** el JSON trae una sola decisión que agrupa las dos divergencias con
  razón `same-reading-two-fields`

#### Scenario: Disjoint distinguishing tokens stay apart
- **WHEN** el efecto y los efectos colaterales del mismo escenario divergen
  sin compartir ningún token distintivo en alguno de los lectores
- **THEN** cada divergencia es su propia decisión, con razón `single`

#### Scenario: A shared particle groups nothing
- **WHEN** las dos lecturas de un lector sólo comparten una palabra vacía, como
  una negación o un artículo
- **THEN** cada divergencia es su propia decisión, con razón `single`

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-DIV-014 · The same readings across scenarios are one decision

WHEN varias divergencias del mismo campo en escenarios distintos, que
R-DIV-013 no haya agrupado ya, enfrentan el mismo conjunto de lecturas
normalizadas, el sistema DEBE agruparlas en una sola decisión con razón
`same-readings-across-scenarios`; con conjuntos de lecturas distintos DEBE
mantenerlas separadas, y nunca DEBE fundir por transitividad dos grupos que no
comparten lecturas.

#### Scenario: The same two status codes in three scenarios
- **WHEN** tres escenarios enfrentan el mismo par de códigos de estado
- **THEN** el JSON trae una sola decisión con los tres escenarios y tres
  divergencias miembro, con razón `same-readings-across-scenarios`

#### Scenario: Different code pairs stay apart
- **WHEN** dos escenarios enfrentan pares de códigos de estado distintos
- **THEN** son dos decisiones, cada una con un solo miembro

#### Scenario: A missing scenario is never grouped
- **WHEN** un escenario sólo lo ve un lector
- **THEN** su divergencia es su propia decisión, con razón `single`

#### Scenario: A two-field decision is not chained across scenarios
- **WHEN** el efecto y los efectos colaterales de un escenario forman una
  decisión de dos campos y otro escenario enfrenta el mismo par de efectos
- **THEN** el segundo escenario es otra decisión: ninguna decisión mezcla
  miembros que no comparten lecturas

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-DIV-015 · The JSON lists every decision without moving the verdict

WHEN se pide `--json`, el sistema DEBE añadir la clave `decisions` con una
entrada por decisión que cubra todas las divergencias —las no agrupadas con
razón `single`—, cada una con `id`, `scenarios`, `fields`, `divergences`
(índices en la lista `divergences`), `hardness`, `reason`, `question` y
`options`, sin alterar `divergences`, `counts` ni `exit_code`; y el informe
markdown DEBE traer la sección «Decisiones agrupadas» cuando alguna decisión
tenga más de un miembro.

#### Scenario: Every divergence belongs to exactly one decision
- **WHEN** el análisis produce divergencias
- **THEN** cada índice de `divergences` aparece en exactamente una entrada de
  `decisions`

#### Scenario: The verdict does not move
- **WHEN** se analiza el fixture `ambiguous-partial-effect`
- **THEN** `counts` sigue diciendo una dura y una blanda, el veredicto sigue
  siendo `diverged` y `decisions` trae una sola entrada

#### Scenario: A grouped question names its scenarios and confronts the readings
- **WHEN** una decisión agrupa varias divergencias
- **THEN** su `question` nombra los escenarios afectados y sus `options` son
  las lecturas enfrentadas más la opción de que no hay divergencia real

#### Scenario: A two-field option carries both fields of its reader
- **WHEN** una decisión agrupa el efecto y los efectos colaterales del mismo
  escenario
- **THEN** la opción de cada lector enlaza su efecto y sus efectos colaterales,
  de modo que el texto elegido describe las dos cosas que se anotan

#### Scenario: The report lists grouped decisions
- **WHEN** alguna decisión tiene más de un miembro
- **THEN** el informe markdown trae la sección «Decisiones agrupadas» con esa
  decisión, su razón y sus escenarios

#### Scenario: No grouped decision, no section
- **WHEN** ninguna decisión tiene más de un miembro
- **THEN** el informe markdown no trae la sección «Decisiones agrupadas»

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-DIV-016 · The diverge skill asks one decision at a time and records every member

WHEN el informe trae decisiones, la skill `/venoxia:diverge` DEBE plantearlas
con `AskUserQuestion` una decisión por llamada, en el orden del informe, con
la pregunta y las opciones literales del script, explicando la decisión raíz
una sola vez y listando los escenarios afectados antes de la llamada, y DEBE
anotar en `decisions.json` una entrada por divergencia miembro con el mismo
`answer` y la clave `decision`; la skill nunca agrupa por su cuenta.

#### Scenario: One decision per call
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que las preguntas se plantean una decisión por llamada, en
  el orden del informe, con la pregunta y las opciones literales del script

#### Scenario: The root decision is explained once
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que antes de la llamada se explica la decisión raíz una sola
  vez y se listan los escenarios afectados

#### Scenario: Every member is recorded
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que en `decisions.json` se anota una entrada por divergencia
  miembro con el mismo `answer` y la clave `decision`

#### Scenario: The skill never groups on its own
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que la skill no agrupa preguntas por su cuenta y que la
  agrupación la hace el script

verifies:   tests/test_diverge_skill.py
confidence: medium
  why:      agrupar reduce llamadas, pero una decisión mal agrupada se contesta sin mirar los escenarios que arrastra
  revisit:  cuando la entrevista agrupada se use sobre un delta real con al menos una decisión de más de un miembro y se compruebe si la respuesta valía para todos
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-DIV-017 · Several active changes are a question, not a guess

WHEN `$ARGUMENTS` no trae ningún id y hay más de un change cuyo estado no es
`archived`, la skill `/venoxia:diverge` DEBE preguntar cuál examinar con los
ids como opciones, sin elegirlo por la fecha de sus ficheros; y un change en
`verified` no DEBE examinarse sin que su id venga en `$ARGUMENTS`, ni volver
nunca a `validated`.

#### Scenario: Several active changes are asked about
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que con más de un change no archivado y sin id en los
  argumentos se pregunta cuál, con los ids como opciones

#### Scenario: The date of the files decides nothing
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** no elige el change por el `change.json` más reciente

#### Scenario: A verified change is never taken by default
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que un change en `verified` no se examina sin su id y que
  nunca vuelve a `validated`

verifies:   tests/test_diverge_skill.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos
