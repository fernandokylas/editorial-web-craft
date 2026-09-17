#!/usr/bin/env python3
"""Audit a stylesheet (or the <style> blocks of an HTML file) for cascade-layer hygiene.

Usage:  check_layers.py styles.css [page.html ...] [--order base,layout,components,utilities]

FAIL:
  - no `@layer a, b, c;` order statement, or it isn't the first layer-related statement
  - a layer used in a block that isn't in the order statement
  - rules outside any layer (unlayered CSS beats every layer — usually a mistake)
    (exempt: @import, @font-face, @property, @keyframes, :root/html token blocks, @media wrappers
     whose inner rules are layered)
  - `!important` inside base/layout/components (inverts layer precedence)
WARN:
  - `!important` in utilities (unnecessary — the layer already wins)
  - ID selectors
  - selectors with 4+ compound parts (deep chains)
  - a component rule setting gap/margin/padding on the *same property* a utility sets
"""
import re
import sys
from pathlib import Path

DEFAULT_ORDER = ["base", "layout", "components", "utilities"]


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def extract_css(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm"):
        return "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.I | re.S))
    return text


def split_blocks(css: str):
    """Yield (prelude, body) for top-level blocks, handling nesting."""
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j == -1:
            tail = css[i:].strip()
            if tail:
                for stmt in tail.split(";"):
                    if stmt.strip():
                        yield stmt.strip(), None
            return
        prelude = css[i:j].strip()
        # statements before this block (e.g. "@layer a,b;")
        if ";" in prelude:
            *stmts, prelude = prelude.split(";")
            for s in stmts:
                if s.strip():
                    yield s.strip(), None
            prelude = prelude.strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        yield prelude, css[j + 1:k - 1]
        i = k


EXEMPT = re.compile(r"^(@import|@font-face|@property|@keyframes|@charset|:root\b)", re.I)
WRAPPER = re.compile(r"^@(media|container|supports)\b", re.I)


def main() -> None:
    args = sys.argv[1:]
    order = DEFAULT_ORDER
    if "--order" in args:
        idx = args.index("--order")
        order = [s.strip() for s in args[idx + 1].split(",")]
        del args[idx:idx + 2]
    if not args:
        sys.exit(__doc__)

    failed = False
    for p in map(Path, args):
        css = strip_comments(extract_css(p))
        fails, warns = [], []

        # Order statement
        m = re.search(r"@layer\s+([\w\-\s,]+);", css)
        declared = [s.strip() for s in m.group(1).split(",")] if m else []
        if not declared:
            fails.append("no `@layer …;` order statement")
        else:
            first_layer_use = re.search(r"@layer\b", css)
            if first_layer_use and first_layer_use.start() != m.start():
                fails.append("order statement is not the first @layer usage")
            missing = [l for l in order if l not in declared]
            if missing:
                fails.append(f"order statement missing layers: {', '.join(missing)} (has: {', '.join(declared)})")

        used = set(re.findall(r"@layer\s+([\w-]+)\s*\{", css))
        for l in sorted(used - set(declared)):
            fails.append(f"layer `{l}` used but not in the order statement")

        # Unlayered rules
        unlayered = []
        for prelude, body in split_blocks(css):
            if body is None or not prelude:
                continue
            if prelude.startswith("@layer"):
                continue
            if EXEMPT.match(prelude):
                continue
            if re.match(r"@media\s*\(\s*prefers-reduced-motion", prelude):
                continue   # the one sanctioned unlayered block: the motion safety net (see reduced-motion-enforcer)
            if WRAPPER.match(prelude):
                inner = [pr for pr, b in split_blocks(body) if b is not None and pr]
                bad = [pr for pr in inner if not pr.startswith("@layer") and not EXEMPT.match(pr)]
                if bad:
                    unlayered.append(f"{prelude} > {bad[0]}")
                continue
            unlayered.append(prelude)
        if unlayered:
            fails.append(f"{len(unlayered)} unlayered rule(s) — they beat every layer: e.g. `{unlayered[0][:60]}`")

        # !important per layer
        layer_bodies = {}
        def collect(blocks):
            for prelude, body in blocks:
                if body is None or not prelude:
                    continue
                lm = re.match(r"@layer\s+([\w-]+)$", prelude)
                if lm:
                    layer_bodies[lm.group(1)] = layer_bodies.get(lm.group(1), "") + body
                elif WRAPPER.match(prelude):
                    collect(split_blocks(body))          # @media { @layer x { … } } counts too
        collect(split_blocks(css))
        for lname, body in layer_bodies.items():
            n_imp = body.count("!important")
            if n_imp and lname != order[-1]:
                fails.append(f"{n_imp} `!important` in @layer {lname} — inverts layer precedence")
            elif n_imp:
                warns.append(f"{n_imp} `!important` in @layer {lname} — unnecessary, the layer already wins")

        # Selector hygiene
        ids = []
        for sel_list in re.findall(r"([^{}\n;]+)\{", css):
            if not sel_list.strip().startswith("@"):
                ids += re.findall(r"(?<![\w\-#])#[a-zA-Z][\w-]*", sel_list)
        if ids:
            warns.append(f"{len(ids)} ID selector(s) — specificity spike, prefer classes")
        deep = []
        for sel_list in re.findall(r"([^{}\n;]+)\{", css):
            if sel_list.strip().startswith("@"):
                continue
            for sel in sel_list.split(","):
                if len(re.split(r"[\s>+~]+", sel.strip())) >= 4:
                    deep.append(sel)
        if deep:
            warns.append(f"{len(deep)} selector(s) with 4+ compound parts, e.g. `{deep[0].strip()[:50]}`")

        # Component vs utility property overlap
        comp, util = layer_bodies.get("components"), layer_bodies.get("utilities")
        if comp and util:
            cprops = set(re.findall(r"\b(gap|margin(?:-\w+)?|padding(?:-\w+)?)\s*:", comp))
            uprops = set(re.findall(r"\b(gap|margin(?:-\w+)?|padding(?:-\w+)?)\s*:", util))
            both = sorted(cprops & uprops)
            if both:
                warns.append(f"components and utilities both set {', '.join(both)} — fine under @layer, but confirm the utility is meant to win")

        print(f"{p}:")
        for w in warns: print(f"  WARN  {w}")
        for f in fails: print(f"  FAIL  {f}")
        if not fails and not warns:
            print(f"  OK    layers: {', '.join(declared)}")
        elif not fails:
            print(f"  ok    layers: {', '.join(declared)}")
        failed |= bool(fails)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
