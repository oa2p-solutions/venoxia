# Venoxia

> Plugin de Claude Code que convierte la especificación en un contrato ejecutable.

## Qué es

Venoxia es un plugin para Claude Code que impone un formato de requisito verificable, lo valida con un script determinista y usa un hook `PreToolUse` para que ese contrato no se pueda ignorar por descuido.

La tesis es corta y cabe en tres frases. **Una especificación es una apuesta sobre el comportamiento futuro de un sistema.** **Toda apuesta debe declarar cómo se resuelve y cuánto se confía en ella.** **Lo que distingue a Venoxia: la spec deja de ser prosa y pasa a ser un contrato que falla en CI cuando miente.**

En la práctica eso significa que cada requisito nace con dos campos que ninguna otra herramienta exige: `verifies:`, la ruta del test que resuelve la apuesta, y `confidence:`, el nivel de confianza declarado. Sin oráculo, no compila. Y como el validador es un script de Python sin modelo detrás, el veredicto es el mismo en tu portátil, en el CI y dentro de la conversación.

Esta entrega cubre el **núcleo verificable**: el acta del proyecto y su linter, el formato del requisito, el validador de 16 reglas, el guardián y el motor de divergencia.

## Instalación

```bash
claude plugin marketplace add oa2p-solutions/venoxia
claude plugin install venoxia@venoxia
```

Requiere Python 3 en el `PATH` (probado con 3.14). Los scripts usan **sólo la biblioteca estándar**: no hay `pip install`, ni entorno virtual, ni dependencias que mantener. La suite de tests del propio plugin tampoco pide nada: es `unittest`, de la biblioteca estándar.

## Empezar un proyecto desde cero

Venoxia empieza donde ya sabes qué comportamiento quieres, y durante la primera versión eso dejó fuera el caso más común de todos: el proyecto que todavía no existe. `/venoxia:specify` pide «el cambio, en una frase», y esa pregunta da por supuesto un sistema anterior del que esto es el delta. Sin producto no hay delta, y la primera media hora del plugin era un callejón sin salida.

`/venoxia:charter` es el paso que faltaba. Éste es el recorrido completo, en el orden real en que ocurre.

**1 · Monta el esqueleto del proyecto antes de adoptar Venoxia.** El `package.json`, el `tsconfig.json`, el `Cargo.toml`, la carpeta de tests, el linter, el primer commit: todo eso primero, y por dos razones distintas que apuntan al mismo sitio. La operativa es que **el guardián se activa en cuanto existe `.venoxia/`**, así que crear el acta antes que el andamiaje convierte cada escritura de configuración en una pelea con el hook. La de fondo es que **el andamiaje no es comportamiento**: nadie lo observa desde fuera, ningún test de aceptación lo comprueba y mañana se puede cambiar entero sin que ningún usuario note nada, que es exactamente la prueba que decide si algo pertenece a la spec. Especificar el `tsconfig.json` produce requisitos que se vuelven mentira en el primer refactor.

**2 · `/venoxia:charter` — la entrevista.** Pregunta y no rellena: a qué problema se dedica el proyecto, quién lo va a usar y qué hace hoy esa gente sin él, qué queda fuera y por qué, y qué se está dando por supuesto sin haberlo comprobado. De ahí salen dos ficheros: `.venoxia/charter.md`, el acta, con el propósito, los usuarios, la lista **priorizada** de capabilities y las apuestas; y `.venoxia/principles.md`, las restricciones que toda spec de este proyecto respetará. El acta pasa por `charter_lint.py` antes de que la skill devuelva el control, igual que un delta pasa por `validate.py`: no es un documento de intenciones, es un documento que puede estar mal. Y termina dándote escrito el comando exacto del paso siguiente.

**3 · `/venoxia:specify "<la capability de prioridad 1>"`.** Una sola, la primera de la tabla, con el texto de su columna «Qué podrá hacer». Escribe el `change.json`, la propuesta y el delta en EARS, cada requisito con su `verifies:` y su `confidence:` desde el primer borrador. Las capabilities 2 y 3 esperan: especificarlas ahora es escribir contra un sistema que todavía no ha contestado nada.

**4 · `/venoxia:validate` — y falla en `V07`. Eso es lo correcto.** El fichero de test que la spec nombra en `verifies:` todavía no existe, el disco contradice a la spec y el validador lo dice. **Ese rojo no es un problema de configuración: es la tesis del plugin funcionando en tu proyecto el primer día.** Si aquí saliera verde, `verifies:` sería un campo decorativo y la spec podría prometer un oráculo inexistente sin coste. No crees un fichero de test vacío para apagarlo: eso es escribir el oráculo para que el validador calle, que es precisamente lo que el campo existe para impedir.

**5 · Escribes el test, con su `@covers`.** En la ruta exacta que dice `verifies:`, con el comentario `@covers R-XXX-000` dentro. El test falla, claro que falla: todavía no hay implementación. Lo que tiene que estar verde en este punto es el validador, no la suite. Vuelve a pasar `/venoxia:validate` hasta que salga `0`.

**6 · `/venoxia:diverge`.** Dos lectores aislados con consignas distintas y el abogado del diablo leen el delta sin haber estado en la conversación donde nació, y el script calcula la divergencia y formula las preguntas cerradas. Con el validador y la divergencia los dos en `0`, y sólo entonces, el `change.json` pasa a `"state": "validated"`.

**7 · El guardián te deja escribir código.** La misma escritura bajo `src/` que en el paso 1 habría sido una pelea, y que sin change validado se habría denegado con un mensaje diciendo qué falta, ahora entra por el tercer camino del guardián: hay contrato firmado y hay delta al lado que lo acredita. A partir de aquí el bucle es el corto —`/venoxia:specify` de la capability 2, y otra vez—, y el acta sólo se vuelve a abrir para añadir una fila o resolver una apuesta.

En comandos, la primera media hora entera:

```text
# 1 · el esqueleto primero: sin .venoxia/, el guardián no estorba
npm create vite@latest . && git init && git add -A && git commit -m "esqueleto"

# 2 · la entrevista: escribe .venoxia/charter.md y .venoxia/principles.md
/venoxia:charter

# 3-7 · una vuelta por capability, empezando por la de prioridad 1
/venoxia:specify "reservar una mesa para una fecha y hora"
/venoxia:validate     # falla en V07: el test no existe todavía. Correcto.
#   … escribes test/booking/reserve.spec.ts con «@covers R-BOO-001» dentro
/venoxia:validate     # verde
/venoxia:diverge      # si converge, change.json → "state": "validated"
#   … y ahora sí, el guardián deja escribir src/
```

## El acta del proyecto

`.venoxia/charter.md` es al proyecto lo que la capability es a un trozo de comportamiento: el documento que vive para siempre y contra el que se contrasta todo lo que venga después. Encabezados y claves en inglés, prosa en español, igual que el resto del plugin. Parseable con expresiones regulares, legible sin herramientas.

```markdown
# Reservas Bistró · Acta del proyecto

## Purpose

Que un restaurante pequeño deje de perder mesas por reservas apuntadas en un
cuaderno que sólo entiende quien lo escribió.

## Users

### owner · Dueño del restaurante
- **hoy:** apunta las reservas en un cuaderno y las repasa cada mañana.
- **con esto:** ve la ocupación de la noche desde el móvil sin llamar a nadie.

### diner · Cliente que reserva
- **hoy:** llama por teléfono y espera a que alguien coja.
- **con esto:** reserva desde el enlace del perfil, a cualquier hora.

## Capabilities

| # | Capability | Qué podrá hacer | Done when | Risk |
|---|---|---|---|---|
| 1 | `booking` | reservar una mesa para una fecha y hora | un cliente reserva y recibe la confirmación con su hora | high |
| 2 | `availability` | ver qué queda libre esta noche | el dueño abre el móvil y ve las mesas libres de hoy | medium |

## Out of scope

- **Pagos y señales.** No se cobra nada en la v1; el riesgo regulatorio no compensa
  hasta que haya reservas de verdad.
- **App nativa.** La web basta para lo que promete el propósito.

## Bets

### B-001 · Nadie anula por WhatsApp

Damos por hecho que un cliente que quiere anular usará el enlace y no el
teléfono del restaurante.

confidence: low
  why:      no lo hemos comprobado con ningún restaurante real
  revisit:  2026-12-15
  fatal:    no
```

### Qué dice cada sección

| Sección | Qué contiene | Por qué existe |
|---|---|---|
| `## Purpose` | De una a tres frases en prosa: qué cambia en el mundo cuando esto exista. | Un propósito escrito en términos de lo que se programa —«una API REST con autenticación»— no permite decidir nada; uno escrito en términos de lo que cambia sí, y es lo que zanja las discusiones de alcance seis semanas después. |
| `## Users` | Uno o más `### <slug> · <Nombre del rol>`, cada uno con las viñetas `**hoy:**` y `**con esto:**`. El slug va en kebab-case. | El «hoy» es la parte que nadie escribe y la que más decide: si no sabes decir qué hace esa persona ahora mismo sin tu producto, no sabes qué le vas a quitar de encima, y probablemente estés construyendo para nadie. |
| `## Capabilities` | La tabla priorizada, con las cinco columnas exactas `#`, `Capability`, `Qué podrá hacer`, `Done when` y `Risk`. La prioridad es un entero que empieza en 1 y no se repite; `Risk` es `high`, `medium` o `low`. | Es el plan de trabajo y a la vez el índice de `.venoxia/capabilities/`: el slug de cada fila, en kebab-case y entre acentos graves, es el mismo nombre del directorio que creará `/venoxia:specify`. |
| `## Out of scope` | Una o más viñetas `- **<Qué>.** <por qué no>`. | Un proyecto se define tanto por lo que no hace como por lo que hace. Sin esta lista escrita, todo está dentro. |
| `## Bets` | Cero o más `### B-NNN · <título>`, cada una con su prosa y un bloque de metadatos con `confidence`, `why`, `revisit` y `fatal`. Misma forma que el bloque de metadatos de un requisito. | Es lo que `confidence:` hace por un requisito, un escalón más arriba: qué se está suponiendo, cuánto se confía, cuándo se vuelve a mirar y si equivocarse mata el proyecto o sólo cuesta una semana. |

### Por qué `Done when` y `Out of scope` son obligatorios

Son las dos casillas que la entrevista no deja en blanco, y las dos por el mismo motivo por el que un requisito no puede quedarse sin `verifies:`.

**`Done when` es el oráculo de la capability.** Una capability sin criterio de terminación se termina cuando alguien se cansa, y eso convierte la tabla de prioridades en una lista de temas. Lo que se pide no es «la funcionalidad está completa», que no se puede comprobar, sino una escena observable: *un cliente reserva y recibe la confirmación con su hora*. Escrito así, a la pregunta «¿ya está?» contesta cualquiera mirando la pantalla, y no hace falta que la conteste quien la implementó, que es justo la persona con menos criterio para hacerlo.

**`Out of scope` es la frontera.** Un proyecto sin fronteras escritas las tiene igualmente: las descubre tarde, de una en una y en mitad de una entrega. Y cada viñeta lleva el porqué, no sólo el qué, porque un «pagos, no» a secas se vuelve a discutir la semana que viene, mientras que un «pagos no, porque el riesgo regulatorio no compensa hasta que haya reservas de verdad» se puede revisar el día en que esa condición cambie. Una frontera sin razón no es una decisión, es un capricho, y los caprichos no sobreviven a la primera reunión.

### Las 16 reglas del linter del acta

Todas deterministas, igual que las del validador: ninguna consulta a un modelo. `scripts/charter_lint.py` sale con `0` si el acta cumple, `1` si no y `2` ante un error de uso. Con `--strict`, los avisos también hacen fallar.

| Regla | Qué comprueba | Severidad |
|---|---|---|
| `C01` | Están las cinco secciones: `## Purpose`, `## Users`, `## Capabilities`, `## Out of scope` y `## Bets`. Un encabezado escrito en español (`## Propósito`) se reconoce para poder decírtelo en la pista, pero no cuenta como sección: los estructurales van en inglés porque los lee el linter. | error |
| `C02` | El propósito no está vacío y no pasa de tres frases. | error |
| `C03` | Hay al menos un usuario, y cada uno declara sus dos viñetas —`**hoy:**` y `**con esto:**`— sin dejar ninguna vacía. | error |
| `C04` | La tabla de capabilities trae al menos una fila, bajo las cinco columnas exactas `# \| Capability \| Qué podrá hacer \| Done when \| Risk`. | error |
| `C05` | El slug de cada capability es kebab-case en minúsculas y no se repite. Es el nombre del directorio bajo `.venoxia/capabilities/`. | error |
| `C06` | Las prioridades son enteros que cubren de 1 a N: sin huecos y sin repetidos. | error |
| `C07` | Cada capability declara su `Done when`. **Es lo que `verifies:` es a un requisito, una fase antes.** | error |
| `C08` | Ese `Done when` no **empieza** por un verbo de implementación (`implementar`, `crear la tabla`, `usar`, `refactorizar`, `montar`, `configurar`, `integrar`, `desplegar`). Mencionar uno de pasada no cuenta: la regla mira sólo el arranque de la frase, para no convertirse en el falso positivo que haría que alguien la apagara entera. | error |
| `C09` | `Risk` vale exactamente `high`, `medium` o `low`. | error |
| `C10` | `## Out of scope` trae al menos una entrada. Un proyecto que todavía no le ha dicho que no a nada no ha decidido nada. | error |
| `C11` | Cada apuesta declara `confidence:` con uno de los tres niveles. | error |
| `C12` | Una apuesta en `low` obliga a `revisit:` con **el hecho que la resuelve**: «cuando hayamos cerrado las diez primeras compras». Ni una fecha ni un «ya veremos»: las dos se rechazan. Misma exigencia que `V10` le hace a un requisito. | error |
| `C13` | El identificador de la apuesta casa `B-NNN` y es único en el acta. | error |
| `C14` | `fatal:`, cuando está, vale `yes` o `no`. | warning |
| `C15` | El acta declara alguna capability de riesgo `high` y no declara ninguna apuesta: una suposición que nadie ha escrito es una suposición que nadie va a revisar. | warning |
| `C16` | El orden en que se está construyendo no es el que el acta declara: alguna capability con `spec.md` vivo va detrás de otra que todavía no tiene ninguno. Aviso y no error, porque adelantarse puede estar justificado; lo que no puede es quedarse sin decir. | warning |
| `C17` | Alguna capability promete un **juicio** —comparar, puntuar, recomendar, ordenar por varios criterios— y `.venoxia/principles.md` no declara ningún principio de dominio que diga cómo se desempata. El criterio existe igual: si no está escrito, lo toma quien implemente. Un aviso por acta, no uno por fila. | warning |
| `C18` | Un `Done when` **absoluto** —«sin corregir ninguno», «nunca falla», «el 100 %»— que ninguna apuesta respalda. O se baja el listón a algo alcanzable, o se declara la apuesta. | warning |
| `C19` | Un `Done when` que sólo se cumple si **alguien vuelve más tarde** —«pasada la entrega, marca si cumplió»— y ninguna apuesta lo reconoce. Es la dependencia que más veces se incumple y la que menos veces está escrita. | warning |

Y como en el validador, el parseo tiene su propio código: `P01` (error) es un acta que no se ha podido leer, y es un fallo de Venoxia, no del acta.

```bash
python3 scripts/charter_lint.py                       # .venoxia/charter.md bajo el directorio actual
python3 scripts/charter_lint.py --root /ruta/proyecto --strict
python3 scripts/charter_lint.py --json --no-color
```

Ni un proyecto sin `.venoxia/` ni un `.venoxia/` sin acta son un error: el linter lo dice y sale con `0`. Un proyecto que no ha adoptado Venoxia no falla por no haberlo adoptado, y uno que la adoptó antes de que existiera el acta tampoco.

## El formato del requisito

Etiquetas y claves en inglés, prosa en español. Parseable con expresiones regulares, legible sin herramientas.

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

El ID vive en el encabezado (`### R-CHK-014 · Título`): estable, linkable y parseable. El separador canónico es `·`, y también se aceptan la raya `—`, el semicuadratín `–` y el guion `-`, éste con espacio a los dos lados para no partir un título que ya lo lleva. La narrativa que sigue al encabezado es la cláusula EARS; los escenarios son la tabla de decisión. El bloque de metadatos usa claves fijas al final del requisito, y su indentación es puramente cosmética.

### Las claves del bloque de metadatos

| Clave | ¿Obligatoria? | Qué contiene | Por qué existe |
|---|---|---|---|
| `verifies` | Sí | Ruta (o rutas separadas por coma o espacio) del fichero de test que decide si el requisito se cumple. | Es el corazón del sistema: la apuesta declara cómo se resuelve. Un requisito sin oráculo es una opinión, y el validador lo rechaza (`V06`, `V07`). |
| `confidence` | Sí | `high`, `medium` o `low`. | Obliga a separar lo que se sabe de lo que se supone, en el momento de escribirlo y no después del incidente (`V09`). |
| `why` | Recomendada | Una frase en español que explica por qué la confianza es esa y no otra. | Convierte «medium» en información accionable: dice **qué** parte concreta es la apuesta. |
| `revisit` | Sí cuando `confidence: low` | El hecho que resuelve la apuesta. No una fecha: `V10` las rechaza. | Lo que cierra una suposición no es que pase el tiempo, es que llegue un dato. El hecho dice qué habrá que mirar y se reconoce cuando ocurre; una fecha llega esté la respuesta o no, y entonces sólo se puede posponer. |
| `from` | Recomendada | Referencia al documento de origen (PR/FAQ, ticket, decisión), con ancla si aplica. | Preserva la trazabilidad hacia la intención de negocio. Su ausencia en un requisito nuevo es un aviso (`V15`). |

El vínculo con el test es **doble**: la spec apunta al fichero con `verifies:`, y el fichero apunta de vuelta al requisito con un comentario `@covers R-CHK-014`. El validador comprueba las dos direcciones (`V07`, `V08`, `V16`), de modo que borrar el test rompe la spec y renombrar el requisito rompe el test.

## Las cuatro skills

Se usan en este orden:

1. **`/venoxia:charter`** — la entrevista que define el proyecto antes de que exista código: propósito, usuarios, capabilities priorizadas, fuera de alcance y apuestas. Escribe `.venoxia/charter.md` y `.venoxia/principles.md`, y entrega el `/venoxia:specify` exacto de la capability de prioridad 1. Se usa una vez por proyecto; después sólo se vuelve al acta para añadir una fila o resolver una apuesta.
2. **`/venoxia:specify "…"`** — lee el acta, los principios y las capabilities existentes, escribe la `proposal.md` y el delta en EARS, con `verifies:` y `confidence:` en cada requisito desde el primer borrador.
3. **`/venoxia:validate`** — ejecuta el validador determinista sobre `.venoxia/` y presenta los findings agrupados por severidad, con la corrección concreta de cada uno.
4. **`/venoxia:diverge`** — despacha dos lectores aislados y un abogado del diablo sobre el delta, y enfrenta sus lecturas para convertir cada desacuerdo en una pregunta cerrada.

   Cómo se comparan las lecturas, que es de donde sale la utilidad del informe:

   | Campo | Cómo se compara | Qué produce |
   |---|---|---|
   | `scenario` | presencia | Un escenario que sólo ve un lector es divergencia **dura** |
   | `status_code` | igualdad | Dos códigos distintos son divergencia **dura** |
   | `side_effects` | cobertura contra el repertorio entero del otro lector —`effect` incluido— | Un efecto que nadie más recoge **en ningún campo** es divergencia **dura** |
   | `effect` | Jaccard de tokens de contenido, umbral `0.6` | Por debajo, divergencia **blanda** |

   La prosa se compara **sin palabras vacías y sin conjugación**: «registra el plazo como 21 días» y «el plazo queda registrado como 21 días» son la misma lectura, y contar los artículos convertía cada diferencia de estilo en una pregunta. Las cifras, en cambio, no se diluyen nunca: si las dos lecturas no nombran los mismos números, la similitud es cero por mucho que compartan el resto —«21 días» contra «14 días» comparten cinco palabras de seis y describen escenarios distintos—.

   Y `side_effects` se mide contra los dos campos a la vez porque el reparto entre `effect` y `side_effects` varía de un lector a otro con igual derecho: ante «rechaza el fichero, indica los formatos y no crea presupuesto», uno lo escribe entero en `effect` y el otro deja el tercero aparte. Eso no es un desacuerdo sobre el comportamiento.

El `change.json` pasa a `"state": "validated"` sólo cuando validador **y** divergencia pasan.

## Las 16 reglas del validador

Todas deterministas: ninguna consulta a un modelo. `scripts/validate.py` sale con `0` si el ámbito es conforme, `1` si no lo es y `2` ante un error de uso. Con `--strict`, los avisos también hacen fallar.

| Regla | Qué comprueba | Severidad |
|---|---|---|
| `V01` | El ID está presente, casa con `^R-[A-Z]{2,4}-\d{3}$` y es único en el ámbito validado. | error |
| `V02` | La narrativa encaja en exactamente un patrón EARS: `WHEN` (event-driven), `WHILE` (state-driven), `WHERE` (optional-feature), `IF … THEN` (unwanted-behaviour), `WHILE … WHEN` (complejo) o ubicuo. | error |
| `V03` | Hay narrativa no vacía antes del primer `#### Scenario:`. | error |
| `V04` | El requisito tiene al menos un escenario. | error |
| `V05` | Cada escenario tiene `**WHEN**` y `**THEN**`. | error |
| `V06` | `verifies:` está presente y con valor no vacío. **El corazón del sistema.** | error |
| `V07` | El fichero de `verifies:` existe en disco, resuelto desde `--root`. | error |
| `V08` | Ese fichero contiene `@covers <ID>`. Con varias rutas, basta que una lo contenga. | error |
| `V09` | `confidence:` está presente y vale `high`, `medium` o `low`. | error |
| `V10` | `confidence: low` obliga a `revisit:` con el hecho que resuelve la apuesta. Una fecha se rechaza —no dice qué mirar cuando llegue— y un «ya veremos» también. | error |
| `V11` | Presupuesto de incertidumbre: como mucho el 30 % de los requisitos del ámbito en `low`. Exactamente 0,30 pasa. | error |
| `V12` | Cada delta declara al menos un bloque `## ADDED\|MODIFIED\|REMOVED\|RENAMED Requirements`. | error |
| `V13` | Los IDs de `MODIFIED`/`REMOVED`/`RENAMED` existen en alguna capability viva. Sin capabilities en disco, la regla no se evalúa. | error |
| `V14` | La narrativa no usa `SHALL` ni `MUST`. | warning |
| `V15` | `from:` ausente en un requisito de una capability nueva. | warning |
| `V16` | Un test declara `@covers <ID>` de un ID que no existe en ninguna spec: comportamiento no especificado. | warning |

Además de las reglas, el parser emite sus propios findings de forma: `P01` (error, fichero ilegible o inexistente), `P02` (aviso, clave de metadatos desconocida), `P03` (aviso, clave repetida; gana la última), `P04` (aviso, bullet de escenario que no encaja en `- **KW** texto`) y `P05` (aviso, un `### ` con forma de requisito que cae dentro de un bloque de código y por tanto no se ha leído como requisito). El parser nunca lanza una excepción: todo problema sale como finding.

Dos límites que conviene conocer antes de confiar en el verde: `V16` escanea sólo los ficheros que algún `verifies:` nombra, no el repositorio entero, así que un test huérfano en una carpeta que nadie referencia no se detecta; y `V01` compara duplicados dentro del ámbito validado, con una excepción a cada lado: un requisito del bloque `ADDED` se compara **además** contra los IDs de las capabilities vivas —declarar como nuevo un ID que ya vive es un duplicado aunque esa capability no entre en el ámbito—, mientras que un `MODIFIED`, `REMOVED` o `RENAMED` que repite el ID de la capability viva es lo esperado y no se denuncia.

Uso directo del script, sin pasar por la skill:

```bash
python3 scripts/validate.py                  # todo lo que haya bajo .venoxia/
python3 scripts/validate.py --change 2026-08-31-checkout --strict
python3 scripts/validate.py --json --no-color
```

Si el proyecto no tiene `.venoxia/`, el validador lo dice y sale con `0`: un proyecto que no ha adoptado Venoxia no falla por no haberlo adoptado.

## El modelo de confianza del guardián

El guardián es la pieza que convierte el hábito en infraestructura, y por eso es la que más honestidad merece: si no sabes exactamente qué bloquea y cómo apagarlo, lo desinstalarás el primer viernes con prisa.

**Qué intercepta.** Un hook `PreToolUse` con el matcher `Edit|Write|NotebookEdit`, y nada más. No intercepta `Bash`: un `sed -i`, un `> fichero` o un `git apply` pasan sin verse. El guardián existe para que escribir código sin spec sea un acto deliberado, no para hacerlo imposible.

**Los cinco caminos de decisión, en orden.** El primero que casa decide:

1. No existe `<raíz>/.venoxia/` → **allow**. El proyecto no ha adoptado Venoxia y el plugin no estorba.
2. La ruta editada cae bajo `.venoxia/` o `prfaq/`, o es markdown de spec (`*.md` bajo `docs/spec*` o `specs/`, o llamado `spec.md`, `proposal.md`, `delta*.md`) → **allow**. Estás escribiendo la especificación. Esos directorios se reconocen **anclados a la raíz**: un `src/prfaq/` no exime de nada.
3. El change activo tiene `"state": "validated"` en su `change.json` **y** un `delta/` con al menos un `.md` no vacío → **allow**. El contrato está firmado, y hay especificación al lado que lo acredita: un `change.json` fabricado a mano, solo, ya no basta.
4. El change activo declara `"via": "direct"` → **allow**, y se anota una línea JSONL en `.venoxia/drift/direct.log` con marca de tiempo, change, herramienta y ruta. Es la vía de escape registrada, no vigilada.
5. Cualquier otro caso → **deny**, con una razón en español que dice qué falta (no hay change validado), el comando exacto que lo arregla (`/venoxia:specify "…"` y luego `/venoxia:validate`) y cómo saltárselo.

El change activo es el `.venoxia/changes/<id>/change.json` cuyo `state` no es `"archived"` y cuyo `mtime` es el más reciente **de los que se pueden leer**. Con `NotebookEdit` la ruta juzgada es `notebook_path`; con las demás herramientas, `file_path`. La ruta se compara con la raíz del proyecto dos veces, por cadena y con las dos rutas resueltas (`realpath`): en macOS `/tmp/p/src/x.ts` y `/private/tmp/p/src/x.ts` son el mismo fichero, y basta con que **una** de las dos medidas lo sitúe dentro del proyecto para juzgarlo.

Hay tres casos más que también permiten, los tres por prudencia: que la herramienta no declare ninguna ruta, que la ruta resuelta caiga fuera de la raíz del proyecto, y que el `change.json` —o el propio `changes/`— no se deje **leer** por un fallo de entrada/salida (permisos denegados, un montaje caído, un `change.json` que resulta ser un directorio). Ese último es un fallo nuestro, no del proyecto: se permite, se deja la traza en `stderr` y se anota en el diario de deriva con `"note": "change-no-legible"`, porque un `allow` concedido sin haber comprobado el respaldo es exactamente lo que ese diario existe para recordar.

Y uno que **ya no** permite: un `change.json` que existe y cuyo **contenido** está mal —JSON corrupto, un array donde iba un objeto, un megabyte de relleno—. Un fichero del usuario que está mal escrito no es un fallo del guardián, y no acredita ninguna especificación validada: se salta, la búsqueda sigue con el siguiente change y, si no queda ninguno bueno, se deniega. Confundir eso con el fail-open era una puerta trasera: bastaba estropear el `change.json` a propósito. La frontera, que es fina, la marca quién tiene la culpa: contenido mal escrito, del usuario, no acredita nada; fallo de E/S al preguntarlo, nuestro, permite.

**Una decisión, siempre, pase lo que pase.** Un hook `PreToolUse` que no escribe nada en `stdout` no ha decidido nada, así que la edición sigue adelante: un `deny` que no se imprime es una escritura consentida. Por eso la decisión se serializa con `ensure_ascii=True` —los acentos y las comillas viajan escapados y el cliente los recompone— y se vuelca ya codificada a `sys.stdout.buffer`, sin depender de la codificación del envoltorio de texto. Con `PYTHONIOENCODING=ascii` o `LC_ALL=C`, o con un `file_path` que ni siquiera es Unicode legal, el guardián seguía denegando en su lógica y no imprimía nada. El payload de entrada corre la misma suerte: se lee en bytes y se decodifica como UTF-8, porque leerlo por el envoltorio de texto hacía que un acento en la ruta —`src/año/checkout.ts`— tumbara la lectura y convirtiese el `deny` en `allow` sin decir nada. Ahora sale ASCII puro, y el testigo de «ya he decidido» sólo se marca después de que el `write` y el `flush` hayan ido bien. La traza de `stderr` está sometida a lo mismo: si su extremo está cerrado, se cambia por un sumidero en vez de tumbar el hook o hacerlo salir con código 120 —que para el cliente es un «error del hook» aunque la decisión esté escrita—.

**Fail-open, por diseño.** `main()` está envuelto entero en un `try/except`: cualquier excepción del propio guardián o un JSON malformado producen **allow** y una traza a `stderr`. Un `change.json` corrupto no entra aquí: eso es un fichero del usuario, y va por el camino de arriba. Un `stdin` vacío también permite, aunque por otro camino y sin traza: un payload vacío no declara ninguna ruta, y sin ruta no hay nada que juzgar. El guardián nunca es la razón por la que no puedes trabajar. El coste de esa decisión es explícito: un guardián roto no protege nada y no lo grita, sólo deja pasar. Presupuesto de latencia por debajo de 100 ms, sin red y sin recorrer el repositorio: un `scandir` de `.venoxia/changes/`, la lectura del `change.json` y, sólo cuando se declara validado, un `scandir` de su `delta/` (medidos: 0,01 ms el delta y 0,02 ms las dos resoluciones de ruta).

**Lo que el guardián no puede impedir.** Con la misma honestidad con la que arriba dice que `Bash` no se intercepta: **quien pueda escribir bajo `.venoxia/` puede fabricarse un change**. El paso 2 permite escribir la especificación —tiene que permitirlo— y el paso 3 sólo comprueba que el `change.json` diga `validated` y que exista un `delta/*.md` con algo dentro; no ejecuta el validador, porque eso rompería el presupuesto de 100 ms y el fail-open. Un `delta/x.md` con una línea cualquiera y un `change.json` a juego bastan para desarmarlo. Exigir el delta sube el precio: de un fichero trivial a fabricar también una especificación falsa, y deja rastro en el diario cuando algo pasa sin respaldo firme (`"note": "validated-sin-delta"` si un `validated` sin delta se cuela por la vía `direct`, `"note": "delta-no-comprobable"` si ni siquiera se pudo mirar el directorio). Pero la frase que importa es ésta: **el guardián es una barrera contra el descuido, no contra la determinación**. Protege del viernes con prisa, no de quien ha decidido saltárselo.

**Cómo desactivarlo.** Tres interruptores, del más local al más definitivo:

- **Por cambio:** poner `"via": "direct"` en el `change.json` activo. Sigue permitiendo todo y deja constancia en `.venoxia/drift/direct.log`.
- **Por proyecto:** borrar (o renombrar) el directorio `.venoxia/`. Sin él, el guardián permite siempre por el camino 1.
- **Del todo:** `claude plugin uninstall venoxia@venoxia`. Se va el hook, se van las skills y las specs que ya tengas escritas siguen siendo markdown legible.

## Verificar regresiones

```bash
python3 -m unittest discover -s tests -q
claude plugin validate . --strict
claude plugin eval venoxia --ablation with-without --allow-tools 'Bash(python3 *)' Write
```

- La suite cubre el núcleo determinista: un caso en positivo y otro en negativo por cada regla `V01`–`V16` del validador y por cada regla `C01`–`C19` del linter del acta, más la gramática del parser, el esquema JSON del informe, los cinco caminos del guardián y la aritmética de divergencia. Es la parte con cobertura obligatoria: de ella depende la credibilidad del resto. Y es `unittest` de la biblioteca estándar a propósito: si para ejecutarla hiciera falta instalar algo, habría un día en que nadie la ejecutaría.
- `claude plugin validate . --strict` comprueba la estructura del plugin: manifiesto, frontmatter de skills y agentes, y el hook declarado.
- `claude plugin eval venoxia --ablation with-without …` mide lo único que no se puede probar con asserts: que el plugin cambia el resultado. El `--allow-tools` no es decorativo: `Bash` y `Write` están con verja, y sin ese permiso de operador los cinco casos fallan por falta de permisos en vez de por regresión (el detalle, en [`evals/README.md`](evals/README.md)). Compara la ejecución con y sin él sobre casos que deben detectarse (código de estado ambiguo, efecto parcial ambiguo, oráculo ausente, presupuesto de incertidumbre excedido) y uno que no debe dar falso positivo (spec limpia).

Y los ejemplos de este README no son decorado: el acta y el requisito que enseña se extraen a ficheros reales y se pasan por `charter_lint.py` y `validate.py` antes de publicarlos. Un README que muestra un ejemplo que su propio linter rechazaría es exactamente el fallo que este plugin existe para impedir, y ya pasó una vez, con un `SHALL` que la regla `V14` marcaba.

## Qué queda fuera de esta entrega

Diseñado, documentado y pospuesto hasta que el núcleo se use en una feature real:

- Triaje por riesgo de tres vías (DIRECTA / NORMAL / CRÍTICA).
- PR/FAQ como documento de origen enlazable desde `from:`. El bucle de promesas con fecha de revisión ya no está aquí: lo cubre el bloque `## Bets` del acta, con su `revisit:` y su `fatal:`.
- `trocear` / `construir` / `revisar` con git worktrees.
- Diario de deriva con estadística acumulada que reescribe las plantillas.
- Panel de salud de capabilities.
- Consolidación automática del delta sobre la capability viva.

De todos, el **panel de salud** es el siguiente con más valor: se deriva del JSON que `validate.py` ya produce, así que es barato en cuanto haya specs reales que mostrar.

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
