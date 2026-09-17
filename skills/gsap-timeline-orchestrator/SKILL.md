---
name: gsap-timeline-orchestrator
description: >-
  Choreographed page and section entrances with GSAP timelines — a single master gsap.timeline() per
  section, elements arriving in reading order with 30–70ms staggers (stagger: 0.03–0.07), power4.out /
  expo.out easing, and small offsets (y: 15–30) — instead of CSS keyframes firing all at once or
  scattered gsap.to() calls. Use this whenever the user wants elements to "animate in", "fade in on
  load", "reveal on scroll", "stagger", "cascade", "waterfall", a "cinematic" or "premium" page load,
  hero/section entrance animation, or mentions GSAP, ScrollTrigger, timeline, or intro animation — and
  whenever a page already has entrance motion that fires simultaneously or feels chaotic.
---

# GSAP Timeline Orchestrator

An interface where everything appears at once has no rhythm; one where each element fires its own independent animation has too much. The premium feel comes from *choreography*: a single timeline that brings elements on in reading order — signpost, then headline, then body — with the pieces overlapping so the eye is led rather than made to wait. GSAP's timeline is the right tool because it gives one sequence, one clock, one place to control playback, and staggers with a single parameter.

Think of it as a stage entrance, not a slideshow: the rail steps in quietly, the headline steps onto its mark while the rail is still settling, and the copy cascades in behind it.

## The rules of the sequence

**One timeline per section.** Everything in a section is a child of one `gsap.timeline({ defaults: { ease, duration } })`. Independent `gsap.from()` calls can't be paused, reversed, or re-timed together, and they collide when the user scrolls mid-animation. Sections get their own timeline so below-fold content can be triggered on scroll.

**Reading order, overlapping.** Use the position parameter to overlap phases — `"-=0.9"` (start 0.9s before the previous ends), `"<"` (start with the previous), or absolute times (`0`, `0.15`, `0.3`). Sequential `.from().from()` with no overlap is the slideshow feel you're avoiding.

**Staggers between 0.03 and 0.07.** For a collective — list items, grid cells, nav links, paragraphs — one tween with `stagger: 0.05`. Below 30ms the items read as simultaneous with jitter; above 70ms the cascade breaks into separate events and the user waits on it. `stagger: { each: 0.05, from: "start" }` when the origin matters (`"center"`, `"edges"`, `"random"` for grids).

**Ease out, hard.** `power4.out` or `expo.out` — fast arrival, long settle. Never `linear`, never `power1.inOut` for entrances; symmetrical eases are for things that go and come back.

**Small displacements.** `y: 15–30` for copy, `x: ±15` for rails, `y: 25` for headlines. Long slides across the screen are distracting and slow. Opacity is doing most of the work; the offset just gives the fade a direction.

**Duration 0.8–1.4s on a hard ease-out.** It sounds long, but with `power4.out` the element is visually 90% there by a third of the way through — the tail is what makes it feel weighted rather than snappy-cheap.

## Canonical entrance

```js
document.addEventListener("DOMContentLoaded", () => {
  const tl = gsap.timeline({ defaults: { duration: 1.2, ease: "power4.out" } });

  tl.from(".meta-rail",              { autoAlpha: 0, x: -15, duration: 1.4 }, "+=0.1")
    .from(".copy-engine h3",         { autoAlpha: 0, y: 25 },                 "-=1.1")
    .from(".copy-engine p, .copy-engine li", { autoAlpha: 0, y: 15, stagger: 0.05 }, "-=0.9");
});
```

`autoAlpha` rather than `opacity`: it also toggles `visibility`, so hidden elements aren't focusable or clickable before they arrive, and it pairs with the flash guard below.

## The three things hand-written entrances forget

1. **Flash of un-animated content.** `.from()` starts from the element's *final* state; for the frames before GSAP runs, everything is visible, then snaps to hidden, then animates. Guard it in CSS, scoped to scripting being available so no-JS users still get content — no bootstrap script needed:
   ```css
   @media (scripting: enabled) { [data-reveal] { visibility: hidden; } }
   ```
   `autoAlpha: 0 → 1` clears the `visibility` at the end of the tween. And because the guard fires whenever scripts *can* run, `entranceAll()` reveals everything if GSAP itself failed to load.

2. **Reduced motion.** Wrap in `gsap.matchMedia()`: under `(prefers-reduced-motion: reduce)`, skip the timeline and `gsap.set('[data-reveal]', { autoAlpha: 1 })`. Motion off must not mean content off.

3. **Below-the-fold sections.** Only the first section plays on load; the rest wait for `ScrollTrigger.create({ trigger, start: "top 80%", once: true, onEnter: () => tl.play() })`. Playing everything on load means users scroll down to already-finished animations.

Also: `clearProps: "transform"` in `onComplete` so leftover inline transforms don't fight CSS `:hover` lifts afterwards (the `tactile-interaction-curves` skill's press/hover rely on `transform`).

`assets/entrance.js` packages all of this as `entrance(section, opts)` / `entranceAll()` with a `data-entrance` / `data-reveal="rail|title|copy"` markup contract. Use it as-is for the standard rail → title → copy pattern; copy and adapt it when the choreography is bespoke.

## Loading GSAP

Two `<script>` tags before your own, from the CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
```
In a bundled project, `import { gsap } from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger"; gsap.registerPlugin(ScrollTrigger);`. In a single-file artifact (`encapsulated-mockup-builder`) the containment check reports these two tags as WARNs, not failures — acknowledge them with `--allow-cdn`. The page must still show all content if GSAP fails to load, which the `scripting: enabled` guard plus the `window.gsap` check in `entrance.js` gives you.

## Performance guardrails

- Animate `x`, `y`, `scale`, `rotation`, `autoAlpha` only — GSAP maps them to `transform`/`opacity`, which stay on the compositor. `width`, `height`, `top`, `margin` cause layout thrash and stutter.
- One stagger tween for a collective, not a loop of tweens. `gsap.from(items, { stagger })` is one timeline entry; `items.forEach(i => gsap.from(i, …))` is N.
- Don't animate more than ~30–40 elements per section entrance. Past that, group them (animate the container, or stagger by row).
- Kill timelines on teardown in SPAs (`tl.kill()`, `ScrollTrigger.getAll().forEach(t => t.kill())`), or the return function from `matchMedia` handles it.

## Quick check

1. One `gsap.timeline()` per section; no orphan `gsap.to/from` calls for entrances.
2. Every `stagger` is between 0.03 and 0.07.
3. Ease is `power4.out` / `expo.out`; no `linear`, no `inOut` on arrivals.
4. Offsets ≤ 30px.
5. `@media (scripting: enabled)` guard present; `prefers-reduced-motion` handled; below-fold sections on ScrollTrigger (with the IntersectionObserver fallback in `entrance.js` if it's missing).

Routing: this skill is for *choreographed* section entrances (several elements in sequence, one timeline, GSAP). For a light "fade in as it enters" on individual elements with no library, use `sub-pixel-inertia-scroll`'s `.arrive`.
