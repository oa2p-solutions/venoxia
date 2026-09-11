# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-charter-technical-axis/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 10
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 7 divergencias blandas sobre los 10 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 7

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: An approved convention is a requirement of technical-contract

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el texto declara que la convención aprobada es requisito». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An approved convention is a requirement of technical-contract» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el texto declara que la convención aprobada es requisito»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An undecided convention is a bet

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el texto declara que la convención sin decidir es apuesta». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An undecided convention is a bet» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el texto declara que la convención sin decidir es apuesta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The principles file carries no technical conventions

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el texto declara que principles.md no lleva convenciones técnicas». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The principles file carries no technical conventions» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el texto declara que principles.md no lleva convenciones técnicas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The delivery hands the approved conventions to specify

El lector A describe el efecto como «el texto de la skill declara que termina llamando a specify»; el lector B describe el efecto como «el texto declara que la entrega termina invocando specify de technical-contract». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The delivery hands the approved conventions to specify» es la correcta?**
- (A) «el texto de la skill declara que termina llamando a specify»
- (B) «el texto declara que la entrega termina invocando specify de technical-contract»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body names the two destinations

El lector A describe el efecto como «el texto de la skill declara los dos destinos posibles»; el lector B describe el efecto como «el texto declara que el juicio va a contract o a bets». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body names the two destinations» es la correcta?**
- (A) «el texto de la skill declara los dos destinos posibles»
- (B) «el texto declara que el juicio va a contract o a bets»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body forbids prose

El lector A describe el efecto como «el texto de la skill prohíbe escribirlo como prosa»; el lector B describe el efecto como «el texto declara que el juicio nunca va a prosa». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body forbids prose» es la correcta?**
- (A) «el texto de la skill prohíbe escribirlo como prosa»
- (B) «el texto declara que el juicio nunca va a prosa»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A bet only when no test can check it today

El lector A describe el efecto como «el texto de la skill declara la condición de apuesta»; el lector B describe el efecto como «el texto declara que sólo es apuesta sin test posible hoy». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A bet only when no test can check it today» es la correcta?**
- (A) «el texto de la skill declara la condición de apuesta»
- (B) «el texto declara que sólo es apuesta sin test posible hoy»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-007 — R-CHL-007 dice que un juicio técnico «sólo es apuesta cuando hoy no existe ningún test que pueda comprobarlo»; como en el ciclo de Venoxia el test se escribe después de `/venoxia:specify`, en el momento en que la skill clasifica nunca existe todavía un test para el juicio nuevo, así que una implementación literal manda todos los juicios técnicos a `## Bets` y ninguno a un requisito con `verifies:`. Los cuatro escenarios siguen en verde (sólo comprueban frases del cuerpo) y el eje técnico queda entero fuera del contrato verificable, que es justo lo que el change pretendía evitar.
- **[medium]** R-CHL-006 — R-CHL-006 obliga a escribir `principles.md` «sólo con los tres principios del método y los de dominio» y sólo protege de la pérdida a «las convenciones técnicas que ese fichero ya traiga»; una implementación literal reescribe el fichero desde cero y borra sin reubicar nada que no encaje en esas categorías —por ejemplo la convención de lectura «tags e identificadores en inglés, prosa en español» del propio repo, que `charter_lint` C17 lee—, dejando el acta gobernada por un principles.md amputado y sin rastro de lo eliminado.
- **[medium]** R-CHL-006 — R-CHL-006 cierra la entrega con «el `/venoxia:specify` tecleado», y el escenario correspondiente sólo exige que el cuerpo declare que la entrega termina ahí; una implementación literal añade la fila de la convención aprobada a la tabla del acta, imprime el comando y termina, sin comprobar que los requisitos lleguen a existir. El resultado es un acta que afirma convenciones aprobadas sin ningún requisito con `verifies:` detrás: exactamente la prosa no gobernada que el requisito prohíbe.

## Escenarios que convergen · 3

- The technical conventions heading is gone
- Existing conventions are moved, not dropped
- The inventory includes the technical contract
