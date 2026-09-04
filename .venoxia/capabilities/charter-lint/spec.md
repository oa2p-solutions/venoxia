# Capability: charter-lint

## Purpose

Decide si `.venoxia/charter.md` tiene sus cinco secciones y cumple los
criterios de cierre que las hacen verificables, con el mismo contrato de
salida y de JSON que el validador de requisitos.

## Requirements

### R-CHL-001 · Exit code contract

WHEN alguien ejecuta `scripts/charter_lint.py`, el sistema DEBE terminar con
`0` si el acta cumple, `1` si no cumple —contando los avisos como fallo
cuando se pide `--strict`— y `2` si el uso del propio CLI es incorrecto.

#### Scenario: Usage error on a missing explicit path
- **WHEN** se nombra un acta que no existe en disco
- **THEN** el proceso termina con código `2` y el mensaje por stderr dice que no existe la ruta

#### Scenario: Strict turns a warning into a failure
- **WHEN** la misma acta con un solo aviso se valida con y sin «--strict»
- **THEN** sin «--strict» sale `0` y con «--strict» sale `1`, con `ok: false` en el JSON

verifies:   tests/test_charter_lint.py
confidence: high
from:       README.md#las-19-reglas-del-linter-del-acta

### R-CHL-002 · Absence of Venoxia or of a charter does not block

WHEN se ejecuta `charter_lint.py` sobre un proyecto sin `.venoxia/`, o con
`.venoxia/` pero sin `charter.md`, el sistema DEBE terminar con `0` e
invitar a escribir el acta en vez de tratar la ausencia como un
incumplimiento.

#### Scenario: No .venoxia/ at all
- **WHEN** la raíz del proyecto no contiene ningún directorio `.venoxia/`
- **THEN** el proceso sale con `0` y dice que el proyecto todavía no ha adoptado Venoxia

#### Scenario: .venoxia/ without a charter
- **WHEN** existe `.venoxia/` pero no `.venoxia/charter.md`
- **THEN** el proceso sale con `0` y menciona `/venoxia:charter` como el paso siguiente

verifies:   tests/test_charter_lint.py
confidence: high
from:       README.md#las-19-reglas-del-linter-del-acta

### R-CHL-003 · C07 requires a Done when per capability

WHEN una fila de la tabla de capabilities no declara «Done when», el sistema
DEBE marcar el hallazgo `C07` señalando esa fila por su slug, con un mensaje
que explique que sin criterio de terminación la fila es un deseo y no una
capability.

#### Scenario: A capability row with an empty Done when
- **WHEN** la columna «Done when» de una fila está vacía
- **THEN** salta `C07` sobre esa fila con un hint que pide quién lo ve y qué ve

verifies:   tests/test_charter_lint.py
confidence: high
from:       README.md#las-19-reglas-del-linter-del-acta

### R-CHL-004 · C12 rejects a date and rejects filler

WHEN una apuesta en `confidence: low` declara «revisit:» con una fecha del
calendario, o con una palabra de relleno que sólo pospone («ya veremos»,
«más adelante», «TBD»), el sistema DEBE marcar el hallazgo `C12`, porque
ninguna de las dos dice qué hecho resuelve la apuesta.

#### Scenario: A future date
- **WHEN** «revisit:» trae una fecha futura
- **THEN** salta `C12` y el mensaje dice que es una fecha y que hace falta el hecho que resuelve la apuesta

#### Scenario: Filler that only means later
- **WHEN** «revisit:» trae «ya veremos», «más adelante» o «TBD»
- **THEN** salta `C12` y el mensaje dice que no nombra ningún hecho

verifies:   tests/test_charter_lint.py
confidence: high
from:       README.md#las-19-reglas-del-linter-del-acta

### R-CHL-005 · Stable JSON schema

WHEN se pide `--json`, el sistema DEBE responder con el documento de esquema
versión 1: `version`, `ok`, `strict`, `root`, `counts`, `findings`,
`budget`, `adopted` y `charter` —este último con el acta anidada cuando
existe, o `null` cuando no.

#### Scenario: The nine schema keys are present
- **WHEN** se pide el JSON de un acta que sí existe
- **THEN** las nueve claves están todas en el primer nivel del documento

verifies:   tests/test_charter_lint.py
confidence: high
from:       README.md#las-19-reglas-del-linter-del-acta
