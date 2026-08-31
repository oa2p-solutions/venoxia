#!/usr/bin/env python3
"""Parser de markdown de Venoxia: convierte una especificación en modelo.

Contrato irrenunciable: **este módulo nunca lanza una excepción**. Un fichero
que no existe, bytes que no son UTF-8, un markdown truncado a media línea, un
bloque de código sin cerrar o un encabezado sin ID no rompen nada: todo se
devuelve como `Finding` para que el validador lo cuente y el informe lo explique
en español.

Códigos de hallazgo que emite este módulo:

* `P01` (error)   fichero ilegible, inexistente o fallo inesperado al parsear.
* `P02` (aviso)   clave de metadatos desconocida.
* `P03` (aviso)   clave de metadatos repetida; gana la última.
* `P04` (aviso)   viñeta de un escenario que no encaja en «- **KW** texto».
* `P05` (aviso)   «### …» que no llegó a requisito por caer dentro de una valla.

El `P05` no está en la tabla del contrato §3: es la salvaguarda de último
recurso contra el único fallo que este módulo no puede permitirse. Un requisito
que el parser pierde no se lo puede reprochar ninguna regla del validador, y el
resultado es un «✓ cumple el contrato» sobre una spec rota. Así que cada «### »
que no se convierte en requisito se anuncia.
"""

from __future__ import annotations

import bisect
import os
import re
from pathlib import Path

from .model import (
    META_KEYS,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    Capability,
    Delta,
    Finding,
    Requirement,
    Scenario,
)

# --------------------------------------------------------------------------
# Expresiones regulares de la gramática. Compiladas una sola vez, con nombre,
# porque el parser las recorre línea a línea sobre ficheros enteros.
# --------------------------------------------------------------------------

# Encabezado de requisito: «### R-CHK-014 · Stock reservation». Captura todo lo
# que sigue a las tres almohadillas; el reparto entre ID y título lo hace
# HEADER_ID_RE. El «(?!#)» evita confundirlo con «#### Scenario:».
REQUIREMENT_HEADER_RE = re.compile(r"^###(?!#)\s+(?P<body>\S.*?)\s*$")

# Reparto del encabezado en ID y título. El separador puede ser «·», la raya
# «—», el semicuadratín «–» o el guion «-». El guion exige espacio a los dos
# lados porque también vive dentro del propio ID: sin esa condición,
# «### R-CHK-014» se partiría en «R-CHK» + «014». Si no hay separador, el
# encabezado entero es el título y el requisito se queda sin ID (ya lo dirá V01).
HEADER_ID_RE = re.compile(
    r"^(?P<id>R-[A-Z0-9-]+)(?:\s*[·—–]\s*|\s+-\s+)(?P<title>.+)$"
)

# Encabezado de bloque de un delta: «## ADDED Requirements». La palabra
# «Requirements» es insensible a mayúsculas; el nombre del bloque, no.
BLOCK_HEADER_RE = re.compile(
    r"^##(?!#)\s+(?P<block>ADDED|MODIFIED|REMOVED|RENAMED)\s+(?i:requirements)\s*$"
)

# Cualquier otro encabezado de nivel 1 o 2: cierra el requisito en curso.
SECTION_BREAK_RE = re.compile(r"^#{1,2}(?!#)\s*\S")

# Encabezado de escenario: «#### Scenario: Stock available on every line».
SCENARIO_HEADER_RE = re.compile(r"^####\s+Scenario:\s*(?P<title>.+)$")

# Viñeta bien formada de un escenario: «- **WHEN** hay stock disponible».
# Admite «-» y «*» como marca, y cualquier sangría por delante.
SCENARIO_BULLET_RE = re.compile(r"^\s*[-*]\s+\*\*(?P<kw>[A-Z]+)\*\*\s*(?P<text>.*)$")

# Cualquier viñeta, bien o mal formada. Sirve para detectar las que no encajan
# en SCENARIO_BULLET_RE y merecen un P04. Exige espacio tras la marca, así que
# ni «---» ni «***» (reglas horizontales) cuentan como viñeta.
ANY_BULLET_RE = re.compile(r"^[ \t]*[-*](?:[ \t].*)?$")

# Línea *con forma* de metadato: «verifies:   test/checkout/reservation.spec.ts».
# La clave es una sola palabra al principio de la línea y la sangría no se topa
# aquí: quién es de verdad un metadato lo decide `_metadata_blocks`, no esta
# expresión. El «(?!//)» evita tragarse una URL de la narrativa («https://…» no
# es un metadato).
META_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z][A-Za-z0-9_.-]{0,31})[ \t]*:(?!//)[ \t]*(?P<value>.*?)[ \t]*$"
)

# Delimitador de bloque de código: tres o más acentos graves o virgulillas, con
# la sangría que sea y una etiqueta de lenguaje opcional. La sangría es libre
# porque una valla perfectamente válida de CommonMark vive dentro de una lista
# anidada, sangrada cuatro columnas o más; toparla en tres dejaba sin blindar
# justo esos ejemplos. Quién puede *cerrar* la valla sí mira la sangría: lo
# resuelve `_code_fence_map`.
FENCE_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<marker>`{3,}|~{3,})[ \t]*(?P<info>.*?)[ \t]*$"
)

# Marca de cobertura en un fichero de test: «@covers R-CHK-014», en cualquier
# tipo de comentario y en cualquier parte del fichero.
COVERS_RE = re.compile(r"@covers\s+(R-[A-Z0-9-]+)")

# Encabezado de la sección de propósito de una capability, en inglés o español.
PURPOSE_HEADER_RE = re.compile(r"^##(?!#)\s+(?i:purpose|prop[oó]sito)\s*:?\s*$")

# Cualquier encabezado markdown, para acotar secciones al extraer el propósito.
ANY_HEADING_RE = re.compile(r"^#{1,6}\s")

# Colapsa cualquier racha de espacios en blanco en uno solo.
WHITESPACE_RE = re.compile(r"\s+")

#: Columnas de sangría a partir de las cuales CommonMark deja de leer el
#: comienzo de una construcción y pasa a leer código sangrado. Es el umbral que
#: usan las dos decisiones de este módulo que dependen de la columna: si una
#: línea sangrada abre valla y si abre bloque de metadatos.
MAX_FLUSH_INDENT = 3


# --------------------------------------------------------------------------
# Lectura de ficheros
# --------------------------------------------------------------------------


def read_text(path) -> tuple[str | None, Finding | None]:
    """Lee un fichero de texto UTF-8 sin lanzar nunca.

    Devuelve `(texto, None)` si se pudo leer y `(None, Finding)` con un `P01` en
    cualquier otro caso: ruta inexistente, directorio, permisos, fichero binario
    o bytes que no son UTF-8. La marca de orden de bytes (BOM) se descarta.
    """
    name = _display_path(path)
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError:
        return None, _read_failure(name, "no existe")
    except IsADirectoryError:
        return None, _read_failure(name, "es un directorio, no un fichero markdown")
    except PermissionError:
        return None, _read_failure(name, "no se puede leer por permisos del sistema")
    except OSError as error:
        return None, _read_failure(name, f"no se puede leer ({error.strerror or error})")
    except Exception as error:  # defensa: aquí no puede caerse nada
        return None, _read_failure(name, f"no se puede leer ({type(error).__name__}: {error})")

    if b"\x00" in raw:
        return None, _read_failure(name, "parece un fichero binario (contiene bytes nulos)")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, _read_failure(name, "no está codificado en UTF-8")
    except Exception as error:  # defensa: aquí no puede caerse nada
        return None, _read_failure(
            name, f"no se puede descodificar ({type(error).__name__}: {error})"
        )

    return text, None


def _read_failure(name: str, reason: str) -> Finding:
    """Construye el hallazgo `P01` de un fichero que no se ha podido leer."""
    return Finding(
        rule="P01",
        severity=SEVERITY_ERROR,
        message=f"No se puede leer «{name}»: {reason}.",
        file=name,
        hint="Comprueba que la ruta es correcta y que el fichero es texto UTF-8.",
    )


def _unexpected_finding(error: Exception, source_file: str) -> Finding:
    """Convierte un fallo inesperado del parser en un hallazgo `P01`."""
    where = source_file or "el texto recibido"
    return Finding(
        rule="P01",
        severity=SEVERITY_ERROR,
        message=(
            f"Fallo inesperado al parsear «{where}»: "
            f"{type(error).__name__}: {error}."
        ),
        file=source_file,
        hint=(
            "Revisa el markdown del requisito; si el fichero parece correcto, "
            "es un fallo de Venoxia y conviene reportarlo."
        ),
    )


def _display_path(path) -> str:
    """Representación legible de una ruta para los mensajes; nunca lanza.

    Acepta lo que le echen: una cadena, un `Path`, una ruta en `bytes` —que se
    descodifica con la codificación del sistema de ficheros— o un objeto
    cualquiera, incluido uno cuyo `__fspath__` reviente. Siempre sale una `str`,
    porque todo lo que viene detrás (`Path(...)`, `os.path.relpath(...)`) sí
    lanzaría con `bytes` o con un entero.
    """
    if isinstance(path, str):
        return path
    try:
        candidate = os.fspath(path)
    except Exception:
        return _safe_str(path)
    if isinstance(candidate, str):
        return candidate
    if isinstance(candidate, bytes):
        try:
            return os.fsdecode(candidate)
        except Exception:
            return _safe_str(candidate)
    return _safe_str(candidate)


def _safe_str(value) -> str:
    """`str(valor)` sin arriesgarse a que un `__str__` ajeno lance."""
    try:
        return str(value)
    except Exception:
        return "<ruta ilegible>"


# --------------------------------------------------------------------------
# Parseo de requisitos
# --------------------------------------------------------------------------


def parse_requirements(
    text: str, source_file: str = "", default_block: str | None = None
) -> tuple[list[Requirement], list[Finding]]:
    """Convierte el markdown de una spec o un delta en requisitos.

    Reconoce, en este orden y siempre fuera de los bloques de código:

    * `## ADDED|MODIFIED|REMOVED|RENAMED Requirements` abre un bloque; los
      requisitos que vengan después quedan marcados con él. `default_block`
      dice a qué bloque pertenecen los que aparezcan antes del primero.
    * `### R-CHK-014 · Título` abre un requisito, que se cierra en el siguiente
      encabezado de nivel 1, 2 o 3.
    * `#### Scenario: Título` abre un escenario, y `- **WHEN** …` lo puebla.
    * `verifies:`, `confidence:`, `why:`, `expires:` y `from:` son metadatos
      cuando forman parte de un **bloque de metadatos**, venga antes o después
      de los escenarios. La regla exacta de qué es un bloque —y por qué no vale
      con mirar cada línea por su cuenta— está escrita entera junto a
      `_metadata_blocks`.

    La narrativa es lo que queda entre el encabezado y el primer escenario (o el
    bloque final de metadatos si no hay escenarios), sin las líneas de esos
    bloques y sin líneas en blanco sobrantes al principio ni al final.

    Nunca lanza: devuelve `(requisitos, hallazgos)`.
    """
    try:
        requirements, findings, _ = _parse_document(text, source_file, default_block)
        return requirements, findings
    except Exception as error:  # defensa: el parser nunca propaga
        return [], [_unexpected_finding(error, source_file)]


def _parse_document(
    text: str, source_file: str, default_block: str | None
) -> tuple[list[Requirement], list[Finding], list[tuple[str, int]]]:
    """Recorrido único del documento.

    Devuelve los requisitos, los hallazgos y los bloques declarados en orden de
    aparición (nombre y línea), que es lo que `parse_delta` necesita para saber
    qué bloques existen aunque estén vacíos.
    """
    requirements: list[Requirement] = []
    findings: list[Finding] = []
    declared_blocks: list[tuple[str, int]] = []
    if not text:
        return requirements, findings, declared_blocks

    lines = text.splitlines()
    in_code = _code_fence_map(lines)
    block = _normalized_block(default_block)
    headers: list[tuple[int, str | None]] = []
    boundaries: list[int] = []

    try:
        for index, line in enumerate(lines):
            if in_code[index]:
                continue
            block_match = BLOCK_HEADER_RE.match(line)
            if block_match:
                block = block_match.group("block").upper()
                declared_blocks.append((block, index + 1))
                boundaries.append(index)
                continue
            if REQUIREMENT_HEADER_RE.match(line):
                headers.append((index, block))
                boundaries.append(index)
                continue
            if SECTION_BREAK_RE.match(line):
                boundaries.append(index)

        for start, requirement_block in headers:
            end = _next_boundary(boundaries, start, len(lines))
            requirements.append(
                _parse_requirement(
                    lines, in_code, start, end, source_file, requirement_block, findings
                )
            )
        findings.extend(_hidden_heading_findings(lines, in_code, source_file))
    except Exception as error:  # defensa: se devuelve lo parseado hasta aquí
        findings.append(_unexpected_finding(error, source_file))

    return requirements, findings, declared_blocks


def _normalized_block(block: str | None) -> str | None:
    """Normaliza el bloque por defecto a mayúsculas, o lo deja en `None`."""
    if isinstance(block, str) and block.strip():
        return block.strip().upper()
    return None


def _next_boundary(boundaries: list[int], start: int, total: int) -> int:
    """Índice de la línea donde termina el requisito que empieza en `start`."""
    position = bisect.bisect_right(boundaries, start)
    if position < len(boundaries):
        return boundaries[position]
    return total


# --------------------------------------------------------------------------
# LA REGLA DE LAS VALLAS — léela antes de tocar `_code_fence_map`.
#
# Aquí se decide qué líneas del documento son código y, por tanto, dejan de ser
# gramática. Equivocarse por exceso tiene una consecuencia mucho peor que
# equivocarse por defecto: un bloque de código mal leído se cobra un hallazgo
# molesto, pero un requisito que la valla se traga **desaparece del modelo**, y
# ninguna regla puede quejarse de un requisito que no ve. Ese fallo se manifestó
# como un «✓ La especificación cumple el contrato» con exit 0 sobre una spec que
# tenía tres errores: la valla huérfana de un requisito se había comido enteros
# los dos siguientes. Por eso, ante la duda, **no se pierde un requisito**.
#
# De ahí las cuatro decisiones de este bloque:
#
#   1. **Pareja compatible.** Una valla sólo la cierra otra del mismo carácter,
#      al menos igual de larga, sin etiqueta de lenguaje y **con su sangría o
#      más**, hasta tres columnas por encima. Las cuatro primeras columnas son
#      una sola banda —CommonMark deja abrir y cerrar a ras con hasta tres
#      espacios—, así que dentro de esa banda la sangría no distingue. Lo que la
#      versión anterior hacía era buscar la pareja **en todo el documento y sin
#      mirar hacia abajo**: cualquier «```» legítimo posterior daba por buena una
#      valla sangrada y huérfana, que entonces se tragaba encabezados y
#      metadatos hasta encontrarlo.
#      Caso que esta regla sacrifica a conciencia: una valla abierta con cinco
#      columnas y cerrada con cuatro se lee como huérfana. Su contenido se
#      interpretará como prosa —ruido—, que es el lado barato del error.
#   2. **Se empareja con la primera pareja, no con la última.** El bloque acaba
#      en el primer cierre compatible que viene después.
#   3. **La pareja de una valla sin etiqueta no está más allá del siguiente
#      encabezado de requisito.** Ésta es la decisión que de verdad cierra el
#      agujero, porque el punto 1 sólo tapaba media variante: dos «```»
#      sangrados y sueltos de requisitos distintos —o uno suelto y el cierre de
#      un ejemplo legítimo de más abajo— tienen la misma forma y se emparejaban
#      igual, tragándose los requisitos de en medio.
#      La excepción de la etiqueta es la única señal honesta que da el texto: al
#      escribir «```markdown» el autor declara que lo de dentro es un ejemplo, y
#      entonces sí puede envolver un «### » —que es justo lo que el contrato §3
#      pide de un bloque de código bien cerrado—. Sin etiqueta no hay tal
#      declaración, y entre creer a una valla anónima y conservar un requisito,
#      se conserva el requisito.
#      Precio, con su test: una valla **sin etiqueta** que envuelve un «### »
#      escrito a ras deja de blindarlo, y ese encabezado se lee como requisito.
#      Cuesta un requisito de mentira con sus hallazgos —ruidoso y visible—, no
#      un requisito de verdad desaparecido.
#   4. **Una valla huérfana no se traga un encabezado de requisito.** Si no hay
#      pareja, la valla sangrada no abre nada (para CommonMark, con cuatro
#      columnas sólo es valla dentro de una lista) y la escrita a ras abre un
#      bloque que **termina en el siguiente «### » o «## … Requirements»**. Así,
#      no cerrar una valla cuesta como mucho la cola del requisito en curso —que
#      se cobrará su V06 bien visible—, nunca los requisitos de detrás.
#
# La frontera de los puntos 3 y 4 es estrecha a propósito: sólo paran a la valla
# los encabezados de nivel de requisito. Un «# comentario» de un ejemplo de
# shell no la para, porque eso sí sería romper bloques de código legítimos.
# --------------------------------------------------------------------------


def _code_fence_map(lines: list[str]) -> list[bool]:
    """Marca qué líneas caen dentro de un bloque de código.

    Recorre el documento saltando de valla en valla: cada apertura busca su
    primera pareja compatible (`_closes`) y el bloque va de una a otra. La
    búsqueda llega hasta el siguiente encabezado de requisito, salvo que la valla
    lleve etiqueta de lenguaje. Sin pareja manda el punto 4 de la regla: la valla
    sangrada no abre nada y la valla a ras abre hasta ese mismo encabezado.

    Las líneas marcadas aquí no se miran para nada más: ni encabezados, ni
    metadatos, ni viñetas.
    """
    total = len(lines)
    in_code = [False] * total
    closers = _closing_candidates(lines)
    headings = _requirement_heading_lines(lines)
    reachable: dict[tuple[str, int, int], list[int]] = {}
    index = 0
    while index < total:
        fence = FENCE_RE.match(lines[index])
        if fence is None:
            index += 1
            continue
        marker = fence.group("marker")
        opener = (marker[0], len(marker), _indent_width(fence.group("indent")))
        heading = _next_heading(headings, index, total)
        limit = total if fence.group("info") else heading
        closing = _first_closing_fence(closers, reachable, opener, index, limit)
        if closing is not None:
            for position in range(index, closing + 1):
                in_code[position] = True
            index = closing + 1
            continue
        if opener[2] > MAX_FLUSH_INDENT:
            # Valla sangrada y huérfana: es texto, no abre bloque ninguno.
            index += 1
            continue
        for position in range(index, heading):
            in_code[position] = True
        index = heading
    return in_code


def _requirement_heading_lines(lines: list[str]) -> list[int]:
    """Índices de los encabezados de nivel de requisito, en orden.

    Son la frontera que ninguna valla cruza sin permiso: el «### …» de un
    requisito y el «## ADDED Requirements» que abre un bloque de delta. Se
    calculan una vez por documento y se consultan con búsqueda binaria.
    """
    return [
        index
        for index, line in enumerate(lines)
        if REQUIREMENT_HEADER_RE.match(line) or BLOCK_HEADER_RE.match(line)
    ]


def _next_heading(headings: list[int], index: int, total: int) -> int:
    """Primer encabezado de requisito posterior a `index`, o el final del texto."""
    spot = bisect.bisect_right(headings, index)
    if spot < len(headings):
        return headings[spot]
    return total


def _closing_candidates(lines: list[str]) -> list[tuple[int, str, int, int]]:
    """Vallas del documento que podrían cerrar algo: `(índice, carácter, largo, sangría)`.

    Una valla con etiqueta de lenguaje abre, pero nunca cierra; se descarta aquí
    para no volver a mirarla en cada búsqueda.
    """
    candidates: list[tuple[int, str, int, int]] = []
    for index, line in enumerate(lines):
        fence = FENCE_RE.match(line)
        if fence is None or fence.group("info"):
            continue
        marker = fence.group("marker")
        candidates.append(
            (index, marker[0], len(marker), _indent_width(fence.group("indent")))
        )
    return candidates


def _first_closing_fence(
    closers: list[tuple[int, str, int, int]],
    reachable: dict[tuple[str, int, int], list[int]],
    opener: tuple[str, int, int],
    index: int,
    limit: int,
) -> int | None:
    """Índice de la primera valla que cierra la abierta en `index`, o `None`.

    `limit` acota hasta dónde vale la pena buscar: para una valla sin etiqueta,
    el siguiente encabezado de requisito. Qué vallas pueden cerrar depende sólo
    de la **forma** de la que abre, no de dónde esté, así que la lista de índices
    compatibles se calcula una vez por forma y después basta una búsqueda
    binaria. Un fichero con miles de vallas iguales hace así un solo recorrido en
    vez de miles.
    """
    positions = reachable.get(opener)
    if positions is None:
        positions = [
            candidate[0] for candidate in closers if _closes(opener, candidate)
        ]
        reachable[opener] = positions
    spot = bisect.bisect_right(positions, index)
    if spot < len(positions) and positions[spot] < limit:
        return positions[spot]
    return None


def _closes(opener: tuple[str, int, int], candidate: tuple[int, str, int, int]) -> bool:
    """¿La valla `candidate` es pareja compatible de la abierta con forma `opener`?"""
    character, length, indent = opener
    _, candidate_character, candidate_length, candidate_indent = candidate
    if candidate_character != character or candidate_length < length:
        return False
    if candidate_indent > indent + MAX_FLUSH_INDENT:
        return False
    return _fence_band(candidate_indent) >= _fence_band(indent)


def _fence_band(indent: int) -> int:
    """Banda de sangría de una valla: las cuatro primeras columnas son una sola.

    CommonMark deja abrir y cerrar un bloque «a ras» con hasta tres espacios de
    cortesía, así que entre 0 y 3 la sangría no distingue nada. A partir de ahí
    sí: una valla de una lista anidada no la cierra una escrita en el margen.
    """
    return 0 if indent <= MAX_FLUSH_INDENT else indent


def _hidden_heading_findings(
    lines: list[str], in_code: list[bool], source_file: str
) -> list[Finding]:
    """Salvaguarda de último recurso: avisa de cada «### » que no llegó a requisito.

    Es la red que se pone debajo de todo lo anterior. Si alguna vez una valla
    vuelve a esconder un encabezado de requisito —por un fallo de este módulo o
    por un markdown que nadie previó—, el requisito ya no desaparece en silencio:
    sale un `P05` con su línea. Un aviso de más es barato; un requisito invisible
    es un falso verde del validador.

    Salta también con el ejemplo perfectamente cerrado que enseña un «### »
    dentro de una valla, y está bien que así sea: desde fuera, un encabezado que
    no es requisito y un requisito que se ha perdido se escriben igual, y sólo el
    autor puede decir cuál de los dos es.
    """
    findings: list[Finding] = []
    for index, line in enumerate(lines):
        if not in_code[index]:
            continue
        header = REQUIREMENT_HEADER_RE.match(line)
        if header is None:
            continue
        findings.append(
            Finding(
                rule="P05",
                severity=SEVERITY_WARNING,
                message=(
                    f"El encabezado «{header.group('body').strip()}» no se ha leído como "
                    "requisito: cae dentro de un bloque de código."
                ),
                file=source_file,
                line=index + 1,
                hint=(
                    "Si es un ejemplo, no hay nada que hacer. Si es un requisito de "
                    "verdad, sácalo del bloque o cierra la valla ``` que lo envuelve."
                ),
            )
        )
    return findings


def _indent_width(line: str) -> int:
    """Columnas de sangría de una línea, contando el tabulador de cuatro en cuatro."""
    width = 0
    for character in line:
        if character == " ":
            width += 1
        elif character == "\t":
            width += 4 - (width % 4)
        else:
            break
    return width


def _parse_requirement(
    lines: list[str],
    in_code: list[bool],
    start: int,
    end: int,
    source_file: str,
    block: str | None,
    findings: list[Finding],
) -> Requirement:
    """Parsea un requisito: encabezado, escenarios, metadatos y narrativa."""
    header = lines[start]
    header_match = REQUIREMENT_HEADER_RE.match(header)
    body = header_match.group("body").strip() if header_match else header.lstrip("#").strip()

    id_match = HEADER_ID_RE.match(body)
    if id_match:
        requirement_id: str | None = id_match.group("id")
        title = id_match.group("title").strip()
    else:
        # Sin separador no hay ID que valga: todo el encabezado es el título.
        requirement_id = None
        title = body

    requirement = Requirement(
        id=requirement_id,
        title=title,
        line=start + 1,
        narrative="",
        source_file=source_file,
        block=block,
        raw_header=header.rstrip(),
    )

    candidates = _meta_candidates(lines, in_code, start + 1, end)
    meta_indices = _metadata_blocks(lines, candidates)
    first_scenario: int | None = None
    scenario: Scenario | None = None

    for index in range(start + 1, end):
        if in_code[index]:
            continue
        line = lines[index]

        scenario_match = SCENARIO_HEADER_RE.match(line)
        if scenario_match:
            scenario = Scenario(title=scenario_match.group("title").strip(), line=index + 1)
            requirement.scenarios.append(scenario)
            if first_scenario is None:
                first_scenario = index
            continue

        meta = candidates.get(index)
        if meta is not None:
            key, value = meta
            if index in meta_indices:
                # Dentro del bloque: la línea sale de la narrativa pase lo que
                # pase. Si la clave es de las cinco, se guarda; si no, se lleva
                # su P02 y se pierde, pero no vuelve a la prosa (contrato §3).
                _record_meta(requirement, key, value, index + 1, source_file, findings)
            elif key not in META_KEYS:
                # Fuera del bloque no hay metadato que valga: es prosa con dos
                # puntos. Una clave desconocida se lleva igualmente su P02 —lo
                # pide el contrato— y se queda donde estaba.
                findings.append(
                    _unknown_key_finding(requirement, key, index + 1, source_file)
                )
            continue

        if scenario is None:
            continue

        bullet = SCENARIO_BULLET_RE.match(line)
        if bullet:
            scenario.bullets.append((bullet.group("kw").upper(), bullet.group("text").strip()))
            continue
        if ANY_BULLET_RE.match(line):
            findings.append(
                Finding(
                    rule="P04",
                    severity=SEVERITY_WARNING,
                    message=(
                        f"Viñeta mal formada en el escenario «{scenario.title}»: "
                        "no encaja en «- **PALABRA** texto»."
                    ),
                    file=source_file,
                    line=index + 1,
                    requirement_id=requirement.id,
                    hint="Escribe la viñeta como «- **WHEN** …» o «- **THEN** …».",
                )
            )

    requirement.narrative = _extract_narrative(
        lines, in_code, start + 1, end, first_scenario, meta_indices
    )
    return requirement


def _match_meta(line: str) -> tuple[str, str] | None:
    """Devuelve `(clave, valor)` si la línea tiene forma de metadato."""
    match = META_LINE_RE.match(line)
    if not match:
        return None
    return match.group("key"), match.group("value").strip()


def _meta_candidates(
    lines: list[str], in_code: list[bool], start: int, end: int
) -> dict[int, tuple[str, str]]:
    """Índice → `(clave, valor)` de las líneas del cuerpo con forma de metadato.

    Sólo forma: aquí no se decide todavía cuáles son metadatos de verdad. Lo que
    cae dentro de una valla de código no se mira siquiera.
    """
    candidates: dict[int, tuple[str, str]] = {}
    for index in range(start, end):
        if in_code[index]:
            continue
        meta = _match_meta(lines[index])
        if meta is not None:
            candidates[index] = meta
    return candidates


# --------------------------------------------------------------------------
# LA REGLA DEL BLOQUE DE METADATOS — léela antes de tocar nada de aquí abajo.
#
# La pregunta que hay que contestar aquí es una sola: **¿qué distingue una línea
# de metadatos de una línea de prosa que se le parece?** Se ha contestado mal dos
# veces. «Su forma» —cualquier «Palabra: texto» es metadato— borraba de la
# narrativa cualquier «Nota: …». «Su forma y su vecindad» —toda una racha
# contigua de «clave: valor» con alguna clave conocida es metadato— seguía
# borrando la prosa que tuviera la mala suerte de estar **pegada** al bloque, sin
# una línea en blanco de por medio.
#
# La respuesta que se sostiene es la tercera: lo que distingue a un metadato es
# **su clave**. El contrato §3 escribe el bloque con las cinco claves y sólo con
# ellas (`verifies|confidence|why|expires|from`); nada más es un metadato. La
# vecindad no promueve prosa a metadato, sólo sirve para lo contrario: para
# entender que lo que cae **entre** dos claves reconocidas forma parte del mismo
# bloque aunque su clave no esté en la lista.
#
# De ahí la regla, en tres condiciones:
#
#   1. **Racha contigua.** Se parte el cuerpo del requisito en rachas de líneas
#      con forma «clave: valor», una detrás de otra. Corta la racha cualquier
#      cosa que no la tenga: una línea en blanco, prosa, una viñeta, un
#      encabezado o una línea de dentro de una valla.
#   2. **El bloque va de la primera clave conocida a la última.** Dentro de una
#      racha, el bloque de metadatos empieza en la primera línea cuya clave está
#      en META_KEYS y acaba en la última. Lo que queda por fuera —por delante o
#      por detrás— es prosa, aunque esté pegado. Una racha sin ninguna clave
#      conocida no es un bloque: es prosa con dos puntos.
#   3. **El bloque abre a ras.** Esa primera clave conocida no lleva más de tres
#      columnas de sangría, el umbral con el que CommonMark deja de leer el
#      comienzo de una construcción. Las demás líneas del bloque van con la
#      sangría que quieran: ésa es la cosmética que el contrato manda ignorar.
#
# Los casos que delimitan la regla, todos con su test:
#
# * «Nota: el sistema reserva el stock.» justo encima de «verifies:» → prosa: la
#   racha empieza antes de la primera clave conocida. Se lleva su P02 y **se
#   queda en la narrativa**. Igual pegada por debajo del bloque, e igual separada
#   por una línea en blanco: las cuatro combinaciones dan lo mismo, que es lo que
#   se le pide a una regla.
# * «owner: alice» **entre** «verifies:» y «from:» → metadato del bloque: emite
#   su P02, no entra en `meta` y no vuelve a la narrativa. Desde fuera no hay
#   forma de distinguirlo de un metadato mal escrito, y en esa posición lo más
#   probable es justo eso.
# * Una de las cinco claves pegada al bloque —«from: …» encima de «verifies: …»—
#   es metadato, esté pegada o separada. Con la clave buena no hay ambigüedad que
#   resolver: por eso la regla mira la clave y no la distancia.
# * «            confidence: xxxxx» de una tabla de ejemplo → no abre bloque
#   (condición 3) y no pisa el `confidence` de verdad.
#
# Lo que esta regla no puede distinguir, y se asume a conciencia: un bloque de
# ejemplo escrito a ras de margen, sin valla y con claves reconocidas, sigue
# leyéndose como metadato. Para eso está la valla ```; documentarlo es más
# honesto que inventar una heurística que falle en el caso legítimo.
# --------------------------------------------------------------------------


def _metadata_blocks(
    lines: list[str], candidates: dict[int, tuple[str, str]]
) -> set[int]:
    """Índices de las líneas que pertenecen a un bloque de metadatos."""
    inside: set[int] = set()
    run: list[int] = []

    def close_run() -> None:
        """Cierra la racha en curso y se queda con el tramo que sea bloque."""
        inside.update(_metadata_span(lines, candidates, run))
        run.clear()

    for index in sorted(candidates):
        if run and index != run[-1] + 1:
            close_run()
        run.append(index)
    close_run()
    return inside


def _metadata_span(
    lines: list[str], candidates: dict[int, tuple[str, str]], run: list[int]
) -> list[int]:
    """Tramo de una racha contigua que es de verdad el bloque de metadatos.

    De la primera clave reconocida **a ras** a la última reconocida, ambas
    incluidas. Si la racha no trae ninguna reconocida, o ninguna a ras, no hay
    bloque: toda la racha es prosa. Que el bloque abra en la primera a ras y no
    en la primera a secas evita perder un «confidence:» de verdad porque encima
    de él hubiera un ejemplo sangrado con una clave reconocida.
    """
    known = [index for index in run if candidates[index][0] in META_KEYS]
    flush = [index for index in known if _indent_width(lines[index]) <= MAX_FLUSH_INDENT]
    if not flush:
        return []
    return [index for index in run if flush[0] <= index <= known[-1]]


def _unknown_key_finding(
    requirement: Requirement, key: str, line_number: int, source_file: str
) -> Finding:
    """Construye el aviso `P02` de una clave de metadatos desconocida."""
    return Finding(
        rule="P02",
        severity=SEVERITY_WARNING,
        message=f"Clave de metadatos desconocida «{key}»: Venoxia la ignora.",
        file=source_file,
        line=line_number,
        requirement_id=requirement.id,
        hint=(
            "Usa una de las claves reconocidas, en minúsculas: "
            + ", ".join(META_KEYS)
            + "."
        ),
    )


def _record_meta(
    requirement: Requirement,
    key: str,
    value: str,
    line_number: int,
    source_file: str,
    findings: list[Finding],
) -> None:
    """Guarda un metadato del bloque y avisa de claves desconocidas o repetidas."""
    if key not in META_KEYS:
        findings.append(_unknown_key_finding(requirement, key, line_number, source_file))
        return

    if key in requirement.meta:
        findings.append(
            Finding(
                rule="P03",
                severity=SEVERITY_WARNING,
                message=(
                    f"La clave de metadatos «{key}» aparece más de una vez en el requisito; "
                    "se conserva el último valor."
                ),
                file=source_file,
                line=line_number,
                requirement_id=requirement.id,
                hint=f"Deja una sola línea «{key}:» por requisito.",
            )
        )

    requirement.meta[key] = value
    requirement.meta_lines[key] = line_number


def _extract_narrative(
    lines: list[str],
    in_code: list[bool],
    start: int,
    end: int,
    first_scenario: int | None,
    meta_indices: set[int],
) -> str:
    """Devuelve la prosa del requisito, limpia de metadatos y de blancos sobrantes.

    La narrativa llega hasta el primer escenario; si no hay escenarios, hasta el
    bloque de metadatos que cierra el requisito. Lo que esté dentro de un bloque
    de código se copia literal, sin recortarle nada.
    """
    if first_scenario is not None:
        stop = first_scenario
    else:
        stop = _trailing_meta_start(lines, in_code, start, end, meta_indices)

    collected: list[str] = []
    for index in range(start, stop):
        if index in meta_indices:
            continue
        collected.append(lines[index] if in_code[index] else lines[index].rstrip())

    while collected and not collected[0].strip():
        collected.pop(0)
    while collected and not collected[-1].strip():
        collected.pop()

    return "\n".join(collected).strip()


def _trailing_meta_start(
    lines: list[str],
    in_code: list[bool],
    start: int,
    end: int,
    meta_indices: set[int],
) -> int:
    """Índice donde arranca el bloque de metadatos final, o `end` si no lo hay."""
    first_meta = end
    index = end - 1
    while index >= start:
        if in_code[index]:
            break
        if not lines[index].strip():
            index -= 1
            continue
        if index in meta_indices:
            first_meta = index
            index -= 1
            continue
        break
    return first_meta


# --------------------------------------------------------------------------
# Capabilities y deltas
# --------------------------------------------------------------------------


def parse_capability(
    path: str | Path, root: str | Path = "."
) -> tuple[Capability, list[Finding]]:
    """Lee una capability viva (`spec.md`) y devuelve su modelo y sus hallazgos.

    El nombre sale del directorio que la contiene (`capabilities/checkout/spec.md`
    → `checkout`); si el fichero no se llama `spec.md`, del nombre del fichero.
    Si no se puede leer, devuelve la capability vacía y un `P01`.
    """
    # El nombre y la ruta relativa se calculan **dentro** del `try`: son las dos
    # únicas líneas que quedaban fuera y bastaba una ruta en `bytes` para que se
    # escapara un `TypeError` y el parser rompiera su promesa de no lanzar.
    relative = ""
    capability = Capability(name="", path="")
    try:
        relative = _relative_path(path, root)
        capability = Capability(name=_capability_name(path), path=relative)
        text, failure = read_text(path)
        if failure is not None:
            failure.file = relative
            return capability, [failure]
        requirements, findings = parse_requirements(text or "", source_file=relative)
        capability.requirements = requirements
        capability.purpose = _extract_purpose(text or "")
        return capability, findings
    except Exception as error:  # defensa: el parser nunca propaga
        return capability, [_unexpected_finding(error, relative)]


def parse_delta(path: str | Path, root: str | Path = ".") -> tuple[Delta, list[Finding]]:
    """Lee un delta y agrupa sus requisitos por bloque.

    `blocks` contiene exactamente los bloques declarados en el fichero, incluso
    los que no traen requisitos. Un requisito escrito antes del primer bloque no
    pertenece a ninguno y se queda fuera: es un delta mal formado y V12 lo dirá.
    """
    # Igual que en `parse_capability`: nada se calcula fuera del `try`.
    relative = ""
    delta = Delta(capability="", path="")
    try:
        relative = _relative_path(path, root)
        delta = Delta(capability=_delta_name(path), path=relative)
        text, failure = read_text(path)
        if failure is not None:
            failure.file = relative
            return delta, [failure]
        requirements, findings, declared_blocks = _parse_document(text or "", relative, None)
        for name, _line in declared_blocks:
            delta.blocks.setdefault(name, [])
        for requirement in requirements:
            if requirement.block:
                delta.blocks.setdefault(requirement.block, []).append(requirement)
        return delta, findings
    except Exception as error:  # defensa: el parser nunca propaga
        return delta, [_unexpected_finding(error, relative)]


def find_covers(text: str) -> set[str]:
    """Devuelve los IDs marcados con «@covers» en un fichero de test."""
    if not text:
        return set()
    try:
        return set(COVERS_RE.findall(text))
    except Exception:  # defensa: el parser nunca propaga
        return set()


def _capability_name(path: str | Path) -> str:
    """Nombre de la capability: su directorio si el fichero es `spec.md`."""
    target = Path(_display_path(path))
    if target.stem.lower() == "spec" and target.parent.name:
        return target.parent.name
    return target.stem or target.name


def _delta_name(path: str | Path) -> str:
    """Nombre de la capability a la que afecta un delta: el del fichero."""
    target = Path(_display_path(path))
    return target.stem or target.name


def _relative_path(path: str | Path, root: str | Path) -> str:
    """Ruta del fichero relativa a la raíz del proyecto, para los mensajes."""
    text = _display_path(path)
    try:
        relative = os.path.relpath(os.path.abspath(text), os.path.abspath(_display_path(root)))
    except Exception:
        # Cualquier fallo —una ruta imposible, un `root` absurdo— se resuelve
        # enseñando la ruta tal cual: el parser no lanza ni por esto.
        return text
    if relative.startswith(".."):
        # Fuera de la raíz: es más útil enseñar la ruta tal cual se pidió.
        return text
    return relative


def _extract_purpose(text: str) -> str:
    """Extrae el propósito de una capability: la sección «## Purpose».

    Si no hay tal sección, se queda con el primer párrafo del documento anterior
    a cualquier sección. Es informativo: ninguna regla depende de él.
    """
    if not text:
        return ""
    lines = text.splitlines()
    in_code = _code_fence_map(lines)

    for index, line in enumerate(lines):
        if in_code[index]:
            continue
        if PURPOSE_HEADER_RE.match(line):
            return _first_paragraph(lines, in_code, index + 1)

    return _document_intro(lines, in_code)


def _first_paragraph(lines: list[str], in_code: list[bool], start: int) -> str:
    """Primer párrafo a partir de `start`, colapsado en una sola línea."""
    collected: list[str] = []
    for index in range(start, len(lines)):
        line = lines[index]
        if not in_code[index] and ANY_HEADING_RE.match(line):
            break
        if not line.strip():
            if collected:
                break
            continue
        collected.append(line.strip())
    return _collapse(" ".join(collected))


def _document_intro(lines: list[str], in_code: list[bool]) -> str:
    """Párrafo introductorio del documento, saltándose el título de nivel 1."""
    collected: list[str] = []
    for index, line in enumerate(lines):
        if not in_code[index] and ANY_HEADING_RE.match(line):
            if collected:
                break
            if line.startswith("# "):
                continue
            break
        if not line.strip():
            if collected:
                break
            continue
        collected.append(line.strip())
    return _collapse(" ".join(collected))


def _collapse(text: str) -> str:
    """Colapsa los espacios en blanco de un texto en una sola línea."""
    return WHITESPACE_RE.sub(" ", text).strip()
