#!/usr/bin/env python3
"""Check the new course prose against the humanizer skill's watch lists.

Not a judge of style. It looks for the specific constructions the skill says
justify an edit on a single sighting: "not X but Y", staged openers, one-line
closers, em dashes, curly quotes, bold labels, and the stock AI vocabulary.
Reports file and line so a human can decide whether the hit is real.

Usage:  python3 tools/humanizer_check.py [module-id ...]
"""

from __future__ import annotations

import json
import os
import re
import sys

TRACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cbp", "data", "track.json",
)

# Each rule: (label, regex, note). Kept close to the skill's section numbers.
RULES = [
    ("§1 not-X-but-Y", re.compile(
        r"\b(?:not (?:just |only |merely )?\w+ but|is not \w+, (?:it'?s|it is)|"
        r"rather than \w+$)", re.I),
     "negative half names a claim nobody made"),
    ("§1b does-not-mean", re.compile(
        r"\bthis does not mean\b.{0,60}\bit means\b", re.I | re.S),
     "contrast split across two sentences"),
    ("§2 closer", re.compile(
        r"^(That is (?:the )?(?:real|whole) \w+\.|This (?:is|was) the (?:point|lesson)"
        r"|Read that again\.|Let that sink in\.)$", re.I),
     "one-sentence paragraph restating the one before"),
    ("§3 saying", re.compile(
        r"\b(?:at its core|what really matters|fundamentally|the deeper issue|"
        r"the real question is|the heart of the matter|the language of)\b", re.I),
     "ordinary point dressed as a hidden truth"),
    ("§4 staged opener", re.compile(
        r"(?:^|\n)\s*(?:Let's dive in|Let's explore|Let's break this down|"
        r"Here's what you need to know|Now let's look at|Without further ado|"
        r"Here's the thing|The thing is|Let's be honest|Real talk|Quick note|"
        r"Here's the)\b", re.I),
     "announces the point instead of making it"),
    ("§5 arguing with no one", re.compile(
        r"\b(?:This isn'?t (?:mainly |just )?about|I'?m not saying|To be clear|"
        r"Don'?t get me wrong|That is not to say|Some might say|One might be "
        r"tempted|A tempting approach would be|One obvious approach|"
        r"You might think)\b", re.I),
     "answers an objection raised nowhere else"),
    ("§6 forced triad", re.compile(
        r"\b(?:\w+, ){2}\w+ and \w+\b"),
     "three parallel items; check each is a distinct idea"),
    ("§8 dash", re.compile(r"[\u2014\u2013]|(?<!-)--(?!-)"),
     "em/en dash or spaced double hyphen; only allowed if a sample uses them"),
    ("§12 AI word", re.compile(
        r"\b(?:Additionally|delve|enduring|enhance|garner|intricate|intricacies|"
        r"landscape|meticulous(?:ly)?|pivotal|showcase|tapestry|testament|"
        r"underscore|vibrant|bolstered|deep dive)\b", re.I),
     "overused AI word"),
    ("§13 inflated", re.compile(
        r"\b(?:stands as a testament|pivotal moment|marks a (?:turning )?"
        r"(?:moment|shift)|setting the stage for|evolving landscape|"
        r"Despite these challenges|continues to thrive|Challenges and Legacy|"
        r"the future looks bright)\b", re.I),
     "ordinary detail said to mark a change"),
    ("§15 -ing rider", re.compile(
        r"\b\w+ing, (?:underscoring|highlighting|emphasizing|ensuring|"
        r"reflecting|symbolizing|showcasing)", re.I),
     "bolted onto a fact to sound deeper"),
    ("§16 sales", re.compile(
        r"\b(?:rich (?:heritage|tapestry|history)|profoundly|groundbreaking|"
        r"renowned|breathtaking|must-visit|stunning|nestled)\b", re.I),
     "reads like an advertisement"),
    ("§17 borrowed authority", re.compile(
        r"\b(?:experts (?:argue|believe|say)|observers have cited|"
        r"industry reports|several publications)\b", re.I),
     "an unnamed authority stands in for what was said"),
    ("§18 avoiding is", re.compile(
        r"\b(?:serves as|stands as|functions as|operates as|boasts|"
        r"maintains a)\b", re.I),
     "use is / are / has"),
    # This rule was written against bold used as decoration, and in its first
    # form it flagged every bold span in the file. The course now emphasises on
    # purpose: one phrase per principle, chosen in build_course.py's EMPHASIS
    # table and validated there, where a phrase that matches nothing fails the
    # build. So the rule targets the shape that is still a tell -- a span that
    # opens a line and stops at a colon or a dash, which is how a bulleted list
    # dresses up as a paragraph. The emphasis itself is counted at the end of
    # the report so it is accounted for rather than invisible.
    ("§19 bold label", re.compile(
        r"(?:^|\n)\s*\*\*[^*\n]{1,60}\*\*\s*(?::|[\u2013\u2014]|-\s)"),
     "bold used as a label rather than as emphasis"),
    ("§20 heading case", re.compile(r"^#+ .*\b(?:And|Or|The|Of|To|In|For|With)\b\s*$"),
     "title case in a heading"),
    ("§21 curly quote", re.compile(r"[\u2018\u2019\u201c\u201d]"),
     "curly quotes where the format uses straight"),
    ("§22 chatbot", re.compile(
        r"\b(?:I hope this helps|Of course!|Great question!|Let me know|"
        r"Would you like|Want me to)\b", re.I), "chat wrapper left in the text"),
    ("§23 disclaimer", re.compile(
        r"\b(?:as of \d{4}|up to my last training|not publicly available|"
        r"it is believed that|likely grew up)\b", re.I),
     "mentions the limits of the model's knowledge"),
    ("§25 about the doc", re.compile(
        r"\b(?:was added to replace|generated from|compiled from|"
        r"the table below|the figures below)\b", re.I),
     "describes the document instead of its subject"),
]


def main() -> int:
    wanted = set(sys.argv[1:])
    with open(TRACK_PATH) as fh:
        track = json.load(fh)["track"]

    modules = [m for m in track["modules"]
               if not wanted or m["id"] in wanted]

    hits = 0
    for module in modules:
        for principle in module["principles"]:
            fields = [("heading", principle["heading"]),
                      ("body", principle["body"]),
                      ("check", principle.get("check", "")),
                      ("subtitle", module["subtitle"])]
            for where, text in fields:
                for label, pattern, note in RULES:
                    for match in pattern.finditer(text):
                        # Code blocks in bodies legitimately contain punctuation
                        # that reads as prose, so a hit inside one is reported
                        # but marked, rather than hidden.
                        start = match.start()
                        line = text[:start].count("\n") + 1
                        hits += 1
                        print(f"{module['id']} / {principle['heading'][:44]!r}")
                        print(f"  {where}:{line}  {label}  -- {note}")
                        print(f"    {match.group(0)!r}")

    emphasised = sum(principle["body"].count("**") // 2
                     for module in modules for principle in module["principles"])
    print(f"\n{hits} hit(s) across {len(modules)} module(s). "
          f"{emphasised} inline emphasis span(s), chosen in build_course.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
