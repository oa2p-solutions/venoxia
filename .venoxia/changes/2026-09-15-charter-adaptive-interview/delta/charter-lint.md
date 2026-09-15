# charter-lint Delta

## ADDED Requirements

### R-CHL-009 · The charter skill asks only for a missing or conflicting slot

WHEN `/venoxia:charter` va a plantear una pregunta, la skill DEBE nombrar antes
la casilla del mapa de cobertura que esa pregunta escribe y su estado, DEBE
plantearla sólo cuando el estado de esa casilla sea `missing` o `conflicting`,
DEBE re-evaluar el mapa entero tras cada respuesta, ante una corrección DEBE
invalidar sólo las casillas que dependen de la corregida, y una casilla
`inferred` sólo DEBE pasar a `known` cuando el usuario la confirme, en la
confirmación general del borrador, que se hace siempre.

#### Scenario: The nine slots are named
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** nombra las nueve casillas `purpose`, `primary_user`,
  `current_workaround`, `first_capability`, `done_when`, `out_of_scope`,
  `evidence`, `bets` y `domain_decisions`

#### Scenario: The five states are named
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** nombra los cinco estados `known`, `inferred`, `missing`, `optional`
  y `conflicting`

#### Scenario: Only a missing or conflicting slot is asked
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una pregunta sólo se hace cuando su casilla está en
  `missing` o en `conflicting`

#### Scenario: The slot is named before the question
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que antes de cada pregunta se nombra la casilla que va a
  escribir

#### Scenario: One answer refreshes the whole map
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que tras cada respuesta se re-evalúa el mapa entero

#### Scenario: A correction invalidates only its dependants
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una corrección invalida sólo las casillas que dependen
  de la corregida

#### Scenario: An inferred slot needs the user's confirmation
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una casilla `inferred` sólo pasa a `known` cuando el
  usuario la confirma, y que la confirmación general del borrador se hace
  siempre

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-010 · The charter skill classifies the entry mode and drafts before it asks

WHEN empieza la entrevista, la skill DEBE clasificar la conversación en uno de
tres modos de entrada —producto ya explicado, proyecto existente, idea difusa—
o en retomar un acta —y con `.venoxia/charter.md` en el disco el modo DEBE
ser retomar un acta aunque haya código—; con el producto ya explicado o con un
proyecto existente DEBE redactar el acta completa, con las inferencias
marcadas con `<!-- inferred -->`, antes de la primera pregunta, enseñándola en
la conversación y sin escribirla en `.venoxia/charter.md` hasta la aprobación;
el modo producto ya explicado DEBE exigir `purpose`, `primary_user` y
`first_capability` dichos por el usuario, y un `Done when` nunca DEBE
inferirse; y con una idea difusa DEBE abrir con la pregunta por la última vez
que ocurrió el problema y seguir con la de qué parte del proceso eliminaría
primero y qué tendría que ver esa persona.

#### Scenario: The modes are named
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** nombra los tres modos de entrada y el de retomar un acta

#### Scenario: An explained product is drafted first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que con el producto ya explicado el acta se redacta antes de
  la primera pregunta

#### Scenario: Inferences are marked in the draft
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que las inferencias van marcadas en el borrador

#### Scenario: The inference mark is the literal comment
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la marca de inferencia es `<!-- inferred -->`

#### Scenario: Resuming wins over an existing project
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que con `.venoxia/charter.md` en el disco el modo es retomar
  un acta aunque haya código

#### Scenario: The draft lives in the conversation until it is approved
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que el borrador se enseña en la conversación y no se escribe
  en `.venoxia/charter.md` hasta la aprobación

#### Scenario: The explained mode needs three slots said by the user
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que el modo producto ya explicado exige `purpose`,
  `primary_user` y `first_capability` dichos por el usuario, y que un
  `Done when` nunca se infiere

#### Scenario: The vague mode opens with the last real case
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** contiene literalmente la pregunta «Cuéntame la última vez que ocurrió
  el problema: quién estaba intentando hacer qué, qué pasos siguió y dónde
  perdió más tiempo o cometió errores.»

#### Scenario: The vague mode continues with what to remove first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** contiene literalmente la pregunta «¿Qué parte de ese proceso
  eliminarías primero y qué tendría que ver esa persona para considerar que ya
  funciona?»

#### Scenario: The fixed rounds are gone
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** no contiene ningún encabezado que empiece por «### Tanda»

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-011 · The charter skill never asks a project for what its disk already says

WHEN el proyecto ya tiene código o documentación, la skill DEBE reconstruir el
propósito, los usuarios, las capabilities y las restricciones desde el
repositorio y presentar esa lectura para corregirla, DEBE preguntar qué cambio
quiere hacer ahora el usuario, no DEBE preguntar por el stack, el comando de
pruebas ni un comportamiento que el disco ya demuestra, y DEBE explicar una
sola vez que la prioridad de la tabla es el orden de adopción de Venoxia.

#### Scenario: The reading is reconstructed from disk
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que con código o documentación delante el propósito, los
  usuarios, las capabilities y las restricciones se reconstruyen desde el
  repositorio y se presentan para corregirlos

#### Scenario: The next change is asked
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que se pregunta qué cambio quiere hacer ahora

#### Scenario: Disk facts are not asked
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que no se pregunta por el stack, el comando de pruebas ni un
  comportamiento que el disco ya demuestra

#### Scenario: Priority is adoption order, said once
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la prioridad es el orden de adopción de Venoxia y que se
  explica una sola vez

verifies:   tests/test_charter_skill.py
confidence: medium
  why:      que la reconstrucción desde el disco baste para no preguntar nada que el disco ya diga depende de cuánto documente cada repositorio
  revisit:  cuando tres entrevistas reales hayan pasado por el modo de proyecto existente y se cuente cuántas preguntas sobraron o faltaron
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-012 · Facts and bets are separated by one synthesis, and no bet is fabricated

WHEN el mapa de cobertura tiene el propósito y la primera capability, la skill
DEBE presentar en una sola síntesis lo que entendió como observado, lo que
entendió como supuesto y la razón de cada clasificación, DEBE pedir una sola
corrección general, DEBE preguntar `revisit` y `fatal` únicamente por las
apuestas que sigan abiertas tras la corrección, y cuando el usuario afirme que
todo está observado DEBE dejar `## Bets` sin apuestas, conservar el aviso `C20`
y dejar registrada la afirmación como comentario bajo `## Bets` del propio
acta, con la fecha.

#### Scenario: One synthesis and one correction
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que hechos y apuestas se presentan en una síntesis con la
  razón de cada clasificación y se pide una sola corrección general

#### Scenario: The per-section question is gone
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que no se vuelve a preguntar «¿lo has visto o lo supones?»
  por cada sección

#### Scenario: Revisit and fatal only for open bets
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que `revisit` y `fatal` se preguntan sólo por las apuestas
  que sigan abiertas

#### Scenario: No bet is fabricated
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que cuando el usuario afirma que todo está observado no se
  escribe ninguna apuesta, el aviso `C20` se conserva y la afirmación queda
  registrada

#### Scenario: The claim is recorded inside the charter
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la afirmación se registra como comentario bajo `## Bets`
  del propio acta, con la fecha

verifies:   tests/test_charter_skill.py
confidence: medium
  why:      que una síntesis con una corrección general separe hechos y apuestas tan bien como la pregunta por sección es la apuesta central del rediseño
  revisit:  cuando tres actas reales hayan salido de la síntesis y alguien compare sus apuestas con lo que después resultó supuesto
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-013 · Reaching the minimum offers to close

WHEN el mapa de cobertura reúne el propósito, un usuario principal con su hoy y
su con esto, la capability prioritaria, un `Done when` observable, un no-alcance
razonado, la clasificación de hechos y apuestas confirmada y —sólo si la fila
de prioridad 1 arbitra entre alternativas— una decisión de dominio, la skill
DEBE presentar el borrador completo y preguntar si aprobarlo o profundizar en
una sección concreta, y no DEBE seguir entrevistando por iniciativa propia.

#### Scenario: The minimum is listed
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** enumera como mínimo el propósito, un usuario con su hoy y su con
  esto, la capability prioritaria, un `Done when` observable, un no-alcance
  razonado, la clasificación confirmada y la decisión de dominio sólo si la
  fila 1 arbitra

#### Scenario: The draft is offered for approval
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que al alcanzar el mínimo se presenta el borrador completo y
  se pregunta si aprobarlo o profundizar en una sección concreta

#### Scenario: No interview on its own initiative
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que no se sigue entrevistando por iniciativa propia

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-014 · Technical preparation happens after the charter and only when relevant

WHEN el acta está aprobada y el linter en verde, la skill DEBE tratar el
comando de pruebas, las convenciones técnicas, la configuración del oráculo, el
guardián y el esqueleto del proyecto en una fase de preparación posterior,
DEBE detectar primero en el repositorio lo que pueda detectarse, DEBE preguntar
sólo ante una ambigüedad que impida ejecutar el paso siguiente, DEBE proponer
una convención técnica sólo cuando la fila de prioridad 1 o el repositorio la
hagan relevante, nunca como lista genérica, DEBE decir que la preparación no
ejecuta el comando detectado —el rojo del primer `/venoxia:verify` es quien
comprueba que prueba algo—, y no DEBE contar como candidato el marcador de
`npm init` («no test specified»).

#### Scenario: Preparation comes after writing the charter
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** la sección de preparación aparece después de la sección que escribe
  el acta y pasa el linter

#### Scenario: The test command is detected before it is asked
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que el comando de pruebas se detecta en el repositorio antes
  de preguntarlo

#### Scenario: Ambiguity is the only reason to ask
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que en la preparación sólo se pregunta ante una ambigüedad
  que impida ejecutar el paso siguiente

#### Scenario: No generic list of conventions
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una convención sólo se propone cuando es relevante para
  el proyecto o para el cambio inmediato y que no se presenta una lista genérica
  de convenciones

#### Scenario: The generic table is gone
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** no contiene la fila «Errores de una API»

#### Scenario: The detected command is not trusted blindly
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la preparación no ejecuta el comando detectado y que el
  rojo del primer `/venoxia:verify` es quien comprueba que prueba algo

#### Scenario: The npm placeholder is not a candidate
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que el marcador de `npm init` («no test specified») no
  cuenta como candidato

verifies:   tests/test_charter_skill.py
confidence: medium
  why:      que la preparación detecte el comando de pruebas sin preguntar depende de que el manifiesto del proyecto declare uno
  revisit:  cuando tres proyectos reales hayan pasado por la preparación y se cuente en cuántos hubo que preguntar
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-015 · Resuming a charter starts from its state, not from its bets

WHEN existe `.venoxia/charter.md`, la skill DEBE resumir el propósito, la
primera capability, el estado y los bloqueos, DEBE agrupar las apuestas
abiertas en una sola vista, DEBE preguntar si el usuario quiere continuar con
la siguiente capability, revisar una sección o resolver una apuesta cuyo hecho
de revisión ya ocurrió, no DEBE preguntar apuesta por apuesta antes de saber
qué quiere hacer, no DEBE usar `mtime` para inferir el objetivo de la sesión,
DEBE enseñar con sus bloqueos un acta que no pasa el linter antes de la
pregunta, DEBE mantener empezar de cero como respuesta escrita, y antes de
pisar el acta anterior DEBE avisar de que no guarda copias y esperar la
confirmación explícita del usuario.

#### Scenario: The state is summarised first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que al retomar se resume el propósito, la primera
  capability, el estado y los bloqueos

#### Scenario: Bets are grouped in one view
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que las apuestas abiertas se agrupan en una sola vista

#### Scenario: One question with three intentions
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que se pregunta si continuar con la siguiente capability,
  revisar una sección o resolver una apuesta cuyo hecho ya ocurrió

#### Scenario: Never bet by bet first
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que no se pregunta apuesta por apuesta antes de saber qué
  quiere hacer el usuario

#### Scenario: No mtime
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** no contiene la palabra `mtime`

#### Scenario: A charter that fails the linter is shown with its blockers
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que un acta que no pasa el linter se enseña con sus bloqueos
  antes de la pregunta y que empezar de cero sigue disponible como respuesta
  escrita

#### Scenario: Starting over never overwrites without a warning
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que antes de pisar el acta anterior se avisa de que la skill
  no guarda copias y se espera la confirmación explícita del usuario

verifies:   tests/test_charter_skill.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos

### R-CHL-016 · C21 rejects an unconfirmed inference left in the charter

WHEN una línea del acta conserva la marca de inferencia sin confirmar
`<!-- inferred -->`, el sistema DEBE marcar el hallazgo `C21` como error sobre
esa línea, con un mensaje que diga que una inferencia sin confirmar no es un
acuerdo.

#### Scenario: A marked line is an error
- **WHEN** una línea del acta contiene `<!-- inferred -->`
- **THEN** salta `C21` como error sobre esa línea

#### Scenario: Each marked line has its own finding
- **WHEN** varias líneas distintas del acta contienen la marca
- **THEN** salta un `C21` por cada una de esas líneas

#### Scenario: A charter without marks is untouched
- **WHEN** ninguna línea del acta contiene la marca
- **THEN** no salta `C21`

verifies:   tests/test_charter_lint.py
confidence: high
from:       2026-09-15-charter-rediseno.md#6-requisitos-propuestos
