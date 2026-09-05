# 2026-09-04-tdd-evidence Proposal

## Why

`scripts/oracle.py` ya ejecuta el test de cada requisito y deja su veredicto en
`oracle.json`, pero nada obliga a que ese veredicto se consulte antes de decir
que un change está terminado. Hoy `change.json` puede declarar
`"state": "verified"` sin que exista ningún `oracle.json`, o con uno cuyo
último run está en rojo: el estado miente y nada lo desmiente. Y al revés, un
requisito puede llegar a verde en su primer run sin haber pasado nunca por
rojo, que es la señal más barata de que el test no está comprobando nada —un
`assert True`, un mock que siempre acierta—. La mitad TDD del sistema
—«el test falla antes de que exista la implementación»— sigue siendo un
hábito de memoria en vez de una comprobación.

## What Changes

- Un quinto estado, `verified`, se añade al ciclo de vida del change:
  `draft → specified → validated → verified → archived`. Lo escribe
  `/venoxia:verify` (DEF-007), nunca `/venoxia:specify` ni `/venoxia:diverge`.
- `validate.py` gana `V17` (error): un change en `verified` sin un
  `oracle.json` legible cuyo último run esté en verde y cubra todos los IDs de
  su delta queda rechazado, nombrando el primer requisito que falta.
- `validate.py` gana `V18` (aviso): un requisito que llega a verde sin que
  ningún run anterior de ese mismo change lo tuviera en rojo se señala, uno
  por requisito.
- Ninguna de las dos reglas ejecuta ningún test: las dos leen `oracle.json`
  del disco, con el mismo criterio determinista que el resto del validador.

## Capabilities

### Modified Capabilities

- `validator`: dos requisitos nuevos, `R-VAL-006` y `R-VAL-007`, sobre las
  reglas `V17` y `V18`. El validador pasa de dieciséis a dieciocho reglas.

## Impact

- `guardian.py` no cambia: sigue abriendo la puerta al código en `validated`,
  nunca en `verified` —escribir el código es lo que convierte el rojo del
  oráculo en verde, así que exigir `verified` antes sería contradictorio—.
- El esquema JSON versión 1 de `validate.py` no cambia de forma: `V17` y
  `V18` son hallazgos con la misma forma que los dieciséis anteriores.
- Los cinco fixtures de `evals/` no declaran `oracle.json` ni `state:
  verified`, así que ninguna de las dos reglas se evalúa sobre ellos y sus
  cifras documentadas no se mueven (comprobado con
  `tests/test_eval_fixtures.py`, nuevo en este change).
- `README.md`, `evals/README.md` y `skills/validate/SKILL.md` recogen las dos
  reglas nuevas y el estado `verified`; `skills/diverge/SKILL.md` y
  `skills/specify/SKILL.md` nombran `/venoxia:verify` como el paso siguiente,
  aunque esa skill todavía no existe —la escribe DEF-007— y hasta entonces el
  comando no tiene qué ejecutar.

## Confidence

- **`V18` se evalúa sin mirar el `state` del change** · `medium` · la
  alternativa era limitarlo a changes `validated` o `verified`, pero la
  disciplina «el test falló antes de existir la implementación» importa
  igual en `specified`, que es cuando de verdad se escribe el test por
  primera vez · se revisa cuando un proyecto real dispare `V18` sobre un
  change en `draft` y el aviso no tenga sentido ahí.
- **El resto de la propuesta** · `high` · mismo criterio determinista que ya
  usan `V01`–`V16`: sin modelo, dos ejecuciones sobre el mismo árbol producen
  el mismo veredicto.

## Cierre

Divergencia pasada el 2026-09-05 desde la sesión principal con dos lectores
aislados y el abogado del diablo (`readings/`, `divergence.md`): 0 duras, 2
blandas de vocabulario, 0 lagunas. Validador y divergencia en `0`, así que el
change pasó a `validated`; `/venoxia:verify` volvió a grabar el oráculo en
verde y, con el rojo del 2026-09-04 en el historial, lo dejó en `verified`.
