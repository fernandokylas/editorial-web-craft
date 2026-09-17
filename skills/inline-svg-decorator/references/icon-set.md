# Crisp 24-grid icon set

Stroke icons on a `0 0 24 24` grid, `stroke-width="1.5"`, round caps and joins, `stroke="currentColor"`, no fill. Coordinates are integers or clean halves so strokes land on pixel edges at 16/24/32px. Copy the `<path>` (or the whole `<symbol>`) — don't retrace them.

All share this wrapper:

```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
  …path…
</svg>
```

| Name | Path(s) |
|---|---|
| arrow-right | `<path d="M4 12h16M14 6l6 6-6 6"/>` |
| arrow-left | `<path d="M20 12H4M10 6l-6 6 6 6"/>` |
| arrow-up-right (external) | `<path d="M7 17L17 7M8 7h9v9"/>` |
| chevron-down | `<path d="M6 9l6 6 6-6"/>` |
| chevron-right | `<path d="M9 6l6 6-6 6"/>` |
| check | `<path d="M5 12l5 5L20 7"/>` |
| close | `<path d="M6 6l12 12M18 6L6 18"/>` |
| plus | `<path d="M12 5v14M5 12h14"/>` |
| minus | `<path d="M5 12h14"/>` |
| search | `<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>` |
| menu | `<path d="M4 7h16M4 12h16M4 17h16"/>` |
| info | `<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>` |
| alert | `<path d="M12 3l9.5 17h-19L12 3zM12 10v4M12 17h.01"/>` |
| calendar | `<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M8 3v4M16 3v4"/>` |
| clock | `<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>` |
| document | `<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>` |
| link | `<path d="M10 14a4 4 0 005.66 0l3-3a4 4 0 00-5.66-5.66l-1.5 1.5"/><path d="M14 10a4 4 0 00-5.66 0l-3 3a4 4 0 005.66 5.66l1.5-1.5"/>` |
| mail | `<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 8l9 6 9-6"/>` |
| star | `<path d="M12 3l2.8 5.9 6.2.8-4.5 4.4 1.1 6.4L12 17.5l-5.6 3 1.1-6.4L3 9.7l6.2-.8z"/>` |
| play (optically shifted) | `<path d="M8.5 5.5v13l10-6.5z"/>` — note the 0.5 shift right toward the point |

## Sprite pattern for repeated icons

When the same icon appears more than twice on a page, define it once and reference it — the browser parses one path, not twenty:

```html
<svg viewBox="0 0 0 0" class="icon-sprite" aria-hidden="true">   <!-- .icon-sprite { position:absolute; width:0; height:0; overflow:hidden } -->
  <symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12l5 5L20 7"/>
  </symbol>
</svg>

<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-check"/></svg>
```

```css
.icon { width: 1em; height: 1em; display: inline-block; vertical-align: -0.125em; }
```

`1em` sizing ties the icon to the surrounding font size; `vertical-align: -0.125em` sits it on the baseline correctly for most fonts (see the `visual-weight-tuner` skill for cap-height nudges beyond that).

## Stroke weight guide

| Rendered size | stroke-width on 24 grid | Why |
|---|---|---|
| 16px | 1.5–1.75 | 1.5 becomes 1px on screen; anything thinner breaks up |
| 20–24px | 1.5 | Matches 400–500 weight text |
| 32px+ | 1.25–1.5 | Heavier strokes start to look like glyphs, not lines |
| Next to 600+ weight text | 2 | Match the text's stem weight |
