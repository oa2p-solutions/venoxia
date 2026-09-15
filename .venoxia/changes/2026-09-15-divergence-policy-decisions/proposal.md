# 2026-09-15-divergence-policy-decisions Proposal

## Why

La agrupación por decisión raíz de la 0.5.0 se probó sobre las lecturas reales
del change `review-fixes` de Consolidar y se quedó corta en cuatro sitios que
`2026-09-15-divergencia-caso-real.md` documenta: agrupa sólo lecturas idénticas
y deja fuera el escenario que cambia de cifra; el informe pide lo mismo dos
veces; las respuestas ya dadas se vuelven a preguntar; y dos respuestas que no
resolvían nada quedaron anotadas como decisiones cerradas. Además nada de lo que
escriben los scripts dice qué versión del plugin las produjo.

## What Changes

- Las lecturas ganan dos campos opcionales, `requirement_id` e `input`; las
  lecturas antiguas siguen valiendo.
- Un tercer criterio de agrupación, `same-policy-across-scenarios`: mismo campo,
  mismo requisito, y en cada lector la misma lectura una vez abstraídas las
  cifras, con las cifras literales conservadas en los miembros.
- Cada decisión lleva `members` (la matriz: escenario, entrada, lecturas,
  dureza) y `resolutions` (qué anota cada opción en cada miembro).
- El informe markdown tiene una única sección accionable, «Decisiones
  pendientes», y un apéndice de evidencia por divergencia; desaparecen
  «Divergencias duras», «Divergencias blandas» y «Decisiones agrupadas».
- El script lee `decisions.json` (`--decisions`, o el del change por defecto) y
  marca cada decisión `pending`, `answered`, `stale` o `unclassified`, con una
  huella estable que no depende del `D-00X`.
- La skill clasifica cada respuesta (`selected`, `equivalent`,
  `custom-resolved`, `needs-clarification`, `changes-contract`), sólo cierra con
  las tres primeras, no vuelve a preguntar lo ya respondido y anuncia la
  versión que corre.
- Los tres informes JSON llevan `tool` con la versión del manifiesto.

## Capabilities

### Modified Capabilities

- `divergence`: agrupación por política, informe único, reconciliación con el
  historial, clasificación de respuestas; `R-DIV-015` y `R-DIV-016` cambian.
- `technical-contract`: los informes declaran la versión que los produjo.

## Impact

- El esquema JSON versión 1 sólo crece (`R-TEC-006`): `decisions[].members`,
  `decisions[].resolutions`, `decisions[].status`, `decisions[].previous`,
  `decisions[].fingerprint`, `decisions[].stale_reason`, `decisions_source`,
  `decisions_pending` y `tool`. Nada se renombra.
- `counts`, `divergences`, `verdict` y `exit_code` no se mueven: las cifras de
  `evals/README.md` siguen valiendo; `diverge-root-decision` sigue puntuando.
- Los tests que fijaban la estructura antigua del informe cambian con
  `R-DIV-015` modificado.
- Un eval nuevo, `diverge-policy-decision`, con los tres escenarios de CLP de
  Consolidar, puntúa la agrupación por política y la reconciliación.

## Confidence

- **Que abstraer las cifras baste para reconocer la misma política en dos
  escenarios** · `medium` · es un criterio de forma, no de significado: dos
  lecturas que sólo cambian de número pueden ser dos políticas distintas ·
  se revisa cuando se haya usado sobre tres deltas reales y se cuente cuántas
  decisiones agrupadas recibieron una respuesta que no valía para algún miembro.
- **Que la huella por lecturas literales detecte todo cambio relevante del
  delta** · `medium` · un cambio del delta que no altere ninguna lectura no
  invalida la respuesta anterior, y eso es deliberado, pero también deja pasar
  un cambio de intención que los lectores no vieron · se revisa cuando una
  respuesta reutilizada resulte no valer para el delta corregido.
- **El resto** · `high` · forma del JSON y del informe, comprobables sobre
  fixtures.
