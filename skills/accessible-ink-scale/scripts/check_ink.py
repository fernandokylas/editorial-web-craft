#!/usr/bin/env python3
"""Find small-text rules that lack weight/tracking/leading compensation.

Usage:  check_ink.py styles.css [page.html ...]

Scans every rule with an explicit small font-size (≤ 0.875rem / 14px / 0.8125rem …)
and reports:
  FAIL  size ≤ 14px with font-weight missing or < 500
  FAIL  size ≤ 13px with no positive letter-spacing
  FAIL  text-transform: uppercase with letter-spacing < 0.08em
var(--token) values are resolved from any custom property declared in the file;
an unresolvable var() is skipped, not failed.
  FAIL  any font-size < 12px / 0.75rem
  WARN  size ≤ 14px with line-height < 1.4
  WARN  colour #fff/#ffffff used on text inside .theme-inverted / dark selectors
  WARN  -webkit-font-smoothing: antialiased outside an inverted/dark selector
Inherited values aren't tracked, so a FAIL means "not set in this rule" — confirm
the compensation isn't coming from a parent before changing it.
"""
import re
import sys
from pathlib import Path

REM = 16.0
WEIGHT_NAMES = {"normal": 400, "bold": 700, "lighter": 300, "bolder": 700}


def to_px(v: str):
    m = re.fullmatch(r"\s*([\d.]+)\s*(px|rem|em|pt)?\s*", v)
    if not m:
        return None
    n, u = float(m.group(1)), (m.group(2) or "px")
    if u == "em":
        return None                          # relative to the parent — unknowable here, so skipped
    return {"px": n, "rem": n * REM, "pt": n * 4 / 3}[u]


def to_em(v: str):
    m = re.fullmatch(r"\s*(-?[\d.]+)\s*(em|rem|px)?\s*", v)
    if not m:
        return None
    n, u = float(m.group(1)), (m.group(2) or "px")
    return n if u in ("em", "rem") else n / REM


TOKENS = {}


def resolve(v):
    """Resolve var(--x) one level from declared custom properties; None if unknown."""
    if v is None:
        return None
    m = re.fullmatch(r"\s*var\(\s*(--[\w-]+)\s*(?:,\s*([^)]*))?\)\s*", v)
    if not m:
        return v
    return TOKENS.get(m.group(1), m.group(2))


def rules(css: str):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    TOKENS.update({k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)(?=[;}])", css)})
    # flatten @layer/@media wrappers: we only need selector { decls }
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if sel.startswith("@"):
            continue
        decls = {}
        for d in body.split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decls[k.strip().lower()] = v.strip().split("!")[0].strip()
        yield sel, decls


def main() -> None:
    files = sys.argv[1:]
    if not files:
        sys.exit(__doc__)
    failed = False
    for p in map(Path, files):
        text = p.read_text(encoding="utf-8", errors="replace")
        css = text if p.suffix.lower() == ".css" else "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.I | re.S))
        fails, warns = [], []
        for sel, d in rules(css):
            dark = bool(re.search(r"inverted|dark|obsidian", sel, re.I))
            fs = resolve(d.get("font-size"))
            px = to_px(fs) if fs else None
            w = resolve(d.get("font-weight"))
            weight = WEIGHT_NAMES.get(w, None) if w else None
            if w and w.isdigit():
                weight = int(w)
            ls = resolve(d.get("letter-spacing"))
            ls_em = to_em(ls) if ls else None
            lh = resolve(d.get("line-height"))
            upper = d.get("text-transform", "").lower() == "uppercase"

            if px is not None:
                if px < 12:
                    fails.append(f"`{sel}` font-size {fs} is below the 12px floor")
                if px <= 14 and (weight is None or weight < 500):
                    fails.append(f"`{sel}` at {fs} has font-weight {w or 'unset'} — boost to ≥500")
                if px <= 13 and (ls_em is None or ls_em <= 0):
                    fails.append(f"`{sel}` at {fs} has no positive letter-spacing — add ≥0.04em")
                if px <= 14 and lh:
                    try:
                        if float(lh) < 1.4:
                            warns.append(f"`{sel}` at {fs} has line-height {lh} — small text wants ≥1.4")
                    except ValueError:
                        pass
            if upper and (ls is None or (ls_em is not None and ls_em < 0.08)):
                fails.append(f"`{sel}` is uppercase with letter-spacing {ls or 'unset'} — needs ≥0.08em")
            col = d.get("color", "").lower().replace(" ", "")
            if dark and col in ("#fff", "#ffffff", "white"):
                warns.append(f"`{sel}` uses pure white text on a dark ground — halation; use #e0e0e0–#f5f5f5")
            if d.get("-webkit-font-smoothing") == "antialiased" and not dark:
                warns.append(f"`{sel}` sets -webkit-font-smoothing: antialiased on a light ground — thins text")

        print(f"{p}:")
        for w_ in warns: print(f"  WARN  {w_}")
        for f in fails: print(f"  FAIL  {f}")
        if not fails and not warns:
            print("  OK")
        failed |= bool(fails)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
