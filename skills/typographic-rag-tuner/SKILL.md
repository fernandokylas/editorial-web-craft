---
name: typographic-rag-tuner
description: >-
  Control how text wraps — `text-wrap: balance` on headings so no single word dangles on the last
  line, `text-wrap: pretty` on paragraphs for a clean ragged edge, and nowrap/hyphenation/overflow
  rules for names, dates, units, and URLs. Use this whenever writing CSS for any text-bearing element
  (headings, hero copy, paragraphs, cards, captions, quotes), setting up base typography, or when the
  user says "orphan", "widow", "dangling word", "the heading wraps badly", "ragged edge", "uneven
  lines", "one word on its own line", "make the typography feel polished", or asks for
  editorial/premium copy layout.
---

# Typographic Rag Tuner

A headline that wraps to two full lines and then one lonely "growth." on a third reads as broken, even though every word is right. A paragraph whose last line is a single "it." looks unfinished. A block whose right edge zig-zags between 30 and 62 characters has a jagged silhouette that tires the eye before it's read anything. Print typographers fix these by hand; the browser now has two algorithms that do most of it, if they're switched on. Treat every text block as a shape, not a stream, and set the wrapping rules that keep the shape clean.

## The two rules

**Headings balance.** `text-wrap: balance` tells the engine to distribute the words so lines are as even as possible — a two-line heading becomes 50/50 instead of 90/10, and the dangling last word disappears. It belongs on anything short and prominent: H1–H4, pull quotes, card titles, hero statements, blurbs under five lines. It stops working past ~6 lines and costs layout time, so it must not go on paragraphs.

**Paragraphs go pretty.** `text-wrap: pretty` looks ahead a few lines and adjusts earlier breaks to avoid an orphan on the final line, and tidies the rag. It belongs on `p`, `li`, `blockquote`, `figcaption`, `dd` — anything multi-line and read continuously. It's cheap enough for whole documents.

```css
@layer base {
  h1, h2, h3, h4, .editorial-title { text-wrap: balance; }
  h1, h2 { letter-spacing: -0.02em; }   /* display sizes set tighter; loose tracking exaggerates gaps */
  h3, h4 { letter-spacing: -0.01em; }   /* sub-heads: a touch, not the display tightness */
  p, li, blockquote, figcaption, dd, .copy-narrative {
    text-wrap: pretty;
    max-width: 62ch;             /* the measure the algorithm needs to find good breaks */
  }
}
```

Both are progressive enhancements — an older browser just wraps normally — so there's no reason to withhold them. Put them in the base layer once, not per component.

## What the algorithms can't do

They choose break *positions*; they don't know that some things must not break at all. Handle those explicitly:

- **Things that belong together** — `Q3 2026`, `Dr. Okafor`, `12 %`, `iPhone 17 Pro`, `4 pm`: `<span class="nowrap">` (`white-space: nowrap`) or a non-breaking space. Use a narrow no-break space (`&#8239;`) before units and `%`.
- **Things that must break somewhere** — URLs, email addresses, hashes, long identifiers: `overflow-wrap: anywhere` on *those elements only*. Globally, it lets prose split mid-word.
- **Long-word languages / technical prose** — `hyphens: auto` with a correct `lang` on `<html>`, and `hyphenate-limit-chars: 6 3 3` so short words stay whole.
- **The measure itself.** No wrapping algorithm rescues a 100ch line or a 35ch one. ~62ch for body, wider only via a deliberate breakout (`layout-editorial-rail`), and heading `max-inline-size` in `ch` when a two-line break keeps landing on a preposition.

`references/wrapping.md` has the full table — browser support, the `balance` line-count caps, hanging punctuation, justified-text cautions, a widont fallback for headings in old engines, and how to read a rag.

## Judging the result

Look at the silhouette, not the words. A heading should be a near-rectangle. A paragraph's right edge should be a soft sawtooth — no line far shorter than its neighbours, no three lines exactly the same length, no single word on the last line. If the shape is wrong after `balance`/`pretty`, the fix is almost always the measure or a nowrap, not more CSS.

## Quick check

1. Every heading selector and `.editorial-title` has `text-wrap: balance`; no paragraph does.
2. `p, li, blockquote` have `text-wrap: pretty`.
3. Dates, names with titles, numbers with units are wrapped in `.nowrap` or joined with `&nbsp;` / `&#8239;`.
4. `overflow-wrap: anywhere` appears only on URL/code/identifier selectors.
5. `<html lang>` is set if `hyphens: auto` is used.
