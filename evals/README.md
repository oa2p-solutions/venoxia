# Evals de Venoxia

Trece casos que responden a una sola pregunta: **¿el sistema falla cuando debe y calla
cuando debe?** No miden si el modelo escribe bonito. Cada caso monta un proyecto de
juguete completo bajo `<caso>/project/`, pide capturar la salida JSON de la herramienta
determinista que corresponda, y puntúa **el contenido de ese JSON**, no la prosa de la
respuesta.

## Cómo se ejecutan

```bash
cd ~/Developments/ia/venoxia
claude plugin eval venoxia --ablation with-without \
  --allow-tools 'Bash(python3 *)' Write Read Glob Grep
```

El `--allow-tools` no es opcional: `Bash` y `Write` son herramientas con verja y sin ese
permiso de operador ningún caso puede ejecutar `validate.py` ni escribir el JSON que se
puntúa. Sin él los casos fallan por falta de permisos, no por regresión.

Variantes útiles:

```bash
# un solo caso
claude plugin eval venoxia --case clean-spec --allow-tools 'Bash(python3 *)' Write

# solo los casos del validador
claude plugin eval venoxia --tag validator --allow-tools 'Bash(python3 *)' Write

# una sola pasada por caso, para iterar rápido mientras se depura un grader
claude plugin eval venoxia --runs 1 --allow-tools 'Bash(python3 *)' Write --keep-temp
```

El umbral por defecto es `1.0`: un caso solo pasa si pasan **todos** sus graders. Es
deliberado. Los graders no miden estilo, miden aritmética; si uno falla, algo ha
cambiado de verdad.

## Qué mide cada caso

| Caso | Qué monta | Qué tiene que pasar |
|---|---|---|
| `clean-spec` | Delta de dos requisitos sobre una capability viva de dos, todo conforme, más dos lecturas que coinciden | El validador acepta (`ok: true`, cero errores, cero avisos, `findings` vacío) **y** la divergencia converge |
| `missing-oracle` | `R-INV-002` nace sin `verifies:` | Rechazo con **V06** y solo con V06, nombrando `R-INV-002` |
| `budget-exceeded` | 2 de 5 requisitos en `confidence: low` (40 %) | Rechazo con **V11** y solo con V11, con `budget.low = 2` y `budget.total = 5` |
| `ambiguous-status-code` | El escenario dice que la petición «se rechaza» sin fijar el código | Divergencia **dura** en `status_code`: 409 contra 422, con pregunta cerrada |
| `ambiguous-partial-effect` | El requisito dice que el sistema «reserva lo que puede» | Divergencia **dura** en `side_effects` (pedido completo contra unidades con stock) y **blanda** en `effect` |
| `oracle-red-then-green` | Change `validated` con dos requisitos: uno con marcador de fallo para el runner falso, otro que pasa tal cual | El oráculo distingue: `R-CHK-001` en `green`, `R-CHK-002` en `red`, `all_green: false` |
| `diverge-root-decision` | Tres escenarios del mismo requisito dicen «se rechaza» sin fijar el código, y las lecturas los resuelven los tres como 409 y 422 | Tres divergencias **duras** en `status_code` y **una sola** entrada en `decisions`, con razón `same-readings-across-scenarios`, que nombra los tres escenarios |
| `diverge-policy-decision` | Tres notaciones de un importe en CLP («1.468.135,00», «1.468.135.00», «$ 1.500.000.-») que las lecturas resuelven con la misma conducta y cifras distintas, más un `decisions.json` antiguo con una respuesta a mano («2 decimales») | Tres divergencias **blandas** en `effect` y **una sola** entrada en `decisions` con razón `same-policy-across-scenarios`, tres miembros con sus cifras e `input` literales, `status` `unclassified`, `decisions_pending: 1` y la clave `tool` |
| `charter-explained` | Esqueleto vacío y un mensaje que ya cuenta propósito, usuario, apaño, primera capability, «Done when» y fuera de alcance | El acta se redacta antes de preguntar: ninguna pregunta por lo ya contado, una confirmación como mucho, linter en verde y las palabras del usuario en el acta |
| `charter-vague-pain` | Esqueleto vacío y una molestia sin nombre, con el relato que el usuario soltaría si se le pregunta bien | La primera pregunta es la narrativa literal y la segunda la de qué eliminar primero; el acta sale con la jefa de cocina y el último pedido |
| `charter-brownfield` | Paquete Python real (`pyproject.toml`, `pytest`, tres módulos, README) y el cambio que el usuario quiere hacer ahora | Capabilities reconstruidas del código, el cambio nuevo en la fila 1, ninguna pregunta por stack ni comando de pruebas, `venoxia.json` con `pytest` |
| `charter-changes-mind` | El usuario explica el producto y a mitad corrige quién lo usa | El acta refleja la corrección (usuaria, apaño, capability 1) y conserva propósito y fuera de alcance |
| `charter-multi-slot` | Un solo párrafo que rellena apaño, capability, «Done when» y fuera de alcance a la vez | Ninguna pregunta por una casilla que el párrafo ya rellenó |
| `charter-resume` | Acta existente con dos capabilities y dos apuestas, y un usuario que quiere continuar | Una sola pregunta con tres intenciones, ninguna por apuesta, el acta intacta y el `/venoxia:specify` de la siguiente capability en la entrega |

### `clean-spec` es el caso que más importa

Los otros cuatro comprueban que el sistema grita. Este comprueba que **no grita cuando no
debe**, que es el fallo que mata la adopción de una herramienta de este tipo: un
validador que da falsos positivos se desinstala el primer viernes. Su fixture pasa las
dieciocho reglas sin un solo aviso y sus dos lecturas convergen. Cualquier regresión que
introduzca ruido — una regla nueva demasiado celosa, un umbral de similitud mal puesto en
`diff_readings.py` — lo tumba antes que ningún otro caso.

Sus cifras exactas son parte del contrato del caso: 4 requisitos, 0 en `low`,
`findings: []`. Si al añadir una regla estas cifras cambian, hay que decidir a
conciencia si cambia el fixture o si la regla nueva está mal.

## Los casos de la entrevista del acta

Los seis casos `charter-*` miden la **entrevista** de `/venoxia:charter`, y ahí `claude
plugin eval` tiene un límite conocido: no simula a un usuario que contesta, así que
`AskUserQuestion` no puede usarse. El protocolo lo declara en vez de esquivarlo: el
mensaje trae todo lo que el usuario sabe, prohíbe la herramienta, y pide al modelo que
anote en `interview-log.json` cada pregunta que **habría hecho** —con su casilla del mapa
de cobertura, su tipo (`question` o `confirmation`), su texto literal y la respuesta
tomada del mensaje— y que guarde la última salida de `charter_lint.py` en
`charter-lint-result.json`. Los graders puntúan esos dos ficheros y el acta escrita:

- `tool_used` sobre `AskUserQuestion` con `max: 0`: la herramienta no se tocó.
- `regex` sobre `charter-lint-result.json` (`"ok": true`) y sobre el acta (sin la marca
  `<!-- inferred -->`): el acta pasa el linter y no le queda ninguna inferencia sin
  confirmar. Desde la 0.6.0 la skill deja además `.venoxia/charter-log.json` con cada
  inferencia, pregunta y decisión propia y la versión del plugin que la hizo; los casos
  no lo puntúan todavía (sin usuario simulado, todas sus inferencias quedarían
  `pending`), y es el primer grader que conviene añadir cuando la eval pueda contestar.
- `regex` sobre `interview-log.json`: en el modo de idea difusa, que las dos primeras
  preguntas sean las literales de la skill; en los de producto explicado y respuesta
  múltiple, que no haya ninguna `question` por una casilla que el mensaje ya rellenaba;
  en el de proyecto existente, ninguna pregunta por el stack ni el comando de pruebas;
  en el de retomar, una sola pregunta con las tres intenciones y ninguna por apuesta.
- `regex` sobre el acta: las palabras del usuario, la fila 1 correcta, el fuera de
  alcance que dictó.
- Un `llm` por caso, con peso `0.5`, para lo que la expresión regular no sabe juzgar:
  que el orden de la entrevista sea el del modo.

Lo que estos casos **no** miden, y conviene decirlo: cómo reacciona la entrevista a una
respuesta que llega a medias o cambia de tema, porque en la eval las respuestas están
escritas de antemano. Eso sólo lo mide el dogfooding sobre un proyecto real.

## Por qué los graders no puntúan la prosa

Un grader que pregunte «¿la respuesta menciona la ambigüedad?» no vale nada: aprueba a un
modelo que se inventa la respuesta correcta sin ejecutar nada. Aquí cada caso pide guardar
la salida JSON **íntegra y sin retocar** del script en un fichero del directorio de
trabajo (`validation-result.json` o `divergence-result.json`), y los graders son
expresiones regulares sobre ese fichero:

- `tool_used` sobre `Bash` con `input_match` comprueba que el script se ejecutó de verdad.
- `file_exists` comprueba que la salida se capturó.
- `regex` sobre `source: file` comprueba el código de regla, la severidad, el requisito
  nombrado, la aritmética del presupuesto y los recuentos de divergencia.
- Un `regex` con `not_contains` y `lookahead` (`"rule":\s*"(?!V06")`) comprueba que el
  caso falla **por la regla concreta** y no por cualquier otra cosa. Sin él, un error de
  sintaxis en el fixture pasaría por éxito: el validador fallaría, sí, pero por el motivo
  equivocado.
- Un `regex` con `not_contains` sobre `Traceback (most recent call last)` en la traza
  comprueba que ningún script vomita una excepción cruda de Python.

Solo hay tres graders de LLM en toda la batería, uno en cada caso de ambigüedad y uno en
el de agrupación, con peso `0.5`, y sirven para algo que una expresión regular no sabe
juzgar: que la pregunta generada sea **cerrada y enfrente las dos lecturas** —o, en la
agrupada, que nombre los tres escenarios en una sola—, en vez de un «¿hay algo ambiguo
aquí?». Son complemento, nunca criterio principal.

El grader `venoxia-skill-fired` lleva `arm: with-only`: bajo `--ablation with-without` no
puntúa, es el indicador de que el plugin ha disparado. La rama sin plugin corre los mismos
graders y debe hundirse: sin Venoxia no hay `V06`, ni `V11`, ni aritmética de divergencia.

## Anatomía de un caso

```
<caso>/
├── case.yaml            esquema 1.0 · prompt, permisos y graders
└── project/             el proyecto de juguete, montado como directorio adicional
    ├── .venoxia/
    │   ├── principles.md
    │   ├── capabilities/<nombre>/spec.md      la capability viva
    │   └── changes/<id>/
    │       ├── change.json
    │       ├── proposal.md
    │       ├── delta/<capability>.md
    │       └── readings/                      solo donde hay que comparar lecturas
    │           ├── reader-a.json
    │           ├── reader-b.json
    │           └── devils-advocate.json
    ├── prfaq/<documento>.md                   el origen que citan los `from:`
    └── test/<capability>/<oráculo>.spec.ts    los ficheros que citan los `verifies:`
```

Las lecturas de los cuatro casos que las usan vienen **prefabricadas**. No se despachan
lectores en la eval: si la comparación dependiera de lo que dos agentes contesten ese día,
el caso mediría el humor del modelo y no la aritmética de `diff_readings.py`. Los ficheros
de test existen de verdad y llevan su `@covers`, porque V07 y V08 los buscan en disco.

## Cifras que los graders dan por buenas

Comprobadas ejecutando `validate.py` y `diff_readings.py` a mano sobre cada fixture
antes de publicar la batería, y contrastando cada expresión regular contra su salida
real. `clean-spec` pasa además en modo `--strict`.

| Caso | `validate.py --json` | `diff_readings.py --json` |
|---|---|---|
| `clean-spec` | `ok: true` · 0 errores · 0 avisos · 4 requisitos · `low: 0` | `converged: true` · hard 0 · soft 0 · gaps 0 · 3 escenarios · 2 lectores |
| `missing-oracle` | `ok: false` · 1 error (V06 en `R-INV-002`) · 0 avisos · 3 requisitos | — |
| `budget-exceeded` | `ok: false` · 1 error (V11) · 0 avisos · 5 requisitos · `low: 2` · ratio 0.4 | — |
| `ambiguous-status-code` | `ok: true` (la ambigüedad es invisible al validador, y eso es la tesis) | `converged: false` · hard 1 · soft 0 · gaps 0 |
| `ambiguous-partial-effect` | `ok: true` | `converged: false` · hard 1 · soft 1 · gaps 0 |
| `oracle-red-then-green` | no aplica (no se ejecuta `validate.py`) | no aplica (no se ejecuta `diff_readings.py`) |
| `diverge-root-decision` | `ok: true` | `converged: false` · hard 3 · soft 0 · gaps 0 · 4 escenarios · `decisions` con 1 entrada de 3 miembros |
| `diverge-policy-decision` | `ok: true` | `verdict: soft_only` · hard 0 · soft 3 · gaps 0 · 3 escenarios · `decisions` con 1 entrada `same-policy-across-scenarios` de 3 miembros · `status: unclassified` · `decisions_pending: 1` · salida 0 |
| `charter-resume` | no aplica; su acta pasa `charter_lint.py --strict` con 0 errores y 0 avisos | no aplica |
| `charter-*` (los otros cinco) | no aplica: el acta la escribe la eval | no aplica |

Que los dos casos de ambigüedad pasen el validador no es un descuido: es el argumento
entero del motor de divergencia. Una especificación puede cumplir las dieciocho reglas y
seguir admitiendo dos lecturas incompatibles. El validador comprueba la forma; la
divergencia comprueba el significado.

Ninguno de los fixtures que pasan por `validate.py` trae `oracle.json`: esos changes se quedan en
`draft`, sin oráculo grabado, así que `V17` (que sólo mira changes en `verified`) y `V18`
(que sólo mira changes con `oracle.json`) no se evalúan sobre ninguno de los cinco y las
cifras de la tabla de arriba no cambian por su llegada.

`oracle-red-then-green` es distinto: no pasa por `validate.py` ni por
`diff_readings.py`, pasa por `oracle.py`. Su change `2026-09-04-oracle-demo` está
`validated` con dos requisitos; `R-CHK-001` (`test/checkout/receipt.spec.ts`) no lleva
marcador y el runner falso lo da por bueno, `R-CHK-002`
(`test/checkout/refund.spec.ts`) lleva `// RESULT: red` y el runner falso sale con `1`.
Comprobado a mano:

```bash
python3 scripts/oracle.py --root evals/oracle-red-then-green/project \
  --change 2026-09-04-oracle-demo --json --no-color
```

produce `all_green: false`, `all_red: false` y `counts` de `green: 1`, `red: 1`,
`missing: 0`, `timeout: 0`, `total: 2` — las cifras que sus graders dan por buenas.

## Cuando un caso falla

1. Ejecuta el script a mano contra el fixture y mira el JSON:
   ```bash
   python3 scripts/validate.py --root evals/clean-spec/project --json
   python3 scripts/diff_readings.py \
     --readings evals/clean-spec/project/.venoxia/changes/2026-08-31-stock-reservation/readings \
     --json
   ```
   Si el JSON ya sale mal aquí, la regresión está en el script y la eval ha hecho su
   trabajo.
2. Si el JSON sale bien a mano pero el caso falla, el problema está en el camino del
   agente: no encontró `project/`, no guardó el fichero o lo retocó. Repite con
   `--runs 1 --keep-temp` y lee la traza del sandbox que se conserva.
3. Los resultados de cada ejecución quedan en `evals/results/<marca de tiempo>/`, que está
   en `.gitignore`.
