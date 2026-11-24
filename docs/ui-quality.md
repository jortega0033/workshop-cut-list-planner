# UI quality rules

Binding rules for the pages of this project (`cut_planner/static/`) and for every user-facing string. The owner set rules 1 and 2 and approved rules 3 to 10 on 2026-11-22 (see [owner-decisions.md](owner-decisions.md)). They exist to avoid the usual marks of generated interfaces.

## The rules

1. No thick accent border on one side of a card, callout, alert, list item or quote (for example `border-left: 4px solid <accent>`). Use spacing, type weight, an icon or a full hairline border instead.
2. No soft tinted background with a thin border of the same hue as the default way to mark a status, tag, callout or card. One neutral surface and one clear signal (text, icon or a solid chip) is enough.
3. No gradient text and no purple-to-blue gradient as a default accent.
4. No blur or glass panels, and no drop shadow plus large radius on every card.
5. No emoji used as icons or bullets, and no sparkle marks.
6. No pill or badge on things that are not states. No all-caps, letter-spaced micro labels as section decoration.
7. No centred hero with a slogan in an application screen. Screens open on the user's task.
8. One accent colour, used for the primary action and the current selection. Status colours only for status.
9. Dense, aligned layouts on a consistent spacing scale. No card grid where a table or a list is the right form.
10. User-facing copy is plain and specific: no filler, no exclamation marks, and the same word for the same thing everywhere.

## How they are applied

- A ticket that changes a page starts with the `ui-ux-pro-max` skill (`.claude/skills/ui-ux-pro-max/`, design-system search for the product type) and ends with a check of each changed screen against this file. The result goes in the pull request.
- User-facing copy, documentation and pull request text go through the `unslop` skill (`.claude/skills/unslop/`) before the pull request is opened.
- Frontend Developer, Accessibility Auditor and Code Reviewer name this file in their checklists (`.claude/agents/`). The Code Reviewer gate runs on every ticket and is where these rules are enforced.
- Rule 1 can be linted, for example `grep -rnE "border-(left|right|top|bottom)[^;]*[2-9]px" cut_planner/static/`. Rule 2 cannot be detected reliably from CSS, so it is a review check.
- The repository rules in `CLAUDE.md` still apply: native HTML, CSS and JavaScript, same-origin assets only, no CDN or external font. No UI source exists yet, so nothing is checked today; every UI ticket applies the rules to its own new screens.
- The printed sheet plan is a drawing, not a screen: rules 1 to 9 apply to the planner, rule 10 to both.
