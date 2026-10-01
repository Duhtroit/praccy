"""Local HTTP server for the browser UI.

Standard library only -- no dependencies to install. Serves the web app and a
small JSON API backed by the same engine the terminal client uses.

    python3 -m cbp.server            # http://127.0.0.1:8777
    python3 -m cbp.server --port 9000
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional

from . import api
from . import settings as preferences
from .adapters import LANGUAGES
from .engine import load_questions
from .toolchain import report as toolchain_report
from .track import track_payload

WEB_ROOT = os.path.join(os.path.dirname(__file__), "web")
DEFAULT_PORT = 8777

# Printed to stdout as `PORT=<n>` before serving, so a launcher can discover
# where to point a webview. Passing --port 0 asks the OS for a free port,
# which is what the app does: a fixed 8777 means a second copy of Praccy, or an
# unrelated dev server, silently breaks the first one.
PORT_PREFIX = "PORT="

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    # The two bundled typefaces. Without the woff2 entry the font request comes
    # back as application/octet-stream and the browser discards it, which looks
    # exactly like a missing font file rather than like a MIME error.
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".wav": "audio/wav",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "Praccy"

    # Keep the terminal readable; the browser is the real audience here.
    def log_message(self, fmt, *args):
        pass

    # -- helpers ----------------------------------------------------------

    def _send_json(self, payload, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, relative: str):
        # Resolve a URL path to a file inside the web root.
        #
        # Written with explicit segment handling rather than
        # `os.path.normpath(...).lstrip("/")` because that idiom is correct only
        # on a platform whose separator is "/". On Windows, `normpath` rewrites
        # "/fonts/x.woff2" to "\\fonts\\x.woff2", `lstrip("/")` does not strip a
        # leading backslash, and `os.path.join` then treats the result as an
        # absolute path and throws the drive letter away -- producing
        # "\fonts\x.woff2", which is not under the web root at all. The guard
        # below then correctly refuses it, and the symptom is a 403 on every
        # static file: the interface loads its HTML and then cannot load its
        # stylesheet, its scripts or its fonts.
        #
        # So the path is treated as what it is -- a list of URL segments -- and
        # ".." is rejected outright rather than being normalised and hoped for.
        # That is both correct on every platform and a clearer refusal.
        parts = [part for part in relative.replace("\\", "/").split("/")
                 if part and part != "."]
        if any(part == ".." for part in parts):
            self._send_json({"error": "forbidden"}, 403)
            return
        path = os.path.join(WEB_ROOT, *parts)
        root = os.path.abspath(WEB_ROOT)
        if os.path.commonpath([root, os.path.abspath(path)]) != root:
            self._send_json({"error": "forbidden"}, 403)
            return
        if not os.path.isfile(path):
            self._send_json({"error": "not found"}, 404)
            return

        ext = os.path.splitext(path)[1]
        with open(path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        # This is a local dev server you edit the source of. Without an
        # explicit no-store the browser heuristically caches style.css and
        # app.js, and every change appears not to have happened.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # -- routes -----------------------------------------------------------

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/", "/index.html"):
            self._send_file("index.html")
        elif path == "/api/track":
            self._send_json(track_payload(load_questions()))
        elif path == "/api/questions":
            self._send_json({
                "questions": api.catalogue(load_questions()),
                "languages": LANGUAGES,
            })
        elif path == "/api/deps":
            self._send_json(toolchain_report())
        elif path == "/api/settings":
            self._send_json({"settings": preferences.read()})
        elif path == "/api/port":
            # Lets the web layer discover an ephemeral port after a redirect,
            # which is how the app recovers if the server ever moves.
            self._send_json({"port": self.server.server_address[1]})
        elif path.startswith("/api/question/"):
            qid = path[len("/api/question/"):]
            self._serve_question(qid, include_solution="?solution=1" in self.path)
        else:
            self._send_file(path)

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/settings":
            # Merged rather than replaced, so a tab that has been open since
            # before a preference existed cannot silently drop it.
            stored = preferences.read()
            stored.update(self._read_body())
            self._send_json({"settings": preferences.write(stored)})
            return
        if path != "/api/run":
            self._send_json({"error": "not found"}, 404)
            return

        body = self._read_body()
        qid = body.get("questionId")
        language = body.get("language")
        source = body.get("code", "")

        if not qid or not language or not source.strip():
            self._send_json({"error": "questionId, language and code are required"}, 400)
            return
        if language not in LANGUAGES:
            self._send_json({"error": f"unsupported language {language!r}"}, 400)
            return

        question = next((q for q in load_questions() if q["id"] == qid), None)
        if question is None:
            self._send_json({"error": f"unknown question {qid!r}"}, 404)
            return

        payload = api.evaluate_payload(question, language, source)
        self._send_json(payload)

    def _serve_question(self, qid: str, include_solution: bool = False):
        question = next((q for q in load_questions() if q["id"] == qid), None)
        if question is None:
            self._send_json({"error": f"unknown question {qid!r}"}, 404)
            return
        self._send_json(api.question_payload(question, include_solution))

    def do_OPTIONS(self):
        # Same-origin only, so this exists purely to be uninteresting.
        self.send_response(204)
        self.end_headers()


def serve(port: int = DEFAULT_PORT, host: str = "127.0.0.1",
          announce: bool = True) -> int:
    if not os.path.isdir(WEB_ROOT):
        print(f"  error: web assets not found at {WEB_ROOT}")
        return 1

    httpd = ThreadingHTTPServer((host, port), Handler)
    bound = httpd.server_address[1]
    # Machine-readable first and on its own line, before the human banner.
    # A launcher reads stdout until it sees this, so it must not be buried
    # under decoration or the app waits forever for a port that already exists.
    print(f"{PORT_PREFIX}{bound}", flush=True)
    if announce:
        print()
        print("  Praccy")
        print("  " + "-" * 40)
        print(f"  open  http://{host}:{bound}")
        print("  stop  Ctrl-C")
        print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        if announce:
            print("\n  stopped.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    port = DEFAULT_PORT
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    sys.exit(serve(port, announce="--quiet" not in sys.argv))
