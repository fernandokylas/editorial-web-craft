---
name: sub-pixel-inertia-scroll
description: >-
  Give deep-scroll editorial pages and presentation layouts a weighted, "velvety" scroll feel —
  parallax planes drifting at reduced velocity factors (0.3 background / 1.0 foreground), scroll-cued
  arrivals with a heavy-tailed rest curve (cubic-bezier(0.1, 0.9, 0.2, 1), 800ms+), lerp-smoothed
  decorative layers, gentle scroll-snap decks — all on top of native scrolling, never replacing it.
  Use this whenever the user asks for parallax, "smooth scroll", "scroll animations", "reveal on
  scroll", "cinematic scrolling", "inertia", "Lenis/Locomotive-style" scrolling, watermark/background
  type that moves, a scroll-snap presentation, or says the page "feels flat/jerky when scrolling" —
  and whenever reviewing code that hijacks wheel events or moves the whole page with transforms.
---

# Sub-Pixel Inertia Scroll

The premium scroll feel — content that glides to a stop, background layers that drift slower than the copy, sections that *arrive* rather than appear — comes from three things: layered velocity, heavy-tailed deceleration, and sub-pixel interpolation between scroll positions. None of them require taking over the scroll. The browser's own scroll is already interpolated at the compositor with the OS's inertia curve; anything that replaces it (wheel-event hijack, a `transform`-moved page canvas) loses find-in-page, space/PageDown, scroll restoration, anchor links, screen-reader navigation, and — on trackpads — fights the user's hand. So the rule: **native scroll stays the track; you add planes and arrivals on top of it.**

## Three mechanisms

**1. Parallax planes on scroll-driven animations.** Background layers move at a fraction of scroll velocity — a watermark numeral at 0.3, a mid plane at 0.6, content at 1.0. CSS scroll-driven animations do this natively, on the compositor, with no scroll listener:

```css
.parallax-meta-bg {
  position: absolute; inset: 0; z-index: 0; pointer-events: none;
  font: 900 clamp(8rem, 20vw, 18rem)/1 var(--font-display);
  color: var(--text-main); opacity: 0.06;
  animation: plane-drift linear both;
  animation-timeline: view();
  animation-range: entry 0% exit 100%;
  --drift: calc(-40vh * 0.3);
}
@keyframes plane-drift {
  from { transform: translateY(calc(var(--drift) * -1)); }
  to   { transform: translateY(var(--drift)); }
}
```

The plane moves *down* relative to the content as the page scrolls up (from `−drift` at entry to `+drift` at exit) — that's what "slower than content" means in transform terms; get the sign backwards and the watermark races ahead. Its position is a pure function of where its section is in the viewport, so it can never lag or drift out of sync. Where `animation-timeline` isn't supported, `assets/inertia-planes.js` takes over the *planes only* with a scroll listener and lerp — `current += (target − current) × 0.12` per frame — which is what gives decorative layers weight without ever delaying the content.

**2. Arrivals with a heavy-tailed rest curve.** Elements that come into view slide the last 24px into place over ~900ms on `cubic-bezier(0.1, 0.9, 0.2, 1)`: almost all the travel happens in the first 200ms, then a long glide to rest. That tail is the "weight". An `IntersectionObserver` flips a class; CSS does the motion:

```css
.arrive { opacity: 0; transform: translateY(24px);
          transition: opacity 900ms linear, transform 900ms cubic-bezier(0.1, 0.9, 0.2, 1); }
.arrive.is-in { opacity: 1; transform: none; }
```

Keep offsets small (16–32px). The eye should notice the *settle*, not the journey. Stagger siblings 40–80ms. The hidden start state is wrapped in `@media (scripting: enabled)` so a no-JS visitor sees everything, and the observer also reveals whatever is left when the page reaches its end (elements in the last few percent of a short page would otherwise never cross the margin). For full section choreography — several elements in sequence on one timeline — use `gsap-timeline-orchestrator`; this is the lightweight, library-free case.

**3. Decks snap gently, natively.** Presentation layouts use `scroll-snap-type: y proximity` (not `mandatory` — proximity lets the user rest between slides), `scroll-behavior: smooth` for anchor navigation, and `100dvh` sections. No transform canvas, no wheel interception.

`assets/kinetic-planes.css` has all three as a layered partial; `assets/inertia-planes.js` has the observer and the JS parallax fallback.

## Rendering hygiene

- **`will-change: transform` only on the planes that actually move**, and only while they're near the viewport if there are many. Every `will-change` element is a compositor layer with its own memory; a page-wide `translate3d(0,0,0)` "GPU hack" is a 2012 workaround that now costs more than it saves.
- **`overflow: clip`, not `hidden`**, on the section that hosts absolutely-positioned planes — `hidden` creates a scroll container and breaks sticky/anchor behaviour inside; `clip` just clips.
- **`isolation: isolate`** on the section so plane `z-index` can't escape.
- Planes are `pointer-events: none` and `user-select: none` — decoration never intercepts a click or a text selection.
- Scroll listeners, when needed, are `{ passive: true }` and do work only in `requestAnimationFrame`.

## If you genuinely need interpolated main-track scrolling

Some brand sites want the whole page to lerp. Don't write it; use a maintained library (Lenis is the current standard) that keeps native scroll as the source of truth and interpolates a wrapper, preserves anchors and keyboard, and exposes `prefers-reduced-motion` handling. Even then: treat it as an opt-in enhancement, keep the lerp light (0.1–0.15), and test find-in-page, tab focus into off-screen elements, and a screen reader before shipping.

## Reduced motion

Under `prefers-reduced-motion: reduce` every mechanism here degrades to *native scrolling with static content*: planes stop (`animation: none; transform: none`), arrivals are already in place, snap and smooth-scroll are off. This isn't a softer version — parallax and scroll-linked motion are among the strongest vestibular triggers (`reduced-motion-enforcer`), so it's all or nothing.

## Quick check

1. No `wheel`/`touchmove` listeners with `preventDefault`; no `transform` on the page/body/content canvas.
2. Planes use `animation-timeline: view()` (or the JS fallback), factors ≤ 0.6; content untouched at 1.0.
3. Arrivals: ≤32px offset, ~900ms, heavy-tailed curve, triggered by IntersectionObserver.
4. `will-change` only on moving planes; `overflow: clip` + `isolation: isolate` on the host.
5. Reduced-motion block turns everything off; find-in-page and keyboard paging still work.
