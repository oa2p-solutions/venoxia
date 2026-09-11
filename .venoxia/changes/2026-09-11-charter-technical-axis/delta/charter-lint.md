# charter-lint Delta

## ADDED Requirements

### R-CHL-006 · The charter skill writes technical decisions as requirements or bets, never as prose

WHEN la tanda de convenciones técnicas de `/venoxia:charter` termina, la skill
DEBE llevar cada convención aprobada a la capability `technical-contract`
—una fila en la tabla del acta y el `/venoxia:specify` tecleado de la
entrega, que escribirá sus requisitos con `verifies:`— y cada convención sin
decidir a `## Bets` con el hecho que la cierra, y DEBE escribir
`principles.md` sólo con los tres principios del método y los de dominio,
repartiendo igual —antes de quitarles la sección y sin perder ninguna— las
convenciones técnicas que ese fichero ya traiga de una entrevista anterior.

#### Scenario: An approved convention is a requirement of technical-contract
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una convención aprobada es un requisito de
  `technical-contract`

#### Scenario: An undecided convention is a bet
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que una convención sin decidir es una apuesta en `## Bets`

#### Scenario: The principles file carries no technical conventions
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que `principles.md` no lleva convenciones técnicas

#### Scenario: The technical conventions heading is gone
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** no contiene el encabezado `## Convenciones técnicas`

#### Scenario: Existing conventions are moved, not dropped
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que las convenciones técnicas que ya estén en
  `principles.md` se reparten igual antes de quitar la sección

#### Scenario: The delivery hands the approved conventions to specify
- **WHEN** se lee el cuerpo de `skills/charter/SKILL.md`
- **THEN** declara que la entrega termina con el `/venoxia:specify` de
  `technical-contract` cuando hay convenciones aprobadas

verifies:   tests/test_charter_skill.py
confidence: high
from:       README.md#cómo-se-usa

### R-CHL-007 · The specify skill sends an ungoverned technical judgement to the contract or to a bet

WHEN `/venoxia:specify` encuentra en el cambio un juicio técnico que ningún
principio de dominio ni requisito de `technical-contract` gobierna, la skill
DEBE llevarlo a un requisito de `technical-contract` con `verifies:` o a una
apuesta de `## Bets` con el hecho que lo cierra, nunca a prosa; y sólo es
apuesta cuando ningún test podría comprobarlo hoy aunque se escribiera —si
un test que todavía no existe bastaría para comprobarlo, es requisito.

#### Scenario: The body names the two destinations
- **WHEN** se lee el cuerpo de `skills/specify/SKILL.md`
- **THEN** declara que un juicio técnico sin principio va a
  `technical-contract` o a `## Bets`

#### Scenario: The body forbids prose
- **WHEN** se lee el cuerpo de `skills/specify/SKILL.md`
- **THEN** declara que un juicio técnico sin principio nunca va a prosa

#### Scenario: A bet only when no test could check it
- **WHEN** se lee el cuerpo de `skills/specify/SKILL.md`
- **THEN** declara que el juicio técnico sólo es apuesta cuando ningún test
  podría comprobarlo aunque se escribiera

#### Scenario: The inventory includes the technical contract
- **WHEN** se lee el cuerpo de `skills/specify/SKILL.md`
- **THEN** manda leer `.venoxia/capabilities/technical-contract/spec.md` antes
  de proponer nada

verifies:   tests/test_specify_skill.py
confidence: high
from:       README.md#cómo-se-usa
