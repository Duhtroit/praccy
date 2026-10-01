"""Prove the app's worst-case environment: no PATH, no toolchain in sight.

A Finder-launched .app inherits `PATH=/usr/bin:/bin:/usr/sbin:/sbin`. That is
the only environment this project has to survive, and nothing in the test suite
exercises it, because a developer runs everything from a shell where Homebrew,
rustup and .NET are all already on PATH.

So this check re-runs one reference solution per language with PATH replaced by
that bare value, using the interpreter Praccy bundles. If any adapter ever
shells out to a bare tool name again, this fails while the cause is still
obvious.

    python3 tools/test_bare_path.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

BARE_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The reference solutions are already in the dataset, so this reuses the
# project's own ground truth instead of a second copy that could drift.
PROBE = '''
import json, sys
from cbp import api
from cbp.toolchain import find

languages = ("python", "cpp", "rust", "csharp", "java")
questions = {q["id"]: q for q in json.load(open("cbp/data/questions.json"))["questions"]}

rows = []
for language in languages:
    path = find("python3" if language == "python" else {
        "cpp": "clang++", "rust": "rustc",
        "csharp": "dotnet", "java": "javac",
    }[language])
    if path is None:
        rows.append({"language": language, "resolved": False,
                     "ok": False, "detail": "binary not found"})
        continue
    question = questions["two-sum"]
    result = api.evaluate_payload(question, language, question["solution"][language])
    error = result.get("error") or {}
    rows.append({
        "language": language,
        "resolved": True,
        "path": path,
        "ok": bool(result.get("ok")),
        "detail": error.get("message", "")[:160],
    })
print("__RESULT__" + json.dumps(rows))
'''


def main() -> int:
    env = dict(os.environ, PATH=BARE_PATH)
    # Belt and braces: an inherited SDKROOT would hide the clang failure this
    # test exists to catch, so it is cleared rather than left alone.
    env.pop("SDKROOT", None)

    proc = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=900,
    )
    marker = "__RESULT__"
    if marker not in proc.stdout:
        print("  FAIL  the probe did not report")
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        return 1

    rows = json.loads(proc.stdout.split(marker, 1)[1].splitlines()[0])
    failures = 0
    print(f"  (PATH={BARE_PATH})\n")
    for row in rows:
        if row["ok"]:
            print(f"  ok    {row['language'].ljust(7)} {row.get('path', '')}")
        else:
            failures += 1
            print(f"  FAIL  {row['language'].ljust(7)} {row['detail']}")

    print()
    if failures:
        print(f"{failures}/{len(rows)} languages need a PATH Praccy will not have")
        return 1
    print(f"{len(rows)}/{len(rows)} languages work with no PATH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
