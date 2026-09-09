# 2026-09-09-oracle-named-runners Proposal

## Why

`.venoxia/venoxia.json` admite un único `test_command` para todo el proyecto,
y ese comando exige el marcador `{files}`. Basta para el eje funcional —cada
requisito nombra un fichero de test y el oráculo lo ejecuta—, pero deja fuera
del contrato todo lo que se verifica con otro comando: la cobertura
(`python3 tools/coverage.py`), que no recibe ficheros y corre sobre el árbol
entero, o cualquier comprobación que no sea «lanza la suite sobre esta ruta».
Hoy esas decisiones técnicas viven como prosa en `principles.md`, sin oráculo,
y `principles.md` ya miente en una de ellas. La conversación de visión del
2026-09-08 y el plan que la sigue (`PLAN.md`, C3) fijaron que el eje técnico
entra al contrato con el **mismo formato** que el funcional (D4) y sin ningún
«runner: none» (D6): un requisito técnico es un requisito EARS con su
`verifies:`, y lo único que le falta al oráculo para ejecutarlo es poder
elegir el comando por requisito.

## What Changes

- `venoxia.json` gana una clave opcional `runners`: un objeto de runners con
  nombre, cada uno con su `command` y, si hace falta, su `cwd`.
- Un requisito puede declarar `runner: <name>` en su bloque de metadatos y el
  oráculo ejecuta ese runner para él. Sin `runner:`, se usa el `test_command`
  como hasta ahora.
- El `command` de un runner con nombre puede no llevar `{files}`: entonces
  corre tal cual, y el `verifies:` del requisito es sólo el ancla del
  `@covers`. El `test_command` sigue exigiendo `{files}`.
- Un `runner:` que nombra algo que `venoxia.json` no declara es un error de
  uso del oráculo: código `2`, nada ejecutado, nada grabado. Nunca un rojo
  falso.
- Cada elemento de `results` del JSON del oráculo (y del historial
  `oracle.json`) dice qué runner lo produjo: nombre, comando resuelto y
  directorio de trabajo. Las claves de primer nivel no cambian.
- `validate.py` gana la regla `V19`: un requisito que declara `runner:` sin
  que `venoxia.json` lo declare es un error, y se ve antes de ejecutar nada.

## Capabilities

### Modified Capabilities

- `oracle`: cuatro requisitos nuevos, `R-ORC-013` a `R-ORC-016`. Ninguno de
  los doce existentes cambia de redacción: `R-ORC-005` sigue exigiendo
  `{files}` al `test_command`, `R-ORC-008` conserva sus ocho claves de primer
  nivel y una sola invocación por requisito.
- `validator`: un requisito nuevo, `R-VAL-008`, la regla `V19`. `runner` pasa
  a ser una clave reconocida del bloque de metadatos, así que deja de
  disparar el aviso `P02` del parser.

## Impact

- Compatible hacia atrás: un `venoxia.json` sin `runners` y un delta sin
  `runner:` se comportan byte a byte como hoy, salvo la clave nueva `runner`
  dentro de cada elemento de `results`. Ningún fixture de evals usa
  `runner:`, así que ninguna cifra de `evals/README.md` debería moverse.
- El esquema JSON del oráculo sigue en versión 1: se añade una clave dentro
  de `results[i]`, no se renombra ni se quita ninguna.
- `gate.py` no necesita ningún paso nuevo: ya ejecuta el oráculo por change
  `verified` (D8). Conserva un límite conocido y preexistente: exige
  `test_command` aunque haya `runners`.
- La tabla del README pasa de 18 a 19 reglas; `tests/test_docs_sync.py` exige
  la fila nueva también en la tabla de remedios de `skills/validate/SKILL.md`.
- `tests/test_parser.py` fija la tupla exacta de `META_KEYS` y cambia de
  expectativa al sumar `runner`.
- El primer consumidor real es C4 (`technical-contract`), que declarará
  `runners.coverage` en el `venoxia.json` de este repo.
- Cuando un runner corre en un `cwd` distinto de la raíz, `{files}` recibe las
  rutas de `verifies:` reescritas en relación a ese `cwd` (decisión del
  usuario, 2026-09-09, ante el ataque del abogado del diablo sobre
  `R-ORC-013`: pegadas tal cual no existirían desde allí y un runner que sale
  con `0` sin ficheros daría un verde falso). Con `cwd: .` nada cambia.
- Límite aceptado (decisión del usuario, 2026-09-09, ataque `high` sobre
  `R-ORC-014`): un runner sin `{files}` corre tal cual, así que un `command`
  que no ejecuta nada —`true`— pone en verde lo que lo declare. El oráculo no
  puede saber qué hace un comando; es la misma clase de límite que el README
  ya declara para `test_command`, y quien declara el runner firma que
  verifica algo. Se escribe en el README junto a aquél.
- Límite aceptado (ataque `medium` sobre `R-VAL-008`): `V19` mira sólo los
  runners que algún requisito declara; un bloque `runners` mal formado que
  nadie usa lo denuncia el oráculo con código `2`, no el validador.
- Un `cwd` de runner «existe en disco» cuando es un directorio: un `cwd` que
  apunta a un fichero regular es el mismo error de uso (ataque `medium` de la
  segunda ronda sobre `R-ORC-015`; mismo criterio que ya aplica el `cwd`
  global). Y «`command` no vacío» se comprueba sin espacios alrededor.

## Confidence

- **Elegir el runner por requisito con `runner:` y que `test_command` siga
  siendo el de por defecto** · `high` · es la decisión D7 del plan, cerrada
  tras la conversación de visión; es el único mecanismo nuevo y no rompe nada
  existente.
- **Un runner con nombre puede no llevar `{files}`** · `high` · D7 lo dice
  con todas las letras; sin ello la cobertura no se puede declarar como
  runner.
- **Un runner no declarado es código `2`, no un rojo** · `high` · el mismo
  criterio que ya rige `R-ORC-005` y `R-ORC-011`: lo que no se pudo mirar no
  es un veredicto.
- **La forma de `results[i].runner`: `name` (`null` para el `test_command`),
  `command` resuelto y `cwd`** · `medium` · las tres claves y el `null` los
  eligió Claude, no el usuario; nadie las lee todavía · se revisa cuando
  `gate.py` o `/venoxia:verify` lean `runner.name` por primera vez.
- **El resto de la propuesta** · `high` · comportamiento decidido con el mismo
  criterio que ya rige `oracle.py` y `validate.py`: determinista, sin modelo,
  códigos 0/1/2.
