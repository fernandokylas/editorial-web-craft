---
name: visual-weight-tuner
description: >-
  Optical balance corrections for UI — align icons to text cap-height instead of flexbox's
  ascender/descender box, give buttons and pills slightly heavier bottom padding so text doesn't look
  sunk, and scale circles/triangles up 10–15% so they read as the same size as squares. Use this
  whenever building or polishing buttons, pills, badges, chips, tags, icon+label rows, nav items,
  avatars, status dots, play/arrow icons, wordmarks, logos, or any component where an icon sits beside
  text or a shape sits beside another shape — including when the user says something "looks slightly
  off", "not quite centered", "icon looks low/high", "button text feels heavy", "make it feel more
  polished / premium / refined", or asks for a design-system component. Also use when reviewing CSS
  that relies on align-items: center or symmetric padding for icon-text pairs.
---

# Visual Weight Tuner

Mathematical centering and optical centering are different things. Flexbox, `text-align`, and symmetric padding center a *bounding box*; the eye centers *visual mass*. Because letterforms sit low in their box, circles have less area than squares, and triangles have their mass on one side, geometrically perfect layouts routinely look a pixel or two wrong — and users feel that as "cheap" without being able to say why.

Work the way a typographer does: lay it out mathematically first, then correct by eye. The corrections are tiny (usually 0.5–2px or 5–15%), but they're the difference between a component that reads as templated and one that reads as crafted.

## The three corrections that matter most

### 1. Icons next to text: align to cap-height, not the line box

`align-items: center` centers the icon against the full line box (ascender to descender). Capitals and most lowercase mass sit above the baseline, so the icon ends up visually *low* next to uppercase labels, button titles, and nav items — it looks like it's sagging.

Fix: keep flex centering as the baseline, then nudge the icon up to meet the cap-height. Prefer `position: relative; top: -1px` or `transform: translateY(-0.5px)`; the exact value depends on font and size, so check it at the rendered size rather than copying blindly.

```css
.action { display: inline-flex; align-items: center; gap: 0.5rem; }
.action-icon {
  position: relative;
  top: -1px;               /* snaps icon mass to the cap-height */
  flex: none;
}
```

Sizing rule of thumb: an inline icon should be roughly the cap-height to x-height-plus-a-bit of the text — usually `1em` to `1.15em` of the font size — not the full line-height.

### 2. Buttons and pills: bottom padding slightly heavier

Text's visual weight sits at the baseline, so with symmetric vertical padding the label looks pushed toward the bottom of the button. Give the bottom a hair more room — about +1px or +0.05rem — or set an explicit `line-height` (e.g. `1`) so the text box has no descender slack to sink into.

```css
.optical-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  line-height: 1.2;
  padding: 0.5rem 1.25rem 0.55rem;   /* top 0.5, bottom 0.55 */
}
.optical-pill-icon {
  align-self: center;
  position: relative;
  top: -1px;
  margin-right: 0.5rem;
}
```

Also watch **horizontal** balance: a pill with an icon on the left needs slightly less left padding than right (or the icon carries its own leading space), otherwise the icon side looks heavier. Icon-only square/circle buttons want the glyph centered on its *visual* mass — a play triangle, chevron, or arrow needs shifting toward its point (typically 1–2px, or ~5% of the button size).

### 3. Shapes next to shapes: circles and triangles need to be bigger

A circle inscribed in a square has ~78% of its area; a triangle ~50%. Side by side at the same nominal size, the circle looks small and the triangle smaller. Scale round and pointed elements up by 10–15% in mass when they sit next to square or rectangular ones — status dots beside square swatches, circular avatars beside rounded-rect cards, a round icon in a square button.

```css
.swatch { width: 12px; height: 12px; }
.status-dot { width: 13.5px; height: 13.5px; border-radius: 50%; }  /* ~+12% to match */
```

The same logic is why well-drawn round letters (O, C, G) overshoot the baseline and cap line by 1–2% — if you're drawing a wordmark or icon set, apply overshoot; if you're placing one, don't "fix" the overshoot by aligning to its outer edge.

## How to apply it

1. Build the component with ordinary flex/grid centering first — get the structure right.
2. Render it at real size (or reason about it at real size) and ask: does the icon look low? Does the label look sunk? Does the round thing look small? Does the arrow look shifted away from its point?
3. Apply the smallest correction that fixes it — half-pixels are fine (`translateY(-0.5px)`) and render well on high-DPI screens.
4. Comment the correction so the next person doesn't "clean it up" back to symmetric. A one-liner like `/* optical: cap-height alignment */` is enough.

Don't over-correct: corrections should be invisible when right and only visible when removed. If a nudge is more than ~2px or ~15%, the underlying size or font metric is probably wrong — fix that instead.

For the fuller kit — uppercase tracking, hanging punctuation, weight matching between icon strokes and text, overshoot values, vertical rhythm around mixed-size text — see `references/optical-corrections.md`.
