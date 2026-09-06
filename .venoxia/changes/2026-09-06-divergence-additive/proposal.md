# 2026-09-06-divergence-additive Proposal

## Why

`compare_side_effects` denuncia como divergencia **dura** todo efecto
colateral que un lector escribe y el otro no recoge en ninguna parte de su
repertorio. La categoría dura significa «estas lecturas no pueden ser todas
correctas a la vez», y sobre deltas largos eso deja de ser cierto: dos
lectores coinciden en el comportamiento y difieren sólo en **cuántas
consecuencias deducen del contexto**. Uno anota «se ejecutan los tests
reales del change» y el otro «ejecución real del `test_command`»; ninguno
contradice al otro, pero el emparejado por cobertura no los casa y el
informe los presenta como incompatibles.

El coste es real y medido, no hipotético. `2026-09-04-oracle` lleva cuatro
rondas sin converger y sigue en `specified` por esto: 6 duras, y ninguna es
un desacuerdo de comportamiento. `2026-09-06-forgejo-only` reprodujo el
mismo patrón en sus rondas 3 y 4, con las lecturas en disco como segundo
caso de prueba. Mientras la regla no distinga añadir de contradecir, el
motor bloquea deltas correctos y enseña a desconfiar de su propia categoría
más alarmante.

## What Changes

- Un efecto colateral sin contraparte en el repertorio del otro lector deja
  de ser automáticamente duro. Se clasifica en dos:
  - **duro** si **contradice** algo del otro repertorio: la misma frase con
    la polaridad cambiada, o la misma frase con otra cifra.
  - **blando** si sólo **añade**: nadie lo niega, simplemente el otro lector
    no dedujo esa consecuencia.
- La detección de contradicción es determinista y de biblioteca estándar,
  como el resto del script: dos frases hablan de lo mismo cuando su
  cobertura, calculada ignorando las marcas de negación y las cifras, llega
  al umbral; contradicen cuando además difieren en polaridad o en cifra.
- El veredicto y los códigos de salida no cambian de significado: una dura
  sigue saliendo con `1`, y las blandas siguen pasando salvo con `--strict`.
- El informe distingue las dos cosas en su prosa, para que quien lo lee no
  tenga que adivinar por qué una diferencia de colaterales es dura y otra no.

## New Capabilities

Ninguna.

## Modified Capabilities

- `divergence`: la regla que convierte un efecto colateral huérfano en
  divergencia dura pasa a exigir contradicción, no sólo ausencia.

## Impact

- Las cifras de los cinco fixtures de `evals/` son el criterio de aceptación
  de este cambio, no un efecto colateral: `ambiguous-partial-effect` **debe
  seguir dando una dura en `side_effects`**, porque ahí el desacuerdo sí es
  una contradicción. Si esa cifra se mueve, la regla está mal.
- `2026-09-04-oracle` y `2026-09-06-forgejo-only` quedan desbloqueados si su
  divergencia era sólo de granularidad; si alguna de sus duras era real,
  seguirá saliendo y eso también es información.
- El esquema JSON versión 1 gana valores, no claves: `hardness` ya existe.

## Confidence

- **Que «contradice» se pueda decidir sin modelo** · `high` · las dos
  señales son sintácticas: una marca de negación de más o de menos, y una
  cifra distinta. `numeric_tokens` ya blinda las cifras hoy.
- **Que el umbral de contradicción no reabra el falso positivo por otro
  lado** · lo fija el fixture `ambiguous-partial-effect`, que tiene que
  seguir dando su dura.
- **La frontera declarada, medida y no escondida.** La regla cambia una
  clase de falso positivo por una clase de falso negativo, y conviene saber
  exactamente cuál. Dos efectos que se contradicen **por el verbo** —«se
  borra el borrador» frente a «se conserva el borrador»— pasan a blandos:
  medido sobre los casos reales, esa pareja da una cobertura de sujeto de
  0,50, idéntica a la de una paráfrasis que sí debe ser blanda («ejecución
  real del test_command» frente a «se ejecutan los tests reales del
  change»). No hay umbral que las separe: distinguir un antónimo de un
  sinónimo exige un léxico semántico, y este script no consulta a ningún
  modelo por diseño.

  Tres cosas acotan el daño, y por eso la frontera es aceptable: la
  divergencia **se sigue presentando** con su pregunta cerrada y sus
  opciones, así que el revisor la ve igual; `--strict` sigue haciendo fallar
  la ejecución con sólo blandas, que es la puerta para quien prefiera la
  severidad anterior; y el informe dice **lo que ha comprobado** —que
  ninguna otra lectura lo niega ni le pone otra cifra— en vez de afirmar que
  nadie lo contradice, que sería prometer más de lo que se ha mirado.

## Pendiente

