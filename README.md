<div align="center">

<img src="docs/images/practice.png" alt="Praccy: a question, a timer and an editor" width="880">

# Praccy

**Get better at technical interviews by practising the way interviews actually go.**

You are given a question, a stopwatch, and a compiler. You write code. A grader
tells you, without hedging, whether it was right.

</div>

---

Most interview practice is dishonest in a quiet way. The question is already
solved when it arrives, so the only thing being practised is typing. The timer is
optional, so the pressure that makes interviews hard never arrives. And when you
get it wrong, you are told you got it wrong, not which test case caught you and
what it expected instead.

Praccy removes those three comforts.

![The verdict panel, showing expected against actual for every test case](docs/images/verdict.png)

That is the whole product, really. Above is a solution that finds the right
pair and returns it in the wrong order. It passes one case of three, and the
panel names the case, prints what it expected, prints what you returned, and
then tells you the three mistakes that produce exactly this failure. Not "wrong
answer". Not a score. The specific thing that went wrong.

## What you get

- **144 questions.** 66 easy, 56 medium, 22 hard. Seventy-two are shaped like
  Coderbyte and seventy-two are real LeetCode problems; 66 of them are the
  Grind 75, in that order.
- **Five languages, and the grader is strict about the output type.** C++,
  C#, Java, Rust and Python. Grading compares the exact value *and its type*,
  the way the real Coderbyte site does, because returning `[2, 7]` where a
  string was expected scores zero and pretending otherwise would be the app
  lying to you.
- **A stopwatch you cannot stop and do not want to.** It measures the question,
  not the attempt. Submitting a wrong answer does not stop it, because in the
  room there is no pause. It resets when you pass.
- **Hints, one at a time, on request.** Two per question. You have to admit you
  are stuck before you can read them.
- **A reference solution, but only if you ask for it.**
- **Progress that persists.** Which questions you have passed, how fast, and a
  streak.

## The course

Thirteen modules, about four and a half hours. One short module on reading a
question and on the bugs that survive review, then twelve on the patterns the
harder questions are built from.

![The course, with a code specimen you can step through line by line](docs/images/course.png)

It is written to be read a beat at a time rather than scrolled through. Each
principle gives you its claim, then the rest of the argument on request, so the
choice you make is "keep going" rather than "read all of this or none of it".

Where there is code, you can walk it line by line. The whole block stays
visible and one line is picked out, because recognising the shape of the finished
code is the skill, and reading it top to bottom only teaches you the syntax.

Every principle names the questions it applies to, and every section shows a ring
filled in by how many of those you have actually solved.

<details>
<summary>Screenshot of the light appearance</summary>

![The course in light mode](docs/images/course-light.png)

</details>

## Running it

Praccy is a local app. Nothing is uploaded, nothing is phoned home, and it works
with the network switched off.

- **macOS** — download `Praccy.app` from the [releases](../../releases) page,
  drag it to Applications, and open it. It bundles its own Python, so there is
  nothing to install.
- **Windows** — download `Praccy.exe` and run it. Windows 10 and 11 already
  contain the WebView2 runtime it needs.
- **Linux** — download the `.AppImage` and run it. It needs a recent
  `webkit2gtk`; that is what the app renders in.

Python ships with the app and is the only language guaranteed to work on a fresh
machine. The other four need a compiler you may or may not have; the app checks
on first run and tells you exactly what to install.

## How it is built

A local HTTP server, a browser view, and a Python engine that shells out to the
real toolchains — `clang++`, `rustc`, `javac`, `dotnet` — because a grader that
does not actually run your code is not a grader.

- `cbp/` is the whole application: the engine, the adapters, the HTTP server
  and the interface. Standard library only.
- `praccy.py` is the shell. One file, about a hundred lines, opening a native
  webview on all three operating systems.
- The two typefaces are bundled, so the interface looks the same on a machine
  that has never heard of any of them.
- No build step is required to run it from a clone: `python3 praccy.py`.

There is much more detail — the grading rules, the strictness rules, the course,
the packaging, and a good number of things that turned out to be harder than they
looked — in **[DEVELOPING.md](DEVELOPING.md)**.

## Licence

Private repository. All rights reserved.
