---
name: html5-native-fallback
description: >-
  Build accordions, disclosures, modals, popovers, dropdowns, toggles, progress bars, and page
  structure from native HTML5 elements — <details>/<summary>, <dialog>, the popover attribute,
  <button>, <main>/<nav>/<aside>/<article> — instead of div-and-span components driven by JavaScript
  state machines and hand-written ARIA. Use this whenever generating or reviewing HTML/JSX for any
  interactive component or page scaffold, and especially when the user asks for an accordion, FAQ,
  collapsible, expandable section, modal, dialog, drawer, dropdown, menu, tooltip, tabs, toggle, or
  "make it accessible / keyboard-friendly / work without JS" — even if they don't mention semantics.
  Also use when reviewing markup that has onclick on divs, href="#" links, or role="button" on non-
  buttons.
---

# HTML5 Native Fallback

The browser already ships an accessible accordion, an accessible modal with focus trapping and `Esc`, an accessible popover with light-dismiss, and a button that works with keyboard, screen reader, and voice control. A `<div onclick>` with a hand-rolled `aria-expanded` toggle re-implements a fraction of that, badly, and stops working the moment the script is slow, blocked, or throws. Native elements get keyboard handling, focus management, ARIA roles, and the accessibility tree for free — and they keep working when JavaScript doesn't.

So the first question for any interactive component is not "how do I build this" but "which element already is this". `references/native-patterns.md` is the lookup table — accordion, exclusive accordion, modal, drawer, popover, dropdown, switch, segmented control, progress, date input, carousel, and the one common component (tabs) that has no native element and needs a small, correct ARIA implementation.

## Three rules that carry most of the weight

**1. Disclosures are `<details>`/`<summary>`.** No click listeners, no `hidden` toggling, no `aria-expanded` — the browser manages all of it. `open` sets the initial state; `name="group"` makes a set exclusive (one open at a time) with no JS. Style `summary` like any button; strip the marker with `list-style: none` and `::-webkit-details-marker { display: none }`.

```html
<div class="semantic-accordion-group">
  <details class="accordion-node" name="method" open>
    <summary class="accordion-trigger">
      <span class="trigger-text">01 / Methodological Rigor</span>
      <span class="trigger-indicator" aria-hidden="true"></span>
    </summary>
    <div class="accordion-content">
      <p>Native structure stays accessible when scripts are blocked, delayed, or fail on a slow connection.</p>
    </div>
  </details>
  <details class="accordion-node" name="method">
    <summary class="accordion-trigger">
      <span class="trigger-text">02 / Automated Focus States</span>
      <span class="trigger-indicator" aria-hidden="true"></span>
    </summary>
    <div class="accordion-content">
      <p>Native components join the accessibility tree automatically — focus, announcements, and state come from the browser.</p>
    </div>
  </details>
</div>
```
```css
.accordion-node { border-bottom: 1px solid var(--rule); padding: 1rem 0; }
.accordion-trigger {
  display: flex; justify-content: space-between; align-items: center;
  list-style: none; cursor: pointer; font-weight: 600;
}
.accordion-trigger::-webkit-details-marker { display: none; }
.accordion-trigger:focus-visible { outline: 2px solid var(--accent-text); outline-offset: 4px; }
.accordion-content { padding-top: 1rem; max-width: 62ch; }
.trigger-indicator { transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1); }
.accordion-node[open] .trigger-indicator { transform: rotate(45deg); }
```

The state hook is the `[open]` attribute — style against it rather than adding classes. The indicator is `aria-hidden` because `summary` already announces expanded/collapsed.

**2. Modals are `<dialog>`; popovers are `popover`.** `dialog.showModal()` is two lines of JS for a focus trap, `Esc`, inert background, and `::backdrop` that would take a hundred lines to replicate. Close it with `<form method="dialog"><button>Close</button></form>` — no JS at all. For menus, tooltips, and non-modal panels, `<button popovertarget="menu">` + `<div id="menu" popover>` gives light-dismiss and top-layer stacking with zero script.

**3. Anything clickable is a `<button>` or a real `<a href>`.** A `<div onclick>` isn't focusable, isn't announced as interactive, and doesn't respond to Enter/Space. An `<a href="#">` navigates (jumps to top) and announces as a link. Rule: if it *goes somewhere*, it's `<a href="/real-url">`; if it *does something*, it's `<button type="button">`. Always set `type` — inside a form, a bare `<button>` submits.

## Structure is semantic too

Page chunks get the landmark that describes them, not a `<div class="sidebar">`:

- `<main>` — exactly one; the primary content.
- `<nav>` — navigation blocks; `aria-label` each when there's more than one.
- `<aside>` — tangential content: a meta rail, related links, a pull-quote column.
- `<article>` — anything that stands alone (post, card in a feed, comment).
- `<section>` — a thematic group *with a heading*. No heading → it's a `<div>`.
- `<header>` / `<footer>` at page level become `banner` / `contentinfo` landmarks.

Headings form an outline: one `<h1>`, then levels that never skip. Screen-reader users navigate by landmark and heading before they read a word; the outline is the table of contents.

`<div>` and `<span>` are still right for pure layout wrappers — grid containers, flex rows, spacing shells. The rule is no *interactive* or *structural* divs, not no divs.

## When JavaScript is still needed

Some things have no native element: tabs, a rich combobox, a data grid, drag-and-drop. Build those with the correct ARIA pattern (WAI-ARIA Authoring Practices) and full keyboard support — and still put a native `<button>` at the centre of each control so the base behaviour survives. Progressive enhancement: the page must be usable before the script runs; the script adds convenience, not existence. If content is only reachable via JS, it's not there for a meaningful share of users.

## Verify

```bash
python scripts/check_semantics.py page.html
```

Fails on `onclick`/`role=button`/`tabindex` on non-interactive elements, `href="#"` buttons, accordion-shaped or modal-shaped markup without `<details>`/`<dialog>`, missing or duplicate `<main>`, and skipped heading levels. Warns on `<button>` without `type`, `<section>` without a heading, unlabelled multiple `<nav>`s, and `<img>` without `alt`. Then tab through the page: every interactive element reachable, every state change announced, nothing you can click that you can't also key.
