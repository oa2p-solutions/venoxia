---
name: validate
description: "Ejecuta el validador determinista de Venoxia sobre las especificaciones del proyecto y presenta el veredicto agrupado por severidad, con el remedio de cada error delante. Debe usarse cuando el usuario pida «valida la spec», «pasa el validador», «¿está verde la especificación?», «comprueba los requisitos», «revisa el delta», o justo después de escribir o modificar cualquier fichero bajo .venoxia/."
disable-model-invocation: false
allowed-tools:
  - Read
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" *)
  - Bash(python3 *)
---

# Venoxia · validar

`validate.py` es la autoridad. Esta skill no juzga la especificación: la ejecuta y hace legible lo que el script ya ha dictado.

## Qué es tuyo y qué no

Tuyo: ejecutar el script, agrupar los findings por severidad, poner los errores delante con su remedio, y dejar el veredicto claro en la primera línea.

No tuyo, en ningún caso:

- **Matizar el veredicto.** Si el script sale con código `1`, la especificación **no** cumple el contrato. No existe «casi verde», «son detalles menores» ni «esto en realidad no debería contar». Dilo como es.
- **Reclasificar findings.** La severidad la fija la regla, no tú. Un error no baja a aviso porque parezca inofensivo, y un aviso no sube a error porque te inquiete.
- **Descartar findings.** Si crees que uno es un falso positivo, ponlo por escrito **después** del informe completo, como comentario tuyo y marcado como tal, sin sacarlo del recuento ni cambiar el veredicto.
- **Arreglar los ficheros.** Esta skill sólo lee. Para corregir, el camino es `/venoxia:specify` o la edición manual del delta; después se vuelve a validar.
- **Inventar findings.** Todo lo que presentes sale del JSON del script. Ni una regla más.

## 1. Localiza la raíz del proyecto

La raíz es el directorio que contiene `.venoxia/`. Normalmente es el directorio de trabajo; si no lo es, sube por los padres hasta encontrarlo. Si no aparece `.venoxia/` en ningún nivel, el proyecto no ha adoptado Venoxia: el script lo dirá y saldrá con `0`. Repite ese mensaje tal cual y no lo interpretes como «la especificación está verde», porque no hay especificación.

## 2. Ejecuta el script

Siempre con `--json` y `--no-color`: el JSON es lo que te permite agrupar, y el color estorba cuando la salida se cita.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" --json --no-color --root "<raíz>"
```

Flags que se pasan sólo cuando corresponde:

| Flag | Cuándo |
|---|---|
| `--change <id>` | El usuario nombra un change concreto, o acaba de trabajar sobre `.venoxia/changes/<id>/` |
| `<PATH>...` | El usuario nombra ficheros o directorios concretos; sustituyen al descubrimiento automático |
| `--strict` | El usuario pide que los avisos cuenten como fallo, o se está validando para CI |
| `-q`, `--quiet` | El usuario sólo quiere el resumen |

Sin `--change` ni rutas, el script descubre y valida todo lo que hay bajo `.venoxia/`.

## 3. Lee el código de salida antes que nada

| Código | Significado | Qué dices |
|---|---|---|
| `0` | Conforme | «La especificación cumple el contrato.» |
| `1` | **No conforme** | Lo dices en la primera línea, sin adornos ni consuelo |
| `2` | Error de uso (ruta inexistente, flag inválido) | No hay veredicto sobre la spec: reproduce el mensaje de error del script y corrige la invocación |

Un `2` nunca se presenta como si la especificación hubiera pasado o fallado: significa que el validador no llegó a juzgarla.

Si la salida no es JSON parseable (el script murió antes de emitirlo), vuelve a ejecutar sin `--json`, muestra el texto crudo tal cual y di que no pudiste agrupar.

## 4. Presenta el resultado

El JSON tiene esta forma (esquema versión 1):

```json
{"version":1,"ok":false,"strict":false,"root":"/abs/path",
 "counts":{"error":2,"warning":1,"requirements":12,"capabilities":2,"deltas":1},
 "findings":[{"rule":"V06","severity":"error","message":"…","file":"…","line":14,
              "requirement_id":"R-CHK-014","hint":"…"}],
 "budget":{"low":1,"total":12,"ratio":0.083,"limit":0.3,"ok":true}}
```

Formato de salida, en este orden:

1. **Veredicto y recuento**, en una línea:
   `CONFORME · 0 errores, 1 aviso · 12 requisitos en 2 capabilities, 1 delta`
   o
   `NO CONFORME · 2 errores, 1 aviso · 12 requisitos en 2 capabilities, 1 delta`
2. **Errores**, primero y completos. Uno por entrada, con la regla, la ubicación, el requisito, el mensaje y el remedio:

   ```
   1. V06 · .venoxia/changes/x/delta/checkout.md:14 · R-CHK-014
      Falta «verifies:»: el requisito no declara cómo se comprueba.
      → Añade «verifies: ruta/al/test» y marca el test con «@covers R-CHK-014».
   ```

   El remedio es el campo `hint` del finding, literal. Si el finding no trae `hint`, usa la tabla de remedios de más abajo y no improvises nada que no esté en ella.
3. **Avisos**, después, con el mismo formato. No los escondas ni los resumas en un «además hay 3 avisos»: se listan.
4. **Presupuesto de incertidumbre**, una línea, siempre que haya requisitos:
   `Presupuesto de incertidumbre: 1 de 12 requisitos en «low» (8,3 % · límite 30 %) — dentro`
   Si `budget.ok` es `false`, esa línea va pegada al error `V11`, no al final.
5. **Qué hacer ahora**, dos o tres líneas como mucho: los ficheros que hay que tocar y el comando para volver a validar. Nada de planes largos.

Mantén el orden de findings que trae el JSON dentro de cada grupo: ya viene ordenado por fichero, línea y regla, y es determinista. Si hay más de veinte findings de la misma severidad, muestra los veinte primeros completos y di cuántos quedan y en qué ficheros, sin resumir su contenido.

## Tabla de remedios (respaldo cuando falta `hint`)

| Regla | Qué falla | Remedio |
|---|---|---|
| `V01` | ID ausente, mal formado o duplicado | Ajusta el ID a `R-` + 2–4 mayúsculas + `-` + tres dígitos; si es duplicado, renumera el nuevo, nunca el que ya vivía |
| `V02` | La narrativa no encaja en un solo patrón EARS | Deja una sola cláusula de arranque (`WHEN`, `WHILE`, `WHERE`, `IF … THEN`) o escríbela como requisito ubicuo |
| `V03` | No hay narrativa antes del primer escenario | Escribe la frase EARS entre el encabezado y el primer `#### Scenario:` |
| `V04` | El requisito no tiene escenarios | Añade al menos un `#### Scenario:` con su caso concreto |
| `V05` | Un escenario sin `**WHEN**` o sin `**THEN**` | Completa el bullet que falta; ambos son obligatorios en todos los escenarios |
| `V06` | Falta `verifies:` | Nombra el fichero de test que falla cuando el requisito se incumple. Sin oráculo no hay requisito |
| `V07` | El fichero de `verifies:` no existe en disco | Crea el test en esa ruta, o corrige la ruta si está mal escrita |
| `V08` | El fichero de `verifies:` no contiene `@covers <ID>` | Añade el comentario `@covers <ID>` dentro del test; el vínculo es doble a propósito |
| `V09` | `confidence:` ausente o fuera de `{high, medium, low}` | Declara uno de los tres valores; no hay valor por defecto |
| `V10` | `confidence: low` sin `revisit:` útil | Escribe en `revisit:` el hecho que resuelve la apuesta —«cuando hayamos visto los diez primeros casos reales»—, nunca una fecha; o sube la confianza si ya no es una apuesta |
| `V11` | Más del 30 % de los requisitos en `low` | Resuelve las apuestas más caras antes de seguir: baja el número de `low`, no el listón |
| `V12` | El delta no declara ningún bloque | Abre al menos un `## ADDED\|MODIFIED\|REMOVED\|RENAMED Requirements` |
| `V13` | Un ID de `MODIFIED`/`REMOVED`/`RENAMED` no existe en ninguna capability viva | Corrige el ID, o mueve el requisito al bloque `ADDED` si de verdad es nuevo |
| `V14` (aviso) | `SHALL` o `MUST` en la narrativa | Escribe el modal en español (`DEBE`); las palabras clave estructurales siguen en inglés |
| `V15` (aviso) | Falta `from:` en un requisito de una capability nueva | Enlaza el documento de origen que justifica el requisito |
| `V16` (aviso) | Un test declara `@covers` de un ID que no existe | Corrige el ID del test, o especifica el comportamiento que ese test ya está comprobando |
| `V17` | Un change `verified` sin `oracle.json` en verde que cubra todos sus IDs | Ejecuta `/venoxia:verify` sobre el change: graba el oráculo antes de dejarlo en `verified` |
| `V18` (aviso) | Un requisito llegó a verde sin haber pasado antes por rojo en ningún run ni figurar en `confirmed_green` | Comprueba que el test de verdad falla sin la implementación; si el usuario ya lo vio fallar, `/venoxia:verify` graba su confirmación con `oracle.py --record --confirm-green <ID>` y el aviso desaparece |
| `V19` | Un requisito declara `runner:` y `.venoxia/venoxia.json` no declara ese nombre bajo `runners` (o lo declara sin `command`, o con un `cwd` que no existe) | Declara el runner en `venoxia.json` —`"runners": {"<name>": {"command": "…"}}`— o quita la línea para que corra con el `test_command` |
| `P01` | Fichero ilegible o inexistente | Comprueba la ruta y los permisos |
| `P02` (aviso) | Clave de metadatos desconocida | Usa sólo `verifies`, `confidence`, `why`, `revisit`, `from` |
| `P03` (aviso) | Clave de metadatos repetida | Deja una sola; el parser se queda con la última |
| `P04` (aviso) | Bullet de escenario con forma inesperada | Escríbelo como `- **WHEN** texto` |
| `P05` (aviso) | Un `### ` con forma de requisito cae dentro de un bloque de código y no se ha leído como requisito | Si es un ejemplo, no hay nada que hacer; si es un requisito de verdad, sácalo del bloque o cierra la valla ` ``` ` que lo envuelve |

## Recordatorio final

Que `V07` salga en rojo porque el test todavía no existe —y `V08` en cuanto ese fichero exista pero aún no lleve su `@covers`— **no es un fallo del sistema, es el sistema funcionando**: la especificación afirma que existe un oráculo y el disco dice que no. Las dos reglas no saltan a la vez sobre el mismo fichero: sin fichero sólo habla `V07`, y `V08` sólo acusa a los ficheros que ha podido leer. Preséntalo como cualquier otro error y no lo disculpes.
