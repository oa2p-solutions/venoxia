# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-06-divergence-additive/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 11
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 7 divergencias blandas sobre los 11 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 7

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A purely added side effect is soft

El lector A describe el efecto como «clasifica la divergencia de efecto colateral como blanda»; el lector B describe el efecto como «el efecto añadido sin contraparte se clasifica blando». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A purely added side effect is soft» es la correcta?**
- (A) «clasifica la divergencia de efecto colateral como blanda»
- (B) «el efecto añadido sin contraparte se clasifica blando»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An opposite polarity is hard

El lector A describe el efecto como «clasifica la divergencia de efecto colateral como dura»; el lector B describe el efecto como «la negación contraria al otro efecto se clasifica dura». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An opposite polarity is hard» es la correcta?**
- (A) «clasifica la divergencia de efecto colateral como dura»
- (B) «la negación contraria al otro efecto se clasifica dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A different number is hard

El lector A describe el efecto como «clasifica la divergencia de efecto colateral como dura»; el lector B describe el efecto como «la cifra distinta entre lectores se clasifica dura». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A different number is hard» es la correcta?**
- (A) «clasifica la divergencia de efecto colateral como dura»
- (B) «la cifra distinta entre lectores se clasifica dura»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An unrelated added effect stays soft

El lector A describe el efecto como «clasifica la divergencia de efecto colateral como blanda»; el lector B describe el efecto como «efecto sin coincidencia ni por negación ni cifra se clasifica blando». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An unrelated added effect stays soft» es la correcta?**
- (A) «clasifica la divergencia de efecto colateral como blanda»
- (B) «efecto sin coincidencia ni por negación ni cifra se clasifica blando»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Strict mode still fails on an addition

El lector A describe el efecto como «la ejecución termina en fallo pese a ser sólo blanda»; el lector B describe el efecto como «la ejecución en modo estricto falla aunque la divergencia sea blanda». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Strict mode still fails on an addition» es la correcta?**
- (A) «la ejecución termina en fallo pese a ser sólo blanda»
- (B) «la ejecución en modo estricto falla aunque la divergencia sea blanda»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A contradiction the rule cannot see stays soft

El lector A describe el efecto como «clasifica como blanda una contradicción no detectable y la presenta al revisor»; el lector B describe el efecto como «contradicción sin negación ni cifra se clasifica blanda y se presenta». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A contradiction the rule cannot see stays soft» es la correcta?**
- (A) «clasifica como blanda una contradicción no detectable y la presenta al revisor»
- (B) «contradicción sin negación ni cifra se clasifica blanda y se presenta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The rule is general, not a special case

El lector A describe el efecto como «el resultado trae divergencia dura en otro proyecto con otras palabras»; el lector B describe el efecto como «el mismo desacuerdo con otras palabras y proyecto también resulta duro». Similitud de contenido 0.33, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The rule is general, not a special case» es la correcta?**
- (A) «el resultado trae divergencia dura en otro proyecto con otras palabras»
- (B) «el mismo desacuerdo con otras palabras y proyecto también resulta duro»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-DIV-005 — El escenario «A contradiction the rule cannot see stays soft» obliga a clasificar como blanda una contradicción real («se borra el borrador» vs «se conserva el borrador»), y ningún escenario fija el comportamiento sin `--strict`: una implementación literal termina en código 0 en la invocación por defecto, con lo que un change en el que un lector afirma que se destruye un dato y el otro que se conserva puede pasar a `validated` y abrir el guardián al código.
- **[medium]** R-DIV-005 — «Sólo añade» se evalúa contra el repertorio del otro lector sin exigir que ese repertorio contenga nada: si un lector devuelve `side_effects` vacío (porque no vio ninguno o porque falló), todos los efectos del otro lector «sólo añaden» y todas las divergencias de colaterales salen blandas, justo el caso en que el desacuerdo es máximo.
- **[medium]** R-DIV-007 — R-DIV-007 exige que el fixture siga siendo duro con una regla general que no lo reconozca por sus cadenas, y nada pone techo a la amplitud del detector de contradicción: una implementación que declare contradicción en cuanto dos efectos comparten palabras significativas cumple R-DIV-007 y los escenarios de R-DIV-005 (que sólo fijan dos casos sin solape léxico), y devuelve duras todas las diferencias de detalle («se reserva el stock» vs «se reserva el stock y se anota la reserva»), reinstaurando el falso positivo que este delta existe para eliminar y bloqueando changes correctos.

## Escenarios que convergen · 4

- A soft divergence is still reported
- A contradiction says so
- An addition says so
- The fixture still diverges hard
