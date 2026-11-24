# Implementer map

Status: **scaffold only; modules are empty shells and no product behaviour exists.** This page maps the boundaries that [PROJECT-PLAN.md](PROJECT-PLAN.md) requires onto a module layout so that parallel tickets do not collide. It adds no requirement; the plan wins where they differ. The names are the orchestrator's proposal, fixed by the scaffold; a ticket that changes one corrects this page in the same pull request.

## Planned module map

| Boundary | Module | Owns | Parent ticket |
|---|---|---|---|
| Project contract | `cut_planner/project.py` | Fields, limits, validation, copy expansion, canonical snapshot | #2 |
| Parts import | `cut_planner/parts_csv.py` | UTF-8 template, row errors, preview, replace or append | #5 |
| Layout search | `cut_planner/layout.py` | Split trees, two attempts, reasons, ranking, work budget | #3 |
| Verifier | `cut_planner/verify.py` | Independent rebuild, overlap, grain, kerf and area checks | #4 |
| Storage | `cut_planner/store.py` | SQLite projects, revisions, selected attempt, versions | #5 |
| Exports | `cut_planner/exports.py` | Parts and offcuts CSV from verified geometry | #6 |
| HTTP | `cut_planner/server.py` | Loopback bind, request guards, routes, static assets | #2 (input), #5, #6 |
| Browser assets | `cut_planner/static/` | Project list, forms, comparison, sheets in SVG, print | #2 (forms), #6 |
| Hand-made trees | `tests/manifests/` | Independent trees and placements, right and wrong | #4 |

Dependency direction: `server` depends on `store`, `layout`, `verify`, `parts_csv` and `exports`; `exports` on verified results only; `layout`, `verify`, `store` and `parts_csv` on `project`. `verify` imports nothing from `layout`. `project` imports nothing from the package.

## Freeze points

Parallel tickets rely on these shapes. A ticket that changes a frozen shape updates this page and every dependent ticket in the same pull request.

- **Project snapshot and validation error shapes**: ticket #2 writes them down here before #3 and #5 build on them.
- **Layout tree and attempt result shapes**: #3, before #4 and #5 start in parallel.
- **Verified result** read by print and export: #4, before #6.

## What is verified where

Python tests run locally and in CI on Linux and Windows. Browser and print checks are manual in Chrome unless a ticket states a headless run.
