# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-04-ci-gate/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 10
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 2 divergencias blandas sobre los 10 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 2

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: Triggers and job names read from disk

El lector A describe el efecto como «el workflow declara los triggers y los cinco jobs correctos»; el lector B describe el efecto como «el workflow declara los tres disparadores y los cinco jobs». Similitud de contenido 0.50, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Triggers and job names read from disk» es la correcta?**
- (A) «el workflow declara los triggers y los cinco jobs correctos»
- (B) «el workflow declara los tres disparadores y los cinco jobs»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: One change in verified with a red requirement fails the job

El lector A describe el efecto como «el paso oracle.py termina con código 1»; el lector B describe el efecto como «el paso oracle.py falla y el job se marca en rojo». Las dos lecturas no nombran las mismas cifras, así que no describen el mismo efecto.

**¿Cuál de estas lecturas del efecto de «One change in verified with a red requirement fails the job» es la correcta?**
- (A) «el paso oracle.py termina con código 1»
- (B) «el paso oracle.py falla y el job se marca en rojo»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 4

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-CI-001 — El requisito sólo exige que el workflow «declare» los cinco jobs y que `tests` «cubra» Python 3.12/3.13/3.14, y el escenario únicamente parsea nombres y disparadores desde disco: un job `tests` con matriz de tres versiones cuyo único paso sea `python3 --version` (o que lleve `continue-on-error: true`) cumple el requisito y pasa el escenario, dejando CI en verde permanente sobre una suite rota.
- **[high]** R-CI-004 — La plantilla de consumidor no tiene ningún disparador especificado: un `venoxia-gate.yml` que sólo se dispare en `workflow_dispatch` (o sobre una rama inexistente) cumple los tres escenarios —checkout fijado, dos pasos strict sin `|| true`, ningún `pip`— y jamás se ejecuta en un pull request, así que la puerta que da nombre al requisito nunca bloquea nada.
- **[high]** R-CI-005 — El `WHILE .venoxia/venoxia.json` deja el caso contrario libre: si el fichero no existe, el paso del oráculo se salta y el job queda verde; como `validate.py` y `charter_lint.py` también salen con 0 en un proyecto sin `.venoxia/`, borrar o renombrar ese directorio convierte todo el gate del consumidor en un no-op silencioso que nadie detecta.
- **[medium]** R-CI-004 — «Referencia fija (`VENOXIA_REF`)» se cumple con `VENOXIA_REF: main`, que es literalmente una referencia y satisface el escenario (el checkout usa `VENOXIA_REF` y `secrets.VENOXIA_TOKEN`): cada push a Venoxia cambia sin aviso el veredicto del gate de todos los consumidores, que es justo lo contrario de fijar la versión.

## Escenarios que convergen · 8

- Both strict commands read from the job
- plugin-validate installs before validating
- plugin-validate does not block the workflow
- evals only runs by hand
- evals needs the API key
- Pinned checkout of Venoxia
- Two strict gates that can fail
- No pip anywhere
