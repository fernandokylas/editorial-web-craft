---
name: ground-inversion-guard
description: >-
  Keep colour contrast and hierarchy intact when a page flips between light ("paper") and dark
  ("obsidian") grounds — dark hero on a light site, inverted footer, dark-mode toggle, alternating
  sections, cards on a dark band. Accent tokens are re-mapped per ground (a deep green *fill* on paper
  becomes a bright mint *text* colour on dark) instead of being reused as-is, and every
  text/background pair is checked against WCAG AAA. Use this whenever generating or reviewing
  CSS/Tailwind/design tokens that involve a dark section, `.dark`/`.inverted` modifier, `prefers-
  color-scheme`, theme variables, badges/links/buttons on coloured backgrounds, or when the user says
  "dark mode", "invert this section", "the green looks muddy on dark", "make sure it's accessible", or
  "contrast".
---

# Ground Inversion Guard

Colour tokens aren't ground-independent. A deep emerald that reads as authoritative on cream turns into unreadable mud on near-black; a soft grey that's fine as muted text on white vanishes on obsidian. The amateur move is to define `--accent: #0e6245` once and use it everywhere. The professional move is to treat each ground as its own contrast system and *mutate* the tokens when the ground flips — same hue family, different job and luminance.

Two rules carry most of the weight:

1. **On light grounds, accents are fills; on dark grounds, accents are text.** A saturated dark colour makes a great background box on paper but a poor text colour on obsidian. Flip its role: keep a *deep* version for background boxes and introduce a *bright* version for typography.
2. **Every pair is measured, not eyeballed.** Ship nothing below 7:1 for body text (AAA), 4.5:1 for large text (≥24px, or ≥19px bold), 3:1 for icons, borders, and UI components. The bundled script does the arithmetic.

## The token contract

Each ground defines the *same set* of variables so components never change; only the values move. Use these as the starting palette:

```css
/* --- Paper ground (root) --- */
:root {
  --bg-main:        #fcfbf9;   /* soft warm white; #ffffff is fine for product UI */
  --text-main:      #1a1a1a;   /* 16.8:1 — off-black, no glare */
  --text-muted:     #555555;   /*  7.2:1 — AAA; #666 only reaches AA on paper */
  --accent-solid:   #0e6245;   /* deep green: BACKGROUND fills, badges, rules */
  --accent-text:    #0e6245;   /*  7.1:1 — the same green also works as text here */
  --accent-on-solid:#ffffff;   /*  7.4:1 — text that sits ON --accent-solid */
  --rule:           #e4e2dc;   /* hairlines; must stay ≥3:1 as a UI boundary if load-bearing */
}

/* --- Obsidian ground (scoped modifier) --- */
.theme-inverted {
  --bg-main:        #0b0c10;   /* deep obsidian; #121212 for a warmer slate */
  --text-main:      #f5f5f5;   /* 17.9:1 — soft white, not pure #fff, to limit halo */
  --text-muted:     #a8a8a8;   /*  8.2:1 on the ground, 7.5:1 on a #15171c card — measure against every surface, not just the ground */
  --accent-solid:   #1b3d32;   /* muted deep green: background boxes ONLY */
  --accent-text:    #4ade80;   /* 11.2:1 — bright mint for links, labels, numbers */
  --accent-on-solid:#f5f5f5;   /* 10.9:1 — text on the deep-green box */
  --rule:           #2a2c33;
  background: var(--bg-main);
  color: var(--text-main);
}
```

The critical line is `--accent-text` in the inverted block. Same hue, but luminance is pushed up until it clears 7:1 on the dark ground. Brighten first; if the result looks garish, desaturate slightly rather than darkening it back.

Note the third accent token, `--accent-on-solid`. Text placed *on* an accent fill needs its own colour — reusing `--text-main` there gives 2.4:1 on paper (dark text on dark green), which is the most common failure in this pattern. The second most common: `--accent-text` on `--accent-solid` (bright mint on deep green, 6.9:1) — an accent label never sits on an accent box.

`--rule` is deliberately faint (≈1.3:1): it's a decorative hairline for table rows, card edges and dividers, where the *content* carries the meaning. A boundary that is the only thing telling the user an element exists — an input's edge, an unfilled button's outline, a toggle track — is *load-bearing* and needs ≥3:1 (WCAG 1.4.11); `adaptive-luminescent-border` keeps a separate `--edge-functional` token for those. Check those with `contrast.py --ui`.

## Components consume roles, never raw colours

```css
.promo-badge {
  background: var(--accent-solid);
  color: var(--accent-on-solid);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
}
.highlight-link {
  color: var(--accent-text);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 0.15em;
}
.stat-number { color: var(--accent-text); }
.section-rule { border-top: 1px solid var(--rule); }
```

Because the badge, link, and rule read variables, dropping any of them inside `.theme-inverted` re-maps them correctly with no component-level overrides. If you find yourself writing `.theme-inverted .promo-badge { color: … }`, a token is missing — add it to both blocks instead.

## Applying an inversion to a section

1. Scope the modifier to the section (`<section class="theme-inverted">`) — don't override globals.
2. Set `background` and `color` on the modifier itself so bare text inside inherits correctly.
3. Walk each accent use inside the section and ask: *is this a fill or is this text?* Fills take `--accent-solid`; text takes `--accent-text`; text on a fill takes `--accent-on-solid`.
4. Check the pairs. From the skill directory:
   ```bash
   python scripts/contrast.py --matrix "#f5f5f5,#a0a0a0,#4ade80" "#0b0c10"
   python scripts/contrast.py "#f5f5f5" "#1b3d32"      # text on the badge fill
   ```
   Anything under 7:1 for body text gets its luminance adjusted, not its opacity. Include every *surface* a text colour lands on — cards, badges, inset panels — not only the section ground; a muted grey that passes on `#0b0c10` can fail on a `#15171c` card.
5. Check the *transition* between grounds: a paper section directly above an obsidian one needs no rule; a dark section on a dark-ish site needs a 1px `--rule` or a tonal step so the boundary is visible (≥3:1 between the two grounds, or a visible edge).

## Things that quietly fail

- **Reusing the light accent as dark text.** `#0e6245` on `#0b0c10` is ~1.6:1. It will look "on-brand" in a mockup thumbnail and be unreadable on a phone outdoors.
- **Pure `#000` / pure `#fff` as grounds.** Maximum contrast isn't the goal — `#fff` on `#000` produces halation on OLED and glare on LCD. Stay in the `#0b0c10`–`#121212` and `#f5f5f5`–`#fcfbf9` bands.
- **Muted text that's muted by opacity.** `opacity: .6` on white text makes its contrast depend on whatever is behind it. Use a solid `--text-muted` that's been measured against `--bg-main`.
- **Tailwind `dark:` classes sprinkled per element.** Fine for one-offs; for a section-level inversion it scatters the contract across the markup. Prefer CSS variables consumed by `bg-[var(--bg-main)]` / `text-[var(--accent-text)]`, or a plugin that exposes the roles as utilities.
- **Border-only elements on dark.** A `1px #2a2c33` outline that was visible on paper disappears on obsidian. Either raise it to ≥3:1 or give the element a tonal background instead.
- **Images and icons carrying baked-in colour.** An SVG icon with `fill="#0e6245"` won't flip. Use `fill: currentColor` and let the parent's text colour drive it.

## Checking a finished section

Run the matrix once for each ground with every text colour used against every background used in that ground, including accent fills as backgrounds. Fix by adjusting luminance in the failing token; then re-run. Contrast is a property of the pair, so both grounds are checked independently — a token that passes on one ground says nothing about the other.
