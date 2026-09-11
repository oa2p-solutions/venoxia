# 2026-09-09-technical-contract Proposal

## Why

Venoxia obliga a que cada comportamiento del sistema nazca con su oráculo, y
no aplica esa regla a las decisiones técnicas de su propio repositorio. Viven
como prosa en `.venoxia/principles.md`, sin nada que falle cuando dejan de ser
verdad, y una ya miente: dice «probado con 3.14» cuando la matriz real es
3.12–3.14. La premisa que sostiene todo veredicto del plugin —«ningún script
consulta a un modelo»— no tiene ningún test que la defienda. Y sus oráculos
reales existen sin que nadie los reclame: `tools/coverage.py` corre en la
puerta local sin que ningún requisito lo nombre, y hay tests que comprueban
los imports del guardián y el esquema del informe sin `@covers`. La
conversación de visión del 2026-09-08 fijó que el eje técnico es parte del
contrato (D4): un requisito técnico es un requisito EARS con `verifies:`,
igual que los demás, y lo que no tiene oráculo posible no es un requisito,
sino una apuesta del acta o un principio de arbitraje (D5, D6).

## What Changes

- Nace la capability `technical-contract` (prefijo `R-TEC-`, fila 7 del acta):
  el sujeto de sus requisitos es el repositorio.
- Seis decisiones técnicas pasan de prosa a requisito con oráculo: sólo
  biblioteca estándar en `scripts/`, `tools/` y `tests/`; ningún módulo de red
  ni cliente de modelo en `scripts/`; el guardián no importa nada compartido;
  cada script por encima de su umbral de cobertura, con `tools/coverage.py`
  como runner con nombre; los cinco CLI comparten los códigos de salida
  `0`/`1`/`2`; y el esquema de informe versión 1 sólo crece.
- `tools/check.py` pierde su paso `coverage`: el gate ya ejecuta
  `tools/coverage.py` como runner de `R-TEC-004`, y correrlo dos veces son
  dos minutos por push (D8). `R-CI-019` pasa a tres pasos.
- `.venoxia/principles.md` se reduce a los tres principios del método y a los
  principios de arbitraje: lo verificable vive ahora en `technical-contract`,
  y la sección «Convenciones técnicas» desaparece (D5).
- El acta gana la fila 7 y revisa tres apuestas: `B-002` y `B-003` quedan
  resueltas (la cobertura con `trace` funciona y la matriz pasa en los tres
  contenedores de la puerta local), `B-004` se reescribe sobre la puerta local
  porque el job de CI al que se refería ya no existe.

## Capabilities

### New Capabilities

- `technical-contract`: las decisiones técnicas verificables del repositorio
  —imports, red, aislamiento del guardián, cobertura, códigos de salida,
  esquema de informe— como requisitos con oráculo.

### Modified Capabilities

- `ci`: `R-CI-019` pasa de cuatro pasos a tres (`matrix`, `gate`,
  `plugin-validate`); la cobertura sigue corriendo, dentro del gate.

## Impact

- `.venoxia/venoxia.json` declara `runners.coverage`: es el primer uso real
  de los runners con nombre de `2026-09-09-oracle-named-runners`.
- Cuatro requisitos nacen en verde sin rojo previo (`R-TEC-001`, `002`,
  `003`, `004` y `006`: los imports ya son stdlib, la cobertura ya supera su
  umbral, y los tests del guardián y del informe ya existen). `V18` avisará y
  `/venoxia:verify` pedirá confirmación: es adopción retroactiva, aceptada
  explícitamente en D12, como hizo `adopt-venoxia`. Sólo `R-TEC-005` y la
  modificación de `R-CI-019` nacen en rojo.
- `tests/test_check.py` cambia de expectativa (`STEP_NAMES` pasa a tres) y
  `tests/test_guardian.py`, `tests/test_report.py` y `tools/coverage.py`
  ganan un `@covers` cada uno.
- `CLAUDE.md` deja de enumerar las convenciones técnicas como prosa propia y
  remite a la capability; el README menciona la capability en la sección de
  principios.
- Límite conocido (D8): un change `archived` deja de ejecutarse en `gate.py`,
  así que los requisitos técnicos viven en este change y se consolidarán
  cuando haya consolidación automática, que sigue fuera de alcance del acta.
  El abogado del diablo lo señaló sobre `R-CI-019`: al archivar este change la
  cobertura dejaría de correr en cada push. Por eso **este change no se
  archiva** mientras no exista una consolidación que conserve su oráculo.
- Decisiones del usuario (2026-09-09) ante el abogado del diablo: sólo
  `oracle.py` y `gate.py` pueden importar `subprocess` (`R-TEC-002`), y el
  guardián importa sólo la biblioteca estándar (`R-TEC-003`), no una lista de
  nombres prohibidos. En la segunda ronda el abogado señaló que `os.system`,
  `os.popen` y `os.exec*` esquivan esa prohibición; se cerró bajo la misma
  decisión (ningún script lanza procesos por `os`; hoy ninguno lo hace), y
  queda señalado para que el usuario lo vete si no lo comparte.
- Límites declarados tras la tercera ronda del abogado: una lista de módulos
  prohibidos es un suelo, no una prueba (`asyncio`, `selectors`, `pty`,
  `multiprocessing` u `os.fork` quedan fuera de la lista; ampliarla es una
  decisión del usuario pendiente); el fichero de umbrales de cobertura es
  parte del repo y se revisa como código, así que bajar un umbral a mano es
  visible en el diff y no lo impide `R-TEC-004`; y copiar código ajeno dentro
  de `scripts/` no lo detecta `R-TEC-001`, porque «cero dependencias» significa
  nada que instalar. Y una decisión de código: `build_payload` no deja que una
  clave extra sobrescriba una del esquema (`R-TEC-006`). Límite que queda: el oráculo ejecuta el comando que el
  proyecto declara, y un análisis estático no puede saber qué hace ese comando;
  es el mismo límite que el README ya declara para `test_command`.
- Decisiones de Claude ante los ataques `medium`: una llamada a
  `importlib.import_module` o `__import__` en `scripts/` o `tools/` cuenta como
  import (`R-TEC-001`; `tests/` queda fuera porque carga módulos del propio
  repo por ruta), y un fichero medido sin entrada en el fichero de umbrales se
  exige al suelo del núcleo, `85`, en vez de a su propia medida (`R-TEC-004`;
  la constante ya existía y las entradas existentes no cambian).

## Confidence

- **Sólo stdlib, también en `tests/`** · `high` · es la convención que el repo
  opera desde el primer día y la suite ya la cumple; ampliarla a `tests/` es
  lo que convierte «`pytest` nunca es un requisito» en algo que falla si deja
  de ser verdad.
- **La lista de módulos de red prohibidos** · `high` · son los de la stdlib
  que abren conexiones; un cliente de modelo cae además bajo `R-TEC-001` por
  no ser stdlib, y se nombra igual porque es la premisa que se protege.
- **`tools/check.py` pierde `coverage` en este mismo change** · `high` ·
  decisión D8 cerrada en el plan; el gate ejecuta el runner y la puerta local
  no lo repite.
- **Cerrar `B-002` y `B-003` y reescribir `B-004`** · `medium` · el hecho que
  resolvía cada una ha ocurrido o ya no puede ocurrir; el acta no tiene
  convención de «apuesta resuelta», así que suben a `high` con el hecho en
  `why:` y conservan su ID · se revisa si el usuario prefiere retirarlas del
  acta en vez de conservarlas resueltas.
- **El resto de la propuesta** · `high` · decisiones D4, D5, D6, D8, D11 y D12
  del plan, cerradas con el usuario.
