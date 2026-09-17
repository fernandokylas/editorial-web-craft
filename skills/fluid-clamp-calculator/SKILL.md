---
name: fluid-clamp-calculator
description: >-
  Replace static px sizes and breakpoint media queries with fluid CSS clamp()/calc() tokens for
  typography, padding, margins, and gaps that scale smoothly between a 320px mobile floor and a
  1200–1440px desktop ceiling. Use this whenever writing or refactoring CSS, Tailwind, styled-
  components, or design tokens for headings, section spacing, container padding, or grid/flex gaps —
  including when the user just says "make it responsive", "fluid type", "scale with the viewport",
  "stop it looking cramped on mobile / huge on wide screens", or asks for a type scale, spacing scale,
  or design tokens. Also use when reviewing CSS that hardcodes font-size or spacing in px across
  several breakpoints.
---

# Fluid Clamp Calculator

Static pixel sizes are guesses that are right at exactly one viewport width. Stacking media queries to patch them produces jumps at each breakpoint and leaves every width in between untuned. A fluid token instead describes the *range* a value should live in and lets the browser interpolate: `clamp(MIN, PREFERRED, MAX)`, where `PREFERRED` is a viewport-relative expression. The result scales continuously, never drops below the mobile floor, and never balloons on ultra-wide screens.

Treat every heading size, section margin, page padding, and component gap as a fluid token. Reserve media queries for things that genuinely change *structure* (column count, showing/hiding), not for resizing.

## Boundaries

- Mobile floor: **320px** (20rem)
- Desktop ceiling: **1200–1440px** (75–90rem). Pick 1200 for content-dense product UI, 1440 for marketing/editorial pages.

Between those two widths the value moves linearly; outside them it's pinned to MIN or MAX.

## Baseline tokens

Start from these unless the design calls for a different scale. They're tuned so the min reads comfortably on a phone and the max doesn't dominate a 27" monitor.

```css
:root {
  /* Typography */
  --fs-display: clamp(2.5rem, 6vw, 5.5rem);    /* H1 / hero */
  --fs-h2:      clamp(1.75rem, 4vw, 3rem);     /* section headings */
  --fs-h3:      clamp(1.25rem, 2.5vw, 1.75rem);/* sub-headings */

  /* Space */
  --pad-page:    clamp(2rem, 5vw, 5rem);       /* vertical page padding; pair with 1.5rem horizontal */
  --gap-section: clamp(3rem, 8vw, 6rem);       /* margin between major sections */
  --gap-grid:    clamp(1.5rem, 4vw, 3.5rem);   /* grid / flex gaps */
}

body { padding: var(--pad-page) 1.5rem; }
h1   { font-size: var(--fs-display); }
h2   { font-size: var(--fs-h2); }
section + section { margin-top: var(--gap-section); }
.grid { gap: var(--gap-grid); }
```

Define them once as custom properties and reference the variables — a page with fifteen scattered `clamp()` literals is as hard to tune as one with fifteen px values.

## Calculating a bespoke token

When a value isn't in the baseline (a 12rem hero on desktop that must be 3rem on mobile, say), don't eyeball the `vw` term — derive it. Run the bundled script:

```bash
python scripts/clamp.py --min 3rem --max 12rem            # 320→1440 by default
python scripts/clamp.py --min 1rem --max 2.25rem --max-vw 1200
python scripts/clamp.py --min 16px --max 40px             # px inputs are converted to rem
```

It prints a `clamp(MIN, calc(A rem + B vw), MAX)` expression whose preferred value hits exactly MIN at the floor and exactly MAX at the ceiling. The math it uses, if you need to do it by hand:

```
slope     = (max − min) / (maxVw − minVw)         # in rem per rem of viewport
intercept = min − slope × minVw
preferred = calc(intercept rem + (slope × 100) vw)
```

A pure `Nvw` middle term (as in the baseline tokens) is fine when the range is forgiving; use the `calc()` form when the endpoints matter, or when a plain `vw` would make the value go *up* on mobile relative to its min (negative-intercept cases).

## Rules that keep it accessible and honest

- **MIN and MAX in rem or em, never px.** The clamp caps are what survive browser zoom and user font-size preferences; px caps silently defeat them. (`vw` in the middle is fine — that's the fluid part.)
- **Add a rem component to the preferred value when the range is wide** (`calc(… rem + … vw)`), so text still grows under browser zoom instead of being purely viewport-driven. WCAG 1.4.4 fails on pure-`vw` type that can't reach 200%.
- **Body text stays near 1rem–1.125rem.** Fluid scaling is for display sizes and space; paragraph text that grows with the viewport hurts line length. Fix body copy and let the *measure* (`max-width: 62ch`) do the work.
- **Line-height tightens as size grows.** Pair display sizes with `line-height: 1.05–1.15`, headings `1.2–1.3`, body `1.5–1.65`. A clamp'd H1 with body line-height looks broken at the top of its range.
- **Don't leave orphan px.** If a "responsive" component still has `padding: 24px` and `@media (min-width: 768px) { padding: 48px }`, convert it — that's exactly the two-point guess a clamp replaces.

## Tailwind / utility frameworks

Use arbitrary values with the same expressions: `text-[clamp(2.5rem,6vw,5.5rem)]`, `py-[clamp(2rem,5vw,5rem)]`, `gap-[clamp(1.5rem,4vw,3.5rem)]`. For a project, put the tokens in `theme.extend.fontSize` / `theme.extend.spacing` so they become `text-display`, `py-page`, `gap-grid` rather than repeated literals.

## Quick self-check before shipping

1. Search the output for `font-size:` / `padding:` / `margin:` / `gap:` followed by `px` — each one either has a reason or should be a token.
2. Search for `@media` — each one should change layout, not just resize something.
3. Every `clamp()` has rem/em caps, and the preferred term is either `Nvw` for a forgiving range or `calc(… + …vw)` for a precise one.
