#!/usr/bin/env python3
"""Fetch the published hints for our LeetCode questions.

LeetCode exposes a question's own hints through its public GraphQL endpoint.
They are written for the original problem, so they are raw material: the
review pass in `tools/build_hints.py` decides what we actually ship.

    python3 tools/fetch_hints.py            # writes tools/leetcode_hints.json

Nothing below runs at app start-up. The app is offline; the output of this
script is committed.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS = os.path.join(ROOT, "cbp", "data", "questions.json")
OUT = os.path.join(ROOT, "tools", "leetcode_hints.json")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
GRAPHQL = "https://leetcode.com/graphql"
QUERY = "query q($t:String!){question(titleSlug:$t){questionFrontendId title hints}}"

TAGS = re.compile(r"<[^>]+>")


def _post(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Referer": "https://leetcode.com/problemset/",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def slug_map() -> dict:
    request = urllib.request.Request(
        "https://leetcode.com/api/problems/all/", headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return {
        pair["stat"]["question_id"]: pair["stat"]["question__title_slug"]
        for pair in data["stat_status_pairs"]
    }


def clean(html: str) -> str:
    """Hints are HTML. Keep the code spans as backticks, drop the rest."""
    text = re.sub(r"<code>(.*?)</code>", lambda m: "`" + m.group(1) + "`", html)
    text = TAGS.sub("", text)
    for entity, char in (
        ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
        ("&#39;", "'"), ("&nbsp;", " "), ("&amp;", "&"),
    ):
        text = text.replace(entity, char)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    questions = json.load(open(QUESTIONS, encoding="utf-8"))["questions"]
    leetcode = [q for q in questions if q["source"] == "LeetCode"]
    slugs = slug_map()

    out: dict = {}
    if os.path.exists(OUT):
        out = json.load(open(OUT, encoding="utf-8"))

    for index, question in enumerate(leetcode, 1):
        qid = question["id"]
        slug = slugs.get(question.get("sourceId"))
        if not slug:
            print(f"[{index:>2}/{len(leetcode)}] {qid}: no slug", flush=True)
            continue
        if qid in out and out[qid].get("slug") == slug:
            print(f"[{index:>2}/{len(leetcode)}] {qid}: cached", flush=True)
            continue
        try:
            data = _post(GRAPHQL, {"query": QUERY, "variables": {"t": slug}})
            hints = (data.get("data") or {}).get("question", {}).get("hints") or []
        except Exception as exc:  # noqa: BLE001 - a scrape must not wedge
            print(f"[{index:>2}/{len(leetcode)}] {qid}: {exc}", flush=True)
            hints = []
        out[qid] = {
            "slug": slug,
            "sourceId": question.get("sourceId"),
            "title": question["title"],
            "hints": [clean(h) for h in hints if clean(h)],
        }
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(out, handle, indent=1, ensure_ascii=False, sort_keys=True)
        print(
            f"[{index:>2}/{len(leetcode)}] {qid}: {len(out[qid]['hints'])} hints",
            flush=True,
        )
        time.sleep(0.35)

    empty = [k for k, v in out.items() if not v["hints"]]
    print(f"wrote {OUT}: {len(out)} questions, {len(empty)} with no published hint")
    if empty:
        print("  " + " ".join(empty))
    return 0


if __name__ == "__main__":
    sys.exit(main())
