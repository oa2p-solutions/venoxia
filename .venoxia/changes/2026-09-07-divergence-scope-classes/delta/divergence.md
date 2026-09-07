# divergence Delta

## ADDED Requirements

### R-DIV-012 · Scope marks contradict only across classes

WHEN dos lectores registran sobre el mismo escenario dos efectos con el mismo
sujeto, el sistema DEBE contar el alcance como contradicción únicamente si los
dos efectos llevan marcas de alcance de clases distintas —«sólo»,
«solamente», «únicamente», «único» y «única» son una clase; «parcial» y sus
formas, otra; «completo», «total», «todo» y sus formas, la tercera—, y no
cuando comparten clase ni cuando sólo uno de los dos lleva marca.

#### Scenario: Two synonyms of the same class
- **WHEN** un lector registra «crea oracle.json como único fichero nuevo» y el
  otro «crea sólo oracle.json»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: A mark against no mark
- **WHEN** un lector registra «crea oracle.json» y el otro «crea sólo
  oracle.json»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: Two marks of different classes
- **WHEN** un lector registra «reserva creada para el pedido completo» y el
  otro «reserva creada sólo para las unidades con stock»
- **THEN** esa diferencia hace dura la divergencia

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#cómo-se-usa
