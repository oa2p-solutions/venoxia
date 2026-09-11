# 2026-09-09-verify-confirm-green Proposal

## Why

`2026-09-09-technical-contract` dejó cinco requisitos en verde sin rojo previo:
comprueban comportamiento que el repositorio ya cumplía, y sus tests no pueden
fallar sin romperlo. D12 lo aceptó como adopción retroactiva y `/venoxia:verify`
pidió la confirmación explícita del usuario, que la dio. Pero esa confirmación
sólo vivió en la conversación: `V18` sigue avisando de los cinco, `--strict`
convierte el aviso en fallo, y `gate.py` —y con él `tools/check.py` y el
`pre-push`— quedan en rojo para siempre sobre un change legítimo. Una
confirmación que no deja rastro en el disco no es una confirmación que el
sistema pueda respetar: es la misma clase de evidencia que el rojo previo, y
tiene que grabarse donde se graba el rojo.

## What Changes

- `oracle.py --record` gana `--confirm-green <IDs>`: anota en el run grabado
  qué requisitos del change ha confirmado el usuario como verde sin rojo
  previo. Un ID que no está en el change, o que no sale verde en ese run, es
  un error de uso; sin `--record` también. El JSON de salida conserva sus ocho
  claves de primer nivel: la confirmación vive en `oracle.json`.
- `V18` deja de avisar de un requisito que algún run del historial trae como
  confirmado. Un verde sin rojo y sin confirmación sigue avisando igual.
- `/venoxia:verify`, tras la confirmación explícita del usuario, vuelve a
  grabar con `--confirm-green` nombrando esos requisitos, y sólo entonces
  escribe `verified`. Sin confirmación, nada cambia, como hasta ahora.

## Capabilities

### Modified Capabilities

- `oracle`: `R-ORC-017` nuevo (el flag) y `R-ORC-010` modificado (la skill graba
  la confirmación antes de escribir `verified`). `R-ORC-008` no cambia: las
  ocho claves de primer nivel siguen siendo las mismas.
- `validator`: `R-VAL-007` modificado (`V18` respeta la confirmación grabada).

## Impact

- El primer consumidor es el propio `2026-09-09-technical-contract`: al quedar
  este change en `verified`, se vuelve a grabar su oráculo con
  `--confirm-green R-TEC-001,R-TEC-002,R-TEC-003,R-TEC-005,R-TEC-006` —la
  confirmación que el usuario ya dio— y `validate.py --strict` vuelve a `0`.
  Hasta entonces no hay push: el `pre-push` fallaría en el gate.
- `oracle.json` gana una clave dentro de cada run que la lleve
  (`confirmed_green`); los runs anteriores no la tienen y se leen igual.
- `skills/verify/SKILL.md` cambia su paso «Verde sin rojo»;
  `tests/test_verify_skill.py` fija que nombre el flag.
- README: el flag en «Ejecutar el oráculo», la fila de `V18` y el ciclo de
  vida; `skills/validate/SKILL.md`, el remedio de `V18`.

## Confidence

- **La confirmación se graba en `oracle.json`, no en `change.json`** · `high`
  · es el fichero que `V18` ya lee y donde vive el resto de la evidencia del
  ciclo; decisión del usuario (2026-09-09) entre tres opciones.
- **Un ID confirmado en cualquier run del historial calla `V18`** · `high` ·
  una confirmación es un hecho que no caduca, igual que un rojo previo.
- **Rechazar un ID que no sale verde en el run** · `high` · confirmar el verde
  de algo que está en rojo es una contradicción, no una opción.
- **El resto de la propuesta** · `high` · mismo criterio que `oracle.py`:
  determinista, sin modelo, códigos 0/1/2.
