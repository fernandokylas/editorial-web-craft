#!/usr/bin/env python3
"""Generate an inline SVG section divider from parameters, with integer-aligned
coordinates and currentColor fill so it inherits the parent's theme colour.

Usage:
  wave.py                                  # 1200x120, 2 crests, gentle
  wave.py --crests 3 --amplitude 50
  wave.py --style tilt --height 80         # straight diagonal cut
  wave.py --style steps --crests 6         # blocky ledger-style steps
  wave.py --flip                           # mirror vertically (top of a section)
  wave.py --class-name hero-wave --seed 7  # deterministic organic variation

Styles: wave (cubic béziers), tilt (diagonal), steps (square wave).
Output is a complete <svg> element ready to paste; the fill is currentColor.
"""
import argparse
import random


def wave_path(w: int, h: int, crests: int, amp: int, rng: random.Random | None) -> str:
    """Smooth wave across the top edge, closed along the bottom."""
    halves = crests * 2                      # one crest = one up + one down
    seg = w / halves
    mid = h // 2
    pts = [f"M0,{mid}"]
    x = 0.0
    for i in range(halves):
        jitter = rng.randint(-amp // 4, amp // 4) if rng else 0
        up = -amp if i % 2 == 0 else amp
        c1x, c2x = round(x + seg * 0.35), round(x + seg * 0.65)
        end_x = round(x + seg)
        pts.append(f"C{c1x},{mid + up + jitter} {c2x},{mid - up - jitter} {end_x},{mid}")
        x += seg
    pts.append(f"L{w},{h} L0,{h} Z")
    return " ".join(pts)


def tilt_path(w: int, h: int) -> str:
    return f"M0,{h} L{w},0 L{w},{h} Z"


def steps_path(w: int, h: int, crests: int) -> str:
    seg = w // crests
    hi, lo = h // 3, (h * 2) // 3
    pts = [f"M0,{lo}"]
    x = 0
    for i in range(crests):
        y = hi if i % 2 == 0 else lo
        pts.append(f"V{y} H{x + seg}")
        x += seg
    pts.append(f"V{h} H0 Z")
    return " ".join(pts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--height", type=int, default=120)
    ap.add_argument("--crests", type=int, default=1, help="full wave periods across the width")
    ap.add_argument("--amplitude", type=int, default=40, help="wave height in viewBox units")
    ap.add_argument("--style", choices=["wave", "tilt", "steps"], default="wave")
    ap.add_argument("--seed", type=int, help="add organic jitter, reproducibly")
    ap.add_argument("--flip", action="store_true", help="mirror vertically for a section top edge")
    ap.add_argument("--class-name", default="vector-divider")
    a = ap.parse_args()

    rng = random.Random(a.seed) if a.seed is not None else None
    if a.style == "wave":
        d = wave_path(a.width, a.height, a.crests, a.amplitude, rng)
    elif a.style == "tilt":
        d = tilt_path(a.width, a.height)
    else:
        d = steps_path(a.width, a.height, a.crests)

    transform = f' transform="scale(1,-1) translate(0,-{a.height})"' if a.flip else ""
    print(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.width} {a.height}" '
        f'preserveAspectRatio="none" class="{a.class_name}" aria-hidden="true" focusable="false">\n'
        f'  <path d="{d}" fill="currentColor"{transform}/>\n'
        f'</svg>'
    )


if __name__ == "__main__":
    main()
