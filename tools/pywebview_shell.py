#!/usr/bin/env python3
"""A cross-platform shell for the existing UI, in place of the Swift one.

PROTOTYPE. This exists to answer one question -- can the macOS-only shell in
`app/main.swift` be replaced by something that also runs on Windows and Linux --
without rewriting any of `cbp/`. The answer it gives is yes, and this file is
the evidence. It is not yet a product: no icon, no dependency panel, no log
menu, no bundle.

    python3 tools/pywebview_shell.py             # open the window
    python3 tools/pywebview_shell.py --check     # start, probe, exit, no window

What it proves, and what it costs, is below. The short version: the whole shell
is about sixty lines because pywebview already owns the three things
`main.swift` spends most of its length on -- the window, the platform webview
(WKWebView, WebView2, WebKitGTK), and the Python<->JS bridge.

The three things worth keeping from the Swift shell:

  * The server runs in-process on an ephemeral port, and the window is pointed
    at it. In-process rather than as a child process, because that removes the
    stdout `PORT=<n>` handshake, the child reaping on quit, and the entire
    class of "the app quit and the server is still running". `ThreadingHTTPServer`
    hands back the port directly (`server_port`), so nothing has to be parsed.
  * A Finder-launched app inherits `PATH=/usr/bin:/bin:/usr/sbin:/sbin`, and the
    toolchain probe depends on what is on it. `_search_path` does the same
    prepending `ServerProcess.searchPath` does.
  * The dependency check runs against the same `/api/deps` the Swift panel
    reads, so the data is already cross-platform; only the panel is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cbp.server import Handler  # noqa: E402  (needs ROOT on the path first)

WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 860

# What a shell would inherit from a Finder-launched .app, and the installs a
# developer has put on their PATH that the toolchain probe should still find.
# The first entry matters most: on macOS `clang++` lives in the xcrun shim and
# has to be found before anything in /usr/local, or the C++ path reports itself
# missing on a machine where it is installed.
EXTRA_PATH = (
    "/usr/bin",
    "/bin",
    "/usr/sbin",
    "/sbin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.cargo/bin"),
)


def _search_path() -> str:
    """A PATH that includes what a shell would have had, first."""
    inherited = os.environ.get("PATH", "")
    parts = [p for p in inherited.split(os.pathsep) if p]
    for entry in EXTRA_PATH:
        if entry not in parts:
            parts.append(entry)
    return os.pathsep.join(parts)


def start_server() -> ThreadingHTTPServer:
    """The same handler on a port the OS picks, in this process.

    Port 0 rather than a fixed 8777 for the reason `server.py` documents: a
    fixed port means a second copy of Praccy, or an unrelated dev server,
    silently breaks the first one.
    """
    os.environ["PATH"] = _search_path()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def probe(port: int) -> dict:
    """Ask the API what the app needs, the way the dependency panel does."""
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/deps", timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="start the server, probe it, and exit without a window")
    args = parser.parse_args()

    httpd = start_server()
    port = httpd.server_port
    url = f"http://127.0.0.1:{port}/"
    print(f"server on {url}")

    deps = probe(port)
    missing = [d["language"] for d in deps.get("languages", []) if not d.get("ok")]
    print(f"toolchains: {'all present' if not missing else 'missing ' + ', '.join(missing)}")

    if args.check:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read().decode()
        print(f"index.html served: {len(body)} bytes, "
              f"theme gate present: {'data-theme' in body}")
        httpd.shutdown()
        httpd.server_close()
        return 0

    import webview

    window = webview.create_window(
        "Praccy",
        url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(420, 320),
    )
    try:
        # `closing` fires before the window goes away, which is the last point
        # at which the port can still be released cleanly.
        def closing():
            httpd.shutdown()
            httpd.server_close()

        window.events.closing += closing
        webview.start()
    finally:
        httpd.shutdown()
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
