---
name: layout-editorial-rail
description: >-
  Two-column "consultancy ledger" page layout — a narrow left meta rail (headings, dates, labels,
  metrics) beside a wide right copy column capped at 62ch. Use this whenever building or restyling
  HTML/CSS/React/Tailwind pages, reports, case studies, docs, briefs, memos, landing pages, or any
  long-form content where the user wants an editorial, premium, journal-like, consulting-report, or
  ledger feel — even if they only say "make it look more editorial", "less SaaS", "less dashboard-y",
  or "like a magazine/report". Also use when the user mentions "editorial rail", "meta rail", "side
  labels", "two-column typography", or asks to fix line length / readability of body text.
---

# Layout Editorial Rail

A page structure borrowed from financial consulting decks, physical ledgers, and high-end journals: a quiet narrow column on the left carries the structural signposts (section titles, dates, labels, small metrics), and a wide column on the right carries all the reading. The reader's eye never has to hunt for where a section starts, and the copy never gets so wide that lines become tiring to scan.

Reach for this instead of the defaults you'd otherwise produce — full-width text blocks, a single centered container, or a SaaS-style card grid. Those read as templated; this reads as considered. It's a layout for *reading*: reports, case studies, long-form, documentation. A dashboard or card grid is a different animal — there, at most, a sticky label column sits beside the grid; don't force the grid into a 62ch column.

## The two columns

**Left — the meta rail.** Narrow (`minmax(180px, 1fr)`), typographically quiet, and only ever holds: section headings, sub-headings, dates, labels, tags, or small meta-metrics ("Q3 2026", "Read time 6 min", "Revenue +12%"). Nothing here should be a paragraph. Style it small, uppercase, tracked-out (`letter-spacing: 0.08em`), muted color, and sticky where it helps (`position: sticky; top: 2rem`). It is an anchor, not a sidebar — no navigation menus, no cards.

**Right — the copy engine.** Everything the reader actually reads: paragraphs, lists, quotes, deep-dive explanation. Hard-capped at `62ch` so lines sit in the 55–75 character range where reading is fastest. This cap is the whole point of the layout; losing it turns the page back into a generic full-width block.

Each section of content is one grid row: rail cell on the left, copy cell on the right. Repeat the pair for every section rather than putting one giant rail beside one giant body.

## CSS blueprint

Use this grid as written unless the framework forces another expression of the same idea (see the Tailwind note below). A ready-made page is in `assets/template.html` — copy it and replace the content when starting from scratch.

```css
.editorial-container {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(auto, 62ch);
  gap: clamp(2rem, 5vw, 4rem);
  align-items: start;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.rail {
  font-size: 0.75rem;
  font-weight: 600;          /* small + uppercase needs the weight to stay legible */
  text-transform: uppercase;
  letter-spacing: 0.08em;
  line-height: 1.4;
  color: var(--text-muted);
  position: sticky;
  top: 2rem;
}

.copy { max-width: 62ch; }
```

Why `minmax(auto, 62ch)` rather than a fixed width: the copy column shrinks gracefully on tablet widths while still never exceeding the reading cap on wide screens. Why `align-items: start`: the rail must sit at the top of its section, not vertically centered against a long body.

### Mobile collapse

Below roughly 720px the two columns stack, with the rail content sitting directly *above* its copy — never below, never hidden. The rail keeps its small uppercase tracked style so it still reads as a label rather than as a stray heading:

```css
@media (max-width: 720px) {
  .editorial-container { grid-template-columns: 1fr; gap: 0.75rem 0; }
  .rail { position: static; margin-bottom: 0.25rem; }
}
```

### Breakouts for wide elements

Code blocks, data tables, wide figures, and charts often need more than 62ch. Let them break out with an explicit utility class, then let the surrounding prose snap straight back to the cap. The breakout must be deliberate and named — never solve it by widening `.copy`:

```css
.editorial-container { --gap-rail: clamp(2rem, 5vw, 4rem); gap: var(--gap-rail); }
.breakout {
  width: calc(100% + var(--gap-rail));      /* extends left into the rail gap */
  max-width: 85ch;
  margin-left: calc(-1 * var(--gap-rail));
  overflow-x: auto;                          /* a very wide table scrolls inside its box */
}
```

The breakout grows *into the gap*, never past the container: because the rail track is `1fr`, the copy column already sits at the container's right edge, so anything centred on the column (the old `100vw` + `translateX(-50%)` trick) spills off-screen and creates a stacking context. Keep prose before and after the breakout in normal `.copy` flow so the reader gets the wide element as a moment of emphasis, not as a change in the page's rhythm.

Put horizontal page padding on `<main>` or a container, not on `body` — full-bleed bands (an inverted section, a wave divider) need to reach the viewport edge.

## Tailwind / utility frameworks

Express the same grid: `grid grid-cols-1 md:grid-cols-[minmax(180px,1fr)_minmax(auto,62ch)] gap-8 lg:gap-16 items-start max-w-[1200px] mx-auto`. Rail: `text-xs uppercase tracking-[0.08em] text-neutral-500 md:sticky md:top-8`. Copy: `max-w-[62ch]`. Don't reach for `prose` without also capping it — Tailwind Typography defaults to 65ch and doesn't give you the rail.

## Things that quietly break the layout

- A hero or nav that's full-width is fine; the *content* below it is what goes on the rail. Don't put the whole page in one grid cell.
- Rail text that turns into sentences. If it needs more than ~6 words, it belongs in the copy column.
- Centering the copy column. It sits left-aligned against the rail; the asymmetry is intentional.
- Dropping the 62ch cap "just for this one section". That's what `.breakout` is for.
- Cards, shadows, and colored panels in the rail. Keep it flat and typographic.

## Example section

```html
<section class="editorial-container">
  <aside class="rail">
    <p>02 — Findings</p>
    <p>Updated 14 Sep 2026</p>
  </aside>
  <div class="copy">
    <h2>Working capital tightened in Q2</h2>
    <p>Receivables stretched from 41 to 56 days …</p>
    <table class="breakout">…</table>
    <p>The table above understates seasonality because …</p>
  </div>
</section>
```
