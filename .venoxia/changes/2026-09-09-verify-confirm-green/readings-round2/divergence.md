# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-verify-confirm-green/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 24
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 13 divergencias duras, 6 blandas y 0 lagunas declaradas sobre los 24 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 13

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: The confirmation lands in the recorded run

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The confirmation lands in the recorded run»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: Several IDs separated by commas

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «Several IDs separated by commas»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: The output keeps its eight top-level keys

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The output keeps its eight top-level keys»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: A run without the flag carries no confirmation

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «A run without the flag carries no confirmation»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

### Escenario: A green run backed by a documented red run

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «A green run backed by a documented red run» de este delta?**
- (A) Sí, y su efecto es «change.json pasa a estado verified» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: A green run with no red run in the history

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «A green run with no red run in the history» de este delta?**
- (A) Sí, y su efecto es «la skill pregunta al usuario sin escribir nada» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: The user confirms and the confirmation is recorded

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «The user confirms and the confirmation is recorded» de este delta?**
- (A) Sí, y su efecto es «la skill vuelve a grabar el oráculo confirmando ese requisito» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: The confirmation names only the IDs the user confirmed

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «The confirmation names only the IDs the user confirmed» de este delta?**
- (A) Sí, y su efecto es «confirm-green nombra sólo el requisito que el usuario confirmó» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: No confirmation is recorded before asking

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «No confirmation is recorded before asking» de este delta?**
- (A) Sí, y su efecto es «ninguna grabación lleva todavía confirm-green» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: The recorded confirmation unlocks verified

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «The recorded confirmation unlocks verified» de este delta?**
- (A) Sí, y su efecto es «change.json pasa a estado verified» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: A confirmation already in the history is enough

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «A confirmation already in the history is enough» de este delta?**
- (A) Sí, y su efecto es «change.json pasa a verified sin volver a preguntar» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: The user does not confirm

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «The user does not confirm» de este delta?**
- (A) Sí, y su efecto es «change.json no cambia» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

### Escenario: A red run never writes verified

El lector B lee este escenario en el delta; el lector A no lo encuentra.

**¿Forma parte «A red run never writes verified» de este delta?**
- (A) Sí, y su efecto es «change.json no cambia sea cual sea su estado» (lectura de B)
- (B) No, el delta no describe ese escenario y sobra en las lecturas que lo traen

## Divergencias blandas · 6

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The confirmation lands in the recorded run

El lector A describe el efecto como «confirmed_green queda con ese ID en el run»; el lector B describe el efecto como «el último run de oracle.json trae confirmed_green con ese ID». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The confirmation lands in the recorded run» es la correcta?**
- (A) «confirmed_green queda con ese ID en el run»
- (B) «el último run de oracle.json trae confirmed_green con ese ID»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The output keeps its eight top-level keys

El lector A registra «se graba el run con confirmed_green en oracle.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The output keeps its eight top-level keys»?**
- (A) «se graba el run con confirmed_green en oracle.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A run without the flag carries no confirmation

El lector A registra «se graba el run en oracle.json sin confirmed_green» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A run without the flag carries no confirmation»?**
- (A) «se graba el run en oracle.json sin confirmed_green»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A run without the flag carries no confirmation

El lector A describe el efecto como «el run grabado no trae la clave confirmed_green»; el lector B describe el efecto como «el último run no tiene la clave confirmed_green». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A run without the flag carries no confirmation» es la correcta?**
- (A) «el run grabado no trae la clave confirmed_green»
- (B) «el último run no tiene la clave confirmed_green»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An ID outside the change is a usage error

El lector A describe el efecto como «termina en error de uso, no confirma nada»; el lector B describe el efecto como «el proceso termina con error de uso». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An ID outside the change is a usage error» es la correcta?**
- (A) «termina en error de uso, no confirma nada»
- (B) «el proceso termina con error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An ID that is not green in this run is a usage error

El lector A describe el efecto como «termina en error, oracle.json no gana ningún run»; el lector B describe el efecto como «termina en error y no añade ningún run». Similitud de contenido 0.56, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An ID that is not green in this run is a usage error» es la correcta?**
- (A) «termina en error, oracle.json no gana ningún run»
- (B) «termina en error y no añade ningún run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-017 — R-ORC-017 acepta `--record --confirm-green <IDs>` de cualquier invocador sin exigir ni registrar prueba alguna de que se preguntó: el run sólo guarda la lista de IDs, no la pregunta ni la respuesta ni quién contestó. Cualquier agente que escriba el código puede ejecutar `oracle.py --record --confirm-green R-X,R-Y,...` con todos los IDs verdes, silenciar V18 y dejar el historial listo para `verified` sin que ningún humano haya visto fallar nada, y sin que quede rastro auditable que lo distinga de una confirmación legítima.
- **[high]** R-ORC-010 — R-ORC-010 acepta un run anterior en `missing` como equivalente al rojo previo: basta grabar un run antes de crear el fichero de test (todo `missing`, que es el estado normal justo tras `specify`) y luego escribir un test que pase siempre para que el change llegue a `verified` sin que ningún test haya fallado nunca. El sello `verified` pasa a significar «existió un momento en que el fichero no existía», no «el test detecta la ausencia del comportamiento».
- **[medium]** R-VAL-007 — Ni R-ORC-010 («figura en `confirmed_green` de algún run anterior → `verified` sin volver a preguntar») ni R-VAL-007 («ningún run del historial lo traiga en su lista `confirmed_green`») atan la confirmación al contenido del test que se confirmó ni la caducan. Una sola confirmación deja ese requisito bendecido para siempre: se puede vaciar el test a `assert True` y todos los runs verdes posteriores siguen pasando a `verified` y sin aviso V18, sin que nadie vuelva a preguntar.
- **[medium]** R-VAL-007 — R-ORC-010 desbloquea `verified` con un run previo en `red` **o** `missing`, pero R-VAL-007 sólo calla V18 con un `red` previo o un `confirmed_green`. Un change verificado por la vía `missing` queda en `verified` arrastrando un aviso V18 permanente que el flujo no puede limpiar: la skill sólo pregunta cuando no hay «ni lo uno ni lo otro», y con `missing` sí lo hay, así que nunca pregunta ni graba confirmación. En `--strict` ese change válido falla la puerta para siempre.

## Escenarios que convergen · 9

- An ID outside the change records nothing
- Confirming without recording is a usage error
- Red preceded the green
- The only run is already green
- Every run has always been green
- One warning per requirement, never one per change
- A confirmed green is silent
- A confirmation covers only the IDs it names
- The confirmation may live in an earlier run
