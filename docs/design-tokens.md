# Design tokens

The visual system is the Pipenzo "Flow look": a black page, Flow-style alpha layers, one accent (Pipenzo yellow `#FECE02`), red only for danger. Dark is the primary design.

## Source and resync

- `cut_planner/static/tokens.css` is a byte-for-byte copy of `extension/sidepanel/tokens.css` in `jortega0033/clip-to-reel-studio` at commit `a13378ce73e5b27213c9a200fc960ec93afef054` (git blob `41d6d6dbb17ea1055db9c4bc2ea8fb0b557ef108`).
- Resync: copy the file over `cut_planner/static/tokens.css`. Never edit the copy; change the source instead.
- The comments in `tokens.css` are narrower than this document (they do not list the current selection or the focus ring). This document takes precedence, because the copy must stay identical to the source.

## Rules

- New UI uses these tokens. No new colour literals in CSS or JavaScript. Code that draws (canvas, SVG) or sets a colour reads the token with `getComputedStyle(document.documentElement).getPropertyValue('--name').trim()`.
- Text never sits on a bare alpha layer; use a solid surface token.
- **14-D1, current selection.** The yellow accent is used for the primary action, the current-step marker and the current selection (decided by the owner, 2026-11-23). How it is drawn (recommended by the orchestrator, adopted under the owner's delegation of the same day): a solid `--primary` fill with `--on-primary` text, not only a yellow border (about 1.5:1 against white on light), a second sign that is not colour (weight, an icon or text), and the fitting aria attribute. Never a tint with a same-hue border and never a thick one-sided border.
- **14-D2, focus ring.** `--focus` is a focus indicator, exempt from the accent limit, including where it is yellow in dark (recommended by the orchestrator, adopted under the owner's delegation of 2026-11-23).
- **14-D3, themes.** Contrast and no-colour-alone checks cover the light and the dark block of `tokens.css` (same source as 14-D2).
- **14-D4, linking.** The ticket that creates a page or its static allowlist links `tokens.css` before any other stylesheet and serves it; the allowlist test covers it (same source as 14-D2).
- `--state-selected` is a neutral layer and does not mark the current selection.

## Status

No screen uses the tokens yet; every UI ticket follows these rules from its first screen. Served folder: `cut_planner/static/`. Not checked in a browser.

## Light and dark

The `:root` block is the light theme. A `prefers-color-scheme: dark` block overrides it, so the operating system colour scheme decides. There is no manual switch.

## Fonts

This repository ships no font files. `--font` and `--font-display` resolve to local system fonts. Never load a web font from another host; bundling a font needs an owner decision.

## Token names by role

- Surfaces: `--bg`, `--bg-raised`, `--bg-sunken`, `--surface`, `--ink`
- Text: `--fg`, `--muted`, `--faint`, `--on-primary`, `--on-ink`, `--on-ink-muted`
- Lines: `--border`, `--hairline`, `--control-border`, `--input-border`, `--focus`
- Accent: `--primary`, `--primary-press`, `--primary-edge`
- Status: `--success`, `--ok`, `--ok-bg`, `--warn-fg`, `--warn-bg`, `--danger`, `--danger-bg`, `--info`
- Type, space, shape, motion: `--font`, `--font-display`, `--mono`, `--space-1` to `--space-7`, `--radius-*`, `--dur-*`, `--ease-*`

The glass, blur, gradient and shadow tokens exist in the file but are not a licence to use them ([ui-quality.md](ui-quality.md) rules 3 and 4). The file itself is the exact list.
