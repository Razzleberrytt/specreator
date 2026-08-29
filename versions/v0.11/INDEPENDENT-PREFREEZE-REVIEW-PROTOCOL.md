# v0.11 Independent Prefreeze Review Protocol

**Purpose:** obtain genuinely separate-context review evidence before any v0.11 freeze.

The receiving context must not implement, freeze, promote, repair, or redesign v0.11. It reviews the preregistration draft and returns evidence only.

## Review obligations

1. Confirm v0.10 and earlier frozen/failed history is treated as immutable.
2. Validate both candidate JSON Schemas as Draft 2020-12 schemas.
3. Validate every candidate fixture parses and is internally coherent.
4. Recompute expected critical paths/waves/conflict behavior for the structural fixtures without trusting the authored expectations.
5. Check that every sequential dependency has a permitted provenance class and every declared parallel wave is dependency/conflict safe.
6. Check lifecycle fixtures can recover one exact next legal action with zero hidden chat state.
7. Audit every denominator and threshold in `EVALUATION-DESIGN.json` for ambiguity or gameability.
8. Confirm empirical wall-clock/context/rework evidence is shadow-only for v0.11 and cannot authorize a speed claim.
9. Confirm serial/control and optimized comparisons require identical obligation hashes and mandatory quality gates.
10. Return PASS/FAIL per obligation, defects with exact artifact locations, and a final recommendation: `READY_FOR_FREEZE_PREPARATION` or `NOT_READY`.

## Evidence package minimum

Return machine-readable JSON plus a concise Markdown report. Include receiver identifier, UTC time, source package SHA-256, reviewed artifact hashes, computations performed, findings, and recommendation. Missing evidence is not PASS.


## Re-review requirements after independent review 001

Independent review 001 returned `NOT_READY` with `DEF-011-REVIEW-001` through `DEF-011-REVIEW-006`. The next receiver must independently regress all six defects rather than accepting `DEFECT-RESOLUTION-001.json` as proof.

The receiver must additionally:

- derive every explicit dependency provenance class from task semantics using `DEPENDENCY-PROVENANCE-RULES.candidate.json`, then derive conflict-serialization edges mechanically;
- derive lifecycle actions from `LIFECYCLE-TRANSITION-RULES.candidate.json` without consulting `expected_next_action` until comparison;
- use only exact universes in `EVALUATION-UNIVERSES.json`;
- confirm the integration denominator is the fixed 23-source-task universe and cannot shrink when workstreams are omitted;
- confirm the parent suite universe contains exactly 155 pytest node IDs, active-regression universe exactly 24 IDs, and frozen-parent hash universe exactly all 1120 v0.10 manifest entries;
- execute the declared validation commands from a clean extraction with no undeclared environment setup; and
- treat the prior review and repair record as claims/evidence to audit, not authority.

## Re-review requirements after independent re-review 002

Independent re-review 002 returned `NOT_READY`. It independently marked `DEF-011-REVIEW-001` through `DEF-011-REVIEW-006` PASS and found one new blocker, `DEF-011-REREVIEW-001`.

The next receiver must independently:

- recompute the protected-parent set as the union of all 1120 `versions/v0.10/MANIFEST.json` `content_hashes` keys plus the explicit protected release manifests, with deduplication;
- read `SUCCESSOR-OWNERSHIP-UNIVERSE.json` only as the candidate claim, then enumerate the actual clean-extracted shipped package paths and independently test whether every non-parent path appears exactly once in that successor universe;
- include root `PACKAGE-MANIFEST.json` in the package-wide classification audit;
- report exact protected-parent, mutable-successor, overlap, stale-member, and unclassified counts;
- explicitly report the class of `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md`, `docs/EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md`, the v0.11 roadmap/prompt/self-improvement drafts, and all v0.11 evaluation evidence files;
- require zero overlaps and zero unclassified/stale successor members;
- verify all 1120 v0.10 manifest-bound hashes remain exact;
- confirm all 15 metric targets remain unchanged; and
- treat `DEFECT-RESOLUTION-002.json` as a claim to audit, not proof.

A PASS on `DEF-011-REREVIEW-001` requires independent whole-package recomputation, not merely successful execution of the authoritative preflight script.
