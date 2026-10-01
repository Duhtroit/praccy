"""Failure forensics.

A pass/fail badge teaches nothing. This module turns each failed case into a
concrete, typed comparison: what the contract demanded, what you returned, and
-- for strings -- exactly which characters differ.
"""

from __future__ import annotations

from typing import List, Optional

from .strictness import python_type_name

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

ERROR_LABEL = {
    "compile": "does not compile",
    "runtime": "crashed",
    "timeout": "timed out (infinite loop?)",
    "interface": "harness problem",
}


def _color(text: str, code: str, enabled: bool) -> str:
    return f"{code}{text}{RESET}" if enabled else text


def format_value(value) -> str:
    """Render a value with its type visible, which is the whole point."""
    if isinstance(value, str):
        return f'"{value}"'
    if value is None:
        return "nothing"
    return repr(value)


def _string_diff(expected: str, actual: str) -> Optional[str]:
    """Describe the first difference between two strings."""
    if len(expected) != len(actual):
        first = _common_prefix(expected, actual)
        where = f"position {first}"
        if len(expected) > len(actual):
            detail = f"expected {len(expected)} chars, got {len(actual)}"
        else:
            detail = f"expected {len(expected)} chars, got {len(actual)} (too long)"
        return f"first difference at {where}; {detail}"
    first = _common_prefix(expected, actual)
    if first < len(expected):
        return (
            f"first difference at position {first}: "
            f"expected {expected[first]!r}, got {actual[first]!r}"
        )
    return None


def _common_prefix(a: str, b: str) -> int:
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i


def explain(result: dict, color: bool = True) -> str:
    """Explain one failed test case."""
    expected = result["expected"]
    actual = result["actual"]
    expected_type = result["expectedType"]

    lines = [f"  input    {format_value(result['args'][0]) if result['args'] else '(none)'}"]
    if len(result["args"]) > 1:
        for i, extra in enumerate(result["args"][1:], start=2):
            lines.append(f"           arg{i}  {format_value(extra)}")

    lines.append(
        f"  expected {_color(format_value(expected) + f'  ({expected_type})', CYAN, color)}"
    )
    actual_type = python_type_name(actual) if actual is not None else "nothing"
    lines.append(f"  you      {_color(format_value(actual) + f'  ({actual_type})', RED, color)}")

    # A type error is the highest-value diagnosis, so lead with it.
    if actual is not None and actual_type != expected_type:
        lines.append(
            f"  {YELLOW if color else ''}-> type mismatch, not a value problem{RESET if color else ''}"
        )
        if expected_type == "string" and actual_type == "bool":
            lines.append(
                "     this question returns the STRING \"true\"/\"false\", not a boolean"
            )
        elif expected_type == "int" and actual_type == "bool":
            lines.append("     True/False is not an int here -- use 1/0 or drop the bool")
        elif expected_type == "float" and actual_type == "int":
            lines.append("     an int was returned where a decimal was required")
        elif expected_type == "int" and actual_type == "float":
            lines.append("     a decimal was returned where a whole number was required")
    elif isinstance(expected, str) and isinstance(actual, str):
        diff = _string_diff(expected, actual)
        if diff:
            lines.append(f"  -> {diff}")
    elif actual is None:
        lines.append("  -> your code returned no value for this input")

    return "\n".join(lines)


def report(evaluation: dict, color: bool = True) -> str:
    """Render a full evaluation: error, or per-case pass/fail breakdown."""
    if evaluation["error"]:
        err = evaluation["error"]
        label = ERROR_LABEL.get(err["kind"], err["kind"])
        out = [_color(f"  Your code {label}:", RED, color)]
        for line in err["message"].splitlines():
            out.append(f"    {line}")
        return "\n".join(out)

    passed = sum(1 for r in evaluation["results"] if r["passed"])
    total = len(evaluation["results"])
    out = []

    if evaluation["all_passed"]:
        out.append(_color(f"  All {total} cases passed.", GREEN, color))
        return "\n".join(out)

    for result in evaluation["results"]:
        if not result["passed"]:
            out.append(_color(f"  FAIL  case {result['index'] + 1}", YELLOW, color))
            out.append(explain(result, color))
            out.append("")

    out.append(f"  {passed}/{total} cases passed.")
    return "\n".join(out)


def failure_kind(evaluation: dict) -> Optional[str]:
    """Classify a failure so the UI can pick an appropriate hint."""
    if evaluation.get("error"):
        return evaluation["error"]["kind"]
    failed = [r for r in evaluation.get("results", []) if not r["passed"]]
    if not failed:
        return None
    for result in failed:
        if result["actual"] is None:
            return "no_output"
        if python_type_name(result["actual"]) != result["expectedType"]:
            return "type"
    return "value"
