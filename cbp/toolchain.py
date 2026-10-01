"""Locating the external compilers Praccy shells out to.

Praccy runs the user's code by handing it to a real toolchain, so four
compilers have to exist on the machine: `clang++`, `rustc`, `javac` and
`dotnet`. Python does not, because the app bundles its own interpreter.

The awkward part is that a `.app` bundle inherits almost nothing. Launched
from Finder, `PATH` is `/usr/bin:/bin:/usr/sbin:/sbin`, which does not
include Homebrew, rustup or the .NET installer. A terminal user never notices
this; a packaged app breaks immediately. So nothing here trusts `PATH` alone.
Every binary is probed at the paths its installer actually uses, and `PATH` is
consulted last.

This module is the single source of truth for two callers: the adapters, which
need an absolute path, and `/api/deps`, which reports what is missing so the
app can show install instructions on first open.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

# Where each installer puts things, in the order they are worth trying. The
# list is deliberately literal rather than clever: these are four vendors with
# four conventions, and the conventions do not change between releases the way
# a heuristic would.
# Per-platform, because the same compiler lives somewhere completely different
# on each of the three systems the app now runs on. macOS keeps its Apple
# entries verbatim above; the Windows and Linux maps below are the reason the
# app works off its own machine at all.
#
# Everything here is an absolute path an installer actually writes. Nothing is
# a registry lookup and nothing is a shell command, because a Finder-launched
# bundle, a Start-Menu launch and a systemd unit all arrive with a PATH that
# contains almost none of this.
_WINDOWS_SEARCH_PATHS: Dict[str, List[str]] = {
    # MSVC is the default toolchain on Windows and clang-cl is the way to talk
    # to the same standard library from a C++17 source, so clang-cl comes
    # first. Both are found under VS's own directory, whose path embeds an
    # edition and build number -- hence the glob.
    "clang-cl": [
        "C:/Program Files/L*/Microsoft Visual Studio/2022/*/VC/Tools/Llvm/x64/bin/clang-cl.exe",
        "C:/Program Files/L*/Microsoft Visual Studio/2022/*/VC/Tools/Llvm/bin/clang-cl.exe",
        "C:/Program Files/L*/Microsoft Visual Studio/2022/BuildTools/VC/Tools/Llvm/x64/bin/clang-cl.exe",
    ],
    "cl": [
        "C:/Program Files/L*/Microsoft Visual Studio/2022/*/VC/Tools/MSVC/*/bin/Hostx64/x64/cl.exe",
        "C:/Program Files/L*/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/*/bin/Hostx64/x64/cl.exe",
    ],
    "rustc": [
        "~/.cargo/bin/rustc.exe",
        "~/.rustup/toolchains/stable-*/bin/rustc.exe",
    ],
    "javac": [
        "C:/Program Files/Eclipse Adoptium/jdk-21*/bin/javac.exe",
        "C:/Program Files/Java/jdk-21*/bin/javac.exe",
        "C:/Program Files/L*/Microsoft/*/jdk-21*/bin/javac.exe",
    ],
    "java": [
        "C:/Program Files/Eclipse Adoptium/jdk-21*/bin/java.exe",
        "C:/Program Files/Java/jdk-21*/bin/java.exe",
    ],
    "dotnet": [
        "C:/Program Files/dotnet/dotnet.exe",
        "~/.dotnet/dotnet.exe",
    ],
}

_LINUX_SEARCH_PATHS: Dict[str, List[str]] = {
    # Distribution packages all put clang in the same place, and the version
    # suffix is the only thing that varies, so the glob covers every supported
    # release without listing them.
    "clang++": [
        "/usr/bin/clang++-*",
        "/usr/lib/llvm-*/bin/clang++",
        "/usr/bin/g++",
        "/usr/bin/c++",
    ],
    "rustc": [
        "~/.cargo/bin/rustc",
        "~/.rustup/toolchains/stable-*/bin/rustc",
    ],
    "javac": [
        "/usr/lib/jvm/java-21-openjdk-*/bin/javac",
        "/usr/lib/jvm/default-java/bin/javac",
        "/usr/lib/jvm/*/bin/javac",
    ],
    "java": [
        "/usr/lib/jvm/java-21-openjdk-*/bin/java",
        "/usr/lib/jvm/default-java/bin/java",
        "/usr/lib/jvm/*/bin/java",
    ],
    "dotnet": [
        "/usr/bin/dotnet",
        "/usr/lib/dotnet/dotnet",
        "~/.dotnet/dotnet",
        "/opt/dotnet/dotnet",
        "/usr/share/dotnet/dotnet",
    ],
}

_SEARCH_PATHS: Dict[str, List[str]] = {
    "clang++": [
        # /usr/bin/clang++ first, and deliberately so. It is a shim that asks
        # xcrun where the macOS SDK lives, so it finds <iostream> even when
        # SDKROOT is unset. The raw Command Line Tools binary below is a real
        # compiler but does no such lookup, so with no SDKROOT in the
        # environment it fails with "iostream file not found" -- which is
        # exactly the state a Finder-launched .app is in.
        "/usr/bin/clang++",
        "/opt/homebrew/opt/llvm/bin/clang++",
        "/usr/local/opt/llvm/bin/clang++",
        # Last resort: the raw CLT binary. Only reached if the shim is gone,
        # and only usable if the caller also sets SDKROOT.
        "/Library/Developer/CommandLineTools/usr/bin/clang++",
    ],
    "rustc": [
        "~/.cargo/bin/rustc",
        "~/.rustup/toolchains/stable-*/bin/rustc",
    ],
    "javac": [
        # Homebrew's openjdk symlinks the JDK into /opt/homebrew/opt, but only
        # when the formula is linked, which it often is not.
        "/opt/homebrew/opt/openjdk@21/bin/javac",
        "/opt/homebrew/opt/openjdk/bin/javac",
        "/usr/local/opt/openjdk@21/bin/javac",
        "/usr/local/opt/openjdk/bin/javac",
        # The .pkg installer unpacks a self-contained JDK here.
        "/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/javac",
        "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/javac",
    ],
    "java": [
        "/opt/homebrew/opt/openjdk@21/bin/java",
        "/opt/homebrew/opt/openjdk/bin/java",
        "/usr/local/opt/openjdk@21/bin/java",
        "/usr/local/opt/openjdk/bin/java",
        "/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/java",
        "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java",
    ],
    "dotnet": [
        # The official installer never symlinks into a bin directory, so this
        # is the only place it is found outside a shell's PATH.
        "/usr/local/share/dotnet/dotnet",
        "~/.dotnet/dotnet",
        "/opt/homebrew/bin/dotnet",
        "/usr/local/bin/dotnet",
        "/opt/homebrew/opt/dotnet/libexec/dotnet",
    ],
}

if sys.platform == "win32":
    _SEARCH_PATHS = _WINDOWS_SEARCH_PATHS
elif sys.platform.startswith("linux"):
    _SEARCH_PATHS = _LINUX_SEARCH_PATHS

# The C++ compiler is not called clang++ everywhere. Windows ships clang-cl
# under that name and drives MSVC's standard library, and on Linux the
# distribution package is g++ as often as clang, so the probe asks for a list
# and takes the first one that runs.
_CPP_BINARY: Dict[str, List[str]] = {
    "darwin": ["clang++"],
    "win32": ["clang-cl", "clang++", "cl"],
}
_CPP_BINARY["linux"] = ["clang++", "g++", "c++"]

# Languages that need a toolchain Praccy does not ship. Python is absent on
# purpose: the app runs it on its own bundled interpreter.
EXTERNAL_LANGUAGES = ("cpp", "rust", "java", "csharp")

_BREW_FORMULA = {
    "cpp": ("llvm", "Homebrew's LLVM"),
    "rust": ("rustup", "Rust"),
    "java": ("openjdk@21", "a JDK"),
    "csharp": ("dotnet-cask", ".NET"),
}


def _candidates(binary: str) -> List[str]:
    import glob

    out: List[str] = []
    for raw in _SEARCH_PATHS.get(binary, []):
        expanded = os.path.expanduser(raw)
        if "*" in expanded:
            out.extend(sorted(glob.glob(expanded)))
        else:
            out.append(expanded)
    return out


def find(binary: str) -> Optional[str]:
    """Absolute path to `binary`, or None if this machine does not have it.

    Probed install locations first, then PATH. The order matters: a Homebrew
    LLVM should win over whatever `/usr/bin/clang++` the Command Line Tools
    happen to provide, because they are usually different major versions.
    """
    for path in _candidates(binary):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return shutil.which(binary)


def _probe(binary: str) -> Optional[str]:
    """Like `find`, but confirms the binary actually runs.

    A dangling symlink or a stub left by a half-removed formula is
    executable and useless. Running `--version` costs milliseconds and turns a
    confusing failure at submission time into an accurate report up front.
    """
    path = find(binary)
    if path is None:
        return None
    try:
        proc = subprocess.run(
            [path, "--version"],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    first = (proc.stdout or proc.stderr).strip().splitlines()
    return first[0].strip() if first else path


def candidates_for(language: str, requested: Optional[str] = None) -> List[str]:
    """Every compiler name worth trying for `language`, best first.

    Only C++ genuinely has more than one name: it is `clang++` on macOS and
    most Linux distributions, `clang-cl` on Windows, and `g++` wherever a
    distribution shipped GCC instead of LLVM. Every other language has exactly
    one driver, so this returns just what was asked for -- listing `javac`
    alongside `java` would let a run of the compiled program silently pick the
    compiler instead.
    """
    if language == "cpp":
        return list(_CPP_BINARY.get(_platform_key(), ["clang++"]))
    return [requested or language]


def _platform_key() -> str:
    """`darwin`, `win32` or `linux`, which is what the search maps are keyed on."""
    if sys.platform == "win32":
        return "win32"
    if sys.platform.startswith("linux"):
        return "linux"
    return "darwin"


def _probe_first(binaries: List[str]) -> Optional[str]:
    """The first binary in `binaries` that is present and actually runs."""
    for binary in binaries:
        version = _probe(binary)
        if version is not None:
            return version
    return None


def _lldb_required() -> bool:
    """True on a stock macOS install with no Command Line Tools.

    `clang++` is nominally present on every Mac, but on a machine that never
    installed the CLT it is a shim that opens a dialog and exits non-zero. The
    probe above catches that; this adds the actionable explanation.
    """
    if sys.platform != "darwin":
        return False
    try:
        proc = subprocess.run(
            ["xcode-select", "-p"], capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return True
    return proc.returncode != 0


_WINDOWS_HINTS = {
    "cpp": (
        "Install Visual Studio 2022 (or the Build Tools) and tick "
        "\"Desktop development with C++\".\n"
        "That provides clang-cl, which is what Praccy compiles C++ with on "
        "Windows."
    ),
    "rust": (
        "winget install Rustlang.Rustup\n"
        "Then restart Praccy, because rustup installs into %USERPROFILE%\\.cargo "
        "bin, which is not on a launched app's PATH."
    ),
    "java": (
        "winget install EclipseAdoptium.Temurin.21.JDK\n"
        "The MSI installer registers java.exe and javac.exe on PATH."
    ),
    "csharp": (
        "winget install Microsoft.DotNet.SDK.8\n"
        "dotnet.exe is installed to C:\\Program Files\\dotnet."
    ),
}

_LINUX_HINTS = {
    "cpp": (
        "sudo apt install clang        # or: sudo dnf install clang\n"
        "On Debian and Ubuntu this is the LLVM toolchain; on Fedora and Arch "
        "the package is also called clang."
    ),
    "rust": (
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh\n"
        "Then restart Praccy: rustup installs into ~/.cargo/bin, which is not "
        "on a launched app's PATH."
    ),
    "java": (
        "sudo apt install openjdk-21-jdk      # Debian, Ubuntu\n"
        "sudo dnf install java-21-openjdk-devel # Fedora\n"
        "sudo pacman -S jdk21-openjdk           # Arch"
    ),
    "csharp": (
        "sudo apt install dotnet-sdk-8.0\n"
        "Or Microsoft's installer, which puts dotnet in /usr/share/dotnet:\n"
        "https://dot.net"
    ),
}


def install_hint(language: str) -> str:
    """One copy-pasteable instruction, written for the platform it is shown on.

    Per platform because `brew install` is not an answer on Windows or on a
    Debian machine, and a first-run panel that tells a Linux user to install
    Homebrew is worse than no panel at all.
    """
    if sys.platform == "win32":
        return _WINDOWS_HINTS[language]
    if sys.platform.startswith("linux"):
        return _LINUX_HINTS[language]
    formula, label = _BREW_FORMULA[language]
    lines = [f"brew install {formula}"]
    if language == "cpp":
        if _lldb_required():
            lines.insert(0, "xcode-select --install")
        lines.append("")
        lines.append(
            "If Homebrew has no llvm formula, the Command Line Tools supply "
            "clang++ on their own: xcode-select --install"
        )
    elif language == "csharp":
        lines[0] = "brew install --cask dotnet"
        lines.append("")
        lines.append(f"Or the installer from dot.net, which puts {label} in "
                     "/usr/local/share/dotnet.")
    elif language == "rust":
        lines.append("")
        lines.append("Or rustup.rs, which puts rustc in ~/.cargo/bin.")
    elif language == "java":
        lines.append("")
        lines.append("Or any JDK 21 from Adoptium, which lands in "
                     "/Library/Java/JavaVirtualMachines.")
    return "\n".join(lines)


def report() -> Dict[str, object]:
    """Everything the first-run panel needs, in one call.

    `bundled` reports the interpreter Praccy is running on, so the panel can
    show it as satisfied even though it is not a Homebrew package.
    """
    probes = {
        "python": f"Python {sys.version.split()[0]} (bundled with Praccy)",
        # C++ is the one language whose compiler has more than one name, so it
        # is probed as a list and the first one that runs wins.
        "cpp": _probe_first(_CPP_BINARY.get(_platform_key(), ["clang++"])),
        "rust": _probe("rustc"),
        "java": _probe("javac"),
        "csharp": _probe("dotnet"),
    }
    languages: List[Dict[str, object]] = []
    for language in ("python", "cpp", "rust", "java", "csharp"):
        version = probes[language]
        languages.append({
            "language": language,
            "ok": version is not None,
            "version": version,
            "install": None if version else install_hint(language),
        })
    return {
        "languages": languages,
        "missing": [entry["language"] for entry in languages if not entry["ok"]],
        "allPresent": all(entry["ok"] for entry in languages),
    }
