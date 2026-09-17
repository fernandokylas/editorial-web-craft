#!/usr/bin/env python3
"""Lint HTML/CSS for layout-shift risks.

Usage:  check_cls.py page.html [styles.css ...]

FAIL:
  - <img> / <video> / <iframe> / <embed> with no width+height attributes AND no
    aspect-ratio on its own class/style or on its immediate wrapper
  - @font-face with a web font src but no font-display
  - content-visibility: auto without contain-intrinsic-size in the same rule
  - transition/animation on height, width, top, left, margin, padding
WARN:
  - <img> with width/height but CSS class sets only width (missing height: auto)
  - elements with class/id matching feed|dynamic|async|data|chart|ad|embed|slot
    with no min-height / height / aspect-ratio in CSS
  - <img loading="lazy"> that appears before the first <h1>/<main> (likely above the fold)
  - missing scrollbar-gutter on html/body
  - @font-face fallback without size-adjust/ascent-override
"""
import re
import sys
from pathlib import Path


def css_rules(css: str):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel = m.group(1).strip()
        if sel.startswith("@") and not sel.startswith("@font-face"):
            continue
        yield sel, m.group(2)


def classes_with(css, prop_regex):
    out = set()
    for sel, body in css_rules(css):
        if re.search(prop_regex, body, re.I):
            out.update(re.findall(r"\.([\w-]+)", sel))
    return out


def main() -> None:
    files = [Path(p) for p in sys.argv[1:]]
    if not files:
        sys.exit(__doc__)
    html = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files if f.suffix.lower() in (".html", ".htm"))
    css = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files if f.suffix.lower() == ".css")
    css += "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S))
    fails, warns = [], []

    ar_classes = classes_with(css, r"aspect-ratio\s*:")
    h_classes = classes_with(css, r"\b(min-height|height|aspect-ratio)\s*:")
    hauto_classes = classes_with(css, r"height\s*:\s*auto")
    w_only = classes_with(css, r"\bwidth\s*:") - hauto_classes - ar_classes

    # Media elements
    tag_re = re.compile(r"<(img|video|iframe|embed|object)\b([^>]*)>", re.I)
    first_content = re.search(r"<(h1|main)\b", html, re.I)
    fold_pos = first_content.start() if first_content else len(html)
    for m in tag_re.finditer(html):
        tag, attrs = m.group(1).lower(), m.group(2)
        has_wh = re.search(r"\bwidth\s*=", attrs) and re.search(r"\bheight\s*=", attrs)
        own_classes = set(re.findall(r"[\w-]+", (re.search(r'class\s*=\s*"([^"]*)"', attrs) or [None, ""])[1]))
        own_style_ar = "aspect-ratio" in (re.search(r'style\s*=\s*"([^"]*)"', attrs) or [None, ""])[1]
        # immediate wrapper: nearest preceding opening tag
        before = html[:m.start()]
        wrap = re.search(r"<(div|figure|picture|a|span|section|article)\b([^>]*)>\s*(?:<!--.*?-->\s*)?$", before, re.I | re.S)
        wrap_classes = set()
        wrap_style_ar = False
        if wrap:
            wrap_classes = set(re.findall(r"[\w-]+", (re.search(r'class\s*=\s*"([^"]*)"', wrap.group(2)) or [None, ""])[1]))
            wrap_style_ar = "aspect-ratio" in (re.search(r'style\s*=\s*"([^"]*)"', wrap.group(2)) or [None, ""])[1]
        reserved = has_wh or own_style_ar or wrap_style_ar or (own_classes & ar_classes) or (wrap_classes & ar_classes) or (own_classes & h_classes and tag != "img")
        snippet = m.group(0)[:70].replace("\n", " ")
        if not reserved:
            fails.append(f"<{tag}> with no reserved dimensions: {snippet}…")
        elif has_wh and tag == "img" and (own_classes & w_only):
            warns.append(f"<img> has width/height attrs but its class sets width without height:auto — ratio may be overridden: {snippet}…")
        if tag == "img" and re.search(r'loading\s*=\s*"lazy"', attrs) and m.start() < fold_pos:
            warns.append(f"<img loading=\"lazy\"> before first <h1>/<main> — likely above the fold: {snippet}…")

    # Dynamic containers
    dyn = re.finditer(r"<\w+\b[^>]*\b(class|id)\s*=\s*\"([^\"]*\b(feed|dynamic|async|chart|advert|ad|embed|slot|widget)\b[^\"]*)\"", html, re.I)
    for m in dyn:
        cls = set(re.findall(r"[\w-]+", m.group(2)))
        if not (cls & h_classes) and "aspect-ratio" not in m.group(0):
            warns.append(f"dynamic container `{m.group(2)[:40]}` has no min-height/height/aspect-ratio")

    # Fonts
    for sel, body in css_rules(css):
        if sel.startswith("@font-face"):
            is_web = re.search(r"url\(", body, re.I)
            if is_web and "font-display" not in body:
                fails.append("@font-face with remote src but no font-display")
            if re.search(r"src\s*:\s*local\(", body, re.I) and not re.search(r"size-adjust|ascent-override", body):
                warns.append("@font-face fallback (local src) without size-adjust/ascent-override — swap will reflow")
        if re.search(r"content-visibility\s*:\s*auto", body) and "contain-intrinsic-size" not in body:
            fails.append(f"`{sel}` uses content-visibility: auto without contain-intrinsic-size")
        if re.search(r"(transition|animation)[^;]*(?<![\w-])(height|width|top|left|right|bottom|margin|padding)(?![\w-])", body):
            fails.append(f"`{sel}` transitions/animates a layout property")

    if not re.search(r"scrollbar-gutter", css):
        warns.append("no scrollbar-gutter: stable — content width shifts when a scrollbar appears")

    for w in warns: print(f"WARN  {w}")
    for f in fails: print(f"FAIL  {f}")
    if not fails and not warns:
        print("OK    no layout-shift risks found")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
