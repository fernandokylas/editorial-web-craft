# Motion → reduced-motion fallback map

What to keep, what to strip. The principle: remove *displacement* (things travelling across the eye), keep *state change* (the user still needs to know something happened).

| Motion | Vestibular risk | Reduced-motion version |
|---|---|---|
| Entrance slide/scale (`y: 30`, `scale(0.95)` → rest) | Low–medium | Opacity-only fade, ≤200ms, zero displacement |
| Hover lift (`translateY(-4px) scale(1.02)`) | Low | No transform; keep the shadow/colour/border change |
| Press compression (`scale(0.97)`) | Low | No transform; keep background/shadow change or none |
| Staggered cascade | Low–medium | Fade all at once (drop the stagger), or set visible instantly |
| Parallax (`background-attachment: fixed`, scroll-speed layers) | **High** | `background-attachment: scroll`; all layers move together (i.e. not at all relative to content) |
| Scroll-driven / scrubbed animation | **High** | Show final state; no scrub |
| Smooth scroll (`scroll-behavior: smooth`, `scrollIntoView({behavior:'smooth'})`) | Medium–high | `auto` / instant jump |
| Zoom / scale transitions (page, image, modal grow-from-point) | **High** | Cross-fade in place |
| 3D flips, rotations, perspective | **High** | Cross-fade between faces |
| Infinite spinners / pulsing | Medium | Static indicator, or a slow ≤1/s opacity pulse; never rotation |
| Marquee / auto-scrolling carousel | **High** | Stop; show static slide with manual controls |
| Autoplay background video | **High** | `video.pause()` and show poster, or `autoplay` removed when the query matches |
| Sticky/fixed elements shifting on scroll (shrinking headers) | Medium | Fix them at one size |
| Skeleton shimmer | Low–medium | Static skeleton, no sweep |
| Toast/notification slide-in | Low | Fade in place |
| Modal / drawer slide | Medium | Fade; drawer appears in final position |
| Page transitions (view transitions, route slides) | Medium–high | Cross-fade, or none |
| Cursor followers, magnetic buttons | Medium | Off |
| Number count-ups | Low | Show final value |

## Duration guidance under reduce

- Opacity fades: 100–200ms are fine and help orientation. 0.01ms "instant" is acceptable but loses the hint.
- Anything with displacement: 0. Not "smaller", zero.
- Colour / shadow / border changes: unchanged — they aren't motion.

## Not vestibular triggers (don't strip these)

Colour changes, opacity changes, shadow changes, border changes, focus rings, underline reveals, small icon swaps. Removing these under `reduce` makes the UI *less* accessible, not more.
