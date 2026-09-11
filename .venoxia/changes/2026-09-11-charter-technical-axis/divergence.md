# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-charter-technical-axis/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 10
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 8 divergencias blandas sobre los 10 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 8

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: An approved convention is a requirement of technical-contract

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el cuerpo de SKILL.md declara la convención aprobada como requisito». Similitud de contenido 0.17, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An approved convention is a requirement of technical-contract» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el cuerpo de SKILL.md declara la convención aprobada como requisito»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An undecided convention is a bet

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el cuerpo de SKILL.md declara la convención sin decidir como apuesta». Similitud de contenido 0.17, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An undecided convention is a bet» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el cuerpo de SKILL.md declara la convención sin decidir como apuesta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The principles file carries no technical conventions

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el cuerpo de SKILL.md declara que principles.md no lleva convenciones técnicas». Similitud de contenido 0.23, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The principles file carries no technical conventions» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el cuerpo de SKILL.md declara que principles.md no lleva convenciones técnicas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Existing conventions are moved, not dropped

El lector A describe el efecto como «el texto de la skill declara la regla, no ejecuta nada»; el lector B describe el efecto como «el cuerpo declara que las convenciones se reparten antes de quitar la sección». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Existing conventions are moved, not dropped» es la correcta?**
- (A) «el texto de la skill declara la regla, no ejecuta nada»
- (B) «el cuerpo declara que las convenciones se reparten antes de quitar la sección»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The delivery hands the approved conventions to specify

El lector A describe el efecto como «el texto de la skill declara que la entrega llama a specify»; el lector B describe el efecto como «el cuerpo declara que la entrega termina invocando specify de technical-contract». Similitud de contenido 0.27, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The delivery hands the approved conventions to specify» es la correcta?**
- (A) «el texto de la skill declara que la entrega llama a specify»
- (B) «el cuerpo declara que la entrega termina invocando specify de technical-contract»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body names the two destinations

El lector A describe el efecto como «el texto de la skill declara los dos destinos posibles»; el lector B describe el efecto como «el cuerpo declara que el juicio sin principio va al contrato o a Bets». Similitud de contenido 0.08, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body names the two destinations» es la correcta?**
- (A) «el texto de la skill declara los dos destinos posibles»
- (B) «el cuerpo declara que el juicio sin principio va al contrato o a Bets»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The body forbids prose

El lector A describe el efecto como «el texto de la skill prohíbe escribirlo como prosa»; el lector B describe el efecto como «el cuerpo declara que ese juicio técnico nunca va a prosa». Similitud de contenido 0.09, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body forbids prose» es la correcta?**
- (A) «el texto de la skill prohíbe escribirlo como prosa»
- (B) «el cuerpo declara que ese juicio técnico nunca va a prosa»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A bet only when no test could check it

El lector A describe el efecto como «el texto de la skill declara ese criterio de apuesta»; el lector B describe el efecto como «el cuerpo declara que sólo es apuesta si ningún test lo comprobaría». Similitud de contenido 0.20, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A bet only when no test could check it» es la correcta?**
- (A) «el texto de la skill declara ese criterio de apuesta»
- (B) «el cuerpo declara que sólo es apuesta si ningún test lo comprobaría»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CHL-006 — «DEBE escribir `principles.md` sólo con los tres principios del método y los de dominio» y la cláusula de no perder nada cubre únicamente las convenciones técnicas: una implementación reescribe el fichero entero descartando cualquier otro contenido que el usuario tuviera allí (notas, glosario, principios no clasificados como de dominio) y el escenario de migración sigue en verde porque las convenciones técnicas sí se repartieron.
- **[medium]** R-CHL-006 — Los seis escenarios sólo observan que el cuerpo de `skills/charter/SKILL.md` «declara» cosas y que no aparece el literal `## Convenciones técnicas`: una skill que añade un párrafo declarativo al final y mantiene en su procedimiento el paso de volcar las convenciones a `principles.md` bajo otro encabezado (`## Convenciones del proyecto`) pasa las seis y deja las decisiones técnicas exactamente donde el change pretendía sacarlas, con instrucciones contradictorias dentro de la misma skill.
- **[medium]** R-CHL-006 — «Repartiendo igual… sin perder ninguna» no exige conservar el estado de decisión: la skill puede mandar todas las convenciones técnicas preexistentes de `principles.md` a `## Bets` (ninguna fue «aprobada» en esta entrevista), con lo que decisiones que ya gobernaban el proyecto pierden fuerza normativa, no llegan nunca a `technical-contract` y quedan como apuestas abiertas que nadie tiene que cerrar.
- **[medium]** R-CHL-007 — «Llevarlo a un requisito de `technical-contract` con `verifies:`» no dice a través de qué change ni en qué estado: `/venoxia:specify` puede escribir el requisito directamente en `.venoxia/capabilities/technical-contract/spec.md`, saltándose el ciclo draft→specified→validated→verified; como el test declarado en `verifies:` aún no existe, la capability queda en rojo permanente por V07/V08 sin ningún change activo que pueda arreglarlo y `gate.py`, que es fail-closed, bloquea el proyecto entero.

## Escenarios que convergen · 2

- The technical conventions heading is gone
- The inventory includes the technical contract
