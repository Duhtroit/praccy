#!/usr/bin/env python3
"""Validate the hints and write cbp/data/hints.json.

    python3 tools/build_hints.py

The check is deliberately strict. A question with no hint, an empty hint, a
hint for a question that no longer exists, or a hint long enough to be an
answer rather than a nudge all stop the build. Everything the app serves comes
out of this file, so it is the one place where the set is known to be complete.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.hints import HINTS  # noqa: E402

QUESTIONS = os.path.join(ROOT, "cbp", "data", "questions.json")
OUT = os.path.join(ROOT, "cbp", "data", "hints.json")

MAX_LENGTH = 420


def main() -> int:
    with open(QUESTIONS, encoding="utf-8") as handle:
        questions = json.load(handle)["questions"]
    ids = [q["id"] for q in questions]

    problems = []

    missing = [qid for qid in ids if qid not in HINTS]
    if missing:
        problems.append(f"{len(missing)} questions have no hint: {' '.join(missing)}")

    unknown = sorted(set(HINTS) - set(ids))
    if unknown:
        problems.append(f"{len(unknown)} hints name no question: {' '.join(unknown)}")

    for qid in ids:
        hints = HINTS.get(qid)
        if hints is None:
            continue
        if not isinstance(hints, list) or not hints:
            problems.append(f"{qid}: no hints")
            continue
        for index, hint in enumerate(hints):
            if not isinstance(hint, str) or not hint.strip():
                problems.append(f"{qid}: hint {index + 1} is empty")
            elif len(hint) > MAX_LENGTH:
                problems.append(
                    f"{qid}: hint {index + 1} is {len(hint)} characters, over {MAX_LENGTH}"
                )

    if problems:
        for problem in problems:
            print(f"  FAIL  {problem}")
        return 1

    payload = {qid: HINTS[qid] for qid in ids}
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, ensure_ascii=False)
        handle.write("\n")

    counts = {}
    for hints in payload.values():
        counts[len(hints)] = counts.get(len(hints), 0) + 1
    spread = ", ".join(f"{n} hint{'s' if n != 1 else ''}: {c}" for n, c in sorted(counts.items()))

    print(f"  ok    {len(payload)} questions, all with hints ({spread})")
    print(f"  ok    wrote {os.path.relpath(OUT, ROOT)}")

    reference = os.path.join(ROOT, "tools", "leetcode_hints.json")
    if os.path.exists(reference):
        with open(reference, encoding="utf-8") as handle:
            scraped = json.load(handle)
        published = [qid for qid, value in scraped.items() if value.get("hints")]
        print(
            f"  note  LeetCode publishes hints for {len(published)} of the "
            f"{len(scraped)} questions we took from it; the rest are written here"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
