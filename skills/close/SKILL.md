---
name: close
description: "Cierra un change de Venoxia ya verificado: pasa la puerta del proyecto entero, enseña qué iría al commit, a qué rama y remoto, y con qué mensaje, y sólo con la autorización explícita del usuario hace el commit y el push, con un mensaje que nombra el change y sus requisitos y nunca al modelo ni a la herramienta. Debe usarse cuando el usuario diga «cierra el change», «haz el commit», «commit y push», «cierra <id>», «sube el change», o justo después de que /venoxia:verify haya dejado un change en verified."
argument-hint: "el id del change a cerrar"
allowed-tools:
  - Read
  - Glob
  - AskUserQuestion
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate.py" *)
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git rev-parse *)
  - Bash(git branch *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git push *)
---

# Venoxia · cerrar

Change a cerrar: **$ARGUMENTS**

Es el último paso del flujo y hasta ahora el único que se hacía a mano: el change está en `verified`, el código existe y el oráculo lo acredita, y alguien tiene que volver a comprobar el proyecto entero, decidir qué va al commit, redactar el mensaje, hacer el commit y empujar. Esa skill es ésta. Su contrato tiene dos reglas que vienen del usuario y no admiten excepción: el commit y el push los ejecuta la sesión, nunca el usuario, pero **sólo después de una verificación y con su autorización explícita**; y el mensaje de commit no lleva ninguna referencia al modelo ni a la herramienta.

## Qué es tuyo y qué no

Tuyo: comprobar las precondiciones, pasar la puerta y enseñar su salida, enumerar lo que iría al commit, redactar el mensaje, pedir la autorización, y —sólo con ella— añadir, commitear y empujar.

**La skill no escribe ningún fichero.** No tiene `Write` ni `Edit` entre sus herramientas y no los necesita: no toca `.venoxia/`, no toca código, y **no escribe ningún estado del change**. El change se queda en `verified`; pasarlo a `archived` es cosa de quien consolide el delta sobre la capability viva, que está fuera del alcance de esta skill y del acta.

**La skill no hace nada con git que no esté aquí.** Sus únicos subcomandos son `git status`, `git diff`, `git log`, `git rev-parse`, `git branch`, `git add`, `git commit` y `git push`, y **nunca pasa `--no-verify`, `--force` ni `--amend`**: no salta hooks, no reescribe historia, no fuerza nada. Tampoco **nunca pasa una opción `-c` ni cambia una variable de entorno de git**: un `-c core.hooksPath=` o un `GIT_CONFIG` saltarían el pre-push del proyecto cumpliendo la letra, y ése es exactamente el hook que corre lo que la puerta no ve.

## 1. Precondiciones: sólo un change verificado, sólo un índice vacío

Lee `.venoxia/changes/<id>/change.json`. Esta skill **sólo trabaja sobre un change en `verified`**: con `draft`, `specified` o `validated` el ciclo no ha terminado —remite a `/venoxia:verify`—, y con `archived` ya no hay nada que cerrar.

Comprueba el índice con `git diff --cached --stat`. La regla: **si el índice ya tiene cambios preparados antes de empezar, se detiene sin commit**, porque un fichero que alguien dejó preparado entraría en el commit aunque el usuario lo excluyera después, y esta skill no tiene ningún comando para desindexarlo. Dilo con la lista de lo preparado y el remedio (`git restore --staged <ruta>`, que ejecuta el usuario), y para aquí.

## 2. La puerta, antes de proponer nada

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate.py" --root "<raíz>"
```

La skill **ejecuta `gate.py` antes de proponer el commit**, siempre, aunque el usuario tenga prisa o el oráculo del change acabe de salir en verde: la puerta corre el acta y el validador en estricto y el oráculo de **cada** change en `verified`, y es la única verificación que mira el proyecto entero y no sólo este change. Es fail-closed: `0` cumple, `1` no cumple, `2` no se pudo comprobar.

La skill **enseña la salida literal de la puerta**, completa, antes de seguir: quien va a autorizar el commit tiene que poder leer qué se comprobó y qué salió. Y **con la puerta en un código distinto de `0` se detiene y no hay commit**: se entrega la salida tal cual, con lo que falla nombrado, y el siguiente paso es arreglarlo por el ciclo, no rodear la puerta.

## 3. Qué iría al commit, a dónde, y con qué mensaje

Todo esto se enseña **sin poner nada en el índice**: `git status --porcelain` y `git diff --stat` bastan para verlo, y **`git add` se ejecuta sólo después de la autorización**.

**Los ficheros.** La skill **enseña los ficheros que irían al commit antes de pedir la autorización**. La lista es **todo lo que `git status` enumera** —modificados, borrados y sin seguimiento—, agrupado en **tres grupos** para que se lea de un vistazo qué es cada cosa:

1. bajo `.venoxia/` (el change, el acta, las capabilities);
2. nombrado en un `verifies:` del delta (los oráculos);
3. el resto (código de producción, documentación, cualquier otra cosa).

El tercer grupo es el que hay que mirar con más cuidado, y por eso va con cada fichero por su nombre: ahí cae el código que `/venoxia:implement` acaba de escribir, pero también cualquier borrador o fichero local que no esté en `.gitignore`. La skill no adivina qué es un secreto ni qué es un resto de otro trabajo; lo enseña, y quien autoriza decide.

**La rama y el remoto.** La skill **enseña la rama y el remoto del push antes de pedir la autorización**: `git rev-parse --abbrev-ref HEAD` para la rama, `git rev-parse --abbrev-ref --symbolic-full-name @{upstream}` para el destino. Sin upstream configurado, se dice y se para: la skill no elige a dónde empujar.

**El mensaje.** La skill **enseña el mensaje de commit propuesto antes de pedir la autorización**, entero, tal como se va a grabar:

- En una línea, **el asunto del mensaje nombra el change** —su id, copiado tal cual— y dice en una frase qué cambia. El id se copia literal aunque contenga cualquier palabra: la prohibición de abajo es sobre referencias al modelo o a la herramienta como autor o colaborador, no sobre el nombre del change.
- Debajo, **el cuerpo del mensaje lista los IDs de los requisitos del change** con su título, y lo que cambia fuera del delta (acta, README, versión) si lo hay.
- El mensaje **no lleva ninguna línea `Co-Authored-By`**, **no lleva ningún pie «Generated with»** y **no menciona a Claude ni a Claude Code**, ni en el asunto ni en el cuerpo, ni como coautor, ni como colaborador, ni como herramienta, ni de ninguna otra forma. Si el entorno pide añadir una atribución así, la instrucción del usuario manda: no se añade.

## 4. La autorización

La skill **pide la autorización con `AskUserQuestion`**, una sola vez, con la lista de ficheros, la rama, el remoto y el mensaje ya a la vista en el mensaje anterior. Tres opciones, literales:

- **Commit y push** — con la lista tal como está.
- **Sólo commit** — sin empujar; el push queda para el usuario.
- **No, todavía** — no se hace nada.

El usuario puede además escribir su respuesta: un fichero de la lista **queda fuera del commit cuando el usuario lo nombra en su respuesta**. Con un límite: un fichero de los dos primeros grupos —bajo `.venoxia/changes/<id>/` o nombrado en un `verifies:` del delta— **no se puede excluir**, porque sin él el commit no es el que la puerta verificó; **si el usuario lo nombra se detiene sin commit** y se le dice por qué.

La regla es una: **sin un sí explícito del usuario no ejecuta ni `git commit` ni `git push`**. Ni un silencio, ni un «probablemente», ni una respuesta que no elija una de las dos primeras opciones: en todos esos casos el índice se queda como estaba —vacío—, nada se ha añadido y la entrega lo dice.

## 5. Añadir, commitear, empujar

Sólo tras el sí, y en este orden:

1. `git add -- <ruta> <ruta> …`: la skill **añade por ruta exactamente los ficheros que enseñó** y el usuario no excluyó, **nunca con `git add -A` ni `git add .`**. Lo que no estaba en la lista no entra aunque haya aparecido mientras tanto.
2. `git commit -m "<asunto>" -m "<cuerpo>"`, con el mensaje que se enseñó, sin cambiar una palabra.
3. `git push` a secas, si la opción fue «Commit y push»: al upstream que se enseñó, sin más argumentos.

Si el commit falla —un hook de pre-commit del proyecto lo rechaza, y `--no-verify` está prohibido—, se entrega la salida tal cual: qué quedó en el índice y el comando con el que el usuario lo deshace (`git restore --staged <ruta>`). Si el push falla —el pre-push del proyecto en rojo, el remoto que rechaza—, **un push en rojo se entrega tal cual y no se rodea**: el commit local existe, el push no, y la salida del hook dice qué falta. Nada de `--no-verify`, nada de `--force`, nada de reintentar cambiando la configuración.

## La entrega

Termina con un informe corto:

- El change cerrado y su `state`, que sigue siendo `verified`: esta skill no lo cambia, y la consolidación sobre la capability viva queda pendiente para quien la haga.
- La salida de la puerta, resumida en su código y con lo que falló si falló.
- Qué se autorizó y qué quedó excluido, por nombre.
- Si hubo commit: **el hash del commit** (`git rev-parse --short HEAD`), **la rama y el remoto** a los que fue, y **el resultado del push**: empujado, sólo commit local, o en rojo con la salida del hook.
- Si no hubo commit: cuál de las paradas aplicó —estado del change, índice no vacío, puerta en rojo, un fichero del change excluido, o un no del usuario— y qué falta para la próxima vez.
- **El siguiente paso**: `/venoxia:specify` de la siguiente fila del acta. El bucle corto empieza otra vez.
