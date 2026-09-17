---
name: reduced-motion-enforcer
description: >-
  Make every animation, transition, transform, parallax, scroll effect, GSAP/JS timeline, autoplay
  video, or smooth-scroll respect `prefers-reduced-motion` — stripping displacement and scale under
  `reduce` while keeping opacity fades and state changes so nothing disappears. Use this whenever CSS
  or JS output includes transition, animation, @keyframes, transform, translate, scale, parallax,
  ScrollTrigger, gsap, framer-motion, scroll-behavior, autoplay, carousels, or hover/entrance effects
  — even if the user never mentions accessibility — and whenever the user says "reduced motion",
  "motion sickness", "vestibular", "accessible animations", "a11y", "WCAG 2.3.3", or asks to audit a
  page's motion.
---

# Reduced Motion Enforcer

Around a third of adults have experienced some vestibular disturbance; for a meaningful number, a parallax hero or a zooming page transition isn't "a bit much" — it's nausea, vertigo, or a migraine. They've told the OS about it (`Reduce motion` on macOS/iOS, `Show animations` off on Windows, `prefers-reduced-motion` in every browser), and that setting is a request the page is expected to honour. WCAG 2.3.3 makes it a criterion. Treat it as part of the component, not a post-launch fix: every rule that moves something ships with the rule that stops it.

The goal isn't a dead interface. It's the same interface with *displacement* removed and *state change* kept. Users with reduced motion on still need to see a card is hoverable, that content has arrived, that a toast appeared — they just need it to happen in place.

## Two layers of protection

**1. A global filter at the end of the stylesheet, outside any `@layer`.** It's the safety net for anything a component forgot. Unlayered rules beat every cascade layer and `!important` beats everything else, so this is the one block that must not be layered — `cascading-specificity-guard`'s lint exempts it. It kills motion properties, not feedback:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    /* Only non-spatial properties may animate */
    transition-property: opacity, color, background-color, border-color, box-shadow, fill, stroke !important;
    transition-duration: 150ms !important;
    animation: none !important;
    scroll-behavior: auto !important;
    background-attachment: scroll !important;   /* neutralises fixed-bg parallax */
  }
}
```

`transition-property` is the key: rather than zeroing every duration (which also kills helpful fades), it whitelists the properties that aren't motion. A `transform` transition simply stops transitioning — the element jumps to its hover/rest state with no travel.

One consequence of `animation: none`: any element that only *reaches* its visible state through an animation — a skeleton's appear delay, a keyframe reveal, a `from { opacity: 0 }` entrance — is left at its starting state, i.e. invisible. Every such component needs its own reduced-motion rule that sets the end state explicitly (`opacity: 1; transform: none`), as `perceived-latency-mask`'s skeleton and `sub-pixel-inertia-scroll`'s arrivals do. The safety net removes motion; it can't know what the final frame was.

**2. A component-level degrade wherever motion is authored.** The global filter is blunt; components know what their motion *means* and can offer the right substitute. Write the reduced-motion rule next to the motion rule so they stay in sync:

```css
.card-item {
  transition: opacity 400ms cubic-bezier(0.16, 1, 0.3, 1),
              transform 400ms cubic-bezier(0.16, 1, 0.3, 1);
}
.card-item:hover { transform: translateY(-4px) scale(1.02); box-shadow: var(--shadow-hover); }

@media (prefers-reduced-motion: reduce) {
  .card-item, .card-item:hover { transform: none; }   /* no travel, no scale */
  .card-item { transition: opacity 150ms ease-out, box-shadow 150ms ease-out; }
  /* shadow still changes on hover — the affordance survives */
}
```

For entrances: the fade stays, the slide goes. `opacity: 0 → 1` over 150–200ms with `transform: none` is the universal degrade — see `references/fallbacks.md` for the full motion → fallback map (parallax, zoom, carousels, autoplay video, count-ups, etc.).

Prefer the *progressive enhancement* form when authoring new components — wrap the motion in `no-preference` so the safe version is the default and nothing needs to be undone:

```css
@media (prefers-reduced-motion: no-preference) {
  .card-item { transition: transform 400ms …; }
  .card-item:hover { transform: translateY(-4px); }
}
```

## JavaScript and GSAP

Query the preference before firing, and *listen for changes* — users toggle it while the page is open:

```js
const mq = window.matchMedia("(prefers-reduced-motion: reduce)");

function init() {
  if (mq.matches) {
    gsap.set(".animate-target", { autoAlpha: 1, y: 0, scale: 1 });   // snap to final state
  } else {
    gsap.from(".animate-target", { autoAlpha: 0, y: 30, duration: 1, ease: "power4.out" });
  }
}
init();
mq.addEventListener("change", init);
```

With GSAP, `gsap.matchMedia()` does the listen-and-revert for you and is the preferred form:

```js
const mm = gsap.matchMedia();
mm.add("(prefers-reduced-motion: no-preference)", () => {
  const tl = gsap.timeline().from(".animate-target", { autoAlpha: 0, y: 30 });
  return () => tl.kill();                       // reverts if the user turns reduce on
});
mm.add("(prefers-reduced-motion: reduce)", () => gsap.set(".animate-target", { autoAlpha: 1 }));
```

Other libraries: framer-motion has `useReducedMotion()`; the Web Animations API can check `mq.matches` before `element.animate()`. Autoplay video: `if (mq.matches) video.pause()` and show the poster. Smooth scrolling in JS: `behavior: mq.matches ? "auto" : "smooth"`.

## What must go, what must stay

| Strip under `reduce` | Keep under `reduce` |
|---|---|
| Translate / slide, scale / zoom, rotate, 3D | Opacity fades ≤200ms |
| Parallax and scroll-linked movement | Colour, background, border changes |
| Smooth scroll, scroll-jacking | Shadow changes (hover affordance) |
| Infinite spinners, shimmer sweeps, marquees | Focus rings |
| Autoplay video / animated backgrounds | Final states of every entrance |
| Staggers (fade together instead) | Content — nothing may be hidden because motion is off |

Zero displacement means zero — a "smaller" slide is still a slide.

## Verifying

Run the audit on every file that contains motion:

```bash
python scripts/check_motion.py index.html styles.css app.js
```

It lists each motion source (transform transitions, keyframes, GSAP, parallax, smooth scroll, autoplay) and fails when CSS motion lacks a `prefers-reduced-motion` block or JS motion lacks a `matchMedia` / `gsap.matchMedia` check. Then test by hand: turn on *Reduce motion* in the OS (macOS: Accessibility → Display; Windows: Settings → Accessibility → Visual effects; DevTools: Rendering → Emulate CSS media feature) and confirm every element still arrives, every hover still signals, and nothing travels.
