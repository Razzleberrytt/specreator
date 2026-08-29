# Spec Creator v0.11 — Iteration, Continuation & Execution Efficiency Discovery

**Status:** UNFROZEN DISCOVERY. No implementation authority.  
**Parent:** v0.10 Protocol MVP — PROMOTED AS EXPERIMENTAL under DEC-0032.  
**Roadmap decision:** DEC-0033.

## Why this cycle exists

v0.10 proved deterministic end-to-end orchestration on three governed fixtures, but its retrospective identified continuation friction: implicit validation profiles, multi-step sealing, reconstructed immutable boundaries, uneven test-runnability of release snapshots, and the need for lower-entropy handoffs.

A second opportunity is now made explicit: Spec Creator already knows how to compile dependency-safe tasks and conservative parallel-safe pairs, but it does not yet treat **time-to-verified-implementation** as a first-class design target. The next architecture should join continuation hygiene with execution efficiency rather than optimizing either in isolation.

## Discovery objective

Design the smallest governed successor that lets a fresh receiver determine the exact next legal action from the package alone **and** lets the package expose an evidence-backed execution architecture that minimizes avoidable serial work, reconstruction, repeated context, and reruns.

## Candidate capability areas

### A. Machine-readable lifecycle / continuation state
A checkpoint should identify current version, release state, immutable boundary, blockers, validation profile, next legal action, stop condition, required artifacts, and hashes without chat reconstruction.

### B. Execution-efficiency analysis
Given a compiled task graph and governed execution context, derive:

- critical path;
- dependency provenance and challengeable edges;
- useful parallel workstreams;
- execution waves;
- conflict/integration boundaries;
- minimum context contracts;
- cache/reuse opportunities;
- safe speculative/preparatory work;
- retry boundaries;
- bottleneck/load-balance warnings.

### C. Atomic release/checkpoint operations
Explore fail-closed freeze/seal/checkpoint transactions so partially completed release operations cannot create ambiguous authority.

### D. Explicit validation profiles
A continuation package should declare exactly which validator/test/evaluator profile applies to the current action rather than requiring reconstruction from historical scripts.

### E. Evidence ingestion and immutable registry
Explore automatic evidence intake plus an explicit immutable-artifact registry so a receiver can distinguish mutable discovery artifacts from frozen/history-bound artifacts mechanically.

## Candidate requirements — NOT FROZEN

1. A fresh receiving context can infer the next legal action from package artifacts alone.
2. Every sequential execution dependency has machine-readable provenance.
3. The system identifies the critical path and all safely parallelizable ready work without introducing unsafe parallelization.
4. Workstream outputs have explicit integration contracts and conflict/write scopes.
5. Context supplied to a workstream is explainably minimal under declared selectors.
6. Reusable valid artifacts have identity and invalidation conditions.
7. Failure of one workstream does not require unrelated successful work to rerun unless a declared dependency invalidates it.
8. Speculative/preparatory work is clearly non-authoritative until prerequisites resolve.
9. Efficiency gains are paired with quality guardrails and cannot be claimed from structural proxies alone when real execution evidence is required.
10. v0.10 and all earlier frozen/failed history remain immutable.

## Candidate metrics — NOT PREREGISTERED

Structural candidates:

- unsupported dependency edges = 0;
- unsafe parallelizations = 0;
- critical-path identification exactness = 1.0 on governed fixtures;
- execution-wave determinism = 1.0;
- workstream integration-contract completeness = 1.0;
- continuation-state field completeness = 1.0;
- hidden/manual state reconstruction = 0;
- immutable-boundary classification errors = 0.

Empirical candidates requiring actual execution trials:

- time-to-verified-implementation versus a declared serial/control plan;
- wall-clock critical-path reduction;
- corrective-prompt rate;
- repeated-work / retry amplification;
- context volume per verified work unit;
- integration conflict / architectural rework rate;
- cache/reuse effectiveness.

No threshold is frozen by this document. Baselines, denominators, fixtures, environments, and anti-gaming guardrails must be defined before any such metric can authorize promotion.

## Non-goals for v0.11 discovery

- no autonomous multi-agent scheduler yet;
- no provider-specific concurrency assumptions;
- no arbitrary task fragmentation to inflate parallelism;
- no weakening of v0.08 dependency/conflict semantics;
- no retroactive reinterpretation of v0.10 evidence;
- no implementation or freeze merely because the design direction is approved.

## Forward capability captured during discovery — OUTSIDE v0.11 promotion scope

A product-direction insight captured after the preregistration draft is **Existing-Solution Intelligence & Synthesis (ESIS)**: when useful, Spec Creator should discover a broad/diverse landscape of existing implementations and knowledge, qualify/deduplicate sources, compare capabilities, extract patterns and failure lessons, analyze compatibility/license/provenance, and synthesize a coherent reference architecture before implementation planning.

This insight is preserved in `docs/EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md`, `versions/v0.11/SPEC-CREATOR-PRODUCT-DIRECTION-v0.11-DRAFT.md`, and the successor roadmap. It is deliberately **not** inserted into the already-prepared v0.11 promotion metrics or candidate schemas. Implementation is scheduled for the post-alpha Existing-Solution & Repository Intelligence series.

## Design rule

The target is **maximum useful parallelism**, not maximum workstream count. A decomposition is worse if coordination, duplicated context, integration cost, or verification burden outweighs saved critical-path time.

## Discovery checkpoint reached

The preregistration-draft evaluation design, candidate schemas, structural/lifecycle fixtures, matched control/optimized empirical protocol, immutable boundary, and validation profile now exist. Provider/runtime-dependent efficiency evidence is intentionally shadow-only for v0.11; structural correctness and deterministic continuation remain promotion-blocking.

## Next discovery action

Obtain a genuinely separate-context prefreeze review under `versions/v0.11/INDEPENDENT-PREFREEZE-REVIEW-PROTOCOL.md`. Do not freeze or implement until that evidence is ingested and any defects are resolved without weakening preregistered targets.


## Review-driven preregistration hardening

Independent prefreeze review 001 returned `NOT_READY` even though all structural DAG fixtures recomputed correctly. The review exposed oracle and denominator weaknesses rather than an execution-architecture failure. v0.11 discovery therefore hardened preregistration with machine-readable provenance derivation, machine-readable lifecycle transition semantics, exact metric universes, source-task-based integration coverage, exact parent/regression/hash snapshots, and self-contained validation bootstrap. See `DEFECT-RESOLUTION-001.json`.

No freeze authority follows from these repairs; independent re-review remains mandatory.
