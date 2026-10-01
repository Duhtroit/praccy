"""The course: principles that generalise across every question.

Loaded from data/track.json. The course teaches method, not answers. A module
ends in a set of drills drawn from the real question catalogue, and an
individual principle may name the questions that use it, so a technique is
learned by doing the questions that depend on it rather than by recognising
the name of it.

The `uses` list on a principle is a cross-reference, not a prerequisite. A
principle about sliding windows links to the four questions in the catalogue
that are sliding-window problems; nothing in the app stops you reading a module
before you have done those four.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

TRACK_PATH = os.path.join(os.path.dirname(__file__), "data", "track.json")

# Which module teaches each pattern. The patterns are a closed vocabulary now
# -- tools/patterns.py owns it and assigns one to every question -- so this is a
# lookup rather than a translation. The old version had to guess, because the
# tags grew out of the question set and the modules grew out of the course, and
# "searching" on 45 questions meant nothing more specific than "this needs a
# loop".
#
# A pattern that is missing from here has no lesson behind it -- "arithmetic",
# "parsing", "single pass" -- and the UI renders it as a plain chip rather than
# linking it somewhere unrelated. tools/patterns.py:check_modules fails the
# build if this table and that file ever disagree.
PATTERN_MODULES = {
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


def load_track() -> dict:
    with open(TRACK_PATH) as fh:
        return json.load(fh)["track"]


def modules() -> List[dict]:
    return load_track()["modules"]


def total_minutes() -> int:
    return sum(module["minutes"] for module in modules())


def module_by_id(module_id: str) -> Optional[dict]:
    return next((m for m in modules() if m["id"] == module_id), None)


def drill_questions(module: dict, questions: List[dict]) -> List[dict]:
    """Resolve a module's drill ids to question records, keeping the order."""
    by_id = {question["id"]: question for question in questions}
    resolved = []
    for drill_id in module.get("drills", []):
        question = by_id.get(drill_id)
        if question:
            resolved.append(question)
    return resolved


def next_module(module_id: Optional[str]) -> Optional[dict]:
    """The module after the given one, or the first if unknown."""
    all_modules = modules()
    if not module_id:
        return all_modules[0] if all_modules else None
    for index, module in enumerate(all_modules):
        if module["id"] == module_id:
            return all_modules[index + 1] if index + 1 < len(all_modules) else None
    return all_modules[0] if all_modules else None


def _summarise(by_id: Dict[str, dict], question_ids: List[str]) -> List[dict]:
    """Resolve question ids to the {id, title, tier} the UI needs, in order.

    Ids that are not in the catalogue are dropped rather than raised, so one
    stale link cannot take the whole course down in the browser. The dataset
    check is what makes a stale link an error.
    """
    out = []
    for question_id in question_ids:
        question = by_id.get(question_id)
        if question:
            out.append({
                "id": question["id"],
                "title": question["title"],
                "tier": question["tier"],
            })
    return out


def track_payload(questions: List[dict]) -> dict:
    """Serialise the whole course for the browser, with questions resolved."""
    by_id = {question["id"]: question for question in questions}
    payload = {"modules": [], "totalMinutes": 0, "title": "", "subtitle": ""}
    track = load_track()
    payload["title"] = track["title"]
    payload["subtitle"] = track["subtitle"]

    for module in track["modules"]:
        principles = []
        for principle in module["principles"]:
            resolved = dict(principle)
            if "uses" in principle:
                resolved["uses"] = _summarise(by_id, principle["uses"])
            principles.append(resolved)

        payload["modules"].append({
            "id": module["id"],
            "title": module["title"],
            "subtitle": module["subtitle"],
            "minutes": module["minutes"],
            "part": module.get("part", "patterns"),
            "principles": principles,
            "drills": _summarise(by_id, module.get("drills", [])),
        })
        payload["totalMinutes"] += module["minutes"]

    payload["parts"] = track.get("parts", [])

    # Pattern chips link into the course by tag. A key whose module is not in
    # this track is dropped rather than shipped, so a typo in the table above
    # costs a link and never produces one that goes nowhere.
    known = {module["id"] for module in payload["modules"]}
    payload["patternModules"] = {
        tag: module_id
        for tag, module_id in _normalise_tags(PATTERN_MODULES).items()
        if module_id in known
    }

    return payload


def _normalise_tags(table: Dict[str, str]) -> Dict[str, str]:
    return {tag.strip().lower(): module_id for tag, module_id in table.items()}


def principle_questions() -> List[tuple]:
    """Every (module_id, principle_heading, question_id) the course claims.

    The dataset check walks this against the catalogue, which is the only
    thing that catches a link to a question that was renamed or removed.
    """
    rows = []
    for module in load_track()["modules"]:
        for principle in module["principles"]:
            for question_id in principle.get("uses", []):
                rows.append((module["id"], principle["heading"], question_id))
    return rows
