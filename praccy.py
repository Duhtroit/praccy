#!/usr/bin/env python3
"""Praccy -- the application shell.

This is the thing you launch. It owns the window and nothing else: the UI is
`cbp/web`, the grading is `cbp/engine.py`, and the HTTP surface between them is
`cbp/server.py`. This file starts that server, points a native webview at it,
and gets out of the way.

    python3 praccy.py            # open the window
    python3 praccy.py --check    # start, probe, exit, no window
    python3 praccy.py --deps     # print the toolchain report and exit

Replaces the macOS-only Swift app in `app/`. The reason it can is that
pywebview already owns the three things `app/main.swift` spent most of its
length on -- the window, the platform webview (WKWebView, WebView2, WebKitGTK)
and the Python/JS bridge -- so the shell is a few dozen lines rather than a few
hundred, and the same file runs on all three systems.

Three things are carried over from the Swift shell deliberately:

  * The server runs in-process on a port the OS picks, and the window is
    pointed at it. In-process rather than as a child, which removes the stdout
    `PORT=<n>` handshake, the child reaping on quit, and the whole class of bug
    where the app quits and the server keeps running. `ThreadingHTTPServer`
    hands back the port directly, so nothing has to be parsed.

  * A launched app inherits a nearly empty PATH -- `/usr/bin:/bin:/usr/sbin:
    /sbin` from Finder, and on Windows whatever Explorer was started with. The
    toolchain probe depends on what is on it, so `_search_path` puts back the
    directories each platform's installers actually use.

  * The dependency check reads the same `/api/deps` the old native panel read,
    so the data was already cross-platform and only the presentation was
    missing. `_dependency_report` and the failure dialog are that presentation.

Only `pywebview` is needed beyond the standard library, and only to open a
window: `--check` and `--deps` run with no third-party import at all, so the
shell can be smoke-tested on a machine that has never installed it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer

APP_NAME = "Praccy"
WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 860


def _resource_root() -> str:
    """The directory holding `cbp/`, wherever this is running from.

    A frozen build (PyInstaller) puts its data next to the unpacked executable
    under `sys._MEIPASS`, and a one-file build unpacks to a temp directory that
    is deleted on exit -- so the web root is only ever valid for the lifetime of
    the process, which is fine, because the server reads it there. A source run
    uses the checkout. Anything else raises rather than guessing, because a
    silent fallback would serve a 404 page and look like a broken app.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", None)
        if base and os.path.isdir(os.path.join(base, "cbp", "web")):
            return base
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(here, "cbp", "web")):
        return here
    # A frozen build where the data is not where it should be is a packaging
    # bug, and saying so is more use than serving a directory of 404s.
    raise SystemExit(
        f"{APP_NAME}: cannot find the interface files (cbp/web).\n"
        f"  looked in: {here}\n"
        f"  this is a packaging error, not a usage one."
    )


ROOT = _resource_root()
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cbp.server import Handler  # noqa: E402  (needs ROOT on the path first)
from cbp.settings import directory as settings_directory  # noqa: E402
from cbp.toolchain import report as toolchain_report  # noqa: E402

# What a launched app inherits, plus the directories each platform's installers
# actually write to. Order is deliberate: on macOS `/usr/bin/clang++` is an
# xcrun shim that has to win over anything in /usr/local, or C++ reports itself
# missing on a machine where it is installed.
_UNIX_PATH = (
    "/usr/bin",
    "/bin",
    "/usr/sbin",
    "/sbin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.cargo/bin"),
    os.path.expanduser("~/.dotnet"),
)

_WINDOWS_PATH = (
    os.path.expanduser("~/.cargo/bin"),
    os.path.expanduser("~/.dotnet"),
    r"C:\Program Files\dotnet",
    r"C:\Program Files (x86)\dotnet",
    r"C:\Program Files\LLVM\bin",
)


def _search_path() -> str:
    """A PATH that has the platform's toolchain directories in it.

    Appended rather than prepended, so a developer running from a terminal
    still gets whatever they have set up first, and a launched app still finds
    the compilers an installer put somewhere unusual.
    """
    inherited = os.environ.get("PATH", "")
    parts = [p for p in inherited.split(os.pathsep) if p]
    extra = _WINDOWS_PATH if sys.platform == "win32" else _UNIX_PATH
    for entry in extra:
        if entry and entry not in parts:
            parts.append(entry)
    return os.pathsep.join(parts)


def start_server() -> ThreadingHTTPServer:
    """The same handler `server.py` serves, on a port the OS picks, in-process.

    Port 0 rather than a fixed 8777 for the reason `server.py` documents: a
    fixed port means a second copy of Praccy, or an unrelated dev server,
    silently breaks the first one.
    """
    os.environ["PATH"] = _search_path()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def get_json(port: int, path: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _dependency_report(port: int) -> dict:
    return get_json(port, "/api/deps")


def _format_deps(deps: dict) -> str:
    """The toolchain as the plain text the failure dialog and `--deps` share."""
    lines = []
    for entry in deps.get("languages", []):
        if entry.get("ok"):
            lines.append(f"  ok        {entry['language']:<7} {entry.get('version') or ''}")
        else:
            lines.append(f"  MISSING   {entry['language']}")
            for hint_line in (entry.get("install") or "").splitlines():
                if hint_line.strip():
                    lines.append(f"              {hint_line.strip()}")
    return "\n".join(lines)


def _log(message: str) -> None:
    """Append to the launch log, the way `app/main.swift`'s AppLog did.

    A window that fails to open is otherwise undebuggable, because the only
    place the reason appeared was a terminal the user had already closed.
    """
    try:
        directory = settings_directory()
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "launch.log"), "a", encoding="utf-8") as fh:
            fh.write(f"{message}\n")
    except OSError:
        pass


def _check(port: int, url: str) -> int:
    """Start, prove the UI and the fonts are actually served, exit."""
    with urllib.request.urlopen(url, timeout=30) as r:
        body = r.read().decode("utf-8")
    print(f"index.html served: {len(body)} bytes, "
          f"theme gate present: {'data-theme' in body}")

    # The fonts are the part most likely to be silently wrong, because a
    # missing file and a wrong Content-Type both end in the browser quietly
    # falling back to a system face -- the app looks fine and the type is not
    # the one that was asked for. So both bytes and MIME type are checked here.
    import mimetypes
    for name in ("InterVariable.woff2", "jbmono.woff2"):
        with urllib.request.urlopen(f"{url}fonts/{name}", timeout=30) as r:
            payload = r.read()
            ctype = r.headers.get("Content-Type")
        print(f"font {name}: {len(payload)} bytes as {ctype}")
    print("mimetypes knows woff2:",
          mimetypes.guess_type("x.woff2")[0] or "(no, the server table is used)")

    deps = _dependency_report(port)
    missing = deps.get("missing") or []
    print(f"toolchains: {'all present' if not missing else 'missing ' + ', '.join(missing)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} -- timed interview reps")
    parser.add_argument("--check", action="store_true",
                        help="start the server, probe it, and exit without a window")
    parser.add_argument("--deps", action="store_true",
                        help="print the toolchain report and exit")
    args = parser.parse_args()

    if args.deps:
        print(_format_deps(toolchain_report()))
        return 0

    httpd = start_server()
    port = httpd.server_port
    url = f"http://127.0.0.1:{port}/"
    print(f"server on {url}")
    _log(f"server on port {port}")

    try:
        if args.check:
            rc = _check(port, url)
            return rc

        try:
            import webview
        except ImportError:
            print(f"  {APP_NAME} needs pywebview to open a window:\n"
                  f"      pip install pywebview\n"
                  f"  Everything else runs on the standard library alone. To use "
                  f"the UI without a window, open:\n      {url}")
            _log("pywebview is not installed; printed the URL instead")
            return 1

        deps = _dependency_report(port)
        window = webview.create_window(
            APP_NAME,
            url,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_size=(420, 320),
        )
        _log(f"window opened on {url} (missing toolchains: "
             f"{', '.join(deps.get('missing') or []) or 'none'})")

        def closing():
            # Fires before the window goes away, which is the last point at
            # which the port can be released cleanly.
            httpd.shutdown()
            httpd.server_close()

        window.events.closing += closing
        webview.start()
        return 0
    finally:
        httpd.shutdown()
        httpd.server_close()
        _log("stopped")


if __name__ == "__main__":
    raise SystemExit(main())
