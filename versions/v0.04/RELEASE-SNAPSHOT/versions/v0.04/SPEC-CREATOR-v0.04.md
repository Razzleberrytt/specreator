# Spec Creator v0.04 — Deterministic Spec Linter

**Status:** Approved candidate specification; implementation not yet started at freeze time  
**Parent:** v0.03 (PROMOTED AS EXPERIMENTAL)  
**Theme:** Detect weak specifications automatically without teaching users to ignore noisy diagnostics.

## 1. Evidence-derived objective

v0.03 made structural artifacts machine-checkable and exposed REG-0004: an apparently rigorous rule rejected valid records because it failed to distinguish declarations from references. v0.04 therefore prioritizes **precision and context** as strongly as defect detection.

The candidate adds a deterministic Markdown linter for specification-quality defects that are observable without model-dependent semantic scoring.

## 2. Supported input profile

v0.04 supports UTF-8 Markdown. Structural rules recognize these explicit conventions when present:

- requirement blocks headed by `### REQ-*` with fields such as `Requirement:`, `Critical:`, `Acceptance:`, `Failure:`, and `Verify:`;
- task blocks headed by `### TASK-*` with `Task:` and optional `Bounded By:`;
- component blocks headed by `### Component:` with `Responsibilities:` and optional `Out of Scope:`;
- declarations `Interface:` and `Entity:` and references `Refs:`;
- deterministic constraints expressed as `Constraint: key = value`;
- governed assumptions expressed as `Assumption: ... [approved DEC-*]` or `[rejected DEC-*]`;
- decision markers such as `Decision:` or `Critical Decision:`.

Contextual prose linting ignores fenced code, blockquotes, and lines beginning `Notes:` or `Rationale:` so examples and commentary are not mistaken for active requirements.

Arbitrary semantic interpretation of unconstrained prose is **not** claimed by v0.04.

## 3. Lint rules

### LINT-001 — Vague or non-testable normative language
Flag configured vague terms in active normative prose when no measurable bound is present. Diagnostics must identify the exact phrase and explain why it is not directly testable.

### LINT-002 — Missing acceptance criteria
A `REQ-*` block must contain non-empty `Acceptance:` content.

### LINT-003 — Missing failure behavior for critical mutating operations
A requirement marked `Critical: true` whose requirement statement performs a mutating/externally consequential operation (for the initial deterministic vocabulary: delete, deploy, write, migrate, send, update, upload, charge, publish, remove, overwrite) must state `Failure:` behavior.

### LINT-004 — Unresolved critical decision
Flag active critical decision markers with unresolved states such as TBD, TODO, pending, unresolved, or undecided. Resolved, approved, rejected, or decision-ID-backed outcomes are not defects.

### LINT-005 — Undefined referenced interface/entity
Every token listed under active `Refs:` must resolve to an `Interface:` or `Entity:` declaration in the same document.

### LINT-006 — Orphan requirement without verification path
A `REQ-*` block must contain non-empty `Verify:` content.

### LINT-007 — Contradictory deterministic constraints
If the same active `Constraint:` key is assigned more than one distinct value, emit a contradiction diagnostic pointing to the later conflicting declaration and the earlier source line.

### LINT-008 — Task too broad
Flag a `TASK-*` block that combines four or more recognized major implementation actions in one task unless it includes an explicit `Bounded By:` line.

### LINT-009 — Unbounded component responsibility
Flag a component with broad/all-encompassing responsibility wording, or more than four comma-separated responsibility domains, unless it includes an explicit `Out of Scope:` boundary.

### LINT-010 — Ungoverned implementation assumption
Flag active `Assumption:` statements that do not carry an approved or rejected `DEC-*` marker. Commentary/examples are ignored.

## 4. Diagnostic contract

Every finding must include:

- stable rule ID;
- severity;
- source line and 1-based column;
- exact source span text;
- deterministic rationale;
- optional related line for contradictions;
- suppression state when applicable.

Findings must be deterministically ordered by source position then rule ID.

## 5. Suppression governance

A local suppression may name one rule and one `DEC-*` decision. It is honored only when the caller supplies that decision ID as approved. Unknown or unapproved decisions may not hide the finding and must emit a suppression-governance diagnostic. Blanket disable-all suppression is out of scope.

## 6. CLI/library surface

Add an importable `spec_creator.linter` library and extend the existing CLI with:

- `spec-creator lint <file>` human-readable diagnostics;
- `spec-creator lint <file> --json` machine-readable diagnostics;
- repeatable `--approved-decision DEC-*` for governed suppressions.

Lint failure exits nonzero when unsuppressed error findings exist. Existing `validate` behavior remains backward compatible.

## 7. Evaluation design

The preregistered evaluation plan is `versions/v0.04/EVALUATION-PLAN.json`. Its corpus is `fixtures/linter/v0.04/corpus.jsonl`, containing 100 cases: five seeded defect cases and five clean counterexamples for each LINT-001 through LINT-010.

The frozen release contract embeds the SHA-256 of that corpus and the evaluation-plan SHA-256. Mutation after freeze is a release failure.

Primary metrics:

- defect-case detection rate;
- clean-case acceptance rate;
- finding precision;
- diagnostic completeness rate.

Guardrails include minimum per-rule precision, zero clean false positives, suppression-governance correctness, inherited regression pass rate, and v0.03 validator compatibility.

## 8. Architecture

Remain in Python and extend the existing package. Use only deterministic parsing/regex/field extraction; do not add an LLM, embeddings, network calls, GUI, or repository-aware code analysis in this candidate.

Core design:

1. line/context scanner;
2. structural block parser;
3. independent rule functions;
4. immutable finding model;
5. suppression resolver;
6. deterministic reporter;
7. corpus evaluator.

Rules must not silently mutate source documents.

## 8.1 Required inherited-validator compatibility repair

The pre-freeze v0.04 setup exposed an implementation defect in v0.03: version manifests hash shared append-only ledgers such as `evaluation/events.jsonl`. Legitimate successor appends therefore make historical manifests fail if the validator compares only the current whole-file hash.

v0.04 must preserve the original v0.03 manifest and release evidence, capture the original v0.03 package manifest as a version-local historical snapshot, and teach manifest verification to distinguish:

- immutable/version-local artifacts, which must still match exactly; and
- explicitly append-only shared ledgers, whose historical prefix through the recorded snapshot byte count must match the frozen release hash.

A changed historical prefix must still fail. Later appended bytes must not invalidate the prior release. This repair is a prerequisite for a clean recursive workspace and must become a permanent regression.

## 9. Non-goals

- model-based semantic scoring;
- automatic rewriting/fixing;
- arbitrary-English contradiction inference;
- repository-aware interface discovery;
- GUI/dashboard;
- automatic promotion or self-certification.

## 10. Promotion interpretation

Passing the frozen synthetic corpus can justify **PROMOTED AS EXPERIMENTAL** only. Full promotion requires later evidence on real software projects showing useful defect prevention without unacceptable false-positive burden.
