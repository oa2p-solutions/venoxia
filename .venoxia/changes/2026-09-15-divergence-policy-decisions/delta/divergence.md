# divergence Delta

## ADDED Requirements

### R-DIV-018 · A reading may name its requirement and its input

WHEN una lectura trae los campos opcionales `requirement_id` —el `### R-XXX-NNN`
bajo el que está el escenario— e `input` —el valor literal que el `WHEN` pone a
prueba, o `null`—, el sistema DEBE conservarlos en los miembros de la decisión y
DEBE seguir aceptando las lecturas que no los traen; y el agente lector DEBE
pedir los dos campos en su contrato de salida.

#### Scenario: A reading without the new fields still parses
- **WHEN** las lecturas traen sólo los seis campos de siempre
- **THEN** el análisis termina igual que antes, con `requirement_id` e `input`
  a `null` en los miembros

#### Scenario: The new fields reach the members
- **WHEN** una lectura trae `requirement_id` e `input`
- **THEN** el miembro correspondiente de la decisión los lleva literales

#### Scenario: The reader agent asks for both fields
- **WHEN** se lee `agents/reader.md` y el contrato de salida de
  `skills/diverge/SKILL.md`
- **THEN** los dos nombran `requirement_id` e `input` como campos de cada lectura

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-1--la-agrupación-sigue-siendo-demasiado-literal

### R-DIV-019 · Scenarios that share a policy are one decision even when the figures differ

WHEN varias divergencias del mismo campo en escenarios distintos, que R-DIV-013
ni R-DIV-014 hayan agrupado, comparten `requirement_id` —o ninguna lo trae— y
en cada lector la lectura es la misma una vez normalizada y con cada cifra
sustituida por un marcador, el sistema DEBE agruparlas en una sola decisión con
razón `same-policy-across-scenarios`, conservando en cada miembro sus lecturas
literales y su entrada; cuando ninguna trae `requirement_id`, DEBE exigir además
que el `status_code` y los `side_effects` normalizados de cada lector coincidan
entre esos escenarios; con `requirement_id` distintos, con un lector cuya
lectura abstraída cambie de un escenario a otro, con el resto del escenario
distinto y sin `requirement_id`, o sobre un escenario que sólo ve un lector,
DEBE mantenerlas separadas.

#### Scenario: Three CLP notations are one decision
- **WHEN** «cola con coma», «cola con punto» y «guion de cierre» enfrentan en
  cada lector la misma lectura salvo la cifra (1468135, 1468135 y 1500000)
- **THEN** el JSON trae una sola decisión con los tres escenarios, tres
  divergencias miembro y razón `same-policy-across-scenarios`

#### Scenario: The figures are never diluted
- **WHEN** una decisión agrupa por política
- **THEN** cada miembro conserva las lecturas literales de cada lector con sus
  cifras, y la matriz del informe las enseña una por fila

#### Scenario: Different requirements stay apart
- **WHEN** dos escenarios con la misma lectura abstraída traen `requirement_id`
  distintos
- **THEN** son dos decisiones

#### Scenario: A reader who changes policy breaks the group
- **WHEN** en uno de los escenarios un lector describe otra conducta —no sólo
  otra cifra—
- **THEN** ese escenario es otra decisión

#### Scenario: Without a requirement the rest of the scenario must match
- **WHEN** dos escenarios sin `requirement_id` comparten la lectura abstraída
  del efecto pero un lector les da `side_effects` distintos
- **THEN** son dos decisiones; con el mismo `requirement_id` en los dos, siguen
  siendo una

#### Scenario: Identical readings keep their old reason
- **WHEN** las lecturas literales coinciden entre escenarios
- **THEN** la razón sigue siendo `same-readings-across-scenarios`

verifies:   tests/test_diff_readings.py
confidence: medium
  why:      abstraer las cifras es un criterio de forma; dos lecturas que sólo cambian de número pueden esconder dos políticas
  revisit:  cuando la agrupación por política se haya usado sobre tres deltas reales y se cuente cuántas decisiones agrupadas recibieron una respuesta que no valía para algún miembro
from:       2026-09-15-divergencia-caso-real.md#hallazgo-1--la-agrupación-sigue-siendo-demasiado-literal

### R-DIV-020 · Every option of a decision says what each member records

WHEN el JSON trae una decisión, el sistema DEBE añadirle `members` —una entrada
por divergencia miembro con `divergence`, `scenario`, `field`,
`requirement_id`, `input`, `hardness` y `readings`— y `resolutions`, una
entrada por opción con `option`, `reader` y `answers`, donde una opción que
recoge la lectura de un lector anota en cada miembro la lectura literal de ese
lector en ese escenario, y una opción que no recoge ninguna lectura —las
lecturas son equivalentes, o los efectos sobran— lleva `reader` a `null` y
`answers` vacío.

#### Scenario: A reader-backed option resolves every member literally
- **WHEN** una decisión agrupa tres escenarios y la opción viene del lector A
- **THEN** `answers` trae, por cada miembro, la lectura literal del lector A en
  ese escenario

#### Scenario: The equivalent option resolves nothing
- **WHEN** la opción es que las lecturas dicen lo mismo
- **THEN** su `reader` es `null` y sus `answers` están vacías

#### Scenario: Members carry their hardness
- **WHEN** una decisión agrupa una divergencia dura y una blanda
- **THEN** cada miembro dice su dureza y la decisión la dureza mayor

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-1--la-agrupación-sigue-siendo-demasiado-literal

### R-DIV-021 · The report has one actionable section

WHEN se genera el informe markdown, el sistema DEBE presentar cada decisión no
respondida una sola vez en la sección «Decisiones pendientes», con su pregunta,
sus opciones y, cuando tenga más de un miembro o alguna entrada, una matriz con
escenario, entrada, lectura de cada lector y dureza; DEBE relegar las
divergencias individuales a la sección «Evidencia por divergencia», con su
dureza, su señal y su detalle pero sin pregunta ni opciones; y no DEBE emitir
las secciones «Divergencias duras», «Divergencias blandas» ni «Decisiones
agrupadas».

#### Scenario: Each question appears once
- **WHEN** una decisión agrupa tres divergencias
- **THEN** su pregunta aparece una sola vez en el informe

#### Scenario: Members are evidence, not questions
- **WHEN** el informe lista la evidencia por divergencia
- **THEN** cada divergencia trae su dureza y su detalle, y ninguna trae opciones

#### Scenario: The old sections are gone
- **WHEN** hay divergencias duras y blandas
- **THEN** el informe no contiene «Divergencias duras», «Divergencias blandas»
  ni «Decisiones agrupadas», y sí «Decisiones pendientes» con su recuento

#### Scenario: The rest of the report does not move
- **WHEN** hay lagunas, ataques y escenarios que convergen
- **THEN** «Lagunas declaradas», «Abogado del diablo» y «Escenarios que
  convergen» siguen con sus recuentos, y el veredicto y el código de salida no
  cambian

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-2--el-informe-vuelve-a-mostrar-las-preguntas-agrupadas

### R-DIV-022 · Earlier decisions are reconciled before asking

WHEN existe un historial de decisiones —el fichero de `--decisions`, o
`decisions.json` junto al directorio de lecturas—, el sistema DEBE dar a cada
decisión una `fingerprint` estable calculada sobre el change, los requisitos,
los escenarios, los campos, la pregunta, las opciones y las lecturas literales
de sus miembros, y un `status` que deciden las entradas más recientes con esa
huella —la última de la lista para cada miembro, por escenario y campo—:
`answered` cuando la de cada miembro tiene `resolution` `selected`,
`equivalent` o `custom-resolved`; `pending` cuando no hay entrada aplicable o
la última de algún miembro tiene `resolution` `needs-clarification` o
`changes-contract`, aunque las de los demás cierren; `stale`, con `stale_reason`, cuando
hay una entrada sobre los mismos escenarios y campos pero la pregunta, las
opciones o las lecturas cambiaron, o cuando la entrada es `equivalent` y algún
miembro sigue siendo una divergencia dura; y `unclassified` cuando la única entrada
aplicable es antigua, sin `fingerprint`, y su respuesta fue escrita a mano. Una
entrada antigua con opción elegida DEBE contar como `answered` con
`previous.migrated` a `true`. El identificador `D-NNN` no DEBE formar parte de
la huella, y el veredicto y el código de salida no DEBEN depender del historial.

#### Scenario: Without a history every decision is pending
- **WHEN** no hay `decisions.json` ni `--decisions`
- **THEN** todas las decisiones salen `pending`, `decisions_source` es `null` y
  `decisions_pending` las cuenta

#### Scenario: A matching resolved answer is answered
- **WHEN** el historial trae una entrada con la misma `fingerprint` y
  `resolution` `selected`
- **THEN** la decisión sale `answered`, con `previous` (`at`, `answer`,
  `resolution`), y no cuenta en `decisions_pending`

#### Scenario: A clarification does not close
- **WHEN** la entrada con la misma huella tiene `resolution` `needs-clarification`
- **THEN** la decisión sigue `pending` y `previous` enseña lo que se contestó

#### Scenario: The latest entry with the fingerprint wins
- **WHEN** el historial trae para la misma huella una entrada `selected` y,
  después, otra `needs-clarification`
- **THEN** la decisión sale `pending` y `previous` es la entrada posterior

#### Scenario: A member left open keeps the decision pending
- **WHEN** la última entrada de un miembro es `changes-contract` y la última
  de otro miembro de la misma decisión, escrita después, es `custom-resolved`
- **THEN** la decisión sale `pending` y `previous` es la entrada
  `changes-contract`

#### Scenario: An equivalence that left the divergence hard is stale
- **WHEN** la entrada con la misma huella es `equivalent` y algún miembro de la
  decisión sigue siendo duro
- **THEN** la decisión sale `stale` y `stale_reason` dice que la equivalencia no
  cerró una divergencia dura

#### Scenario: A legacy chosen option is migrated
- **WHEN** la entrada antigua no trae `fingerprint`, casa por escenario, campo,
  pregunta y opciones, y su `chosen` es un índice
- **THEN** la decisión sale `answered` con `previous.migrated` a `true`

#### Scenario: A legacy hand-written answer is unclassified
- **WHEN** la entrada antigua casa igual pero su `chosen` es `null`
- **THEN** la decisión sale `unclassified` con `previous.answer` a la vista

#### Scenario: Changed options make the earlier answer stale
- **WHEN** hay una entrada sobre el mismo escenario y campo pero las opciones ya
  no son las mismas
- **THEN** la decisión sale `stale` y `stale_reason` dice qué cambió

#### Scenario: The verdict ignores the history
- **WHEN** todas las decisiones salen `answered`
- **THEN** `counts`, `verdict` y `exit_code` son los mismos que sin historial

verifies:   tests/test_diff_readings.py
confidence: medium
  why:      la huella se calcula sobre las lecturas y no sobre el delta, así que un cambio del delta que no mueva ninguna lectura conserva la respuesta anterior
  revisit:  cuando una respuesta reutilizada por la huella resulte no valer para el delta corregido
from:       2026-09-15-divergencia-caso-real.md#hallazgo-3--se-vuelven-a-preguntar-decisiones-anteriores

### R-DIV-023 · The skill records how each answer resolved the decision

WHEN la skill `/venoxia:diverge` anota una respuesta, DEBE escribir en cada
entrada de `decisions.json` las claves `decision`, `fingerprint`,
`plugin_version` y `resolution`, con `resolution` en `selected`, `equivalent`,
`custom-resolved`, `needs-clarification` o `changes-contract`; DEBE tratar como
cerrada sólo una decisión con `selected`, `equivalent` o `custom-resolved`;
ante `needs-clarification` DEBE hacer una llamada más con la misma pregunta y la
información aportada, y si la aclaración es que la respuesta no vale para todos
los miembros, esa llamada se hace por miembro y cada uno anota su propio
`answer`; ante `changes-contract` DEBE decir qué contradice y
remitir a `/venoxia:specify` o a `/venoxia:charter` sin cerrar la decisión;
DEBE pasar el historial al script y no preguntar las decisiones `answered`,
volver a preguntar las `stale` enseñando `previous` y pedir confirmar la
respuesta antigua en las `unclassified`; y DEBE anunciar al empezar la versión del plugin leída
de su manifiesto.

#### Scenario: The five resolutions are named
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** nombra las cinco resoluciones y las claves `decision`,
  `fingerprint`, `plugin_version` y `resolution`

#### Scenario: Only three resolutions close
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que sólo `selected`, `equivalent` y `custom-resolved`
  cierran una decisión

#### Scenario: A clarification gets one more call
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que ante `needs-clarification` se hace una llamada más con
  la misma pregunta y la información aportada

#### Scenario: An answer that does not fit every member is asked per member
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que si la aclaración es que la respuesta no vale para todos
  los miembros, la llamada siguiente se hace por miembro y cada uno anota su
  propio `answer`

#### Scenario: A contract change is routed, not closed
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que ante `changes-contract` se dice qué contradice y se
  remite a `/venoxia:specify` o a `/venoxia:charter` sin cerrar la decisión

#### Scenario: Answered decisions are not asked again
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que el historial se pasa al script con `--decisions`, que
  las decisiones `answered` no se preguntan, que las `stale` se vuelven a
  preguntar enseñando `previous` y que en las `unclassified` se pide confirmar
  la respuesta antigua

#### Scenario: The skill announces the running version
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que al empezar se anuncia la versión del plugin leída de
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`

verifies:   tests/test_diverge_skill.py
confidence: medium
  why:      clasificar una respuesta escrita a mano es juicio de la skill, y la skill puede llamar custom-resolved a lo que sólo aporta contexto
  revisit:  cuando tres decisiones reales cerradas como custom-resolved se comprueben contra el delta corregido y se cuente cuántas resolvían de verdad todos los miembros
from:       2026-09-15-divergencia-caso-real.md#hallazgo-4--se-aceptan-respuestas-que-no-resuelven-la-pregunta

## MODIFIED Requirements

### R-DIV-015 · The JSON lists every decision without moving the verdict

WHEN se pide `--json`, el sistema DEBE añadir la clave `decisions` con una
entrada por decisión que cubra todas las divergencias —las no agrupadas con
razón `single`—, cada una con `id`, `scenarios`, `fields`, `divergences`
(índices en la lista `divergences`), `hardness`, `reason`, `question` y
`options`, sin alterar `divergences`, `counts` ni `exit_code`; y el informe
markdown DEBE traer cada decisión una sola vez en la sección «Decisiones
pendientes».

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

#### Scenario: The report lists every decision once
- **WHEN** alguna decisión tiene más de un miembro
- **THEN** el informe markdown la trae una sola vez en «Decisiones pendientes»,
  con su razón y sus escenarios

verifies:   tests/test_diff_readings.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-2--el-informe-vuelve-a-mostrar-las-preguntas-agrupadas

### R-DIV-016 · The diverge skill asks one decision at a time and records every member

WHEN el informe trae decisiones, la skill `/venoxia:diverge` DEBE plantearlas
con `AskUserQuestion` una decisión por llamada, en el orden del informe, con
la pregunta y las opciones literales del script, explicando la decisión raíz
una sola vez y listando los escenarios afectados antes de la llamada, y DEBE
anotar en `decisions.json` una entrada por divergencia miembro con la clave
`decision` y el `answer` que la opción elegida le asigna en `resolutions`; la
skill nunca agrupa por su cuenta.

#### Scenario: One decision per call
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que las preguntas se plantean una decisión por llamada, en
  el orden del informe, con la pregunta y las opciones literales del script

#### Scenario: The root decision is explained once
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que antes de la llamada se explica la decisión raíz una sola
  vez y se listan los escenarios afectados

#### Scenario: Every member is recorded with its own answer
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que en `decisions.json` se anota una entrada por divergencia
  miembro con la clave `decision` y el `answer` que `resolutions` asigna a ese
  miembro

#### Scenario: The skill never groups on its own
- **WHEN** se lee el cuerpo de `skills/diverge/SKILL.md`
- **THEN** declara que la skill no agrupa preguntas por su cuenta y que la
  agrupación la hace el script

verifies:   tests/test_diverge_skill.py
confidence: medium
  why:      agrupar reduce llamadas, pero una decisión mal agrupada se contesta sin mirar los escenarios que arrastra
  revisit:  cuando la entrevista agrupada se use sobre un delta real con al menos una decisión de más de un miembro y se compruebe si la respuesta valía para todos
from:       2026-09-15-divergencia-caso-real.md#hallazgo-1--la-agrupación-sigue-siendo-demasiado-literal
