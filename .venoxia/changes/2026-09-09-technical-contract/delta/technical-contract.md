# technical-contract Delta

## ADDED Requirements

### R-TEC-001 · Scripts, tools and tests import only the standard library

El repositorio DEBE mantener cada fichero `.py` bajo `scripts/`, `tools/` y
`tests/`, a cualquier profundidad, importando sólo módulos de la biblioteca
estándar de Python o módulos del propio repositorio.

#### Scenario: Every import resolves to the standard library or to the repository
- **WHEN** se recorren con `ast` los `import` de todos los ficheros `.py` bajo
  `scripts/`, `tools/` y `tests/`, a cualquier profundidad
- **THEN** cada módulo importado está en `sys.stdlib_module_names` o es un
  fichero o paquete del propio repositorio

#### Scenario: A third-party import fails the test
- **WHEN** un fuente analizado importa un paquete ajeno, como `requests`
- **THEN** el test falla nombrando el fichero y el módulo

#### Scenario: pytest is never a requirement
- **WHEN** se recorren con `ast` los `import` de todos los ficheros `.py` bajo
  `tests/`, a cualquier profundidad
- **THEN** ninguno nombra `pytest`

#### Scenario: A dynamic import fails the test
- **WHEN** un fuente bajo `scripts/` o `tools/` llama a `importlib.import_module`
  o a `__import__`
- **THEN** el test falla nombrando el fichero y la llamada

verifies:   tests/test_technical_contract.py
confidence: high
from:       2026-09-08-vision-conversacion.md

### R-TEC-002 · No script reaches the network or a model

El repositorio DEBE mantener cada fichero `.py` bajo `scripts/` sin importar
ningún módulo de red de la biblioteca estándar —`urllib`, `http`, `socket`,
`ssl`, `smtplib`, `ftplib`, `xmlrpc`—, ningún cliente de modelo —`anthropic`,
`openai`—, sin importar `subprocess` fuera de `scripts/oracle.py` y
`scripts/gate.py`, y sin lanzar procesos por `os` (`os.system`, `os.popen`,
`os.exec*`, `os.spawn*`, `os.posix_spawn*`).

#### Scenario: No network module in any script
- **WHEN** se recorren con `ast` los `import` de todos los ficheros `.py` de
  `scripts/`
- **THEN** ninguno nombra `urllib`, `http`, `socket`, `ssl`, `smtplib`,
  `ftplib` ni `xmlrpc`

#### Scenario: No model client in any script
- **WHEN** se recorren con `ast` los `import` de todos los ficheros `.py` de
  `scripts/`
- **THEN** ninguno nombra `anthropic` ni `openai`

#### Scenario: A network import fails the test
- **WHEN** un fuente analizado importa `urllib.request`
- **THEN** el test falla nombrando el fichero y el módulo

#### Scenario: Only the oracle and the gate spawn subprocesses
- **WHEN** se recorren con `ast` los `import` de todos los ficheros `.py` bajo
  `scripts/`
- **THEN** los únicos que nombran `subprocess` son `scripts/oracle.py` y
  `scripts/gate.py`

#### Scenario: No script shells out through os
- **WHEN** se recorren con `ast` las llamadas de todos los ficheros `.py` bajo
  `scripts/`
- **THEN** ninguna es a `os.system`, `os.popen`, `os.exec*`, `os.spawn*` ni
  `os.posix_spawn*`

verifies:   tests/test_technical_contract.py
confidence: high
from:       2026-09-08-vision-conversacion.md

### R-TEC-003 · The guardian imports nothing shared

El repositorio DEBE mantener `scripts/guardian.py` importando sólo módulos de
la biblioteca estándar de Python.

#### Scenario: Only the standard library
- **WHEN** se recorren con `ast` los `import` de `scripts/guardian.py`
- **THEN** cada módulo importado está en `sys.stdlib_module_names`

#### Scenario: No shared package
- **WHEN** se recorren con `ast` los `import` de `scripts/guardian.py`
- **THEN** ninguno nombra `venoxia` ni `validate`

#### Scenario: No subprocess and no dynamic import
- **WHEN** se recorren con `ast` los `import` de `scripts/guardian.py`
- **THEN** ninguno nombra `subprocess`, `runpy` ni `importlib`

verifies:   tests/test_guardian.py
confidence: high
from:       README.md#el-modelo-de-confianza-del-guardián

### R-TEC-004 · Every script stays above its coverage threshold

WHEN se ejecuta `tools/coverage.py`, el sistema DEBE terminar con código `0`
sólo si cada fichero de `scripts/**/*.py` alcanza el porcentaje de líneas
ejecutadas que `tools/coverage-threshold.json` le asigna.

#### Scenario: Every file at or above its threshold
- **WHEN** todos los ficheros medidos alcanzan su umbral
- **THEN** el proceso termina con código `0`

#### Scenario: One file below its threshold
- **WHEN** algún fichero medido queda por debajo de su umbral
- **THEN** el proceso termina con código `1`

#### Scenario: The report names each file with its figures
- **WHEN** termina la medición
- **THEN** la salida lista cada fichero de `scripts/**/*.py`, tenga datos o
  no, con su porcentaje y su umbral

#### Scenario: A script the suite never runs is below its threshold
- **WHEN** un fichero de `scripts/**/*.py` no tiene ninguna línea ejecutada
  por la suite
- **THEN** cuenta como por debajo de su umbral y el proceso termina con
  código `1`

#### Scenario: A file without an entry is held to the core floor
- **WHEN** un fichero medido no tiene entrada en `tools/coverage-threshold.json`
- **THEN** su umbral es el suelo del núcleo, `85`, y no su propia medida

verifies:   tools/coverage.py, tests/test_coverage.py
runner:     coverage
confidence: high
from:       2026-09-08-vision-conversacion.md

### R-TEC-005 · The five CLIs share the exit-code contract

El repositorio DEBE mantener en `scripts/validate.py`,
`scripts/charter_lint.py`, `scripts/diff_readings.py`, `scripts/oracle.py` y
`scripts/gate.py` el mismo contrato de códigos de salida: `0` cumple, `1` no
cumple y `2` no hubo veredicto.

#### Scenario: An unknown option is 2 in all five
- **WHEN** cada uno de los cinco se invoca con una opción que no existe
- **THEN** cada uno termina con código `2`

#### Scenario: A root that does not exist is 2 in all five
- **WHEN** cada uno de los cinco recibe una raíz —o, en `diff_readings.py`,
  un directorio de lecturas— que no existe en disco
- **THEN** cada uno termina con código `2`

#### Scenario: In the gate, 2 means it could not look
- **WHEN** `scripts/gate.py` encuentra un `.venoxia/` sin `venoxia.json`
- **THEN** el proceso termina con código `2`

verifies:   tests/test_technical_contract.py
confidence: high
from:       2026-09-08-vision-conversacion.md

### R-TEC-006 · Report schemas only grow

WHEN quien invoca `build_payload` del módulo compartido de informes añade
claves de primer nivel, el sistema DEBE conservar las siete claves del esquema
versión 1 con `version` igual al entero `1`.

#### Scenario: Extra keys never remove the schema ones
- **WHEN** se llama a `build_payload` con claves extra
- **THEN** las siete claves del esquema siguen presentes junto a las añadidas

#### Scenario: The version is the integer one
- **WHEN** se construye cualquier informe
- **THEN** `version` vale `1` y es un entero, no una cadena

#### Scenario: Serialisation keeps every key
- **WHEN** el informe pasa por `render_json`
- **THEN** el JSON resultante conserva todas las claves del informe

verifies:   tests/test_report.py
confidence: high
from:       2026-09-08-vision-conversacion.md
