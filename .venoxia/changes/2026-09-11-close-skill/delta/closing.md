# closing Delta

## ADDED Requirements

### R-CLS-001 · The close skill starts only from a verified change and runs the gate first

WHEN se invoca `/venoxia:close <change-id>`, la skill DEBE comprobar que el
`change.json` está en `verified` y, sólo entonces, ejecutar `gate.py` sobre
la raíz del proyecto antes de proponer ningún commit, y con cualquier otro
estado o con la puerta en un código distinto de `0` DEBE detenerse sin
ejecutar ningún comando de git que escriba.

#### Scenario: The skill is named close and takes a change id
- **WHEN** se lee el frontmatter de `skills/close/SKILL.md`
- **THEN** `name` es `close` y `argument-hint` nombra el id del change

#### Scenario: The body requires the verified state
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que sólo trabaja sobre un change en `verified`

#### Scenario: The body runs the gate before proposing the commit
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que ejecuta `gate.py` antes de proponer el commit

#### Scenario: A red gate stops the skill
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que con la puerta en un código distinto de `0` se detiene
  y no hay commit

#### Scenario: The gate output is shown literally
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que enseña la salida literal de la puerta

verifies:   tests/test_close_skill.py
confidence: high
from:       README.md#las-siete-skills

### R-CLS-002 · Commit and push happen only with the user's explicit authorization

WHEN la puerta sale con código `0`, la skill `/venoxia:close` DEBE
comprobar que el índice está vacío, enseñar sin poner nada en él la lista
exacta de ficheros que irían al commit —todo lo que `git status` enumera,
agrupado—, la rama y el remoto del push y el mensaje propuesto, pedir la
autorización con `AskUserQuestion`, y sólo tras un sí explícito del usuario
añadir por ruta exactamente los ficheros de esa lista que el usuario no haya
excluido —los del propio change no se pueden excluir— y ejecutar
`git commit` y `git push`, sin pasar nunca `--no-verify`, `--force`,
`--amend` ni una opción `-c` o variable de entorno que cambie la
configuración de git.

#### Scenario: A non-empty index stops the skill
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que si el índice ya tiene cambios preparados antes de
  empezar, se detiene sin commit

#### Scenario: Nothing is staged before the yes
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que `git add` se ejecuta sólo después de la autorización

#### Scenario: Only the listed files are staged
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que añade por ruta exactamente los ficheros que enseñó,
  nunca con `git add -A` ni `git add .`

#### Scenario: Every changed file is proposed, grouped
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que la lista propuesta es todo lo que `git status`
  enumera, agrupado en tres grupos: bajo `.venoxia/`, nombrado en un
  `verifies:` del delta, y el resto

#### Scenario: The user excludes a file by naming it
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que un fichero de la lista queda fuera del commit cuando
  el usuario lo nombra en su respuesta

#### Scenario: The change's own files cannot be excluded
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que un fichero bajo `.venoxia/changes/<id>/` o nombrado
  en un `verifies:` del delta no se puede excluir, y que si el usuario lo
  nombra se detiene sin commit

#### Scenario: The branch and the remote are shown before asking
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que enseña la rama y el remoto del push antes de pedir la
  autorización

#### Scenario: No git configuration override
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que nunca pasa una opción `-c` ni cambia una variable de
  entorno de git

#### Scenario: The files to commit are shown before asking
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que enseña los ficheros que irían al commit antes de
  pedir la autorización

#### Scenario: The proposed message is shown before asking
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que enseña el mensaje de commit propuesto antes de pedir
  la autorización

#### Scenario: Authorization goes through AskUserQuestion
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que pide la autorización con `AskUserQuestion`

#### Scenario: No commit nor push without an explicit yes
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que sin un sí explícito del usuario no ejecuta ni
  `git commit` ni `git push`

#### Scenario: History is never rewritten nor hooks skipped
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que nunca pasa `--no-verify`, `--force` ni `--amend`

#### Scenario: A failed push is delivered as it is
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que un push en rojo se entrega tal cual y no se rodea

verifies:   tests/test_close_skill.py
confidence: high
from:       README.md#las-siete-skills

### R-CLS-003 · The commit message names the change and never the model nor the tool

WHEN la skill `/venoxia:close` redacta el mensaje de commit, el asunto DEBE
nombrar el change y el cuerpo DEBE listar los IDs de sus requisitos, y
ninguna línea del mensaje DEBE contener una referencia al modelo ni a la
herramienta, es decir, ni `Co-Authored-By`, ni «Generated with», ni
«Claude», ni «Claude Code».

#### Scenario: The subject names the change
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el asunto del mensaje nombra el change

#### Scenario: The body lists the requirement IDs
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el cuerpo del mensaje lista los IDs de los requisitos
  del change

#### Scenario: No co-author trailer
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el mensaje no lleva ninguna línea `Co-Authored-By`

#### Scenario: No generated-with footer
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el mensaje no lleva ningún pie «Generated with»

#### Scenario: No mention of the model nor the tool
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el mensaje no menciona a Claude ni a Claude Code

verifies:   tests/test_close_skill.py
confidence: high
from:       README.md#las-siete-skills

### R-CLS-004 · The close skill writes no file and its tools are bounded to the gate and git

La skill `/venoxia:close` NO DEBE escribir ningún fichero —ni bajo
`.venoxia/`, ni ningún estado del change, ni código— y su `allowed-tools`
DEBE ser exactamente `Read`, `Glob`, `AskUserQuestion`, el `Bash` acotado a
`gate.py` y los `Bash` acotados a `git status`, `git diff`, `git log`,
`git rev-parse`, `git branch`, `git add`, `git commit` y `git push`, y su
entrega DEBE nombrar el hash del commit, la rama y el remoto, el resultado
del push y `/venoxia:specify` como siguiente paso.

#### Scenario: The tools are exactly the twelve declared
- **WHEN** se lee el frontmatter de `skills/close/SKILL.md`
- **THEN** `allowed-tools` es exactamente `Read`, `Glob`, `AskUserQuestion`,
  el `Bash` acotado a `gate.py` y los ocho `Bash` acotados a `git status`,
  `git diff`, `git log`, `git rev-parse`, `git branch`, `git add`,
  `git commit` y `git push`

#### Scenario: No generic Bash
- **WHEN** se lee el frontmatter de `skills/close/SKILL.md`
- **THEN** ninguna entrada de `allowed-tools` es un `Bash` sin acotar

#### Scenario: No Write nor Edit
- **WHEN** se lee el frontmatter de `skills/close/SKILL.md`
- **THEN** ninguna entrada de `allowed-tools` es `Write` ni `Edit`

#### Scenario: The body says it writes no file
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que no escribe ningún fichero

#### Scenario: The body says it writes no state
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que no escribe ningún estado del change

#### Scenario: The delivery names the commit hash
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que la entrega nombra el hash del commit

#### Scenario: The delivery names the branch and the remote
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que la entrega nombra la rama y el remoto

#### Scenario: The delivery names the push result
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que la entrega nombra el resultado del push

#### Scenario: The next step is specify
- **WHEN** se lee el cuerpo de `skills/close/SKILL.md`
- **THEN** declara que el siguiente paso es `/venoxia:specify`

verifies:   tests/test_close_skill.py
confidence: medium
  why:      sin Bash genérico la skill no puede lanzar la suite entera ni un build; se elige porque la puerta es el contrato declarado del proyecto (B-006)
from:       README.md#las-siete-skills
