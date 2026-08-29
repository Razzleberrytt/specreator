# Prompt — Independent v0.11 Prefreeze Re-review After NOT_READY Repair

You are a genuinely separate receiving context performing **one independent prefreeze re-review** for Spec Creator v0.11.

Treat the attached repaired Spec Creator checkpoint ZIP as the sole source of truth for the candidate now under review. Extract and inspect it. Do **not** continue development, implement, freeze, promote, repair, or redesign v0.11.

Independent review 001 returned `NOT_READY` with six blocking defects, `DEF-011-REVIEW-001` through `DEF-011-REVIEW-006`. Independent re-review 002 subsequently confirmed all six PASS but returned `NOT_READY` because of one new blocker, `DEF-011-REREVIEW-001` (immutable-boundary selector/classification mismatch). The authoritative context claims that new defect is repaired. **Do not trust either repair record as proof. Recompute all relevant evidence independently.**

Read at minimum:

- `versions/v0.11/LIFECYCLE-CHECKPOINT-DRAFT.json`
- `versions/v0.11/CONTINUATION.md`
- `versions/v0.11/DISCOVERY.md`
- `versions/v0.11/EVALUATION-DESIGN.json`
- `versions/v0.11/EVALUATION-UNIVERSES.json`
- `versions/v0.11/EXECUTION-TRIAL-PROTOCOL.json`
- `versions/v0.11/IMMUTABILITY-BOUNDARY-DRAFT.json`
- `versions/v0.11/LIFECYCLE-TRANSITION-RULES.candidate.json`
- `versions/v0.11/DEPENDENCY-PROVENANCE-RULES.candidate.json`
- `versions/v0.11/PARENT-SUITE-UNIVERSE.json`
- `versions/v0.11/ACTIVE-REGRESSION-UNIVERSE.json`
- `versions/v0.11/DEFECT-RESOLUTION-001.json`
- `versions/v0.11/DEFECT-RESOLUTION-002.json`
- `versions/v0.11/SUCCESSOR-OWNERSHIP-UNIVERSE.json`
- `versions/v0.11/PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json`
- `versions/v0.11/INDEPENDENT-PREFREEZE-REVIEW-PROTOCOL.md`
- both files under `versions/v0.11/candidate-schemas/`
- both corpora under `versions/v0.11/candidate-fixtures/`
- `versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-001/review-report.md`
- `versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-001/review-evidence.json`
- `versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-REREVIEW-002/review-report.md`
- `versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-REREVIEW-002/review-evidence.json`
- `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md`
- `versions/v0.10/MANIFEST.json`
- `versions/v0.10/FROZEN-RELEASE-CONTRACT.json`

Follow `INDEPENDENT-PREFREEZE-REVIEW-PROTOCOL.md` exactly, including its re-review section.

## Mandatory regression checks for the six prior defects

1. **DEF-011-REVIEW-001 — dependency provenance**  
   For every explicit dependency edge, derive its provenance class from machine-readable task semantics **before** comparing with the authored provenance label. Independently derive conflict-serialization edges. Confirm the exact effective edge universe and report any zero-match, multi-match, unsupported, or misclassified edge.

2. **DEF-011-REVIEW-002 — lifecycle derivability + bootstrap**  
   Apply `LIFECYCLE-TRANSITION-RULES.candidate.json` to each lifecycle fixture using only `state` and `blockers`; do not read `expected_next_action` until after deriving the action. Also derive the current checkpoint action from `release_state` plus OPEN blocker `transition_token` values and compare it with `next_legal_action.action_token`. Execute the validation profile exactly as declared from a clean extraction with no undeclared setup.

3. **DEF-011-REVIEW-003 — critical-path denominator**  
   Confirm the denominator is exactly all six canonical execution fixtures and that tie truth is the complete set of all maximum-weight paths in the effective DAG. Recompute all six independently.

4. **DEF-011-REVIEW-004 — integration denominator**  
   Confirm integration completeness uses the fixed canonical source-task universe, not emitted workstream count. Verify the universe contains exactly 23 source-task keys and that the candidate output schema requires every emitted task/workstream to carry non-empty `source_task_ids` plus an integration contract.

5. **DEF-011-REVIEW-005 — exact guardrail universes**  
   Independently confirm: exactly 155 parent pytest node IDs, exactly 24 active regression IDs, and exactly all 1120 `versions/v0.10/MANIFEST.json` `content_hashes` entries with no subset-selection escape.

6. **DEF-011-REVIEW-006 — self-executable validation profile**  
   From a clean extracted package, run the exact commands in `validation_profile.commands`. Report command, exit code, and concise output. Any undeclared environment manipulation is a failure.


## Mandatory regression check for DEF-011-REREVIEW-001

7. **DEF-011-REREVIEW-001 — package-wide immutable-boundary classification**  
   Independently enumerate the clean-extracted package. Recompute the protected-parent set from all 1120 v0.10 content-hash keys plus explicit protected manifests. Then independently compare every remaining shipped path against `SUCCESSOR-OWNERSHIP-UNIVERSE.json`. Include `PACKAGE-MANIFEST.json`. Report exact class counts, overlaps, stale successor members, and unclassified paths. Explicitly classify `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md` and the other root successor drafts/evaluation files identified by re-review 002. PASS requires zero unclassified paths, zero overlaps, zero stale members, and 1120/1120 frozen-parent hash integrity.

## Additional obligations

- Recompute structural waves, critical paths, conflict behavior, speculative authority behavior, and retry preservation independently.
- Audit every primary/guardrail metric universe, numerator rule, target, missing-data rule, and anti-gaming rule for residual ambiguity or gameability.
- Confirm empirical wall-clock/context/rework evidence remains shadow-only and cannot authorize a v0.11 speed claim.
- Confirm serial/control and optimized comparisons require identical obligation hashes and mandatory quality gates.
- Confirm v0.10 and earlier protected history remains immutable.
- Check that the repairs did not weaken targets merely to make the review pass.
- Report any **new** blocking defect even if all six prior defects are repaired.

Return a ZIP containing raw machine-readable review evidence and a concise Markdown report. Include PASS/FAIL for each original defect regression and each review obligation, exact artifact locations, hashes, computations, command evidence, and final recommendation.

The final recommendation must be exactly one of:

- `READY_FOR_FREEZE_PREPARATION`
- `NOT_READY`
