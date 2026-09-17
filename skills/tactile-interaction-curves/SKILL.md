---
name: tactile-interaction-curves
description: >-
  Physics-feeling micro-interactions for buttons, cards, list rows, toggles, menus, and modals — ease-
  out hover-in under 300ms, faster hover-out, a fast :active press with scale(0.97–0.98), and no
  `transition: all … linear`. Use this whenever writing or reviewing CSS/Tailwind/styled-components
  that includes :hover, :active, :focus, transition, transform, animation, or any interactive state,
  and whenever the user says "make it feel premium / tactile / responsive / snappy / alive", "hover
  effect", "click animation", "button feedback", "it feels flat / laggy / janky", or asks for a
  polished interactive component — even if they don't mention motion.
---

# Tactile Interaction Curves

A button that snaps instantly between two colours, or slides linearly from one state to another, tells the user "this is a picture of a button". One that accelerates quickly out of rest and settles softly, then visibly compresses under the cursor, tells them "this has mass". The difference is a few lines of CSS, and it's the single cheapest way to make an interface feel expensive.

The model is physical: things at rest need a push to move (fast start), things in motion lose energy (slow landing), and pressing something compresses it (scale down, fast). Every interactive state change should be legible as one of those three.

## The three rules

**1. Ease out, never linear, never `all`.** Motion uses a curve with a fast start and a long deceleration — `cubic-bezier(0.16, 1, 0.3, 1)` is the workhorse, `cubic-bezier(0.25, 1, 0.5, 1)` for smaller elements. Keep it under 300ms — that's the budget for the *visible* change to land; a spring recoil or settle tail (as in `magnetic-hitbox-warp`) may run on to ~400–450ms because the state has already arrived and only the last few pixels are still moving. `linear` is banned for *motion*; it's fine — actually preferable — for pure colour crossfades (`background-color 150ms linear`), which is what your eye expects from a tint change. `transition: all` is banned because it silently animates layout properties (`width`, `padding`, `height`) that jank, and makes the exit timing impossible to control.

**2. Enter slower than you leave.** Hover-in at 200–300ms feels considered; hover-out at 150–200ms feels responsive. Set the *exit* timing on the base rule and the *enter* timing on the `:hover` rule — that's the only way to get asymmetric durations in plain CSS:

```css
.tactile-action {
  transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 180ms cubic-bezier(0.16, 1, 0.3, 1),
              background-color 150ms linear;          /* exit timings */
}
@media (hover: hover) {
  .tactile-action:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgb(0 0 0 / 0.08);
    transition-duration: 260ms;                       /* enter timing */
  }
}
```

The `@media (hover: hover)` wrapper matters: on touch devices `:hover` sticks after a tap, leaving buttons floating in their lifted state. Only pointer devices get the hover layer.

**3. Press is fast and physical.** `:active` compresses the element — `scale(0.97)` for buttons, `scale(0.98–0.985)` for larger cards (bigger surfaces need less shrink to feel the same) — over 60–100ms so it tracks the click instantly. Pair it with a shadow that drops back to rest: the element is being pushed *into* the page, not lifted off it.

```css
.tactile-action:active {
  transform: translateY(0.5px) scale(0.97);
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.04);
  transition-duration: 80ms;
}
```

Release uses the base rule's timing automatically, so the button springs back over ~180ms — that asymmetry (fast in, softer out) is what reads as mechanical travel.

## Applying it across a page

- **Tokenise the physics.** Two curves, three durations, two shadows in `:root` (`--ease-out`, `--dur-in`, `--dur-out`, `--dur-press`, `--shadow-rest`, `--shadow-hover`). Every component references them, so the whole page shares one material. Mixed beziers across components is the interactive equivalent of mixed fonts.
- **Match the response to the element.** Buttons lift and compress. Cards lift more, compress less. List rows and menu items *don't* lift — a tint change at 120–150ms and at most `scale(0.995)`; rows that float in a list feel jittery. Toggles use a symmetric in-out curve because they travel both ways. `references/curves.md` has recipes for each, plus dropdown, modal, sheet, and staggered reveal.
- **Only animate compositor properties.** `transform`, `opacity`, `box-shadow`, `filter`, colours. Never `width`, `height`, `margin`, `padding`, `top/left` — they trigger layout on every frame. Move with `transform: translate()`, grow with `transform: scale()`, reveal with `opacity` + `transform`.
- **Focus is a state too.** `:focus-visible` gets a visible ring (`outline: 2px solid var(--accent-text); outline-offset: 2px`) — instantly, no transition. Keyboard users shouldn't wait for feedback.
- **Respect reduced motion.** A `prefers-reduced-motion: reduce` block that collapses durations to ~0 but *keeps* the state changes (colour, shadow). Motion off ≠ feedback off.

## Quick check

1. Search the CSS for `linear` on anything other than colour/opacity, and for `transition: all` — replace both.
2. Every `:hover` that moves something is inside `@media (hover: hover)`.
3. Every primary button and clickable card has an `:active` with `scale()` and a short duration.
4. Hover-out duration ≤ hover-in duration.
5. Nothing animates `width`, `height`, `padding`, `margin`, or positional offsets.
6. `:focus-visible` exists and is not transitioned; `prefers-reduced-motion` block exists.
