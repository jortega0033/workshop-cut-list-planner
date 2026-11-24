# Releasing

Only the owner releases. Agents never tag, publish or create a GitHub release.

## What a release is here

A release is a Git tag on a commit of `main`, `vMAJOR.MINOR.PATCH`. Nothing is published and nothing is deployed: the product is a Python package run from a clone (`python -m cut_planner serve`). No release exists yet, and none should be tagged before every child ticket of epic #1 is closed.

## Checks before tagging

1. CI is green on the tip of `main` for every job, and no step was skipped that should have run.
2. `python -m unittest discover -s tests` passes on Linux and Windows, and the print check of ticket #7 is recorded.
3. The final verification ticket (#7) has recorded its evidence, and its owner checks were done by the owner.
4. `CHANGELOG.md`: move the `Unreleased` entries under a new version heading with the date.

## Tagging

1. In a pull request, update `CHANGELOG.md`; the owner merges it.
2. On the merge commit: `git tag -a vX.Y.Z -m "vX.Y.Z"` and `git push origin vX.Y.Z`.
3. Optional: create a GitHub release from the tag with the changelog section as its text.
