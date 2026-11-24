## Ticket

Part of epic #1

Closes #

## What changed

## Evidence

Each command and its observed result (pasted output or a CI run link). Python is installed on the owner's PC, so every command runs locally and in CI; record both.

| Command | Result |
|---|---|
| | |

## Owner checks

Acceptance steps that need a person (marked manual in the ticket), with what the agent did as far as it could.

## Agent roles run

| Role | What it was asked | Verdict |
|---|---|---|
| Code Reviewer | | |
| Reality Checker | | |

## Risks and rollback

## Checklist

- [ ] CI is green on the current diff
- [ ] Both gate roles ran after the last code edit
- [ ] Docs, fixtures and README changed in the same pull request where behaviour changed
- [ ] `docs/ui-quality.md` checked for any changed screen or text
- [ ] Copy and pull request text went through the `unslop` skill
- [ ] `CHANGELOG.md` has a line under Unreleased
- [ ] No dependency, external request or non-loopback listener was added
