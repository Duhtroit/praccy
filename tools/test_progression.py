#!/usr/bin/env python3
"""Check the progression rules in cbp/web/progress.js.

That file is the one piece of the browser code with numbers in it that a user
will notice being wrong, so it gets tested here rather than by looking at it.
The rules are evaluated in a small JS context alongside the real file, so the
test cannot drift from what the browser runs.

Run:  python3 tools/test_progression.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_JS = os.path.join(ROOT, "cbp", "web", "progress.js")

PRELUDE = """\
const fs = require('fs');
const vm = require('vm');
// progress.js is loaded into a context of its own, and its `const` bindings
// stay there. The check body is run in that same context, because it cannot
// see them otherwise.
const context = vm.createContext({ console });
vm.runInContext(fs.readFileSync(%s, 'utf8'), context);
context.__result = vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), context);
""" % json.dumps(PROGRESS_JS)



def run_js(body: str):
    """Evaluate a snippet in a context that has progress.js loaded.

    The snippet is a function body, so it is wrapped in an IIFE and its return
    value is what comes back.
    """
    driver = PRELUDE + "\nconsole.log(JSON.stringify(context.__result));\n"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(driver)
        driver_path = fh.name
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write("(function () {\n" + body + "\n})()")
        body_path = fh.name
    try:
        proc = subprocess.run(["node", driver_path, body_path],
                              capture_output=True, text=True, timeout=60)
    finally:
        os.unlink(driver_path)
        os.unlink(body_path)
    if proc.returncode != 0:
        print(body, file=sys.stderr)
        raise SystemExit(f"node failed:\n{proc.stderr}")
    return json.loads(proc.stdout)


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  {detail}" if detail else ""))
    return ok


def load_questions() -> list:
    with open(os.path.join(ROOT, "cbp", "data", "questions.json")) as fh:
        return [{"id": q["id"], "tier": q["tier"], "source": q.get("source") or "Coderbyte"}
                for q in json.load(fh)["questions"]]


def main() -> int:
    if not os.path.exists(PROGRESS_JS):
        print(f"missing {PROGRESS_JS}")
        return 1

    checks = []

    # ── the level curve ───────────────────────────────────────────
    curve = run_js("""
    const rows = [];
    for (let xp = 0; xp <= 4000; xp += 7) {
      const p = levelProgress(xp);
      rows.push({ xp, level: p.level, ratio: p.ratio, span: p.span });
    }
    return rows;
    """)
    checks.append(check("level never goes down as xp rises",
                        all(a["level"] <= b["level"] for a, b in zip(curve, curve[1:]))))
    checks.append(check("ratio always in [0, 1)",
                        all(0 <= row["ratio"] < 1 for row in curve)))
    checks.append(check("every level span is positive",
                        all(row["span"] > 0 for row in curve)))
    checks.append(check("level 1 at 0 xp",
                        curve[0]["level"] == 1 and curve[0]["ratio"] == 0))
    # The curve is quadratic, so each level must need at least as much as the
    # one before it. A flat spot would mean the level-up animation fires for
    # no reason.
    first_span = {}
    for row in curve:
        first_span.setdefault(row["level"], row["span"])
    spans = [first_span[level] for level in sorted(first_span)]
    checks.append(check("each level needs at least as much as the last",
                        all(b >= a for a, b in zip(spans, spans[1:])),
                        f"spans {spans[:5]}..."))

    # ── the points rules ──────────────────────────────────────────
    points = run_js("""
    return ['easy', 'medium', 'hard'].map(tier => ({
      tier,
      first: pointsForSolve(tier, false, false),
      firstBest: pointsForSolve(tier, false, true),
      repeat: pointsForSolve(tier, true, false),
    }));
    """)
    by_tier = {row["tier"]: row for row in points}
    checks.append(check("a hard question beats a medium one on points",
                        by_tier["hard"]["first"] > by_tier["medium"]["first"]))
    checks.append(check("a medium question beats an easy one on points",
                        by_tier["medium"]["first"] > by_tier["easy"]["first"]))
    checks.append(check("a repeat is worth less than a first solve",
                        all(row["repeat"] < row["first"] for row in points)))
    checks.append(check("a personal best pays a bonus",
                        all(row["firstBest"] > row["first"] for row in points)))
    checks.append(check("no question is worth zero",
                        all(row["first"] > 0 for row in points)))

    # ── the achievement definitions ───────────────────────────────
    ach = run_js("""
    return ACHIEVEMENTS.map(a => ({ id: a.id, name: a.name, hint: a.hint,
                                    hasTest: typeof a.test === 'function' }));
    """)
    ids = [a["id"] for a in ach]
    checks.append(check("achievement ids are unique", len(ids) == len(set(ids))))
    checks.append(check("every achievement has a test", all(a["hasTest"] for a in ach)))
    checks.append(check("every achievement has a name and a hint",
                        all(a["name"] and a["hint"] for a in ach)))
    checks.append(check("there is a reasonable number of them", 8 <= len(ach) <= 25,
                        f"{len(ach)}"))

    # ── reachability ──────────────────────────────────────────────
    # Solving the whole catalogue must earn every achievement, and must not
    # award any of them twice. An achievement whose test can never be true is
    # invisible dead weight in the sheet.
    questions = load_questions()
    reach = run_js(f"""
    const questions = {json.dumps(questions)};
    const state = {{ solved: new Set(), best: {{}}, days: [], xp: 0, achievements: [] }};
    const awarded = [];
    questions.forEach((q, i) => {{
      state.solved.add(q.id);
      state.best[q.id] = 30;
      if (state.days.length < 10) state.days.push('day-' + state.days.length);
      // The points are added before the trophies are recomputed, which is the
      // order the app uses. The other order makes every milestone a solve late.
      const reward = rewardForSolve(state, questions, q, {{ wasSolved: false, isNewBest: true }});
      state.xp += reward.points;
      const after = rewardForSolve(state, questions, q, {{ wasSolved: false, isNewBest: true }});
      const fresh = after.unlocked.filter(a => !state.achievements.includes(a.id));
      state.achievements.push(...fresh.map(a => a.id));
      awarded.push(...fresh.map(a => a.id));
    }});
    return {{
      total: ACHIEVEMENTS.length,
      earned: state.achievements.length,
      missing: ACHIEVEMENTS.filter(a => !state.achievements.includes(a.id)).map(a => a.id),
      duplicates: awarded.filter((id, i) => awarded.indexOf(id) !== i),
      xp: state.xp,
      level: levelForXp(state.xp),
    }};
    """)
    checks.append(check("solving everything earns every achievement",
                        reach["missing"] == [], f"missing {reach['missing']}"))
    checks.append(check("no achievement is awarded twice",
                        reach["duplicates"] == [], f"{reach['duplicates']}"))
    checks.append(check("finishing the catalogue is a high level",
                        reach["level"] >= 12, f"level {reach['level']} at {reach['xp']} xp"))

    # The level trophies exist because XP used to move a number and nothing
    # else, so they have to land on the solve that crossed the line rather than
    # on the one after it. That is the whole difference the ordering buys.
    crossing = run_js(f"""
    const questions = {json.dumps(questions)};
    const state = {{ solved: new Set(), best: {{}}, days: [], xp: 0, achievements: [] }};
    let crossed = false, awardedInTime = false;
    questions.forEach((q) => {{
      if (crossed) return;
      const reward = rewardForSolve(state, questions, q, {{ wasSolved: false, isNewBest: false }});
      state.solved.add(q.id);
      state.xp += reward.points;
      const after = rewardForSolve(state, questions, q, {{ wasSolved: false, isNewBest: false }});
      const fresh = after.unlocked.filter(a => !state.achievements.includes(a.id));
      state.achievements.push(...fresh.map(a => a.id));
      if (levelForXp(state.xp) >= 3) {{
        crossed = true;
        awardedInTime = state.achievements.includes('level-3');
      }}
    }});
    return {{ crossed, awardedInTime }};
    """)
    checks.append(check("a level trophy lands on the solve that crossed the line",
                        crossing["crossed"] and crossing["awardedInTime"], str(crossing)))
    checks.append(check("the account has trophies tied to the points",
                        any(a["id"].startswith("level-") for a in ach),
                        str([a["id"] for a in ach])))

    # A single easy solve must not unlock half the list.
    first = run_js(f"""
    const questions = {json.dumps(questions)};
    const state = {{ solved: new Set(), best: {{}}, days: [], xp: 0, achievements: [] }};
    const q = questions.find(x => x.tier === 'easy');
    state.solved.add(q.id); state.best[q.id] = 20; state.days.push('d0');
    const after = rewardForSolve(state, questions, q, {{ wasSolved: false, isNewBest: true }});
    return {{ points: after.points, unlocked: after.unlocked.map(a => a.id) }};
    """)
    checks.append(check("one easy solve is a modest amount of points",
                        0 < first["points"] <= 20, f"{first['points']} xp"))
    checks.append(check("one solve does not unlock everything",
                        len(first["unlocked"]) <= 2, f"{first['unlocked']}"))

    passed = sum(1 for ok in checks if ok)
    print(f"\n{passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
