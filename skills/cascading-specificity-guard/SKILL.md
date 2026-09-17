---
name: cascading-specificity-guard
description: >-
  Structure stylesheets with CSS cascade layers — `@layer base, layout, components, utilities;` — so
  layout utilities (gap, margin, padding, alignment, display) always win over component styles without
  `!important` or specificity hacks. Use this whenever writing a stylesheet or <style> block longer
  than a few rules, setting up CSS for a prototype/page/design system, adding utility classes, or
  debugging "my gap/margin/padding class isn't applying", "the component overrides my utility", "why
  do I need !important", "specificity war", or "CSS order matters". Also use when integrating third-
  party or framework CSS (Tailwind, normalize, a vendor stylesheet) alongside custom styles.
---

# Cascading Specificity Guard

Every stylesheet past a few dozen rules develops the same disease: a component rule (`.profile-card { gap: 1rem }`) beats a layout utility (`.gap-wide { gap: 4rem }`) because it was written later or has a longer selector, someone adds `!important` to the utility, then a *component* needs to override *that*, and the cascade turns into an arms race. The fix isn't discipline about selector length — it's putting the rules into named tiers whose precedence is declared once, up front, and can't be changed by source order or specificity.

CSS `@layer` does exactly that. Rules in a later-declared layer beat rules in an earlier one *regardless of specificity or order within the file*. Declare the tiers, put every rule in the right one, and utilities win by construction.

## The four tiers

```css
@layer base, layout, components, utilities;   /* first line; precedence goes left → right */
```

| Layer | Holds | Why it's here |
|---|---|---|
| `base` | Reset/normalize, element defaults (`body`, `h1`, `p`, `a`, `button`), typography defaults | Lowest authority — anything more specific should be able to override an element default |
| `layout` | Grid tracks, container caps, section rhythm, the editorial rail, flex distributions | Structure sits under components but above resets |
| `components` | Cards, pills, forms, nav, accordions — things with a class and a look | Most of the CSS lives here; it should never be able to break structure below or utilities above |
| `utilities` | Single-purpose overrides: `.gap-wide`, `.mt-0`, `.text-center`, `.hidden`, `.stack` | Highest authority — a utility on an element is an explicit instruction and must win every time |

```css
@layer base {
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; background: var(--bg-main); color: var(--text-main); font-family: var(--font-body); }
}
@layer layout {
  .grid-ledger { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(auto, 62ch); gap: 2rem; }
}
@layer components {
  .profile-card { background: var(--surface-card); border: 1px solid var(--rule); gap: 1rem; }
}
@layer utilities {
  .gap-wide { gap: clamp(2rem, 5vw, 4rem); }   /* beats .profile-card's gap — no !important needed */
  .mt-0     { margin-top: 0; }
}
```

`<div class="profile-card gap-wide">` gets the wide gap. Reorder the file, add `.grid-ledger .profile-card` specificity to the component, it doesn't matter — `utilities` was declared last, so it wins.

Tokens (`:root { --… }`) can sit outside layers; custom property declarations don't compete the way normal properties do, and keeping them at the top makes them easy to find. One other block is deliberately unlayered: the `@media (prefers-reduced-motion: reduce)` safety net from `reduced-motion-enforcer`, placed *last*, with `!important` — it exists precisely to beat every layer, and unlayered-plus-important is the only position that guarantees it. Everything else goes in a layer.

## The three things that break it

**1. Unlayered rules.** Any rule *outside* an `@layer` block beats *every* layer, including utilities. One stray `.card { gap: 0 }` at the bottom of the file, or a component someone pasted outside the block, silently overrides the whole architecture. This is the most common failure and the hardest to spot by eye — the audit script exists mainly for it. Third-party CSS must be imported *into* a layer:

```css
@import url("normalize.css") layer(base);
@import url("vendor-datepicker.css") layer(components);
```

**2. `!important`.** It inverts layer order — `!important` declarations in *earlier* layers beat `!important` in later ones (base > layout > components > utilities). So an `!important` in a component doesn't just win against one utility; it flips the tier logic. Under `@layer` there is no reason for `!important` outside one deliberate case: a `.hidden { display: none !important }` style utility that must beat inline styles or JS-set properties. Even then, prefer `[hidden]`.

**3. Media queries written outside layers.** `@media (max-width: 720px) { .grid-ledger { … } }` at the bottom of the file is unlayered (see 1). Put the `@layer` *inside* the media query — `@media (…) { @layer layout { … } }` — or nest the media query inside the layer block. Same for `@container` and `@supports`.

## Working inside the tiers

- **Keep specificity flat within a layer.** Layers settle *cross-tier* conflicts; within a tier, ordinary specificity and order still apply. Single-class selectors (`.card`, `.card-title`) and `:where()` for zero-specificity resets keep the inside of each layer predictable. IDs and four-deep descendant chains are a smell in any tier.
- **Component styles set component properties.** A component may set its own internal `gap`, `padding`, `margin`; that's fine — a utility on the same element wins when applied. What a component must not do is reach *out* and style the layout around it (`.card + .card { margin-top }` belongs to layout, or better, to a `.stack` utility on the parent).
- **Utilities are single-purpose and named for what they do.** `.gap-wide`, not `.card-spacing-fix`. One declaration, maybe two; if a utility grows a third property it's a component.
- **Frameworks already do this.** Tailwind v4 emits `@layer theme, base, components, utilities;` — match its names and drop your custom CSS into the same layers so the two cooperate instead of fighting. For unlayered legacy CSS you can't edit, import it into `base` or a new `legacy` layer declared *before* `components` so your rules can override it.
- **Single-file artifacts.** `@layer` works inside a `<style>` block exactly the same way; the order statement is the first line of the block.

## Verify

```bash
python scripts/check_layers.py styles.css          # or page.html — reads its <style> blocks
python scripts/check_layers.py app.css --order theme,base,components,utilities   # Tailwind v4 names
```

Fails on: no order statement or one that isn't the first `@layer` use; a layer used but not declared; **unlayered rules** (with the first offender named); `!important` in any layer but the last. Warns on `!important` in utilities (redundant), ID selectors, 4+-part selector chains, and component/utility overlap on `gap`/`margin`/`padding` so you can confirm the intent. Run it after any stylesheet change that touches more than one tier.
