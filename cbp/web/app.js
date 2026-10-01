/* Praccy — app front end.
 *
 * Talks to the local API in cbp/server.py. The interface cannot compile C++,
 * C# or Java, so submission runs in a server-side subprocess; this file is
 * the interface, not the judge.
 *
 * Everything here is plain DOM. The only stateful thing worth naming is
 * `state`, and there are no third-party dependencies.
 */

const STORAGE_KEY = "cbp.progress.v1";
const RING_RADIUS = 15;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

const LANGUAGE_NAMES = { python: "Python", cpp: "C++", rust: "Rust", csharp: "C#", java: "Java" };

const state = {
  questions: [],
  languages: [],
  track: null,
  hintsShown: 0,
  view: "track",       // the course is the front door; practice is one click away
  current: null,        // full question payload
  solved: new Set(),    // question ids
  attempted: new Set(),
  best: {},             // question id -> fastest passing seconds
  days: [],             // "YYYY-MM-DD" on which something was solved
  celebrated: [],       // milestone counts already acknowledged
  sourceFilter: "",     // "" | "Coderbyte" | "LeetCode"
  xp: 0,
  achievements: [],     // achievement ids already earned
  startedAt: null,     // when the clock started; null while it is idle
  timerHandle: null,
  sheet: null,          // which panel is open: "trophies" | "sound"
  sheetOpener: null,    // the control to hand focus back to when it closes
  sound: Sound.settingsFor(),
  solutionLoaded: false,   // whether the reference solution is already in the DOM
};

const el = (id) => document.getElementById(id);

// ── persistence ────────────────────────────────────────────────

/* Progress goes through Store rather than straight to localStorage: the
   server's port is different every launch, so localStorage is scoped to an
   origin that does not outlive the session. Store mirrors it locally and syncs
   it to the settings file, which is what makes a solve survive a restart. */
function loadProgress() {
  const data = Store.json(STORAGE_KEY, null);
  if (!data) return;
  (data.solved || []).forEach((id) => state.solved.add(id));
  (data.attempted || []).forEach((id) => state.attempted.add(id));
  state.best = data.best || {};
  state.days = data.days || [];
  state.celebrated = data.celebrated || [];
  state.xp = data.xp || 0;
  state.achievements = data.achievements || [];
}

function saveProgress() {
  Store.set(STORAGE_KEY, JSON.stringify({
    solved: [...state.solved],
    attempted: [...state.attempted],
    best: state.best,
    days: state.days,
    celebrated: state.celebrated,
    xp: state.xp,
    achievements: state.achievements,
  }));
}

// ── appearance ─────────────────────────────────────────────────

/* Light or dark, and the choice is the user's rather than the system's.
 *
 * The stylesheet holds one block of tokens per appearance and switches between
 * them on an attribute on <html>, so the whole theme is one write and nothing
 * else on the page has to know which appearance is in force. The head script in
 * index.html sets that attribute before the first paint from the mirror in
 * localStorage, falling back to the system setting; this runs after the server
 * has answered, so the stored copy wins if the two ever disagree.
 *
 * The system is still listened to. With nothing stored the app follows macOS
 * when it changes at noon, and only the button pins it. */
const THEME_KEY = "cbp.theme";
const THEME_CANVAS = { light: "#edf0ec", dark: "#0e1618" };
const systemTheme = window.matchMedia("(prefers-color-scheme: light)");

function storedTheme() {
  const value = Store.get(THEME_KEY);
  return value === "light" || value === "dark" ? value : null;
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  // The window colour follows the appearance, so the chrome around the webview
  // is the same ground as the page rather than a dark band around a light one.
  const meta = document.getElementById("theme-color");
  if (meta) meta.content = THEME_CANVAS[theme];
  const button = el("theme-btn");
  if (button) {
    const next = theme === "dark" ? "light" : "dark";
    button.setAttribute("aria-label", `Switch to ${next} appearance`);
    button.title = `Switch to ${next} appearance`;
  }
}

function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  Store.set(THEME_KEY, next);
  applyTheme(next);
}

systemTheme.addEventListener("change", (event) => {
  if (!storedTheme()) applyTheme(event.matches ? "light" : "dark");
});

// ── boot ───────────────────────────────────────────────────────

async function init() {  // The store must hydrate before anything reads a preference: every launch is
  // a new origin, so the browser's copy is always empty and the server's
  // settings file is the only thing that persists. The sound module is
  // reloaded here because it parsed on its defaults.
  await Store.ready();
  state.sound = Sound.reload();
  applyTheme(storedTheme() || (systemTheme.matches ? "light" : "dark"));
  loadProgress();
  wireEvents();
  buildDrift();
  syncGutter();
  updateProgress();

  try {
    const res = await fetch("/api/questions");
    const data = await res.json();
    state.questions = data.questions;
    state.languages = data.languages;
  } catch (err) {
    showToast("Could not reach the local server. Is it running?");
    return;
  }

  // The track is optional: a failure here must not block practising.
  try {
    const trackRes = await fetch("/api/track");
    state.track = await trackRes.json();
  } catch (err) {
    state.track = null;
  }

  buildLanguageSelect();
  buildQuestionList();
  renderTrack();
  // Teaching first: the app opens on the course, so the first thing you see
  // is the material and where you are in it, not an empty editor. The practice
  // view is one click away and remembers nothing about how you got there.
  setView("track");
  updateProgress();
  // After the questions load, so the totals behind the trophies are real
  // rather than zero.
  updateScore();
  positionThumb();
  window.addEventListener("resize", positionThumb);
}

function buildLanguageSelect() {
  const select = el("language-select");
  select.innerHTML = "";
  state.languages.forEach((lang) => {
    const opt = document.createElement("option");
    opt.value = lang;
    opt.textContent = LANGUAGE_NAMES[lang] || lang;
    select.appendChild(opt);
  });
  const preferred = Store.get("cbp.lang");
  if (preferred && state.languages.includes(preferred)) select.value = preferred;
  else select.value = "python";
}

// ── progress, streak, bests ────────────────────────────────────

function dayKey(date) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/* A streak survives until you miss a whole day, so not solving *yet*
   today does not break yesterday's run. */
function currentStreak() {
  const days = new Set(state.days);
  if (!days.size) return 0;

  const cursor = new Date();
  if (!days.has(dayKey(cursor))) {
    cursor.setDate(cursor.getDate() - 1);
    if (!days.has(dayKey(cursor))) return 0;
  }

  let streak = 0;
  while (days.has(dayKey(cursor))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

function setRing(node, solved, total) {
  if (!node) return;
  const fraction = total ? solved / total : 0;
  node.style.strokeDasharray = RING_CIRCUMFERENCE;
  node.style.strokeDashoffset = RING_CIRCUMFERENCE * (1 - fraction);
}

function updateProgress() {
  const total = state.questions.length;
  const solved = state.solved.size;
  setRing(el("ring-fill"), solved, total);

  const chip = el("progress-chip");
  if (chip) chip.textContent = `${solved} of ${total}`;

  const welcome = el("welcome-count");
  if (welcome) {
    welcome.textContent = solved === 0
      ? `None of the ${total} solved yet`
      : solved === total
        ? `All ${total} solved`
        : `${solved} of ${total} solved`;
  }

  updateStreak();
}

function updateStreak() {
  const node = el("streak");
  const count = el("streak-count");
  if (!node || !count) return;
  const streak = currentStreak();
  // A zero streak is not a failure state, so it stays hidden until there
  // is genuinely something to keep.
  node.hidden = streak === 0;
  node.classList.toggle("lit", streak > 0);
  node.title = streak === 1
    ? "1 day in a row. Solve one tomorrow to make it 2."
    : `${streak} days in a row.`;
  count.textContent = streak;
  el("streak-label").textContent = streak === 1 ? "day streak" : "days in a row";
}

function recordSolve(questionId, seconds) {
  const wasSolved = state.solved.has(questionId);
  const previousBest = state.best[questionId];
  const question = state.questions.find((q) => q.id === questionId);

  // The points are settled before anything moves: they depend on whether this
  // solve was a repeat and on whether it beat the record, not on the state.
  const reward = rewardForSolve(state, state.questions, question || { tier: "easy" },
                                { wasSolved, isNewBest: false });
  const levelBefore = levelForXp(state.xp || 0);

  state.attempted.add(questionId);
  state.solved.add(questionId);

  // A time of zero means the answer was never typed, so it cannot be a
  // personal best for anything.
  const isNewBest = seconds > 0 && (!previousBest || seconds < previousBest);
  if (isNewBest) state.best[questionId] = seconds;

  const today = dayKey(new Date());
  if (!state.days.includes(today)) state.days.push(today);

  // The points land before the trophies are recomputed. That ordering is the
  // whole reason a trophy for reaching a level fires on the solve that crossed
  // the line rather than on the one after it, and several others ("first one",
  // "a week of this") are only true once the solve itself is recorded.
  state.xp += reward.points;
  const after = rewardForSolve(state, state.questions, question || { tier: "easy" },
                               { wasSolved, isNewBest });

  const fresh = after.unlocked.filter((a) => !state.achievements.includes(a.id));
  state.achievements.push(...fresh.map((a) => a.id));

  saveProgress();
  updateProgress();
  updateScore();
  return { wasSolved, isNewBest, points: reward.points, unlocked: fresh,
           levelBefore, levelAfter: levelForXp(state.xp) };
}

/* The scoreboard in the topbar: two readings with one number each.
 *
 * The level badge is what XP produces and the bar is how far the next one is;
 * the trophy count is what the levels and the milestones have earned so far.
 * The raw XP total used to sit here next to the badge, where it was a number
 * in a header with nothing to explain it -- which is why it read as doing
 * nothing. It is in the trophy panel now, on a labelled bar that says what the
 * next level costs. */
function updateScore() {
  const xp = state.xp || 0;
  const { level, ratio } = levelProgress(xp);
  const badge = el("level-badge");
  if (badge) {
    badge.textContent = String(level);
    el("level-fill").style.width = Math.round(ratio * 100) + "%";
    el("level-chip").title = `Level ${level}, ${levelTitle(level)}: ${xp} points.`;
  }
  const count = el("trophy-count");
  if (count) {
    count.textContent = `${state.achievements.length}/${ACHIEVEMENTS.length}`;
    const chip = el("trophy-chip");
    const earned = state.achievements.length;
    chip.title = `${earned} of ${ACHIEVEMENTS.length} trophies earned`;
    chip.classList.toggle("has-any", earned > 0);
    chip.classList.toggle("is-complete", earned === ACHIEVEMENTS.length);
  }
}

/* ── the panels ─────────────────────────────────────────────────
 * One sheet element, two things it can show. They share a shape -- a head, a
 * body, one Done button -- so they share the element and the CSS, and
 * `state.sheet` is what tells the handlers which one is open.
 *
 * Trophies first, because that is the one worth opening. */

function renderTrophies() {
  const xp = state.xp || 0;
  const done = levelProgress(xp);
  const next = Math.max(0, levelFloor(done.level + 1) - xp);
  const earned = state.achievements.length;

  return `
    <div class="sheet-head">
      <h2 id="sheet-title">Trophies</h2>
      <button class="sheet-close" id="sheet-close" type="button" data-sound="close">Done</button>
    </div>
    <p class="sheet-sub">${earned} of ${ACHIEVEMENTS.length} earned</p>

    <div class="level-block">
      <div class="level-block-head">
        <span class="level-block-badge">${done.level}</span>
        <span class="level-block-title">${escapeHtml(levelTitle(done.level))}</span>
        <span class="level-block-xp">${xp} xp</span>
      </div>
      <span class="level-block-bar" aria-hidden="true">
        <span class="level-block-fill" style="width:${Math.round(done.ratio * 100)}%"></span>
      </span>
      <p class="level-block-next">${next} more xp reaches level ${done.level + 1}.</p>
    </div>

    <ul class="achievement-list">
      ${ACHIEVEMENTS.map((a) => {
        const got = state.achievements.includes(a.id);
        return `
          <li class="achievement${got ? " earned" : ""}">
            <span class="achievement-mark" aria-hidden="true">${icon("i-trophy")}</span>
            <span class="achievement-text">
              <span class="achievement-name">${escapeHtml(a.name)}</span>
              <span class="achievement-hint">${escapeHtml(a.hint)}</span>
            </span>
            <span class="visually-hidden">${got ? "Earned" : "Not earned yet"}</span>
          </li>`;
      }).join("")}
    </ul>
  `;
}

/* The sound panel. Every switch previews the thing it controls as it comes on,
 * which is the only way to choose a sound without leaving the panel, and the
 * rows under the master switch are hidden while it is off so the panel opens
 * with one decision in it rather than five. */
const SOUND_ROWS = [
  ["typing", "Typing", "A soft click under every key"],
  ["ui", "Interface", "Buttons, panels and hints"],
  ["verdict", "Verdict", "A run passing or failing"],
  ["awards", "Trophies", "The moment one is earned"],
];

const SOUND_PREVIEWS = { typing: "key", ui: "toggle", verdict: "pass", awards: "trophy" };

/* The keyboard picker. It appears only while typing is switched on: choosing a
 * keyboard you have just silenced is a decision with no consequence, and a
 * settings panel should not offer those.
 *
 * The note under the options describes the pack that is selected rather than
 * sitting on each option, which keeps the row short enough that both names fit
 * and keeps the panel from reading as a wall of small print. */
function renderPacks() {
  const packs = Sound.packs();
  const current = packs.find((p) => p.id === state.sound.pack) || packs[0];
  return `
    <div class="pack" role="group" aria-label="Typing sound">
      <div class="pack-options">
        ${packs.map((p) => `
          <button class="pack-option${p.id === current.id ? " is-active" : ""}" type="button"
                  data-pack="${p.id}" aria-pressed="${p.id === current.id}">${escapeHtml(p.name)}</button>`).join("")}
      </div>
      <p class="pack-note">${escapeHtml(current.note)}</p>
    </div>`;
}

function renderSound() {
  const s = state.sound;
  const row = (key, name, note) => `
    <button class="switch" type="button" role="switch" data-setting="${key}"
            aria-checked="${s[key] ? "true" : "false"}">
      <span class="switch-text">
        <span class="switch-name">${escapeHtml(name)}</span>
        <span class="switch-note">${escapeHtml(note)}</span>
      </span>
      <span class="switch-track" aria-hidden="true"><span class="switch-thumb"></span></span>
    </button>`;

  return `
    <div class="sheet-head">
      <h2 id="sheet-title">Sound</h2>
      <button class="sheet-close" id="sheet-close" type="button" data-sound="close">Done</button>
    </div>
    ${Sound.available() ? "" :
      '<p class="sheet-sub">This build cannot play audio, so nothing here will work.</p>'}
    ${row("on", "Sound effects", "Off until you turn it on")}
    <div class="setting-group"${s.on ? "" : " hidden"}>
      ${SOUND_ROWS.map(([key, name, note]) =>
        row(key, name, note) + (key === "typing" && s.typing ? renderPacks() : "")
      ).join("")}
      <label class="volume">
        <span class="switch-name">Volume</span>
        <input type="range" id="sound-volume" min="0" max="1" step="0.05"
               value="${s.volume}" aria-label="Volume">
      </label>
    </div>
    <p class="sheet-foot">Generated on this Mac by tools/build_sounds.py, so
      there is nothing to license and nothing downloaded. Nothing you type
      leaves the app.</p>
  `;
}

const SHEETS = { trophies: renderTrophies, sound: renderSound };

function openSheet(kind) {
  state.sheet = SHEETS[kind] ? kind : "trophies";
  // Remembered so closing puts focus back where it came from, which matters
  // more now that two buttons open this.
  state.sheetOpener = document.activeElement;
  const sheet = el("sheet");
  // A close that is still in flight must not leave its animation on the panel
  // that is about to open.
  sheet.classList.remove("is-closing");
  sheet.innerHTML = SHEETS[state.sheet]();
  sheet.hidden = false;
  document.body.classList.add("sheet-open");
  Sound.play("open");
  el("sheet-close").focus();
}

/* Every panel leaves the same way it arrives.
 *
 * Done used to hide the sheet in the same frame as the press, so the panel you
 * had just dismissed blinked out and the open animation never had a matching
 * one. Now the class goes on, the panel slides down, and the element is only
 * hidden once the animation has actually ended. The timeout is a backstop for
 * an animationend that never arrives -- a backgrounded tab does not paint, and
 * a panel stuck open is worse than a panel that closed without ceremony. */
function closeSheet() {
  const sheet = el("sheet");
  if (sheet.hidden) return;
  const opener = state.sheetOpener;
  state.sheetOpener = null;
  document.body.classList.remove("sheet-open");

  const finish = () => {
    sheet.hidden = true;
    sheet.classList.remove("is-closing");
    if (opener && opener.focus) opener.focus();
  };

  if (REDUCED_MOTION) {
    finish();
    return;
  }

  let settled = false;
  const once = (event) => {
    // The open animation can still be running when Done is pressed quickly.
    // Only the close is allowed to finish the job.
    if (event && event.animationName && event.animationName !== "sheet-down") return;
    if (settled) return;
    settled = true;
    sheet.removeEventListener("animationend", once);
    finish();
  };
  sheet.classList.add("is-closing");
  sheet.addEventListener("animationend", once);
  window.setTimeout(once, 340);
}

/* Flip one switch. The panel is re-rendered rather than patched, because five
 * rows of static markup do not need a diff, and focus is put back on the
 * switch that was just pressed so the keyboard does not lose its place. */
function toggleSetting(key) {
  const turningOn = !state.sound[key];
  const ok = Sound.update({ [key]: turningOn });
  state.sound = Sound.settingsFor();
  el("sheet").innerHTML = SHEETS[state.sheet]();
  const again = el("sheet").querySelector(`.switch[data-setting="${key}"]`);
  if (again) again.focus();
  if (ok && turningOn) Sound.play(key === "on" ? "toggle" : SOUND_PREVIEWS[key]);
  if (!ok) showToast("This build has no audio available.");
}

/* Swap the keyboard. The panel is re-rendered so the note under the picker
 * describes the pack that is now selected, and the new pack plays straight
 * away -- there is no way to choose a sound except by hearing it, and one
 * keystroke is enough to tell the two apart. */
function choosePack(id) {
  Sound.update({ pack: id });
  state.sound = Sound.settingsFor();
  el("sheet").innerHTML = SHEETS[state.sheet]();
  const again = el("sheet").querySelector(`.pack-option[data-pack="${id}"]`);
  if (again) again.focus();
  Sound.play("key");
}

function renderBest(node, id) {
  if (!node) return;
  const record = state.best[id];
  node.hidden = !record;
  if (record) node.textContent = `Best ${formatDuration(record)}`;
}

function celebrate(result) {
  // The ring takes the hit, so nothing else needs to.
  const ring = el("ring-fill");
  if (ring) {
    ring.classList.remove("ring-accept");
    void ring.getBoundingClientRect();   // restart the animation
    ring.classList.add("ring-accept");
  }

  const streak = el("streak");
  if (streak && !streak.hidden) {
    streak.classList.remove("streak-pop");
    void streak.getBoundingClientRect();
    streak.classList.add("streak-pop");
  }

  const dot = document.querySelector(`.question-item[data-id="${result.id}"] .qi-dot`);
  if (dot) {
    dot.classList.add("just-solved");
    setTimeout(() => dot.classList.remove("just-solved"), 600);
  }

  // The shard burst fires from the result box, which is the thing that just
  // changed. It is the loudest moment in the app and it is reserved for a
  // genuine pass, so it never fires on a failure or a repeat.
  const result_box = el("result");
  if (result_box) burst(result_box);
}

// ── question list ──────────────────────────────────────────────

function buildQuestionList(filter = "", keepScroll = false) {
  const nav = el("question-list");
  // Rebuilding the list empties the nav, and a container with no content has
  // nothing to scroll, so the layout clamps scrollTop to 0 before the rows go
  // back in. Selecting a question called this on every click, which threw the
  // list back to the top each time. Saving and restoring is the whole fix.
  const previous = keepScroll ? nav.scrollTop : 0;
  nav.innerHTML = "";
  const needle = filter.trim().toLowerCase();
  const source = state.sourceFilter;

  const matches = (q) =>
    (!source || q.source === source) &&
    (!needle || q.title.toLowerCase().includes(needle) ||
      q.tags.some((t) => t.toLowerCase().includes(needle)) ||
      (q.patterns || []).some((p) => p.toLowerCase().includes(needle)));

  // Difficulty is the only grouping. Where a question came from is a filter
  // and a badge on the row, not a heading of its own.
  const tiers = ["easy", "medium", "hard"];
  tiers.forEach((tier) => {
    const items = state.questions.filter((q) => q.tier === tier && matches(q));
    if (!items.length) return;

    const heading = document.createElement("div");
    heading.className = "tier-heading";
    const total = state.questions.filter(
      (q) => q.tier === tier && (!source || q.source === source)
    ).length;
    heading.append(
      document.createTextNode(tier[0].toUpperCase() + tier.slice(1) + " "),
      Object.assign(document.createElement("span"), {
        className: "tier-count",
        textContent: String(total),
      })
    );
    nav.appendChild(heading);

    items.forEach((q) => nav.appendChild(questionButton(q)));
  });

  if (!nav.children.length) {
    const empty = document.createElement("p");
    empty.className = "pane-empty";
    empty.textContent = `Nothing matches “${filter.trim()}”.`;
    nav.appendChild(empty);
  }

  if (keepScroll && previous) nav.scrollTop = previous;
}

function questionButton(q) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "question-item";
  if (state.current && state.current.id === q.id) btn.classList.add("active");
  btn.dataset.id = q.id;

  const dot = document.createElement("span");
  dot.className = "qi-dot";
  if (state.solved.has(q.id)) {
    dot.classList.add("solved");
    dot.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>';
  } else if (state.attempted.has(q.id)) {
    dot.classList.add("failed");
  }

  const title = document.createElement("span");
  title.className = "qi-title";
  title.textContent = q.title;

  // A small monogram rather than the word: the column is narrow, and C for
  // Coderbyte against L for LeetCode is readable at this size.
  const mark = document.createElement("span");
  mark.className = "qi-source qi-source-" + (q.source || "coderbyte").toLowerCase();
  mark.textContent = q.source === "LeetCode" ? "L" : "C";
  mark.title = q.source === "LeetCode"
    ? `LeetCode${q.sourceId ? " " + q.sourceId : ""}`
    : "Coderbyte";

  btn.append(dot, title, mark);
  btn.addEventListener("click", () => openQuestion(q.id));
  return btn;
}

function refreshSidebar() {
  buildQuestionList(el("filter-input").value, true);
}

// ── question pane ──────────────────────────────────────────────

async function openQuestion(id) {
  let question;
  try {
    const res = await fetch(`/api/question/${id}`);
    question = await res.json();
  } catch (err) {
    showToast("Could not load that question.");
    return;
  }

  state.current = question;
  el("pane-empty").hidden = true;
  el("question").hidden = false;

  const index = state.questions.findIndex((q) => q.id === id);
  el("question-position").textContent =
    index >= 0 ? `Question ${index + 1} of ${state.questions.length}` : "";

  el("question-title").textContent = question.title;

  const tier = el("question-tier");
  tier.textContent = question.tier[0].toUpperCase() + question.tier.slice(1);
  tier.classList.toggle("meta-hard", question.tier === "hard");

  // The source is a coloured badge now, in the same colour the sidebar filter
  // chip and the list monogram use for that source, so "where did this come
  // from" reads the same in all three places.
  const source = el("question-source");
  source.hidden = !question.source;
  source.classList.toggle("is-coderbyte", question.source === "Coderbyte");
  source.classList.toggle("is-leetcode", question.source === "LeetCode");
  if (question.source) {
    source.textContent = `${question.source}${
      question.sourceId ? " " + question.sourceId : ""
    }`;
  }

  const best = el("question-best");
  renderBest(best, id);

  renderHints(question);
  renderPatterns(question);

  el("question-prompt").textContent = question.prompt;

  const args = question.signature.argNames.join(", ");
  el("question-signature").textContent = `${question.functionName}(${args})`;

  const contract = el("question-contract");
  contract.textContent = typeLabel(question.expectedType);

  const note = el("question-note");
  note.hidden = !question.note;
  note.textContent = question.note || "";

  const list = el("examples-body");
  list.innerHTML = "";
  question.examples.forEach((ex, index) => {
    const item = document.createElement("li");
    item.className = "example";
    item.innerHTML =
      `<div class="example-head"><span class="example-num">Example ${index + 1}</span></div>` +
      `<div class="example-io">` +
      `<span class="example-key">Input</span>` +
      `<span class="example-val">${escapeHtml(ex.args.map((a) => formatArg(a)).join(", "))}</span>` +
      `<span class="example-key">Output</span>` +
      `<span class="example-val example-out">${escapeHtml(ex.expected)}` +
      `<span class="example-type">${escapeHtml(ex.expectedType)}</span></span>` +
      `</div>`;
    list.appendChild(item);
  });

  // Examples stay out of the way only if you asked them to, and the choice
  // holds across questions, because the reason to hide them is that you have
  // got the shape, and that does not change when the question does.
  applyExamplesState(readHiddenExamples());

  el("editor-label").textContent = `Your ${languageLabel()} code`;
  el("editor").value = starterFor(question);
  el("result").hidden = true;
  el("lesson").hidden = true;
  el("solution-block").open = false;
  clearSolution();
  syncGutter();

  // The clock is re-armed here, idle: it starts on the first keystroke.
  resetTimer();
  refreshSidebar();
  el("pane").scrollTop = 0;

  // A short slide-and-fade as the question arrives, so moving through the
  // list feels like turning a page rather than a jump cut. It plays on every
  // navigation including prev/next, and is skipped under reduced motion.
  if (!REDUCED_MOTION) {
    replay(el("question"), "question-in");
  }
}

const HIDDEN_EXAMPLES_KEY = "cbp.examples.hidden";

function readHiddenExamples() {
  return Store.get(HIDDEN_EXAMPLES_KEY) === "1";
}

/* One control, and it stays where it is. The examples header is always on
 * screen; only the list inside it collapses. The header used to disappear with
 * the list and a separate "Show examples" button appear in its place, so the
 * second click landed somewhere else on the page than the first.
 *
 * The state word is a child span rather than the button's own text, because
 * the button now also contains the label: setting `textContent` on it would
 * take "Examples" with it. `is-collapsed` on the block is what the collapsed
 * card's bottom padding hangs off, so the space the list had does not stay
 * behind as an empty strip. */
function applyExamplesState(hidden) {
  el("examples-body").hidden = hidden;
  const toggle = el("examples-toggle");
  el("examples-state").textContent = hidden ? "Show" : "Hide";
  el("examples-block").classList.toggle("is-collapsed", hidden);
  toggle.setAttribute("aria-expanded", String(!hidden));
  toggle.setAttribute("aria-label", hidden ? "Show the examples" : "Hide the examples");
}

function setExamplesHidden(hidden) {
  Store.set(HIDDEN_EXAMPLES_KEY, hidden ? "1" : "0");
  applyExamplesState(hidden);
}

/* ── hint ─────────────────────────────────────────────────────
 * Every question carries two or three hints, written for it and shipped in
 * cbp/data/hints.json. They are revealed one at a time rather than all at
 * once, because the first one is usually enough and there is no way to
 * un-read the second. The count is on the label before the first reveal, so
 * you can see how much help is on offer before spending any of it.
 *
 * The count is deliberately not persisted: reopening a question starts with
 * nothing revealed, so a hint is something you asked for during this attempt
 * rather than a permanent label on the question. */

/* Inline markup, in one place because two features are written in it.
 *
 * Exactly two spans carry meaning: `code` around a fragment that is literally
 * code, and **emphasis** around the term a sentence is about. Everything else
 * is text. That is why this is two substitutions rather than a markdown
 * parser -- a richer language would be a second thing to learn, and neither
 * the hints nor the course need one.
 *
 * Escaping happens first and the tags are inserted after, so nothing an author
 * writes can arrive as markup. The substitutions run on escaped text, which is
 * also why they cannot be fooled by a `<` inside a code span. */
function inlineMarkup(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function renderHints(question) {
  const hints = question.hints || [];
  // Nothing is revealed on arrival, so the block starts empty and out of the
  // layout: the trigger above the editor is the whole of the hint until you
  // spend one.
  el("hint-block").hidden = true;
  el("hint-list").innerHTML = "";
  el("hint-count").textContent = hints.length ? `0 of ${hints.length}` : "";
  const ask = el("hint-ask");
  el("hint-ask-text").textContent = "Show a hint";
  ask.disabled = hints.length === 0;
  ask.setAttribute("aria-expanded", "false");
  state.hintsShown = 0;
}

function showNextHint() {
  const hints = (state.current && state.current.hints) || [];
  const index = state.hintsShown;
  if (index >= hints.length) return;

  // Revealing the first one is what puts the block above the editor on screen.
  el("hint-block").hidden = false;

  const item = document.createElement("li");
  item.className = "hint-item is-new";
  item.innerHTML =
    `<span class="hint-num" aria-hidden="true">${index + 1}</span>` +
    `<span class="hint-text">${inlineMarkup(hints[index])}</span>`;
  el("hint-list").appendChild(item);

  state.hintsShown = index + 1;
  const spent = state.hintsShown >= hints.length;
  el("hint-count").textContent = `${state.hintsShown} of ${hints.length}`;
  const ask = el("hint-ask");
  el("hint-ask-text").textContent = spent ? "All hints shown" : "Another hint";
  ask.setAttribute("aria-expanded", "true");
  ask.disabled = spent;
}

/* ── patterns ─────────────────────────────────────────────────
 * The techniques a question is built from. These words used to be printed
 * under the title, which told you the shape of the answer before you had read
 * the question; they are now the last thing on the page, and covered until you
 * ask for them.
 *
 * They come from `patterns` rather than `tags`. The tags were free text and
 * rotted into topics -- "algorithm" was on 96 of the 144 questions, and
 * "math fundamentals" is a school subject, not something you can do. The
 * patterns are a closed vocabulary, assigned per question in
 * tools/patterns.py and checked at build time, so every chip names a technique
 * and every question has at least one.
 *
 * The ones the course teaches link into it. That mapping is a table in
 * cbp/track.py that ships with the course payload, not something guessed here.
 * A pattern with no module -- "arithmetic", "single pass" -- has no lesson
 * behind it, so it stays a plain chip rather than a link that goes nowhere.
 * That difference is what the row is telling you. */

function titleCase(tag) {
  return tag.replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
}

function patternModuleFor(tag) {
  const links = (state.track && state.track.patternModules) || {};
  return links[tag.toLowerCase()] || "";
}

function renderPatterns(question) {
  const tags = question.patterns || [];
  const block = el("patterns-block");
  block.hidden = tags.length === 0;
  // Every question starts with the row covered again. The reveal is a decision
  // about this question, not a setting that follows you around.
  block.classList.remove("is-revealed", "is-shining");
  el("patterns-reveal").setAttribute("aria-expanded", "false");
  el("patterns-hint").textContent = "Reveal";

  const list = el("pattern-list");
  list.innerHTML = "";
  tags.forEach((tag) => {
    const moduleId = patternModuleFor(tag);
    const item = document.createElement("li");
    if (moduleId) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "pattern is-linked";
      button.dataset.module = moduleId;
      button.title = "Open the module that teaches this";
      button.innerHTML = `${escapeHtml(titleCase(tag))}${icon("i-chevron")}`;
      item.appendChild(button);
    } else {
      const chip = document.createElement("span");
      chip.className = "pattern";
      chip.textContent = titleCase(tag);
      item.appendChild(chip);
    }
    list.appendChild(item);
  });
}

/* Uncover the pattern row. The chips are blurred and inert until this runs, so
 * the words that name the technique cannot be read off the screen before the
 * question has been thought about. The shine is one sweep across the row, once:
 * it is the sound of the cover coming off, not a decoration that lives there. */
function revealPatterns() {
  const block = el("patterns-block");
  if (!block || block.hidden || block.classList.contains("is-revealed")) return;
  block.classList.add("is-revealed", "is-shining");
  el("patterns-reveal").setAttribute("aria-expanded", "true");
  el("patterns-hint").textContent = "Shown";
  window.setTimeout(() => block.classList.remove("is-shining"), 900);
}

/* Follow a pattern chip into the course: change view, open the module, land on
   it. The scroll and the flash are the difference between a link that works
   and a link that looks like it did nothing, because the module it opened is
   two screens above where you were. */
function openModule(moduleId) {
  setView("track");
  const module = document.querySelector(`.module[data-module="${moduleId}"]`);
  if (!module) return;
  module.open = true;
  module.scrollIntoView({ behavior: REDUCED_MOTION ? "auto" : "smooth", block: "center" });
  // Restart the animation when the same chip is pressed twice: the class has
  // to come off and the layout be read before it goes back on.
  module.classList.remove("is-flashing");
  void module.offsetWidth;
  module.classList.add("is-flashing");
  window.setTimeout(() => module.classList.remove("is-flashing"), 1600);
}

function languageLabel() {
  const lang = el("language-select").value;
  return LANGUAGE_NAMES[lang] || lang;
}

function formatArg(value) {
  if (typeof value === "string") return `"${value}"`;
  if (Array.isArray(value)) return "[" + value.map(formatArg).join(", ") + "]";
  return String(value);
}

/* Contract type names, spelled for a sentence. The bare names are for the
   code; these are for the reader. */
const TYPE_LABELS = {
  string: "string", int: "int", float: "float", bool: "bool",
  array: "list of numbers", stri: "list of strings", list: "linked list",
  tree: "tree", matrix: "matrix", graph: "graph",
  charmatrix: "grid of characters", strarray: "list of words",
  strmatrix: "rows of words",
};
const typeLabel = (t) => TYPE_LABELS[t] || t;

/* The resolved argument types, which distinguish int[] from string[] where
   the stored signature cannot. */
const argTypesOf = (q) => q.argTypes || q.signature.argTypes;

/* A minimal starting point, not a solution. */
function starterFor(q) {
  const name = q.functionName;
  const args = q.signature.argNames.join(", ");
  const ret = cppType(q.expectedType);
  // A tree is a vector of optionals, and optional is not in the headers
  // the other starters already carry.
  const extraIncludes = argTypesOf(q).includes("tree") || q.expectedType === "tree"
    ? "#include <optional>\n"
    : "";

  switch (el("language-select").value) {
    case "cpp":
      return `#include <iostream>\n#include <string>\n#include <vector>\n${extraIncludes}using namespace std;\n\n${ret} ${name}(${argTypesOf(q).map((t, i) => `${cppType(t)} ${q.signature.argNames[i]}`).join(", ")}) {\n    // your code here\n}\n`;
    case "csharp":
      return `using System;\nusing System.Linq;\n\npublic class Solution\n{\n    public static ${csType(q.expectedType)} ${name}(${argTypesOf(q).map((t, i) => `${csType(t)} ${q.signature.argNames[i]}`).join(", ")})\n    {\n        // your code here\n    }\n}\n`;
    case "java":
      return `public class Solution {\n    public static ${javaType(q.expectedType)} ${name.charAt(0).toLowerCase()}${name.slice(1)}(${argTypesOf(q).map((t, i) => `${javaType(t)} ${q.signature.argNames[i]}`).join(", ")}) {\n        // your code here\n    }\n}\n`;
    case "rust":
      return `impl Solution {\n    pub fn ${rustName(name)}(${argTypesOf(q).map((t, i) => `${q.signature.argNames[i]}: ${rustArgType(t)}`).join(", ")}) -> ${q.polymorphic ? "CBResult" : rustReturnType(q.expectedType)} {\n        // your code here\n    }\n}\n`;
    default:
      return `def ${name}(${args}):\n    # your code here\n    pass\n`;
  }
}

/* Coderbyte's PascalCase name to Rust's snake_case, matching the adapter's
   _rust_method so the starter and the harness agree: ABCheck -> ab_check. */
function rustName(name) {
  let out = "";
  for (let i = 0; i < name.length; i++) {
    const c = name[i];
    if (c === c.toUpperCase() && c !== c.toLowerCase() && i > 0) {
      const prev = name[i - 1];
      const next = name[i + 1] || "";
      const isUpper = (ch) => ch !== ch.toLowerCase() && ch === ch.toUpperCase();
      const prevIsLower = prev === prev.toLowerCase() && !isUpper(prev);
      const prevIsDigit = prev >= "0" && prev <= "9";
      const nextIsLower = next === next.toLowerCase() && !isUpper(next);
      if (prevIsLower || prevIsDigit || (isUpper(prev) && nextIsLower)) out += "_";
    }
    out += c.toLowerCase();
  }
  return out;
}

const cppType = (t) => ({ string: "string", int: "int", float: "double", bool: "bool", array: "vector<int>", stri: "vector<string>", list: "vector<int>", tree: "vector<optional<int>>", matrix: "vector<vector<int>>", graph: "vector<vector<int>>", charmatrix: "vector<vector<string>>", strmatrix: "vector<vector<string>>", strarray: "vector<string>" }[t] || t);
const csType = (t) => ({ string: "string", int: "int", float: "double", bool: "bool", array: "int[]", stri: "string[]", list: "int[]", tree: "int?[]", matrix: "int[][]", graph: "int[][]", charmatrix: "string[][]", strmatrix: "string[][]", strarray: "string[]" }[t] || t);
const javaType = (t) => ({ string: "String", int: "int", float: "double", bool: "boolean", array: "int[]", stri: "String[]", list: "int[]", tree: "Integer[]", matrix: "int[][]", graph: "int[][]", charmatrix: "String[][]", strmatrix: "String[][]", strarray: "String[]" }[t] || t);
/* Rust borrows a string argument but owns one on the way out, so the two
   directions need separate tables. */
const rustArgType = (t) => ({ string: "&str", int: "i64", float: "f64", bool: "bool", array: "Vec<i64>", stri: "Vec<String>", list: "Vec<i64>", tree: "Vec<Option<i64>>", matrix: "Vec<Vec<i64>>", graph: "Vec<Vec<i64>>", charmatrix: "Vec<Vec<String>>", strmatrix: "Vec<Vec<String>>", strarray: "Vec<String>" }[t] || t);
const rustReturnType = (t) => ({ string: "String", int: "i64", float: "f64", bool: "bool", array: "Vec<i64>", list: "Vec<i64>", tree: "Vec<Option<i64>>", matrix: "Vec<Vec<i64>>", graph: "Vec<Vec<i64>>", charmatrix: "Vec<Vec<String>>", strmatrix: "Vec<Vec<String>>", strarray: "Vec<String>" }[t] || t);

// ── submission ─────────────────────────────────────────────────

async function submit() {
  const code = el("editor").value;
  if (!code.trim()) {
    showToast("Write some code first.");
    return;
  }
  if (!state.current) return;

  const btn = el("submit-btn");
  const label = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Running…';
  el("result").classList.add("running");

  const language = el("language-select").value;
  // A snapshot, not a stop. The clock keeps running through a failure on
  // purpose; this is the reading at the moment of the submission, which is
  // what the verdict and the best-time record want.
  const elapsed = timerSeconds();

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId: state.current.id, language, code }),
    });
    const data = await res.json();

    if (data.ok) {
      // A pass ends the question, so the clock does too.
      announceSolve(recordSolve(state.current.id, elapsed), elapsed);
      resetTimer();
    } else {
      state.attempted.add(state.current.id);
      saveProgress();
    }

    renderResult(data, elapsed);
    renderBest(el("question-best"), state.current.id);
    refreshSidebar();
    if (state.view === "track") renderTrack();
    // The result lands below the fold on a long question, and a verdict you
    // have to go looking for is not feedback.
    el("result").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showToast("Request failed. Is the server still running?");
  } finally {
    btn.disabled = false;
    btn.innerHTML = label;
    el("result").classList.remove("running");
  }
}

function announceSolve(outcome, elapsed) {
  celebrate({ id: state.current.id });

  // The points line, always. It is the immediate answer to "what did that get
  // me", and it is the thing that makes the next question feel worth starting.
  const bits = [`+${outcome.points} xp`];
  if (outcome.isNewBest && elapsed > 0) bits.push("a new best");
  if (outcome.levelAfter > outcome.levelBefore) {
    bits.push(`level ${outcome.levelAfter}`);
  }
  showToast(`${bits.join(", ")}. Solved in ${formatDuration(elapsed)}.`);

  // Trophies land a beat later, one at a time, so a question that earns two of
  // them does not fire two messages on top of each other. The sound goes with
  // the toast rather than with the solve, so what you hear lines up with what
  // you are reading.
  outcome.unlocked.forEach((trophy, index) => {
    setTimeout(() => {
      showToast(`Trophy: ${trophy.name}. ${trophy.hint}.`, 4200);
      Sound.play("trophy");
    }, 900 + index * 700);
  });

  if (outcome.levelAfter > outcome.levelBefore) {
    const chip = el("level-chip");
    if (chip) {
      chip.classList.remove("level-up");
      void chip.getBoundingClientRect();
      chip.classList.add("level-up");
    }
    // A level with no trophy attached only gets the softer cue, and it waits
    // for the trophy toasts to finish so two sounds never overlap.
    if (outcome.unlocked.length === 0) {
      setTimeout(() => Sound.play("cue"), 900);
    }
  }
}

function renderResult(data, elapsed) {
  const box = el("result");
  box.hidden = false;
  box.className = "result " + (data.error ? "error" : data.ok ? "pass" : "fail");

  // The verdict, before the markup, so the sound and the colour arrive
  // together. A harness failure gets the fail sound: something went wrong and
  // the user has to do something about it either way.
  Sound.play(data.ok ? "pass" : "fail");
  box.innerHTML = "";

  // A miss gets a short shake, a hit does not. The shake is the difference
  // between "your code is wrong, here is why" and "something happened" -- it
  // reads as feedback rather than a bug, and it is suppressed for reduced
  // motion. It fires after a frame so the class lands on a laid-out box.
  if (!data.ok && !REDUCED_MOTION) {
    requestAnimationFrame(() => replay(box, "shake"));
  }

  const head = document.createElement("div");
  head.className = "result-head";

  const time = `<span class="head-time">${formatDuration(elapsed)}</span>`;
  if (data.error) {
    const label = { compile: "Does not compile", runtime: "Crashed", timeout: "Timed out", interface: "Harness problem" }[data.error.kind] || "Error";
    head.innerHTML = icon("i-x") + escapeHtml(label) + time;
  } else if (data.ok) {
    head.innerHTML = icon("i-check") + `All ${data.totalCount} test cases passed` + time;
  } else {
    head.innerHTML = icon("i-x") + `${data.passedCount} of ${data.totalCount} passed` + time;
  }
  box.appendChild(head);

  if (data.error) {
    const log = document.createElement("div");
    log.className = "error-log";
    log.textContent = data.error.message;
    box.appendChild(log);
    return;
  }

  const list = document.createElement("div");
  list.className = "case-list";

  data.cases.forEach((c) => {
    const row = document.createElement("div");
    row.className = "case " + (c.passed ? "pass" : "fail");

    const verdict = document.createElement("div");
    verdict.className = "case-verdict";
    verdict.innerHTML = icon(c.passed ? "i-check" : "i-x") +
      `<span>${c.passed ? "pass" : "fail"}</span>`;
    row.appendChild(verdict);

    row.appendChild(line("input", c.args.map(formatArg).join(", ")));
    row.appendChild(valueLine("expected", c.expected, "expected"));
    if (!c.passed) row.appendChild(valueLine("you", c.actual, "actual-fail"));

    if (!c.passed && c.detail) {
      const detail = document.createElement("div");
      detail.className = "case-detail";
      detail.textContent = c.detail;
      row.appendChild(detail);
    }
    if (!c.passed && c.advice) {
      const advice = document.createElement("div");
      advice.className = "case-advice";
      advice.textContent = c.advice;
      row.appendChild(advice);
    }
    list.appendChild(row);
  });

  box.appendChild(list);

  // A lesson is shown whenever the attempt failed.
  if (!data.ok && data.lesson) {
    const lesson = el("lesson");
    lesson.hidden = false;
    lesson.textContent = data.lesson;
  } else {
    el("lesson").hidden = true;
  }
}

function icon(name) {
  return `<svg class="icon" aria-hidden="true" focusable="false"><use href="#${name}"/></svg>`;
}

function line(label, value) {
  const div = document.createElement("div");
  div.className = "case-line";
  div.innerHTML =
    `<span class="case-label">${escapeHtml(label)}</span>` +
    `<span class="case-value">${escapeHtml(value)}</span>`;
  return div;
}

function valueLine(label, value, cls) {
  const div = document.createElement("div");
  div.className = "case-line";
  div.innerHTML =
    `<span class="case-label">${escapeHtml(label)}</span>` +
    `<span class="case-value ${cls}">${escapeHtml(value === null ? "nothing" : value)}</span>`;
  return div;
}

function formatDuration(seconds) {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds - m * 60;
  return `${m}m ${s.toFixed(1).padStart(4, "0")}s`;
}

/* ── the clock ────────────────────────────────────────────────────
 * Deliberately NOT started by opening the question. Reading the prompt and
 * the examples is thinking time, and that is yours to spend; the clock is
 * here to measure writing code. It starts on the first change to the answer.
 *
 * A failed submission does not touch it. The clock measures how long the
 * question took, and a question is not finished because one answer was wrong;
 * it stopped at the first submit that did not solve, so every later attempt
 * was handed a fresh clock and the time you spent on the failed one was
 * thrown away. It runs straight through a miss now, and the number under the
 * timer keeps climbing while you read the failure and fix it, which is the
 * honest reading: all of that was spent on this question.
 *
 * Two things stop it. A pass, because the question is over and the number is
 * recorded as your best, and Reset, because you have said you are starting
 * that question over.
 */
function startTimer() {
  if (state.startedAt) return;
  state.startedAt = Date.now();
  if (!state.timerHandle) state.timerHandle = setInterval(renderTimer, 100);
  renderTimer();
}

function resetTimer() {
  if (state.timerHandle) {
    clearInterval(state.timerHandle);
    state.timerHandle = null;
  }
  state.startedAt = null;
  renderTimer();
}

function timerSeconds() {
  return state.startedAt ? (Date.now() - state.startedAt) / 1000 : 0;
}

function renderTimer() {
  const node = el("question-timer");
  if (!node) return;
  if (!state.current) {
    node.hidden = true;
    return;
  }
  node.hidden = false;
  const seconds = timerSeconds();
  el("question-timer-text").textContent = formatDuration(seconds);
  node.classList.toggle("running", !!state.startedAt);
  node.classList.toggle("stopped", !state.startedAt);
}

// ── solution ───────────────────────────────────────────────────

/* Fetched on the first open, not on the render: the answer is the last resort
 * on the page now, and a question you never give up on should not cost a
 * request to keep it closed.
 *
 * The cache was keyed on nothing at all, which was the bug. `solutionLoaded`
 * was only cleared by a language change when the disclosure happened to be
 * open at that moment, so the ordinary sequence -- open the solution, read it,
 * change the language, come back to it -- found the cache still warm and showed
 * the previous language's code beside an editor full of another one. Clearing
 * it belongs to the language change itself, open or not.
 */
function clearSolution() {
  state.solutionLoaded = false;
  el("solution-code").textContent = "";
}

async function loadSolution() {
  if (!state.current || state.solutionLoaded) return;
  state.solutionLoaded = true;
  // Captured here rather than read on arrival. A language change or a move to
  // another question while this is in flight makes the answer the wrong one,
  // and whoever wanted the right one has already asked for it.
  const id = state.current.id;
  const language = el("language-select").value;
  try {
    const res = await fetch(`/api/question/${id}?solution=1`);
    const question = await res.json();
    if (state.current.id !== id || el("language-select").value !== language) return;
    el("solution-code").textContent =
      question.solution[language] || "(no solution in this language)";
  } catch (err) {
    state.solutionLoaded = false;
    showToast("Could not load the reference solution.");
  }
}

// ── editor helpers ─────────────────────────────────────────────

function syncGutter() {
  const editor = el("editor");
  const lines = editor.value.split("\n").length;
  el("gutter").textContent = Array.from({ length: lines }, (_, i) => i + 1).join("\n");
  el("gutter").scrollTop = editor.scrollTop;
}

function insertAtCursor(text) {
  const editor = el("editor");
  const start = editor.selectionStart;
  const end = editor.selectionEnd;
  editor.value = editor.value.slice(0, start) + text + editor.value.slice(end);
  editor.selectionStart = editor.selectionEnd = start + text.length;
}

/* Any change to the answer starts the clock. Tab and Enter are handled in
 * keydown and rewrite the value directly, so they never fire `input` and
 * have to call this themselves -- otherwise a first keystroke of Tab would
 * leave the timer sitting at zero. */
function noteEdit() {
  syncGutter();
  startTimer();
}

/* Which of the three keyboard samples a keypress gets, if any.
 *
 * Three, because the keys that feel different under a finger are the ones that
 * sound different: an ordinary character, space or enter (longer keys with a
 * stabiliser bar under them, so they are deeper and slower), and delete (a
 * lighter switch, so it is shorter and brighter). Modified shortcuts and arrow
 * keys are silent -- Cmd+S is not typing. */
function keySoundFor(event) {
  if (event.metaKey || event.ctrlKey || event.altKey) return "";
  if (event.key === "Backspace" || event.key === "Delete") return "key-delete";
  if (event.key === "Enter" || event.key === " ") return "key-space";
  if (event.key.length === 1) return "key";
  return "";
}

el("editor").addEventListener("keydown", (event) => {
  const editor = event.target;
  const typing = keySoundFor(event);
  if (typing) Sound.type(typing);

  if (event.key === "Tab") {
    event.preventDefault();
    if (editor.selectionStart !== editor.selectionEnd) return; // leave selection alone
    insertAtCursor("    ");
    noteEdit();
    return;
  }

  if (event.key === "Enter") {
    // Keep the current indentation, and add a level after an opening brace.
    const before = editor.value.slice(0, editor.selectionStart);
    const lineStart = before.lastIndexOf("\n") + 1;
    const indent = (before.slice(lineStart).match(/^\s*/) || [""])[0];
    const opensBlock = /[{[(]\s*$/.test(before);
    event.preventDefault();
    const addition = opensBlock ? "\n" + indent + "    " : "\n" + indent;
    insertAtCursor(addition);
    noteEdit();
  }
});

el("editor").addEventListener("input", noteEdit);
el("editor").addEventListener("scroll", () => {
  el("gutter").scrollTop = el("editor").scrollTop;
});

// Ctrl/Cmd+Enter submits, as in most code editors.
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    submit();
  }
});

// ── learning track ──────────────────────────────────────────────

/* The track teaches method, then sends you into the questions that need it.
 *
 * Progress is measured two ways, and the distinction matters. A module "done"
 * means every one of its drills is solved -- a deliberate, finite checklist.
 * A section's ring is wider than that: it also counts the questions its
 * principles are "used by", so finishing the reading opens questions you can
 * go and solve, and the ring fills as you do. The bar at the very top still
 * uses drills only, because that is the honest "have I done the work" measure;
 * the per-section rings are the teaching-through-practice measure. */

/* Every question id a section touches: its own drills plus the questions its
 * principles point at. This is the denominator for section progress. */
function sectionQuestions(modules) {
  const ids = new Set();
  for (const module of modules) {
    for (const drill of module.drills || []) ids.add(drill.id);
    for (const principle of module.principles || []) {
      for (const use of principle.uses || []) ids.add(use.id);
    }
  }
  return ids;
}

function sectionProgress(modules) {
  const ids = sectionQuestions(modules);
  let solved = 0;
  for (const id of ids) if (state.solved.has(id)) solved += 1;
  return { solved, total: ids.size };
}

/* A module counts as done once every one of its drills has been solved. */
function moduleSolved(module) {
  return module.drills.length > 0 &&
    module.drills.every((drill) => state.solved.has(drill.id));
}

function renderTrack() {
  const pane = el("track-pane");
  if (!state.track) {
    pane.innerHTML = '<p class="pane-empty">The learning track could not be loaded.</p>';
    return;
  }

  const track = state.track;
  const done = track.modules.filter(moduleSolved).length;
  const percent = track.modules.length ? Math.round((done / track.modules.length) * 100) : 0;

  pane.innerHTML = `
    <div class="track-head">
      <h1>${escapeHtml(track.title)}</h1>
      <p>${escapeHtml(track.subtitle)}</p>
      <p class="track-meta">
        <span><b>${track.modules.length}</b> modules</span>
        <span><b>${track.totalMinutes}</b> min of reading</span>
        <span><b>${done}</b> done</span>
      </p>
    </div>
    <div class="track-progress">
      <div class="track-progress-fill" style="width:${percent}%"></div>
    </div>
    ${renderParts(track)}
  `;

  // A module is open by default once its drills are done, so review is easy.
  animateSectionRings();
  pane.querySelectorAll(".module").forEach((element) => {
    element.addEventListener("toggle", () => {
      if (element.open) {
        const key = "cbp.track.open." + element.dataset.module;
        Store.set(key, "1");
      }
    });
  });
}

function capitalise(word) {
  return word ? word[0].toUpperCase() + word.slice(1) : word;
}

/* The questions a principle is actually used by. These are cross-references,
   so they read as a quieter line than the module's drill list: a concept is
   named once and then you can go and use it on a problem. */
function renderPrincipleUses(principle) {
  if (!principle.uses || !principle.uses.length) return "";
  return `
    <div class="principle-uses">
      <span class="principle-uses-label">Used by</span>
      <div class="principle-uses-list">
        ${principle.uses.map((question) => `
          <button class="use-chip" data-drill="${escapeHtml(question.id)}" type="button"
                  title="${escapeHtml(capitalise(question.tier))}">
            <span class="qi-dot ${state.solved.has(question.id) ? "solved" : state.attempted.has(question.id) ? "failed" : ""}"
                  aria-hidden="true"></span>
            ${escapeHtml(question.title)}
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

/* Progress for a course section: a ring beside a label, not a number inside
 * the ring.
 *
 * The number used to sit in the middle of the circle, which forced the ring to
 * stay small enough to hold text and left the arc hard to read at a glance --
 * at 15% you were reading a glyph, not seeing a sweep. Moving the text beside
 * the circle lets the ring be a clean, unlettered arc at a readable size.
 *
 * The label is the percentage and the word that says what it is. It used to
 * carry a second line of arithmetic -- "15 of 26 solved" -- and that line was
 * doing the same job as the ring, badly: nobody checks it against the arc, and
 * two numbers for one fact invites the reader to work out which one to trust.
 * The count is still in the accessible name, where it costs nothing and is
 * read out loud rather than counted. */
function renderSectionRing(progress) {
  const { solved, total } = progress;
  const r = 15;
  const c = 2 * Math.PI * r;
  const fraction = total ? solved / total : 0;
  const offset = c * (1 - fraction);
  const percent = total ? Math.round(fraction * 100) : 0;
  const complete = total > 0 && solved === total;
  return `
    <div class="section-progress${complete ? " complete" : ""}">
      <div class="section-ring" role="img"
           aria-label="${percent}% complete, ${solved} of ${total} questions solved">

        <svg viewBox="0 0 36 36" aria-hidden="true" focusable="false">
          <circle class="section-ring-track" cx="18" cy="18" r="${r}"/>
          <circle class="section-ring-fill" cx="18" cy="18" r="${r}"
                  data-offset="${offset.toFixed(2)}"
                  style="stroke-dasharray:${c.toFixed(2)};stroke-dashoffset:${c.toFixed(2)}"/>
        </svg>
      </div>
      <div class="section-progress-label">
        <span class="section-progress-percent">${percent}<span class="section-progress-pct">%</span></span>
        <span class="section-progress-word">Complete</span>
      </div>
    </div>
  `;
}

/* Draw every section ring from empty to its value once the track is on screen.
 * The fill circles are written at offset = full circumference; this sets the
 * real offset a frame later so the CSS transition sweeps them open. Without
 * the rAF the offset would be applied before the first paint and the sweep
 * would be skipped. */
function animateSectionRings() {
  const rings = document.querySelectorAll(".section-ring-fill");
  if (!rings.length) return;
  const target = REDUCED_MOTION;
  requestAnimationFrame(() => {
    rings.forEach((ring) => {
      ring.style.strokeDashoffset = target ? ring.dataset.offset : ring.dataset.offset;
    });
  });
}

/* The course is two halves and they are not the same kind of thing, so they
 * get a heading each rather than running together as one list of twenty. The
 * module counts per part are stated, because "12 modules" tells you nothing
 * about how long the reading is. */
function renderParts(track) {
  const byPart = new Map();
  for (const module of track.modules) {
    const key = module.part || "patterns";
    if (!byPart.has(key)) byPart.set(key, []);
    byPart.get(key).push(module);
  }

  const order = (track.parts || []).map((p) => p.id)
    .filter((id) => byPart.has(id));
  for (const id of byPart.keys()) if (!order.includes(id)) order.push(id);

  return order.map((partId) => {
    const part = (track.parts || []).find((p) => p.id === partId) || { title: partId };
    const modules = byPart.get(partId);
    const minutes = modules.reduce((sum, m) => sum + m.minutes, 0);
    const done = modules.filter(moduleSolved).length;
    const progress = sectionProgress(modules);
    return `
      <section class="track-part" data-part="${escapeHtml(partId)}">
        <div class="part-head">
          <div class="part-head-text">
            <h2 class="part-title">${escapeHtml(part.title)}</h2>
            <span class="part-meta">
              <span>${modules.length} module${modules.length === 1 ? "" : "s"}</span>
              <span>${minutes} min</span>
              ${done ? `<span>${done} done</span>` : ""}
            </span>
          </div>
          ${renderSectionRing(progress)}
        </div>
        ${part.blurb ? `<p class="part-blurb">${escapeHtml(part.blurb)}</p>` : ""}
        ${modules.map((module) => renderModule(module)).join("")}
      </section>
    `;
  }).join("");
}

/* A principle, split into the beats it is read in.
 *
 * The prose renderer below turns a body into blocks; this turns those blocks
 * into a sequence the reader advances through. The reason is that a principle
 * is an argument with a shape -- claim, then the mechanism, then the failure
 * mode it avoids -- and rendering all of it at once presents that argument as
 * a wall, where the reader's only choice is to read it all or stop. Revealing
 * a beat at a time turns the choice into "keep going", which is the choice
 * worth making.
 *
 * The first beat is never hidden: the claim is the reason to continue, so
 * hiding it would be hiding the invitation.
 */
function principleBeats(principle) {
  const blocks = String(principle.body || "")
    .split(/\n{2,}/)
    .map((raw) => raw.replace(/\s+$/, ""))
    .filter(Boolean);
  const beats = blocks.map((block) => {
    const lines = block.split("\n");
    if (lines.length > 1 && lines.every((line) => /^ {2,}/.test(line))) {
      const code = lines.map((line) => line.replace(/^ {2}/, "")).join("\n");
      return { kind: "code", html: walkthroughMarkup(code) };
    }
    return { kind: "prose", html: proseMarkup(block) };
  });
  // A specimen is the point of the beat it sits in, so the sentence that
  // introduces it is folded into the walkthrough as its caption -- and dropped
  // from the sequence, because a paragraph shown once above the code and again
  // as the caption reads as a duplication bug rather than as a structure.
  const folded = new Set();
  for (let i = 0; i < beats.length - 1; i += 1) {
    if (beats[i].kind === "prose" && beats[i + 1].kind === "code" && !folded.has(i)) {
      beats[i + 1].caption = beats[i].html;
      folded.add(i);
    }
  }
  return beats.filter((_, index) => !folded.has(index));
}

/* A code specimen you walk through a line at a time.
 *
 * Every line is a step, and stepping highlights one and dims the rest rather
 * than revealing them in order. That is a deliberate inversion: the technique
 * is visible in the finished block, and the finished block is what the reader
 * is being asked to recognise. Reading it top to bottom explains the syntax;
 * seeing one line picked out of a whole explains the role that line plays.
 */
function walkthroughMarkup(code) {
  const lines = code.split("\n");
  return `
    <div class="walkthrough" data-step="0">
      <div class="walk-code">
        ${lines.map((line, index) => `
          <button class="walk-line" type="button" data-line="${index}"
                  aria-label="Line ${index + 1}"><span class="walk-gutter">${index + 1}</span><span class="walk-text">${escapeHtml(line) || " "}</span></button>
        `).join("")}
      </div>
      <div class="walk-bar">
        <span class="walk-count"><b class="walk-at">1</b> / ${lines.length}</span>
        <span class="walk-note">Click any line to jump to it</span>
      </div>
    </div>
  `;
}

/* The course bodies are written in a deliberately small block language, and
 * this is the whole of the renderer for it.
 *
 * A blank line separates blocks. A block whose every line is indented by at
 * least two spaces is a specimen: two spaces are the fence, and they come off
 * so the block can be indented to sit in the layout without the code moving
 * with it. Everything else is a paragraph, and the first one is set as a lead,
 * because in every one of these principles the opening paragraph is the claim
 * and the rest is the argument for it.
 *
 * It is deliberately not a markdown subset with headings, quotes and tables.
 * The bodies contain no headings and no quotes, and a language with syntax
 * nobody writes is a language nobody maintains. */
function proseMarkup(text) {
  return String(text || "").split(/\n{2,}/).map((raw, index) => {
    const block = raw.replace(/\s+$/, "");
    if (!block) return "";
    const lines = block.split("\n");

    if (lines.length > 1 && lines.every((line) => /^ {2,}/.test(line))) {
      const body = lines.map((line) => line.replace(/^ {2}/, "")).join("\n");
      return `<pre class="prose-code"><code>${escapeHtml(body)}</code></pre>`;
    }

    if (lines.every((line) => /^\s*-\s+/.test(line))) {
      return `<ul class="prose-list">${lines
        .map((line) => `<li>${inlineMarkup(line.replace(/^\s*-\s+/, ""))}</li>`)
        .join("")}</ul>`;
    }

    // The authors wrap at a margin, so lines inside a paragraph are joined:
    // a hard wrap in the source is not a line break in the sentence.
    const joined = lines.map((line) => line.trim()).join(" ");
    return `<p class="prose${index === 0 ? " prose-lead" : ""}">${inlineMarkup(joined)}</p>`;
  }).join("");
}

function renderModule(module) {
  const done = moduleSolved(module);
  const stored = Store.get("cbp.track.open." + module.id);
  const open = done || stored === "1";
  const number = module.title.split(".")[0].trim();
  const progress = sectionProgress([module]);
  const complete = progress.total > 0 && progress.solved === progress.total;

  return `
    <details class="module${done ? " done" : ""}" data-module="${escapeHtml(module.id)}"${open ? " open" : ""}>
      <summary>
        <span class="module-num">${done ? icon("i-check") : escapeHtml(number)}</span>
        <span class="module-title">
          ${escapeHtml(module.title.replace(/^\d+\.\s*/, ""))}
          <span class="module-sub">${escapeHtml(module.subtitle)}</span>
        </span>
        <span class="module-progress" role="img"
              aria-label="${progress.solved} of ${progress.total} questions solved">
          <span class="module-progress-bar">
            <span class="module-progress-fill${complete ? " complete" : ""}"
                  style="width:${progress.total ? Math.round((progress.solved / progress.total) * 100) : 0}%"></span>
          </span>
          <span class="module-progress-count">${progress.solved}/${progress.total}</span>
        </span>
        <span class="module-mins">${module.minutes} min</span>
        <span class="module-chevron">${icon("i-chevron")}</span>
      </summary>
      <div class="module-body">
        ${module.principles.map((principle) => renderPrinciple(principle)).join("")}

        <div class="drills">
          <div class="drills-label">Practise these — ${module.drills.length} question${module.drills.length === 1 ? "" : "s"}</div>
          <div class="drill-list">
            ${module.drills.map((drill) => `
              <button class="drill" data-drill="${escapeHtml(drill.id)}" type="button">
                <span class="qi-dot ${state.solved.has(drill.id) ? "solved" : state.attempted.has(drill.id) ? "failed" : ""}">
                  ${state.solved.has(drill.id) ? icon("i-check") : ""}
                </span>
                ${escapeHtml(drill.title)}
              </button>
            `).join("")}
          </div>
        </div>
      </div>
    </details>
  `;
}

/* One principle: the claim, then the beats behind a control, then the check
 * and the questions that use it.
 *
 * The beats are marked up but left hidden, and the control carries the count,
 * so the reader can see how much argument is left before deciding whether to
 * spend it. Once the last beat is out the control becomes a reset rather than
 * disappearing, because a reader who wants to re-read the third beat of six
 * should not have to reopen the module to get it.
 */
function renderPrinciple(principle) {
  const beats = principleBeats(principle);
  const last = Math.max(beats.length - 1, 0);
  const uses = renderPrincipleUses(principle);
  return `
    <div class="principle">
      <h2>${escapeHtml(principle.heading)}</h2>
      <div class="prose-body">
        ${beats.map((beat, index) => `
          <div class="beat${index === 0 ? " is-open" : ""}" data-beat="${index}"${index === 0 ? "" : " hidden"}>
            ${index > 0 && beat.caption ? `<div class="beat-caption">${beat.caption}</div>` : ""}
            ${beat.html}
          </div>
        `).join("")}
        <button class="beat-more" type="button" data-more="${last}"
                aria-label="${beats.length > 1 ? "Show the rest of this principle" : "Reveal the rest of this principle"}">
          <span class="beat-more-label">${beats.length > 1 ? "Show the rest" : "Show the rest"}</span>
          <span class="beat-more-count">${beats.length - 1} more</span>
        </button>
        ${principle.check ? `<div class="principle-check">${icon("i-check")}<span>${inlineMarkup(principle.check)}</span></div>` : ""}
        ${uses}
      </div>
    </div>
  `;
}

/* Opening the next beat, or closing the last one back to the first.
 *
 * A single toggle rather than a "next" that can only go forwards: being able
 * to fold a principle back to its claim is what makes the reading feel like
 * handling something rather than falling down a page.
 */
function stepPrinciple(principle, forwards) {
  const beats = Array.from(principle.querySelectorAll(".beat"));
  if (!beats.length) return;
  const open = beats.filter((beat) => !beat.hidden);
  const at = open.length - 1;
  if (forwards && open.length === beats.length) {
    // Everything is already out, so the control folds back to the claim.
    const folded = beats.slice(0, 1);
    beats.forEach((beat) => { beat.hidden = !folded.includes(beat); });
    principle.querySelector(".beat-more-label").textContent = "Show the rest";
    principle.querySelector(".beat-more-count").textContent =
      `${beats.length - 1} more`;
    return;
  }
  const target = forwards ? open.length : (at > 0 ? at - 1 : 0);

  beats.forEach((beat) => { beat.hidden = true; });
  beats.forEach((beat, index) => { beat.hidden = index > target; });
  if (!REDUCED_MOTION) {
    const arriving = beats[target];
    if (arriving) replay(arriving, "beat-in");
  }
  principle.querySelector(".beat-more-label").textContent =
    target === beats.length - 1 ? "Collapse" : "Show the rest";
  principle.querySelector(".beat-more-count").textContent =
    target === beats.length - 1 ? "back to the top" : `${beats.length - 1 - target} more`;
}

/* Move a walkthrough to `index`, wrapping at either end so the control cannot
 * run out. The dimming is what carries the meaning: the whole specimen stays
 * on screen because recognising the shape of the finished code is the skill,
 * and the picked-out line says which part of it is being talked about. */
function setWalkStep(walk, index) {
  const lines = Array.from(walk.querySelectorAll(".walk-line"));
  if (!lines.length) return;
  const at = ((index % lines.length) + lines.length) % lines.length;
  walk.dataset.step = String(at);
  lines.forEach((line, i) => line.classList.toggle("is-at", i === at));
  const counter = walk.querySelector(".walk-at");
  if (counter) counter.textContent = String(at + 1);
  if (!REDUCED_MOTION) {
    const active = lines[at];
    if (active) replay(active, "walk-step");
  }
}

function setView(view) {
  state.view = view;
  const isPractice = view === "practice";
  el("sidebar").hidden = !isPractice;
  el("pane").hidden = !isPractice;
  el("track-pane").hidden = isPractice;
  el("layout").classList.toggle("is-track", !isPractice);
  el("view-practice").classList.toggle("is-active", isPractice);
  el("view-track").classList.toggle("is-active", !isPractice);
  el("view-practice").setAttribute("aria-pressed", String(isPractice));
  el("view-track").setAttribute("aria-pressed", String(!isPractice));
  positionThumb();
  if (!isPractice) renderTrack();
  // The practice pane always animated when a question arrived; the course pane
  // had nothing, so switching to it was a jump cut. One entrance for both is
  // what makes the two views feel like the same app rather than two pages.
  if (!REDUCED_MOTION) replay(isPractice ? el("pane") : el("track-pane"), "view-in");
}

function positionThumb() {
  const active = document.querySelector(".segmented-btn.is-active");
  const segment = el("segmented");
  const thumb = el("segmented-thumb");
  if (!active || !segment || !thumb) return;
  const a = active.getBoundingClientRect();
  const s = segment.getBoundingClientRect();
  // 3px is the track's own padding, which the thumb is positioned inside.
  thumb.style.setProperty("--thumb-x", `${a.left - s.left - 3}px`);
  thumb.style.setProperty("--thumb-w", `${a.width}px`);
}

// ── wiring ─────────────────────────────────────────────────────

function wireEvents() {
  el("view-practice").addEventListener("click", () => setView("practice"));
  el("view-track").addEventListener("click", () => setView("track"));
  el("track-pane").addEventListener("click", (event) => {
    const drill = event.target.closest("[data-drill]");
    if (drill) {
      setView("practice");
      openQuestion(drill.dataset.drill);
      return;
    }
    // Progressive reveal. Delegated because the beats do not exist until the
    // module is rendered, and a module is re-rendered whenever progress moves.
    const more = event.target.closest(".beat-more");
    if (more) {
      const principle = more.closest(".principle");
      if (principle) stepPrinciple(principle, true);
      return;
    }
    // A walkthrough line. Clicking the active line steps on, so the code can
    // be read at the same pace as the prose without a second control.
    const line = event.target.closest(".walk-line");
    if (line) {
      const walk = line.closest(".walkthrough");
      if (!walk) return;
      const index = Number(line.dataset.line);
      const current = Number(walk.dataset.step);
      setWalkStep(walk, current === index ? index + 1 : index);
    }
  });

  el("submit-btn").addEventListener("click", submit);
  el("hint-ask").addEventListener("click", showNextHint);
  // The reference solution fetches on its first open rather than when the
  // question renders, so a question you never give up on costs no request.
  el("solution-block").addEventListener("toggle", () => {
    if (el("solution-block").open) loadSolution();
  });
  // The reveal control is the label; the row itself answers too while it is
  // still covered, because a blurred chip is not a click target.
  el("patterns-reveal").addEventListener("click", revealPatterns);
  el("patterns-block").addEventListener("click", (event) => {
    if (event.target.closest(".pattern[data-module]")) return;
    revealPatterns();
  });
  // Delegated, so the chips work for whichever question is open. A pattern
  // chip only carries data-module when the course has a module for it.
  el("pane").addEventListener("click", (event) => {
    const chip = event.target.closest(".pattern[data-module]");
    if (chip) openModule(chip.dataset.module);
  });
  el("reset-btn").addEventListener("click", () => {
    if (state.current) {
      el("editor").value = starterFor(state.current);
      el("result").hidden = true;
      el("lesson").hidden = true;
      syncGutter();
      // Reset throws away the attempt, so the clock goes back to idle too.
      resetTimer();
    }
  });

  el("filter-input").addEventListener("input", (e) => buildQuestionList(e.target.value));

  el("examples-toggle").addEventListener("click", () =>
    setExamplesHidden(!el("examples-body").hidden));

  el("level-chip").addEventListener("click", () => openSheet("trophies"));
  el("trophy-chip").addEventListener("click", () => openSheet("trophies"));
  el("sound-btn").addEventListener("click", () => openSheet("sound"));
  el("theme-btn").addEventListener("click", toggleTheme);

  el("sheet").addEventListener("click", (event) => {
    if (event.target.id === "sheet-close" || event.target.id === "sheet") {
      closeSheet();
      return;
    }
    const toggle = event.target.closest(".switch[data-setting]");
    if (toggle) { toggleSetting(toggle.dataset.setting); return; }
    const packOption = event.target.closest(".pack-option[data-pack]");
    if (packOption) choosePack(packOption.dataset.pack);
  });
  el("sheet").addEventListener("input", (event) => {
    if (event.target.id !== "sound-volume") return;
    Sound.update({ volume: Number(event.target.value) });
    state.sound = Sound.settingsFor();
  });
  // Fired on release, so the volume gives one click to judge rather than a
  // sound per pixel of travel.
  el("sheet").addEventListener("change", (event) => {
    if (event.target.id === "sound-volume") Sound.play("tap");
  });

  // Anything pressable makes a sound, from one listener. Capture phase and
  // pointerdown rather than click, because a press has to be answered as it
  // happens: a click arrives after the button has already done its work, and
  // on anything slow that is audibly late. A `data-sound` attribute is how an
  // element asks for something other than the default tick.
  document.addEventListener("pointerdown", (event) => {
    const target = event.target.closest('button, summary, [role="switch"], a[href]');
    if (!target || target.disabled) return;
    if (target.getAttribute("aria-disabled") === "true") return;
    // The sound switches and the keyboard picker play a preview of what they
    // control when they are pressed, so they must not also fire the default
    // tick.
    if (target.classList.contains("switch") || target.classList.contains("pack-option")) return;
    Sound.play(target.dataset.sound || "tap");
  }, true);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !el("sheet").hidden) closeSheet();
  });

  document.querySelector(".source-filter").addEventListener("click", (event) => {
    const chip = event.target.closest("[data-source]");
    if (!chip) return;
    state.sourceFilter = chip.dataset.source;
    document.querySelectorAll(".source-chip").forEach((other) => {
      const on = other === chip;
      other.classList.toggle("is-active", on);
      other.setAttribute("aria-pressed", String(on));
    });
    buildQuestionList(el("filter-input").value);
  });

  el("language-select").addEventListener("change", (e) => {
    Store.set("cbp.lang", e.target.value);
    if (state.current) {
      el("editor-label").textContent = `Your ${languageLabel()} code`;
      // A C++ solution is not a Java one, so re-seed when the language changes.
      el("editor").value = starterFor(state.current);
      el("result").hidden = true;
      syncGutter();
      // A C++ answer is not a Java one, so the previous attempt is gone.
      resetTimer();
      // The code in the reference solution is for one language only, so the
      // cached copy is dropped whether or not it happens to be on screen right
      // now. Only refetch when it is showing.
      clearSolution();
      if (el("solution-block").open) loadSolution();
    }
  });

  el("prev-btn").addEventListener("click", () => step(-1));
  el("next-btn").addEventListener("click", () => step(1));

  // A new user should not have to work out what to click first.
  el("start-btn").addEventListener("click", () => {
    const next = state.questions.find((q) => !state.solved.has(q.id)) || state.questions[0];
    if (next) openQuestion(next.id);
  });
  el("start-track-btn").addEventListener("click", () => setView("track"));
}

function step(direction) {
  const ids = [...document.querySelectorAll(".question-item")].map((b) => b.dataset.id);
  const index = ids.indexOf(state.current.id);
  const next = ids[index + direction];
  if (next) openQuestion(next);
}

// ── motion ─────────────────────────────────────────────────────

/* The celebration burst.
 *
 * On a solve, a ring of coloured shards flies out from the result box and
 * fades. It is drawn into a dedicated overlay rather than the result element
 * so the shards can travel over the whole window without being clipped by the
 * pane's overflow, and so the result box itself can keep its own layout. The
 * nodes remove themselves when the animation ends, so nothing accumulates.
 *
 * Everything here is transform-and-opacity only, which keeps it on the
 * compositor, and it is all suppressed under prefers-reduced-motion. */
const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function burst(anchor, options = {}) {
  if (REDUCED_MOTION) return;
  const layer = el("fx-layer");
  if (!layer || !anchor) return;

  const box = anchor.getBoundingClientRect();
  const cx = box.left + box.width / 2;
  const cy = box.top + box.height / 2;
  // The shard palette is the theme's accents, so a pass looks like it came from
  // this app rather than from a generic confetti library.
  const colors = options.colors || ["#34d399", "#7c6cff", "#c084fc", "#fbbf24", "#45d0e8"];
  const count = options.count || 14;

  for (let i = 0; i < count; i += 1) {
    // An even spread around the circle, with a little jitter so it does not
    // look like a clock face.
    const angle = (i / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.4;
    const distance = 70 + Math.random() * 60;
    const shard = document.createElement("span");
    shard.className = "fx-shard";
    shard.style.left = `${cx}px`;
    shard.style.top = `${cy}px`;
    shard.style.background = colors[i % colors.length];
    shard.style.setProperty("--dx", `${Math.cos(angle) * distance}px`);
    shard.style.setProperty("--dy", `${Math.sin(angle) * distance}px`);
    shard.style.animationDelay = `${Math.random() * 40}ms`;
    layer.appendChild(shard);
    // Matched to the shard's flight time in CSS.
    setTimeout(() => shard.remove(), 900);
  }
}

/* The drifting code.
 *
 * A few dozen tokens from the languages this app runs, each one an element
 * travelling the height of the window on its own long cycle. They are built
 * here rather than written into index.html because every one of them wants a
 * different position, duration and heading: fixed markup would mean the same
 * handful of lines repeated with hand-tuned offsets, which drifts out of shape
 * the moment the vocabulary changes.
 *
 * The vocabulary is the app's own subject, which is what keeps this from being
 * decoration of a different kind. `{{` and `}};` are the two things on screen
 * more than any others, so a field built from them looks like what the app is
 * about rather than like a screensaver.
 *
 * Nothing here loops on a shared clock, and the offsets are per element, so
 * the field never pulses. Every duration is over a minute and the negative
 * delays mean the field is already populated when it is built rather than
 * filling in from the bottom over the first minute. */
const DRIFT_TOKENS = [
  "{{", "}}", "();", "=>", "[]", "::", "for", "while", "if", "else", "return",
  "let", "const", "fn", "impl", "struct", "enum", "match", "await", "async",
  "int", "auto", "var", "#include", "using", "public", "static", "void",
  "def", "class", "new", "self", "this", "lambda", "yield", "elif",
  "[i]", "[j]", "[k]", "->", "|", "&", "*", "&&", "||", "++", "--", "==",
  "!=", ">=", "<=", "+=", "->", "::", "0x1f", "0b1011", "3.14", "None",
  "null", "nil", "true", "false", "usize", "str", "bool", "u32", "i64",
  "cout", "printf", "System.out", "assert", "yield", "match", "mut", "ref",
];

function buildDrift() {
  const layer = el("bg-code");
  if (!layer || REDUCED_MOTION) return;

  // One token per 90 square pixels of window, floored so a small window still
  // has a field and capped so a very large one does not turn into wallpaper.
  const area = window.innerWidth * window.innerHeight;
  const count = Math.max(18, Math.min(52, Math.round(area / 9000)));

  for (let i = 0; i < count; i += 1) {
    const token = document.createElement("span");
    token.className = "drift";
    // Every ninth token takes the brass. Enough to give the field a second
    // voice without making the accent something the eye goes looking for.
    if (i % 9 === 4) token.classList.add("is-key");
    token.textContent = DRIFT_TOKENS[Math.floor(Math.random() * DRIFT_TOKENS.length)];
    token.style.setProperty("--x", `${(Math.random() * 100).toFixed(2)}%`);
    token.style.setProperty("--dx", `${(Math.random() * 26 - 13).toFixed(1)}px`);
    // A minute and a half to two and a half. Long enough that no single pass
    // is watchable, which is the point.
    token.style.setProperty("--dur", `${(90 + Math.random() * 80).toFixed(0)}s`);
    // Negative, so the animation starts partway through rather than at the
    // bottom edge. This is what fills the window on the first frame.
    token.style.setProperty("--delay", `${(-Math.random() * 160).toFixed(1)}s`);
    layer.appendChild(token);
  }
}

// ── small utilities ────────────────────────────────────────────

/* Restart a one-shot animation by removing the class, forcing a reflow, and
 * adding it back. Without the reflow the browser coalesces the two mutations
 * and the animation does not replay. */
function replay(node, className) {
  if (!node) return;
  node.classList.remove(className);
  void node.getBoundingClientRect();
  node.classList.add(className);
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

let toastTimer;
function showToast(message, ms = 3600) {
  const toast = el("toast");
  toast.textContent = message;
  // Unhiding is what restarts the CSS animation, so a second toast while one
  // is on screen still animates in.
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, ms);
}

document.addEventListener("DOMContentLoaded", init);
