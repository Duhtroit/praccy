#!/usr/bin/env python3
"""Generate the sound set in cbp/web/sounds.

    python3 tools/build_sounds.py

Why synthesised rather than downloaded. The brief asked for public-domain
audio, and the cleanest way to satisfy that is not to ship anyone else's file
at all: every sample here is computed from the maths below, so there is no
third-party licence to track, nothing to attribute, and nothing that can change
upstream between two builds. The other reason is fit. A pack of game UI blips
would have to be filtered and re-timed to match a muted keyboard under a text
editor, and the result would be somebody else's samples wearing a hat.

Three rules decide how everything here sounds.

  The app's own voice is soft. Every sample that is not a keystroke is put
  through one more low pass on the way out and written quieter, so the
  interface sits under the thing you are doing rather than announcing itself.
  A settings panel should not be louder than the typing it is configuring.

  Nothing is bright. Every transient is low-passed, most of it below 5 kHz.
  A click with a hard edge is a notification; a soft one is a thing being
  touched.

  Nothing is a beep. The body of each sound is a short low sine, and the click
  is noise that has been filtered until it is a texture rather than a click.
  That is what keeps a keypress from reading as "mechanical".

The keyboard ships in two packs, and they are the two mechanical keyboards
worth imitating by ear. A pack is a whole instrument rather than a volume
setting, and the two are built from opposite ends of the switch.

  `creamy` is the lubed board: a low, rounded body that rings for a while and
a click filtered right down and mixed well under it, so a keystroke is a thud
with a hint of plastic rather than a click with a hint of thud.

  `clicky` is the blue-switch board: a short, bright, band-limited click that
lands on the press and a second, quieter one on the release, over a tighter
body. It is the one place in the set where a keystroke is allowed a hard edge,
because that edge is the entire difference between the two instruments.

Everything else in the set -- the interface ticks, the verdicts, the trophy --
is the app's own voice and does not change with the pack.

Regenerating is deterministic: the noise is drawn from a fixed seed, so a
rebuild produces byte-identical files and a build never churns.
"""

from __future__ import annotations

import math
import os
import random
import struct
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cbp", "web", "sounds")

# 32 kHz is plenty: everything here is deliberately under 6 kHz, so this leaves
# headroom for the noise without paying for the 44.1 kHz of a music file.
RATE = 32000
SEED = 20260930

# How loud each file is written, as a fraction of full scale. This is a balance
# between the sounds rather than a quality of any one of them: typing has to be
# audible under the verdict, and the verdict has to be the loudest thing the
# app does because it is the only moment worth interrupting for.
GAINS = {
    # The two keyboards sit at the top of the range on purpose: typing is the
    # thing you are doing, and everything below it is the app answering.
    # Creamy is written a little louder than clicky, because a low-passed click
    # reads as quieter than it measures -- without the lift, choosing it feels
    # like a volume drop rather than a change of instrument.
    "key-creamy": 0.34,
    "key-creamy-space": 0.40,
    "key-creamy-delete": 0.30,
    "key-clicky": 0.30,
    "key-clicky-space": 0.35,
    "key-clicky-delete": 0.27,
    # Everything from here down is softened twice: once by construction and
    # once by the low pass in main(). These are the quiet half of the set.
    "tap": 0.14,
    "toggle": 0.20,
    "cue": 0.24,
    "open": 0.17,
    "close": 0.17,
    "pass": 0.30,
    "fail": 0.24,
    "trophy": 0.28,
}

# The extra low pass applied to every sample that is not a keystroke. One pole,
# so it is a slope rather than a wall: it takes the hard edge off a transient
# without making the sound muffled, which is exactly the difference between
# "softer" and "broken". The keyboards are left alone -- a keyboard is a
# mechanical object and has to sound like one.
SOFT_CUTOFF = 2400.0


# ── the toolkit ─────────────────────────────────────────────────────────────

def silence(seconds: float) -> list:
    return [0.0] * int(RATE * seconds)


def noise(seconds: float, rng: random.Random) -> list:
    return [rng.uniform(-1.0, 1.0) for _ in range(int(RATE * seconds))]


def lowpass(signal: list, cutoff: float) -> list:
    """One-pole low pass. The gentle slope is the point: a steeper filter rings
    and rings are what make a short sound read as electronic."""
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / RATE)
    out, last = [], 0.0
    for value in signal:
        last += alpha * (value - last)
        out.append(last)
    return out


def highpass(signal: list, cutoff: float) -> list:
    """The complement of `lowpass`, for taking the rumble off a noise burst."""
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / RATE)
    out, last, last_in = [], 0.0, 0.0
    for value in signal:
        last += alpha * (value - last)
        out.append(value - last)
        last_in = value
    del last_in
    return out


def envelope(length: int, attack: float, decay: float, curve: float = 1.0) -> list:
    """An attack ramp into an exponential decay, in seconds.

    `attack` is never zero anywhere in this file. A sound that starts at full
    amplitude has a click in it, and a click is the opposite of creamy.
    """
    attack_samples = max(1, int(RATE * attack))
    decay_samples = max(1, int(RATE * decay))
    out = []
    for i in range(length):
        if i < attack_samples:
            level = i / attack_samples
        else:
            level = math.exp(-(i - attack_samples) / decay_samples)
        out.append(level ** curve)
    return out


def sine(freq: float, length: int, phase: float = 0.0) -> list:
    step = 2.0 * math.pi * freq / RATE
    return [math.sin(phase + step * i) for i in range(length)]


def sweep(start: float, end: float, length: int) -> list:
    """A sine whose frequency slides from start to end, integrated so the phase
    stays continuous. Frequency is interpolated geometrically, which is what
    makes a sweep sound like it moves evenly rather than lurching at the top."""
    out, phase = [], 0.0
    for i in range(length):
        t = i / max(1, length - 1)
        freq = start * (end / start) ** t
        phase += 2.0 * math.pi * freq / RATE
        out.append(math.sin(phase))
    return out


def shape(signal: list, env: list, gain: float = 1.0) -> list:
    return [value * env[i] * gain for i, value in enumerate(signal)]


def scale(signal: list, gain: float) -> list:
    return [value * gain for value in signal]


def mix(*layers: list) -> list:
    length = max(len(layer) for layer in layers)
    out = [0.0] * length
    for layer in layers:
        for i, value in enumerate(layer):
            out[i] += value
    return out


def pad(layer: list, seconds: float) -> list:
    return layer + silence(seconds)


def bell(freq: float, seconds: float, decay: float, partials=(1.0, 2.0, 3.0),
         gains=(1.0, 0.22, 0.08), attack: float = 0.004) -> list:
    """A struck tone.

    Deliberately sparse in harmonics and with the upper partials decaying
    faster than the fundamental, which is how a physical object behaves. Dense
    harmonics with one shared decay is the sound of an alarm.
    """
    length = int(RATE * seconds)
    layers = []
    for index, ratio in enumerate(partials):
        partial_decay = decay / (1.0 + index * 0.9)
        env = envelope(length, attack, partial_decay)
        layers.append(shape(sine(freq * ratio, length), env, gains[index]))
    return mix(*layers)


def thock(freq: float, seconds: float, decay: float) -> list:
    """The body under a keypress: one low sine, no harmonics at all."""
    length = int(RATE * seconds)
    return shape(sine(freq, length), envelope(length, 0.002, decay), 1.0)


def click(cutoff: float, seconds: float, decay: float, rng: random.Random,
          attack: float = 0.0015) -> list:
    """The texture on top: filtered noise with a short envelope."""
    length = int(RATE * seconds)
    grains = highpass(lowpass(noise(seconds, rng), cutoff), 180.0)
    return shape(grains[:length], envelope(length, attack, decay), 1.0)


def click_band(low: float, high: float, seconds: float, decay: float,
               rng: random.Random, attack: float = 0.0008) -> list:
    """A click held between two corners.

    `click` is a low pass over noise, which leaves a soft, dull texture. A
    blue-switch click is the opposite shape: it is a narrow band of noise with
    almost nothing below it, which is what makes it read as plastic snapping
    rather than as a hiss. High-passing after the low pass is what puts the
    floor under it, and keeping both corners under 6 kHz is what stops the
    brightness check from failing the build.
    """
    length = int(RATE * seconds)
    grains = highpass(lowpass(noise(seconds, rng), high), low)
    return shape(grains[:length], envelope(length, attack, decay), 1.0)


def normalise(signal: list) -> list:
    peak = max(abs(value) for value in signal) or 1.0
    return [value / peak for value in signal]


def fade(signal: list) -> list:
    """Two milliseconds at each end, so the file never begins or ends on a
    discontinuity. Without it every sound has a small pop at the tail."""
    n = max(1, int(RATE * 0.002))
    out = list(signal)
    for i in range(min(n, len(out))):
        out[i] *= i / n
        out[-1 - i] *= i / n
    return out


# ── the sounds ──────────────────────────────────────────────────────────────
#
# Typing. Three samples per pack, because a keyboard that makes one sound for
# every key is a novelty and a keyboard that makes a different sound for the
# ones you press differently is an instrument. Space and enter are deeper and
# longer (a stabiliser bar), delete is shorter and brighter (a lighter switch).

# Creamy. The lubed board. Three things change together, because changing any
# one alone does not read as a different keyboard: the body drops to a fifth
# below middle and rings for half again as long, the click's filter drops to
# well under a kilohertz, and the click is mixed in at well under a third of
# the body's level instead of level with it. What is left is a keypress with no
# snap in it at all -- the mechanism rather than the cap.

def key_creamy(rng):
    body = thock(108, 0.078, 0.024)
    top = click(600, 0.032, 0.011, rng, attack=0.0022)
    return mix(body, scale(pad(top, 0.032), 0.30))


def key_creamy_space(rng):
    body = thock(76, 0.096, 0.032)
    top = click(480, 0.036, 0.014, rng, attack=0.0026)
    return mix(body, scale(pad(top, 0.048), 0.28))


def key_creamy_delete(rng):
    body = thock(142, 0.060, 0.018)
    top = click(860, 0.026, 0.009, rng, attack=0.0018)
    return mix(body, scale(pad(top, 0.028), 0.34))


# Clicky. The blue-switch board, and the mirror image of creamy: where creamy
# buries the click under the body, clicky leads with it and keeps the body
# short so nothing muffles it. Two clicks rather than one, because that is what
# the switch actually does -- a sharp one as the key passes the bump and a
# quieter one as it comes back up. The delay between them is roughly how long a
# key is held, and it is the part that makes the sound read as a mechanism
# rather than as a notification.

def key_clicky(rng):
    body = thock(132, 0.050, 0.012)
    press = click_band(1700, 5200, 0.016, 0.0030, rng)
    release = click_band(2100, 4600, 0.012, 0.0024, rng, attack=0.0010)
    return mix(body, pad(press, 0.006), scale(pad(release, 0.040), 0.55))


def key_clicky_space(rng):
    body = thock(96, 0.064, 0.016)
    press = click_band(1500, 4800, 0.018, 0.0034, rng)
    release = click_band(1900, 4300, 0.014, 0.0028, rng, attack=0.0010)
    return mix(body, pad(press, 0.008), scale(pad(release, 0.052), 0.52))


def key_clicky_delete(rng):
    body = thock(168, 0.044, 0.010)
    press = click_band(1900, 5400, 0.014, 0.0026, rng)
    release = click_band(2300, 4800, 0.010, 0.0021, rng, attack=0.0009)
    return mix(body, pad(press, 0.005), scale(pad(release, 0.032), 0.58))


# Interface. Small, quiet, and placed so the ear reads them as the surface
# responding rather than as notifications.

def tap(rng):
    return click(2600, 0.020, 0.004, rng, attack=0.001)


def toggle(rng):
    """Two steps. The first says something was selected, the second says which
    way. A single step would be indistinguishable from `tap`."""
    length = int(RATE * 0.055)
    first = shape(sine(560, length), envelope(length, 0.006, 0.018))
    second = pad(shape(sine(760, length), envelope(length, 0.006, 0.020)), 0.045)
    return mix(first, second)


def cue(rng):
    """The hint reveal: one struck tone, a fifth above the app's neutral."""
    return bell(740.0, 0.40, 0.055, partials=(1.0, 2.01), gains=(1.0, 0.14),
                attack=0.005)


def open(rng):
    """A panel arriving: a short rise, soft at both ends."""
    length = int(RATE * 0.19)
    body = shape(sweep(320.0, 520.0, length), envelope(length, 0.02, 0.05))
    air = pad(shape(highpass(lowpass(noise(0.06, rng), 3000.0), 400.0),
                    envelope(int(RATE * 0.06), 0.004, 0.018)), 0.01)
    return mix(body, shape(air, [1.0] * len(air), 0.12))


def close(rng):
    """The same gesture in reverse, a little shorter, so leaving is quicker
    than arriving."""
    length = int(RATE * 0.16)
    body = shape(sweep(470.0, 300.0, length), envelope(length, 0.012, 0.045))
    return body


# Verdicts.

def passed(rng):
    """Two notes, a fifth apart, the second higher and later. Rising is the
    only thing that means "good" without needing to be learned, and two notes
    rather than three keeps it from sounding like a jingle."""
    low = bell(523.25, 0.46, 0.075, attack=0.006)
    high = pad(bell(783.99, 0.52, 0.085, attack=0.006), 0.105)
    return mix(low, high)


def failed(rng):
    """A low thud with a beat in it. Two sines a few Hz apart beat slowly
    against each other, which the ear hears as unease, and it does that without
    any dissonant interval to find grating."""
    length = int(RATE * 0.34)
    env = envelope(length, 0.004, 0.055)
    pair = mix(shape(sine(184.0, length), env),
               shape(sine(178.0, length), env))
    thud = shape(lowpass(noise(0.05, rng), 380.0),
                 envelope(int(RATE * 0.05), 0.002, 0.012))
    return mix(shape(pair, env), pad(thud, 0.13))


# Awards. Distinct from the pass sound on purpose: a trophy can land on a run
# that failed, so it must not be mistakable for one.

def trophy(rng):
    """Four notes up a major seventh chord, spaced evenly. Deliberately the
    longest and the only one that changes pitch more than once."""
    notes = [523.25, 659.25, 783.99, 1046.50]
    layers = []
    for index, freq in enumerate(notes):
        tone = bell(freq, 0.62, 0.095, partials=(1.0, 2.0), gains=(1.0, 0.12),
                    attack=0.005)
        layers.append(pad(tone, 0.085 * index))
    return mix(*layers)


BUILDERS = {
    "key-creamy": key_creamy,
    "key-creamy-space": key_creamy_space,
    "key-creamy-delete": key_creamy_delete,
    "key-clicky": key_clicky,
    "key-clicky-space": key_clicky_space,
    "key-clicky-delete": key_clicky_delete,
    "tap": tap,
    "toggle": toggle,
    "cue": cue,
    "open": open,
    "close": close,
    "pass": passed,
    "fail": failed,
    "trophy": trophy,
}


# A sound may not have more than this share of its energy above 6 kHz. It is
# the one rule that makes the set sound like one instrument rather than a
# collection, so it is checked rather than trusted.
MAX_BRIGHTNESS = 0.10
BRIGHT_ABOVE = 6000.0


def brightness(signal: list) -> float:
    """Energy above `BRIGHT_ABOVE` as a fraction of the whole."""
    smooth = lowpass(signal, BRIGHT_ABOVE)
    total = sum(value * value for value in signal) or 1.0
    return sum((signal[i] - smooth[i]) ** 2 for i in range(len(signal))) / total


def write(name: str, signal: list) -> int:
    peak = GAINS[name]
    samples = [int(max(-1.0, min(1.0, value)) * peak * 32767) for value in signal]
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(b"".join(struct.pack("<h", value) for value in samples))
    return os.path.getsize(path)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    total = 0
    failures = []
    for name, builder in BUILDERS.items():
        # One seed per file, derived from the name, so adding a sound cannot
        # change the noise in any other one.
        rng = random.Random(SEED + sum(name.encode()))
        # Faded first, then normalised, so the file's peak is exactly the gain
        # in the table above: the other order lets the fade-in eat the attack
        # and quietly pulls every peak below its intended level.
        signal = builder(rng)
        # The app's own voice gets one more pass on the way out. Keystrokes are
        # excluded: a keyboard has to keep its edge, and the two packs are only
        # different from each other because neither one is smoothed flat.
        if not name.startswith("key-"):
            signal = lowpass(signal, SOFT_CUTOFF)
        signal = normalise(fade(signal))
        bright = brightness(signal)
        if bright > MAX_BRIGHTNESS:
            failures.append(f"{name}: {bright * 100:.1f}% of its energy is above 6 kHz")
        size = write(name, signal)
        total += size
        print(f"  {name:<11} {len(signal) / RATE * 1000:>6.0f} ms  {size / 1024:>5.1f} KB  "
              f"{bright * 100:>5.2f}% above 6 kHz")
    print(f"  {'total':<11} {'':>6}     {total / 1024:>5.1f} KB in {os.path.relpath(OUT, ROOT)}")
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
