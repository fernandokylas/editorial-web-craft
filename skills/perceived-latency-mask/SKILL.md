---
name: perceived-latency-mask
description: >-
  Skeleton loading states that mirror the exact layout of incoming content — same grid, same column
  widths, heading and text bars at the real type sizes with varied widths — with a compositor-only
  shimmer, a 300ms appear delay so fast loads never flash, aria-busy handling, and a static fallback
  under reduced motion. Use this whenever UI waits on data or assets: fetch/async rendering, lazy-
  loaded sections, infinite scroll, image modules, dashboards, feeds, tables, or when the user says
  "loading state", "skeleton", "shimmer", "placeholder", "spinner", "the page flashes/jumps while
  loading", "FOUC", "layout shift", or "make it feel faster" — even if they'd otherwise reach for a
  spinner.
---

# Perceived Latency Mask

The same 800ms wait feels like two different products depending on what's on screen. A blank region or a centred spinner says "nothing is here yet, and I don't know what will be" — the user's attention has nowhere to land and every millisecond registers. A skeleton that already has the shape of the content says "here's what's coming, it's on its way": the eye starts parsing layout, the brain pre-commits to the structure, and when the content lands in exactly those slots the wait is barely remembered. Skeletons don't make the network faster; they make the wait *legible*, and legible waits feel shorter.

That only works if the skeleton is honest about the shape. A generic grey rectangle where a two-column section will appear gives the eye nothing to hold — and when the real layout arrives somewhere else, the jump costs more than the skeleton saved.

## Rules of the shape

**Same container, same grid, only the leaves swapped.** Build the skeleton with the *real* layout classes — `.editorial-container`, `.card`, `.grid` — and replace only the text, images, and controls inside with bars. If a section is a rail + 62ch copy column, its skeleton is a rail + 62ch copy column. This guarantees zero layout shift on swap and is the difference between a skeleton and a decoration.

**Bars at the real type sizes.** A heading placeholder is as tall as the heading (`height: var(--fs-h2)`); paragraph bars are one line-height tall (`1.05rem` for 1rem text) and stacked at the paragraph's line spacing. Widths vary — `100%, 95%, 100%, 62%` — because real text has a ragged last line and equal-width bars read as a barcode, not prose. Rail labels are short (60–110px); a partial last bar ends a block.

**Count what will actually show.** Three cards in a skeleton that loads twelve is a shift; twelve where the first page has six is noise. Render the number of rows/cards the first response will contain, or as many as fit the viewport.

**Reserve media with `aspect-ratio`.** Image and video placeholders hold the real box; the loaded asset drops into it without resizing.

## The shimmer

Static grey blocks read as frozen. A soft highlight drifting left-to-right every ~1.6s says "in progress" without demanding attention. Implement it as a **pseudo-element moved with `transform`**, not by animating `background-position`:

```css
.skeleton-bar { position: relative; overflow: hidden; background: var(--skeleton-base); border-radius: 4px; }
.skeleton-bar::after {
  content: ""; position: absolute; inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, var(--skeleton-sheen), transparent);
  animation: skeleton-sheen 1.6s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}
@keyframes skeleton-sheen { to { transform: translateX(100%); } }
```

`background-position` animations repaint the element every frame — on a grid of forty bars that's real CPU and visible jank on mid-range phones. `transform` on a pseudo-element is composited: the same look at near-zero cost. Colours are tokens (`--skeleton-base`, `--skeleton-sheen`) so an inverted section gets a dark base with a faint sheen instead of a white flash (`ground-inversion-guard`).

`assets/skeleton.css` has the full engine — stubs for headings, text, avatars, images, buttons, rows; the appear-delay; the crossfade; the reduced-motion fallback — already wrapped in `@layer components`. `references/recipes.md` has the skeleton anatomy for editorial sections, card grids, tables, avatar rows, KPI tiles and media, plus the JS swap.

## Timing

- **Don't show for fast responses.** A skeleton that appears and vanishes in 120ms is a flash, not a mask. The region starts at `opacity: 0` and a zero-duration animation with a 300ms delay reveals it — pure CSS, no timers. Responses under 300ms never show a skeleton at all.
- **Once shown, hold it ≥400ms** before swapping, so a 350ms response doesn't flicker.
- **Swap with a 150ms opacity crossfade**, content in place — no slide, no scale (the layout is already right; motion would say otherwise).
- **Give up gracefully.** Past ~10s, replace the skeleton with a message and a retry. A skeleton that never resolves *is* the frozen-app signal it was meant to prevent.

## Accessibility

The skeleton is decoration: `aria-hidden="true"` on it, `aria-busy="true"` on the region while loading (screen readers announce the region as busy and skip the placeholder), `aria-busy="false"` when content lands. Under `prefers-reduced-motion: reduce` the sheen stops and the bars stay static grey — still clearly placeholders, no motion. Don't add a live-region "Loading…" for every skeleton; one is fine for a page-level wait, forty is spam.

## What not to mask

Navigation, header, footer, anything server-rendered — that's content, not a wait. A single badge or number — an empty slot is quieter than a shimmer. A whole page — skeleton the *region* that's waiting and leave the rest usable. Skeletons make waits legible; they don't excuse making everything wait.

## Quick check

1. Skeleton uses the same layout classes/grid as the loaded state; swapping causes no shift.
2. Bar heights match the type scale; widths vary; count matches the first response.
3. Shimmer is a `transform`-animated pseudo-element, not `background-position`.
4. Appear delay ≈300ms, hold ≥400ms, crossfade in place, timeout with retry.
5. `aria-hidden` on skeleton, `aria-busy` on region; static under reduced motion.
