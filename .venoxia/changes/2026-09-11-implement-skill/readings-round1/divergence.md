# Informe de divergencia

- **Lecturas:** `.venoxia/changes/2026-09-11-implement-skill/readings`
- **Lectores:** 2 (`reader-a`, `reader-b`)
- **Escenarios comparados:** 15
- **Umbral de similitud de `effect`:** 0.60
- **Modo estricto (`--strict`):** no
- **Código de salida:** 1

## Veredicto

**Las lecturas no convergen.** 1 divergencia dura, 3 blandas y 0 lagunas declaradas sobre los 15 escenarios. Esta ejecución sale con código 1.

## Divergencias duras · 1

Estas lecturas no pueden ser todas correctas a la vez. Responde cada pregunta con su
letra, corrige el delta con la respuesta y vuelve a ejecutar la divergencia.

### Escenario: The body stops on a green oracle

El lector A responde **0**; el lector B no da ningún código.

**¿Qué código de estado debe devolver el sistema en «The body stops on a green oracle»?**
- (A) 0
- (B) Ninguno, el escenario no devuelve código de estado

## Divergencias blandas · 3

Puede que sólo sea vocabulario distinto, o puede que no. Confírmalo antes de implementar.

### Escenario: The body requires a recorded red run

El lector A describe el efecto como «el cuerpo declara que exige un run rojo previo en oracle.json»; el lector B describe el efecto como «el cuerpo declara que exige un run con algún requisito en red». Similitud de contenido 0.40, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The body requires a recorded red run» es la correcta?**
- (A) «el cuerpo declara que exige un run rojo previo en oracle.json»
- (B) «el cuerpo declara que exige un run con algún requisito en red»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: The tools are exactly the seven declared

El lector A describe el efecto como «el frontmatter lista exactamente esas siete herramientas permitidas»; el lector B describe el efecto como «el frontmatter lista exactamente los siete allowed-tools indicados». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «The tools are exactly the seven declared» es la correcta?**
- (A) «el frontmatter lista exactamente esas siete herramientas permitidas»
- (B) «el frontmatter lista exactamente los siete allowed-tools indicados»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

### Escenario: No generic Bash

El lector A describe el efecto como «ninguna entrada allowed-tools es un Bash sin acotar»; el lector B describe el efecto como «el frontmatter no incluye ninguna entrada Bash sin acotar». Similitud de contenido 0.44, por debajo del umbral 0.60. Se comparan las palabras que dicen algo, sin artículos ni conjugación.

**¿Cuál de estas lecturas del efecto de «No generic Bash» es la correcta?**
- (A) «ninguna entrada allowed-tools es un Bash sin acotar»
- (B) «el frontmatter no incluye ninguna entrada Bash sin acotar»
- (C) Ambas lecturas describen lo mismo con otras palabras, no hay divergencia real

## Abogado del diablo · 3

Implementaciones que cumplirían el delta al pie de la letra y aun así serían inaceptables.

- **[high]** R-IMP-002 — R-IMP-002 sólo prohíbe editar `.venoxia/` y los ficheros que un `verifies:` nombra; una implementación literal edita `tests/venoxia_fixtures.py`, `tests/conftest.py` o cualquier módulo auxiliar que el test importe (ninguno está bajo `.venoxia/` ni aparece en un `verifies:`) hasta vaciar las aserciones, con lo que `oracle.py` sale con código `0` y la skill termina según R-IMP-003 sobre un verde falso que `/venoxia:verify` grabará como `verified`.
- **[medium]** R-IMP-002 — R-IMP-002 prohíbe sin excepción editar cualquier fichero bajo `.venoxia/`, y `decisions.json` vive en `.venoxia/changes/<id>/decisions.json`: una implementación obediente pregunta con `AskUserQuestion` la decisión no escrita, la usa para escribir el código y no la anota en ninguna parte, dejando la razón de la decisión de producto sólo en la conversación, que se pierde al cerrar la sesión.
- **[medium]** R-IMP-001 — R-IMP-001 sólo exige que exista un run con «al menos un requisito en `red`»; con un change de cinco requisitos donde uno tiene test en rojo y los otros cuatro están en `missing` (su test no existe), la skill arranca legítimamente y escribe el código de los cinco, que es exactamente el código naciendo antes que el test que el rojo previo debía impedir.

## Escenarios que convergen · 11

- The skill is named implement and takes a change id
- The body requires the validated state
- The inventory precedes any edit
- The body forbids editing .venoxia
- The body forbids editing the oracle files
- The body says the guardian keeps watching
- The body forbids recording
- An unwritten decision is asked, not chosen
- The delivery lists every requirement with its state
- The delivery lists the files touched
- The next step is verify
