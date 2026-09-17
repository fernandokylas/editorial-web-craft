# Ink scale

Compensations by size band. "Weight" is relative to the body's regular weight (usually 400). Contrast ratios are against `#fcfbf9` (paper) and `#0b0c10` (obsidian), verified with `ground-inversion-guard/scripts/contrast.py`.

| Band | Size | Weight | Tracking | Leading | Paper colour | Obsidian colour |
|---|---|---|---|---|---|---|
| Display | ≥ 2rem | as designed (600–700) | −0.02 to −0.03em | 1.05–1.15 | `#1a1a1a` 16.8:1 | `#f5f5f5` 17.9:1 |
| Headings (H3/H4) | 1.25–2rem | as designed | −0.01em | 1.2–1.3 | `#1a1a1a` | `#f5f5f5` |
| Body | 1–1.125rem | 400 | 0 | 1.5–1.65 | `#1a1a1a` / `#2c2c2c` 13.5:1 | `#e0e0e0` 14.8:1 |
| Small body / fine print | 0.8–0.875rem (13–14px) | **+1 tier → 500** | **+0.02em** | **1.5** | `#2c2c2c` | `#dfdfdf` 14.7:1 |
| Micro / meta / labels | 0.75–0.8rem (12–13px) | **+1–2 tiers → 500–600** | **+0.04em** (lowercase) / **+0.08em min, 0.12em at 0.75rem** (uppercase) | **1.4** | `#555555` 7.2:1 | `#dfdfdf`, or `#a8a8a8` 7.5:1 on card surfaces for muted |
| Floor | 0.75rem (12px) | — | — | — | nothing smaller; use a tooltip or hide | — |

## Rules of thumb

- **Step weight up one tier per band below body.** 400 → 500 at ≤14px, → 600 at ≤12px or when uppercase. Variable fonts: `font-weight: 520` is fine — use the axis.
- **Tracking scales inversely with size.** Large negative, body zero, small positive. Uppercase always needs more than lowercase at the same size because caps have no ascender/descender rhythm to separate them.
- **Leading opens as tracking opens.** Wider letters need more vertical room or the block looks squashed: small text at 1.4–1.5, not the 1.2 people copy from headings.
- **Muted ≠ light.** "Muted" small text still needs 7:1. On paper `#555` (7.2:1) is the floor; `#666` (5.6:1) fails AAA and reads as grey mush at 12px. On obsidian `#a0a0a0` (7.5:1) is the floor; `#b4b4b4` is more comfortable.
- **Never pure white on dark.** `#fff` on `#0b0c10` halates — strokes visually bleed and look thinner. `#e0e0e0`–`#f5f5f5` is the working range; small text toward the lower end.
- **Optical sizing.** Fonts with an `opsz` axis (Newsreader, Fraunces, Source Serif 4, Inter 4) do the stroke compensation themselves — leave `font-optical-sizing: auto` (the default) on and you may need less manual weight boost. Test rather than assume.
- **Font smoothing.** `-webkit-font-smoothing: antialiased` thins text on macOS. Apply it *only* on dark grounds, where it counteracts the over-bold glow of subpixel AA on light-on-dark text. Applied globally on light grounds it makes body text lighter — the opposite of what this skill is for.
- **Fallback metrics.** If the primary font may not load, `font-size-adjust: ex-height from-font` keeps the fallback's x-height (and therefore perceived size) matched, so the small text doesn't shrink further on fallback.
