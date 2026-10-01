#!/usr/bin/env python3
"""Package Praccy for the machine this runs on.

`tools/build_app.py` builds a macOS `.app` around the Swift shell. This builds
the other thing: a self-contained application around `praccy.py`, for Windows or
Linux, using PyInstaller. Same UI, same engine, same bundled fonts; only the
window comes from pywebview instead of WKWebView.

    python3 tools/build_portable.py               # build for this machine
    python3 tools/build_portable.py --onefile    # a single file to hand over

Run it on the target OS. PyInstaller is not a cross-compiler: it reads the
interpreter it is installed into and links against that platform's extension
modules, so a Windows binary has to be built on Windows. The GitHub Actions
workflow in `.github/workflows/build.yml` does that on both platforms, and
`--onefile` on Linux additionally produces an AppImage, which is the format a
friend can actually double-click.

The pieces that are easy to get wrong, and what this does about them:

  * **The fonts have to be collected.** PyInstaller walks imports, and a woff2
    referenced from a stylesheet is not an import. Without them the app starts,
    renders, and quietly falls back to a system face -- which looks fine and is
    the exact bug the fonts were bundled to fix. They are added as data, and
    the build then checks they are actually inside the output.

  * **The web root is found next to the executable, not in the CWD.** A frozen
    app is launched from wherever the user double-clicked it, so a relative
    `cbp/web` resolves to the desktop. `praccy.py` handles that itself (see
    `_resource_root`); the check here confirms it after the build.

  * **`pywebview` backends are imported lazily**, by platform, so only the one
    that can work is pulled in. The Windows build needs the WebView2 runtime,
    which is present on every Windows 10 and 11 machine but is worth stating.

  * **One file versus one directory.** `--onefile` produces a single
    executable, which is what you want to send to someone. It starts slower,
    because it unpacks itself to a temp directory on every launch, and the
    server is in-process, so that cost is paid once per start. The default is a
    directory, which is faster and is what to install.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_NAME = "Praccy"
VERSION = "1.0"
# Matches the bundle identifier the macOS build registers, so the two installs
# are the same app to LaunchServices, to Spotlight and to a licence file.
APP_ID = "dev.praccy.app"


def log(message: str) -> None:
    print(f"  {message}", flush=True)


def target_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64",
            "aarch64": "arm64"}.get(machine, machine)
    if system == "darwin":
        return f"macos-{arch}"
    if system == "windows":
        return f"windows-{arch}"
    return f"linux-{arch}"


def require_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("\n  PyInstaller is not installed. In a virtualenv:\n"
              "      python3 -m venv .venv && . .venv/bin/activate\n"
              "      pip install pywebview pyinstaller\n")
        raise SystemExit(1)
    return PyInstaller.__version__


def build_icon() -> str:
    """Draw the platform's icon format with the stdlib renderer.

    `app/Icon.swift` is the original, and it is AppKit-only. `make_icon.py`
    draws the same mark anywhere, which is the only reason a Windows .ico and a
    Linux hicolor tree can exist at all.
    """
    out = ROOT / "dist" / "icon"
    out.mkdir(parents=True, exist_ok=True)
    generator = [sys.executable, str(ROOT / "tools" / "make_icon.py")]

    if sys.platform == "win32":
        # Windows reads .ico for both the executable and the taskbar.
        path = out / f"{APP_NAME}.ico"
        subprocess.run(generator + ["--ico", str(path)], check=True)
        return str(path)

    if sys.platform == "darwin":
        # PyInstaller refuses a PNG here and wants .icns. The macOS .app built
        # by build_app.py uses AppKit's own renderer, so this is only for a
        # PyInstaller bundle on macOS -- but it has to be right or the build
        # fails at the BUNDLE step with an error about image formats.
        path = out / f"{APP_NAME}.icns"
        subprocess.run(generator + ["--icns", str(path)], check=True)
        return str(path)

    # Linux takes a PNG for the PyInstaller window icon, and the hicolor tree is
    # installed alongside the binary.
    png = out / f"{APP_NAME}.png"
    subprocess.run(generator + ["--png", str(png), "--size", "512",
                                "--hicolor", str(out / "share")], check=True)
    return str(png)


def _payload_root(bundle: Path) -> Path:
    """Where PyInstaller put the data, which is not the same place on each OS.

    A one-file build unpacks to a temp directory and has no data directory at
    all until it runs. An onedir build puts it in `_internal` (PyInstaller 6)
    or beside the executable (PyInstaller 5), and a macOS .app adds a layer of
    Contents. Rather than encode three layouts, the directory that actually
    contains `cbp/web` is found -- and a build with none is a build that failed,
    which is the useful thing to say.
    """
    candidates = [bundle, bundle / "_internal", bundle / "Contents" / "Resources",
                  bundle / "Contents" / "Resources" / "_internal",
                  bundle.parent]
    for candidate in candidates:
        if (candidate / "cbp" / "web" / "index.html").exists():
            return candidate
    return bundle


def verify_output(bundle: Path) -> None:
    """Prove the build is complete before it is called a build.

    Every check here corresponds to a way the artifact can be subtly wrong
    rather than absent: a missing font file renders fine and looks wrong, a web
    root that is not next to the executable starts and then 404s on the
    stylesheet, and a shell that imports pywebview eagerly fails to start on a
    machine with no webview at all.
    """
    problems = []
    root = _payload_root(bundle)

    fonts = sorted((root / "cbp" / "web" / "fonts").glob("*.woff2"))
    if len(fonts) < 2:
        problems.append(f"expected 2 bundled woff2, found {len(fonts)}")
    else:
        log(f"fonts  {[f.name for f in fonts]}")

    for required in ("cbp/web/index.html", "cbp/web/style.css",
                     "cbp/web/app.js", "cbp/data/questions.json"):
        if not (root / required).exists():
            problems.append(f"missing {required} (looked under {root})")
    log(f"assets {len(list((root / 'cbp' / 'web').rglob('*')))} web files "
        f"under {root.name or root}")

    # The executable is named for the app on every platform, and lives either
    # at the top of the bundle or inside it on macOS.
    name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    binaries = [p for p in bundle.rglob(name)
                if p.is_file() and p.parent.name in ("", "MacOS", "bin")]
    if not binaries:
        problems.append(f"no executable named {name} under {bundle}")
    else:
        binary = max(binaries, key=lambda p: p.stat().st_size)
        size = binary.stat().st_size
        log(f"binary {binary.relative_to(bundle)} {size // 1024 // 1024}MB")
        if size < 100_000:
            problems.append("the executable is implausibly small")

    if problems:
        print("\n  BUILD INCOMPLETE")
        for problem in problems:
            print(f"    - {problem}")
        raise SystemExit(1)
    log("verified: assets, fonts and executable all present")


def build(onefile: bool, workdir: Path) -> Path:
    pyinstaller = require_pyinstaller()
    log(f"pyinstaller {pyinstaller} on {target_name()}")

    icon = build_icon()
    log(f"icon    {icon}")

    outdir = ROOT / "dist" / target_name()
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--name", APP_NAME,
        "--distpath", str(outdir),
        "--workpath", str(workdir),
        "--specpath", str(workdir),
        # The two typefaces. Listed as data because nothing imports them.
        "--add-data", f"{ROOT / 'cbp' / 'web' / 'fonts'}{os.pathsep}cbp/web/fonts",
        "--add-data", f"{ROOT / 'cbp' / 'data'}{os.pathsep}cbp/data",
        "--add-data", f"{ROOT / 'cbp' / 'web'}{os.pathsep}cbp/web",
        "--hidden-import", "webview",
        # The backend for this platform only. pywebview picks at runtime, but a
        # frozen build cannot import something it never collected.
        "--hidden-import", _backend(),
        "--collect-submodules", "cbp",
        "--windowed",           # no console window on Windows or Linux
        "--osx-bundle-identifier", APP_ID,
    ]
    if onefile:
        command.append("--onefile")
    else:
        command.append("--onedir")
    if sys.platform != "win32":
        command += ["--icon", icon]
    command.append(str(ROOT / "praccy.py"))

    log("running: " + " ".join(command[:6]) + " ...")
    proc = subprocess.run(command)
    if proc.returncode != 0:
        raise SystemExit(f"PyInstaller failed with {proc.returncode}")

    # PyInstaller's output shape follows --onefile/--onedir and the platform, so
    # the artifact is found by looking rather than by assuming a filename.
    if onefile:
        artifact = outdir / (f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME)
        verify_onefile(outdir, artifact)
    else:
        bundle = outdir / (f"{APP_NAME}.app" if sys.platform == "darwin" else APP_NAME)
        verify_output(bundle)
        artifact = bundle
    return artifact


def verify_onefile(outdir: Path, artifact: Path) -> None:
    """Check a one-file build by running it, because nothing else is possible.

    A one-file build has no data directory to inspect: PyInstaller packs the
    typefaces and the web root into the executable and unpacks them to a
    temporary directory at startup, deleting it on exit. So the only honest
    check is to start it and ask. `--check` does exactly that -- it starts the
    server, fetches the page and both woff2 files, and exits -- and it needs no
    display, so it works on a build machine and in CI.

    This is also the check that would catch a missing font at the only point
    where it is visible. The failure it prevents is quiet: a one-file build with
    no bundled typeface starts, renders, and falls back to a system face, which
    looks like a working app and is the exact bug the fonts were bundled to fix.
    """
    problems = []

    # PyInstaller puts a one-file app inside a .app on macOS, so the artifact is
    # whichever of the two shapes exists.
    candidates = [artifact, outdir / f"{APP_NAME}.app" / "Contents" / "MacOS" / APP_NAME]
    binary = next((p for p in candidates if p.exists()), None)
    if binary is None:
        print(f"\n  BUILD INCOMPLETE\n    - no one-file executable under {outdir}")
        raise SystemExit(1)

    size = binary.stat().st_size
    log(f"binary {binary.name} {size // 1024 // 1024}MB")
    if size < 5_000_000:
        # A one-file build is the interpreter plus the data; anything this small
        # means the data did not go in.
        problems.append(f"the one-file executable is {size} bytes, which is "
                        "too small to contain the interpreter and the app")

    log("running it, because a one-file build cannot be inspected")
    proc = subprocess.run([str(binary), "--check"], capture_output=True, text=True,
                          timeout=300)
    for line in (proc.stdout or "").splitlines():
        if line.strip():
            log(f"  {line.strip()}")
    if proc.returncode != 0:
        problems.append(f"--check exited {proc.returncode}: "
                        f"{(proc.stderr or '').strip()[-300:]}")
    elif "font " not in (proc.stdout or ""):
        problems.append("--check did not report the bundled fonts, so the "
                        "typefaces are not in the executable")

    if problems:
        print("\n  BUILD INCOMPLETE")
        for problem in problems:
            print(f"    - {problem}")
        raise SystemExit(1)
    log("verified: the one-file build starts, serves the page and both fonts")


def _backend() -> str:
    """The pywebview backend module for this platform.

    These are the names pywebview imports internally. Naming the right one is
    what stops the frozen app from failing at startup with a bare ImportError
    that no user can act on.
    """
    return {
        "darwin": "webview.platforms.cocoa",
        "win32": "webview.platforms.edgechromium",
    }.get(sys.platform, "webview.platforms.gtk")


def appimage(artifact: Path) -> Path | None:
    """Wrap the onefile build in an AppImage, on Linux only.

    An AppImage is a single file that runs without installing anything, which
    is the difference between a friend running Praccy and a friend reading a
    README about how to install it. The tooling is downloaded rather than
    assumed, and the whole step is skipped with a note rather than failing the
    build if it cannot be fetched.
    """
    if not sys.platform.startswith("linux"):
        return None
    if "appimagetool" in os.environ.get("PATH", ""):
        tool = "appimagetool"
    else:
        cached = ROOT / "dist" / "appimagetool"
        if not cached.exists():
            log("fetching appimagetool")
            url = ("https://github.com/AppImage/AppImageKit/releases/download/"
                   "continuous/appimagetool-x86_64.AppImage")
            try:
                subprocess.run(["curl", "-fsSL", url, "-o", str(cached)],
                               check=True)
                cached.chmod(0o755)
            except (subprocess.CalledProcessError, OSError) as exc:
                log(f"skipped: could not fetch appimagetool ({exc})")
                return None
        tool = str(cached)

    staging = ROOT / "dist" / "AppDir"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "usr" / "bin").mkdir(parents=True)
    target = staging / "usr" / "bin" / APP_NAME
    shutil.copy2(artifact, target)
    target.chmod(0o755)

    icon_src = ROOT / "dist" / "icon"
    if icon_src.exists():
        shutil.copytree(icon_src / "share", staging / "usr" / "share",
                        dirs_exist_ok=True)
    (staging / f"{APP_NAME}.png").write_bytes(
        (icon_src / f"{APP_NAME}.png").read_bytes())

    (staging / "AppRun").write_text(
        "#!/bin/sh\n"
        "# AppRun: the AppImage entry point. Everything is relative to the\n"
        "# mount point AppImageKit gives us, which is $APPDIR.\n"
        'HERE="$(dirname "$(readlink -f "$0")")"\n'
        f'exec "$HERE/usr/bin/{APP_NAME}" "$@"\n'
    )
    (staging / "AppRun").chmod(0o755)
    (staging / f"{APP_NAME}.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={APP_NAME}\n"
        "Comment=Timed interview reps\n"
        f"Exec={APP_NAME}\n"
        f"Icon={APP_NAME}\n"
        "Categories=Development;\n"
        "Terminal=false\n"
    )

    out = ROOT / "dist" / f"{APP_NAME}-{VERSION}-x86_64.AppImage"
    proc = subprocess.run([tool, "--no-appstream", str(staging), str(out)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        log(f"appimagetool failed: {proc.stderr[-400:]}")
        return None
    out.chmod(0o755)
    log(f"appimage {out.name} {out.stat().st_size // 1024 // 1024}MB")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=f"package {APP_NAME}")
    parser.add_argument("--onefile", action="store_true",
                        help="a single executable, and an AppImage on Linux")
    parser.add_argument("--workdir", default=str(ROOT / "dist" / "work"),
                        help="PyInstaller's scratch directory")
    args = parser.parse_args()

    print(f"\n  Packaging {APP_NAME} {VERSION} for {target_name()}")
    print("  " + "-" * 52)
    artifact = build(args.onefile, Path(args.workdir))
    image = appimage(artifact) if args.onefile else None
    print("  " + "-" * 52)
    log(f"artifact {artifact}")
    if image:
        log(f"appimage {image}")

    # A machine-readable list of what was produced, so the CI workflow and any
    # script can find the binary without re-deriving a path that depends on the
    # OS, the arch, and whether --onefile was passed. Those three together are
    # exactly the sort of thing that is right in a script and stale in a
    # hand-written path.
    manifest = ROOT / "dist" / "artifacts.json"
    entries = [{
        "kind": "appimage" if image else ("onefile" if args.onefile else "onedir"),
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
    } for path in ([artifact] + ([image] if image else []))]
    manifest.write_text(json.dumps({
        "app": APP_NAME,
        "version": VERSION,
        "target": target_name(),
        "python": sys.version.split()[0],
        "artifacts": entries,
    }, indent=2) + "\n", encoding="utf-8")
    log(f"manifest {manifest.relative_to(ROOT)}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
