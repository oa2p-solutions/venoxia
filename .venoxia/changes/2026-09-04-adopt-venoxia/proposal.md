# 2026-09-04-adopt-venoxia Proposal

## Why

Un plugin que impone especificar antes de programar y no se especifica a sí
mismo no tiene autoridad: hoy quien quiere saber qué hace `validate.py` o
cuándo permite el guardián tiene que leer el código o el README, y nada
comprueba que las dos cosas sigan de acuerdo. Además, las capabilities de este
change son el terreno sobre el que se van a escribir como deltas de verdad los
ajustes que vienen después en esta misma entrega.

## What Changes

- El repositorio pasa a tener `.venoxia/charter.md` y `.venoxia/principles.md`,
  y los dos cumplen sus propios linters en `--strict`.
- Cuatro capabilities —`validator`, `charter-lint`, `guardian` y
  `divergence`— documentan, en el formato de Venoxia, comportamiento que ya
  existe y ya tiene test: no cambia nada observable para quien usa el plugin.
- Cada requisito nuevo apunta con `verifies:` a un test que ya pasaba, y ese
  test gana el comentario `# @covers <ID>` que lo declara su oráculo.
- `.venoxia/` deja de estar en `.gitignore`: a partir de aquí la
  especificación del propio proyecto se versiona como el resto del código.

## Capabilities

### New Capabilities

- `validator`: las 16 reglas de `scripts/validate.py` sobre requisitos.
- `charter-lint`: las 19 reglas de `scripts/charter_lint.py` sobre el acta.
- `guardian`: el allow/deny de `scripts/guardian.py` sobre una edición.
- `divergence`: la aritmética de `scripts/diff_readings.py` entre lecturas.

### Modified Capabilities

Ninguna: no hay comportamiento vivo previo que este change cambie.

## Impact

- El guardián empieza a vigilar este mismo repositorio: a partir de este
  change, editar `scripts/` sin un change validado al lado queda sujeto a las
  mismas reglas que le exige a cualquier proyecto que adopte el plugin.
- La capability `oracle` se deja fuera a propósito: nace como delta en un
  change posterior, así que su fila del acta no lleva todavía `spec.md`.
- No hay migración de datos ni ruptura de contrato: todo lo que describen las
  cuatro capabilities es comportamiento observable que ya estaba en producción
  y ya tenía cobertura.

## Confidence

- **Documentar comportamiento retroactivo con `confidence: high` o
  `medium`.** · `high` · el comportamiento está decidido, contrastado y tiene
  test desde antes de este change; no hay nada que apostar sobre él · no
  requiere revisión programada.
- **Usar la vía `direct` para escribir este change y su `.venoxia/`
  inicial.** · `high` · es la única forma de arrancar sin un change validado
  previo —no puede haber uno, porque `.venoxia/` no existe todavía— y queda
  anotada una sola vez en `.venoxia/drift/direct.log`, como marca el README en
  «El modelo de confianza del guardián».
