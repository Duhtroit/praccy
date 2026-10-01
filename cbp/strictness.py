"""Strict output-type comparison.

This module is the heart of the project. Coderbyte rejects answers that are
logically correct but the wrong *type*: PalindromeTwo must return the string
"false", not the boolean False. Every comparison in this program goes through
`judge` so that mistake is impossible to make by accident.
"""

from __future__ import annotations

import json
from typing import Any, Optional, Tuple

# The scalar types a question can return, plus the list types.
STRING = "string"
INT = "int"
FLOAT = "float"
BOOL = "bool"
ARRAY = "array"

# The structural types. Each one is a list, but the elements and the meaning
# are pinned down, and that is the whole point: a list argument to Maximum Sum
# is a run of numbers, a list argument to Reverse Linked List is a chain of
# nodes, and a function that returns the wrong one is wrong even though Python
# cannot tell the difference.
#
# The wire encodings are the compact ones the question's own text uses, so a
# problem reads the same here as it does anywhere else:
#
#   tree       [1, 2, 3, null, 5]      level order, null for a missing child
#   list       [1, 2, 3]               head first, in order
#   matrix     [[1, 2], [3, 4]]        rows of numbers
#   graph      [[1, 2], [2], []]       adjacency list, indexed by node
#   strarray   ["cat", "dog"]          list of words
#   charmatrix [["a", "b"], ["c", "d"]]  rows of single characters
#   strmatrix  [["cat", "dog"]]          rows of words
TREE = "tree"
LIST = "list"
MATRIX = "matrix"
GRAPH = "graph"
STRARRAY = "strarray"
CHARMATRIX = "charmatrix"
# Rows of words rather than rows of characters. Accounts Merge is the
# reason it exists: its answer is a list of lists of names, which is neither a
# matrix (its cells are strings) nor a charmatrix (its cells are words, not
# single characters).
STRMATRIX = "strmatrix"

# A list type that only ever appears as an argument. `stri` predates the rest:
# the original dataset recorded string-list arguments as `array` and this is
# the resolved name the harness and the browser use.
STRI = "stri"

# Everything a signature or an expectedType may name.
VALID_TYPES = {STRING, INT, FLOAT, BOOL, ARRAY,
               TREE, LIST, MATRIX, GRAPH, STRARRAY, CHARMATRIX, STRMATRIX, STRI}

# The subset usable as a return contract.
RETURN_TYPES = VALID_TYPES - {STRI}

# Every list type, and what the judge actually compares: the elements. A tree
# is judged as a list of ints and nulls, a matrix as a list of lists. The label
# never enters the comparison, so `judge` needs no special case per type.
LIST_TYPES = {ARRAY, TREE, LIST, MATRIX, GRAPH, STRARRAY, CHARMATRIX, STRMATRIX, STRI}


def is_list_type(name: str) -> bool:
    return name in LIST_TYPES


def wire_type(name: str) -> str:
    """The shape a contract name is actually compared as.

    Every list contract is compared as a list. Python cannot tell a tree from
    a linked list once both are lists, and pretending otherwise would mean
    five near-identical comparison functions. What the label still buys is the
    error message, the starter signature, and the envelope tag -- the three
    places where "you returned the wrong kind of list" has to be legible.
    """
    return ARRAY if name in LIST_TYPES else name


class TypeMismatch(Exception):
    """Raised when a value is of the wrong type for the question contract."""


def python_type_name(value: Any) -> str:
    """Name a Python value's type the way the question contract names it."""
    # bool MUST be checked before int: bool is a subclass of int in Python, so
    # `isinstance(True, int)` is True. Checking int first would let a boolean
    # silently pass an int contract -- exactly the bug this module exists for.
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return INT
    if isinstance(value, float):
        return FLOAT
    if isinstance(value, str):
        return STRING
    if isinstance(value, (list, tuple)):
        return ARRAY
    return type(value).__name__


def check_type(value: Any, expected_type: str) -> None:
    """Raise TypeMismatch unless `value` matches `expected_type` exactly."""
    if expected_type not in VALID_TYPES:
        raise ValueError(f"unknown expected type {expected_type!r}")

    actual = python_type_name(value)
    if actual != wire_type(expected_type):
        # The label is what the user was told to return, so it is the name that
        # belongs in the error, even though the comparison ran on the elements.
        raise TypeMismatch(f"expected type {expected_type}, got {actual}")


def shape_problem(value: Any, expected_type: str) -> Optional[str]:
    """Describe how `value` fails a contract's element rules, or return None.

    `check_type` catches "you returned a string". This catches the quieter
    mistakes: a tree handed in as a flat list of numbers with no nulls, a
    matrix row that is a string, a graph that is not a list of lists. The
    dataset is checked with this too, so a typo in a builder script is caught
    at build time instead of showing up as a puzzle nobody can solve.
    """
    if expected_type not in LIST_TYPES:
        return None
    if not isinstance(value, (list, tuple)):
        return f"expected a list for {expected_type}, got {type(value).__name__}"

    if expected_type in (TREE, LIST, ARRAY, STRI, STRARRAY):
        wants_text = expected_type in (STRI, STRARRAY)
        for index, item in enumerate(value):
            if expected_type == TREE:
                if item is not None and (isinstance(item, bool) or not isinstance(item, int)):
                    return (f"tree position {index} is {item!r}; a tree holds ints "
                            f"and null (null for a missing child)")
            elif wants_text:
                if not isinstance(item, str):
                    return f"position {index} is {item!r}; {expected_type} holds strings"
            elif isinstance(item, bool) or not isinstance(item, int):
                return f"position {index} is {item!r}; {expected_type} holds ints"
        return None

    if expected_type in (MATRIX, GRAPH, CHARMATRIX, STRMATRIX):
        for row_index, row in enumerate(value):
            if not isinstance(row, (list, tuple)):
                return (f"row {row_index} is {row!r}; {expected_type} is a list "
                        f"of lists")
            for cell_index, cell in enumerate(row):
                if expected_type == CHARMATRIX:
                    if not isinstance(cell, str) or len(cell) != 1:
                        return (f"cell [{row_index}][{cell_index}] is {cell!r}; a "
                                f"charmatrix holds single characters")
                elif expected_type == STRMATRIX:
                    if not isinstance(cell, str):
                        return (f"cell [{row_index}][{cell_index}] is {cell!r}; "
                                f"an strmatrix holds words")
                elif isinstance(cell, bool) or not isinstance(cell, int):
                    return (f"cell [{row_index}][{cell_index}] is {cell!r}; "
                            f"{expected_type} holds ints")
        return None

    return None


def values_equal(actual: Any, expected: Any) -> bool:
    """Compare two values of the same type, avoiding True == 1 and 1 == 1.0.

    A null inside a tree compares as equal only to another null: `None == 0`
    is False in Python, but `None == False` is also False, so the explicit
    branch below is what keeps a tree from matching a tree full of zeroes.
    """
    if expected is None or actual is None:
        return expected is None and actual is None

    a_kind, e_kind = python_type_name(actual), python_type_name(expected)
    if a_kind != e_kind:
        return False
    if e_kind == ARRAY:
        if len(actual) != len(expected):
            return False
        return all(values_equal(a, e) for a, e in zip(actual, expected))
    if e_kind == FLOAT:
        # Tolerate float representation noise, but not a genuine value gap.
        return abs(actual - expected) < 1e-9
    return actual == expected


def judge(actual: Any, case: dict) -> Tuple[bool, str]:
    """Judge one test case.

    Returns (passed, message). A message is always supplied on failure so the
    forensics view has something concrete to show the user.
    """
    expected = case["expected"]
    expected_type = case["expectedType"]

    try:
        check_type(actual, expected_type)
    except TypeMismatch as exc:
        return False, f"wrong type: {exc}"

    if values_equal(actual, expected):
        return True, ""

    return False, (
        f"right type, wrong value: expected {expected!r}, got {actual!r}"
    )


def decode_wire(payload: str) -> Any:
    """Decode the JSON envelope a non-Python adapter prints.

    Each adapter emits {"t": <type>, "v": <value>} so the type survives the
    trip across the process boundary. Falling back to a bare JSON value would
    lose the distinction between the string "true" and the boolean true.
    """
    envelope = json.loads(payload)
    if not isinstance(envelope, dict) or "t" not in envelope or "v" not in envelope:
        # Not an envelope -- treat the whole thing as an untyped value.
        return envelope
    return envelope["v"]


def encode_wire(value: Any) -> str:
    """Build the JSON envelope an adapter prints."""
    return json.dumps({"t": python_type_name(value), "v": value})
