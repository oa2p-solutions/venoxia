#!/usr/bin/env python3
"""Runner de pruebas falso para el fixture `oracle-red-then-green`.

Copia exacta de `tests/fake_runner.py` (el que usa `tests/test_oracle.py`),
metida dentro del proyecto de juguete para que `.venoxia/venoxia.json` pueda
declarar un `test_command` que no sale del propio fixture. `oracle.py` no
distingue este script de un runner de verdad: recibe las rutas que
`verifies:` declaraba, ya sustituidas en el `test_command`, como argumentos
posicionales. No ejecuta ningún test real; sólo lee el marcador que el
propio fichero de test lleva escrito y hace lo que dice:

* `// RESULT: red` (o `# RESULT: red`) en cualquiera de los ficheros
  recibidos → sale con `1`.
* `// RESULT: sleep <N>` (o `# RESULT: sleep <N>`) → duerme `N` segundos
  antes de decidir el código.
* en cualquier otro caso → sale con `0`.
"""

from __future__ import annotations

import re
import sys
import time

RED_RE = re.compile(r"(?:#|//)\s*RESULT:\s*red\b", re.IGNORECASE)
SLEEP_RE = re.compile(r"(?:#|//)\s*RESULT:\s*sleep\s+([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)


def main(argv: list[str]) -> int:
    paths = argv[1:]

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
