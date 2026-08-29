# Spec Creator v0.11 — Iteration, Continuation & Execution Efficiency

**Status:** APPROVED FROZEN-TARGET IMPLEMENTATION SPECIFICATION. Implementation authority begins only when `REL-0.11-FROZEN-001` exists and validates.  
**Parent:** v0.10 Protocol MVP — PROMOTED AS EXPERIMENTAL under DEC-0032.  
**Governance origin:** DEC-0033 plus the independently reviewed v0.11 preregistration artifacts and defect history.

## Objective

Implement the smallest governed successor that lets a fresh receiving context infer the exact next legal action from package artifacts alone and that produces a deterministic, evidence-backed execution architecture designed to minimize avoidable serial work, repeated context, duplicated work, unsafe concurrency, and retry amplification.

v0.11 optimizes **time-to-verified-implementation structurally**, but it must not claim a general real-world speedup from synthetic fixtures or unmatched provider/runtime observations. Provider/runtime-dependent efficiency evidence is mandatory shadow calibration only.

## Frozen requirements

### REQ-011-001 — Package-only lifecycle state
Provide a machine-readable lifecycle checkpoint conforming to the frozen lifecycle-checkpoint candidate schema. It must carry candidate/parent version, release state, immutable boundary, blockers, exact validation profile, required artifacts, stop condition, and exactly one next legal action. A fresh receiver must not need hidden chat reconstruction to determine authority.

### REQ-011-002 — Deterministic lifecycle transition derivation
Derive the next legal action from release state plus blocker transition tokens using the frozen transition rules. Authored expected answers may be used only for comparison, never as the derivation oracle.

### REQ-011-003 — Dependency provenance and effective DAG
Every explicit sequential dependency in an execution architecture must have exactly one permitted machine-derivable provenance class. Write/conflict serialization edges must be derived mechanically and included in the effective DAG. Unsupported, ambiguous, or provenance-free edges are invalid.

### REQ-011-004 — Critical path and deterministic execution waves
Compute the complete set of all maximum-total-work critical paths over the effective DAG and deterministic dependency/conflict-safe execution waves. Tied maximum paths are a set and require exact set equality. Parallelization may never violate dependencies or write/conflict constraints.

### REQ-011-005 — Maximum useful parallelism and integration contracts
Optimize for maximum **useful** parallelism, not maximum task count. Every emitted workstream must identify one or more canonical source-task IDs and provide explicit context, cache, retry, integration, and verification contracts. Integration completeness is measured over the fixed source-task universe, never emitted-workstream count.

### REQ-011-006 — Retry isolation and reusable work
A failed workstream may invalidate itself and declared dependents, but unrelated successful work must be preserved unless an explicit dependency/invalidation rule requires rerun. Reusable artifacts must have identity inputs and invalidation conditions.

### REQ-011-007 — Speculative work is non-authoritative
Preparatory/speculative work may overlap latency only when it cannot acquire executable authority before its prerequisites resolve. Speculative outputs must remain distinguishable from authoritative outputs.

### REQ-011-008 — Explicit validation and immutable-boundary mechanics
Current lifecycle state must declare an exact validation profile. Historical v0.10 and earlier frozen/failed bytes remain immutable. Package-path ownership/classification must be mechanically checkable with zero unclassified, overlapping, or stale members under the applicable frozen rules.

### REQ-011-009 — Parent and regression preservation
All exact 155 parent pytest node IDs, all 24 active regressions, and all 1120 v0.10 manifest-bound hashes remain mandatory guardrails. Missing/skipped/malformed/unreconciled evidence is unavailable, never PASS or zero.

### REQ-011-010 — Evidence and claim governance
All 15 promotion-authoritative structural/guardrail metrics use the frozen universes, numerator rules, and targets. Serial/control and optimized empirical comparisons require identical obligation hashes and mandatory quality-gate sets. Wall-clock/context/rework/cache metrics remain shadow-only for v0.11 and cannot authorize a general speed claim or promotion.

## Frozen execution-architecture contract

The implementation must be capable of emitting objects valid under `candidate-schemas/execution-architecture-v1.candidate.schema.json`. At minimum an architecture contains:

- source task graph identity and obligation-set identity;
- optimization actions with pillar and justification;
- workstreams with non-empty `source_task_ids`;
- dependency objects with provenance and reason;
- estimated work units plus read/write scopes;
- minimum-context selection contracts;
- cache identity/invalidation contracts;
- retry boundaries and preservation semantics;
- integration outputs/consumers/merge rules;
- verification contracts;
- all maximum-work critical paths;
- deterministic execution waves;
- useful-parallelism policy;
- integration points and optional bottleneck warnings;
- deterministic plan hash.

Implementation module/file layout is intentionally not frozen. The behavior and artifacts are.

## Frozen lifecycle contract

The implementation must support the frozen lifecycle states and derive action tokens through `LIFECYCLE-TRANSITION-RULES.candidate.json`. The `FROZEN` state with no open blockers deterministically resolves to `implement_frozen_candidate`.

## Evaluation and promotion

The exact promotion-authoritative metrics, denominators, universes, anti-gaming rules, and missing-data policy are frozen in `EVALUATION-DESIGN.json`, `EVALUATION-UNIVERSES.json`, and `EVALUATION-PLAN.json`.

Promotion ceiling: **PROMOTED AS EXPERIMENTAL**.

Implementation does not self-certify. Final promotion requires a genuinely independent evaluator actor, complete frozen-denominator reconciliation, exact frozen-artifact integrity, package validation from a clean extraction, and zero critical-gate bypass.

## Shadow empirical trial rule

The matched serial/control versus optimized trial protocol remains mandatory shadow evidence. Any observed wall-clock/context/rework/cache differences are descriptive calibration only in v0.11. No general speedup claim is allowed from synthetic structural fixtures or incomparable provider/runtime runs.

## Non-goals

- no autonomous multi-agent scheduler;
- no provider-specific concurrency assumptions;
- no arbitrary task fragmentation to inflate parallelism;
- no weakening of v0.08 dependency/conflict semantics;
- no rewriting frozen or failed historical evidence;
- no promotion based on shadow efficiency observations.

## Forward product direction — not a v0.11 promotion obligation

Existing-Solution Intelligence & Synthesis (ESIS), including the hard default **Top-5 Repository Prototype Synthesis** rule, is preserved as forward product direction. When ESIS becomes applicable in a later governed version, Spec Creator should search broadly, deduplicate/qualify candidates, select exactly five distinct qualified repositories when five exist, and synthesize a coherent prototype from their strongest compatible mechanisms with provenance/license safeguards. A source shortfall must be reported rather than padded with weak repositories.

This ESIS rule is intentionally outside the v0.11 implementation and promotion metrics so it cannot retroactively move the independently reviewed v0.11 goalposts.
