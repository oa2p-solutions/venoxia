---
name: diverge
description: "Somete el delta de un change de Venoxia a dos lectores aislados con consignas distintas y al abogado del diablo, y deja que el script calcule la divergencia y formule las preguntas cerradas. Debe usarse cuando el usuario pida «busca ambigüedades», «pasa la divergencia», «lanza los lectores», «¿esto se lee igual por dos personas?», o justo después de que /venoxia:validate quede en verde."
argument-hint: "el id del change a examinar (opcional)"
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
  - Agent(venoxia:reader, venoxia:devils-advocate)
  - Bash(mkdir -p *)
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/diff_readings.py" *)
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" *)
  - Bash(python3 *)
---

# Venoxia · divergencia

Change a examinar: **$ARGUMENTS**

Pedirle al mismo modelo que encuentre sus propias ambigüedades no funciona: ya sabe qué quiso decir, así que rellena los huecos sin darse cuenta de que eran huecos. La ambigüedad sólo aparece cuando dos lectores que **no** estuvieron en la conversación leen el mismo texto y responden distinto a la misma pregunta.

Tu trabajo aquí es de logística, no de criterio: montar el panel en condiciones, guardar lo que devuelve sin tocarlo y dejar que el script haga la aritmética.

**Y al empezar se anuncia la versión del plugin** que está corriendo, en la primera línea, leída de `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (`Venoxia 0.6.0 · diverge`); si el fichero no se puede leer, se dice `unknown` con la misma claridad. Es lo que permite demostrar después, con el informe delante, que corrió la versión instalada y no una copia vieja: el JSON del script lleva la misma versión en su clave `tool`.

---

## Paso 1 · Localizar el change y sus deltas

Si `$ARGUMENTS` trae un id, ese. Si no, mira los `.venoxia/changes/*/change.json` con `state` distinto de `archived`: con uno solo, ese, y di cuál es antes de seguir; con **más de un change** no archivado, pregunta cuál examinar con `AskUserQuestion`, **con los ids como opciones** y su estado en la descripción. La fecha de los ficheros no decide nada: el que se modificó hace un minuto no es necesariamente el que el usuario tiene en la cabeza.

Y **un change en `verified` no se examina sin su id**, y tampoco con él: ya está verificado, y esta skill **nunca vuelve a `validated`** un estado que el oráculo respalda. Dilo y para; si el comportamiento tiene que cambiar, el camino es un change nuevo por `/venoxia:specify`.

Los deltas son `.venoxia/changes/<id>/delta/*.md`. Si no hay ninguno, no hay nada que leer: dilo y para, el camino es `/venoxia:specify` primero.

Anota las rutas **absolutas** de cada delta. Es lo único que van a recibir los lectores.

## Paso 2 · Despachar el panel: dos lectores y el abogado, en un solo mensaje

**Las tres llamadas a `Agent` van en el mismo mensaje.** Dos razones, y las dos importan: corren en paralelo, y —más relevante— nada de lo que devuelva el primero puede influir en cómo despachas al segundo. En cuanto los encadenas, el panel deja de medir lo que dice medir.

### Qué recibe cada agente, y qué no

Cada uno recibe **sólo la ruta del delta** y su contrato de salida. Nada más.

Prohibido pasarles, en cualquier forma y por muy útil que parezca:

- El contexto de la conversación donde nació la spec.
- La propuesta, el `proposal.md`, el ticket, el PR/FAQ o la intención del cambio.
- Un resumen tuyo de qué hace el cambio o de qué se pretende.
- La salida del otro lector, o cualquier pista sobre lo que ha respondido.
- Cualquier aclaración de las que tú diste al redactar la spec.

Si les explicas la intención, les has dado la respuesta y el panel ya no mide nada. La pregunta que responden es literalmente *«qué dice este documento, leído a solas»*, y si el documento no lo dice, ese es el hallazgo.

### Lector A — consigna de implementador

Lee el delta como el contrato que tiene que implementar mañana. Por cada `#### Scenario:` del fichero: qué tiene que hacer el código, qué efecto observable produce, qué código de estado devuelve y qué queda modificado en el sistema. **Se compromete con una lectura concreta**: donde el texto admita dos interpretaciones, elige la que elegiría al escribir el código, sin señalarlo. Sólo marca `unclear: true` cuando de verdad no pueda elegir ninguna.

### Lector B — consigna de responsable de QA

Lee el delta como el suite de aceptación que tiene que escribir. Por cada `#### Scenario:`: qué evidencia demuestra que el escenario se cumple, qué ve exactamente el cliente en la respuesta, y qué estado queda en el sistema después. Mismo compromiso: se moja con una lectura, y sólo declara `unclear: true` cuando no hay forma de decidir qué habría que comprobar.

Las dos consignas son distintas **a propósito**: el riesgo conocido de este diseño es que dos lectores con el mismo prompt converjan en el mismo error y la convergencia salga verde por parecido, no por claridad. No las suavices hasta que digan lo mismo, y no reutilices el texto de una para la otra.

Contrato de salida de los dos lectores: un **array** JSON, un objeto por escenario, sin texto alrededor.

```json
[{"scenario": "<título literal del escenario>",
  "requirement_id": "<el R-XXX-NNN bajo el que está el escenario>",
  "input": "<el valor literal que el WHEN pone a prueba, o null>",
  "effect": "<≤12 palabras>",
  "status_code": "<código o null>", "side_effects": ["…"],
  "unclear": false, "unclear_why": null}]
```

`scenario` se copia literal del delta: es la clave por la que el script empareja las lecturas, y un título reescrito se convierte en una divergencia falsa de tipo `missing_scenario`. `requirement_id` e `input` son los dos campos que permiten al script agrupar por política sin fundir requisitos distintos y enseñar en la matriz de cada decisión de qué entrada habla cada fila; las lecturas antiguas que no los traen siguen valiendo, con los dos a `null`.

### Abogado del diablo

Un solo trabajo: encontrar el caso en el que cumplir la spec **al pie de la letra** produce un resultado que nadie quiere. No busca errores de redacción ni huecos, busca obediencia literal con consecuencias inaceptables.

```json
[{"attack": "…", "requirement_id": "R-CHK-014", "severity": "high"}]
```

`severity` es `high`, `medium` o `low`.

## Paso 3 · Guardar la salida cruda, sin arreglarla

```bash
mkdir -p ".venoxia/changes/<id>/readings"
```

Y escribe, tal cual llegó:

| Agente | Fichero |
|---|---|
| Lector A | `.venoxia/changes/<id>/readings/reader-a.json` |
| Lector B | `.venoxia/changes/<id>/readings/reader-b.json` |
| Abogado del diablo | `.venoxia/changes/<id>/readings/devils-advocate.json` |

**Literal.** No reordenes los objetos, no normalices los códigos de estado, no completes un campo que falte, no unifiques la redacción de dos `effect` parecidos, no borres un escenario que un lector se inventó ni añadas el que se dejó. Cada una de esas «mejoras» borra exactamente la señal que has ido a buscar: si arreglas la salida de A para que case con la de B, has fabricado una convergencia.

Si un lector devuelve JSON malformado, guárdalo malformado. El script lo reportará en el informe y saldrá con `2`; eso es información real sobre lo que pasó, y taparla no.

La única intervención permitida es quitar la valla de código markdown con la que algún agente haya envuelto su JSON —las tres comillas invertidas y la etiqueta `json`—: eso es embalaje de transporte, no contenido.

## Paso 4 · Que el script calcule la divergencia

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/diff_readings.py" \
  --readings ".venoxia/changes/<id>/readings" \
  --out ".venoxia/changes/<id>/divergence.md" \
  --no-color
```

**La skill no decide si hay divergencia: eso lo calcula el script.** La normalización, el emparejado de escenarios, la comparación campo a campo y el umbral de similitud están en código precisamente para que no dependan del criterio de un modelo. Tú no tienes voto sobre si dos lecturas «vienen a decir lo mismo».

El script compara la prosa sin palabras vacías y sin conjugación, así que la voz activa y la pasiva cuentan como la misma lectura; las cifras nunca se diluyen; y los efectos colaterales se buscan contra `effect` y `side_effects` juntos, porque el reparto entre esos dos campos es cosa de cada lector y no del delta. Si aun así el informe te trae una pregunta que es puro vocabulario, la opción «no hay divergencia real» está para eso —pero no la uses para despachar en bloque: cada pregunta que se cierra sin mirar es una ambigüedad que llega al código.

| Código de salida | Significado | Qué dices |
|---|---|---|
| `0` | La ejecución no falla. Son **dos** veredictos distintos: `converged` (ni duras, ni blandas, ni lagunas) y `soft_only` (sólo divergencias blandas, que por sí solas no tumban la ejecución salvo con `--strict`) | Copia el titular del informe. Sólo dices «convergen» si el informe lo dice: con `soft_only` dice «Las lecturas casi convergen» y hay desacuerdo que presentar |
| `1` | Hay al menos una divergencia dura o una laguna declarada — o sólo blandas si se pasó `--strict` | «Las lecturas no convergen», y las preguntas detrás |
| `2` | La ejecución no produjo un veredicto utilizable: fichero ilegible o JSON malformado en `readings/`, menos de dos lectores, o ningún escenario que comparar | No hubo comparación: di qué faltó y no lo presentes ni como convergencia ni como divergencia |

**Un `0` no es un certificado de convergencia.** El código de salida dice si la ejecución falla; `converged` dice si las lecturas coinciden, y con divergencias blandas valen cero y falso a la vez. El informe trae los dos: el titular del veredicto y el recuento. Repítelos como están en vez de deducir uno del otro.

Si necesitas la salida en máquina, `--json` emite el mismo veredicto con las claves `version`, `converged`, `verdict` (uno de `converged`, `soft_only`, `diverged`, `errors`, `too_few_readers`, `no_scenarios`), `strict`, `exit_code`, `counts`, `divergences`, `gaps`, `attacks`, `advocate` (`absent`, `empty`, `listed` o `unreadable`), `decisions`, `decisions_source`, `decisions_pending`, `tool` (`name`, `version` y `script`: quién produjo el informe) y, cuando hubo problemas de lectura, `errors`.

**`decisions` es la unidad de la entrevista.** El script agrupa las divergencias que nacen de la misma ambigüedad —la misma lectura escrita en `effect` y en `side_effects` del mismo escenario (`same-reading-two-fields`), el mismo par de lecturas repetido en varios escenarios (`same-readings-across-scenarios`), o la misma política con cifras distintas en escenarios del mismo requisito (`same-policy-across-scenarios`: «1.468.135,00», «1.468.135.00» y «$ 1.500.000.-» son tres entradas de una sola decisión, y cada fila conserva su cifra)— y deja el resto como decisiones de un solo miembro (`single`). Cada decisión trae su `id`, sus `scenarios`, sus `fields`, los índices de sus `divergences`, su `hardness`, su `reason`, una `question` con sus `options`, sus `members` (una entrada por divergencia miembro, con `scenario`, `field`, `requirement_id`, `input`, `hardness` y sus `readings` literales), sus `resolutions` (por opción, de qué `reader` viene y qué `answers` anota en cada miembro; la opción de equivalencia no anota nada), y lo que el historial dice de ella: `status`, `previous`, `fingerprint` y `stale_reason`. El informe markdown trae cada decisión **una sola vez** en «Decisiones pendientes», con su matriz —escenario, entrada, lectura de cada lector, dureza— y su pregunta; las divergencias individuales van debajo, en «Evidencia por divergencia», sin pregunta. Y **la skill no agrupa preguntas por su cuenta**: si dos preguntas te parecen la misma y el script las trae separadas, se plantean separadas; **la agrupación la hace el script**, con criterios de conjuntos, para que no dependa del criterio de un modelo.

**El historial se pasa al script con `--decisions`** —o se deja que lo encuentre solo: por defecto lee el `decisions.json` que hay junto a `readings/`— y el script reconcilia antes de que preguntes nada. Cada decisión lleva una `fingerprint` estable (change, requisitos, escenarios, campos, pregunta, opciones y lecturas literales; nunca el `D-NNN`, que cambia de una pasada a otra) y un `status`: **las decisiones `answered` no se preguntan**; **las `stale` se vuelven a preguntar enseñando `previous`** y el `stale_reason` que explica qué cambió —las opciones, la pregunta, las lecturas, o que una equivalencia anterior no cerró una divergencia dura—; **en las `unclassified` se pide confirmar la respuesta antigua**, que es una respuesta escrita a mano de una versión anterior del plugin que nadie clasificó; y las `pending` se preguntan como siempre, enseñando `previous` si hubo una aclaración anterior. El veredicto y el código de salida no dependen del historial: una decisión dura respondida y no llevada al delta sigue sacando `1`, y el informe la enseña en «Decisiones ya respondidas» para que se vea que lo que falta es llevar la respuesta al delta, no contestar otra vez.

Y **no resumas ni reinterpretes el informe.** Las preguntas cerradas que escribe el script llevan las dos lecturas enfrentadas y sus opciones; se presentan al usuario con su texto, su orden y sus opciones tal como el script las emitió. No las agrupes por tu cuenta, no las priorices, no contestes ninguna y no añadas «esta probablemente sea menor»: la que te parece menor es la que nadie preguntará y la que aparecerá en producción.

Lo que sí haces: decir dónde está el informe (`.venoxia/changes/<id>/divergence.md`), dar el recuento del script, y luego plantear las preguntas como entrevista, que es el paso siguiente.

Cuando una divergencia es dura, el informe dice **por qué señal** lo es —su negación, su alcance, la cifra, o que el otro lector no registró ningún efecto— y el JSON lo lleva en la clave `signal`. Repítelo tal cual al presentar la pregunta: es lo que permite reconocer a simple vista un falso positivo del motor (dos lecturas que dicen lo mismo y la señal las enfrenta por una palabra) y contarlos después con `grep '"signal": "polarity"'` sobre los informes en JSON.

Los ataques del abogado del diablo aparecen en el informe pero **no** cuentan para el código de salida. Un ataque de severidad `high` con el script en `0` merece que lo pongas delante del usuario igualmente, señalado como lo que es: no bloquea el estado, pero es la clase de cosa que se descubre tarde.

## Paso 4b · La entrevista: una decisión por llamada

Las preguntas del informe —las entradas de `decisions` y las de `gap_questions`, en el JSON— se plantean al usuario con `AskUserQuestion`, **una decisión por llamada**, en el orden del informe, y se paran cuando el usuario lo pida. Una decisión de un solo miembro es una pregunta por llamada, como siempre; una agrupada es una sola llamada para todos sus escenarios. Contestarlas en bloque es lo que este paso viene a evitar: las últimas de una lista larga se contestan sin mirar, y la que se contesta sin mirar es la ambigüedad que llega al código. Y preguntar la misma cuatro veces produce lo mismo por el otro lado: la cuarta se contesta sin mirar.

Cómo se monta cada llamada:

- **La pregunta y las opciones son las del script, literales.** El texto de `question` va como pregunta; cada entrada de `options` va como una opción, con su texto tal cual, en su orden. No se reordenan por importancia y no se reescriben las opciones para que suenen mejor: el usuario tiene que elegir entre lo que los lectores leyeron, no entre tu resumen de lo que leyeron.
- **Antes de la llamada, en el mensaje, se explica la decisión raíz una sola vez y se listan los escenarios afectados**: el `detail` del informe —el párrafo que explica el desacuerdo y, en las duras, la señal que la hizo dura— y, en una decisión agrupada, su `reason` y la lista de escenarios que van a recibir la misma respuesta. Así la pregunta no llega sin contexto y el usuario sabe para cuántos sitios está decidiendo.
- **La descripción de cada opción sólo dice dos cosas**: de qué lector viene esa lectura (lo dice el propio informe) y qué tendría que decir el delta si se elige («el escenario pasaría a decir esto en su `THEN`»; «el delta tendría que decirlo explícitamente»; «las dos lecturas se dan por equivalentes y el delta no cambia»). Nada de recomendaciones, nada de «probablemente», nada de ventajas que el informe no diga: la skill no tiene voto sobre las lecturas, tampoco disfrazado de descripción.
- **El encabezado** es el título del escenario, recortado si hace falta; en una decisión agrupada, el primero de la lista y cuántos más.
- Con dos lectores ninguna pregunta del script pasa de cuatro opciones, que es lo que admite la herramienta. Con tres lectores alguna podría pasar; si ocurre, plantéala en el mensaje con todas sus opciones y pide la letra, y dilo como límite conocido.
- **Si la respuesta no vale para todos los escenarios de una decisión agrupada**, el usuario lo escribe —«en el de borrar, 404»— y se anota lo que escribió como `needs-clarification`; y si la aclaración es que la respuesta no vale para todos los miembros, la llamada siguiente se hace por miembro, uno por llamada, con la pregunta de su divergencia miembro, y cada uno anota su propio `answer`.

## Paso 4c · Anotar cada respuesta tal cual

Cada respuesta se **añade** a `.venoxia/changes/<id>/decisions.json` en cuanto llega, sin borrar las anteriores, con esta forma:

```json
{"version": 1, "change": "<id>",
 "decisions": [
   {"at": "2026-09-07T18:40:00Z",
    "decision": "D-001",
    "fingerprint": "<la fingerprint de la decisión, copiada del JSON>",
    "plugin_version": "0.6.0",
    "resolution": "selected",
    "scenario": "<título literal del escenario>",
    "field": "side_effects",
    "question": "<texto literal de la pregunta>",
    "options": ["<opción A literal>", "<opción B literal>"],
    "chosen": 0,
    "answer": "<texto literal de la opción elegida, o lo que el usuario escribió>"}
 ]}
```

- `scenario`, `question` y `options` se copian del informe; `chosen` es el índice de la opción elegida, o `null` si el usuario escribió su propia respuesta; `answer` es el texto que va a ir al delta; `decision` es el `id` de la decisión del script a la que pertenece la entrada, `fingerprint` su huella (es lo que la próxima pasada usa para no volver a preguntarla: el `id` no sirve, cambia), y `plugin_version` la versión anunciada al empezar.
- **Cada respuesta se clasifica en `resolution`**, y la clasificación es un juicio tuyo que hay que poder auditar, por eso se escribe: `selected` (eligió una opción con lectura de un lector), `equivalent` (eligió que las lecturas dicen lo mismo), `custom-resolved` (escribió su propia respuesta **y esa respuesta contesta la pregunta para todos los miembros**: dice qué pasa en cada escenario), `needs-clarification` (escribió algo que aporta contexto pero no contesta —«hay una moneda por defecto», «2 decimales»— o que sólo vale para parte de los miembros), o `changes-contract` (lo que escribió contradice el delta o el acta: no es una respuesta, es un cambio de contrato). Y sólo `selected`, `equivalent` y `custom-resolved` cierran una decisión: ante `needs-clarification` se hace una llamada más con la misma pregunta y la información aportada, para que conteste ya sabiendo lo que él mismo acaba de añadir; y ante `changes-contract` se dice qué contradice —qué escenario, qué requisito o qué línea del acta— y se remite a `/venoxia:specify` o a `/venoxia:charter` sin cerrar la decisión: se anota tal cual y queda `pending` hasta que el contrato cambie.
- **Una decisión agrupada se anota como una entrada por divergencia miembro**, con la misma clave `decision` y la misma `fingerprint`, una por escenario y campo, y cada entrada lleva **el `answer` que `resolutions` asigna a ese miembro** en el JSON del script: la lectura literal de ese lector en ese escenario, con su cifra, no un texto común diluido. Quien lleve las respuestas al delta va escenario a escenario y tiene que encontrar la suya sin deducirla de otra. La trazabilidad es por divergencia; la pregunta fue por decisión.
- **Una respuesta escrita a mano se anota con las palabras del usuario**, no con las tuyas mejoradas. Ese texto es el dato; tu reformulación es una interpretación que nadie ha aprobado.
- Si el fichero ya existe de una pasada anterior, se le añaden las entradas nuevas sin borrar las anteriores; cada entrada lleva su `at`, y ante dos entradas con la misma huella y el mismo miembro el script toma la última de la lista. Así una segunda divergencia sobre el delta corregido no pierde lo que ya se decidió, y tampoco lo confunde con lo nuevo. Las entradas de versiones anteriores, sin `fingerprint`, las migra el script solo: una opción elegida cuenta como respondida y una escrita a mano sale `unclassified`, para confirmarla.
- Si el usuario para la entrevista a medias, el fichero conserva lo contestado hasta ahí y la entrega dice cuántas decisiones quedan (`decisions_pending`), cuántas estaban ya respondidas por el historial y cuántas respondidas siguen bloqueando el código de salida porque su respuesta no ha llegado al delta.

## Paso 5 · El estado sólo cambia si pasan los dos

`change.json` pasa a `"state": "validated"` **sólo** cuando el validador y la divergencia salen los dos con `0`. Comprueba **los dos códigos de salida** antes de escribir nada.

1. Vuelve a ejecutar el validador ahora, aquí, aunque estuviera verde antes: el delta ha podido cambiar desde entonces y un estado `validated` apoyado en una ejecución vieja es una firma en falso.
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" --root "<raíz>" --change "<id>" --no-color
   ```
2. Toma el código de salida de `diff_readings.py` del paso 4.
3. Los dos `0` y sólo entonces: lee `change.json`, cambia **únicamente** la clave `state` a `"validated"` y vuelve a escribirlo dejando el resto de claves y sus valores intactos.
4. Si alguno no es `0`, el estado se queda como está y dices cuál de los dos lo ha bloqueado, con su código de salida y con lo que falta.

Nunca escribas `validated` porque el resultado «parece razonable», porque las divergencias sean pocas o porque el usuario tenga prisa. Ese estado es lo único que el guardián mira para dejar tocar el código; concederlo sin las dos condiciones vacía de sentido todo lo demás.

Con `validated` ya escrito, el siguiente paso tecleado es `/venoxia:verify`: antes de escribir el código de verdad, esa skill graba el oráculo en rojo —el test existe y falla, que es lo que demuestra que comprueba algo— y sólo cuando el código lo pone en verde vuelve a grabar y deja el change en `verified`. Esta skill no lo hace por su cuenta: `diverge` decide `validated`, nunca `verified`.

## Cuando el usuario responde las preguntas

Las respuestas se llevan al delta —`/venoxia:specify` o edición manual—, no aquí: esta skill no edita deltas. Quien las lleve copia al escenario el `answer` de `decisions.json` **literal**, sin reformularlo: la opción elegida es la lectura de un lector o las palabras del usuario, y en cuanto se «mejora» vuelve a ser texto que nadie ha leído a solas. Después se vuelve a pasar `/venoxia:validate` y `/venoxia:diverge`, con lecturas nuevas. Reutilizar las lecturas viejas contra un delta corregido no comprueba nada.

Y una advertencia honesta sobre el alcance del panel: que dos lectores converjan demuestra que **estos dos** leyeron igual, no que el texto sea unívoco. Es un suelo, no una prueba. Dilo si el usuario le atribuye más de lo que da, pero no lo uses para poner en duda un veredicto del script.
