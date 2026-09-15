# charter-lint Delta

## ADDED Requirements

### R-CHL-017 · Every confirmed inference leaves evidence

WHEN la skill `/venoxia:charter` rellena una casilla por inferencia, la
confirma, corrige o descarta, hace una pregunta o toma una decisión que la
entrevista no cubría, DEBE añadir una entrada a `.venoxia/charter-log.json`
—fichero de versión `1` con la lista `entries`, que se conserva entre
sesiones— con `at`, `plugin_version`, `kind` (`inference`, `question` u
`own-decision`), `slot`, el texto propuesto o preguntado, el desenlace
(`pending` mientras la inferencia no se ha presentado, y `confirmed`,
`corrected` o `dropped` cuando se resuelve) y las palabras literales del
usuario cuando las hubo; la entrada `inference` se escribe al rellenar la
casilla, no al confirmarla; confirmarla, corregirla o descartarla cambia el
desenlace de esa misma entrada y le añade `resolved_at` —«sin borrar las
anteriores» habla de entradas, no de desenlaces—, y descartarla quita además
del acta la línea inferida; una casilla cuya entrada sigue `pending` conserva
la marca `<!-- inferred -->` en el acta, de modo que C21 la rechaza hasta que
se resuelva, y al retomar un acta las inferencias `pending` del registro y las
filas `dropped` por «sin respuesta» se presentan antes de cualquier pregunta
nueva; un registro existente ilegible o de otra versión DEBE
renombrarse a `charter-log.json.corrupt-<marca>` —con `<marca>` la fecha y
hora UTC hasta el segundo, y un sufijo numérico si ese nombre ya existe— antes
de crear uno nuevo y nunca sobrescribirse, y la entrega nombra la copia
apartada; y la entrega DEBE nombrar el fichero, decir cuántas entradas de cada
clase escribió, cuántas inferencias quedan `pending` y nombrar cada fila
`dropped` con su motivo.

#### Scenario: The evidence file and its shape are named
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** nombra `.venoxia/charter-log.json`, la lista `entries` y las claves
  `at`, `plugin_version`, `kind`, `slot`

#### Scenario: The three kinds and the three outcomes are named
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** nombra `inference`, `question` y `own-decision`, y `confirmed`,
  `corrected` y `dropped`

#### Scenario: Own decisions go to the log, not only to the delivery
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que toda decisión que la skill toma sola se anota en el
  registro como `own-decision`, además de decirse en la entrega

#### Scenario: The log survives the session
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que el registro se conserva entre sesiones y que las entradas
  nuevas se añaden sin borrar las anteriores

#### Scenario: An inference is logged when it is written, not when it is confirmed
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la entrada `inference` se escribe al rellenar la casilla,
  con desenlace `pending` hasta que se confirme, corrija o descarte

#### Scenario: An unreadable log is kept, not overwritten
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que un registro ilegible o de otra versión se renombra a
  `charter-log.json.corrupt-<marca>` antes de crear uno nuevo y nunca se
  sobrescribe, y que la entrega nombra la copia apartada

#### Scenario: Pending inferences are counted and keep the mark
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una casilla cuya entrada sigue `pending` conserva la
  marca `<!-- inferred -->` y que la entrega dice cuántas inferencias quedan
  `pending`

#### Scenario: The corrupt copy never replaces an earlier one
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que `<marca>` es la fecha y hora UTC hasta el segundo, con un
  sufijo numérico si ese nombre ya existe

#### Scenario: Resolving an inference updates its own entry
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que confirmar, corregir o descartar una inferencia cambia el
  desenlace de esa misma entrada y le añade `resolved_at`, sin añadir otra

#### Scenario: A dropped inference leaves the charter
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que descartar una inferencia quita además del acta la línea
  inferida

#### Scenario: Pending inferences are resumed first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que al retomar un acta las inferencias `pending` del registro
  se presentan antes de cualquier pregunta nueva

#### Scenario: An unanswered row is offered again when resuming
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que al retomar un acta las filas `dropped` por «sin
  respuesta» se presentan de nuevo, junto a las inferencias `pending`

#### Scenario: Dropped rows are named in the delivery
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la entrega nombra cada fila `dropped` con su motivo

verifies:   tests/test_charter_skill.py
confidence: medium
  why:      el registro lo escribe el mismo modelo que hizo la inferencia
  revisit:  cuando tres actas reales tengan su charter-log.json y se coteje con la transcripción de cada sesión
from:       2026-09-15-divergencia-caso-real.md#hallazgo-5--las-inferencias-confirmadas-no-dejan-rastro

### R-CHL-018 · A row the skill drafts is confirmed before it is written

WHEN la skill `/venoxia:charter` redacta por su cuenta una fila de la tabla de
capabilities —incluida `technical-contract` al repartir convenciones—, DEBE
presentar su «Qué podrá hacer», su `Done when`, su `Risk` y su prioridad
marcados como inferidos y confirmarlos en una sola llamada antes de escribir
la fila; DEBE escribir la fila sólo con el sí del usuario, volver a
confirmarla si la corrige y no escribirla —anotando `dropped` con las palabras
literales del usuario, o «sin respuesta» si no contestó— si la rechaza o no la
contesta;
no DEBE escribir una fila que el usuario no haya visto; y no DEBE juntar en
una llamada dos preguntas cuando la segunda depende de la respuesta de la
primera.

#### Scenario: The drafted row is confirmed in one call
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una fila redactada por la skill se confirma con su
  contenido y su prioridad en una sola llamada antes de escribirse

#### Scenario: No row the user has not seen
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que no se escribe ninguna fila que el usuario no haya visto

#### Scenario: A rejected row is never written
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la fila se escribe sólo con el sí del usuario, que una
  corrección se vuelve a confirmar y que una fila rechazada no se escribe y se
  anota como `dropped`

#### Scenario: An unanswered row leaves a trace
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una fila presentada y no contestada tampoco se escribe y
  se anota como `dropped` con «sin respuesta»

#### Scenario: Dependent questions never share a call
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que dos preguntas donde la segunda depende de la primera no
  van en la misma llamada, y pone el reparto de convenciones y la prioridad de
  la fila como ejemplo

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-5--las-inferencias-confirmadas-no-dejan-rastro

### R-CHL-019 · The charter skill announces the running version

WHEN arranca la skill `/venoxia:charter`, DEBE anunciar en su primera línea la
versión del plugin leída de `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`
—o `unknown`, dicho igual de claro, si la variable no está definida o el
manifiesto no se puede leer— y DEBE escribir esa misma versión en cada entrada
de `.venoxia/charter-log.json`.

#### Scenario: The version is announced first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que al empezar se anuncia la versión del plugin leída de
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`

#### Scenario: The version travels with the evidence
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que cada entrada del registro lleva `plugin_version`

#### Scenario: A missing manifest is announced as unknown
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que sin `CLAUDE_PLUGIN_ROOT` o sin manifiesto legible la
  versión anunciada y anotada es `unknown`

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-6--no-hay-forma-de-demostrar-qué-versión-corre
