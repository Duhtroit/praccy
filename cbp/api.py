"""JSON-friendly views of engine results, for the browser UI.

The terminal renderer in `forensics` is not reusable here: it emits ANSI colour
codes and human prose. This module produces plain data the web layer can turn
into markup, keeping the diagnosis logic in exactly one place.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .adapters import effective_arg_types
from .hints import hints_for
from .lessons import lesson_for, question_note
from .strictness import python_type_name


def _display(value: Any) -> Optional[str]:
    """Render a value the way the UI should show it, preserving type cues.

    Quoting strings is the point: it is what makes `"true"` and `true` look
    different on screen, which is the mistake this tool exists to catch.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_display(v) or "null" for v in value) + "]"
    return str(value)


def _common_prefix(a: str, b: str) -> int:
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i


def explain_case(result: dict) -> dict:
    """Turn one failed case into structured data for the UI."""
    expected = result["expected"]
    actual = result["actual"]
    expected_type = result["expectedType"]
    actual_type = python_type_name(actual) if actual is not None else "nothing"

    detail = None
    advice = None
    kind = "value"

    if actual is None:
        kind = "no_output"
        detail = "Your function returned no value for this input."
        advice = "Check that every branch returns, and that you return rather than print."
    elif actual_type != expected_type:
        kind = "type"
        detail = f"Expected a {expected_type}, but you returned a {actual_type}."
        advice = _TYPE_ADVICE.get((expected_type, actual_type))
    elif isinstance(expected, str) and isinstance(actual, str):
        first = _common_prefix(expected, actual)
        if first < len(expected):
            kind = "value"
            detail = (
                f"First difference at position {first}: "
                f"expected {expected[first]!r}, you returned {actual[first]!r}."
            )
        if len(expected) != len(actual):
            detail = (detail or "The values differ.") + (
                f" Length differs too: expected {len(expected)} "
                f"characters, got {len(actual)}."
            )
    elif expected_type == "int" and actual_type == "int":
        diff = actual - expected
        kind = "value"
        detail = f"Off by {abs(diff)} ({'too high' if diff > 0 else 'too low'})."

    return {
        "index": result["index"],
        "args": result["args"],
        "expected": _display(expected),
        "expectedType": expected_type,
        "actual": _display(actual),
        "actualType": actual_type,
        "detail": detail,
        "advice": advice,
        "kind": kind,
    }


_TYPE_ADVICE = {
    ("string", "bool"): 'The prompt says "return the string true/false" -- '
                        "return a string, not a boolean.",
    ("bool", "string"): "This question wants a real boolean, not the words "
                        "true/false as text.",
    ("int", "bool"): "True/False is not accepted as 1/0 here -- return an int.",
    ("bool", "int"): "Return true or false, not 1 or 0.",
    ("int", "float"): "A decimal was returned where a whole number is required.",
    ("float", "int"): "An int was returned where a decimal is required.",
    ("string", "int"): "Return the words, not a number.",
    ("int", "string"): "Return a number, not text.",
    ("string", "float"): "Return text, not a number.",
    ("float", "string"): "Return a number, not text.",
}


def evaluate_payload(question: dict, language: str, source: str) -> dict:
    """Run a submission and return everything the UI needs as plain data."""
    from .engine import evaluate

    evaluation = evaluate(question, language, source)
    payload: Dict[str, Any] = {
        "ok": bool(evaluation["all_passed"]),
        "language": language,
        "error": evaluation["error"],
        "cases": [],
        "passedCount": 0,
        "totalCount": 0,
        "lesson": None,
    }

    if evaluation["error"]:
        payload["cases"] = []
        payload["totalCount"] = len(question["cases"])
        return payload

    results = evaluation["results"]
    payload["totalCount"] = len(results)
    payload["passedCount"] = sum(1 for r in results if r["passed"])

    for result in results:
        entry = {
            "index": result["index"],
            "passed": result["passed"],
            "args": result["args"],
            "expected": _display(result["expected"]),
            "expectedType": result["expectedType"],
            "actual": _display(result["actual"]),
            "actualType": (
                python_type_name(result["actual"])
                if result["actual"] is not None else "nothing"
            ),
        }
        if not result["passed"]:
            entry.update(explain_case(result))
        payload["cases"].append(entry)

    if not payload["ok"]:
        payload["lesson"] = lesson_for(evaluation, question)

    return payload


def question_payload(question: dict, include_solution: bool = False) -> dict:
    """Serialise a question for the browser, optionally with its solution."""
    payload = {
        "id": question["id"],
        "title": question["title"],
        "tier": question["tier"],
        # `tags` are the free-text topics the sidebar searches; `patterns` are
        # the techniques the question is actually built from, from the closed
        # vocabulary in tools/patterns.py, and they are what the Patterns row
        # shows. The two are deliberately different: "math fundamentals" is a
        # reasonable thing to search for and not a technique.
        "tags": question["tags"],
        "patterns": question.get("patterns", []),
        "verified": question.get("verified", True),
        "polymorphic": question.get("polymorphic", False),
        "source": question.get("source"),
        "sourceId": question.get("sourceId"),
        "sourceNote": question.get("sourceNote"),
        "prompt": question["prompt"],
        # Written per question, revealed one at a time in the UI. There are
        # always at least two; tools/build_hints.py is what enforces that.
        "hints": hints_for(question["id"]),
        "functionName": question["functionName"],
        "expectedType": question["expectedType"],
        "note": question_note(question),
        "signature": question["signature"],
        # The stored `array` cannot say whether the elements are ints or
        # strings, so the browser gets the resolved element types too.
        "argTypes": effective_arg_types(question),
        "examples": [
            {
                "args": case["args"],
                "expected": _display(case["expected"]),
                "expectedType": case["expectedType"],
            }
            for case in question["cases"]
        ],
    }
    if include_solution:
        payload["solution"] = question["solution"]
    return payload


def catalogue(questions: List[dict]) -> List[dict]:
    """Lightweight listing for the sidebar."""
    return [
        {
            "id": q["id"],
            "title": q["title"],
            "tier": q["tier"],
            "tags": q["tags"],
            "patterns": q.get("patterns", []),
            "verified": q.get("verified", True),
            "polymorphic": q.get("polymorphic", False),
            "source": q.get("source"),
            "sourceNote": q.get("sourceNote"),
        }
        for q in questions
    ]
