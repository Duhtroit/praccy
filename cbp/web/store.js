/* Store — the app's preferences, on disk instead of in the browser.
 *
 * The server binds an ephemeral port on purpose, so a second copy of the app
 * cannot break the first, and every launch is therefore a different origin as
 * far as the browser is concerned. localStorage is scoped to the origin, so a
 * setting written by one launch belongs to an address the next launch never
 * sees again -- which is why the sound switch used to come back off and the
 * keyboard came back to its default every time.
 *
 * So the preferences live in the server's settings file and this module is the
 * bridge. It reads synchronously (from the map hydrated at startup) and writes
 * optimistically (to the map, to localStorage as a same-session mirror, and to
 * the server on a short debounce so a slider being dragged is one round trip
 * rather than forty).
 *
 * The values are strings, because they are the same strings the app used to
 * put in localStorage -- a JSON blob is just another string as far as this is
 * concerned. That is deliberate: nothing above has to change shape to be
 * persisted, and a new preference is a key and a call.
 *
 * Ordering matters. `ready()` must be awaited before anything reads, because
 * until it resolves the map only holds what the defaults say. It merges rather
 * than replaces: the server is the source of truth across launches, and
 * localStorage is the fallback for the very first run of a build that predates
 * this file.
 */

const Store = (() => {
  const PREFIX = "cbp.";
  const SAVE_DELAY_MS = 160;

  let data = {};
  let timer = null;
  let hydrated = false;

  function readLocal() {
    const found = {};
    try {
      for (let i = 0; i < localStorage.length; i += 1) {
        const key = localStorage.key(i);
        if (key && key.startsWith(PREFIX)) found[key] = localStorage.getItem(key);
      }
    } catch (e) { /* storage disabled: the server copy still works */ }
    return found;
  }

  function mirror() {
    try {
      Object.keys(data).forEach((key) => localStorage.setItem(key, data[key]));
    } catch (e) { /* ignore */ }
  }

  async function ready() {
    const local = readLocal();
    let remote = {};
    try {
      const res = await fetch("/api/settings");
      if (res.ok) {
        const payload = await res.json();
        remote = (payload && payload.settings) || {};
      }
    } catch (e) { /* no server settings: fall back to what is local */ }
    data = Object.assign({}, local, remote);
    mirror();
    hydrated = true;
    return data;
  }

  function flush() {
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
    const body = JSON.stringify(data);
    try {
      // A settings write is small and has to survive the window closing, so it
      // goes out as a beacon when we are being torn down and as an ordinary
      // fetch otherwise.
      if (document.visibilityState === "hidden" && navigator.sendBeacon) {
        navigator.sendBeacon("/api/settings", new Blob([body], { type: "application/json" }));
        return;
      }
      fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        keepalive: true,
      }).catch(() => {});
    } catch (e) { /* ignore */ }
  }

  function schedule() {
    if (timer) clearTimeout(timer);
    timer = setTimeout(flush, SAVE_DELAY_MS);
  }

  function get(key) {
    return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null;
  }

  function set(key, value) {
    data[key] = value;
    try { localStorage.setItem(key, value); } catch (e) { /* ignore */ }
    schedule();
  }

  function remove(key) {
    delete data[key];
    try { localStorage.removeItem(key); } catch (e) { /* ignore */ }
    schedule();
  }

  /* A convenience for the JSON blobs the sound module and the progress record
     are stored as: parse if we can, and hand back the fallback if we cannot,
     because a corrupt blob should cost a preference and not the app. */
  function json(key, fallback) {
    const raw = get(key);
    if (raw === null) return fallback;
    try {
      const parsed = JSON.parse(raw);
      return parsed === null ? fallback : parsed;
    } catch (e) {
      return fallback;
    }
  }

  // The last chance to get a pending write out the door. `visibilitychange`
  // fires on a reload and on a tab going away, which is exactly the case a
  // debounce would otherwise drop.
  window.addEventListener("pagehide", flush);
  window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flush();
  });

  return {
    ready: ready,
    flush: flush,
    get: get,
    set: set,
    remove: remove,
    json: json,
    isReady: () => hydrated,
  };
})();

window.Store = Store;
