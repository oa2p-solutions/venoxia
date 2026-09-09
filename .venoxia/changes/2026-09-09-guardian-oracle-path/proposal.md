# 2026-09-09-guardian-oracle-path Proposal

## Why

El flujo manda escribir el fichero de test en el paso 5, con el change en
`specified`, y el guardián deniega exactamente esa escritura. Reproducido
sobre un proyecto de juguete con el guardián de hoy: un `Write` sobre
`tests/test_tec.py` con el cambio activo en `specified` cae en el último
camino de decisión y sale `deny`, con el mismo mensaje que recibe una
edición de código de producción.

El remedio que ofrece ese mensaje —`/venoxia:specify` y `/venoxia:validate`—
no desbloquea nada, porque es lo que ya se acaba de hacer, y el camino que sí
desbloquearía está cerrado en círculo: `/venoxia:diverge` no escribe
`validated` mientras `validate.py` no salga `0`, y `validate.py` no sale `0`
sin el test que existe (`V07`).

Quien lo sufre es el usuario para el que este plugin está diseñado: el que no
programa a mano. Escribiendo con un editor, el guardián ni se enteraría —
`Bash` y los editores no pasan por el hook. Con Claude Code, cada fichero de
test entra por `Write` y choca de frente. Hoy la única salida es poner
`"via": "direct"` en el `change.json` mientras se escribe el test, es decir,
convertir la vía de escape en parte del flujo normal.

## What Changes

- Con el cambio activo en `specified`, escribir un fichero que su delta
  declara en `verifies:` se permite.
- Cualquier otra ruta sigue denegada con el cambio en `specified`, incluidas
  las que parecen un test y que ningún `verifies:` nombra.
- El `deny` de un cambio en `specified` nombra los ficheros que el delta
  declara como lo siguiente que hay que escribir, y ofrece los comandos que
  de verdad desbloquean en lugar de mandar repetir `/venoxia:specify`.

## Capabilities

### Modified Capabilities

- `guardian`: `specified` deja de ser un estado sin puerta. El criterio de
  apertura no es la forma de la ruta, es que la especificación la haya
  declarado como su oráculo.

## Impact

- El contrato del guardián pasa de cinco caminos de decisión a seis. El
  `README.md` («El modelo de confianza del guardián») y `CLAUDE.md` los
  describen, y los dos quedan desfasados hasta que se actualicen.
- Nada cambia para un cambio en `draft`, `validated`, `verified` ni
  `archived`: los caminos anteriores deciden antes y siguen decidiendo igual.
- Un cambio con `"via": "direct"` sigue anotando en el diario de deriva toda
  edición, incluida la del oráculo declarado: el camino nuevo se evalúa
  después del de deriva, no antes.
- El guardián pasa a leer el **contenido** de `delta/*.md`, que hoy sólo
  cuenta y mide. Ocurre sólo cuando el estado es `specified` y ningún camino
  anterior ha decidido, así que el caso común —escribir la spec, editar con
  un cambio validado— no lee un byte más que hoy.
- La superficie de la vía de escape se reduce: escribir un test deja de ser
  motivo para tocar `"via": "direct"`.

## Confidence

- **El criterio es el vínculo declarado, no la forma de la ruta** · `medium` ·
  la alternativa era abrir la puerta a lo que parezca un test (`tests/`,
  `*.spec.*`, `*_test.*`), que es más barato y no exige leer el delta; se
  descartó porque concede permiso a una clase entera de rutas sin que nada en
  la especificación las respalde, y el vínculo doble spec↔test ya existe en el
  modelo · se revisa cuando el primer change ejercite la vía con un delta
  real y se sepa si nombrar el fichero en `verifies:` antes de escribirlo
  resulta natural o forzado.
- **Que el camino nuevo vaya después de la vía «direct»** · `high` · un
  cambio en `direct` está fuera del flujo entero, y anotar de más en el
  diario es el error que el proyecto ya declaró preferir: «un falso positivo
  pesa más que un falso negativo».
- **El resto de la propuesta** · `high` · el bloqueo está reproducido y la
  circularidad del remedio es comprobable leyendo las dos reglas implicadas.
