---
name: cls-dimension-anchor
description: >-
  Prevent layout shift (CLS) by reserving space before anything arrives — width/height attributes and
  aspect-ratio on images, video, iframes and embeds; min-height on async data regions, feeds, charts,
  ad slots and dashboards; font metric overrides so web-font swaps don't reflow; scrollbar-gutter;
  content-visibility with intrinsic size. Use this whenever generating or reviewing HTML/CSS that
  includes <img>, <picture>, <video>, <iframe>, embeds, lazy-loaded sections, fetched data, charts,
  third-party widgets, web fonts, or cookie/promo banners — and whenever the user says "layout shift",
  "CLS", "the page jumps", "content moves when it loads", "Core Web Vitals", "Lighthouse", or "things
  pop in and push stuff down".
---

# CLS Dimension Anchor

A page that jumps while it loads is a page the user can't trust: the link they were about to tap moves, the paragraph they were reading slides off, the footer lurches down as a chart appears. Every one of those movements has the same cause — something arrived and took space it hadn't been given. The browser lays out what it knows; an image with no dimensions is a 0×0 box until the bytes land, a data region with `height: auto` is nothing until the fetch resolves, a headline in a fallback font is a different width until the web font swaps. Layout shift isn't a performance problem to tune later; it's the absence of a reservation, and reservations are made in markup and CSS before any request goes out.

Treat every non-text module as a box that must have a size *before* its content exists.

## Reserve media with intrinsic dimensions

`<img>` gets `width` and `height` attributes — the browser derives the aspect ratio from them and reserves the box on first layout, before the request starts. Then CSS makes it responsive without breaking the ratio:

```html
<div class="media-aspect-enforcer">
  <img src="remote-asset.jpg" alt="Editorial context description"
       width="800" height="450" class="shielded-image" loading="lazy">
</div>
```
```css
.media-aspect-enforcer { width: 100%; aspect-ratio: 16 / 9; background: var(--rule); overflow: hidden; }
.shielded-image { width: 100%; height: 100%; object-fit: cover; display: block; }
```

Belt and braces on purpose: the attributes reserve the box even before CSS applies; the wrapper's `aspect-ratio` holds the shape when the image is missing, broken, or replaced by a different-ratio source. The soft background is the placeholder colour so an empty box doesn't read as a hole. The one CSS mistake to avoid: `img { width: 100% }` alone *discards* the attribute ratio — pair it with `height: auto` (or the wrapper's `height: 100%`).

`<video>`, `<iframe>`, and embeds (YouTube, maps, tweets, forms) have no intrinsic size until content loads and often resize themselves. Always wrap them in an `aspect-ratio` box with `overflow: hidden` and give the element `width: 100%; height: 100%`.

## Reserve dynamic regions with minimum mass

A feed, table, chart, or dashboard tile that's empty until data arrives must not be `height: auto`. Give it a `min-height` sized to the *typical filled height*, so the footer and neighbours are already where they'll end up:

```css
.dynamic-feed-container { min-height: clamp(120px, 15vh, 200px); padding: 1.5rem; }
.dashboard-chart        { min-height: clamp(300px, 40vh, 600px); }
```

The exact value comes from the design, not a guess — measure the loaded state and reserve that. A skeleton (`perceived-latency-mask`) inside the reserved box does double duty: it holds the height *and* tells the user what's coming. Ad slots and third-party widgets get a fixed `height` or `min-height` at their largest expected size, reserved even when unfilled.

## The shifts people forget

- **Web fonts.** The largest single shift on an editorial page is usually the headline reflowing when Playfair replaces Georgia. `font-display: swap` alone doesn't fix it — add a fallback `@font-face` with `size-adjust`, `ascent-override`, `descent-override` so the fallback's metrics match. `references/cls-sources.md` has the pattern.
- **Banners injected at the top** (cookie, promo, app-install) push everything down. Reserve the slot in the layout, or make them `position: fixed` overlays that take no flow space.
- **Scrollbars.** When content grows past the viewport, the vertical scrollbar appears and every centred element shifts left. `html { scrollbar-gutter: stable; }`.
- **`content-visibility: auto`** without `contain-intrinsic-size` makes off-screen sections zero-height until scrolled to — the scrollbar jumps as they render. Always pair them.
- **Animating layout properties.** A transition on `height`, `margin`, or `top` is a shift on every frame. `transform` and `opacity` only.
- **Lazy-loading above the fold.** `loading="lazy"` on the hero image delays it past first paint; use `fetchpriority="high"` there and lazy-load only below the fold. Dimensions are still required either way.

## Verify

```bash
python scripts/check_cls.py page.html styles.css
```

Fails on media with no reserved dimensions (attributes, own `aspect-ratio`, or an `aspect-ratio` wrapper), `@font-face` without `font-display`, `content-visibility: auto` without intrinsic size, and transitions on layout properties. Warns on `width`-only image CSS, dynamic-looking containers with no height reservation, lazy images above the fold, missing `scrollbar-gutter`, and fallback fonts without metric overrides. Then confirm in Chrome DevTools → Performance → Layout Shifts, or Lighthouse's CLS audit — target ≤ 0.1.
