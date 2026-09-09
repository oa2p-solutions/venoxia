#!/usr/bin/env python3
"""El guardián de Venoxia: hook «PreToolUse» para «Edit|Write|NotebookEdit».

Lee el payload del hook por la entrada estándar, decide si la edición puede
seguir adelante y escribe la decisión en JSON por la salida estándar.

**La garantía, en una frase: pase lo que pase, el guardián termina con código 0
y por su stdout ha salido exactamente un documento JSON parseable con una
decisión válida.** Las dos mitades se sostienen aparte, porque contra un stdout
que no admite escritura —un descriptor cerrado, un pipe sin lector— no hay
decisión que valga: el código 0 se cumple **siempre**, y el documento único
siempre que en stdout se pueda escribir algo. Para el cliente, un código
distinto de 0 y de 2 es «error no bloqueante del hook» y la edición sigue: por
eso terminar con 120 porque quedaron bytes sin vaciar es tan grave como no
decidir. Véase «exit_now».

Tres propiedades mandan sobre cualquier otra consideración:

1. **Por stdout sale siempre exactamente una decisión válida.** Un hook
   «PreToolUse» que no escribe nada no ha decidido nada, y la edición sigue
   adelante: un «deny» que no se imprime es una escritura consentida. Por eso la
   decisión se serializa con «ensure_ascii=True» y se vuelca **ya codificada** a
   «sys.stdout.buffer», sin depender de la codificación del envoltorio de texto
   («PYTHONIOENCODING=ascii», «LC_ALL=C») ni de que la ruta editada sea texto
   Unicode legal (un surrogate suelto en «file_path» reventaba la escritura).
   El testigo de emisión se marca **después** de que el «write» y el «flush»
   hayan ido bien, nunca antes. La entrada corre la misma suerte: el payload se
   lee en bytes y se decodifica como UTF-8, porque leerlo por el envoltorio de
   texto hacía que un acento en la ruta tumbara la lectura y convirtiera el
   «deny» en «allow». Y la traza de stderr, que es un extra, jamás puede
   impedir que la decisión salga: véase «write_stderr».
2. **Fail-open absoluto ante los errores del guardián.** Cualquier error
   interno —entrada vacía, JSON malformado, permisos denegados, una ruta
   imposible— se traduce en «allow» y una traza por stderr. Un guardián que
   rompe el flujo de trabajo por un fallo propio se desinstala el primer día.
   Ojo a la distinción, que es justo donde se abría el agujero y por donde se
   volvió a cerrar de más: un fichero del **usuario** que está mal (un
   «change.json» con JSON corrupto) no es un error del guardián, es una
   respuesta que no acredita nada y no da derecho a pasar; un fallo de
   **entrada/salida** al leer ese mismo fichero (permisos denegados, un
   montaje caído, un «change.json» que resultó ser un directorio) sí es
   nuestro, y se permite. Véase «find_active_change».
3. **Presupuesto de latencia por debajo de 100 ms.** Sin red, sin recorrer el
   repositorio, sin importar el resto de los módulos de Venoxia ni ejecutar el
   validador. Sólo un «scandir» de un nivel sobre «.venoxia/changes/», la
   lectura de los «change.json» que hagan falta y, cuando un cambio se declara
   validado, un «scandir» de su «delta/». La ruta editada se clasifica con
   aritmética de cadenas, sin tocar el disco; sólo cuando esa aritmética dice
   «fuera del proyecto» —el caso raro— se pagan los «realpath» y los «stat»
   que comparan por identidad de fichero (véase «relative_to_root»).
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback

# --- Constantes de protocolo y de disposición en disco -----------------------

HOOK_EVENT_NAME = "PreToolUse"
DECISION_ALLOW = "allow"
DECISION_DENY = "deny"

VENOXIA_DIRNAME = ".venoxia"
CHANGES_DIRNAME = "changes"
CHANGE_FILENAME = "change.json"
DELTA_DIRNAME = "delta"
DELTA_SUFFIX = ".md"
DRIFT_DIRNAME = "drift"
DRIFT_LOG_FILENAME = "direct.log"

STATE_SPECIFIED = "specified"
STATE_VALIDATED = "validated"
STATE_ARCHIVED = "archived"
VIA_DIRECT = "direct"

# La línea «verifies:» de un requisito, a ras de margen, como la escribe el
# parser del validador; el valor admite varias rutas separadas por coma o
# espacio (la misma partición que aplica el validador). Se leen con un regex y
# no con el parser a propósito: el guardián no importa el paquete compartido.
VERIFIES_LINE_RE = re.compile(r"^verifies:[ \t]*(\S[^\r\n]*)$", re.MULTILINE)
VERIFIES_SPLIT_RE = re.compile(r"[,\s]+")

# Rutas relativas que se muestran en los mensajes al usuario.
DRIFT_LOG_DISPLAY = f"{VENOXIA_DIRNAME}/{DRIFT_DIRNAME}/{DRIFT_LOG_FILENAME}"
CHANGES_DISPLAY = f"{VENOXIA_DIRNAME}/{CHANGES_DIRNAME}/"

# Directorios **de primer nivel** cuyo contenido es siempre especificación o
# material previo a ella. Anclados a la raíz del proyecto a propósito: sin el
# anclaje, un «mkdir src/prfaq» bastaría para sacar del alcance del guardián
# cualquier fichero, de cualquier extensión, metido dentro.
SPEC_DIR_NAMES = frozenset({VENOXIA_DIRNAME, "prfaq"})
# El markdown es documentación vaya donde vaya: no tiene comportamiento que
# vigilar. Sólo «.md»; «.mdx» puede llevar JSX, y eso ya es código.
MARKDOWN_SUFFIX = ".md"

# Clave de ruta preferida por herramienta; el resto de claves quedan de reserva.
PATH_KEYS_BY_TOOL = {"NotebookEdit": ("notebook_path", "file_path")}
PATH_KEYS_DEFAULT = ("file_path", "notebook_path")

# Topes defensivos: acotan el peor caso sin afectar a ningún proyecto real.
MAX_CHANGE_ENTRIES = 512      # «change.json» que se miran, del más reciente al más viejo
MAX_CHANGE_BYTES = 1 << 20    # 1 MiB: por encima de eso el fichero no es nuestro
MAX_DELTA_ENTRIES = 512       # entradas de «delta/» que se miran antes de rendirse
MAX_ID_LENGTH = 120           # un «id» más largo que esto no se enseña en un mensaje
MAX_IDENTITY_HOPS = 128       # ancestros que se miran al comparar por inodo

# Resultados de la búsqueda del cambio activo.
CHANGE_NONE = "none"          # no hay ningún cambio activo
CHANGE_FOUND = "found"        # hay cambio activo y su estado se pudo leer
CHANGE_BROKEN = "broken"      # había cambios, pero su JSON está corrupto: no acreditan nada
CHANGE_UNREADABLE = "io"      # fallo de E/S al mirarlos: es un fallo **nuestro**

# Marcas del diario de deriva: dicen **por qué** se permitió sin respaldo firme.
NOTE_VALIDATED_WITHOUT_DELTA = "validated-sin-delta"
NOTE_DELTA_UNCHECKED = "delta-no-comprobable"
NOTE_CHANGE_UNREADABLE = "change-no-legible"

# --- Mensajes ----------------------------------------------------------------

REASON_NOT_ADOPTED = (
    f"Venoxia no está adoptado en este proyecto (no existe «{VENOXIA_DIRNAME}/»): "
    "el guardián no interviene."
)
REASON_NO_PATH = (
    "Venoxia: la herramienta no declara ninguna ruta de fichero, "
    "así que no hay nada que comprobar."
)
REASON_FALLBACK = (
    "Venoxia: el guardián ha fallado y permite la edición por diseño (fail-open). "
    "La traza del error está en stderr."
)

# Razones de reserva **sólo ASCII**, sin acentos a propósito: son el penúltimo
# escalón de la emisión, el que se usa si la razón de verdad no se pudo
# serializar. Que el texto se lea peor importa mucho menos que quedarse mudo.
REASON_ASCII_ALLOW = (
    "Venoxia: el guardian permite la edicion. El mensaje original no se pudo "
    "serializar; la traza esta en stderr."
)
REASON_ASCII_DENY = (
    "Venoxia ha bloqueado la edicion: no hay ninguna especificacion validada que "
    'la respalde. Ejecuta /venoxia:specify "describe el cambio" y luego '
    "/venoxia:validate. Para saltartelo, pon \"via\": \"direct\" en el change.json."
)
ASCII_REASONS = {DECISION_ALLOW: REASON_ASCII_ALLOW, DECISION_DENY: REASON_ASCII_DENY}

# Último recurso: los bytes exactos de una decisión válida, ya escritos a mano.
# No hay serialización que pueda fallar aquí, sólo un «write».
LAST_RESORT_BYTES = {
    DECISION_ALLOW: (
        b'{"hookSpecificOutput": {"hookEventName": "PreToolUse", '
        b'"permissionDecision": "allow", "permissionDecisionReason": '
        b'"Venoxia: fallo interno del guardian; se permite la edicion '
        b'(fail-open). La traza esta en stderr."}}\n'
    ),
    DECISION_DENY: (
        b'{"hookSpecificOutput": {"hookEventName": "PreToolUse", '
        b'"permissionDecision": "deny", "permissionDecisionReason": '
        b'"Venoxia ha bloqueado la edicion: no hay especificacion validada. '
        b'Ejecuta /venoxia:specify y luego /venoxia:validate."}, '
        b'"systemMessage": "Venoxia ha bloqueado la edicion: no hay '
        b'especificacion validada. Ejecuta /venoxia:specify y luego '
        b'/venoxia:validate."}\n'
    ),
}

HELP_TEXT = f"""guardian.py · el guardián de Venoxia (hook PreToolUse)

Uso:
  python3 scripts/guardian.py < payload.json

No toma argumentos: lee por la entrada estándar el payload JSON del hook
«{HOOK_EVENT_NAME}» de Claude Code y escribe por la salida estándar la decisión,
también en JSON. Sale siempre con código 0.

Entrada (los campos que se usan):
  {{"hook_event_name": "{HOOK_EVENT_NAME}", "cwd": "/abs/proyecto",
   "tool_name": "Write", "tool_input": {{"file_path": "src/checkout.ts"}}}}
  Para NotebookEdit la ruta llega en «tool_input.notebook_path».

Salida:
  {{"hookSpecificOutput": {{"hookEventName": "{HOOK_EVENT_NAME}",
    "permissionDecision": "allow"|"deny", "permissionDecisionReason": "…"}}}}
  Al denegar se añade además «systemMessage» con el mismo texto.

Orden de decisión:
  1. No existe «{VENOXIA_DIRNAME}/» en la raíz                → allow
  2. La ruta editada es especificación o queda fuera      → allow
  3. El cambio activo está en «state»: «{STATE_VALIDATED}» **y**
     tiene un «{DELTA_DIRNAME}/» con markdown no vacío        → allow
  4. El cambio activo declara «via»: «{VIA_DIRECT}»             → allow y anota
     una línea JSONL en «{DRIFT_LOG_DISPLAY}»
  5. Cualquier otro caso                                  → deny

Cualquier error interno se resuelve permitiendo la edición y dejando la traza
en stderr, y el proceso termina siempre con código 0. La frontera, que es fina:
un «change.json» cuyo **contenido** está mal (JSON corrupto) no es un error del
guardián, no acredita nada y no basta para pasar; no poder **leerlo** (permisos,
un montaje caído) sí es un error del guardián, y entonces se permite y se anota.
"""

# Testigo de emisión: garantiza que nunca se escriben dos decisiones.
_decision_sent = False
# Testigo de escritura: stdout se intenta **una sola vez** por proceso. Si el
# primer intento reventó puede haber dejado bytes a medias, y dos decisiones
# pegadas son peor que una rota.
_write_attempted = False


# --- La traza de stderr ------------------------------------------------------

# Testigo de stderr: en cuanto se demuestra roto, se deja de escribir en él.
_stderr_ok = True


def trace() -> None:
    """Deja la traza del error en stderr sin que eso pueda tumbar al guardián.

    Si el otro extremo de stderr está cerrado, escribir ahí lanza —y una traza
    que lanza dentro del «except» de «main()» deja al hook sin decisión, que es
    justo el fallo que este módulo existe para no cometer—. Peor todavía: los
    bytes que se quedan sin vaciar hacen que el intérprete termine con código
    120 al salir, y un código distinto de 0 convierte la decisión en «error del
    hook» aunque esté escrita. Por eso, ante el primer fallo, el stderr roto se
    sustituye por un sumidero y no se vuelve a intentar.
    """
    write_stderr(traceback.format_exc())


def warn(message: str) -> None:
    """Un aviso por stderr, con la misma protección que la traza."""
    write_stderr(message)


def write_stderr(text: str) -> None:
    """Escribe en stderr y, si stderr está roto, lo sustituye por un sumidero."""
    global _stderr_ok
    if not _stderr_ok:
        return
    try:
        sys.stderr.write(text)
        sys.stderr.flush()
    except BaseException:  # noqa: BLE001 — la traza es un extra, la decisión no
        _stderr_ok = False
        try:
            sys.stderr = open(os.devnull, "w", encoding="ascii", errors="replace")
        except BaseException:  # noqa: BLE001
            pass


# --- Emisión de la decisión --------------------------------------------------


def decision_payload(decision: str, reason: str) -> dict:
    """El sobre JSON que Claude Code espera de un hook «PreToolUse»."""
    payload: dict[str, object] = {
        "hookSpecificOutput": {
            "hookEventName": HOOK_EVENT_NAME,
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    if decision == DECISION_DENY:
        payload["systemMessage"] = reason
    return payload


def encode_decision(decision: str, reason: str) -> bytes:
    """Serializa la decisión a bytes **ASCII puros**.

    «ensure_ascii=True» no es cosmético: escapa los acentos y las comillas
    angulares a «\\uXXXX» —que el cliente recompone al parsear— y con ellos
    cualquier surrogate suelto que venga en la ruta editada. El resultado se
    puede escribir en cualquier salida, tenga la codificación que tenga.
    """
    return (json.dumps(decision_payload(decision, reason), ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def decision_bytes(decision: str, reason: str) -> bytes:
    """Los bytes de la decisión. **Nunca lanza**: baja de escalón hasta la constante."""
    for candidate in (reason, ASCII_REASONS.get(decision, REASON_ASCII_ALLOW)):
        try:
            return encode_decision(decision, candidate)
        except BaseException:  # noqa: BLE001 — quedarse mudo es la única falta grave
            trace()
    return LAST_RESORT_BYTES.get(decision) or LAST_RESORT_BYTES[DECISION_ALLOW]


def write_decision_bytes(data: bytes) -> bool:
    """Vuelca los bytes por stdout y devuelve si salieron enteros.

    Escribe a «sys.stdout.buffer» —la capa binaria— justamente para no pasar por
    el codificador del envoltorio de texto: con «PYTHONIOENCODING=ascii» o
    «LC_ALL=C» ese codificador reventaba y el hook se quedaba mudo. Si stdout no
    tiene capa binaria (alguien lo sustituyó por un «StringIO»), se escribe el
    texto ASCII, que también encaja en cualquier codificación.
    """
    global _write_attempted
    if _write_attempted:
        return False
    _write_attempted = True
    try:
        stream = getattr(sys.stdout, "buffer", None)
        if stream is None:
            sys.stdout.write(data.decode("ascii"))
            sys.stdout.flush()
            return True
        try:
            # Por si el envoltorio de texto tuviera algo pendiente: primero lo
            # suyo, luego lo nuestro. Que no se pueda vaciar no nos detiene.
            sys.stdout.flush()
        except BaseException:  # noqa: BLE001
            pass
        stream.write(data)
        stream.flush()
        return True
    except BaseException:  # noqa: BLE001 — sin decisión no hay guardián
        trace()
        return False


def emit(decision: str, reason: str) -> None:
    """Escribe la decisión en stdout. La primera **que sale** gana; el resto no hace nada.

    El testigo se marca sólo si el «write» y el «flush» fueron bien. Marcarlo
    antes era el fallo más grave del plugin: si la escritura reventaba, el
    «except» de «main()» llamaba otra vez y esta función no hacía nada, así que
    el hook terminaba con cero bytes en stdout y código 0 —ninguna decisión— y
    la edición pasaba igual.
    """
    global _decision_sent
    if _decision_sent:
        return
    if write_decision_bytes(decision_bytes(decision, reason)):
        _decision_sent = True


def write_text(text: str) -> None:
    """Escribe texto libre por stdout sin depender de la codificación del envoltorio."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        data = text.encode(encoding, "backslashreplace")
    except BaseException:  # noqa: BLE001 — codificación desconocida: al ASCII
        encoding = "ascii"
        data = text.encode("ascii", "backslashreplace")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        sys.stdout.write(data.decode(encoding, "replace"))
        sys.stdout.flush()
        return
    stream.write(data)
    stream.flush()


# --- Lectura del payload -----------------------------------------------------


def read_stdin() -> str:
    """Lee la entrada estándar como bytes y la decodifica como UTF-8, pase lo que pase.

    El payload del hook viene en UTF-8. Leerlo por el envoltorio de texto lo
    hacía depender de la codificación del entorno: con «PYTHONIOENCODING=ascii»
    o «LC_ALL=C», un payload con un solo acento —una ruta como «src/año/x.ts»—
    lanzaba «UnicodeDecodeError», el guardián caía en su fail-open y el «deny»
    se convertía en «allow» sin que nadie se enterase. Los bytes que no sean
    UTF-8 legal se sustituyen en vez de tumbar la lectura: una ruta con un
    carácter de reemplazo se sigue pudiendo juzgar; un payload sin leer, no.
    """
    stream = getattr(sys.stdin, "buffer", None)
    if stream is None:
        return sys.stdin.read()
    return stream.read().decode("utf-8", "replace")


def read_payload() -> dict:
    """Devuelve el payload del hook, o un diccionario vacío si no hay nada legible."""
    raw = read_stdin()
    if not raw or not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def project_root(payload: dict) -> str:
    """Raíz del proyecto: el «cwd» del payload y, si falta, el del proceso."""
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return os.path.normpath(os.path.abspath(cwd))
    return os.path.normpath(os.path.abspath(os.getcwd()))


def target_path(payload: dict) -> str | None:
    """Ruta que la herramienta quiere escribir, tal cual la declara el payload.

    Cada herramienta tiene su clave preferida: «NotebookEdit» trae la suya en
    «notebook_path» (contrato §6) y las demás en «file_path». La otra clave
    queda de reserva, porque un payload con una sola de las dos tiene que
    seguir decidiéndose. Mirar siempre «file_path» primero hacía que un
    «NotebookEdit» con los dos campos juzgara el fichero equivocado: bastaba un
    «file_path»: «spec.md» de adorno para editar cualquier cuaderno.
    """
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for key in PATH_KEYS_BY_TOOL.get(tool_name(payload), PATH_KEYS_DEFAULT):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def tool_name(payload: dict) -> str:
    """Nombre de la herramienta que dispara el hook, para el diario de deriva."""
    name = payload.get("tool_name")
    return name if isinstance(name, str) and name else "desconocida"


# --- Rutas -------------------------------------------------------------------


def resolve(path: str) -> str:
    """«realpath» defensivo: ante cualquier fallo devuelve la ruta tal cual.

    «os.path.realpath» no sólo puede fallar por un bucle de symlinks o por
    permisos: con un surrogate suelto en la ruta lanza «UnicodeEncodeError» al
    codificarla para el sistema de ficheros. Nada de eso puede tumbar al
    guardián, así que se captura todo y se vuelve al comportamiento anterior.
    """
    try:
        return os.path.normpath(os.path.realpath(path))
    except BaseException:  # noqa: BLE001 — resolver es un extra, no un requisito
        return path


def strip_root(root: str, candidate: str) -> str | None:
    """Devuelve «candidate» relativo a «root», o None si cae fuera. Sólo cadenas."""
    if candidate == root:
        return "."
    prefix = root if root.endswith(os.sep) else root + os.sep
    if not candidate.startswith(prefix):
        return None
    return candidate[len(prefix):].replace(os.sep, "/")


def file_identity(path: str) -> tuple[int, int] | None:
    """La identidad del fichero: el par «(st_dev, st_ino)», o None si no se pudo mirar.

    Es la única forma de comparar dos rutas que **no** depende de cómo se
    escriban. «os.stat» sigue los enlaces a propósito: lo que se compara es el
    fichero al que se llega, no el nombre por el que se llega. Que falle es
    normal —la ruta de un «Write» todavía no existe— y no es un error: es un
    «no lo sé» que devuelve None y deja decidir a quien llame.
    """
    try:
        status = os.stat(path)
    except BaseException:  # noqa: BLE001 — inexistente, sin permiso, surrogate suelto…
        return None
    return (status.st_dev, status.st_ino)


def relative_by_identity(root: str, candidate: str) -> str | None:
    """«candidate» relativo a «root» comparando **identidad de fichero**, o None.

    Sube por los ancestros de «candidate» —quedándose con el nombre de cada
    tramo que deja atrás— hasta dar con uno que sea el mismo fichero que
    «root», y devuelve el camino acumulado.

    Se sube porque el caso normal de un «Write» es que el fichero **todavía no
    exista**: de una ruta que no está en el disco no hay identidad que comparar,
    sólo la de sus ancestros. Y se comparan **todos** los ancestros, no sólo el
    primero que exista, porque los directorios intermedios («src/») suelen
    existir sin ser la raíz: pararse en el primero que respondiera dejaría fuera
    del proyecto todo lo que cuelgue de un directorio ya creado.

    El ascenso está acotado por MAX_IDENTITY_HOPS: una ruta más profunda que eso
    no se sigue investigando. Es un tope defensivo contra una ruta absurda, no
    un límite que ningún proyecto real vaya a rozar.
    """
    target = file_identity(root)
    if target is None:  # la raíz no se deja mirar: no hay nada contra qué comparar
        return None
    tail: list[str] = []
    current = candidate
    for _hop in range(MAX_IDENTITY_HOPS):
        if file_identity(current) == target:
            return "/".join(reversed(tail)) if tail else "."
        parent = os.path.dirname(current)
        if parent == current:  # se llegó a la raíz del sistema de ficheros
            return None
        tail.append(os.path.basename(current))
        current = parent
    return None


def relative_to_root(root: str, raw_path: str) -> str | None:
    """Normaliza «raw_path» contra «root» y lo devuelve relativo, con «/» como separador.

    Devuelve None sólo si la ruta cae fuera del proyecto **según las tres
    medidas**, que se prueban en este orden y de las que basta que **una** diga
    «dentro»:

    1. **Aritmética de cadenas.** El camino frecuente, y el único que no toca el
       disco: una ruta relativa como «src/checkout.ts» se resuelve aquí, con
       cero llamadas al sistema. Los pasos 2 y 3 sólo se pagan cuando éste ya ha
       dicho «fuera», que es el caso raro.
    2. **«realpath» de las dos rutas.** La raíz de un proyecto tiene más de un
       nombre absoluto: en macOS «/tmp/p/src/x.ts» y «/private/tmp/p/src/x.ts»
       son el mismo inodo, pero con el «cwd» ya resuelto la primera se
       clasificaba «fuera del proyecto» y se permitía. Esto cierra los symlinks
       —«/tmp», «/var», «/etc»— y nada más.
    3. **Identidad de fichero: el par «(st_dev, st_ino)».** Porque el paso 2 se
       queda corto y durante una ronda entera este docstring dijo lo contrario.
       Tres alias inodo-idénticos siguen escribiéndose distinto **después** de
       pasar por «realpath», y ninguno de los tres hay que preparar:
       los **firmlinks** de «/System/Volumes/Data/…», que «realpath» no resuelve
       (deja la ruta tal cual); la **caja**, porque APFS es insensible a
       mayúsculas por defecto; y **NFC frente a NFD**, que es lo que pasa al
       copiar del Finder una ruta con acentos. Comparar el inodo es la única
       medida que no depende de cómo se escriba la ruta. Véase
       «relative_by_identity».

    Que basten una de las tres para decir «dentro» es deliberado: resolver
    **sólo** por identidad o por «realpath» abriría el rodeo contrario —un
    symlink dentro del proyecto que apunte fuera sacaría del alcance del
    guardián todo lo que colgara de él—. Entre un «deny» de más y un «allow» de
    más, el producto se juega la premisa en el segundo.
    """
    try:
        candidate = os.path.expanduser(raw_path)
    except BaseException:  # noqa: BLE001 — un «~» imposible no es asunto nuestro
        candidate = raw_path
    if not os.path.isabs(candidate):
        candidate = os.path.join(root, candidate)
    candidate = os.path.normpath(candidate)

    relative = strip_root(root, candidate)
    if relative is not None:
        return relative
    resolved = strip_root(resolve(root), resolve(candidate))
    if resolved is not None:
        return resolved
    return relative_by_identity(root, candidate)


def is_spec_path(relative: str) -> bool:
    """¿La ruta es especificación, documentación o material del que nace la spec?

    Cubre lo que dice el contrato (§6, paso 2) con dos reglas: cualquier cosa
    bajo «.venoxia/» o «prfaq/» **de primer nivel**, y cualquier fichero cuyo
    nombre termine en «.md», a cualquier profundidad. El markdown es
    documentación: no tiene comportamiento que un test ejecute ni que un
    usuario observe, y vigilarlo sólo convertía la vía «direct» en parte del
    flujo normal —70 de las 193 líneas del diario de deriva de este repo eran
    documentación—.

    El anclaje de los directorios es lo que impide el rodeo para lo que **no**
    es markdown: reconocer «prfaq» a cualquier profundidad convertía un «mkdir
    src/prfaq/» en un desvío que anulaba al guardián para todo lo que se
    metiera dentro. Ahí, ante la duda, se elige lo restrictivo: un «deny» de
    más le cuesta al usuario un comando; un «allow» de más le cuesta al
    producto su premisa.

    «relative» ya viene normalizada y dentro del proyecto (véase
    «relative_to_root»); aquí sólo hay aritmética de cadenas, sin tocar disco.
    """
    parts = [part for part in relative.split("/") if part not in ("", ".")]
    if not parts:
        return False
    directories, filename = parts[:-1], parts[-1].lower()
    if directories and directories[0] in SPEC_DIR_NAMES:
        return True
    return filename.endswith(MARKDOWN_SUFFIX)


def spec_path_reason(relative: str) -> str:
    """La razón del «allow» del paso 2: la spec siempre, el markdown también."""
    parts = [part for part in relative.split("/") if part not in ("", ".")]
    if len(parts) > 1 and parts[0] in SPEC_DIR_NAMES:
        return f"Venoxia: «{relative}» es especificación; escribir la spec siempre está permitido."
    return (
        f"Venoxia: «{relative}» es markdown; la documentación no tiene comportamiento "
        "que vigilar y siempre se puede escribir."
    )


# --- El cambio activo --------------------------------------------------------


def field(data: dict, key: str) -> str:
    """Lee una clave de texto del «change.json», normalizada y en minúsculas."""
    value = data.get(key)
    return value.strip().lower() if isinstance(value, str) else ""


def display_id(declared: object, fallback: str) -> str:
    """El «id» que se enseña en los mensajes: el del fichero si es simple, si no el del directorio.

    El «id» declarado sale de un fichero del usuario, así que puede traer
    cualquier cosa: un megabyte de texto, saltos de línea que descuadren el
    mensaje o barras que hagan pensar en una ruta. Para construir rutas se usa
    **siempre** el nombre del directorio, nunca esto.
    """
    if not isinstance(declared, str):
        return fallback
    value = declared.strip()
    if not value or len(value) > MAX_ID_LENGTH:
        return fallback
    if "/" in value or "\\" in value or any(ord(char) < 32 for char in value):
        return fallback
    return value


def find_active_change(root: str) -> tuple[str, str, str, dict]:
    """Localiza el cambio activo: el «change.json» legible y no archivado más reciente.

    Devuelve «(estado, id_para_mensajes, nombre_del_directorio, contenido)», con
    el estado en CHANGE_NONE, CHANGE_FOUND, CHANGE_BROKEN o CHANGE_UNREADABLE.

    **La distinción que se ha confundido dos veces, escrita de una vez:**

    * Un «change.json» cuyo **contenido** está mal —JSON corrupto, un array
      donde iba un objeto, un megabyte de relleno— es un fichero **del usuario**
      que está mal. No es un error del guardián: es una respuesta que no
      acredita nada. Se salta, la búsqueda sigue con el siguiente y, si no queda
      ninguno bueno, el estado es CHANGE_BROKEN y la decisión llega al «deny».
      Tratar esto como fail-open era la mitad del agujero: bastaba dejar el
      «change.json» corrupto para desactivar el guardián entero.
    * Un fallo de **entrada/salida** al mirar ese mismo fichero —permisos
      denegados tras un «sudo», un montaje de red que va y viene, un
      «change.json» que resultó ser un directorio— es un fallo **nuestro**: no
      dice nada del proyecto, dice que no hemos podido preguntar. Ahí manda el
      fail-open (CHANGE_UNREADABLE) y la edición pasa. Meterlo en el mismo
      «except» que el JSON corrupto convertía un EACCES en un «deny» de todas
      las ediciones, con un mensaje que manda ejecutar «/venoxia:specify», que
      no lo arregla: el escenario exacto por el que un guardián se desinstala.

    El fallo de E/S corta la búsqueda en el sitio en que aparece. Como los
    candidatos se miran del más reciente al más viejo, cualquier cambio que
    hubiera podido decidir por sí solo ya se ha mirado antes; seguir hacia atrás
    sería decidir con la certeza de no haber podido leer justo el que mandaba.
    """
    changes_dir = os.path.join(root, VENOXIA_DIRNAME, CHANGES_DIRNAME)
    candidates: list[tuple[float, str, str]] = []
    try:
        with os.scandir(changes_dir) as entries:
            for entry in entries:
                if len(candidates) >= MAX_CHANGE_ENTRIES:
                    break
                if not entry.is_dir():
                    continue
                change_file = os.path.join(entry.path, CHANGE_FILENAME)
                try:
                    stat_result = os.stat(change_file)
                except (FileNotFoundError, NotADirectoryError):
                    continue  # un directorio sin «change.json»: normal, no es un fallo
                except OSError:  # permisos, E/S: no hemos podido preguntar
                    trace()
                    return (CHANGE_UNREADABLE, entry.name, entry.name, {})
                candidates.append((stat_result.st_mtime, entry.name, change_file))
    except (FileNotFoundError, NotADirectoryError):
        return (CHANGE_NONE, "", "", {})  # todavía no hay ningún cambio: normal
    except OSError:  # el propio «changes/» no se deja mirar: fallo nuestro
        trace()
        return (CHANGE_UNREADABLE, "", "", {})

    # Más reciente primero; el nombre desempata para que el resultado sea determinista.
    candidates.sort(key=lambda item: (-item[0], item[1]))

    broken = ""  # el primer cambio con el contenido roto, para poder nombrarlo al denegar
    for _mtime, dirname, change_file in candidates:
        data: object = None
        try:
            if os.path.getsize(change_file) <= MAX_CHANGE_BYTES:
                with open(change_file, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
        except OSError:  # fallo **nuestro**: no se pudo leer → fail-open
            trace()
            return (CHANGE_UNREADABLE, dirname, dirname, {})
        except (ValueError, UnicodeDecodeError):  # fichero **del usuario** mal escrito
            trace()
        if not isinstance(data, dict):
            broken = broken or dirname
            continue
        if field(data, "state") == STATE_ARCHIVED:
            continue
        return (CHANGE_FOUND, display_id(data.get("id"), dirname), dirname, data)

    if broken:
        return (CHANGE_BROKEN, broken, broken, {})
    return (CHANGE_NONE, "", "", {})


def has_delta_evidence(root: str, change_dirname: str) -> bool | None:
    """¿El cambio trae un «delta/» con al menos un «.md» no vacío?

    Devuelve True/False, o **None** si no se pudo mirar el directorio: eso sí es
    un fallo del guardián (permisos, un «delta» que es un fichero, una ruta
    imposible) y se resuelve por fail-open, no denegando.

    Sirve para que un «change.json» escrito a mano deje de bastar. Con sólo la
    herramienta «Write» se podía desactivar el guardián en dos pasos: escribir
    «.venoxia/changes/zzz/change.json» —permitido, porque «.venoxia/» es
    especificación— con «state»: «validated» dentro, y a partir de ahí editar
    cualquier código. Exigir el delta obliga a fabricar también la
    especificación del cambio; sigue siendo un «scandir» de un nivel.
    """
    delta_dir = os.path.join(root, VENOXIA_DIRNAME, CHANGES_DIRNAME, change_dirname, DELTA_DIRNAME)
    try:
        with os.scandir(delta_dir) as entries:
            for seen, entry in enumerate(entries):
                if seen >= MAX_DELTA_ENTRIES:
                    break
                if not entry.name.lower().endswith(DELTA_SUFFIX):
                    continue
                try:
                    if entry.is_file() and entry.stat().st_size > 0:
                        return True
                except OSError:
                    continue
        return False
    except FileNotFoundError:
        return False
    except NotADirectoryError:
        return False
    except OSError:
        trace()
        return None


def declared_oracle_paths(root: str, change_dirname: str) -> set[str] | None:
    """Las rutas que los «verifies:» del «delta/» del cambio nombran, normalizadas.

    Es lo que abre la puerta del paso 5: con el cambio en «specified», el único
    fichero de fuera de la especificación que se puede escribir es el oráculo
    que la propia especificación declara. La puerta la abre el vínculo, no la
    forma de la ruta: un «tests/otro.py» que ningún «verifies:» nombra se queda
    fuera igual que «src/».

    Devuelve el conjunto (vacío si no hay delta o ningún «verifies:»), o
    **None** si no se pudo leer el directorio o alguno de sus deltas: eso es un
    fallo del guardián y se resuelve por fail-open, nunca denegando. Los topes
    son los mismos que ya acotan el «delta/» y el «change.json»: un delta más
    grande que MAX_CHANGE_BYTES no es nuestro y se ignora.

    Las rutas se comparan relativas a la raíz y normalizadas (`os.path.normpath`),
    que es exactamente la forma en que «relative_to_root» entrega la ruta
    editada; un «verifies:» absoluto se reduce a la raíz por el mismo camino.
    """
    delta_dir = os.path.join(root, VENOXIA_DIRNAME, CHANGES_DIRNAME, change_dirname, DELTA_DIRNAME)
    declared: set[str] = set()
    try:
        with os.scandir(delta_dir) as entries:
            for seen, entry in enumerate(entries):
                if seen >= MAX_DELTA_ENTRIES:
                    break
                if not entry.name.lower().endswith(DELTA_SUFFIX):
                    continue
                if not entry.is_file() or entry.stat().st_size > MAX_CHANGE_BYTES:
                    continue
                with open(entry.path, "rb") as handle:
                    text = handle.read(MAX_CHANGE_BYTES).decode("utf-8", "replace")
                for match in VERIFIES_LINE_RE.finditer(text):
                    for token in VERIFIES_SPLIT_RE.split(match.group(1)):
                        if not token:
                            continue
                        if os.path.isabs(token):
                            inside = relative_to_root(root, token)
                            if inside is None:
                                continue
                            token = inside
                        declared.add(os.path.normpath(token))
        return declared
    except FileNotFoundError:
        return set()
    except NotADirectoryError:
        return set()
    except OSError:
        trace()
        return None


# --- Diario de deriva --------------------------------------------------------


def record_direct_edit(
    root: str, change_id: str, tool: str, relative: str, note: str | None = None
) -> bool:
    """Anota una línea JSONL en «.venoxia/drift/direct.log». Devuelve si lo consiguió.

    Los cuatro campos del contrato («ts», «change», «tool», «path») van siempre.
    «note» añade un quinto sólo cuando la edición pasó sin respaldo firme —un
    «validated» sin delta que lo acredite— y dice por qué, para que el diario
    sirva de rastro de lo que el guardián dejó pasar a sabiendas.

    Escribe siempre en modo «append» y con la excepción capturada: si el disco
    está lleno, el directorio es de sólo lectura o la ruta es imposible, se deja
    la traza en stderr y la edición se permite igual. El diario es un registro,
    nunca un obstáculo.
    """
    try:
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        entry = {
            "ts": timestamp.replace("+00:00", "Z"),
            "change": change_id,
            "tool": tool,
            "path": relative,
        }
        if note:
            entry["note"] = note
        drift_dir = os.path.join(root, VENOXIA_DIRNAME, DRIFT_DIRNAME)
        os.makedirs(drift_dir, exist_ok=True)
        with open(os.path.join(drift_dir, DRIFT_LOG_FILENAME), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False))
            handle.write("\n")
        return True
    except BaseException:  # noqa: BLE001 — el diario nunca bloquea la edición
        trace()
        return False


# --- El mensaje de denegación ------------------------------------------------


def deny_reason(
    relative: str, change_dirname: str, motive: str, declared: tuple[str, ...] = ()
) -> str:
    """Redacta el «deny»: qué ha pasado, por qué, qué teclear y cómo saltárselo.

    La ruta que se ofrece al usuario se construye con el **nombre del
    directorio** del cambio, no con el «id» que declara su JSON: son la misma
    cosa en cualquier proyecto normal, pero si difieren, la única que existe en
    el disco es la primera, y un mensaje que manda editar un fichero que no
    está es peor que no decir nada.

    «declared» son los oráculos que el delta del cambio activo nombra en
    «verifies:». Cuando hay alguno, el cambio está en «specified» y el remedio
    no es volver a «/venoxia:specify» —eso ya está hecho y no desbloquea nada—,
    sino escribir esos ficheros y pasar la divergencia: son lo único que saca a
    un cambio de «specified».
    """
    change_ref = f"{CHANGES_DISPLAY}{change_dirname or '<id>'}/{CHANGE_FILENAME}"
    if declared:
        oracles = "\n".join(f"     «{path}»" for path in declared)
        remedy = (
            f"Para desbloquearlo, en este orden:\n"
            f"  1. Escribe el oráculo que el delta declara en «verifies:»:\n"
            f"{oracles}\n"
            f"  2. /venoxia:validate\n"
            f"  3. /venoxia:diverge\n"
        )
    else:
        remedy = (
            f"Para desbloquearlo, dos comandos:\n"
            f'  1. /venoxia:specify "describe en una frase el cambio que vas a hacer"\n'
            f"  2. /venoxia:validate\n"
        )
    return (
        f"Venoxia ha bloqueado la edición de «{relative}».\n"
        f"\n"
        f"{motive}\n"
        f"Escribir el comportamiento antes que el código es justo lo que este plugin protege.\n"
        f"\n"
        f"{remedy}"
        f"\n"
        f"¿Con prisa y sin especificación? Pon \"via\": \"direct\" en «{change_ref}»:\n"
        f"la edición pasará y quedará anotada en «{DRIFT_LOG_DISPLAY}»."
    )


def deny_motive(status: str, change_id: str, change_dirname: str, state: str, unbacked: bool) -> str:
    """La primera frase del «deny»: por qué no hay especificación que respalde la edición.

    CHANGE_BROKEN es siempre un fichero **del usuario** mal escrito; el fichero
    que no se ha podido leer nunca llega hasta aquí, porque ése se resuelve
    permitiendo mucho antes (véase «decide»).
    """
    if status == CHANGE_BROKEN:
        return (
            f"Ningún cambio tiene la especificación validada: el «{CHANGE_FILENAME}» del cambio "
            f"«{change_id}» se leyó pero no se pudo interpretar, y un fichero roto no acredita "
            "nada (la traza está en stderr)."
        )
    if unbacked:
        delta_ref = f"{CHANGES_DISPLAY}{change_dirname}/{DELTA_DIRNAME}/"
        return (
            f"El cambio activo «{change_id}» dice «state»: «{STATE_VALIDATED}», pero no tiene "
            f"ningún delta en «{delta_ref}»: un «{CHANGE_FILENAME}» sin especificación al lado "
            "no acredita que nada se haya validado."
        )
    if change_id:
        return (
            f"Ningún cambio tiene la especificación validada: el cambio activo «{change_id}» "
            f"está en «state»: «{state or 'sin estado'}» y hace falta «{STATE_VALIDATED}»."
        )
    return (
        "Ningún cambio tiene la especificación validada: no hay ningún cambio activo "
        f"en «{CHANGES_DISPLAY}»."
    )


# --- El orden de decisión ----------------------------------------------------


def decide(payload: dict) -> None:
    """Aplica los seis pasos del contrato, en orden, y emite la decisión."""
    root = project_root(payload)

    # Paso 1 · el proyecto no ha adoptado Venoxia: el guardián no estorba.
    if not os.path.isdir(os.path.join(root, VENOXIA_DIRNAME)):
        emit(DECISION_ALLOW, REASON_NOT_ADOPTED)
        return

    # Paso 2 · la ruta editada es especificación, o no es asunto nuestro.
    raw_path = target_path(payload)
    if raw_path is None:
        emit(DECISION_ALLOW, REASON_NO_PATH)
        return
    relative = relative_to_root(root, raw_path)
    if relative is None:
        emit(
            DECISION_ALLOW,
            f"Venoxia: «{raw_path}» queda fuera del proyecto; el guardián no interviene.",
        )
        return
    if is_spec_path(relative):
        emit(DECISION_ALLOW, spec_path_reason(relative))
        return

    status, change_id, change_dirname, change = find_active_change(root)

    # Fail-open · no se pudo **leer** el cambio activo. Un EACCES o un EISDIR no
    # dicen nada del proyecto: dicen que no hemos podido preguntar, y por un
    # fallo nuestro no se bloquea a nadie. Queda anotado, como todo «allow» que
    # se concede sin haber comprobado el respaldo.
    if status == CHANGE_UNREADABLE:
        where = (
            f"el «{CHANGE_FILENAME}» del cambio «{change_id}»"
            if change_id
            else f"«{CHANGES_DISPLAY}»"
        )
        record_direct_edit(
            root, change_id, tool_name(payload), relative, note=NOTE_CHANGE_UNREADABLE
        )
        emit(
            DECISION_ALLOW,
            f"Venoxia: no se pudo leer {where} (fallo de entrada/salida, no un "
            "fichero mal escrito); se permite por prudencia (fail-open) y queda "
            f"anotado en «{DRIFT_LOG_DISPLAY}». La traza está en stderr.",
        )
        return

    state = field(change, "state")
    unbacked = False  # un «validated» que ningún delta respalda

    # Paso 3 · hay un cambio activo con la especificación validada… y con delta.
    if status == CHANGE_FOUND and state == STATE_VALIDATED:
        evidence = has_delta_evidence(root, change_dirname)
        if evidence is None:
            # No se pudo ni mirar el «delta/»: eso es un fallo nuestro, y los
            # fallos nuestros se resuelven permitiendo. Queda anotado, porque un
            # «allow» sin respaldo comprobado es exactamente lo que el diario de
            # deriva existe para recordar.
            record_direct_edit(
                root, change_id, tool_name(payload), relative, note=NOTE_DELTA_UNCHECKED
            )
            emit(
                DECISION_ALLOW,
                f"Venoxia: el cambio «{change_id}» dice «{STATE_VALIDATED}» y no se pudo "
                f"comprobar su «{DELTA_DIRNAME}/»; se permite por prudencia (fail-open) y "
                f"queda anotado en «{DRIFT_LOG_DISPLAY}». La traza está en stderr.",
            )
            return
        if evidence:
            emit(
                DECISION_ALLOW,
                f"Venoxia: el cambio «{change_id}» tiene la especificación validada "
                f"(«state»: «{STATE_VALIDATED}»).",
            )
            return
        unbacked = True

    # Paso 4 · el cambio activo declara «via»: «direct»: se permite y se anota.
    if status == CHANGE_FOUND and field(change, "via") == VIA_DIRECT:
        recorded = record_direct_edit(
            root,
            change_id,
            tool_name(payload),
            relative,
            note=NOTE_VALIDATED_WITHOUT_DELTA if unbacked else None,
        )
        note = (
            f"Edición permitida y anotada en «{DRIFT_LOG_DISPLAY}»."
            if recorded
            else f"Edición permitida; no se pudo anotar en «{DRIFT_LOG_DISPLAY}» "
            "(la traza está en stderr)."
        )
        emit(
            DECISION_ALLOW,
            f"Venoxia: el cambio «{change_id}» declara «via»: «{VIA_DIRECT}». {note}",
        )
        return

    # Paso 5 · el cambio activo está en «specified» y la ruta es el oráculo que
    # su delta declara en «verifies:». El test nace antes que el código: es el
    # paso del flujo que sigue a «specify», y sin esta puerta se denegaba con el
    # mismo mensaje que una edición de producción. Va **después** de la vía
    # «direct» a propósito: un cambio que ya está fuera del flujo anota todo, y
    # anotar de más es el error que el proyecto prefiere.
    declared: set[str] = set()
    if status == CHANGE_FOUND and state == STATE_SPECIFIED:
        oracles = declared_oracle_paths(root, change_dirname)
        if oracles is None:
            # No se pudo leer el «delta/»: fallo nuestro, y los fallos nuestros
            # se resuelven permitiendo y anotando, igual que en el paso 3.
            record_direct_edit(
                root, change_id, tool_name(payload), relative, note=NOTE_DELTA_UNCHECKED
            )
            emit(
                DECISION_ALLOW,
                f"Venoxia: el cambio «{change_id}» está en «{STATE_SPECIFIED}» y no se pudo "
                f"leer su «{DELTA_DIRNAME}/»; se permite por prudencia (fail-open) y queda "
                f"anotado en «{DRIFT_LOG_DISPLAY}». La traza está en stderr.",
            )
            return
        declared = oracles
        if os.path.normpath(relative) in declared:
            emit(
                DECISION_ALLOW,
                f"Venoxia: el cambio «{change_id}» está en «state»: «{STATE_SPECIFIED}» y "
                f"«{relative}» es el oráculo que su delta declara en «verifies:»: el test "
                "se escribe antes que el código.",
            )
            return

    # Paso 6 · no hay especificación validada que respalde esta edición.
    emit(
        DECISION_DENY,
        deny_reason(
            relative,
            change_dirname,
            deny_motive(status, change_id, change_dirname, state, unbacked),
            declared=tuple(sorted(declared)),
        ),
    )


def close_stdout() -> None:
    """Vacía y **cierra** stdout dentro de nuestro control.

    Mientras queden bytes en el «BufferedWriter», el que acaba vaciándolos es
    «Py_FinalizeEx» al terminar el intérprete, ya fuera de todo «try»: si ahí
    falla —stdout es un pipe sin lector, el disco está lleno, el descriptor no
    admite escritura— el proceso termina con código 120 y una decisión escrita
    con código 120 es, para el cliente, un error del hook: la edición sigue.
    Vaciar y cerrar aquí deja el fallo dentro de un «except» nuestro.
    """
    stream = sys.stdout
    if stream is None:
        return
    for step in ("flush", "close"):
        method = getattr(stream, step, None)
        if method is None:
            continue
        try:
            method()
        except BaseException:  # noqa: BLE001 — el fallo se traza, no se propaga
            trace()


def exit_now() -> None:
    """Termina el proceso con código 0 sin dejar que nadie vuelva a intentar nada.

    «os._exit» se salta la finalización del intérprete, y con ella el reintento
    de vaciado que convertía un stdout roto en un código 120. Lo que se pierde
    con ella no importa en este programa: no hay «atexit» registrado, no hay
    hilos que esperar, no hay temporales que borrar, y los dos únicos buffers
    que existen ya están vaciados a mano —el de stdout justo aquí arriba, el de
    stderr en cada llamada a «write_stderr»—. A cambio se gana lo único que el
    cliente mira además del JSON: el código de salida.
    """
    close_stdout()
    try:
        sys.stderr.flush()
    except BaseException:  # noqa: BLE001 — un stderr roto no decide nada
        pass
    os._exit(0)


def main() -> int:
    """Punto de entrada. Devuelve siempre 0: el guardián jamás rompe el flujo."""
    try:
        argv = sys.argv[1:]
        if argv:
            if argv[0] in ("-h", "--help"):
                write_text(HELP_TEXT)
                return 0
            warn(
                f"guardian.py no acepta argumentos (recibió {argv!r}); "
                "lee el payload del hook por la entrada estándar. Usa «--help» para la ayuda.\n"
            )
        decide(read_payload())
    except BaseException:  # noqa: BLE001 — fail-open: cualquier fallo permite
        trace()
        try:
            emit(DECISION_ALLOW, REASON_FALLBACK)
        except BaseException:  # noqa: BLE001 — ni siquiera esto puede romper
            pass
    return 0


if __name__ == "__main__":
    # El «finally» es parte de la garantía: ni un «SystemExit» ni un
    # «KeyboardInterrupt» a destiempo pueden colar un código distinto de 0.
    try:
        main()
    finally:
        exit_now()  # no vuelve
