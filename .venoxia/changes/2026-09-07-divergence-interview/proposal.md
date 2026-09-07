# 2026-09-07-divergence-interview Proposal

## Why

Dos observaciones sobre `/venoxia:diverge` con deltas reales. La primera: el
informe vuelca todas las preguntas cerradas de golpe y quien lo lee tiene que
contestarlas en bloque, con lo que las últimas se contestan sin mirar y una
ambigüedad que nadie preguntó llega al código. La segunda: cuando el script
marca una divergencia como dura porque dos efectos se contradicen, el informe
dice «lo contradice» y nada más; la señal que lo decidió —una negación, una
marca de alcance, una cifra distinta— se queda dentro del código. La señal de
polaridad ya ha dado dos falsos positivos sobre prosa real, los dos corregidos
con test de regresión, y el criterio pendiente dice que un tercero obliga a
replantearla; sin que el informe nombre la señal, ese tercero sólo se
reconocería releyendo el código, y nadie lo hace.

## What Changes

- Una divergencia dura de `side_effects` dice en el informe qué señal la hizo
  dura —la negación con su marca, el alcance con su marca, la cifra con los dos
  números, o que el otro lector no registrara ningún efecto— y el JSON la lleva
  en la clave `signal`, `null` en las blandas.
- `/venoxia:diverge` plantea las preguntas del informe como entrevista: una
  por llamada a `AskUserQuestion`, en el orden del informe, con la pregunta y
  las opciones literales del script, y la descripción de cada opción dice
  sólo de qué lector viene y qué tendría que decir el delta si se elige.
- Cada respuesta se anota tal cual en `.venoxia/changes/<id>/decisions.json`
  —la opción elegida o el texto escrito a mano—, y el siguiente paso copia ese
  texto al escenario del delta sin reformularlo.

## Capabilities

### Modified Capabilities

- `divergence`: tres requisitos nuevos, `R-DIV-008` a `R-DIV-010`. Ninguno de
  los siete existentes cambia: la aritmética de `diff_readings.py` sigue igual,
  lo que se añade es qué dice el informe de cada dura y cómo la skill presenta
  el resultado y recoge la respuesta.

## Impact

- El esquema JSON de `diff_readings.py` sigue en versión 1 con una clave
  añadida, `signal`, en cada elemento de `divergences`; los graders de los
  evals leen por regex y una clave nueva no les afecta.
- `skills/diverge/SKILL.md` gana `AskUserQuestion` en `allowed-tools` y sigue
  sin editar deltas.
- Aparece `decisions.json` junto a `divergence.md`; vive fuera de `readings/`,
  así que `diff_readings.py` no lo ve.
- Con dos lectores ninguna pregunta del script pasa de cuatro opciones, que es
  el tope de `AskUserQuestion`; un panel de tres lectores podría pasarlo y la
  skill lo declara como límite.

## Pendiente

Dos rondas de divergencia: la única dura de la primera fue «ambos números»
frente a «los dos números (15 y 30)», que la cifra separa por diseño y la
segunda ronda no repitió. Ataques del abogado que se resuelven en la
implementación y en el texto de la skill, sin cambiar el contrato:

- Cuando concurren varias señales, `signal` lleva la primera por precedencia
  (polaridad, alcance, cifra) y el informe **nombra todas** las que disparan,
  con sus marcas o sus números.
- Para `scope` el informe nombra las marcas de cada lector; para
  `empty-repertoire` dice que el otro lector no registró ningún efecto.
- La dureza no se estrecha: las señales son las que ya decidían antes de este
  change; lo que se añade es nombrarlas. Los antónimos verbales siguen del lado
  blando, que es la frontera declarada en `R-DIV-005`.
- Cada entrada de `decisions.json` lleva su instante `at`, y ante dos entradas
  con el mismo escenario y la misma pregunta vale la más reciente: una segunda
  pasada no pierde lo decidido ni lo confunde con lo nuevo.

## Confidence

- **Una pregunta por llamada, aunque la herramienta admita cuatro** ·
  `medium` · agrupar cuatro preguntas de escenarios distintos sería más rápido,
  pero es justo el «contestar en bloque» que motiva el cambio; se revisa cuando
  la entrevista se haya usado sobre un delta real con más de diez preguntas.
- **Nombrar la señal en vez de retirar la de polaridad** · `high` · dos falsos
  positivos en prosa real no bastan para retirar una señal que caza el
  desacuerdo más flagrante posible; lo que falta es poder contar el tercero sin
  releer el código.
- **El resto de la propuesta** · `high` · la aritmética no cambia, y el
  contrato de la skill sigue el de `/venoxia:verify`: la skill presenta, el
  script decide.
