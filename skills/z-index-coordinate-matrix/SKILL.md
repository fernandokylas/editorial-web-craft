---
name: z-index-coordinate-matrix
description: >-
  Replace arbitrary z-index numbers (999, 9999, 99999) with a declared depth matrix — --z-subground
  (-10), --z-ground (0), --z-rail-sticky (100), --z-navigation (200), --z-disclosure (300), --z-modal
  (400), --z-critical (500) — plus deliberate stacking contexts (isolation: isolate) at component
  roots and the browser top layer for dialogs/popovers. Use this whenever writing CSS with position:
  fixed/sticky/absolute, sticky headers or rails, dropdowns, popovers, tooltips, modals, toasts,
  overlays, parallax/background layers, or when the user says "z-index", "it's rendering
  behind/under", "the dropdown is hidden by the next card", "stacking", "overlay order", "the modal is
  under the header", or any layering bug.
---

# Z-Index Coordinate Matrix

`z-index: 99999` is not a value, it's a confession — someone couldn't find why an element rendered underneath something and kept adding zeros until it didn't. The next person adds one more zero. Depth in an interface is a floor plan with a small, fixed number of storeys: things behind the content, the content, things that stick while scrolling, the header, things that pop out of components, things that take over the page, and things that must be visible above even those. Name the storeys once, give each a number with room between them, and every element declares which storey it lives on. A layering bug then becomes "this element is on the wrong floor" or "this element is trapped inside a room" — both diagnosable — instead of an arms race.

## The matrix

```css
:root {
  --z-subground:   -10;   /* parallax planes, watermark type, grid canvas lines — behind content */
  --z-ground:        0;   /* text, tables, columns, cards — the baseline */
  --z-rail-sticky: 100;   /* sticky meta rail, sidebar, table headers — overlap content while scrolling */
  --z-navigation:  200;   /* fixed/sticky primary header — over sticky rails */
  --z-disclosure:  300;   /* dropdowns, popovers, hand-built tooltips — pop out of components */
  --z-modal:       400;   /* dialogs, drawers, full-page overlays and their backdrops */
  --z-critical:    500;   /* system alerts, toasts, tooltips over modals — nothing above this */
}
```

Seven tiers, gaps of 100, nothing else. Declare all seven even if a page uses two — the matrix is the vocabulary, not a usage list, and a native `<dialog>` page will legitimately never touch `--z-modal`. Every `z-index` in the codebase is `var(--z-…)`; a raw number outside this block is a lint failure. Local ordering *inside* an isolated component may use `0`/`1`/`-1` (e.g. a card's image under its caption) because those numbers are relative to the component, not the page.

```css
.editorial-container      { position: relative; isolation: isolate; }        /* a room: children stack among themselves */
.parallax-meta-bg         { position: absolute; z-index: var(--z-subground); }
.meta-rail.is-sticky      { position: sticky; top: 2rem; z-index: var(--z-rail-sticky); }
.global-navigation-header { position: fixed; top: 0; width: 100%; z-index: var(--z-navigation); }
.dropdown-panel           { position: absolute; z-index: var(--z-disclosure); }
.modal-backdrop, .modal   { position: fixed; z-index: var(--z-modal); }
.toast                    { position: fixed; z-index: var(--z-critical); }
```

## Rooms: stacking contexts on purpose

`z-index` only orders siblings within one stacking context. Give every major component a context of its own with `isolation: isolate` (cleaner than `position: relative; z-index: 1` — no number, no side effects). Inside it, children can use small local values and never leak into the page's floors; a card's hover shadow, image, and badge sort among themselves without touching the header.

The flip side is the cause of almost every real z-index bug: **contexts you didn't ask for.** `transform`, `opacity < 1`, `filter`, `backdrop-filter`, `will-change`, `mix-blend-mode`, `clip-path`, `contain`, `container-type`, and `position: sticky` all create a stacking context. A tooltip inside a card that lifts on hover is inside that card's context and *cannot* rise above the neighbouring card — no number will fix it. `references/stacking-contexts.md` lists every trigger and the escape routes.

## The top layer changes the rules

Native `<dialog>` (`showModal()`) and `[popover]` elements render in the browser's **top layer** — above all stacking contexts, ordered by open time, with no z-index at all. That's where modals, dropdowns, menus, tooltips, and toasts should live (`html5-native-fallback`): they can't be trapped by a card's transform, they don't need `--z-modal`, and a tooltip opened over a modal lands above it because it opened later. The `--z-disclosure` / `--z-modal` / `--z-critical` tiers exist for the cases that can't use the top layer — a hand-positioned overlay, a third-party widget, a legacy component — and for their backdrops.

When an overlay must be hand-built and *is* trapped, portal it: render it as a child of `<body>` and position from the trigger's bounding rect (or use CSS anchor positioning). Moving it up the tree is the fix; raising its number is not.

## Rules

- No raw numbers outside the `:root` matrix; no `!important` on z-index — if you need it, you're fighting a context.
- Negative tiers only inside an isolated parent, or they sink behind `body`.
- `position: sticky` elements get a tier (`--z-rail-sticky` / `--z-navigation`) explicitly — sticky creates a context, and two sticky elements without tiers order by source, which flips when the DOM changes.
- Backdrops share the tier of what they back (`--z-modal`), placed before the panel in source order.
- Don't add tiers for one component. If something genuinely needs a floor between two existing ones, the matrix has 99 numbers of room — but first ask whether it should be in the top layer instead.

## Verify

```bash
python scripts/check_zindex.py styles.css page.html
```

Fails on raw or magic numbers outside the matrix, undeclared `--z-` tokens, values above `--max` (500), and z-index on rules with no positioning context. Warns on `!important`, unused tokens, and rules that create a stacking context on component-ish selectors (card, panel, item, row, tile) — the overlays-inside-transformed-cards trap. Then, for any remaining "it's behind X" bug, open DevTools → Layers and find which room the element is in before changing any number.
