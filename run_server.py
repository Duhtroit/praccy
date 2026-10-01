#!/usr/bin/env python3
"""Start the practice server fully detached from the calling shell.

A plain `&` is not enough: the process stays in the shell's process group and
is reaped when that session ends. This double-forks into a new session, which
is the standard POSIX daemon pattern.

    python3 run_server.py [--port 8777]
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    port = 8777
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])

    root = os.path.dirname(os.path.abspath(__file__))

    if os.fork() > 0:
        # Parent exits immediately; the child is reparented to init.
        return 0

    os.setsid()  # new session, detached from the controlling terminal
    if os.fork() > 0:
        os._exit(0)

    # Grandchild: fully detached.
    os.chdir(root)
    os.umask(0o022)

    # Redirect the standard streams so nothing holds the shell open.
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 0)
    log = os.open("/tmp/cbp_server.log", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(log, 1)
    os.dup2(log, 2)

    sys.path.insert(0, root)
    from cbp.server import serve

    serve(port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
