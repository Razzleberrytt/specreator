# Spec Creator

**Controlled, evidence-driven specification and execution infrastructure for AI software development.**

Spec Creator turns product intent into governed discovery, traceable specifications, deterministic execution artifacts, verification evidence, and reproducible releases. It is also recursively developing itself under the same governance it imposes on its own development.

> **Project invariant:** observe → evidence → root cause → hypothesis → preregister → freeze → implement → independently verify → reconcile → adopt/reject → preserve regression memory → specify successor.

## What Spec Creator is

Spec Creator is not a generic idea-to-spec generator. It is infrastructure for making specification and execution work **auditable, deterministic, provenance-preserving, and resistant to self-deception**.

The system is designed to preserve a chain from goals and requirements through discovery, traceability, task compilation, prompt/context compilation, execution planning, validation, history, and release governance. Frozen criteria stay frozen. Failed experiments stay visible. Missing evidence is not success. Tests and denominators cannot be weakened after the fact to manufacture promotion.

## Core principles

- **Evidence before promotion.** Claims require the evidence defined before implementation.
- **Frozen contracts.** Acceptance criteria, metrics, denominators, and guardrails cannot be rewritten after a candidate begins.
- **Deterministic artifacts.** Governed inputs should produce reproducible outputs with explicit provenance.
- **Traceability.** Goals, requirements, features, tasks, tests, gates, prompts, and execution artifacts remain connected.
- **Fail-closed freshness.** A PASS or READY recommendation becomes stale when its promotion-authoritative inputs change.
- **Independent verification.** Candidate implementation and release verification remain separate authorities.
- **Regression memory.** Discovered failures become durable tests rather than disappearing after repair.
- **Historical immutability.** Failed and superseded experiments remain part of the record.
- **Convergence over version churn.** Successors must close an objective capability gap or necessary uncertainty.

## Capability evolution

| Version | Outcome | Capability |
| --- | --- | --- |
| v0.01 | Historical baseline | Measured specification protocol |
| v0.02 | Evidence incomplete | Controlled recursive-improvement protocol |
| v0.03 | Promoted experimental | Executable schemas and structural validation |
| v0.04 | Promoted experimental | Deterministic Spec Linter and recursive-history integrity |
| v0.05 | Promoted experimental | Typed Traceability Engine and deterministic change-impact analysis |
| v0.06 | Retry required | Ambiguity Engine candidate; invalid benchmark dependencies discovered before implementation |
| v0.06.1 | Promoted experimental | Governed Ambiguity Engine retry and hardened release mechanics |
| v0.07 | Promoted experimental | Adaptive Discovery with safe defaults, dependency frontiering, budgets, provenance, and held-out evaluation |
| v0.08 | Promoted experimental | Deterministic Task Compiler and append-only execution replay |
| v0.09 | Retry required | Prompt Compiler candidate with contradictory negative benchmark case |
| v0.09.1 | Retry required | Invalid freeze transaction preserved as failed history |
| v0.09.2 | Promoted experimental | Fail-closed Prompt Compiler with exact context closure and continuation replay |
| v0.10+ | Governed evolution | Transfer, lifecycle, execution, and recursive-governance maturation toward v1.00 |

Historical release artifacts and repository governance are authoritative for exact release status; this table is an orientation layer, not a replacement control plane.

## Architecture

The intended governed lifecycle is:

```text
Intent / evidence
      ↓
Governed discovery & clarification
      ↓
Specification + decisions
      ↓
Typed traceability graph
      ↓
Deterministic task compilation
      ↓
Prompt / context compilation
      ↓
Execution planning + resumable history
      ↓
Validation + independent verification
      ↓
Reconciliation / adoption or rejection
      ↓
Regression memory + reproducible release
```

Every transformation should preserve enough provenance to answer: **where did this requirement come from, what depends on it, what changed, what must be revalidated, and what evidence authorizes the current state?**

## Executable capability families

### Structural validation

The validator family covers JSON/JSONL and schema validity, stable IDs and references, event supersession, regression governance, denominator reconciliation, missing-data enforcement, frozen-contract hashing, release-manifest verification, and candidate self-certification detection where actor evidence is available.

### Spec Linter

The deterministic Markdown linter identifies vague or non-testable normative language, missing acceptance/failure behavior, unresolved decisions, undefined references, contradictions, overly broad tasks, unbounded components, and ungoverned assumptions. Findings carry stable rule IDs and source locations; suppression requires an explicitly governed decision.

### Traceability Engine

The typed graph supports the canonical chain:

```text
Goal → Requirement → Feature → Task → Test → Gate
```

It validates relation/type transitions, references, cycles and critical-chain completeness, and computes deterministic upstream/downstream change impact.

### Ambiguity Engine

The ambiguity layer detects unresolved/defaulted options, missing measurable bounds, undefined referents, conflicting constraints, assumption-governance problems, and unresolved status markers. It can bind findings to traceability impact and distinguish owner decisions from governed defaults or specification corrections.

### Adaptive Discovery

Discovery turns unresolved ambiguity into a deterministic question/default plan. It may apply only explicitly safe defaults, respects dependency frontiers, batches only governed decisions, uses bounded question budgets, and preserves provenance for every action.

### Task Compiler

The compiler turns governed normalized task evidence into immutable task graphs. Dependencies must come from validated trace edges, explicit ordering, or unique producer/consumer evidence. It refuses unresolved owner decisions, rejects cycles, avoids inventing architectural splits, identifies write-conflict zones, and permits parallelism only when dependency and conflict checks allow it.

### Prompt / Context Compiler

The prompt compiler builds deterministic execution context while retaining obligations, authority boundaries, prerequisites, ownership, verifier constraints, and continuation/replay information. Context closure is governed rather than guessed.

## Governance and recursive development

Spec Creator dogfoods its own governance. A normal successor lifecycle is:

1. Observe a real gap or uncertainty.
2. Gather evidence and identify root cause.
3. State a falsifiable hypothesis.
4. Preregister metrics, denominators, guardrails, and acceptance evidence.
5. Freeze the contract.
6. Implement without rewriting that contract.
7. Produce an exact-state handoff receipt.
8. Independently verify the exact candidate.
9. Reconcile the evidence and adopt, retry, or reject.
10. Preserve failures as regression memory.
11. Create a successor only when an objective remaining capability requires one.

A candidate may never promote itself merely because it is newer.

## Canonical automation control plane

Autonomous development is coordinated through machine-readable repository state. The control plane is intentionally separate from historical release evidence and does not retroactively rewrite it.

Key responsibilities include:

- one canonical phase/release/candidate state;
- mechanical work claims to prevent incompatible duplicate work;
- append-only handoff and verifier receipts bound to exact candidate identity;
- fail-closed verification freshness;
- one prospective Version 1.00 trajectory;
- formal convergence reviews that distinguish true v1 MUST blockers from optional post-v1 improvements.

Major phase transitions are reconciled by the orchestration authority only after their mechanical preconditions are satisfied.

## Current repository state

The repository is currently in a **governed baseline restoration/reconciliation phase** before autonomous successor implementation may proceed. Historical release evidence is preserved separately from the live GitHub tree, and the automation is required to fail closed until the canonical baseline identity and exact-state evidence are reconciled.

Do not infer release authority from this README. The machine-readable state under `ops/`, exact repository history, frozen release contracts, manifests, receipts, and verifier evidence are authoritative.

## Path to Version 1.00

Version 1.00 is a convergence target, not a date or arbitrary version counter. The prospective v1 contract must objectively cover the complete intended lifecycle:

- specification and governed discovery/clarification;
- traceability and deterministic change propagation;
- task compilation;
- prompt/context compilation;
- execution planning, handoff, and resume;
- validation and release/history lifecycle;
- deterministic and provenance-preserving artifacts;
- package/install and clean-extraction reproducibility;
- security and data integrity;
- durable regression memory;
- documentation and examples matching behavior;
- justified API/CLI/workflow usability;
- real-project transfer evidence;
- fresh independent verification of the exact release candidate;
- explicit non-goals.

Every v1 MUST requirement needs objective acceptance evidence. When no objective MUST blocker remains, development enters release-candidate hardening rather than inventing another exploratory successor. After verified v1.0.0, autonomous feature expansion stops unless a regression invalidates the completion evidence.

## Install and run

Once the complete package is present in the working tree:

```bash
pip install -e .

spec-creator validate .
spec-creator lint path/to/spec.md
spec-creator lint path/to/spec.md --json
spec-creator trace-validate graph.json
spec-creator trace-impact graph.json NODE-ID [NODE-ID ...]
spec-creator ambiguity path/to/spec.md --json
spec-creator discovery path/to/spec.md --profile profile.json --trace-graph graph.json --json
spec-creator task-compile task-project.json --json
spec-creator task-graph-validate compiled-task-graph.json --json
spec-creator task-replay compiled-task-graph.json execution-events.jsonl --json
```

Additional release- and version-specific commands are defined by the corresponding governed artifacts. Do not substitute README examples for frozen release instructions.

## Historical evidence matters

Spec Creator deliberately retains unsuccessful experiments. Examples include invalid benchmark dependencies, contradictory benchmark cases, invalid freeze transactions, stale-authority defects, duplicate metadata behavior, and unsafe stable-ID assumptions. Repairs become regression memory; the original failures are not erased or retroactively counted as successes.

That is a feature of the project, not clutter: **the history is part of the evidence.**

## Status authority

For exact current status, consult the canonical machine-readable state and repository evidence rather than prose documentation. In particular, `ops/spec-creator-state.json`, work-claim/receipt artifacts, frozen contracts, package manifests, tests, and verifier evidence govern release decisions.

---

**Spec Creator's goal is not to produce more specifications. It is to make the path from intent to execution inspectable, reproducible, governable, and increasingly reliable.**
