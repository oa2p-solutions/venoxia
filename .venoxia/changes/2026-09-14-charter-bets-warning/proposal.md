# 2026-09-14-charter-bets-warning Proposal

## Why

Un acta recién escrita para un producto que todavía no existe pasó el linter en
estricto con cero apuestas: `0 errores, 0 avisos`. El acta afirmaba así que el
proyecto no da nada por supuesto, cuando la premisa de la que colgaban sus dos
capabilities —que un agente lea un documento por su cuenta y construya con él— no
estaba escrita en ninguna parte.

`C15` no lo vio porque ninguna fila declaraba riesgo alto: mira las apuestas sólo
cuando hay un `high` en la tabla. Y la tanda E de `/venoxia:charter` —la que separa
lo observado de lo supuesto— no deja rastro en disco cuando se salta, así que nada
distingue un acta cuyo autor comprobó todo lo que afirma de otra a la que nadie hizo
la pregunta.

## What Changes

- El acta que no declara ninguna apuesta recibe un aviso que nombra la sección vacía
  y dice qué se está perdiendo.
- Un acta con riesgo alto y sin apuestas sigue recibiendo un solo aviso, el que ya
  daba `C15`, y no dos por lo mismo.
- Un acta con al menos una apuesta no cambia en nada.

## Capabilities

### Modified Capabilities

- `charter-lint`: el linter del acta gana una regla sobre la sección de apuestas.

## Impact

- `charter_lint.py --strict` pasa a salir con `1` sobre un acta sin apuestas, y con
  él `gate.py` de cualquier proyecto que la tenga así. Es el efecto buscado y es la
  clase de aviso que el proyecto prefiere: un falso positivo pesa menos que un falso
  negativo.
- El acta de este repositorio declara seis apuestas y no se ve afectada.
- La tabla de reglas del README pasa de diecinueve filas a veinte.

## Confidence

- **Que el aviso no se solape con `C15`** · `medium` · dos avisos sobre la misma
  sección vacía se leen como ruido, pero quien tiene riesgo alto y ninguna apuesta
  quizá merezca los dos · se revisa cuando alguien reciba el aviso sobre un acta
  suya y diga si le sobró o le faltó información.
- **El resto de la propuesta** · `high` · una sección declarada y vacía es un hecho
  comprobable en el fichero, sin juicio de por medio.
