# 2026-09-15-charter-evidence Proposal

## Why

La sesión real de `/venoxia:charter` sobre Consolidar (hallazgos 5 y 6 de
`2026-09-15-divergencia-caso-real.md`) enseñó tres cosas que la entrevista
adaptativa de la 0.5.0 no cubría: la skill escribió una fila nueva de la tabla
con un `Done when` y un `Risk` que nadie confirmó y cambió un principio del
método por su cuenta, y lo único que lo dice es la entrega, que se pierde con la
conversación; juntó en una llamada dos preguntas dependientes; y nada de lo que
escribió dice qué versión del plugin corrió.

## What Changes

- La skill deja evidencia auditable en `.venoxia/charter-log.json`: una entrada
  por inferencia (propuesta, desenlace y palabras del usuario), una por pregunta
  y una por decisión que la skill tomó sola, todas con la versión del plugin.
- Una fila que la skill redacta —incluida `technical-contract`— se confirma con
  su contenido y su prioridad en una sola llamada antes de escribirse; dos
  preguntas dependientes nunca comparten llamada, y el test lo comprueba.
- La skill anuncia al empezar la versión que corre, leída del manifiesto.

## Capabilities

### Modified Capabilities

- `charter-lint`: la skill `/venoxia:charter` gana la evidencia, la confirmación
  de filas redactadas y el anuncio de versión.

## Impact

- Ningún cambio en `charter_lint.py`: el fichero de evidencia no lo lee el
  linter; es para quien audite la sesión.
- La entrega de la skill nombra el fichero y cuenta sus entradas.

## Confidence

- **Que una skill escriba fielmente lo que infirió y lo que el usuario dijo** ·
  `medium` · el registro lo escribe el mismo modelo que hizo la inferencia · se
  revisa cuando tres actas reales tengan su `charter-log.json` y se coteje con
  la transcripción de cada sesión.
- **El resto** · `high` · frases comprobables en el cuerpo de la skill.
