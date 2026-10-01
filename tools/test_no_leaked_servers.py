"""Report any Praccy servers still running.

Matching is on the *executable* rather than on the line containing a path, and
that distinction is the whole point. A substring search matches any process
that merely mentions the path -- including the shell running this check, whose
command line contains it -- and a check that reports itself as a leak is worse
than no check. Three phantom leaks came from that before this was fixed.

    python3 tools/test_no_leaked_servers.py
"""

import subprocess
import sys

APP_EXECUTABLE_SUFFIX = "MacOS/" + "Praccy"
SERVER_EXECUTABLE_SUFFIX = (
    ".app/Contents/Resources/" + "python/bin/python3.12"
)
SERVER_MODULE = "-m cbp.server"


def _argv(line: str) -> list:
    return line.split()


def classify() -> tuple:
    ps = subprocess.run(["ps", "-Ao", "pid,command"],
                        capture_output=True, text=True).stdout
    apps, servers = [], []
    for line in ps.splitlines()[1:]:
        argv = _argv(line)
        if len(argv) < 2 or not argv[0].isdigit():
            continue
        pid, argv = argv[0], argv[1:]
        if not argv:
            continue
        # The first argument is the program being run. Only that counts.
        if argv[0].endswith(APP_EXECUTABLE_SUFFIX):
            apps.append((pid, line))
        elif argv[0].endswith(SERVER_EXECUTABLE_SUFFIX) and SERVER_MODULE in argv:
            servers.append((pid, line))
    return apps, servers


def main() -> int:
    apps, servers = classify()

    if apps:
        # A running app is supposed to have a server. Reporting one here as a
        # leak is wrong, and was: an earlier version of this check flagged the
        # healthy steady state as a failure.
        print(f"  running: {len(apps)} app, {len(servers)} server -- expected")
        return 0

    if servers:
        print(f"  LEAK: {len(servers)} server(s) with no app:")
        for _, line in servers:
            print(f"    {line.strip()[:110]}")
        print("\n  A server outliving the app holds its port. Quit Praccy.")
        return 1

    print("  no leaked servers (app not running)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
