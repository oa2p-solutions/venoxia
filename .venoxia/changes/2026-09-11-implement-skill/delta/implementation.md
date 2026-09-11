# implementation Delta

## ADDED Requirements

### R-IMP-001 · The implement skill starts only from a validated change with a recorded red

WHEN se invoca `/venoxia:implement <change-id>`, la skill DEBE comprobar,
antes de editar nada, que el `change.json` está en `validated` y que el
último run de `oracle.json` no tiene ningún requisito del change en
`missing` y tiene al menos uno en `red`, y con cualquier otra situación DEBE
detenerse sin editar nada, remitiendo a `/venoxia:diverge` o a
`/venoxia:verify`.

#### Scenario: The skill is named implement and takes a change id
- **WHEN** se lee el frontmatter de `skills/implement/SKILL.md`
- **THEN** `name` es `implement` y `argument-hint` nombra el id del change

#### Scenario: The body requires the validated state
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que sólo trabaja sobre un change en `validated`

#### Scenario: The body requires a recorded red run
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que exige un run de `oracle.json` con algún requisito en
  `red` antes de escribir código

#### Scenario: The body refuses a missing test
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que se detiene si el último run trae algún requisito del
  change en `missing`

#### Scenario: The inventory precedes any edit
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que lee el delta, `decisions.json`, `principles.md`, las
  capabilities tocadas y los ficheros de `verifies:` antes de editar nada

verifies:   tests/test_implement_skill.py
confidence: high
from:       README.md#las-seis-skills

### R-IMP-002 · The implement skill never edits the specification or its oracles

La skill `/venoxia:implement` NO DEBE editar ningún fichero bajo `.venoxia/`
—salvo el `decisions.json` del propio change, donde añade las respuestas del
usuario sin borrar las que ya hay—, ni ningún fichero que un `verifies:` del
delta nombre, ni ningún otro fichero del directorio que contiene a cada uno
de ellos, subdirectorios incluidos, y DEBE decirlo con todas las letras en su
cuerpo.

#### Scenario: The body forbids editing .venoxia
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que nunca edita `.venoxia/`

#### Scenario: The body forbids editing the oracle files
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que nunca edita ningún fichero que un `verifies:` nombre

#### Scenario: The body forbids editing the test directories
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que nunca edita ningún otro fichero del directorio que
  contiene a un fichero de `verifies:`, subdirectorios incluidos

#### Scenario: decisions.json is the one exception
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que el `decisions.json` del change es el único fichero de
  `.venoxia/` que escribe

#### Scenario: decisions.json only grows
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que en `decisions.json` añade sin borrar lo que ya hay

#### Scenario: The body says the guardian keeps watching
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que el guardián intercepta también las ediciones hechas
  desde la skill

verifies:   tests/test_implement_skill.py
confidence: high
from:       README.md#las-seis-skills

### R-IMP-003 · The implement skill runs the oracle without recording and stops on green

WHEN la skill `/venoxia:implement` comprueba su avance, DEBE ejecutar
`oracle.py` sobre el change sin `--record` y DEBE terminar cuando el oráculo
sale con código `0`, o cuando un intento no cambia el estado de ningún
requisito, o cuando la respuesta a una decisión no escrita cambia el
comportamiento observable —entonces remite a `/venoxia:specify`, porque el
delta va antes que el código—; la grabación queda para `/venoxia:verify`.

#### Scenario: The tools are exactly the seven declared
- **WHEN** se lee el frontmatter de `skills/implement/SKILL.md`
- **THEN** `allowed-tools` es exactamente `Read`, `Glob`, `Grep`, `Edit`,
  `Write`, `AskUserQuestion` y el `Bash` acotado a `oracle.py`

#### Scenario: No generic Bash
- **WHEN** se lee el frontmatter de `skills/implement/SKILL.md`
- **THEN** ninguna entrada de `allowed-tools` es un `Bash` sin acotar

#### Scenario: The body forbids recording
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que nunca pasa `--record` a `oracle.py`

#### Scenario: The body stops on a green oracle
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que termina en cuanto el oráculo queda todo en verde

#### Scenario: An unwritten decision is asked, not chosen
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que una decisión no escrita que deja un requisito en rojo
  se pregunta con `AskUserQuestion` y se anota en `decisions.json`

#### Scenario: An answer that changes behaviour goes back to specify
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que si la respuesta cambia el comportamiento observable la
  skill se detiene y remite a `/venoxia:specify`

#### Scenario: No progress stops the loop
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que se detiene cuando un intento no cambia el estado de
  ningún requisito

verifies:   tests/test_implement_skill.py
confidence: medium
  why:      sin Bash genérico la skill no puede lanzar la suite entera ni un linter; se elige porque un comando a ojo es justo lo que el oráculo sustituye (B-005)
from:       README.md#las-seis-skills

### R-IMP-004 · The delivery names each requirement with its state and hands over to verify

WHEN la skill `/venoxia:implement` termina, su entrega DEBE listar cada
requisito del change con su estado en la última ejecución del oráculo, los
ficheros que tocó y `/venoxia:verify` como siguiente paso.

#### Scenario: The delivery lists every requirement with its state
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que la entrega nombra cada requisito con su estado

#### Scenario: The delivery lists the files touched
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que la entrega nombra los ficheros tocados

#### Scenario: The next step is verify
- **WHEN** se lee el cuerpo de `skills/implement/SKILL.md`
- **THEN** declara que el siguiente paso es `/venoxia:verify`

verifies:   tests/test_implement_skill.py
confidence: high
from:       README.md#las-seis-skills
