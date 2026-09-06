# ci Delta

## MODIFIED Requirements

### R-CI-008 · The workflow declares its triggers, its jobs and a runner it does not name

WHEN se busca el workflow del repositorio, el sistema DEBE tener uno que se
dispare en `push` y `pull_request` sobre la rama `main`, y también en
`workflow_dispatch`, que declare los cinco jobs `tests`, `self-spec`,
`coverage`, `plugin-validate` y `evals`, y cuyos `runs-on` tomen el nombre del
runner de una variable del repositorio en vez de escribirlo.

El repositorio es público, así que una etiqueta literal publica a cada persona
que lo clona el mapa de una infraestructura que no es suya y que no le sirve
para nada. Un workflow tiene que decir en qué runner corre; no tiene que
decirlo **aquí**, y quien administre la forja declara esas variables una vez.

La frontera, declarada: el directorio `.forgejo/workflows/` se queda. Es la
ruta que la forja exige, y moverlo a `.github/` quitaría la palabra a cambio de
un problema peor, porque GitHub Actions ejecutaría el workflow en el
repositorio público y fallaría por runners que allí no existen.

#### Scenario: Triggers read from disk
- **WHEN** se parsea el workflow del repositorio
- **THEN** declara `push` y `pull_request` acotados a `main`, y
  `workflow_dispatch`

#### Scenario: The five jobs by name
- **WHEN** se parsea el workflow del repositorio
- **THEN** declara los cinco jobs `tests`, `self-spec`, `coverage`,
  `plugin-validate` y `evals`

#### Scenario: No runner label is written down
- **WHEN** se parsea el workflow del repositorio
- **THEN** cada `runs-on` es una expresión que lee una variable del
  repositorio, y ninguno contiene una etiqueta escrita a mano

verifies:   tests/test_ci_workflow.py
confidence: high
from:       README.md#verificar-un-proyecto

### R-CI-018 · The published documentation does not describe the internal CI

WHEN se lee la documentación que el plugin publica a quien lo instala —
`README.md`, `CONTRIBUTING.md`, `docs/**`, `skills/**`, `agents/**`,
`templates/**`, `scripts/**`, `hooks/**`, `.claude-plugin/**` **y el workflow
de CI**—, el sistema DEBE explicar cómo verificar un proyecto nombrando
`scripts/gate.py` y sus códigos de salida, DEBE advertir de que la puerta
ejecuta el `test_command` que declara el proyecto inspeccionado, y DEBE no
nombrar la forja interna de la organización, sus etiquetas de runner ni el
espejo de respaldo.

El workflow entra ahora en el barrido, y ésa es toda la diferencia con la
versión anterior de este requisito. Antes quedaba fuera con un argumento que
era cierto: un workflow **tiene** que decir en qué runner corre. Desde
`R-CI-008` lo dice leyendo una variable del repositorio, así que la excepción
ya no se sostiene y el fichero se mide como cualquier otro: comentarios
incluidos, que son lo primero que lee quien lo abre.

Lo que sigue fuera, y por qué: la capability que especifica el CI y el acta
que apuesta por él viven bajo `.venoxia/`, que es el registro de cómo se
construye Venoxia y no lo que Venoxia hace. Y una precisión incómoda que
conviene no tapar: **una lista de términos prohibidos publica lo que
prohíbe**. Los tres que quedan viven en un solo sitio, el test que los mantiene
fuera de todo lo demás; quitarlos de ahí es quitar el cable trampa.

#### Scenario: The workflow is scanned like everything else
- **WHEN** se leen los ficheros de documentación publicada
- **THEN** el workflow de CI está entre ellos

#### Scenario: The workflow does not name the internal forge
- **WHEN** se lee el texto del workflow, comentarios incluidos
- **THEN** no aparece el nombre de la forja interna en ninguna combinación de
  mayúsculas y minúsculas

#### Scenario: The workflow does not name the internal runner labels
- **WHEN** se lee el texto del workflow, comentarios incluidos
- **THEN** no aparece ninguna de las dos etiquetas del runner interno

verifies:   tests/test_gate.py
confidence: high
from:       README.md#verificar-un-proyecto
