# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-14-charter-bets-warning/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 3
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 3 divergencias blandas sobre los 3 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: A charter without a single bet

El lector A describe el efecto como «marca hallazgo C20 sobre la línea de la sección»; el lector B describe el efecto como «el linter reporta el hallazgo C20 sobre la sección de apuestas». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A charter without a single bet» es la correcta?**
- (A) «marca hallazgo C20 sobre la línea de la sección»
- (B) «el linter reporta el hallazgo C20 sobre la sección de apuestas»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: A high risk row keeps its own warning

El lector A describe el efecto como «no marca C20 en esa sección»; el lector B describe el efecto como «el linter no reporta C20 pese a la sección vacía». Similitud de contenido 0.38, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «A high risk row keeps its own warning» es la correcta?**
- (A) «no marca C20 en esa sección»
- (B) «el linter no reporta C20 pese a la sección vacía»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One bet is enough

El lector A describe el efecto como «no marca C20 en esa sección»; el lector B describe el efecto como «el linter no reporta C20 con una apuesta declarada». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «One bet is enough» es la correcta?**
- (A) «no marca C20 en esa sección»
- (B) «el linter no reporta C20 con una apuesta declarada»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 2

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[medium]** R-CHL-008 — La excepción «salvo que alguna capability declare riesgo alto» es global y sin cuota: una implementación que apaga C20 en cuanto existe una sola fila de riesgo alto en todo el acta deja sin aviso precisamente al acta más arriesgada del proyecto, y convierte marcar cualquier capability como riesgo alto en un interruptor permanente para silenciar el aviso de apuestas vacías.
- **[medium]** R-CHL-008 — El requisito sólo dispara cuando el acta «declara su sección de apuestas»; una implementación que no marca nada cuando la sección no existe cumple los tres escenarios, de modo que la forma más barata de quitarse el aviso es borrar el encabezado: el acta queda sin ninguna apuesta escrita y pasa `charter_lint --strict` en verde, que es peor que la sección vacía que el requisito quería señalar.
