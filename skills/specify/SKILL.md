---
name: specify
description: "Redacta la especificación de un cambio en el formato de Venoxia: propuesta, delta en EARS y un oráculo de verificación por requisito, y no devuelve el control hasta que el validador lo acepta. Debe usarse cuando el usuario pida «especifica …», «escribe la spec de …», «prepara el delta de …», «quiero cambiar el comportamiento de …», o cuando el guardián deniegue una edición por no haber un change validado."
model: opus
effort: xhigh
argument-hint: "el cambio que hay que especificar, en una frase"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" *)
---

# Venoxia · especificar

El cambio a especificar: **$ARGUMENTS**

Si llega vacío, mira primero qué hay en el proyecto. Cuando no existe `.venoxia/charter.md` **ni** ninguna capability bajo `.venoxia/capabilities/`, preguntar por «el cambio, en una frase» no tiene respuesta posible: no hay comportamiento previo que cambiar, así que no hay cambio. Remite entonces a **`/venoxia:charter`**, que es la entrevista que define el propósito, los usuarios y la lista priorizada de capabilities, y que termina entregando el `/venoxia:specify` exacto de la primera. Con acta escrita o con capabilities vivas sí hay de dónde partir: pregunta por el cambio en una sola frase y espera. Sin cambio no hay nada que especificar y adivinarlo produce una spec que nadie pidió.

Produces tres cosas y sólo tres, todas bajo `.venoxia/`: un `change.json`, un `proposal.md` y uno o más ficheros de delta. **Nunca tocas código de producción desde esta skill.** Escribir la spec y escribir la implementación en el mismo impulso es exactamente lo que el guardián existe para impedir.

---

## Las dos reglas que gobiernan la redacción

> ### 1. Si la implementación puede cambiar sin que cambie el comportamiento observable, no pertenece a la spec.
>
> El nombre de la tabla, la librería del cliente HTTP, si hay caché o no, el número de reintentos internos: todo eso puede reescribirse mañana entero sin que ningún usuario, ningún sistema vecino y ningún test de aceptación noten nada. Lo que no pertenece a la spec y aun así se escribe en ella se convierte en una mentira en cuanto alguien refactoriza, y una spec que miente ya no la lee nadie. La prueba a la que someter cada frase antes de escribirla: *¿podría reescribir la implementación de cero, dejando el comportamiento intacto, y hacer falsa esta frase?* Si la respuesta es sí, la frase se queda fuera.

> ### 2. `confidence` mide la confianza en el requisito, no en la implementación.
>
> No dice «sé programar esto». Dice «estoy convencido de que este es el comportamiento correcto». `high` es un hecho conocido: un requisito legal, una integración con contrato firmado, una regla que el negocio ya opera. `medium` es una decisión razonada que podría revisarse. `low` es una apuesta: alguien eligió los 15 minutos, el 409 o el reintento porque había que elegir algo.
>
> Por eso `low` sin `revisit:` es una apuesta que nadie sabe cómo cerrar, y por eso el validador la rechaza (`V10`). Una apuesta que nadie se compromete a resolver deja de ser una apuesta y se convierte en deuda silenciosa: nadie la mira, nadie la corrige y a los seis meses es «como funciona el sistema».
>
> **`revisit:` es el hecho que la resuelve, no una fecha, y tú no lo inventas.** Lo que cierra una apuesta es que llegue un dato —«cuando hayamos procesado los primeros veinte documentos reales», «cuando el primer cliente lo use en producción»—, y ese hecho sale del proyecto, no de tu criterio: no sabes a qué ritmo llegan los documentos ni cuándo entra el primer cliente. Si el cambio que estás especificando no te da el hecho, pregúntalo; es una pregunta corta y tiene respuesta. Escribir una fecha estimada es peor que dejarlo en blanco: parece un compromiso, no lo firmó nadie, y `V10` la rechaza.

---

## Paso 1 · Leer antes de proponer nada

No se propone nada hasta que este inventario existe. Especificar sin leer lo que ya hay produce duplicados —el mismo comportamiento con dos IDs y dos redacciones distintas— y contradicciones, que son peores: dos requisitos vivos que se niegan el uno al otro y un validador que no puede detectarlo porque los dos están bien formados.

1. **`.venoxia/charter.md`**, si existe. El acta dice para qué existe el proyecto, quién lo usa, qué capabilities están previstas y en qué orden, qué se declaró fuera de alcance y qué se está dando por supuesto. Es el marco dentro del cual el cambio que te piden cae o no cae, y saberlo antes de escribir sale mucho más barato que descubrirlo después. Si no existe, sigue: los proyectos que adoptaron Venoxia antes que el acta no la tienen, y su ausencia no bloquea nada.
2. **`.venoxia/principles.md`**, entero. Son las restricciones que toda spec de este proyecto respeta. Si el fichero no existe pero `.venoxia/` sí, sigue adelante y dilo en la entrega: estás redactando sin principios declarados.

   Mira con especial cuidado **`## Principios de dominio`**, porque es la sección que decide comportamiento sin estar en ningún requisito. Si el cambio que te piden implica un juicio —qué opción gana cuando dos son buenas, qué se prefiere a costa de qué— y ahí abajo no hay ningún principio que lo gobierne, **no lo decidas tú en silencio**. Es la forma más silenciosa que tiene una spec de mentir: el criterio queda escrito, parece acordado, y nadie recuerda haberlo elegido. Dos salidas, y las dos son legítimas: preguntar al usuario y proponerle que el principio se añada al acta, o escribir el requisito con `confidence: low` y su `revisit:`, diciendo con todas las letras en la propuesta que el desempate lo elegiste tú porque había que elegir algo. Lo que no vale es la tercera, que es escribirlo como si fuera un hecho.
3. **Todas las capabilities vivas**: `Glob` sobre `.venoxia/capabilities/*/spec.md` y `Read` de **cada** fichero completo. No basta con `grep`, ni con leer la que crees que toca. Un requisito de `billing` puede contradecir el que vas a escribir en `checkout`, y sólo lo ves si lo has leído.
4. **Los changes en vuelo**: `Glob` sobre `.venoxia/changes/*/change.json`. Un change con `state` distinto de `archived` que toque la misma capability es un conflicto que hay que resolver **antes** de escribir: o se continúa aquel change, o se dice explícitamente en la propuesta por qué este va aparte.

Con eso, construye un inventario mental: qué capabilities existen, qué promete cada una, qué IDs están ocupados y dónde está la frontera de cada una.

**Si `.venoxia/` no existe**, el proyecto no ha adoptado Venoxia. Dilo antes de escribir nada, y distingue dos situaciones que no se arreglan igual. Si el proyecto está **en cero** —no hay producto todavía y lo que falta no es una spec, sino saber qué se construye—, éste no es el camino: es `/venoxia:charter`, que hace la entrevista, escribe el acta y los principios, y sale con la primera capability ya nombrada y priorizada. Si el proyecto **ya tiene producto** y sólo le falta adoptar Venoxia, pide al usuario los principios en dos o tres frases; con ellos escribes `.venoxia/principles.md`, y el resto del árbol lo van creando los `Write` de los pasos siguientes. No inventes principios: unos fabricados por ti son peores que ninguno, porque parecen acordados.

## Paso 2 · Decidir el alcance y escribir la propuesta

**Capability nueva o modificación de una existente.** El criterio no es el tamaño del cambio, es el propósito: una capability es un conjunto coherente de comportamiento observable con una sola razón de existir. Si el cambio cabe bajo el propósito que la capability ya declara, es una **modificación**. Sólo si exige escribir un propósito nuevo es una **capability nueva**.

Ante la duda, modifica. Una capability nueva que se solapa con una existente es el error más caro de esta fase: parte en dos la verdad sobre un mismo comportamiento y a partir de ahí las dos mitades divergen sin que nada lo señale.

**Si hay acta, la capability debería estar en su tabla.** Busca el slug en `## Capabilities` de `.venoxia/charter.md`. Si está, úsalo tal cual: el acta y `.venoxia/capabilities/<slug>/spec.md` nombran la misma cosa, y bautizarla distinto aquí parte la trazabilidad en dos sin que ninguna regla pueda verlo. Si **no** está, dilo y pregunta si se añade al acta antes de seguir. Puede que el acta se quedara corta, y entonces se añade una fila y listo; o puede que este cambio esté fuera de lo que el proyecto declaró que iba a hacer, y ésa es exactamente la conversación que conviene tener antes de escribir la spec y no después de implementarla.

Después:

1. **Elige el identificador del change**: corto, en `kebab-case` y en inglés, describiendo el cambio y no la fecha (`stock-reservation`, `guest-checkout`). Único bajo `.venoxia/changes/`; si ya existe, sufija con `-2` o afina el nombre.
2. **Escribe `.venoxia/changes/<id>/change.json`**:
   ```json
   {"id": "<id>", "state": "draft", "via": "spec",
    "capabilities": ["checkout"], "created": "2026-08-31T09:14:00Z"}
   ```
   `state` arranca en `draft`. `via` es `spec` salvo que el usuario pida explícitamente saltarse el flujo, en cuyo caso es `direct` y el guardián lo anotará como deriva. `capabilities` lista los nombres de las capabilities que el delta toca. `created` es el instante actual en ISO 8601 UTC, no la fecha del ejemplo.
3. **Escribe `.venoxia/changes/<id>/proposal.md`** a partir de `${CLAUDE_PLUGIN_ROOT}/templates/proposal.md`: léelo primero y respeta sus encabezados estructurales tal cual, en inglés. La prosa la escribes tú, en español. No añadas secciones que la plantilla no tiene, sigue sus comentarios guía para lo que no aplique, y borra esos comentarios y la prosa de ejemplo al rellenar: el ejemplo de la plantilla es ejemplo, no contenido heredado.

La propuesta responde al *por qué* y al *qué cambia de alcance*. El *qué hace el sistema* va en el delta, no aquí, y no se duplica en los dos sitios.

## Paso 3 · Redactar el delta en EARS, con oráculo desde el primer borrador

Un fichero por capability tocada: `.venoxia/changes/<id>/delta/<capability>.md`, a partir de `${CLAUDE_PLUGIN_ROOT}/templates/delta.md`. Como en la propuesta, los comentarios guía y el requisito de ejemplo de la plantilla se borran al rellenar.

Cada fichero declara al menos un bloque (`V12`), con el encabezado exacto:

```markdown
## ADDED Requirements
## MODIFIED Requirements
## REMOVED Requirements
## RENAMED Requirements
```

Y dentro, requisitos con esta forma exacta:

```markdown
### R-CHK-014 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de todas las
líneas del pedido durante 15 minutos.

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

Título del requisito en inglés, narrativa y escenarios en español. Las palabras clave estructurales (`WHEN`, `WHILE`, `WHERE`, `IF`, `THEN`, `AND`) van en inglés y en mayúsculas; el modal va en español (`DEBE`), porque `SHALL` y `MUST` disparan el aviso `V14`.

### Los patrones EARS

| Patrón | Forma | Cuándo |
|---|---|---|
| Ubicuo | `El sistema DEBE …` | Comportamiento permanente, sin condición |
| Event-driven | `WHEN <disparador>, el sistema DEBE …` | Reacción a un suceso |
| State-driven | `WHILE <estado>, el sistema DEBE …` | Mientras dura una situación |
| Optional-feature | `WHERE <opción activa>, el sistema DEBE …` | Sólo si una capacidad está habilitada |
| Unwanted-behaviour | `IF <condición indeseada>, THEN el sistema DEBE …` | Manejo de error o abuso |
| Complejo | `WHILE <estado>, WHEN <disparador>, el sistema DEBE …` | Combinación de estado y suceso |

Un requisito, un patrón, una frase. Si necesitas dos frases con dos disparadores, son dos requisitos (`V02`).

### Tres reglas para que dos lectores lean lo mismo

Después de `/venoxia:validate` viene `/venoxia:diverge`: dos lectores que no estuvieron en esta conversación leen el delta a solas y el script cuenta en qué difieren. Un delta bien formado puede no converger nunca sin que haya un solo desacuerdo sobre el comportamiento, y las tres causas más frecuentes se evitan al redactar:

1. **Un hecho por escenario.** Un `THEN` con dos consecuencias —«queda `missing` y el proceso termina con código `1`»— produce dos lecturas que difieren en cuál de las dos recogen, y el script las enfrenta aunque ninguna niegue a la otra. Si son dos hechos, son dos escenarios.
2. **Ningún código de salida ni valor dentro del `WHEN`.** El `WHEN` describe la condición; el resultado —código, estado, cifra— va sólo en el `THEN`. Cuando el `WHEN` ya trae el resultado, un lector se lo lleva al efecto y el otro no, y la divergencia que sale no habla del sistema sino de dónde puso cada uno la misma frase.
3. **El mismo sustantivo para la misma cosa en todo el delta.** Si el delta llama «runner» a lo que tres párrafos después llama «el comando» y en los metadatos `test_command`, los lectores heredan una palabra cada uno y dos efectos que dicen lo mismo salen con similitud cero. Elige la palabra en el primer requisito y no la cambies.

El caso que fijó las tres: el delta de `oracle` (13 escenarios de línea de comandos) pasó cuatro rondas de divergencia sin converger, con seis duras en la última, y ninguna era un desacuerdo sobre comportamiento. En «A runner that sleeps past the limit» un lector escribió «mata el proceso del test_command» y el otro «marca el requisito como timeout»: el mismo escenario contaba dos hechos, y cada lector recogió uno. Con un hecho por escenario, el resultado fuera del `WHEN` y una sola palabra para el runner, la relectura dio cero duras.

### `verifies:` y `confidence:` se escriben con el requisito, nunca después

Esto no es un detalle de estilo. **Un oráculo añadido al final se escribe para que el validador calle, no para que la spec sea verdad.** Cuando el requisito ya está redactado y sólo falta rellenar `verifies:`, la pregunta que te haces es «¿qué ruta hace que pase `V07`?»; cuando lo escribes a la vez, la pregunta es «¿qué test falla si esto se incumple?», que es una pregunta sobre el comportamiento y a menudo cambia la redacción del requisito.

Así que el orden es: **título → oráculo → narrativa → escenarios → confianza**. Si no eres capaz de nombrar el test que fallaría, todavía no tienes un requisito: tienes un deseo, y hay que hablarlo con el usuario antes de escribirlo.

- `verifies:` es una ruta de fichero de test relativa a la raíz del proyecto. Se admiten varias separadas por coma o espacio; basta con que **una** contenga el `@covers`.
- El fichero **puede no existir todavía**. Mientras no exista sale `V07` en rojo (y `V08` en su lugar en cuanto el fichero exista sin el `@covers`; las dos no saltan a la vez sobre el mismo fichero), y ese rojo es correcto: la spec afirma que hay un oráculo y el disco dice que no. No crees un test vacío ni un fichero de relleno para apagarlos; eso es precisamente escribir el oráculo para que el validador calle.
- El test lleva `@covers <ID>` en un comentario. El vínculo es doble a propósito: desde la spec al test y desde el test a la spec, para que borrar uno de los dos lados se note.
- `confidence:` es `high`, `medium` o `low` (`V09`). `low` obliga a `revisit:` con el hecho que resuelve la apuesta —nunca una fecha, y nunca un «ya veremos»—: eso lo comprueba `V10` y sin ello el validador rechaza. El `why:` no lo exige ninguna regla, pero escríbelo igual en todo lo que no sea `high`: una apuesta sin porqué no se puede revisar, y quien la mire en tres meses no sabrá qué reconsiderar. Y el conjunto tiene presupuesto: como mucho el 30 % de los requisitos del ámbito en `low` (`V11`). Si te pasas, no bajes etiquetas para cuadrar: significa que hay demasiadas preguntas abiertas y toca resolver algunas con el usuario antes de seguir.
- `from:` enlaza el documento de origen que justifica el requisito. Su ausencia en una capability nueva es aviso (`V15`).

### Asignación de IDs

Formato: `R-` + **2 a 4 letras mayúsculas** del dominio + `-` + **tres dígitos**. `R-CHK-014`, `R-BILL-003`, `R-AUTH-101`.

- El prefijo de dominio es estable por capability: una vez que `checkout` es `CHK`, lo es para siempre. Si la capability ya tiene requisitos, hereda su prefijo tal cual; no lo reinventes.
- **Antes de asignar un número, comprueba los que ya están ocupados.** Con la herramienta `Grep`, patrón `R-[A-Z]{2,4}-[0-9]{3}`, sobre `.venoxia/` entero —capabilities y changes en vuelo, no sólo la capability que tocas— con `output_mode: content`. Dos changes abiertos a la vez pueden reclamar el mismo número si sólo miras las capabilities vivas.
- Numera de forma ascendente a partir del mayor existente del prefijo. Los huecos se dejan como están; nunca se rellenan ni se renumera lo que ya vive: un ID publicado es una dirección estable a la que apuntan tests, commits y conversaciones.
- En `MODIFIED`, `REMOVED` y `RENAMED` se reutiliza **exactamente** el ID que ya existe en la capability viva (`V13`). Cambiar el ID de un requisito existente lo convierte en otro requisito distinto y rompe la trazabilidad.

## Paso 4 · Validar y corregir hasta verde antes de devolver el control

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" --root "<raíz>" --change "<id>" --no-color
```

`0` conforme, `1` no conforme, `2` error de uso.

Itera: lee cada finding, corrige el delta o la propuesta, vuelve a ejecutar. **No devuelvas el control mientras quede un solo error que la propia spec pueda arreglar** — es decir, todo salvo `V07` y `V08`, que dependen de un test que aún no está escrito. Corregir aquí es barato; corregirlo después de que alguien haya implementado contra una spec mal formada, no.

Los avisos no bloquean, pero se resuelven o se justifican uno a uno en la entrega. Un aviso ignorado en silencio es un aviso que nadie volverá a mirar.

Cuando no quede ningún error salvo `V07`/`V08`, actualiza `change.json` a `"state": "specified"`. **Esta skill nunca escribe `"state": "validated"`**: ese estado sólo lo otorga `/venoxia:diverge`, y sólo cuando el validador y la divergencia pasan los dos.

## La entrega

Termina con un informe corto, sin adornos:

- Los ficheros escritos, con ruta.
- Los requisitos creados o modificados, ID y título, una línea cada uno.
- El veredicto literal del validador y, si quedan `V07`/`V08`, la lista exacta de tests que hay que escribir con la línea `@covers` que debe llevar cada uno.
- Toda decisión que tomaste tú porque la petición no la cubría, marcada como tal. Una asunción tuya que el usuario no ve es una asunción que nadie revisa.
- El siguiente paso, la cadena completa hasta el código: escribir los tests → `/venoxia:diverge` para someter el delta a los lectores aislados → `/venoxia:verify` graba el oráculo en rojo → se escribe el código → `/venoxia:verify` otra vez graba el verde y deja el change en `verified`. Escribir esos tests está permitido con el change en `specified`: son el oráculo que el delta declara en `verifies:`, y es la única puerta que el guardián abre antes de `validated`.
