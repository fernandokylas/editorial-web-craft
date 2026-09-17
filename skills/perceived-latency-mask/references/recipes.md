# Skeleton recipes

Every skeleton is built from the same principle: **same container, same grid, same dimensions as the real content** — only the leaves are replaced by bars. If the skeleton and the loaded state don't share a layout, the swap causes a layout shift, which is worse than a spinner.

All use the classes in `assets/skeleton.css`.

## Editorial rail section
```html
<section class="editorial-container is-loading-state" aria-hidden="true">
  <aside class="rail">
    <div class="skeleton-bar title-stub"></div>
    <div class="skeleton-bar text-stub-short"></div>
  </aside>
  <div class="copy">
    <div class="skeleton-bar heading-stub"></div>
    <div class="skeleton-bar text-stub-full"></div>
    <div class="skeleton-bar text-stub-long"></div>
    <div class="skeleton-bar text-stub-full"></div>
    <div class="skeleton-bar text-stub-partial"></div>
  </div>
</section>
```
Same `.editorial-container` / `.rail` / `.copy` classes as the real section, so the grid tracks, gap and 62ch cap are identical.

## Card grid
```html
<div class="grid is-loading-state" aria-hidden="true">
  <article class="card">                       <!-- repeat × visible count -->
    <div class="skeleton-bar image-stub"></div>
    <div class="skeleton-bar heading-stub" style="height:1.25rem;width:70%;margin-top:1rem"></div>
    <div class="skeleton-bar text-stub-full"></div>
    <div class="skeleton-bar text-stub-partial"></div>
  </article>
</div>
```
Render exactly as many cards as the first page will show (or as fit the viewport), not a random three.

## List / table rows
```html
<div class="is-loading-state" aria-hidden="true">
  <div class="skeleton-bar row-stub"></div>   <!-- × N, N = rows per page -->
</div>
```
For tables, keep the real `<thead>` visible and skeleton only `<tbody>` rows — headers are known before data.

## Avatar + text row (comment, notification, contact)
```html
<div class="row is-loading-state" aria-hidden="true" style="display:flex;gap:.75rem;align-items:center">
  <div class="skeleton-bar avatar-stub"></div>
  <div style="flex:1">
    <div class="skeleton-bar text-stub-short" style="width:30%"></div>
    <div class="skeleton-bar text-stub-long" style="margin-top:.4rem"></div>
  </div>
</div>
```

## KPI tiles
Number stub at the display size (`height: var(--fs-display); width: 4ch`), label stub below at 0.75rem. Tiles keep their real `min-height`.

## Image / media module
`.image-stub` with the real `aspect-ratio`. When the image loads, put it in the *same box* — never let the box resize.

## What not to skeleton
- Navigation, headers, footers, page chrome — render immediately; they don't depend on data.
- Anything already in the HTML — server-rendered content is *content*, not a placeholder.
- A single small element (one badge, one number) — a subtle inline placeholder or just the empty slot is less noisy than a shimmer.
- Whole pages. Skeleton the region that's waiting; let the rest be usable.

## The swap

```js
async function load(region, fetcher, render) {
  region.setAttribute('aria-busy', 'true');
  const skeleton = region.querySelector('.is-loading-state');
  const shownAt = performance.now();
  try {
    const data = await fetcher();
    // If the skeleton became visible, keep it ≥ 400ms so it doesn't flicker
    const visibleFor = performance.now() - shownAt - 300;         // 300 = appear delay
    if (visibleFor > 0 && visibleFor < 400) await new Promise(r => setTimeout(r, 400 - visibleFor));
    skeleton.replaceWith(render(data));
    region.lastElementChild.classList.add('is-loaded-state');
  } catch (err) {
    skeleton.replaceWith(renderError(err));                       // never leave a skeleton forever
  } finally {
    region.setAttribute('aria-busy', 'false');
  }
}
```

Timing rules: nothing under ~300ms gets a skeleton (the CSS appear-delay handles it); once shown, hold ≥400ms; past ~10s, replace with a message and a retry — a skeleton that never resolves is the "frozen app" signal it was meant to prevent.
