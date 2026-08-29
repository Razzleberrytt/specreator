# Spec Creator v0.06 — Ambiguity Engine

**Status:** DRAFT successor specification; not frozen; implementation forbidden until release contract freeze  
**Parent:** v0.05 (PROMOTED AS EXPERIMENTAL)

## Objective

Identify implementation-blocking ambiguity before execution, distinguish questions that require an owner decision from gaps already covered by a governed default, and prioritize required questions using specification criticality plus v0.05 traceability impact.

v0.05 demonstrated that syntactically valid references are insufficient unless relationship semantics are executable. v0.06 applies the same principle to ambiguity: a vague warning is insufficient unless the finding identifies its owning requirement/task, classifies whether a decision is required, and yields a reproducible priority.

## Deliberate scope

The first ambiguity engine is deterministic and rule-bounded. It does not claim general natural-language understanding. The release evaluates six preregistered ambiguity families and a clarification-interception proxy on hash-locked micro-projects. Real-project outcome evidence remains a later requirement for promotion beyond experimental.

The six candidate families are documented in the evaluation plan and represented by stable codes `AMB-001` through `AMB-006`.

## Requirements

### REQ-006-001
Requirement: Parse active Markdown requirement/task blocks and produce deterministic structured ambiguity findings with source locations and owning block identifiers.
Critical: true
Acceptance: Every frozen candidate case yields stable code, line, span, block identifier, category, severity, disposition, and decision-needed fields in deterministic order.
Verify: tests/test_ambiguity.py::test_frozen_candidate_detection_and_diagnostics

### REQ-006-002
Requirement: Implement the preregistered ambiguity taxonomy for unresolved alternatives, missing measurable bounds, undefined referents, conflicting constraints, ungoverned assumptions, and unresolved markers.
Critical: true
Acceptance: At least 95% of frozen defect cases contain every preregistered expected ambiguity code and no critical ambiguity case escapes detection.
Verify: tests/test_ambiguity.py::test_frozen_candidate_detection_and_diagnostics

### REQ-006-003
Requirement: Classify each ambiguity candidate as owner_decision, governed_default, or spec_correction and state whether a pre-implementation question is required.
Critical: true
Acceptance: Decision-needed classification accuracy is at least 95% across all frozen labeled candidates; every governed-default candidate emits no question.
Verify: tests/test_ambiguity.py::test_decision_needed_classification

### REQ-006-004
Requirement: Treat an explicit matching Default field or approved DEC governance marker as resolution evidence only for the candidate it governs.
Critical: true
Acceptance: Every frozen resolved case is classified without a required question, while mismatched defaults and unapproved assumptions remain question-required.
Verify: tests/test_ambiguity.py::test_governed_defaults_are_scoped

### REQ-006-005
Requirement: Link each finding to its requirement/task block and, when a valid v0.05 graph is supplied, compute deterministic upstream/downstream impact context for that block.
Critical: true
Acceptance: Frozen graph-backed priority cases report the exact preregistered downstream impact count and reject invalid trace graphs rather than silently ignoring them.
Verify: tests/test_ambiguity.py::test_traceability_impact_context

### REQ-006-006
Requirement: Rank required clarification questions by a declared deterministic score derived from severity, block criticality, and downstream traceability impact.
Critical: true
Acceptance: At least 90% of frozen priority cases select the preregistered top question, with stable tie-breaking by block identifier, code, then line.
Verify: tests/test_ambiguity.py::test_question_priority

### REQ-006-007
Requirement: Generate a bounded question only for findings classified as decision-needed and never generate a question for governed-default candidates.
Critical: true
Acceptance: Frozen question-required candidates produce non-empty deterministic questions; unnecessary-question rate is at most 5% and governed-default question count is zero.
Verify: tests/test_ambiguity.py::test_question_generation_guardrails

### REQ-006-008
Requirement: Measure the preregistered implementation-time clarification interception proxy across frozen evaluation micro-projects without treating missing cases as zero.
Critical: true
Acceptance: At least 80% of preregistered implementation-time clarification triggers are surfaced before implementation, critical ambiguity escape count is zero, and denominators equal the frozen corpus labels.
Verify: tests/test_ambiguity_evaluator.py::test_clarification_interception_proxy

### REQ-006-009
Requirement: Expose ambiguity analysis through an importable Python API and CLI JSON output with an optional traceability graph input.
Critical: true
Acceptance: CLI/API outputs are deterministic; malformed inputs and invalid supplied trace graphs return nonzero without partial success claims.
Verify: tests/test_ambiguity_cli.py::test_ambiguity_cli

### REQ-006-010
Requirement: Preserve validator, linter, traceability, historical-release, append-only, and regression behavior from v0.05.
Critical: true
Acceptance: The inherited 83-test suite and active regressions REG-0001 through REG-0007 remain passing.
Verify: tests/test_validator.py, tests/test_linter.py, tests/test_traceability.py, and tests/test_traceability_cli.py

## Candidate rule contract

The v0.06 evaluator preregisters these deterministic families before implementation:

- `AMB-001` — `Options: key = value | value` candidate. A matching `Default: key = value` resolves the choice as `governed_default`; otherwise it is an `owner_decision`.
- `AMB-002` — a Requirement field containing a preregistered unbounded term without a non-empty `Bound:` field in the same block.
- `AMB-003` — a Requirement field beginning with an ambiguous demonstrative/pronoun whose `Refs:` targets are absent or undeclared.
- `AMB-004` — conflicting `Constraint: key = value` declarations.
- `AMB-005` — an `Assumption:` candidate without an `[approved DEC-*]` marker; approved assumptions are classified as governed rather than questioned.
- `AMB-006` — an active normative `TBD`, `TODO`, `pending`, `unresolved`, or `undecided` marker.

Quoted Markdown, fenced code, Notes, and Rationale are non-normative for this release and must not create candidates.

## Priority contract

Required-question priority score is machine-defined before implementation:

`severity_weight + critical_block_weight + min(downstream_impact_count, 99)`

Severity weights are `high=300`, `medium=200`, `low=100`. Critical requirement/task blocks add `50`. Sort descending score, then ascending block identifier, ambiguity code, and line number.

Preregistered category severity before resolution:

- conflicting constraint: high
- unresolved marker: high in a critical block, medium otherwise
- unresolved options: high in a critical block, medium otherwise
- undefined referent: high in a critical block, medium otherwise
- missing bound: medium in a critical block, low otherwise
- ungoverned assumption: medium in a critical block, low otherwise

Governed-default candidates are severity low and never enter the question queue.

## Evaluation interpretation

The clarification metric in v0.06 is an explicit **interception proxy**: a preregistered ambiguity that would require a decision during implementation counts as intercepted when the engine surfaces the corresponding decision-needed question before implementation. It is not evidence that an external coding agent actually asked fewer questions on a production project.

The frozen contract must therefore cap synthetic success at `PROMOTED AS EXPERIMENTAL`. A later separately preregistered evaluation can test actual project outcomes.

## Architecture

Use deterministic Python only. Reuse v0.04 Markdown block conventions and v0.05 traceability APIs where possible. No GUI, network call, LLM, embedding model, repository source analysis, or automatic owner-decision answering is permitted in v0.06.

## Failure behavior

Invalid Markdown encoding, malformed evaluator records, or invalid supplied traceability graphs must fail explicitly. Missing outcome evidence is incomplete evidence, never a zero count. The engine may propose a governed default only when the document contains the preregistered explicit governance evidence; it must not invent product choices.
