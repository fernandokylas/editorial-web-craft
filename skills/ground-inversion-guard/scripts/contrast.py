#!/usr/bin/env python3
"""WCAG 2.x contrast checker for text/background pairs.

Usage:
  contrast.py "#1a1a1a" "#fcfbf9"                 # one pair
  contrast.py "#4ade80" "#0b0c10" --large         # large text (>=24px or >=19px bold)
  contrast.py --matrix "#0e6245,#4ade80" "#fcfbf9,#0b0c10"   # every fg × every bg

Reports ratio and AA / AAA pass for normal and large text, plus the 3:1
non-text threshold (UI components, borders, icons).

Exit code: 1 if any pair is below the threshold for the mode — 4.5:1 by default
(text), 3:1 with --large or --ui. Check hairlines/borders with --ui, not in the
same matrix as text.
"""
import argparse
import sys


def parse_hex(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise SystemExit(f"Bad hex colour: {h!r}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    r, g, b = (lin(c) for c in parse_hex(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def verdict(r: float) -> str:
    tags = []
    tags.append("AAA" if r >= 7 else "AA" if r >= 4.5 else "FAIL")
    tags.append("large:AAA" if r >= 4.5 else "large:AA" if r >= 3 else "large:FAIL")
    tags.append("ui:ok" if r >= 3 else "ui:FAIL")
    return "  ".join(tags)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fg", help="text colour, or comma list with --matrix")
    ap.add_argument("bg", help="background colour, or comma list with --matrix")
    ap.add_argument("--matrix", action="store_true", help="check every fg against every bg")
    ap.add_argument("--large", action="store_true", help="only print the large-text verdict (3:1 threshold)")
    ap.add_argument("--ui", action="store_true", help="non-text mode: 3:1 threshold for borders, icons, controls")
    a = ap.parse_args()

    fgs = a.fg.split(",") if a.matrix else [a.fg]
    bgs = a.bg.split(",") if a.matrix else [a.bg]
    worst_fail = False
    for bg in bgs:
        for fg in fgs:
            r = ratio(fg, bg)
            v = verdict(r)
            if a.large:
                v = v.split("  ")[1]
            elif a.ui:
                v = v.split("  ")[2]
            print(f"{fg.strip():>8} on {bg.strip():<8}  {r:5.2f}:1   {v}")
            if r < (3.0 if (a.large or a.ui) else 4.5):
                worst_fail = True
    sys.exit(1 if worst_fail else 0)


if __name__ == "__main__":
    main()
