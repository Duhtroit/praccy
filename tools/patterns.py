#!/usr/bin/env python3
"""The technique behind every question, written down once.

The catalogue used to describe each question with free-text `tags`, and the
Patterns row in the app showed them. That vocabulary rotted. It reached 33
words for 144 questions, and most of them were not patterns at all:

  "algorithm"           on 96 questions -- a synonym for "this is a question"
  "math fundamentals"   on 31 -- a school subject, not a technique
  "string manipulation" on 43 -- a data type, not a technique
  "searching"           on 32 -- binary search and scanning a string for a
                        character, described with one word
  "matrix"              on Three Sum, K Closest Points and Merge Intervals,
                        none of which see a grid

and the plurals had drifted apart from the singulars, so "tree" and "trees"
were different chips leading to the same module.

This file replaces that with a controlled vocabulary and an assignment per
question. Two rules decide whether a word belongs:

  A pattern is a technique. You can learn it, it transfers to a question that
  does not look like the one you learned it on, and knowing it changes how you
  write the function. "Dynamic programming" is a pattern. "Math fundamentals"
  is a topic that says nothing about what to do.

  Every question gets at least one. Some of them genuinely have no cleverness
  in them -- Rectangle Area is a multiplication -- and for those the honest
  answer is the smallest true technique, which is usually "arithmetic" or
  "single pass". A blank row would be worse: it reads as missing data rather
  than as a question that is simply easy.

The `tags` on each question are left alone and still drive the sidebar search,
because a search for "matrix" or "math" is a reasonable thing to do. They are
no longer what the Patterns row shows.

What each pattern teaches is `MODULES`: a pattern in that table gets a chip
that links into the course, and one that is not gets a plain chip. The link
table itself lives in cbp/track.py, which is what the server reads, and
`check_modules` below is what keeps the two in step.

Adding a question means adding a line here. `apply` refuses to write a
catalogue where a question has no patterns, where a pattern is not in the
vocabulary, or where a question in the table no longer exists, so the table
cannot quietly fall behind the questions.
"""

from __future__ import annotations

from typing import Dict, List

# The vocabulary, in the order chips should prefer. Only techniques: a word
# that does not change how you write the function does not belong here.
PATTERNS: List[str] = [
    # The course's own techniques, one per module it teaches.
    "hash map",
    "frequency counting",
    "two pointers",
    "sliding window",
    "binary search",
    "sorting",
    "prefix sums",
    "stack",
    "monotonic stack",
    "linked list",
    "tree traversal",
    "binary search tree",
    "depth-first search",
    "breadth-first search",
    "topological sort",
    "backtracking",
    "recursion",
    "dynamic programming",
    "greedy",
    "heap",
    "divide and conquer",
    # Techniques with no module of their own. Still techniques.
    "intervals",
    "bit manipulation",
    "number theory",
    "digit manipulation",
    "arithmetic",
    "single pass",
    "simulation",
    "parsing",
    "running best",
    "matrix traversal",
    "voting",
    "in-place rearrangement",
]

# Patterns the course teaches, by the module id that teaches them. Mirrors
# cbp/track.py:PATTERN_MODULES; check_modules is what keeps them identical.
MODULES: Dict[str, str] = {
    "binary search": "m10-searching-sorted",
    "two pointers": "m11-two-pointers",
    "sliding window": "m12-sliding-window",
    "hash map": "m13-hash-structures",
    "frequency counting": "m13-hash-structures",
    "stack": "m14-stacks",
    "monotonic stack": "m14-stacks",
    "linked list": "m15-linked-lists",
    "tree traversal": "m16-trees",
    "binary search tree": "m16-trees",
    "depth-first search": "m17-graph-traversal",
    "breadth-first search": "m17-graph-traversal",
    "topological sort": "m17-graph-traversal",
    "backtracking": "m18-backtracking",
    "recursion": "m18-backtracking",
    "dynamic programming": "m19-dynamic-programming",
    "greedy": "m20-heaps-greedy",
    "heap": "m20-heaps-greedy",
}

# The assignment. Most salient first, because that is the order the chips read
# in and the first one is the one worth reading.
QUESTION_PATTERNS: Dict[str, List[str]] = {
    # -- Coderbyte and the hand-written core ------------------------------
    "ab-check": ["frequency counting"],
    "additive-persistence": ["digit manipulation"],
    "alphabet-soup": ["sorting"],
    "arith-geo": ["number theory"],
    "array-addition-i": ["running best"],
    "array-matching": ["single pass"],
    "basic-roman-numerals": ["greedy"],
    "binary-reversal": ["bit manipulation"],
    "bitwise-one": ["bit manipulation"],
    "changing-sequence": ["simulation"],
    "check-nums": ["single pass"],
    "counting-minutes-i": ["parsing", "arithmetic"],
    "dash-insert": ["parsing", "single pass"],
    "division-stringified": ["arithmetic"],
    "even-pairs": ["arithmetic"],
    "ex-oh": ["frequency counting"],
    "first-factorial": ["number theory"],
    "first-reverse": ["two pointers"],
    "hamming-distance": ["bit manipulation"],
    "largest-pair": ["hash map"],
    "letter-capitalize": ["parsing"],
    "letter-changes": ["parsing"],
    "letter-count-i": ["frequency counting", "sorting"],
    "longest-increasing-sequence": ["dynamic programming"],
    "longest-word": ["parsing"],
    "mean-mode": ["frequency counting"],
    "multiplicative-persistence": ["digit manipulation"],
    "nonrepeating-character": ["frequency counting"],
    "number-addition": ["digit manipulation"],
    "off-line-minimum": ["hash map"],
    "other-products": ["prefix sums"],
    "overlapping-ranges": ["intervals"],
    "palindrome": ["two pointers"],
    "powers-of-two": ["bit manipulation"],
    "product-digits": ["digit manipulation"],
    "rectangle-area": ["arithmetic"],
    "second-greatlow": ["sorting"],
    "simple-adding": ["arithmetic"],
    "simple-symbols": ["single pass"],
    "superincreasing": ["prefix sums"],
    "swap-case": ["parsing"],
    "third-greatest": ["sorting"],
    "time-convert": ["arithmetic"],
    "vowel-count": ["frequency counting"],
    "wave-sorting": ["sorting"],
    "word-count": ["parsing"],
    "valid-anagram": ["frequency counting"],
    "contains-duplicate": ["hash map"],
    "arith-geo-ii": ["number theory"],
    "array-addition": ["hash map"],
    "bracket-matcher": ["stack"],
    "caesar-cipher": ["parsing"],
    "coin-determiner": ["dynamic programming"],
    "consecutive": ["sorting"],
    "counting-minutes": ["parsing", "arithmetic"],
    "lc-decode-ways": ["dynamic programming"],
    "letter-count": ["frequency counting"],
    "palindrome-two": ["two pointers"],
    "prime-time": ["number theory"],
    "run-length": ["parsing"],
    "lc-search-rotated": ["binary search"],
    "simple-mode": ["frequency counting"],
    "string-reduction": ["stack", "simulation"],
    "string-scramble": ["frequency counting"],
    "lc-subarray-sum-k": ["prefix sums", "hash map"],
    "three-five-multiples": ["number theory"],
    "two-sum": ["hash map"],
    "maximum-subarray": ["running best"],
    "lc-container-water": ["two pointers"],
    "valid-palindrome-ii": ["two pointers"],
    "best-time-to-trade": ["running best"],
    "lc-candy": ["greedy"],
    "lc-first-missing-positive": ["in-place rearrangement"],
    "house-robber": ["dynamic programming"],
    "longest-common-prefix": ["single pass"],
    "longest-repeating-char": ["single pass"],
    "lc-median-two-sorted": ["binary search", "divide and conquer"],
    "missing-number": ["bit manipulation", "arithmetic"],
    "plus-one": ["in-place rearrangement"],
    "product-except-self": ["prefix sums"],
    "reverse-words": ["two pointers"],
    "search-insert-position": ["binary search"],
    "single-number": ["bit manipulation"],
    "lc-trapping-rain-water": ["two pointers"],

    # -- Grind 75 ---------------------------------------------------------
    "g-valid-parentheses": ["stack"],
    "g-merge-two-sorted-lists": ["linked list", "two pointers"],
    "g-best-time-to-trade": ["running best"],
    "g-valid-palindrome": ["two pointers"],
    "g-invert-binary-tree": ["tree traversal", "recursion"],
    "g-binary-search": ["binary search"],
    "g-flood-fill": ["depth-first search", "matrix traversal"],
    "g-lca-bst": ["binary search tree", "tree traversal"],
    "g-balanced-binary-tree": ["tree traversal"],
    "g-first-bad-version": ["binary search"],
    "g-ransom-note": ["frequency counting"],
    "g-climbing-stairs": ["dynamic programming"],
    "g-longest-palindrome": ["frequency counting"],
    "g-reverse-linked-list": ["linked list"],
    "g-majority-element": ["voting"],
    "g-add-binary": ["bit manipulation", "arithmetic"],
    "g-diameter-binary-tree": ["tree traversal"],
    "g-middle-linked-list": ["linked list", "two pointers"],
    "g-maximum-depth-binary-tree": ["tree traversal", "recursion"],
    "g-insert-interval": ["intervals"],
    "g-zero-one-matrix": ["breadth-first search", "matrix traversal"],
    "g-k-closest-points": ["heap", "sorting"],
    "g-longest-unique-substring": ["sliding window"],
    "g-three-sum": ["two pointers", "sorting"],
    "g-level-order-traversal": ["breadth-first search", "tree traversal"],
    "g-evaluate-rpn": ["stack"],
    "g-course-schedule": ["depth-first search", "topological sort"],
    "g-coin-change": ["dynamic programming"],
    "g-product-except-self": ["prefix sums"],
    "g-validate-bst": ["binary search tree", "tree traversal"],
    "g-number-of-islands": ["depth-first search", "matrix traversal"],
    "g-rotting-oranges": ["breadth-first search", "matrix traversal"],
    "g-search-rotated": ["binary search"],
    "g-combination-sum": ["backtracking"],
    "g-permutations": ["backtracking"],
    "g-merge-intervals": ["intervals", "sorting"],
    "g-lca-binary-tree": ["tree traversal"],
    "g-accounts-merge": ["hash map", "sorting"],
    "g-sort-colors": ["in-place rearrangement"],
    "g-word-break": ["dynamic programming"],
    "g-can-partition": ["dynamic programming"],
    "g-atoi": ["parsing"],
    "g-spiral-matrix": ["matrix traversal", "simulation"],
    "g-subsets": ["backtracking"],
    "g-right-side-view": ["breadth-first search", "tree traversal"],
    "g-longest-palindromic-substring": ["two pointers"],
    "g-unique-paths": ["dynamic programming"],
    "g-build-tree": ["tree traversal", "recursion", "divide and conquer"],
    "g-letter-combinations": ["backtracking"],
    "g-word-search": ["backtracking", "matrix traversal"],
    "g-find-anagrams": ["sliding window", "frequency counting"],
    "g-min-height-trees": ["breadth-first search", "topological sort"],
    "g-task-scheduler": ["greedy", "heap"],
    "g-kth-smallest": ["binary search tree", "tree traversal"],
    "g-min-window-substring": ["sliding window", "frequency counting"],
    "g-ladder-length": ["breadth-first search"],
    "g-basic-calculator": ["stack", "parsing"],
    "g-max-profit-jobs": ["dynamic programming", "sorting"],
    "g-merge-k-sorted": ["heap", "divide and conquer"],
    "g-largest-rectangle": ["monotonic stack"],
}


class PatternError(RuntimeError):
    """The table and the catalogue disagree -- a build failure, not a warning."""


def check_vocabulary() -> None:
    """Every assigned pattern is in the vocabulary, and every module is too."""
    known = set(PATTERNS)
    if len(PATTERNS) != len(known):
        raise PatternError("the vocabulary has a duplicate entry")
    for module_pattern in MODULES:
        if module_pattern not in known:
            raise PatternError(f"module link for unknown pattern {module_pattern!r}")
    for question_id, patterns in QUESTION_PATTERNS.items():
        if not patterns:
            raise PatternError(f"{question_id} has no patterns")
        for pattern in patterns:
            if pattern not in known:
                raise PatternError(f"{question_id} uses {pattern!r}, which is not in the vocabulary")


def check_modules() -> None:
    """The module table here matches the one the server actually reads."""
    import os
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    from cbp.track import PATTERN_MODULES

    if MODULES != PATTERN_MODULES:
        only_here = {k: v for k, v in MODULES.items() if PATTERN_MODULES.get(k) != v}
        only_there = {k: v for k, v in PATTERN_MODULES.items() if MODULES.get(k) != v}
        raise PatternError(
            "tools/patterns.py and cbp/track.py disagree about which module teaches "
            f"which pattern: here={only_here} track={only_there}"
        )


def apply(questions: List[dict]) -> List[dict]:
    """Write `patterns` onto every question, refusing to guess at a gap.

    Idempotent, so whichever builder runs last leaves the catalogue correct.
    """
    check_vocabulary()
    ids = {question["id"] for question in questions}
    unassigned = sorted(ids - set(QUESTION_PATTERNS))
    stale = sorted(set(QUESTION_PATTERNS) - ids)
    if unassigned:
        raise PatternError(
            "questions with no pattern assigned: " + ", ".join(unassigned)
        )
    if stale:
        raise PatternError(
            "patterns assigned to questions that do not exist: " + ", ".join(stale)
        )
    for question in questions:
        question["patterns"] = list(QUESTION_PATTERNS[question["id"]])
    return questions


def report(questions: List[dict]) -> None:
    from collections import Counter

    counts = Counter(p for q in questions for p in q.get("patterns", []))
    print(f"  {len(PATTERNS)} patterns over {len(questions)} questions")
    for pattern in PATTERNS:
        tag = "->" if pattern in MODULES else "  "
        print(f"    {tag} {pattern:<22} {counts.get(pattern, 0)}")


if __name__ == "__main__":
    import json
    import os
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "cbp", "data", "questions.json")
    with open(path) as handle:
        catalogue = json.load(handle)["questions"]
    apply(catalogue)
    check_modules()
    report(catalogue)
    sys.exit(0)
