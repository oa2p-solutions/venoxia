#!/usr/bin/env python3
"""Runner de pruebas falso para `tests/test_oracle.py`.

`oracle.py` no distingue este script de un runner de verdad: recibe las
rutas que `verifies:` declaraba, ya sustituidas en el `test_command`, como
argumentos posicionales. No ejecuta ningún test real; sólo lee el marcador
que el propio test escribió dentro del fichero y hace lo que dice:

* `# RESULT: red` (o `// RESULT: red`, para ficheros que comentan con `//`) en
  cualquiera de los ficheros recibidos → sale con `1`.
* `# RESULT: sleep <N>` (o `// RESULT: sleep <N>`) → duerme `N` segundos antes
  de decidir el código.
* en cualquier otro caso → sale con `0`.

Cada invocación deja constancia de qué rutas recibió en el fichero que señala
la variable de entorno `FAKE_RUNNER_LOG` (una línea, las rutas separadas por
tabulador). Es lo que permite a los tests comprobar que un requisito con
`verifies:` inexistente **no** invoca este runner: si no hay línea con esa
ruta, no se llamó.
"""

from __future__ import annotations

import os
import re
import sys
import time

RED_RE = re.compile(r"(?:#|//)\s*RESULT:\s*red\b", re.IGNORECASE)
SLEEP_RE = re.compile(r"(?:#|//)\s*RESULT:\s*sleep\s+([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)

LOG_ENV_VAR = "FAKE_RUNNER_LOG"


def _log_invocation(paths: list[str]) -> None:
    """Anota esta llamada en el log, si el test ha pedido uno."""
    log_path = os.environ.get(LOG_ENV_VAR)
    if not log_path:
        return
    try:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write("\t".join(paths))
            handle.write("\n")
    except OSError:
        # El propio fake_runner no puede tumbar el test por no poder loguear.
        pass


def main(argv: list[str]) -> int:
    paths = argv[1:]
    _log_invocation(paths)

    red = False
    sleep_seconds = 0.0
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        if RED_RE.search(text):
            red = True
        match = SLEEP_RE.search(text)
        if match:
            sleep_seconds = max(sleep_seconds, float(match.group(1)))

    if sleep_seconds:
        time.sleep(sleep_seconds)

    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
