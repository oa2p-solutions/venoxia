#!/usr/bin/env python3
"""Envoltorio de `trace` que conserva el código de salida real y sobrevive a `os._exit`.

Medir con `python3 -m trace --count` tiene dos huecos que este script cierra
sin tocar el código medido:

1. `trace.main()` atrapa el `SystemExit` de lo que ejecuta con un
   `except SystemExit: pass` explícito y nunca lo relanza (verificado en el
   `trace.py` de la stdlib). Bajo esa medición, cualquier subproceso que
   termina con `sys.exit(N)` para `N != 0` devuelve `0` al proceso que lo
   lanzó — la medición deja de ser la suite: un test que comprueba
   `returncode == 1` de `validate.py` falla sólo por estar bajo `trace`,
   aunque el script decida bien.
2. `scripts/guardian.py` termina siempre con `os._exit(0)` en un `finally` —
   parte del fail-open que ningún ajuste de este proyecto toca. `os._exit`
   salta la finalización del intérprete, y con ella el volcado de resultados
   de `trace` (`CoverageResults.write_results`, que `Trace.runctx` sólo llama
   **después** de que la ejecución que envuelve retorne). Un proceso que
   llama `os._exit` nunca llega a ese retorno: su `.cover` no se escribe
   nunca y la cobertura de `guardian.py` mide 0 % para siempre.

La solución: ejecutar el objetivo en **este mismo proceso** (no en un
subproceso nuevo) con `runpy`, dentro de `Trace.runctx`; capturar el
`SystemExit` que lance y usarlo como código de salida real de este proceso; y
sustituir `os._exit` por una función que primero vuelca las cuentas
acumuladas y **después** llama al `os._exit` original — así el proceso sigue
terminando de inmediato (el comportamiento observable del fail-open no
cambia), pero la medición ya no se pierde.

Uso
---
    python3 tools/trace_run.py <script> [args...]
    python3 tools/trace_run.py -m <módulo> [args...]

La segunda forma es la que usa `tools/coverage.py` para lanzar la suite
entera (`-m unittest discover -s tests -q`), igual que `python3 -m <módulo>`.

Con `VENOXIA_TRACE_DIR` en el entorno, acumula en `<VENOXIA_TRACE_DIR>/counts`
y deja los `.cover` en ese mismo directorio — el formato y la ubicación que
espera `tools/coverage.py`. Sin la variable, ejecuta el objetivo tal cual (sin
`trace`, en este mismo proceso) y no escribe nada: es un passthrough, no un
segundo intérprete.
"""

from __future__ import annotations

import os
import runpy
import sys
import threading
import trace
from pathlib import Path

USAGE = "uso: trace_run.py <script> [args...]  |  trace_run.py -m <módulo> [args...]"


def _exit_code_of(exc: SystemExit) -> int:
    """El código de salida que el intérprete le daría a este `SystemExit`."""
    code = exc.code
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    # Un `SystemExit` con un mensaje de texto: como el intérprete, se imprime
    # a stderr y el código de salida es 1.
    print(code, file=sys.stderr)
    return 1


def _prepare_sys_path(script: str | None) -> None:
    """Ajusta `sys.path[0]` como haría el intérprete real al arrancar.

    Para un script suelto (`python3 <script>`), el intérprete pone el
    directorio del script en `sys.path[0]`; `runpy.run_path` no lo hace por
    su cuenta. Sin este ajuste, un import relativo al propio directorio del
    script fallaría. Y bajo `trace`, `_fullmodname` —quien decide el nombre
    del `.cover`, buscando en `sys.path` el prefijo más largo que casa con la
    ruta tal cual se compiló— sólo encuentra ese prefijo si es
    **literalmente** el mismo string que `dirname(script)`, sin pasar por
    `abspath`: es exactamente lo que hacía `trace.main()`
    (`sys.path[0] = os.path.dirname(opts.progname)`, con `opts.progname` sin
    normalizar), y se repite aquí tal cual para que `tools/coverage.py` siga
    viendo los mismos nombres de siempre (`guardian.cover`, no
    `scripts.guardian.cover`).

    Para un módulo (`python3 -m <módulo>`), el intérprete antepone en cambio
    el directorio actual (`""`, que `sys.path` resuelve como el cwd) — así
    encuentra los paquetes del proyecto (`tests`, aquí) igual que lo haría
    `python3 -m unittest` corrido a mano.
    """
    sys.path.insert(0, os.path.dirname(script) if script is not None else "")


def _target_source(module: str | None, script: str | None) -> tuple[str, dict[str, object]]:
    """La expresión a ejecutar (para `exec`/`Trace.runctx`) y sus globals.

    Exactamente una de `module`/`script` no es `None`. `runpy.run_module` con
    `alter_sys=True` es la forma programática de `python3 -m <módulo>`:
    ajusta `sys.argv[0]` y `sys.modules["__main__"]` como lo haría el
    intérprete, y lo deshace al terminar.
    """
    if module is not None:
        return (
            "runpy.run_module(__vr_target__, run_name='__main__', alter_sys=True)",
            {"runpy": runpy, "__vr_target__": module},
        )
    return (
        "runpy.run_path(__vr_target__, run_name='__main__')",
        {"runpy": runpy, "__vr_target__": script},
    )


def _run_plain(module: str | None, script: str | None, args: list[str]) -> int:
    """Sin `VENOXIA_TRACE_DIR`: ejecuta el objetivo tal cual, en este proceso."""
    sys.argv = [module or script, *args]
    _prepare_sys_path(script)
    source, source_globals = _target_source(module, script)
    try:
        exec(source, source_globals)
    except SystemExit as exc:
        return _exit_code_of(exc)
    return 0


class _IgnoreByPath:
    """Sustituto de `trace._Ignore` que decide por la ruta del fichero.

    `trace._Ignore.names(filename, modulename)` cachea su veredicto por
    `modulename`, y `trace` le pasa el nombre **base** del fichero: todos los
    `__init__.py` del proceso comparten la clave `__init__`. El primero que se
    ejecuta decide por los demás: si es uno de la stdlib (bajo `sys.prefix`,
    ignorado), `scripts/venoxia/__init__.py` queda ignorado también y su
    `.cover` no se escribe nunca. Es lo que pasó en el primer run real de
    `coverage` en CI («SIN DATOS (FALLA)» para ese fichero).

    Además compara contra la ruta real de cada prefijo: con un `sys.prefix`
    que es un symlink (Python de Homebrew en macOS), `co_filename` trae la
    ruta resuelta y `trace._Ignore` no reconocía la stdlib, así que la
    medía entera —lento, y con un `.cover` por módulo de la stdlib.
    """

    def __init__(self, dirs: list[str]) -> None:
        prefixes: list[str] = []
        for directory in dirs:
            for candidate in (directory, os.path.realpath(directory)):
                prefix = os.path.normpath(candidate) + os.sep
                if prefix not in prefixes:
                    prefixes.append(prefix)
        self._prefixes = tuple(prefixes)
        self._cache: dict[str, int] = {}

    def names(self, filename: str | None, modulename: str) -> int:  # noqa: ARG002
        if filename is None:  # un built-in: `trace` los ignora siempre
            return 1
        verdict = self._cache.get(filename)
        if verdict is None:
            verdict = 1 if filename.startswith(self._prefixes) else 0
            self._cache[filename] = verdict
        return verdict


def _run_traced(
    module: str | None, script: str | None, args: list[str], trace_dir: Path
) -> int:
    """Con `VENOXIA_TRACE_DIR`: ejecuta bajo `trace`, a prueba de `os._exit`."""
    trace_dir.mkdir(parents=True, exist_ok=True)
    counts_file = str(trace_dir / "counts")
    tracer = trace.Trace(
        count=1,
        trace=0,
        ignoredirs=[sys.prefix, sys.exec_prefix],
        infile=counts_file,
        outfile=counts_file,
    )
    # `Trace.__init__` construye `self.ignore = _Ignore(ignoremods, ignoredirs)`
    # y `globaltrace_lt` sólo lo consulta vía `.names(...)`: se sustituye entero.
    tracer.ignore = _IgnoreByPath([sys.prefix, sys.exec_prefix])  # type: ignore[assignment]

    dumped = False

    def dump() -> None:
        # Idempotente a propósito: tanto el `os._exit` parcheado como el
        # `finally` de más abajo llaman a esto, y sólo el primero en llegar
        # debe volcar de verdad.
        nonlocal dumped
        if dumped:
            return
        dumped = True
        try:
            tracer.results().write_results(show_missing=True, coverdir=str(trace_dir))
        except Exception as error:  # noqa: BLE001 — ver el comentario
            # La instrumentación no puede cambiar el veredicto del programa
            # medido. `write_results` recorre las cuentas acumuladas y abre cada
            # fichero fuente para escribir su `.cover`; si uno de ellos ya no
            # existe —un test borrado desde la corrida anterior— revienta con
            # `FileNotFoundError`, y sin este `except` esa excepción se
            # convertiría en el código de salida del envoltorio. Eso es
            # exactamente lo que este fichero existe para no hacer: preservar
            # el código real del objetivo.
            print(f"trace_run: no se pudieron volcar las cuentas: {error}", file=sys.stderr)

    real_exit = os._exit

    def patched_exit(status: int = 0) -> None:
        # `Trace.runctx` sólo desinstala su propio `sys.settrace` en su
        # `finally`, y ese `finally` nunca llega a correr si el código que
        # envuelve termina aquí, en `os._exit`, en vez de retornar. Sin
        # desinstalarlo a mano, la traza seguiría activa mientras
        # `write_results` recorre `self.counts`, contando las propias líneas
        # de ese recorrido y mutando el diccionario mientras se itera.
        sys.settrace(None)
        threading.settrace(None)
        dump()
        real_exit(status)

    sys.argv = [module or script, *args]
    _prepare_sys_path(script)
    os._exit = patched_exit  # type: ignore[assignment]
    exit_code = 0
    try:
        source, source_globals = _target_source(module, script)
        try:
            tracer.runctx(source, globals=source_globals)
        except SystemExit as exc:
            exit_code = _exit_code_of(exc)
    finally:
        os._exit = real_exit
        dump()
    return exit_code


def main(argv: list[str]) -> int:
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2

    if argv[0] == "-m":
        if len(argv) < 2:
            print(USAGE, file=sys.stderr)
            return 2
        module, script, rest = argv[1], None, argv[2:]
    else:
        module, script, rest = None, argv[0], argv[1:]

    trace_dir_value = os.environ.get("VENOXIA_TRACE_DIR")
    if not trace_dir_value:
        return _run_plain(module, script, rest)
    return _run_traced(module, script, rest, Path(trace_dir_value))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
