# Spec Creator v0.08 — Task Compiler (Unfrozen Draft)

**Status:** Evidence-derived draft; no implementation is authorized until a v0.08 evaluation corpus, success criteria, and frozen release contract are preregistered.
**Parent:** v0.07 (PROMOTED AS EXPERIMENTAL)

## Objective

Compile an approved, machine-checkable specification into a deterministic dependency-safe task graph. The compiler must refuse to produce an implementation-ready graph when owner decisions are still represented by `ask_now`, `defer_dependency`, or `defer_budget` actions in the supplied v0.07 discovery plan.

The compiler does not invent product intent, implementation architecture, interfaces, or acceptance criteria. It converts already-governed requirements and traceability evidence into bounded work units while preserving source references.

## Proposed deterministic output

Each compiled task record should contain:

- a compilation-scoped deterministic task identifier;
- source requirement IDs;
- owned write scopes;
- required read/reference scopes;
- prerequisite task IDs;
- produced artifacts;
- verification/test IDs;
- gate IDs;
- conflict-zone identifiers;
- parallelization eligibility;
- a numeric complexity score and the factors that produced it;
- provenance linking every derived field to source specification or traceability evidence.

Task ordering should be a deterministic topological order with stable lexical tie-breaking only among dependency-independent tasks.

## Proposed atomicity model

A task is compilable only when all of these proposed bounds hold:

1. it owns at most three source requirements;
2. it owns at most two top-level write scopes unless an approved requirement explicitly spans more;
3. its complexity score is at most 10;
4. its verification references are non-empty;
5. every critical source requirement has at least one compiled task and one downstream test/gate reference;
6. tasks sharing a write scope are assigned the same conflict zone and are not marked parallel-safe;
7. prerequisite edges form a directed acyclic graph;
8. every task dependency is attributable to a source traceability edge, artifact producer/consumer relation, or explicit ordering constraint.

Proposed complexity score:

`3 * source_requirement_count + 2 * write_scope_count + prerequisite_count + verification_reference_count`

If a source requirement cannot fit within the proposed bounds without inventing an architectural split, compilation must emit a structured `needs_spec_refinement` diagnostic instead of creating an oversized task.

## Proposed compilation blockers

Compilation should fail with a structured diagnostic when any of these conditions is present:

- the source specification fails the active linter;
- the supplied traceability graph fails validation;
- any critical requirement lacks a complete Requirement → Feature → Task/Test/Gate trace foundation needed for compilation;
- the v0.07 discovery plan contains an owner-decision action that has not been converted into governed specification evidence;
- task dependency edges contain a cycle;
- a required interface, write scope, produced artifact, verification reference, or gate cannot be traced to source evidence.

## Proposed requirements

### REQ-008-001
Requirement: Compile governed requirements into deterministic task records with source requirements, write scopes, dependencies, verification references, gates, complexity, and provenance.
Critical: true
Acceptance: Every accepted benchmark project produces exactly the preregistered task records and deterministic ordering.
Verify: tests/test_task_compiler.py::test_frozen_task_graphs

### REQ-008-002
Requirement: Refuse implementation-ready compilation when the supplied discovery plan still contains owner-decision actions `ask_now`, `defer_dependency`, or `defer_budget`.
Critical: true
Acceptance: Every frozen owner-decision blocker case returns a nonzero compilation result and identifies each blocking source action.
Verify: tests/test_task_compiler.py::test_owner_decisions_block_compilation

### REQ-008-003
Requirement: Derive prerequisite edges only from validated traceability relationships, explicit ordering constraints, or artifact producer/consumer relationships.
Critical: true
Acceptance: Every frozen dependency edge has one machine-readable provenance reference and no benchmark case contains an invented dependency.
Verify: tests/test_task_compiler.py::test_dependency_provenance

### REQ-008-004
Requirement: Reject task graphs containing a dependency cycle.
Critical: true
Acceptance: Every frozen cycle case is rejected with the exact cycle node set and no valid acyclic case is rejected for a cycle.
Verify: tests/test_task_compiler.py::test_cycle_rejection

### REQ-008-005
Requirement: Enforce the preregistered atomicity bounds of at most three source requirements, at most two top-level write scopes unless explicitly authorized, complexity score at most 10, and at least one verification reference.
Critical: true
Acceptance: Every frozen boundary case is classified exactly as compilable or needs_spec_refinement and reports the controlling bound.
Verify: tests/test_task_compiler.py::test_atomicity_bounds

### REQ-008-006
Requirement: Detect shared write scopes as conflict zones and prohibit parallel-safe classification for tasks in the same conflict zone.
Critical: true
Acceptance: Frozen conflict cases identify every shared write-scope pair and no conflicting pair is marked parallel-safe.
Verify: tests/test_task_compiler.py::test_conflict_zones

### REQ-008-007
Requirement: Mark tasks parallel-safe only when they have no dependency path between them and no shared write-scope conflict zone.
Critical: true
Acceptance: Every frozen parallelization label matches the preregistered result.
Verify: tests/test_task_compiler.py::test_parallelization_rules

### REQ-008-008
Requirement: Preserve complete critical requirement coverage from source requirement through compiled task to verification and release gate.
Critical: true
Acceptance: Critical compilation coverage is 100% on every accepted frozen benchmark project and missing coverage blocks compilation.
Verify: tests/test_task_compiler.py::test_critical_coverage

### REQ-008-009
Requirement: Expose task compilation and task-graph validation through deterministic Python API and CLI JSON output.
Critical: true
Acceptance: Repeated runs over byte-identical inputs produce byte-equivalent normalized outputs and malformed inputs return nonzero status with structured diagnostics.
Verify: tests/test_task_compiler_cli.py::test_task_compiler_cli

### REQ-008-010
Requirement: Preserve all active validator, linter, traceability, ambiguity, discovery, history, ledger, and package regressions.
Critical: true
Acceptance: The sealed v0.07 parent suite and every active regression pass unchanged before v0.08 promotion.
Verify: evaluation/independent_verifier_v0.08.py

### REQ-008-011
Requirement: Evaluate task compilation on hash-locked development and held-out graph projects that include valid, cyclic, oversized, conflict-zone, owner-decision-blocked, and parallel-safe cases.
Critical: true
Acceptance: The frozen evaluator reports every preregistered denominator, exact task/dependency labels, false-positive counts, and missing-data status without imputing absent evidence.
Verify: tests/test_task_compiler_evaluator.py::test_frozen_task_compiler_corpus

### REQ-008-012
Requirement: Require role-separated verification, reconciled metrics, rollback evidence, and manifest-last package sealing before any v0.08 promotion decision.
Critical: true
Acceptance: Every frozen mandatory gate has explicit evidence and the final extracted package validates with zero errors and zero warnings.
Verify: evaluation/independent_verifier_v0.08.py

## Proposed evaluation emphasis

The v0.08 benchmark should measure exact task/dependency compilation and critical coverage while using false-positive task splitting, oversized-task escape, dependency-cycle escape, invented dependency count, write-conflict escape, and owner-decision escape as guardrails. A held-out partition must be hash-locked before implementation.

A useful task compiler is not the compiler that creates the most tasks. It is the compiler that creates the smallest dependency-safe work graph justified by the approved specification without erasing product decisions or manufacturing architecture.

## Non-goals

- no prompt compiler;
- no code generation;
- no automatic architectural redesign;
- no multi-agent scheduler;
- no optimization for maximum parallelism at the expense of write conflicts or dependency correctness;
- no full promotion claim from same-cycle synthetic evidence alone.
