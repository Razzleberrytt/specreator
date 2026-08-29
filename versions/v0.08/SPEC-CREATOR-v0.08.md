# Spec Creator v0.08 — Task Compiler

**Status:** Approved specification; implementation is authorized only after the v0.08 schemas, benchmark partitions, evaluation plan, and frozen release contract are hash-locked.
**Parent:** v0.07 (PROMOTED AS EXPERIMENTAL)

## Objective

Compile governed specification evidence into a deterministic dependency-safe task graph without inventing product intent, architecture, interfaces, acceptance criteria, dependencies, or task splits. If existing source task structure cannot satisfy preregistered atomicity bounds, emit `needs_spec_refinement` rather than manufacturing a decomposition.

A supplied v0.07 discovery plan containing `ask_now`, `defer_dependency`, or `defer_budget` is a project-level implementation-readiness blocker. The compiler may report the blocking actions, but it must not emit a ready task graph until those actions are replaced by governed specification evidence.

## Normalized compilation input

v0.08 compiles a versioned machine-readable project IR rather than attempting a second natural-language parser. The IR contains the approved specification text, the validated v0.05 traceability graph, the v0.07 discovery plan, source-task metadata for write/read scopes and produced/consumed artifacts, and explicit ordering constraints with source references. Requirement membership, tests, and gates are derived from traceability edges rather than copied from task metadata.

Source task definitions are immutable compilation evidence. Execution progress is represented separately as append-only task execution events tied to the compiled task-graph hash.

## Deterministic output

Each compiled task record contains a compilation-scoped deterministic identifier, source task ID, source requirement IDs, owned write scopes, required read scopes, produced/consumed artifacts, prerequisite compiled task IDs, verification/test IDs, gate IDs, conflict-zone IDs, pairwise `parallel_with` eligibility, complexity score/factors, and machine-readable provenance for every derived field.

Task ordering is a deterministic topological order with stable lexical tie-breaking among dependency-independent source tasks. Dependency edges may arise only from validated traceability `precedes` edges, explicit ordering constraints, or unique artifact producer/consumer relationships.

## Atomicity model

A task is compilable only when all of these bounds hold:

1. at most three source requirements;
2. at most two declared top-level write scopes unless a non-empty governed wide-scope authorization reference is supplied;
3. complexity score at most 10;
4. at least one verification reference;
5. every critical source requirement reaches at least one compiled task, test, and release gate;
6. tasks sharing a write scope receive the same deterministic conflict zone and are never listed as parallel with one another;
7. prerequisite edges form a directed acyclic graph;
8. every prerequisite edge has trace, artifact, or explicit-order provenance.

Complexity score is frozen as:

`3 * source_requirement_count + 2 * write_scope_count + prerequisite_count + verification_reference_count`

If a source task violates an atomicity bound, v0.08 emits `needs_spec_refinement` and does not invent a split.

## Event-sourced task execution state

Compiled task definitions contain no mutable execution status. Task progress uses `task-execution-event-v1` records tied to the immutable compiled graph hash. The initial event is `null -> planned`; allowed transitions are `planned -> ready|cancelled`, `ready -> in_progress|blocked|cancelled`, `in_progress -> blocked|done|cancelled`, and `blocked -> ready|cancelled`. Replay must reject unknown tasks, graph-hash drift, duplicate event IDs, mismatched `from_state`, non-monotonic event time, or invalid transitions.

## Compilation blockers

Compilation fails or refuses readiness when the active linter rejects the source specification, the traceability graph is invalid, critical traceability coverage is incomplete, unresolved owner-decision actions remain, dependency cycles exist, artifact producer identity is ambiguous, source task metadata is missing, or required provenance cannot be derived.

## Requirements

### REQ-008-001
Requirement: Compile governed traceability and source-task evidence into deterministic task records with requirements, scopes, artifacts, dependencies, verification references, gates, complexity, and provenance.
Critical: true
Acceptance: Every accepted frozen benchmark project produces the preregistered normalized task graph and ordering.
Verify: tests/test_task_compiler.py::test_frozen_task_graphs

### REQ-008-002
Requirement: Refuse implementation-ready compilation while any supplied discovery action remains ask_now, defer_dependency, or defer_budget.
Critical: true
Acceptance: Every frozen owner-decision blocker case returns blocked status and identifies every blocking source action.
Verify: tests/test_task_compiler.py::test_owner_decisions_block_compilation

### REQ-008-003
Requirement: Derive prerequisite edges only from traceability precedes edges, explicit ordering constraints, or unique artifact producer-consumer relationships.
Critical: true
Acceptance: Every frozen dependency edge has exact machine-readable provenance and invented dependency count is zero.
Verify: tests/test_task_compiler.py::test_dependency_provenance

### REQ-008-004
Requirement: Reject combined prerequisite graphs containing a dependency cycle and report the exact cycle source-task set.
Critical: true
Acceptance: Every frozen cycle case is rejected with the preregistered cycle node set and no acyclic case is rejected for a cycle.
Verify: tests/test_task_compiler.py::test_cycle_rejection

### REQ-008-005
Requirement: Enforce the frozen source-requirement, write-scope, complexity, and verification atomicity bounds without inventing task splits.
Critical: true
Acceptance: Every frozen boundary case is classified exactly as compiled or needs_spec_refinement and reports every controlling bound.
Failure: Return needs_spec_refinement with the violated bound codes; do not emit a ready task graph.
Verify: tests/test_task_compiler.py::test_atomicity_bounds

### REQ-008-006
Requirement: Detect shared write scopes as deterministic conflict zones and prevent conflicting task pairs from parallel eligibility.
Critical: true
Acceptance: Every frozen conflict case identifies every shared write scope and unsafe parallelization count is zero.
Failure: Treat any unresolved shared write-scope relationship as a compilation blocker rather than marking the pair parallel.
Verify: tests/test_task_compiler.py::test_conflict_zones

### REQ-008-007
Requirement: Compute pairwise parallel eligibility only when no dependency path exists in either direction and no shared write-scope conflict exists.
Critical: true
Acceptance: Every frozen parallel_with list exactly matches preregistration.
Failure: Omit the pair from parallel_with whenever dependency or write-scope safety cannot be proven.
Verify: tests/test_task_compiler.py::test_parallelization_rules

### REQ-008-008
Requirement: Preserve complete critical requirement coverage from source requirement through compiled task to verification and release gate.
Critical: true
Acceptance: Critical compilation coverage is 100 percent on accepted cases and missing critical coverage blocks compilation.
Verify: tests/test_task_compiler.py::test_critical_coverage

### REQ-008-009
Requirement: Expose compilation and compiled-task-graph validation through deterministic Python API and CLI JSON output.
Critical: true
Acceptance: Byte-identical inputs produce byte-equivalent normalized outputs and malformed inputs return nonzero status with structured diagnostics.
Verify: tests/test_task_compiler_cli.py::test_task_compiler_cli

### REQ-008-010
Requirement: Preserve all active validator, linter, traceability, ambiguity, discovery, history, ledger, and package regressions from the sealed parent.
Critical: true
Acceptance: The exact v0.07 parent suite and every active regression pass before promotion.
Verify: evaluation/independent_verifier_v0.08.py

### REQ-008-011
Requirement: Evaluate task compilation on hash-locked development and held-out projects spanning valid, dependent, conflicting, owner-blocked, oversized, cyclic, and parent-invalid cases.
Critical: true
Acceptance: The evaluator reports every frozen denominator, exact accepted graph, negative classification, dependency label, and missing-data state without imputation.
Verify: tests/test_task_compiler_evaluator.py::test_frozen_task_compiler_corpus

### REQ-008-012
Requirement: Require role-separated verification, reconciled metrics, rollback evidence, historical snapshots, and manifest-last sealing before promotion.
Critical: true
Acceptance: Every frozen mandatory gate has explicit evidence and the final extracted package validates with zero errors and warnings.
Verify: evaluation/independent_verifier_v0.08.py

### REQ-008-013
Requirement: Keep compiled task definitions immutable and derive execution status only by replaying append-only task execution events bound to the compiled graph hash.
Critical: true
Acceptance: Every frozen valid execution stream replays exactly and every invalid transition, duplicate event ID, graph-hash drift, unknown task, from-state mismatch, or time reversal is rejected.
Verify: tests/test_task_execution.py::test_frozen_execution_corpus

## Non-goals

- no prompt compiler;
- no code generation;
- no automatic architecture redesign;
- no automatic source-task splitting;
- no multi-agent scheduler;
- no mutation of compiled task definitions to store execution state;
- no optimization for maximum parallelism at the expense of safety;
- no full promotion claim from same-cycle synthetic evidence alone.
