#!/usr/bin/env python3
"""Audit files for motion that lacks a prefers-reduced-motion guard.

Usage:  check_motion.py file.html [more.css app.js ...]

For each file, lists motion sources found (transform transitions, @keyframes,
GSAP/anime/framer calls, smooth scroll, autoplay media, parallax hints) and
whether a guard exists:
  CSS guard:  @media (prefers-reduced-motion: reduce) { ... }   or  no-preference wrapping
  JS guard:   matchMedia("(prefers-reduced-motion") / gsap.matchMedia / useReducedMotion
Exit 1 if any file has motion and no guard of the matching kind.
"""
import re
import sys
from pathlib import Path

CSS_MOTION = [
    (r"transition[^;]*\btransform\b", "transition on transform"),
    (r"transition\s*:\s*all\b", "transition: all (animates transform implicitly)"),
    (r"@keyframes\s+[\w-]+", "@keyframes"),
    (r"\banimation(-name)?\s*:", "animation"),
    (r"scroll-behavior\s*:\s*smooth", "smooth scrolling"),
    (r"background-attachment\s*:\s*fixed", "parallax (background-attachment: fixed)"),
    (r"perspective\s*:|translateZ\(|translate3d\(", "3D transform"),
    (r"view-transition|animation-timeline\s*:", "scroll-driven / view transition"),
]
JS_MOTION = [
    (r"\bgsap\.(to|from|fromTo|timeline)\b", "GSAP tween/timeline"),
    (r"ScrollTrigger|scrub\s*:", "GSAP ScrollTrigger"),
    (r"\banime\s*\(|\banime\.timeline", "anime.js"),
    (r"framer-motion|<motion\.", "framer-motion"),
    (r"\.animate\(\s*\[", "Web Animations API"),
    (r"scrollIntoView\(\s*\{[^}]*smooth", "smooth scrollIntoView"),
]
HTML_MOTION = [
    (r"<video\b[^>]*\bautoplay\b", "autoplay video"),
    (r"<marquee\b", "marquee"),
    (r"data-(parallax|speed|scroll-speed)=", "parallax attribute"),
]
CSS_GUARD = re.compile(r"prefers-reduced-motion\s*:\s*(reduce|no-preference)", re.I)
JS_GUARD = re.compile(r"matchMedia\(\s*[\"'][^\"']*prefers-reduced-motion|gsap\.matchMedia|useReducedMotion|prefersReducedMotion", re.I)


def scan(text: str, patterns):
    found = []
    for pat, label in patterns:
        n = len(re.findall(pat, text, re.I))
        if n:
            found.append(f"{label} ×{n}")
    return found


def main() -> None:
    files = [Path(p) for p in sys.argv[1:]]
    if not files:
        sys.exit(__doc__)
    failed = False
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        ext = f.suffix.lower()
        css = text if ext == ".css" else "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.I | re.S))
        js = text if ext in (".js", ".mjs", ".ts", ".jsx", ".tsx") else "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", text, re.I | re.S))
        html = text if ext in (".html", ".htm") else ""

        css_m = scan(css, CSS_MOTION)
        js_m = scan(js, JS_MOTION)
        html_m = scan(html, HTML_MOTION)
        css_g = bool(CSS_GUARD.search(css))
        js_g = bool(JS_GUARD.search(js))

        print(f"{f}:")
        for m in css_m: print(f"  css   {m}")
        for m in js_m: print(f"  js    {m}")
        for m in html_m: print(f"  html  {m}")
        if not (css_m or js_m or html_m):
            print("  no motion sources found")
            continue

        if css_m and not css_g:
            print("  FAIL  CSS motion present but no @media (prefers-reduced-motion) block"); failed = True
        elif css_m:
            print("  ok    CSS guard present")
        if js_m and not js_g:
            print("  FAIL  JS motion present but no matchMedia/gsap.matchMedia reduced-motion check"); failed = True
        elif js_m:
            print("  ok    JS guard present")
        if html_m and not (css_g or js_g):
            print("  FAIL  autoplay/parallax markup with no reduced-motion handling"); failed = True
        elif html_m:
            print("  warn  autoplay/parallax markup — confirm the guard pauses/neutralises it")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
