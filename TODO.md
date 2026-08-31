# Venoxia · TODO de construcción

> Núcleo verificable como plugin de Claude Code.
> Diseño completo: https://claude.ai/code/artifact/6efadf27-49e2-4f6c-8398-e23cd3823d48

---

## Contexto

**Tesis:** una especificación es una apuesta sobre el comportamiento futuro de un sistema, y toda apuesta debe declarar cómo se resuelve y cuánto se confía en ella.

Lo que distingue a Venoxia de las herramientas existentes: la spec deja de ser prosa y pasa a ser un contrato que **falla en CI cuando miente**. Cada requisito nace con su oráculo de verificación y su nivel de confianza; sin oráculo, no compila.

Esta entrega cubre el **núcleo verificable** (fases 01-03 del diseño): formato del requisito, validador determinista, guardián que lo hace inevitable, y motor de divergencia. Es el 70% del valor y se prueba contra una feature real en días.

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

Las skills de plugin se invocan como `/<plugin>:<skill>`, así que el prefijo `vx-` sería redundante. **Nombres definitivos:** `/venoxia:specify`, `/venoxia:validate`, `/venoxia:diverge`. Actualizar el artifact al cerrar la entrega.

---

## Arquitectura

```
venoxia/
├── .claude-plugin/
│   ├── plugin.json               manifiesto
│   └── marketplace.json          marketplace de un solo plugin
│
├── skills/
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
│   └── venoxia/
│       ├── parser.py
│       ├── model.py
│       └── report.py
│
├── templates/
│   ├── capability.md
│   ├── delta.md
│   └── proposal.md
│
├── evals/                        casos para `claude plugin eval`
├── tests/                        pytest sobre validate.py y el parser
├── README.md
└── LICENSE
```

**Lo que el plugin crea en el proyecto del usuario:**

```
.venoxia/
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
  expires:  2026-10-30
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
| `V10` | `confidence: low` obliga a `expires:` con fecha futura | error |
| `V11` | Presupuesto de incertidumbre: ≤30% de requisitos con `low` | error |
| `V12` | El delta declara al menos un bloque `## ADDED\|MODIFIED\|REMOVED\|RENAMED Requirements` | error |
| `V13` | Los IDs de `MODIFIED`/`REMOVED` existen en la capability viva | error |
| `V14` | Sin `SHALL`/`MUST` en el cuerpo | warning |
| `V15` | `from:` ausente en una capability nueva | warning |
| `V16` | Test con `@covers` de un ID inexistente → comportamiento no especificado | warning |

- [x] Flag `--strict` (warnings cuentan como fallo) y códigos de salida `0` / `1`
- [x] `tests/` con pytest: un fixture por regla, en positivo y negativo. **Única parte con cobertura obligatoria** — de este componente depende la credibilidad de todo lo demás
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
  - `effect` con similitud por tokens bajo umbral → divergencia blanda
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

- [ ] **Confirmar antes de crear nada remoto.** Crear `oa2p-solutions/venoxia` privado y empujar
- [x] `.claude-plugin/marketplace.json` — un solo plugin. **Corrección sobre el diseño:** `claude plugin validate` rechaza `source: "git"` («plugins.0.source: Invalid input»); la forma válida que conserva la misma URL es `{source: "url", url: "https://github.com/oa2p-solutions/venoxia.git"}`
- [x] `README.md` en español: qué es, la tesis en tres frases, instalación, el formato del requisito, y **el modelo de confianza del guardián** (qué bloquea y cómo desactivarlo)
- [x] Instalación para el equipo:
  ```bash
  claude plugin marketplace add oa2p-solutions/venoxia
  claude plugin install venoxia@venoxia
  ```
- [ ] `claude plugin tag` para la release `venoxia--v0.1.0`

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
- [x] 8. `python3 -m pytest tests/ -q` en verde
- [x] 9. `claude plugin validate . --strict` y `claude plugin eval venoxia` en verde

---

## Fuera de alcance en esta entrega

Diseñado, documentado y pospuesto hasta que el núcleo se use en una feature real:

- Triaje por riesgo de tres vías (DIRECTA / NORMAL / CRÍTICA)
- PR/FAQ y el bucle de promesas con fecha de revisión
- `trocear` / `construir` / `revisar` con git worktrees
- Diario de deriva con estadística acumulada que reescribe las plantillas
- Panel de salud de capabilities
- Consolidación automática del delta sobre la capability viva

De todos, el **panel de salud** es el siguiente con más valor: se deriva del JSON que `validate.py` ya produce en la Fase 1, así que es barato en cuanto haya specs reales que mostrar.
