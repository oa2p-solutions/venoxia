# Capability: divergence

## Purpose

Coteja dos o más lecturas aisladas del mismo delta y convierte cada
desacuerdo detectable en una divergencia dura o blanda, sin que ningún
modelo participe en la aritmética de la comparación.

## Requirements

### R-DIV-001 · A different status code is a hard divergence

WHEN dos lecturas del mismo escenario declaran un `status_code` distinto,
el sistema DEBE marcar el campo `status_code` como divergencia dura y hacer
que la ejecución termine con código `1`.

#### Scenario: 409 against 422 on the same scenario
- **WHEN** una lectura dice `409` y la otra `422` para el mismo escenario
- **THEN** la divergencia queda marcada como dura sobre el campo `status_code` y el proceso sale con `1`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-002 · Fewer than two readers cannot claim convergence

WHEN se ejecuta `diff_readings.py` con menos de dos ficheros de lectura en
`readings/`, el sistema DEBE terminar con código `2` y responder con
`"converged": false` y `"verdict": "too_few_readers"`, sin afirmar ningún
acuerdo que no se pudo contrastar.

#### Scenario: A single reader
- **WHEN** `readings/` contiene un único fichero de lectura
- **THEN** el JSON dice `converged: false`, `verdict: too_few_readers` y el proceso sale con `2`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-003 · Only soft divergences pass unless strict

WHEN la única divergencia entre dos lecturas es blanda, el sistema DEBE
terminar con código `0` por omisión, y DEBE terminar con código `1` cuando
se pide `--strict`, dejando claro en el informe qué modo decidió el
resultado.

#### Scenario: Without strict, a soft divergence is a warning
- **WHEN** dos lecturas sólo divergen de forma blanda y no se pide `--strict`
- **THEN** el proceso sale con `0` y el resumen se marca con «⚠»

#### Scenario: With strict, the same pair fails
- **WHEN** el mismo par se compara con `--strict`
- **THEN** el proceso sale con `1` y el resumen se marca con «✗»

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-004 · A different number is never diluted

WHEN dos lecturas describen la misma acción con una cifra distinta, el
sistema DEBE devolver una similitud de `0.0` entre ellas, aunque compartan
casi todas las demás palabras del texto.

#### Scenario: Same words, different number
- **WHEN** una lectura dice «21 días» y la otra «14 días» sobre el mismo hecho
- **THEN** la similitud calculada es exactamente `0.0`

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills
