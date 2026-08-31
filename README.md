# Venoxia

> Plugin de Claude Code que convierte la especificación en un contrato ejecutable.

## Qué es

Venoxia es un plugin para Claude Code que impone un formato de requisito verificable, lo valida con un script determinista y usa un hook `PreToolUse` para que ese contrato no se pueda ignorar por descuido.

La tesis es corta y cabe en tres frases. **Una especificación es una apuesta sobre el comportamiento futuro de un sistema.** **Toda apuesta debe declarar cómo se resuelve y cuánto se confía en ella.** **Lo que distingue a Venoxia: la spec deja de ser prosa y pasa a ser un contrato que falla en CI cuando miente.**

En la práctica eso significa que cada requisito nace con dos campos que ninguna otra herramienta exige: `verifies:`, la ruta del test que resuelve la apuesta, y `confidence:`, el nivel de confianza declarado. Sin oráculo, no compila. Y como el validador es un script de Python sin modelo detrás, el veredicto es el mismo en tu portátil, en el CI y dentro de la conversación.

Esta entrega cubre el **núcleo verificable**: el formato del requisito, el validador de 16 reglas, el guardián y el motor de divergencia.

## Instalación

```bash
claude plugin marketplace add oa2p-solutions/venoxia
claude plugin install venoxia@venoxia
```

Requiere Python 3 en el `PATH` (probado con 3.14). Los scripts usan **sólo la biblioteca estándar**: no hay `pip install`, ni entorno virtual, ni dependencias que mantener. `pytest` hace falta únicamente para ejecutar la suite de tests del propio plugin.

## El formato del requisito

Etiquetas y claves en inglés, prosa en español. Parseable con expresiones regulares, legible sin herramientas.

```markdown
### R-CHK-014 · Stock reservation on payment confirmation

WHEN el cliente confirma el pago, el sistema DEBE reservar el stock de
todas las líneas del pedido durante 15 minutos.

#### Scenario: Stock available on every line
- **WHEN** hay stock disponible en todas las líneas
- **THEN** se crea la reserva con TTL de 15 minutos

#### Scenario: Insufficient stock on one line
- **WHEN** falta stock en al menos una línea
- **THEN** responde 409 y no crea ninguna reserva

verifies:   test/checkout/reservation.spec.ts
confidence: medium
  why:      los 15 minutos son una apuesta, no un dato
  expires:  2026-10-30
from:       prfaq/checkout-express.md#sin-sorpresas-al-pagar
```

El ID vive en el encabezado (`### R-CHK-014 · Título`): estable, linkable y parseable. El separador canónico es `·`, y también se aceptan la raya `—`, el semicuadratín `–` y el guion `-`, éste con espacio a los dos lados para no partir un título que ya lo lleva. La narrativa que sigue al encabezado es la cláusula EARS; los escenarios son la tabla de decisión. El bloque de metadatos usa claves fijas al final del requisito, y su indentación es puramente cosmética.

### Las claves del bloque de metadatos

| Clave | ¿Obligatoria? | Qué contiene | Por qué existe |
|---|---|---|---|
| `verifies` | Sí | Ruta (o rutas separadas por coma o espacio) del fichero de test que decide si el requisito se cumple. | Es el corazón del sistema: la apuesta declara cómo se resuelve. Un requisito sin oráculo es una opinión, y el validador lo rechaza (`V06`, `V07`). |
| `confidence` | Sí | `high`, `medium` o `low`. | Obliga a separar lo que se sabe de lo que se supone, en el momento de escribirlo y no después del incidente (`V09`). |
| `why` | Recomendada | Una frase en español que explica por qué la confianza es esa y no otra. | Convierte «medium» en información accionable: dice **qué** parte concreta es la apuesta. |
| `expires` | Sí cuando `confidence: low` | Fecha ISO `YYYY-MM-DD` estrictamente futura. | Una suposición sin fecha de caducidad se vuelve permanente. Con fecha, el validador la mata solo (`V10`). |
| `from` | Recomendada | Referencia al documento de origen (PR/FAQ, ticket, decisión), con ancla si aplica. | Preserva la trazabilidad hacia la intención de negocio. Su ausencia en un requisito nuevo es un aviso (`V15`). |

El vínculo con el test es **doble**: la spec apunta al fichero con `verifies:`, y el fichero apunta de vuelta al requisito con un comentario `@covers R-CHK-014`. El validador comprueba las dos direcciones (`V07`, `V08`, `V16`), de modo que borrar el test rompe la spec y renombrar el requisito rompe el test.

## Las tres skills

Se usan en este orden:

1. **`/venoxia:specify "…"`** — lee los principios y las capabilities existentes, escribe la `proposal.md` y el delta en EARS, con `verifies:` y `confidence:` en cada requisito desde el primer borrador.
2. **`/venoxia:validate`** — ejecuta el validador determinista sobre `.venoxia/` y presenta los findings agrupados por severidad, con la corrección concreta de cada uno.
3. **`/venoxia:diverge`** — despacha dos lectores aislados y un abogado del diablo sobre el delta, y enfrenta sus lecturas para convertir cada desacuerdo en una pregunta cerrada.

El `change.json` pasa a `"state": "validated"` sólo cuando validador **y** divergencia pasan.

## Las 16 reglas del validador

Todas deterministas: ninguna consulta a un modelo. `scripts/validate.py` sale con `0` si el ámbito es conforme, `1` si no lo es y `2` ante un error de uso. Con `--strict`, los avisos también hacen fallar.

| Regla | Qué comprueba | Severidad |
|---|---|---|
| `V01` | El ID está presente, casa con `^R-[A-Z]{2,4}-\d{3}$` y es único en el ámbito validado. | error |
| `V02` | La narrativa encaja en exactamente un patrón EARS: `WHEN` (event-driven), `WHILE` (state-driven), `WHERE` (optional-feature), `IF … THEN` (unwanted-behaviour), `WHILE … WHEN` (complejo) o ubicuo. | error |
| `V03` | Hay narrativa no vacía antes del primer `#### Scenario:`. | error |
| `V04` | El requisito tiene al menos un escenario. | error |
| `V05` | Cada escenario tiene `**WHEN**` y `**THEN**`. | error |
| `V06` | `verifies:` está presente y con valor no vacío. **El corazón del sistema.** | error |
| `V07` | El fichero de `verifies:` existe en disco, resuelto desde `--root`. | error |
| `V08` | Ese fichero contiene `@covers <ID>`. Con varias rutas, basta que una lo contenga. | error |
| `V09` | `confidence:` está presente y vale `high`, `medium` o `low`. | error |
| `V10` | `confidence: low` obliga a `expires:` con fecha ISO estrictamente futura. | error |
| `V11` | Presupuesto de incertidumbre: como mucho el 30 % de los requisitos del ámbito en `low`. Exactamente 0,30 pasa. | error |
| `V12` | Cada delta declara al menos un bloque `## ADDED\|MODIFIED\|REMOVED\|RENAMED Requirements`. | error |
| `V13` | Los IDs de `MODIFIED`/`REMOVED`/`RENAMED` existen en alguna capability viva. Sin capabilities en disco, la regla no se evalúa. | error |
| `V14` | La narrativa no usa `SHALL` ni `MUST`. | warning |
| `V15` | `from:` ausente en un requisito de una capability nueva. | warning |
| `V16` | Un test declara `@covers <ID>` de un ID que no existe en ninguna spec: comportamiento no especificado. | warning |

Además de las reglas, el parser emite sus propios findings de forma: `P01` (error, fichero ilegible o inexistente), `P02` (aviso, clave de metadatos desconocida), `P03` (aviso, clave repetida; gana la última), `P04` (aviso, bullet de escenario que no encaja en `- **KW** texto`) y `P05` (aviso, un `### ` con forma de requisito que cae dentro de un bloque de código y por tanto no se ha leído como requisito). El parser nunca lanza una excepción: todo problema sale como finding.

Dos límites que conviene conocer antes de confiar en el verde: `V16` escanea sólo los ficheros que algún `verifies:` nombra, no el repositorio entero, así que un test huérfano en una carpeta que nadie referencia no se detecta; y `V01` compara duplicados dentro del ámbito validado, con una excepción a cada lado: un requisito del bloque `ADDED` se compara **además** contra los IDs de las capabilities vivas —declarar como nuevo un ID que ya vive es un duplicado aunque esa capability no entre en el ámbito—, mientras que un `MODIFIED`, `REMOVED` o `RENAMED` que repite el ID de la capability viva es lo esperado y no se denuncia.

Uso directo del script, sin pasar por la skill:

```bash
python3 scripts/validate.py                  # todo lo que haya bajo .venoxia/
python3 scripts/validate.py --change 2026-08-31-checkout --strict
python3 scripts/validate.py --json --no-color
```

Si el proyecto no tiene `.venoxia/`, el validador lo dice y sale con `0`: un proyecto que no ha adoptado Venoxia no falla por no haberlo adoptado.

## El modelo de confianza del guardián

El guardián es la pieza que convierte el hábito en infraestructura, y por eso es la que más honestidad merece: si no sabes exactamente qué bloquea y cómo apagarlo, lo desinstalarás el primer viernes con prisa.

**Qué intercepta.** Un hook `PreToolUse` con el matcher `Edit|Write|NotebookEdit`, y nada más. No intercepta `Bash`: un `sed -i`, un `> fichero` o un `git apply` pasan sin verse. El guardián existe para que escribir código sin spec sea un acto deliberado, no para hacerlo imposible.

**Los cinco caminos de decisión, en orden.** El primero que casa decide:

1. No existe `<raíz>/.venoxia/` → **allow**. El proyecto no ha adoptado Venoxia y el plugin no estorba.
2. La ruta editada cae bajo `.venoxia/` o `prfaq/`, o es markdown de spec (`*.md` bajo `docs/spec*` o `specs/`, o llamado `spec.md`, `proposal.md`, `delta*.md`) → **allow**. Estás escribiendo la especificación. Esos directorios se reconocen **anclados a la raíz**: un `src/prfaq/` no exime de nada.
3. El change activo tiene `"state": "validated"` en su `change.json` **y** un `delta/` con al menos un `.md` no vacío → **allow**. El contrato está firmado, y hay especificación al lado que lo acredita: un `change.json` fabricado a mano, solo, ya no basta.
4. El change activo declara `"via": "direct"` → **allow**, y se anota una línea JSONL en `.venoxia/drift/direct.log` con marca de tiempo, change, herramienta y ruta. Es la vía de escape registrada, no vigilada.
5. Cualquier otro caso → **deny**, con una razón en español que dice qué falta (no hay change validado), el comando exacto que lo arregla (`/venoxia:specify "…"` y luego `/venoxia:validate`) y cómo saltárselo.

El change activo es el `.venoxia/changes/<id>/change.json` cuyo `state` no es `"archived"` y cuyo `mtime` es el más reciente **de los que se pueden leer**. Con `NotebookEdit` la ruta juzgada es `notebook_path`; con las demás herramientas, `file_path`. La ruta se compara con la raíz del proyecto dos veces, por cadena y con las dos rutas resueltas (`realpath`): en macOS `/tmp/p/src/x.ts` y `/private/tmp/p/src/x.ts` son el mismo fichero, y basta con que **una** de las dos medidas lo sitúe dentro del proyecto para juzgarlo.

Hay tres casos más que también permiten, los tres por prudencia: que la herramienta no declare ninguna ruta, que la ruta resuelta caiga fuera de la raíz del proyecto, y que el `change.json` —o el propio `changes/`— no se deje **leer** por un fallo de entrada/salida (permisos denegados, un montaje caído, un `change.json` que resulta ser un directorio). Ese último es un fallo nuestro, no del proyecto: se permite, se deja la traza en `stderr` y se anota en el diario de deriva con `"note": "change-no-legible"`, porque un `allow` concedido sin haber comprobado el respaldo es exactamente lo que ese diario existe para recordar.

Y uno que **ya no** permite: un `change.json` que existe y cuyo **contenido** está mal —JSON corrupto, un array donde iba un objeto, un megabyte de relleno—. Un fichero del usuario que está mal escrito no es un fallo del guardián, y no acredita ninguna especificación validada: se salta, la búsqueda sigue con el siguiente change y, si no queda ninguno bueno, se deniega. Confundir eso con el fail-open era una puerta trasera: bastaba estropear el `change.json` a propósito. La frontera, que es fina, la marca quién tiene la culpa: contenido mal escrito, del usuario, no acredita nada; fallo de E/S al preguntarlo, nuestro, permite.

**Una decisión, siempre, pase lo que pase.** Un hook `PreToolUse` que no escribe nada en `stdout` no ha decidido nada, así que la edición sigue adelante: un `deny` que no se imprime es una escritura consentida. Por eso la decisión se serializa con `ensure_ascii=True` —los acentos y las comillas viajan escapados y el cliente los recompone— y se vuelca ya codificada a `sys.stdout.buffer`, sin depender de la codificación del envoltorio de texto. Con `PYTHONIOENCODING=ascii` o `LC_ALL=C`, o con un `file_path` que ni siquiera es Unicode legal, el guardián seguía denegando en su lógica y no imprimía nada. El payload de entrada corre la misma suerte: se lee en bytes y se decodifica como UTF-8, porque leerlo por el envoltorio de texto hacía que un acento en la ruta —`src/año/checkout.ts`— tumbara la lectura y convirtiese el `deny` en `allow` sin decir nada. Ahora sale ASCII puro, y el testigo de «ya he decidido» sólo se marca después de que el `write` y el `flush` hayan ido bien. La traza de `stderr` está sometida a lo mismo: si su extremo está cerrado, se cambia por un sumidero en vez de tumbar el hook o hacerlo salir con código 120 —que para el cliente es un «error del hook» aunque la decisión esté escrita—.

**Fail-open, por diseño.** `main()` está envuelto entero en un `try/except`: cualquier excepción del propio guardián o un JSON malformado producen **allow** y una traza a `stderr`. Un `change.json` corrupto no entra aquí: eso es un fichero del usuario, y va por el camino de arriba. Un `stdin` vacío también permite, aunque por otro camino y sin traza: un payload vacío no declara ninguna ruta, y sin ruta no hay nada que juzgar. El guardián nunca es la razón por la que no puedes trabajar. El coste de esa decisión es explícito: un guardián roto no protege nada y no lo grita, sólo deja pasar. Presupuesto de latencia por debajo de 100 ms, sin red y sin recorrer el repositorio: un `scandir` de `.venoxia/changes/`, la lectura del `change.json` y, sólo cuando se declara validado, un `scandir` de su `delta/` (medidos: 0,01 ms el delta y 0,02 ms las dos resoluciones de ruta).

**Lo que el guardián no puede impedir.** Con la misma honestidad con la que arriba dice que `Bash` no se intercepta: **quien pueda escribir bajo `.venoxia/` puede fabricarse un change**. El paso 2 permite escribir la especificación —tiene que permitirlo— y el paso 3 sólo comprueba que el `change.json` diga `validated` y que exista un `delta/*.md` con algo dentro; no ejecuta el validador, porque eso rompería el presupuesto de 100 ms y el fail-open. Un `delta/x.md` con una línea cualquiera y un `change.json` a juego bastan para desarmarlo. Exigir el delta sube el precio: de un fichero trivial a fabricar también una especificación falsa, y deja rastro en el diario cuando algo pasa sin respaldo firme (`"note": "validated-sin-delta"` si un `validated` sin delta se cuela por la vía `direct`, `"note": "delta-no-comprobable"` si ni siquiera se pudo mirar el directorio). Pero la frase que importa es ésta: **el guardián es una barrera contra el descuido, no contra la determinación**. Protege del viernes con prisa, no de quien ha decidido saltárselo.

**Cómo desactivarlo.** Tres interruptores, del más local al más definitivo:

- **Por cambio:** poner `"via": "direct"` en el `change.json` activo. Sigue permitiendo todo y deja constancia en `.venoxia/drift/direct.log`.
- **Por proyecto:** borrar (o renombrar) el directorio `.venoxia/`. Sin él, el guardián permite siempre por el camino 1.
- **Del todo:** `claude plugin uninstall venoxia@venoxia`. Se va el hook, se van las skills y las specs que ya tengas escritas siguen siendo markdown legible.

## Verificar regresiones

```bash
python3 -m pytest tests/ -q
claude plugin validate . --strict
claude plugin eval venoxia --ablation with-without --allow-tools 'Bash(python3 *)' Write
```

- `pytest` cubre el núcleo determinista: un caso en positivo y otro en negativo por cada regla `V01`–`V16`, más la gramática del parser, el esquema JSON del informe, los cinco caminos del guardián y la aritmética de divergencia. Es la parte con cobertura obligatoria: de ella depende la credibilidad del resto.
- `claude plugin validate . --strict` comprueba la estructura del plugin: manifiesto, frontmatter de skills y agentes, y el hook declarado.
- `claude plugin eval venoxia --ablation with-without …` mide lo único que no se puede probar con asserts: que el plugin cambia el resultado. El `--allow-tools` no es decorativo: `Bash` y `Write` están con verja, y sin ese permiso de operador los cinco casos fallan por falta de permisos en vez de por regresión (el detalle, en [`evals/README.md`](evals/README.md)). Compara la ejecución con y sin él sobre casos que deben detectarse (código de estado ambiguo, efecto parcial ambiguo, oráculo ausente, presupuesto de incertidumbre excedido) y uno que no debe dar falso positivo (spec limpia).

## Qué queda fuera de esta entrega

Diseñado, documentado y pospuesto hasta que el núcleo se use en una feature real:

- Triaje por riesgo de tres vías (DIRECTA / NORMAL / CRÍTICA).
- PR/FAQ y el bucle de promesas con fecha de revisión.
- `trocear` / `construir` / `revisar` con git worktrees.
- Diario de deriva con estadística acumulada que reescribe las plantillas.
- Panel de salud de capabilities.
- Consolidación automática del delta sobre la capability viva.

De todos, el **panel de salud** es el siguiente con más valor: se deriva del JSON que `validate.py` ya produce, así que es barato en cuanto haya specs reales que mostrar.

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
