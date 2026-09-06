# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repo

Venoxia es un **plugin de Claude Code** (no una librería ni una app) que convierte la especificación en un contrato verificable: cada requisito nace con `verifies:` (ruta del test que lo resuelve) y `confidence:`, y un validador determinista lo rechaza si falta cualquiera de los dos. El plugin se compone de skills (`skills/*/SKILL.md`), agentes (`agents/*.md`), un hook `PreToolUse` (`hooks/hooks.json` → `scripts/guardian.py`) y scripts Python que son la única lógica ejecutable.

Convenciones fijas de todo el repo:

- **Python 3 stdlib, cero dependencias.** Ni pip, ni venv, ni pytest (aunque pytest ejecuta la suite igual). Probado con 3.14.
- **Tags, claves e identificadores en inglés; prosa, valores y mensajes en español.** Aplica a código, docs, skills, plantillas y mensajes de error.
- **Ningún script consulta a un modelo.** La aritmética de todos los veredictos está en código; las skills sólo envuelven y presentan.
- **Ningún campo puede pedir un valor que el modelo tenga que inventar.** Por eso `revisit:` es «el hecho que resuelve la apuesta», nunca una fecha (V10/C12 rechazan fechas).
- El plugin se carga desde `~/.claude-b2bcarts/skills/venoxia` como symlink a este repo: se edita aquí sin reinstalar.

## Comandos

```bash
# Suite completa (735 tests, ~30 s). unittest de la stdlib, sin -t .
python3 -m unittest discover -s tests -q

# Un fichero, una clase, un test. El import cualificado tests.venoxia_fixtures exige lanzarlo desde la raíz.
python3 -m unittest tests.test_rules_late -v
python3 -m unittest tests.test_guardian.GuardianDecisionPathsTest -v
python3 -m unittest tests.test_rules_early.TestRuleV06Oracle.test_v06_fails_when_verifies_is_absent

# Estructura del plugin (manifiesto, frontmatter de skills/agentes, hook)
claude plugin validate . --strict

# Evals (usan LLM, cuestan tokens). --allow-tools no es opcional: sin él fallan por permisos.
claude plugin eval venoxia --ablation with-without --allow-tools 'Bash(python3 *)' Write
claude plugin eval venoxia --case clean-spec --runs 1 --allow-tools 'Bash(python3 *)' Write --keep-temp

# Los scripts a mano, sobre un fixture de evals
python3 scripts/validate.py --root evals/clean-spec/project --json --no-color
python3 scripts/charter_lint.py --root <proyecto> --strict
python3 scripts/diff_readings.py --readings evals/clean-spec/project/.venoxia/changes/2026-08-31-stock-reservation/readings --json
echo '{"tool_name":"Write","tool_input":{"file_path":"/x/src/a.ts"},"cwd":"/x"}' | python3 scripts/guardian.py

# El oráculo: ejecuta verifies: por requisito y atribuye green/red/missing/timeout
python3 scripts/oracle.py --root . --change <id> --dry-run     # sólo lista los comandos, no ejecuta nada
python3 scripts/oracle.py --root . --change <id> --record      # ejecuta y añade el run a changes/<id>/oracle.json

# Cobertura con la stdlib (trace), subprocesos incluidos; falla si algún fichero baja de su umbral
python3 tools/coverage.py
```

No hay linter ni formateador configurado (el núcleo es pequeño y las convenciones se sostienen por revisión y por los propios validadores). Sí hay CI: un único workflow (jobs `tests` en matriz de Python, `self-spec` con `validate.py`/`charter_lint.py --strict`, `coverage` con `tools/coverage.py`, `plugin-validate`, y `evals` sólo por `workflow_dispatch`), y es el único: el proyecto dejó de usar GitHub y no queda nada bajo `.github/`. Un proyecto consumidor no copia ninguna plantilla: corre `python3 scripts/gate.py --root <proyecto>`, que no obliga a declarar runner, checkout ni autenticación.

## Arquitectura

### Los seis scripts y el paquete compartido

| Script | Qué decide | Sobre qué |
|---|---|---|
| `scripts/validate.py` | reglas `V01`–`V18` sobre requisitos (incluye `V17`/`V18`, que leen `oracle.json` sin ejecutar nada) | `.venoxia/capabilities/*/spec.md` y `.venoxia/changes/<id>/delta/*.md` |
| `scripts/charter_lint.py` | 19 reglas `C01`–`C19` sobre el acta | `.venoxia/charter.md` (y lee `principles.md` para C17, `capabilities/` para C16) |
| `scripts/diff_readings.py` | divergencia entre lecturas aisladas | `.venoxia/changes/<id>/readings/reader-*.json` + `devils-advocate.json` |
| `scripts/guardian.py` | allow/deny de una edición | payload del hook por stdin; sólo lee `change.json` y `delta/` |
| `scripts/oracle.py` | ejecuta `verifies:` por requisito y atribuye `green`/`red`/`missing`/`timeout`; con `--record` deja el historial en `changes/<id>/oracle.json` | el `delta/*.md` de un change y el `test_command` de `.venoxia/venoxia.json` |
| `scripts/gate.py` | la puerta para un proyecto consumidor: acta y validador en estricto, y el oráculo de cada change en `verified`, con un veredicto único. **Fail-closed** (lo contrario del guardián) y ejecuta **sus propios** scripts, nunca los de la raíz inspeccionada | un proyecto entero, por `--root` |

`scripts/venoxia/` (`parser.py`, `model.py`, `report.py`) lo comparten `validate.py` y `charter_lint.py`. `parser.py` convierte markdown en `Requirement`/`Scenario`/`Capability`/`Delta` y **nunca lanza**: todo problema de forma sale como `Finding` con código `P01`–`P05`. `model.py` define `Finding`, los niveles de confianza, las claves de metadatos y `RETIRED_META_KEYS` (`expires` → `revisit`). `report.py` produce el texto en español y el JSON versión 1.

`guardian.py` y `diff_readings.py` **no importan** el paquete: el guardián por presupuesto de latencia (<100 ms) y para no depender de nada que pueda fallar; diff_readings porque trabaja sobre JSON, no sobre markdown.

Contrato común a validate, charter_lint y diff_readings: flags `--json`, `--no-color`, `--strict`; códigos de salida `0` cumple / `1` no cumple / `2` error de uso. Un proyecto sin `.venoxia/` **no es error**: se avisa y se sale con 0 (`adopted: false` en JSON). El esquema JSON es versión 1 y estable: los evals lo puntúan con regex, así que añadir claves es seguro y renombrarlas rompe los graders.

### El guardián es distinto a todo lo demás

`guardian.py` tiene una garantía que ningún otro script tiene: **siempre código 0 y exactamente un JSON de decisión por stdout**, pase lo que pase (`os._exit(0)` en `finally`, escritura en bytes ASCII a `sys.stdout.buffer`, stderr sustituido por un sumidero si falla). Es **fail-open**: cualquier excepción propia → `allow`. La frontera que hay que respetar al tocarlo: un `change.json` con **contenido** malo (JSON corrupto) es culpa del usuario y **no acredita** nada (sigue buscando, y si no queda ninguno, `deny`); un fallo de **E/S** al leerlo es culpa nuestra y permite anotando en `.venoxia/drift/direct.log`. Confundir las dos cosas fue una puerta trasera real. Los cinco caminos de decisión están en `decide()` y documentados en el README («El modelo de confianza del guardián»).

### Ciclo de vida de un change y quién escribe cada estado

Cinco estados, siempre en este orden; ninguna skill escribe uno que no le toca y ningún estado se salta:

| Estado | Lo escribe | Cuándo |
|---|---|---|
| `draft` | quien crea el directorio del change | Antes de que exista `proposal.md` o `delta/`. |
| `specified` | `/venoxia:specify` | Delta en EARS con `verifies:`/`confidence:`; `validate.py` puede estar en rojo por `V07`/`V08` (el test aún no existe) y es lo esperado. |
| `validated` | `/venoxia:diverge` | Sólo cuando `validate.py` **y** `diff_readings.py` salen los dos con `0` en la misma pasada. |
| `verified` | `/venoxia:verify` | Sólo cuando `scripts/oracle.py --record` deja el último run en verde cubriendo todos los requisitos del change; `V17` audita que el disco lo respalde. |
| `archived` | quien cierra el change | El comportamiento ya vive en la capability y el change deja de ser el ámbito activo. |

```
/venoxia:charter  → .venoxia/charter.md + principles.md      (charter_lint hasta verde)
/venoxia:specify  → changes/<id>/{change.json,proposal.md,delta/*.md}   state: draft → specified
                    (validate.py; V07/V08 en rojo es lo esperado: el test aún no existe)
   el usuario escribe el test con «@covers R-XXX-000»
/venoxia:validate → validate.py en verde
/venoxia:diverge  → 2 lectores + abogado del diablo → readings/*.json → diff_readings.py
                    state: validated  SÓLO si validador Y divergencia salen 0
guardian          → permite Edit/Write de código cuando hay change validated con delta/*.md no vacío
   el usuario escribe el código hasta que el test pasa
/venoxia:verify   → oracle.py --record (rojo antes del código, verde después)
                    state: verified  SÓLO si el oráculo queda en verde y el rojo previo está en el historial
```

Reglas duras del flujo: `specify` nunca escribe `validated` ni `verified`; `diverge` es la única que escribe `validated`; `verify` es la única que escribe `verified`; ninguna skill toca código de producción; `readings/` se guarda **crudo**, sin arreglar, y la skill no tiene voto sobre si dos lecturas «dicen lo mismo». Los agentes `reader` y `devils-advocate` reciben **sólo la ruta del delta**, deliberadamente sin el contexto de la conversación. `guardian.py` sigue abriendo la puerta al código en `validated`, no en `verified`: escribir el código es justo lo que convierte el rojo del oráculo en verde.

### Tests

`tests/venoxia_fixtures.py` es el andamio de toda la suite: `Project()` monta un `.venoxia/` limpio en un `tempfile.TemporaryDirectory` que pasa las 16 reglas en `--strict`, y los scripts se ejecutan **por subproceso** (`Project.run` → `sys.executable script`), con `HOME` falso y timeout de 30 s. El patrón de cada test de regla es: proyecto limpio, romper una sola cosa, comprobar que salta una sola regla (`run.rule_set() == {"V06"}`). `requirement(...)` genera el markdown canónico de un requisito y admite `omit=` para quitar metadatos. `tests/conftest.py` sólo ajusta `sys.path`; unittest no lo carga, por eso `venoxia_fixtures.py` repite el ajuste.

Los tests importan como `from tests.venoxia_fixtures import Project` (funciona con discover, con módulo y con pytest). Reglas del validador: V01–V08 en `test_rules_early.py`, V09–V16 en `test_rules_late.py`, V17/V18 en `test_rules_oracle.py`.

Cuando la variable de entorno `VENOXIA_TRACE_DIR` está definida, `Project.run` antepone `tools/trace_run.py` al argv de cada subproceso en vez de lanzar el script tal cual; sin la variable, el argv no cambia. `tools/trace_run.py` (stdlib, sin dependencias) ejecuta el objetivo con `runpy` dentro de `trace.Trace.runctx`, conserva el código de salida real —incluido el de `sys.exit(N)`, que `trace.main()` por sí solo enmascara— y vuelca las cuentas acumuladas antes de un `os._exit`, sin tocar `guardian.py`. `tools/coverage.py` es quien pone esa variable: lanza la suite entera bajo el envoltorio, acumula un único fichero de cuentas entre el proceso principal y todos los subprocesos (la suite es secuencial), y calcula el porcentaje ejecutado por fichero de `scripts/**/*.py` contra `tools/coverage-threshold.json`, fallando si alguno baja de su umbral.

### Evals

`evals/<caso>/case.yaml` + `project/` es un proyecto de juguete completo. Los graders son **regex sobre el JSON que el script escribe**, nunca sobre la prosa del modelo. Las lecturas de los casos de divergencia vienen **prefabricadas**: no se despachan lectores en la eval. Las cifras de `evals/README.md` («Cifras que los graders dan por buenas») son parte del contrato: si una regla nueva las mueve, hay que decidir si está mal la regla o el fixture. `clean-spec` es el caso que más importa (mide el falso positivo).

## Al cambiar cosas

- **Regla nueva en validate.py o charter_lint.py:** añadirla a `RULES`, un test positivo y uno negativo, la fila en la tabla del README y en la tabla de remedios de `skills/validate/SKILL.md`, y comprobar que los cinco fixtures de evals siguen dando sus cifras.
- **Texto de una skill o plantilla:** los ejemplos de markdown del README y de `templates/` tienen que pasar por los linters como ficheros reales (el README ya coló una vez un `SHALL` que V14 marca).
- **Cambio de formato del requisito o del acta:** tocar `parser.py`/`charter_lint.py`, las plantillas de `templates/`, el ejemplo del README y las skills a la vez; el formato está descrito en tres sitios y los tres tienen que coincidir.
- `TODO.md` es el plan de construcción por fases y recoge las «correcciones sobre el diseño» tomadas por el camino; el diseño completo vive en un artifact enlazado al principio de ese fichero.
