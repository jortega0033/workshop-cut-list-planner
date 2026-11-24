# Workshop Cut-List Planner

An offline planner for laying rectangular parts out on sheet stock, comparing material use, and printing dimensioned plans.

## Product requirements

A DIY furniture maker or small workshop planner needs to turn a batch of rectangular parts into a sheet estimate. A plan must account for usable stock, part orientation, the width occupied by cuts, and offcuts worth retaining. Comparing two valid layouts should show the numbers behind the recommendation.

**First usable slice.** Open an empty project in Chrome, enter one stock type and three part copies, then generate and inspect a dimensioned layout. Save the project, reopen it, and reproduce the same result from the same inputs with the same planner version.

**Primary workflow.** Enter stock and parts manually or import a local parts CSV. Set the sheet margins, kerf, grain rules, and minimum reusable offcut dimensions. Generate two deterministic plans. Compare sheet count, reusable offcut area, and kerf loss. Inspect placements or unplaced parts, select a valid plan, then print a sheet diagram or export its inventory.

**Release scope.**

- Support axis-aligned rectangular parts of integer millimetre dimensions and finite quantities of user-entered sheet types. Copies may turn by 90 degrees only when the part and stock permit that orientation.
- Generate bounded guillotine cut layouts, composed of straight splits across a rectangular region. Zero-area regions are omitted. Preserve part identity and inventory accounting.
- Show incomplete layouts with the exact unplaced parts and their reason. A format error leaves the previous valid project intact.
- Include dimensioned print views and CSV inventories for valid, complete layouts. Mark any incomplete preview in the interface.
- Support offline operation using generated fixtures. The plan is a material layout estimate. Product scope excludes machinery control, physical operation procedures, joinery, irregular shapes, and a claim of globally optimal packing.

**Proposed defaults to confirm.** Use whole millimetres, a single kerf value per project, and an optional grain axis per stock type. Start with project-level reusable offcut thresholds. Workpiece names and examples are fictional. Confirm whether the first user needs another unit or independent thresholds by material before expanding scope.

## Technical design

### Runtime and boundaries

Target a Python 3 standard-library server on loopback and a locally available Chrome browser on Linux. Use a small SQLite database under a configurable data directory, static HTML and JavaScript, CSS print styles, and SVG generated from a validated output. Check Python, SQLite support, and Chrome at setup. Bundle all runtime assets. No network service, account, paid package, or device integration is required.

Keep input validation, layout generation, geometry verification, persistence, and browser views separate. The browser submits description data and displays verified snapshots. Only the verifier can admit a result for print and export. The print output includes real dimensions as labels and a drawn scale indicator. The drawing can scale to fit a page.

### Project contract

A project stores a name, integer revision, kerf in millimetres, the minimum long and short side for a reusable leaf, stock records, and part records. IDs are generated and immutable within a project.

- Stock fields are label, width, height, four separate trim margins, grain axis of X, Y, or none, and available copies. The usable rectangle is the original sheet minus the four margins. Origin for geometry is the top-left of the usable rectangle. Display the margins separately in the original sheet view.
- Part fields are label, width, height, quantity, reference grain axis of X, Y, or none, and rotation permission. Expand quantities in stable part-ID and copy-number order. For a 90-degree turn, swap width and height and transform X grain into Y, or Y into X. A directional part requires a stock axis matching its transformed axis. A part without grain requirement may use any stock axis.
- Proposed caps are 20 stock types, 50 sheets total, 200 expanded parts, dimensions from 1 to 10,000 mm, kerf from 0 to 20 mm, and import size at most 128 KiB. Reject trim values that make a usable dimension zero or less. Reject unsupported units, duplicate IDs, invalid enum values, negative or fractional inputs, and quantities over caps. Use integer arithmetic for all comparisons and area totals.
- Parts CSV uses an explicit UTF-8 template with header `label,width_mm,height_mm,quantity,grain,allow_rotate`. Parse quoted fields using the standard-library CSV reader. Validate every row against the same rules as manual entry, show row-specific errors, and stage rather than commit an import with any error. Provide a preview and explicit replace or append choice against the current draft.

### Layout generation and scoring

Represent each opened sheet by a tree rooted at the usable rectangle. Leaves are an identified part or remaining material. A split partitions one parent into an occupied-side region, a kerf strip, and an offcut-side region along a single axis. Apply kerf once to each nonzero split. When the desired dimension exactly matches the parent along an axis, skip that split. Otherwise require the remaining width or height to be at least the full kerf. Include a kerf strip covering the parent extent perpendicular to the cut. Omit strip and zero-area children when their dimensions are zero. Blade paths and hardware instructions are outside the data model.

For an oriented part at the top-left of a free leaf, test horizontal-first and vertical-first split orders: first isolate the desired height or width, then isolate the other dimension within that subregion. Enforce trim, available inventory and grain checks before considering either order. Enumerate compatible free leaves by sheet copy ID, Y, X, height, width and a stable leaf ID. Choose the first fitting leaf, then the first fitting allowed orientation with unturned first, then the selected split order. Try existing sheets before opening the next available compatible stock copy in stable stock-ID order. Allow an attempt to continue when a part cannot be placed.

Preclassify copies with no fitting legal orientation and split on any empty usable stock as NO_FIT. Keep these copies in the report and exclude them from attempt ordering. Run two release attempts with a fixed horizontal-first preference and use the other split order only when the preferred order fails. Attempt A processes copies by descending area then source order. Attempt B alternates the largest remaining copy with the smallest remaining copy, using source order to break ties within the selected area. Bound search to the specified part, sheet and shape caps. If the search work limit is reached, return a budget status and retain the last complete result on screen.

Distinguish `NO_FIT`, when a part has no legal orientation and split in any empty usable stock type, from `NOT_PLACED`, when available sheets, prior placements, or search ordering prevented placement. A found plan is complete only when every requested copy appears once. Compare attempts lexicographically by more placed copies, fewer opened sheets, larger reusable offcut area, lower kerf area, and a stable attempt order. A heuristic can return an incomplete plan even when another arrangement is possible.

### Independent verification

Accept an attempt only when all the following checks pass. Implement the verifier independently of the nesting decisions and compare counts from the original request.

1. Rebuild every child rectangle from the root and split axis, offset, and kerf. Check that every child is enclosed, sibling areas partition the parent, and there are no duplicate tree nodes or empty leaves. Check each cut strip against the declared kerf.
2. Verify placements against the reconstructed leaves and also check pairwise rectangle intersections of all parts on the sheet. Edge contact is allowed. Verify length, width, orientation, grain, copy uniqueness, and stock count.
3. For each sheet, verify `stock area = trim area + parts area + kerf area + remaining material area`. Reusable offcut area includes only remaining leaves whose long and short sides meet the normalized long and short thresholds. Keep leaves separate because the separating cuts already consumed material. Never add reusable area again to the area balance.
4. Reconcile requested copies with placed and unplaced counts. Require a reason for each unplaced copy. Derive report totals from verified geometry. A mismatch returns a named diagnostic and disallows final export.

### Storage and interface

Persist project names, revisions, validated input JSON, and a selected attempt ID which is scoped to an input snapshot and planner version. Recompute layouts deterministically when opening a saved project. Record schema and planner versions separately. If the saved selection no longer matches the current snapshot or version, reopen the inputs and prompt a fresh plan. Update revision and project data atomically and guard updates with the submitted revision. A conflict preserves the unsaved local draft and offers reload or save-as-copy.

Use project list, stock and parts forms, comparison table, sheets, and print view. Display orientation, offcut usability, diagnostics and incomplete status in text as well as on the diagram. Focus first error on failed submit. Supply field labels, ordered keyboard navigation, accessible text summaries of each sheet, and a layout inventory table alongside SVG. A plan request disables repeated generation while pending. An outdated response never replaces a plan generated from a newer draft.

CSV export uses separate parts and offcuts files with one row per verified leaf or part, stable sheet and copy IDs, dimensions, orientation, and area. The offcut file identifies reusable and other leaves. Escape spreadsheet formula leading characters in user labels on export and document the escaping. Print uses one titled section per sheet, a dimension legend, and the acceptance criteria summary. Invalid or incomplete plans remain inspectable with a missing-part table.

## Original verification fixtures

These are independently calculated expectations for the planned implementation. Browser, print, persistence and export checks are future observations.

### Main comparison

Use one 22 × 14 mm X-grain sheet trimmed by 1 mm on each side. Usable bounds are 20 × 12 mm. Use a 1 mm kerf. Offcuts are reusable when their short side is at least 4 mm and their long side is at least 5 mm. Use parts A-1 and A-2 at 8 × 5 mm and B-1 at 6 × 5 mm, with X grain and rotation off. Coordinates below are relative to the usable sheet.

| Attempt | Placements as (x, y) | Remaining leaves as (width, height) | Parts | Kerf | Remaining | Reusable |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | A-1 (0, 0), A-2 (9, 0), B-1 (0, 6) | (2, 5), (13, 5) | 110 | 55 | 75 | 65 |
| B | A-1 (0, 0), B-1 (9, 0), A-2 (0, 6) | (4, 5), (11, 5) | 110 | 55 | 75 | 75 |

The common trim area is 68 mm². In both attempts, the total is 308 = 68 + 110 + 55 + 75 mm². Each attempt uses one sheet and all three requested copies. Attempt B ranks first because both its remaining leaves meet the threshold. Both row separations consume 20 mm² each. The three width splits consume 5 mm² each. Explicitly check that the second row uses its whole unused 1 mm height as kerf without producing an empty leaf.

### Boundary and independent checks

- Add part C at 21 × 5 mm with X grain. Neither its original size nor a rotated version with grain adjustment can fit the sheet. Report one `NO_FIT` copy, leave the other three placements and area unchanged, and disable final print and export.
- On 6 × 9 mm Y-grain stock with no trim and 1 mm kerf, a 9 × 6 mm part with X grain fits with rotation enabled. It occupies exactly 54 mm² and uses no kerf. With rotation disabled, the same copy is `NO_FIT`.
- On 10 × 8 mm stock with no trim and 2 mm kerf, a 9 × 8 mm no-grain part leaves only 1 mm of width, which cannot sustain a full split. The copy is `NO_FIT`. An exact 10 × 8 mm part needs no split and is valid.
- A verifier harness uses hand-authored trees and placement manifests. Independently reject a changed child offset, intersecting placements, duplicate copy ID, rotated grain mismatch, and one missing square millimetre in the report. Verify reference expectations without calling the search algorithm.
- Reopen a saved main fixture and compare its canonical plan body and selected attempt to the original. Test an edit from a stale tab, retry a failed save, and verify the first revision remains available after a restart. Check both CSV files against verified geometry and inspect preview and print layout in Chrome with external networking blocked.

## Epic · Plan and compare sheet layouts offline

Deliver a workbook that takes a small workshop order from manual or CSV input to a verified, dimensioned layout, with an explanation of unused material and a reproducible project state. A complete release demonstration uses the main comparison and no-fit fixture. Save and reopen the project, print the complete layout, export the inventories, and record what Chrome actually rendered. Total estimated engineering effort is **14–22 hours**, including verification.

**Sequencing.** Land CL-01 before any geometry or storage work. CL-02 delivers the layout contract and first slice. CL-03 and CL-04 can proceed in parallel after CL-02 to independently verify the geometry and make projects durable. CL-05 integrates both lanes. CL-06 runs the offline acceptance sequence and closes the release gate.

### CL-01 · Define projects and validate stock and part input

As a planner, I want a consistent way to enter stock and parts so invalid dimensions cannot become a layout.

**Estimate.** 3–4 hours. **Dependencies.** None.

- **CL-01-A.** A blank project accepts the main fixture and expands A into stable A-1 and A-2 copies in the documented order.
- **CL-01-B.** Validation identifies invalid trim, quantities, dimensions, grain enum, and fractional values at the relevant fields. A rejected draft leaves the saved project intact.
- **CL-01-C.** Contract tests exercise both sides of the part and stock caps. All sample labels and dimensions are original data.

### CL-02 · Generate and compare bounded cut layouts

As a planner, I want two reproducible arrangements and clear placement reasons when a part does not fit.

**Estimate.** 3–5 hours. **Dependencies.** CL-01.

- **CL-02-A.** Both deterministic attempts contain the expected main fixture coordinates and complete copy counts. A second run returns identical canonical data.
- **CL-02-B.** Grain and rotation isolate the correct orientation. The kerf and exact-match fixtures distinguish insufficient gap from no required split.
- **CL-02-C.** Finite stock or search exhaustion produces the stated incomplete or budget outcome with affected copy IDs. A complete plan remains manually inspectable with a local fixture driver.

### CL-03 · Verify layout geometry and material accounting

As a reviewer, I want proof that a proposed layout preserves parts and stock areas before it can be exported.

**Estimate.** 3–5 hours. **Dependencies.** CL-02.

- **CL-03-A.** The independent tree and overlap checks accept both hand-authored complete trees. They reject each named inconsistent geometry case.
- **CL-03-B.** Both attempts reconcile to 308 mm². Attempt A offers 65 mm² of reusable material and B offers 75 mm², so complete plan B ranks first.
- **CL-03-C.** Missing and duplicate copy IDs, stock overuse, and unplaced reason mismatches stop the verified export path and identify the error.

### CL-04 · Save, reopen and import plans safely

As a returning planner, I want to reopen work and replace a parts list only after a clear preview.

**Estimate.** 2–3 hours. **Dependencies.** CL-01 and CL-02.

- **CL-04-A.** Valid fixture CSV imports through the shared validator. A bad row, invalid header, or oversized file identifies why the whole change was rejected.
- **CL-04-B.** Save and restart preserve inputs, revision, and plan choice. Reopen after a planner version change requests a fresh comparison.
- **CL-04-C.** Stale saves return the current revision and preserve uncommitted browser fields. An atomic update changes revision and input together.

### CL-05 · Build accessible comparison, print and export views

As a planner, I want a readable sheet and material inventory to review and print.

**Estimate.** 2–3 hours. **Dependencies.** CL-03 and CL-04.

- **CL-05-A.** Chrome shows the two fixture attempts, their numerically accurate score explanations, and a text table corresponding to the sheet diagram.
- **CL-05-B.** The full workflow is keyboard reachable. Focus lands on validation errors and unplaced reasons remain readable without relying on colour.
- **CL-05-C.** Verified complete plans print with labels and export exact placements and offcuts. Incomplete plans retain the preview and unplaced list while final exports remain unavailable.

### CL-06 · Prove the complete workflow in offline Chrome

As a release reviewer, I want repeatable evidence that we can plan, save, reopen, and deliver the same result locally.

**Estimate.** 1–2 hours. **Dependencies.** CL-05.

- **CL-06-A.** A clean local run with external networking blocked completes the fixture flow and matches independent expected totals.
- **CL-06-B.** A restart, invalid import, and stale-tab save preserve the prior valid data. Export row counts and print labels match the verified inventory.
- **CL-06-C.** Record commands, actual browser and dependency versions, outcomes, and any unrun check. Keep the known heuristic and rendering limits visible in the project readme.
