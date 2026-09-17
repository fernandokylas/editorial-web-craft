#!/usr/bin/env python3
"""Derive a CSS clamp() whose preferred value hits MIN exactly at the mobile
floor and MAX exactly at the desktop ceiling.

Usage:
  clamp.py --min 3rem --max 12rem
  clamp.py --min 16px --max 40px --min-vw 320 --max-vw 1200
  clamp.py --min 1rem --max 2.25rem --name fs-h2      # prints as a custom property

Sizes accept rem or px (px converted at 16px/rem). Viewport bounds are px.
"""
import argparse
import re

REM = 16.0


def to_rem(value: str) -> float:
    m = re.fullmatch(r"\s*([\d.]+)\s*(rem|px|em)?\s*", value)
    if not m:
        raise SystemExit(f"Can't parse size: {value!r} (use e.g. 3rem or 48px)")
    n, unit = float(m.group(1)), m.group(2) or "rem"
    return n / REM if unit == "px" else n


def fmt(n: float, places: int = 3) -> str:
    s = f"{n:.{places}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min", required=True, help="size at the mobile floor (rem or px)")
    ap.add_argument("--max", required=True, help="size at the desktop ceiling (rem or px)")
    ap.add_argument("--min-vw", type=float, default=320, help="mobile floor in px (default 320)")
    ap.add_argument("--max-vw", type=float, default=1440, help="desktop ceiling in px (default 1440)")
    ap.add_argument("--name", help="emit as --name: clamp(...); for a :root block")
    a = ap.parse_args()

    lo, hi = to_rem(a.min), to_rem(a.max)
    vw_lo, vw_hi = a.min_vw / REM, a.max_vw / REM
    if vw_hi <= vw_lo:
        raise SystemExit("--max-vw must be greater than --min-vw")

    slope = (hi - lo) / (vw_hi - vw_lo)          # rem per rem of viewport
    intercept = lo - slope * vw_lo               # rem
    vw_term = slope * 100                        # as vw units

    preferred = f"calc({fmt(intercept)}rem + {fmt(vw_term)}vw)"
    if abs(intercept) < 0.0005:                  # pure vw is cleaner when it works out
        preferred = f"{fmt(vw_term)}vw"

    # clamp() handles inverted ranges, but flag it since it's usually a mistake
    a_min, a_max = (lo, hi) if lo <= hi else (hi, lo)
    expr = f"clamp({fmt(a_min)}rem, {preferred}, {fmt(a_max)}rem)"

    if a.name:
        print(f"--{a.name.lstrip('-')}: {expr};")
    else:
        print(expr)

    # Show what it resolves to at the boundaries and midpoint so the result is checkable
    for px in (a.min_vw, (a.min_vw + a.max_vw) / 2, a.max_vw):
        v = intercept + slope * (px / REM)
        v = min(max(v, a_min), a_max)
        print(f"  @ {int(px)}px viewport → {fmt(v, 2)}rem ({fmt(v * REM, 1)}px)")


if __name__ == "__main__":
    main()
