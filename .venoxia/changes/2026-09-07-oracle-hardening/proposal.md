# 2026-09-07-oracle-hardening Proposal

## Why

El panel del 2026-09-07 sobre el delta de `oracle` dejó nueve ataques del
abogado del diablo, y dos de ellos siguen abiertos en el código. El primero
fabrica evidencia: `--dry-run` y `--record` no se excluyen, así que una
invocación con los dos grabaría en `oracle.json` un run que no ejecutó nada,
indistinguible de un verde para quien sólo lee el disco, que es exactamente
lo que hacen `V17`, `gate.py` y `/venoxia:verify`. El segundo destruye
evidencia: un `oracle.json` que no se deja interpretar se sustituye por un
historial nuevo sin conservar el original, y con él se va el rojo que el ciclo
exige para conceder `verified`. Un byte de más, y `V18` sólo puede avisar de
un «verde sin rojo» cuyo rojo ya no existe.

## What Changes

- Invocar `oracle.py` con `--dry-run` y `--record` a la vez es un error de uso:
  código `2`, aviso por `stderr` que nombra los dos flags, y nada ejecutado ni
  escrito.
- Cuando `--record` encuentra un `oracle.json` que no es JSON válido o no tiene
  la forma esperada, conserva el contenido original en una copia junto a él
  —`oracle.json.corrupt-<marca>`— antes de escribir el historial nuevo, y el
  aviso de `stderr` nombra esa copia.
- Los dos ataques restantes del panel no cambian comportamiento y se declaran
  como límites en el README: el `test_command` sólo se comprueba por la
  presencia de `{files}`, y el presupuesto de `--timeout` es por requisito, no
  agregado.

## Capabilities

### Modified Capabilities

- `oracle`: dos requisitos nuevos, `R-ORC-011` y `R-ORC-012`. Ninguno de los
  diez existentes cambia de redacción: `R-ORC-006` sigue prometiendo que
  `--dry-run` no toca nada, y `R-ORC-007` que un historial corrupto se
  sustituye por uno nuevo con un único run; lo que se añade es qué pasa con la
  combinación de flags y con el fichero original.

## Impact

- `/venoxia:verify` no cambia: ya lanza `--dry-run` y `--record` en dos
  invocaciones separadas.
- El esquema JSON del oráculo sigue en versión 1 sin claves nuevas.
- Aparece un fichero nuevo junto a `oracle.json` sólo cuando éste estaba
  corrupto; `validate.py` y `gate.py` leen `oracle.json` por nombre exacto y no
  lo ven.
- La marca de la copia sale del `ran_at` del run que la crea, sin `:` ni `-`,
  para que el nombre sea válido en cualquier sistema de ficheros.

## Pendiente

Seis rondas de divergencia. Cinco de las duras de las rondas 2 a 5 fueron el
código de salida heredado —un lector lo deduce del requisito y el otro sólo
anota lo que el `THEN` dice—, y se cerraron poniendo el código en cada `THEN`;
dos fueron falsos positivos de la señal de polaridad («no se modifica» frente
a «conserva»; «se crea oracle.json» frente a «no se crea ninguna copia») y
una del alcance («único» frente a «sólo»), que dieron lugar a
`2026-09-07-divergence-false-positives` y `2026-09-07-divergence-scope-classes`.

Ataques del abogado que no cambian el contrato y se aceptan como límites:

- El historial nuevo tras una corrupción arranca con un único run, y el rojo
  previo sólo sobrevive en la copia. `V18` avisa del «verde sin rojo» y
  `/venoxia:verify` pide confirmación antes de escribir `verified`; quien
  quiera recuperar el rojo tiene los bytes en `oracle.json.corrupt-*`.
- Cuando la copia falla, cada reintento repite la suite y sale con `2` hasta
  que alguien aparte el fichero a mano. Es un fallo de E/S del disco, no del
  oráculo, y el `2` es justo lo que impide que `gate.py` lo tome por verde.
- El sufijo de la segunda copia es un contador que crece: la tercera
  corrupción con la misma marca recibe `-3`, no vuelve a `-2`.
- Un `oracle.json` legible con claves de más no es corrupto: sólo lo es lo que
  no es JSON o no trae la lista `runs`.

## Confidence

- **Rechazar la combinación en vez de ignorar `--record` bajo `--dry-run`** ·
  `high` · ignorarlo en silencio dejaría a quien tecleó los dos flags creyendo
  que grabó algo; un error de uso es la única salida que no miente.
- **Conservar la copia junto al historial, sin límite de copias** · `high` ·
  un historial corrupto es un suceso raro y cada copia lleva su marca; borrar
  copias viejas sería volver a destruir evidencia por comodidad.
- **El resto de la propuesta** · `high` · comportamiento decidido con el mismo
  criterio que ya rige `oracle.py`: determinista, sin modelo, códigos 0/1/2.
