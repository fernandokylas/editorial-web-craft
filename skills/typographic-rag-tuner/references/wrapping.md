# Line-wrapping control cheat-sheet

## The two engine algorithms

| Property | What it does | Where it belongs | Limits |
|---|---|---|---|
| `text-wrap: balance` | Equalises line lengths so a heading wraps as a symmetric block, not 90% + one word | H1–H4, pull quotes, card titles, hero statements, short blurbs (≤ 4–5 lines) | Browsers cap it — Chromium ≈ 6 lines, Firefox ≈ 10. Beyond that it silently does nothing. It's also O(n) per re-layout, so never on `p` or long-form. Chrome 114+, Safari 17.5+, Firefox 121+ |
| `text-wrap: pretty` | Looks ahead a few lines to avoid an orphan (single short word) on the last line, and (in newer engines) improves rag consistency and hyphenation points | `p`, `li`, `blockquote`, `dd`, `figcaption`, any multi-line prose | Chrome 117+, Safari 26+ (typographic version), Firefox in progress. Harmless where unsupported — it's a hint, not a layout change |

Both are progressive enhancements: unsupported browsers fall back to `wrap` and nothing breaks.

## What they *don't* solve

| Problem | Fix |
|---|---|
| A name, date, product, or number splitting across lines (`Q3` / `2026`, `Dr.` / `Okafor`, `12` / `%`) | Wrap in `<span class="nowrap">` with `white-space: nowrap`, or use `&nbsp;` / `&#8239;` (narrow no-break space) before units: `12&#8239;%`, `4&nbsp;pm` |
| Orphan in a heading on a browser without `balance` | JS "widont": replace the last space in the heading with `&nbsp;` (see below) |
| Long URLs, emails, hashes, code tokens overflowing the container | `overflow-wrap: anywhere` on those elements only (not globally — it lets prose break mid-word) |
| Rag is jagged because words are long (German, technical prose) | `hyphens: auto` + a correct `lang` attribute on `<html>`; set `hyphenate-limit-chars: 6 3 3` so it doesn't hyphenate short words |
| Opening quotes / bullets making the left edge look ragged | `hanging-punctuation: first` (Safari) or `text-indent: -0.4em` on the quote line |
| Justified text with rivers | Don't justify on the web unless `hyphens: auto` is also on and the measure is ≥ 60ch; even then prefer ragged-right |
| Heading breaks before a one-letter word (`a`, `I`) or after a preposition | `balance` usually fixes it; if not, `&nbsp;` after the short word |
| Very short last line in a heading (`balance` unsupported and text is 2 lines) | `max-inline-size` tuned in `ch` so the break falls mid-sentence |
| Cards in a grid whose titles wrap to different line counts | `balance` on titles + `min-height` or grid `align-items: start` so bodies still align |

## Widont — heading orphan guard for browsers without `balance`

Only for headings and short blocks; never for paragraphs.

```js
document.querySelectorAll('h1, h2, h3, .editorial-title').forEach(el => {
  if (CSS.supports('text-wrap', 'balance')) return;      // engine does it better
  const words = el.textContent.trim().split(/\s+/);
  if (words.length < 3) return;
  el.innerHTML = el.innerHTML.replace(/\s+(\S+)\s*$/, '&nbsp;$1');
});
```

## Reading the rag

A good ragged-right edge looks like a gentle sawtooth: lines alternate slightly longer/shorter, no line dramatically shorter than its neighbours, no run of three lines the same length (that reads as a hard edge). If the rag looks wrong after `pretty`, the measure is usually the problem — ~62ch with a 1rem sans gives the engine enough room to choose good breaks; under ~45ch there's no good break to find.
