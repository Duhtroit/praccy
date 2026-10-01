#!/usr/bin/env python3
"""Assemble cbp/data/track.json from the course sources.

Three inputs, kept apart on purpose:

  course_primer.py    one compressed primer module and the recognition module
  course_patterns.py  the twelve pattern modules, the bulk of the reading

The split exists because the two halves are different kinds of thing. A pattern
module answers "how do I solve this shape of question" and every principle in it
names the questions that use it. The primer answers "how do I read a question
and avoid the three bugs that survive review", and those answers are not
attached to particular questions because they are not techniques.

Order is primer first, then recognition, then the patterns. Recognition sits at
the head of the pattern half rather than at the end of the primer because it is
about choosing a technique, which is what the pattern half is for.

Run it and it rewrites track.json. It is idempotent, and it refuses to write
when a drill or a `uses` link names a question that is not in the catalogue, or
when a principle has no self-check, or when a module has no part. A course with
a dead link looks fine and teaches nothing.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from course_patterns import PATTERNS          # noqa: E402
from course_primer import PRIMER, RECOGNITION  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(ROOT, "cbp", "data", "questions.json")
TRACK_PATH = os.path.join(ROOT, "cbp", "data", "track.json")

PART_ORDER = ["essentials", "patterns"]

# The phrase each principle emboldens, keyed by its heading.
#
# Emphasis is a claim about which phrase a sentence is about, and that is an
# editorial decision rather than something a rule can infer, so it is written
# out. It lives here rather than as `**` inside the prose for one practical
# reason and one editorial one. Practically, the bodies are Python string
# literals split across source lines, so a tag often straddles two of them and
# the prose stops reading as prose. Editorially, a table is one place to read
# what the course chooses to highlight, which is the sort of choice that should
# survive a review rather than being spread across eleven hundred lines.
#
# It is checked rather than trusted. A phrase that appears nowhere in the
# principle it is filed under, or more than once in it, fails the build: an
# emphasis that silently matches nothing looks exactly like emphasis nobody
# asked for, and that is a bug you cannot see on screen.
EMPHASIS = {
    # Reading the question.
    "The return type is part of the question": "the exact value and its type",
    "The examples are the specification": "the prompt's vagueness gets resolved",
    "Rewrite the paragraph as a numbered list": "the rules are the part you need",
    "Name the shape, then trace one by hand": "the shape decides your first move",
    "One pass with a named accumulator": "what you need to remember as you go",
    "The three bugs that survive review": "one of three things",

    # Choosing a technique.
    "Read the answer, not the input": "the answer that tells you the technique",
    "Three questions, in order": "stop at the first yes",
    "Write the slow version, then find the waste": "obviously correct and obviously too slow",
    "When two patterns fit, take the simpler one": "the more impressive one",

    # The patterns.
    "Binary search is an interval, not a loop": "what your two variables mean",
    "Off by one, by construction": "who owns the boundary case",
    "Monotonicity, not sorting": "a claim that survives every halving",
    "Decide which way each finger points": "one technique with three arrangements",
    "The nested loop you are removing": "usually asking a membership question",
    "Order is information you have to keep": "A map throws away position",
    "Shrink the window until it is valid again": "forbidden from going backwards",
    "A fixed-size window is the easy case": "both ends advance together",
    "Palindromes, from the middle out": "a window that grows",
    "The key is the whole design": "what the key should be",
    "Counting beats comparing": "counting into a map is usually shorter",
    "In a group, the element is special": "appears more than half the time",
    "A stack is the right answer when things nest": "opening and closing has to match",
    "A stack evaluates postfix for free": "the postfix ordering already encodes the grouping",
    "A stack that refuses to go down": "a monotonic stack",
    "Draw the pointers before you move them": "which node holds which pointer",
    "The slow and fast pointers": "Two pointers at different speeds",
    "Merging needs one decision, made once per element": "the textbook two-pointer chase",
    "Most tree questions have one shape": "recurse and keep a running value",
    "A running answer beats a returned one": "does not live at any single node",
    "The BST order is a promise about the whole subtree":
        "a bound travels down with the recursion",
    "Mark on the way in, not on the way out": "placed at the right moment",
    "Breadth-first is the one that counts distance": "by the shortest path",
    "A cycle and a prerequisite problem are the same question":
        "the graph has a cycle in it",
    "A recursion that is allowed to fail": "explores a space of candidates",
    "Decide what makes two answers the same": "differ only in what they forbid",
    "A search on a grid is recursion with a budget": "a graph search with a rule",
    "Name the state before writing the code": "the sentence you have to finish",
    "Top-down or bottom-up, and why you would pick": "memoising what it has computed",
    "An unreachable state is a real answer": "states that cannot happen",
    "Greedy is a proof, not a preference": "cannot cost you anything later",
    "A heap is a promise about which element comes next": "the collection you will have",
    "Counting beats ordering when the keys are small": "count into a small array",
}

# How the renderer fences a specimen. It has to agree with `proseMarkup` in
# cbp/web/app.js, which is what actually reads these bodies.
EMPHASIS_OPEN = "**"
EMPHASIS_CLOSE = "**"


def apply_emphasis(modules: list) -> list:
    """Bold each tabulated phrase in the body it belongs to.

    Returns the problems rather than raising, so one bad entry is reported
    alongside the others instead of hiding them behind a traceback.
    """
    problems = []
    headings = {principle["heading"]
                for module in modules for principle in module["principles"]}

    for heading in EMPHASIS:
        if heading not in headings:
            problems.append(f"emphasis filed under {heading!r}, which is not a principle")

    for module in modules:
        for principle in module["principles"]:
            phrase = EMPHASIS.get(principle["heading"])
            if not phrase:
                continue
            body = principle["body"]
            seen = body.count(phrase)
            if seen != 1:
                problems.append(
                    f"{module['id']} / {principle['heading']!r}: emphasis "
                    f"{phrase!r} appears {seen} times, and it has to appear once")
                continue
            principle["body"] = body.replace(
                phrase, f"{EMPHASIS_OPEN}{phrase}{EMPHASIS_CLOSE}")
    return problems


def build_modules() -> list:
    """Primer, recognition, then the patterns, numbered as one sequence."""
    modules = []
    for module in PRIMER:
        modules.append(dict(module))
    for module in RECOGNITION:
        modules.append(dict(module))
    for module in PATTERNS:
        # The pattern modules carry no part of their own; the half they belong
        # to is decided here so the twelve files do not each have to say so.
        copy = dict(module)
        copy["part"] = "patterns"
        copy["partTitle"] = "Patterns"
        modules.append(copy)

    for index, module in enumerate(modules, start=1):
        title = module["title"]
        _, _, rest = title.partition(". ")
        module["title"] = f"{index}. {rest}"
    return modules


def check(modules: list, questions: dict) -> list:
    problems = []
    ids = {question["id"] for question in questions}

    for module in modules:
        module_id = module["id"]
        if module.get("part") not in PART_ORDER:
            problems.append(f"{module_id}: part {module.get('part')!r} is not one of {PART_ORDER}")
        if not module.get("minutes"):
            problems.append(f"{module_id}: no reading time")
        if not module.get("principles"):
            problems.append(f"{module_id}: no principles")
        if not module.get("drills"):
            problems.append(f"{module_id}: no drills, so it can never be marked done")

        for question_id in module.get("drills", []):
            if question_id not in ids:
                problems.append(f"{module_id}: drills on {question_id!r}, not a question")
        for principle in module.get("principles", []):
            heading = principle.get("heading", "<no heading>")
            for field in ("heading", "body"):
                if not principle.get(field):
                    problems.append(f"{module_id} / {heading!r}: no {field}")
            if not principle.get("check"):
                problems.append(f"{module_id} / {heading!r}: no self-check")
            if not principle.get("uses"):
                problems.append(
                    f"{module_id} / {heading!r}: no `uses`, so it is not attached "
                    "to any question")
            for question_id in principle.get("uses", []):
                if question_id not in ids:
                    problems.append(
                        f"{module_id} / {heading!r}: links to {question_id!r}, "
                        "not a question")
    return problems


def main() -> int:
    with open(QUESTIONS_PATH) as fh:
        questions = json.load(fh)["questions"]

    modules = build_modules()
    # Emphasis runs before validation so the checks below see the text that
    # will actually ship, bold markers and all.
    problems = apply_emphasis(modules)
    problems += check(modules, questions)
    if problems:
        print("course does not check out, nothing written:", file=sys.stderr)
        for problem in problems:
            print("  " + problem, file=sys.stderr)
        return 1

    track = {
        "track": {
            # The title states the course's job rather than repeating the
            # product name, which is already in the header above it. The
            # subtitle counts what is actually here: the pattern half is
            # twelve modules, not the eleven an earlier draft of the course
            # had, and a course that miscounts itself is a course you stop
            # trusting.
            "title": "How to read a question and pick a technique",
            "subtitle": (
                "One module on reading a prompt and on the bugs that survive "
                "review, then twelve on the patterns the harder questions are "
                "built from. Every principle names the questions it applies "
                "to, so you can read it and go straight to the practice."
            ),
            "parts": [
                {"id": "essentials", "title": "Essentials",
                 "blurb": "Read the prompt, say what type the answer is, and "
                          "catch the three mistakes that pass your own tests."},
                {"id": "patterns", "title": "Patterns",
                 "blurb": "Twelve techniques, each with the questions in the "
                          "catalogue that use it."},
            ],
            "modules": modules,
        }
    }

    with open(TRACK_PATH, "w") as fh:
        json.dump(track, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    # Two markers per emphasised phrase, so the count of markers halves it.
    emphasise = sum(p["body"].count(EMPHASIS_OPEN) // 2
                    for m in modules for p in m["principles"])
    for part in PART_ORDER:
        in_part = [m for m in modules if m["part"] == part]
        principles = sum(len(m["principles"]) for m in in_part)
        minutes = sum(m["minutes"] for m in in_part)
        links = sum(len(p.get("uses", [])) for m in in_part for p in m["principles"])
        print(f"{part:11s} {len(in_part):2d} modules  {principles:2d} principles  "
              f"{minutes:3d} min  {links:3d} links")
    print(f"{'total':11s} {len(modules):2d} modules  "
          f"{sum(len(m['principles']) for m in modules):2d} principles  "
          f"{sum(m['minutes'] for m in modules):3d} min  "
          f"{emphasise} emphasised")
    missing = [h for h in (p["heading"] for m in modules for p in m["principles"])
               if h not in EMPHASIS]
    if missing:
        # Not a failure: a principle may simply have nothing worth picking out.
        # Printed so the number above is never a mystery.
        print(f"  {len(missing)} principle(s) carry no emphasis")
        for heading in missing:
            print(f"    {heading}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
