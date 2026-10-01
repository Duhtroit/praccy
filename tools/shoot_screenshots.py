#!/usr/bin/env python3
"""Capture the screenshots in docs/images, for the README.

The app is a local web UI, so the honest way to photograph it is a browser
loading it from the same server the app uses -- not a mock-up, and not the
native window. `screencapture` is unavailable on this machine (assistive
access is not granted), and in any case a windowed screenshot of the real app
would vary with the window size and the user's display, which is the wrong
thing to put in a README that has to look the same for everyone who reads it.

So this drives a headless Chrome over the DevTools protocol, with the viewport
fixed, and writes PNGs. It runs the same `cbp/server.py` the app runs, so what
lands in the file is the app.

    python3 tools/shoot_screenshots.py
    python3 tools/shoot_screenshots.py --port 8777   # an already-running server

Everything is standard library plus Chrome, because the point of this script is
to document a project with no dependencies, and a screenshot tool that needed a
package manager would be a poor advertisement for it.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"

WIDTH, HEIGHT = 1280, 860
SCALE = 2  # Retina, because a README screenshot at 1x looks soft on most displays

# Chrome, in the order a developer is most likely to have it. Brave is Chromium
# under another name and speaks the same protocol, so it is a valid fallback
# rather than a curiosity.
CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def find_chrome() -> str:
    for path in CANDIDATES:
        if path and os.path.exists(path):
            return path
    raise SystemExit("No Chrome or Chromium found. Install one, or pass --chrome.")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Chrome:
    """A headless Chrome driven over the DevTools protocol.

    Minimal on purpose: launch, open a page, run some JavaScript, screenshot,
    close. Anything more would be a browser automation library, and this only
    needs four verbs.
    """

    def __init__(self, binary: str, port: int):
        self.binary = binary
        self.port = port
        self.profile = tempfile.mkdtemp(prefix="praccy-shots-")
        self.process = None
        self.socket = None
        self._id = 0

    def __enter__(self):
        self.process = subprocess.Popen([
            self.binary,
            "--headless=new",
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile}",
            # Fixed window size, and no scrollbar, so the capture is the layout
            # rather than the layout plus whatever the reader's scrollbar does.
            f"--window-size={WIDTH},{HEIGHT}",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
            "--disable-extensions",
            "--mute-audio",
            "--disable-background-networking",
            # An empty profile rather than the user's: otherwise Chrome loads
            # their extensions into the page being photographed, and one of them
            # injecting a stylesheet or a devtools overlay lands in the README.
            "--incognito",
            "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # The protocol endpoint is only listening once the browser has started,
        # and it prints the URL, which is more reliable than a fixed guess.
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{self.port}/json/list", timeout=2) as r:
                    targets = json.loads(r.read().decode())
                # Only a real page, and only about:blank -- Chrome lists its own
                # browser_ui and extension targets first, and driving one of
                # those closes the socket rather than answering.
                pages = [t for t in targets
                         if t.get("type") == "page"
                         and t.get("url", "").startswith("about:")]
                if pages:
                    target = pages[0]
                    break
            except Exception:
                time.sleep(0.2)
        if not target:
            raise SystemExit("Chrome did not expose a page to drive.")

        self.socket = _connect(target["webSocketDebuggerUrl"])
        self.send("Page.enable")
        self.send("Runtime.enable")
        return self

    def __exit__(self, *exc):
        try:
            if self.socket:
                self.socket.close()
        finally:
            if self.process:
                self.process.terminate()
            shutil.rmtree(self.profile, ignore_errors=True)

    def send(self, method, params=None):
        """One CDP call, by id, reading back the matching reply."""
        self._id += 1
        message = json.dumps({"id": self._id, "method": method,
                              "params": params or {}}).encode()
        self.socket.sendall(_frame(message))
        while True:
            reply = json.loads(_recv(self.socket).decode())
            if reply.get("id") == self._id:
                if "error" in reply:
                    raise RuntimeError(f"{method}: {reply['error']}")
                return reply.get("result", {})

    def goto(self, url: str, settle_ms: int = 2500):
        self.send("Page.navigate", {"url": url})
        # A fixed wait rather than a load event: the app's content arrives from
        # /api/track after first paint, so "loaded" is too early to photograph.
        time.sleep(settle_ms / 1000.0)

    def js(self, expression: str, settle_ms: int = 900):
        """Run JS in the page and wait afterwards, for the app to settle.

        `awaitPromise` means a script that returns a promise is waited on, so
        the shot that has to wait for the grader waits for the grader rather
        than for a guessed interval.

        A thrown exception here is fatal, and it is checked explicitly. The
        alternative -- ignoring `exceptionDetails` -- means a script with a
        syntax error captures the app's default state and reports success, which
        is how a broken shot script produces four plausible-looking screenshots
        of the wrong thing instead of one error.
        """
        result = self.send("Runtime.evaluate", {
            "expression": f"(async function(){{ {expression} }})()",
            "awaitPromise": True,
            "returnByValue": True,
        })
        if "exceptionDetails" in result:
            detail = result["exceptionDetails"]
            text = detail.get("exception", {}).get("description") or detail.get("text")
            raise SystemExit(f"The screenshot script threw: {text}")
        time.sleep(settle_ms / 1000.0)
        return result.get("result", {}).get("value")

    def shot(self, path: Path):
        result = self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(result["data"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return len(data)


def _connect(url: str):
    """A WebSocket client, in about forty lines of standard library."""
    import base64 as b64
    import hashlib
    import os as _os
    import socket as _socket
    import struct

    assert url.startswith("ws://")
    rest = url[5:]
    hostport, _, path = rest.partition("/")
    host, _, port = hostport.partition(":")
    sock = _socket.create_connection((host, int(port or 80)), timeout=30)

    key = b64.b64encode(_os.urandom(16)).decode()
    request = (
        f"GET /{path} HTTP/1.1\r\n"
        f"Host: {hostport}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(request.encode())
    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(4096)
    # Long: one evaluate waits on the grader compiling and running code, which
    # takes tens of seconds, and the default 30s socket timeout aborts it
    # mid-wait and takes the browser session down with it.
    sock.settimeout(180)
    if b"101" not in response.split(b"\r\n")[0]:
        raise SystemExit(f"WebSocket upgrade failed: {response[:200]!r}")
    del hashlib  # imported for the shape of the upgrade; unused
    return sock


def _frame(payload: bytes) -> bytes:
    """One masked client text frame.

    The mask is not optional. RFC 6455 requires every frame from a client to be
    masked, and Chrome enforces it: an unmasked frame is not answered and not
    reported, the connection simply closes, which is why this failed as a bare
    ConnectionError with nothing in the browser's log to explain it.
    """
    import os as _os
    import struct as _struct

    mask = _os.urandom(4)
    masked = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
    length = len(payload)
    # The 7-bit length covers short frames; the rest need an explicit 16- or
    # 64-bit form, and a CDP command is well under 126 bytes.
    if length < 126:
        header = b"\x81" + bytes([0x80 | length])
    elif length < 65536:
        header = b"\x81" + bytes([0x80 | 126]) + _struct.pack(">H", length)
    else:
        header = b"\x81" + bytes([0x80 | 127]) + _struct.pack(">Q", length)
    return header + mask + masked


def _recv(sock) -> bytes:
    """Read one WebSocket frame, unmasked from the server as the spec requires."""
    def read(n):
        out = b""
        while len(out) < n:
            chunk = sock.recv(n - len(out))
            if not chunk:
                raise ConnectionError("closed")
            out += chunk
        return out

    header = read(2)
    length = header[1] & 0x7F
    if length == 126:
        length = int.from_bytes(read(2), "big")
    elif length == 127:
        length = int.from_bytes(read(8), "big")
    return read(length)


# The shots. Each is a JS snippet that puts the app in a state worth
# photographing, then a capture.
#
# Opening a question is asynchronous: the click fetches /api/question/<id> and
# the editor is filled with the starter code when that resolves. A script that
# clicks and immediately assigns `editor.value` therefore writes into an editor
# that is about to be overwritten, and the shot captures the starter instead.
# So the click returns a promise that settles once the starter has landed, and
# everything after it is sequenced behind that.
OPEN_TWO_SUM = """
  async function openTwoSum() {
    const items = [...document.querySelectorAll('.question-item')];
    const two = items.find(i => i.textContent.includes('Two Sum'));
    const started = Date.now();
    (two || items[0]).click();
    // "pass" is the starter code for this question, so its presence is proof
    // the fetch has resolved and the editor has been seeded. Writing before
    // that lands writes into an editor that is about to be overwritten.
    for (;;) {
      const ed = document.getElementById('editor');
      if (ed && ed.value.indexOf('pass') !== -1) return true;
      if (Date.now() - started > 15000) throw new Error('question never loaded');
      await new Promise(r => setTimeout(r, 150));
    }
  }
"""

# Wait for the grader. Submitting is not instant: the code is written to a temp
# directory, compiled or interpreted, and run against every case, and
# photographing a spinner would show nothing useful.
SUBMIT = """
  async function submitAndWait() {
    document.getElementById('submit-btn').click();
    const started = Date.now();
    for (;;) {
      const r = document.getElementById('result');
      const settled = r && !r.hidden && /pass|fail|error/i.test(r.className || '');
      if (settled && Date.now() - started > 2500) return 'graded';
      if (Date.now() - started > 60000) throw new Error('the grader never returned');
      await new Promise(res => setTimeout(res, 300));
    }
  }
"""

# The examples panel is tall, and left open it pushes the editor -- the part a
# reader is actually looking at -- below the fold. It is a <section> with a
# toggle button rather than a <details>, so there is no `open` to clear; the
# button is pressed when the state reads "Hide", which is how the app itself
# collapses it.
COLLAPSE_EXAMPLES = """
  const toggle = document.getElementById('examples-toggle');
  const state = document.getElementById('examples-state');
  if (toggle && state && state.textContent.trim() === 'Hide') toggle.click();
"""

# The pane, not the window, is what scrolls: `.pane` carries `overflow-y:
# auto`. Scrolling the window scrolls nothing, which is why the editor stayed
# below the fold in the first capture.
FRAME = """
  function frame(placeholder, offset) {
    const pane = document.getElementById('pane');
    const target = document.getElementById(placeholder);
    if (!pane || !target) throw new Error('cannot frame ' + placeholder);
    pane.scrollTop = Math.max(0, target.offsetTop - pane.clientHeight * offset);
  }
"""


def frame(placeholder: str, offset: float = 0.12) -> str:
    return (f"frame('{placeholder}', {offset});")

SET_CODE = """
  const ed = document.getElementById('editor');
  ed.value = CODE.join('\\n');
  ed.dispatchEvent(new Event('input', {bubbles: true}));
"""

GOOD_CODE = ["def TwoSum(nums, target):",
             "    seen = {}",
             "    for i, n in enumerate(nums):",
             "        want = target - n",
             "        if want in seen:",
             "            return [seen[want], i]",
             "        seen[n] = i",
             "    return 'not possible'"]

# Deliberately returning [j, i] -- the pair is right and the order is
# backwards. That is the mistake the panel exists to catch, and it passes two
# of the three cases, which is exactly what a near-miss looks like.
NEAR_MISS_CODE = ["def TwoSum(nums, target):",
                  "    for i in range(len(nums)):",
                  "        for j in range(i + 1, len(nums)):",
                  "            if nums[i] + nums[j] == target:",
                  "                return [j, i]",
                  "    return 'not possible'"]


def code(lines) -> str:
    """SET_CODE with the code spliced in as a real JS array literal."""
    literal = ", ".join("'" + line.replace("\\", "\\\\").replace("'", "\\'") + "'"
                        for line in lines)
    return SET_CODE.replace("CODE", "[" + literal + "]")


SHOTS = [
    ("practice.png", "dark", f"""
      {FRAME}
      document.getElementById('view-practice').click();
      {OPEN_TWO_SUM}
      await openTwoSum();
      {code(GOOD_CODE)}
      {COLLAPSE_EXAMPLES}
      {frame('editor')}
    """, 20000),

    ("verdict.png", "dark", f"""
      {FRAME}
      document.getElementById('view-practice').click();
      {OPEN_TWO_SUM}
      {SUBMIT}
      await openTwoSum();
      {code(NEAR_MISS_CODE)}
      {COLLAPSE_EXAMPLES}
      await submitAndWait();
      {frame('result', 0.0)}
    """, 40000),

    ("course.png", "dark", f"""
      {FRAME}
      document.getElementById('view-track').click();
      document.querySelectorAll('.module')[0].open = true;
      const p = [...document.querySelectorAll('.principle')]
        .find(x => x.querySelector('.walkthrough'));
      const more = p.querySelector('.beat-more');
      for (let i = 0; i < 5; i++) more.click();
      p.querySelectorAll('.walk-line')[1].click();
      frame('track-pane', 0.0);
      window.scrollTo(0, 0);
    """),

    ("course-light.png", "light", f"""
      {FRAME}
      document.getElementById('theme-btn').click();
      document.getElementById('view-track').click();
      document.querySelectorAll('.module')[0].open = true;
      const p = [...document.querySelectorAll('.principle')]
        .find(x => x.querySelector('.walkthrough'));
      const more = p.querySelector('.beat-more');
      for (let i = 0; i < 5; i++) more.click();
      p.querySelectorAll('.walk-line')[1].click();
      frame('track-pane', 0.0);
      window.scrollTo(0, 0);
    """),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="capture README screenshots")
    parser.add_argument("--port", type=int, help="use an already-running server")
    parser.add_argument("--chrome", help="path to a Chrome or Chromium binary")
    args = parser.parse_args()

    binary = args.chrome or find_chrome()
    print(f"  chrome  {binary}")

    server = None
    port = args.port
    if not port:
        # A dedicated state directory, so photographing the app cannot write to
        # the real settings file. A screenshot that changed the viewer's
        # preferences would be a surprising thing for a script to do.
        state = tempfile.mkdtemp(prefix="praccy-shots-state-")
        env = dict(os.environ, PRACCY_STATE_DIR=state)
        server = subprocess.Popen(
            [sys.executable, "-m", "cbp.server", "--port", "0", "--quiet"],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, text=True,
        )
        port = int(server.stdout.readline().strip().split("=")[1])
        print(f"  server  http://127.0.0.1:{port} (isolated state)")

    try:
        with Chrome(binary, free_port()) as chrome:
            chrome.goto(f"http://127.0.0.1:{port}/")
            # The store has to hydrate before any shot reads a preference, or
            # the theme and the question list are both at their defaults.
            chrome.js("return new Promise(r => setTimeout(r, 2000));", 1200)

            for shot in SHOTS:
                name, theme, script = shot[0], shot[1], shot[2]
                # A shot whose script waits on something (the grader) gets its
                # own budget; the rest are a fixed beat for the entrance
                # animations to finish.
                settle = shot[3] if len(shot) > 3 else 1400
                # Each shot starts from the top of the app rather than from
                # wherever the last one left it.
                chrome.goto(f"http://127.0.0.1:{port}/", settle_ms=2600)
                chrome.js("return new Promise(r => setTimeout(r, 1200));", 600)
                if theme == "dark" and chrome.js(
                        "return document.documentElement.dataset.theme;") == "light":
                    chrome.js("document.getElementById('theme-btn').click();", 500)
                chrome.js(script, settle)
                size = chrome.shot(OUT / name)
                print(f"  shot    docs/images/{name} "
                      f"({size // 1024}KB, {WIDTH}x{HEIGHT} @{SCALE}x)")
    finally:
        if server:
            server.terminate()

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
