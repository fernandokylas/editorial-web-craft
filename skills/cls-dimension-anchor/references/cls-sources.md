# Where layout shift comes from, and the fix for each

CLS scores every unexpected movement of visible content. Anything that arrives late — bytes over the network, script output, a font — and takes space it wasn't given is a shift. The fix is always the same shape: **reserve the space before the thing arrives.**

| Source | What happens | Fix |
|---|---|---|
| `<img>` without dimensions | Renders at 0 height, then pops to full size | `width` + `height` attributes (browser derives the ratio) **and** `width: 100%; height: auto` in CSS; or a wrapper with `aspect-ratio` |
| Responsive `<picture>` / `srcset` | Same as above per source | `width`/`height` on the `<img>` (ratio applies to every candidate); if sources have different ratios, `aspect-ratio` per media query on the wrapper |
| `<video>`, `<iframe>`, embeds (YouTube, maps, tweets) | No intrinsic size until content loads; embeds often resize themselves | Wrapper with `aspect-ratio: 16 / 9` (or the known ratio) and `overflow: hidden`; iframe `width: 100%; height: 100%` |
| Ads / third-party slots | Slot expands when the ad fills | `min-height` (or fixed `height`) on the slot at the largest expected creative; reserve even when unfilled |
| Async data (feeds, tables, charts, dashboards) | Container is `height: auto` at 0 until data arrives, then everything below slams down | `min-height: clamp(…)` sized to the typical filled height; a skeleton with the same layout (`perceived-latency-mask`) |
| Web fonts (FOUT / FOIT) | Fallback font has different metrics; text reflows when the web font swaps | `font-display: swap` **plus** `@font-face` metric overrides on the fallback: `size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`; or `font-display: optional` for non-critical faces |
| Late-injected banners (cookie bars, promos, "app available") | Pushed into the top of the flow | Reserve the slot in the layout, or overlay it (`position: fixed`) so it takes no flow space |
| Late CSS / CSS-in-JS | Elements render unstyled, then jump | Critical CSS inline in `<head>`; never inject layout styles after first paint |
| `content-visibility: auto` sections | Off-screen sections size to 0 until scrolled into view | `contain-intrinsic-size: auto 600px` (an estimate, corrected once rendered) |
| Animating `height`, `width`, `top`, `margin`, `padding` | Every frame is a layout shift | Animate `transform` / `opacity` only (`tactile-interaction-curves`) |
| Accordions expanding | Content below moves — expected, not scored *if* within 500ms of user input | Fine; but don't auto-expand on load |
| Scrollbars appearing | Content width changes when a vertical scrollbar appears | `scrollbar-gutter: stable` on the scroll container / `html` |
| Lazy-loaded images above the fold | Placeholder then image, with a decode pause | Don't `loading="lazy"` above the fold; `fetchpriority="high"` on the LCP image; dimensions still required |
| Images with no `alt` box when broken | Broken image icon changes size | Dimensions + `alt` — the broken state keeps the reserved box |

## Font metric overrides — the one people skip

```css
@font-face {
  font-family: "Playfair Fallback";
  src: local("Georgia");
  size-adjust: 104%;           /* match x-height/width of the web font */
  ascent-override: 95%;
  descent-override: 25%;
  line-gap-override: 0%;
}
:root { --font-display: "Playfair Display", "Playfair Fallback", Georgia, serif; }
```

Values are per pair; tools like `fontaine`, `capsize`, or Chrome DevTools' font metrics panel compute them. Without overrides, a swap between a wide serif and a narrow fallback reflows every line of a headline — usually the largest single shift on an editorial page.

## Measuring

Chrome DevTools → Performance → "Layout Shifts" track, or Lighthouse's CLS audit with the "Avoid large layout shifts" list. Field data: `web-vitals` library `onCLS`. Target ≤ 0.1; anything above 0.25 is user-visible jank.
