# 2026-09-06-portable-gate Proposal

## Why

El repositorio es público desde hoy, y con él salió a la calle
`templates/ci/venoxia-gate.yml`. Ese fichero tiene dos problemas que resultan
ser el mismo.

El primero es de exposición: pide `runs-on: oa2p-debian` y hace checkout de
`OA2P/venoxia` con un token privado. Cómo se ejecutan el respaldo y las
pruebas internas de la organización no es de interés público, y ahí estaba
escrito.

El segundo es que **no le sirve a nadie de fuera**. Esa etiqueta no existe en
el pool de runners de otro proyecto y ese repositorio no lo puede clonar. La
plantilla que el plugin ofrece como su puerta de CI es el único artefacto que
sólo funciona dentro.

Y los dos salen de la misma causa. Un fichero de workflow obliga a declarar
`runs-on` —es obligatorio en el esquema de Actions—, un checkout y una forma
de autenticarse. Son tres opiniones sobre la infraestructura de quien lo
copia, y ninguna de las tres le corresponde a Venoxia. Cambiar la etiqueta por
`ubuntu-latest` no arregla eso: lo traslada, y garantiza repetir este trabajo
la próxima vez que cambie algo.

Hay un tercer motivo, interno y anterior a la publicación. La plantilla lleva
dentro **lógica de Venoxia escrita en un heredoc de YAML**: qué changes están
activos, cómo se normaliza su `state`, cuándo se falla. Es el único trozo del
plugin cuya conducta no comprueba ningún test — lo único que hoy se verifica
es que ciertas cadenas aparecen en el fichero. En un proyecto cuya tesis es
que el comportamiento se declara y se verifica, eso está fuera de sitio.

## What Changes

- Existe `scripts/gate.py`: un comando que corre el acta, el validador y el
  oráculo por cada change en `validated` o `verified`, y termina con `0` si el
  proyecto pasa la puerta, `1` si no la pasa y `2` si el uso es incorrecto —
  los mismos códigos que el resto del núcleo. La lógica que vivía en el
  heredoc pasa aquí, con sus tests.
- `templates/ci/venoxia-gate.yml` deja de existir, y con él `runs-on`, los dos
  checkouts, el token y `VENOXIA_REF`. Un proyecto consumidor añade una línea
  al CI que ya tenga, sea el que sea.
- El `README.md` deja de documentar el CI interno: ni la forja, ni sus
  etiquetas de runner, ni el espejo de respaldo. En su lugar explica cómo
  verificar un proyecto que ha adoptado Venoxia, con los comandos que
  cualquiera puede ejecutar y un ejemplo de CI que se lee como ejemplo, no
  como artefacto mantenido.
- Los comentarios de `.forgejo/workflows/ci.yml` se quedan en lo operativo
  —por qué hace falta `nodejs`, por qué un usuario sin privilegios— y sueltan
  lo que explicaba la infraestructura de la organización.

## New Capabilities

Ninguna.

## Modified Capabilities

- `ci`: la puerta que Venoxia ofrece a un proyecto consumidor deja de ser un
  fichero de workflow y pasa a ser un comando. El CI de este repositorio
  (`R-CI-011`, `R-CI-012`) no cambia.

## Impact

- `tests/test_ci_template.py` se retira: su sujeto desaparece. Lo sustituye
  `tests/test_gate.py`.
- Un consumidor que ya hubiera copiado la plantilla sigue teniéndola en su
  repo y le sigue funcionando; simplemente deja de estar mantenida, y la
  llamada a `gate.py` la sustituye con una línea.
- Ningún cambio en `validate.py`, `charter_lint.py`, `oracle.py`, el guardián
  ni el esquema JSON versión 1.
- Las cifras de los cinco fixtures de `evals/` no cambian.
- `scripts/` pasa de cinco scripts a seis. `CLAUDE.md` lo recoge.

## Confidence

- **Que un comando cubra lo que cubría la plantilla** · `high` · la plantilla
  hacía tres cosas de Venoxia —acta, validador, oráculo por change activo— y
  las tres son invocaciones de scripts que ya existen y ya tienen tests.
- **Que la lógica gane cobertura al salir del YAML** · `high` · pasa a ser
  Python ejecutado por la suite, no cadenas comprobadas por regex.
- **Que un consumidor sepa dónde meter la línea** · no es un requisito de este
  delta: depende de su CI, que Venoxia no conoce. Se documenta con un ejemplo
  y se declara aquí, no se convierte en requisito, por la misma razón por la
  que `R-CI-006` y `R-CI-007` salieron del delta el 2026-09-05.
- **El límite que no se va:** si la suite del consumidor tiene dependencias,
  tiene que instalarlas antes de llamar al comando. Con la plantilla era un
  fallo silencioso por `ModuleNotFoundError`; con un comando documentado es
  evidente y suyo.

## Pendiente

