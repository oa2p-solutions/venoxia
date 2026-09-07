# divergence Delta

## ADDED Requirements

### R-DIV-011 · Style quantifiers and subordinate negations do not make a divergence hard

WHEN dos lectores registran sobre el mismo escenario dos efectos con el mismo
sujeto, el sistema DEBE dejar fuera de la señal de polaridad la diferencia
entre «ambos» y «ambas», la negación que va dentro de una subordinada cuando
sólo uno de los dos efectos trae esa subordinada, y la negación de un
predicado que el otro efecto no repite, de modo que ninguna de esas tres
diferencias haga dura la divergencia por sí sola.

#### Scenario: Gender variants of the same quantifier
- **WHEN** un lector registra «stderr nombra ambas flags» y el otro «stderr
  nombra ambos flags»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: A negation deep inside a subordinate clause
- **WHEN** un lector registra «mensaje en stderr indicando que no se grabó el
  run» y el otro «stderr avisa de que el run no se ha grabado»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: A condition dragged into one effect only
- **WHEN** un lector registra «un oráculo que no termina en verde deja el job
  en fallo» y el otro «el job queda en fallo»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: A negation against a different verb
- **WHEN** un lector registra «oracle.json no se modifica» y el otro
  «oracle.json conserva su contenido byte a byte»
- **THEN** esa diferencia no hace dura la divergencia

#### Scenario: A negated condition against an affirmed one
- **WHEN** un lector registra «deniega cuando el change no está validado» y el
  otro «deniega cuando el change está validado»
- **THEN** esa diferencia hace dura la divergencia

#### Scenario: A plain negation still contradicts
- **WHEN** un lector registra «se crea el presupuesto» y el otro «no se crea
  el presupuesto»
- **THEN** esa diferencia hace dura la divergencia

verifies:   tests/test_diff_readings.py
confidence: medium
  why:      la señal de polaridad lleva cinco falsos positivos y cero aciertos sobre prosa real; se conserva por el caso flagrante
  revisit:  cuando la clave signal acumule veinte duras de polaridad sobre deltas reales y se pueda contar cuántas fueron desacuerdos de verdad
from:       README.md#cómo-se-usa
