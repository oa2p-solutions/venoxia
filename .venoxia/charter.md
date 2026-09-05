# Venoxia · Acta del proyecto

## Purpose

Que una especificación deje de ser prosa y pase a ser un contrato que falla
en CI cuando miente.

## Users

### plugin-author · Autor del plugin
- **hoy:** revisa a mano que el README y las reglas coincidan.
- **con esto:** el repo se lo dice.

### adopting-team · Equipo que adopta Venoxia
- **hoy:** escribe specs que nadie contrasta con el código.
- **con esto:** cada requisito tiene su test y su estado rojo/verde.

## Capabilities

| # | Capability | Qué podrá hacer | Done when | Risk |
|---|---|---|---|---|
| 1 | `validator` | decidir si una especificación cumple su propio contrato, regla a regla | quien ejecuta `python3 scripts/validate.py --root . --strict` sobre un requisito sin `verifies:` ve el proceso terminar con código 1 y el hallazgo `V06` en la salida | low |
| 2 | `charter-lint` | decidir si el acta del proyecto tiene sus cinco secciones y sus criterios de cierre | quien ejecuta `python3 scripts/charter_lint.py --root . --strict` sobre un acta sin `Done when` en alguna fila ve el proceso terminar con código 1 y el hallazgo `C07` en la salida | low |
| 3 | `guardian` | impedir que se edite código de producción cuando no hay un change validado al lado | quien intenta un `Write` sobre código de producción sin un change `validated` con delta ve la edición denegada, con el comando exacto que la desbloquea | medium |
| 4 | `divergence` | cotejar dos lecturas aisladas del mismo delta y convertir cada desacuerdo en una pregunta cerrada | quien ejecuta `python3 scripts/diff_readings.py` sobre dos lecturas con `status_code` distintos ve el proceso terminar con código 1 y la divergencia marcada como dura | medium |
| 5 | `oracle` | traducir el resultado del `test_command` declarado en `venoxia.json` en verificado o no verificado | quien ejecuta `/venoxia:verify` sobre un change con oráculo ve el resultado del `test_command` convertido en verificado o no verificado, sin tener que leer la salida del test a mano | high |
| 6 | `ci` | hacer que la especificación falle en CI cuando miente, en el plugin y en los proyectos que lo adoptan | quien empuja una spec con un `SHALL` ve el job `self-spec` en rojo con el hallazgo `V14` en el registro del run | medium |

## Out of scope

- **Triaje por riesgo de tres vías (DIRECTA / NORMAL / CRÍTICA).** Diseñado y
  documentado, pero pospuesto hasta que el núcleo se use en una feature real.
- **PR/FAQ como documento de origen enlazable desde `from:`.** El bucle de
  promesas con fecha de revisión ya no hace falta aquí: lo cubre `## Bets`
  del acta, con su `revisit:` y su `fatal:`.
- **`trocear` / `construir` / `revisar` con git worktrees.** Mismo motivo que
  el triaje: pospuesto hasta que el núcleo se use en una feature real.
- **Diario de deriva con estadística acumulada que reescribe las
  plantillas.** Pospuesto hasta que el núcleo se use en una feature real.
- **Panel de salud de capabilities.** Se deriva del JSON que ya produce
  `validate.py`, así que será barato en cuanto haya specs reales que
  mostrar; hoy no las hay.
- **Consolidación automática del delta sobre la capability viva.** Pospuesto
  hasta que el núcleo se use en una feature real.

## Bets

### B-001 · Los lectores no comparten el mismo punto ciego

`/venoxia:diverge` despacha dos lectores aislados sobre el mismo delta, y los
dos comparten el mismo modelo subyacente. Damos por hecho que consignas
distintas bastan para que no converjan en el mismo error sistemático de
lectura; si convergieran, la capability `divergence` daría una falsa sensación
de haber contrastado algo que en realidad nadie miró dos veces.

confidence: low
  why:      no se ha medido si los dos lectores comparten sesgos sistemáticos
  revisit:  cuando los evals de ambigüedad hayan corrido diez veces con y sin consigna distinta
  fatal:    yes

### B-002 · El trace de la stdlib basta para medir cobertura

Suponemos que el módulo `trace` de la stdlib basta para medir qué líneas
ejecuta el `test_command` de la capability `oracle` cuando corre por
subproceso, sin tener que instrumentar código con dependencias externas.

confidence: low
  why:      no se ha probado todavía con el volumen real de tests que trae DEF-010
  revisit:  cuando DEF-010 produzca su primer informe
  fatal:    no

### B-003 · La matriz de Python pasa en los runners reales

La capability `ci` declara en `.github/workflows/ci.yml` una matriz con
Python 3.12, 3.13 y 3.14. Suponemos que la suite pasa en las tres sobre los
runners de GitHub Actions: aquí sólo se ha comprobado con 3.13 y 3.14, y no
se ha lanzado ningún run remoto todavía.

confidence: low
  why:      no hay Python 3.12 en esta máquina y no ha habido ningún run real de la matriz
  revisit:  cuando exista el primer run real de la matriz en GitHub Actions
  fatal:    no

### B-004 · El CLI valida el plugin sin credenciales en un runner limpio

El job `plugin-validate` de la capability `ci` da por hecho que
`claude plugin validate . --strict` funciona en un runner sin sesión de
Claude Code autenticada. Mientras no se sepa, el job lleva
`continue-on-error: true` para no bloquear el resto del workflow.

confidence: low
  why:      esta máquina ya tiene sesión autenticada, así que aquí no se puede comprobar
  revisit:  cuando exista el primer run real del job plugin-validate en un runner limpio
  fatal:    no
