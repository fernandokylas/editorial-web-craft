# Display / body pairings

Each row is a tested pair: a display face for H1/H2/hero, a body/UI sans for everything else. All display and body faces are on Google Fonts (free) unless marked *system-only*; every stack ends in system fallbacks so the page looks intentional with fonts blocked. Weights listed are the ones worth loading — don't load nine.

| Tone | Display face (weights) | Body / UI face (weights) | Notes |
|---|---|---|---|
| Classic editorial, magazine | **Playfair Display** 700, 400i | System sans stack | The default. High-contrast, dramatic; keep tracking −0.03em at large sizes |
| Literary, warm, long-form | **Newsreader** 500, 600 (opsz axis) | **Inter Tight** 400, 600 | Optical sizing makes it work at H3 sizes too; body at 1.0625rem reads like a printed page |
| Consulting / financial report | **Fraunces** 600 (`"SOFT" 50`) | **IBM Plex Sans** 400, 600 | Fraunces "soft" axis dials down the drama; Plex has real tabular figures for tables |
| Modern luxury, fashion | **Cormorant Garamond** 600, 500i | **Manrope** 400, 600 | Cormorant is light — use it *large* (≥2.5rem) or it disappears; never for body |
| Architecture / studio | **DM Serif Display** 400 | **DM Sans** 400, 500 | Same family origin, so x-heights agree; very calm pairing |
| Tech editorial, product blog | **Instrument Serif** 400, 400i | **Geist** 400, 600 or system | Instrument is narrow — good for long headlines; Geist has system-like neutrality |
| Journal / essay, quiet | **Source Serif 4** 600 | **Source Sans 3** 400, 600 | Designed together; safest "invisible" pairing when brand isn't the point |
| Bold, poster-like | **Bricolage Grotesque** 800 (display sans) | **Bricolage Grotesque** 400 (text sizes) | A sans display pairing for when serif reads too traditional; contrast via weight + size |
| *System-only* (no network) | Georgia / Cambria / "Times New Roman" 700 | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial` | Georgia at −0.02em with 1.1 line-height is more editorial than people expect |
| *System-only*, modern | `"Iowan Old Style", "Palatino Linotype", Palatino, serif` 700 | `system-ui` | Iowan is on every Mac/iOS; Palatino on Windows |

## Loading

One `<link>` with only the weights you use, `display=swap`, and `preconnect`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
```

Variable fonts (Fraunces, Newsreader, Manrope, Bricolage) take an axis range: `family=Newsreader:opsz,wght@6..72,400..600`.

## Sizing the two faces together

Serif display faces have smaller x-heights than sans body faces, so a serif H3 at `1.25rem` beside sans body at `1rem` can look *smaller* than the body. Either give H3 to the body face (as the default rules do — H3 and below are sans) or bump serif sub-headings ~10% larger than the sans size they'd otherwise be.

## Figures

Tables, KPIs, dates, prices: `font-variant-numeric: tabular-nums` on the body face so columns align. Display faces in KPI tiles are fine (`--font-display` at 600) but still set `tabular-nums` or the digits will dance between "1" and "8" widths.
