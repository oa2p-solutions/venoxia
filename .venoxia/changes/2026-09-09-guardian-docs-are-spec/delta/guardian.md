# guardian Delta

## ADDED Requirements

### R-GRD-008 · Markdown anywhere is documentation, never production code

El sistema DEBE permitir la edición de cualquier ruta del proyecto cuyo nombre
de fichero termine en `.md`, a cualquier profundidad y sin exigir ningún
cambio que la respalde, y seguir tratando como código de producción lo que no
es markdown fuera de `.venoxia/` y `prfaq/` de primer nivel.

#### Scenario: The README at the root, with nothing backing it
- **WHEN** no hay ningún cambio validado ni vía «direct» y se juzga una edición de «README.md»
- **THEN** la decisión es «allow» y la razón menciona «markdown»

#### Scenario: Markdown nested under a directory that is not a spec directory
- **WHEN** el cambio activo está en «draft» y se juzga una edición de «docs/guia/instalacion.md»
- **THEN** la decisión es «allow»

#### Scenario: Markdown inside a code directory that mimics a spec directory
- **WHEN** el cambio activo está en «draft» y se juzga una edición de «src/prfaq/notas.md»
- **THEN** la decisión es «allow»

#### Scenario: Code under a nested spec-named directory stays code
- **WHEN** el cambio activo está en «draft» y se juzga una edición de «src/prfaq/checkout.ts»
- **THEN** la decisión es «deny»

verifies:   tests/test_guardian.py
confidence: medium
  why:      en un proyecto cuyo producto sea el propio markdown, el guardián deja de vigilar su contenido; se decidió con la deriva de este repo delante (70 de 193 líneas eran documentación)
from:       README.md#el-modelo-de-confianza-del-guardián
