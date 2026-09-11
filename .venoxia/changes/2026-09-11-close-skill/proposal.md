# 2026-09-11-close-skill Proposal

## Why

Con `/venoxia:implement` el flujo tiene dueño en todos los pasos menos en el
último: cerrar el change. Hoy, con el change en `verified`, alguien tiene que
volver a comprobar el proyecto entero, decidir qué se commitea, redactar el
mensaje, hacer el commit y empujar, y nada de eso está escrito en ningún
sitio que la sesión lea al empezar. El resultado es el que se ve en el
historial de este mismo repositorio: cuarenta y ocho commits con una línea de
coautoría que el usuario no pidió y que la herramienta añade por defecto. El
usuario ha fijado dos reglas (2026-09-11): el commit y el push los ejecuta la
sesión de Claude Code, nunca él, pero sólo después de una verificación y con
su autorización explícita; y ningún mensaje de commit menciona al modelo ni a
la herramienta, ni como coautor, ni como colaborador, ni de ninguna otra
forma. Una regla que vive en la memoria de una sesión se cumple hasta que
alguien abre otra; una skill con test la cumple siempre igual.

## What Changes

- `/venoxia:close <change-id>` sólo trabaja sobre un change en `verified`;
  con cualquier otro estado se detiene sin ejecutar nada y remite a
  `/venoxia:verify`.
- Antes de proponer nada ejecuta `gate.py` sobre la raíz del proyecto y
  enseña su salida literal; con un código distinto de `0` se detiene y no
  hay commit.
- Enseña, sin haber puesto nada en el índice, la lista exacta de ficheros
  que irían al commit y el mensaje propuesto, que nombra el change y los IDs
  de sus requisitos, y pide la autorización con `AskUserQuestion`; sin un sí
  explícito no ejecuta `git commit` ni `git push`. La lista es todo lo que
  `git status` enumera, agrupado en tres grupos (bajo `.venoxia/`, en un
  `verifies:` del delta, y el resto: código y documentación), junto con la
  rama y el remoto del push; el usuario excluye un fichero nombrándolo en su
  respuesta. Tras el sí añade por ruta exactamente los ficheros no excluidos,
  nunca con `git add -A` ni `git add .` (dos ataques del abogado, `high`: la
  primera redacción excluía por defecto los ficheros sin seguimiento ajenos
  al change, y ahí cae justo el código que `/venoxia:implement` acaba de
  escribir).
- Nunca pasa una opción `-c` ni cambia una variable de entorno de git: un
  `-c core.hooksPath=` saltaría el pre-push cumpliendo la letra (ataque del
  abogado, `high`).
- Exige el índice vacío antes de empezar: un fichero ya preparado entraría
  en el commit aunque el usuario lo excluyera, y la skill no tiene comando
  para desindexarlo (ataque del abogado, `high`). Los ficheros del propio
  change —bajo `.venoxia/changes/<id>/` o en un `verifies:` del delta— no se
  pueden excluir: sin ellos el commit no es el que la puerta verificó
  (ataque del abogado, `medium`).
- Límite aceptado: un fichero sin seguimiento con secretos que no esté en
  `.gitignore` aparece en el grupo «el resto» con su nombre y sólo entra si
  el usuario no lo excluye; la skill no adivina qué es un secreto.
- El mensaje de commit no contiene ninguna referencia al modelo ni a la
  herramienta: ni `Co-Authored-By`, ni «Generated with», ni «Claude», ni
  «Claude Code», en el asunto ni en el cuerpo.
- Nunca pasa `--no-verify`, `--force` ni `--amend`: si el hook de pre-push del
  proyecto deja el push en rojo, la salida se entrega tal cual y no se rodea.
- No escribe ningún fichero: ni bajo `.venoxia/`, ni el estado `archived`
  —la consolidación sigue fuera del alcance del acta—, ni código.
- La entrega nombra el hash del commit, la rama y el remoto, el resultado del
  push y `/venoxia:specify` de la siguiente fila como siguiente paso.

## Capabilities

### New Capabilities

- `closing`: el cierre de un change verificado —verificación con la puerta,
  autorización y commit con push— con sus fronteras escritas.

## Impact

- Skill nueva `skills/close/SKILL.md` con `allowed-tools` acotado a `gate.py`
  y a los subcomandos de git que necesita (`status`, `diff`, `log`,
  `rev-parse`, `branch`, `add`, `commit`, `push`), sin `Bash` genérico y sin
  `Write` ni `Edit`; `tests/test_close_skill.py` fija su contrato.
- Acta: fila 9 `closing` y apuesta `B-006` (la puerta basta como verificación
  previa al commit). Sin `spec.md`: es la última fila, así que `C16` no tiene
  una capability viva detrás de ella.
- README: «Las seis skills» pasan a ser siete y el flujo gana el paso 10;
  `CLAUDE.md`, el diagrama del ciclo y la tabla de estados; la entrega de
  `/venoxia:verify` nombra `/venoxia:close` como siguiente paso;
  `plugin.json` y `marketplace.json`, versión `0.4.0` y keyword.
- Ningún script cambia. El guardián no interviene: no intercepta `Bash`, y
  la skill no hace ningún `Edit` ni `Write`.

## Confidence

- **Sin `Bash` genérico: la puerta es la verificación** · `medium` · la skill
  no puede lanzar la suite entera ni un build, sólo `gate.py`; se elige
  porque la puerta es el contrato declarado del proyecto y lo que no ve lo
  atrapa el hook de pre-push, si existe (`B-006`) · se revisa cuando el
  primer change de este repo se cierre con la skill.
- **La sesión ejecuta el commit y el push con autorización** · `high` ·
  instrucción literal del usuario (2026-09-11): «el git commit y git push
  debe hacerlo la sesión de Claude Code con mi autorización, después de una
  verificación del código».
- **Ningún mensaje menciona al modelo ni a la herramienta** · `high` ·
  instrucción literal del usuario (2026-09-11): «todos los commit deben
  excluir comentarios o referencias a CLAUDE o CLAUDE CODE, como coeditor,
  colaborador o algo referenciado».
- **El resto de la propuesta** · `high` · mismas fronteras y mismo patrón de
  test estructural que `implement` y `verify`.
