"""Hints, one short list per question.

Loaded from data/hints.json, which `tools/build_hints.py` writes from the
hand-written set in tools/hints.py. The build refuses to write the file while
any question is missing a hint, so at runtime every question has at least one
and no caller has to handle the empty case.

The file is small and read once per question request, next to the questions
file that is loaded the same way.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

HINTS_PATH = os.path.join(os.path.dirname(__file__), "data", "hints.json")


def load_hints() -> Dict[str, List[str]]:
    try:
        with open(HINTS_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        # The app is usable without hints; a missing file must not stop a
        # question from opening. tools/build_hints.py is what guarantees the
        # file is there in a real build.
        return {}


def hints_for(question_id: str) -> List[str]:
    return load_hints().get(question_id, [])
