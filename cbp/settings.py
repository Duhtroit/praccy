"""Where the app's preferences live between launches.

A browser stores its own settings per origin, and this server's origin changes
every launch: it binds an ephemeral port on purpose, so a second copy of the
app, or an unrelated dev server, cannot break the first one. That is exactly
the right call for the socket and exactly the wrong one for persistence --
`http://127.0.0.1:52001` and `http://127.0.0.1:52002` are different origins,
and neither can read the other's localStorage. So the settings are kept here,
on disk, and the web layer reads and writes them through `/api/settings`.

Nothing here interprets the payload. The web layer decides what a setting
means; this module only remembers the last thing it was told, which keeps one
place to add a preference rather than two. The value is a flat object of
strings, which is enough for a language, a volume, a pack and a pile of
booleans.

The write is atomic -- a temporary file, then `os.replace` -- because a
settings file half-written by a crash is worse than no file at all: it would
take the sound panel's settings with it and look like the app had forgotten
everything.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

ENV_DIR = "PRACCY_STATE_DIR"
FILENAME = "settings.json"


def directory() -> str:
    """Where the settings file lives, honouring an override for tests.

    Application Support rather than Caches on macOS, matching the launch log:
    this is a record the user owns, and macOS is entitled to empty Caches
    behind their back.
    """
    override = os.environ.get(ENV_DIR)
    if override:
        return override
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library",
                            "Application Support", "Praccy")
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config")
    return os.path.join(base, "praccy")


def path() -> str:
    return os.path.join(directory(), FILENAME)


def read() -> dict:
    """The stored settings, or an empty object if there are none yet.

    A file that cannot be parsed is treated as absent rather than as fatal. The
    alternative -- refusing to start over a corrupt settings blob -- is how a
    preferences bug becomes an app that will not launch.
    """
    try:
        with open(path(), encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write(data: dict) -> dict:
    """Replace the stored settings with `data` and return what was written."""
    clean = {str(key): value for key, value in data.items()}
    folder = directory()
    os.makedirs(folder, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=folder, prefix=".settings-", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(clean, stream, ensure_ascii=False, sort_keys=True, indent=2)
        os.replace(temporary, path())
    except OSError:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return clean
