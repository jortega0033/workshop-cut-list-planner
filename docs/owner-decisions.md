# Owner decisions

A dated record of the decisions made for this repository, so the rules do not depend on anyone's memory of a conversation. Changing any entry needs the owner. An agent that finds a decision blocking a ticket stops and says so.

The owner made decisions 1 to 10 and 12 on 2026-11-22 for all repositories that get the SDLC kit, and asked on 2026-11-24 to apply the kit here (jortega0033/sdlc-kit v1.2.0). Each row says who decided.

| # | Decision | Source | Date | Implemented in |
|---|---|---|---|---|
| 1 | The instructions, tooling and playbook live on the default branch (`main`). | decided by the owner | 2026-11-22 | `CLAUDE.md`, `.claude/`, `.github/` |
| 2 | Persona agents run automatically during ticket work and carry instructions tailored to this project. | decided by the owner | 2026-11-22 | `.claude/agents/`, `.claude/agency-agents/README.md`, `CLAUDE.md` "Agent roles" |
| 3 | Every open ticket is about app implementation; tooling is installed, not ticketed. | decided by the owner | 2026-11-22 | `.claude/`, `.github/`, `docs/` |
| 4 | Agents may take a ticket up to a ready pull request. Only the owner merges and releases. | decided by the owner | 2026-11-22 | `CLAUDE.md`, `.claude/skills/next-ticket/SKILL.md`, `docs/RELEASING.md`, `.claude/settings.json` |
| 5 | No scheduler. Ticket work starts only on the owner's go signal (`/next-ticket`), because the repository is used to train AI models. | decided by the owner | 2026-11-22 | `.claude/skills/next-ticket/SKILL.md`, `LOOP.md` |
| 6 | A review gate hook blocks opening or readying a pull request until the gate roles have run after the last code edit. | decided by the owner | 2026-11-22 | `.claude/hooks/role_gate.py`, `.claude/settings.json` |
| 7 | Loop Engineering stays at L1, report-only and unscheduled. | decided by the owner | 2026-11-22 | `LOOP.md`, `loop-constraints.md`, `loop-budget.md` |
| 8 | Continuous integration runs on Linux and Windows; the default branch requires a pull request and green checks. | decided by the owner | 2026-11-22 | `.github/workflows/ci.yml`; branch protection is a repository setting |
| 9 | Permission rules: documented commands are allowed; force pushes, pushes to the default branch, merges, releases and reads of secrets are denied; edits to CI, agent configuration and Loop files ask first. | decided by the owner | 2026-11-22 | `.claude/settings.json` |
| 10 | Open decisions on tickets are settled with the ticket's stated default; where a ticket states none, the conservative option is taken and flagged in the issue. | decided by the owner | 2026-11-22 | The list below; the issues themselves |
| 11 | Nothing is installed on the owner's PC for this project: Python is already there. No third-party Python package is used, in the application or in tests. | recommended by the orchestrator, following the plan (Python 3 standard-library server, bundled assets) | 2026-11-24 | `CLAUDE.md` "Commands", `.github/workflows/ci.yml` |
| 12 | The ten UI rules in `docs/ui-quality.md` are binding, and the `ui-ux-pro-max` and `unslop` skills are installed in the repository and used for UI work and for copy. | decided by the owner | 2026-11-22 | `docs/ui-quality.md`, `.claude/skills/` |
| 13 | Visual system: the Pipenzo Flow look tokens. | decided by the owner | 2026-11-23 | `cut_planner/static/tokens.css`, `docs/design-tokens.md` |
| 14 | Token rules 14-D1 to 14-D4. | 14-D1 use of yellow decided by the owner; how it is drawn, and 14-D2 to 14-D4, recommended by the orchestrator and adopted under the owner's delegation of 2026-11-23 | 2026-11-23 | `docs/design-tokens.md`; applied in UI tickets |

## Open ticket decisions settled by default (entry 10)

The plan leaves these open. Each is a recommendation by the orchestrator, adopted under entry 10 on 2026-11-24, and holds unless the owner changes it in the issue. None blocks a ticket.

| Issue | Decision | Default |
|---|---|---|
| all | Python versions | 3.12 and 3.13 in CI; the code uses nothing newer than 3.12. |
| all | Units and thresholds | Whole millimetres, one kerf per project, project-level offcut thresholds, as the plan proposes. |
| #2 | Address and data directory | `http://127.0.0.1:8770`, changed with `--port`; `--data-dir`, default `./data` (git-ignored). |
| #3 | Work budget | 200,000 tested leaf and orientation pairs per attempt; more gives the budget status and keeps the last complete result. |
| #3 | Planner version | An integer in the package, raised by any change that can alter a layout. |
| #5 | Selected attempt | Stored with the hash of the input snapshot and the planner version; a mismatch asks for a new plan. |
| #6 | Print | Browser print with CSS page rules; no PDF library. The paper size is A4. |
| #6 | Formula escaping | A leading `=`, `+`, `-`, `@`, tab or carriage return in a label gets a leading apostrophe in the CSV. |
| none | Licence | MIT, already in the repository (`LICENSE`). No ticket changes it. |

## Program decisions (owner, 2026-11-24)

The owner accepted the goal and each suggestion below. They apply from the phase they name; the rules of `CLAUDE.md` hold for phase 1 as written.

| Decision | Implemented in |
|---|---|
| The repository has a program goal above phase 1: a cutting and nesting engine with proofs, in 6 phases. | Program issue #31 |
| Irregular shapes, joinery and claims of an optimum are outside the first release. Suggested: they enter with phases 3, 4 and 6, each with its proof. | Program issue #31 |
| Machine control stays outside every phase. Suggested: cut order is printed for people and no machine code is written. | Program issue #31 |
| Plain Python may be too slow for the exact phases. Suggested: choose the engine language at the start of phase 2 and keep Python for the server and the checker. | Program issue #31 |
| Public instances must be reusable. Suggested: the phase checks the licence first and fetches a pinned version outside the repository. | Program issue #31 |
