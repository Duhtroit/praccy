"""Tests for toolchain resolution and the dependency report.

Two things are worth proving here, and neither is visible from the outside:

  1. `find` prefers an installer's real location over `PATH`. A .app inherits
     a PATH with no Homebrew, no cargo and no dotnet in it, so anything that
     worked in a shell has to be found by absolute path.
  2. `report` produces the exact contract the first-run panel reads. The panel
     is Swift, so a renamed key or a changed type fails at runtime on a user's
     machine rather than in a test -- and only on the one path that shows
     itself when something is missing.

The missing-toolchain case is simulated by pointing `find` at an empty search
list, which is the only way to exercise it on a machine where all four
compilers happen to be installed.

    python3 tools/test_toolchain.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cbp import toolchain

failures = []


def expect(name, condition, detail=""):
    if condition:
        print(f"  ok    {name}")
    else:
        failures.append(name)
        print(f"  FAIL  {name}  {detail}")


# -- resolution ------------------------------------------------------------

print("Resolution")
print("=" * 64)

# Every toolchain the app needs must resolve to an absolute path, and every one
# of them must exist. `shutil.which` would also satisfy the first condition on
# a developer machine and fail the moment the app is launched from Finder.
for binary in ("clang++", "rustc", "javac", "dotnet"):
    path = toolchain.find(binary)
    expect(f"{binary} resolves", path is not None and os.path.isabs(path or ""), str(path))
    if path:
        expect(f"{binary} is executable", os.access(path, os.X_OK), path)

# The bare-PATH case, which is the one that matters. An empty PATH proves the
# answer came from an install path and not from the environment.
saved_path = os.environ.get("PATH")
try:
    os.environ["PATH"] = "/nonexistent"
    for binary in ("clang++", "rustc", "javac", "dotnet"):
        path = toolchain.find(binary)
        expect(f"{binary} found with an empty PATH", path is not None, "not found")
finally:
    if saved_path is None:
        os.environ.pop("PATH", None)
    else:
        os.environ["PATH"] = saved_path

# clang++ specifically: the /usr/bin shim resolves the SDK through xcrun, so
# it must win over the raw Command Line Tools binary, which cannot find
# <iostream> when SDKROOT is unset. Getting this backwards breaks every C++
# submission inside the app while working perfectly in a terminal.
clang = toolchain.find("clang++")
expect("clang++ is the xcrun shim, not the raw CLT binary",
       clang == "/usr/bin/clang++", str(clang))

# -- the report contract ---------------------------------------------------

print("\nDependency report")
print("=" * 64)

report = toolchain.report()
expect("report has the three keys the panel reads",
       set(report) == {"languages", "missing", "allPresent"}, str(sorted(report)))

entries = report["languages"]
expect("every language is reported", len(entries) == 5, str(len(entries)))
expect("languages are in a stable order",
       [e["language"] for e in entries]
       == ["python", "cpp", "rust", "java", "csharp"],
       str([e["language"] for e in entries]))

# The panel is Swift. A key that changes type here is a crash or a blank panel
# on a user's machine, so the shape is pinned exactly.
for entry in entries:
    language = entry["language"]
    expect(f"{language} entry has the exact keys",
           set(entry) == {"language", "ok", "version", "install"},
           str(sorted(entry)))
    expect(f"{language}.ok is a bool", isinstance(entry["ok"], bool),
           type(entry["ok"]).__name__)
    expect(f"{language}.version is a string or None",
           entry["version"] is None or isinstance(entry["version"], str))
    expect(f"{language}.install is a string exactly when missing",
           (entry["install"] is not None) == (not entry["ok"]),
           f"ok={entry['ok']}")

expect("missing agrees with the entries",
       report["missing"] == [e["language"] for e in entries if not e["ok"]],
       str(report["missing"]))
expect("allPresent agrees with the entries",
       report["allPresent"] == all(e["ok"] for e in entries))

expect("python is always present, it ships with the app",
       entries[0]["ok"] and entries[0]["version"].startswith("Python 3."))

# -- the missing case ------------------------------------------------------

print("\nWhen a toolchain is missing")
print("=" * 64)

# Simulated by emptying the search list, since this machine has all four. The
# panel's only job on a fresh machine is this path, and it never runs here.
saved_paths = toolchain._SEARCH_PATHS
try:
    toolchain._SEARCH_PATHS = {key: [] for key in saved_paths}
    original_which = toolchain.shutil.which
    toolchain.shutil.which = lambda binary: None
    try:
        broken = toolchain.report()
    finally:
        toolchain.shutil.which = original_which
finally:
    toolchain._SEARCH_PATHS = saved_paths

expect("all four external toolchains report missing",
       sorted(broken["missing"]) == ["cpp", "csharp", "java", "rust"],
       str(broken["missing"]))
expect("python is still present", "python" not in broken["missing"])
expect("allPresent is false", broken["allPresent"] is False)

# A blank panel is worse than no panel: the user needs a command to type.
for entry in broken["languages"]:
    if entry["ok"]:
        continue
    hint = entry["install"] or ""
    expect(f"{entry['language']} hint names a brew command",
           "brew install" in hint, hint[:60])
    expect(f"{entry['language']} hint is not a placeholder",
           len(hint) > 20, hint)

# C# is the one that most needs explaining, because `brew install dotnet` does
# not exist -- it is a cask, and getting this wrong sends the user to a formula
# that is not there.
csharp_hint = next(e["install"] for e in broken["languages"]
                   if e["language"] == "csharp")
expect("the dotnet hint uses a cask, not a formula",
       "brew install --cask dotnet" in csharp_hint, csharp_hint[:80])

print()
if failures:
    print(f"{len(failures)} failed")
    for name in failures:
        print(f"  - {name}")
    sys.exit(1)
print("all checks passed")
