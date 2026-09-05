# Venoxia · TODO de construcción

> Núcleo verificable como plugin de Claude Code.
> Diseño completo: https://claude.ai/code/artifact/6efadf27-49e2-4f6c-8398-e23cd3823d48

---

## Contexto

**Tesis:** una especificación es una apuesta sobre el comportamiento futuro de un sistema, y toda apuesta debe declarar cómo se resuelve y cuánto se confía en ella.

Lo que distingue a Venoxia de las herramientas existentes: la spec deja de ser prosa y pasa a ser un contrato que **falla en CI cuando miente**. Cada requisito nace con su oráculo de verificación y su nivel de confianza; sin oráculo, no compila.

Esta entrega cubre el **núcleo verificable** (fases 01-03 del diseño): formato del requisito, validador determinista, guardián que lo hace inevitable, y motor de divergencia. La Fase 7 le añade la puerta de entrada que faltaba: el acta del proyecto y su linter, para que el plugin sirva también antes de que exista la primera línea de código. Es el 70% del valor y se prueba contra una feature real en días.

Greenfield: no hay código previo. `~/Developments/ia/spec/` contiene los clones de `github/spec-kit` y `Fission-AI/OpenSpec` usados como investigación. Referencias de formato útiles:

- `spec/OpenSpec/schemas/spec-driven/templates/` — plantillas proposal/spec/design/tasks
- `spec/OpenSpec/openspec/specs/cli-validate/spec.md` — reglas de validación que Venoxia extiende

### Decisiones tomadas

| Decisión | Valor |
|---|---|
| Alcance | Núcleo verificable (formato, validador, guardián, divergencia) |
| Idioma | **Tags, nombres e identificadores en inglés; valores, prosa y mensajes en español** |
| Distribución | Repo **privado** `oa2p-solutions/venoxia` + marketplace propio |
| Ubicación | `~/Developments/ia/venoxia` |
| Scripts | Python 3 stdlib, **cero dependencias** (nada de pip/uv) |

### Asunciones a corregir si fallan

- El repo destino es GitHub `oa2p-solutions`, no el Forgejo de OA2P (que aparece como origen en `ecommerce-foundations`).
- Claude Code 2.1.251 con `claude plugin init|validate|eval|tag`. Python 3.14.6 en el sistema.

### Cambio respecto al documento de diseño

Las skills de plugin se invocan como `/<plugin>:<skill>`, así que el prefijo `vx-` sería redundante. **Nombres definitivos:** `/venoxia:charter`, `/venoxia:specify`, `/venoxia:validate`, `/venoxia:diverge`. Actualizar el artifact al cerrar la entrega.

---

## Arquitectura

```
venoxia/
├── .claude-plugin/
│   ├── plugin.json               manifiesto
│   └── marketplace.json          marketplace de un solo plugin
│
├── skills/
│   ├── charter/SKILL.md          entrevistar y escribir el acta del proyecto
│   ├── specify/SKILL.md          redactar capability + delta + oráculos
│   ├── diverge/SKILL.md          despachar lectores y reportar divergencia
│   └── validate/SKILL.md         envoltorio legible de validate.py
│
├── agents/
│   ├── reader.md                 lector aislado · salida cerrada
│   └── devils-advocate.md        cumple la spec y produce lo inaceptable
│
├── hooks/
│   └── hooks.json                PreToolUse → guardian.py
│
├── scripts/
│   ├── validate.py               EL CONTRATO · determinista, sin LLM
│   ├── guardian.py               PreToolUse · fail-open
│   ├── diff_readings.py          compara lecturas · aritmética en código
│   ├── charter_lint.py           EL ACTA · 19 reglas C01–C19, sin LLM
│   └── venoxia/
│       ├── parser.py
│       ├── model.py
│       └── report.py
│
├── templates/
│   ├── capability.md
│   ├── charter.md
│   ├── delta.md
│   └── proposal.md
│
├── evals/                        casos para `claude plugin eval`
├── tests/                        unittest de la stdlib sobre scripts y parser
├── README.md
└── LICENSE
```

**Lo que el plugin crea en el proyecto del usuario:**

```
.venoxia/
├── charter.md                    acta del proyecto · propósito, usuarios, capabilities
├── principles.md
├── capabilities/<name>/spec.md    estado actual · vive para siempre
├── changes/<id>/
│   ├── change.json               {state, via, capabilities}
│   ├── proposal.md
│   ├── delta/<capability>.md
│   └── readings/                 salida cruda de cada lector
└── drift/
```

---

## El formato del requisito

Tags en inglés, prosa en español. Parseable con regex, legible sin herramientas.

```markdown
### R-CHK-014 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de
todas las líneas del pedido durante 15 minutos.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas
- **THEN** se crea la reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea
- **THEN** responde 409 y no crea ninguna reserva

verifies:   test/checkout/reservation.spec.ts
confidence: medium
  why:      los 15 minutos son una apuesta, no un dato
  revisit:  cuando hayamos medido un mes de reservas caducadas
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
```

El ID vive en el encabezado: estable, linkable, parseable. El bloque de metadatos usa claves fijas en inglés al final del requisito.

---

## Fase 0 · Esqueleto y bucle de desarrollo

- [x] `claude plugin init venoxia --with skills agents hooks` para obtener el scaffold canónico
- [x] Mover el resultado a `~/Developments/ia/venoxia` y dejar `~/.claude/skills/venoxia` como **symlink** al repo → auto-carga como `venoxia@skills-dir`, se edita sin reinstalar
- [x] `.claude-plugin/plugin.json`: `name`, `version 0.1.0`, `description` en español, `author`, `license MIT`, `keywords` en inglés, `hooks: "./hooks/hooks.json"`
- [x] `git init` y `.gitignore` (`__pycache__/`, `evals/results/`, `.venoxia/` de pruebas)
- [x] Verificar: `claude plugin validate . --strict` en verde

---

## Fase 1 · El formato y el validador

> Sin esto nada más tiene sentido: es el momento en que la spec deja de ser prosa.

- [x] `scripts/venoxia/model.py` — dataclasses `Requirement`, `Scenario`, `Capability`, `Delta`, `Finding` (severidad `error` / `warning`)
- [x] `scripts/venoxia/parser.py` — markdown a modelo. Extrae ID del encabezado, cuerpo narrativo, escenarios y bloque de metadatos. Devuelve findings de forma, **nunca lanza excepción**
- [x] `scripts/venoxia/report.py` — salida humana en español (con `--no-color` para CI) y `--json` estable para el guardián y el futuro panel
- [x] `scripts/validate.py` con las reglas siguientes. Todas deterministas, ninguna consulta a un modelo:

| Regla | Comprueba | Severidad |
|---|---|---|
| `V01` | ID bien formado `R-[A-Z]{2,4}-\d{3}` y único en el repo | error |
| `V02` | El cuerpo encaja en exactamente un patrón EARS (`WHEN` / `WHILE` / `WHERE` / ubicuo / complejo) | error |
| `V03` | Hay narrativa antes del primer `#### Scenario:` | error |
| `V04` | Al menos un escenario por requisito | error |
| `V05` | Cada escenario tiene `**WHEN**` y `**THEN**` | error |
| `V06` | `verifies:` presente y no vacío | **error — el corazón del sistema** |
| `V07` | El fichero de `verifies:` existe en disco | error |
| `V08` | El fichero de `verifies:` contiene `@covers <ID>` (doble vínculo) | error |
| `V09` | `confidence:` ∈ `{high, medium, low}` | error |
| `V10` | `confidence: low` obliga a `revisit:` con el hecho que la resuelve | error |  **Corrección sobre el diseño:** el campo se llamaba `expires:` y pedía una fecha ISO futura. Lo escribía el modelo, que no tiene forma de saber cuándo llega la evidencia, así que producía plazos redondos con aspecto de compromiso —seis apuestas de un proyecto real, todas el mismo día—. Una fecha inventada es peor que ninguna. Ahora pide el hecho que cierra la apuesta, que sí sale del proyecto, y `V10`/`C12` rechazan tanto la fecha como el «ya veremos» |
| `V11` | Presupuesto de incertidumbre: ≤30% de requisitos con `low` | error |
| `V12` | El delta declara al menos un bloque `## ADDED\|MODIFIED\|REMOVED\|RENAMED Requirements` | error |
| `V13` | Los IDs de `MODIFIED`/`REMOVED` existen en la capability viva | error |
| `V14` | Sin `SHALL`/`MUST` en el cuerpo | warning |
| `V15` | `from:` ausente en una capability nueva | warning |
| `V16` | Test con `@covers` de un ID inexistente → comportamiento no especificado | warning |

- [x] Flag `--strict` (warnings cuentan como fallo) y códigos de salida `0` / `1`
- [x] `tests/` con `unittest` de la stdlib: un fixture por regla, en positivo y negativo. **Única parte con cobertura obligatoria** — de este componente depende la credibilidad de todo lo demás
- [x] `skills/validate/SKILL.md` — envoltorio que ejecuta el script y agrupa findings por severidad. `disable-model-invocation: false`, `allowed-tools: Bash(python3 *)`

---

## Fase 2 · El guardián

> Convierte el hábito en infraestructura. Sin esto, todo lo demás es una sugerencia que se salta cualquiera con prisa un viernes.

- [x] `scripts/guardian.py` — hook `PreToolUse`, matcher `Edit|Write|NotebookEdit`. Decisión en orden:

  1. No existe `.venoxia/` → `allow` (proyecto no adoptado, el plugin no estorba)
  2. El path editado cae bajo `.venoxia/`, `prfaq/` o es markdown de spec → `allow` (estás escribiendo la spec)
  3. Hay cambio activo con `state: validated` en `change.json` → `allow`
  4. El cambio activo declara `via: direct` → `allow` y anota en `.venoxia/drift/direct.log`
  5. Cualquier otro caso → `deny` con `permissionDecisionReason` en español: qué falta y qué comando lo arregla

- [x] **Fail-open sin excepciones**: cualquier error interno, timeout o JSON malformado devuelve `allow`. Envolver `main()` en try/except que emite `allow` y traza a stderr. Un guardián que rompe el flujo por un bug se desinstala el primer día
- [x] Presupuesto de latencia <100 ms: sin red, sin cargar el repo entero — leer solo `change.json`
- [x] `hooks/hooks.json` con `"${CLAUDE_PLUGIN_ROOT}/scripts/guardian.py"` y `timeout: 5`
- [x] Probar los cinco caminos a mano, verificando que el mensaje de `deny` es accionable

---

## Fase 3 · La skill de especificar

- [x] `templates/capability.md`, `templates/delta.md`, `templates/proposal.md` — encabezados estructurales en inglés, comentarios guía y prosa de ejemplo en español
- [x] `skills/specify/SKILL.md` — frontmatter: `model: opus`, `effort: xhigh`, `argument-hint`, `allowed-tools: Read, Write, Glob, Grep, Bash(python3 *)`
- [x] Cuerpo de la skill, en este orden:
  1. Leer `.venoxia/principles.md` y las capabilities existentes **antes** de proponer nada
  2. Decidir si el cambio crea capabilities nuevas o modifica existentes → escribir `proposal.md`
  3. Redactar el delta en EARS, **cada requisito con `verifies:` y `confidence:` desde el primer borrador** — nunca como paso posterior
  4. Ejecutar `validate.py` y corregir hasta verde antes de devolver el control
- [x] Regla explícita en el prompt: *si la implementación puede cambiar sin cambiar el comportamiento observable, no pertenece a la spec*

---

## Fase 4 · El motor de divergencia

> La pieza que no existe en ninguna herramienta actual. Pedirle al mismo modelo que encuentre sus propias ambigüedades no funciona: ya sabe qué quiso decir.

- [x] `agents/reader.md` — `model: sonnet`, `effort: medium`, `tools: Read` únicamente. Recibe **solo la ruta del delta**, sin el contexto de la conversación donde nació. Devuelve tabla de decisión cerrada, un objeto por escenario:

  ```json
  {"scenario": "<título literal>", "effect": "<≤12 palabras>",
   "status_code": "<código o null>", "side_effects": ["..."],
   "unclear": false, "unclear_why": null}
  ```

- [x] `agents/devils-advocate.md` — `model: opus`, `effort: high`, `tools: Read`. Un solo trabajo: encontrar el caso donde cumplir la spec al pie de la letra produce un resultado que nadie quiere. Devuelve `{"attack": "...", "requirement_id": "...", "severity": "..."}`
- [x] `skills/diverge/SKILL.md` — `allowed-tools` incluye `Agent(venoxia:reader, venoxia:devils-advocate)`. Despacha **dos lectores en paralelo más el abogado del diablo**, escribe cada salida cruda en `.venoxia/changes/<id>/readings/`, llama a `diff_readings.py`
- [x] `scripts/diff_readings.py` — **la aritmética la hace el código, no un modelo**. Normaliza (minúsculas, sin acentos ni puntuación), compara campo a campo por escenario:
  - `status_code` distinto → divergencia dura
  - `side_effects` con diferencia de conjunto → divergencia dura
  - `effect` con similitud por tokens bajo umbral → divergencia blanda  **Corrección sobre el diseño:** la similitud se calculaba sobre tokens crudos y `side_effects` se comparaba como conjunto exacto de cadenas. Sobre prosa española escrita por dos modelos eso producía ruido masivo —en un delta real de 17 escenarios, 19 preguntas de las que ninguna era una ambigüedad: voz activa contra pasiva en las blandas, un artículo de diferencia en las duras—. Ahora se comparan tokens de contenido (sin palabras vacías ni conjugación, con las cifras blindadas) y los efectos se buscan por cobertura contra `effect` y `side_effects` juntos. El mismo delta pasó de 19 preguntas a 4, todas legítimas
  - cualquier `unclear: true` → laguna declarada
- [x] Salida: por cada divergencia, **una pregunta cerrada con las dos lecturas enfrentadas**, nunca un "¿hay algo ambiguo?". Informe en `.venoxia/changes/<id>/divergence.md`
- [x] Marcar `change.json` como `state: validated` solo cuando validador **y** divergencia pasan

**Riesgo conocido:** si los dos lectores comparten modelo y prompt pueden converger en el mismo error. Mitigación en esta fase: consignas distintas (uno lee como implementador, otro como responsable de QA). Medirlo en los evals antes de plantearse modelos distintos.

*Referencia validada:* el plugin `claude-security` de Anthropic ya usa este patrón — panel de verificadores aislados con la aritmética del veredicto calculada fuera del modelo. Ver `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/claude-security/agents/scan-verifier.md`.

---

## Fase 5 · Evals

- [x] `evals/` con casos para `claude plugin eval venoxia --ablation with-without`:
  - `ambiguous-status-code/` — escenario que admite dos códigos. **Debe** detectarse
  - `ambiguous-partial-effect/` — reserva total vs parcial. **Debe** detectarse
  - `clean-spec/` — delta sin ambigüedad. **No debe** haber falso positivo
  - `missing-oracle/` — requisito sin `verifies:`. El validador **debe** fallar
  - `budget-exceeded/` — 40% de requisitos en `low`. **Debe** rechazarse
- [x] Graders que comprueben el resultado del script (determinista), no la prosa del modelo
- [x] Documentar el comando de eval en el README como forma de verificar regresiones

---

## Fase 6 · Repo y distribución

- [x] **Confirmar antes de crear nada remoto.** Crear `oa2p-solutions/venoxia` privado y empujar (hecho el 2026-09-05 con la cuenta `arochaoscar` de `gh`; `oscar-ppay` no tiene permiso de crear repos en la organización)
- [x] `.claude-plugin/marketplace.json` — un solo plugin. **Corrección sobre el diseño:** `claude plugin validate` rechaza `source: "git"` («plugins.0.source: Invalid input»); la forma válida que conserva la misma URL es `{source: "url", url: "https://github.com/oa2p-solutions/venoxia.git"}`
- [x] `README.md` en español: qué es, la tesis en tres frases, instalación, el formato del requisito, y **el modelo de confianza del guardián** (qué bloquea y cómo desactivarlo)
- [x] Instalación para el equipo:
  ```bash
  claude plugin marketplace add oa2p-solutions/venoxia
  claude plugin install venoxia@venoxia
  ```
- [x] `claude plugin tag` para la release: la primera publicada es `venoxia--v0.2.0` (2026-09-05), empujada a `origin`. La 0.1.0 no llegó a etiquetarse

---

## Fase 7 · La puerta de entrada

> Venoxia empezaba donde ya sabes qué comportamiento quieres, y ése resultó ser el hueco. El primer usuario que lo probó contra un proyecto en cero lo dijo entero:
>
> > «eso no define el proyecto, ni dice qué es lo que quiero construir. Este plugin es para alguien que está creando un proyecto de cero y necesita definir todo antes de que se escriba la primera línea de código.»
>
> Y tenía razón. `/venoxia:specify` pide «el cambio, en una frase»: una pregunta que da por supuesto un sistema anterior del que esto es el delta. Sin producto no hay delta, así que la primera media hora del plugin era un callejón sin salida. Faltaba el paso cero.

**Qué se ha construido.** `/venoxia:charter`, la entrevista que define el proyecto antes de que exista una línea de código y produce un acta verificable: propósito, usuarios con su «hoy» y su «con esto», capabilities priorizadas con su criterio de terminación, fuera de alcance razonado y apuestas con fecha de revisión. El acta no es un documento de intenciones: tiene su propio linter determinista, igual que el requisito tiene el suyo. Y termina entregando el `/venoxia:specify` exacto de la capability de prioridad 1, que es la costura con todo lo demás.

**Por qué el acta se valida y no se limita a existir.** Un documento de visión que nadie comprueba se convierte en decoración en tres semanas. Las dos casillas que no se pueden dejar en blanco son `Done when` y `Out of scope`: sin criterio de terminación, una capability se termina cuando alguien se cansa; sin fuera de alcance escrito, todo está dentro y la primera entrega no llega nunca. Las dos son la versión, a escala de proyecto, de lo que `verifies:` es a escala de requisito.

- [x] `templates/charter.md` — encabezados estructurales y claves en inglés, prosa y comentarios guía en español, como el resto de plantillas
- [x] `scripts/charter_lint.py` — 19 reglas `C01`–`C19` sobre `.venoxia/charter.md`, deterministas y sin modelo detrás. Mismos códigos de salida y mismas convenciones (`--json`, `--no-color`, `--strict`) que `validate.py`
- [x] `skills/charter/SKILL.md` — la entrevista: pregunta, no rellena; escribe `.venoxia/charter.md` y `.venoxia/principles.md`; pasa el linter hasta verde antes de devolver el control, y entrega el `/venoxia:specify` de la primera capability
- [x] `tests/test_charter_lint.py` — un caso en positivo y otro en negativo por cada regla `C01`–`C19`, con `unittest.TestCase` como el resto de la suite
- [x] `skills/specify/SKILL.md` — lee el acta en el paso 1 junto con los principios; si no hay ni acta ni capabilities, remite a `/venoxia:charter` en vez de pedir «el cambio, en una frase»; si hay acta, comprueba que la capability figura en su tabla y pregunta antes de inventarse una fila
- [x] `README.md` — «Empezar un proyecto desde cero» con el recorrido de siete pasos (esqueleto → acta → spec → el rojo correcto de `V07` → test → divergencia → código) y «El acta del proyecto» con las secciones y la tabla de las 19 reglas
- [x] Verificar: los ejemplos de markdown del README pasados por `validate.py` y `charter_lint.py` **como ficheros reales**, no como bloques que nadie ejecuta. El README ya coló una vez un `SHALL` que su propia regla `V14` marcaba

---

## Fase 8 · El oráculo se ejecuta

> `validate.py` comprueba que cada requisito **declare** su oráculo en `verifies:` y que el fichero exista; nunca lo ejecuta. La mitad de TDD que faltaba —correr el test y anotar si pasa— seguía siendo manual y de memoria, requisito a requisito, cada vez que alguien quería saber si un change ya estaba implementado de verdad.

**Qué se ha construido (`DEF-004`).** `scripts/oracle.py`: ejecuta el `test_command` que el proyecto declara en `.venoxia/venoxia.json` una vez por requisito de un change, sustituyendo `{files}` por sus rutas de `verifies:`, y atribuye `green`/`red`/`missing`/`timeout` a cada uno. `--record` deja el historial en `.venoxia/changes/<id>/oracle.json`, con un tope de 50 runs. Mismo criterio que el resto del núcleo: determinista, sin modelo, códigos `0`/`1`/`2`.

- [x] `scripts/oracle.py` — `load_config`, `collect_requirements` (reutiliza `venoxia.parser.parse_delta`), `run_one`/`run_all`, `analyse`, `build_payload`, `record`, `render_text`, `build_parser`/`main`; nunca lanza por los datos del proyecto
- [x] `tests/fake_runner.py` — runner de mentira que lee un marcador (`RESULT: red` / `RESULT: sleep N`) de los ficheros que recibe y registra cada invocación, para poder comprobar qué se llamó y qué no
- [x] `tests/test_oracle.py` — un caso por criterio de aceptación: todo en verde, un rojo nombrado, un `verifies:` inexistente que no se invoca, un timeout sin traceback, los dos errores de uso (`venoxia.json` ausente, `{files}` ausente), `--dry-run`, `--record` acumulando y sobreviviendo a un historial corrupto, el esquema estable y varias rutas en una sola invocación
- [x] `tests/venoxia_fixtures.py` — `Project.oracle_config(command, cwd)`, `Project.run_oracle(*args)`/`run_oracle_json(*args)`, y `test_file(..., result=…)` para fabricar el marcador del runner falso
- [x] `templates/venoxia.json` y `README.md` («## Ejecutar el oráculo», y el recorrido de siete pasos gana el rojo y el verde grabados)
- [x] `skills/charter/SKILL.md` — la Tanda F pregunta el comando de test y el Paso 8 escribe `.venoxia/venoxia.json`; sin respuesta, se deja sin crear y se dice en la entrega
- [x] Hueco conocido, correctamente diagnosticado y no atribuible a `oracle.py`: `python3 scripts/oracle.py --change 2026-09-04-adopt-venoxia --dry-run` no puede listar «un comando por requisito retroactivo» porque ese change tiene 0 requisitos (`exit 0`, sin traceback: el comportamiento correcto). Ese change (`DEF-008`) no tiene `delta/`: las cuatro capabilities retroactivas se escribieron directamente como `.venoxia/capabilities/*/spec.md`, nunca como delta de `2026-09-04-adopt-venoxia`. Lo que sí quedó en el alcance de `DEF-004`: `--dry-run` con 0 requisitos ya no se queda mudo, imprime una línea que nombra la causa («este change no tiene delta/ o su delta/ no declara requisitos»), así que deja de leerse como un fallo silencioso. Resolver el hueco de verdad (que el comando liste algo) exige (a) una tarea de `DEF-008` que añada un `delta/` retroactivo a ese change, fuera del `files.create`/`modify` declarado aquí, o (b) reescribir el criterio de aceptación de `DEF-004` que lo exige tal cual, para que no dependa de un fichero que la arquitectura de `DEF-008` decidió no crear. Ninguna de las dos está en el alcance de esta tarea.
- [x] `DEF-006` — dos reglas nuevas en `validate.py`: `V17` (error) exige que un change `verified` tenga su último run de `oracle.json` en `all_green` cubriendo todos los `requirement_id` del delta; `V18` (aviso) señala cualquier requisito en verde que nunca pasó antes por rojo. `tests/test_rules_oracle.py` cubre los positivos y negativos de ambas reglas; `tests/test_eval_fixtures.py` (nuevo) fija las cifras de los cinco fixtures de evals — ninguno tiene `oracle.json`, así que ni `V17` ni `V18` intervienen y las cifras de `evals/README.md` no se mueven. Sobre este repo, el change `.venoxia/changes/2026-09-04-tdd-evidence` tiene su rojo y su verde grabados en `oracle.json`; queda en `specified` por la misma razón que `DEF-007`: esta sesión no dispone de la herramienta para despachar los lectores de `/venoxia:diverge` — el paso a `validated` y a `verified` lo hace la sesión principal, anotado en el `## Pendiente` de su `proposal.md`
- [x] `DEF-007` — `skills/verify/SKILL.md`: envuelve `oracle.py`, es la única skill que escribe `"state": "verified"`, y sólo lo hace con un verde que trae un rojo o `missing` anterior en `oracle.json` para cada requisito —o con confirmación explícita del usuario cuando no lo trae—. `tests/test_verify_skill.py` comprueba el frontmatter (nombre, disparadores, `allowed-tools` sin `Bash` genérico) y que el cuerpo nombra el contrato. Sobre este repo, el change `.venoxia/changes/2026-09-04-verify-skill` tiene su rojo y su verde grabados en `oracle.json`; queda en `specified` porque esta sesión no dispone de la herramienta para despachar los lectores de `/venoxia:diverge` — el paso a `validated` y a `verified` lo hace la sesión principal, anotado en el `## Pendiente` de su `proposal.md`

---

## Fase 9 · Cobertura medida con subprocesos incluidos

> `tests/venoxia_fixtures.py` (`Project.run`) ejecuta `validate.py`, `charter_lint.py`, `guardian.py`, `diff_readings.py` y `oracle.py` por subproceso, nunca importados. Medir cobertura sólo en el proceso de `unittest` vería una fracción de lo que la suite ejercita de verdad.

**Qué se ha construido (`DEF-010`).** `tools/coverage.py`: lanza la suite entera bajo `python3 -m trace --count` con `VENOXIA_TRACE_DIR` puesta, y ese mismo ajuste hace que `Project.run` anteponga el mismo `trace --count` a cada subproceso que lanza — sin que ningún test declare nada. El proceso principal y todos los subprocesos acumulan en un único fichero de cuentas (la suite es secuencial: no hay carrera). El script calcula el porcentaje ejecutado por fichero de `scripts/**/*.py` a partir de los `.cover` de `trace`, lo compara contra `tools/coverage-threshold.json` y sale con código 1 si alguno baja de su umbral.

- [x] `tools/coverage.py` — `run_suite_under_trace`, `measure`/`parse_cover_file`, `compute_threshold`/`build_thresholds`, `render_table`, `--init` para fijar el umbral la primera vez (medido menos 2 puntos, suelo de 85 para los cinco scripts del núcleo)
- [x] `tests/venoxia_fixtures.py` (`Project.run`) — el prefijo del envoltorio de traza es condicional a `VENOXIA_TRACE_DIR` en el entorno efectivo (el real de `os.environ`, o el que llega por `env=`); sin la variable, el argv no cambia. `tests/test_trace_wrapping.py` comprueba las dos ramas
- [x] Dos huecos que documentaba esta fase — **cerrados por `DEF-013`** — están resueltos en `tools/trace_run.py`, no escondidos: ver la entrada de `DEF-013` justo debajo, con las cifras finales.

**Qué se ha corregido (`DEF-013`).** `python3 -m trace` tenía dos huecos que rompían la medición en vez de sólo dejarla incompleta: `trace.main()` atrapa el `SystemExit` de lo que ejecuta y nunca lo relanza, así que cualquier script bajo medición que sale con `sys.exit(N != 0)` devolvía `0` — 210 tests que comprueban un código de salida distinto de 0 fallaban sólo por estar bajo `trace`, no por una regresión; y `scripts/guardian.py`, que termina siempre con `os._exit(0)` en su `finally` fail-open, medía 0 % para siempre porque `os._exit` salta el volcado de `trace`. `tools/trace_run.py` (nuevo, stdlib) ejecuta el objetivo en el mismo proceso con `runpy` dentro de `Trace.runctx`, captura el `SystemExit` real como código de salida propio, y sustituye `os._exit` por una función que vuelca las cuentas acumuladas antes de llamar al `os._exit` original — sin tocar `scripts/guardian.py` en absoluto. `Project.run` y `tools/coverage.py` (su `run_suite_under_trace`, ahora `python3 tools/trace_run.py -m unittest discover -s tests -q`) usan el mismo envoltorio.

- [x] `tools/trace_run.py` — soporta `<script> [args...]` y `-m <módulo> [args...]`; conserva el código de salida real en las dos formas, con y sin `VENOXIA_TRACE_DIR`; `tests/test_trace_wrapping.py` (`TraceRunScriptTest`) comprueba un `sys.exit(3)` de punta a punta
- [x] `tools/coverage.py` — `main()` hace fallar la ejecución (código 1) si la suite no termina en `OK` bajo medición, porque ese código ya no es un artefacto de la instrumentación
- [x] `tests/test_oracle.py` — ganó los casos de la lista que dejaba esta fase (config con JSON inválido, `venoxia.json` que no es objeto, `test_command` ausente/vacío/con comillas desparejadas, `cwd` inexistente o de tipo raro, runner inexistente, requisito sin `verifies:` dentro y fuera de `--dry-run`, `--root` inválido o sin adoptar, el veredicto «incompleto» en modo texto, y las ramas de `OSError` de `load_config`/`collect_requirements`/`_load_history`/`record` que sólo se alcanzan parcheando un método de `Path`)
- [x] `tests/test_guardian.py` (`GuardianCliArgumentsTest`) — `--help`/`-h` y un argumento inesperado, sin los cuales `write_text`/`warn` quedaban sin ejercitar
- [x] Cifras finales de `python3 tools/coverage.py --init` sobre este repo, con la suite completa en `OK` bajo medición: `charter_lint.py` 95,4 % (umbral 93) · `diff_readings.py` 93,7 % (91) · `guardian.py` 87,5 % (85) · `oracle.py` 97,8 % (95) · `validate.py` 93,8 % (91) · `venoxia/__init__.py` 100 % (98) · `venoxia/model.py` 99,2 % (97) · `venoxia/parser.py` 83,5 % (81) · `venoxia/report.py` 93,5 % (91). Los cinco scripts del núcleo, `guardian.py` y `oracle.py` incluidos, miden por encima de 85

---

## Fase 10 · CI: la tesis falla en CI cuando miente

> «Lo que distingue a Venoxia: la spec deja de ser prosa y pasa a ser un contrato que falla en CI cuando miente.» Hasta esta fase no había ningún CI: la frase era una promesa que sólo se cumplía si alguien ejecutaba los scripts a mano.

**Qué se ha construido (`DEF-009`).** `.github/workflows/ci.yml`, el CI del propio plugin, con cinco jobs (`tests` en matriz 3.12/3.13/3.14, `self-spec` con `validate.py`/`charter_lint.py --strict`, `coverage` con `tools/coverage.py`, `plugin-validate` con el CLI instalado por `npm`, y `evals` restringido a `workflow_dispatch`); y `templates/ci/venoxia-gate.yml`, la plantilla para que un proyecto consumidor haga checkout de un Venoxia fijado por tag y corra la puerta sin `pip`, incluido el oráculo por cada change `validated`/`verified`.

- [x] `.github/workflows/ci.yml` — disparadores `push`/`pull_request` sobre `main` y `workflow_dispatch`; jobs `tests`, `self-spec`, `coverage`, `plugin-validate`, `evals`
- [x] `templates/ci/venoxia-gate.yml` — checkout fijado de `oa2p-solutions/venoxia` con `secrets.VENOXIA_TOKEN`, `charter_lint.py --strict`, `validate.py --strict`, y `oracle.py --change <id>` por cada change en `validated`/`verified` cuando existe `.venoxia/venoxia.json`, sin ningún paso de `pip`
- [x] `tests/test_ci_workflow.py` — comprueba estructuralmente (regex sobre el YAML, sin librería de YAML: cero dependencias) los disparadores, los cinco jobs, la matriz, los comandos exactos de `self-spec`, la plantilla del consumidor y la sección nueva del README
- [x] `README.md` — sección «## Verificar en CI» que explica los dos workflows y por qué `evals` es manual; «Instalación» pasa a nombrar la matriz 3.12–3.14 en vez de sólo «probado con 3.14»
- [x] Hueco conocido y documentado, no atribuible a `DEF-009`: **el job `self-spec`, tal como el criterio de aceptación lo pide (`--strict` en los dos comandos), falla hoy sobre este mismo repositorio.** No por nada que esta fase haya introducido: `python3 scripts/validate.py --root . --strict --json` ya devolvía `exit 1` antes de esta fase, con 8 avisos `V18` heredados de `.venoxia/changes/2026-09-04-oracle` (`R-ORC-001`…`R-ORC-008`), cuyo primer run de `oracle.json` quedó en `missing` en vez de `red` — un hueco de `DEF-004`/`DEF-006`, no de este change. `charter_lint.py --strict` sí sale en verde (0/0). Arreglarlo exige reescribir el historial de `oracle.json` de ese change o revisar si `V18` debería tratar `missing` como equivalente a `red` para este caso, y ninguna de las dos está en el alcance de `DEF-009`. Mientras no se resuelva, el job `self-spec` de `ci.yml` fallará en el primer `push`/`pull_request` real — es correcto que falle, porque el aviso es cierto, pero conviene saber que la causa es anterior a esta fase, no una regresión suya
- [x] **El primer run real de GitHub Actions no llegó a ejecutarse** (2026-09-05): el run 33976875711 de `oa2p-solutions/venoxia` estuvo más de veinte minutos en `queued` sin runner asignado, con la política de la organización ya en `selected`, presupuesto de Actions con consumo cero, plan `free` y sin anotaciones en los check-runs; terminó `cancelled`. La causa no se ve desde la API. Como la organización tiene un Forgejo interno con Actions y un `forgejo-runner` en `oa2p-server` (etiquetas `oa2p-debian` y `oa2p-node`), el change `2026-09-05-forgejo-ci` añade `.forgejo/workflows/ci.yml` como espejo del de GitHub (`R-CI-008`…`R-CI-010`, `tests/test_forgejo_workflow.py` vigila la paridad) y el repo se espeja en `OA2P/venoxia`. `B-003` y `B-004` se resuelven con el primer run real que corra, sea cual sea el proveedor
- [ ] **Actions estaba deshabilitado por política de la organización** (`enabled_repositories: none`) cuando se creó el repo el 2026-09-05; se cambió a `selected` con `oa2p-solutions/venoxia` como único repo autorizado. Cualquier otro repo de la organización que quiera CI tiene que añadirse a esa lista. El primer run real de `ci.yml` es el que dispara el push de esta línea
- [ ] Dos partes del criterio de aceptación de `DEF-009` exigen un run real en GitHub Actions, imposible sin `git push` (ninguna acción remota en esta sesión): (a) que la matriz de `tests` pase de verdad en las tres versiones de Python en los runners de GitHub — no probado localmente para 3.12 (intérprete no instalado en esta máquina; sí se corrió la suite completa en 3.13 y 3.14, verde en ambos, y no se ha encontrado sintaxis posterior a 3.12 en el código); (b) la prueba negativa de un `SHALL` en `.venoxia/capabilities/validator/spec.md` empujado a una rama, con el enlace al run fallido de `self-spec` como evidencia — se hizo su forma local equivalente (`validate.py --strict` con el `SHALL` introducido y revertido) y confirmó que `V14` dispara, pero eso no sustituye al run de GitHub Actions que pide el criterio
- [x] El change `.venoxia/changes/2026-09-04-ci-gate` de este repo tiene su rojo y su verde grabados en `oracle.json` (`R-CI-001`…`R-CI-005`); queda en `specified` porque esta sesión no dispone de la herramienta para despachar los lectores de `/venoxia:diverge` — el paso a `validated` y a `verified` lo hace la sesión principal, anotado en el `## Pendiente` de su `proposal.md`
- [x] Corrección tras revisión: el delta de `2026-09-04-ci-gate` llevaba `confidence: low` en `R-CI-001` y `R-CI-003` sobre afirmaciones puramente estructurales (lo que el fichero YAML declara, no si un run real las cumple), dejando el 40 % del ámbito en `low` — por encima del 30 % de `V11`. Se separó cada una en su parte estructural (ahora `high`, cubierta por `tests/test_ci_workflow.py` sin ninguna apuesta) y una apuesta nueva y honesta: `R-CI-006` (que la matriz pase de verdad en GitHub Actions; no probada, sin Python 3.12 en esta máquina y sin acción remota permitida) y `R-CI-007` (que `claude plugin validate` no exija credenciales en un runner limpio; esta máquina ya tiene sesión autenticada). El ámbito pasó de 5 a 7 requisitos con 2 en `low` (28,6 %), verde en `V11`. Como el código de `ci.yml` ya existía y pasaba, no hay forma retroactiva de grabar un rojo para `R-CI-006`/`R-CI-007`: `python3 scripts/oracle.py --change 2026-09-04-ci-gate --record` sólo pudo grabar un run verde para las siete, así que `validate.py --strict` sobre este change emite dos avisos `V18` nuevos (`R-CI-006`, `R-CI-007`), del mismo tipo ya aceptado para `R-ORC-001`…`R-ORC-008` de `2026-09-04-oracle` — cero errores, sólo avisos, y quedan documentados aquí y en el `## Pendiente` de `proposal.md`. **Cierre tras la divergencia (2026-09-05):** los dos lectores declararon laguna sobre `R-CI-006` y `R-CI-007` porque ningún test puede comprobarlos; salieron del delta y pasaron a ser las apuestas `B-003` y `B-004` del acta, y sus `@covers` se retiraron del test. Lo que no puede comprobar un test no es un requisito, es una suposición
- [x] Pasar `/venoxia:diverge` y `/venoxia:verify` sobre los changes de 2026-09-04 desde la sesión principal (hecho el 2026-09-05, con lectores y abogado reales): `tdd-evidence` convergió a la primera; `ci-gate` y `verify-skill` a la tercera ronda, tras reescribir sus deltas con un hecho por escenario y sin códigos de salida dentro de los WHEN; los tres están en `verified`. `2026-09-04-oracle` **no converge** tras cuatro rondas y se queda en `specified`: ver la Fase 11

---

## Verificación de extremo a extremo

Sobre un proyecto real, no un fixture:

- [x] 1. `mkdir -p /tmp/venoxia-demo && cd $_ && git init` y crear `.venoxia/principles.md`
- [x] 2. Con el plugin cargado, intentar `Write` de un fichero de código → **el guardián deniega** con un mensaje que dice qué hacer
- [x] 3. `/venoxia:specify "reservar stock al confirmar el pago durante 15 minutos"` → produce `proposal.md` y `delta/checkout.md` con requisitos EARS, cada uno con `verifies:` y `confidence:`
- [x] 4. `/venoxia:validate` → **falla** en `V07`/`V08` porque el test todavía no existe. **Este fallo es el comportamiento correcto y es la demostración de la tesis.** Si no falla, el sistema no sirve
- [x] 5. Crear el test con `@covers R-CHK-014` → `/venoxia:validate` en verde
- [x] 6. `/venoxia:diverge` → sobre la spec ambigua a propósito devuelve la pregunta con las dos lecturas enfrentadas; sobre la corregida, converge
- [x] 7. Reintentar el `Write` de código → **ahora el guardián permite**
- [x] 8. `python3 -m unittest discover -s tests -q` en verde
- [x] 9. `claude plugin validate . --strict` y `claude plugin eval venoxia` en verde

---

## Fase 11 · La divergencia se resuelve como entrevista

> Observación recogida al usar `/venoxia:diverge` sobre un delta real («Divergencias duras · 3 · Escenario: Extraction service does not answer»): el informe vuelca todas las preguntas cerradas de golpe y el usuario tiene que contestarlas en bloque.

> Segunda observación, del 2026-09-05, sobre el delta de `2026-09-04-oracle` (13 escenarios de línea de comandos): cuatro rondas con lectores nuevos y ninguna converge, y **ninguna de las duras es un desacuerdo sobre comportamiento**. Los dos lectores coinciden en códigos y efectos; difieren en cuántos colaterales deducen del contexto («no invoca el runner», «termina la ejecución del test_command») y `diff_readings.py` cuenta como dura cada colateral que el otro lector no recoge, aunque no lo contradiga. Tres cosas que sí ayudaron y conviene fijar en `skills/specify/SKILL.md`: un hecho por escenario, ningún código de salida dentro del WHEN, y el mismo sustantivo para la misma cosa en todo el delta.

- [ ] `diff_readings.py`: un colateral que el otro lector **no recoge** sólo es divergencia dura si **contradice** algo del otro repertorio (una negación del mismo hecho, otra cifra, otro código); si sólo añade, es blanda. Medirlo contra los cinco fixtures de evals antes de tocar el umbral: `ambiguous-partial-effect` debe seguir dando una dura en `side_effects`
- [ ] `skills/specify/SKILL.md`: las tres reglas de redacción de arriba, con el ejemplo del oráculo
- [ ] Volver a pasar `/venoxia:diverge` sobre `2026-09-04-oracle` cuando lo anterior esté hecho; sólo entonces `/venoxia:verify` (su `oracle.json` ya trae rojo y verde)

- [ ] Las preguntas de divergencia se plantean **como entrevista al usuario, una por una**, con `AskUserQuestion`: cada opción es una de las lecturas enfrentadas y lleva sus ventajas y desventajas en la descripción, igual que hace `/venoxia:charter` en su entrevista. La aritmética sigue en `diff_readings.py`; lo que cambia es cómo la skill presenta el resultado y recoge la respuesta, y que la respuesta elegida se lleve al delta sin pasar por una reformulación de la skill.

---

## Fuera de alcance en esta entrega

Diseñado, documentado y pospuesto hasta que el núcleo se use en una feature real:

- Triaje por riesgo de tres vías (DIRECTA / NORMAL / CRÍTICA)
- PR/FAQ como documento de origen enlazable desde `from:`. El **bucle de promesas con fecha de revisión** ya no está aquí: lo cubre el bloque `## Bets` del acta, con su `revisit:` y su `fatal:` (Fase 7)
- `trocear` / `construir` / `revisar` con git worktrees
- Diario de deriva con estadística acumulada que reescribe las plantillas
- Panel de salud de capabilities
- Consolidación automática del delta sobre la capability viva

De todos, el **panel de salud** es el siguiente con más valor: se deriva del JSON que `validate.py` ya produce en la Fase 1, así que es barato en cuanto haya specs reales que mostrar.
