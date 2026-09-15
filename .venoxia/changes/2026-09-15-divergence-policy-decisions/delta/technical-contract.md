# technical-contract Delta

## ADDED Requirements

### R-TEC-007 · Every report says which Venoxia produced it

WHEN `validate.py`, `charter_lint.py` o `diff_readings.py` emiten su informe
JSON, el sistema DEBE añadir la clave `tool` con `name` igual a `venoxia`,
`version` igual a la versión del manifiesto `.claude-plugin/plugin.json` que
acompaña a los scripts y `script` con el nombre del script; el informe de texto
DEBE nombrar la misma versión; y con un manifiesto ilegible o ausente DEBE
escribir `unknown` como versión sin alterar el veredicto ni el código de
salida.

#### Scenario: The three JSON reports name the version
- **WHEN** se ejecutan los tres scripts con `--json` sobre un proyecto
- **THEN** cada JSON trae `tool.name` igual a `venoxia`, `tool.version` igual a
  la del manifiesto y `tool.script` con el nombre del script

#### Scenario: The text report names the version
- **WHEN** se ejecutan los tres scripts sin `--json`
- **THEN** la salida contiene «Venoxia» seguido de la versión del manifiesto

#### Scenario: A missing manifest does not break the report
- **WHEN** el manifiesto no se puede leer
- **THEN** `tool.version` vale `unknown` y el veredicto y el código de salida
  son los mismos

verifies:   tests/test_tool_version.py
confidence: high
from:       2026-09-15-divergencia-caso-real.md#hallazgo-6--no-hay-forma-de-demostrar-qué-versión-corre
