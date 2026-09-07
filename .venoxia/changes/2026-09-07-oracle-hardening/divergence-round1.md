# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-07-oracle-hardening/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 6
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 7 divergencias blandas sobre los 6 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 7

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Both flags in one invocation

El lector A describe el efecto como «el proceso termina sin ejecutar el runner»; el lector B describe el efecto como «el proceso termina con código de error de uso». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Both flags in one invocation» es la correcta?**
- (A) «el proceso termina sin ejecutar el runner»
- (B) «el proceso termina con código de error de uso»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Nothing is written under both flags

El lector A describe el efecto como «oracle.json sigue sin existir tras la invocación»; el lector B describe el efecto como «no se escribe ningún historial oracle.json». Similitud de contenido 0.22, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Nothing is written under both flags» es la correcta?**
- (A) «oracle.json sigue sin existir tras la invocación»
- (B) «no se escribe ningún historial oracle.json»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The usage error names both flags

El lector A describe el efecto como «stderr recibe un aviso que nombra ambas flags»; el lector B describe el efecto como «stderr muestra aviso nombrando --dry-run y --record». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The usage error names both flags» es la correcta?**
- (A) «stderr recibe un aviso que nombra ambas flags»
- (B) «stderr muestra aviso nombrando --dry-run y --record»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The original bytes survive in the copy

El lector A describe el efecto como «aparece una copia del oracle.json original»; el lector B describe el efecto como «se crea copia del oracle.json corrupto original». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The original bytes survive in the copy» es la correcta?**
- (A) «aparece una copia del oracle.json original»
- (B) «se crea copia del oracle.json corrupto original»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The warning names the copy

El lector B registra «se escribe oracle.json.corrupt-<marca>» y ningún otro lector lo recoge. Se han comparado «effect» y «side_effects» juntos, así que no es una diferencia de dónde colocó cada lector el mismo efecto. Ninguna otra lectura lo niega ni le pone otra cifra: nadie lo contradice en lo que se ha podido comprobar, así que sólo añade.

**¿Qué efectos observables debe producir «The warning names the copy»?**
- (A) «se escribe oracle.json.corrupt-<marca>»
- (B) Ninguno de esos efectos pertenece al escenario: sobran de la lectura

### Escenario: The warning names the copy

El lector A describe el efecto como «stderr recibe un aviso que nombra la ruta de la copia»; el lector B describe el efecto como «stderr muestra aviso con la ruta de la copia». Similitud de contenido 0.57, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The warning names the copy» es la correcta?**
- (A) «stderr recibe un aviso que nombra la ruta de la copia»
- (B) «stderr muestra aviso con la ruta de la copia»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No history, no copy

El lector A describe el efecto como «no aparece ningún fichero oracle.json.corrupt-<marca>»; el lector B describe el efecto como «no se crea ningún fichero de copia corrupta». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No history, no copy» es la correcta?**
- (A) «no aparece ningún fichero oracle.json.corrupt-<marca>»
- (B) «no se crea ningún fichero de copia corrupta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-ORC-011 — El requisito sólo prohíbe «escribir `oracle.json`» y el único escenario que lo observa se ejecuta sobre un change *sin* `oracle.json`; una implementación que abre el fichero de salida en modo escritura (truncándolo) al arrancar y sólo después detecta el conflicto de flags cumple los tres escenarios y sale con 2, pero deja vacío el historial de un change que sí lo tenía, destruyendo el run rojo previo que `/venoxia:verify` y V17 exigen para llegar a `verified`.
- **[high]** R-ORC-012 — El requisito exige copiar el original «antes de escribir el historial nuevo» pero no dice qué hacer si la copia no se puede escribir (permisos, disco lleno, nombre colisionado); una implementación que envuelve la copia en un try/except silencioso y continúa con el `--record` cumple los tres escenarios en el caso feliz y, en el caso de fallo, sobrescribe el `oracle.json` corrupto perdiendo para siempre los bytes originales, que era justo lo que el requisito venía a salvar.
- **[medium]** R-ORC-012 — Nada obliga a que `<marca>` sea única: usar una constante (`oracle.json.corrupt-old`) o una marca de segundo entero satisface los tres escenarios, pero una segunda corrupción sobrescribe la copia de la primera y el único rastro del historial original desaparece sin aviso.
