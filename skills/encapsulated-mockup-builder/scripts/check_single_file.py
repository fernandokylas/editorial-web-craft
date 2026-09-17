#!/usr/bin/env python3
"""Verify an HTML mockup is genuinely self-contained.

Usage:  check_single_file.py prototype.html [--strict] [--allow-cdn] [--allow-fonts]

Fails (exit 1) on:
  - <link rel="stylesheet"> or <script src> pointing at local/relative files
  - <img>, <source>, <video>, <audio>, url() pointing at local paths (not data: / http(s))
  - more than one <style> block, or more than one inline <script> block
    (one extra tiny bootstrap <script> in <head>, under 160 chars — e.g. the html.js class — is allowed)
  - <svg> without a viewBox
  - a viewport meta tag missing
Warns on (FAIL instead with --strict; silenced with --allow-cdn / --allow-fonts):
  - remote CDN scripts/styles
  - remote web font stylesheets
Warns on:
  - hex colours used outside token blocks (mask/alpha-mask values are ignored)
  - file size over 400 KB
"""
import re
import sys
from pathlib import Path

REMOTE = re.compile(r"^(https?:)?//", re.I)
DATA = re.compile(r"^data:", re.I)


def is_local(url: str) -> bool:
    u = url.strip().strip("'\"")
    return not (REMOTE.match(u) or DATA.match(u) or u.startswith("#") or u.startswith("mailto:") or u == "")


def main() -> None:
    args = sys.argv[1:]
    allow_cdn, allow_fonts, strict = "--allow-cdn" in args, "--allow-fonts" in args, "--strict" in args
    errors, warns = [], []
    remote_bucket = errors if strict else warns
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 1:
        sys.exit(__doc__)
    path = Path(paths[0])
    html = path.read_text(encoding="utf-8")

    # External stylesheets / scripts
    for m in re.finditer(r"<link\b[^>]*\bhref\s*=\s*([\"'])(.*?)\1[^>]*>", html, re.I):
        tag, href = m.group(0), m.group(2)
        if re.search(r"rel\s*=\s*[\"']?stylesheet", tag, re.I):
            if is_local(href):
                errors.append(f"local stylesheet linked: {href}")
            elif "fonts.googleapis" in href or "fonts." in href:
                if not allow_fonts: remote_bucket.append(f"remote font stylesheet: {href}")
            else:
                if not allow_cdn: remote_bucket.append(f"remote stylesheet: {href}")
    for m in re.finditer(r"<script\b[^>]*\bsrc\s*=\s*([\"'])(.*?)\1", html, re.I):
        src = m.group(2)
        if is_local(src):
            errors.append(f"local script linked: {src}")
        elif not allow_cdn:
            remote_bucket.append(f"remote script: {src}")

    # @import inside <style> — same rules as <link>
    for m in re.finditer(r"@import\s+(?:url\(\s*)?[\"']?([^\"')\s;]+)", html, re.I):
        target = m.group(1)
        if is_local(target):
            errors.append(f"@import of a local stylesheet: {target}")
        elif "fonts." in target:
            if not allow_fonts: remote_bucket.append(f"@import remote font stylesheet: {target}")
        elif not allow_cdn:
            remote_bucket.append(f"@import remote stylesheet: {target}")

    # Media assets
    for m in re.finditer(r"<(img|source|video|audio|iframe)\b[^>]*\bsrc\s*=\s*([\"'])(.*?)\2", html, re.I):
        if is_local(m.group(3)):
            errors.append(f"<{m.group(1)}> points at a local path (will be missing): {m.group(3)}")
    for m in re.finditer(r"url\(\s*([\"']?)(.*?)\1\s*\)", html, re.I):
        if is_local(m.group(2)):
            errors.append(f"CSS url() points at a local path: {m.group(2)}")

    # Block counts
    n_style = len(re.findall(r"<style\b", html, re.I))
    inline_scripts = re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.I | re.S)
    head = (re.search(r"<head\b.*?</head>", html, re.I | re.S) or [""])[0]
    head_boot = [s for s in re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", head, re.I | re.S) if len(s.strip()) <= 160]
    n_script = len(inline_scripts) - min(len(head_boot), 1)   # one tiny head bootstrap is tolerated
    if n_style == 0:
        errors.append("no <style> block")
    elif n_style > 1:
        errors.append(f"{n_style} <style> blocks — consolidate into one in <head>")
    if n_script > 1:
        errors.append(f"{len(inline_scripts)} inline <script> blocks — one main block before </body> (plus at most one tiny bootstrap in <head>)")

    # SVG viewBox
    for m in re.finditer(r"<svg\b[^>]*>", html, re.I):
        if "viewbox" not in m.group(0).lower():
            errors.append(f"<svg> without viewBox: {m.group(0)[:60]}…")

    # Viewport meta
    if not re.search(r"<meta\b[^>]*name\s*=\s*[\"']viewport", html, re.I):
        errors.append("missing <meta name=\"viewport\">")

    # Token hygiene: hex colours outside :root
    style = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S))
    root_blocks = re.findall(r":root\s*\{[^}]*\}", style)
    # Any rule that declares custom properties (:root, .theme-*, [data-theme]) is a token block
    outside = re.sub(r"[^{}]*\{[^}]*--[\w-]+\s*:[^}]*\}", "", style)
    outside = re.sub(r"/\*.*?\*/", "", outside, flags=re.S)
    outside = re.sub(r"(-webkit-)?mask(-image)?\s*:[^;]*;", "", outside)   # alpha masks aren't colour choices
    stray = re.findall(r"#[0-9a-fA-F]{3,8}\b", outside)
    if stray:
        warns.append(f"{len(stray)} hex colour(s) outside :root (e.g. {stray[0]}) — prefer var(--token)")
    if not root_blocks:
        warns.append("no :root token block found")

    size_kb = path.stat().st_size / 1024
    if size_kb > 400:
        warns.append(f"file is {size_kb:.0f} KB — check for oversized data URIs")

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if not errors:
        print(f"OK    {path.name} is self-contained ({size_kb:.0f} KB, {n_style} style, {n_script} script)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
