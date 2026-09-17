#!/usr/bin/env python3
"""Lint HTML for non-native interactive patterns and missing semantics.

Usage:  check_semantics.py page.html [more.html ...]

FAIL:
  - onclick / role=button on <div>, <span>, <a>
  - <a href="#"> or <a href="javascript:…"> used as a button
  - <div>/<span> with tabindex (fake focusables)
  - accordion-shaped markup (class contains accordion|collapse|disclosure) without <details>
  - modal-shaped markup (class/id contains modal|dialog) without <dialog>
  - no <main>; more than one <main>
  - heading levels that skip (h2 → h4)
WARN:
  - <button> without type
  - <section> without a heading
  - multiple <nav> without aria-label
  - <img> without alt
"""
import re
import sys
from pathlib import Path


def main() -> None:
    files = sys.argv[1:]
    if not files:
        sys.exit(__doc__)
    failed = False
    for p in files:
        html = Path(p).read_text(encoding="utf-8", errors="replace")
        body = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.I | re.S)
        fails, warns = [], []

        for m in re.finditer(r"<(div|span|a|li|td|p)\b[^>]*\bonclick\s*=", body, re.I):
            fails.append(f"onclick on <{m.group(1)}> — use <button>")
        for m in re.finditer(r"<(div|span|a)\b[^>]*\brole\s*=\s*[\"']button", body, re.I):
            fails.append(f"role=button on <{m.group(1)}> — use <button>")
        for m in re.finditer(r"<a\b[^>]*\bhref\s*=\s*[\"'](#|javascript:[^\"']*)[\"']", body, re.I):
            fails.append(f"<a href=\"{m.group(1)}\"> acting as a button — use <button>")
        for m in re.finditer(r"<(div|span)\b[^>]*\btabindex\s*=", body, re.I):
            fails.append(f"tabindex on <{m.group(1)}> — fake focusable; use a native control")

        has_details = bool(re.search(r"<details\b", body, re.I))
        if re.search(r"class\s*=\s*[\"'][^\"']*\b(accordion|collapse|collapsible|disclosure)\b", body, re.I) and not has_details:
            fails.append("accordion/disclosure markup without <details>/<summary>")
        has_dialog = bool(re.search(r"<dialog\b", body, re.I))
        if re.search(r"(class|id)\s*=\s*[\"'][^\"']*\b(modal|dialog)\b", body, re.I) and not has_dialog:
            fails.append("modal/dialog markup without <dialog>")

        mains = len(re.findall(r"<main\b", body, re.I))
        if mains == 0:
            fails.append("no <main> landmark")
        elif mains > 1:
            fails.append(f"{mains} <main> elements — only one allowed")

        levels = [int(l) for l in re.findall(r"<h([1-6])\b", body, re.I)]
        for a, b in zip(levels, levels[1:]):
            if b > a + 1:
                fails.append(f"heading skips h{a} → h{b}")
                break

        for m in re.finditer(r"<button\b(?![^>]*\btype\s*=)[^>]*>", body, re.I):
            warns.append("<button> without type (defaults to submit inside forms)")
            break
        for m in re.finditer(r"<section\b[^>]*>(.*?)</section>", body, re.I | re.S):
            if not re.search(r"<h[1-6]\b", m.group(1), re.I):
                warns.append("<section> without a heading — probably a <div>")
                break
        navs = re.findall(r"<nav\b[^>]*>", body, re.I)
        if len(navs) > 1 and any("aria-label" not in n.lower() for n in navs):
            warns.append(f"{len(navs)} <nav> elements; label each with aria-label")
        if re.search(r"<img\b(?![^>]*\balt\s*=)[^>]*>", body, re.I):
            warns.append("<img> without alt")

        print(f"{p}:")
        for w in warns: print(f"  WARN  {w}")
        for f in fails: print(f"  FAIL  {f}")
        if not fails and not warns:
            print("  OK")
        failed |= bool(fails)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
