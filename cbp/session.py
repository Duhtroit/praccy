"""Interactive practice session.

The clock starts when the first line of your answer is typed and stops the
moment you submit. It never fails you for going slow -- it only measures you,
and reports at the end. It measures writing code, not reading the question.
"""

from __future__ import annotations

import random
import time
from typing import List, Optional

from . import forensics
from .adapters import LANGUAGES
from .engine import all_tags, evaluate, load_questions
from .lessons import lesson_for, question_note

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def fmt_duration(seconds: float) -> str:
    seconds = max(0.0, seconds)
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    if minutes == 0:
        return f"{remainder:4.1f}s"
    return f"{minutes}m {remainder:04.1f}s"


def read_source(language: str, question: dict) -> tuple:
    """Read the user's code, returning it with the time spent typing it.

    The clock starts on the first line of code entered, not when the prompt is
    printed, so it measures writing the answer rather than reading the
    question. Submitting nothing means no time at all, which is the honest
    answer.
    """
    print(f"  {DIM}Enter your {language} code. Finish with a line containing only 'END'.{RESET}")
    if question.get("polymorphic"):
        note = question.get("polymorphicNote")
        if note:
            print(f"  {YELLOW}{note}{RESET}")
    print()
    lines = []
    started = None
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        if started is None:
            started = time.monotonic()
        lines.append(line)
    elapsed = 0.0 if started is None else time.monotonic() - started
    return "\n".join(lines), elapsed


def run_session(questions: List[dict], language: str) -> dict:
    """Run one practice session. Returns a summary dict."""
    results = []

    for index, question in enumerate(questions, start=1):
        print()
        print("=" * 68)
        print(f"{BOLD}Question {index} of {len(questions)}{RESET}  "
              f"{CYAN}{question['title']}{RESET}  "
              f"{DIM}[{question['tier']} | {', '.join(question['tags'])}]{RESET}")
        print("=" * 68)
        print()
        print(question["prompt"])
        print()

        note = question_note(question)
        if note:
            print(f"{YELLOW}  note: {note}{RESET}")
            print()

        # The timer starts on the first typed line and stops at END.
        source, elapsed = read_source(language, question)

        evaluation = evaluate(question, language, source)
        passed = evaluation["all_passed"]

        print()
        print(forensics.report(evaluation))

        if passed:
            print(f"  {GREEN}solved in {fmt_duration(elapsed)}{RESET}")
        else:
            print(f"  {DIM}time {fmt_duration(elapsed)}{RESET}")
            lesson = lesson_for(evaluation, question)
            if lesson:
                print()
                print(f"  {YELLOW}{'~' * 66}{RESET}")
                for line in lesson.splitlines():
                    print(f"  {line}")
                print(f"  {YELLOW}{'~' * 66}{RESET}")

        # The worked solution is always reachable.
        print()
        if input("  [s]how solution, [r]etry, [n]ext > ").strip().lower().startswith("s"):
            print()
            print(f"  {DIM}--- reference solution ({language}) ---{RESET}")
            for line in question["solution"].get(language, "(none)").splitlines():
                print(f"  {line}")
            print()

        results.append({
            "id": question["id"],
            "title": question["title"],
            "tier": question["tier"],
            "tags": question["tags"],
            "passed": passed,
            "seconds": elapsed,
        })

    return summarize(results)


def summarize(results: List[dict]) -> dict:
    """Print an end-of-session breakdown by time and by tag."""
    print()
    print("=" * 68)
    print(f"{BOLD}Session summary{RESET}")
    print("=" * 68)
    if not results:
        return {}

    solved = [r for r in results if r["passed"]]
    total_time = sum(r["seconds"] for r in results)

    print(f"  solved      {len(solved)}/{len(results)}")
    print(f"  total time  {fmt_duration(total_time)}")
    if solved:
        fastest = min(solved, key=lambda r: r["seconds"])
        print(f"  fastest     {fastest['title']} ({fmt_duration(fastest['seconds'])})")

    # Per-tag accuracy tells you what to drill next.
    by_tag: dict = {}
    for r in results:
        for tag in r["tags"]:
            entry = by_tag.setdefault(tag, {"pass": 0, "total": 0, "time": 0.0})
            entry["total"] += 1
            entry["time"] += r["seconds"]
            if r["passed"]:
                entry["pass"] += 1

    if by_tag:
        print()
        print(f"  {DIM}by topic{RESET}")
        for tag, entry in sorted(by_tag.items(), key=lambda kv: kv[1]["pass"] / kv[1]["total"]):
            rate = entry["pass"] / entry["total"] * 100
            bar = "#" * int(rate / 10)
            print(f"    {tag:24s} {entry['pass']}/{entry['total']}  "
                  f"{rate:5.1f}%  {DIM}{bar}{RESET}")

    unsolved = [r for r in results if not r["passed"]]
    if unsolved:
        print()
        print(f"  {YELLOW}worth another look:{RESET} "
              f"{', '.join(r['title'] for r in unsolved)}")
    print()
    return {"solved": len(solved), "total": len(results), "time": total_time}


def pick_questions(questions: List[dict], tier: Optional[str] = None,
                   tag: Optional[str] = None, count: int = 5) -> List[dict]:
    pool = questions
    if tier:
        pool = [q for q in pool if q["tier"] == tier]
    if tag:
        pool = [q for q in pool if tag in q["tags"]]
    if not pool:
        return []
    return random.sample(pool, min(count, len(pool)))
