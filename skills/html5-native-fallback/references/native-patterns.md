# Component → native element map

Before writing a JS state machine, check this table. "JS needed" means the minimum to invoke a native API, not to manage state or focus.

| Component | Native answer | JS needed | Notes |
|---|---|---|---|
| Accordion / disclosure | `<details><summary>` | none | Keyboard, focus, `aria-expanded` all built in. Style `summary` freely; hide the marker with `list-style: none` + `::-webkit-details-marker { display:none }` |
| Exclusive accordion (one open) | `<details name="faq">` on each | none | Same `name` = radio-group behaviour. Baseline 2024 (Chrome 120, Safari 17.2, Firefox 130); older browsers just allow multiple open — a fine degrade |
| Modal dialog | `<dialog>` + `dialog.showModal()` | 2 lines | Focus trap, `Esc` to close, `::backdrop`, inert background, `role=dialog` — all native. Close with `<form method="dialog"><button>` — no JS |
| Non-modal dialog / toast / drawer | `<dialog>` + `dialog.show()`, or `popover` | 1–2 lines | `popover` needs zero JS: `<button popovertarget="x">` + `<div id="x" popover>` |
| Dropdown menu / popover / tooltip | `popover` attribute | none (positioning may need 3 lines) | Light-dismiss, `Esc`, top-layer stacking. Position with CSS anchor positioning (`anchor-name` / `position-anchor`) where supported; elsewhere set `top/left` from the trigger's `getBoundingClientRect()` on open — a top-layer element ignores any ancestor's `position: relative` |
| Native select | `<select>` | none | Style with `appearance: none` + your own chevron. Customisable `<select>` via `appearance: base-select` (Chrome 135+) allows rich options |
| Combobox / autocomplete | `<input list="x">` + `<datalist>` | none | Basic but fully accessible. Only build custom when you need rich option rendering |
| Toggle switch | `<input type="checkbox" role="switch">` | none | `:checked` drives the visual; `role=switch` gives the right announcement |
| Radio cards / segmented control | `<input type="radio">` + `<label>` | none | Group with `<fieldset><legend>`; `:checked + label` styling |
| Tabs | **no native element** | small | Use `role=tablist/tab/tabpanel`, `aria-selected`, arrow-key handling — ~25 lines. Or: if tabs are just navigation between pages, they're `<nav>` links; if it's a settings pane, radio inputs + `:checked ~ .panel` works with zero JS |
| Progress / meter | `<progress>` / `<meter>` | none | `<progress>` for task completion, `<meter>` for a value in a range (disk usage, score) |
| Date / time / colour / range input | `<input type="date|time|month|color|range">` | none | Native pickers are accessible and mobile-friendly; custom pickers rarely are |
| Number stepper | `<input type="number" step>` | none | |
| Form validation | `required`, `pattern`, `min/max`, `:user-invalid` | none | `:user-invalid` (not `:invalid`) so errors show after interaction, not on load |
| Search box | `<search><form role="search">` | none | `<search>` element is Baseline 2023 |
| Expand/collapse content with animation | `<details>` + `::details-content` + `interpolate-size: allow-keywords` | none | Chrome 131+; elsewhere it opens instantly — acceptable |
| Skip link | `<a href="#main">` as first focusable | none | Visually hidden until focused |
| Breadcrumb | `<nav aria-label="Breadcrumb"><ol>` | none | |
| Carousel | `<ul>` with `scroll-snap-type` + `overflow-x: auto` | optional | Native scroll = native keyboard/touch/AT. Add prev/next `<button>`s that call `scrollBy` if wanted |
| Sticky header / sidebar | `position: sticky` | none | |
| Copy-to-clipboard, share | `<button>` + `navigator.clipboard` / `navigator.share` | 1 line each | The button is native; the action needs the API |

## Landmarks

One `<main>`. `<header>` / `<footer>` at page level are `banner` / `contentinfo`. `<nav>` for navigation blocks (label them if more than one: `aria-label="Primary"`, `aria-label="Footer"`). `<aside>` for content tangential to the main flow — a meta rail, related links, a pull-out. `<article>` for anything that would make sense syndicated on its own — a post, a card in a feed, a comment. `<section>` for thematic grouping *with a heading*; a `<section>` without a heading is just a `<div>`.

## When a `<div>` is right

Pure layout wrappers with no meaning — grid containers, flex rows, spacing shells. The rule is not "no divs", it's "no *interactive* or *structural* divs".
