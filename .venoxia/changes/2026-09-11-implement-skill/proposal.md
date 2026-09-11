# 2026-09-11-implement-skill Proposal

## Why

«Implementa el change» es el único paso del flujo de Venoxia sin skill, y es
el 80 % de la jornada de quien usa el plugin como está diseñado: alguien que
dirige a Claude Code y no escribe el código a mano. Hoy ese paso depende de
que el agente encuentre el delta, lea `decisions.json`, respete
`principles.md`, sepa que no puede tocar la spec ni los tests, y sepa que el
criterio de parada es el oráculo y no su propia sensación de haber terminado.
Nada de eso está escrito en ningún sitio que el agente lea al empezar, así
que cada implementación lo redescubre o lo ignora. El guardián sigue
vigilando dentro de una skill —los hooks `PreToolUse` interceptan todo
`Edit`/`Write` de la sesión—, así que dar dueño al paso no abre ninguna
puerta: la cierra.

## What Changes

- `/venoxia:implement <change-id>` escribe el código de producción de un
  change en `validated` cuyo `oracle.json` ya tiene un rojo grabado; con
  cualquier otro estado se detiene y remite a `/venoxia:diverge` o a
  `/venoxia:verify`.
- Antes de editar nada lee el delta, las decisiones literales, los
  principios, las capabilities tocadas y los ficheros que `verifies:` nombra.
- Nunca edita `.venoxia/` ni ningún fichero que un `verifies:` nombre; nunca
  graba el oráculo (`--record` es de `/venoxia:verify`); ejecuta `oracle.py`
  sin grabar hasta que sale `0`, y ahí para.
- Una decisión no escrita que deja un requisito en rojo se pregunta al
  usuario y se anota en `decisions.json`; no se elige en silencio.
- La entrega nombra cada requisito con su estado, los ficheros tocados y
  `/venoxia:verify` como siguiente paso.

## Capabilities

### New Capabilities

- `implementation`: el paso central del flujo —escribir el código de un
  change validado hasta que su oráculo sale en verde— con sus fronteras
  escritas.

## Impact

- Skill nueva `skills/implement/SKILL.md` con `allowed-tools` acotado (sin
  `Bash` genérico); `tests/test_implement_skill.py` fija su contrato.
- README: el flujo de «Empezar un proyecto desde cero» pasa a decir quién
  hace cada paso (el usuario contesta, Claude Code escribe test y código, los
  scripts deciden) y el paso 8 es `/venoxia:implement`; «Las cinco skills»
  pasan a ser seis; se escribe que el guardián intercepta también las
  ediciones hechas desde una skill. `CLAUDE.md`, el diagrama del ciclo.
  `plugin.json`, `keywords`.
- Acta: fila 8 `implementation` y apuesta `B-005` (el oráculo basta como
  criterio de parada). Ni `technical-contract` ni `implementation` ganan
  `spec.md`: son las dos últimas filas del acta, así que `C16` no tiene una
  viva detrás de ellas, y `gate.py` rechaza un `spec.md` sin requisitos.
- Ningún script cambia.

## Confidence

- **Sin `Bash` genérico: el criterio de parada es el oráculo** · `medium` ·
  un comando a ojo es justo lo que el oráculo sustituye · se revisa cuando el
  primer change real se implemente con la skill y se cuente cuántas veces
  hizo falta correr algo fuera de `oracle.py` (`B-005`).
- **La skill escribe código** · `high` · decisión D9 del plan (usuario,
  2026-09-09): la regla «ninguna skill toca código» protege que spec y código
  no nazcan en el mismo impulso, y aquí la spec ya está validada y congelada.
- **El resto de la propuesta** · `high` · mismas fronteras que ya tienen
  `verify` y `diverge`, con tests estructurales del mismo patrón.
