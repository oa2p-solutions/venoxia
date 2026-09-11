# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-verify-confirm-green/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 25
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 15 divergencias blandas sobre los 25 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 15

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The confirmation lands in the recorded run

El lector A describe el efecto como «graba confirmed_green con ese ID en el run»; el lector B describe el efecto como «el último run guarda confirmed_green con ese ID». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The confirmation lands in the recorded run» es la correcta?**
- (A) «graba confirmed_green con ese ID en el run»
- (B) «el último run guarda confirmed_green con ese ID»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Several IDs separated by commas

El lector A describe el efecto como «graba ambos IDs en confirmed_green del run»; el lector B describe el efecto como «el último run guarda confirmed_green con los dos IDs». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Several IDs separated by commas» es la correcta?**
- (A) «graba ambos IDs en confirmed_green del run»
- (B) «el último run guarda confirmed_green con los dos IDs»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The output keeps its eight top-level keys

El lector A describe el efecto como «el JSON conserva exactamente las ocho claves de siempre»; el lector B describe el efecto como «el documento JSON conserva sus ocho claves de primer nivel». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The output keeps its eight top-level keys» es la correcta?**
- (A) «el JSON conserva exactamente las ocho claves de siempre»
- (B) «el documento JSON conserva sus ocho claves de primer nivel»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An ID outside the change is a usage error

El lector A describe el efecto como «termina en error de uso sin grabar nada»; el lector B describe el efecto como «el proceso termina en error de uso». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An ID outside the change is a usage error» es la correcta?**
- (A) «termina en error de uso sin grabar nada»
- (B) «el proceso termina en error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: An ID outside the change records nothing

El lector B registra «el directorio del change no gana ningún fichero» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «An ID outside the change records nothing»?**
- (A) «el directorio del change no gana ningún fichero»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: An ID that is not green in this run is a usage error

El lector A describe el efecto como «termina en error y oracle.json no gana ningún run»; el lector B describe el efecto como «termina en error de uso sin grabar ningún run». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «An ID that is not green in this run is a usage error» es la correcta?**
- (A) «termina en error y oracle.json no gana ningún run»
- (B) «termina en error de uso sin grabar ningún run»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Confirming without recording is a usage error

El lector A describe el efecto como «termina en error sin ejecutar ningún comando»; el lector B describe el efecto como «termina en error de uso sin ejecutar nada». Similitud de contenido 0.43, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Confirming without recording is a usage error» es la correcta?**
- (A) «termina en error sin ejecutar ningún comando»
- (B) «termina en error de uso sin ejecutar nada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A prior missing run is not a prior red run

El lector B registra «no escribe nada en change.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A prior missing run is not a prior red run»?**
- (A) «no escribe nada en change.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: A green run with no red run in the history

El lector B registra «no escribe nada en change.json» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A green run with no red run in the history»?**
- (A) «no escribe nada en change.json»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The user confirms and the confirmation is recorded

El lector B registra «se ejecuta --record --confirm-green nombrando ese requisito» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The user confirms and the confirmation is recorded»?**
- (A) «se ejecuta --record --confirm-green nombrando ese requisito»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The user confirms and the confirmation is recorded

El lector A describe el efecto como «la skill regraba el oráculo con confirm-green»; el lector B describe el efecto como «la skill graba de nuevo el oráculo con confirm-green». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The user confirms and the confirmation is recorded» es la correcta?**
- (A) «la skill regraba el oráculo con confirm-green»
- (B) «la skill graba de nuevo el oráculo con confirm-green»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The confirmation names only the IDs the user confirmed

El lector B registra «se graba confirm-green con un único ID» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The confirmation names only the IDs the user confirmed»?**
- (A) «se graba confirm-green con un único ID»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: No confirmation is recorded before asking

El lector A describe el efecto como «la skill no pasa confirm-green en ninguna grabación»; el lector B describe el efecto como «la skill no usa confirm-green antes de preguntar». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No confirmation is recorded before asking» es la correcta?**
- (A) «la skill no pasa confirm-green en ninguna grabación»
- (B) «la skill no usa confirm-green antes de preguntar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A confirmation already in the history is enough

El lector B registra «no se pregunta al usuario» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «A confirmation already in the history is enough»?**
- (A) «no se pregunta al usuario»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: One warning per requirement, never one per change

El lector A describe el efecto como «V18 se dispara una vez, nombrando el sin rojo previo»; el lector B describe el efecto como «V18 se dispara una sola vez nombrando ese requisito». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One warning per requirement, never one per change» es la correcta?**
- (A) «V18 se dispara una vez, nombrando el sin rojo previo»
- (B) «V18 se dispara una sola vez nombrando ese requisito»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-017 — R-ORC-017 sólo rechaza IDs que no pertenecen al change o que no salen en `green`: un `oracle.py --record --confirm-green R-A,R-B,R-C` como primerísima ejecución del change es legal y graba un historial de un único run, todo verde y todo confirmado. Con eso V18 calla y R-ORC-010 escribe `verified` sin que nadie haya visto fallar jamás un test; la prohibición «nunca como primera grabación del change» ata a la skill, no al script, y el script es justo lo que un agente puede invocar directamente.
- **[high]** R-ORC-010 — La confirmación grabada no caduca ni queda atada al test que se ejecutó (sólo es un ID en una lista de un run pasado): confirmado R-X una vez, se puede después vaciar su test o apuntar su `verifies:` a otro fichero, y el escenario «A confirmation already in the history is enough» obliga a escribir `verified` sin volver a preguntar, con V18 callado para siempre. El change queda verificado sobre un test que nunca se demostró capaz de fallar.
- **[medium]** R-ORC-017 — «cualquier otro estado es un error de uso, código 2, que no graba nada» permite tirar el run entero: si al re-grabar con `--confirm-green R-A` otro requisito del change sale en `red` o `timeout`, el proceso sale con 2 y `oracle.json` no gana ningún run, perdiendo precisamente el rojo que habría acreditado a ese otro requisito por la vía legítima, además de la confirmación recién obtenida del usuario.

## Escenarios que convergen · 11

- A run without the flag carries no confirmation
- A green run backed by a documented red run
- The recorded confirmation unlocks verified
- The user does not confirm
- A red run never writes verified
- Red preceded the green
- The only run is already green
- Every run has always been green
- A confirmed green is silent
- A confirmation covers only the IDs it names
- The confirmation may live in an earlier run
