# Praccy

A local macOS app for practising interview questions in **C++, C#, Java, Rust
or Python**, with the output-type strictness the real Coderbyte site applies,
plus a course on the principles that make any question solvable.

- **144 questions** (66 easy, 56 medium, 22 hard), all with reference solutions
  in five languages. 72 are Coderbyte-shaped and 72 are real LeetCode problems,
  and 66 of them are the Grind 75, in the order the list puts them in.
- **A course** — 13 modules, 43 principles, ~266 min of reading, and the view
  the app opens on. One short module on reading a question, then twelve on the
  patterns the harder questions are built from. Every principle links to the
  questions that use it, and every section shows a ring filled by how many of
  those questions you have solved.

## The Mac app

```bash
python3 tools/build_app.py          # build, verify, install to /Applications
open /Applications/Praccy.app
```

A window, a Dock icon and a menu bar around the same web UI the browser build
serves, so there is one implementation of the product rather than two.

**Python ships inside it.** The bundle carries its own trimmed CPython 3.12, so
the app needs nothing installed to run. The other four are compilers, and
several gigabytes of JDK, .NET and Rust cannot be packed: those stay external.

**On first open, missing toolchains are reported, not installed.** A panel
lists each one with a `brew install` line to copy, a Copy All button, and a
Re-check. It never runs `brew` itself. Installing a compiler is a deliberate act
with system-wide consequences, and an app that does it unasked is a worse
neighbour than one that explains itself.

The app is **44MB** (46MB of disk blocks once the filesystem rounds up
thousands of small stdlib files), ad-hoc signed, arm64 (use `--arch x86_64` for
Intel). Ad-hoc rather than a Developer ID because this is not distributed: a
signature saying "made on this Mac" is enough for the machine that built it.

| | |
|---|---|
| Bundle | 44MB — 43MB of it the trimmed interpreter |
| Download, once | 24MB, cached in `dist/python-cache/` |
| Startup | ~1s; the server binds an ephemeral port, so two copies coexist |

Two things the build checks rather than trusts, because both fail silently
otherwise: the bundled interpreter starts the server and reports a port, and
quitting the app reaps that server. A leaked server holds its port and looks
like a broken next launch.

**If the window ever looks wrong, read the log.** *Show Log* in the File menu
opens `~/Library/Application Support/Praccy/`, which holds `praccy.log` (the
server's stderr) and `launch.log` (what the app did at startup: the window
frame, whether the webview was sized, and whether the page finished loading).
A Finder-launched app has no terminal, so without this a GUI problem leaves no
evidence at all.

The build also checks the window itself. It launches the installed app, waits
for the page to render, and fails if the webview is 0x0, if the page did not
load, or if the window did not end up on a display that is actually attached.
That last one is worth its own line: a window on the wrong screen is
indistinguishable, from where the user sits, from no window at all.

`./tools/preview_panel.sh` shows the dependency panel with toolchains simulated
as missing, which is the only way to see it on a machine where nothing is.
`python3 tools/test_no_leaked_servers.py` reports whether a server is outliving
the app.

## Browser

```bash
python3 run_server.py          # detached; then open http://127.0.0.1:8777
```

Or run it in the foreground with `python3 -m cbp.server` (Ctrl-C to stop).
`--port 9000` if 8777 is taken, `--port 0` to let the OS choose and print it.

> **Why a server?** A browser cannot compile C++, C#, Java or Rust — there is no
> way around that. The UI is a browser; the code still runs locally in a
> subprocess so all five languages work for real. The server is bound to
> `127.0.0.1` and is not reachable from your network.

This is a development path. The app ships its own window around the same files,
and nothing in the interface is written for a browser you are meant to open:
the viewport is fixed, the appearance is chosen in the app rather than by the
system, and every preference is read from disk rather than from `localStorage`.
A browser is still the fastest way to work on `cbp/web`, and the file list is
the reason.

### The shell, and how it runs on three systems

`praccy.py` is the app. It owns the window and nothing else, and it replaces
the macOS-only Swift shell in `app/`:

```bash
python3 -m pip install pywebview      # the only dependency, and only for a window
python3 praccy.py                     # open the window
python3 praccy.py --check             # start, probe, exit, no window
python3 praccy.py --deps              # the toolchain report, as plain text
```

pywebview supplies the three things `app/main.swift` spent most of its length
on -- the window, the platform webview (WKWebView, WebView2, WebKitGTK) and
the Python/JS bridge -- which is why the shell is a few dozen lines rather than
a few hundred, and why the same file runs on all three systems. Everything else
is standard library, so `--check` and `--deps` work on a machine that has never
installed pywebview at all.

Two things carried over from the Swift shell deliberately:

- **The server runs in-process**, on a port the OS picks.
  `ThreadingHTTPServer` hands back the port directly (`server_port`), so there
  is no `PORT=<n>` stdout handshake to parse, no child process to reap on quit,
  and no way for the app to exit leaving a server behind.
- **A launched app inherits almost no `PATH`** -- `/usr/bin:/bin:/usr/sbin:
  /sbin` from Finder, and whatever Explorer was started with on Windows --
  and the toolchain probe depends on what is on it. `_search_path` puts the
  directories each platform's installers actually write to back in.

What the shell cannot fix is the same thing a rewrite in Rust could not fix:
`cbp/toolchain.py` and `cbp/adapters.py` are where the per-OS work lives, and
it is now done.

- **Finding the compilers.** Each platform has its own search map of the
  absolute paths its installers write to -- MSVC's edition-and-build-numbered
  `VC/Tools` tree on Windows, `/usr/lib/jvm/java-21-openjdk-*` and
  `/usr/bin/clang++-*` on Linux -- because none of them are on a launched app's
  `PATH`. The install hints are written per platform too; telling a Debian user
  to `brew install` is worse than saying nothing.
- **C++ has more than one name.** It is `clang++` on macOS and most Linux
  distributions, `clang-cl` on Windows (which speaks MSVC's command line and
  links the same standard library, so a C++17 source that works on one works on
  the other), and `g++` wherever a distribution shipped GCC instead of LLVM.
  `candidates_for("cpp")` returns the ordered list and the adapter takes the
  first that runs.
- **The C++ command line differs too.** clang-cl wants `/std:c++17` and
  `/Fe:out.exe` where clang++ wants `-std=c++17 -o out`, and it litters the
  directory with `.obj` and `.pdb` files without `/nologo`.

The prototype that answered the original question is still at
`tools/pywebview_shell.py`; `praccy.py` is the version that replaced it.

### Giving it to someone

`tools/build_portable.py` packages the app for the machine it runs on, using
PyInstaller:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pywebview pyinstaller

python3 tools/build_portable.py            # a directory; fast to start
python3 tools/build_portable.py --onefile  # one file; this is the one to send
```

**PyInstaller is not a cross-compiler.** It links against the extension modules
of the interpreter it is installed into, so a Windows binary has to be built on
Windows and a Linux one on Linux. That is not a limitation to work around, it
is the reason the next section exists.

Each build writes `dist/artifacts.json` listing what it produced, with paths and
sizes, so a script or a CI job never has to re-derive a filename that depends on
the OS, the architecture and `--onefile` all at once.

#### The three things that are easy to get wrong

Each of these produces an app that starts, renders, and is subtly wrong, which
is why the build checks for them rather than trusting a zero exit code.

- **The typefaces have to be collected explicitly.** PyInstaller walks Python
  imports, and a woff2 referenced from a stylesheet is not an import. Left out,
  the app falls back to a system face: it looks fine, and it is exactly the bug
  the fonts were bundled to fix. So they are added as data, and the build then
  fetches both over HTTP and checks the byte counts.
- **The web root has to be found next to the executable, not in the working
  directory.** A frozen app is launched from wherever the user double-clicked
  it, so a relative `cbp/web` resolves to the desktop. `praccy.py` handles that
  in `_resource_root`, which raises with a plain message rather than serving a
  directory of 404s.
- **The pywebview backend is imported lazily, by platform.** A frozen build
  cannot import something it never collected, so the Cocoa, EdgeChromium or GTK
  backend is named as a hidden import. Getting it wrong is a bare `ImportError`
  at startup that no user can act on.

#### A one-file build cannot be inspected, only run

A one-file build has no data directory: PyInstaller packs the fonts and the web
root into the executable and unpacks them to a temporary directory at startup,
deleting it on exit. So its verification runs the artifact and reads the answer,
rather than listing files that are not there. `--check` starts the server,
fetches the page and both typefaces, and exits without needing a display, which
is what makes it usable on a build machine.

That check is worth more than it looks. A one-file build with no bundled
typeface starts, renders the whole interface, and quietly uses the system font.
Nothing crashes and nothing is logged, because nothing is wrong as far as the
app is concerned.

#### Icons for the other two platforms

`app/Icon.swift` draws the mark with AppKit, which exists on exactly one of the
three systems. `tools/make_icon.py` draws the same mark in the standard library
alone -- `zlib` for the PNG, `struct` for the containers -- and writes `.ico`
for Windows, `.icns` for macOS, and a freedesktop hicolor tree for Linux. The
anti-aliasing is analytic rather than by supersampling: every pixel's coverage
comes from a signed distance function, so a 1024px icon is one pass of about a
million evaluations instead of sixteen, and it is exact at the edge.

Writing the `.icns` by hand was instructive. The format's table is sequential
and length-prefixed, not the offset-based directory that the documentation
also describes. The offset variant produces a file that `iconutil` accepts as
valid and then extracts a single 16x16 slot from, because the first offset it
follows points into the middle of the first PNG. Comparing against an `.icns`
that AppKit's own `iconutil` had written is what showed the difference; both
variants validate, and only one of them is the one macOS reads.

If the mark changes, change it in both `app/Icon.swift` and
`tools/make_icon.py`. The numbers in the second are transcribed from the first.

#### Building on Windows and Linux

`.github/workflows/build.yml` runs `build_portable.py --onefile` on
`windows-latest` and `ubuntu-latest`, verifies each artifact by running it, and
uploads the results. Trigger it from the Actions tab or push a `v*` tag.

The Linux job installs `libwebkit2gtk-4.1-0` and friends, and that is not
incidental: they are the webview the app renders in, so without them
PyInstaller cannot collect the backend and the frozen binary dies at startup.
The same libraries are what a friend needs installed to run it, which is the
real constraint on Linux and the reason an AppImage is worth the extra step.

Windows needs the WebView2 runtime, which is present on Windows 10 and 11 by
default. A machine without it shows a dialog asking for the runtime rather than
starting, and that is Microsoft's installer, not this app's.

## Terminal

```bash
python3 practice.py                      # interactive
python3 practice.py --list               # browse the catalogue
python3 practice.py --track              # read the course
python3 practice.py --tier medium        # practise a tier
python3 practice.py --tag "string manipulation"
python3 practice.py --lang java          # pick a language
python3 practice.py --count 8
```

Enter code and finish with a line containing only `END`.

## The interface

- **The course is the front door.** The app opens on the Course, not an empty
  editor, because the material is the thing worth seeing first and practice is
  one click away. The two views sit behind a Practice / Course switch.
- **Per-section progress you can trust.** Each part carries a ring and each
  module a bar, both measured by how many of the questions that section actually
  touches have been solved — its drills *and* the questions its principles are
  used by, not reading progress dressed up as a score. A module still counts as
  "done" only when every drill is solved, which is the honest measure and what
  the thin bar at the top uses. The ring and its percentage sit together in one
  pill, the number *beside* the circle rather than inside it: an arc small enough
  to hold two digits is a glyph, not a sweep. The label reads "58% Complete" and
  nothing else. It used to carry a second line of arithmetic underneath ("15 of
  26 solved"), which was the ring's own job done worse: two numbers for one fact
  invites the reader to work out which one to trust, and nobody checks the line
  against the arc. The count is still in the accessible name, where it costs
  nothing and is read out rather than counted. A finished section turns the pill
  green.
- **One column, centred.** The welcome card, the question and the course are each
  a centred measure rather than a full-bleed page, so the text keeps a readable
  line length at any window size and the eye stays in one place as you move
  between views.
- Each principle shows the questions that use it, and each module ends in drills
  to try. A pass fires a shard burst from the result box, the ring and streak pop,
  and the XP toast; a miss shakes the result once. Both are suppressed under
  `prefers-reduced-motion`, and question changes cross-fade.
- Questions grouped **Easy / Medium / Hard** in the sidebar, with a segmented
  **All / Coderbyte / LeetCode** filter above the search box, a `C` or `L`
  monogram on every row, and a ✓ when solved (saved on disk, like every other
  preference).
- **Language selector** for Python / C++ / Rust / C# / Java; the starter code and
  the reference solution follow it.
- **A light/dark switch** in the header, beside the sound control, because it is
  the same kind of thing: a global preference, one press, no mode to think
  about. The app opens on the system appearance and keeps following it until
  you press the button.
- The **contract** is stated up front — `FirstReverse(str)` must return a
  `string` — because that is the thing people get wrong.
- **Examples** are always visible, one card per case with the input above the
  output and the return type beside it. The header of that card is the control:
  the whole row, label included, opens and closes the list, and the arrow points
  down when the list is showing and right when it is away. It went through two
  worse shapes first — a Hide in the header with a separate Show button down
  where the block had been, so the click that closed the list landed somewhere
  other than the click that reopened it, and then a 54px button inside a
  full-width row that looked like it should also work. The choice sticks across
  questions.
- The editor has line numbers, tab-to-indent, auto-indent after `{`, and
  `Cmd/Ctrl+Enter` to submit.
- **Hints, above the answer.** Every question carries two or three hints written
  for it, revealed one at a time. The trigger sits in the editor's own row,
  beside Reset, and the hints land directly above the code they are about —
  because help you have to scroll to find is help you do not use. The first
  names what the input is really asking about, the second names the technique;
  neither shows code. The count is stated before you spend the first one, and
  each reveal arrives with a sweep of light.
- **Patterns, below the answer and covered.** The techniques the question is
  built from, blurred until you ask for them: `sliding window` is most of a
  sliding-window problem, so the words are a spoiler rather than a label, and a
  press uncovers them with a shine. The patterns are a closed vocabulary of 33
  techniques, assigned per question in `tools/patterns.py` and checked at build
  time — every question carries at least one, and no chip is a topic wearing a
  pattern's clothes. The ones the course teaches link straight to the module
  that teaches them; the rest (`arithmetic`, `single pass`) are stated but not
  linked. The free-text `tags` are still shipped and still drive the sidebar
  search, so "math" still finds something.
- **A lesson when you miss**, matched to why: a type error teaches a type rule, a
  wrong value teaches an algorithm idea.
- **The reference solution last**, a disclosure at the very bottom of the page.
  It ends the attempt, so it does not belong beside the things that help with
  it, and it is fetched only when it is opened. The cache is dropped on every
  language change, whether or not it is on screen at the time: it used to be
  cleared only when the disclosure happened to be open, so reading the solution,
  closing it, switching language and coming back showed the previous language's
  code beside an editor full of another one.

## Progress you can see
Deliberately quiet, and all of it is real — every number below is derived from
attempts you actually made, stored on disk by the app's own settings store.

- A **progress ring** in the header. It is also the app's icon: the mark and the
  status are the same object, and it is the only element that moves on its own.
- A **streak** of consecutive days with at least one solve. A streak survives
  until you miss a whole day, and stays hidden at zero — a zero streak is not a
  failure state, so it is not something to show you.
- A **personal best** per question, shown next to the tier once you have one. A
  time of zero never counts as a record, because zero means the answer was
  never typed.
- **Question N of 144**, so you know where you are in the run.
- A **level** chip next to the streak, with a bar filling toward the next level,
  and a **trophy** chip beside it counting what you have earned. Both open the
  same sheet. The level is how far along you are and the count is what you have
  to show for it — one chip carrying both numbers is how the points total ended
  up meaning nothing.
- Solving pulses the ring, fills the sidebar dot, and says the time in a toast.

### Points and levels

A first solve is worth 10 points on an easy question, 25 on a medium and 50 on a
hard, because that is roughly the ratio of how long they take to get right the
first time. A question you have already solved is worth 4, and beating your own
record on it adds 6. The level curve is quadratic, so the first few levels arrive
quickly and later ones do not: level 2 at 40 points, level 3 at 120, level 10 at
1200, level 15 at 2800. Finishing all 144 lands around level 13.

Two things it deliberately does not do. Points never decay, because losing them
for taking a day off turns a practice tool into a debt. And nothing is compared
to anyone else, because the only comparison worth making is with your own last
month.

Seventeen **trophies** are checked against the whole progress state rather than a
counter, so they cannot fire out of order or twice. Three of them *are* the
levels — level 3, 6 and 10 — which is what stops the points being a scoreboard
nobody is keeping: each of those is named after the level it marks, so reaching
level 6 does not hand you a badge and a separate word for it. The sheet states
how many points the next level costs, which is the answer to what the total in
the corner is for. Reaching level 10 also earns every other trophy, so the set is
provably completable; that is checked by `tools/test_progression.py`, along with
the shape of the curve and the points rules.

### Sound

Off until you switch it on. Silent by default is a decision, not an oversight: an
app that makes noises the first time you open it is an app you mute, and a
drill that beeps at you while you think is worse than a quiet one.

Every sample is generated on your Mac by `tools/build_sounds.py` rather than
downloaded, so there is no third-party licence to track, nothing to attribute,
and nothing that can change upstream between two builds. The generator is
deterministic — the noise comes from a fixed seed, so a rebuild produces
byte-identical files — and it is checked rather than trusted: a sample with more
than 10% of its energy above 6 kHz fails the build. That one rule is what keeps
the set sounding like a single instrument instead of a box of blips.

The keyboard comes in two packs, and they are the two mechanical keyboards worth
imitating by ear. **Creamy** is the lubed board — the body a fifth lower and
ringing half again as long, with the click filtered down and mixed well under
it. **Clicky** is the blue-switch board: a short, bright, band-limited click on
the press and a second, quieter one on the release over a tighter body. You can
hear the difference in the build output, where cream carries hundredths of a
percent of its energy above 6 kHz against clicky's four tenths. Only the
keystrokes change with the pack — the interface ticks and the verdicts are the
app's voice, and a button that sounded different depending on how you had set
the keyboard would be incoherent.

Everything the app says for itself is softened twice — once by construction and
once by an extra low pass applied to every file that is not a keystroke — and
written quieter than the keyboard it sits under. A settings panel should not be
louder than the typing it is configuring.

One master switch, then four categories — typing, interface, verdict, trophies —
each of which can be silenced on its own, plus a volume. Switching one on plays
the thing it controls, because there is no way to choose a sound except by
hearing it. Space and enter are deeper and slower than an ordinary key and delete
is shorter and brighter, because those are the keys that feel different under a
finger; every keystroke is detuned slightly and two closer together than 26 ms
share one sample, so a paragraph does not sound like a machine gun. Nothing is
recorded and nothing leaves the app.

Those switches — and the language, and the hidden examples, and your progress —
are remembered between launches. That is not free: the server binds an ephemeral
port on purpose, so every launch is a different origin as far as the browser is
concerned, and `localStorage` is scoped to the origin. `cbp/web/store.js`
bridges the two, hydrating from the server's settings file at startup and
writing changes back through a short debounce, so a preference survives both a
reload and a restart.

## How the interface is put together

No frameworks, no build step, no dependencies — one HTML file, one stylesheet,
four small scripts, all served from `cbp/web`.

- **Materials, not boxes.** Depth comes from layered translucency and hairline
  separation rather than a border around every element. The header and the toast
  use `backdrop-filter`, so they sit on the content rather than above it.
- **Petrol and brass.** The dark scheme is a dark blue-green rather than a
  near-black, and the one accent is brass: the colour a needle is painted. Light
  mode is chalk with the same cast, not cream — cream plus a mid-tone accent is
  the most recognisable generated palette there is. Both are driven by custom
  properties and `color-scheme` follows the one in force, so native controls
  match. See **Light and dark** below for how the choice is made.
- **Colour is a verdict, with one deliberate exception.** The chrome is
  colourless on purpose: outside the brass controls, saturated colour appears
  when a run passes or fails. The hint is the exception — help is not a result,
  so it gets its own warm sand, kept well away from the verdict green and red so
  it can never be read as one. A gradient appears in exactly one place, and only
  for the length of a reveal: the shine that sweeps a row when the cover comes
  off.
- **Squares and pills, not cards.** Grouped content takes a 6px corner and a
  flat fill; anything you press is a pill. Nothing in between. One radius for
  everything is most of what makes an interface read as a template.
- **Readings in the rounded face.** The stopwatch, the ring's percentage, the
  level, the per-section counts and the verdict are set in `ui-rounded` (SF
  Rounded, with the body font as the fallback) with tabular figures. It gives
  the numbers a voice of their own without shipping a second font file.
- **Spring motion.** Everything that moves uses `cubic-bezier(.32, .72, 0, 1)`,
  the iOS/macOS sheet curve, and animates only `transform` and `opacity`. Motion
  answers an action — opening, confirming, advancing — with one exception, the
  drifting code described below.
- **One bold thing.** The verdict. Everything around it stays quiet.
- **Reduced motion is honoured.** The whole animation set collapses to near-zero
  and no information is lost, because everything animated is also stated in text.
  The drifting code is dropped outright rather than shortened: run at a
  thousandth of a second it would freeze as a half-drawn field of glyphs across
  the reading column.

### Light and dark

The two appearances are two blocks of custom properties in `style.css` — the
dark one on `:root`, the light one on `:root[data-theme="light"]` — and an
attribute on `<html>` picks between them. Nothing else on the page knows which
one is in force, and there is no `@media (prefers-color-scheme)` block left to
argue with the choice.

The attribute has to be set before the first paint, so a small script in the
head of `index.html` does it from the mirror `store.js` keeps in `localStorage`,
falling back to the system setting. `app.js` re-applies it once the server's
settings file has answered. With nothing stored the app follows macOS, live:
switching Appearance at noon switches the app with it. The button in the header
pins it, and the glyph shows where the press goes rather than where you are,
so it reads as a switch instead of a readout. The preference is `cbp.theme` in
the settings file, like every other one.

Two failure modes here are silent, so `test_api.py` checks for both: a token
that exists for light and not for dark leaves that element unstyled in the
appearance most people run, and an unterminated `/*` in the stylesheet swallows
every rule after it without a parser saying so. That second one had been true of
the `reduced motion` block for the whole life of the file.

### Type, and why the font files are in the repository

Two variable typefaces are bundled under `cbp/web/fonts`: Inter for text and
readings, JetBrains Mono for code. Both are latin-subset, variable in weight,
and served from the app's own loopback server, so the whole app works with no
network at all.

The reason for shipping files rather than naming system faces is that the type
stack used to be built out of them, and it degraded differently on every
platform: `-apple-system` and `Segoe UI` and Roboto are all fine, but the
`--display` token began with `ui-rounded` and `"SF Pro Rounded"`, which exist
on macOS and nowhere else. The readings -- the stopwatch, the ring, the level,
the verdict -- were therefore set in a rounded cut of the system face on a Mac
and in the same face as the body text on Windows and Linux, which is a
difference nobody asked for and nobody could see was missing.

So the distinction is now made the portable way. The readings are the same
Inter as the prose, at weight 620 and slightly negative tracking, and the
stopwatch at 700 with the tracking tightened further. `font-display: swap` is
deliberate: on a cold cache the fallback is used for one frame and then
replaced, which beats a blank block of text while a local file is parsed. Each
bundled name is followed by a real fallback chain ending in `sans-serif` or
`monospace`.

Two things here fail silently, so `test_api.py` checks both. A woff2 served as
`application/octet-stream` is discarded by the browser, which presents as a
missing font rather than as a MIME error -- hence the entry in the server's
`CONTENT_TYPES` and the check on the header. And a font loaded from a CDN looks
perfect until the machine is offline, so a test now greps every HTML, CSS and
JS file for an off-machine URL; the only permitted matches are the two XML
namespace identifiers, which are names rather than fetches.

### The drifting code

A field of code tokens rises behind the panes: `{{`, `}};`, `=>`, `#[derive]`,
`0b1011`, taken from the languages the app actually runs, at the bottom of the
label ramp, over cycles of a minute and a half to two and a half. It is the
only motion here that is not answering something you did, so it is built to be
missed rather than watched, and four things keep it that way:

- **Transform and opacity only**, so all of it stays on the compositor and
  nothing on the main thread lays out per frame.
- **One element per token**, each travelling the full height of the window on
  its own duration with a negative delay, so the field is already populated on
  the first frame and never pulses as the cycles line up.
- **A mask**, faded out through the middle of the window where the reading
  column sits in both views. A glyph crossing a sentence is the one thing that
  would make this noticeable rather than atmospheric.
- **Tokens for the appearance**, so chalk and petrol each get an alpha that
  reads as ground on their own ground.
- **Keyboard and screen readers.** A skip link, a real focus ring on every
  interactive element, `aria-live` on the verdict and the toast, labels on every
  control, and an h1 → h2 outline with no skipped levels.

Editing `style.css` or `app.js` takes effect on the next reload: the server
sends `Cache-Control: no-store` for static files, because a local dev server
that caches its own assets makes every change look like it did not happen.

## Question types, and how the awkward ones are passed

Most questions take a string or a number. Some take a tree, a grid, or a
linked list, and those have to cross the boundary somehow. The encodings are
the compact ones, so a problem reads the same here as it does anywhere else:

| Type | Wire form | Example |
|---|---|---|
| `tree` | level order, `null` for a missing child | `[1, 2, 3, null, null, null, 5]` |
| `list` | the values, head first | `[1, 2, 3]` |
| `matrix` | rows of numbers | `[[1, 2], [3, 4]]` |
| `graph` | adjacency list, indexed by node | `[[1, 2], [2], []]` |
| `charmatrix` | rows of single characters | `[["A", "B"], ["C", "D"]]` |
| `strmatrix` | rows of words | `[["cat", "dog"]]` |
| `strarray` | a list of words | `["cat", "dog"]` |

**A tree is a heap-indexed array.** The node at index `p` has its left child
at `2p+1` and its right child at `2p+2`. Trailing nulls are trimmed and the
empty tree is `[]`, so `[1, 2, 3, null, null, null, 5]` is a root of 1 whose
right child 3 has a right child of 5.

That indexing is the choice worth explaining. It is the one layout that needs
no bookkeeping to walk: level `d` occupies indices `2^d - 1` through
`2^(d+1) - 2`, so a depth answer is a loop that doubles an index, and a
left/right swap is arithmetic rather than a traversal. It also means the
answer to a tree question can be *longer* than the array it was given — a node
that was a left child with no right sibling becomes a right child with no left
sibling, and its value moves to an index the input never reached. Invert
Binary Tree is the question that makes this obvious, and the prompt says so.

**Passing the structure rather than the object is deliberate.** A harness that
handed over a ready-made `TreeNode` would hide the one thing a tree question is
about. Here you get an array and you do the decoding, which is the part worth
practising.

Each language spells these differently, and the differences are the interesting
part: a tree is `vector<optional<int>>` in C++, `int?[]` in C#, `Integer[]` in
Java and `Vec<Option<i64>>` in Rust — a null has to be *expressible*, which is
why the type is not just the list type with a different name.

`cbp/structures.py` holds a probe for every one of these, with a reference
solution in all five languages, run by the self-test. The practice catalogue
cannot prove them on its own, because every one of the Coderbyte questions
returns a scalar or a flat array.

## Three tiers, and a separate question of where it came from

| Tier | Count | Shape |
|---|---|---|
| `easy` | 66 | one function, a few arguments, a handful of cases |
| `medium` | 56 | the same, with an idea worth finding |
| `hard` | 22 | the same, and the idea is the whole problem |

There used to be a fourth tier, `stretch`, holding every LeetCode problem. That
was a mistake: it filed a LeetCode Easy next to a LeetCode Hard under a heading
that described neither, because `stretch` was an answer to a different question
(how long does this take?) in the slot meant for difficulty (how hard is this?).
The two are now separate.

`tier` is difficulty and nothing else. A LeetCode question's difficulty is the
one LeetCode publishes, which was already recorded in each question's
`sourceNote` as "LeetCode 226 (Easy)". A Coderbyte question keeps the tier we
judged it to be, since there is no published figure to copy. `tools/retier.py`
does the move and refuses to write if a LeetCode question's note cannot be
read, because silently leaving one behind is the bug the migration exists to
remove.

`source` says where the question came from, `Coderbyte` or `LeetCode`, and the
same word goes into `tags` so the text filter finds it. The sidebar has a
segmented **All / Coderbyte / LeetCode** control and a `C` or `L` monogram on
each row. Each source keeps one colour everywhere it is named — the active
filter chip, the row monogram, and the badge on the question.

`sourceNote` is no longer rendered. It read "LeetCode 226 (Easy). The first tree
on the list…" directly under a badge that already said `LeetCode 226`, and the
second half of it gave the technique away. The field stays in the dataset
because `tools/retier.py` reads the published difficulty out of it, and because
it is the record of where each question came from.

The two axes together are the useful part. A LeetCode Easy like Valid
Parentheses sits beside Coderbyte Easies and can be filtered out if you only
want assessment-shaped work; a LeetCode Hard sits in `hard` where it belongs,
with a note saying so.

| | Coderbyte | LeetCode |
|---|---|---|
| easy | 46 | 20 |
| medium | 15 | 41 |
| hard | 11 | 11 |

`hard` is what a Coderbyte Hard challenge would look like if one existed: one
function, a few arguments, a handful of cases. The real site has 58 of them,
but they are not public, so this tier is a **reconstruction**, not a copy.

Sixty-six of the questions are the **Grind 75** list, added in the order that
list puts them. Each carries a `grind75` field holding its 1-based position on
the canonical list, and the catalogue sorts by that rather than by title, because
the ordering is the point of the list. Six of them were already in the set
under their own prompts -- Two Sum, Valid Anagram, Contains Duplicate,
Maximum Subarray, Container With Most Water and Trapping Rain Water -- so the
driver stamps the position onto the existing question rather than duplicating
it.

Six LeetCode questions are not on the Grind 75: Trapping Rain Water (42), First
Missing Positive (41), Search Rotated Sorted Array (33), Median of Two Sorted
Arrays (4), Decode Ways (91) and Candy (135).

Nine of the 75 are not here, at positions 12, 13, 32, 35, 38, 47, 65, 68 and
70. Eight are design problems that build a class and keep state between calls
rather than returning a value (Implement Queue using Stacks, Clone Graph,
Implement Trie, Min Stack, Time Based Key-Value Store, LRU Cache, Serialize
and Deserialize Binary Tree, Find Median from Data Stream). Each would need a
harness that can construct an object and then poke at it, and this one runs a
function once per case and throws it away. The ninth is Linked List Cycle at
12, which asks whether a list points back at itself — an array has no pointers
for Floyd's algorithm to chase, and a rephrasing would not be the same
question. They are skipped rather than rewritten, and the driver says so
loudly if a wave ever claims one of those positions.

Prompts throughout are **written or adapted to be self-contained**, not
verbatim from Coderbyte — where the original wording depended on a page this
could not read, the prompt says so in its own terms. Treat them as practice
material, not as the assessment.

## The course

Thirteen modules in two parts, and the split is the point.

**Essentials** is one module, twenty minutes, six principles: read the return
type off the prompt, treat the examples as the specification, rewrite the
paragraph as a numbered list, name the input's shape and trace one by hand, do
one pass with a named accumulator, and know the three bugs that survive review.
It is short on purpose.

**Patterns** is the other twelve, and it is where the reading time goes:

| | | |
|---|---|---|
| 2. Recognising the pattern | 3. Searching a sorted sequence | 4. Two pointers |
| 5. Sliding window | 6. Hash maps and sets | 7. Stacks |
| 8. Linked lists | 9. Trees | 10. Graphs and traversal |
| 11. Backtracking and recursion | 12. Dynamic programming | 13. Heaps and greedy choices |

Recognising the Pattern sits at the head of that half rather than the end of the
primer, because it is about choosing a technique and that is what the pattern
half is for. It reads the answer rather than the input, gives three questions to
ask before you write anything, and says what to do when two patterns both fit:
take the one you could write correctly first time.

The shape of a pattern principle is the same each time: a claim about when the
technique applies, the argument for why it works, the specific mistake people
make inside it, and a question to ask yourself before moving on. That last part
is set apart in a box of its own rather than run into the prose, because it is
the sentence worth carrying out of the room.

### Reading it a beat at a time

The course used to render a principle as a wall: the whole argument at once, so
the reader's only choice was all of it or none of it, and forty-three of those
walls in a row is a document rather than a lesson. Two changes, both in
`app.js`:

- **Progressive reveal.** A principle is split into its blocks and given one at
  a time. The first is never hidden -- the claim is the reason to keep going,
  and hiding it would hide the invitation. The control carries the count of
  what is still folded ("Show the rest · 2 more"), because a reader deciding
  whether to keep going is owed the size of what is left. When the last beat is
  out it becomes a collapse rather than disappearing, so a beat can be folded
  and unfolded without reopening the module.
- **Walkthroughs.** A code specimen stays whole and one line is picked out of
  it, rather than being revealed in order. That inversion is the point: the
  finished block is what the reader is learning to recognise, so hiding it would
  remove the thing being taught. Lines are real buttons, so the code is
  navigable by keyboard and the active line is announced rather than only
  shown. The sentence that introduces a specimen is folded into it as a
  caption.

Both are worth noting for what they do *not* do. Nothing was added to the prose:
the beats are the blocks that were already in `track.json`, cut at the
paragraph boundaries the file already uses. The course is not longer, and no
principle was rewritten, which is why `tools/humanizer_check.py` had nothing to
object to.

A principle is set as three typographic steps: the heading names it, the first
paragraph states the claim in the brightest text on the page, and the paragraphs
underneath are the argument for it, one step quieter. That first-paragraph rule
is not a style preference — in all forty-three principles the opening paragraph
really is the claim, so the shape of a principle is legible before you read it.

Bodies are written in a format of two inline spans and one fence, rendered by
about thirty lines of `proseMarkup` in `app.js`. A backtick pair is a code
fragment; a double-asterisk pair is emphasis; a block whose every line is
indented by two or more spaces is a specimen, drawn in a box that scrolls
sideways rather than wrapping, because a wrapped line of code has stopped being
a line of code. Three principles use one today, including the two conventions of
a binary search loop side by side.

Which phrase each principle emphasises is decided in an `EMPHASIS` table in
`tools/build_course.py`, not by markup inside the prose. That is partly because
the bodies are Python string literals split across source lines, so a tag often
straddles two of them, and mostly because a table is one place to read what the
course chooses to highlight. It is checked rather than trusted: a phrase that
appears nowhere in the principle it is filed under, or twice, fails the build. An
emphasis that silently matches nothing looks exactly like emphasis nobody asked
for, and neither is visible on screen. `tools/humanizer_check.py` used to flag
every bold span as decoration; it now flags the shape that is still a tell, a
span that opens a line and stops at a colon, and reports the deliberate emphasis
as a count so it stays accounted for.

Every principle in both parts carries a **Used by** line naming the questions in
this catalogue that use the thing it just taught. That is the part worth using
the course for. Reading about a monotonic stack is cheap; the four questions
under it are where it becomes a thing you can do. The links are checked at build
time, so a renamed question fails `selftest` rather than leaving a dead chip.

### Why the first half got shorter

The course used to open with nine modules, 149 minutes, on reading advice,
debugging advice and per-language trivia. Not one principle among those
thirty-seven linked to a question, because none of them was a technique. They
were things worth knowing that do not attach to a particular problem, and they
sat in front of the material that does.

Compressing them removed three principles outright, because they taught what
modules 4 and 6 now teach properly: "two pointers, and when they beat a set",
"the set trick", and "sort first when order does not matter" were the same
material at a shallower depth.

The language trivia did not become course content. Loop ranges, the lambda
equivalents, the string traps and the division rules are in
[REFERENCE.md](REFERENCE.md), because nobody learns a range convention by being
told to and it is worth having the moment you need it.

The material is written from two public study guides, neither of them copied:
[grind75bot.com/theory](https://grind75bot.com/theory/) for the per-technique
shape, and the
[Tech Interview Handbook study cheatsheet](https://www.techinterviewhandbook.org/algorithms/study-cheatsheet/)
for the topic ordering and the general advice about clarifying assumptions and
validating input. `tools/humanizer_check.py` flags the AI-prose patterns
against the course text, and the course is currently clean on every one of them.

## The thing this tool exists to teach

Coderbyte scores the **exact value and its type**. Returning the boolean
`False` when the prompt says "return the string false" is marked **wrong**,
even though the logic is perfect. This is the single most common way to fail
the real assessment.

So the runner here is deliberately unforgiving:

| Question asks for | You return | Result |
|---|---|---|
| the string `"true"` | `True` | **wrong** — type mismatch |
| the string `"true"` | `"true"` | correct |
| the boolean `true` | `1` | **wrong** — `bool` is not `int` |
| the int `1` | `1.0` | **wrong** — float is not int |
| `"Arithmetic"` | `"arithmetic"` | **wrong** — case matters |

Every failure is explained rather than just scored:

```
  FAIL  case 1
  input    [1, 2, 3, 4, 5, 6]
  expected "true"  (string)
  you      True  (bool)
  -> type mismatch, not a value problem
     this question returns the STRING "true"/"false", not a boolean
```

## The timer

The clock is visible in the question header, **starts the first time you change
your answer, and stops when the question is over**. It measures writing code,
not staring at a blank editor and not re-reading the prompt — thinking time is
yours to spend.

**A failed submission does not stop it.** The clock measures how long the
question took, and a question is not over because one answer was wrong. It used
to stop at every submit, so each retry was handed a fresh clock and the time
spent on the failed attempt was discarded — which quietly flattered every
result, since the attempt that eventually succeeds is usually the second one.
It now runs straight through a miss: the number keeps climbing while you read
the failure and fix it, and the recorded best is the honest total.

Exactly two things stop it: a pass, because the question is over and that
number is recorded as your best, and **Reset**, because you have said you are
starting the question over. The header shows three states: dimmed and idle
before you start, green and counting while you type, blue once stopped.

It never fails you for going slow and there is no hard cutoff. At the end of a
session you get total time, fastest solve, and accuracy by topic so you can see
what to drill. In the terminal the same rule applies: the clock starts on your
first line of code, not when the prompt is printed.

## Hints and solutions

- Hints are written by hand, two or three per question, in `tools/hints.py`. The
  first says what the input is really asking about, the second names the
  technique or the invariant, and neither contains code for the question it
  belongs to. They appear one at a time because the first is usually enough, and
  there is no way to un-read the second.
- `tools/fetch_hints.py` pulls the hints LeetCode publishes for the 72 questions
  taken from there, via its public GraphQL endpoint. That is worth doing and not
  sufficient: 49 of the 72 have none published at all, so the fetch is reference
  material rather than the shipped set. `tools/build_hints.py` is what validates
  the whole set and writes `cbp/data/hints.json`, and it refuses to write the
  file while any question is missing a hint, while any hint names a question that
  no longer exists, or while any hint is long enough to be an answer rather than
  a nudge.
- Lessons are matched to *why* you failed — a type error teaches a type rule, a
  wrong value teaches an algorithm idea.
- **The worked solution is always reachable afterwards.** Reviewing a solution
  you earned yourself is the highest-value study move, so it is never gated
  behind anything.

## Verifying the harness

Before trusting any result, the harness proves itself. Every reference solution
is run in every language against its own test cases:

```bash
python3 -m cbp.selftest        # dataset check + 720 checks: 144 questions x 5 languages
python3 tools/build_hints.py   # every question has hints, none of them an answer
python3 test_api.py            # the browser path, including hints and pattern links
python3 -m cbp.strictness_test # 17 checks on the comparison rules
python3 test_api.py            # the HTTP path the browser uses (starts its own server)
python3 -m cbp.structures      # 8 structural probes x 5 languages, if you want them on their own
python3 tools/test_progression.py  # 21 checks on the XP curve and the trophies
```

All three must be green. The self-test runs the structural probes too, so
`cbp.selftest` alone covers both suites. The strictness tests assert *rejections* as well as
acceptances, including the Python `bool`-is-a-subclass-of-`int` trap.

The self-test also validates the **dataset** itself: that each question's
declared return type matches its test cases, that non-polymorphic questions
don't disagree with themselves, that every case has the right arity, that
every type name is one the harness can render, and that every argument and
answer matches the shape its contract promises. That
check exists because a stale `expectedType` on *Check Nums* once made the UI
tell the user to return a `bool` for a question whose cases demanded `"true"` —
the tool teaching the exact mistake it exists to prevent. It has since caught
several more: a question whose two cases disagreed on return type without being
flagged, and three cases with the wrong argument count.

## Languages

| Language | Requires | Found at |
|---|---|---|
| Python | `python3` | bundled with the app; `python3` otherwise |
| C++ | `clang++` | `/usr/bin/clang++`, Homebrew LLVM |
| Rust | `rustc` | `~/.cargo/bin`, rustup toolchains |
| C# | `dotnet` | `/usr/local/share/dotnet`, `~/.dotnet` |
| Java | a JDK (`javac`) | Homebrew `openjdk@21`, `/Library/Java/…` |

**Nothing trusts `PATH`.** A Finder-launched `.app` inherits
`PATH=/usr/bin:/bin:/usr/sbin:/sbin`, which has no Homebrew, no rustup and no
.NET in it, so `cbp/toolchain.py` probes the paths those installers actually use
and falls back to `PATH` last. Two consequences worth knowing:

- `clang++` resolves to the `/usr/bin` shim, not the raw Command Line Tools
  binary. The shim asks `xcrun` where the SDK is; the raw compiler does not, so
  with no `SDKROOT` it fails with *iostream file not found* — only inside the
  app, never in a terminal.
- `dotnet` is found at `/usr/local/share/dotnet/dotnet`, which the official
  installer never symlinks into a `bin` directory.

`/api/deps` reports the same thing as JSON, which is what the first-run panel
reads. `tools/test_bare_path.py` re-runs a solution per language with `PATH`
replaced by the bare value, so the app's worst case stays verified;
`tools/test_toolchain.py` covers resolution and the report's shape, including
the missing-toolchain case.

Each language is run in a subprocess with a hard timeout, so an infinite loop
cannot hang your session. Three questions whose cases disagree on return type
(Arith Geo, Arith Geo II and Two Sum each return an int or a string *and*
something else) are flagged `polymorphic` and use a variant return
(`std::variant`, `object`, `Object`, a `CBResult` enum). Argument types are
inferred from the test data, so a question taking `string[]` and one taking
`int[]` both get the right signature — in the generated harness *and* in the
starter code shown in the browser.

Rust submissions use the LeetCode shape, `impl Solution { pub fn ... }`, with
snake_case method names derived from the Coderbyte name (`ABCheck` becomes
`ab_check`). The user's code is emitted first in the generated file, so a
compiler error on line 12 means line 12 of what they wrote.

## Layout

```
run_server.py          detached launcher for the browser UI
practice.py            terminal CLI entry point
app/
  main.swift           the app: server lifecycle, webview, menu, Dock icon
  DependencyPanel.swift  the first-run panel listing missing toolchains
  Icon.swift           draws the app icon at build time
tools/build_app.py         builds, verifies, signs and installs Praccy.app
tools/preview_panel.sh     shows the dependency panel with things missing
tools/test_toolchain.py    toolchain resolution and the /api/deps contract
tools/test_bare_path.py    all five languages with no PATH
tools/test_no_leaked_servers.py  reports a server outliving the app
tools/hints.py             the hand-written hints, keyed by question id
tools/build_hints.py       validates the hint set and writes cbp/data/hints.json
tools/fetch_hints.py       pulls LeetCode's published hints for reference
tools/build_questions.py   regenerates the easy/medium catalogue
tools/build_hard.py        adds the hard tier
tools/retier.py            moves LeetCode questions to their real difficulty
tools/test_progression.py  checks the XP curve and the trophies
tools/build_sounds.py      generates the sound set; rejects any sample with too
                           much of its energy above 6 kHz
tools/build_grind75.py     merges the Grind 75 waves into the catalogue
tools/build_course.py      assembles the course from the two course sources
tools/course_primer.py     the essentials primer and the recognition module
tools/course_patterns.py   the twelve pattern modules
tools/humanizer_check.py   flags the AI-prose patterns in the course text
tools/grind75_common.py    contract types, prompt notes, the q()/S()/c() helpers
tools/grind75_wave1.py      Grind 75 positions 2-11
tools/grind75_wave2.py      Grind 75 positions 14-23
tools/grind75_wave3.py      Grind 75 positions 26-37
tools/grind75_wave4.py      Grind 75 positions 38-49
tools/grind75_wave5.py      Grind 75 positions 50-61
tools/grind75_wave6.py      Grind 75 positions 62-75
tools/_ref_wave4.py         reference implementations used to compute wave 4's answers
tools/_ref_wave56.py        reference implementations for waves 5 and 6
tools/patterns.py          the pattern vocabulary and which question uses what
tools/retier.py            the `stretch` migration: tier from real difficulty
tools/rust_solutions.py    Rust reference solutions, one entry per question
cbp/
  strictness.py        exact type+value comparison  <- the core rule
  adapters.py          Python / C++ / Rust / C# / Java runners
  toolchain.py         locating the four external compilers
  engine.py            load, run, judge
  api.py               JSON views of results, for the browser
  track.py             the course: modules, principles, links to questions
  server.py            local HTTP server (stdlib only, no dependencies)
  settings.py          the preference file the browser reads and writes
  web/                 browser UI: index.html, app.js, progress.js, store.js,
                       sound.js, style.css
  forensics.py         expected vs actual, with types (terminal)
  lessons.py           hints matched to the failure
  session.py           practice loop, timer, summary (terminal)
  selftest.py          golden suite + dataset validation
  structures.py        conformance probes for the tree/list/matrix/graph types
  strictness_test.py   tests for the comparison rules
  data/questions.json  the catalogue (generated)
  data/track.json      the course (generated; run tools/build_course.py)
test_api.py            end-to-end test of the HTTP path
```

## Editing questions

`cbp/data/questions.json` is generated. To change a question, edit its
definition in `tools/build_questions.py` (easy/medium),
`tools/build_hard.py` (hard) or `tools/build_grind75.py` (Grind 75)
and run:

```bash
python3 tools/build_questions.py && python3 tools/build_hard.py \
  && python3 tools/build_grind75.py && python3 -m cbp.selftest
```

Each builder is idempotent and merges into whatever is already there, so order
does not matter. `tools/rust_solutions.py` holds the Rust half separately and
the builders refuse to finish if a question has no Rust entry — four languages
and a hole in the fifth is not a state worth shipping.

Each builder also assigns the question's patterns (`tools/patterns.py`) and its
real tier (`tools/retier.py`) before writing, so the catalogue is correct
whichever one ran last. Both used to be separate steps, and the tier one was
missing from these instructions: building the catalogue without it silently
reverted every Grind 75 question to the old `stretch` tier and 68 questions
vanished from the sidebar.

The self-test is the arbiter. If a question fails there, the question is wrong,
not the harness — that is how roughly two dozen wrong test cases were caught
while building this (an off-by-one in a hand-computed expected value, a
palindrome filtered incorrectly, a "no pair sums to zero" case that actually did).

## Adding a question

Append to `cbp/data/questions.json`:

```json
{
  "id": "my-question",
  "title": "My Question",
  "tier": "easy",
  "tags": ["string manipulation"],
  "patterns": ["two pointers"],
  "verified": true,
  "functionName": "MyQuestion",
  "expectedType": "string",
  "prompt": "Have the function MyQuestion(str) take ...",
  "signature": { "argNames": ["str"], "argTypes": ["string"] },
  "cases": [
    { "args": ["abc"], "expected": "cba", "expectedType": "string" }
  ],
  "solution": { "python": "...", "cpp": "...", "rust": "...", "csharp": "...", "java": "..." }
}
```

Then add two or three hints for it to `tools/hints.py` and run
`python3 tools/build_hints.py`, which validates the whole set and writes
`cbp/data/hints.json`. It fails on a question with no hints, on a hint for a
question that does not exist, and on a hint longer than a nudge is meant to be,
so a new question cannot be added without them.

Every question also needs a pattern. Add a line to `QUESTION_PATTERNS` in
`tools/patterns.py` — the builders refuse to write a catalogue where a question
has none, where a pattern is not in the vocabulary, or where the table names a
question that no longer exists. A pattern that the course teaches goes in
`MODULES` there (and in `PATTERN_MODULES` in `cbp/track.py`, which is what the
server reads; the two are checked against each other). A pattern with no module
still shows up as a chip; it just does not link.

Finally run `python3 -m cbp.selftest`. If a question fails there, the *question*
is wrong, not your code — that is how the two bad test cases in this repo's
early draft were caught.

## Later: one executable

The long-term goal is a single binary for macOS and Windows that someone can
double-click, with no Python install and no toolchain setup. Nothing here
blocks that, and a few decisions were made to keep it reachable:

- **The server is stdlib-only.** `cbp/server.py` has no third-party
  dependencies, so freezing the UI into a shipped binary needs no dependency
  resolution at all.
- **Toolchains are discovered at runtime, not assumed.** `cbp/adapters.py::_find`
  probes known install paths and then `PATH`, so a frozen binary still finds
  `rustc` and the JDK on the user's machine.
- **Data is plain JSON.** `cbp/data/*.json` can be embedded in the binary and
  read back out; it is never generated at runtime.

The realistic shape is a PyInstaller-style bundle for the Python side plus the
UI assets, with the five language toolchains left to the user's machine — the
app orchestrates compilers, it does not ship them.
