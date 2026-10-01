"""Golden self-test.

Every reference solution in the dataset is run in every language against its
own test cases, and the structural contract types are proved by a second suite
that the practice dataset cannot reach. This must be fully green before any
result shown to a user can be trusted -- a failure here is a bug in the
harness, not the user.

Run with:  python3 -m cbp.selftest
           python3 -m cbp.selftest --lang python
"""

from __future__ import annotations

import sys

from .adapters import LANGUAGES, effective_arg_types
from .engine import evaluate, load_questions
from .strictness import VALID_TYPES, shape_problem
from .structures import run as run_structures


def check_dataset(questions) -> list:
    """Validate the dataset itself, before any code is run.

    Two things are checked. The top-level `expectedType` is what the UI shows
    as "Must return", while the judge uses each case's own `expectedType`; if
    those disagree the user is told to return the wrong type, which is the
    exact mistake this tool teaches. And every declared type name has to be one
    the harness can actually render, with every value matching the shape that
    name promises -- a tree whose levels are not a list, a matrix row that is a
    string, a type spelled `ture` in a builder script. Those are data bugs, and
    a data bug that reaches a user looks exactly like the user being wrong.
    """
    problems = []
    for question in questions:
        declared = question["expectedType"]
        case_types = {case["expectedType"] for case in question["cases"]}

        if declared not in case_types:
            problems.append(
                f"{question['id']}: declared expectedType {declared!r} matches no "
                f"test case (cases use {sorted(case_types)})"
            )

        # For non-polymorphic questions every case must agree with each other.
        if not question.get("polymorphic") and len(case_types) > 1:
            problems.append(
                f"{question['id']}: test cases disagree on return type "
                f"{sorted(case_types)} but the question is not marked polymorphic"
            )

        if not question.get("solution"):
            problems.append(f"{question['id']}: no reference solutions")

        arity = len(question["signature"]["argNames"])
        for name in question["signature"]["argTypes"]:
            if name not in VALID_TYPES:
                problems.append(f"{question['id']}: unknown argument type {name!r}")
        for name in case_types:
            if name not in VALID_TYPES:
                problems.append(f"{question['id']}: unknown return type {name!r}")

        # `array` is the one contract name that does not say what it holds: the
        # original dataset used it for every list, and the element type is
        # settled from the first test case. The stored name is therefore no use
        # for a shape check, and the resolved one is what gets checked -- which
        # is exactly the point, since a later case that drifts to a different
        # element type is a real data bug.
        resolved = effective_arg_types(question)

        for index, case in enumerate(question["cases"]):
            if len(case["args"]) != arity:
                problems.append(
                    f"{question['id']}: case {index + 1} has {len(case['args'])} "
                    f"args but the signature takes {arity}"
                )
                continue
            for name, value in zip(resolved, case["args"]):
                trouble = shape_problem(value, name)
                if trouble:
                    problems.append(f"{question['id']}: case {index + 1} {trouble}")
            trouble = shape_problem(case["expected"], case["expectedType"])
            if trouble:
                problems.append(f"{question['id']}: case {index + 1} answer {trouble}")
    return problems


def check_course(questions) -> list:
    """Validate the course: every link and drill has to name a real question.

    A principle that links to a question which no longer exists renders as a
    dead chip in the browser, and a module whose drills do not resolve reports
    itself complete as soon as it has none. Both are invisible until someone
    clicks, so they are checked here instead.
    """
    problems = []
    by_id = {question["id"] for question in questions}

    try:
        from .track import load_track
        track = load_track()
    except Exception as exc:                      # noqa: BLE001
        return [f"course could not be loaded: {exc}"]

    if not track["modules"]:
        return ["course has no modules"]

    seen_ids = set()
    parts = {part["id"] for part in track.get("parts", [])}
    for module in track["modules"]:
        module_id = module["id"]
        if module_id in seen_ids:
            problems.append(f"course: duplicate module id {module_id!r}")
        seen_ids.add(module_id)

        if parts and module.get("part") not in parts:
            problems.append(
                f"course: module {module_id!r} is in part "
                f"{module.get('part')!r}, which is not one of {sorted(parts)}")
        if not module.get("minutes"):
            problems.append(f"course: module {module_id!r} has no reading time")
        if not module.get("principles"):
            problems.append(f"course: module {module_id!r} has no principles")

        for question_id in module.get("drills", []):
            if question_id not in by_id:
                problems.append(
                    f"course: module {module_id!r} drills on {question_id!r}, "
                    "which is not in the catalogue")
        if not module.get("drills"):
            problems.append(
                f"course: module {module_id!r} has no drills, so it cannot be "
                "marked complete")

        for principle in module.get("principles", []):
            heading = principle.get("heading", "<no heading>")
            for field in ("heading", "body"):
                if not principle.get(field):
                    problems.append(
                        f"course: module {module_id!r} principle {heading!r} "
                        f"has no {field}")
            if not principle.get("check"):
                problems.append(
                    f"course: module {module_id!r} principle {heading!r} has no "
                    "self-check question")
            for question_id in principle.get("uses", []):
                if question_id not in by_id:
                    problems.append(
                        f"course: module {module_id!r} principle {heading!r} "
                        f"links to {question_id!r}, which is not in the catalogue")
    return problems


def run(languages=None) -> int:
    languages = languages or LANGUAGES
    questions = load_questions()
    failures = []
    checks = 0

    problems = check_dataset(questions) + check_course(questions)
    if problems:
        print("Dataset problems (these are wrong, not merely untested):")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(f"  dataset ok   {len(questions)} questions, contracts self-consistent")

    for language in languages:
        print(f"\n=== {language} ===")
        for question in questions:
            source = question["solution"].get(language)
            if source is None:
                print(f"  SKIP  {question['id']:20s} (no {language} solution)")
                continue

            report = evaluate(question, language, source)
            checks += 1
            if report["error"]:
                failures.append((language, question["id"], report["error"]["kind"],
                                 report["error"]["message"]))
                print(f"  ERROR {question['id']:20s} [{report['error']['kind']}]")
                for line in report["error"]["message"].splitlines()[:4]:
                    print(f"          {line}")
            elif not report["all_passed"]:
                bad = [r for r in report["results"] if not r["passed"]]
                failures.append((language, question["id"], "wrong",
                                 bad[0]["message"] if bad else "?"))
                print(f"  FAIL  {question['id']:20s} {bad[0]['message']}")
            else:
                print(f"  pass  {question['id']:20s} ({len(report['results'])} cases)")

    print("\n" + "=" * 60)
    print(f"{checks - len(failures)}/{checks} passed across {len(languages)} language(s)")
    if failures:
        print(f"\n{len(failures)} FAILURE(S) -- the harness is not trustworthy yet:")
        for lang, qid, kind, msg in failures:
            print(f"  [{lang}] {qid}: {kind}")
            for line in str(msg).splitlines()[:3]:
                print(f"      {line}")
        return 1

    # The practice set never returns a tree or a matrix, so those contracts are
    # proved by their own suite rather than by the 84 questions above.
    if run_structures(languages):
        return 1

    print("Harness verified. Results shown to the user can be trusted.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    langs = None
    if "--lang" in args:
        langs = [args[args.index("--lang") + 1]]
    sys.exit(run(langs))
