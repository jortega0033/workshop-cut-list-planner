---
name: implement-ticket
description: Playbook for implementing a GitHub issue in this repository from start to pull request, with the project subagents run at fixed steps. Use whenever asked to implement, start, continue or finish a ticket, an issue or an epic child, for example "implement #12" or "work on the next ticket".
argument-hint: "[issue number]"
---

# Implement a ticket

Use this playbook for every implementation ticket in this repository. `CLAUDE.md` holds the commands, the architecture boundaries, the Git workflow and the evidence rules; where this playbook and `CLAUDE.md` differ, `CLAUDE.md` wins.

The project subagents in `.claude/agents/` are part of the work. Delegate to them at the steps below without waiting to be asked. If a step names a role that is not installed, do that step yourself and say so in the pull request.

## Steps

1. **Read the ticket.** `gh issue view <number>` and the epic it belongs to. If it is a `tracking` ticket or has open sub-issues, stop, list its open sub-issues and ask which one to work (or start `/next-ticket`); never work a parent. Check that every prerequisite issue is closed and that no owner decision named in the ticket is still open. If the ticket is blocked, stop and say what blocks it.
2. **Read the rules.** `CLAUDE.md`, then the architecture notes it links to.
3. **Orient and check the approach.** Delegate as the table "Before coding" says. Settle open design questions before writing code. For a ticket that changes the page (`cut_planner/static/`), start with the `ui-ux-pro-max` skill (design-system search for a workshop planning tool, `python .claude/skills/ui-ux-pro-max/scripts/search.py`) and read [`docs/ui-quality.md`](../../../docs/ui-quality.md).
4. **Branch** as the Git workflow in `CLAUDE.md` says. Never work on the default branch. Do not change agent configuration (`.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, `.claude/settings.json`), `LOOP.md` or the Loop files in a ticket. CI (`.github/workflows/`), `CLAUDE.md` and `AGENTS.md` may change only as the ticket's own scope names them. Any other change to them is outside the ticket (stop and ask). In a ticket worktree the `ask` rules cover agent configuration only, not CI, `CLAUDE.md` or `AGENTS.md`, so this scope rule is the control and the owner reviews those files at merge; say in the pull request which file the ticket's scope required.
5. **Implement** inside the ticket's stated scope. Delegate the work to the implementing role that matches the files being changed (table "While coding"). Do not widen scope; note anything else you find as a follow-up.
6. **Test.** Add or change tests for every acceptance criterion and material edge case, then run the checks listed in `CLAUDE.md` that can run here. Run them locally and record each command with its result.
7. **UI and writing check.** For a ticket that changed a screen, check each changed screen against `docs/ui-quality.md`. Run the `unslop` skill over user-facing copy, documentation and the pull request text before the gates, so they judge the final diff.
8. **Changelog.** Add one line to `CHANGELOG.md` under Unreleased, before the gates, so they judge the final diff.
9. **Specialist review.** Run every role in the table "After coding" whose trigger matches the change.
10. **Review gate, always.** Write the diff and the local evidence to `.claude/state/review/` in the worktree (`git diff --stat origin/main...HEAD`, `git diff origin/main...HEAD`, the check outputs) because the reviewers have no shell, and name those files in the request. Run Code Reviewer on the full diff. Fix every material finding, re-run the checks, and have the reviewer look again until no material finding is left.
11. **Acceptance gate, always.** Run Reality Checker with the ticket's acceptance criteria and the local evidence you produced. It checks that a test exists for each criterion and that CI is configured to run it; do not ask it to confirm a CI result, which does not exist yet. A criterion that needs a person and is marked manual in the ticket is done as far as an agent can, and the rest goes under "Owner checks" in the pull request. Do not open the pull request unless it passes.
12. **Hand off.** Capture the evidence `CLAUDE.md` asks for. Then open the pull request as a draft from `.github/pull_request_template.md`, saying `Part of epic #1` and `Closes #<ticket>`, only after both gates passed on the current diff (the gate hook enforces this). If the ticket is the last open sub-issue of a parent, also say `Closes #<parent>`. Wait for CI on the draft without polling: end the turn with "Draft pull request #N is waiting for CI" and read `gh pr checks` once when woken. If it fails, fix, re-run the local checks and both gates, and push. Mark the pull request ready (the hook checks the gates again) only when CI is green on the current diff, and link the run in a comment on the issue. The owner merges; never merge it yourself.

## Roles

### Before coding

| Role | Access | Delegate to it |
|---|---|---|
| Software Architect | read-only reviewer | Before implementing a ticket that adds or changes a module boundary, data model, storage schema, public API or dependency, to check the approach against the architecture notes |

### While coding

| Role | Access | Delegate to it |
|---|---|---|
| Backend Architect | can edit | When a ticket changes server-side code, HTTP routes, validation, persistence or the engine |
| Frontend Developer | can edit | When a ticket changes browser-side code such as pages, components, client state, styling or keyboard interaction |

### After coding

| Role | Access | Delegate to it |
|---|---|---|
| Application Security Engineer | read-only reviewer | After a ticket touches input parsing, file upload or import, sanitization, origin and host checks, or any handling of untrusted data |
| Accessibility Auditor | read-only reviewer | After a ticket changes user-facing UI, keyboard handling, focus order or markup |
| API Tester | can edit | After a ticket adds or changes an HTTP endpoint, status code or request and response contract |

### Gates that run on every ticket

| Role | Access | Delegate to it |
|---|---|---|
| Code Reviewer | read-only reviewer | After implementing or changing code for a ticket, before the work is called done or a pull request is opened |
| Reality Checker | read-only reviewer | As the acceptance gate of every ticket, after Code Reviewer and before the draft pull request is opened, to check each acceptance criterion against evidence that was actually produced |

## Rules

- The session or role that wrote a change does not count as its reviewer.
- Read-only reviewers cannot run commands. Give them the diff, the acceptance criteria and the recorded command output.
- Where a role's general advice (frameworks, dependencies, cloud services) conflicts with `CLAUDE.md`, `CLAUDE.md` wins.
- In the pull request description, add a section "Agent roles run" listing each role that ran, what it was asked and its verdict, and any step you did yourself because a role was missing.
