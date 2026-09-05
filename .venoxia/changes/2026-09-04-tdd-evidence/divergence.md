# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-04-tdd-evidence/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 9
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 2 divergencias blandas sobre los 9 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 2

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Verified with a green run that forgot a requirement

El lector A describe el efecto como «V17 se dispara nombrando el ID nunca visto por el run»; el lector B describe el efecto como «V17 se dispara nombrando el requisito que el run nunca vio». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Verified with a green run that forgot a requirement» es la correcta?**
- (A) «V17 se dispara nombrando el ID nunca visto por el run»
- (B) «V17 se dispara nombrando el requisito que el run nunca vio»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Red preceded the green

El lector A describe el efecto como «el validador no marca ningún hallazgo V18 para ese requisito»; el lector B describe el efecto como «V18 no se dispara para ese requisito». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Red preceded the green» es la correcta?**
- (A) «el validador no marca ningún hallazgo V18 para ese requisito»
- (B) «V18 no se dispara para ese requisito»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-VAL-006 — El requisito condiciona la aceptación a que «el último run tenga `all_green: true`» y a que cubra los IDs; una implementación que lee sólo ese booleano y nunca contrasta los estados individuales acepta un `oracle.json` con `all_green: true` y todos sus requisitos en `red`/`timeout`, y pasa igual el escenario del run rojo porque allí el fichero trae `all_green: false`. Resultado: un change queda `verified` con la suite entera en rojo, que es exactamente lo que V17 existe para impedir.
- **[medium]** R-VAL-006 — Nada exige que el run verde sea posterior al contenido actual del delta ni de los tests: basta con que los `requirement_id` coincidan. Reescribir por completo el cuerpo de un requisito y su test conservando el ID deja V17 en silencio y el change en `verified` sobre una ejecución vieja que nunca vio ese código, convirtiendo el sello de evidencia TDD en una firma caducada e invisible.
- **[medium]** R-VAL-006 — El requisito no fija severidad para V17 y ningún escenario observa el código de salida: sólo comprueban que «`V17` se dispara». Emitir V17 como `warning` (como V18, que sí lo dice) cumple los cuatro escenarios y deja `validate.py` saliendo con 0, de modo que un change en `verified` sin `oracle.json` o con oracle corrupto no rechaza nada pese al «DEBE rechazar la especificación».

## Escenarios que convergen · 7

- Verified with a green run that covers every requirement
- Verified with no oracle.json at all
- Verified with a red run
- A corrupt oracle.json does not crash the validator
- The only run is already green
- Every run has always been green
- One warning per requirement, never one per change
