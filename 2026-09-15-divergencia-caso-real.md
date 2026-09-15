# Lo que la ejecución real sobre Consolidar enseñó · 2026-09-15

La 0.5.0 salió con la suite en verde, la cobertura por encima de sus umbrales,
`gate.py` en `0` y los oráculos de la entrevista adaptativa y de la agrupación
por decisión raíz en verde. Y al pasar el motor nuevo sobre las lecturas reales
del change `review-fixes` de Consolidar, y la skill `/venoxia:charter` sobre su
acta, aparecieron cuatro problemas que ninguna prueba estructural detecta. Este
documento los recoge tal como se observaron y fija lo que Venoxia tiene que
cambiar. Es el `from:` de los requisitos que salen de él. Consolidar es sólo el
caso de verificación: su código de producción no se toca.

## Objetivo

1. Que la entrevista haga menos preguntas en una sesión real.
2. Que la divergencia pregunte una sola vez por cada decisión de negocio.
3. Que una respuesta que no resuelve la pregunta no quede registrada como
   decisión cerrada.
4. Que las decisiones anteriores no vuelvan a preguntarse sin motivo.
5. Que las inferencias confirmadas durante `/venoxia:charter` dejen evidencia
   auditable.
6. Que se pueda demostrar qué versión del plugin está corriendo.

Todo por el ciclo completo de Venoxia; ningún change `via: direct`.

## Hallazgo 1 · La agrupación sigue siendo demasiado literal

`diff_readings.py` sobre las seis lecturas de `review-fixes`: 6 divergencias, 5
decisiones, 1 agrupada. Sólo se agruparon «cola decimal con coma» y «cola
decimal con punto», porque los dos lectores escribieron exactamente las mismas
palabras y la misma cifra (1468135) en los dos escenarios. El tercero —«guion de
cierre chileno», 1500000— quedó fuera aunque la política que los lectores
aplican es la misma: el importe se registra como entero en CLP sin inventar
parte decimal y la subida responde 201 y no 503.

El criterio «mismo conjunto de lecturas» sólo reconoce lecturas idénticas. Una
decisión compartida cuyos escenarios cambian de cifra no se ve.

**Cambio:** la unidad `decision` agrupa las divergencias que comparten una
política observable aunque cada escenario conserve sus cifras. Las cifras no se
diluyen: una decisión agrupada presenta una matriz con cada escenario, su
entrada literal, lo que leyó cada lector y su dureza. La pregunta raíz se hace
una vez; cada número sigue visible y trazable. Las lecturas ganan dos campos
opcionales, `requirement_id` e `input`, para que el agrupamiento tenga con qué
distinguir requisitos y con qué rellenar la columna de entrada. La agrupación
sigue siendo cálculo determinista del script, nunca criterio de la skill. Una
agrupación sólo vale cuando una misma respuesta puede aplicarse a todos sus
miembros: por eso cada opción dice qué anota en cada miembro.

## Hallazgo 2 · El informe vuelve a mostrar las preguntas agrupadas

El markdown enseñaba «Decisiones agrupadas» y después las mismas divergencias
miembro dentro de «Divergencias duras» y «Divergencias blandas», con su pregunta
y sus opciones otra vez. Para quien lo lee, pide lo mismo dos veces.

**Cambio:** una única sección accionable, «Decisiones pendientes», con cada
decisión una sola vez; las divergencias individuales quedan como evidencia en un
apéndice, sin repetir pregunta ni opciones. Se conservan el recuento, la dureza
de cada miembro, los índices, el veredicto y el esquema JSON.

## Hallazgo 3 · Se vuelven a preguntar decisiones anteriores

`review-fixes` tenía un `decisions.json` con cuatro respuestas y el análisis
nuevo volvió a producir las mismas preguntas. Conservar las respuestas no es
reconciliarlas con la ejecución siguiente.

**Cambio:** antes de preguntar, el script lee el historial y busca una
respuesta anterior aplicable a cada decisión comparando change, requisito,
escenarios, campos, pregunta, opciones y la huella de las lecturas que la
originaron. Si todo sigue igual, la decisión sale como ya respondida y no se
pregunta; si el delta cambió, se explica por qué la respuesta quedó obsoleta.
Las entradas antiguas sin `decision` se migran sin darlas por cerradas cuando
no se puede saber si lo estaban. El identificador `D-00X` no sirve como clave:
cambia entre ejecuciones.

## Hallazgo 4 · Se aceptan respuestas que no resuelven la pregunta

Dos respuestas reales:

- A «¿qué efectos observables debe producir “Quote without a stated currency”?»
  se respondió «Hay una moneda por defecto y debe estar seteada en el
  proyecto». Añade contexto, no decide entre los efectos presentados.
- A «¿cuál de estas lecturas del efecto de “Amount in a currency without
  subunit” es la correcta?» se respondió «2 decimales». Contradice el contrato
  vigente de CLP y cambiaría comportamiento observable.

Las dos quedaron registradas como si cerraran la decisión.

**Cambio:** cada respuesta se clasifica como `selected` (eligió una opción),
`equivalent` (las lecturas dicen lo mismo), `custom-resolved` (respuesta propia
que resuelve todos los miembros), `needs-clarification` (aporta información
pero no resuelve) o `changes-contract` (contradice o modifica el acta, los
principios, una capability viva o el delta). Sólo las tres primeras cierran.

## Hallazgo 5 · Las inferencias confirmadas no dejan rastro

En la sesión de `/venoxia:charter` sobre Consolidar la skill escribió una fila
nueva de la tabla con un «Qué podrá hacer», un `Done when` y un `Risk` que
nadie confirmó, y cambió el texto de un principio del método por su cuenta. Lo
declaró en la entrega, pero la entrega se pierde con la conversación. Además
juntó en una llamada dos preguntas dependientes: qué convenciones aprobar y qué
prioridad dar a una fila que sólo existe si se aprueba alguna.

**Cambio:** toda inferencia confirmada, toda pregunta y toda decisión propia de
la skill quedan en `.venoxia/charter-log.json`; una fila que la skill redacta se
confirma —contenido y prioridad en la misma llamada— antes de escribirse; dos
preguntas dependientes nunca comparten llamada.

## Hallazgo 6 · No hay forma de demostrar qué versión corre

La sesión de Consolidar corrió la 0.5.0 porque se comprobó a mano el
`gitCommitSha` del plugin instalado. Nada de lo que escriben las skills o los
scripts lo dice.

**Cambio:** los tres informes JSON llevan `tool` con el nombre y la versión del
plugin leída de su manifiesto; los informes markdown dicen la versión; las
skills anuncian la versión al arrancar y la escriben en `decisions.json` y en
`charter-log.json`.
