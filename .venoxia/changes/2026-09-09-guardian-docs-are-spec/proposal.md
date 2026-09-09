# 2026-09-09-guardian-docs-are-spec Proposal

## Why

El guardián trata la documentación como código de producción. Con `.venoxia/`
en pie, escribir `README.md`, `TODO.md`, `CLAUDE.md` o cualquier `docs/*.md`
exige un cambio `validated` activo o la vía `direct`, y el diario de deriva
dice lo que eso ha costado: de las 193 líneas de `.venoxia/drift/direct.log`
—todas de la semana del 3 al 9 de septiembre de 2026—, **70 son markdown**
(`TODO.md` 41, `README.md` 16, `evals/README.md` 5 y otros). Es el 36 % de la
deriva registrada, y ninguna de esas líneas señala código escrito sin
especificación: señalan que el flujo no tiene puerta para la documentación.

El guardián existe para que el comportamiento se escriba antes que el código
que lo produce. El markdown no tiene comportamiento: ningún test de aceptación
lo ejecuta, ningún usuario del sistema lo observa, y reescribirlo entero no
cambia lo que el sistema hace. Vigilarlo no protege la premisa del plugin y sí
convierte la vía de escape en parte del flujo normal, que es lo que la
desactiva como señal.

Decisión de producto del usuario, 2026-09-09: todo `*.md` del proyecto es
documentación y el guardián lo permite siempre (D3 del plan para completar el
plugin). Este cambio va aparte de `2026-09-09-guardian-oracle-path`, que
también toca `guardian` y está en `verified`: aquél abrió el camino 5 (el
oráculo declarado en `specified`) y su ciclo rojo→verde ya está cerrado en
disco; reabrirlo borraría esa evidencia, y éste cambia otro camino, el 2.

## What Changes

- Cualquier ruta del proyecto cuyo nombre de fichero termine en `.md` se
  permite siempre, a cualquier profundidad y sin cambio que la respalde:
  `README.md`, `docs/guia/x.md`, `src/notas.md`.
- Lo que no es markdown no cambia: `.venoxia/**` y `prfaq/**` de primer nivel
  siguen siendo especificación; `src/prfaq/x.ts` sigue siendo código y sigue
  necesitando un cambio `validated` o la vía `direct`.
- Las reglas que hoy reconocen markdown por nombre o por directorio
  (`spec.md`, `proposal.md`, `delta*.md`, `specs/`, `docs/spec*/`) quedan
  subsumidas: todas eran casos particulares de «es markdown».

## Capabilities

### Modified Capabilities

- `guardian`: el camino 2 deja de distinguir entre markdown de especificación
  y markdown a secas. El anclaje a la raíz se conserva para lo que no es
  markdown, que es donde el rodeo `mkdir src/prfaq/` hacía daño.

## Impact

- El `README.md` («El modelo de confianza del guardián», camino 2) y
  `CLAUDE.md` describen la regla antigua y hay que actualizarlos.
- Tres tests de `tests/test_guardian.py` cambian de expectativa:
  `test_nested_specs_and_docs_directories_do_not_launder_markdown` esperaba
  `deny` sobre markdown bajo `lib/specs/`, `src/vendor/specs/`,
  `src/docs/specs/` y `a/b/docs/spec/`; `test_code_under_a_nested_spec_directory_is_denied`
  incluye `src/prfaq/notas.md` entre lo denegado. Los casos no-markdown de
  esos tests y `test_spec_filenames_travel_anywhere_but_only_as_markdown`
  siguen válidos.
- `TODO.md` (ignorado en `main`, `.gitignore:12`) deja de exigir la vía
  `direct` del cambio de adopción para editarse.
- Sólo `.md`. `.markdown` no está en la decisión y `.mdx` puede llevar código
  (JSX), así que los dos siguen siendo código para el guardián. La
  comparación del sufijo no distingue mayúsculas, como el resto de
  `is_spec_path`.
- Un proyecto cuyo producto sea el propio markdown —un sitio de documentación
  cuyo contenido son ficheros `.md`— pierde la vigilancia del guardián sobre
  ese contenido. Es el coste conocido de la decisión y la razón de su
  confianza.
- El caso más cercano es este mismo repo: en un plugin de Claude Code las
  skills, los agentes y las plantillas son markdown y son comportamiento. Lo
  señaló el abogado del diablo en la divergencia (severidad `high`) y el
  usuario decidió el 2026-09-09 mantener la regla tal cual: lo compensa que el
  comportamiento de cada skill ya está especificado con tests (`R-DIV-009/010`,
  `R-ORC-009/010`), así que el gate atrapa la regresión aunque el guardián no
  la frene, y la alternativa —una lista de rutas en `venoxia.json`— pondría al
  guardián a leer configuración en su camino más frecuente.

## Confidence

- **Todo `.md` es documentación, sin lista de nombres ni de directorios** ·
  `medium` · la alternativa —una lista de nombres de la raíz (`README.md`,
  `TODO.md`, `CLAUDE.md`)— vuelve a exigir la vía `direct` con el primer
  `docs/` nuevo; se eligió la regla general con la deriva de este repo delante
  · se revisa cuando el plugin se adopte en un proyecto cuyo producto sea
  markdown y haya que decidir si su contenido merece un cambio validado.
- **El anclaje a la raíz se conserva para lo que no es markdown** · `high` ·
  es el comportamiento vigente, con test, y el rodeo que impide sigue siendo
  real.
- **El resto de la propuesta** · `high` · la cifra de deriva está en el
  diario y se puede recontar.
