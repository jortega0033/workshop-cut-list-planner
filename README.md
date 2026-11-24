# Workshop Cut-List Planner

An offline panel layout tool with stock, grain, kerf and printable cutting plans.

This repository contains the plan for the first implementation epic and a runnable scaffold. There is no product behaviour yet.

- [Product requirements](docs/PROJECT-PLAN.md#product-requirements)
- [Technical design](docs/PROJECT-PLAN.md#technical-design)
- [Epic and implementation tickets](https://github.com/jortega0033/workshop-cut-list-planner/issues)

The first plan of phase 1 said 14–22 engineering hours. Its open tickets, with tests and review, add up to 53 to 79 hours; the whole program is larger and is described below. All figures are estimates.

Licensed under the [MIT License](LICENSE).

## Program goal

Turn the planner into an exact cutting engine: own linear and integer optimiser with certificates, proven layouts for every guillotine rule, nesting of irregular shapes in exact geometry, planning over weeks with reusable offcuts, and furniture models that produce the parts, with no solver, geometry or document library.

The program is planned ([#31](https://github.com/jortega0033/workshop-cut-list-planner/issues/31)). Phase 1 is the current epic [#1](https://github.com/jortega0033/workshop-cut-list-planner/issues/1) and the only phase with tickets.

**Score.** Share of public cutting and packing benchmark instances solved to a proven optimum or within a stated gap, with every layout and bound accepted by a separate exact checker.

| Phase | Content | Hours (rough) | Issue |
|---|---|---|---|
| 1 | The current epic and its tickets | 53 to 79 | [#1](https://github.com/jortega0033/workshop-cut-list-planner/issues/1) |
| 2 | Bounds and column generation | 140 to 240 | [#32](https://github.com/jortega0033/workshop-cut-list-planner/issues/32) |
| 3 | Exact layouts | 160 to 280 | [#33](https://github.com/jortega0033/workshop-cut-list-planner/issues/33) |
| 4 | Irregular shapes | 160 to 280 | [#34](https://github.com/jortega0033/workshop-cut-list-planner/issues/34) |
| 5 | Orders over weeks | 110 to 190 | [#35](https://github.com/jortega0033/workshop-cut-list-planner/issues/35) |
| 6 | Furniture models and drawings | 140 to 240 | [#36](https://github.com/jortega0033/workshop-cut-list-planner/issues/36) |

About 760 to 1310 engineer hours in total: rough estimates, not measurements. The numbers in the score and the finish lines are targets until a run shows them. Only phase 1 has tickets to work; the sub-issues of a later phase are written when it starts. No single session is expected to reach the end.
