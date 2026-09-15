# Venoxia · rediseño de la entrevista de `/venoxia:charter` (y la agrupación de `/venoxia:diverge`)

**Fecha:** 2026-09-15 · **Estado:** propuesta, pendiente de aprobación · **Origen:** petición del usuario (la entrevista actual resulta redundante, tarda en llegar al desarrollo y vuelve a preguntar lo ya dicho)

Este documento no cambia el plugin. Analiza la skill instalada (`skills/charter/SKILL.md`, 449 líneas, tras los tres retoques del 2026-09-14), propone el rediseño y enumera los changes de Venoxia que lo ejecutarían. Cuando se apruebe, es el `from:` de sus requisitos.

---

## 1 · Mapa de las preguntas actuales y la casilla que intenta completar cada una

Casillas del mapa nuevo: `purpose`, `primary_user`, `current_workaround`, `first_capability`, `done_when`, `out_of_scope`, `evidence`, `bets`, `domain_decisions`. «—» significa que la pregunta no escribe ninguna casilla del acta.

| Dónde | Pregunta actual (literal o resumida) | Casilla | Observación |
|---|---|---|---|
| Paso 2 | Por cada apuesta viva: «¿ese hecho ya ha ocurrido?» | `bets` | Una pregunta por apuesta, antes de saber qué quiere hacer el usuario |
| Paso 2 | «¿Continuar, revisar una sección o empezar de cero?» | — (control) | Correcta, pero llega después del interrogatorio de apuestas |
| Tanda A·1 | «Cuando esto funcione, ¿qué podrá hacer alguien que hoy no puede?» | `purpose` (y de facto `first_capability`) | Pide imaginar el futuro; vuelve vacía en el caso difuso |
| Tanda A·2 | «¿Quién tiene hoy ese problema?» | `primary_user` | Casi siempre está en la primera frase del usuario |
| Tanda B | «¿Y cómo se apaña hoy?» | `current_workaround` (+ candidata a `first_capability`, + `evidence`) | La mejor pregunta de la skill: una respuesta rellena tres casillas |
| Tanda C·1 | «Si sólo pudieras entregar una cosa el mes que viene, ¿cuál eliges, y qué podría hacer tu usuario ese día?» | `first_capability` | **Duplica A·1** («qué podrá hacer») |
| Tanda C·2 | «¿Qué tendría que pasar para que dijeras que eso ya funciona? ¿Quién lo ve y qué ve?» | `done_when` | Necesaria; casi nunca viene dada |
| Tanda D·1 | «¿Qué va a seguir haciendo tu usuario en otro sitio, igual que hoy? ¿Quién se lo resuelve?» | `out_of_scope` | Necesaria cuando no se infiere del apaño |
| Tanda D·2 | «¿Con qué otra herramienta van a confundir esto…?» | `out_of_scope` | Repesca de D·1 |
| Tanda E.1 | «¿Qué has visto, y cuántas veces?» sobre el propósito **y** sobre la fila 1 | `evidence` | **Vuelve a entrevistar** sobre casillas ya contestadas; la evidencia suele estar en la historia de la Tanda B |
| Tanda E.1 | «¿Qué verías que te haría cambiar de opinión?» (por apuesta `low`) | `bets.why` | Sólo tiene sentido sobre apuestas reales abiertas |
| Tanda E.1 | «¿Y qué tendría que pasar para que pudieras verlo?» (por apuesta `low`) | `bets.revisit` | Ídem |
| Tanda E.1 | «Si esto sale mal, ¿el proyecto sigue teniendo sentido?» | `bets.fatal` | Ídem; sólo sobre la apuesta que sostiene el propósito o la fila 1 |
| Tanda E.2 | «Para que esta fila valga, ¿alguien tiene que hacer algo que hoy no hace?» (+ 3 subpreguntas si sí) | `bets` | Legítima; pero se puede **deducir de la celda `Done when`** (es lo que `C19` detecta) y preguntar sólo si la celda lo implica |
| Tanda F | Selección múltiple de convenciones técnicas (tabla genérica de seis) | — (contrato técnico) | **Otra fase**; la tabla genérica se ofrece aunque no sea relevante |
| Tanda F | «¿Con qué comando corren los tests de este proyecto?» | — (`venoxia.json`) | **Otra fase**; detectable en el repo |
| Paso 4 | «La fila 2 compara por precio y plazo. Si uno es más barato y tarda un mes más, ¿cuál gana?» | `domain_decisions` | Correcta y condicional (sólo si una fila arbitra) |
| Paso 4 | Confirmar los principios de dominio cazados al vuelo | `domain_decisions` | Correcta; cabe en la confirmación general del borrador |
| Paso 5 | «¿Cerrar ya o seguir con una sección concreta?» | — (control) | Correcta; es la salida |
| Paso 6 | «¿El esqueleto ya está / falta / escribe el acta igualmente?» | — (onboarding operativo) | **Otra fase** |
| Paso 7 | Por cada dolor del `**hoy:**` sin destino: «¿lo resuelve el sistema o se sigue resolviendo como hoy?» | `out_of_scope` / fila de la tabla | Correcta, pero una pregunta por cabo; cabe como inferencia marcada en el borrador |
| Paso 9 | Preguntas de remedio del linter (`Done when` vacío, no-alcance, `hoy`/`con esto`, `high` sin apuesta, `C17`–`C20`) | la casilla que falte | Correctas: son la red de seguridad |
| «Cuando la respuesta no es una respuesta» | «Cuéntame el último que hiciste…» | `current_workaround` + `evidence` | **Debería ser la primera pregunta del modo difuso**, no la reacción a un fallo |

Recuento de una entrevista limpia hoy, sin retomar nada: A (2) + B (1) + C (2) + D (1) + E.1 (2, más 2–3 por cada apuesta `low`) + E.2 (1, más 3 si la respuesta es sí) + F (2) + dominio (0–1) + guardián (1) + cabos sueltos (1–2) + cerrar (1) → **entre 14 y 22 preguntas**. Con el «camino corto» del Paso 1 (producto ya explicado), el mínimo del Paso 5 sigue exigiendo la Tanda E entera sobre propósito y fila 1, la F y el guardián: **8–10 preguntas** para alguien que ya lo ha contado todo.

## 2 · Preguntas redundantes o que pertenecen a otra fase

**Redundantes (se eliminan o se funden):**

1. A·1 y C·1 preguntan lo mismo (el resultado futuro). Queda una sola casilla `first_capability`, que en el modo difuso se obtiene de «qué parte del proceso eliminarías primero» y en los demás modos viene dada.
2. A·1, A·2, B y la primera capability se sacan de **una sola historia** (la última vez que ocurrió el problema). Hoy son cuatro preguntas en dos tandas.
3. E.1 vuelve a entrevistar sobre propósito y fila 1. Pasa a ser una **síntesis** (observado / supuesto / por qué) con **una sola corrección general**; `why`, `revisit` y `fatal` sólo para las apuestas que sigan abiertas después de la corrección.
4. E.2 se pregunta sólo cuando la celda `Done when` o «Qué podrá hacer» implique que una persona hace algo que hoy no hace (el mismo criterio que `C19` aplica al fichero). Si la celda no lo implica, no hay pregunta.
5. Paso 2: las apuestas se muestran **agrupadas** y sólo se resuelven las que el usuario elija.
6. Paso 7: los cabos sueltos del `**hoy:**` se colocan como **inferencias marcadas** en el borrador (`out_of_scope` inferido con su porqué) y se confirman en la corrección general, no uno a uno.

**De otra fase (salen de la entrevista de producto a una «preparación» breve posterior al acta):**

7. Convenciones técnicas (Tanda F, Paso 4 «De convención técnica»).
8. Comando de tests y `venoxia.json` (Tanda F, Paso 8).
9. Aviso y pregunta del guardián y el esqueleto (Paso 6).
10. Directorios de capabilities (Paso 10; sigue siendo «sólo si se piden»).

**Contradicción interna que se corrige:** el Paso 1 dice «se redacta primero y se pregunta después» cuando el producto viene claro, pero el mínimo del Paso 5 exige después las dos mitades de la Tanda E, la F y el Paso 6. El nuevo mínimo (sección 3.4) es el que manda, y el borrador precede a la primera pregunta.

## 3 · El flujo nuevo

### 3.1 · El mapa de cobertura

Antes de la primera pregunta, y después de **cada** respuesta, la skill mantiene un mapa de nueve casillas con un estado cada una:

| Estado | Significado | Qué hace la skill con ella |
|---|---|---|
| `known` | el usuario lo dijo explícitamente | va al borrador con sus palabras, sin marca |
| `inferred` | se deduce de lo dicho, pero no está dicho | va al borrador **marcada como inferencia**, se confirma en la corrección general; nunca se pregunta sola |
| `missing` | falta y bloquea el acta mínima | es la única que justifica una pregunta |
| `optional` | puede completarse después | no se pregunta; se ofrece en «profundizar» |
| `conflicting` | dos interpretaciones incompatibles de lo dicho | se pregunta, con las dos interpretaciones como opciones literales |

Reglas del mapa:

- **Casillas bloqueantes:** `purpose`, `primary_user` (con su `hoy` y su `con esto`), `first_capability`, `done_when`, `out_of_scope`, `evidence` (la clasificación hechos/apuestas confirmada) y `domain_decisions` **sólo si** la fila 1 arbitra entre alternativas. `bets` no bloquea (ver 3.3). El resto de filas, usuarios y apuestas son `optional`.
- **Antes de cada pregunta, la skill nombra la casilla** en el mensaje que precede a la llamada (`→ done_when`). Si la casilla no está en `missing` ni en `conflicting`, la pregunta no se hace. Dos preguntas con la misma casilla objetivo son, por definición, una redundancia.
- **Una respuesta puede completar varias casillas.** Tras cada respuesta se re-evalúa el mapa entero, no sólo la casilla preguntada.
- **Una corrección invalida sólo lo que depende de ella.** Dependencias: `primary_user` → `current_workaround` → `first_capability` → `done_when`; `first_capability` → `out_of_scope` y `domain_decisions`; `evidence` cuelga de cada casilla por separado. Corregir el `Done when` no toca el propósito; corregir el usuario devuelve apaño y capability a `inferred` (no a `missing`) si siguen siendo plausibles.
- El mapa **no se persiste** en un fichero: se enseña en la conversación (tabla de «qué entendí») y su oráculo en disco es el propio linter, cuyas reglas cubren las casillas bloqueantes (`C02` propósito, `C03` usuario con `hoy`/`con esto`, `C04`/`C07`/`C08` capability y `Done when`, `C10` no-alcance, `C17` desempate, `C20` apuestas). Ver decisión D-B.

### 3.2 · Los tres modos de entrada (y el cuarto: retomar)

La skill lee la sala (disco y mensaje) y clasifica **una vez**, diciéndolo en una línea.

**Modo 1 · Producto ya explicado** (dijo qué construye, para quién y qué problema resuelve). Redacta el acta completa antes de la primera pregunta; marca las inferencias; la primera y normalmente única llamada es la **confirmación general** (corregir/aprobar el borrador, incluida la síntesis hechos/apuestas). Después, como máximo una pregunta por una casilla `missing` o `conflicting` (casi siempre `done_when`). Nunca vuelve a preguntar propósito, usuario ni primera capability.

**Modo 2 · Proyecto existente** (hay código o documentación). Reconstruye propósito, usuarios, capabilities y restricciones desde `README`, manifiestos, tests y código; presenta esa lectura **para corregirla** (1 pregunta); pregunta **qué cambio quiere hacer ahora** (1 pregunta, dependiente de la anterior); la fila 1 es lo primero que se va a especificar, y explica **una sola vez** que `#` es el orden de adopción de Venoxia, no el de programación. No pregunta stack, comando de tests ni comportamiento que el disco demuestra. Las filas de lo que ya funciona llevan un `Done when` de «sigue siendo cierto».

**Modo 3 · Idea difusa** (no sabe describir el producto). No pide imaginar el futuro. Primera pregunta, literal:

> «Cuéntame la última vez que ocurrió el problema: quién estaba intentando hacer qué, qué pasos siguió y dónde perdió más tiempo o cometió errores.»

De esa respuesta extrae usuario, proceso actual, dolor, evidencia, propósito preliminar y candidata a primera capability. Segunda pregunta, literal:

> «¿Qué parte de ese proceso eliminarías primero y qué tendría que ver esa persona para considerar que ya funciona?»

Produce `first_capability` y `done_when`. Sólo después, y sólo si sigue `missing`, pregunta la frontera (`out_of_scope`) en positivo, como hoy. Luego la síntesis hechos/apuestas (una corrección general) y la oferta de cierre.

**Retomar un acta** (existe `.venoxia/charter.md`). Pasa el linter, resume en cuatro líneas (propósito, fila 1 con su `Done when`, estado del linter, bloqueos), enseña **todas las apuestas abiertas en una sola vista** con su `revisit`, y hace **una** pregunta: continuar con la siguiente capability / revisar una sección (cuál) / resolver una apuesta cuyo hecho ya ocurrió (cuál). «Empezar de cero» queda como respuesta escrita, con el aviso de que pisa el acta. Nunca pregunta apuesta por apuesta antes de saber qué quiere hacer. Nunca usa `mtime` para adivinar el objetivo de la sesión.

### 3.3 · Hechos y apuestas: síntesis, no interrogatorio

Una sola vez, la skill presenta tres listas: **lo que entendió como observado** (con la frase del usuario que lo demuestra: «lo hago cada mes», «me lo han pedido tres clientes»), **lo que entendió como supuesto** (sin evidencia mencionada, o en futuro condicional), y **por qué** clasificó cada uno así. Pide una **sola corrección general**. Sólo para las apuestas que queden abiertas pregunta `revisit` (el hecho, nunca una fecha) y, únicamente para la que sostiene el propósito o la fila 1, `fatal`. `why` sale de la propia síntesis.

Si el usuario afirma que todo está observado, **no se fabrica ninguna apuesta**: `## Bets` queda vacía, `C20` avisa, la afirmación queda registrada como comentario bajo la sección (`<!-- El usuario afirmó el <fecha> que todo lo que el acta declara está observado; C20 se deja puesto a propósito. -->`) y la entrega lo dice. Ver decisión D-D.

### 3.4 · La frontera mínima y el cierre

El acta mínima existe cuando hay: un propósito · un usuario principal con su hoy y su con esto · una capability prioritaria · un `Done when` observable · un no-alcance razonado · la clasificación hechos/apuestas confirmada · una decisión de dominio **sólo si** la fila 1 arbitra. Al alcanzarlo, la skill presenta el borrador completo y pregunta **aprobar** o **profundizar en una sección concreta**. No sigue entrevistando por iniciativa propia; el tope de seis tandas sin `Done when` observable se conserva como hallazgo («el proyecto no está en condiciones de spec»).

### 3.5 · La preparación (después del acta, breve)

Con el acta aprobada y el linter en verde:

1. **Comando de tests.** Se detecta en el repo (`package.json` → `scripts.test`; `pyproject.toml`/`pytest.ini`/`tests/` → `pytest` o `unittest`; `Cargo.toml` → `cargo test`; `go.mod` → `go test ./...`; `Makefile` con `test:`). Si la detección es unívoca, se escribe `venoxia.json`; si hay dos candidatos, una pregunta con los candidatos literales; si no hay nada, no se escribe y se dice (como hoy). Ver D-F.
2. **Convenciones técnicas.** Sólo las que la fila 1 o el repo hagan relevantes (la fila 1 maneja dinero → «enteros en la unidad mínima»; expone una API → «errores `4xx`/`5xx`»). **Nunca la tabla genérica de seis.** Las aprobadas siguen yendo a `technical-contract` y a la entrega con su `/venoxia:specify`; las abiertas a `## Bets` (R-CHL-006 intacto). Si ninguna es relevante, no se plantea ninguna y se dice en una línea.
3. **Guardián y esqueleto.** Si el disco tiene esqueleto (manifiesto o `src/`), una línea de aviso, sin pregunta. Si no lo tiene, la pregunta actual de tres opciones, aquí y no en la entrevista. Ver D-G.
4. Directorios de capabilities: sin cambios (sólo si se piden).

### 3.6 · Ejemplos antes / después

**Modo 1 · producto explicado.** Usuario: «Quiero una herramienta de línea de comandos que lea las facturas PDF de mis tres proveedores y me saque el CSV mensual para mi contable. Hoy copio los importes a mano de cada PDF a una hoja, me lleva una tarde al mes y me equivoco en los decimales.»

*Antes (skill actual, camino corto):* redacta un borrador, y aun así pregunta E.1 sobre el propósito, E.1 sobre la fila 1, E.2 sobre la fila 1, D·1 frontera, C·2 `Done when`, F convenciones (tabla de seis), F comando de tests, Paso 6 guardián, Paso 5 cerrar → **8–9 llamadas**.

*Después:*

> Lo que entendí (mapa): `purpose` known · `primary_user` known (tú, autónomo con tres proveedores) · `current_workaround` known (copiar a mano a una hoja) · `first_capability` known (extraer las líneas de las facturas a un CSV mensual) · `evidence` known (lo haces cada mes: observado) · `out_of_scope` **inferred** (la contabilidad la sigue haciendo el contable con su programa) · `done_when` **missing** · `bets` optional · `domain_decisions` no aplica (la fila 1 no arbitra).
>
> [borrador completo del acta, con `<!-- inferred -->` en la viñeta de no-alcance]
>
> → confirmación general · «¿Corrijo algo del borrador, o lo doy por bueno tal cual?» (opciones: tal cual / corrijo esto: …)
>
> → `done_when` · «¿Qué ve tu contable el día que esto funciona?» (opciones sacadas de lo dicho: «recibe un CSV con las líneas de los tres proveedores del mes, sin que yo haya tecleado ningún importe» / «abre el CSV en su programa y cuadra con las facturas sin corregir ningún decimal»)

Dos llamadas, acta escrita, linter en verde. Preparación: `package.json` con `"test": "vitest"` → `venoxia.json` escrito sin preguntar; ninguna convención relevante (CLI sin dinero ni API); esqueleto presente → una línea sobre el guardián.

**Modo 3 · idea difusa.** Usuario: «Algo que nos ayude con los informes mensuales.»

*Antes:* A·1 («¿qué podrá hacer alguien…?») vuelve vacía; la skill salta a B; luego C·1, C·2, D·1, E.1 ×2, E.2, F ×2, Paso 6, cerrar → **11–14 llamadas**, la primera de ellas pidiendo imaginar el futuro.

*Después:* «Cuéntame la última vez que ocurrió el problema…» → «El viernes pasado Marta, de operaciones, sacó los tres exports de la plataforma, los pegó en la plantilla, y se pasó la mañana cuadrando totales porque un export venía en otra moneda.» → mapa: usuario, apaño, dolor, evidencia (viernes pasado: observado), propósito preliminar, candidata (cuadrar los exports sin mano). «¿Qué parte de ese proceso eliminarías primero y qué tendría que ver Marta para considerar que ya funciona?» → fila 1 + `Done when`. Frontera: `inferred` (la plantilla la sigue diseñando Marta) → va al borrador marcada. Síntesis hechos/apuestas: «la moneda distinta pasa cada mes» es supuesto → una apuesta; `revisit` = «cuando hayan pasado tres cierres mensuales». Cierre: aprobar/profundizar. **Cinco llamadas.**

**Modo 2 · brownfield.** Repo con `README`, `pyproject.toml`, `src/`, `tests/`. *Antes:* la skill lee el disco y «dice en voz alta» el stack, pero después recorre las tandas y vuelve a preguntar el comando de tests en F y el esqueleto en el Paso 6. *Después:* lectura reconstruida (propósito del README, dos usuarios de la doc, tres capabilities del código con `Done when` de «sigue siendo cierto») → «¿Corrijo algo de esta lectura?» → «¿Qué cambio quieres hacer ahora?» → fila 1 = la capability que ese cambio toca (explicando una sola vez por qué el `#` es orden de adopción) → `Done when` del cambio si falta. **Dos o tres llamadas.** Preparación: `pytest` detectado, `venoxia.json` escrito; guardián: una línea.

**Retomar.** *Antes:* seis preguntas seguidas («¿ya ocurrió el hecho de B-001?» … «¿de B-006?») antes de preguntar qué quiere hacer. *Después:* resumen de cuatro líneas, tabla de apuestas abiertas con su `revisit`, y una pregunta: continuar con `#N` / revisar sección / resolver B-00x cuyo hecho ya ocurrió.

## 4 · Preguntas esperadas por modo

| Modo | Hoy (skill actual) | Nuevo: entrevista | Nuevo: preparación | Borrador |
|---|---|---|---|---|
| 1 · Producto explicado | 8–10 | **1–2** (confirmación general + ≤1 bloqueante) | 0–1 | antes de la primera pregunta |
| 2 · Proyecto existente | 10–14 | **2–3** (corregir lectura + qué cambio + ≤1 `Done when`) | 0 (todo detectado) | antes de la primera pregunta |
| 3 · Idea difusa | 14–22 | **4–7** (2 narrativas + ≤1 frontera + 1 síntesis + ≤2 `revisit`/`fatal` + 1 cierre) | 0–1 | tras la segunda respuesta |
| Retomar | 1 + una por apuesta viva | **1** (+ lo que pida) | 0 | no aplica |

En todos los modos, la salida es la misma pregunta: aprobar o profundizar. El máximo de una llamada de `AskUserQuestion` sigue siendo cuatro preguntas, pero el rediseño no lo necesita: casi todas las llamadas llevan una.

## 5 · Cambios necesarios

### Skills

- **`skills/charter/SKILL.md`** — reescritura del cuerpo (el frontmatter conserva `allowed-tools`; la `description` corrige «apuestas con fecha de revisión» por «con el hecho que las resuelve»). Estructura nueva: reglas (las cinco actuales, la 5 ampliada con el mapa) · el mapa de cobertura · los tres modos y retomar · la síntesis hechos/apuestas · la frontera mínima y el cierre · escribir el acta y los principios (Pasos 7, 8 y 9 actuales casi intactos) · **la preparación** (test command detectado, convenciones relevantes, guardián) · la entrega. Desaparecen los encabezados «Tanda A…F» y el Paso 6 como paso de la entrevista. Se conservan literalmente las frases que `tests/test_charter_skill.py` exige para R-CHL-006.
- **`skills/diverge/SKILL.md`** — Paso 1: con varios changes activos se pregunta cuál (opciones: los ids), sin `mtime`. Paso 4b: se itera sobre `decisions` del JSON, **una decisión por llamada**, en el orden del informe, con `question` y `options` literales del script; antes de la llamada, el mensaje explica la decisión raíz una vez y lista los escenarios afectados. Paso 4c: una entrada en `decisions.json` **por divergencia miembro** (mismo `answer`, misma `question`, y una clave nueva `decision` con el id del grupo) para conservar la trazabilidad individual. Las frases que `tests/test_diverge_skill.py` exige para R-DIV-009/010 se mantienen.

### Scripts

- **`scripts/diff_readings.py`** — agrupación determinista por **decisión raíz**, sin constantes nuevas:
  - *Misma lectura vista desde dos campos:* `effect` y `side_effects` del **mismo escenario** se agrupan cuando comparten al menos un token distintivo en **cada** lado (los tokens de contenido que sólo tiene un lector). En `ambiguous-partial-effect`: lado A comparte «pedido», lado B «unidades»/«stock» → una decisión.
  - *Mismas lecturas en escenarios distintos:* divergencias del **mismo campo** en escenarios distintos se agrupan cuando las lecturas normalizadas coinciden lector a lector (mismos códigos en `status_code`; mismas cifras y mismo conjunto de tokens distintivos en prosa). Igualdad, no similitud.
  - Todo lo demás queda individual. Ninguna divergencia se agrupa «para reducir la cantidad»; el informe dice **por qué** se agrupó (`reason`: `same-reading-two-fields` / `same-readings-across-scenarios` / `single`).
  - JSON: clave nueva `decisions` (lista que cubre **todas** las divergencias, singletons incluidos: `id` «D-1»…, `scenarios`, `fields`, `divergences` (índices), `hardness`, `reason`, `question`, `options`); `divergences` no cambia. Esquema versión 1 sólo crece (R-TEC-006). Markdown: sección «Decisiones» con los grupos de más de un miembro. Código de salida y `counts` intactos: las cifras de `evals/README.md` no se mueven.
- **`scripts/charter_lint.py`** — opcional (D-C): regla `C21`, error, «el acta conserva una inferencia sin confirmar» (`<!-- inferred -->` en cualquier línea). Convierte «el silencio no aprueba nada» en algo que el linter impone. Exige fila en el README (21 reglas), remedio en `skills/validate/SKILL.md`, test positivo y negativo, y `tests/test_docs_sync.py` lo audita solo.

### Plantillas

- `templates/charter.md`: sin cambios de forma. Si se aprueba D-C, el comentario guía de `## Bets` menciona la marca de inferencia y su regla.
- `templates/venoxia.json`: sin cambios.

### Tests (stdlib, patrón existente)

- `tests/test_charter_skill.py`: una clase por requisito nuevo (R-CHL-009…014), estructurales como las de R-CHL-006: nombres de las nueve casillas y los cinco estados, la regla «casilla `missing` o `conflicting` o no hay pregunta», las dos preguntas literales del modo difuso, «redacta antes de la primera pregunta» en el modo explicado, ausencia de los encabezados «Tanda», la preparación **después** de la sección de escritura (posición en el texto), la vista agrupada de apuestas al retomar, ausencia de `mtime`.
- `tests/test_diverge_skill.py`: `decisions`, «una decisión por llamada», clave `decision` en `decisions.json`, la pregunta por el change con varios activos.
- `tests/test_diff_readings.py`: agrupación intra-escenario sobre el fixture de `ambiguous-partial-effect` (1 decisión, 2 miembros), agrupación inter-escenario sobre un fixture nuevo (409/422 en tres escenarios → 1 decisión, 3 miembros), **no agrupación** de dos divergencias independientes (tokens distintivos disjuntos), `decisions` cubre todas las divergencias, `counts`/`exit_code` intactos.
- `tests/test_charter_lint.py`: `C21` positivo y negativo (si D-C).
- `tests/test_eval_fixtures.py`: cifras del caso `diverge-root-decision` (hard 3, decisions 1) y lint en estricto del acta del caso `charter-resume`.

### Evals

Hallazgo previo, verificado en la documentación oficial de `claude plugin eval` (`https://code.claude.com/docs/en/plugin-evals.md`): **no existe un usuario simulado multi-turno** (`context.history_file` sólo reanuda una conversación pasada) y **el comportamiento de `AskUserQuestion` dentro de una eval no está documentado**. Los graders disponibles son `regex` (sobre `last_message`, `trace`, `files` o un fichero; `match: contains|not_contains|count:N`), `tool_used` (`min`/`max`), `tool_order`, `file_exists`, `llm` (criterios, juez a 2 de 3) y `baseline`; hay `append_system_prompt`, `add_dirs` y `scaffold_script`.

Protocolo propuesto para los seis casos conversacionales (`evals/charter-*/`):

- Cada caso trae `project/` (vacío, brownfield, o con acta) y `persona.md`: el mensaje inicial del usuario y un **banco de respuestas por casilla** (`done_when: …`, `out_of_scope: …`, y «no sé» para lo que la persona no sabe), más, en el caso «cambia de opinión», la corrección que da al ver el borrador.
- `execution.append_system_prompt` declara la simulación: el usuario no está presente; cada vez que la skill fuera a llamar a `AskUserQuestion`, en su lugar añade la pregunta a `interview-log.json` (`turn`, `target` casilla, `question`, `answer` tomada de `persona.md` por casilla) y sigue; el borrador se escribe en `charter-draft.md` **antes** de la primera entrada del log cuando el modo lo pida; al terminar ejecuta `charter_lint.py --json` sobre el acta escrita y guarda `charter-lint-result.json`.
- Graders: `tool_used AskUserQuestion max: 0` (no se llama a la herramienta real; `arm: with-only`); `regex` sobre `interview-log.json` con `count:N` y lookahead para el máximo de preguntas y para que ninguna casilla aparezca dos veces como `target`; `tool_order` Write(`charter-draft.md`) antes de Write(`interview-log.json`) en los modos 1 y 2; `regex` sobre `charter-lint-result.json` (`"ok": true`, sin `C01`); `regex not_contains` sobre el acta de palabras que la persona nunca dijo (una «trampa» por caso: una moneda, un plazo, un segundo usuario); `llm` para contenido inventado (todo lo que el acta afirma está en `persona.md` o marcado como propuesta) y para «la primera pregunta del modo difuso pide el último caso real». Sin `Traceback` en la traza, como hoy.
- Casos: `charter-explained` (≤2 preguntas, borrador antes de la primera), `charter-vague-pain` (primera pregunta narrativa, ≤7), `charter-brownfield` (README + código: ninguna pregunta sobre stack, tests ni lo que el disco demuestra), `charter-changes-mind` (la corrección sólo invalida las casillas dependientes: el propósito del borrador 2 es el del borrador 1), `charter-multi-slot` (una respuesta marca ≥3 casillas: `target` de la siguiente pregunta no es ninguna de ellas), `charter-resume` (acta existente con tres apuestas: 1 pregunta, vista agrupada, ninguna pregunta por apuesta).
- `diverge-root-decision`: lecturas prefabricadas con 409/422 en tres escenarios; graders `regex` sobre el JSON de `diff_readings.py` (`"decisions"` con un solo grupo de tres miembros, `hard: 3`). Es el único caso determinista puro y entra en las cifras del README.
- Métricas pedidas y dónde se miden: cantidad de preguntas y repetidas → `interview-log.json` (regex); casillas por respuesta → `covers` en cada entrada del log (regex `count`); tiempo hasta el primer borrador → `tool_order` y `turn`; correcciones del usuario al borrador → entradas con `target: correction`; contenido inventado → `llm` + trampa regex; actas que pasan el linter → `charter-lint-result.json`.
- Límite que se declara en `evals/README.md`: la eval mide la **lógica** de la entrevista, no el manejo real de `AskUserQuestion`. Primer paso de la implementación: una pasada `--runs 1 --keep-temp` de prueba para observar qué hace la herramienta dentro de una eval.

### Documentación

- `README.md`: punto 1 de «Las siete skills» (modos, mapa, preparación) y punto 4 (decisiones raíz); paso 2 de «Empezar un proyecto desde cero»; tabla de reglas si hay `C21`.
- `CLAUDE.md`: la línea de `diverge` («una por llamada») pasa a «una decisión por llamada»; la fila de `diff_readings.py` menciona `decisions`.
- `evals/README.md`: filas nuevas, protocolo de persona, límite declarado.
- `TODO.md` (rama taller): nota de la corrección sobre el diseño.
- Ninguna plantilla de acta cambia de formato: los proyectos Venoxia existentes no se ven afectados.

### Correspondencia con los doce criterios verificables

| # | Criterio | Dónde se demuestra |
|---|---|---|
| 1 | Explicación clara → sin preguntas sobre lo ya dado | `charter-explained` (`target` ∉ {purpose, primary_user, first_capability}) |
| 2 | Borrador útil antes de la primera pregunta | `charter-explained`, `charter-brownfield` (`tool_order`) |
| 3 | Misma casilla objetivo = redundante | test estructural R-CHL-009 + regex «ninguna casilla dos veces» en los seis casos |
| 4 | Idea difusa empieza por el último caso real | `charter-vague-pain` (regex de la pregunta literal en el log + `llm`) |
| 5 | Brownfield sin preguntas sobre datos del disco | `charter-brownfield` (`target` ∉ {test_command, stack}; regex not_contains) |
| 6 | Convenciones sólo si son relevantes | `charter-explained` (CLI sin dinero ni API: ninguna entrada `target: convention`) + test estructural R-CHL-013 |
| 7 | Alcanzado el mínimo, ofrece cerrar | `target: close` es la última entrada del log en los seis casos + R-CHL-012 |
| 8 | Una respuesta completa varias casillas | `charter-multi-slot` (`covers` con ≥3 casillas) |
| 9 | Una corrección invalida sólo lo dependiente | `charter-changes-mind` (`llm` compara borradores 1 y 2) |
| 10 | Misma decisión raíz → una pregunta | `diverge-root-decision` + `tests/test_diff_readings.py` |
| 11 | Todas las secciones de `charter_lint.py` | `charter-lint-result.json` con `ok: true` en los seis casos |
| 12 | Reducir preguntas no permite inventar | `llm` + trampa regex en los seis casos; `C21` si se aprueba |

## 6 · Requisitos propuestos

Dos changes, ambos por el ciclo completo (`specify` → tests con `@covers` → `validate` → `diverge` → `verify` rojo → `implement` → `verify` verde → `close`), sin `via: direct`. Los IDs continúan los existentes (`R-CHL-008` y `R-DIV-012` son los últimos). Todos `ADDED`: ningún requisito vivo se modifica, así que no hace falta consolidar `charter-lint` ni `divergence` antes.

**Change A · `2026-09-15-charter-adaptive-interview`** · capability `charter-lint` · `verifies: tests/test_charter_skill.py` salvo el último.

| ID | Título | Enunciado EARS (resumen) |
|---|---|---|
| R-CHL-009 | The charter skill asks only for a missing or conflicting slot | WHEN la skill va a plantear una pregunta, DEBE nombrar antes la casilla del mapa (`purpose`, `primary_user`, `current_workaround`, `first_capability`, `done_when`, `out_of_scope`, `evidence`, `bets`, `domain_decisions`) y su estado (`known`, `inferred`, `missing`, `optional`, `conflicting`), y sólo preguntar si el estado es `missing` o `conflicting`; una respuesta re-evalúa el mapa entero y una corrección sólo invalida las casillas dependientes. |
| R-CHL-010 | The charter skill classifies the entry mode and drafts first when it can | WHEN empieza la entrevista, la skill DEBE clasificar el modo (producto explicado, proyecto existente, idea difusa, retomar); en los dos primeros redactar el acta antes de la primera pregunta con las inferencias marcadas; en el difuso abrir con la pregunta por la última vez que ocurrió el problema y seguir con la de qué parte eliminaría primero y qué tendría que ver esa persona. |
| R-CHL-011 | The charter skill never asks a project for what its disk already says | WHEN hay código o documentación, la skill DEBE reconstruir propósito, usuarios, capabilities y restricciones del repositorio, presentarlos para corregirlos, preguntar qué cambio quiere hacer ahora, y no preguntar por stack, comando de tests ni comportamiento que el disco demuestra; la prioridad se explica una sola vez como orden de adopción. |
| R-CHL-012 | Facts and bets are separated by one synthesis, and no bet is fabricated | WHEN el mapa tiene propósito y primera capability, la skill DEBE presentar hechos observados, supuestos y la razón de cada clasificación, pedir una sola corrección general, preguntar `revisit` y `fatal` sólo por las apuestas que queden abiertas, y con «todo está observado» dejar `## Bets` vacía, `C20` puesto y la afirmación registrada. |
| R-CHL-013 | Reaching the minimum offers to close | WHEN están propósito, usuario con hoy/con esto, capability prioritaria, `Done when` observable, no-alcance razonado, clasificación confirmada y —sólo si la fila 1 arbitra— la decisión de dominio, la skill DEBE presentar el borrador completo y preguntar aprobar o profundizar en una sección, y no seguir entrevistando por iniciativa propia. |
| R-CHL-014 | Technical preparation happens after the charter and only when relevant | WHEN el acta está aprobada y el linter en verde, la skill DEBE tratar comando de tests, convenciones técnicas, guardián y esqueleto en una preparación posterior, detectando primero lo que el repositorio dice, preguntando sólo ante una ambigüedad que impide el paso siguiente, y proponiendo una convención sólo si la fila 1 o el repositorio la hacen relevante, nunca una lista genérica. (R-CHL-006 sigue gobernando el destino de cada convención.) |
| R-CHL-015 | Resuming a charter starts from its state, not from its bets | WHEN existe `.venoxia/charter.md`, la skill DEBE resumir propósito, fila 1, estado y bloqueos, agrupar las apuestas abiertas en una vista y preguntar si continuar, revisar una sección o resolver una apuesta cuyo hecho ya ocurrió, sin preguntar apuesta por apuesta ni usar `mtime` para inferir el objetivo. |
| R-CHL-016 (si D-C) | C21 rejects an unconfirmed inference | WHEN el acta conserva una marca de inferencia sin confirmar, el sistema DEBE marcar el hallazgo `C21` como error sobre esa línea. `verifies: tests/test_charter_lint.py`. |

Confianza: `high` en 009, 010, 013, 015 y 016 (son afirmaciones sobre el texto de la skill o sobre el fichero); `medium` en 011, 012 y 014 con su `revisit` («cuando tres entrevistas reales hayan pasado por el modo brownfield / por la síntesis / por la preparación y se cuente cuántas preguntas sobraron o faltaron»).

**Change B · `2026-09-15-divergence-root-decisions`** · capability `divergence`.

| ID | Título | Enunciado EARS (resumen) | `verifies` |
|---|---|---|---|
| R-DIV-013 | Two fields of one scenario that read the same way are one decision | WHEN `effect` y `side_effects` del mismo escenario divergen y comparten al menos un token distintivo en cada lado, el sistema DEBE agruparlas en una decisión con razón `same-reading-two-fields`. | `tests/test_diff_readings.py` |
| R-DIV-014 | The same readings across scenarios are one decision | WHEN divergencias del mismo campo en escenarios distintos tienen lecturas normalizadas iguales lector a lector, el sistema DEBE agruparlas en una decisión con razón `same-readings-across-scenarios`; con lecturas distintas o tokens distintivos disjuntos DEBE mantenerlas separadas. | `tests/test_diff_readings.py` |
| R-DIV-015 | The JSON lists every decision without changing the verdict | WHEN se pide `--json`, el sistema DEBE añadir `decisions` cubriendo todas las divergencias (singletons incluidos) con `id`, `scenarios`, `fields`, `divergences`, `hardness`, `reason`, `question`, `options`, sin alterar `divergences`, `counts` ni `exit_code`. | `tests/test_diff_readings.py`, `tests/test_eval_fixtures.py` |
| R-DIV-016 | The diverge skill asks one decision at a time and records every member | WHEN el informe trae decisiones, la skill DEBE plantear una decisión por llamada, en el orden del informe, con `question` y `options` literales, explicando la decisión raíz una vez y listando los escenarios afectados, y anotar en `decisions.json` una entrada por divergencia miembro con el mismo `answer` y la clave `decision`. | `tests/test_diverge_skill.py` |
| R-DIV-017 | Several active changes are a question, not a guess | WHEN `$ARGUMENTS` no trae id y hay más de un change no archivado, la skill DEBE preguntar cuál con los ids como opciones, sin elegir por `mtime`. | `tests/test_diverge_skill.py` |

Confianza: `high` en 013–015 (aritmética sobre fixtures); `medium` en 016 (la agrupación reduce llamadas pero una decisión mal agrupada se contesta sin mirar: `revisit` «cuando la entrevista agrupada se use sobre un delta real con al menos una decisión de más de un miembro»); `high` en 017.

Efecto sobre R-DIV-009: su texto («una pregunta por llamada, en el orden del informe, con la pregunta y las opciones literales del script») se sigue cumpliendo literalmente porque **la agrupación la hace el script**, no la skill; la propuesta del change B lo dice con todas las letras para que nadie lea el cambio como una relajación.

## 7 · Decisiones que necesitan aprobación

| # | Decisión | Recomendación |
|---|---|---|
| D-A | ¿Dos changes (charter, divergence) o uno? | **Dos.** Capabilities distintas, oráculos distintos, divergencias más cortas. Charter primero. |
| D-B | ¿Persistir el mapa de cobertura en un fichero (`.venoxia/interview.json`)? | **No.** Se enseña en la conversación; el linter es su oráculo en disco; un JSON escrito por el modelo no es evidencia y sería el cuarto fichero de la skill. |
| D-C | ¿Regla `C21` (inferencia sin confirmar es error)? | **Sí.** Es la única pieza determinista del criterio 12; coste: una regla, dos tests, una fila del README. |
| D-D | ¿Dónde queda registrada la afirmación «todo está observado»? | Comentario HTML bajo `## Bets` + la entrega. Sin fichero nuevo. |
| D-E | ¿Protocolo de evals con persona en `append_system_prompt` y `interview-log.json`? | **Sí**, declarando el límite (no ejercita `AskUserQuestion` real). Primer paso: una pasada de prueba para observar la herramienta en eval. |
| D-F | Comando de tests: ¿detectar y, en ambigüedad, preguntar o dejar sin escribir? | Detectar; con **dos** candidatos, una pregunta con ambos; sin ninguno, no escribir y decirlo (como hoy). |
| D-G | Pregunta del esqueleto/guardián | Sólo en la preparación y sólo si **no** hay esqueleto detectable; con esqueleto, una línea. Sus tres opciones no cambian. |
| D-H | Criterios de agrupación de divergencias | Los dos de la sección 5 (token distintivo compartido en cada lado; igualdad lector a lector entre escenarios). Sin constantes nuevas. |
| D-I | «Sin `mtime`» ¿sólo en `diverge` o también en `verify`, `implement` y `close`? | **Sólo `diverge` ahora** (es la skill del encargo); las otras tres quedan anotadas como change aparte. |
| D-J | ¿La `description` del frontmatter de charter corrige «fecha de revisión» por «hecho que la resuelve»? | **Sí**, de paso: hoy contradice a `C12`. |
