# Spec Creator v0.11 Independent Prefreeze Review

**Receiver:** `receiver:gpt-5.6-sol:independent-prefreeze-review:v0.11`  
**Reviewed at:** `2026-08-24T21:02:16Z`  
**Source package SHA-256:** `9dc0a6e9de984653413cc1f86951ed407d62f8a3cf07490f2a74129e01a4de3d`  
**Scope:** evidence-only independent review; no v0.11 implementation, repair, freeze, promotion, or redesign was performed.

## Result

The structural fixtures recompute cleanly: all six authored wave schedules are dependency/conflict safe; every supplied critical-path expectation matches independent computation; both candidate schemas are valid Draft 2020-12; v0.10 manifest integrity is 1120/1120; and the inherited/current suite passes 155/155.

Freeze preparation is blocked by preregistration testability/governance gaps: dependency provenance is not independently oracle-testable from the execution corpus, lifecycle fixture actions are not independently derivable from package transition semantics, and several evaluation denominators are ambiguous or gameable. The validation profile also contains a command that fails from a clean extracted package unless undeclared `PYTHONPATH=src` state is supplied.

## Obligations

1. **PASS** — v0.10 and earlier frozen/failed history is treated as immutable. Independent v0.10 manifest check: 1120/1120 content hashes match; all historical version files are transitively bound except the manifest file itself.
2. **PASS** — Both candidate JSON Schemas are valid Draft 2020-12 schemas.
3. **PASS** — All 10 fixture records parse and are locally coherent; execution DAGs have valid references, positive weights, and no cycles.
4. **PASS** — Structural critical paths, waves, conflict behavior, speculative overlap, bottleneck, and retry preservation were independently recomputed; every authored structural expectation that is present matches.
5. **FAIL** — Declared waves are safe, but the 21 explicit fixture dependency edges have no machine-readable provenance class, so provenance correctness cannot be independently confirmed.
6. **FAIL** — Lifecycle fixture actions are not independently derivable from package transition rules, and the exact declared validation command requires undeclared environment bootstrap state.
7. **FAIL** — The evaluation design contains ambiguous/gameable denominators: critical-path eligibility, emission-dependent integration completeness, and three pass-rate guardrails without exact denominators.
8. **PASS** — Empirical wall-clock/context/rework evidence is explicitly shadow-only and cannot authorize a v0.11 speed claim.
9. **PASS** — Serial/control and optimized comparisons explicitly require identical obligation_set_hash values and identical mandatory quality-gate sets.
10. **PASS** — The returned package includes machine-readable evidence, concise Markdown, per-obligation PASS/FAIL, exact defect locations, hashes, computations, findings, and an allowed recommendation.

## Independent structural recomputation

- `EXEC-011-001-LINEAR` — waves `[['A'], ['B'], ['C']]`; critical path(s) `[['A', 'B', 'C']]`; critical work `6`; declared-wave safety issues: 0.
- `EXEC-011-002-DIAMOND` — waves `[['A'], ['B', 'C'], ['D']]`; critical path(s) `[['A', 'B', 'D'], ['A', 'C', 'D']]`; critical work `5`; declared-wave safety issues: 0.
- `EXEC-011-003-CONFLICT` — waves `[['A'], ['B'], ['C']]`; critical path(s) `[['A', 'B', 'C']]`; critical work `5`; declared-wave safety issues: 0.
- `EXEC-011-004-LOAD-BALANCE` — waves `[['A'], ['B', 'C', 'D'], ['E']]`; critical path(s) `[['A', 'B', 'E']]`; critical work `10`; declared-wave safety issues: 0.
- `EXEC-011-005-SPECULATIVE` — waves `[['DECIDE', 'PREP'], ['IMPLEMENT'], ['VERIFY']]`; critical path(s) `[['DECIDE', 'IMPLEMENT', 'VERIFY']]`; critical work `8`; declared-wave safety issues: 0.
- `EXEC-011-006-RETRY-ISOLATION` — waves `[['A'], ['B', 'C'], ['D']]`; critical path(s) `[['A', 'B', 'D'], ['A', 'C', 'D']]`; critical work `5`; declared-wave safety issues: 0.

`EXEC-011-003-CONFLICT` independently requires conflict-serialization edge `A -> B`, yielding `A-B-C` at 5 work units. For fixtures without authored critical-path fields, the independent results are `DECIDE-IMPLEMENT-VERIFY` at 8 work units and tied `A-B-D` / `A-C-D` paths at 5 work units.

## Blocking defects

- **DEF-011-REVIEW-001** — Execution fixtures do not carry expected machine-readable provenance classes for declared dependency edges.  
  Location: `versions/v0.11/candidate-fixtures/execution-architecture-corpus.jsonl:1-6 tasks[*].deps`; `versions/v0.11/EVALUATION-DESIGN.json:55-56`
- **DEF-011-REVIEW-002** — Lifecycle fixture next actions are answer keys rather than independently derivable package semantics.  
  Location: `versions/v0.11/candidate-fixtures/lifecycle-continuation-corpus.jsonl:1-4`; `versions/v0.11/candidate-schemas/lifecycle-checkpoint-v1.candidate.schema.json:/properties/release_state`; `versions/v0.11/candidate-schemas/lifecycle-checkpoint-v1.candidate.schema.json:/properties/next_legal_action`
- **DEF-011-REVIEW-003** — Critical-path metric denominator has an undefined selection-sensitive predicate.  
  Location: `versions/v0.11/EVALUATION-DESIGN.json:29-31`
- **DEF-011-REVIEW-004** — Integration-contract completeness uses an emission-dependent denominator.  
  Location: `versions/v0.11/EVALUATION-DESIGN.json:44-46`
- **DEF-011-REVIEW-005** — Three guardrail pass-rate targets lack exact denominators.  
  Location: `versions/v0.11/EVALUATION-DESIGN.json:71-80`
- **DEF-011-REVIEW-006** — The declared validation profile is not self-executable as written from the extracted package.  
  Location: `versions/v0.11/LIFECYCLE-CHECKPOINT-DRAFT.json:31-36`

## Additional evidence

- Candidate schemas: Draft 2020-12 valid; draft lifecycle checkpoint: zero schema errors.
- Candidate fixtures: 10/10 parse; no graph cycle, unknown dependency, nonpositive weight, or declared-wave safety violation.
- v0.10 manifest: **1120 checked, 0 missing, 0 mismatched**; frozen contract canonical hash recomputes exactly.
- `python -m pytest -q`: **155 passed**.
- Exact declared CLI validation command fails with `ModuleNotFoundError`; the same command with `PYTHONPATH=src` passes 0 errors / 0 warnings.
- Empirical wall-clock/context/rework metrics are explicitly shadow-only and non-promotional; general speedup claims are prohibited.
- Serial/control and optimized comparisons explicitly require identical `obligation_set_hash` and mandatory quality-gate sets.

## Final recommendation

NOT_READY
