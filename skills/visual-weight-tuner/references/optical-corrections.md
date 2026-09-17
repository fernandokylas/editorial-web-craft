# Optical corrections reference

A working list of the adjustments typographers and icon designers apply by eye. Values are starting points; verify at rendered size. Read this when a component involves anything beyond a basic icon-plus-label or pill.

| Situation | Why it looks wrong | Correction |
|---|---|---|
| Icon beside uppercase / title-case text | Flex centers on the line box; text mass sits at the baseline | Nudge icon up `0.5–1.5px`; size icon ≈ `1–1.15em` |
| Icon beside all-lowercase text | Mass is at x-height, lower than for caps | Smaller nudge (`0–0.5px`) or none; check per font |
| Label inside filled button / pill | Baseline gravity; descender slack below | Bottom padding `+1px` / `+0.05rem`, or `line-height: 1–1.2` |
| Pill with leading icon | Icon side reads heavier | Reduce padding on the icon side by ~`0.1–0.2rem`, or let icon carry its own margin |
| Play ▶, chevron ›, arrow → in a square/circle button | Mass is on the flat side; point looks pushed to the edge | Shift toward the point `1–2px` (~5% of button width) |
| Circle next to square, same nominal size | Circle has ~78% of the area | Scale circle up `10–15%` |
| Triangle next to square | ~50% of the area | Scale up `15–20%`, or match on visual width not bounding box |
| Round letterforms / round icons on a baseline | Curves visually fall short of a straight edge | Overshoot baseline and cap line by `1–2%` of cap-height when drawing; don't align to overshoot when placing |
| All-caps text at small sizes | Caps set tight read as a dense block | `letter-spacing: 0.08–0.12em` (0.08 is the shared floor; 0.12 at 0.75rem) |
| Large display headings | Default tracking looks loose at big sizes | `letter-spacing: -0.01 to -0.03em` |
| Bulleted lists, quotes, brackets at a left margin | Punctuation makes the margin look ragged | Hanging punctuation: pull bullets/quotes into the gutter (`text-indent: -0.4em` or `hanging-punctuation: first`) |
| Icon stroke next to text | Stroke weight doesn't match font weight | Match icon stroke to the text's stem weight (≈ `1.5px` icon stroke for 400–500 weight body; `2px` for 600+) |
| Two different font sizes on one line (e.g. `12` and `px`) | Baselines align but the small text looks low | `align-items: baseline`, then nudge the small text up `~0.05em` |
| Vertically centered text in a tall box (hero, card) | Text box centered but visual mass low | Shift text up `~2–4%` of the container height |
| Horizontal centering of a wordmark / logo | Bounding box includes a descender, tail, or serif that adds no mass | Center on the letterforms' visual mass; ignore the stray glyph feature |
| Dark shape on light vs light on dark | Light-on-dark appears larger (irradiation) | Reduce light-on-dark elements/strokes by `~5–10%`, or bump dark-on-light |
| Thin lines / dividers vs bold text | 1px line disappears next to heavy type | Use `1.5px` or lower the line's opacity rather than thickness; keep it as a visual rhythm, not a wall |

## Reading the result

- If a correction is doing its job, nobody notices it. If people notice it, it's over-applied.
- Corrections compound: a pill with an icon needs the cap-height nudge *and* the asymmetric padding *and* the icon-side padding trim. Apply each, then look at the whole.
- Always comment optical offsets (`/* optical */`). Uncommented `top: -1px` gets deleted in the next refactor.
