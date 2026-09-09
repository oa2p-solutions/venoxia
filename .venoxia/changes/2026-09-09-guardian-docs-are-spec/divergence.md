# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-09-guardian-docs-are-spec/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 4
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 0

## Veredicto

**Las lecturas casi convergen.** 3 divergencias blandas sobre los 4 escenarios: el desacuerdo puede ser sólo de vocabulario, así que confírmalo antes de implementar. Las blandas por sí solas no hacen fallar la ejecución. Esta ejecución sale con código 0.

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The README at the root, with nothing backing it

El lector A describe el efecto como «permite la edición del README sin exigir change»; el lector B describe el efecto como «permite la edición y la razón menciona markdown». Similitud de contenido 0.25, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The README at the root, with nothing backing it» es la correcta?**
- (A) «permite la edición del README sin exigir change»
- (B) «permite la edición y la razón menciona markdown»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Markdown nested under a directory that is not a spec directory

El lector A describe el efecto como «permite editar el markdown aunque el change esté en draft»; el lector B describe el efecto como «permite la edición del markdown anidado». Similitud de contenido 0.29, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Markdown nested under a directory that is not a spec directory» es la correcta?**
- (A) «permite editar el markdown aunque el change esté en draft»
- (B) «permite la edición del markdown anidado»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: Markdown inside a code directory that mimics a spec directory

El lector A describe el efecto como «permite editar el markdown pese a estar bajo ruta tipo prfaq»; el lector B describe el efecto como «permite la edición del markdown pese al nombre de carpeta». Similitud de contenido 0.30, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «Markdown inside a code directory that mimics a spec directory» es la correcta?**
- (A) «permite editar el markdown pese a estar bajo ruta tipo prfaq»
- (B) «permite la edición del markdown pese al nombre de carpeta»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-GRD-008 — El requisito afirma que todo `.md` es documentación «never production code» y ordena permitir su edición sin cambio que la respalde; en un plugin de Claude Code el comportamiento ejecutable vive en markdown (`skills/*/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `templates/*.md`), así que la implementación literal deja reescribir la lógica del producto sin acta, sin delta, sin lectores y sin oráculo: el guardián deja de vigilar exactamente el artefacto que decide qué hace el sistema.
- **[medium]** R-GRD-008 — «Cualquier ruta del proyecto cuyo nombre de fichero termine en `.md`, a cualquier profundidad y sin exigir ningún cambio que la respalde» incluye `.venoxia/changes/<id>/delta/*.md` y `.venoxia/charter.md`: la implementación literal permite reescribir el delta de un change ya `validated` o `verified` en cualquier momento, de modo que el contrato que firmaron los dos lectores y que el oráculo dio por verde puede cambiar debajo sin que nada lo detecte.
- **[medium]** R-GRD-008 — Los escenarios sólo observan `allow` y que la razón mencione «markdown», y el requisito no exige registrar nada: una implementación permite cada edición de markdown sin anotarla en `.venoxia/drift/direct.log` ni en ningún otro sitio, dejando ciega justamente la medición de deriva (70 de 193 líneas) con la que este cambio se justifica.

## Escenarios que convergen · 1

- Code under a nested spec-named directory stays code
