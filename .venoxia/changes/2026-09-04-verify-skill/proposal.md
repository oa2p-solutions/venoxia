# 2026-09-04-verify-skill Proposal

## Why

`validate.py` comprueba que cada requisito **declare** su oráculo con
`verifies:` y `scripts/oracle.py` sabe ejecutarlo y anotar `green`/`red`/
`missing`/`timeout`, pero nadie decide todavía **cuándo** ese verde basta
para dejar un change en `verified`. Hoy ese estado se escribiría a mano, sin
comprobar que hubo un rojo antes ni que el verde cubre todos los requisitos
del delta — exactamente el mismo hueco que tenía `validated` antes de que
existiera `/venoxia:diverge`.

## What Changes

- Existe `/venoxia:verify`, la única skill autorizada a escribir
  `"state": "verified"` en un `change.json`.
- Localiza el change activo en `validated` o `verified`; sobre `draft` o
  `specified` remite a `/venoxia:validate` y `/venoxia:diverge` y para.
- Si falta `.venoxia/venoxia.json`, pregunta el comando de test y lo escribe
  a partir de `templates/venoxia.json`, mostrando el contenido exacto antes
  de escribirlo.
- Ejecuta primero `oracle.py --dry-run` y enseña los comandos antes de
  lanzar nada; después ejecuta con `--record --json` y lee el código de
  salida antes de decir nada, con el mismo criterio que `/venoxia:validate`.
- Con exit `1` y todo el change en `red`/`missing`, dice «rojo correcto» y
  no toca `change.json`.
- Con exit `0` y un run anterior en rojo para cada requisito, cambia
  únicamente `state` a `verified`.
- Con exit `0` sin ningún rojo anterior, no escribe `verified`: presenta el
  aviso de «verde sin rojo» y sólo escribe el estado tras una confirmación
  explícita del usuario.

## Modified Capabilities

- `oracle`: gana el paso que decide `verified` a partir del historial de
  `oracle.json`, hoy inexistente. Ningún cambio en el esquema JSON de
  `oracle.py` ni en `validate.py`: `V17`/`V18` ya auditaban ese estado desde
  el lado del validador; esta skill es quien lo produce.

## Impact

- README: «Las cuatro skills» pasa a «Las cinco skills», con `verify` en
  quinto lugar, y el recorrido de la primera media hora deja de decir que
  la skill «no forma parte todavía de esta entrega».
- Ningún cambio en `guardian.py`: sigue abriendo la puerta al código sólo
  con `validated`, porque escribir el código es lo que convierte el rojo
  del oráculo en verde; exigir `verified` antes sería pedir el código antes
  de que pueda existir.
- Ningún cambio en el esquema JSON versión 1 de `validate.py` ni de
  `diff_readings.py`.

## Confidence

- **Preguntar confirmación explícita en vez de inferir el rojo de un
  histórico ausente** · `medium` · un `oracle.json` que nace ya en verde es
  ambiguo entre «se te olvidó grabar el rojo» y «el test estaba mal escrito
  y siempre pasó»; pedir confirmación es más barato que adivinar cuál de
  las dos es la verdadera · se revisa cuando el aviso de «verde sin rojo»
  se haya visto disparar sobre un change real y sepamos si la gente
  confirma sin mirar.
- **El resto de la propuesta** · `high` · mismo criterio que ya gobierna
  `/venoxia:validate` y `/venoxia:diverge`: la aritmética de rojo/verde vive
  en `oracle.py`, la skill sólo lee el código de salida y presenta.

## Pendiente

Esta sesión no dispone de la herramienta para despachar los lectores de
`/venoxia:diverge`, así que este change se deja en `specified`, con
`oracle.json` grabando el rojo (`skills/verify/SKILL.md` todavía no
existía) y después el verde (una vez escrita), en ese orden. El paso a
`validated` con `/venoxia:diverge` y a `verified` con `/venoxia:verify`
—sobre este mismo change, una vez exista la skill que este change
especifica— los hace la sesión principal.
