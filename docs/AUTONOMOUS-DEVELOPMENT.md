# Autonomous Development Governance

This document explains how the five-lane Spec Creator automation is intended to operate. It is explanatory documentation; machine-readable state, claims, receipts, frozen contracts and repository evidence remain authoritative.

## Lane responsibilities

| Lane | Primary authority |
| --- | --- |
| 1 | Integrity, baseline restoration, packaging, manifests, clean extraction, release infrastructure, CI foundations |
| 2 | Evidence, experiments, preregistration, algorithms and implementation within legally frozen successors |
| 3 | Execution/transfer integration, task/prompt usability, resume, interoperability and real-project transfer evidence |
| 4 | Independent verification and adversarial quality assessment |
| 5 | Canonical orchestration, reconciliation, roadmap/trajectory, phase transitions and final release judgment |

## Hourly pipeline

The automation is staggered intentionally. Earlier lanes can produce evidence or implementation; Lane 4 verifies only legally handed-off exact candidates; Lane 5 reconciles the completed cycle. Hourly cadence is a polling/coordination cadence, not a requirement to create a commit.

## Canonical transaction

A promotion-authoritative successor normally moves through:

`OBSERVED → EVIDENCED → PREREGISTERED → FROZEN → IMPLEMENTING → HANDED_OFF → VERIFYING → RECONCILING → ADOPTED | RETRY | REJECTED`

Names may vary in machine state, but authority boundaries must not collapse.

### Observe/evidence

A real capability gap, defect, risk, or uncertainty is demonstrated. Optional polish does not become MUST work merely because a lane can implement it.

### Preregister/freeze

Metrics, denominators, acceptance evidence, guardrails and failure behavior are defined before promotion-authoritative implementation. Freeze failure means no candidate implementation authority.

### Implement

The implementing lane changes only the frozen scope. Deterministic defects may be repaired without changing frozen criteria. If the contract itself is invalid, the candidate follows governed retry rather than silently rewriting criteria.

### Handoff

The producer emits a machine-readable receipt binding exact candidate SHA, frozen contract hash, authoritative/changed artifacts, tests and metric definitions, timestamp, producer and intended verifier.

### Independent verification

Lane 4 recomputes required evidence rather than trusting candidate-produced summaries. It does not repair the candidate it verifies. Candidate or promotion-authoritative input changes make the recommendation stale.

### Reconciliation

Lane 5 compares frozen criteria, implementation evidence, verifier evidence, regression state, freshness and repository reality. It chooses ADOPT, RETRY or REJECT only from that evidence.

## Claims and collision prevention

Before work begins, a lane should hold a live claim containing task identity, scope, owner, candidate/release identity, conflict key and heartbeat/staleness information. Incompatible overlapping live claims are rejected. Claims may be retired when completed, superseded, invalidated by candidate identity change, or genuinely expired after checking owner activity.

Claims coordinate work; they do not grant phase authority.

## Freshness

Verification fails closed when promotion-authoritative identity changes. Freshness inputs include at least:

- candidate SHA;
- frozen contract hash;
- required test definitions;
- relevant package membership/manifest;
- dependency lockfile/identity;
- promotion-authoritative artifact set;
- verifier-required criteria.

A historical PASS remains historical evidence but cannot authorize a different exact state.

## Convergence

After every three adopted successor cycles—and whenever no blocking defect exists or remaining work looks optional—Lane 5 asks:

> What specifically prevents v1.00 right now?

The answer must contain only objective evidence-backed MUST blockers. Zero blockers triggers release-candidate hardening and forbids exploratory successor creation.

## No-churn rules

Automation should not create duplicate PRs, comments, reruns, claims or successor versions simply because another hour elapsed. If an exact candidate is waiting on an independent lane or unchanged external condition, a no-op is healthier than competing state.

## Merge policy

Safe deterministic work should be repaired and merged automatically when the exact intended head is current, conflict-free, legal for the current phase, and all applicable required checks/governance gates are green. Automation must never weaken a test, validator, frozen criterion, regression, branch protection or provenance rule merely to obtain green.

## Baseline restoration gate

The current program treats faithful historical baseline restoration as a hard gate. Restoration must preserve exact historical bytes and evidence rather than bootstrap a new architecture. Successor product implementation remains blocked until the restoration transaction is reconciled by Lane 5.

## v1 stop condition

After exact Version 1.00 completion evidence is independently verified and sealed, autonomous feature expansion stops. Further autonomous mutation is limited to repairing regressions that invalidate the v1 completion receipt until a separately governed post-v1 program is authorized.
