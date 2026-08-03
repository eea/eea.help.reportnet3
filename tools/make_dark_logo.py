#!/usr/bin/env python3
"""
Produce a dark-background variant of the EEA logo for the site footer.

The EEA logo is black lettering plus a colourful starburst on transparency.
Material's footer strip is dark in both colour schemes, so the lettering is
invisible on it as supplied.

A CSS filter is not good enough here. `invert(1)` would flip the starburst's
teal and blue to orange and yellow, and `brightness(0) invert(1)` would flatten
the whole mark to solid white, discarding the brand colours. Instead this
recolours only the lettering, leaving the starburst exactly as it is.

Lettering is identified by saturation: the type is near-neutral (max and min
channel within 40 of each other) and dark, while the starburst is strongly
saturated. Lightness is mirrored rather than forced flat, which keeps the
anti-aliased edges of the type smooth instead of jagged.

Re-run this if the EEA ever updates its logo.

Usage:
  python tools/make_dark_logo.py

Dependencies:
  pip install pillow
"""

import argparse
from pathlib import Path

from PIL import Image

NEUTRAL_TOLERANCE = 40   # max-min channel spread below which a pixel is "grey"
DARKNESS_CEILING = 160   # only recolour pixels darker than this


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="docs/assets/theme/eea-logo.png")
    ap.add_argument("--output", default="docs/assets/theme/eea-logo-on-dark.png")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.is_file():
        raise SystemExit(f"ERROR: {src} not found")

    img = Image.open(src).convert("RGBA")
    px = img.load()
    width, height = img.size
    changed = 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if max(r, g, b) - min(r, g, b) < NEUTRAL_TOLERANCE \
                    and max(r, g, b) < DARKNESS_CEILING:
                v = 255 - r
                px[x, y] = (v, v, v, a)
                changed += 1

    out = Path(args.output)
    img.save(out, optimize=True)
    print(f"Recoloured {changed} lettering pixels, starburst untouched.")
    print(f"Wrote {out} ({img.size[0]}x{img.size[1]}, {out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
