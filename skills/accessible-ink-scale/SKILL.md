---
name: accessible-ink-scale
description: >-
  Keep small and muted text legible by compensating weight, letter-spacing, line-height, and colour as
  type scales down or sits on a dark ground — ≤14px steps up a weight tier, ≤13px gets open tracking,
  uppercase labels get 0.08–0.12em, light-on-dark text avoids pure white and gets a weight bump. Use
  this whenever styling labels, captions, metadata, table cells, badges, form hints, legal/fine print,
  timestamps, nav links, footer text, or any text under ~0.875rem, and whenever text sits in a
  dark/inverted section — including when the user says "the small text is hard to read", "looks thin /
  washed out / blurry", "labels disappear", "fine print", "micro-typography", or asks for a design-
  system type scale.
---

# Accessible Ink Scale

A font's stroke doesn't shrink proportionally with its size — at 12px a 400-weight sans has strokes about one pixel wide, anti-aliased into grey, and on a glossy screen in daylight those strokes simply aren't there. Letter shapes also crowd: the counters and gaps that make "rn" different from "m" close up as the size drops. And on a dark ground, light strokes bleed outward (halation), which the eye reads as *thinner* letters, not brighter ones. Print typographers solved this a century ago with optical sizes — a 6pt cut of a face was drawn heavier and wider than the 12pt cut. On the web you do it by hand: as text scales down or inverts, add weight, open tracking, and open leading. It's not styling; it's keeping the ink on the page.

## The three compensations

**1. Weight steps up as size steps down.** Below 14px (`0.875rem`) the regular weight erodes — move to 500. At 12–13px or anything uppercase, 600. Variable fonts let you land between (`font-weight: 520`); use the axis. This isn't emphasis — the small text should still look *quieter* than body, which colour and size handle. Weight just keeps its strokes solid.

**2. Tracking opens as size drops.** Body text at 1rem sits at `letter-spacing: 0`. At ≤13px, add `0.02–0.04em` for lowercase. Uppercase needs far more — `0.08em` minimum at any size, `0.12em` at 0.75rem — because caps have no ascender/descender rhythm to separate them and pack into a wall. (These are the shared floors for the whole skill set; the audit enforces 0.08em.) Leading opens with tracking: small text at `1.4–1.5`, never the 1.2 borrowed from headings, or the wider letters read as a squashed block.

**3. Light-on-dark gets armour.** Never `#fff` on a dark ground — pure white on `#0b0c10` halates and the strokes look eaten away. Use `#e0e0e0` for body-size, `#dfdfdf` for small, `#b4b4b4`–`#a0a0a0` for muted (all ≥7:1 — see `ground-inversion-guard`). Keep the small-text weight bump, and apply `-webkit-font-smoothing: antialiased` *only here* — on macOS it counteracts the over-bold glow of subpixel AA on inverted text. Applied globally it thins light-ground text, which is the opposite of what you want.

```css
/* Meta label on paper */
.ui-metadata-tag {
  font-size: 0.75rem;
  font-weight: 600;            /* two tiers up: 12px + uppercase */
  letter-spacing: 0.08em;
  line-height: 1.4;
  text-transform: uppercase;
  color: var(--text-muted);    /* #555 on paper — 7.2:1, the muted floor */
}

/* Same label inverted */
.theme-inverted .ui-metadata-tag {
  color: #dfdfdf;              /* soft silver, no halation; 14.7:1 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Fine print */
.fine-print-legal {
  font-size: 0.8rem;
  font-weight: 500;            /* one tier up */
  letter-spacing: 0.02em;
  line-height: 1.5;
  color: var(--text-main);
}
```

Colour is still the muted-vs-main token from the ground system; this skill adjusts the *mechanics* around it. `references/ink-scale.md` has the full band table (display → floor) with verified contrast ratios on both grounds, plus notes on optical-size axes, `font-size-adjust` for fallbacks, and the 12px floor.

## Where it applies

Anything that isn't body or heading: table cells and headers, form labels and hints, badges and chips, timestamps, breadcrumbs, captions, footnotes, nav and footer links, KPI labels, the meta rail in an editorial layout, legal copy, tooltips. These are the elements that get sized down "to be quiet" and then vanish. Quiet is fine; invisible isn't. Make them quiet with colour (muted token) and size — never by letting the strokes thin out.

And nothing below `0.75rem` (12px). If it needs to be smaller than that to fit, it doesn't fit — use a tooltip, truncate, or drop it.

## Verify

```bash
python scripts/check_ink.py styles.css page.html
```

Fails on rules with `font-size` ≤14px and weight unset or <500; ≤13px with no positive tracking; uppercase with tracking <0.08em; any size below 12px. Warns on small text with leading <1.4, pure white on a dark selector, and `antialiased` on a light one. It resolves `var()` tokens declared in the file, skips `em` sizes (parent-relative), and reads one rule at a time — so declare size, weight and tracking *together* in the rule that sets the size; a size on the parent and a weight on the child passes the eye but not the audit, and confuses the next developer the same way. Then look at the result on a real screen at 100% zoom, ideally a non-retina one — that's where thin type fails first.
