#!/usr/bin/env python3
"""Draw the app icon on any platform, with no dependencies.

`app/Icon.swift` draws the same mark for the macOS bundle, and it is the
authoritative description of what the icon *is*: a petrol plate carrying a
brass ring that is a little over three quarters full, so the mark is the app's
progress indicator and its status at once. That is fine as a generator, and it
is useless as a way to ship an icon to Windows and Linux, because AppKit does
not exist on either of them and there is nothing to run `swiftc` against.

So the mark is drawn again here, in the standard library only: `zlib` for the
PNG, `struct` for the container. Same geometry, same colours, same sweep, so
the icon is recognisably one object across all three platforms. If the mark
changes, change it in both places -- the numbers below are transcribed from
Icon.swift and the comments say so where they are subtle.

Anti-aliasing is analytic rather than by supersampling: every pixel's coverage
comes from a signed distance function, so a 1024px icon is one pass of about a
million evaluations instead of sixteen. Pure Python supersampling at that size
takes minutes; this takes a second or two, and it is exact at the edge.

    python3 tools/make_icon.py --ico dist/Praccy.ico
    python3 tools/make_icon.py --png dist/icon.png --size 512
    python3 tools/make_icon.py --hicolor dist/share/icons   # Linux hicolor tree
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import sys
import zlib

# ── the mark, transcribed from app/Icon.swift ───────────────────────────

# Petrol plate, `--surface-2` at the top through a shade under `--canvas`.
PLATE_TOP = (0.102, 0.157, 0.173)
PLATE_BOTTOM = (0.047, 0.078, 0.086)
# Brass, the app's accent, and the soft pool of it behind the top of the plate.
ACCENT = (0.851, 0.643, 0.255)
GLOW_ALPHA = 0.22
TRACK_ALPHA = 0.20

# Apple's macOS icon grid: a 824pt rounded square with a 22.5% corner radius
# inside a 1024pt canvas. Windows and Linux have their own conventions (a
# square icon on Windows, a themeable one on most Linux desktops), but the
# plate is inset on all of them, so one geometry serves all three.
PLATE_FRACTION = 824 / 1024
CORNER_FRACTION = 0.225

# Drawn in a 36-unit space to match the SVG in the web UI, so the mark stays
# the same object at 16px in a taskbar and at 1024px on a desktop.
RADIUS_UNITS = 9.4
WIDTH_UNITS = 2.3
# "A little over three quarters": 4.9 of 2*pi, clockwise from the top, which is
# the direction a progress indicator fills on all three platforms.
SWEEP = 4.9

TOP = math.pi / 2  # 12 o'clock, in the y-down space the raster is written in


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return low if value < low else high if value > high else value


def _rounded_rect_distance(x: float, y: float, half: float, radius: float) -> float:
    """Signed distance from a point to a rounded square centred on the origin.

    Negative inside, positive outside. The corner term is what makes the
    radius right: a plain box would give the corners a hard corner, and the
    diagonal is where a rounded square's edge is furthest from the axis-aligned
    bound the rest of the shape is described by.
    """
    dx = abs(x) - (half - radius)
    dy = abs(y) - (half - radius)
    outside = math.hypot(max(dx, 0.0), max(dy, 0.0))
    return outside + min(max(dx, dy), 0.0) - radius


def _ring_band_distance(x: float, y: float, radius: float, half_width: float) -> float:
    """Distance from a point to the ring's stroke, ignoring the sweep."""
    return abs(math.hypot(x, y) - radius) - half_width


def _over(dst, src, alpha: float):
    """Composite `src` over `dst` at `alpha`. Both are (r, g, b) in 0..1."""
    return tuple(d + (s - d) * alpha for d, s in zip(dst, src))


def _render(size: int) -> bytes:
    """RGBA rows for one icon, as raw bytes with no PNG wrapper."""
    s = float(size)
    centre = s / 2.0
    half_plate = s * PLATE_FRACTION / 2.0
    corner = half_plate * CORNER_FRACTION
    radius = s * RADIUS_UNITS / 36.0
    half_width = s * WIDTH_UNITS / 36.0 / 2.0

    rows = bytearray()
    # One pixel of coverage per pixel of the image, so the antialiasing is a
    # function of distance rather than of a supersampling factor.
    for py in range(size):
        rows.append(0)  # PNG filter type 0 for this scanline
        y = py + 0.5 - centre
        for px in range(size):
            x = px + 0.5 - centre

            # The plate, and everything painted on it, is clipped to the
            # rounded square. Below, the transparent outside stays at alpha 0.
            plate = _rounded_rect_distance(x, y, half_plate, corner)
            plate_coverage = _clamp(0.5 - plate)
            if plate_coverage <= 0.0:
                rows.extend(b"\x00\x00\x00\x00")
                continue

            # Linear gradient down the plate, then the pool of accent behind
            # the top, so the material has a light source rather than being a
            # flat fill.
            t = _clamp((y + half_plate) / (2 * half_plate))
            colour = tuple(
                bottom + (top - bottom) * (1 - t)
                for top, bottom in zip(PLATE_TOP, PLATE_BOTTOM)
            )
            glow = max(0.0, 1.0 - math.hypot(x, y - (centre - s * 0.42)) / (s * 0.66))
            if glow > 0.0:
                colour = _over(colour, ACCENT, glow * glow * GLOW_ALPHA)

            # The unfilled track: the whole circle, thin and quiet.
            track = _ring_band_distance(x, y, radius, half_width)
            track_coverage = _clamp(0.5 - track) * TRACK_ALPHA
            if track_coverage > 0.0:
                colour = _over(colour, ACCENT, track_coverage)

            # The progress: the sweep, plus a round cap at each end. The ends
            # are discs rather than part of the band, which is what the round
            # cap in the Swift original draws and what stops the arc from
            # looking sawn off.
            angle = math.atan2(y, x)
            sweep = (angle - TOP) % (2 * math.pi)
            if sweep <= SWEEP:
                distance = _ring_band_distance(x, y, radius, half_width)
            else:
                end = TOP + SWEEP
                distance = min(
                    math.hypot(x - radius * math.cos(TOP),
                               y - radius * math.sin(TOP)),
                    math.hypot(x - radius * math.cos(end),
                               y - radius * math.sin(end)),
                ) - half_width
            progress = _clamp(0.5 - distance)
            if progress > 0.0:
                colour = _over(colour, ACCENT, progress)

            rows.extend((
                int(_clamp(colour[0]) * 255 + 0.5),
                int(_clamp(colour[1]) * 255 + 0.5),
                int(_clamp(colour[2]) * 255 + 0.5),
                int(plate_coverage * 255 + 0.5),
            ))
    return bytes(rows)


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + tag + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))


def _png(size: int, raw: bytes) -> bytes:
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def png_bytes(size: int) -> bytes:
    return _png(size, _render(size))


# ── containers ──────────────────────────────────────────────────────────

# Windows reads a PNG inside an .ico entry directly from Vista on, so the same
# encoded bytes are used for both the directory and the payload. Building the
# BMP/DIB form by hand would only add the alpha mask that PNG already carries.
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def write_ico(path: str, sizes=ICO_SIZES) -> None:
    images = [(size, png_bytes(size)) for size in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    directory = b""
    for size, payload in images:
        # 0 means 256 in the ICO directory, which is a byte rather than a
        # dimension; writing 256 there truncates to 0 and produces no entry.
        directory += struct.pack(
            "<BBBBHHII",
            0 if size >= 256 else size,
            0 if size >= 256 else size,
            0, 0, 1, 32,
            len(payload), offset,
        )
        offset += len(payload)
    with open(path, "wb") as handle:
        handle.write(header + directory + b"".join(p for _, p in images))


def write_png(path: str, size: int) -> None:
    with open(path, "wb") as handle:
        handle.write(png_bytes(size))


# The freedesktop hicolor tree. A Linux desktop will scale whatever it finds,
# but it looks for these paths by convention and falls back to a generic icon
# if they are missing, which is the difference between an app that looks
# installed and one that looks unpacked.
HICOLOR = {
    16: "16x16/apps", 24: "24x24/apps", 32: "32x32/apps",
    48: "48x48/apps", 64: "64x64/apps", 128: "128x128/apps",
    256: "256x256/apps", 512: "512x512/apps",
}


def write_hicolor(root: str, name: str = "praccy") -> None:
    for size, path in HICOLOR.items():
        directory = os.path.join(root, *path.split("/"))
        os.makedirs(directory, exist_ok=True)
        write_png(os.path.join(directory, f"{name}.png"), size)
    scalable = os.path.join(root, "scalable", "apps")
    os.makedirs(scalable, exist_ok=True)
    with open(os.path.join(scalable, f"{name}.svg"), "w", encoding="utf-8") as handle:
        handle.write(_svg())


def _svg() -> str:
    """The same mark as a vector, for the scalable hicolor slot."""
    side = 1024
    plate = int(side * PLATE_FRACTION)
    offset = (side - plate) / 2
    radius = side * RADIUS_UNITS / 36
    width = side * WIDTH_UNITS / 36
    centre = side / 2
    circumference = 2 * math.pi * radius
    top = (centre, centre - radius)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/make_icon.py. Same mark as app/Icon.swift. -->
<svg xmlns="http://www.w3.org/2000/svg" width="{side}" height="{side}"
     viewBox="0 0 {side} {side}">
  <defs>
    <linearGradient id="plate" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="rgb(12,20,22)"/>
      <stop offset="1" stop-color="rgb(26,40,44)"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.08" r="0.66">
      <stop offset="0" stop-color="rgb(217,164,65)" stop-opacity="0.22"/>
      <stop offset="1" stop-color="rgb(217,164,65)" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="{offset}" y="{offset}" width="{plate}" height="{plate}"
        rx="{plate * CORNER_FRACTION}" fill="url(#plate)"/>
  <rect x="{offset}" y="{offset}" width="{plate}" height="{plate}"
        rx="{plate * CORNER_FRACTION}" fill="url(#glow)"/>
  <circle cx="{centre}" cy="{centre}" r="{radius}" fill="none"
          stroke="rgb(217,164,65)" stroke-opacity="0.20" stroke-width="{width}"/>
  <circle cx="{top[0]}" cy="{top[1]}" r="{radius}" fill="none"
          stroke="rgb(217,164,65)" stroke-width="{width}" stroke-linecap="round"
          stroke-dasharray="{circumference * SWEEP / (2 * math.pi):.2f} {circumference:.2f}"
          transform="rotate(90 {centre} {centre})"/>
</svg>
"""


# ── .icns ───────────────────────────────────────────────────────────────

# macOS needs .icns, and the container is simple enough to write by hand: a
# header, then a table of (type, size, offset), then the PNGs. Every modern
# macOS reads a PNG entry, so this does not need the bitmap encodings that the
# format also allows. It exists because PyInstaller refuses a PNG icon on
# macOS, and `app/Icon.swift` cannot run on the two platforms that need the
# other formats -- so one renderer has to cover all three.
ICNS_TYPES = {
    16: "icp4",     # 16x16
    32: "icp5",     # 32x32, also the 16x16@2x
    64: "icp6",     # 64x64
    128: "ic07",    # 128x128
    256: "ic08",    # 256x256
    512: "ic09",    # 512x512
    1024: "ic10",   # 1024x1024
}
# 'icns' is the file type, and every entry is a PNG payload under a four
# character tag naming its pixel size.


def write_icns(path: str, sizes=(16, 32, 128, 256, 512, 1024)) -> None:
    images = [(ICNS_TYPES[size], png_bytes(size)) for size in sizes]
    # The table is sequential and length-prefixed, not a directory of offsets:
    # each entry is a four-character type and a length that *includes* its own
    # 8-byte header, and the reader walks forward by that length.
    #
    # An offset-based table is the other documented variant of the format, and
    # it is what this used to write. `iconutil` accepted the result -- the file
    # was well formed enough to pass validation -- and then extracted a single
    # 16x16 slot, because the first offset it followed pointed into the middle
    # of the first PNG. Comparing against an .icns that AppKit's own `iconutil`
    # had produced is what showed the difference; both formats validate, and
    # only one of them is the one macOS reads.
    entries = b"".join(
        struct.pack(">4sI", tag.encode().ljust(4, b"\0"), len(payload) + 8)
        + payload
        for tag, payload in images
    )
    with open(path, "wb") as handle:
        # The length in the header covers the header and every entry.
        handle.write(b"icns" + struct.pack(">I", 8 + len(entries)) + entries)


def main() -> int:
    parser = argparse.ArgumentParser(description="draw the Praccy icon")
    parser.add_argument("--ico", help="write a Windows .ico")
    parser.add_argument("--icns", help="write a macOS .icns")
    parser.add_argument("--png", help="write a single PNG")
    parser.add_argument("--size", type=int, default=512, help="size for --png")
    parser.add_argument("--hicolor", help="write a freedesktop hicolor tree here")
    args = parser.parse_args()

    if not any((args.ico, args.icns, args.png, args.hicolor)):
        parser.error("give at least one of --ico, --icns, --png, --hicolor")

    for flag, writer in (("--ico", write_ico), ("--icns", write_icns)):
        target = getattr(args, flag.lstrip("-"))
        if target:
            writer(target)
            print(f"  {flag[2:]:<6} {target} "
                  f"({os.path.getsize(target) // 1024}KB)")
    if args.png:
        write_png(args.png, args.size)
        print(f"  png    {args.png} {args.size}px "
              f"({os.path.getsize(args.png) // 1024}KB)")
    if args.hicolor:
        write_hicolor(args.hicolor)
        print(f"  hicolor {args.hicolor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
