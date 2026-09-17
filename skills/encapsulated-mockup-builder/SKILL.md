---
name: encapsulated-mockup-builder
description: >-
  Build front-end prototypes, mockups, landing pages, dashboards, component demos, and interactive UI
  concepts as ONE self-contained HTML file — a single <style> block in <head>, a single <script> block
  before </body>, tokens in :root, and every icon/graphic/image embedded inline (SVG or data URI) so
  the file opens and works with zero external dependencies, bundlers, or missing assets. Use this
  whenever the user asks for a prototype, mockup, demo, "quick page", "something I can open in the
  browser", "show me what it'd look like", an artifact/preview, a design handoff, or any front-end
  that isn't being wired into an existing build system — even if they don't say "single file". Also
  use when converting a React/Vue/Tailwind snippet into something runnable without npm.
---

# Encapsulated Mockup Builder

A prototype earns its keep by being *looked at*. A folder of `index.html` + `styles.css` + `app.js` + an `images/hero.png` that needs a dev server, or a JSX snippet that needs a bundler, delays that moment and usually breaks on the way. One HTML file that opens from a double-click, works offline, and renders exactly the same on the reviewer's laptop as it did in yours is the most reliable way to get a design in front of someone — and it's trivially shareable, diffable, and versionable.

So: everything in one file. Not as a constraint to work around, but as the unit of delivery.

## The structure

Start every artifact from `assets/boilerplate.html` and keep its four zones in order:

```
<head>
  <meta charset> <meta viewport> <title>
  <style>
    1. :root tokens  — colours, type scale, spacing, radius, motion. The only place raw values live.
       (+ .theme-inverted or [data-theme] blocks that re-map the same tokens)
    2. Reset, base, layout, components — everything references var(--token)
  </style>
</head>
<body>
  (inline SVG sprite, if icons repeat)
  3. Semantic markup — <main>, <section>, <nav>, <button>, real headings; #app-root if JS renders
  <script>
    4. One IIFE: state object, event delegation on the root, init on DOMContentLoaded
  </script>
</body>
```

Why tokens first: a reviewer's most common request is "can we see it in the brand green / with more breathing room". If every colour and spacing value is a `:root` variable, that's a one-line change that cascades everywhere. If values are scattered through the rules, it's a hunt.

Why one script block, as an IIFE with a `state` object and delegated events: prototypes grow. Three scattered `<script>` tags with global `let`s become unmaintainable by the second review round; a single closure with one `root.addEventListener('click', …)` dispatching on `data-action` scales to a real interactive demo without restructuring.

## Self-sufficiency rules

- **No local files.** No `<link href="styles.css">`, no `<script src="app.js">`, no `<img src="images/…">`. There is no `images/` — the file *is* the deliverable.
- **Graphics are inline.** Icons and decorations as inline SVG with `viewBox` and `currentColor` (the `inline-svg-decorator` skill covers drawing them; its `../inline-svg-decorator/references/icon-set.md` has a ready 24-grid set). Photos, if genuinely needed, as small data-URI JPEG/WebP — or, better, a styled placeholder block (`aspect-ratio`, a subtle gradient or SVG pattern, a caption) that communicates "image goes here" without pretending to be one.
- **Fonts fall back gracefully.** Default to `system-ui` / a system serif stack. A single Google Fonts `<link>` is acceptable when typography *is* the point — but the page must still look intentional when it's blocked, so the stack always ends in a system font.
- **Libraries are the exception, not the default.** Vanilla CSS and JS cover nearly every prototype. If a chart, map, or animation library (GSAP) is truly required, one or two CDN `<script>` tags are tolerable; note them in a comment and make sure the rest of the page renders if they fail. The containment check reports remote scripts and font links as WARNs (FAILs only with `--strict`), so the choice is visible without blocking the build.
- **Nothing that needs compiling.** No JSX, no SCSS, no TypeScript, no Tailwind classes without the runtime. If the user hands you a React component, translate it into markup + CSS + a few lines of vanilla JS that reproduce the same interaction.

## What "production-grade" means in a single file

- Semantic HTML: headings in order, `<button>` for actions, `<a>` for navigation, `<label>` for inputs, landmarks (`<main>`, `<nav>`, `<header>`). Screen-reader and keyboard behaviour come free with the right elements.
- Responsive without breakpoint spaghetti: fluid `clamp()` tokens for type and space, `grid` with `minmax()`/`auto-fit`, `max-width` measures for text. Media queries only where structure changes.
- Motion is opt-out: `transition` on hover/focus with the `--transition-smooth` token, and the `prefers-reduced-motion` safety net from `reduced-motion-enforcer` — unlayered, last in the stylesheet — which strips transforms but keeps ≤200ms fades and colour changes.
- States exist: hover, focus-visible, active, disabled, empty, loading, error — at least for the components the prototype is *about*. A mockup of a form with no error state hasn't answered the question the reviewer will ask.
- Content is real-shaped: plausible names, dates, numbers, sentence lengths. Lorem ipsum hides layout problems that real copy exposes.

## Delivering

1. Copy `assets/boilerplate.html`, rename the `<title>`, and build inside its zones.
2. Before handing it over, run the containment check:
   ```bash
   python scripts/check_single_file.py prototype.html
   ```
   It fails on any local link/asset, more than one `<style>`, more than one main `<script>` (one tiny bootstrap script in `<head>` is tolerated), `<svg>` without `viewBox`, or a missing viewport meta. It warns on remote scripts/fonts (`--strict` turns those into FAILs; `--allow-cdn` / `--allow-fonts` silence ones you've chosen), stray hex colours outside token blocks, and files over 400 KB. Fix every FAIL; treat WARNs as questions to answer deliberately.
3. Tell the user how to open it (double-click, or drag into a browser tab) and what to try — which buttons work, which states are demonstrated.

## Composes with

Horizontal padding lives on `.container`, not `body`, so an inverted `.band` or a wave divider can run edge to edge; put a `.container` inside each band. The boilerplate already carries the conventions from the sibling skills so they don't have to be re-derived: fluid `clamp()` type/space tokens (`fluid-clamp-calculator`), paired light/inverted token sets (`ground-inversion-guard`), optical nudges on the button (`visual-weight-tuner`), an inline sprite (`inline-svg-decorator`), and a `.container` that a `layout-editorial-rail` grid can drop straight into. Reach for those skills when the *content* of a zone needs their depth; this skill governs the *container*.
