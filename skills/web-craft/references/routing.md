# Routing: which skills, for which page, in which phase

Classify the job on five axes first; the matrix then tells you what to load. Load a skill by reading its `SKILL.md` (in Claude Code the `Skill` tool does this by name; elsewhere read `../<name>/SKILL.md`). Read a skill's `references/` or `assets/` only when the phase that needs them arrives.

## Axes

| Axis | Values | Tell-tales in the brief |
|---|---|---|
| **Kind** | `reading` · `grid` · `deck` · `mixed` | reading: case study, report, article, docs, brief, memo, landing with long copy · grid: dashboard, portfolio, catalogue, pricing, feature cards · deck: presentation, pitch, one-screen-per-section · mixed: hero + rail sections + a card band |
| **Ground** | `paper` · `obsidian` · `mixed` | "dark", "night", "on black" → obsidian; "a dark section / band / footer" → mixed; otherwise paper |
| **Motion** | `none` · `tactile` · `choreographed` | none: docs, legal, anything the user calls "simple/static"; tactile: buttons and cards should feel good (default); choreographed: "cinematic", "animate in", "reveal on scroll", "parallax", "premium launch page" |
| **Network** | `zero` · `fonts` · `cdn` | zero: "works offline", "no dependencies", artifact for review; fonts: a Google Fonts link is fine; cdn: user asked for GSAP/a chart lib, or motion = choreographed |
| **Task** | `new` · `improve` | improve: an existing file/URL is given; audit and preview it *before* changing anything |

## Matrix

**A — Always** (every page, every kind):

| Skill | Phase | Why it's unconditional |
|---|---|---|
| `cascading-specificity-guard` | build | the four-layer stylesheet is the container every other rule goes in |
| `ground-inversion-guard` | build | both palettes are defined even on a single-ground page; the tokens are the vocabulary |
| `editorial-type-tokens` | build | two faces, roles, the metadata voice |
| `fluid-clamp-calculator` | build | sizing tokens; no px breakpoints |
| `typographic-rag-tuner` | build / polish | balance + pretty, nowrap for dates and units |
| `accessible-ink-scale` | build / polish | any label, caption, footer, table cell |
| `html5-native-fallback` | build | landmarks, headings, `<button>`; and any disclosure/dialog/menu the page has |
| `z-index-coordinate-matrix` | build | declare the matrix; isolate components |
| `cls-dimension-anchor` | build / verify | any image, embed, async region, web font |
| `reduced-motion-enforcer` | build / verify | the safety net ships even when motion = none (hover states are motion) |
| `visual-weight-tuner` | polish | every icon+label pair and every pill |

**B — By deliverable:**

| Condition | Skill |
|---|---|
| single-file deliverable (default for `new`) | `encapsulated-mockup-builder` — start from its boilerplate |
| into an existing codebase | skip the boilerplate; apply the layer order and tokens to the existing stylesheet; still run `audit.py` on the touched files |

**C — By kind:**

| Kind | Load | Skip |
|---|---|---|
| reading | `layout-editorial-rail` (rail + 62ch copy; breakout for tables) | card grids inside the copy column |
| grid | `adaptive-luminescent-border` for card edges; a sticky label column is fine but do **not** force the grid into a rail | `layout-editorial-rail` for the grid itself (it is a reading layout) |
| deck | `sub-pixel-inertia-scroll` (`.deck` proximity snap) + `layout-editorial-rail` inside each slide | GSAP unless motion = choreographed |
| mixed | `layout-editorial-rail` for reading sections, `adaptive-luminescent-border` for the card band, `inline-svg-decorator` for the divider between grounds | — |

**D — By ground:**

| Ground | Notes |
|---|---|
| paper | tokens as `:root`; `adaptive-luminescent-border` groove profile |
| obsidian | `.theme-inverted` on `body`/`main`; `accessible-ink-scale` dark rules (no `#fff`, `antialiased` only here); check muted text on **card surfaces**, not just the ground |
| mixed | each dark section is a `.theme-inverted` band; `inline-svg-decorator` wave/tilt at the boundary; re-run contrast for the band's own pairs |

**E — By motion:**

| Motion | Load | Skip |
|---|---|---|
| none | `reduced-motion-enforcer` only (safety net) | tactile, magnetic, gsap, inertia |
| tactile | `tactile-interaction-curves`; `magnetic-hitbox-warp` **only** for the primary CTA and top-level nav (≤ 6 per view) | gsap, inertia |
| choreographed | `tactile-interaction-curves` + `gsap-timeline-orchestrator` (needs network = cdn) **or** `sub-pixel-inertia-scroll` (no library: `.arrive` + planes). Use GSAP for multi-element sequences, inertia for parallax + light arrivals. | magnetic on anything but the CTA |

**F — Conditional:**

| Condition | Skill |
|---|---|
| anything loads after first paint (fetch, lazy section, simulated API) | `perceived-latency-mask` — skeleton in the same grid, `aria-busy`, timeout |
| icons, dividers, decorative shapes, a placeholder logo | `inline-svg-decorator` (icon set, `wave.py`) |
| a dark section on a light page, or vice-versa | `ground-inversion-guard` badge/link/rule re-mapping + `adaptive-luminescent-border` profile switch |

## Skip rules (the mistakes the matrix exists to prevent)

- No skeletons on server-rendered content. If nothing loads late, `perceived-latency-mask` is off.
- No magnetic fields on inline links, list rows, or anything in a grid. Primary CTA + nav only.
- No GSAP when network = zero. Use `sub-pixel-inertia-scroll`'s CSS-only arrivals instead.
- No rail layout around a card grid; no card grid inside a 62ch copy column.
- No luminous edge on structural separators (table rows, accordion items) — plain `1px solid var(--rule)` there.
- No `transform`-canvas scroll hijack, ever. Inertia skill plays on top of native scroll.
- Improve-task: audit and preview **first**, list what fails, then change — the user wants to know what was wrong, not just a new file.

## Phase order

1. **Foundation** — A + B: file, layers, tokens (both grounds), faces, sizes, depth matrix.
2. **Structure** — C: the layout for the kind; landmarks and headings from `html5-native-fallback`.
3. **Surface** — D + F: edges, dividers, icons, skeletons.
4. **Interaction** — E: press physics, entrances, fields.
5. **Polish** — rag, ink, optical nudges.
6. **Verify** — `audit.py`, then the preview protocol.
