# Loop Configuration: Issue Triage

The Loop files follow the scaffold of `npx --yes @cobusgreyling/loop@0.2.0 init . --pattern issue-triage --tool claude` ([Loop Engineering](https://github.com/cobusgreyling/loop-engineering), MIT), copied on 2026-11-24 from a prepared repository of the same owner and adapted here. The generated `.grok/` and `.codex/` variants were removed; this repository uses the Claude Code files only. The scaffold generated no workflow file, and none was added.

## Active Loops

| Pattern | Cadence | Status | Command |
|---------|---------|--------|---------|
| Issue Triage | Manual, on request | L1 report-only | `/issue-triage` in a Claude Code session at the repository root |

## Operating level: L1 report-only

- The loop reads open issues with `gh issue list` and `gh issue view` and rewrites `issue-triage-state.md`. That file and `loop-run-log.md` are the only files it may change.
- It never applies labels, comments, closes or edits issues, edits source or tests, commits, pushes, opens pull requests or merges.
- No scheduler is configured. Do not wrap the skill in `/loop`, a cron entry, a scheduled task or a GitHub workflow. The "2h" cadence in the generated skill text describes the upstream pattern, not this repository.
- `loop doctor` prints its own readiness score. That score describes the scaffold, not the operating level. The operating level here stays L1 until the owner changes this file.

## Ticket work is not a loop run

Implementing a ticket is not part of this loop. The owner starts it with `/next-ticket`; it is governed by `CLAUDE.md` (section "Delivery workflow"), the `implement-ticket` playbook, the review gate hook, CI and branch protection. The loop stays at L1: report-only and unscheduled.

## Next manual triage run

From the repository root, in a new Claude Code session:

```text
/loop-constraints
/issue-triage
```

Headless equivalent:

```text
claude -p "Run the loop-constraints skill, then the issue-triage skill in L1 report-only mode. Update issue-triage-state.md and append one entry to loop-run-log.md. Make no GitHub writes and change no other file."
```

Review the diff of `issue-triage-state.md` afterwards. Committing it is a human decision.

## Health checks

```text
npx --yes @cobusgreyling/loop@0.2.0 doctor .
npx --yes @cobusgreyling/loop@0.2.0 status .
```

Doctor exit codes: 0 healthy, 1 warnings, 2 blocked. Both commands fetch the package from npm, so they need a network connection. The product itself never does.

## Human Gates

- Priority assignment (P0, P1): human only.
- Anything touching the request guards (127.0.0.1 bind, origin and content-type checks, size caps), the kerf, grain and split rules, the search order and ranking, the planner version, the independence of the verifier, the area balance, the print and export gate, the project schema version, new dependencies or external requests: always escalate. These are described in [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md); no code exists yet.
- Anything that would add a dependency, a package download, an external request or a listener other than 127.0.0.1: always escalate. The product is offline by design.
- Duplicate closure: human confirms.
- Stale issue closure: human confirms.
- Any change to this file, `loop-budget.md` or `loop-constraints.md`: human only.

## Verifier

`.claude/agents/loop-verifier.md` is the checker for a later maker/checker level. It is limited to `Read, Grep, Glob`, so it cannot run the tests itself and must answer `ESCALATE_HUMAN` when a verdict depends on a test run. It has no role at L1 because the loop proposes no changes.

## Budget

- Sub-agent spawns per run: 0 at L1.
- See `loop-budget.md`.

## MCP

MCP is not required for this pattern. The triage skill reads issues through the `gh` command line.

## Recorded doctor result

Run on 2026-11-24 (Windows 11): `doctor .` printed `Ready: 100/100 L2` and `Status: HEALTHY (exit 0)`.

## Doctor suggestions that were not adopted here

`loop doctor` suggests a `docs/safety.md`, issue and pull request templates, workflows, and a patterns registry. The denylists and merge policy are in `loop-constraints.md`. A scheduled workflow would be the scheduler that L1 excludes, so none is added. Templates and the pull request workflow belong to the delivery setup of the repository, not to the loop. An L1 run edits two report files only, so it needs no worktree of its own.

## Links

- Pattern: https://github.com/cobusgreyling/loop-engineering/blob/main/patterns/issue-triage.md
- Repository instructions: [CLAUDE.md](CLAUDE.md)
- Backlog source of truth: [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md) and the epic issue (#1)
