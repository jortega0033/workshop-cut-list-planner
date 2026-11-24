# Loop Budget: workshop-cut-list-planner

> Primary loop: **Issue Triage** (scaffolded by loop-init). Manual runs only; no scheduler is configured.

## Daily limits

| Loop | Max runs/day | Max tokens/day | Max sub-agent spawns/run |
|------|--------------|----------------|--------------------------|
| Issue Triage | 2 (manual) | 80k | 0 (L1) |

## On budget exceed

1. Stop. There is no scheduler to pause; do not start another run that day.
2. Append the event to `loop-run-log.md`.
3. Tell the human in the run output and under "Needs human" in `issue-triage-state.md`.

## Kill switch

- Flag: a line reading `loop-pause-all` under "Alerts This Period" below. When present, every loop skill exits immediately.
- Only a human removes the flag.

## Alerts This Period

- (none)

## Estimate spend (optional)

The scaffold points at a separate helper package, `@cobusgreyling/loop-cost`. It is not part of the L1 setup, no loop skill calls it, and it was not run or inspected during preparation. Check its version and licence on npm before running it.
