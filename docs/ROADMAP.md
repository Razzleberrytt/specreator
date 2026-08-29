# Spec Creator — Governed Roadmap to Version 1.00

## Purpose

This roadmap describes the prospective path from the preserved mature v0.11.1 checkpoint to Version 1.00. It is planning documentation, not promotion authority. `ops/spec-creator-state.json`, `ops/V1-TRAJECTORY.json`, frozen contracts, exact repository history, claims, receipts, manifests, tests, and independent verifier evidence remain authoritative.

The roadmap is additive. It must never retroactively redefine historical releases, frozen metrics, denominators, failures, or promotion decisions.

## North star

Version 1.00 should make the complete path from intent to governed execution reproducible and inspectable:

`intent → discovery → specification → traceability → task compilation → prompt/context compilation → execution plan/resume → validation → independent verification → reconciliation → release/history`

A project should be able to answer, mechanically where practical: what is required; why; where the evidence came from; what remains ambiguous; what depends on what; what can run safely in parallel; what context an executor needs; what changed; what became stale; what was tested; what failed historically; and what exact evidence authorizes the current release state.

## Roadmap rules

1. Restore and reconcile the canonical baseline before successor implementation.
2. Admit a successor only for an objective v1 MUST gap or necessary uncertainty.
3. Preregister and freeze before promotion-authoritative implementation.
4. Keep implementation and independent verification separate.
5. Bind handoffs and verification to exact candidate identity and contract hash.
6. Treat changed authoritative inputs as freshness invalidation.
7. Preserve failures and regressions instead of rewriting history.
8. Run convergence review after every three adopted successor cycles and whenever blocking work appears exhausted or optional.
9. Move optional improvements behind the v1 boundary when zero objective MUST blockers remain.
10. Stop autonomous feature expansion after verified v1.0.0 unless a regression invalidates its completion evidence.

## Phase 0 — Canonical baseline restoration and reconciliation

**Priority: P0 / current hard gate**

Goal: establish the exact historical v0.11.1 capability in GitHub without changing its frozen bytes or manufacturing a replacement release.

Required evidence before exit:

- exact historical package identity is restored;
- historical hash universes and ownership classifications reconcile;
- no unclassified, overlapping, or stale shipping members remain;
- clean-environment package/install/extraction behavior is reproduced where required by the historical transaction;
- frozen tests and active regressions pass on the exact state;
- additive automation/control-plane files remain distinguishable from historical sealed bytes;
- exact-state handoff and independent verification freshness are mechanically established;
- Lane 5 reconciles the legal release state.

No successor product implementation is legal during this phase.

## Phase 1 — Canonical control-plane hardening

Goal: make recursive development mechanically governable rather than convention-driven.

V1 MUST capabilities:

- exactly one canonical phase/candidate/release state;
- mechanical work claims with collision and staleness rules;
- append-only phase-boundary handoff receipts;
- exact candidate SHA + frozen-contract binding;
- verification-freshness invalidation for tests, manifests, package membership, dependencies, authoritative artifacts, and criteria;
- prospective V1 trajectory with objective MUST/optional distinction;
- convergence-cycle accounting;
- deterministic legal-transition validation;
- clear separation between historical evidence and live orchestration state.

Exit criterion: an invalid/stale/ambiguous transition fails closed without relying on an operator noticing prose drift.

## Phase 2 — End-to-end specification lifecycle completeness

Goal: close functional gaps between discovery and executable governed work.

V1 MUST coverage:

- structured project intent and requirement capture;
- governed ambiguity detection and clarification;
- explicit safe defaults with provenance;
- complete typed traceability;
- deterministic stale/change propagation;
- deterministic task compilation;
- conflict-zone and safe-parallelism reasoning;
- prompt/context compilation with exact obligation retention;
- execution planning and resumable continuation;
- validation and gate compilation;
- durable history linking outputs back to authoritative inputs.

The roadmap does not prescribe a new successor version for each bullet. Prefer the smallest number of governed candidates that close objectively related gaps.

## Phase 3 — Incremental change and stale-state correctness

Goal: make Spec Creator useful after the first specification pass, not merely at project creation.

V1 MUST capabilities:

- identify downstream artifacts affected by an authoritative change;
- invalidate stale compiled artifacts deterministically;
- preserve unaffected artifacts when identity/provenance proves reuse is safe;
- distinguish recomputation from semantic owner decisions;
- prevent stale prompts/tasks/tests/releases from silently retaining authority;
- resume execution against a changed project without losing historical lineage;
- regression coverage for stale-authority escapes.

Expected value: lower reconstruction/rework cost while preserving correctness.

## Phase 4 — Real-project transfer and interoperability

Goal: prove the system transfers beyond its own synthetic/self-dogfood environment.

V1 MUST evidence should include preregistered, genuinely separate project contexts and exact denominators. Candidate transfer dimensions include:

- requirement/decision reconstruction burden;
- unresolved ambiguity escape rate;
- trace completeness;
- invented dependency/requirement rate;
- execution-context completeness;
- rework after change;
- resumability correctness;
- import/export fidelity;
- user/operator intervention required to recover state.

Synthetic fixtures remain useful regression instruments but cannot substitute for real-transfer evidence where the contract requires external contexts.

## Phase 5 — Usability surface

Goal: expose governed capability without forcing users to understand repository internals.

V1 MUST where justified by evidence:

- coherent CLI workflow and help output;
- stable machine-readable API/artifact contracts;
- actionable diagnostics with source locations and next legal actions;
- examples covering a representative end-to-end project;
- clear error behavior for blocked, stale, ambiguous, or invalid states;
- installation and clean-start instructions verified against reality;
- deterministic noninteractive paths suitable for automation.

A graphical/web interface is not automatically a v1 MUST. It becomes one only if objective usability evidence demonstrates that CLI/API workflow cannot satisfy the intended v1 user contract.

## Phase 6 — Security, integrity, and reproducibility hardening

Goal: ensure governance cannot be bypassed accidentally through storage, packaging, or execution mechanics.

V1 MUST coverage:

- path and artifact-boundary safety;
- safe handling of untrusted project inputs;
- deterministic serialization/canonical hashing where authority depends on bytes;
- append-only evidence integrity;
- dependency and lockfile reproducibility;
- package ownership completeness;
- clean extraction/install validation;
- no hidden mutable authority outside governed artifacts;
- failure-atomic writes for promotion-authoritative state;
- recovery behavior for interrupted transactions;
- explicit treatment of secrets/private data if supported by the product surface.

## Phase 7 — Release-candidate hardening

Entry condition: formal convergence review finds zero unresolved objective v1 MUST capability blockers and all required predecessor candidates are legally reconciled.

Exploratory successor creation is forbidden here.

Required work:

- freeze the additive VERSION-1.00 contract/checklist;
- build the exact release candidate;
- run complete clean-environment test/install/package/extraction validation;
- run all active regressions;
- reconcile exact package ownership and hashes;
- verify documentation against behavior;
- verify real-transfer claims against preregistered evidence;
- produce exact implementation→verification and release/seal receipts;
- obtain fresh independent verification for the exact candidate;
- repair only release-blocking defects through governed retry semantics.

## Phase 8 — Version 1.00

Version 1.00 may be declared only when every canonical v1 MUST requirement has objective evidence and no blocking defect remains.

Completion artifacts should include:

- final VERSION-1.00 contract/checklist;
- fresh independent verifier recommendation;
- v1 completion receipt;
- authoritative shipping manifest and final seal;
- changelog and release notes;
- package/install instructions matching tested behavior;
- version `1.0.0`;
- tag/release `v1.0.0` when repository tooling permits.

After verified v1.0.0, autonomous feature expansion stops. New feature ideas move to a post-v1 backlog; only regressions that invalidate the v1 completion evidence may reopen the completion transaction.

## Cross-cutting quality bars

These are persistent constraints rather than standalone phases:

| Area | Required direction |
| --- | --- |
| Determinism | Same authoritative inputs yield reproducible governed artifacts |
| Provenance | Derived obligations can be traced to authoritative sources |
| Freshness | Changed authority invalidates stale evidence automatically |
| Safety | Missing/ambiguous evidence fails closed |
| History | Failed experiments and superseded states remain visible |
| Testing | Criteria are not weakened to obtain promotion |
| Transfer | Claims use preregistered real evidence where required |
| Packaging | Ownership, hashes, extraction and installation are exact |
| Automation | Duplicate authority and overlapping incompatible work are mechanically prevented |
| Usability | Diagnostics explain what failed and the next legal action |

## Prospective opportunity pool

The following are **candidate areas**, not pre-authorized successors. Lane 5 should admit them only when evidence shows they close a remaining v1 MUST gap:

- incremental recompilation and cache correctness;
- deterministic project snapshot/import/export;
- execution checkpoint/resume ergonomics;
- semantic diff and change-impact explanation;
- validation-plan compilation from requirements and gates;
- machine-readable diagnostic/remediation protocol;
- project migration/version compatibility;
- reproducible context minimization without obligation loss;
- artifact graph visualization as a derived/non-authoritative view;
- performance scaling for large trace/task graphs;
- governance transaction crash recovery;
- security threat model and adversarial fixtures;
- end-to-end tutorial/reference project;
- API stability/versioning policy;
- installation/package matrix where supported environments justify it.

## Explicit post-v1 candidates unless evidence promotes them

- polished graphical IDE;
- hosted multi-user SaaS control plane;
- marketplace/plugin ecosystem;
- autonomous architecture invention;
- probabilistic replacement of deterministic governance checks;
- broad provider integrations unrelated to the core specification→execution lifecycle;
- cosmetic features that do not close a v1 MUST capability or release risk.

## Convergence question

At every required convergence review, ask:

> **What specifically prevents v1.00 right now?**

Only evidence-backed objective MUST blockers belong in the answer. When that answer is empty, stop inventing successors and harden the release candidate.
