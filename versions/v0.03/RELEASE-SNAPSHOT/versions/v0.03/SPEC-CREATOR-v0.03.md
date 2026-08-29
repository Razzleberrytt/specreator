# Spec Creator v0.03 — Executable Validation Layer

**Version:** 0.03  
**Status:** Candidate specification, preregistered before implementation  
**Parent:** v0.02 (experimental, not validated)  
**Mode:** Exhaustive  
**Theme:** Executable Schemas and Validator

## 1. Evidence basis

v0.03 is derived from the first audit of the supplied v0.02 package, not merely copied from the roadmap.

### Evidence-backed requirements

- **EB-001:** The evaluation workspace was empty, so promotion and metric reconciliation were not reproducible (`DEF-0001`).
- **EB-002:** Schemas existed without an executable validator or automated regression corpus (`DEF-0002`).
- **EB-003:** The frozen-contract schema could not express the full governance contract or its own integrity (`DEF-0003`).
- **EB-004:** The v0.02 manifest was weaker than the manifest structure required by its specification (`DEF-0004`).
- **EB-005:** Current critical regressions were manual only (`DEF-0005`).
- **EB-006:** v0.01 already requires stable IDs, append-only events, denominator snapshots, same-cutoff/scope metric reconciliation, and explicit missing-data handling.

### Exploratory hypotheses

- **HYP-001:** A small deterministic CLI/library is sufficient for v0.03; a GUI is unnecessary.
- **HYP-002:** JSON Schema should handle record shape/controlled enums while Python semantic checks handle graph/lifecycle/integrity rules.
- **HYP-003:** Candidate self-certification can be mechanically detected when release scorecards explicitly identify implementer and evaluator actors.

### Deferred ideas

Natural-language spec linting, ambiguity scoring, full traceability graph construction, repository intelligence, UI, statistical baseline comparison, tamper-evident event chains, and plugin architecture remain deferred to their roadmap versions unless required to make v0.03's validator correct.

## 2. Scope

Build the first executable Spec Creator component: a Python library and CLI that validates a Spec Creator workspace.

It must support:

1. JSON and JSONL parsing with line-aware errors.
2. JSON Schema Draft 2020-12 validation.
3. Schemas for events, improvements, regressions, experiments, decisions, frozen contracts, denominator snapshots, metric records, release scorecards, release manifests, requirements, tasks, and gates.
4. Controlled-enum and stable-ID validation.
5. Duplicate-ID detection.
6. Cross-reference validation.
7. Event lifecycle and supersession consistency.
8. Regression retirement governance.
9. Denominator snapshot and metric-ledger reconciliation.
10. Missing-data declarations.
11. Frozen-contract canonical hash verification.
12. Release-manifest content hash verification.
13. Candidate self-certification detection where actor records make it observable.
14. A deterministic workspace validation report and process exit code.
15. Automated valid/invalid fixtures and tests.

## 3. Non-goals

- No GUI.
- No natural-language linting.
- No automatic requirement extraction.
- No autonomous promotion.
- No rewriting a frozen contract.
- No statistical claim that v0.03 improves real-world software delivery; this version validates protocol artifacts only.

## 4. Architecture

### ADR reference

`DEC-0003` selects Python 3.11+ and `jsonschema` Draft 2020-12.

### Components

- `src/spec_creator/models.py` — result/issue structures and canonical hashing.
- `src/spec_creator/schema_registry.py` — artifact-to-schema registry.
- `src/spec_creator/validator.py` — parsing, schema validation, semantic workspace checks.
- `src/spec_creator/cli.py` — `validate` and `hash-contract` commands.
- `schemas/*.schema.json` — machine-readable record contracts.
- `tests/` and `fixtures/` — deterministic regression corpus.

## 5. Stable identifier conventions

New v0.03 schemas enforce:

- Events: `EVT-*`
- Improvements: `IMP-*`
- Regressions: `REG-*`
- Experiments: `EXP-*`
- Decisions: `DEC-*`
- Contracts: `REL-*`
- Metrics: `MET-*`
- Denominator snapshots: `DEN-*`
- Release evaluations/scorecards: `EVAL-*`
- Requirements: `REQ-*`
- Tasks: `TASK-*`
- Gates: `GATE-*`

Legacy v0.01/v0.02 records are accepted only where their IDs already conform or a declared compatibility rule applies.

## 6. Semantic invariants

### Events
- Duplicate event IDs fail.
- `parent_event_id` must resolve.
- `superseded` events must identify `attributes.superseded_by_event_id`, which must resolve to a distinct event.
- Superseded events are not eligible for active metric entity counts.

### Regressions
- Duplicate regression IDs fail.
- `retired` or `superseded` records require a non-null `superseding_decision_id` resolving to an approved governance decision.
- Active critical regressions in a frozen contract must resolve to active regression records.

### Metrics and denominators
- Every metric record must reference an existing denominator snapshot.
- Metric and snapshot cutoff, scope, denominator value, and unit must match.
- Complete records require a denominator and a reproducible value.
- Incomplete/unavailable records must declare missing data and may not masquerade as zero.
- Division-by-zero is represented explicitly, never guessed.
- Source event IDs must resolve when supplied.

### Frozen contracts
- Canonical SHA-256 is calculated over the JSON object with `contract_hash` omitted.
- A mismatch fails validation.
- Candidate and parent versions must differ.
- Required goals, requirements, gates, regressions, metrics, failure conditions, promotion conditions, rollback expectations, and frozen timestamp must be present.

### Release scorecards
- The evaluator actor must not appear in the implementation actor set.
- Every mandatory gate and applicable critical regression from the frozen contract must have a recorded outcome.
- Promotion is rejected when a critical required outcome is not PASS/PASS WITH ACCEPTED RISK where the contract allows accepted risk.

### Manifests
- Declared content hashes must match current bytes.
- The manifest's release contract hash must match the frozen contract.
- Critical regression removals require governance evidence.

## 7. CLI contract

### Validate workspace

`spec-creator validate [PATH] [--json]`

- Exit 0: no validation errors.
- Exit 1: one or more validation errors.
- Human output lists code, severity, artifact, and message.
- JSON output is deterministic and includes summary counts.

### Hash a contract

`spec-creator hash-contract FILE`

Print the canonical contract SHA-256 calculated with `contract_hash` omitted.

## 8. Test and regression corpus

Preregistered tests include valid fixtures and failures for:

- malformed JSON
- malformed JSONL
- missing required fields
- invalid controlled enums
- invalid stable IDs
- duplicate IDs
- broken references
- invalid event supersession
- frozen-contract mutation
- missing metric denominator/snapshot
- metric cutoff mismatch
- metric scope mismatch
- metric calculation mismatch
- missing-data misuse
- regression retirement without governance
- candidate self-certification
- manifest hash mismatch
- valid complete workspace

No failing test may be weakened merely to obtain promotion.

## 9. Quality gates

- **GATE-003-SCHEMA:** all owned schemas are valid Draft 2020-12 schemas and all owned production records validate.
- **GATE-003-TEST:** full automated suite passes.
- **GATE-003-SEMANTIC:** preregistered invalid fixture detection = 100%; valid fixture acceptance = 100%.
- **GATE-003-INTEGRITY:** frozen contract and manifest integrity checks pass; mutation fixture fails.
- **GATE-003-REGRESSION:** all applicable critical regressions pass.
- **GATE-003-RECONCILIATION:** release metrics reconcile to frozen denominator snapshots/raw events, or are explicitly unavailable.
- **GATE-003-INDEPENDENT:** verifier actor distinct from implementation actor records the release recommendation.
- **GATE-003-ROLLBACK:** v0.02 source files remain unchanged and a rollback declaration identifies them.

## 10. Promotion constraint

v0.03 may be classified `PROMOTED AS EXPERIMENTAL` only if every condition in its frozen release contract passes. The experimental label is mandatory because the parent v0.02 was not previously validated and the cycle evaluates artifact integrity rather than multi-project delivery outcomes.

## 11. Migration strategy

Schemas are immutable by filename. Breaking schema changes create a new versioned schema file (for example `event-v2.schema.json`) rather than editing the historical schema contract. Validators may support multiple schema versions through explicit registry mappings. Historical records are not silently rewritten; migrations create new records/files with provenance.

## 12. Exit

A successful v0.03 makes invalid core protocol artifacts automatically rejectable and produces a release decision reproducible from frozen machine-readable evidence. Only then may the promoted experimental v0.03 specify v0.04.
