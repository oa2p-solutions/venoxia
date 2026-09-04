---
name: charter
description: "Conduce la entrevista que define un proyecto que todavía no existe y escribe el acta verificable: propósito, usuarios con su apaño de hoy, capabilities priorizadas con su criterio de terminación, fuera de alcance razonado y apuestas con fecha de revisión. Debe usarse cuando el usuario diga «empiezo un proyecto», «quiero definir qué voy a construir», «no sé por dónde empezar», «define el alcance», «proyecto nuevo desde cero», o cuando /venoxia:specify no encuentre comportamiento previo que cambiar."
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

Produces dos ficheros, y un tercer grupo sólo si el usuario lo pide, todo bajo `.venoxia/`: `charter.md`, `principles.md` y los directorios de las capabilities. **Nunca tocas código de producción desde esta skill, ni el andamiaje del proyecto.** Igual que `/venoxia:specify`: definir y construir en el mismo impulso es exactamente lo que el guardián existe para impedir.

---

## Las cuatro reglas que gobiernan la entrevista

> ### 1. Esto es una entrevista, no un formulario.
>
> Un cuestionario fijo de doce preguntas se contesta con doce respuestas genéricas, porque nadie se esfuerza en contestar una pregunta que se le habría hecho igual a cualquier otro. **Cada tanda se construye con lo que la anterior reveló**, y la segunda pregunta de verdad es siempre la que no tenías preparada. Si al terminar te das cuenta de que podrías haber preguntado lo mismo antes de escuchar nada, no has entrevistado: has rellenado un impreso.

> ### 2. Se pregunta por comportamiento observable, no por vocabulario de producto.
>
> Ésta es la diferencia entre una entrevista útil y un brief de agencia. La columna de la izquierda produce prosa que no se puede verificar; la de la derecha produce, literalmente, las filas de la tabla de capabilities.
>
> | No preguntes | Pregunta |
> |---|---|
> | «¿Cuál es tu propuesta de valor?» | «Cuando esto funcione, ¿qué podrá hacer alguien que hoy no puede?» |
> | «¿Quién es tu usuario objetivo?» | «¿Quién tiene hoy este problema, y cómo se apaña sin ti?» |
> | «¿Qué funcionalidades quieres?» | «Si sólo pudieras entregar una cosa el mes que viene, ¿cuál dolería no tener?» |
> | «¿Cuál es el alcance?» | «¿Qué te van a pedir que hagas y vas a decir que no? Di el porqué.» |
>
> La prueba antes de lanzar cualquier pregunta: *¿la respuesta va a nombrar a alguien haciendo algo?* Si sólo puede producir un adjetivo —ágil, escalable, intuitivo—, la pregunta está mal hecha y la culpa no es de quien la contesta.

> ### 3. Lo que se supone no se escribe como si se supiera.
>
> Es la tesis de Venoxia aplicada a la fase de definición. Un requisito declara `confidence:` porque una apuesta sobre el comportamiento futuro no vale lo mismo que un hecho; un acta hace lo mismo con `## Bets`. Todo lo que el acta afirma sale de dos sitios muy distintos —de algo que alguien ha visto, o de algo que alguien supone—, y escritos con la misma tipografía se leen igual dentro de tres meses.
>
> Por eso la pregunta **«¿esto lo has visto o lo supones?»** se hace explícitamente, y como mínimo sobre el propósito y sobre la capability de prioridad 1. Lo observado se queda en la prosa del acta; lo supuesto baja a `## Bets` con su `confidence`, su `revisit` y su `fatal`. **Un acta que no distingue lo observado de lo supuesto es un documento de deseos**, y se lee como si fuera un plan.

> ### 4. Nada entra en el acta que el usuario no haya dicho o elegido.
>
> Puedes proponer todo lo que quieras: para eso están las opciones de cada pregunta. Lo que **nunca** haces es rellenar un hueco por tu cuenta y presentarlo como acordado. Vale el mismo criterio que `/venoxia:specify` aplica a los principios: unos inventados son peores que ninguno, porque parecen decididos, y nadie vuelve a discutir lo que ya parece decidido.
>
> Todo lo que propongas va marcado como propuesta tuya, y el usuario lo aprueba, lo tacha o lo corrige. El silencio no aprueba nada.
>
> Y si al escribir el acta te falta una casilla, hay dos caminos y ninguno es rellenarla con lo que suele ponerse ahí. Si el acta puede vivir sin ella —un segundo usuario, una fila más de la tabla—, se queda vacía y lo dices en la entrega. Si es de las que el linter exige —el `Done when` de una capability, un no-alcance—, no se puede dejar vacía **ni** inventar: es exactamente el motivo de una pregunta más.

---

## Cómo se pregunta

Se conduce con `AskUserQuestion`, y el manejo de la herramienta no es un detalle: es dónde se gana o se pierde la entrevista.

- **Como mucho cuatro preguntas por llamada, y sólo van juntas las que no dependen unas de otras.** Dos preguntas en la misma tanda donde la redacción de la segunda depende de lo que conteste la primera son una tanda mal montada: pregunta la primera sola y monta la siguiente con la respuesta.
- **Cada opción es una respuesta que el usuario podría haber dado con sus palabras, no una categoría.** «El dueño, que lleva las reservas en un cuaderno» es una opción; «usuario interno» no lo es. Dos a cuatro opciones por pregunta: con una no hay elección y con seis no hay lectura.
- **Marca la recomendación sólo cuando tengas una razón sacada de lo que el usuario ya ha dicho**, ponla en la descripción de esa opción y di la razón ahí mismo («recomendada: es la única que el apaño de hoy justifica»). Una recomendación sin razón no es una recomendación, es un empujón. Cuando no la tengas, no marques ninguna: da igual que la herramienta la admita.
- **No gastes una opción en «otra cosa»**: el usuario siempre puede escribir lo suyo, y esa opción sólo sirve para que parezca que hay tres cuando hay dos.
- **Una respuesta escrita a mano gana a cualquier opción tuya.** Cópiala al acta con sus palabras, no con las tuyas mejoradas. La frase del usuario es el dato; tu reformulación es una interpretación que nadie ha aprobado.

## Paso 1 · Leer la sala antes de la primera pregunta

Preguntar por el stack teniendo un `package.json` delante es una entrevista que no ha leído la sala, y el usuario lo nota en la primera pregunta.

1. `Glob` sobre las señas de un proyecto ya empezado: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, `pom.xml`, `Gemfile`, `*.csproj`, `Dockerfile`, `README.md`, `docs/**`, `prfaq/**`.
2. `Read` de lo que aparezca, y `Grep` para lo grande. Un `README` de tres párrafos suele contener ya el propósito y medio no-alcance.
3. `Glob` sobre `.venoxia/**` para saber si hay acta, principios o capabilities vivas.

Con eso, **di en voz alta lo que has deducido y sigue**, en una línea, sin convertirlo en pregunta: «veo un `package.json` con Next.js y Prisma: doy por hecho el stack y no pregunto por él; corrígeme si va a cambiar». Lo que el disco ya contesta no se pregunta, se confirma de pasada.

Y una lectura que cambia toda la entrevista: **si ya hay código, el acta se escribe a posteriori.** Entonces el propósito hay que reconstruirlo de lo que el código ya hace, la mitad de las capabilities existen aunque nadie las haya nombrado, y la de prioridad 1 casi nunca es la primera del proyecto sino la siguiente. Dilo y adapta las tandas: preguntar «¿qué vas a construir?» a quien lleva seis meses construyéndolo es empezar por ofender.

Con código delante hay que decidir además una cosa que la tabla no tiene columna para decir, así que se dice aquí: **la prioridad `#` de un proyecto ya empezado es el orden en que las capabilities se van a poner bajo especificación, no el orden en que se van a programar.** Lo que ya funciona ocupa fila igual —un acta que sólo lista lo que falta describe medio sistema—, y su `Done when` se escribe como el hecho que tiene que **seguir** siendo cierto: es el criterio de no romperlo, y es exactamente lo que su primer delta tendrá que preservar. Ojo al número que le pones: si le das uno alto y luego resulta que hay que especificarla primero —porque el cambio que quieres hacer la toca—, `C16` avisará de que el orden que se sigue no es el que el acta declara, y con `--strict` eso es rojo. Cuando lo primero que vas a especificar es comportamiento que ya existe, ésa es la fila 1, aunque su código lleve seis meses escrito.

## Paso 2 · Si ya hay acta, se retoma

Si existe `.venoxia/charter.md`, léelo entero y pásale el linter antes de preguntar nada. Después enseña lo que hay en cuatro líneas —el propósito, cuántos usuarios, la capability 1 con su `Done when`, cuántas apuestas— y **lo que falta**, que es lo que de verdad interesa.

Trae también, delante de todo, **todas las apuestas vivas con su `revisit`**, y pregunta una por una si ese hecho ya ha ocurrido. Ése es el momento en que una apuesta se resuelve, y por eso `revisit` declara un hecho y no una fecha: nadie abre un fichero porque hoy sea 12 de noviembre, pero cualquiera sabe contestar a «¿ya habéis cerrado las diez primeras compras?». Las que hayan ocurrido se resuelven ahora —sube la confianza y quita el `revisit`, o corrige lo que la apuesta daba por hecho—; las que no, se quedan como están y se dice.

Luego pregunta, con opciones y sin dar por hecho ninguna: **continuar por donde se quedó**, **revisar una sección concreta** (y cuál) o **empezar de cero**. Si es lo último, avisa antes de escribir: el acta nueva pisa la anterior y esta skill no guarda copias —escribe tres cosas y no una cuarta—, así que si quiere conservarla, que la aparte antes.

## Paso 3 · La entrevista, tanda a tanda

Seis cosas hay que sacar, y ninguna se saca preguntándola por su nombre. Lo que sigue es el material de la entrevista, **no su guion**: el orden lo fija lo que el usuario acaba de decir.

### Tanda A · Qué cambia en el mundo, y quién lo nota

Sale de aquí: el borrador de `## Purpose` y el primer usuario.

Dos preguntas, y caben en la misma llamada porque no dependen la una de la otra:

1. **«Cuando esto funcione, ¿qué podrá hacer alguien que hoy no puede?»** Las opciones son tres formulaciones concretas del cambio, sacadas de la frase con la que arrancó el usuario y escritas como algo que alguien hace.
2. **«¿Quién tiene hoy ese problema?»** Opciones: papeles concretos con su contexto pegado, no segmentos de mercado.

Lo que **no** va en esta tanda: «¿y cómo se apaña hoy?». Su redacción depende de a quién haya elegido, así que va en la siguiente. Éste es el ejemplo canónico de la regla de arriba.

Y una salida que hay que tener preparada, porque es el caso más común de todos: **si la primera pregunta vuelve vacía —«no sé, por eso te pregunto»—, no insistas ni la reformules.** Da por buena la respuesta, salta a la tanda B y vuelve al propósito cuando tengas el apaño delante. La primera pregunta da por supuesto que el usuario ya ha imaginado el futuro, y quien llega con «algo que nos ayude con los informes mensuales» no lo ha imaginado todavía; describir lo que hizo el mes pasado, en cambio, sabe hacerlo cualquiera. Un proyecto difuso se ordena por el pasado, no por el futuro.

### Tanda B · El apaño de hoy

Sale de aquí: la viñeta `**hoy:**` de cada usuario y —esto es lo que casi nadie ve— **la primera capability**. Una capability es lo que hace que un apaño deje de hacer falta: si el apaño es «repasa el cuaderno cada mañana», la capability es lo que sustituye a ese repaso, y ya está nombrada sin haber preguntado por funcionalidades.

Qué escuchas:

- Si el apaño **existe y es trabajoso**, tienes usuario, capability y motivo, los tres del tirón. Es la mejor respuesta posible.
- Si el apaño es **«hoy nadie hace esto»**, no hay usuario todavía: hay una hipótesis. Anótala como apuesta y monta la tanda siguiente sobre ella: quién está pagando hoy el coste de que no exista, y en qué se le nota.
- Si el apaño es **otro producto que ya usan**, la pregunta siguiente es qué les obliga a hacer ese producto que no quieren hacer. Ahí está la frontera de tu propósito, y también medio no-alcance.

### Tanda C · La primera entrega y su prueba

Sale de aquí: la fila 1 de la tabla con su `Done when`.

**«Si sólo pudieras entregar una cosa el mes que viene, ¿cuál dolería no tener?»** Las opciones son las capabilities que ya han aparecido en las tandas anteriores, cada una con el apaño que quita. Y en la llamada siguiente —no en la misma, porque depende de ésta—: **«¿Qué tendría que pasar para que dijeras que eso ya funciona? ¿Quién lo ve y qué ve?»**

**Regla de no avanzar.** Si el `Done when` no nombra a alguien y algo que esa persona ve, la tanda no termina: se reformula la pregunta, no se apunta la respuesta. «Que sea rápido» no tiene sujeto, «que funcione bien» no tiene verbo comprobable y «desplegado en producción» describe un hito nuestro, no algo que le pase a nadie. Un `Done when` que no se puede observar lo da por cumplido quien tenga prisa, que es justo el escenario contra el que se escribe.

### Tanda D · El no

Sale de aquí: `## Out of scope`, y de paso el orden del resto de la tabla.

**«¿Qué te van a pedir que hagas y vas a decir que no? Di el porqué.»** Opciones: las cosas que en un proyecto así se piden siempre, cada una con la razón por la que sería un no aquí.

Distingue las dos cosas que se confunden en esta tanda, porque el acta las guarda en sitios distintos: **«más adelante» no es un no-alcance**, es una fila con un número alto en la tabla. Aquí abajo va lo que no se va a hacer y por qué no compensa. Si todo lo que sale es «más adelante», el proyecto todavía no ha dicho que no a nada, y eso hay que decirlo tal cual.

### Tanda E · ¿Lo has visto o lo supones?

Obligatoria, y como mínimo sobre el propósito y sobre la capability de prioridad 1. Es la tanda que convierte el acta en un documento honesto. Tiene dos mitades y las dos son obligatorias: la primera mira al pasado y la segunda al futuro, y **una apuesta que no aparece en la primera casi siempre aparece en la segunda**.

#### E.1 · Lo que ya pasó

Primera pregunta, con estas cuatro opciones tal cual:

| Respuesta | Qué se hace con ella |
|---|---|
| «Lo he visto: me lo ha contado alguien que lo sufre, más de una vez» | No es apuesta. Va a la prosa del acta |
| «Lo he visto una vez, en un caso» | Apuesta con `confidence: medium` |
| «Lo supongo, pero me parece razonable» | Apuesta con `confidence: medium` |
| «Es una corazonada» | Apuesta con `confidence: low` |

Y para cada apuesta, dos preguntas más, y la primera va **partida en dos** porque juntas se contesta sólo la mitad:

- **«¿Qué verías que te haría cambiar de opinión?»** → `why`.
- **«¿Y qué tendría que pasar para que pudieras verlo?»** → `revisit`.

La segunda pide un **hecho**, no una fecha: «cuando hayamos cerrado las diez primeras compras», «cuando el primer proveedor conteste por el hilo». **Tú no lo inventas nunca**, y no es una regla de estilo: no sabes a qué ritmo pasan las cosas en este negocio, así que cualquier plazo que escribas es un número al aire con aspecto de compromiso. Si la respuesta no llega, no la rellenes: pregunta por el ritmo real —«¿cuántos presupuestos os llegan a la semana?»— y deja que el hecho salga de ahí. `C12` rechaza tanto las fechas como los «ya veremos», y con razón: las dos cosas son la misma, una casilla ocupada sin nada dentro.

Y la tercera: **«si esto sale mal, ¿el proyecto sigue teniendo sentido?»**, que es `fatal`.

#### E.2 · Lo que hará falta que alguien haga

Sobre **cada fila de la tabla**, no sólo sobre la primera, una pregunta que la mitad de arriba no puede hacer:

> **«Para que esta fila valga, ¿alguien tiene que hacer algo que hoy no hace?»**

«¿Lo has visto o lo supones?» pregunta por hechos del presente, y la respuesta honesta sobre un comportamiento que todavía no existe es «no lo he visto porque no existe». Por ahí se cuela intacta la suposición más cara que un acta puede tener: **que alguien va a rellenar un dato manualmente, más tarde, sin recompensa inmediata.** Marcar si el proveedor cumplió, valorar al candidato, cerrar la incidencia, confirmar la recepción. En la entrevista todo el mundo dice de buena fe que sí lo hará, y en el mes tres nadie lo hace.

Cuando la respuesta sea que sí, tres preguntas más, y son las que deciden lo que se escribe:

| Pregunta | Qué destapa |
|---|---|
| **¿Cuánto tarda en pasar desde que la persona hace lo suyo?** | Dentro de la misma sesión no es una apuesta. Días o semanas después, sí |
| **¿Qué gana quien lo hace, en ese momento?** | Si el beneficio se lo lleva otro, u otro día, la apuesta es de las malas |
| **¿Qué fila se queda vacía si nadie lo hace?** | Si alguna otra capability lee ese dato, el daño no sale donde lo esperas |

Con eso ya tienes la apuesta entera. Y si la tercera pregunta señala a otra fila —una que ordena, puntúa o resume a partir de lo que aquí se marca—, es **`fatal: yes`** aunque la fila que lo recoge parezca inofensiva: cuando nadie marque, no fallará esta capability, saldrá en blanco la otra, y quien la mire creerá que el fallo está donde no está.

La apuesta se escribe **nombrando el slug de la fila en su prosa**. No es cosmético: es lo único que enlaza una apuesta con la capability que sostiene, y es lo que miran `C18` y `C19` para saber si el riesgo ya está declarado. Sin el slug, la apuesta existe y el linter sigue avisando, con razón: dentro de tres meses nadie sabrá de qué fila hablaba.

Y una salida que conviene ofrecer antes de dar la apuesta por buena: **si al escribirla ves que no te fías del todo, la respuesta no es la apuesta, es rediseñar la fila** para que el dato lo recoja el sistema en vez de esperar a que alguien entre a ponerlo. Una apuesta declarada avisa; un dato que se recoge solo no hace falta que avise.

#### Lo que sale de las dos mitades

Una apuesta con `fatal: yes` y `confidence: low` es la línea más importante del acta. No la entierres entre las demás: se dice en voz alta en la entrega y es lo que habría que ir a comprobar esta semana, antes de escribir ninguna spec.

### Tanda F · Confirmar los principios

Los que fuiste anotando durante la entrevista, más las convenciones técnicas. Va en el Paso 4, porque no se pregunta igual que lo demás.

### Cuando la respuesta no es una respuesta

Cuatro casos, y los cuatro se arreglan con la pregunta siguiente, no señalando el error:

- **No lo sabe todavía** («no sé», «para eso te pregunto», «algo que nos ayude con los informes»). Es la respuesta más común cuando el proyecto nace de una molestia y no de una idea, y no tiene nada de mala: es la pregunta la que ha pedido imaginar un futuro. **No la repitas con otras palabras: cámbiala por el pasado.** «Cuéntame el último que hiciste: qué hiciste, en qué orden, y dónde se te fue el tiempo.» De ahí sale el apaño de la tanda B, y del trozo del apaño que más duele sale la primera capability, sin haber preguntado nunca qué quiere construir. Si la respuesta al pasado también viene vacía, entonces sí que no hay proyecto todavía, y eso se dice.
- **Contesta con una funcionalidad** («quiero un dashboard»). Pregunta qué decisión toma mirándolo y qué haría distinto después de mirarlo. Un dashboard que nadie usa para decidir nada no es una capability; y si sí decide algo, ya tienes escrito el `Done when`.
- **Contesta con implementación** («necesito Postgres y una cola»). Eso no es asunto del acta. Anótalo como candidato a convención técnica para el Paso 4, dilo, y vuelve a la pregunta.
- **Todo es prioridad 1.** No discutas: fuerza la elección de dos en dos. «Si sólo cupiera una de estas dos el mes que viene, ¿cuál?» tiene respuesta aunque «ordena estas seis» no la tenga.

## Paso 4 · Los principios se recogen, no se piden

**«¿Cuáles son tus principios?» es una pregunta que nadie sabe contestar.** Lo que se obtiene preguntándola es una lista de virtudes que no excluye nada, y un principio que no excluye nada no gobierna nada. Un principio aparece en otro sitio: **cuando el usuario elige entre dos cosas que las dos son buenas.** El trabajo se reparte en dos clases y se hace de dos maneras distintas.

**De convención técnica.** Los propones tú enteros y el usuario tacha. Son decisiones que hay que tomar sí o sí, que casi nunca tienen una respuesta mejor que otra y que sólo hacen daño cuando cada trozo del sistema elige la suya. Propón únicamente las que la forma del proyecto justifique —no ofrezcas convenciones HTTP a una herramienta de línea de comandos— y pregúntalas en **una sola llamada de selección múltiple**: lo que no se marque, no entra.

| Tensión | Convención que puedes proponer entera |
|---|---|
| Errores de una API | `4xx` lo que el cliente puede arreglar, `5xx` lo que no; `409` para el conflicto de estado; nunca un `200` con un error dentro |
| Reintentos | toda escritura reintentable es idempotente y acepta clave de idempotencia |
| Tiempo | se guarda en UTC y se muestra en la zona del usuario; las fechas, ISO 8601 |
| Dinero | enteros en la unidad mínima, nunca coma flotante |
| Identificadores | opacos y estables; no se reutilizan ni se renumeran |
| Borrado | se marca, no se borra, mientras algo pueda referenciarlo |

**De dominio.** Salen del usuario, siempre, y no se preguntan: se cazan mientras habla. El detector es una frase con dos cosas buenas y una elegida —«prefiero X, aunque…», «mejor perder Y que Z», «si tengo que elegir…»—. Anótala **literal** en el momento, con sus palabras, y al final de la entrevista devuélvesela en la forma canónica para que la confirme:

> **Ante `<la tensión>`, se prefiere `<A>` a costa de `<B>`.** `<Por qué, con las palabras del usuario.>`

**No los inventes**: un principio de dominio fabricado por ti se convierte en una restricción que nadie recuerda haber aceptado y que a partir de mañana decide specs.

**Pero cazar no basta, porque hay tensiones que la tabla trae escritas aunque el usuario no las haya dicho en voz alta.** Cuando una capability promete un juicio y no un dato —comparar, puntuar, ordenar por varios criterios, recomendar, señalar cuál gana—, el desempate existe: alguien va a tener que decidir qué pasa cuando el más barato es el más lento. Que no aparezca en la entrevista no significa que no haga falta; significa que se va a tomar sin que nadie mire. Ahí sí se pregunta, y se pregunta **con la tensión concreta de su tabla delante**, no en abstracto:

> «La fila 2 compara por precio, plazo y forma de pago. Si un proveedor es 600 € más barato y tarda un mes más, ¿cuál quieres que salga marcado como el que gana?»

Ésa es una pregunta que se puede contestar, a diferencia de «¿cuáles son tus principios?». Y **preguntar no es inventar**: lo que no puedes escribir es la respuesta; la pregunta es tuya y es tu trabajo hacerla. Tres respuestas posibles y las tres son buenas:

- **Elige uno.** Ya tienes el principio, con sus palabras.
- **«Depende».** Pregunta de qué depende: eso también es el principio, y suele ser mejor que el anterior.
- **«Que no elija el sistema, que lo vea el comprador y decida él.»** Entonces no hay principio que escribir, pero **hay una celda que arreglar**: si la capability no arbitra, «Qué podrá hacer» no puede decir que arbitra. Corrige la fila.

Si aun así el usuario no quiere decidirlo hoy, se respeta, y entonces el desempate es una apuesta: va a `## Bets` con su `revisit`, no a los principios. Lo que no puede es desaparecer.

Y si de verdad no apareció ninguno y la tabla tampoco arbitra, `principles.md` sale sin principios de dominio y lo dices. Es un final legítimo: hay proyectos que sólo mueven datos de un sitio a otro y no tienen ningún juicio que declarar.

## Paso 5 · Cuándo se para

**Una entrevista que no termina es peor que una corta.** Hay un mínimo y es corto: cuando estén

1. el propósito,
2. **un** usuario con su `**hoy:**` y su `**con esto:**`,
3. la capability de prioridad 1 con su `Done when` observable,
4. **un** no-alcance con su porqué,
5. la tanda E pasada —**las dos mitades**— sobre el propósito y sobre la capability de prioridad 1, con lo que resulte supuesto ya escrito en `## Bets`,
6. y, **sólo si alguna fila de la tabla arbitra**, el desempate resuelto: o un principio de dominio, o una apuesta que diga que aún no se ha decidido.

el acta ya vale para escribir la primera spec. Todo lo demás —el segundo usuario, la fila 4, la apuesta que se le acaba de ocurrir— se completa después, y se completa mejor cuando haya algo funcionando. Cuando tengas esas cosas, **ofrece cerrar**; no sigas preguntando porque queden casillas.

Las dos últimas entran en el mínimo y no en «todo lo demás», y no es un capricho: son las únicas de la lista que no se pueden añadir más tarde en las mismas condiciones. Las otras cuatro siguen ahí mañana esperando a que alguien las escriba. La diferencia entre lo que el usuario vio y lo que supuso, en cambio, se borra sola en cuanto pasan unas semanas, y entonces el acta entera se lee como si todo estuviera comprobado. Y un desempate que no está escrito cuando se redacta la primera spec no se queda pendiente: **se toma solo**, en una línea de un requisito, y a partir de ahí es «como funciona el sistema» sin que nadie recuerde haberlo acordado. Dos preguntas cuestan dos minutos hoy y no se recuperan después.

Y hay un tope por el otro lado: si después de seis tandas no hay una capability de prioridad 1 con un `Done when` observable, para igualmente y dilo. No es un fracaso de la entrevista, es su hallazgo más útil: el proyecto todavía no está en condiciones de que le escriban una spec, y saberlo hoy es mucho más barato que descubrirlo con tres meses de código encima.

## Paso 6 · Antes de escribir: el guardián se pone en pie

Esto se avisa **antes** del primer `Write`, no después del primer `deny`.

El guardián permite siempre mientras no exista `.venoxia/`: es su primer camino de decisión. El primer fichero que escribas crea ese directorio, y **a partir de ese instante toda edición de código fuera de `.venoxia/` se deniega** hasta que haya un change validado. El esqueleto del proyecto —`package.json`, `tsconfig.json`, `pyproject.toml`, `Dockerfile`, el `git init`— no es comportamiento observable, no va a tener nunca una spec y por tanto nunca va a tener un change que lo acredite. Se monta antes, o se pasa por la vía registrada.

Y si ya hay código —el caso del acta a posteriori—, el aviso es el mismo pero muerde antes, y hay que darlo con todas las letras: el esqueleto está montado, sí, pero lo siguiente que ibas a hacer era tocar `src/`, y desde el primer `Write` de esta skill eso pasa por un change validado. No es una molestia futura que ya se verá: es la próxima orden que el usuario va a teclear. Dilo antes de escribir el acta, con el comando que la desbloquea —`/venoxia:specify` y luego `/venoxia:validate`—, y no después.

Así que pregunta, una sola pregunta, tres opciones:

- **El esqueleto ya está** —o ya hay código de sobra—. Se escribe el acta ahora, sabiendo que a partir de ese momento la siguiente edición fuera de `.venoxia/` necesita su change validado.
- **Falta el esqueleto.** Se pausa la escritura, se monta ahora —fuera de esta skill, mientras el guardián todavía duerme— y después se escribe el acta. Es el camino recomendado cuando el proyecto está de verdad en cero.
- **Escribe el acta igualmente.** Entonces el andamiaje irá por un change con `"via": "direct"`, que el guardián permite y anota en `.venoxia/drift/direct.log`. El `change.json` no lo escribes tú: esta skill escribe tres cosas y no una cuarta. Dale el contenido exacto en la entrega para que lo cree él o se lo pida a Claude fuera de aquí.

Un usuario que descubre esta secuencia a base de `deny` desinstala el plugin, y con razón: se le ha bloqueado por no saber algo que nadie le dijo.

## Paso 7 · Escribir el acta

`.venoxia/charter.md`, a partir de `${CLAUDE_PLUGIN_ROOT}/templates/charter.md`: léelo primero y respeta sus encabezados estructurales tal cual, en inglés. La prosa la escribes tú, en español, y con las palabras del usuario siempre que las tengas. Los comentarios guía y el contenido de ejemplo de la plantilla se borran al rellenar: el ejemplo es ejemplo, no contenido heredado.

La forma es vinculante porque la comprueba un script:

| Sección | Forma exacta | Por qué así |
|---|---|---|
| `## Purpose` | Prosa, de una a tres frases. Dice qué cambia en el mundo, no qué se programa | Es la regla con la que se mide todo lo demás. Un propósito que no deja fuera nada no puede contestar «¿esto sirve al propósito?» |
| `## Users` | Uno o más `### <slug> · <Nombre del rol>`, cada uno con las viñetas `**hoy:**` y `**con esto:**`. El slug, kebab-case | La distancia entre las dos viñetas es el valor del proyecto para ese usuario. Si se parecen, para él no cambia nada |
| `## Capabilities` | Tabla con las cinco columnas exactas del bloque de abajo | Es de donde sale el `/venoxia:specify` de cada una y el nombre de su directorio |
| `## Out of scope` | Una o más viñetas `- **<Qué>.** <por qué no>` | Un «no» sin razón se vuelve a abrir en la primera reunión en la que alguien insista |
| `## Bets` | Cero o más `### B-NNN · <título>`, con prosa y el bloque de metadatos | Separa lo observado de lo supuesto antes de que pase el tiempo y ya no se distingan |

**Antes de dar el acta por escrita, un repaso que ningún script puede hacer por ti: cada dolor que nombraste en un `**hoy:**` tiene que acabar en algún sitio.** O en una fila de la tabla, o en `## Out of scope`. Las viñetas de `**hoy:**` son la parte del acta que se escribe con las palabras del usuario y sin filtrar, así que casi siempre nombran más problemas de los que el proyecto va a resolver —«y además somos tres comprando, cada uno con su hoja, sin ver lo que ha pedido el otro»—. Ese «además» es un dolor real que alguien ha dicho en voz alta, y si no aparece en ninguna de las dos secciones, el acta lo deja colgado: no está prometido, pero tampoco está descartado. Alguien lo leerá dentro de dos meses y dará por hecho que entra.

Recórrelas una por una y decide con el usuario, en una sola pregunta por cabo suelto: **entra** —y se le busca fila y prioridad—, o **no entra** —y se escribe como no-alcance, con su porqué—. La respuesta suele ser la segunda, y tarda diez segundos. Un no escrito vale más que un silencio.

Ese mismo repaso destapa la otra cosa que se escapa: **un dolor que no es del usuario que tienes en la lista**. Si la tabla promete algo que mira alguien por encima —un responsable que ve el histórico, un jefe de equipo que compara— y en `## Users` sólo está quien hace el trabajo del día, falta un papel. O se añade con sus dos viñetas, o la fila es del usuario que ya está; lo que no puede es que la capability sirva a alguien que el acta no nombra.

Las cinco secciones van siempre, en este orden y con estos encabezados exactos: es lo primero que comprueba el linter. `## Bets` puede quedarse sin ninguna apuesta debajo —es legal—, pero si en la tabla hay un `high`, el aviso llegará y con razón.

Las columnas de la tabla, en este orden y con estos títulos:

```
# | Capability | Qué podrá hacer | Done when | Risk
```

- **`#`** es la prioridad: entero, empieza en 1 y no se repite. Ordena por el dolor de no tenerlo, no por lo que cuesta hacerlo.
- **`Capability`** es el slug entre acentos graves, en kebab-case y en inglés. Es el mismo nombre que tendrá `.venoxia/capabilities/<slug>/spec.md`; bautizarla distinto en los dos sitios parte la trazabilidad sin que ninguna regla pueda verlo.
- **`Qué podrá hacer`** se escribe de modo que quepa literal entre comillas detrás de `/venoxia:specify "…"`, porque ahí es donde va a acabar.
- **`Done when`** es observable: quién lo ve y qué ve. El linter rechaza las dos maneras de no serlo. Una es arrancar con un verbo de implementación, en infinitivo o en participio —«implementar el endpoint», «desplegado en producción»—: eso dice lo que alguien va a programar. La otra es ser una fórmula que se puede dar por cumplida sin mirar nada —«el sistema funciona correctamente», «la funcionalidad está completa», «que sea rápido»—: eso dice lo que alguien va a **decir**. Y ninguna de las dos se arregla redactando mejor: se arregla con la pregunta de la tanda C, que es de quién lo ve y de qué ve.
- **`Risk`** es `high`, `medium` o `low`, y mide lo que no se sabe de esa capability, no lo que cuesta programarla. Un `high` sin ninguna apuesta escrita en `## Bets` es un aviso del linter, y casi siempre significa que la tanda E se despachó deprisa: un riesgo alto es, por definición, algo que se está dando por hecho.

El bloque de metadatos de una apuesta tiene la misma forma que el de un requisito —sangría cosmética, claves fijas en inglés— con estas cuatro claves:

```
confidence: low
  why:      no lo hemos comprobado con ningún restaurante real
  revisit:  cuando hayamos hablado con tres restaurantes que ya reserven por enlace
  fatal:    no
```

`confidence` es `high`, `medium` o `low`; `revisit` es **el hecho que resuelve la apuesta**, nunca una fecha y nunca un «más adelante»; `fatal` es `yes` o `no` y contesta a si el proyecto sigue teniendo sentido cuando la apuesta sale mal.

## Paso 8 · Escribir los principios

`.venoxia/principles.md`, en este orden: los tres principios del método, las convenciones técnicas que el usuario aprobó y los principios de dominio que dijo él.

Los tres del método se escriben sin preguntar, y no es una excepción a la regla 4: **no son del proyecto, son del plugin**, y quien instala Venoxia los acepta con él. Dilo así en el fichero.

```markdown
# Principios de la especificación

Este proyecto especifica antes de construir. Tres principios gobiernan cada requisito:

1. **Toda apuesta declara cómo se resuelve.** Un requisito sin `verifies:` no entra: si
   nadie puede comprobarlo, no es un requisito, es una intención.
2. **La confianza se declara, no se presume.** `confidence:` dice cuánto nos fiamos de la
   apuesta, y una apuesta con poca confianza nace con fecha de caducidad.
3. **La especificación describe comportamiento observable.** Si la implementación puede
   cambiar sin que cambie lo que el cliente ve, no pertenece a la especificación.

El presupuesto de incertidumbre del proyecto es del 30 %: como mucho tres de cada diez
requisitos pueden nacer con `confidence: low`.

## Convenciones técnicas

- **<Tensión>.** <La convención, en una frase.>

## Principios de dominio

- **Ante <la tensión>, se prefiere <A> a costa de <B>.** <Por qué, con las palabras del usuario.>
```

De este fichero el linter lee una sola cosa —si hay principios de dominio, para `C17`—; todo lo demás lo leen las personas y `/venoxia:specify` antes de redactar nada. Por eso sus encabezados van en español, a diferencia de los del acta, y por eso el de dominio se escribe **exactamente** así: `## Principios de dominio`.

Si una de las dos secciones quedó vacía, bórrala en vez de dejar el hueco con un ejemplo dentro. El hueco de la plantilla —el que trae `<la tensión>` entre ángulos— no cuenta como principio ni para el linter ni para nadie: dejarlo puesto es peor que borrar la sección, porque aparenta un acuerdo que no existe.

Con una excepción, y es la que `C17` va a señalar: **si alguna fila de la tabla arbitra, la sección de dominio no se borra por vacía.** O lleva el desempate, o la entrevista todavía no ha terminado. Vuelve al Paso 4 y haz la pregunta con la tensión concreta delante.

## Paso 9 · Pasar el linter y corregir hasta verde

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/charter_lint.py" --root "<raíz>" --strict --no-color
```

`0` conforme · `1` no conforme · `2` error de uso. Con `--json` sale el mismo veredicto en máquina.

**Con `--strict` desde la primera ejecución**, y aquí no hay excusa posible para el rojo. La spec tiene una: `V07` y `V08` se quedan rojas esperando un test que todavía no está escrito, y ese rojo es correcto. El acta no depende de nada externo —todo lo que necesita está en el mismo fichero—, así que **todo hallazgo, error o aviso, se resuelve aquí**, a veces con una pregunta más de por medio. Devolver el control con uno pendiente es dejar el acta a medio acordar.

Itera: lee cada hallazgo, corrige el acta, vuelve a ejecutar. Las reglas se llaman `C01`–`C19`, como las `V01`–`V16` del validador, y cada hallazgo trae su remedio: preséntalo como lo hace `/venoxia:validate`, con el error delante y el remedio pegado. No reclasifiques la severidad, no descartes un hallazgo por parecerte menor y no matices el veredicto: si el script sale con `1`, el acta no cumple.

Tres casos que se paran a preguntar en vez de corregirse solos, y los tres por el mismo motivo: el remedio pasaría por **inventar contenido**.

- Una columna `Done when` vacía —o llena con una fórmula que no dice quién ve qué— y un no-alcance que no existe —o que dice «nada por ahora», que para el linter es lo mismo— no se arreglan escribiendo algo plausible: se arreglan con una pregunta más al usuario.
- Una viñeta `**hoy:**` o `**con esto:**` que falta tampoco se completa con lo que ese papel suele hacer. O se pregunta, o se borra el usuario entero: un acta con un solo usuario de verdad es mejor que una con dos, uno de ellos con dos frases que nadie ha dicho, porque la segunda aparenta que se ha hablado con dos personas.
- Un riesgo alto sin apuestas **no se arregla bajando el riesgo a `medium`**. Eso apaga el aviso sin tocar el problema, que es el peor arreglo posible en una herramienta que existe para señalar lo que no se sabe. Se arregla preguntando qué se está dando por hecho en esa capability.

Y tres más, que son los avisos de fondo: `C17`, `C18` y `C19` no señalan la forma del acta, señalan algo que no se ha decidido todavía. Ninguno se calla escribiendo lo que suene bien.

- **`C17` · una capability arbitra y no hay principio de dominio.** El remedio es la pregunta del Paso 4, con la tensión concreta de su tabla delante. Escribir un principio que el usuario no ha dicho es exactamente lo que el Paso 4 prohíbe, y de propina apaga el aviso: quedaría un criterio inventado gobernando todas las specs del proyecto.
- **`C18` · un «Done when» absoluto sin apuesta que lo respalde.** Dos salidas y las dos son del usuario: bajar el listón a algo alcanzable, o dejarlo y declarar la apuesta. No elijas tú. «Sin corregir ninguno» puede ser una exigencia deliberada del negocio o una frase que sonaba bien, y sólo quien la escribió sabe cuál de las dos.
- **`C19` · un «Done when» que espera a que alguien vuelva.** Es la tanda E.2 sin hacer. Vuelve a ella con esa fila: cuánto tarda, qué gana quien lo hace, y qué otra fila se queda en blanco si no lo hace. Y **no lo arregles quitando el paso diferido de la celda**: la frase se queda limpia y la dependencia sigue ahí, sólo que ya no la ve nadie.

Los tres se callan también con el arreglo bueno cuando el arreglo bueno es rediseñar la fila —que el sistema recoja el dato en vez de esperar a alguien, que la celda no prometa un juicio que la capability no hace—. Eso no es apagar un aviso: es lo que el aviso pedía.

Corregir la forma es tuyo; rellenar el fondo, no.

## Paso 10 · Los directorios de las capabilities, sólo si se piden

Si el usuario lo pide, escribe `.venoxia/capabilities/<slug>/spec.md` a partir de `${CLAUDE_PLUGIN_ROOT}/templates/capability.md`, con el `## Purpose` sacado de la fila de la tabla y **sin ningún requisito**: los requisitos los escribe `/venoxia:specify` como delta, y adelantarlos aquí es escribir una spec sin oráculo por la puerta de atrás.

Crea sólo las que se vayan a tocar ya, y en el orden que declara la tabla. Una capability vacía que sigue vacía tres meses después es una promesa que nadie ha cumplido, con la agravante de que ocupa sitio y parece trabajo empezado; y una que existe saltándose a la de prioridad 1 hace que el linter avise de lo que está pasando de verdad —el orden que se sigue no es el que el acta declara—, que es un aviso que conviene escuchar en vez de callar.

## La entrega

Termina con un informe corto, sin adornos:

- Los ficheros escritos, con ruta.
- El acta en cuatro líneas: el propósito, cuántos usuarios, la capability 1 con su `Done when`, y cuántas apuestas hay.
- **Las apuestas con `fatal: yes`, delante y por su nombre**, con la fecha en la que se resuelven. Si alguna es además `confidence: low`, ésa es la primera frase de la entrega.
- **El desempate, si alguna fila arbitra**: el principio de dominio tal como quedó escrito, o —si el usuario prefirió no decidirlo hoy— la apuesta en la que se aparcó y su fecha. Es la línea del acta que más lejos llega: la va a leer cada `/venoxia:specify` de aquí en adelante, y es la única que decide comportamiento sin estar en ningún requisito.
- El veredicto literal del linter.
- Lo que quedó sin cerrar y qué haría falta para cerrarlo. Una casilla vacía se dice; no se disimula.
- Toda decisión que tomaste tú porque la entrevista no la cubría, marcada como tal. Una asunción tuya que el usuario no ve es una asunción que nadie revisa.
- **El siguiente paso, tecleado.** Literalmente la celda «Qué podrá hacer» de la fila 1, entre comillas:

  ```
  /venoxia:specify "reservar una mesa para una fecha y hora"
  ```

- Y el recordatorio del andamiaje si aún no está montado: `.venoxia/` ya existe, así que el guardián está en pie y el esqueleto del proyecto necesita un change con `"via": "direct"` para pasar.

  ```json
  {"id": "project-scaffold", "state": "draft", "via": "direct",
   "capabilities": [], "created": "2026-09-01T10:00:00Z"}
  ```

  En `.venoxia/changes/project-scaffold/change.json`, con la fecha de hoy. Queda anotado en `.venoxia/drift/direct.log`, que es exactamente para lo que existe ese diario.
