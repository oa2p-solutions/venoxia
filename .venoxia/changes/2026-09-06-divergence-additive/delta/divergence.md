# divergence Delta

## ADDED Requirements

### R-DIV-005 · An added side effect is soft, a contradicted one is hard

WHEN un lector registra un efecto colateral que no aparece recogido en el
repertorio de otro lector, el sistema DEBE clasificar esa divergencia como
dura si el efecto contradice algo de ese repertorio, y como blanda si sólo
añade, porque dos lecturas que no se niegan pueden ser las dos correctas y
la categoría dura afirma justo lo contrario.

#### Scenario: A purely added side effect is soft
- **WHEN** un lector registra «se ejecutan los tests del change» y el
  repertorio del otro no dice nada sobre ejecutar tests
- **THEN** la divergencia se clasifica como blanda

#### Scenario: An opposite polarity is hard
- **WHEN** un lector registra «no se crea el presupuesto» y el otro registra
  «se crea el presupuesto»
- **THEN** la divergencia se clasifica como dura

#### Scenario: A different number is hard
- **WHEN** un lector registra «reserva durante 15 minutos» y el otro
  «reserva durante 30 minutos»
- **THEN** la divergencia se clasifica como dura

#### Scenario: An unrelated added effect stays soft
- **WHEN** un lector registra un efecto cuyo contenido no coincide con nada
  del otro repertorio ni siquiera ignorando negaciones y cifras
- **THEN** la divergencia se clasifica como blanda

#### Scenario: A soft divergence is still reported
- **WHEN** una divergencia de efectos colaterales se clasifica como blanda
- **THEN** sigue apareciendo en el informe con su pregunta cerrada y sus
  opciones, porque bajar de categoría no es descartar

#### Scenario: Strict mode still fails on an addition
- **WHEN** se ejecuta con `--strict` y la única divergencia es un efecto
  colateral añadido
- **THEN** la ejecución termina con código `1`

#### Scenario: A contradiction the rule cannot see stays soft
- **WHEN** dos lectores registran «se borra el borrador» y «se conserva el
  borrador», que se contradicen sin negación ni cifra
- **THEN** la divergencia se clasifica como blanda, y sigue presentándose al
  revisor con su pregunta

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-006 · The report says which of the two it is

WHEN el informe presenta una divergencia de efectos colaterales, el sistema
DEBE decir si el efecto contradice al otro lector o si sólo lo añade, para
que quien lo lee no tenga que deducir por qué una diferencia de colaterales
aparece como dura y otra como blanda.

#### Scenario: A contradiction says so
- **WHEN** el informe presenta una divergencia dura de efectos colaterales
- **THEN** su detalle dice que el efecto contradice lo que registra el otro
  lector

#### Scenario: An addition says so
- **WHEN** el informe presenta una divergencia blanda de efectos colaterales
- **THEN** su detalle dice que ninguna otra lectura lo niega ni le pone otra
  cifra, que es exactamente lo comprobado, en vez de afirmar que nadie lo
  contradice

verifies:   tests/test_diff_readings.py
confidence: high
from:       README.md#las-cuatro-skills

### R-DIV-007 · The known-hard fixture keeps its hard divergence

WHEN se ejecuta la divergencia sobre las lecturas prefabricadas del fixture
`evals/ambiguous-partial-effect`, el sistema DEBE seguir devolviendo una
divergencia dura en `side_effects`, porque el desacuerdo de ese fixture es
una contradicción y aflojar la regla hasta perderlo sería cambiar el
falso positivo por un falso negativo.

#### Scenario: The fixture still diverges hard
- **WHEN** se comparan las lecturas de `evals/ambiguous-partial-effect`
- **THEN** el resultado trae al menos una divergencia dura en `side_effects`

#### Scenario: The rule is general, not a special case
- **WHEN** se comparan dos efectos con la misma diferencia de alcance que el
  fixture pero con otras palabras y en otro proyecto
- **THEN** el resultado también trae una divergencia dura, porque la regla
  no reconoce el fixture ni por su ruta ni por sus cadenas

verifies:   tests/test_diff_readings.py
confidence: high
from:       evals/README.md
