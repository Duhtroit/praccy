"""End-to-end test of the HTTP API, as the browser uses it.

Exercises every language, the type-mismatch diagnosis, and the error paths.
The server is started in-process on a spare port, so no setup is needed:

    python3 test_api.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from cbp.adapters import LANGUAGES
from cbp.engine import load_questions
from tools.build_sounds import BUILDERS as SOUND_BUILDERS
from cbp.hints import hints_for
from cbp.server import Handler
from cbp.track import track_payload

# The length ceiling for a hint lives with the hint set, so the test and the
# build cannot drift apart on what "too long to be a hint" means.
from tools.build_hints import MAX_LENGTH as HINT_MAX

# The pattern vocabulary and its module links, so this file checks the shipped
# catalogue against the same table the builders use.
from tools.patterns import MODULES as PATTERN_LINKS
from tools.patterns import PATTERNS as PATTERN_VOCAB

failures = []


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()
BASE = f"http://127.0.0.1:{PORT}"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.loads(r.read().decode())


def post(path, payload):
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        # Error responses carry a JSON body; the client shows that message.
        return json.loads(exc.read().decode())


def expect(name, condition, detail=""):
    if condition:
        print(f"  ok    {name}")
    else:
        failures.append((name, detail))
        print(f"  FAIL  {name}  {detail}")


def start_server():
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


httpd = start_server()
print(f"  (test server on {BASE})\n")

print("Catalog")
print("=" * 64)
catalogue = get("/api/questions")
expect("every registered language is advertised",
       catalogue["languages"] == list(LANGUAGES),
       str(catalogue["languages"]))
expect("questions listed", len(catalogue["questions"]) > 0, str(len(catalogue["questions"])))
print()

print("Reference solutions through the API (the browser's real path)")
print("=" * 64)
local = {q["id"]: q for q in json.load(open("cbp/data/questions.json"))["questions"]}

for qid, question in local.items():
    for language in catalogue["languages"]:
        code = question["solution"].get(language)
        if not code:
            continue
        started = time.monotonic()
        result = post("/api/run", {
            "questionId": qid, "language": language, "code": code,
        })
        took = time.monotonic() - started
        detail = ""
        if result.get("error"):
            detail = f"{result['error']['kind']}: {result['error']['message'][:90]}"
        expect(f"{qid} [{language}] passes", result["ok"], detail)

print()
print("The strictness diagnosis survives the round trip")
print("=" * 64)

# Returning a boolean where the contract wants the string "true".
result = post("/api/run", {
    "questionId": "check-nums",
    "language": "python",
    "code": "def CheckNums(arr):\n    return all(n > 0 for n in arr)",
})
expect("bool answer rejected for a string contract", not result["ok"])
first = result["cases"][0]
expect("actual shown as 'true', not 'True'", first["actual"] == "true", str(first["actual"]))
expect("actualType is bool", first["actualType"] == "bool", str(first["actualType"]))
expect("expectedType is string", first["expectedType"] == "string", str(first["expectedType"]))
expect("kind classified as a type error", first.get("kind") == "type", str(first.get("kind")))
expect("advice mentions the string requirement",
       "string" in (first.get("advice") or "").lower(), str(first.get("advice")))
expect("a lesson is attached", bool(result.get("lesson")))

# Wrong value: the diff should point at the first difference.
result = post("/api/run", {
    "questionId": "vowel-count",
    "language": "python",
    "code": 'def VowelCount(s):\n    v="aeiouAEIOU"\n    return sum(1 for c in s if c in v) - 1',
})
expect("off-by-one rejected", not result["ok"])
expect("value error, not type error", result["cases"][0].get("kind") == "value",
       str(result["cases"][0].get("kind")))
expect("numeric gap explained", "Off by 1" in (result["cases"][0].get("detail") or ""),
       str(result["cases"][0].get("detail")))

print()
print("Error paths")
print("=" * 64)

result = post("/api/run", {
    "questionId": "first-reverse",
    "language": "python",
    "code": "def FirstReverse(s):\n    return s[::-1]\nundefined_name()",
})
expect("runtime crash reported", result["error"] and result["error"]["kind"] == "runtime",
       str(result.get("error")))
expect("no temp paths leak into the message",
       "cbp_python_" not in result["error"]["message"], result["error"]["message"][:80])

result = post("/api/run", {
    "questionId": "first-reverse",
    "language": "cpp",
    "code": "string FirstReverse(string s) { this is not c++ }",
})
expect("compile error reported", result["error"] and result["error"]["kind"] == "compile",
       str(result.get("error")))

result = post("/api/run", {
    "questionId": "no-such-question", "language": "python", "code": "def x(): pass",
})
expect("unknown question rejected",
       "unknown question" in str(result.get("error")), str(result.get("error")))

result = post("/api/run", {
    "questionId": "first-reverse", "language": "cobol", "code": "x",
})
expect("unsupported language rejected", result.get("error", "").startswith("unsupported"),
       str(result.get("error")))

print()
print("Question content")
print("=" * 64)

# Hints and pattern links are content, and content rots: a question that loses
# its hint, or a tag that points at a module id which was renamed, both fail
# silently in the UI -- one shows nothing, the other shows a chip that looks
# live and does nothing. Checked across the whole catalogue rather than on one
# sample, because the failure mode is a handful of rows.
questions = load_questions()

unhinted = [q["id"] for q in questions if not hints_for(q["id"])]
expect("every question has at least one hint", not unhinted,
       f"{len(unhinted)}: {' '.join(unhinted[:6])}")

lengths = [(len(hint), q["id"]) for q in questions for hint in hints_for(q["id"])]
longest, longest_id = max(lengths) if lengths else (0, "")
expect("no hint is long enough to be an answer", longest <= HINT_MAX,
       f"{longest_id} is {longest} characters")

thin = [q["id"] for q in questions if len(hints_for(q["id"])) < 2]
expect("every question has more than one hint", not thin,
       f"{len(thin)}: {' '.join(thin[:6])}")

track = track_payload(questions)
module_ids = {m["id"] for m in track["modules"]}
broken = [f"{tag}->{mid}" for tag, mid in track["patternModules"].items()
          if mid not in module_ids]
expect("every pattern links at a real module", not broken, " ".join(broken))
expect("the pattern table is not empty", len(track["patternModules"]) >= 10,
       str(len(track["patternModules"])))

# The course bodies carry two inline markers, and `proseMarkup` in
# cbp/web/app.js is what reads them: a backtick pair is a code fragment and a
# double-asterisk pair is emphasis. Neither is escaped, because both are
# substituted after the text is escaped, so an unclosed marker does not throw
# and does not look like an error -- it renders as a literal asterisk in the
# middle of a sentence, which is exactly the sort of thing that gets shipped.
# build_course.py is what should have caught it; this is the backstop for a
# track.json that was written some other way.
principles = [p for m in track["modules"] for p in m["principles"]]
unclosed = [p["heading"] for p in principles
            if p["body"].count("**") % 2 or p["body"].count("`") % 2]
expect("every markup marker in the course is closed", not unclosed,
       " ".join(unclosed))
emphasised = sum(1 for p in principles if "**" in p["body"])
expect("most principles emphasise the phrase they are about",
       emphasised >= 30, f"{emphasised} of {len(principles)}")

detail = get("/api/question/g-longest-unique-substring")
expect("hints travel with the question", len(detail.get("hints") or []) >= 2,
       str(detail.get("hints")))
expect("the recipe of the question is unchanged",
       detail["functionName"] == "LengthOfLongestSubstring", detail["functionName"])

print()
print("Patterns")
print("=" * 64)

# The Patterns row shows a technique, and it is a closed vocabulary rather than
# free text -- that is the whole point of the rewrite. Every failure below is
# invisible in the browser: a question with no pattern shows an empty row, a
# pattern outside the vocabulary renders as a chip nobody can act on, and a
# course pattern with no module link is a lesson you cannot reach.
patterns_by_question = {
    q["id"]: list(q.get("patterns") or []) for q in catalogue["questions"]
}
unpatterned = sorted(qid for qid, names in patterns_by_question.items() if not names)
expect("every question names at least one pattern", not unpatterned,
       f"{len(unpatterned)}: {' '.join(unpatterned[:6])}")

used = {name for names in patterns_by_question.values() for name in names}
unknown = sorted(used - set(PATTERN_VOCAB))
expect("every assigned pattern is in the vocabulary", not unknown, " ".join(unknown))
expect("no pattern in the vocabulary goes unused",
       not (set(PATTERN_VOCAB) - used), " ".join(sorted(set(PATTERN_VOCAB) - used)))

retired = {"algorithm", "math fundamentals", "string manipulation", "searching"}
expect("the retired topic words are not shown as patterns",
       not (used & retired), " ".join(sorted(used & retired)))

expect("every pattern the course teaches has a module link",
       set(PATTERN_LINKS) <= set(track["patternModules"]),
       " ".join(sorted(set(PATTERN_LINKS) - set(track["patternModules"]))))

detail = get("/api/question/ab-check")
expect("patterns travel with the question",
       detail.get("patterns") == ["frequency counting"], str(detail.get("patterns")))

print()
print("Sound")
print("=" * 64)

# The one failure mode a sound test cannot hear is a file that is not there:
# a wrong name in sound.js plays nothing and looks exactly like sound being
# turned off. So the names in the module, the files on disk and the list the
# generator produces are all checked against each other.
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cbp", "web")
SOUND_DIR = os.path.join(WEB, "sounds")
with open(os.path.join(WEB, "sound.js"), encoding="utf-8") as handle:
    sound_source = handle.read()

named = sorted(set(re.findall(r'"([a-z][a-z-]*)\.wav"', sound_source)))
expect("the sound module names a full set of samples", len(named) >= 8, str(named))

generated = set(SOUND_BUILDERS)
expect("every named sample has a generator", set(named) <= generated,
       " ".join(sorted(set(named) - generated)))
expect("every generator is named in the module", generated <= set(named),
       " ".join(sorted(generated - set(named))))

missing, malformed = [], []
for name in named:
    path = os.path.join(SOUND_DIR, name + ".wav")
    if not os.path.isfile(path):
        missing.append(name)
        continue
    with open(path, "rb") as handle:
        head = handle.read(12)
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        malformed.append(name)
expect("every named sample exists on disk", not missing, " ".join(missing))
expect("every sample is a real wav file", not malformed, " ".join(malformed))

extra = sorted(set(os.listdir(SOUND_DIR)) - {name + ".wav" for name in named})
expect("nothing unplayed is left in the sound directory", not extra, " ".join(extra))

# Both keyboards are fetched, not just the default one: a pack whose files are
# named wrong fails the same silent way as a typo in the module, and the only
# way to catch it here is to ask for the pair.
for name in ("key-creamy", "key-clicky"):
    with urllib.request.urlopen(BASE + f"/sounds/{name}.wav", timeout=30) as response:
        served = response.read()
        ctype = response.headers.get("Content-Type")
    expect(f"{name} is served as audio, not as an opaque download",
           ctype == "audio/wav", str(ctype))
    expect(f"{name} is not truncated", len(served) > 1000, str(len(served)))

print()
print("Sound persistence")
print("=" * 64)

# The bug this guards: the audio context was created in exactly one place, and
# that place was only reachable by flipping the master switch from off to on.
# So a launch that restored `on: true` came up with the right setting and no
# AudioContext at all -- every `play` returned false at its `if (!context)`
# guard, and toggling the switch fixed it. That is exactly how it presented,
# as a preference that would not save, when the preference was saved correctly
# the whole time and nothing was reading it back into a live context.
#
# So the check is not that the value round-trips through the API -- the
# Settings section already proves that -- but that a restored `on: true` has a
# path to an audio context without a toggle.
with open(os.path.join(WEB, "sound.js"), encoding="utf-8") as handle:
    sound_js = handle.read()

expect("a restored on:true arms the audio context",
       "armUnlock" in sound_js and "disarmUnlock" in sound_js,
       "no arm/disarm of the context on reload")
expect("reloading the settings arms or disarms the context",
       re.search(r"function reload\s*\(\)\s*\{[^}]*armUnlock", sound_js, re.S)
       is not None,
       "reload does not touch the armed listener")
expect("changing the switch keeps the armed listener in step",
       re.search(r"function update\s*\([^)]*\)\s*\{.*armUnlock", sound_js, re.S)
       is not None,
       "update does not touch the armed listener")
# `unlock` used to be exported and never called. An exported function with no
# call site is the exact shape of that bug, so it is worth naming.
call_sites = len(re.findall(r"unlock\(\)", sound_js))
expect("unlock is actually called from more than its own definition",
       call_sites >= 3, f"{call_sites} references")

# The first sound of a session used to be dropped, because decoding had not
# finished. It is now deferred, but only once: a general queue would turn a
# burst of typing into a delayed volley when the samples landed.
expect("a not-yet-decoded sample is deferred rather than dropped",
       re.search(r"if\s*\(!buffer\)\s*\{[^}]*loadBuffer", sound_js, re.S) is not None)
expect("the deferral is a latch, not a queue",
       re.search(r"if\s*\(pending\)\s*\{", sound_js) is not None,
       "no latch, so a burst would queue up and arrive late")

print()
print("Theme")
print("=" * 64)

# The two appearances are one block of tokens each, and CSS fails silently: a
# token missing from the light block is not an error, it is an element that
# keeps the dark value, and a token missing from the dark block is an element
# that is unstyled. So the two blocks are diffed against each other here.
STYLE_PATH = os.path.join(WEB, "style.css")
with open(STYLE_PATH, encoding="utf-8") as handle:
    style = handle.read()

# An unterminated block comment swallows every rule after it, and a CSS parser
# reports nothing: the reduced-motion block sat commented out for the whole life
# of the file without a line of this test noticing. Cheap to check, and the
# failure it prevents is invisible everywhere else.
SHARED = {"--display", "--mono", "--sans", "--quick", "--radius", "--radius-lg",
          "--radius-pill", "--radius-sm", "--sidebar-w", "--spring", "--topbar-h"}

opens, closed = style.count("/*"), style.count("*/")
expect("the stylesheet has no unterminated comment",
       opens == closed, f"{opens} open, {closed} close")

dark_block = style.split(":root {", 1)[1].split("\n}", 1)[0]
light_at = style.find(':root[data-theme="light"]')
expect("the light appearance is a block of its own", light_at > 0)
light_block = style[light_at:].split("\n}", 1)[0]


def tokens(block):
    return set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", block, re.M))


dark_tokens, light_tokens = tokens(dark_block), tokens(light_block)
# Tokens the two appearances share by design (fonts, radii, easing curves and
# the layout metrics) are only in the dark block, which is also the default, so
# the check that matters is the other direction: a token defined for light and
# not for dark leaves that element unstyled in the appearance most people run.
expect("no token is defined for light and not for dark",
       light_tokens <= dark_tokens, " ".join(sorted(light_tokens - dark_tokens)))

# And the colour tokens have to actually differ. Identical values mean one
# block was pasted over the other, which renders as a theme that only half
# works and reads as a bug nobody can reproduce.


def value_of(block, name):
    match = re.search(r"^\s*" + re.escape(name) + r"\s*:\s*([^;]+);", block, re.M)
    return match.group(1).strip() if match else None


same = sorted(
    name for name in (dark_tokens & light_tokens) - SHARED
    if value_of(dark_block, name) == value_of(light_block, name)
)
expect("the two appearances are not the same colours twice",
       not same, " ".join(same))

# The appearance is chosen on an attribute, so nothing else may depend on the
# system setting for colour. A media query on prefers-color-scheme would undo
# the choice on any Mac whose Appearance is set the other way.
scheme_queries = re.findall(
    r"@media[^{]*prefers-color-scheme[^{]*", style)
expect("no rule keys colour off the system appearance",
       not scheme_queries, " ".join(scheme_queries[:2]))

print()
print("Type and offline")
print("=" * 64)

# The app has to look the same on a machine that has never heard of
# ui-rounded, and it has to do that with no network. Both are checked here
# rather than trusted, because each fails silently: a system-only font stack
# renders perfectly and is simply the wrong typeface on Windows and Linux, and
# a CDN-hosted font looks right right up until the machine is offline.
FONT_DIR = os.path.join(WEB, "fonts")
font_files = sorted(os.listdir(FONT_DIR)) if os.path.isdir(FONT_DIR) else []
expect("the typefaces are bundled, not fetched", len(font_files) > 0, str(font_files))

for family in ("Praccy Sans", "Praccy Mono"):
    expect(f"{family} is declared with a local source",
           re.search(r'@font-face\s*{[^}]*font-family:\s*"' + family + r'"[^}]*url\("fonts/',
                     style, re.S) is not None)

# A woff2 served as application/octet-stream is discarded by the browser, which
# presents as a missing font rather than as a MIME error, so the header itself
# is the thing worth asserting.
for name in font_files:
    if not name.endswith((".woff2", ".woff")):
        continue
    request = urllib.request.Request(f"{BASE}/fonts/{name}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        ctype = response.headers.get("Content-Type")
    expect(f"{name} is served as a font",
           ctype in ("font/woff2", "font/woff"), str(ctype))
    expect(f"{name} is not empty", len(body) > 20000, f"{len(body)} bytes")

# Nothing in the shipped UI may reach off the machine. The two XML namespaces
# below are identifiers, not fetches, so they are the only allowed matches.
offline_risk = []
for name in sorted(os.listdir(WEB)):
    if not name.endswith((".html", ".css", ".js")):
        continue
    with open(os.path.join(WEB, name), encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            for match in re.findall(r"https?://[^\"'\s)]+", line):
                if "127.0.0.1" in match or "localhost" in match:
                    continue
                if "www.w3.org" in match:
                    continue
                offline_risk.append(f"{name}:{number} {match}")
expect("the UI never reaches the network", not offline_risk,
       " | ".join(offline_risk[:3]))

# The old Apple-only stack is what made the readings look right on a Mac and
# ordinary everywhere else, so it must not come back. Checked against the token
# values rather than the whole file, because the comments discuss the faces they
# replaced by name, and a test that cannot tell a mention from a declaration
# gets either ignored or made vague.
code_only = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
type_stacks = re.findall(r"--(?:sans|display|mono)\s*:\s*([^;]+);", code_only)
expect("the type stacks name no Apple-only face",
       type_stacks
       and not any("ui-rounded" in s or "SF Pro Rounded" in s for s in type_stacks),
       " ".join(type_stacks))
expect("every type stack falls back to a face every platform has",
       all(re.search(r"(sans-serif|monospace)\s*$", s.strip()) for s in type_stacks),
       " ".join(type_stacks))

print()
print("Course reading")
print("=" * 64)

# The course arrived as a wall: every principle rendered its whole argument at
# once, so the reader's only choice was all of it or none. The beats and the
# walkthrough are what make it a lesson, and both are checked as present in
# the renderer so a refactor cannot quietly turn the course back into prose.
with open(os.path.join(WEB, "app.js"), encoding="utf-8") as handle:
    app_js = handle.read()
for symbol, why in (("principleBeats", "the beats are never produced"),
                    ("renderPrinciple", "principles render as a wall again"),
                    ("stepPrinciple", "the reveal control is inert"),
                    ("walkthroughMarkup", "specimens are not walkable"),
                    ("setWalkStep", "walkthrough lines cannot be picked")):
    expect(f"{why} is guarded", symbol in app_js)

track = get("/api/track")
all_principles = [p for m in track["modules"] for p in m["principles"]]
expect("every principle has something to reveal",
       all(len(p["body"].split("\n\n")) >= 2 for p in all_principles),
       f"{sum(1 for p in all_principles if len(p['body'].split(chr(10) * 2)) < 2)} flat")

print()
print("Settings persistence")
print("=" * 64)

# Preferences live in a file rather than in the browser, because the port is
# ephemeral and localStorage is scoped to an origin that changes every launch.
# The check runs against a temporary directory so it never touches the real one.
state_dir = tempfile.mkdtemp(prefix="praccy-settings-")
os.environ["PRACCY_STATE_DIR"] = state_dir
try:
    written = post("/api/settings", {"cbp.sound.v1": '{"on":true}', "cbp.lang": "rust"})
    expect("settings are written",
           written["settings"].get("cbp.lang") == "rust", str(written))
    merged = post("/api/settings", {"cbp.examples.hidden": "1"})
    expect("a later write merges instead of replacing",
           merged["settings"].get("cbp.lang") == "rust"
           and merged["settings"].get("cbp.examples.hidden") == "1", str(merged))
    read_back = get("/api/settings")["settings"]
    expect("settings survive a fresh read",
           read_back.get("cbp.sound.v1") == '{"on":true}'
           and read_back.get("cbp.lang") == "rust", str(read_back))
finally:
    os.environ.pop("PRACCY_STATE_DIR", None)
    shutil.rmtree(state_dir, ignore_errors=True)

print()
print("=" * 64)
httpd.shutdown()
if failures:
    print(f"{len(failures)} FAILURE(S)")
    for name, detail in failures:
        print(f"  {name}: {detail}")
    sys.exit(1)
print("All API tests passed. The browser path is trustworthy.")
