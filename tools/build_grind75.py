#!/usr/bin/env python3
"""The Grind 75 list, added in waves, in the order the list puts them.

Grind 75 is Yangshun Tay's successor to Blind 75, built to rebalance the
original: the early problems are small and warm-up shaped, and the difficulty
ramps as the list goes on. The order is the point, so each question carries
`grind75`, its 1-based position on the canonical list, and the catalogue sorts
by that rather than by title.

The questions live in one module per wave, with the shared vocabulary in
`grind75_common.py`. This file is only the driver: it merges every wave into
the catalogue and writes the result. Adding the next ten questions should mean
adding a `grind75_wave3.py` and one import line, and nothing else.

Three things about the list do not survive contact with a harness that runs
`one function, a few arguments, a value back`:

  * Eight design problems build a class and keep state between calls instead
    of returning a value -- Implement Queue using Stacks at 13, Implement Trie
    at 35, Min Stack at 38, Time Based Key-Value Store at 47, Clone Graph at
    32, LRU Cache at 65, Serialize and Deserialize Binary Tree at 68, and Find
    Median from Data Stream at 70. They are skipped rather than rewritten,
    because the honest version of each needs a harness that can call a
    constructor and then poke at the object, and this one runs a function once
    per case and throws it away.
  * Linked List Cycle at 12 asks whether a list points back at itself. An array
    has no pointers, so there is nothing for Floyd's algorithm to chase. Also
    skipped; a rephrasing would not be the same problem.
  * Accounts Merge returns a list of lists of strings, which no contract type
    covered yet. Wave 4 added `strmatrix` for it.

That is nine of the seventy-five, so the catalogue holds sixty-six. Two of the
rest were already here from the original LeetCode set under their own ids --
Container With Most Water and Trapping Rain Water -- and the ADOPT table below
stamps their positions onto those rather than adding a second copy.

Everything else carries over. Several need a type this project did not have
until the structural contracts landed -- a tree argument, a matrix, a graph --
so the waves are also what proves those types earn their place.

Run with the self-test afterwards:

    python3 tools/build_grind75.py && python3 -m cbp.selftest
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(ROOT, "cbp", "data", "questions.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grind75_common import LC
from grind75_wave1 import QUESTIONS as WAVE1
from grind75_wave2 import QUESTIONS as WAVE2
from grind75_wave3 import QUESTIONS as WAVE3
from grind75_wave4 import QUESTIONS as WAVE4
from grind75_wave5 import QUESTIONS as WAVE5
from grind75_wave6 import QUESTIONS as WAVE6

QUESTIONS = WAVE1 + WAVE2 + WAVE3 + WAVE4 + WAVE5 + WAVE6

# Four questions on the list were already here from the original Coderbyte
# set, under their own ids and their own (Coderbyte) prompts. Rather than
# duplicate them, the driver stamps the canonical position and the LeetCode
# reference onto the question that is already in the catalogue. This is the
# only place that mutates a question the waves do not own.
ADOPT = {
    "two-sum": (1, 1, "LeetCode 1 (Medium). Opens the list."),
    "valid-anagram": (7, 242, "LeetCode 242 (Easy). A counting table rather than sorting."),
    "contains-duplicate": (24, 217, "LeetCode 217 (Easy). A set answers it in one pass."),
    "maximum-subarray": (25, 53, "LeetCode 53 (Medium). Kadane's algorithm, and why the running minimum is not the answer."),
    "lc-container-water": (59, 11, "LeetCode 11 (Medium). Two pointers from both ends; the shorter line is the one that has to move."),
    "lc-trapping-rain-water": (69, 42, "LeetCode 42 (Hard). One pass from both ends, tracking the tallest bar seen from each side."),
}


def main() -> int:
    with open(QUESTIONS_PATH) as fh:
        existing = json.load(fh)["questions"]

    by_id = {question["id"]: question for question in existing}
    added = 0
    for question in QUESTIONS:
        if question["id"] not in by_id:
            added += 1
        by_id[question["id"]] = question

    for qid, (position, source_id, note) in ADOPT.items():
        if qid not in by_id:
            print(f"  adopt target {qid} is not in the catalogue", file=sys.stderr)
            return 1
        by_id[qid]["grind75"] = position
        by_id[qid]["source"] = LC
        by_id[qid]["sourceId"] = source_id
        by_id[qid]["sourceNote"] = note

    seen = {}
    for question in QUESTIONS + [by_id[qid] for qid in ADOPT]:
        position = question["grind75"]
        if position in seen:
            print(f"  position {position} claimed by both {seen[position]} and "
                  f"{question['id']}", file=sys.stderr)
            return 1
        seen[position] = question["id"]

    # Rust goes on last: the merge above replaces whole question objects, so
    # attaching earlier would be undone by every question defined in the waves.
    from rust_solutions import attach

    attach(list(by_id.values()))

    order = {"easy": 0, "medium": 1, "hard": 2, "stretch": 3}

    def sort_key(question):
        # Within a tier, the questions that were always here stay alphabetical
        # and the Grind 75 block follows in the order the list puts it in.
        position = question.get("grind75")
        return (order.get(question["tier"], 9),
                1 if position is not None else 0,
                position if position is not None else 0,
                question["title"].lower())

    merged = sorted(by_id.values(), key=sort_key)

    # The patterns are assigned centrally, here and in the other two builders,
    # so the catalogue is correct whichever of them ran last.
    from patterns import apply as apply_patterns

    apply_patterns(merged)

    # Tiering runs here too. It used to be a separate step that the build
    # instructions forgot, so building the catalogue reverted every Grind 75
    # question to the old "stretch" tier and 68 questions fell out of the
    # sidebar. Idempotent, which is what makes this safe to repeat.
    from retier import retier as retier_question

    for question in merged:
        retier_question(question)

    with open(QUESTIONS_PATH, "w") as fh:
        json.dump({"questions": merged}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    grind = [q for q in merged if q.get("grind75")]
    print(f"added {added} questions; catalogue now {len(merged)} "
          f"({len(grind)} of them Grind 75)")
    for question in sorted(grind, key=lambda q: q["grind75"]):
        print(f"  {question['grind75']:3d}. {question['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
