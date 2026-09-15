## ADDED Requirements

### R-CHK-011 · Quote amounts in a currency without subunit

WHEN se carga un presupuesto en pesos chilenos cuyo importe viene escrito con
separadores de miles y una cola decimal o un guion de cierre, el sistema registra
el importe como entero en CLP y acepta el presupuesto.

#### Scenario: Amount written with a comma decimal tail
- **WHEN** el importe del presupuesto viene escrito como «1.468.135,00»
- **THEN** el presupuesto se acepta con el importe registrado en CLP

#### Scenario: Amount written with a dot decimal tail
- **WHEN** el importe del presupuesto viene escrito como «1.468.135.00»
- **THEN** el presupuesto se acepta con el importe registrado en CLP

#### Scenario: Amount written in the Chilean closing-dash notation
- **WHEN** el importe del presupuesto viene escrito como «$ 1.500.000.-»
- **THEN** el presupuesto se acepta con el importe registrado en CLP

verifies:   test/checkout/quote-amounts.spec.ts
confidence: medium
  why:      el PR/FAQ dice «se acepta» sin decir qué entero queda registrado ni con qué respuesta
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
