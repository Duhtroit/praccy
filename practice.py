#!/usr/bin/env python3
"""Praccy -- local practice, five languages, strict output types.

Usage:
  python3 practice.py                    interactive menu
  python3 practice.py --list             show the question catalogue
  python3 practice.py --tier medium      practise a tier
  python3 practice.py --tag "string manipulation"
  python3 practice.py --lang java        practise in a specific language
  python3 practice.py --count 8          how many questions
"""

from __future__ import annotations

import argparse
import random
import sys

from cbp.adapters import LANGUAGES
from cbp.engine import all_tags, load_questions
from cbp.session import pick_questions, run_session

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
YELLOW = "\033[33m"


def list_questions(questions):
    print(f"{BOLD}Praccy -- {len(questions)} questions{RESET}\n")
    current_tier = None
    for q in questions:
        if q["tier"] != current_tier:
            current_tier = q["tier"]
            print(f"\n{BOLD}{current_tier.upper()}{RESET}")
        flag = "" if q.get("verified", True) else f" {YELLOW}[unverified]{RESET}"
        poly = f" {DIM}(polymorphic){RESET}" if q.get("polymorphic") else ""
        print(f"  {q['title']:24s} {DIM}{', '.join(q['tags'])}{RESET}{poly}{flag}")
    print()
    print(f"{DIM}topics: {', '.join(all_tags(questions))}{RESET}")


def choose_language(preferred=None):
    if preferred:
        return preferred
    print(f"  {DIM}languages: {', '.join(LANGUAGES)}{RESET}")
    while True:
        choice = input("  language > ").strip().lower()
        if choice in LANGUAGES:
            return choice
        if choice in ("", "1"):
            return "python"
        print(f"  {YELLOW}pick one of: {', '.join(LANGUAGES)}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Praccy, local practice")
    parser.add_argument("--tier", choices=["easy", "medium", "hard"])
    parser.add_argument("--tag")
    parser.add_argument("--lang", choices=LANGUAGES)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--list", action="store_true", dest="do_list")
    parser.add_argument("--track", action="store_true",
                        help="read the course (principles, links, drills)")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    questions = load_questions()
    if args.do_list:
        list_questions(questions)
        return 0

    if args.track:
        from cbp.track import modules, total_minutes, drill_questions, load_track

        all_modules = modules()
        by_id = {q["id"]: q for q in questions}
        track = load_track()
        print()
        print(f"{BOLD}{track['title']}{RESET}  "
              f"{DIM}{len(all_modules)} modules, {total_minutes()} min{RESET}")

        part_titles = {p["id"]: p["title"] for p in track.get("parts", [])}
        current_part = None
        for module in all_modules:
            part = module.get("part")
            if part != current_part:
                current_part = part
                part_modules = [m for m in all_modules if m.get("part") == part]
                print()
                print(f"{BOLD}{part_titles.get(part, part).upper()}{RESET}  "
                      f"{DIM}{len(part_modules)} modules, "
                      f"{sum(m['minutes'] for m in part_modules)} min{RESET}")

            drills = drill_questions(module, questions)
            print()
            print(f"  {BOLD}{module['title']}{RESET}  {DIM}{module['minutes']} min{RESET}")
            print(f"  {DIM}{module['subtitle']}{RESET}")
            for principle in module["principles"]:
                print()
                print(f"    {BOLD}{principle['heading']}{RESET}")
                for line in principle["body"].splitlines():
                    print(f"    {line}")
                if principle.get("check"):
                    print(f"    {YELLOW}-> {principle['check']}{RESET}")
                used = [by_id[q] for q in principle.get("uses", []) if q in by_id]
                if used:
                    print(f"    {DIM}used by: "
                          f"{', '.join(d['title'] for d in used)}{RESET}")
            if drills:
                print()
                print(f"    {DIM}drills: "
                      f"{', '.join(d['title'] for d in drills)}{RESET}")
        print()
        return 0

    if args.seed is not None:
        random.seed(args.seed)

    if not sys.stdin.isatty():
        print("This is an interactive tool; run it from a terminal.")
        return 1

    print()
    print(f"{BOLD}Praccy{RESET}")
    print(f"  {DIM}The clock runs per question: it starts when the question opens{RESET}")
    print(f"  {DIM}and stops when you submit. It never fails you for being slow.{RESET}")
    language = choose_language(args.lang)

    picked = pick_questions(questions, args.tier, args.tag, args.count)
    if not picked:
        print(f"\n  {YELLOW}no questions match that filter.{RESET}")
        return 1

    run_session(picked, language)
    return 0


if __name__ == "__main__":
    sys.exit(main())
