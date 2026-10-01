"""Per-question lessons and progressive hints.

A lesson is shown only when it is needed: a wrong type teaches a type rule, a
wrong value teaches an algorithm idea.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .forensics import failure_kind

# Lessons keyed by failure kind, with {fn} substituted for the function name.
TYPE_LESSONS = {
    "type": """RETURN TYPES ARE THE TRAP

Coderbyte compares the exact value AND its type. Returning the boolean
False when the question asked for the string "false" is scored wrong even
though your logic is perfect.

  expected  "false"   (string)   <- quotes matter
  you       False     (bool)

Rule of thumb: if the prompt says 'return the string true/false', return a
string. If it says 'return true or false' with no quotes, a boolean is fine.
When in doubt, the sample cases in the question text show the real contract.""",

    "value": """READ THE SAMPLES, THEN THE WORDS

The logic ran without crashing but produced the wrong answer. Common causes:

  * an off-by-one in a range (<= vs <) -- check whether the boundary counts
  * updating a variable only inside the wrong branch
  * returning on the first match instead of the best match
  * a tie-break rule you missed ("return the first one" / "do not count y")

Rewrite the sentence in the prompt as a numbered recipe and follow it exactly.""",

    "no_output": """NOTHING CAME BACK

Your function ran but no value reached the harness.

  * you forgot a return statement on every path
  * you printed instead of returned
  * the function name does not match the one the question specifies

Every branch must return a value. If the input can be empty or a single
element, handle it explicitly.""",

    "compile": """IT DID NOT COMPILE

A compile error means the answer never ran, so there is nothing to judge yet.

  * check the return type matches the contract
  * in C++/C#/Java you must declare the return type before the function name
  * check brackets, semicolons and matching braces
  * if you use a library, make sure it is imported at the top""",

    "runtime": """IT CRASHED

The code started and then threw or aborted.

  * an index out of range -- is the array guaranteed non-empty?
  * division by zero
  * a null/None reference
  * an infinite loop that hit the time limit

Print intermediate values to find which line dies.""",
}


def lesson_for(evaluation: dict, question: dict) -> Optional[str]:
    """Return a lesson matching why the attempt failed, or None if it passed."""
    kind = failure_kind(evaluation)
    if kind is None:
        return None
    template = TYPE_LESSONS.get(kind)
    if template is None:
        return None
    return template.replace("{fn}", question.get("functionName", "the function"))


def question_note(question: dict) -> str:
    """A short, always-relevant warning attached to a question."""
    if question.get("polymorphic"):
        return question.get("polymorphicNote", "")
    expected = question["cases"][0]["expectedType"]
    if expected == "string":
        return f'This question returns a STRING, not a number or a boolean.'
    return ""
