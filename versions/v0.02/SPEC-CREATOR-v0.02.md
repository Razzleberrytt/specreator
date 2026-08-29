# Spec Creator v0.02 — Recursive Improvement Edition

**Version:** 0.02  
**Status:** Experimental successor specification  
**Parent:** v0.01  
**Purpose:** Turn Spec Creator from a static specification protocol into a controlled, evidence-driven recursive improvement system that can specify, evaluate, and propose the next version of itself without allowing self-modification to bypass predeclared tests or human governance.

## 1. Design Thesis

v0.01 established specification quality gates, event logging, traceability, and measurable evaluation.

v0.02 adds the missing meta-layer:

**Spec Creator N → specifies N+1 → freezes N+1 success criteria → N+1 is implemented → independent evaluation → evidence-backed retrospective → proposed improvements → adopt/reject → regression corpus grows → N+1 may specify N+2.**

This is controlled bootstrapping, not unconstrained self-rewriting.

## 2. New Non-Negotiable Invariants

### INV-001 — No Self-Certification
A candidate version must not be the sole authority deciding whether it passed its own release criteria.

### INV-002 — Pre-Registration
Success criteria, comparison metrics, mandatory regressions, and critical gates for version N+1 must be frozen before implementation of N+1 begins.

### INV-003 — Immutable Evaluation History
Raw evaluation events are append-only. Corrections supersede but never erase prior records.

### INV-004 — No Goalpost Movement
A release criterion may not be weakened after observing candidate results unless the release is marked failed under the original criterion and the criterion change is recorded as a separate governance decision for a future release.

### INV-005 — Evidence Before Adoption
A process change may be promoted from proposal to adopted rule only when its evidence requirement is satisfied.

### INV-006 — Permanent Regression Memory
A confirmed failure mode that results in an adopted fix must generate a regression test, lint rule, gate rule, or explicit documented reason why automation is impossible.

### INV-007 — Backward Capability Preservation
A new version must pass all still-applicable prior critical regression tests unless an explicit breaking-change decision supersedes one.

### INV-008 — Reversible Promotion
Every candidate release must preserve a rollback path to the previous validated protocol.

## 3. Meta-Specification Lifecycle

Each version has seven controlled phases:

1. **Observe** — gather failure and performance evidence.
2. **Diagnose** — classify root causes.
3. **Propose** — create improvement hypotheses.
4. **Pre-register** — define expected effect and acceptance tests before implementation.
5. **Implement** — build candidate version.
6. **Evaluate** — compare candidate with parent/baseline.
7. **Promote or Reject** — make a governed release decision.

A version cannot skip directly from proposal to promotion.

## 4. Improvement Ledger

Maintain `/self-improvement/improvement-ledger.jsonl`.

Each improvement record has:

- `improvement_id`
- `origin_version`
- `target_version`
- `observed_problem`
- `evidence_refs`
- `root_cause`
- `hypothesis`
- `proposed_change`
- `expected_metrics`
- `preregistered_acceptance`
- `risk_level`
- `status`
- `result`
- `disposition`
- `regression_ids`
- `decision_id`

Statuses:
- observed
- diagnosed
- proposed
- preregistered
- implementing
- evaluating
- adopted
- rejected
- deferred
- superseded

## 5. Experiment Registry

Each candidate change that claims measurable improvement must have an experiment record before implementation.

Required fields:
- experiment ID
- hypothesis
- comparison unit
- parent/candidate versions
- project corpus
- controlled variables
- primary metric
- guardrail metrics
- minimum acceptable improvement
- failure criteria
- missing-data policy
- evaluator identity/method
- freeze timestamp

Candidate results cannot alter these fields retroactively.

## 6. Regression Corpus

Maintain a permanent machine-readable regression registry.

Each regression records:
- regression ID
- origin incident
- first fixed version
- description
- reproducer or fixture
- expected behavior
- severity
- applicable modes
- automated/manual status
- test command or verification procedure
- superseding decision if retired

Release gate:
**All applicable critical regressions must pass.**

## 7. Version Manifest

Every release contains a manifest with:
- version
- parent version
- status
- protocol/schema versions
- added capabilities
- removed/deprecated capabilities
- breaking changes
- required migrations
- new/retired regressions
- preregistered goals
- evaluation result
- promotion decision
- content hashes

This makes each release inspectable and reproducible.

## 8. Independent Evaluator Role

Introduce an evaluator role separate from the implementation agent.

The evaluator:
- reads frozen criteria
- inspects raw events and repository evidence
- runs/validates regressions
- checks metric reconciliation
- records disagreements
- cannot silently alter requirements
- recommends promote/reject/conditional retry

For high-risk or major versions, use two evaluators or evaluator agreement sampling.

## 9. Self-Improvement Quality Gate

A proposed successor specification passes the Self-Improvement Gate only when:

- parent-version evidence is available
- root causes are separated from symptoms
- each material change links to evidence or an explicit exploratory hypothesis
- success criteria are frozen
- guardrail metrics prevent local optimization from hiding regressions
- applicable regressions are identified
- rollback is defined
- evaluator independence is defined
- no critical parent invariant is removed without an explicit breaking-change decision

## 10. Candidate Promotion Gate

A candidate may be promoted only when:

- all critical gates pass
- all critical regressions pass
- preregistered primary criteria pass or the release is explicitly classified experimental
- guardrail metrics do not breach hard limits
- event and denominator reconciliation passes
- no critical open defect exists
- evaluator recommendation is recorded
- release manifest is complete
- rollback package exists

If metrics improve but a critical invariant regresses, promotion fails.

## 11. Anti-Gaming Rules

The system must not:
- redefine task boundaries to improve task-success metrics
- exclude difficult events without a preregistered classification rule
- classify specification defects as user scope changes without evidence
- change denominator cutoffs after seeing results
- cherry-pick only successful projects
- silently discard failed experiments
- retire regression tests merely because they fail
- allow the candidate version to edit its own frozen release contract

## 12. Meta-Metrics

In addition to v0.01 metrics, track:

### Improvement Adoption Precision
Adopted improvement proposals that produce their preregistered benefit ÷ adopted proposals evaluated.

### Regression Recurrence Rate
Previously fixed failure modes that recur ÷ applicable regression opportunities.

### Proposal Yield
Adopted improvements ÷ preregistered improvement experiments.

### False Improvement Rate
Changes initially appearing beneficial but later rejected due to guardrail/regression failure ÷ evaluated candidate changes.

### Evaluator Agreement Rate
Evaluation decisions with matching independent judgments ÷ multiply evaluated decisions.

### Version Delivery Efficiency
Total effort to produce and validate successor ÷ number of successfully adopted improvements.

## 13. v0.02 Generation Contract for v0.03

v0.02 is authorized to propose v0.03 only after at least one recursive build cycle is logged.

The v0.03 specification must be generated from:
1. unresolved v0.02 limitations
2. failed or weak gates
3. high-frequency corrective prompts
4. recurring ambiguity/rework root causes
5. accepted improvement proposals
6. regression-corpus gaps
7. user friction evidence

v0.02 must distinguish:
- evidence-backed requirements
- exploratory hypotheses
- deferred ideas

It may not present exploratory features as proven improvements.

## 14. v0.02 Added Package Artifacts

Add:
- `/self-improvement/improvement-ledger.jsonl`
- `/self-improvement/experiment-registry.jsonl`
- `/self-improvement/regressions.jsonl`
- `/self-improvement/LESSONS.md`
- `/evaluation/release-scorecards.jsonl`
- `/versions/<version>/MANIFEST.json`
- `/versions/<version>/FROZEN-RELEASE-CONTRACT.json`
- `/versions/<version>/RETROSPECTIVE.md`

## 15. v0.02 Acceptance Criteria

v0.02 is structurally complete when:
- it can create a frozen successor release contract
- it can record an improvement hypothesis and experiment
- it can preserve append-only evidence
- it can turn an adopted failure lesson into a permanent regression record
- it can generate a successor spec while distinguishing evidence from hypothesis
- it can reject a candidate even when one headline metric improves
- it can reproduce the promotion decision from raw records
- it preserves all v0.01 critical quality/evaluation invariants

v0.02 is validated only after it successfully governs at least one v0.03 candidate cycle and the cycle is independently reproducible.

## 16. First Recursive Experiment

Use **Spec Creator itself** as the first recursive project.

Parent: v0.01  
Candidate: v0.02  
Objective: determine whether the recursive controls reduce unmanaged design drift while preserving or improving implementation usability.

The parent specification defines this v0.02 contract. Before implementing a software form of v0.02, freeze its acceptance criteria and regression set. Record all resulting corrections as evidence for v0.03.

## Current Status

v0.02 is specified but not validated. Its most important contribution is governance: improvement is now a measured, preregistered, regression-protected process rather than open-ended self-editing.
