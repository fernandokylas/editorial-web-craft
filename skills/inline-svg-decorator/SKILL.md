---
name: inline-svg-decorator
description: >-
  Build crisp, theme-aware inline SVGs — icons, section dividers/waves, decorative shapes, logos,
  simple illustrations, chart marks — from clean parametric coordinates instead of icon fonts,
  external image links, emoji, or text placeholders like "[icon]". Every SVG gets an explicit viewBox,
  scales with its container, uses currentColor so it inherits the theme, and sits on integer
  coordinates so strokes stay sharp. Use this whenever HTML/JSX/CSS output needs any graphic: icons in
  buttons/nav/lists, a hero or footer divider, background decoration, a placeholder logo,
  arrows/checks/chevrons, or when the user says "add an icon", "make a wave", "section divider",
  "decorative shape", "use SVG", "no icon library", or the design would otherwise reach for Font
  Awesome / Lucide / an <img> that doesn't exist.
---

# Inline SVG Decorator

Icon fonts ship hundreds of glyphs to draw six, break when the font fails to load, and can't be themed per-path. External `<img src="wave.svg">` links break the moment the asset isn't there — which in generated code is always. Emoji and `[icon]` placeholders read as unfinished. An inline SVG built from a few integer coordinates is lighter than any of those, styles with ordinary CSS, and inherits colour from the text around it.

Draw what's needed, at the size it's needed, with the fewest points that still read cleanly.

## The four non-negotiables

**1. Explicit `viewBox`, no fixed `width`/`height` attributes.** The viewBox defines the coordinate space; CSS defines the rendered size. Standard grids: `0 0 24 24` for UI icons, `0 0 1200 120` for full-width dividers, `0 0 800 400` for section backgrounds. Then size in CSS:

```css
.icon   { width: 1em; height: 1em; }             /* follows the font size */
.divider{ width: 100%; height: clamp(2.5rem, 8vw, 5rem); display: block; }
```

`preserveAspectRatio="none"` only on dividers and backgrounds that are meant to stretch; never on icons (they'd distort).

**2. `currentColor`, never hex, inside the SVG.** `fill="currentColor"` or `stroke="currentColor"` on paths, then colour the *wrapper* with a theme token. One SVG, every theme:

```html
<div class="editorial-divider">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none"
       class="vector-wave" aria-hidden="true" focusable="false">
    <path d="M0,60 C150,90 350,120 600,40 C850,-40 1050,30 1200,10 L1200,120 L0,120 Z" fill="currentColor"/>
  </svg>
</div>
```
```css
.editorial-divider { color: var(--accent-solid); opacity: 0.08; line-height: 0; overflow: hidden; }
.vector-wave       { width: 100%; height: clamp(2.5rem, 8vw, 5rem); display: block; }
```

Two colours in one graphic? Use `currentColor` for the primary and a CSS custom property (`fill="var(--accent-text)"`) for the secondary — still no literals. Multi-colour illustrations get a `<style>` block scoped by class inside the SVG or CSS variables set on the wrapper.

**3. Integer (or clean half) coordinates.** `M4 12h16` renders sharp; `M4.27 11.86h15.9` smears across pixel boundaries and looks soft at 16px. Round while drawing, not after. For a 1px-effective stroke on an odd stroke width, coordinates on the `.5` grid line up on pixel centres.

**4. Stroke consistency across a set.** Related icons share one `stroke-width` (`1.5` on a 24-grid is the workhorse), the same `stroke-linecap`/`stroke-linejoin` (`round` for a friendly set, `square`/`miter` for a technical one). When a stroked shape must scale without its line thickening — a chart line, a map outline, a large decorative outline — add `vector-effect: non-scaling-stroke`.

## Building the graphic

- **Icons:** don't retrace common glyphs. Take them from `references/icon-set.md` — twenty crisp 24-grid stroke icons plus the `<symbol>`/`<use>` sprite pattern for icons that repeat. Draw a new one only when the set lacks it, and draw it on the same grid and stroke.
- **Dividers, waves, tilts, steps:** generate them rather than hand-typing béziers. `python scripts/wave.py --crests 3 --amplitude 50 --seed 7` emits a complete `<svg>` with integer control points and `currentColor`; `--style tilt` and `--style steps` cover the other common cuts, `--flip` mirrors for a section's top edge.
- **Decorative shapes / backgrounds:** `<circle>`, `<rect rx>`, `<polygon>`, and `<line>` primitives with `opacity` and `mix-blend-mode` on the wrapper go a long way; reach for `<path>` only when a primitive can't express it. Keep backgrounds under ~10 elements — an SVG with 300 nodes stops being "light".
- **Placeholder logos / wordmarks:** a geometric mark (two overlapping shapes, or a monogram in `<text>` with `font-family: inherit`) inside a `0 0 32 32` box beats a broken `<img>` every time.
- **Simple charts / sparklines:** `<polyline points="0,20 10,14 20,17 30,8">` with `vector-effect: non-scaling-stroke` and `fill="none"`. For anything with axes, legends, or more than one series, use a charting approach rather than hand-drawn SVG.

## Accessibility and hygiene

- Decorative: `aria-hidden="true" focusable="false"`. Meaningful (an icon that *is* the label, a chart): `role="img"` plus a `<title>` as the first child, and drop `aria-hidden`.
- An icon-only button still needs an accessible name — `aria-label` on the `<button>`, not on the SVG.
- Include `xmlns="http://www.w3.org/2000/svg"` on standalone or copy-pastable SVGs; it's optional in HTML5 but harmless and makes the snippet portable.
- Strip editor cruft: no `id`s you don't reference, no `<defs>` with nothing in them, no `data-name`, no inline `style=""` where an attribute does the job.
- If the same icon appears more than twice, sprite it (`<symbol>` + `<use>`) — one parse, many draws.

## Quick check before shipping

1. Every `<svg>` has a `viewBox`; none has hardcoded `width="…px"` attributes doing the sizing.
2. `grep '#[0-9a-fA-F]\{3,6\}'` inside the SVG markup returns nothing — colours come from `currentColor` or variables.
3. Path data has no stray long decimals.
4. Each icon set shares stroke width and caps.
5. Decorative SVGs are `aria-hidden`; meaningful ones have a `<title>`.
