---
name: editorial-type-tokens
description: >-
  Two-face typographic system for premium, editorial, magazine-grade UI — a high-contrast
  serif/display face for H1, H2, hero and section titles, and a clean geometric/humanist sans for
  body, labels, tables, forms, buttons and metadata — mapped as CSS custom properties with weight,
  tracking and line-height per role. Use this whenever writing or reviewing CSS/Tailwind/design tokens
  for headings and body text, picking fonts, building a type scale, or when the page would otherwise
  default to a single face (Inter, Arial, Roboto, system-ui everywhere) — including when the user says
  "make it feel premium / editorial / like a magazine / less generic", "font pairing", "what fonts
  should I use", "typography", or asks for a landing page, report, case study, portfolio, or brand
  site.
---

# Editorial Type Tokens

One font family across a whole interface reads as a default, not a decision. Publications and consultancies that look expensive almost always run two faces with clearly separated jobs: a display face that carries drama at large sizes, and a text face that gets out of the way at small ones. The contrast between them — serif against sans, heavy against regular, tight against open — is what creates hierarchy before the reader has read a word.

Set up both faces as tokens, assign every element a role, and never let the roles blur.

## The two roles

**Display face** — H1, H2, hero statements, pull quotes, editorial section titles, big KPI numbers. A high-contrast serif (Playfair Display, Fraunces, Newsreader) or a heavy display sans when serif is wrong for the brand. Heavy weight (600–700), *negative* tracking (−0.02 to −0.03em — large serifs set loose look amateurish), tight leading (1.05–1.15). Its job is to be noticed.

**Body / UI face** — paragraphs, H3 and below, labels, inputs, buttons, table cells, nav, metadata rails, captions. A geometric or humanist sans that is legible at 12–18px and doesn't call attention to itself. Regular 400 for reading, 500–600 for emphasis and buttons, zero tracking at body size, generous leading (1.5–1.65). Its job is to disappear.

H3 goes to the *body* face on purpose: serif sub-headings at 1.25rem look smaller than the sans text around them (serif x-heights are lower), and three levels of serif dilutes the drama of the top two. Sub-heads in the sans at 600 keep the hierarchy crisp.

## Token contract

```css
:root {
  /* Display — editorial tone */
  --font-display: "Playfair Display", Georgia, Cambria, "Times New Roman", Times, serif;
  --font-weight-display: 700;
  --letter-spacing-display: -0.03em;
  --line-height-display: 1.15;

  /* Body / UI — utility, high scan rate */
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-weight-body-regular: 400;
  --font-weight-body-bold: 600;
  --letter-spacing-body: 0;
  --line-height-body: 1.6;

  /* Metadata — the third voice, still the body face */
  --font-size-meta: 0.75rem;
  --letter-spacing-meta: 0.12em;
}

h1, h2, .editorial-headline {
  font-family: var(--font-display);
  font-weight: var(--font-weight-display);
  letter-spacing: var(--letter-spacing-display);
  line-height: var(--line-height-display);
  color: var(--text-main);
  text-wrap: balance;
}

p, h3, h4, li, td, th, label, input, select, textarea, button, .ui-metadata {
  font-family: var(--font-body);
  font-weight: var(--font-weight-body-regular);
  letter-spacing: var(--letter-spacing-body);
  line-height: var(--line-height-body);
}
h3, h4, th, button { font-weight: var(--font-weight-body-bold); line-height: 1.3; }
h3, h4 { letter-spacing: -0.01em; }                  /* sub-heads in the body face still tighten slightly */
input, select, textarea, button { font: inherit; }   /* form controls don't inherit by default */

.ui-metadata {
  font-size: var(--font-size-meta);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-meta);
  font-weight: var(--font-weight-body-bold);
  color: var(--text-muted);
}
```

Colours reference `--text-main` / `--text-muted` rather than hex so the system survives a dark section (see `ground-inversion-guard`). Sizes come from fluid tokens (`--fs-display`, `--fs-h2`, `--fs-h3` in `fluid-clamp-calculator`) — this skill decides *which face and how it's set*, not how big.

## The metadata voice

Small, uppercase, tracked-out sans (`.ui-metadata`) is the third register: dates, section numbers, labels, table headers, the left rail in an editorial layout. It provides architectural contrast against the big serif without introducing a third family. Tracking scales inversely with size — the shared floor across this skill set is **0.08em for any uppercase text**, rising to 0.12em at 0.75rem; never on lowercase body text. Keep `font-size`, `font-weight` and `letter-spacing` in the *same rule* so the compensation is visible to the next reader and to `accessible-ink-scale`'s audit.

## Choosing the pair

Playfair + system sans is the default and needs no justification. When the brief has a tone — financial, literary, luxury, studio, tech — pick from `references/pairings.md`, which lists tested pairs with the weights to load, the Google Fonts link pattern, and the system-only stacks for offline artifacts. Load two or three weights, not the whole family; a variable font with an axis range is ideal.

If fonts can't load (blocked network, single-file artifact with no `<link>`), the system serif fallback still does the job: Georgia at 700 / −0.02em / 1.1 is more editorial than most people expect. Always design so the fallback looks intentional.

## Things that undo the system

- **Serif body text in UI.** Fine for a long essay page; wrong for anything with forms, tables, or controls. Keep the serif to display sizes.
- **Loose tracking on big serifs.** Positive or zero `letter-spacing` at 3rem+ reads as default. Tighten.
- **Tight leading on body.** `line-height: 1.2` on paragraphs is a heading setting. Body wants 1.5–1.65.
- **Uppercase without tracking.** All-caps at 0.75rem with 0 tracking is a dense block; add 0.08–0.12em.
- **Buttons and inputs in a different face.** They inherit nothing by default — `font: inherit` is mandatory or they'll silently fall to the browser's default sans.
- **Three families.** Display, body, and a mono for code if there's code. Not a fourth.
- **Digits that dance.** Tables and KPIs need `font-variant-numeric: tabular-nums`.
