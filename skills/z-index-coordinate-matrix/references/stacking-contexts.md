# Stacking contexts — the real cause of z-index wars

`z-index` only compares elements **within the same stacking context**. A child can never rise above a sibling of its context's root, no matter how large its number. Nearly every `z-index: 99999` in the wild is someone fighting a context they didn't know existed.

## Properties that create a stacking context (often by accident)

| Property | Creates a context when | Typical accidental case |
|---|---|---|
| `position: relative/absolute` + `z-index` ≠ auto | always | intended |
| `position: fixed` / `sticky` | always, even with `z-index: auto` | sticky headers, sticky rails |
| `isolation: isolate` | always | intended — the clean way |
| `opacity` < 1 | always | fade-in cards, disabled states |
| `transform` (any) | always | hover lifts, entrance animations, `translate3d(0,0,0)` hacks |
| `filter`, `backdrop-filter` | always | glass panels, blurred images |
| `will-change: transform/opacity/filter` | always | "performance" hints |
| `mix-blend-mode` ≠ normal | always | luminous borders, blend effects |
| `clip-path`, `mask` | always | masked gradient strokes |
| `perspective`, `transform-style: preserve-3d` | always | 3D cards |
| `contain: paint / layout / strict / content` | always | `content-visibility: auto` |
| `container-type: size / inline-size` | always | container queries |
| flex / grid **item** with `z-index` ≠ auto | always | ordering within a grid |
| top layer (`<dialog>` modal, `popover`) | separate top-layer stack | see below |

So: a card with a hover `transform` (`tactile-interaction-curves`), a fade-in (`gsap-timeline-orchestrator`), a glass border (`adaptive-luminescent-border`), or a container query is a stacking context. A tooltip *inside* it is trapped — it will render under the next card. That's not a z-index problem.

## Escaping a context

1. **Use the top layer.** `<dialog>.showModal()` and `[popover]` render in the browser's top layer, above *everything*, ordered by open time. Tooltips, dropdowns, menus, toasts, and modals should be `popover` / `<dialog>` (`html5-native-fallback`) — then they need no z-index at all and can't be trapped.
2. **Portal it.** If the overlay must be hand-positioned, render it as a child of `<body>` (React portal, `document.body.append`) and position it from the trigger's `getBoundingClientRect()`. CSS anchor positioning (`anchor-name` / `position-anchor`) does this natively where supported.
3. **Remove the accidental context.** If a card only has `transform` for a hover, that's a context only while hovered — usually fine. If it has `will-change: transform` permanently, drop it.

## Negative z-index

`z-index: -1` puts an element behind its stacking context's root *background* if the root doesn't create a context (it sinks behind `body`). With `isolation: isolate` on the container, `--z-subground` stays inside the container, behind its content but above the container's background. Always pair subground layers with an isolated parent.

## Reading a stack

Chrome DevTools → Elements → Layers panel, or the "3D view" in Edge, shows every stacking context as a box. When something won't rise, look for which box it's inside before touching a number.
