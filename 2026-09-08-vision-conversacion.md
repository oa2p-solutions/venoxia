# Venoxia · conversación de visión

**Fecha:** 2026-09-08 · **Sesión:** `87e61b69`

> Transcripción literal, extraída del registro de la sesión. Se han omitido
> el razonamiento interno, las llamadas a herramientas y sus resultados: queda
> lo que se dijo. La conversación arranca explicando el plugin y termina
> corrigiendo la visión de producto para incluir el eje técnico.

---

## Óscar

explicame el funcionamiento del plugin

## Claude

Venoxia es un plugin de Claude Code que convierte la especificación en un contrato ejecutable. Aquí está el funcionamiento completo, de la tesis a las piezas.

### La tesis

Tres frases:

1. Una especificación es **una apuesta** sobre el comportamiento futuro del sistema.
2. Toda apuesta debe declarar **cómo se resuelve** (`verifies:`) y **cuánto se confía en ella** (`confidence:`).
3. Por eso la spec deja de ser prosa y pasa a ser algo que **falla cuando miente**.

La consecuencia de diseño que lo sostiene todo: **ningún script consulta a un modelo**. Toda la aritmética de los veredictos está en Python de la stdlib, así que el resultado es idéntico en tu portátil, en la puerta local y dentro de la conversación. Las skills sólo envuelven y presentan.

### Las cuatro piezas del plugin

| Pieza | Qué es |
|---|---|
| **Skills** (`skills/*/SKILL.md`) | Los cinco comandos `/venoxia:*`. Conducen entrevistas, escriben markdown, llaman a los scripts. Nunca tocan código de producción. |
| **Agentes** (`agents/*.md`) | `reader` y `devils-advocate`. Los despacha `/venoxia:diverge`; reciben **sólo la ruta del delta**, deliberadamente sin el contexto de la conversación. |
| **Hook** (`hooks/hooks.json` → `guardian.py`) | Un `PreToolUse` con matcher `Edit|Write|NotebookEdit`. Decide allow/deny sobre cada edición. |
| **Scripts** (`scripts/*.py`) | La única lógica ejecutable. Seis deciden algo; `scripts/venoxia/` es el paquete compartido. |

### El formato del requisito

Todo gira alrededor de esto (`README.md:177`):

```markdown
### R-CHK-014 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock…

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas
- **THEN** se crea la reserva con TTL de 15 minutos

verifies:   test/checkout/reservation.spec.ts
confidence: medium
  why:      los 15 minutos son una apuesta, no un dato
  revisit:  cuando hayamos medido un mes de reservas caducadas
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
```

Dos detalles no obvios:

- **El vínculo con el test es doble.** La spec apunta al fichero con `verifies:`; el fichero apunta de vuelta con `@covers R-CHK-014`. Borrar el test rompe la spec (`V07`); renombrar el requisito rompe el test (`V08`, `V16`).
- **`revisit:` es un hecho, nunca una fecha** (`V10` rechaza fechas). Una fecha llega esté la respuesta o no, y entonces sólo se puede posponer. Es un caso del principio general del repo: ningún campo puede pedir un valor que el modelo tenga que inventar.

### Los seis scripts

| Script | Qué decide |
|---|---|
| `validate.py` | 18 reglas `V01`–`V18` sobre requisitos |
| `charter_lint.py` | 19 reglas `C01`–`C19` sobre el acta |
| `diff_readings.py` | divergencia entre lecturas aisladas |
| `guardian.py` | allow/deny de una edición |
| `oracle.py` | ejecuta `verifies:` por requisito → `green`/`red`/`missing`/`timeout` |
| `gate.py` | la puerta de un proyecto consumidor, veredicto único |

Contrato común de los tres primeros: `--json`, `--no-color`, `--strict`; salida `0` cumple / `1` no cumple / `2` error de uso. **Un proyecto sin `.venoxia/` no es error**: avisa y sale con `0`.

La regla que más carga lleva es `V06` (`verifies:` presente): sin oráculo, no compila. Y `V11` es el presupuesto de incertidumbre: como mucho el 30 % de los requisitos del ámbito en `confidence: low`.

### El flujo, y quién escribe cada estado

```
/venoxia:charter  → charter.md + principles.md      (charter_lint hasta verde)
/venoxia:specify  → changes/<id>/{change.json,proposal.md,delta/*.md}
                    state: draft → specified
                    ⚠ validate.py en rojo por V07 es LO ESPERADO: el test aún no existe
   tú escribes el test con «@covers R-XXX-000»
/venoxia:validate → validate.py en verde
/venoxia:diverge  → 2 lectores + abogado del diablo → readings/*.json → diff_readings.py
                    state: validated  SÓLO si validador Y divergencia salen 0
guardian          → ahora sí deja escribir código
/venoxia:verify   → oracle.py --record: graba el ROJO (antes del código)
   tú escribes el código hasta que el test pasa
/venoxia:verify   → graba el VERDE, state: verified
```

Reglas duras: `specify` nunca escribe `validated` ni `verified`; `diverge` es la única que escribe `validated`; `verify` es la única que escribe `verified`.

**El detalle más contraintuitivo**: el guardián abre la puerta al código en `validated`, no en `verified`. Exigir `verified` antes de escribir sería pedirle al código que exista antes de poder existir — escribir el código es justo lo que convierte el rojo en verde.

### El motor de divergencia

Dos lectores con consignas distintas y un abogado del diablo leen el delta **sin haber estado en la conversación que lo originó**. Devuelven una tabla de decisión cerrada en JSON. El script enfrenta las lecturas:

| Campo | Comparación | Produce |
|---|---|---|
| `scenario` | presencia | escenario que ve uno solo → divergencia **dura** |
| `status_code` | igualdad | dos códigos distintos → **dura** |
| `side_effects` | cobertura contra el repertorio entero del otro | dura sólo si el otro **contradice** (polarity/scope/numeric); si sólo añade, **blanda** |
| `effect` | Jaccard de tokens, umbral `0.6` | por debajo, **blanda** |

La prosa se compara sin palabras vacías y sin conjugación, pero **las cifras nunca se diluyen**: «21 días» contra «14 días» dan similitud cero por mucho que compartan el resto.

Las `readings/` se guardan **crudas**, sin arreglar, y la skill no tiene voto sobre si dos lecturas dicen lo mismo. Las preguntas se plantean como entrevista (`AskUserQuestion`, una por llamada, opciones literales del script) y cada respuesta se anota tal cual en `decisions.json` — ese texto va al delta sin reformular.

### El guardián: la pieza distinta

Cinco caminos de decisión, el primero que casa gana:

1. No existe `.venoxia/` → **allow** (el plugin no estorba a quien no lo ha adoptado).
2. La ruta es spec (`.venoxia/`, `prfaq/`, `specs/`, `spec.md`…) → **allow**.
3. Change activo `validated` **y** `delta/` con un `.md` no vacío → **allow**.
4. Change activo con `"via": "direct"` → **allow**, anotando en `.venoxia/drift/direct.log`.
5. Cualquier otro caso → **deny**, con el comando exacto que lo arregla.

Tres garantías que ningún otro script tiene: **siempre código 0**, **exactamente un JSON por stdout pase lo que pase** (`os._exit(0)` en `finally`, ASCII puro a `sys.stdout.buffer`), y **fail-open** — cualquier excepción propia permite. Un `deny` que no se imprime es una escritura consentida, y por eso la salida no depende de la codificación del envoltorio de texto.

La frontera fina que hay que respetar al tocarlo: un `change.json` con **contenido** malo es culpa del usuario y **no acredita** nada (sigue buscando; si no queda ninguno, `deny`); un fallo de **E/S** al leerlo es culpa nuestra y permite anotando. Confundirlas fue una puerta trasera real — bastaba corromper el `change.json` a propósito.

Y lo que declara sin adornos: no intercepta `Bash`, y quien pueda escribir bajo `.venoxia/` puede fabricarse un change. **Es una barrera contra el descuido, no contra la determinación.**

### El oráculo

`validate.py` comprueba que el oráculo se **declare** y exista; `oracle.py` lo **ejecuta**. Es una invocación **por requisito** — es lo único que permite decir *cuál* falló, no sólo cuántos. El proyecto declara su runner una vez en `.venoxia/venoxia.json` con `{files}`; sin eso, `oracle.py` no adivina y sale con `2`.

`--record` **añade** el run al historial (tope 50) en vez de sustituirlo, y por eso el ciclo rojo→verde queda escrito en disco en vez de recordado. `V17` audita que un `verified` esté respaldado; `V18` avisa de un verde sin rojo detrás. `--dry-run` y `--record` se excluyen: un run grabado sin ejecutar nada sería indistinguible de un verde real.

Dos límites declarados porque no tienen arreglo dentro de él: el `test_command` es del proyecto y el oráculo no lo juzga (un comando que siempre sale `0` pone todo en verde — por eso viaja en `runner.command`), y el `--timeout` es por requisito, no por change.

---

Si quieres, puedo entrar en profundidad en cualquiera de las piezas — el motor de divergencia y el guardián son las dos que más decisiones de diseño esconden.

## Óscar

como funciona el plugin con un proyecto que ya tiene escrito el codigo?

## Claude

Es el caso que el plugin trata con más cuidado, porque es el más común — y este mismo repositorio es la prueba: Venoxia se adoptó a sí mismo con el código ya escrito (`.venoxia/changes/2026-09-04-adopt-venoxia/`).

### El principio: no se especifica el pasado

La adopción es **incremental por diseño**. Nada obliga a documentar las 40 capabilities que ya existen: `validate.py` sólo mira lo que hay bajo `.venoxia/`, y un proyecto sin `.venoxia/` ni siquiera es un error (sale `0`). La spec entra por la puerta por la que ya ibas a pasar: el **próximo** cambio.

### El primer choque, y hay que avisarlo antes

El guardián permite siempre mientras no exista `.venoxia/` (camino 1). El primer `Write` de `/venoxia:charter` crea ese directorio, y **desde ese instante toda edición fuera de `.venoxia/` se deniega** hasta que haya un change validado.

En greenfield eso se resuelve montando el esqueleto antes. Con código delante muerde antes y más fuerte, porque lo siguiente que ibas a teclear era tocar `src/`. `skills/charter/SKILL.md:253` lo trata como paso obligatorio previo al primer `Write`:

> Un usuario que descubre esta secuencia a base de `deny` desinstala el plugin, y con razón: se le ha bloqueado por no saber algo que nadie le dijo.

La válvula es un change con `"via": "direct"` — el camino 4 del guardián: permite todo y anota cada edición en `.venoxia/drift/direct.log`. Es lo que hizo este repo:

```json
{"id": "2026-09-04-adopt-venoxia", "state": "draft", "via": "direct",
 "capabilities": [], "created": "2026-09-04T17:56:22Z"}
```

Sigue ahí, en `draft`, un año después y con 192 líneas en el diario de deriva. Detalle operativo real: como el change activo es el de **mtime más reciente**, reactivar esa vía es un `touch` a su `change.json`.

### `/venoxia:charter` cambia de forma cuando hay código

La skill hace `Glob` sobre `package.json`, `pyproject.toml`, `go.mod`, `README.md`… antes de la primera pregunta, y `charter/SKILL.md:83` fija tres correcciones al acta:

- **El propósito se reconstruye de lo que el código ya hace.** «Preguntar "¿qué vas a construir?" a quien lleva seis meses construyéndolo es empezar por ofender.»
- **La prioridad `#` es el orden en que las capabilities se ponen bajo especificación, no el orden en que se programan.** Lo que ya funciona ocupa fila igual — un acta que sólo lista lo que falta describe medio sistema.
- **El `Done when` de lo que ya existe es el hecho que tiene que _seguir_ siendo cierto.** Es el criterio de no romperlo, y es lo que su primer delta tendrá que preservar.

Y `C16` avisa si el orden que sigues no es el que el acta declara — con `--strict`, rojo.

### Dos vías para el código que ya está

**a) Documentación retroactiva** (capabilities directas, sin `delta/`). Es lo que hizo `adopt-venoxia` con `validator`, `charter-lint`, `guardian` y `divergence`: escribir `.venoxia/capabilities/<slug>/spec.md` describiendo comportamiento que ya existe, con `verifies:` apuntando a un test **que ya pasaba** y añadiendo `@covers <ID>` a ese test.

```markdown
verifies:   tests/test_rules_late.py
confidence: high
from:       README.md#las-16-reglas-del-validador
```

`confidence: high` está justificado y la propuesta lo argumenta: «el comportamiento está decidido, contrastado y tiene test desde antes de este change; no hay nada que apostar sobre él».

Estos changes **no tienen `delta/`**, así que `oracle.py` no tiene nada que atribuirles — `collect_requirements` sólo lee `delta/*.md`, por diseño, para poder decir de qué change es cada rojo o verde. No es error (sale `0`) y `--dry-run` lo dice en vez de callarse (`README.md:315`).

**b) El bucle normal** para todo lo que venga después: `specify` → `validate` → `diverge` → `verify`. Ahí el ciclo rojo→verde funciona igual que en greenfield.

### Lo que se comporta distinto en brownfield

| | Greenfield | Con código escrito |
|---|---|---|
| `V07` (el test existe) | rojo al principio, **y eso es correcto** | puede salir verde desde el primer minuto |
| `V18` (verde con rojo detrás) | se cumple solo | **es donde aparece la fricción real** |
| `V16` (test con `@covers` huérfano) | poco ruido | poco ruido también: sólo escanea los ficheros que algún `verifies:` nombra, no el repo entero |

`V18` es el punto que hay que entender: si especificas comportamiento cuyo test **ya pasa**, el oráculo graba verde sin rojo previo. `V18` lo marca como aviso y `/venoxia:verify` no escribe `verified` en silencio — avisa de «verde sin rojo» y **pide confirmación explícita**. No lo prohíbe, porque en adopción retroactiva es legítimo; lo deja anotado, que es distinto de fingir que hubo TDD.

### El recorrido, en comandos

```bash
# 0 · el interruptor, antes de que el guardián se ponga en pie
#     .venoxia/changes/adopt/change.json con "via": "direct"

/venoxia:charter        # el acta a posteriori; capabilities existentes incluidas
                        # → escribes capabilities retroactivas + @covers en tests que ya pasan
/venoxia:validate       # verde sin haber escrito una línea de código nuevo

# a partir de aquí, el bucle normal para el cambio siguiente
/venoxia:specify "…"    # el delta del cambio que de verdad querías hacer
/venoxia:validate
/venoxia:diverge
/venoxia:verify         # rojo
#   … código
/venoxia:verify         # verde
```

### El coste honesto

Dos cosas que conviene saber antes de adoptarlo en un repo grande:

1. **La vía `direct` es adictiva.** 192 líneas de `drift/direct.log` en este repo lo dicen: cada vez que hay prisa, un `touch` al `change.json` de adopción abre la puerta. Está registrada, no vigilada — es exactamente el diseño («barrera contra el descuido, no contra la determinación»), pero un equipo que la usa por defecto no ha adoptado nada.
2. **Documentar retroactivamente cuesta tiempo real y no produce comportamiento nuevo.** La razón por la que este repo lo hizo está escrita en su propia propuesta: «un plugin que impone especificar antes de programar y no se especifica a sí mismo no tiene autoridad». En un proyecto ajeno, la vara es más pragmática: documenta retroactivamente **sólo las capabilities que el próximo delta va a tocar**, y deja las demás sin fila hasta que les toque.

## Óscar

Explicame la parte de 
"tú escribes el código hasta que el test pasa"

## Claude

Es el único paso del ciclo que **no tiene comando**. Y eso es deliberado — es el hueco donde el plugin se aparta.

### Quién es «tú»

Quien programa: tú a mano, Claude Code en conversación normal, tu IDE, lo que sea. Lo que está prohibido es que lo haga **una skill de Venoxia**, y las cuatro lo declaran en su primera pantalla:

```
specify/SKILL.md:21   «Nunca tocas código de producción desde esta skill.»
charter/SKILL.md:22   «Nunca tocas código de producción desde esta skill,
                       ni el andamiaje del proyecto.»
verify/SKILL.md:22    «Nunca editas tests ni código de producción.»
```

Y las dos dan la misma razón, con las mismas palabras:

> Escribir la spec y escribir la implementación en el mismo impulso es exactamente lo que el guardián existe para impedir.

Si `/venoxia:specify` pudiera escribir `src/`, la spec se escribiría **para justificar el código** en vez de al revés, y el ciclo entero sería teatro. La separación no se pide por buenas costumbres: se hace imposible dentro de la skill.

`verify` añade su propia versión, más afilada: si tocara el test o la implementación, **el rojo que acaba de grabar dejaría de ser honesto**.

### Qué pasa exactamente en ese momento

En ese punto el disco ya tiene cuatro cosas colocadas:

| | |
|---|---|
| `delta/*.md` | el requisito con su `verifies:` y su `confidence:` |
| el fichero de test | existe, con `@covers R-XXX-000` dentro |
| `change.json` | `"state": "validated"` — validador **y** divergencia en `0` |
| `oracle.json` | run 1 con `all_green: false` — el rojo grabado |

Con eso, cada `Edit`/`Write` que hagas sobre `src/` entra por el **camino 3** del guardián (`scripts/guardian.py:883`): change activo `validated` + `delta/` con un `.md` no vacío → **allow**. Sin eso habría sido `deny` con el comando exacto que lo arregla.

Aquí está la asimetría que más cuesta ver: **el guardián abre la puerta en `validated`, no en `verified`**. Exigir `verified` antes de escribir sería pedirle al código que exista antes de poder existir — escribir el código es literalmente la operación que convierte el rojo en verde.

### «Hasta que el test pasa» no es una impresión

Ése es el punto de todo el montaje. El criterio de parada no es «cuando me parezca que está», es un exit code:

```bash
python3 scripts/oracle.py --root . --change <id>    # 0 = todos green
```

Una invocación **por requisito**, no una por change: por eso puede decir *cuál* falló, no sólo cuántos. Y como el rojo del paso 7 ya está en `oracle.json`, cuando el verde llegue tendrá un antes documentado — que es exactamente lo que `V18` busca y lo que `/venoxia:verify` exige antes de escribir `verified`.

De ahí la simetría del paso siguiente: `verify` **no toca `change.json`** cuando el resultado es rojo. Se queda en `validated` y dice «rojo correcto» (`verify/SKILL.md:79`). El estado sólo avanza cuando el disco lo respalda.

### Los tres límites, dichos sin adornos

1. **El guardián no comprueba *qué* fichero estás editando.** El camino 3 mira que exista un change `validated` con delta no vacío, y ya. Un delta sobre `checkout` te deja escribir en `billing/` igual: no hay correspondencia entre la ruta editada y el requisito. Comprobarlo rompería el presupuesto de 100 ms.

2. **`Bash` no se intercepta.** Un `sed -i`, un `>` o un `git apply` pasan sin verse. El matcher es `Edit|Write|NotebookEdit` y nada más.

3. **El verde vale lo que valga el test.** El oráculo no juzga el `test_command`: sólo comprueba que traiga `{files}`. Un comando que siempre termina en `0` pone todo en verde. Por eso `runner.command` viaja dentro de cada run de `oracle.json` — quien revisa un `verified` mira también qué comando lo produjo.

Los tres apuntan a lo mismo, que es la frase con la que el README cierra la sección del guardián: **es una barrera contra el descuido, no contra la determinación**. Protege del viernes con prisa, no de quien ha decidido saltárselo.

## Óscar

yo no programo, lo hace clade code, yo solo le digo que debe programar y para eso es el plugin, se debe crear todo el spec y pruebas necesarias para que el claude code sepa que y como lo tiene que programar y probar

## Claude

Exacto, y ése es el uso para el que está diseñado. Reencuadro el ciclo con los roles reales, porque el README lo narra en segunda persona («tú escribes el test») y eso oculta lo que de verdad pasa en tu modo de trabajo.

### Los roles reales

| Paso | Quién actúa | Herramienta |
|---|---|---|
| Definir el proyecto | **tú**, contestando la entrevista | `/venoxia:charter` |
| Redactar la spec | la skill, con tus respuestas | `/venoxia:specify` |
| Comprobar que la spec es válida | el script, sin modelo | `/venoxia:validate` |
| Resolver ambigüedades | **tú**, eligiendo en las preguntas cerradas | `/venoxia:diverge` |
| **Escribir el test** | **Claude Code**, en conversación normal | `Write` |
| **Escribir el código** | **Claude Code**, en conversación normal | `Edit`/`Write` |
| Decidir si está hecho | el script, sin modelo | `/venoxia:verify` |

Las cuatro decisiones que importan las tomas tú (qué construir, en qué orden, cómo se resuelve cada ambigüedad, qué cuenta como hecho) o las toma un script determinista. Ninguna la toma un modelo.

Lo que las skills prohíben no es que Claude Code programe: es que **la skill** programe. `/venoxia:specify` no puede escribir `src/` porque escribir la spec y la implementación en el mismo impulso hace que la spec se redacte para justificar el código. Fuera de la skill, en conversación normal, Claude Code programa con toda naturalidad — y el guardián le deja porque hay un change `validated` que lo acredita.

### Qué recibe Claude Code como instrucción

Cuando le dices «implementa el change `<id>`», lo que le dice qué hacer no es tu frase, son cuatro cosas en disco:

1. **`delta/*.md`** — la cláusula EARS: qué debe pasar, cuándo.
2. **Los `#### Scenario:`** — la tabla de decisión cerrada, caso por caso, ya desambiguada por `/venoxia:diverge` con tus respuestas literales en `decisions.json`.
3. **`principles.md`** — las restricciones que toda spec de este proyecto respeta.
4. **El criterio de parada** — no «cuando parezca listo», sino `oracle.py` en verde, requisito por requisito.

### Pero el «cómo» no está en la spec, y es deliberado

Aquí tengo que corregir una parte de tu frase, porque afecta a lo que puedes esperar. `specify/SKILL.md:27` lo pone como primer principio:

> **Si la implementación puede cambiar sin que cambie el comportamiento observable, no pertenece a la spec.**
>
> El nombre de la tabla, la librería del cliente HTTP, si hay caché o no, el número de reintentos internos: […] Lo que no pertenece a la spec y aun así se escribe en ella se convierte en una mentira en cuanto alguien refactoriza, y una spec que miente ya no la lee nadie.

La spec te da el **qué** con precisión de contrato. El **cómo** vive en otros dos sitios: `principles.md` (convenciones técnicas del proyecto — el stack, los patrones, lo que no se hace) y el propio test, que fija el contrato ejecutable. Si intentas meter el «cómo» en el delta, `/venoxia:validate` no te lo impide, pero la spec se vuelve falsa en el primer refactor y habrás perdido lo único que la hacía útil.

Si quieres dirigir más el «cómo», el sitio es `principles.md`. Ahí es donde escribes «TypeScript estricto, sin `any`», «nada de ORM», «los errores se propagan, no se tragan» — y eso lo lee cada `/venoxia:specify` de aquí en adelante.

### Un hueco real del flujo, y en tu modo de trabajo muerde

Esto lo acabo de verificar ejecutando el guardián, no es una sospecha.

El README manda escribir el test en el paso 5, cuando el change está en `specified` (`validated` no llega hasta el paso 6, tras `/venoxia:diverge`). Pero un fichero de test **no es spec path** — `is_spec_path` sólo reconoce `.venoxia/`, `prfaq/`, y markdown bajo `docs/spec*`/`specs/` o llamado `spec.md`/`proposal.md`/`delta*.md`. Con el change en `specified`, el camino 3 no casa y cae al 5:

```
state: specified  → Write test/checkout/reservation.spec.ts  →  DENY
state: validated  → Write test/checkout/reservation.spec.ts  →  allow
```

El mensaje del deny te manda a `/venoxia:specify` y `/venoxia:validate` — que es justo lo que ya has hecho y no desbloquea nada. Y hay circularidad: `/venoxia:diverge` sólo escribe `validated` si `validate.py` sale `0`, pero `validate.py` no puede salir `0` sin el test (`V07`).

Programando a mano con un editor ni te enterarías. **Programando con Claude Code, cada test pasa por `Write` y choca de frente.** Y `specify/SKILL.md:179` termina entregando «la lista exacta de tests que hay que escribir» sin avisar de que escribirlos va a ser denegado.

Salidas posibles, de menos a más invasiva:

- **Hoy, sin tocar nada:** `"via": "direct"` en el `change.json` mientras se escribe el test, y quitarlo después. Funciona y queda anotado en `drift/direct.log`, pero convierte la vía de escape en parte del flujo normal, que es justo lo que no quieres.
- **Arreglo pequeño:** reconocer en `is_spec_path` los ficheros que algún `verifies:` del change activo nombra. Cuesta leer el delta en el guardián — presupuesto de 100 ms.
- **Arreglo barato:** que el camino 3 acepte `specified` **sólo** para rutas que parezcan test (`test/`, `tests/`, `*.spec.*`, `*_test.*`). El código es comportamiento; el test es el oráculo, y el oráculo nace antes por diseño.

Si quieres, especifico esto como un change y lo pasamos por el propio ciclo — es exactamente la clase de hallazgo que el plugin existe para atrapar, y sería buen dogfooding.

## Óscar

A que te refieres con "tu modo de trabajo"?

## Claude

A lo que acabas de describirme: que tú no programas y todas las escrituras de fichero las hace Claude Code.

Eso no es un detalle de estilo, decide si el guardián existe o no:

| Cómo se escribe el fichero | ¿Pasa por el hook? |
|---|---|
| Claude Code con `Write`/`Edit` | **sí** — el matcher es `Edit\|Write\|NotebookEdit` |
| Tú en vim, VS Code, cualquier editor | no — el editor escribe directo al disco |
| `cat > fichero`, `sed -i`, `git apply` | no — `Bash` no se intercepta |

Así que en tu caso **el 100 % de las escrituras se someten al guardián**, y por eso el deny al escribir el test aparece siempre. Quien programa a mano nunca lo ve: escribe `test/checkout/reservation.spec.ts` con el change en `specified` y no se entera de que el guardián lo habría denegado.

Lo interesante es que la relación va en los dos sentidos. Tu modo es el único en el que el plugin está de verdad en pie — en los otros el guardián es casi decorativo y sólo quedan los scripts que corres tú a mano. **Es el modo para el que Venoxia está diseñado, y a la vez el único que tropieza con ese hueco.** Que el flujo del README no lo contemple sugiere que se escribió pensando en el otro.

## Óscar

Estas dando vueltas, define bien segun tu como seria la forma de trabajo con este plugin, no el como esta hecho, sino cual es la vision de producto segun tu yo tengo y que fue lo que me entendiste para crear este plugin ultrathink

## Claude

No estás pidiendo la mecánica. Estás pidiendo que te devuelva tu propia tesis para ver si la entendí. Aquí va, en primera persona y sin hablar de scripts.

---

### Lo que entendí que querías

**Tú no revisas código. Ese es el axioma, y todo lo demás sale de ahí.**

Quien dirige a un agente que programa tiene un problema que no es técnico: **no puede verificar el trabajo leyendo el trabajo**. Un jefe de equipo lee el PR. Tú no. Entonces te quedan tres formas de saber si lo que te entregaron es lo que pediste, y las tres son malas:

- la palabra del agente («listo, implementado») — es la parte interesada;
- probarlo a mano — sólo encuentras lo que se te ocurre probar;
- que los tests pasen — pero los tests los escribió el mismo agente.

Y hay una segunda mitad. Cuando dices *«que se reserve el stock al pagar»*, tú tienes en la cabeza una película completa: qué pasa si falta stock en una línea, cuánto dura la reserva, qué ve el cliente. El agente tiene **una** interpretación de esa frase, no la tuya, y **rellena los huecos en silencio**. Programa rapidísimo la cosa equivocada y lo hace con confianza total. Tú lo descubres al final, cuando ya hay código, ya hay tests, y la conversación donde nació el malentendido ya ni existe.

Venoxia es una respuesta a esas dos cosas a la vez:

> **Mover toda la conversación difícil al momento en que es barata —antes de que exista una línea de código— y dejar lo acordado por escrito en un formato que una máquina pueda comprobar sin preguntarle a nadie.**

Eso es el producto. Lo demás son consecuencias forzadas.

### Tu jornada, que es de lo que va todo

Cuatro momentos, y sólo cuatro:

**1. Dices lo que quieres.** Una frase. «Que el cliente pueda reservar mesa para una fecha y hora.» No especificas nada: eso es trabajo del sistema.

**2. Contestas preguntas cerradas.** Y aquí es donde el producto vale lo que vale. Dos lectores leen la especificación **sin haber estado en tu conversación** — que es exactamente la situación del agente que va a programar mañana, o de la persona que llegue en seis meses. Donde los dos leen cosas distintas, hay un hueco. Y ese hueco no se rellena solo ni lo rellena el modelo: **te sube a ti convertido en una pregunta de producto**, con dos o tres opciones concretas. «Si falta stock en una línea: ¿se reserva el resto, o no se reserva nada?» Tú eliges. Tu respuesta se guarda **literal**, sin que nadie la mejore de camino.

Eso es lo que estás comprando de verdad: **un mecanismo que convierte lo que no dijiste en preguntas que sí sabes contestar**. Y sólo de producto — nunca «¿usamos Redis o Postgres?», porque eso no es tuyo.

**3. Sueltas al agente.** «Implementa esto.» No miras el diff. No supervisas. No te asomas.

**4. Miras un veredicto.** Verde o rojo, y si es rojo, qué requisito falló. Un número, no una opinión.

Entre el 3 y el 4 **no hay revisión de código**. Esa es la eliminación: el producto sustituye la revisión de código —que tú no puedes hacer— por un contrato acordado antes que sí puedes leer.

### Por qué el diseño sale forzado de ahí

Cada decisión rara del plugin deja de ser rara si aceptas el axioma:

**Ningún script consulta a un modelo.** No es purismo de ingeniería. Si el juez que dice «esto está hecho» es un modelo, has vuelto a preguntarle a la parte interesada. El veredicto tiene que ser creíble para alguien que no puede auditarlo, y eso obliga a que sea aritmética.

**Todo requisito nace con su test declarado.** «Está hecho» tiene que significar algo fuera de la conversación. Si el test se añade al final, se escribe para que el validador calle; si nace con el requisito, la pregunta que se hace el que escribe es *«¿qué falla si esto se incumple?»*, que es una pregunta sobre el comportamiento.

**El rojo se graba antes que el código.** Porque el agente escribe el test y también la implementación, y un test que nunca se vio fallar no ha demostrado nada. El rojo previo es la prueba de que el oráculo medía algo. Es la desconfianza justa hacia quien hace las dos mitades del trabajo.

**Ningún campo pide un valor inventado.** Le pides una fecha a un modelo y te la da — y es basura, porque no la sabe. Por eso `revisit` es *el hecho que resuelve la apuesta* y no un día del calendario: un hecho hay que apoyarlo en algo real, y además te dice qué mirar cuando llegue. Nadie abre un fichero porque hoy sea 12 de noviembre; cualquiera sabe contestar a «¿ya habéis cerrado las diez primeras compras?».

**La implementación no entra en la spec.** Porque la spec es tu único mapa del sistema. En el momento en que habla de librerías y tablas, se vuelve mentira en el primer refactor, y tú te quedas sin mapa y sin manera de saber que lo perdiste.

**El guardián.** Todo lo anterior es un buen hábito, y los buenos hábitos se caen el viernes con prisa. El guardián lo convierte en infraestructura: no lo hace imposible, lo hace **deliberado**. Y cuando te lo saltas, lo apunta, en vez de fingir que no pasó.

**La confianza va declarada.** Tú no puedes juzgar si un requisito es sólido. El que lo escribe sí, y tiene que decirlo — con el por qué. `confidence: medium · los 15 minutos son una apuesta, no un dato` te da algo que hacer; «medium» a secas, no.

### El cambio real, en una línea

Sin el plugin, tu bucle es: **pides → programa → miras → «no, así no» → vuelve a programar.** La corrección ocurre *después* del código, que es donde es cara y donde tú estás peor equipado.

Con el plugin: **pides → contestas cuatro preguntas → programa → veredicto.** La corrección ocurre *antes*, sobre frases en español, que es donde eres el experto.

**Desplaza tu intervención de la revisión al encargo.** Y como efecto secundario, lo que decidiste el martes sigue existiendo el jueves: los agentes olvidan cada sesión, y `.venoxia/` es la memoria del proyecto en un formato que el agente lee y una máquina comprueba.

### Dónde el plugin todavía no alcanza a esa visión

Parte de haber entendido la idea es ver dónde el artefacto se queda corto. Cuatro cosas, la primera es la grande:

**1. Falta el comando del paso que más haces.** «Implementa el change» es el momento central de tu jornada y es el único sin skill. Hoy se hace a pelo, confiando en que el agente encuentre el delta, lea los principios, respete tus decisiones literales y sepa que el criterio de parada es el oráculo. Los pasos que tú apenas tocas tienen los cinco comandos; el que ocupa el 80 % de tu tiempo no tiene ninguno. **Ese es el hueco de producto más caro que le veo.**

**2. La narrativa del README está escrita para el usuario que no eres.** «Tú escribes el test» en el paso 5. Tú no escribes tests. El bloqueo del guardián que encontré antes es el síntoma; la causa es que el recorrido canónico supone a alguien que programa.

**3. Nada comprueba que el test cubra los escenarios.** Se comprueba que el test exista, que apunte al requisito y que se le viera fallar. Pero un requisito con cuatro escenarios y un test que comprueba uno pasa igual. Los escenarios están ahí, escritos y contados — están pidiendo que alguien los enfrente al test.

**4. El veredicto habla en el idioma del sistema, no en el tuyo.** «R-CHK-014 en rojo» es correcto. «El pedido con una línea sin stock todavía crea la reserva» es lo que tú necesitas leer, y está escrito en el escenario, a un paso de distancia.

---

Si la lectura te encaja, el punto 1 es por donde yo empezaría, y da un plugin distinto: uno que también dirige la implementación, no sólo la autoriza. Y si no encaja, dime en qué me desvié — es más útil corregir esto que cualquier detalle de los scripts.

## Óscar

Yo se escribir codigo, simplemente no lo quiero hacer para eso uso claude code, y tu vision del proyecto deja por fuera las definiciones tecnicas, lineamientos, como indicaste el principles.md, yo soy el lider tecnico y product owner al mismo tiempo, quiero que todas las definiciones del producto tanto tecnicas como funcionales esten escritas desde antes de generar una linea de codigo, sebe quedar definido, stack, despliegue, pruebas, valores por default, constantes, todo lo que invlucra el desarrollo de software, entonces tu definicion se esta quedando corta ultrathink

## Claude

Tienes razón, y el error no fue de matiz. Te describí como alguien que no puede leer código —no es el caso, eliges no escribirlo— y, más grave, tomé un principio que **acota un contenedor** y lo convertí en el límite del producto.

### Dónde me equivoqué

«La implementación no pertenece a la spec» acota **el requisito**: si metes «usamos Redis» dentro de una cláusula EARS con escenarios y un test detrás, fabricas un requisito que se vuelve falso en el primer refactor. Eso sigue siendo cierto.

Pero de ahí yo salté a **«el cómo no pertenece al contrato»**, y eso es falso y además contradice lo que tú ya construiste. El contrato del proyecto tiene dos contenedores desde el principio: el requisito y `principles.md`. Lo que pasa es que el segundo es un pariente pobre, y ahí está el hueco de verdad.

### La asimetría

Un proyecto dirigido por un agente sufre **dos derivas**, no una:

**Deriva funcional** — le dices «reserva el stock al pagar», él elige en silencio qué hacer si falta stock en una línea, y programa la cosa equivocada con total confianza.

**Deriva técnica** — le pides una feature el lunes y valida con `zod`; el jueves, en otra sesión, con `yup`. Elige un timeout de 30 s aquí y de 5 s allá. Monta el test junto al fichero o en `tests/` según le pille. **Ninguna de esas decisiones fue tuya, ninguna quedó escrita, y ninguna es la misma dos veces.**

Es el mismo fallo: el agente rellena un hueco sin decírtelo. Y tu plugin tiene un aparato entero para la primera —delta EARS, lectores aislados, divergencia, preguntas cerradas, decisiones literales, oráculo, guardián, gate— y para la segunda tiene **un fichero markdown en prosa, sin oráculo, sin confianza declarada, sin ciclo de vida y sin nadie que compruebe que se cumple**.

Ésa es la cojera. No es que falte contenido en `principles.md`: es que `principles.md` no está sometido a la misma tesis que todo lo demás.

### La tesis, completa

La original:

> Un requisito sin `verifies:` es una opinión.

La que faltaba, con la misma forma:

> **Una decisión técnica sin verificación es una intención.** Stack, despliegue, estrategia de pruebas, constantes, valores por defecto: son apuestas sobre el sistema exactamente igual que un requisito, y deben declarar cómo se comprueba que siguen vigentes y cuánta confianza tienen.

Porque el `verifies:` de una decisión técnica no es un test de comportamiento — es **un comando que falla si la decisión se incumple**. Y casi todas lo tienen:

| Decisión | Qué la comprueba |
|---|---|
| «TypeScript estricto, sin `any`» | `tsc --strict` + regla de lint |
| «Python 3 stdlib, sin dependencias» | la matriz en Docker, un import-check |
| «Postgres, no MySQL» | el lockfile |
| «Cobertura mínima por fichero» | un umbral y un exit code |
| «Esquema JSON versión 1, estable» | los graders de regex |
| «El timeout por defecto son 5 s» | una constante en un sitio y un test que la lee |
| «Despliegue en Vercel» | **ninguno** — y eso hay que declararlo, no fingirlo |

Esa última fila importa tanto como las otras. Igual que admites `confidence: low` con su `revisit:`, aquí hace falta admitir decisiones que **ninguna máquina comprueba**, marcadas como tales. Un principio que dice «esto se verifica en revisión humana» es honesto; uno que aparenta oráculo y no lo tiene es peor que no tenerlo.

### Ya lo construiste, pero fuera del modelo

Esto es lo que más me convence de que la lectura va bien: **los oráculos de tus principios ya existen en tu repo y no los llamaste así**.

`tools/coverage.py` con umbrales por fichero es un principio técnico con verificación determinista. `tools/check.py` es la puerta que corre todos los oráculos técnicos a la vez —matriz 3.12/3.13/3.14, cobertura, gate, plugin validate—. Y tu `principles.md` ya dice exactamente lo que describes: stack, comando de pruebas, idiomas, contratos de exit codes, estabilidad del esquema JSON.

Lo que falta es que esas dos mitades se conozcan. Hoy `principles.md` **afirma** «Python 3 stdlib, probado con 3.14» y `check.py` **lo comprueba**, pero nada las une: puedes cambiar una sin que la otra se entere, que es la definición exacta de spec que miente. Y la cobertura ni siquiera figura como principio, sólo como herramienta.

### Una corrección al «antes de la primera línea de código»

Con un matiz, porque sale de tu propio principio de no inventar valores.

El stack, el despliegue, las convenciones y la estrategia de pruebas **sí** se deciden el día 1: son decisiones que tienes tomadas o que puedes tomar con la información que ya hay.

Los valores por defecto y las constantes de un módulo que aún no existe, **no**. Obligarte a fijar el TTL de una reserva antes de haber hablado de reservas produce un número inventado, que es justo lo que `revisit:` existe para impedir.

La formulación exacta es la que ya usas con las capabilities: **el inventario completo desde el día 1, la resolución antes del change que la necesita.** El acta lista las capabilities todas y priorizadas, pero sólo se especifica la que toca. Igual aquí: el conjunto de decisiones técnicas se declara entero al principio —incluidas las que están **abiertas**—, y cada una se cierra antes de la línea de código que la consume. Una decisión técnica pendiente ya tiene sitio en tu modelo: es una apuesta del acta, con el hecho que la resuelve.

### Lo que eso cambia, en corto

- `principles.md` deja de ser prosa y pasa a ser **decisiones con ID, verificación y confianza**, con su propio linter — igual que el acta tiene el suyo.
- Las que hoy son `tools/*.py` sueltos se declaran como el oráculo de la decisión que verifican.
- `gate.py` corre también esos oráculos: hoy tu puerta comprueba el acta, la spec y el comportamiento; le falta comprobar que el proyecto sigue siendo el que dijiste que era.
- La divergencia sirve igual: «usa caché donde haga falta» se lee de cinco maneras, y el motor de lectores es agnóstico al contenido.
- Y las decisiones técnicas abiertas se te suben a ti, porque eres el que las decide — cosa que yo tenía mal anotada y acabo de corregir.

---

Dime si **ahora** la lectura es la tuya. Si lo es, el siguiente movimiento natural es especificar esto por el propio ciclo: es un cambio de comportamiento del plugin, con capability propia, y es el candidato más claro que le veo a la siguiente entrega.

## Óscar

guarda esta conversacion en un archivo para no perderla

---

## Cierre

La respuesta a la última petición no aparece arriba: el registro se escribe
con un turno de retraso.

**El hilo, en tres pasos:**

1. Explicación del plugin: piezas, flujo, guardián, oráculo, y cómo se adopta
   en un proyecto con el código ya escrito.
2. Hallazgo verificado: con el change en `specified`, el guardián **deniega**
   escribir el fichero de test que el propio flujo manda escribir en ese punto.
   Sólo muerde cuando quien programa es Claude Code, porque es el único modo
   en que todas las escrituras pasan por `Edit`/`Write`.
3. Corrección de la visión: el contrato no es sólo el comportamiento. Las
   definiciones técnicas —stack, despliegue, pruebas, constantes, valores por
   defecto— son apuestas igual que un requisito y necesitan su propia
   verificación. Hoy viven en `principles.md` sin oráculo, mientras sus
   oráculos reales (`tools/coverage.py`, `tools/check.py`) viven fuera del
   modelo, sin que nada una las dos mitades.
