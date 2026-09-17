---
name: magnetic-hitbox-warp
description: >-
  Magnetic hover for high-value controls — an invisible field 20–45px around a nav item, primary CTA,
  or close button that begins reacting before the cursor reaches the edge, pulls the control's visual
  up to ~6px toward the pointer along the cursor vector, scales it slightly, and springs it back with
  a dampened recoil on exit. Use this whenever the user asks for "magnetic buttons", "cursor
  attraction", "the button follows the mouse", "premium nav hover", "gravity / pull effect", an
  Awwwards-style header, or wants primary actions and menu items to feel more alive than a colour snap
  — and when reviewing hover states on a small set of hero controls.
---

# Magnetic Hitbox Warp

A hover state that flips colour the instant the cursor crosses a pixel boundary feels like a switch. A control that *notices you coming* — starts to respond a couple of centimetres out, leans toward the cursor by a few pixels, and settles back with a small spring when you leave — feels like it has mass and wants to be pressed. The effect is tiny (never more than ~6px of travel, a 3% scale) and that's the point: it's felt more than seen. Used on a handful of primary controls it reads as craft; used on every link it reads as a gimmick and makes the page feel unstable.

## Anatomy

Two elements with strictly separated jobs:

- **The field** (`.magnetic`, a `span`) — an inline-flex host whose `::before` extends `--magnet-reach` (2rem) beyond the box on every side. It's what the pointer enters and what tracks position. It never moves.
- **The target** (`.magnetic-target`, the real `<button>` or `<a>`) — the visible control. It's the only thing that translates and scales, driven by `--mx`/`--my` custom properties the script sets.

```html
<span class="magnetic" data-magnetic="6">
  <button class="btn magnetic-target" type="button">Book a call</button>
</span>
```

`.magnetic-target` adds *only* the motion — transform, transition, the tracking state — and never sets colour, padding or radius, so it layers onto whatever button style the page already has (`.btn` from the boilerplate, `tactile-interaction-curves`' recipe). `.magnetic-pill` is an optional look for when there isn't one.

Why the field is a pseudo-element rather than padding + negative margin: negative margins overlap the neighbouring controls' hit areas — in a nav, the field of one item steals hovers from the next. `inset: -2rem` on a `::before` grows the *hover* zone without touching layout or neighbours. And why the field and the target are separate: the enlarged, static field is what the cursor interacts with, so the button can never run away from the pointer — the classic failure of moving the hit area itself.

## The motion

While inside the field, the script maps the cursor's offset from the host centre (normalised over half-size + reach) to a displacement clamped at `--magnet-pull` (6px), and the target follows with a tight `150ms` ease-out so it tracks without lag. On leave, `--mx/--my` reset to 0 and the target returns over `400ms` on a **dampened spring** — a `linear()` easing with one small overshoot and settle — which is the recoil that says "it snapped back onto something." Scale sits at `1.03` while tracking, `0.97` on `:active`, and the background shifts to the accent so the change is legible even at a glance.

```css
.magnetic-target {
  transition: transform 450ms var(--ease-recoil), background-color 150ms linear;
  transform: translate3d(var(--mx, 0px), var(--my, 0px), 0) scale(var(--ms, 1));
}
@media (hover: hover) and (pointer: fine) {
  .magnetic.is-tracking .magnetic-target {
    --ms: 1.03;
    background: var(--accent-solid); color: var(--accent-on-solid);
    transition: transform 150ms var(--ease-track), background-color 150ms linear;
  }
}
```

`assets/magnetic.css` (layered partial) and `assets/magnetic.js` (`initMagnetic()`) carry the full implementation — rAF-throttled `pointermove`, per-host `data-magnetic` pull, focus/blur mirroring the visual state for keyboard users, and reduced-motion handling.

## Where it belongs — and doesn't

Reserve it for controls that carry intent: the primary CTA, top-level nav items, a modal's close button, a "next" arrow in a gallery. Three to six per view is the ceiling. Not on: inline body links (they're in reading flow — motion there is a distraction), form inputs, list rows, table actions, anything repeated in a grid, anything smaller than ~32px (the pull becomes the whole element).

Never on touch. `(hover: hover) and (pointer: fine)` gates both the CSS and the script; a phone gets a normal button with a normal `:active`. And `prefers-reduced-motion: reduce` removes the pull and the spring entirely — colour and shadow still change so the hover is still signalled.

## Details

- The target keeps `position: relative` and the field `isolation: isolate` so `z-index: -1` on the `::before` stays inside the component.
- The button is the focusable element, with a `:focus-visible` ring that does *not* move — the ring belongs to the anchor position, not the displaced visual.
- Don't add `will-change: transform` permanently; three to six controls don't need a standing compositor layer. If a nav has jank, add it on `pointerenter` and remove on leave.
- Bottom padding slightly heavier than top (`visual-weight-tuner`) — the pull makes optical imbalance more noticeable, not less.
- Combine with `tactile-interaction-curves` for the base press physics; this skill adds the approach field on top.

## Quick check

1. Field is a `::before` with negative `inset`; no negative margins.
2. Only the target transforms; the field and the focus ring stay anchored.
3. Pull ≤ 6px, scale ≤ 1.03, tracking ≤ 150ms, recoil ~400ms on a spring curve (the visible state lands early; the tail is the settle).
4. Gated by `(hover: hover) and (pointer: fine)`; reduced-motion strips transform, keeps colour.
5. At most a handful per view; none on inline text links or repeated grid items.
