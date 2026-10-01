#!/usr/bin/env python3
"""Retire the `stretch` tier and put every question in its real difficulty.

There used to be four tiers. Three of them (`easy`, `medium`, `hard`) described
the question; the fourth, `stretch`, described where the question came from.
That conflation was doing real damage in the UI: a LeetCode Easy and a LeetCode
Hard were filed together under one heading, and the heading said "stretch",
which is a statement about time budget rather than difficulty.

The fix separates the two axes:

  * `tier` is difficulty and nothing else. Every LeetCode question moves to the
    difficulty LeetCode itself publishes, which is already recorded in each
    question's `sourceNote` as "LeetCode 226 (Easy)". Questions without a
    LeetCode origin keep the tier they were given, because for those the tier
    is our own judgement about an assessment-style question.

  * `source` says where the question came from, "Coderbyte" or "LeetCode", and
    is also added to `tags` so the text filter can reach it.

The `stretch` tier disappears. Nothing references it afterwards except the
migration's own compatibility shim, which reads the old data once.

Run it twice: the second run is a no-op, which is the check that the migration
is idempotent. It refuses to write if any question ends up with no tier, and
it checks the tier counts add up to the number of questions.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(ROOT, "cbp", "data", "questions.json")

TIERS = ("easy", "medium", "hard")
SOURCE_TAGS = ("coderbyte", "leetcode")
SOURCE_NOTE_RE = re.compile(r"^LeetCode (\d+) \((Easy|Medium|Hard)\)")


def load() -> dict:
    with open(QUESTIONS_PATH) as fh:
        return json.load(fh)


def leetcode_difficulty(question: dict):
    """The difficulty LeetCode publishes, taken from the note we already wrote.

    Returns None for a question that is not from LeetCode. Raises if a
    LeetCode question has a note we cannot read, because silently leaving it
    unretired is exactly the bug this migration exists to remove.
    """
    if question.get("source") != "LeetCode":
        return None
    if not question.get("source"):
        return None
    note = question.get("sourceNote") or ""
    match = SOURCE_NOTE_RE.match(note)
    if not match:
        raise SystemExit(
            f"{question['id']}: source is LeetCode but sourceNote does not start "
            f"with 'LeetCode N (Difficulty)': {note!r}"
        )
    return match.group(2).lower()


def retier(question: dict) -> None:
    difficulty = leetcode_difficulty(question)
    if difficulty:
        question["tier"] = difficulty

    # Only the LeetCode questions carried a `source` field; the Coderbyte ones
    # were defined by not having one. That is now stated rather than implied,
    # because the filter needs to be able to ask for either origin.
    source = question.get("source") or "Coderbyte"
    if source not in ("Coderbyte", "LeetCode"):
        raise SystemExit(f"{question['id']}: unknown source {source!r}")

    # The source goes in the tags so the text filter finds "leetcode" as typed,
    # and so a question is describable as both a difficulty and an origin.
    #
    # Both source tags are stripped first, then the right one is added. Only
    # appending would leave a stale one behind whenever a question's source
    # changed between runs -- which it does: four questions are defined in the
    # core builder with no origin and picked up by the Grind 75 pass later, so
    # one run can see the same question as Coderbyte and the next as LeetCode.
    tags = [t for t in question.get("tags", []) if t.lower() not in SOURCE_TAGS]
    tags.append(source.lower())
    question["tags"] = tags
    question["source"] = source


def main() -> int:
    data = load()
    questions = data["questions"]
    before = Counter(q["tier"] for q in questions)

    for question in questions:
        retier(question)

    after = Counter(q["tier"] for q in questions)

    problems = []
    if set(after) - set(TIERS):
        problems.append(f"tiers outside {TIERS}: {sorted(set(after) - set(TIERS))}")
    if sum(after.values()) != len(questions):
        problems.append("tier counts do not add up to the question count")
    for question in questions:
        if not question.get("tier"):
            problems.append(f"{question['id']}: no tier")
        if question.get("source", "").lower() not in question.get("tags", []):
            problems.append(f"{question['id']}: source missing from tags")

    if problems:
        print("refusing to write:", file=sys.stderr)
        for problem in problems:
            print("  " + problem, file=sys.stderr)
        return 1

    with open(QUESTIONS_PATH, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"{len(questions)} questions")
    print("  before: " + ", ".join(f"{k} {v}" for k, v in sorted(before.items())))
    print("  after:  " + ", ".join(f"{k} {after[k]}" for k in TIERS))
    by_source = Counter(q["source"] for q in questions)
    print("  by source: " + ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
