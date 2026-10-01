"""Build Praccy.app.

Assembles four things into a bundle:

  * a trimmed CPython, so the app needs nothing installed to run
  * the `cbp` package, imported via PYTHONPATH rather than copied into
    site-packages, so upgrading is replacing one directory
  * a Swift shell compiled against WebKit
  * an Info.plist and an icon

Then it ad-hoc signs and installs to /Applications. Ad-hoc rather than a
Developer ID because this is not distributed: a signature that says "made on
this Mac" is enough for the machine that built it, and the alternative is a
paid account for no benefit here.

The Python is the interesting part. python-build-standalone ships 66MB, most of
it Tk, idlelib, turtledemo, ensurepip, lib2to3, pip and C headers, none of
which Praccy imports. Trimming brings it to 45MB.

    python3 tools/build_app.py                # build and install
    python3 tools/build_app.py --no-install   # build only
    python3 tools/build_app.py --arch x86_64  # Intel
"""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_NAME = "Praccy"
VERSION = "1.0"

# python-build-standalone, install_only_stripped. Pinned: an unpinned URL means
# a rebuild can silently change the interpreter under a shipped app.
PY_VERSION = "3.12.14"
PY_BUILD = "20260929"


def python_archive_name(target_arch: str) -> str:
    return f"cpython-{PY_VERSION}+{PY_BUILD}-{target_arch}-apple-darwin-install_only_stripped.tar.gz"

RELEASE = "https://github.com/astral-sh/python-build-standalone/releases/download"

# Directories and files the app cannot reach. Removing them is safe because
# `cbp.toolchain.report` and a cold `import cbp.server` are both checked
# afterwards, and the bundle only ever serves questions and runs compilers.
TRIM_DIRS = [
    "include", "share", "lib/tcl9.0", "lib/tk9.0", "lib/itcl4.3.8",
    "lib/tcl9", "lib/thread3.0.6", "lib/pkgconfig",
]
# Sibling of the dylib above rather than inside lib/tcl9.0, so listing the
# directory does not remove it. tkinter is the only thing that needs Tcl, and
# tkinter is gone.
TRIM_FILES = [
    "lib/libtcl9.0.dylib", "lib/libtcl9tk9.0.dylib",
]
TRIM_STDLIB = [
    "tkinter", "idlelib", "turtledemo", "turtle.py", "ensurepip", "lib2to3",
    "site-packages", "pydoc_data", "distutils", "unittest", "test",
    "tests", "config-3.12-darwin", "sqlite3", "venv", "wsgiref",
]
TRIM_BIN = [
    "pip", "pip3", "idle", "idle3", "pydoc", "pydoc3", "turtle",
    "2to3", "2to3-3.12", "python3-config", "python3.12-config",
    "python3.12-config.py", "python-config",
]


def log(message: str) -> None:
    print(f"  {message}", flush=True)


def run(command: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)


def arch() -> str:
    machine = os.uname().machine
    return "aarch64" if machine == "arm64" else "x86_64"


# --------------------------------------------------------------------------
# Python
# --------------------------------------------------------------------------

def fetch_python(destination: Path, target_arch: str) -> Path:
    """Download and extract a pristine interpreter, or reuse the cache.

    The cache deliberately holds the *untrimmed* tree. Trimming mutates, so
    trimming the cache would make the second build trim an already-trimmed tree
    and a changed TRIM list would never apply. The 66MB download is a
    once-per-machine cost; correctness of rebuilds is worth more.
    """
    if destination.is_dir():
        log(f"python: reusing cached download at {destination}")
        return destination

    name = python_archive_name(target_arch)
    url = f"{RELEASE}/{PY_BUILD}/{name}"
    log(f"python: downloading {name} (24MB, once)")

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "python.tar.gz"
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive) as tar:
            # The 3.12 extraction filter. The archive is a GitHub release
            # asset, so it is trusted, but the default became 'data' for
            # exactly this reason and the warning is worth silencing
            # deliberately rather than by suppressing it.
            if hasattr(tarfile, "data_filter"):
                tar.extractall(tmp, filter="data")
            else:
                tar.extractall(tmp)
        extracted = Path(tmp) / "python"
        shutil.move(str(extracted), str(destination))

    log("python: extracted")
    return destination


def trim_python(root: Path) -> None:
    """Delete what the app cannot reach, and report what it kept.

    Deliberately does not consult the import list at build time. Deciding what
    to ship from a static analysis of the source is exactly the kind of cleverness
    that produces a bundle that works until a rarely-taken path runs. The
    list below is a fixed set of things no HTTP server and no compiler driver
    needs, and the post-trim smoke test is what actually proves it.
    """
    for relative in TRIM_DIRS:
        target = root / relative
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)

    for relative in TRIM_FILES:
        target = root / relative
        if target.exists():
            target.unlink()

    for name in TRIM_STDLIB:
        target = root / "lib" / "python3.12" / name
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink()

    for name in TRIM_BIN:
        for candidate in (root / "bin" / name, root / "bin" / f"{name}3.12"):
            if candidate.exists() or candidate.is_symlink():
                candidate.unlink()

    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for cache in root.rglob("*.pyc"):
        cache.unlink(missing_ok=True)

    # `python3` and `python` are the names an operator reaches for first, so
    # they are kept as symlinks rather than trimmed away.
    for name in ("python", "python3"):
        link = root / "bin" / name
        if not link.exists():
            link.symlink_to("python3.12")

    log(f"python: trimmed to {directory_size(root) // (1024 * 1024)}MB")


def directory_size(path: Path) -> int:
    """Bytes actually occupied on disk.

    `is_file()` follows symlinks, so `bin/python`, `bin/python3` and
    `bin/python3.12` -- all the same 17MB file -- would be counted three times
    over and the reported size inflated by a third. Skipping symlinks measures
    what the bundle costs, which is the number worth reporting.
    """
    total = 0
    for entry in path.rglob("*"):
        if entry.is_symlink() or not entry.is_file():
            continue
        total += entry.stat().st_size
    return total


# --------------------------------------------------------------------------
# Bundle
# --------------------------------------------------------------------------

def copy_package(resources: Path) -> None:
    """Copy the cbp package and drop the caches a working tree accumulates."""
    destination = resources / "cbp"
    shutil.copytree(
        ROOT / "cbp", destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        symlinks=True,
    )
    log(f"cbp: {directory_size(destination) // 1024}KB")


def write_info_plist(bundle: Path) -> None:
    """Info.plist.

    NSHighResolutionCapable is worth stating explicitly: without it macOS
    renders the window at 1x on a Retina display, which on a text-heavy UI
    looks broken rather than soft.
    """
    info = {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": "dev.praccy.app",
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "CFBundleExecutable": APP_NAME,
        "CFBundlePackageType": "APPL",
        "CFBundleInfoDictionaryVersion": "6.0",
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        # The UI is a local server, so there is nothing to browse to. Declaring
        # the type keeps the window from gaining a proxy icon and keeps
        # WebKit from offering a "save page" affordance that cannot work.
        "LSApplicationCategoryType": "public.app-category.developer-tools",
        "CFBundleIconFile": "AppIcon",
        "NSHumanReadableCopyright": "Praccy",
        # The UI is served over http://127.0.0.1 by the app's own child
        # process, and WKWebView applies App Transport Security to it like any
        # other load. NSAllowsLocalNetworking permits loopback and .local
        # without opening the app up to plaintext HTTP anywhere else, which
        # NSAllowsArbitraryLoads would do.
        "NSAppTransportSecurity": {
            "NSAllowsLocalNetworking": True,
        },
    }
    with (bundle / "Contents" / "Info.plist").open("wb") as handle:
        plistlib.dump(info, handle)
    log("Info.plist: written")


def build_icon(bundle: Path) -> None:
    """Draw the app icon.

    Compiled and run at build time rather than committed as a binary, because
    the mark is the same object the web UI draws and a generator is reviewable
    in a diff where a .icns is not.
    """
    resources = bundle / "Contents" / "Resources"
    with tempfile.TemporaryDirectory() as tmp:
        generator = Path(tmp) / "makeicon"
        run(["swiftc", "-O", "-swift-version", "5",
             "-o", str(generator), str(ROOT / "app" / "Icon.swift")])
        run([str(generator), str(resources)])
        try:
            run(["iconutil", "-c", "icns",
                 str(resources / "AppIcon.iconset"),
                 "-o", str(resources / "AppIcon.icns")])
        finally:
            shutil.rmtree(resources / "AppIcon.iconset", ignore_errors=True)

    size = (resources / "AppIcon.icns").stat().st_size
    log(f"icon: {size // 1024}KB, drawn from the brand mark")


def compile_swift(bundle: Path) -> None:
    binary = bundle / "Contents" / "MacOS" / APP_NAME
    run([
        "swiftc", "-O", "-swift-version", "5",
        # The app has no entitlements and no sandbox: it starts a local server,
        # reads a bundled interpreter and shells out to four compilers, none of
        # which a sandboxed process can do without a pile of exceptions.
        "-framework", "AppKit", "-framework", "WebKit",
        "-o", str(binary),
        str(ROOT / "app" / "main.swift"),
        str(ROOT / "app" / "DependencyPanel.swift"),
    ])
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    log(f"swift: {binary.stat().st_size // 1024}KB")


def sign(bundle: Path) -> None:
    """Ad-hoc sign, after signing the nested interpreter.

    Order matters: signing the outer bundle after the inner one keeps the
    seal valid. Signing the reverse would report a broken signature on the
    nested binary, which the outer seal does not forgive.
    """
    run(["codesign", "--force", "--sign", "-",
         str(bundle / "Contents" / "Resources" / "python" / "bin" / "python3.12")])
    run(["codesign", "--force", "--deep", "--sign", "-", str(bundle)])
    check = run(["codesign", "--verify", "--verbose=2", str(bundle)])
    log(f"signed: {check.stderr.strip().splitlines()[-1] if check.stderr else 'ad-hoc'}")


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def smoke_test(bundle: Path) -> None:
    """Prove the bundle works before it is installed anywhere.

    Runs the bundled interpreter against the bundled package with no PATH
    beyond the system default, which is the only environment a Finder-launched
    app ever has. A build that cannot do this is not shipped.
    """
    resources = bundle / "Contents" / "Resources"
    python = resources / "python" / "bin" / "python3.12"
    environment = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        # The Resources directory, matching what the app sets. Pointing this at
        # cbp/ instead makes `import cbp` look for cbp/cbp, which is a mistake
        # this check is here to catch -- so it must reproduce the app's own
        # environment exactly, not an approximation of it.
        "PYTHONPATH": str(resources),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "HOME": os.path.expanduser("~"),
    }
    check = """
import json, sys
from cbp import api
from cbp.server import Handler
from cbp.toolchain import report
questions = json.load(open("cbp/data/questions.json"))["questions"]
assert len(questions) > 100, len(questions)
missing = report()["missing"]
print("MISSING:" + ",".join(missing))
"""
    proc = subprocess.run(
        [str(python), "-c", check], cwd=resources, env=environment,
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise SystemExit(f"  smoke test failed:\n{proc.stdout}\n{proc.stderr}")
    missing = ""
    for line in proc.stdout.splitlines():
        if line.startswith("MISSING:"):
            missing = line.split(":", 1)[1]
    if missing:
        log(f"smoke: ok, but missing toolchains: {missing}")
    else:
        log("smoke: interpreter, package, dataset and all toolchains verified")

    # The real handshake: launch the server the way the app does and confirm it
    # reports a port. An import succeeding and `python -m cbp.server` working
    # are different claims, and it was the second that was broken.
    server = subprocess.Popen(
        [str(python), "-m", "cbp.server", "--port", "0", "--quiet"],
        cwd=resources, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        port = ""
        for _ in range(200):
            line = server.stdout.readline().strip()
            if line.startswith("PORT="):
                port = line.split("=", 1)[1]
                break
            if not line and server.poll() is not None:
                break
        if not port:
            errors = server.stderr.read()[-800:] if server.stderr else ""
            raise SystemExit(f"  the server did not start:\n{errors}")
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/port",
                                    timeout=30) as response:
            served = json.loads(response.read())["port"]
        if str(served) != port:
            raise SystemExit(f"  port mismatch: announced {port}, served {served}")
        log(f"smoke: server started on {port} and answered /api/port")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def _app_pids() -> list:
    """PIDs of the running Praccy app, matched on the *executable*.

    Matching argv[0] rather than the whole line is deliberate. A substring
    search also matches the shell that is running this build script, whose
    command line mentions the path -- and a build that tries to kill, or reports
    a leak from, its own shell produces results that are pure noise.
    """
    ps = subprocess.run(["ps", "-Ao", "pid,command"], capture_output=True, text=True)
    found = []
    for line in ps.stdout.splitlines():
        argv = line.split()
        if len(argv) < 2 or not argv[0].isdigit():
            continue
        if argv[1].endswith("MacOS/Praccy"):
            found.append(int(argv[0]))
    return found


def stop_everything() -> None:
    """Stop the app and clear any server it left behind.

    A process killed outright never runs its cleanup, so the child can outlive
    it. The app now traps SIGTERM, but a SIGKILL from anywhere -- or a crash --
    still orphans one, and a stale server makes the next verification report a
    leak that is not there.
    """
    stop_app()
    for pid in _server_pids():
        subprocess.run(["kill", "-9", str(pid)], capture_output=True)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and _server_pids():
        time.sleep(0.2)


def stop_app() -> None:
    """Quit the app and wait for it to be gone, escalating to SIGKILL.

    Returning before the process has exited is what made a whole build verify
    the wrong binary, so this blocks until `ps` agrees there is nothing left.
    """
    for _ in range(2):
        pids = _app_pids()
        if not pids:
            return
        for pid in pids:
            subprocess.run(["kill", str(pid)], capture_output=True)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and _app_pids():
            time.sleep(0.2)
    for pid in _app_pids():
        subprocess.run(["kill", "-9", str(pid)], capture_output=True)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and _app_pids():
        time.sleep(0.2)


def _server_pids() -> list:
    """PIDs of Praccy's own bundled servers, and nothing else.

    Same reasoning as `_app_pids`: the interpreter path must be argv[0], so a
    dev-checkout `python -m cbp.server` is not counted and neither is a shell
    whose command line happens to mention the path.
    """
    ps = subprocess.run(["ps", "-Ao", "pid,command"], capture_output=True, text=True)
    found = []
    suffix = ".app/Contents/Resources/python/bin/python3.12"
    for line in ps.stdout.splitlines():
        argv = line.split()
        if len(argv) < 2 or not argv[0].isdigit():
            continue
        if argv[1].endswith(suffix) and "-m" in argv and "cbp.server" in argv:
            found.append(int(argv[0]))
    return found


def verify_window(installed: Path) -> None:
    """Launch the app and require a window with a non-zero webview.

    The window can be perfect and the app still show nothing: a webview left at
    0x0 by a collapsed Auto Layout system opens a real window with a real
    server behind it and renders a blank rectangle. Nothing about the process,
    the port or the HTTP response distinguishes that from success, so the only
    way to catch it is to read the app's own launch log and check the sizes.
    """
    log_path = Path.home() / "Library" / "Application Support" / "Praccy" / "launch.log"

    stop_everything()
    time.sleep(1)
    if _app_pids():
        raise SystemExit("  a Praccy process would not exit; not testing a new build")

    # The log is deleted rather than just read. `open -a` activates a running
    # instance instead of launching the new binary, and a stale process leaves
    # its old log behind -- which is how a build ends up cheerfully verifying
    # the previous build's behaviour. Removing the file first means the log can
    # only have been written by a process started after this point.
    log_path.unlink(missing_ok=True)
    launched = time.time()

    subprocess.run(["open", "-a", str(installed)], capture_output=True)

    deadline = time.monotonic() + 30
    text = ""
    # The settled line is written two seconds after the window is placed, so
    # the wait has to outlast it before the log can be trusted.
    while time.monotonic() < deadline:
        # Wait for the load to finish, not just for the window: the webview is
        # sized during present(), and a page title only appears once the
        # document has actually rendered into it.
        if log_path.is_file():
            text = log_path.read_text(errors="replace")
            if "settled:" in text and ("didFinish:" in text or "didFail" in text):
                break
        time.sleep(0.4)

    if not text:
        raise SystemExit("  the app wrote no launch log; it is not reaching its UI")
    if log_path.stat().st_mtime < launched - 1:
        raise SystemExit("  the launch log predates this launch; a stale process answered")

    for line in text.splitlines():
        if line.startswith(("present: set", "present: content", "didFinish:", "didFail", "start:")):
            log(f"  {line}")

    # The webview must have a real size. A 0x0 or nil webview is the failure
    # this whole check exists for.
    sized = False
    for line in text.splitlines():
        if line.startswith("didFinish:"):
            sized = "webview=(0.0, 0.0, 0.0, 0.0)" not in line
    if not sized:
        raise SystemExit(
            "  the page never rendered into a sized webview.\n"
            + text
            + "\n  A 0x0 webview opens a working window that shows nothing."
        )

    if "didFail" in text or "didFailProvisional" in text:
        raise SystemExit("  the webview could not load the local server:\n" + text)

    # The native loading spinner must not survive the page load. It is an
    # NSProgressIndicator drawn over the webview, and stopAnimation alone only
    # halts the spin -- the control stays on screen. The app logs the fact from
    # inside itself, because no external check can see another process's views.
    if "spinnerGone=true" not in text:
        raise SystemExit(
            "  the loading spinner is still on screen after the page loaded:\n"
            + text
            + "\n  A spinner that outlives the page it covered reads as a hung app."
        )
    log("spinner: gone once the page rendered")

    # The window has to end up on a real screen, and the main one. Not
    # "wherever I asked for it": on a multi-display Mac the arrangement can
    # finish reconfiguring after launch, and the system relocates the window
    # onto whichever display became main. That is correct, and a window on the
    # main display is exactly what the user needs to see something.
    settled = next((line for line in text.splitlines()
                    if line.startswith("settled: onMainScreen=")), "")
    if not settled:
        raise SystemExit("  the app never reported a settled window state:\n" + text)
    if "onMainScreen=true" not in settled:
        raise SystemExit(
            f"  the window is not on the main display:\n    {settled}\n"
            "  A window on a display nobody is looking at is indistinguishable "
            "from no window at all."
        )
    log(f"  {settled}")

    log("window: visible, sized, on the main display, page rendered")


def verify_lifecycle(installed: Path) -> None:
    """Launch the installed app, then quit it, and check the server dies.

    The server is a child process holding a TCP port. If it survives the app,
    the next launch either fails to bind or silently accumulates servers, and
    nothing in a build log says so. Quitting is the only moment the bug is
    visible, which is why it is checked here rather than trusted.
    """
    stop_everything()
    if _server_pids():
        raise SystemExit("  a Praccy server was already running; quit it first")

    subprocess.run(["open", "-a", str(installed)], capture_output=True)

    pids: list = []
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        pids = _server_pids()
        if pids:
            break
        time.sleep(0.3)
    if not pids:
        raise SystemExit("  the app launched but never started its server")
    log(f"lifecycle: server started (pid {pids[0]})")

    subprocess.run(["osascript", "-e", 'tell application "Praccy" to quit'],
                   capture_output=True)

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if not _server_pids():
            log("lifecycle: quitting the app reaped the server")
            return
        time.sleep(0.3)

    leaked = _server_pids()
    for pid in leaked:
        subprocess.run(["kill", "-9", str(pid)], capture_output=True)
    raise SystemExit(
        f"  the server survived the app quitting: pids {leaked}\n"
        "  a leaked server holds its port, so the next launch looks broken"
    )


# --------------------------------------------------------------------------
# Install
# --------------------------------------------------------------------------

def install(bundle: Path, target: Path) -> None:
    if target.exists():
        # Removed rather than overwritten. A merge would leave a stale file
        # from a previous build -- a trimmed-away stdlib module, say -- and the
        # app would keep loading it with nothing in the manifest to explain
        # why. Rebuilding is rare enough that the cost does not matter.
        shutil.rmtree(target, ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    # --noqtn preserves symlinks; without it ditto dereferences them and the
    # installed copy is 51MB larger than the one that was just verified.
    run(["ditto", "--noqtn", str(bundle), str(target)])
    run(["touch", str(target)])
    log(f"installed: {target} ({directory_size(target) // (1024 * 1024)}MB)")


# The LaunchServices database is what Finder, the Dock and Launchpad read to
# turn a bundle into a name and an icon. It is keyed on the bundle identifier,
# and this build produces two bundles carrying the same one: the copy in dist/
# and the copy in /Applications. With both registered, either can win, and the
# symptom is not an error anywhere -- it is a Dock tile and a Finder row
# showing the wrong icon and a stale name for an app that is installed and
# perfectly fine.
LSREGISTER = ("/System/Library/Frameworks/CoreServices.framework/Frameworks"
              "/LaunchServices.framework/Support/lsregister")


def reregister(bundle: Path, target: Path) -> None:
    """Leave exactly one app claiming dev.praccy.app.

    The build output is unregistered and the installed copy re-registered, so
    the name and icon Finder shows are the ones that were just installed. The
    build output is left on disk: it is the artefact, and deleting it here
    would mean the next build could not be compared against what shipped.
    """
    if not os.path.exists(LSREGISTER):
        return
    run([LSREGISTER, "-u", str(bundle)])
    run([LSREGISTER, "-f", str(target)])
    log("registered: one app claims the identifier, the installed one")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Praccy.app")
    parser.add_argument("--no-install", action="store_true",
                        help="build into dist/ without installing")
    parser.add_argument("--arch", default=arch(),
                        help="target architecture (default: this machine)")
    parser.add_argument("--app-dir", default=str(ROOT / "dist"))
    parser.add_argument("--install-to", default="/Applications/Praccy.app")
    options = parser.parse_args()

    if sys.platform != "darwin":
        raise SystemExit("  Praccy.app is macOS only.")

    target_arch = "aarch64" if options.arch in ("arm64", "aarch64") else "x86_64"
    print(f"\n  {APP_NAME} {VERSION}  ({target_arch})\n")

    dist = Path(options.app_dir)
    bundle = dist / f"{APP_NAME}.app"
    cache = dist / "python-cache" / target_arch

    print("Python")
    fetch_python(cache, target_arch)
    trim_python(cache)
    print("Bundle")
    if bundle.exists():
        shutil.rmtree(bundle)
    resources = bundle / "Contents" / "Resources"
    (bundle / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    # symlinks=True is load-bearing, not tidiness. The interpreter ships as one
    # 17MB binary with `python` and `python3` symlinked to it; copytree's
    # default dereferences them and the bundle grows by 51MB to hold four
    # identical copies of the same file.
    shutil.copytree(cache, resources / "python", symlinks=True)
    copy_package(resources)
    write_info_plist(bundle)
    build_icon(bundle)
    compile_swift(bundle)

    total = directory_size(bundle) // (1024 * 1024)
    log(f"bundle: {total}MB")

    print("\nVerify")
    smoke_test(bundle)
    sign(bundle)

    if options.no_install:
        log(f"built: {bundle}")
        return 0

    print("\nInstall")
    installed = Path(options.install_to)
    install(bundle, installed)
    reregister(bundle, installed)

    # After installing, and against the installed copy: a leaked server is
    # invisible in a build log and only shows up as a second copy failing to
    # bind its port. Quitting is the only moment the bug is visible.
    print("\nWindow")
    try:
        verify_window(installed)
    finally:
        # Always leave nothing running. A verification that fails with the app
        # still up hands the next build a live process, and `open -a` will then
        # activate that old binary instead of the one just installed.
        stop_everything()

    print("\nLifecycle")
    try:
        verify_lifecycle(installed)
    finally:
        stop_everything()
    return 0


if __name__ == "__main__":
    sys.exit(main())
