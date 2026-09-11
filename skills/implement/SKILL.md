---
name: implement
description: "Escribe el código de producción de un change de Venoxia ya validado, hasta que su oráculo sale en verde, sin tocar la especificación ni los tests que la verifican. Debe usarse cuando el usuario diga «implementa el change», «escribe el código», «haz que pase el oráculo», «pon el change en verde», «implementa <id>», o justo después de que /venoxia:verify haya grabado el rojo de un change validado."
model: opus
effort: xhigh
argument-hint: "el id del change a implementar"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - AskUserQuestion
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" *)
---

# Venoxia · implementar

Change a implementar: **$ARGUMENTS**

Es el paso central del flujo y hasta ahora era el único sin dueño: la spec está validada, el test existe y está en rojo, y alguien tiene que escribir el código que lo pone en verde. Esa skill es ésta. Su contrato es corto y no tiene excepciones: lee todo antes de editar nada, escribe sólo código de producción, el criterio de parada lo dicta `oracle.py` y la grabación del verde no es suya.

## Qué es tuyo y qué no

Tuyo: comprobar las precondiciones, leer el inventario completo, escribir y corregir código de producción, ejecutar el oráculo sin grabar, preguntar cuando una decisión no está escrita, y entregar el estado de cada requisito.

**La skill nunca edita `.venoxia/`.** Ni el delta, ni `change.json`, ni `oracle.json`, ni el acta, ni los principios. La única excepción es el `decisions.json` del propio change, donde anota las respuestas del usuario a las preguntas de esta skill: es **el único fichero de `.venoxia/` que escribe**, y en él **añade sin borrar lo que ya hay** —las decisiones que `/venoxia:diverge` recogió son el único registro de por qué el change llegó a `validated`, y se conservan intactas—.

**La skill nunca edita los oráculos:** ni ningún fichero que un `verifies:` nombre, **ni ningún otro fichero del directorio que contiene a cada uno de ellos, subdirectorios incluidos**: un helper, un fixture o un `conftest` vaciado ponen el test en verde sin implementar nada, y ese verde es el que `/venoxia:verify` grabaría como prueba. La prohibición no se limita al delta de este change: alcanza a todo fichero que cualquier `verifies:` de `.venoxia/` nombre, porque el oráculo de otra capability es un comportamiento ya contratado. Dos límites conocidos: un módulo que el test importe desde fuera de esos directorios no se puede acotar sin analizar imports, y en un proyecto con los tests junto al código (`src/checkout/total.test.ts`) la regla se reduce a los ficheros de test de ese directorio —los que comparten patrón con el que `verifies:` nombra—, porque de otro modo cubriría el propio código que hay que escribir.

**La skill nunca pasa `--record`** a `oracle.py`, ni `--dry-run`: `--record` es de `/venoxia:verify` —grabar el verde es afirmar que el ciclo rojo→verde ocurrió, y eso lo afirma quien lo audita, no quien escribe el código— y `--dry-run` no ejecuta nada, así que su `0` no dice nada del comportamiento.

**El guardián sigue vigilando.** Los hooks `PreToolUse` interceptan todo `Edit` y `Write` de la sesión, dentro de una skill también: **el guardián intercepta también las ediciones hechas desde la skill**. Que el change esté en `validated` es justo lo que le hace abrir la puerta al código; si la deniega, algo de arriba no se cumple, y el remedio es el que el mensaje del guardián dice, no rodearlo.

## 1. Precondiciones: sólo desde un change validado con un rojo grabado

Lee `.venoxia/changes/<id>/change.json`. Esta skill **sólo trabaja sobre un change en `validated`**: con `draft` o `specified` no hay contrato aceptado —remite a `/venoxia:validate` y `/venoxia:diverge`—; con `verified` no hay nada que implementar; con `archived`, menos.

Lee `.venoxia/changes/<id>/oracle.json` y mira su último run como lo mira `V17`: tiene que traer todos los requisitos del change, ninguno en `missing` y **algún requisito en `red`**. Si no existe, si trae **algún requisito del change en `missing`**, o si no cumple las tres cosas, se detiene sin editar nada y remite a `/venoxia:verify`: el rojo se graba **antes** de escribir código, y un test que todavía no existe (`missing`) no es un rojo, es un test que alguien tiene que escribir primero. Un run que no menciona a todos los requisitos tampoco vale: `missing` es una atribución del oráculo, y un requisito que el run no vio no está en ningún estado.

Con las dos precondiciones, sigue. Sin ellas, la entrega dice cuál falla y qué skill la resuelve, y aquí termina.

## 2. El inventario, antes de editar nada

En este orden, y **antes de editar nada**:

1. `.venoxia/changes/<id>/delta/*.md` — el contrato: cada requisito con sus escenarios es lo que el código tiene que cumplir, ni más ni menos.
2. `.venoxia/changes/<id>/decisions.json` — las respuestas literales del usuario en la divergencia. Una decisión anotada ahí gobierna la implementación aunque el delta no la repita palabra por palabra.
3. `.venoxia/principles.md` — los tres del método y los principios de dominio; los de dominio deciden los desempates que ningún requisito recoge.
4. `.venoxia/capabilities/<slug>/spec.md` de cada capability que el change toca — el comportamiento vivo que el delta modifica o al que se suma, para no romper lo que ya está contratado.
5. Los ficheros que cada `verifies:` del delta nombra — el contrato ejecutable. Se leen enteros: dicen exactamente qué va a comprobar el oráculo, y se leen para implementar contra ellos, nunca para editarlos.

## 3. Escribir el código, con el oráculo como único criterio

Escribe el código de producción con `Edit` y `Write` (`Write` crea los directorios padre que falten; borrar o mover un fichero se pide al usuario, no se hace). Después de cada tanda de cambios, ejecuta el oráculo **sin grabar**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" --root "<raíz>" --change "<id>" --json --no-color
```

Lee `results` y `all_green` del JSON. La skill **termina en cuanto el oráculo queda todo en verde**: `all_green: true`, código `0`. Ahí se para de escribir código, aunque se te ocurra una mejora: lo que el oráculo no pide no es de este change.

Tres paradas más, porque un bucle sin salida es peor que un rojo entregado:

- **Una decisión no escrita.** Si un requisito sigue en rojo y la causa es algo que ni el delta, ni `decisions.json`, ni los principios deciden —qué valor por defecto, qué ocurre en un caso que el escenario no cubre—, **no lo elijas en silencio**: se pregunta con `AskUserQuestion`, una pregunta por llamada, y la respuesta **se anota en `decisions.json`** con la misma forma que usa `/venoxia:diverge` (`at`, `scenario`, `question`, `options`, `chosen`, `answer`), añadiendo sin borrar. Si la respuesta **cambia el comportamiento observable** —hace falta un escenario o un requisito que el delta no tiene—, la skill se detiene y remite a `/venoxia:specify`: el delta va antes que el código, y un comportamiento pactado sólo en `decisions.json` es exactamente la conducta fuera de la especificación que Venoxia existe para impedir.
- **Sin progreso.** Se detiene cuando un intento **no cambia el estado de ningún requisito**, y también cuando el conjunto de estados repite uno ya visto en un intento anterior (poner `R1` en verde rompiendo `R2` y a la inversa es no avanzar). Entrega el rojo tal cual, con el diagnóstico.
- **El guardián deniega.** No se rodea: se entrega el mensaje del guardián y qué falta.

## 4. La entrega

Termina con un informe corto:

- El estado final: **cada requisito del change con su estado** en la última ejecución del oráculo (`green`, `red`, `missing`, `timeout`), con su ID.
- Todos **los ficheros tocados**, con ruta.
- Las decisiones que hubo que preguntar, con la respuesta literal y dónde quedó anotada.
- Cuál de las paradas aplicó: todo en verde, sin progreso, una respuesta que devuelve el change a `/venoxia:specify`, o una precondición que no se cumplía.
- **El siguiente paso**: con todo en verde, `/venoxia:verify`, que es quien graba el verde y escribe `verified`; con rojo, qué falta para que la próxima ejecución llegue al verde.
