---
name: next-ticket
description: Owner-started driver that takes one ticket of epic #1 from the queue to a ready pull request, using the implement-ticket playbook. Starting it is the owner's go signal; it never merges.
argument-hint: "[issue number]"
disable-model-invocation: true
---

# Next ticket

Only the owner starts this skill (`/next-ticket` or `/next-ticket <issue number>`). Starting it is the go signal for one ticket, and counts as the owner's request, for this run, to push the ticket branch and open the pull request. Nothing starts it automatically and nothing schedules it: this repository is used to train AI models, so every run needs the owner's go.

Run exactly one ticket, then stop. Never merge, never tag or release, never start another run.

Epic: #1 (`jortega0033/workshop-cut-list-planner`); every pull request says `Part of epic #1`. Dependency order: the order of the parents, then of their sub-issues (the table "Tickets, in dependency order" in the epic is the source; if it differs, the table wins). A ticket labelled `tracking` or with open sub-issues is a container and is never worked; list a parent's sub-issues with `gh api repos/jortega0033/workshop-cut-list-planner/issues/<n>/sub_issues`. The epic #1 itself is such a container.

## Labels

`status:ready`, `status:blocked`, `status:in-progress`, `needs-decision`, `tracking`. If a label does not exist yet, do not create it: say so in the run summary and use the epic's dependency table instead.

## Steps

1. **Refresh the queue.** `gh issue list --state open --label status:blocked`. (a) Blockers: for a parent use "Needs" in the epic table; for a sub-issue use the "Needs:" line at the top of its body plus any native blocked-by links. If no blocker source is found for a ticket, leave it blocked and report it; never treat a missing source as "no blockers". If every blocker is closed and the ticket carries no `needs-decision`, change its label to `status:ready`. (b) Closing: only a parent that has at least one sub-issue, and whose sub-issues are all closed, is closed (a `tracking` ticket without sub-issues stays open), with a comment naming them. A leaf ticket is never closed this way. Do not touch anything else.
2. **Pick the ticket.** Only leaf tickets are work: skip `tracking` tickets and any ticket with open sub-issues. The order is the order of the parents in the epic table, then the order of the sub-issues inside each parent. With an issue number: use it, and stop with a reason if it is closed, `status:blocked`, `status:in-progress` or `needs-decision`; if it is a `tracking` ticket or has open sub-issues, refuse it and list its open sub-issues. Without one: the first `status:ready` leaf ticket in that order that is not `status:in-progress` and not `needs-decision`. If none qualifies, say why (for example "the next ticket is `needs-decision`") and stop.
3. **Claim it.** Label it `status:in-progress` (`gh issue edit <n> --add-label status:in-progress --remove-label status:ready`).
4. **Branch in a fresh worktree**, as `CLAUDE.md` "Git workflow" says: `git fetch origin`, then `git worktree add .claude/worktrees/<n> -b <n>-<short-slug> origin/main` (`.claude/worktrees/` is git-ignored and inside the project, so edits there do not prompt as outside-folder edits; the branch name is `<issue-number>-<short-slug>` as in `CLAUDE.md`). One branch and one pull request per issue. Never work on `main` and never touch the owner's checkout.
5. **Run the playbook** [`.claude/skills/implement-ticket/SKILL.md`](../implement-ticket/SKILL.md) for the ticket, in the new worktree. It runs the roles, both gates, the evidence list of `CLAUDE.md` and the UI and writing checks. Before calling Code Reviewer and Reality Checker (they have no shell), write the diff and the local evidence to `.claude/state/review/` in the worktree (`git diff --stat origin/main...HEAD`, `git diff origin/main...HEAD`, the check outputs) and name those files in each request.
6. **Open the pull request** only after Code Reviewer and Reality Checker both ran on the current diff and passed. Push the branch (`git push -u origin <branch>`; the review gate hook blocks `gh pr create` and `gh pr ready` until both gates have run after the last code edit) and open it as a draft (`gh pr create --draft`) from `.github/pull_request_template.md` with `Closes #<n>` only when every acceptance criterion is met. If this is the last open sub-issue of a parent, the description also says `Closes #<parent>`. A criterion that needs a person (marked manual in the ticket) is done as far as an agent can, with the evidence, and the rest is listed under "Owner checks". Never leave a gate open to open the pull request.
7. **Wait for CI without polling.** After the push, bind the pull request to the session if the app offers it, then end the turn with the line "Draft pull request #N is waiting for CI". Do not loop, sleep or watch. When woken (a CI event, or the owner says "continue"), read `gh pr checks <n>` once. Red: fix, re-run the local checks and both gates on the new diff, push, and end the turn again with the same line. Still running: end the turn again with the same line. Green on the current diff (every job of every workflow, and no step skipped that should have run): mark the pull request ready (`gh pr ready`); green CI is checked here, not by Reality Checker.
8. **Report on the issue.** Comment on the issue with the pull request link, the CI run link and result, and anything not verified. Keep the label `status:in-progress` until the owner merges.
9. **Stop.** Print one summary: ticket, branch, pull request, CI result, open questions. The owner merges.

## Stop and say so

A ticket that needs an owner decision, a change to `CLAUDE.md`, `AGENTS.md`, `LOOP.md` or CI beyond what the ticket's own scope names, a change to agent configuration or the Loop files, a new dependency, or anything under the human gates in `LOOP.md`: stop, label it `needs-decision` if the label exists, comment what is needed, and end the run.
