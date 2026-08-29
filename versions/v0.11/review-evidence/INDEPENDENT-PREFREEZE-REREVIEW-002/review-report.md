# Spec Creator v0.11 Independent Prefreeze Re-review After NOT_READY Repair

**Receiver:** `receiver:gpt-5.6-sol:independent-prefreeze-rereview:v0.11:002`  
**Reviewed at:** `2026-08-24T22:39:25Z`  
**Source package SHA-256:** `af2879fcb3f07ceff1f8c518618ee19cb38634cc56e58ef8b36eefb3a60ec4c7`  
**Scope:** evidence-only independent re-review; no v0.11 implementation, repair, freeze, promotion, or redesign was performed.

## Result

All six defects from independent review 001 are independently regressed as **PASS**. The repaired provenance oracle, lifecycle oracle/bootstrap, six-fixture critical-path denominator, fixed 23-source-task integration denominator, exact 155/24/1120 guardrail universes, and clean-extraction validation profile all hold under recomputation.

A **new blocking defect** remains in the repaired guardrail universe: `immutable_boundary_classification_error_count` targets zero, and `EVALUATION-UNIVERSES.json` says relevant paths matching neither protected-parent nor declared mutable-successor selectors are `UNCLASSIFIED` errors. The mandatory reviewed `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md` is outside both selectors. It was changed after review 001 (prior SHA-256 `24fe09ed6660ea4a9ee06e3b1d63cbecc85ebc68cce91e133db40488127cb4d0`, current `4fe8f0c666a65191ef7ea7ff054eb7e7717897c36c97b9179a7ce4d86cd933ae`) while `IMMUTABILITY-BOUNDARY-DRAFT.json` remained byte-identical. Parent history itself is intact; the defect is the successor-classification universe/registry mismatch.

## Original defect regressions

| Defect | Verdict | Independent result |
|---|---|---|
| DEF-011-REVIEW-001 | **PASS** | 21/21 explicit edges have exactly one semantic provenance match; derived conflict edge is exactly `EXEC-011-003-CONFLICT::A->B`; effective universe 22/22. |
| DEF-011-REVIEW-002 | **PASS** | 4/4 lifecycle fixtures and current checkpoint derive exactly; all three declared validation commands exit 0 from clean extraction with no undeclared setup. |
| DEF-011-REVIEW-003 | **PASS** | Denominator is all 6 fixtures; all maximum-weight path sets match, including both complete two-path ties. |
| DEF-011-REVIEW-004 | **PASS** | Fixed universe is exactly 23 source tasks; output task schema requires non-empty `source_task_ids` and `integration_contract`. |
| DEF-011-REVIEW-005 | **PASS** | Fresh exact universes: 155 pytest node IDs, 24 active regressions, 1120/1120 v0.10 manifest hashes. |
| DEF-011-REVIEW-006 | **PASS** | Exact declared profile is self-executable from clean extraction. |

## Structural recomputation

- `EXEC-011-001-LINEAR`: waves `A | B | C`; critical path `A-B-C`, work 6.
- `EXEC-011-002-DIAMOND`: waves `A | B,C | D`; critical paths `A-B-D` and `A-C-D`, work 5.
- `EXEC-011-003-CONFLICT`: independently derived conflict edge `A->B`; waves `A | B | C`; critical path `A-B-C`, work 5.
- `EXEC-011-004-LOAD-BALANCE`: waves `A | B,C,D | E`; critical path `A-B-E`, work 10.
- `EXEC-011-005-SPECULATIVE`: waves `DECIDE,PREP | IMPLEMENT | VERIFY`; `PREP` remains non-authoritative; escape count 0; critical path `DECIDE-IMPLEMENT-VERIFY`, work 8.
- `EXEC-011-006-RETRY-ISOLATION`: waves `A | B,C | D`; tied critical paths `A-B-D` and `A-C-D`, work 5; failure of B preserves A and C; unrelated rerun count 0.

## Exact command evidence

| Command | Exit | Concise output |
|---|---:|---|
| `python -m pytest -q` | 0 | `155 passed in 12.46s` |
| `PYTHONPATH=src python -m spec_creator.cli validate . --no-package-manifest` | 0 | `PASS: 0 error(s), 0 warning(s)` |
| `python versions/v0.11/tools/preregistration_preflight.py` | 0 | PASS; 2 schemas, 6 execution fixtures, 21+1 edges, 4 lifecycle fixtures, 23 source tasks, 155 tests, 24 regressions, 1120/1120 hashes. |

Supplemental fresh collection produced exactly 155 node IDs in exactly the stored order. All 24 active regression IDs match the active source rows, and each maps to a node ID in the all-passing 155-test collection.

## Metric / anti-gaming audit

The critical-path denominator is exactly all six canonical fixtures with complete all-maximum-path tie truth. Integration completeness is fixed to all 23 canonical source-task keys rather than emitted workstream count. Parent-suite, active-regression, and frozen-parent universes are exact at 155, 24, and 1120 with no subset selector. Missing evidence cannot count as PASS. All 15 metric targets are unchanged from the hash-authenticated review-001 source artifacts; repairs tightened denominators rather than lowering thresholds.

Empirical wall-clock/context/rework evidence remains **shadow-only**: every required shadow metric has `promotion_authoritative=false`, and the trial explicitly forbids a general v0.11 speedup claim. Serial/control and optimized comparisons require identical `obligation_set_hash` and identical mandatory quality-gate sets.

## New blocking defect

### DEF-011-REREVIEW-001 — immutable-boundary selector/classification mismatch

`IMMUTABILITY-BOUNDARY-DRAFT.json` declares only `versions/v0.11/` and `evaluation/v011-` as mutable-successor prefixes. `EVALUATION-UNIVERSES.json` says a relevant path matching neither protected-parent nor mutable-successor selectors is `UNCLASSIFIED` and counts against the zero-error guardrail.

`docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md` is a mandatory reviewed artifact, is not one of the 1120 v0.10 manifest content-hash paths, is not a protected manifest, and matches neither mutable prefix. It also demonstrably changed after review 001; the post-review ESIS validation is timestamped `2026-08-24T22:03:17Z`. A conservative whole-package classification yields 13 unclassified files (12 excluding `PACKAGE-MANIFEST.json`), including multiple explicit v0.11 draft/evaluation artifacts.

This does **not** indicate v0.10 history was mutated—1120/1120 parent hashes still match. It means the newly “exact” immutable-boundary guardrail cannot derive zero classification errors under its own selectors as written. Because this is a promotion guardrail with target 0, freeze preparation remains blocked.

## Review obligations

1. **PASS** — protected parent/history integrity.
2. **PASS** — both candidate schemas are valid Draft 2020-12.
3. **PASS** — all 10 fixture records parse and are coherent.
4. **PASS** — structural waves/paths/conflicts/speculation/retry recompute exactly.
5. **PASS** — dependency provenance and wave safety.
6. **PASS** — lifecycle derivability and clean-extraction validation bootstrap.
7. **FAIL** — residual/new gameability/ambiguity in immutable-boundary classification universe.
8. **PASS** — empirical efficiency evidence is shadow-only.
9. **PASS** — matched obligation hash and mandatory quality gates required.
10. **PASS** — raw machine-readable evidence and report returned.

## Final recommendation

NOT_READY
