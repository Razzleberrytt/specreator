# Spec Creator v0.11.1 — Governed Retry: Iteration, Continuation & Execution Efficiency

**Status:** UNFROZEN PREREGISTRATION RETRY CANDIDATE.  
**Executable parent:** v0.10 Protocol MVP — PROMOTED AS EXPERIMENTAL under DEC-0032.  
**Failed predecessor:** v0.11 / `REL-0.11-FROZEN-001` — preserved, implementation blocked by `DEF-011-POSTFREEZE-001`.  
**Retry decision:** `versions/v0.11.1/DEC-0034.json`.

## Objective

Retry the v0.11 product target without rewriting its failed frozen history. v0.11.1 must deliver package-only lifecycle authority plus deterministic execution architecture while closing the ownership/classification defect that made the v0.11 frozen checkpoint unsatisfiable.

The retry preserves every v0.11 structural behavior target and adds a stricter preregistered rule: all known freeze-time, implementation, test, verification, shadow, release-snapshot, and final-package outputs must already fall under immutable, disjoint path selectors before freeze.

## Retry invariants

1. **No failed-history rewrite.** Every byte captured in `FAILED-PREDECESSOR-v0.11-BASELINE.json` is immutable.
2. **No parent rewrite.** All 1120 v0.10 manifest-bound hashes remain exact; the protected-parent selector remains 1121 unique paths including protected manifests.
3. **No target weakening.** The original five primary and ten guardrail v0.11 promotion metrics retain their targets and denominator semantics. v0.11.1 adds a sixteenth promotion-authoritative metric for prospective output classification closure.
4. **Isolated implementation.** New implementation code may be written only under `src/spec_creator/v0111/`; new tests only under `tests/v0111/`; retry evaluation evidence only under the preregistered evaluation filename prefixes; all retry governance/review/freeze/release artifacts live under `versions/v0.11.1/`.
5. **Selector authority, snapshot evidence.** The frozen successor path selectors are authoritative for later legal outputs. A current-member snapshot is audit evidence only and is not a closed future enumeration.
6. **Independent freeze gate.** This planning context may not self-certify the candidate. A genuinely separate receiving context must independently review the retry preregistration before any freeze transaction.

## Functional requirements

### REQ-0111-001 — Package-only lifecycle state
Provide a machine-readable lifecycle checkpoint conforming to the inherited candidate schema. It carries candidate/parent version, release state, immutable boundary, blockers, exact validation profile, required artifacts, stop condition, and exactly one next legal action.

### REQ-0111-002 — Deterministic lifecycle transition derivation
Derive the next legal action from release state plus blocker transition tokens using the retry-bound transition rules. Authored expected answers are comparison evidence only.

### REQ-0111-003 — Dependency provenance and effective DAG
Every explicit sequential dependency has exactly one permitted machine-derivable provenance class. Write/conflict serialization edges are derived mechanically and included in the effective DAG. Unsupported, ambiguous, or provenance-free edges are invalid.

### REQ-0111-004 — Critical path and deterministic execution waves
Compute the complete set of all maximum-total-work critical paths over the effective DAG and deterministic dependency/conflict-safe execution waves. Tied maximum paths require exact set equality.

### REQ-0111-005 — Maximum useful parallelism and integration contracts
Optimize useful parallelism, not task count. Every emitted workstream identifies canonical source-task IDs and supplies explicit context, cache, retry, integration, and verification contracts. Integration completeness remains measured over the fixed 23-source-task universe.

### REQ-0111-006 — Retry isolation and reusable work
A failed workstream invalidates itself and declared dependents only. Unrelated successful work is preserved unless an explicit invalidation rule requires rerun. Reusable artifacts have identity inputs and invalidation conditions.

### REQ-0111-007 — Speculative work remains non-authoritative
Preparatory/speculative work may overlap latency only when it cannot acquire executable authority before prerequisites resolve. Speculative outputs remain distinguishable from authoritative outputs.

### REQ-0111-008 — Explicit validation and immutable-boundary mechanics
Current lifecycle state declares an exact validation profile. Every shipped path must classify exactly once after immutable precedence. v0.10 and earlier protected bytes plus the failed-v0.11 retry baseline remain immutable. Retry-owned paths must match exactly one frozen retry-successor selector.

### REQ-0111-009 — Prospective output closure
Before freeze, every member of `candidate-fixtures/ownership-prospective-paths.json` must classify exactly once as `MUTABLE_RETRY_SUCCESSOR`, while no immutable path may match a retry-successor selector. This regression is rerun after freeze, implementation, verification, release snapshot, and final package sealing.

### REQ-0111-010 — Parent and regression preservation
All exact 155 parent pytest node IDs, all 24 inherited active regressions, retry-local REG-0025, and all 1120 v0.10 manifest-bound hashes remain mandatory guardrails. Missing/skipped/malformed/unreconciled evidence is unavailable, never PASS.

### REQ-0111-011 — Evidence and claim governance
All 16 promotion-authoritative metrics use the preregistered universes, numerator rules, targets, and anti-gaming rules. Wall-clock/context/rework/cache metrics remain shadow-only and cannot authorize a general speed claim.

## Frozen-after-review implementation layout contract

If independently approved and frozen, implementation is constrained to these namespaces:

- `src/spec_creator/v0111/` — retry implementation library;
- `tests/v0111/` — retry-specific tests and executable REG-0025 coverage;
- `evaluation/v0111-*`, `evaluation/pytest-v0.11.1-*`, `evaluation/workspace-validation-v0.11.1-*` — retry evidence;
- `versions/v0.11.1/` — governance, review, freeze, verification, release snapshot, manifests, retrospective, rollback;
- root `PACKAGE-MANIFEST.json` — regenerated manifest-last.

No existing v0.10 or failed-v0.11 path may be edited to integrate the retry.

## Evaluation and promotion

The semantic schemas, lifecycle fixtures, execution fixtures, dependency-provenance rules, structural targets, and shadow trial shape are inherited from the failed v0.11 target and re-preregistered here. The retry adds only stronger ownership closure and regression memory.

Promotion ceiling remains **PROMOTED AS EXPERIMENTAL**. Final promotion still requires a genuinely independent evaluator actor, complete frozen-denominator reconciliation, exact immutable-history integrity, clean-extraction validation, and zero critical-gate bypass.

## Non-goals

- no autonomous multi-agent scheduler;
- no provider-specific concurrency assumptions;
- no arbitrary task fragmentation to inflate parallelism;
- no weakening of v0.08 dependency/conflict semantics;
- no rewriting v0.11 failure evidence;
- no general speedup claim from synthetic or incomparable evidence;
- no ESIS/top-5 implementation in this retry.

## Forward direction

The preserved Existing-Solution Intelligence & Synthesis / Top-5 Repository Prototype Synthesis direction remains outside v0.11.1 promotion obligations and continues on the later governed roadmap.
