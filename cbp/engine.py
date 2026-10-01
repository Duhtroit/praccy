"""Question loading, running and judging."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .adapters import ADAPTERS
from .errors import RunError
from .strictness import decode_wire, judge

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "questions.json")


def load_questions() -> List[dict]:
    with open(DATA_PATH) as fh:
        return json.load(fh)["questions"]


def all_tags(questions: List[dict]) -> List[str]:
    tags = set()
    for q in questions:
        tags.update(q["tags"])
    return sorted(tags)


def _user_code_for(question: dict, language: str) -> str:
    """Return the user's source plus any adapter-specific prep."""
    return question["_userCode"]


def run_submission(question: dict, language: str, source: str) -> List[Any]:
    """Run `source` against every test case. Returns one value per case.

    Raises RunError if the code fails to compile, crashes or hangs.
    """
    if language not in ADAPTERS:
        raise RunError("interface", f"unsupported language {language!r}", language)

    # Each case needs its own argument literals baked into the harness, so the
    # harness evaluates every case in one process and prints one envelope per
    # line. `_argLiterals` is consumed by the language-specific harness.
    working = dict(question)
    working["_userCode"] = source
    working["_argLiterals"] = []  # populated per case inside the adapters

    return ADAPTERS[language].run(working, source)


def judge_all(question: dict, actuals: List[Any]) -> List[dict]:
    """Judge the returned values against the question's cases.

    Returns a list of per-case results, each with passed/message plus an
    'expected' field for the forensics view.
    """
    results = []
    for i, case in enumerate(question["cases"]):
        if i < len(actuals):
            passed, message = judge(actuals[i], case)
        else:
            passed, message = False, "no value returned for this case"
        results.append(
            {
                "index": i,
                "args": case["args"],
                "expected": case["expected"],
                "expectedType": case["expectedType"],
                "actual": actuals[i] if i < len(actuals) else None,
                "passed": passed,
                "message": message,
            }
        )
    return results


def evaluate(question: dict, language: str, source: str) -> dict:
    """Full pipeline: run then judge. Never raises; returns a report."""
    try:
        actuals = run_submission(question, language, source)
    except RunError as exc:
        return {
            "ok": False,
            "error": {"kind": exc.kind, "message": exc.message, "language": exc.language},
            "results": [],
            "all_passed": False,
        }

    results = judge_all(question, actuals)
    return {
        "ok": True,
        "error": None,
        "results": results,
        "all_passed": all(r["passed"] for r in results),
    }
