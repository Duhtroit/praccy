#!/usr/bin/env python3
"""Shared vocabulary for the Grind 75 question waves.

The list is 75 long and is being added in waves, so each wave lives in its own
module and they all import from here. A change to a contract type, a prompt
note, or the shape of a `q(...)` call therefore lands in every wave at once,
rather than needing the same edit repeated in each one.

`build_grind75.py` is the only module that writes anything; the waves just
describe questions.
"""

from __future__ import annotations

STR, INT, BOOL = "string", "int", "bool"
ARR, STRI = "array", "stri"
LIST, TREE, MATRIX, GRAPH = "list", "tree", "matrix", "graph"
STRMATRIX, CHARMATRIX, STRARRAY = "strmatrix", "charmatrix", "strarray"

STRETCH = "stretch"
ALGO, SEARCH, SM, DP, TREE_TAG = (
    "algorithm", "searching", "string manipulation", "dynamic programming", "tree",
)
LC = "LeetCode"

# Every tree question says the same thing about the encoding, because getting it
# wrong makes the question unsolvable rather than hard.
TREE_NOTE = (
    "A tree arrives as a flat array in level order: the node at index p has its "
    "left child at 2p+1 and its right child at 2p+2. A missing child is null, "
    "trailing nulls are trimmed, and the empty tree is []. So [1, 2, 3, null, "
    "null, null, 5] is a root of 1 whose right child 3 has a right child of 5."
)

# A matrix is just a list of equal-length rows, which is close to obvious, but
# saying it once here is cheaper than saying it on every question that takes a
# grid or a point cloud.
MATRIX_NOTE = (
    "A matrix arrives as a list of rows, each row a list of the same length, "
    "and is returned the same way. The empty matrix is []."
)

LINKED_LIST_NOTE = (
    "A linked list arrives as its values from head to tail, so the list [1, 2, "
    "3] is three nodes pointing forward and the empty list is []."
)


def q(qid, title, tier, tags, fn, prompt, sig, cases, sol,
      position=None, source=None, sourceId=None, sourceNote=None, **extra):
    """Build one question dict in the shape `cbp/engine.py` expects."""
    arg_names, arg_types = sig
    case_types = {c["expectedType"] for c in cases}
    question = {
        "id": qid,
        "title": title,
        "tier": tier,
        "tags": list(dict.fromkeys(tags)),
        "verified": extra.pop("verified", True),
        "functionName": fn,
        "expectedType": cases[0]["expectedType"],
        "prompt": prompt,
        "signature": {"argNames": arg_names, "argTypes": arg_types},
        "cases": cases,
        "solution": sol,
    }
    # `grind75` is the 1-based position on the canonical list. The catalogue
    # sorts on it, because the ordering is the whole point of the list.
    if position is not None:
        question["grind75"] = position
    if source is not None:
        question["source"] = source
        question["sourceId"] = sourceId
        question["sourceNote"] = sourceNote
    if len(case_types) > 1:
        question["polymorphic"] = True
        question.setdefault("polymorphicNote", (
            "This question returns more than one type depending on the input "
            f"({', '.join(sorted(case_types))}). Statically typed languages must "
            "return a variant type (std::variant in C++, object in C#, Object "
            "in Java, the CBResult enum in Rust)."
        ))
    question.update(extra)
    return question


def S(p, cpp, cs, java):
    """The four inline solutions. Rust lives in `rust_solutions.py`."""
    return {"python": p, "cpp": cpp, "csharp": cs, "java": java}


def c(args, expected, t):
    """One test case."""
    return {"args": args, "expected": expected, "expectedType": t}
