---
name: verify
description: "Envuelve el oráculo de Venoxia: graba el rojo antes de escribir el código, graba el verde después, y es la única skill autorizada a escribir «state»: «verified» en un change. Debe usarse cuando el usuario pida «verifica el cambio», «graba el rojo», «pasa el oráculo», «¿está en verde?», «corre los tests de la spec», o justo después de que el guardián haya dejado escribir el código de un change validado."
argument-hint: "el id del change a verificar (opcional)"
allowed-tools:
  - Read
  - Glob
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" *)
  - Write
---

# Venoxia · verificar

Change a verificar: **$ARGUMENTS**

`validate.py` comprueba que cada requisito **declare** su oráculo con `verifies:`; `oracle.py` sabe ejecutarlo y anotar `green`/`red`/`missing`/`timeout`. Lo que faltaba es quién decide, con esos dos datos, cuándo un change ha terminado de verdad — y quien lo decida tiene que ser el único que puede escribir `"state": "verified"`. Esa skill es ésta, con el mismo criterio que `/venoxia:diverge` aplica a `validated`: la aritmética la hace el script, tú lees el veredicto y lo presentas.

## Qué es tuyo y qué no

Tuyo: localizar el change, preguntar y escribir `.venoxia/venoxia.json` si falta, ejecutar `oracle.py` en el orden que manda esta skill, leer su código de salida, decidir si `verified` procede según las reglas de más abajo, y escribir esa única clave cuando proceda.

**Nunca editas tests ni código de producción.** Si el rojo dice que falta implementación, el siguiente paso es escribirla — en otra sesión de trabajo, no en ésta. Esta skill no toca ni un fichero bajo `src/`, ni el test que `verifies:` nombra: si lo hicieras, el rojo que acabas de grabar dejaría de ser honesto.

**Nunca reinterpretas el JSON.** El estado de cada requisito (`green`, `red`, `missing`, `timeout`) y el código de salida de `oracle.py` son el veredicto; no hay «este rojo en realidad no cuenta» ni «el test seguro que es flaky». La misma regla que gobierna `/venoxia:diverge` frente a `diff_readings.py`: tú no tienes voto sobre lo que el script ya calculó.

**No inventas nada que el proyecto no haya dicho.** El comando de test de `.venoxia/venoxia.json` lo escribe el usuario, nunca tú; si no existe, se pregunta, nunca se adivina.

## 1. Localiza el change activo

El change a verificar es el que trae `$ARGUMENTS`, si lo trae. Si no, busca con `Glob` sobre `.venoxia/changes/*/change.json` el que tenga `state` distinto de `archived` y `change.json` con `mtime` más reciente, y di cuál has elegido.

Lee su `state`:

- **`validated` o `verified`** — sigue al paso 2. Un change ya `verified` puede volver a pasar por aquí: es exactamente lo que ocurre cuando el segundo `--record` deja el run en verde tras el primero en rojo.
- **`draft` o `specified`** — no hay nada que verificar todavía: no hay divergencia comprobada, y verificar sin ella es construir sobre un contrato que ni el propio proyecto ha aceptado. Dilo, remite a `/venoxia:validate` y a `/venoxia:diverge`, y **para aquí**. No ejecutes `oracle.py` sobre un change que no ha llegado a `validated`.

## 2. Asegura `.venoxia/venoxia.json`

Con `Read`, comprueba si existe. Si existe, sigue al paso 3 sin tocarlo: el comando de test es del proyecto, no tuyo, y sobrescribirlo sin que nadie lo pida borraría una decisión que ya se tomó.

Si **no** existe, pregunta al usuario el comando con el que se corren los tests de este proyecto — el mismo que usaría a mano, con el marcador `{files}` donde van las rutas de `verifies:` — y el directorio (`cwd`) desde el que se lanza si no es la raíz. Con la respuesta, muestra el contenido exacto que vas a escribir antes de escribirlo:

```json
{"version": 1, "test_command": "<lo que ha contestado>", "cwd": "."}
```

Y escríbelo a partir de `${CLAUDE_PLUGIN_ROOT}/templates/venoxia.json` con `Write`. Sin respuesta del usuario, no lo inventes: dilo en la entrega y para aquí, porque `oracle.py` va a fallar con el error de uso que nombra este mismo fichero.

## 3. `--dry-run` primero, y enséñalo

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" --root "<raíz>" --change "<id>" --dry-run --no-color
```

Muestra la salida completa **antes** de ejecutar nada de verdad: es el comando exacto que se va a lanzar por requisito, y quien lee la entrega tiene que poder comprobarlo antes de que corra. Si aquí ya sale un error de uso (falta `venoxia.json`, o su `test_command` no trae `{files}`), repite el mensaje tal cual y para: no hay oráculo que ejecutar hasta que se arregle.

## 4. Ejecuta de verdad y graba

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/oracle.py" --root "<raíz>" --change "<id>" --record --json --no-color
```

Siempre con `--record`: sin historial no hay forma de comprobar, en el siguiente paso, que un verde estuvo antes en rojo. Siempre con `--json`: es lo que te permite leer `results`, `counts`, `all_green` y `all_red` sin adivinar nada de un informe de texto.

## 5. Lee el código de salida antes que nada

Igual que hace `/venoxia:validate`:

| Código | Significado | Qué haces |
|---|---|---|
| `0` | Todos los requisitos del change en `green` | Sigue al paso 6: puede que toque escribir `verified` |
| `1` | Al menos uno en `red`, `missing` o `timeout` | Sigue a «El rojo correcto», más abajo. No toques `change.json` |
| `2` | Error de uso: falta `venoxia.json`, el `test_command` no trae `{files}`, o el change no existe | No hay veredicto sobre el oráculo: reproduce el mensaje del script y corrige la invocación, no `change.json` |

Un `2` nunca se presenta como un rojo ni como un verde: el oráculo no llegó a correr.

### El rojo correcto (código `1`)

Con todos los requisitos del change en `red` o `missing` —el caso normal antes de escribir una sola línea de código—, dilo así: **«rojo correcto»**. Es la prueba de que el oráculo funciona, no un problema. El siguiente paso es escribir el código de producción, y esta skill no lo hace: **no toca `change.json`**, se queda en `validated` (o en `verified`, si venía de ahí, sin que nada cambie).

Si el rojo es parcial —unos requisitos en verde y otros en rojo—, el mismo criterio se aplica sin matices: mientras no estén todos en `green`, no hay nada que escribir en `change.json`, y lo dices con la lista exacta de qué falta.

### El verde con rojo detrás (código `0`, con historial)

Antes de escribir nada, lee `.venoxia/changes/<id>/oracle.json` con `Read` y mira su `runs`: una lista ordenada del más antiguo al más reciente. Para cada requisito que el último run trae en `green`, busca si **algún run anterior** (no el último) tiene ese mismo `requirement_id` en `red` o `missing`.

- **Todos lo tienen** — el ciclo rojo→verde está documentado en el disco. Lee `change.json`, cambia **únicamente** la clave `state` a `"verified"` y deja el resto de claves intactas. Dilo con todas las letras: «`<id>` pasa a "verified": el oráculo está en verde y el historial acredita que cada requisito estuvo en rojo antes».
- **Alguno no lo tiene** — sigue al párrafo de abajo: es «verde sin rojo», y ahí no se escribe nada todavía.

### Verde sin rojo (código `0`, sin historial que lo respalde)

Que el primer run de un requisito ya salga en verde es ambiguo entre dos historias muy distintas: se te olvidó grabar el rojo antes de implementar, o el test nunca comprobó nada y pasaría igual sin la implementación. **No escribas `verified` en este caso.** Presenta el aviso con el requisito exacto que no tiene un rojo previo, y pregunta al usuario, en una frase: *¿has visto fallar este test antes de que la implementación existiera?*

Sólo con una confirmación explícita del usuario —no un silencio, no un «probablemente»— escribes `"state": "verified"`, y lo dejas dicho en la entrega tal cual: «`<id>` pasa a "verified" por confirmación explícita del usuario: el run no tenía un rojo previo grabado». Sin confirmación, `change.json` se queda como está y lo dices.

## La entrega

Termina con un informe corto:

- El change verificado y su `state` antes y después de esta ejecución.
- El código de salida de `oracle.py` y el recuento (`green`/`red`/`missing`/`timeout`).
- Cuál de los tres casos de arriba aplicó, y por qué.
- Si escribiste `verified`: qué requisitos lo acreditan y con qué run de `oracle.json` (fecha de `ran_at`).
- Si no escribiste nada: qué falta exactamente para que la próxima ejecución sí pueda.
- El siguiente paso: escribir el código si el rojo era correcto, confirmar si el aviso pedía confirmación, o —con `verified` ya escrito— que el bucle corto sigue con `/venoxia:specify` de la siguiente capability.
