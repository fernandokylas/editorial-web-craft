# Preview protocol — Chrome DevTools MCP

Tools are named by suffix here (`navigate_page`, `take_screenshot`, …). The full name depends on which plugin provides the server: `mcp__plugin_editorial-web-craft_chrome-devtools__<suffix>` when bundled with this plugin, `mcp__plugin_chrome-devtools-mcp_chrome-devtools__<suffix>` from the official plugin, or `mcp__chrome-devtools__<suffix>` from a user-level MCP entry. Use whichever is present; if none is, skip to **Static mode** at the end.

The audits catch what a script can catch. The preview is for the other half: does it *look* right, does it survive a phone, does it stay still while loading, does it still work with motion off. Run the whole protocol once on the first build; on later iterations re-run only the steps whose inputs changed.

## 0. Open the page

- `new_page` with the file URL (`file:///abs/path/page.html` — Chrome opens local files directly). If the page fetches anything relative, serve it instead: `python3 -m http.server 8766 --bind 127.0.0.1` from the file's directory and open `http://127.0.0.1:8766/page.html`.
- `list_console_messages` — expect **zero errors** (a 404 for `favicon.ico` is noise; anything else is a defect).

## 1. Three widths

For each of `1280×900`, `768×1024`, `390×844`: `resize_page`, then `take_screenshot` (full page at 1280, viewport at the others is enough), then run the probe:

```js
() => {
  const de = document.documentElement;
  const q = s => document.querySelector(s);
  const r = el => el && el.getBoundingClientRect();
  const c = r(q('.editorial-container, .container, main'));
  const rail = r(q('.rail, .meta-rail, [class*="rail"]'));
  const copy = r(q('.copy, .copy-engine'));
  const brk = r(q('.breakout'));
  const copyW = copy ? copy.width / parseFloat(getComputedStyle(q('.copy, .copy-engine')).fontSize) * 1.9 : null; // ≈ characters
  return JSON.stringify({
    vw: innerWidth,
    horizontalOverflow: de.scrollWidth > innerWidth,             // must be false
    containerInsideViewport: c ? c.left >= 0 && c.right <= innerWidth : null,
    railStacksOnMobile: innerWidth < 720 && rail && copy ? rail.bottom <= copy.top + 1 : null,
    railStickyOnDesktop: innerWidth >= 720 && rail ? getComputedStyle(q('.rail, .meta-rail')).position === 'sticky' : null,
    breakoutInsideContainer: brk && c ? brk.left >= c.left - 1 && brk.right <= c.right + 1 : null,
    breakoutClearsRail: brk && rail && innerWidth >= 720 ? brk.left >= rail.right - 1 : null,
    copyMeasureCh: copyW ? Math.round(copyW) : null,               // ≤ ~66 on desktop
    layersDeclared: [...document.styleSheets].some(s => { try { return [...s.cssRules].some(r => r.constructor.name === 'CSSLayerStatementRule'); } catch { return false; } }),
    lastRuleIsMotionNet: (() => { try { const rs = [...document.styleSheets[0].cssRules]; return /prefers-reduced-motion/.test(rs[rs.length - 1].cssText); } catch { return null; } })(),
  });
}
```

Pass: `horizontalOverflow === false` at all three widths; rail sticky at 1280, stacked above copy at 390; breakout inside the container and clear of the rail; measure ≤ ~66ch at 1280.

Then **look at the screenshots** — this is the part no script does:
- Hierarchy: can you tell in one glance what the page is about and where to start reading?
- Rag: headings near-rectangular (no one-word last line); paragraphs a soft sawtooth, no orphan.
- Optical: icons sit on the cap-height of their labels; pills don't look bottom-heavy; round dots don't look smaller than square swatches beside them.
- Rhythm: consistent section spacing; nothing cramped at 390, nothing swimming at 1280.
- Does it read as *considered* rather than templated — asymmetry, two faces, edges not walls?

## 2. Interactive states

If the page has a dialog, menu, accordion, or CTA: `take_snapshot`, then `click` each control and `take_screenshot` after. Probe:

```js
() => {
  const d = document.querySelector('dialog[open]');
  const r = d && d.getBoundingClientRect();
  return JSON.stringify({
    dialogOpen: !!d,
    dialogCentred: r ? Math.abs((r.left + r.right) / 2 - innerWidth / 2) < 2 : null,
    detailsCount: document.querySelectorAll('details').length,
    popoverOpen: !!document.querySelector(':popover-open'),
    focusVisibleStyled: !!(getComputedStyle(document.activeElement, ':focus-visible').outlineStyle !== 'none'),
  });
}
```

`press_key` `Escape` closes a dialog/popover; `press_key` `Tab` a few times and confirm focus is visible in a screenshot.

## 3. Reduced motion

`emulate` with `{ "prefers-reduced-motion": "reduce" }` (or the tool's equivalent media-feature option), reload with `navigate_page`, `take_screenshot`, and probe:

```js
() => {
  const hidden = [...document.querySelectorAll('.arrive, [data-reveal], .is-loading-state, .card, section')]
    .filter(el => { const cs = getComputedStyle(el); return el.offsetParent !== null && (parseFloat(cs.opacity) < 0.99 || cs.visibility === 'hidden'); }).length;
  const moving = [...document.querySelectorAll('*')].filter(el => { const cs = getComputedStyle(el); return cs.animationName !== 'none' && cs.animationPlayState !== 'paused'; }).length;
  const transformTransitions = [...document.querySelectorAll('*')].filter(el => /transform/.test(getComputedStyle(el).transitionProperty)).length;
  return JSON.stringify({ hiddenUnderReduce: hidden, runningAnimations: moving, transformTransitions });
}
```

Pass: `hiddenUnderReduce === 0` (nothing disappears), `runningAnimations === 0`, `transformTransitions === 0`. Hover a button and screenshot — the colour/shadow should still change; nothing should lift or scale. Clear the emulation afterwards.

## 4. Layout shift and paint

`performance_start_trace` with `reload: true, autoStop: true`, then `performance_analyze_insight` for `CLSCulprits` and `LCPBreakdown`. Pass: CLS ≤ 0.1 with no culprit elements; LCP element is the hero heading or hero image, not a late-loaded asset. If the page has skeletons, screenshot at ~200ms and ~1500ms after `navigate_page` to see the skeleton → content swap and confirm nothing below it moved.

Optional on a final pass: `lighthouse_audit` (`categories: ["accessibility", "best-practices"]`) — read the failures, not the score.

## 5. Report

For each width, the screenshot path. For each probe, the JSON and a one-line verdict. Then a short list: what the eye caught that the audits didn't, and what was changed in response. Close the page with `close_page`.

## Static mode (no browser tools)

State that no browser is available, run `audit.py`, and give the user the three-width checklist above as things to look at when they open the file. Never claim a preview happened. If the environment renders HTML inline (an artifact/preview surface), use it for the 1280 view and say which checks that covers.
