# validator Delta

## ADDED Requirements

### R-VAL-008 · V19 requires every declared runner to exist in venoxia.json

IF un requisito declara `runner: <name>` y `.venoxia/venoxia.json` no declara
ese nombre bajo `runners` con un `command` no vacío y un `cwd` que exista en
disco, THEN el sistema DEBE marcar el hallazgo `V19` con severidad `error`
sobre ese requisito, nombrando el runner y el fichero.

#### Scenario: An undeclared runner name
- **WHEN** un requisito declara `runner: nope` y `venoxia.json` no tiene
  `nope` bajo `runners`
- **THEN** salta `V19` sobre ese requisito y es la única regla que salta

#### Scenario: No venoxia.json at all
- **WHEN** un requisito declara `runner: alt` y no existe
  `.venoxia/venoxia.json`
- **THEN** salta `V19` sobre ese requisito

#### Scenario: A declared runner is silent
- **WHEN** un requisito declara `runner: alt` y `venoxia.json` declara `alt`
  bajo `runners` con un `command` no vacío
- **THEN** el validador no emite ningún hallazgo

#### Scenario: No runner, no rule
- **WHEN** ningún requisito declara `runner:` y no existe `venoxia.json`
- **THEN** `V19` no se dispara

#### Scenario: An empty runner
- **WHEN** un requisito declara `runner:` sin valor
- **THEN** salta `V19` y el mensaje dice que no nombra ningún runner

#### Scenario: A declared runner without a command
- **WHEN** un requisito declara `runner: alt` y `venoxia.json` declara `alt`
  bajo `runners` sin `command`
- **THEN** salta `V19` sobre ese requisito

#### Scenario: A declared runner whose cwd does not exist
- **WHEN** un requisito declara `runner: alt` y `venoxia.json` declara `alt`
  bajo `runners` con un `cwd` que no existe en disco
- **THEN** salta `V19` sobre ese requisito

#### Scenario: A corrupt venoxia.json does not crash the validator
- **WHEN** un requisito declara `runner: alt` y `venoxia.json` no se puede
  interpretar como JSON
- **THEN** salta `V19` con un mensaje que dice que el fichero no se pudo leer,
  sin ningún «Traceback» en la salida

#### Scenario: The hint shows the entry to add
- **WHEN** un requisito declara `runner: alt` y `venoxia.json` no tiene `alt`
  bajo `runners`
- **THEN** el hint del hallazgo enseña una entrada de `runners` con la clave
  `alt`

verifies:   tests/test_rules_oracle.py
confidence: high
from:       README.md#las-19-reglas-del-validador
