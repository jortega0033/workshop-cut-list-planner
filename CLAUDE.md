# CLAUDE.md

Working instructions for this repository. Read this file first, then the documents it links to. It does not repeat them.

## What this is

An offline planner for a furniture maker or small workshop: enter sheets and rectangular parts, get two deterministic layouts, compare sheets, reusable offcuts and kerf loss, see why a part does not fit, save the project and print a dimensioned plan. Python 3.12 standard library and SQLite, `127.0.0.1` only, whole millimetres, fictional projects.

**Only the scaffold exists; there is no product behaviour yet.** The repository holds the plan, the delivery tooling, the backlog in epic #1 and a runnable scaffold (package, smoke tests, CI). Commands marked planned below do not work yet. Do not describe a planned thing as working, and do not claim a passing product baseline beyond the smoke tests.

## Sources of truth

| Topic | Document |
|---|---|
| Product scope, design, fixtures with expected values | [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md) |
| Planned module map, freeze points, planned versus implemented | [docs/architecture.md](docs/architecture.md) |
| Backlog | Epic issue #1 and its child tickets on GitHub. The epic's table is authoritative for order, dependencies and estimates; tickets state their own owner-decision defaults. |
| Loop setup and its limits | [LOOP.md](LOOP.md), [loop-constraints.md](loop-constraints.md) |
| Project subagents, origin and local changes | [.claude/agency-agents/README.md](.claude/agency-agents/README.md) |
| Ticket workflow and the step at which each role runs | [.claude/skills/implement-ticket/SKILL.md](.claude/skills/implement-ticket/SKILL.md), section "Agent roles" below |
| How a ticket goes from the queue to a ready pull request, who may do what | "Delivery workflow" below |
| UI and copy rules, design tokens | [docs/ui-quality.md](docs/ui-quality.md), [docs/design-tokens.md](docs/design-tokens.md) |
| Decisions the owner made, with dates | [docs/owner-decisions.md](docs/owner-decisions.md) |

The plan wins for product design; the epic and tickets win for order and scope. A ticket that changes a contract fixes the plan in the same pull request.

## Stack and constraints

- Python 3.12, **standard library only**, in the application and in the tests. No package download in any launch, fixture or test step.
- Serves bundled HTML, CSS, JavaScript and SVG and a small JSON API on `127.0.0.1`. No build step.
- Axis-aligned rectangles, whole millimetres, guillotine splits, finite stock.
- Offline: same-origin assets and data only. Fictional projects only.
- Machine control, operating procedures, joinery, irregular shapes and any claim of an optimal layout are outside the first release.
- A runtime version change, a dependency, an external request or a non-loopback listener needs the owner's approval first, not a pull request.

## Commands

Python 3.12 or 3.13. No install step is needed.

| Purpose | Command | Status |
|---|---|---|
| Tests | `python -m unittest discover -s tests` | real (scaffold) |
| Help and version | `python -m cut_planner --help` | real (scaffold) |
| Run the app | `python -m cut_planner serve --port 8770 --data-dir ./data` | planned: #2 |
| Plan a project file | `python -m cut_planner plan <project.json>` | planned: #3 |

## Architecture boundaries

The planned module map is in [docs/architecture.md](docs/architecture.md). Invariants every change must keep (the plan is the source):

- Input validation, layout generation, verification, storage and browser views stay separate. The browser sends inputs and shows verified snapshots.
- The verifier shares no code with the layout search and counts from the original request. Only the verifier can admit a layout for print and export.
- All sizes, areas and totals are integers. No floating point in geometry or accounting.
- Coordinates start at the top left of the usable rectangle, which is the sheet minus its four trim margins.
- A split takes the kerf once along one axis. An exact match needs no split; otherwise at least the full kerf must remain. Zero-area strips and children are omitted.
- Search order is fixed by the plan: leaves by sheet, Y, X, height, width and leaf ID; unturned before turned; preferred split first; existing sheets before a new one. The same input and planner version give identical canonical data.
- `NO_FIT`, `NOT_PLACED` and the budget status stay distinct. A heuristic result is never described as optimal or as proof that no layout exists.
- A 90-degree turn swaps the sides and the grain axis. A directional part needs a stock axis equal to its turned axis.
- For every sheet: stock = trim + parts + kerf + remaining. Reusable area is counted from single remaining leaves that meet both thresholds and is never added to the balance again.
- A layout is complete only when every requested copy appears exactly once. An incomplete or rejected layout can be inspected but never printed as final or exported.
- Limits are checked before work: 20 stock types, 50 sheets, 200 copies, 1 to 10,000 mm, kerf 0 to 20 mm, 128 KiB per import, and the search budget.
- An import is previewed and either replaces or appends as a whole; one bad row rejects it and names the row. A rejected draft leaves the saved project as it was.
- Revision and project data change in one transaction guarded by the submitted revision. A conflict keeps the draft and offers reload or save as copy. An older response never replaces a newer plan.
- The server binds `127.0.0.1`, accepts writes only from its own origin with a JSON content type and a bounded body, and never builds a path, SQL or markup from input.
- Labels are rendered as text in HTML and SVG. CSV exports escape leading formula characters, as documented.
- Every sheet drawing has a text summary and an inventory table. Focus goes to the first error, states are text as well as colour, and everything works by keyboard.

## Git workflow

- `main` is the default branch. Work on one branch per ticket: `<issue-number>-<short-slug>`. Never commit to `main`.
- Small commits with imperative subjects and a type prefix (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Order for every ticket: local evidence, Code Reviewer, Reality Checker, then a draft pull request that says `Part of epic #1` and `Closes #<ticket>`, then CI on that draft, then `gh pr ready` only when CI is green.
- Do not push or open a pull request unless the owner asked in the current session; starting `/next-ticket` is that request for one ticket. Only the owner merges and releases. Do not push to `main`, force-push, or merge your own pull request.
- Never commit a data folder (`data/`), `.env*`, or build output.
- Do not change `.claude/agents/`, `LOOP.md`, `loop-constraints.md` or `loop-budget.md` as part of a feature ticket.
- Open owner decisions on a ticket are settled with the ticket's stated default. Where a ticket states none, take the conservative option and say so in the pull request.

## Evidence before a ticket is called done

Paste real output into the pull request; never summarise a run you did not make.

1. For each acceptance criterion of the issue: the name of the test that proves it, or the exact step and what was observed.
2. The full output of `python -m unittest discover -s tests` locally, and the link to the green CI run on the draft pull request (Linux and Windows, Python 3.12 and 3.13).
3. For a layout change: the fixture from the plan, the coordinates, the leaves and the area balance, computed without the search.
4. For a verifier change: the hand-made tree and the named rejection.
5. For a UI or print change: the Chrome version, the steps and what was observed, and that the page made no external request.
6. `git status` shows no stray files, and no dependency, external URL or non-loopback listener was added.
7. Anything not verified, said plainly.

## Agent roles

Project subagents are in `.claude/agents/`: eight Agency Agents roles and `loop-verifier`, which belongs to the Loop setup. Each Agency Agents role file starts with a section "In this repository", written for this project. That section and this file override the generic text below it. Sources, licence, local changes and the name collision with a user-level install are in [.claude/agency-agents/README.md](.claude/agency-agents/README.md).

When asked to implement, continue or finish a GitHub issue, follow the playbook [`.claude/skills/implement-ticket/SKILL.md`](.claude/skills/implement-ticket/SKILL.md). Claude Code loads it on its own for ticket work; `/implement-ticket <issue number>` starts it by hand. Delegate to the roles without waiting to be asked: each role's `description` ends with a "Use proactively ..." sentence, which is what makes Claude Code delegate. The playbook gives the exact trigger of each role.

| When | Roles | Access |
|---|---|---|
| Before coding | Software Architect | `Read, Grep, Glob` |
| While coding | Backend Architect, Frontend Developer | can edit |
| After coding, when the trigger matches | Application Security Engineer, Accessibility Auditor | `Read, Grep, Glob` |
| After coding, when the trigger matches | API Tester | can edit |
| Gate on every ticket | Code Reviewer on the full diff, until no material finding is left | `Read, Grep, Glob` |
| Acceptance gate on every ticket, after Code Reviewer | Reality Checker on each acceptance criterion and the recorded evidence, and that CI is configured to run the checks (no CI result is needed yet) | `Read, Grep, Glob` |

- The two gates run on every ticket, whatever its size. A ticket is not called done before both have passed.
- Roles limited to `Read, Grep, Glob` cannot run commands. Give them the diff, the acceptance criteria and whatever command output exists.
- The session or role that wrote a change does not count as its reviewer.
- If a role is missing or cannot be delegated to, the session does the before-coding, while-coding and specialist steps itself and says so. It cannot pass the two gates on its own change: do not push or open the pull request. Stop, report that the gates could not run, and leave the run for the owner. This overrides the playbook's sentence "do that step yourself" for the two gates.
- In the pull request description, list under "Agent roles run" each role that ran, what it was asked and its verdict, and any step done without a role.

## Delivery workflow

How a ticket reaches the owner. Each piece is described in its own file; this part only links them.

- **Start:** the owner runs `/next-ticket` ([`.claude/skills/next-ticket/SKILL.md`](.claude/skills/next-ticket/SKILL.md)); it picks one leaf ticket (never a `tracking` parent or a ticket with open sub-issues; the last sub-issue's pull request also closes the parent), creates the branch and worktree, and runs the playbook [`.claude/skills/implement-ticket/SKILL.md`](.claude/skills/implement-ticket/SKILL.md). Nothing is scheduled.
- **Gate hook:** [`.claude/hooks/role_gate.py`](.claude/hooks/role_gate.py) blocks `gh pr create` and `gh pr ready` until Code Reviewer and Reality Checker ran after the last code edit. `ROLE_GATE=off` in the environment Claude Code is started from switches it off for that session; only the owner does that.
- **Permissions:** [`.claude/settings.json`](.claude/settings.json). Agent configuration edits ask in the main checkout and in ticket worktrees; CI, `CLAUDE.md`, `AGENTS.md` and Loop-file edits ask only in the main checkout; in a ticket worktree they are limited by the playbook's scope rule and reviewed by the owner at merge (shell-made edits are not covered, so a ticket never changes agent configuration); force pushes, pushes to `main`, `gh pr merge`, releases and reads of `.env` are denied.
- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Every job must be green on the current diff before a pull request is marked ready. The agent does not poll: it ends its turn with "Draft pull request #N is waiting for CI" and reads `gh pr checks` once when woken. Reviewers read the diff and evidence from `.claude/state/review/`. An acceptance step that needs a person is listed under "Owner checks" in the pull request.
- **Pull request:** [`.github/pull_request_template.md`](.github/pull_request_template.md). Tickets use [`.github/ISSUE_TEMPLATE/implementation-ticket.md`](.github/ISSUE_TEMPLATE/implementation-ticket.md).
- **Labels:** `status:ready`, `status:blocked`, `status:in-progress`, `needs-decision`, `tracking` (parent container, never worked; its sub-issues are the work items).
- **Changelog:** every ticket pull request adds one line under Unreleased in [CHANGELOG.md](CHANGELOG.md).
- **UI and copy:** [docs/ui-quality.md](docs/ui-quality.md); the `ui-ux-pro-max` and `unslop` skills are in `.claude/skills/`. Colours come from the shared design tokens in `cut_planner/static/tokens.css` ([docs/design-tokens.md](docs/design-tokens.md)); new UI adds no colour literals.
- **Decisions:** [docs/owner-decisions.md](docs/owner-decisions.md). Security reports: [SECURITY.md](SECURITY.md).
- **Merge and release:** only the owner merges and releases ([docs/RELEASING.md](docs/RELEASING.md)). An agent stops at a ready pull request.

## Loop

Issue triage runs at L1: report-only, started by hand, no scheduler, no GitHub writes. See [LOOP.md](LOOP.md).
