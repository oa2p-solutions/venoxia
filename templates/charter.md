# Reservas Bistró · Acta del proyecto

<!-- Plantilla del acta de Venoxia. El acta es el documento que existe antes de que haya
     producto: dice para qué se construye esto, quién lo va a notar, qué capabilities hay
     y en qué orden, qué se ha decidido no hacer y qué se está dando por supuesto. Vive en
     `.venoxia/charter.md` y la escribe `/venoxia:charter` a partir de una entrevista.

     Sustituye «Reservas Bistró» por el nombre de tu proyecto y deja el resto del
     encabezado como está: `<nombre> · Acta del proyecto` es la forma por la que se
     reconoce el fichero.

     Los encabezados estructurales y las claves de metadatos van en inglés porque los
     parsea `charter_lint.py`; la prosa va en español. Un acta rellenada tiene que pasar
     `python3 scripts/charter_lint.py --strict` antes de servir para nada: mientras el
     linter esté en rojo, lo que hay es un borrador de conversación, no un acuerdo.

     EL PROPÓSITO lleva su guía aquí arriba y no bajo su encabezado, porque `## Purpose`
     es la única sección de prosa libre del acta y ahí abajo se cuenta lo que hay: de una
     a tres frases que dicen qué cambia en el mundo cuando esto funcione, y nada más. Lo
     que no va ahí: qué se programa, con qué se programa y cuántas pantallas tiene. El
     propósito es la regla con la que se mide todo lo demás —dentro de dos meses alguien
     propondrá una capability nueva y la única pregunta será «¿esto sirve al propósito?»—,
     así que escríbelo de forma que un «no» sea posible: «ser la plataforma líder de
     gestión hostelera» no deja fuera nada, y por eso no contesta nada.

     El contenido de ejemplo es el mismo proyecto de arriba abajo, a propósito: se lee
     entero para ver cómo cada pieza obliga a la siguiente. Bórralo al rellenar, y borra
     también estos comentarios guía. -->

## Purpose

Que un restaurante pequeño deje de perder mesas por reservas apuntadas en un
cuaderno que sólo entiende quien lo escribió.

## Users

<!-- Uno o más `### <slug> · <Nombre del rol>`. El slug va en kebab-case y en inglés: es
     el nombre corto con el que el resto de la documentación se refiere a ese papel.

     Las dos viñetas no son adorno. `**hoy:**` es lo único verificable del apartado —se
     comprueba preguntándoselo a una persona de verdad— y `**con esto:**` es la promesa.
     La distancia entre las dos frases es exactamente el valor del proyecto para ese
     usuario: si se parecen, para él no cambia nada y sobra del acta.

     Un usuario cuyo `**hoy:**` no sabes escribir es un usuario inventado. Eso no lo
     prohíbe nadie, pero entonces la suposición baja a `## Bets` con su fecha de
     revisión, en vez de quedarse aquí con aspecto de hecho comprobado. -->

### owner · Dueño del restaurante
- **hoy:** apunta las reservas en un cuaderno y las repasa cada mañana.
- **con esto:** ve la ocupación de la noche desde el móvil sin llamar a nadie.

### diner · Cliente que reserva
- **hoy:** llama por teléfono y espera a que alguien coja.
- **con esto:** reserva desde el enlace del perfil, a cualquier hora.

## Capabilities

<!-- Tabla con cinco columnas exactas, en este orden y con estos títulos: `#`,
     `Capability`, `Qué podrá hacer`, `Done when` y `Risk`.

     · `#` — la prioridad. Entero, empieza en 1 y no se repite. Ordena por el dolor de no
       tenerlo, no por lo que cuesta hacerlo: la fila 1 es la que dolería no tener el mes
       que viene. Una tabla sin orden es una tabla en la que se empieza por lo cómodo.
     · `Capability` — el slug entre acentos graves, en kebab-case y en inglés. Es el mismo
       nombre que tendrá `.venoxia/capabilities/<slug>/spec.md`: bautizarla distinto en
       los dos sitios parte la trazabilidad sin que ninguna regla pueda verlo.
     · `Qué podrá hacer` — la capacidad en infinitivo, desde fuera. Escríbela de modo que
       quepa literal entre comillas detrás de `/venoxia:specify "…"`, porque ahí es donde
       va a acabar. Si para escribirla necesitas nombrar una tabla, un endpoint o una
       librería, todavía no es una capability: es una tarea.
     · `Done when` — cómo se sabrá que está hecha. Tiene que ser observable, y la prueba
       de que lo es son dos preguntas: **¿quién lo ve?** y **¿qué ve?**. «Que sea rápido»,
       «que funcione bien» y «desplegado en producción» no las contestan; el primero no
       tiene sujeto, el segundo no tiene verbo comprobable y el tercero describe un hito
       nuestro, no algo que le pase a nadie. Un `Done when` que no se puede observar se
       declara cumplido por quien tenga prisa. Los tres los rechaza el linter, y con
       ellos la frase que arranca por un verbo de implementación —«montar el
       formulario»— y la que es sólo una fórmula —«el sistema funciona correctamente»,
       «la funcionalidad está completa»—. Mencionar uno de esos verbos de pasada, en
       cambio, no cuenta: «el dueño ve las mesas libres sin configurar nada» describe un
       hecho y pasa.
       Y ojo con el criterio que no admite un fallo —«sin corregir ninguno», «siempre
       acierta»—: no está prohibido, pero casi nunca se elige a sabiendas, y el linter
       pide que se declare como apuesta o se baje a algo alcanzable. Lo mismo con el que
       sólo se cumple si alguien vuelve semanas después a rellenar un dato.
     · `Risk` — `high`, `medium` o `low`. Mide lo que no se sabe de esta capability, no lo
       que cuesta programarla: `high` es que puede resultar que no era la que hacía falta,
       o que su comportamiento correcto todavía está por decidir. Un `high` en la fila 1 no
       es un error, es la información más valiosa del acta: dice por dónde vas a aprender
       algo y qué apuestas va a tener que declarar la primera spec. -->

| # | Capability | Qué podrá hacer | Done when | Risk |
|---|---|---|---|---|
| 1 | `booking` | reservar una mesa para una fecha y hora | un cliente reserva y recibe la confirmación con su hora | high |
| 2 | `availability` | ver qué queda libre esta noche | el dueño abre el móvil y ve las mesas libres de hoy | medium |

## Out of scope

<!-- Una o más viñetas `- **<Qué>.** <por qué no>`. El porqué no es cortesía: un «no» sin
     razón se vuelve a abrir en la primera reunión en la que alguien insista, y entonces
     ya no hay nada escrito que oponer.

     **Un no-alcance vacío es sospechoso**, y ésa es la razón de que esta sección exista.
     Un proyecto que no ha dicho que no a nada no ha decidido nada todavía: significa que
     nadie ha mirado lo que va a pedir el primer cliente, o que se ha contestado «ya
     veremos» a todo. Los tres primeros meses de un proyecto así se van en la cuarta
     prioridad de alguien.

     Ojo a la confusión típica: «más adelante» no es un no-alcance. Lo que se hará después
     es una fila con un número alto en la tabla de arriba. Aquí abajo va lo que **no** se
     va a hacer, y por qué no compensa.

     Y una viñeta no es una entrada: «- nada por ahora», «- TBD» o «- ya veremos» ocupan
     la sección sin excluir nada, y el linter las cuenta como lo que son, que es como no
     haber escrito ninguna. -->



- **Pagos y señales.** No se cobra nada en la v1; el riesgo regulatorio no compensa
  hasta que haya reservas de verdad.
- **App nativa.** La web basta para lo que promete el propósito.

## Bets

<!-- Cero o más `### B-NNN · <título>`, numeradas de tres dígitos y sin reutilizar un
     número ya usado. Cada una lleva su prosa y, al final, el bloque de metadatos con las
     cuatro claves fijas —la misma forma que el bloque de un requisito, con la sangría
     puramente cosmética y las claves en inglés.

     Ésta es la sección que separa un acta de una lista de deseos. Todo lo que el acta
     afirma sale de dos sitios muy distintos: de algo que alguien ha visto, o de algo que
     alguien supone. Las dos cosas escritas con la misma tipografía se leen igual dentro
     de tres meses, y para entonces nadie recuerda cuál era cuál. Lo observado se queda
     arriba, en prosa; **lo supuesto baja aquí, con su fecha**.

     · `confidence` — `high`, `medium` o `low`, con el mismo significado que en un
       requisito: cuánto te fías de que esto sea verdad, no de saber implementarlo.
     · `why` — por qué es una apuesta y no un hecho. Sin el porqué, quien la revise no
       sabrá qué tiene que mirar para resolverla.
     · `revisit` — **el hecho que resuelve la apuesta**, no una fecha. Lo que cierra
       una suposición no es que pase el tiempo, es que llegue un dato: «cuando hayamos
       servido las cincuenta primeras reservas», «cuando el primer cliente reserve por
       el enlace». El hecho dice qué habrá que mirar y se reconoce cuando ocurre; una
       fecha llega esté la respuesta disponible o no, y entonces sólo se puede
       posponer. `C12` rechaza las fechas por eso, y también los «ya veremos».
     · `fatal` — `yes` o `no`. Si esta apuesta sale mal, ¿el proyecto sigue teniendo
       sentido? Un `fatal: yes` con `confidence: low` es la línea más importante del
       documento y lo que habría que ir a comprobar esta semana, antes de escribir
       ninguna spec.

     **Nombra el slug de la capability en la prosa de la apuesta.** El acta no tiene un
     campo que las enlace, así que el nombre es lo único que dice de qué fila hablaba
     ésta el día que alguien llegue a su `revisit:`. También es lo que miran `C18` y
     `C19` para saber si el riesgo de una fila ya está declarado.

     Dos apuestas que casi nunca se escriben solas y que el linter va a ir a buscar:

     · **El «Done when» absoluto** (`C18`). «Sin corregir ninguno», «nunca falla», «el
       100 %»: un criterio que no admite un fallo es una suposición sobre lo bien que va
       a salir algo que todavía no existe. O se baja el listón a algo alcanzable, o se
       escribe aquí abajo como lo que es.
     · **El paso que espera a alguien** (`C19`). «Pasada la entrega, marca si cumplió el
       plazo.» Manual, semanas después, y quien lo hace no cobra el beneficio: se lo
       lleva quien use el dato el mes que viene. Es la dependencia que más veces se
       incumple y la que menos veces está escrita. Mira bien el `fatal:` de ésta: si otra
       fila ordena o resume a partir de ese dato, cuando nadie lo rellene no fallará la
       fila que lo pide, saldrá en blanco la otra.

     El encabezado se queda aunque no tengas ninguna apuesta: las cinco secciones son
     obligatorias. Ahora bien, un acta con un `high` en la tabla y esta sección vacía es
     un acta que no ha mirado, y el linter lo dice. -->

### B-001 · Nadie anula por WhatsApp

Damos por hecho que un cliente que quiere anular usará el enlace y no el
teléfono del restaurante.

confidence: low
  why:      no lo hemos comprobado con ningún restaurante real
  revisit:  cuando hayamos hablado con tres restaurantes que ya reserven por enlace
  fatal:    no

### B-002 · El cliente se fía de una confirmación automática

Suponemos que ver la hora confirmada en pantalla basta, y que el dueño no va a
tener que llamar igualmente para confirmar cada reserva. Si tiene que llamar, el
propósito no se cumple: el cuaderno desaparece y el teléfono se queda.

confidence: low
  why:      corazonada; ningún cliente ha reservado todavía por el enlace
  revisit:  cuando las cincuenta primeras reservas hayan pasado por el enlace
  fatal:    yes
