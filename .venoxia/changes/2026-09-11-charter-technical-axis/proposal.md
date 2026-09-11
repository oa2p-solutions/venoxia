# 2026-09-11-charter-technical-axis Proposal

## Why

`/venoxia:charter` escribe hoy las convenciones técnicas que el usuario aprueba
como prosa en `principles.md`, bajo `## Convenciones técnicas`. Es la única
salida del plugin que afirma algo sobre el sistema sin oráculo: nadie
comprueba nunca que «el dinero va en enteros» o que «el tiempo se guarda en
UTC», y el propio `principles.md` de este repositorio llegó a mentir («probado
con 3.14» cuando la matriz real es 3.12–3.14). Desde `2026-09-09-technical-contract`
existe el sitio donde una decisión técnica sí se verifica —la capability
`technical-contract`, requisitos con `verifies:` y `runner:`— y el acta ya tiene
`## Bets` para lo que todavía no se puede verificar. Lo que falta es que la
entrevista reparta cada convención en uno de esos dos destinos y deje de
inventar un tercero. Y `/venoxia:specify` tiene el mismo hueco en pequeño:
cuando un cambio implica un juicio técnico que ningún principio gobierna, hoy
puede acabar como prosa en el delta.

## What Changes

- La tanda de convenciones técnicas de `/venoxia:charter` produce dos salidas:
  lo aprobado va a la capability `technical-contract` —una fila en la tabla del
  acta y el `/venoxia:specify` tecleado de la entrega, que escribirá los
  requisitos con `verifies:`—; lo que el usuario no decide hoy va a `## Bets`
  con el hecho que lo cierra.
- `principles.md` sale con los tres principios del método y los de dominio;
  la sección `## Convenciones técnicas` desaparece de la skill.
- `/venoxia:specify`, ante un juicio técnico que ningún principio ni requisito
  de `technical-contract` gobierna, lo lleva a `technical-contract` o a
  `## Bets`, nunca a prosa.

## Capabilities

### Modified Capabilities

- `charter-lint`: dos requisitos nuevos sobre las skills que escriben y leen
  el acta, `R-CHL-006` (charter) y `R-CHL-007` (specify), con el mismo patrón
  que `R-DIV-009`/`R-DIV-010` sobre `/venoxia:diverge`.

## Impact

- `skills/charter/SKILL.md` (Paso 4, Paso 8 y la entrega) y
  `skills/specify/SKILL.md` (Paso 1) cambian de texto; ningún script cambia.
- `charter_lint.py` no necesita regla nueva: `C17` sólo mira
  `## Principios de dominio`, y el fixture de `tests/test_charter_lint.py` que
  trae un `## Convenciones técnicas` de prueba sigue pasando.
- Los proyectos que ya tienen un `principles.md` con `## Convenciones técnicas`
  no se rompen: nada lee esa sección; la próxima entrevista no la vuelve a
  escribir.
- README: la descripción de `/venoxia:charter` en «Cómo se usa» y en la lista
  de skills.

## Confidence

- **Lo aprobado va al acta como fila `technical-contract` y a la entrega como
  `/venoxia:specify`, no como change escrito por la skill** · `high` · el acta
  sólo escribe acta y principios; los requisitos los escribe `/venoxia:specify`
  (Paso 10 de la propia skill).
- **Sin sección intermedia para «convenciones sin oráculo»** · `high` ·
  decisión D6 del plan: una decisión técnica sin oráculo posible es una
  apuesta o un principio de arbitraje, nunca un requisito ni prosa.
- **El resto de la propuesta** · `high` · sólo cambia texto de skills, con
  tests estructurales como los de `diverge` y `verify`.
