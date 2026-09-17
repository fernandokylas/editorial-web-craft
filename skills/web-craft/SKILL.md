---
name: web-craft
description: >-
  Orchestrates the editorial-web-craft skill set to build a new website, landing page, case study,
  report, dashboard mockup, portfolio, or any HTML/CSS front-end — or to take an existing page and make
  it feel premium, editorial, and considered instead of templated. Routes the brief to the right
  skills (ledger layout, fluid type, two-face typography, dual-ground colour, optical polish, tactile
  motion, native semantics), builds from a self-contained boilerplate, runs the combined audit, and
  previews the result in Chrome DevTools at three widths and under reduced motion. Use this whenever
  the user asks to build, design, redesign, mock up, prototype, polish, review, or preview a web page
  or site, says "make it look premium / editorial / high-end / less generic / less like a SaaS
  dashboard", asks for a landing page or one-pager, or hands over an HTML file to improve — even if
  they don't mention any of the individual skills.
---

# Web Craft

The twenty skills beside this one each fix one thing well. A page needs most of them, in the right order, and then needs to be *looked at* — because the last mile of premium is judged by eye, not by lint. This skill is the order and the eye: it classifies the job, loads what's needed phase by phase, builds, audits, previews in a real browser, and iterates until the page passes both the scripts and the screenshot.

Read `references/routing.md` before building anything; it decides what to load. Read `references/preview-protocol.md` when you reach the preview step.

## 0. What's available

Check before promising anything:

- **Browser**: are Chrome DevTools tools present (any name ending in `navigate_page`, `take_screenshot`, `evaluate_script`, `emulate`, `performance_start_trace`)? → *full mode*: build, audit, preview, iterate. Absent → *static mode*: build and audit, then hand the user the preview checklist. Never block on a missing browser and never claim a preview you didn't run.
- **Python 3**: needed for `scripts/audit.py` and the skills' generators. Absent → apply the skills' quick-check lists by hand and say so.

## 1. Intake

Classify on five axes (`routing.md` has the tell-tales): **kind** (reading / grid / deck / mixed), **ground** (paper / obsidian / mixed), **motion** (none / tactile / choreographed), **network** (zero / fonts / cdn), **task** (new / improve). Ask only if two readings would produce materially different pages — a "dashboard" that's really a report, a "landing page" with no copy to lay out. Otherwise decide and state the assumptions in the report.

For an **improve** task: read the file, run `audit.py`, and — in full mode — run the preview protocol on it *before* touching anything. The user wants to know what was wrong. List it, then fix it.

## 2. Route and load

`routing.md` gives the matrix. Load the always-on set (layers, both palettes, faces, fluid sizes, rag, ink, native semantics, depth matrix, CLS anchors, motion safety net, optical polish), then the conditional skills the classification calls for. In Claude Code, load a skill with the `Skill` tool by name; in other agents, read `../<skill-name>/SKILL.md`. Read a skill's `references/` or `assets/` only when the phase that needs them arrives — the set is designed for progressive loading.

Respect the skip rules: no skeletons without async content, no magnetic fields off the CTA and nav, no GSAP when the page must be zero-network, no rail around a grid, no luminous edges on table rows.

## 3. Build

Single-file deliverable (the default for a new page): start from `../encapsulated-mockup-builder/assets/boilerplate.html` — it already declares the four layers, both palettes, the fluid and depth tokens, the motion safety net, an icon sprite, and a button with the optical nudges. Reading pages take `../layout-editorial-rail/assets/template.html`'s grid. Partials from other skills (`skeleton.css`, `luminous-borders.css`, `kinetic-planes.css`, `magnetic.css`) paste in under the boilerplate's layer order; scripts (`entrance.js`, `inertia-planes.js`, `magnetic.js`) go inside the single `<script>` block.

Into an existing codebase: keep their structure, introduce the layer order and the tokens at the top of their stylesheet, and apply skills to the files you touch.

Content is real-shaped: plausible names, dates, figures, sentence lengths. Lorem ipsum hides every layout problem the skills exist to solve.

Use the generators rather than guessing: `clamp.py` for any size not in the baseline, `contrast.py` for every new colour pair (include card surfaces, not just the ground), `wave.py` for dividers.

## 4. Audit

```bash
python3 scripts/audit.py page.html            # or: page.html styles.css app.js
python3 scripts/audit.py page.html --allow-cdn --allow-fonts   # acknowledge chosen remote assets
```

Seven checkers in one run: containment, cascade layers, motion guards, semantics, micro-type ink, layout shift, stacking. Fix every FAIL. Read every WARN and decide — some are intentional (a component and a utility both setting `gap` under `@layer` is fine; a remote GSAP tag you chose is fine). Re-run until the FAIL count is zero. If a checker is reported UNAVAILABLE, the set is partially installed; say so and apply that skill's quick-check by hand.

## 5. Preview

Full mode only. Follow `references/preview-protocol.md` exactly: open the page, zero console errors, three widths with screenshots and the layout probe, interactive states, reduced-motion emulation with the "nothing hidden, nothing moving" probe, a performance trace for CLS/LCP. Then judge the screenshots for what scripts can't see — hierarchy, rag, optical alignment, rhythm, whether it reads as considered.

Static mode: run the audit, then give the user the three-width checklist from the protocol and say plainly that no browser preview was run.

## 6. Iterate, then report

Fix what the preview caught, re-audit, re-run only the affected preview steps. Cap at three rounds; if something still isn't right after three, report it as open rather than looping.

The report, in this order:

1. **What was built or changed**, and the five-axis classification with any assumptions.
2. **Skills applied** — one line each on what it changed in this page. Skills deliberately skipped and why.
3. **Audit** — the final `audit.py` output, with each remaining WARN explained.
4. **Preview** — screenshot paths per width, probe results, what the eye caught and what was done about it; or the static-mode checklist.
5. **How to open it** — double-click / drag into a browser, what to try (which controls work, which states exist).
6. **Open items** — anything not resolved, and what would resolve it.

## Judgement calls the skills leave to you

- A brief that says "dashboard" but is mostly prose is a reading page with a KPI band, not a grid.
- A dark hero on a light site is a `mixed` ground with one `.theme-inverted` band — not a dark-mode toggle.
- "Animate it" without specifics means `tactile` plus one entrance for the hero; not parallax on everything.
- When two skills' defaults touch (a heading's tracking, a border on a table row), the routing file's skip rules and the sibling skills' "composes with" notes decide; if still unclear, the more restrained option wins.
- Premium is restraint plus precision. If the page is starting to look busy, remove a mechanism rather than tune it.
