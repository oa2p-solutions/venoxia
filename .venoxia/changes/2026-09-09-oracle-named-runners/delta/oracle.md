# oracle Delta

## ADDED Requirements

### R-ORC-013 · A requirement chooses its runner by name

WHEN un requisito declara `runner: <name>` y `.venoxia/venoxia.json` declara
ese nombre bajo `runners`, el sistema DEBE ejecutar el `command` de ese runner
para ese requisito en lugar del `test_command`.

#### Scenario: The named runner replaces the default for that requirement
- **WHEN** un requisito declara `runner: alt` y el `command` del runner `alt`
  es distinto del `test_command`
- **THEN** el comando que se ejecuta para ese requisito es el `command` del
  runner `alt`

#### Scenario: A requirement without runner keeps the default
- **WHEN** un change tiene un requisito con `runner: alt` y otro sin `runner:`
- **THEN** el comando que se ejecuta para el requisito sin `runner:` es el
  `test_command`

#### Scenario: The placeholder of a named runner is substituted
- **WHEN** el `command` del runner `alt` contiene `{files}`
- **THEN** el comando que se ejecuta lleva las rutas de `verifies:` del
  requisito en el lugar de `{files}`

#### Scenario: A runner with its own cwd runs there
- **WHEN** el runner `alt` declara un `cwd` relativo a la raíz del proyecto
- **THEN** el comando se ejecuta con ese directorio como directorio de trabajo

#### Scenario: The paths follow the runner into its cwd
- **WHEN** el runner `alt` declara `cwd: sub` y su `command` contiene `{files}`
- **THEN** el comando que se ejecuta lleva las rutas de `verifies:` reescritas
  en relación a `sub`, de modo que desde `sub` apuntan al mismo fichero

#### Scenario: A runner without cwd inherits the project's
- **WHEN** el runner `alt` no declara `cwd`
- **THEN** el comando se ejecuta con el `cwd` del proyecto como directorio de
  trabajo

#### Scenario: A failing named runner is a red requirement
- **WHEN** el `command` del runner `alt` termina con código `1`
- **THEN** el requisito que lo declara queda con `status: red` y
  `exit_code: 1`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-014 · A named runner without {files} runs verbatim

WHEN el `command` del runner con nombre que un requisito declara no contiene
`{files}`, el sistema DEBE ejecutar ese `command` tal cual, sin sustituir
nada en él.

#### Scenario: The command runs character for character
- **WHEN** el `command` del runner `coverage` no contiene `{files}` y el
  fichero de `verifies:` del requisito existe
- **THEN** el comando que se ejecuta es el `command` del runner `coverage`,
  carácter a carácter

#### Scenario: A verbatim runner that passes is a green requirement
- **WHEN** el `command` del runner `coverage` no contiene `{files}` y termina
  con código `0`
- **THEN** el requisito que lo declara queda con `status: green`

#### Scenario: The verifies path is still the anchor
- **WHEN** el fichero de `verifies:` del requisito no existe y su runner no
  contiene `{files}`
- **THEN** el requisito queda con `status: missing`

#### Scenario: A missing anchor does not run the verbatim command
- **WHEN** el fichero de `verifies:` del requisito no existe y su runner no
  contiene `{files}`
- **THEN** el comando de ese runner no se ejecuta

#### Scenario: Dry run prints the verbatim command
- **WHEN** se pide `--dry-run` sobre un requisito cuyo runner no contiene
  `{files}`
- **THEN** la línea de ese requisito muestra el `command` del runner tal cual

#### Scenario: The default runner still demands the placeholder
- **WHEN** el `test_command` no contiene `{files}` y `runners` declara un
  runner válido
- **THEN** el proceso termina con código `2`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-015 · An undeclared or malformed runner is a usage error, never a red

IF algún requisito del change declara `runner: <name>` sin que
`.venoxia/venoxia.json` declare ese nombre bajo `runners` con un `command` no
vacío, o `runners` no es un objeto JSON, THEN el sistema DEBE terminar con
código `2` sin ejecutar ningún comando y sin escribir ningún fichero.

#### Scenario: An undeclared name is a usage error
- **WHEN** un requisito declara `runner: nope` y `runners` no tiene la clave
  `nope`
- **THEN** el proceso termina con código `2`

#### Scenario: Nothing runs, not even the other requirements
- **WHEN** un change tiene dos requisitos, el primero sin `runner:` y el
  segundo con `runner: nope` no declarado
- **THEN** el proceso termina con código `2` y no se ejecuta ningún comando,
  tampoco el del primer requisito

#### Scenario: The message names the runner and the file
- **WHEN** un requisito declara `runner: nope` y `runners` no tiene la clave
  `nope`
- **THEN** el proceso termina con código `2` y `stderr` recibe un aviso que
  nombra `nope` y `venoxia.json`

#### Scenario: Nothing is recorded
- **WHEN** se pide `--record` sobre un change sin `oracle.json` y un requisito
  declara `runner: nope` no declarado
- **THEN** el proceso termina con código `2` y el directorio del change no
  gana ningún fichero

#### Scenario: Dry run is a usage error too
- **WHEN** se pide `--dry-run` y un requisito declara `runner: nope` no
  declarado
- **THEN** el proceso termina con código `2`

#### Scenario: A runner without a command
- **WHEN** `runners` declara `alt` sin `command`, o con un `command` vacío, y
  un requisito declara `runner: alt`
- **THEN** el proceso termina con código `2`

#### Scenario: A runners key that is not an object
- **WHEN** `runners` es una lista JSON en vez de un objeto, aunque ningún
  requisito declare `runner:`
- **THEN** el proceso termina con código `2`

#### Scenario: A runner whose cwd does not exist
- **WHEN** el runner `alt` declara un `cwd` que no existe en disco y un
  requisito declara `runner: alt`
- **THEN** el proceso termina con código `2`

verifies:   tests/test_oracle.py
confidence: high
from:       README.md#ejecutar-el-oraculo

### R-ORC-016 · Each result names the runner that produced it

WHEN el oráculo produce el documento JSON de un run, el sistema DEBE incluir
en cada elemento de `results` una clave `runner` con exactamente las claves
`name`, `command` y `cwd`, conservando el conjunto de claves de primer nivel
del documento.

#### Scenario: A named runner is named in its result
- **WHEN** un requisito declara `runner: alt`
- **THEN** su elemento de `results` trae `runner.name` igual a `alt`

#### Scenario: The command recorded is the one that ran
- **WHEN** el `command` del runner de un requisito contiene `{files}`
- **THEN** `runner.command` de su elemento de `results` trae las rutas de
  `verifies:` ya sustituidas

#### Scenario: The default runner has no name
- **WHEN** un requisito no declara `runner:`
- **THEN** su elemento de `results` trae `runner.name` igual a `null`

#### Scenario: The default runner still records its command
- **WHEN** un requisito no declara `runner:`
- **THEN** `runner.command` de su elemento de `results` es el `test_command`
  con las rutas de `verifies:` ya sustituidas

#### Scenario: The working directory is recorded
- **WHEN** el runner de un requisito declara un `cwd` propio
- **THEN** `runner.cwd` de su elemento de `results` nombra ese directorio

#### Scenario: A missing requirement carries its runner too
- **WHEN** el fichero de `verifies:` de un requisito no existe
- **THEN** su elemento de `results` trae la clave `runner` igual que los demás

#### Scenario: The recorded history carries it
- **WHEN** se pide `--record` sobre un change con un requisito con
  `runner: alt`
- **THEN** el último run de `oracle.json` trae `runner.name` igual a `alt` en
  el elemento de `results` de ese requisito

#### Scenario: The top level keeps its eight keys
- **WHEN** se pide `--json` sobre un change con un requisito con `runner: alt`
- **THEN** las claves de primer nivel del documento son exactamente las ocho
  de `R-ORC-008`

verifies:   tests/test_oracle.py
confidence: medium
  why:      el null como nombre del test_command y las tres claves las eligió Claude; nadie las lee todavía
  revisit:  cuando gate.py o /venoxia:verify lean runner.name por primera vez
from:       README.md#ejecutar-el-oraculo
