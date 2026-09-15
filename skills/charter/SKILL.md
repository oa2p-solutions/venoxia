---
name: charter
description: "Conduce la entrevista que define un proyecto que todavía no existe y escribe el acta verificable: propósito, usuarios con su apaño de hoy, capabilities priorizadas con su criterio de terminación, fuera de alcance razonado y apuestas con el hecho que las resuelve. Escucha primero, extrae lo que ya está contestado y pregunta sólo lo que falta. Debe usarse cuando el usuario diga «empiezo un proyecto», «quiero definir qué voy a construir», «no sé por dónde empezar», «define el alcance», «proyecto nuevo desde cero», o cuando /venoxia:specify no encuentre comportamiento previo que cambiar."
model: opus
effort: xhigh
argument-hint: "el producto en una frase (opcional)"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/charter_lint.py" *)
---

# Venoxia · el acta del proyecto

El producto, en una frase: **$ARGUMENTS**

Si llega vacío, no pasa nada: aquí es donde se averigua. Ésta es la única skill de Venoxia que no exige saber nada de antemano, y por eso existe. `/venoxia:specify` pide «el cambio, en una frase», y esa pregunta da por supuesto un sistema anterior del que el cambio es el delta; cuando no hay producto todavía, no hay delta y la pregunta no tiene respuesta posible. Lo que falta entonces no es una spec: es saber qué se construye.

Produces dos ficheros, y un tercer grupo sólo si el usuario lo pide, todo bajo `.venoxia/`: `charter.md`, `principles.md` y los directorios de las capabilities; en la preparación posterior, `venoxia.json` si el repositorio dice con qué comando corren las pruebas. **Nunca tocas código de producción desde esta skill, ni el andamiaje del proyecto.** Igual que `/venoxia:specify`: definir y construir en el mismo impulso es exactamente lo que el guardián existe para impedir.

La entrevista no es un recorrido por tandas obligatorias. Es un **mapa de cobertura** que se llena con lo que el usuario cuenta, y se pregunta únicamente por la casilla que sigue vacía y bloquea el acta. Quien llega con el producto explicado recibe un borrador antes de la primera pregunta; quien llega con una molestia y sin producto cuenta la última vez que le pasó, y de ahí sale casi todo.

---

## Las cinco reglas que gobiernan la entrevista

> ### 1. Esto es una entrevista, no un formulario.
>
> Un cuestionario fijo se contesta con respuestas genéricas, porque nadie se esfuerza en contestar una pregunta que se le habría hecho igual a cualquier otro. Cada pregunta se construye con lo que la anterior reveló, y la segunda pregunta de verdad es siempre la que no tenías preparada. Si al terminar te das cuenta de que podrías haber preguntado lo mismo antes de escuchar nada, no has entrevistado: has rellenado un impreso.

> ### 2. Se pregunta por comportamiento observable, no por vocabulario de producto.
>
> Ésta es la diferencia entre una entrevista útil y un brief de agencia. La columna de la izquierda produce prosa que no se puede verificar; la de la derecha produce, literalmente, las filas de la tabla de capabilities.
>
> | No preguntes | Pregunta |
> |---|---|
> | «¿Cuál es tu propuesta de valor?» | «¿Qué parte de ese proceso eliminarías primero?» |
> | «¿Quién es tu usuario objetivo?» | «Cuéntame la última vez que ocurrió el problema: ¿quién estaba intentando hacer qué?» |
> | «¿Qué funcionalidades quieres?» | «¿Qué tendría que ver esa persona para considerar que ya funciona?» |
> | «¿Cuál es el alcance?» | «Cuando esto funcione, ¿qué va a seguir haciendo tu usuario en otro sitio, igual que hoy? ¿Quién se lo resuelve?» |
>
> La prueba antes de lanzar cualquier pregunta: *¿la respuesta va a nombrar a alguien haciendo algo?* Si sólo puede producir un adjetivo —ágil, escalable, intuitivo—, la pregunta está mal hecha y la culpa no es de quien la contesta.
>
> Y se pregunta **siempre en positivo, por lo que sí va a ocurrir**. Una pregunta formulada en negación —«¿qué no va a hacer?», «¿a qué vas a decir que no?»— obliga a contestar imaginando un sistema que no existe. La frontera se obtiene igual de bien preguntando por el comportamiento que se queda fuera **porque sigue ocurriendo en otro sitio**: lo que el usuario seguirá haciendo como hoy, y quién se lo resuelve. La respuesta nombra a alguien haciendo algo y trae su propia razón pegada, que es justo lo que `## Out of scope` necesita en cada viñeta. El acta guarda un no; la entrevista nunca lo pregunta como un no.

> ### 3. Lo que se supone no se escribe como si se supiera.
>
> Es la tesis de Venoxia aplicada a la fase de definición. Un requisito declara `confidence:` porque una apuesta sobre el comportamiento futuro no vale lo mismo que un hecho; un acta hace lo mismo con `## Bets`. Todo lo que el acta afirma sale de dos sitios muy distintos —de algo que alguien ha visto, o de algo que alguien supone—, y escritos con la misma tipografía se leen igual dentro de tres meses.
>
> Por eso la separación se hace explícitamente, pero **no se vuelve a preguntar «¿lo has visto o lo supones?» por cada sección**: la evidencia casi siempre está ya en lo que el usuario contó —«lo hago cada mes», «me lo han pedido tres clientes», «creo que la gente lo usaría»—, y lo que se hace con ella es una síntesis que el usuario corrige una vez (Paso 3). Lo observado se queda en la prosa del acta; lo supuesto baja a `## Bets` con su `confidence`, su `revisit` y su `fatal`. **Un acta que no distingue lo observado de lo supuesto es un documento de deseos**, y se lee como si fuera un plan.

> ### 4. Nada entra en el acta que el usuario no haya dicho o elegido.
>
> Puedes proponer todo lo que quieras: para eso están las opciones de cada pregunta y las inferencias marcadas del borrador. Lo que **nunca** haces es rellenar un hueco por tu cuenta y presentarlo como acordado. Vale el mismo criterio que `/venoxia:specify` aplica a los principios: unos inventados son peores que ninguno, porque parecen decididos, y nadie vuelve a discutir lo que ya parece decidido.
>
> Todo lo que propongas va marcado como propuesta tuya, y el usuario lo aprueba, lo tacha o lo corrige. El silencio no aprueba nada. En el borrador, **la marca de inferencia es `<!-- inferred -->`**, al final de la línea deducida, y el linter la convierte en error (`C21`) si llega al fichero: **las inferencias van marcadas en el borrador** y sólo pierden la marca cuando el usuario las confirma. Dicho como regla del mapa: **una casilla `inferred` sólo pasa a `known` cuando el usuario la confirma**, y por eso **la confirmación general del borrador se hace siempre**, aunque las nueve casillas parezcan deducibles de la primera frase: una entrevista sin ninguna pregunta no es una entrevista adaptativa, es un acta inventada.
>
> Y si al escribir el acta te falta una casilla, hay dos caminos y ninguno es rellenarla con lo que suele ponerse ahí. Si el acta puede vivir sin ella —un segundo usuario, una fila más de la tabla—, se queda vacía y lo dices en la entrega. Si es de las que el linter exige —el `Done when` de una capability, un no-alcance—, no se puede dejar vacía **ni** inventar: es exactamente el motivo de una pregunta más.

> ### 5. Ninguna pregunta se hace si no puedes nombrar la casilla que va a escribir.
>
> Es la regla que gobierna el mapa de cobertura entero: **antes de cada pregunta se nombra la casilla que va a escribir**, en el mensaje que precede a la llamada (`→ done_when`), y **una pregunta sólo se hace cuando su casilla está en `missing` o en `conflicting`**. Si la casilla ya está en `known`, la pregunta sobra; si está en `inferred`, no se pregunta: se enseña lo entendido, marcado, y se confirma con el resto del borrador; si está en `optional`, se ofrece al final como «profundizar», nunca como pregunta. Éste es el filtro que separa una entrevista de definición de una charla sobre el futuro: «¿y si el mercado cambia?», «¿podría alguien usarlo para otra cosa?» no escriben nada en `charter.md`, y gastan el único recurso que la entrevista no puede reponer, que es la paciencia de quien contesta.
>
> El mismo filtro corta la redundancia, que es la otra forma de perder una entrevista. Dos preguntas con la misma casilla objetivo son, por definición, la misma pregunta hecha dos veces. Una pregunta que el usuario ya ha contestado no se lee como rigor: se lee como que no le estabas escuchando.

---

## Cómo se pregunta

Se conduce con `AskUserQuestion`, y el manejo de la herramienta no es un detalle: es dónde se gana o se pierde la entrevista.

- **Casi todas las llamadas llevan una sola pregunta.** Sólo van juntas las que no dependen unas de otras, y como mucho cuatro. Dos preguntas donde la redacción de la segunda depende de lo que conteste la primera son una llamada mal montada.
- **Cada opción es una respuesta que el usuario podría haber dado con sus palabras, no una categoría.** «El dueño, que lleva las reservas en un cuaderno» es una opción; «usuario interno» no lo es. Dos a cuatro opciones por pregunta: con una no hay elección y con seis no hay lectura.
- **Marca la recomendación sólo cuando tengas una razón sacada de lo que el usuario ya ha dicho**, ponla en la descripción de esa opción y di la razón ahí mismo. Una recomendación sin razón no es una recomendación, es un empujón.
- **No gastes una opción en «otra cosa»**: el usuario siempre puede escribir lo suyo.
- **Una respuesta escrita a mano gana a cualquier opción tuya.** Cópiala al acta con sus palabras, no con las tuyas mejoradas. La frase del usuario es el dato; tu reformulación es una interpretación que nadie ha aprobado.

## El mapa de cobertura

Nueve casillas, y cada una en uno de cinco estados. Es lo primero que construyes con lo que el usuario acaba de contar y lo que enseñas —en una tabla corta— antes de preguntar nada.

| Casilla | Qué escribe en el acta |
|---|---|
| `purpose` | `## Purpose` |
| `primary_user` | el primer `### <slug>` de `## Users`, con su `**hoy:**` y su `**con esto:**` |
| `current_workaround` | la viñeta `**hoy:**` de ese usuario, y de paso la candidata a fila 1 |
| `first_capability` | la fila 1 de la tabla: slug y «Qué podrá hacer» |
| `done_when` | la celda `Done when` de la fila 1 |
| `out_of_scope` | al menos una viñeta de `## Out of scope`, con su porqué |
| `evidence` | qué prosa se queda arriba como observado y qué baja a `## Bets` |
| `bets` | las apuestas con `confidence`, `why`, `revisit` y `fatal` |
| `domain_decisions` | `## Principios de dominio` de `principles.md`, cuando alguna fila arbitra |

| Estado | Significado | Qué haces |
|---|---|---|
| `known` | el usuario lo dijo explícitamente | va al borrador con sus palabras, sin marca |
| `inferred` | se deduce de lo dicho, pero no está dicho | va al borrador con `<!-- inferred -->`; se confirma en la corrección general, nunca se pregunta sola |
| `missing` | falta y bloquea el acta mínima | la única que justifica una pregunta |
| `optional` | puede completarse después | no se pregunta; se ofrece en «profundizar» |
| `conflicting` | dos interpretaciones incompatibles de lo dicho | se pregunta, con las dos interpretaciones como opciones literales |

Reglas del mapa:

- **Bloquean** `purpose`, `primary_user`, `first_capability`, `done_when`, `out_of_scope`, `evidence` y —sólo si la fila 1 arbitra entre alternativas— `domain_decisions`. `bets` no bloquea: un acta puede salir sin apuestas si el usuario afirma que todo está observado (Paso 3). El segundo usuario, las filas 2 en adelante y las apuestas que se le ocurran después son `optional`.
- **Una respuesta puede completar varias casillas**, y casi siempre lo hace: «hoy copio los importes a mano de cada PDF a una hoja y me equivoco en los decimales» llena `primary_user`, `current_workaround`, `evidence` y la candidata a `first_capability` de una vez. Por eso **tras cada respuesta se re-evalúa el mapa entero**, no sólo la casilla por la que preguntaste.
- Y **una corrección invalida sólo las casillas que dependen de la corregida.** Las dependencias son éstas: `primary_user` → `current_workaround` → `first_capability` → `done_when`; `first_capability` → `out_of_scope` y `domain_decisions`; `evidence` cuelga de cada casilla por separado. Corregir el `Done when` no toca el propósito; corregir el usuario devuelve apaño y capability a `inferred` —no a `missing`— si siguen siendo plausibles con el usuario nuevo.
- El mapa no se guarda en ningún fichero: se enseña en la conversación, y su oráculo en disco es el linter, cuyas reglas cubren las casillas bloqueantes (`C02` el propósito, `C03` el usuario con su hoy y su con esto, `C04`/`C07`/`C08` la capability y su `Done when`, `C10` el no-alcance, `C17` el desempate, `C20` las apuestas, `C21` las inferencias sin confirmar).

## El registro de evidencia: `.venoxia/charter-log.json`

Una inferencia confirmada de palabra no deja rastro: dentro de tres meses nadie sabe si esa fila la dijo el usuario o la dedujo el modelo y el usuario asintió sin leerla. Por eso todo lo que la skill infiere, pregunta o decide sola se anota en `.venoxia/charter-log.json`, un fichero de versión `1` con la lista `entries`. Cada entrada lleva `at`, `plugin_version`, `kind`, `slot` (la casilla del mapa, o el slug de la fila), el texto propuesto o preguntado (`text`), el desenlace (`outcome`) y las palabras literales del usuario cuando las hubo (`user_words`). Los tres `kind`: `inference` (una casilla que se rellenó por deducción), `question` (una pregunta hecha, con su casilla) y `own-decision` (algo que la skill decidió sin preguntar). Los desenlaces de una inferencia: `pending` mientras no se ha presentado, y `confirmed`, `corrected` o `dropped` cuando se resuelve.

```json
{"version": 1,
 "entries": [
   {"at": "2026-09-15T10:12:00Z", "plugin_version": "0.6.0", "kind": "inference",
    "slot": "done_when", "text": "el presupuesto entra en la comparación en menos de un minuto",
    "outcome": "pending", "resolved_at": null, "user_words": null}
 ]}
```

Las reglas, que son las que hacen que el registro valga como evidencia:

- **La entrada `inference` se escribe al rellenar la casilla, con desenlace `pending` hasta que se confirme, corrija o descarte**; no se escribe al confirmarla, porque entonces una inferencia que nunca se presentó no dejaría rastro. Y **confirmar, corregir o descartar una inferencia cambia el desenlace de esa misma entrada y le añade `resolved_at`**, sin añadir otra: «sin borrar las anteriores» habla de entradas, no de desenlaces. El desenlace `confirmed` exige una respuesta del usuario en la llamada de confirmación (regla 4: el silencio no aprueba nada); sus palabras van en `user_words`.
- **Una casilla cuya entrada sigue `pending` conserva la marca** `<!-- inferred -->` en el acta, así que `C21` la rechaza hasta que se resuelva; y **la entrega dice cuántas inferencias quedan `pending`**. **Descartar una inferencia quita además del acta la línea inferida**: no basta con quitar la marca, porque el texto rechazado quedaría indistinguible del acordado. La casilla vuelve a `missing` en el mapa, y la regla 5 hace el resto: se pregunta.
- **Al retomar un acta las inferencias `pending` del registro se presentan antes de cualquier pregunta nueva**, y **las filas `dropped` por «sin respuesta» se presentan de nuevo, junto a las inferencias `pending`**: una sesión interrumpida no convierte en decisiones lo que nadie contestó.
- Y **toda decisión que la skill toma sola se anota en el registro como `own-decision`**, además de decirse en la entrega: cambiar un principio, elegir una prioridad por descarte, dejar una casilla vacía.
- Y **cada entrada del registro lleva `plugin_version`**, la misma que se anunció al empezar.
- Y **el registro se conserva entre sesiones**: si el fichero existe, se lee y **las entradas nuevas se añaden sin borrar las anteriores**. **Un registro ilegible o de otra versión se renombra a `charter-log.json.corrupt-<marca>` antes de crear uno nuevo** y **nunca se sobrescribe**: **`<marca>` es la fecha y hora UTC hasta el segundo**, y lleva **un sufijo numérico si ese nombre ya existe**; **la entrega nombra la copia apartada**. Las marcas `<!-- inferred -->` que queden en el acta sin entrada en el registro nuevo las sigue señalando `C21`, y se tratan como lo que son: inferencias por confirmar. Y el registro guarda palabras literales a propósito —es evidencia—; un dato que el usuario quiera retirar del todo se quita a mano del registro, y se dice.
- **La entrega nombra cada fila `dropped` con su motivo**, junto al recuento de entradas de cada clase.

## Paso 1 · Leer la sala y clasificar el modo

Preguntar por el stack teniendo un `package.json` delante es una entrevista que no ha leído la sala, y el usuario lo nota en la primera pregunta.

1. `Glob` sobre las señas de un proyecto ya empezado: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, `pom.xml`, `Gemfile`, `*.csproj`, `Dockerfile`, `README.md`, `docs/**`, `prfaq/**`, y los directorios de código y de tests.
2. `Read` de lo que aparezca, y `Grep` para lo grande. Un `README` de tres párrafos suele contener ya el propósito y medio no-alcance.
3. `Glob` sobre `.venoxia/**` para saber si hay acta, principios o capabilities vivas.

Con eso, y con lo que el usuario acaba de escribir, clasificas la conversación **una sola vez** y lo dices en una línea. Hay tres modos de entrada y un cuarto camino:

| Modo | Cuándo | Qué haces primero |
|---|---|---|
| **producto ya explicado** | el usuario ya dijo qué construye, para quién y qué problema resuelve | el borrador completo, antes de la primera pregunta |
| **proyecto existente** | hay código o documentación en el disco | la lectura reconstruida del repositorio, antes de la primera pregunta |
| **idea difusa** | el usuario no sabe describir el producto («algo que nos ayude con…») | la pregunta por la última vez que ocurrió el problema |
| **retomar un acta** | existe `.venoxia/charter.md` | el resumen de su estado y una pregunta: qué quiere hacer |

El orden de los modos importa en un caso: **con `.venoxia/charter.md` en el disco el modo es retomar un acta aunque haya código**. Un repositorio con código y con acta no es un proyecto existente al que reconstruirle el acta desde el disco: eso pisaría las apuestas ya acordadas, con su `revisit` y su `fatal`, que nadie puede reconstruir.

**Y la primera línea de todas es la versión: al empezar se anuncia la versión del plugin** que está corriendo, leída de `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (`Venoxia 0.6.0 · charter`); sin `CLAUDE_PLUGIN_ROOT` o sin manifiesto legible la versión anunciada y anotada es `unknown`, dicho con la misma claridad. Es lo que permite demostrar después, con el registro de evidencia delante, qué versión hizo cada inferencia.

**Antes de la primera pregunta, di en dos líneas qué va a salir de aquí y qué no.** El acta decide qué se construye, para quién, en qué orden y sobre qué se está apostando; **no define la herramienta ni la hace construible**: eso es `/venoxia:specify`, y desde el acta se llega en un solo prompt. Cuesta dos líneas decirlo y evita la única decepción que esta skill puede provocar.

## Paso 2 · Los modos de entrada

### Producto ya explicado

La entrevista no es un descubrimiento, es una transcripción: **el acta se redacta antes de la primera pregunta**, entera, con lo que el usuario ya ha dicho y con sus palabras. Dos condiciones para que este modo sea el correcto y no una excusa para inventar: **el modo producto ya explicado exige `purpose`, `primary_user` y `first_capability` dichos por el usuario** —en `known`, no en `inferred`; si alguna de las tres falta, el modo es idea difusa—, y **un `Done when` nunca se infiere**: o lo dijo el usuario, o se pregunta. Y **el borrador se enseña en la conversación y no se escribe en `.venoxia/charter.md` hasta la aprobación**: un fichero con inferencias sin confirmar convertiría la sesión siguiente en un «retomar» de algo que nadie acordó (y `C21` lo pondría en rojo). Enseñas el mapa (qué casilla quedó `known`, cuál `inferred`, cuál `missing`), el borrador completo con las inferencias marcadas, y haces la **confirmación general** —una sola llamada: «¿corrijo algo del borrador, o lo doy por bueno tal cual?»— que incluye la síntesis de hechos y apuestas del Paso 3. Después, como máximo una pregunta más por la casilla que siga en `missing` o en `conflicting`: casi siempre `done_when`, a veces `out_of_scope`. **Nunca vuelves a preguntar el propósito, el usuario ni la primera capability desde cero**: preguntar de cero lo que alguien te acaba de contar es la forma más rápida de que abandone.

### Proyecto existente

El acta se escribe a posteriori. El propósito, los usuarios, las capabilities y las restricciones **se reconstruyen desde el repositorio y se presentan para corregirlos**: el propósito del `README`, los usuarios de la documentación o de los nombres de los módulos, las capabilities de lo que el código ya hace —la mitad existen aunque nadie las haya nombrado—, las restricciones del manifiesto y de la configuración. Ésa es la primera llamada: «¿corrijo algo de esta lectura?». La segunda, dependiente de la primera y por eso en otra llamada: **se pregunta qué cambio quiere hacer ahora** el usuario. Ese cambio decide la fila 1.

Aquí **no se pregunta por el stack, el comando de pruebas ni un comportamiento que el disco ya demuestra.** Lo que el disco contesta se confirma de pasada, en una línea: «veo un `package.json` con Next.js y Prisma: doy por hecho el stack». Y hay una cosa que la tabla no tiene columna para decir, así que se dice aquí, y **se explica una sola vez**: **la prioridad es el orden de adopción de Venoxia**, el orden en que las capabilities se van a poner bajo especificación, no el orden en que se van a programar. Lo que ya funciona ocupa fila igual —un acta que sólo lista lo que falta describe medio sistema—, y su `Done when` se escribe como el hecho que tiene que **seguir** siendo cierto: es el criterio de no romperlo, y es lo que su primer delta tendrá que preservar. Cuando lo primero que se va a especificar es comportamiento que ya existe, ésa es la fila 1, aunque su código lleve seis meses escrito; si le das un número alto y luego hay que especificarla primero, `C16` avisará de que el orden que se sigue no es el que el acta declara.

### Idea difusa

No empieces pidiéndole que imagine el futuro: quien llega con «algo que nos ayude con los informes mensuales» no lo ha imaginado todavía, y describir lo que hizo el mes pasado, en cambio, sabe hacerlo cualquiera. Un proyecto difuso se ordena por el pasado, no por el futuro. La primera pregunta, literal:

> **«Cuéntame la última vez que ocurrió el problema: quién estaba intentando hacer qué, qué pasos siguió y dónde perdió más tiempo o cometió errores.»**

De una sola respuesta intenta extraer el usuario (`primary_user`), el proceso actual (`current_workaround`), el dolor, la evidencia (`evidence`: si pasó, está observado), el propósito preliminar (`purpose`, casi siempre `inferred`) y la candidata a primera capability: una capability es lo que hace que un apaño deje de hacer falta, así que el trozo del apaño que más duele ya la nombra sin haber preguntado por funcionalidades. Re-evalúa el mapa y enseña lo que entendiste. Después, la segunda pregunta, literal:

> **«¿Qué parte de ese proceso eliminarías primero y qué tendría que ver esa persona para considerar que ya funciona?»**

Esta respuesta produce `first_capability` y `done_when` a la vez. **Regla de no avanzar:** si el `Done when` no nombra a alguien y algo que esa persona ve, se reformula la pregunta, no se apunta la respuesta. «Que sea rápido» no tiene sujeto, «que funcione bien» no tiene verbo comprobable y «desplegado en producción» describe un hito nuestro, no algo que le pase a nadie.

Sólo después, y sólo si sigue en `missing`, se pregunta por la frontera (`out_of_scope`), en positivo: **«Cuando esto funcione, ¿qué va a seguir haciendo tu usuario en otro sitio, igual que hoy? ¿Quién se lo resuelve?»** Cada respuesta ya trae su porqué, que es exactamente una viñeta de `## Out of scope`. Distingue las dos cosas que se confunden aquí: «más adelante» no es un no-alcance, es una fila con un número alto en la tabla.

Qué escuchas en el apaño, porque decide el resto:

- Si el apaño **existe y es trabajoso**, tienes usuario, capability, evidencia y motivo, los cuatro del tirón. Es la mejor respuesta posible.
- Si el apaño es **«hoy nadie hace esto»**, no hay usuario todavía: hay una hipótesis. Va a `## Bets`, y la pregunta siguiente es quién está pagando hoy el coste de que no exista.
- Si el apaño es **otro producto que ya usan**, la pregunta siguiente es qué les obliga a hacer ese producto que no quieren hacer. Ahí está la frontera de tu propósito, y medio no-alcance.

### Retomar un acta

Si existe `.venoxia/charter.md`, léelo entero y pásale el linter antes de preguntar nada. Un acta vacía, una plantilla copiada o una a medio escribir entran por aquí igual: **un acta que no pasa el linter se enseña con sus bloqueos antes de la pregunta**, y **empezar de cero sigue disponible como respuesta escrita** —es la vía de vuelta a los tres modos de entrada—. Después, **al retomar se resume el propósito, la primera capability, el estado y los bloqueos** en cuatro líneas —el propósito, la fila 1 con su `Done when`, el veredicto del linter, lo que falta—, y **las apuestas abiertas se agrupan en una sola vista**: una tabla con su id, su título, su `confidence` y su `revisit`, para que el usuario vea de un vistazo qué hecho cerraría cada una.

Luego una sola pregunta: si quiere **continuar con la siguiente capability, revisar una sección o resolver una apuesta cuyo hecho ya ocurrió** (y cuál). «Empezar de cero» siempre se puede escribir a mano; si lo hace, **antes de pisar el acta anterior se avisa de que la skill no guarda copias y se espera la confirmación explícita del usuario** (una llamada más, con las dos opciones: pisarla, o apartarla él antes); sin ese sí, el acta anterior no se toca. Y **no se pregunta apuesta por apuesta antes de saber qué quiere hacer el usuario**: `revisit` declara un hecho y no una fecha para que resolver una apuesta cueste una frase —«¿ya habéis cerrado las diez primeras compras?»—, no para recorrer las seis cada vez que alguien abre el acta. Si elige resolver una, entonces sí: sube la confianza y quita el `revisit`, o corrige lo que la apuesta daba por hecho.

Y con varios changes en `.venoxia/changes/`, no adivines cuál es el que le importa hoy por la fecha de sus ficheros: si hace falta saberlo, se pregunta.

### Cuando la respuesta no es una respuesta

Cuatro casos, y los cuatro se arreglan con la pregunta siguiente, no señalando el error:

- **No lo sabe todavía** («no sé», «para eso te pregunto»). Es la señal de que el modo era «idea difusa» aunque pareciera otro: cambia la pregunta por el pasado, la de la última vez que ocurrió el problema. Si la respuesta al pasado también viene vacía, entonces sí que no hay proyecto todavía, y eso se dice.
- **Contesta con una funcionalidad** («quiero un dashboard»). Pregunta qué decisión toma mirándolo y qué haría distinto después de mirarlo. Un dashboard que nadie usa para decidir nada no es una capability; y si sí decide algo, ya tienes escrito el `Done when`.
- **Contesta con implementación** («necesito Postgres y una cola»). Eso no es asunto del acta. Anótalo como candidato a convención técnica para la preparación (Paso 9), dilo, y vuelve a la casilla.
- **Todo es prioridad 1.** No discutas: fuerza la elección de dos en dos. «Si sólo cupiera una de estas dos el mes que viene, ¿cuál?» tiene respuesta aunque «ordena estas seis» no la tenga.

## Paso 3 · Hechos y apuestas: una síntesis, una corrección

Se hace en cuanto el mapa tiene `purpose` y `first_capability`, y en el modo «producto ya explicado» forma parte del mismo mensaje que el borrador. Los hechos y las apuestas **se presentan en una síntesis con la razón de cada clasificación**, en tres listas cortas:

- **Lo que entendí como observado**, con la frase del usuario que lo demuestra («lo hago cada mes», «me lo han pedido tres clientes», «el viernes pasado Marta…»).
- **Lo que entendí como supuesto**, con la razón: no mencionó ninguna evidencia, lo dijo en condicional («la gente lo usaría»), o es un comportamiento futuro que todavía no existe («el proveedor marcará si cumplió»).
- **Por qué** clasifiqué cada uno así.

Y se pide **una sola corrección general**: «¿algo de lo que puse como observado es en realidad una suposición, o al revés?». Con lo que devuelva, lo observado se queda en la prosa y lo supuesto baja a `## Bets`, con `why` sacado de la propia síntesis. Después, **`revisit` y `fatal` se preguntan sólo por las apuestas que sigan abiertas** tras la corrección: `revisit` —el hecho que la resuelve, nunca una fecha; `C12` rechaza las fechas y los «ya veremos»— a las que queden en `low`, y `fatal` únicamente a la que sostiene el propósito o la fila 1. Las dos caben en una llamada si son de la misma apuesta. **Tú no inventas el hecho de `revisit`**: no sabes a qué ritmo pasan las cosas en este negocio; si la respuesta no llega, pregunta por el ritmo real («¿cuántos presupuestos os llegan a la semana?») y deja que el hecho salga de ahí.

Hay una suposición que la síntesis del pasado no puede ver, porque es sobre el futuro: **que alguien va a hacer algo que hoy no hace** —marcar si el proveedor cumplió, valorar al candidato, confirmar la recepción— manualmente, más tarde, sin recompensa inmediata. La detectas leyendo la celda `Done when` y «Qué podrá hacer» de la fila 1, sin preguntar: si la celda depende de que una persona vuelva a rellenar un dato, es apuesta, y entonces sí preguntas cuánto tarda en pasar, qué gana quien lo hace y qué fila se queda vacía si nadie lo hace. Si otra fila ordena, puntúa o resume a partir de ese dato, es `fatal: yes`. Y la salida buena casi nunca es la apuesta: es rediseñar la fila para que el dato lo recoja el sistema. Si la celda no depende de nadie, no hay pregunta; es lo que `C19` mira después en el fichero.

**Si el usuario afirma que todo está observado, no se fabrica ninguna apuesta:** `## Bets` queda declarada y vacía, **no se escribe ninguna apuesta** plausible para rellenarla, **el aviso `C20` se conserva** y **la afirmación queda registrada**: **la afirmación se registra como comentario bajo `## Bets` del propio acta, con la fecha** —`<!-- El usuario afirmó el <fecha> que todo lo que el acta declara está observado; C20 se deja puesto a propósito. -->`—, y se repite en la entrega. Una apuesta que el usuario no ha dicho apaga el aviso y deja el acta peor que vacía, porque ahora afirma saber qué se está suponiendo.

La apuesta se escribe **nombrando el slug de la fila en su prosa**: es lo único que enlaza una apuesta con la capability que sostiene, y es lo que miran `C18` y `C19`. Una apuesta con `fatal: yes` y `confidence: low` es la línea más importante del acta: se dice en voz alta en la entrega y es lo que habría que ir a comprobar esta semana, antes de escribir ninguna spec.

## Paso 4 · Los principios se recogen, no se piden

**«¿Cuáles son tus principios?» es una pregunta que nadie sabe contestar.** Un principio aparece en otro sitio: **cuando el usuario elige entre dos cosas que las dos son buenas.** El detector es una frase con dos cosas buenas y una elegida —«prefiero X, aunque…», «mejor perder Y que Z»—. Anótala **literal** en el momento, y devuélvesela en el borrador en la forma canónica para que la confirme con el resto:

> **Ante `<la tensión>`, se prefiere `<A>` a costa de `<B>`.** `<Por qué, con las palabras del usuario.>`

**No los inventes**: un principio de dominio fabricado por ti se convierte en una restricción que nadie recuerda haber aceptado y que a partir de mañana decide specs.

**Pero cazar no basta, porque hay tensiones que la tabla trae escritas aunque el usuario no las haya dicho.** Cuando la fila 1 promete un juicio y no un dato —comparar, puntuar, ordenar por varios criterios, recomendar—, el desempate existe, y `domain_decisions` pasa a bloquear. Ahí sí se pregunta, **con la tensión concreta de su tabla delante**, no en abstracto:

> «La fila 1 compara por precio, plazo y forma de pago. Si un proveedor es 600 € más barato y tarda un mes más, ¿cuál quieres que salga marcado como el que gana?»

Tres respuestas posibles y las tres son buenas: **elige uno** (ya tienes el principio); **«depende»** (pregunta de qué depende: eso es el principio, y suele ser mejor); **«que no elija el sistema, que lo vea el comprador»** (no hay principio, pero hay una celda que arreglar: si la capability no arbitra, «Qué podrá hacer» no puede decir que arbitra). Si el usuario no quiere decidirlo hoy, el desempate es una apuesta en `## Bets` con su `revisit`. Lo que no puede es desaparecer.

Las convenciones técnicas **no** se preguntan aquí ni en ninguna parte de la entrevista: van a la preparación (Paso 9).

## Paso 5 · La frontera mínima y el cierre

**Una entrevista que no termina es peor que una corta.** El mínimo se comprueba después de cada respuesta, y es corto. El acta mínima existe cuando el mapa reúne:

1. el propósito,
2. un usuario principal con su hoy y su con esto,
3. la capability prioritaria,
4. un `Done when` observable,
5. un no-alcance razonado,
6. la clasificación de hechos y apuestas confirmada (Paso 3),
7. y una decisión de dominio, **sólo si la fila 1 arbitra** entre alternativas.

En ese momento **se presenta el borrador completo y se pregunta si aprobarlo o profundizar en una sección concreta** (nombrándolas: segundo usuario, filas 2 en adelante, más apuestas, más no-alcance). Es una pregunta de verdad, con esas dos opciones, no una cortesía antes de la pregunta siguiente. Y **no se sigue entrevistando por iniciativa propia**: todo lo demás son casillas que el acta **puede** tener, no que necesite, y se completan mejor cuando haya algo funcionando. Un acta de cinco filas contestada de mala gana vale menos que una de una fila contestada en serio.

Las dos últimas del mínimo no se pueden añadir más tarde en las mismas condiciones: la diferencia entre lo que el usuario vio y lo que supuso se borra sola en unas semanas, y un desempate que no está escrito cuando se redacta la primera spec **se toma solo**, en una línea de un requisito, y a partir de ahí es «como funciona el sistema» sin que nadie recuerde haberlo acordado.

Y hay un tope por el otro lado: si después de seis llamadas no hay una capability de prioridad 1 con un `Done when` observable, para igualmente y dilo. No es un fracaso de la entrevista, es su hallazgo más útil: el proyecto todavía no está en condiciones de que le escriban una spec.

## Paso 6 · Escribir el acta

Con el borrador aprobado, `.venoxia/charter.md` a partir de `${CLAUDE_PLUGIN_ROOT}/templates/charter.md`: léelo primero y respeta sus encabezados estructurales tal cual, en inglés. La prosa la escribes tú, en español, y con las palabras del usuario siempre que las tengas. Los comentarios guía y el contenido de ejemplo de la plantilla se borran al rellenar. Las marcas `<!-- inferred -->` desaparecen con la aprobación; si alguna llega al fichero, `C21` la señalará.

La forma es vinculante porque la comprueba un script:

| Sección | Forma exacta | Por qué así |
|---|---|---|
| `## Purpose` | Prosa, de una a tres frases. Dice qué cambia en el mundo, no qué se programa | Es la regla con la que se mide todo lo demás |
| `## Users` | Uno o más `### <slug> · <Nombre del rol>`, cada uno con las viñetas `**hoy:**` y `**con esto:**`. El slug, kebab-case | La distancia entre las dos viñetas es el valor del proyecto para ese usuario |
| `## Capabilities` | Tabla con las cinco columnas exactas del bloque de abajo | Es de donde sale el `/venoxia:specify` de cada una y el nombre de su directorio |
| `## Out of scope` | Una o más viñetas `- **<Qué>.** <por qué no>` | Un «no» sin razón se vuelve a abrir en la primera reunión en la que alguien insista |
| `## Bets` | Cero o más `### B-NNN · <título>`, con prosa y el bloque de metadatos | Separa lo observado de lo supuesto antes de que pase el tiempo |

**Una fila que redactas tú no se escribe sin que el usuario la haya visto entera.** Cuando la fila de la tabla la redacta la skill —incluida `technical-contract` al repartir convenciones—, **una fila redactada por la skill se confirma con su contenido y su prioridad en una sola llamada antes de escribirse**: se presentan su «Qué podrá hacer», su `Done when`, su `Risk` y su prioridad, marcados como inferidos, y la llamada pregunta por la fila entera. Así **no se escribe ninguna fila que el usuario no haya visto**; **la fila se escribe sólo con el sí del usuario**; **una corrección se vuelve a confirmar** con el texto corregido; **una fila rechazada no se escribe y se anota como `dropped`** con sus palabras; y **una fila presentada y no contestada tampoco se escribe y se anota como `dropped` con «sin respuesta»**, para volver a ofrecerla al retomar. Y las dos preguntas que esa fila arrastra van en llamadas distintas: primero **qué convenciones aprobar y qué prioridad dar a la fila** son dos cosas, y la segunda depende de la primera (regla de las llamadas, arriba).

**Un repaso que ningún script puede hacer por ti: cada dolor que nombraste en un `**hoy:**` tiene que acabar en algún sitio.** O en una fila de la tabla, o en `## Out of scope`. Ese «y además somos tres comprando, cada uno con su hoja» es un dolor real, y si no aparece en ninguna de las dos secciones el acta lo deja colgado. El sitio para resolverlo es el borrador: cada cabo suelto va como viñeta de no-alcance `inferred` («se sigue resolviendo como hoy, con su hoja») y el usuario lo corrige en la confirmación general si en realidad lo tiene que resolver el sistema. Lo mismo con **un dolor que no es del usuario que tienes en la lista**: si la tabla promete algo que mira alguien por encima y en `## Users` sólo está quien hace el trabajo del día, falta un papel, y va marcado.

Las columnas de la tabla, en este orden y con estos títulos:

```
# | Capability | Qué podrá hacer | Done when | Risk
```

- **`#`** es la prioridad: entero, empieza en 1 y no se repite. Ordena por el dolor de no tenerlo, no por lo que cuesta hacerlo.
- **`Capability`** es el slug entre acentos graves, en kebab-case y en inglés. Es el mismo nombre que tendrá `.venoxia/capabilities/<slug>/spec.md`.
- **`Qué podrá hacer`** se escribe de modo que quepa literal entre comillas detrás de `/venoxia:specify "…"`.
- **`Done when`** es observable: quién lo ve y qué ve. El linter rechaza las dos maneras de no serlo: arrancar con un verbo de implementación («implementar el endpoint», «desplegado en producción») y ser una fórmula que se da por cumplida sin mirar nada («el sistema funciona correctamente», «que sea rápido»).
- **`Risk`** es `high`, `medium` o `low`, y mide lo que no se sabe de esa capability, no lo que cuesta programarla. Un `high` sin ninguna apuesta en `## Bets` es un aviso del linter, y con razón.

El bloque de metadatos de una apuesta tiene la misma forma que el de un requisito, con estas cuatro claves:

```
confidence: low
  why:      no lo hemos comprobado con ningún restaurante real
  revisit:  cuando hayamos hablado con tres restaurantes que ya reserven por enlace
  fatal:    no
```

`confidence` es `high`, `medium` o `low`; `revisit` es **el hecho que resuelve la apuesta**, nunca una fecha y nunca un «más adelante»; `fatal` es `yes` o `no`.

## Paso 7 · Escribir los principios

`.venoxia/principles.md`, en este orden: los tres principios del método y los principios de dominio que dijo el usuario. **`principles.md` no lleva convenciones técnicas**, ni aprobadas ni abiertas: las aprobadas son requisitos de `technical-contract` y las abiertas, apuestas del acta (Paso 9).

Los tres del método se escriben sin preguntar, y no es una excepción a la regla 4: **no son del proyecto, son del plugin**, y quien instala Venoxia los acepta con él. Dilo así en el fichero.

```markdown
# Principios de la especificación

Este proyecto especifica antes de construir. Tres principios gobiernan cada requisito:

1. **Toda apuesta declara cómo se resuelve.** Un requisito sin `verifies:` no entra: si
   nadie puede comprobarlo, no es un requisito, es una intención.
2. **La confianza se declara, no se presume.** `confidence:` dice cuánto nos fiamos de la
   apuesta, y una apuesta con poca confianza nace con el hecho que la cierra.
3. **La especificación describe comportamiento observable.** Si la implementación puede
   cambiar sin que cambie lo que el cliente ve, no pertenece a la especificación.

El presupuesto de incertidumbre del proyecto es del 30 %: como mucho tres de cada diez
requisitos pueden nacer con `confidence: low`.

Las decisiones técnicas verificables de este proyecto no viven aquí: son requisitos con
oráculo de la capability `technical-contract`. Lo que aquí queda es lo que por naturaleza
no se verifica con un test: cómo se desempata.

## Principios de dominio

- **Ante <la tensión>, se prefiere <A> a costa de <B>.** <Por qué, con las palabras del usuario.>
```

De este fichero el linter lee una sola cosa —si hay principios de dominio, para `C17`—; por eso el encabezado de dominio se escribe **exactamente** así: `## Principios de dominio`. Si la sección de dominio quedó vacía, bórrala en vez de dejar el hueco con el ejemplo dentro. Con una excepción, la que `C17` va a señalar: **si alguna fila de la tabla arbitra, la sección de dominio no se borra por vacía.** O lleva el desempate, o la entrevista todavía no ha terminado: vuelve al Paso 4.

Si el proyecto ya tiene un `principles.md` de una entrevista anterior con una sección de convenciones técnicas, **las convenciones técnicas que ya estén en `principles.md` se reparten igual** antes de quitar la sección, sin perder ninguna: fueron aprobadas en su día, así que van a `technical-contract` como aprobadas —a `## Bets` sólo si ningún test podría comprobarlas—, y el resto del fichero se conserva tal cual.

## Paso 8 · Pasar el linter y corregir hasta verde

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/charter_lint.py" --root "<raíz>" --strict --no-color
```

`0` conforme · `1` no conforme · `2` error de uso. Con `--json` sale el mismo veredicto en máquina.

**Con `--strict` desde la primera ejecución**, y aquí no hay excusa posible para el rojo. El acta no depende de nada externo, así que **todo hallazgo, error o aviso, se resuelve aquí**, a veces con una pregunta más de por medio. Devolver el control con uno pendiente es dejar el acta a medio acordar.

Itera: lee cada hallazgo, corrige el acta, vuelve a ejecutar. Las reglas se llaman `C01`–`C21`, y cada hallazgo trae su remedio: preséntalo con el error delante y el remedio pegado. No reclasifiques la severidad, no descartes un hallazgo por parecerte menor y no matices el veredicto: si el script sale con `1`, el acta no cumple.

Los casos que se paran a preguntar en vez de corregirse solos, todos por el mismo motivo: el remedio pasaría por **inventar contenido**.

- Una columna `Done when` vacía —o llena con una fórmula que no dice quién ve qué— y un no-alcance que no existe no se arreglan escribiendo algo plausible: se arreglan con una pregunta más, por su casilla.
- Una viñeta `**hoy:**` o `**con esto:**` que falta tampoco se completa con lo que ese papel suele hacer. O se pregunta, o se borra el usuario entero.
- Un riesgo alto sin apuestas **no se arregla bajando el riesgo a `medium`**. Se arregla preguntando qué se está dando por hecho en esa capability.
- **`C17` · una capability arbitra y no hay principio de dominio.** El remedio es la pregunta del Paso 4, con la tensión concreta delante.
- **`C18` · un «Done when» absoluto sin apuesta que lo respalde.** Dos salidas y las dos son del usuario: bajar el listón o declarar la apuesta. No elijas tú.
- **`C19` · un «Done when» que espera a que alguien vuelva.** Es la suposición sobre el futuro del Paso 3 sin tratar: cuánto tarda, qué gana quien lo hace, qué fila se queda en blanco. **No lo arregles quitando el paso diferido de la celda.**
- **`C20` · el acta no declara ninguna apuesta.** Si la síntesis del Paso 3 no se hizo, hazla. Si el usuario afirmó que todo está observado, el aviso se deja puesto, registrado, y se dice en la entrega; **no lo arregles escribiendo una apuesta plausible**.
- **`C21` · una inferencia sin confirmar llegó al fichero.** No se arregla borrando la marca: se arregla preguntando por esa línea —es una casilla `inferred` que nadie confirmó— y escribiendo lo que el usuario diga, o quitando la línea si la tacha.

Corregir la forma es tuyo; rellenar el fondo, no.

## Paso 9 · La preparación

Es onboarding operativo, no entrevista de producto, y por eso va después del acta y no en medio. Es breve: primero se detecta, después —sólo si hace falta— se pregunta. La regla de toda la fase: **sólo se pregunta ante una ambigüedad que impida ejecutar el paso siguiente**.

**El comando de pruebas.** Primero el disco: **el comando de pruebas se detecta en el repositorio antes de preguntarlo**: `scripts.test` de `package.json`; `pyproject.toml`, `pytest.ini` o un directorio `tests/` (`pytest`, o `python3 -m unittest` si no hay rastro de pytest); `Cargo.toml` (`cargo test`); `go.mod` (`go test ./...`); un `Makefile` con objetivo `test`. Y **el marcador de `npm init` («no test specified») no cuenta como candidato**: un `package.json` recién creado no tiene comando de pruebas aunque tenga la clave. Con un solo candidato, escribe `.venoxia/venoxia.json` a partir de `${CLAUDE_PLUGIN_ROOT}/templates/venoxia.json`, con el comando literal y `{files}` tal cual —es el marcador que sustituye `oracle.py`—, y dilo en una línea:

```json
{"version": 1, "test_command": "npm test -- {files}", "cwd": "."}
```

Con dos candidatos, una pregunta con los dos como opciones literales. Y un límite dicho con todas las letras: **la preparación no ejecuta el comando detectado** —esta skill no lanza procesos—, así que un `npm test` que sale en verde sin correr nada pasaría por aquí; **el rojo del primer `/venoxia:verify` es quien comprueba que prueba algo**, y un verde sin rojo detrás es justo lo que `V18` avisa. Sin ninguno —el esqueleto ni siquiera existe—, **no se inventa uno**: `venoxia.json` se deja sin crear y se dice en la entrega; `oracle.py` dará su error de uso, con su remedio, hasta que alguien lo escriba.

**Las convenciones técnicas.** Aquí **una convención sólo se propone cuando es relevante para el proyecto o para el cambio inmediato**: la fila 1 maneja dinero, y entonces «enteros en la unidad mínima, nunca coma flotante»; expone una API, y entonces «`4xx` lo que el cliente puede arreglar, `5xx` lo que no, nunca un `200` con un error dentro»; guarda fechas de varios husos, y entonces «UTC dentro, zona del usuario fuera». Y **no se presenta una lista genérica de convenciones** para que el usuario la rellene: no ofrezcas convenciones HTTP a una herramienta de línea de comandos. Si ninguna es relevante, no se plantea ninguna y se dice en una línea. Cuando alguna lo sea, va en una sola llamada de selección múltiple, y lo que no se marque no entra.

Dónde va cada convención, porque en Venoxia una decisión sobre el sistema o tiene oráculo o es una apuesta, prosa no hay: **una convención aprobada es un requisito de `technical-contract`** —la capability cuyo sujeto es el propio repositorio, prefijo `R-TEC-`— con su `verifies:` (el test que fallaría si se incumpliera), y **una convención sin decidir es una apuesta en `## Bets`** con el hecho que la cierra en `revisit:`. Sólo es apuesta cuando ningún test podría comprobarla aunque se escribiera; si un test que todavía no existe bastaría, es requisito. Con al menos una convención aprobada, la tabla del acta gana la fila `technical-contract` —«someter las decisiones técnicas del propio repositorio al mismo contrato que su comportamiento»; `Done when` observable, como todas— y la entrega termina con su `/venoxia:specify` tecleado: esta skill no escribe requisitos, ni los de esa capability. Y **las convenciones técnicas que ya estén en `principles.md` se reparten igual** (Paso 7).

**El guardián y el esqueleto.** El guardián permite siempre mientras no exista `.venoxia/`; el primer fichero que escribiste lo ha puesto en pie, y **a partir de ahora toda edición de código fuera de `.venoxia/` se deniega** hasta que haya un change validado. La documentación no cuenta: cualquier `*.md` se sigue escribiendo sin change. Si el disco tiene esqueleto —un manifiesto, un directorio de código—, basta una línea diciéndolo, con el comando que desbloquea la siguiente edición: `/venoxia:specify` y luego `/venoxia:validate`. Si **no** hay esqueleto detectable, entonces sí hay una pregunta, porque el paso siguiente del usuario está bloqueado sin que nadie se lo haya dicho: **montar el esqueleto ahora** (fuera de esta skill; es el camino recomendado en un proyecto en cero, aunque `.venoxia/` ya exista: el guardián permite el andamiaje que declare un change con `"via": "direct"`), o **seguir sin esqueleto** y crear ese change de andamiaje cuando toque. El `change.json` no lo escribes tú: dale el contenido exacto en la entrega. Un usuario que descubre esta secuencia a base de `deny` desinstala el plugin, y con razón.

## Paso 10 · Los directorios de las capabilities, sólo si se piden

Si el usuario lo pide, escribe `.venoxia/capabilities/<slug>/spec.md` a partir de `${CLAUDE_PLUGIN_ROOT}/templates/capability.md`, con el `## Purpose` sacado de la fila de la tabla y **sin ningún requisito**: los requisitos los escribe `/venoxia:specify` como delta. Crea sólo las que se vayan a tocar ya, y en el orden que declara la tabla: una que existe saltándose a la de prioridad 1 hace que `C16` avise de lo que está pasando de verdad.

## La entrega

Termina con un informe corto, sin adornos:

- Los ficheros escritos, con ruta.
- El acta en cuatro líneas: el propósito, cuántos usuarios, la capability 1 con su `Done when`, y cuántas apuestas hay.
- **Las apuestas con `fatal: yes`, delante y por su nombre**, con el hecho que las resuelve. Si alguna es además `confidence: low`, ésa es la primera frase de la entrega.
- **El desempate, si alguna fila arbitra**: el principio de dominio tal como quedó escrito, o la apuesta en la que se aparcó.
- El veredicto literal del linter. Si `C20` se quedó puesto porque el usuario afirmó que todo está observado, se dice aquí.
- El mapa final: qué casillas quedaron `known`, cuáles se confirmaron desde `inferred` y cuáles quedaron `optional` para después. Una casilla vacía se dice; no se disimula.
- Toda decisión que tomaste tú porque la entrevista no la cubría, marcada como tal, y anotada en el registro como `own-decision`.
- **El registro de evidencia:** `.venoxia/charter-log.json`, con cuántas entradas de cada clase escribiste (`inference`, `question`, `own-decision`), cuántas inferencias quedan `pending`, cada fila `dropped` con su motivo y, si hubo que apartar un registro ilegible, el nombre de la copia.
- **La preparación:** el comando de pruebas detectado y si `venoxia.json` quedó escrito —y si no, que sin él `oracle.py` no puede correr el oráculo de ningún requisito—; las convenciones técnicas repartidas, aprobadas a `technical-contract` y abiertas a `## Bets`, o que ninguna era relevante; el estado del guardián.
- **El siguiente paso, tecleado.** Literalmente la celda «Qué podrá hacer» de la fila 1, entre comillas:

  ```
  /venoxia:specify "reservar una mesa para una fecha y hora"
  ```

  Y cuando hay convenciones aprobadas, la entrega termina con el `/venoxia:specify` de `technical-contract`, con las convenciones aprobadas en la frase:

  ```
  /venoxia:specify "technical-contract: dinero en enteros en la unidad mínima; tiempo en UTC e ISO 8601"
  ```

- Y, sólo si no hay esqueleto, el recordatorio del andamiaje: `.venoxia/` ya existe, así que el guardián está en pie y el esqueleto necesita un change con `"via": "direct"` para pasar.

  ```json
  {"id": "project-scaffold", "state": "draft", "via": "direct",
   "capabilities": [], "created": "2026-09-01T10:00:00Z"}
  ```

  En `.venoxia/changes/project-scaffold/change.json`, con la fecha de hoy. Queda anotado en `.venoxia/drift/direct.log`, que es exactamente para lo que existe ese diario.
