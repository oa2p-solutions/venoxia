# ci Delta

## MODIFIED Requirements

### R-CI-019 · The local check runs the CI gate as one command

WHEN se ejecuta `tools/check.py` desde la raíz del repositorio, el sistema
DEBE ejecutar tres pasos —`matrix`, `gate` y `plugin-validate`— y DEBE
terminar con código `0` sólo si los tres terminan en verde, con `1` si alguno
falla y con `2` si un paso no se pudo ejecutar o la invocación es incorrecta.

Los tres pasos son la puerta entera, en local: `matrix` es la suite en cada
versión de Python soportada, `gate` es `scripts/gate.py --root .` sobre este
mismo repositorio —que incluye el acta y el validador en estricto y el
oráculo de cada change en `verified`, y con él `tools/coverage.py` como
runner de `R-TEC-004`—, y `plugin-validate` es `claude plugin validate .
--strict`. La cobertura ya no es un paso propio: correrla dentro del gate y
otra vez fuera eran dos minutos por push midiendo lo mismo. El job `evals`
se queda fuera a propósito: cuesta tokens y se lanza a mano.

Un paso que no se pudo ejecutar no es un paso en rojo ni en verde: es una
comprobación que no ocurrió, y aprobarla sería aprobar lo que no se ha
mirado. Por eso el código es `2`, el mismo que el resto del núcleo reserva
para el error de uso.

#### Scenario: The three steps by name
- **WHEN** se pide la lista de pasos con `--list`
- **THEN** la salida nombra `matrix`, `gate` y `plugin-validate` con el
  comando de cada uno, no se ejecuta ninguno y la comprobación termina con
  código `0`

#### Scenario: Coverage is not a step of its own
- **WHEN** se pide la lista de pasos con `--list`
- **THEN** ningún paso se llama `coverage`

#### Scenario: One step fails
- **WHEN** un paso termina en fallo
- **THEN** el resumen lo marca en rojo, muestra el final de su salida y la
  comprobación termina con código `1`

#### Scenario: Every step passes
- **WHEN** los tres pasos terminan en verde
- **THEN** la comprobación termina con código `0`

#### Scenario: A required executable is missing
- **WHEN** falta en el `PATH` un ejecutable que un paso necesita
- **THEN** la comprobación termina con código `2` y el mensaje nombra el
  ejecutable que falta

#### Scenario: An unknown option
- **WHEN** se invoca con una opción que no existe
- **THEN** la comprobación termina con código `2` y el mensaje de uso

verifies:   tests/test_check.py
confidence: high
from:       README.md#verificar-regresiones
