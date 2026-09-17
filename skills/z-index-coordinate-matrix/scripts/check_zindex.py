#!/usr/bin/env python3
"""Audit z-index usage against a token matrix.

Usage:  check_zindex.py styles.css [page.html ...] [--max 500]

FAIL:
  - raw numeric z-index outside a token definition (e.g. `z-index: 999`)
  - z-index above --max (default 500) or a "magic" value (99, 999, 9999, 2147483647…)
  - z-index: var(--z-…) referencing a token that isn't declared
  - z-index on a rule with no position/display context (position static → ignored)
WARN:
  - a rule creating a stacking context by side effect (transform, filter, opacity<1,
    will-change, mix-blend-mode, backdrop-filter, contain: paint/layout) that also
    contains an overlay-ish child selector (tooltip|popover|dropdown|menu|modal)
  - !important on z-index
  (declaring all seven tiers with some unused is expected, not warned)
"""
import re
import sys
from pathlib import Path

MAGIC = {"99", "999", "9999", "99999", "999999", "2147483647", "1000", "10000"}
CTX_PROPS = re.compile(r"(?<![\w-])(transform|filter|will-change|mix-blend-mode|backdrop-filter|perspective|clip-path|mask)\s*:|(?<![\w-])opacity\s*:\s*0?\.\d|(?<![\w-])contain\s*:\s*[^;]*(paint|layout|strict|content)", re.I)


def rules(css: str):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel = m.group(1).strip()
        if sel.startswith("@") and not sel.startswith("@layer"):
            continue
        yield sel, m.group(2)


def main() -> None:
    args = sys.argv[1:]
    zmax = 500
    if "--max" in args:
        i = args.index("--max"); zmax = int(args[i + 1]); del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    css = ""
    for p in map(Path, args):
        t = p.read_text(encoding="utf-8", errors="replace")
        css += t if p.suffix.lower() == ".css" else "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", t, re.I | re.S))

    fails, warns = [], []
    declared = dict(re.findall(r"(--z-[\w-]+)\s*:\s*(-?\d+)\s*;", css))
    used = set()
    nonlocal_z = False

    for sel, body in rules(css):
        is_token_block = bool(re.search(r"--z-[\w-]+\s*:", body))
        for m in re.finditer(r"z-index\s*:\s*([^;]+);", body):
            val = m.group(1).strip()
            if "!important" in val:
                warns.append(f"`{sel}` z-index !important — fix the stacking context instead")
                val = val.replace("!important", "").strip()
            tok = re.match(r"var\(\s*(--z-[\w-]+)", val)
            if tok:
                used.add(tok.group(1))
                if tok.group(1) not in declared:
                    fails.append(f"`{sel}` uses {tok.group(1)} which isn't declared")
            elif val == "auto":
                pass
            elif re.fullmatch(r"-?\d+", val):
                n = int(val)
                if is_token_block:
                    continue
                if val in MAGIC or abs(n) > zmax:
                    fails.append(f"`{sel}` z-index: {val} — magic number; map to a --z- token")
                elif n not in (0, 1, -1):
                    fails.append(f"`{sel}` z-index: {val} — raw number; use var(--z-…)")
                    nonlocal_z = True
                # 0/1/-1 are tolerated as local ordering inside an isolated context
            if not re.search(r"position\s*:\s*(relative|absolute|fixed|sticky)|display\s*:\s*(grid|flex|inline-grid|inline-flex)", body) \
               and not is_token_block and val != "auto":
                fails.append(f"`{sel}` sets z-index without position (or a grid/flex item context) — it has no effect")
        if CTX_PROPS.search(body) and re.search(r"card|panel|item|row|tile", sel, re.I) and "::" not in sel \
           and not re.search(r":(hover|active|focus)", sel):   # a hover-only transform is a context only while hovered
            warns.append(f"`{sel}` creates a stacking context (transform/filter/opacity/…) — any tooltip/popover inside it can't rise above siblings; portal overlays or use popover/dialog top layer")

    # Declaring the full seven-tier matrix is the rule, so unused tiers are not a warning.
    if not declared and (used or nonlocal_z):
        fails.append("no --z- token matrix declared")

    for w in warns: print(f"WARN  {w}")
    for f in fails: print(f"FAIL  {f}")
    if not fails and not warns:
        print(f"OK    tokens: {', '.join(f'{k}={v}' for k, v in declared.items())}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
