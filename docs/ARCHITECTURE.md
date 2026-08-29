# Spec Creator Architecture

## Purpose

This document explains the intended system architecture of Spec Creator as governed specification-to-execution infrastructure. It is descriptive, not promotion authority. Exact repository bytes, frozen contracts, manifests, machine-readable state, receipts, tests, and verifier evidence remain authoritative.

## Architectural objective

Spec Creator is designed to transform uncertain project intent into governed execution while preserving provenance and legal state transitions.

```text
Project intent / evidence
        ↓
Governed discovery
        ↓
Clarified specification + decisions
        ↓
Typed traceability graph
        ↓
Deterministic task graph
        ↓
Prompt/context packages
        ↓
Execution plan / waves / checkpoints
        ↓
Validation and regression evidence
        ↓
Independent verification
        ↓
Reconciliation and release lifecycle
```

Each layer should make unsupported authority harder to introduce and stale authority easier to detect.

## Core architectural layers

### 1. Evidence and intent layer

Captures project goals, constraints, source evidence, explicit assumptions, owner decisions, and unresolved uncertainty. This layer is the source of semantic authority; downstream compilers may normalize or derive from it but must not invent missing owner intent.

### 2. Discovery and clarification layer

Detects ambiguity, dependency-blocked decisions, conflicting constraints, unsafe defaults, and missing measurable bounds. It produces deterministic clarification/default plans with provenance.

Key invariant: unresolved owner decisions remain unresolved work.

### 3. Specification layer

Represents the governed project definition and its accepted decisions. Normative requirements should have measurable acceptance/failure behavior and stable identities suitable for traceability.

### 4. Traceability layer

Connects the specification to execution and verification. The canonical progression is:

```text
Goal → Requirement → Feature → Task → Test → Gate
```

The graph supports reference validation, governed relation transitions, cycle detection, critical-chain completeness, and deterministic impact analysis.

### 5. Compilation layer

Transforms governed semantic artifacts into executable representations:

- task compilation;
- dependency derivation;
- conflict-zone detection;
- safe-parallelism analysis;
- prompt/context compilation;
- validation/gate planning;
- execution-wave construction.

Derived artifacts must record the authoritative inputs and hashes from which they were produced.

### 6. Execution state layer

Execution progress is represented separately from immutable compiled definitions. Append-only events/checkpoints should make it possible to reconstruct legal current state and resume without rewriting historical task meaning.

### 7. Freshness and change-propagation layer

When authoritative inputs change, Spec Creator should identify which derived artifacts lose authority. Reuse is safe only when provenance and identity demonstrate that the relevant inputs are unchanged.

This layer is central to reducing rework without permitting stale context, tasks, tests, prompts, or release evidence to remain silently authoritative.

### 8. Validation and regression layer

Validation checks structural correctness, contract obligations, artifact relationships, metrics, denominators, provenance, package integrity, and other frozen acceptance criteria. Discovered defects become durable regression memory.

Tests and regressions are evidence instruments; they must not be weakened to obtain promotion.

### 9. Independent verification layer

A verifier independently recomputes promotion-authoritative evidence for the exact candidate. Verification is bound to candidate identity, contract identity, test definitions, package membership, dependencies, authoritative artifact set, and verifier criteria.

If any relevant identity changes, the prior recommendation becomes stale for promotion purposes.

### 10. Reconciliation and release layer

The orchestration authority decides whether a candidate is adopted, retried, or rejected after comparing frozen criteria, implementation evidence, verifier evidence, freshness, regression state, and repository reality.

Release packaging, shipping manifests, clean extraction, completion receipts, and version/tag identity belong to this layer.

## Two planes: product evidence and orchestration

Spec Creator intentionally separates two kinds of state.

### Product/release evidence plane

Contains the artifacts that define or prove product behavior: specifications, schemas, traces, fixtures, tests, regressions, frozen contracts, release manifests, transfer evidence, and immutable historical records.

### Orchestration/control plane

Coordinates live autonomous work: current phase, candidate identity, work claims, blockers, handoff receipts, verification freshness, convergence state, and prospective v1 trajectory.

The control plane may point to product evidence but may not rewrite historical evidence. Conversely, prose documentation may explain either plane but cannot become promotion authority.

## Authority boundaries

The architecture is deliberately restrictive at semantic boundaries:

- discovery may propose but not fabricate owner decisions;
- compilers may derive structure only from governed inputs;
- executors may act on compiled authority but not silently redefine it;
- implementing lanes may not independently certify their own promotion;
- verifier findings do not themselves mutate implementation;
- orchestration may reconcile evidence but cannot rewrite frozen history;
- generative or probabilistic helpers may assist analysis only where the frozen contract explicitly permits them and may not silently replace deterministic authority.

## Artifact identity

Promotion-authoritative artifacts should have stable identity that can be mechanically compared. Depending on artifact type, identity may include:

- canonical path;
- stable semantic ID;
- canonical serialization hash;
- source artifact hashes;
- frozen contract hash;
- candidate commit SHA;
- package-manifest membership;
- dependency/lock identity;
- producing tool/version;
- producing lane/actor;
- timestamp when time is part of evidence rather than semantics.

The purpose is not hashing for its own sake. Identity enables stale-state detection and reproducible handoffs.

## Failure model

Spec Creator should fail closed for conditions that would otherwise create false confidence, including:

- missing required evidence;
- stale verifier recommendations;
- unresolved owner decisions;
- invalid trace/dependency structure;
- changed frozen criteria after implementation begins;
- mismatched package membership;
- ambiguous candidate identity;
- missing denominators;
- unverifiable transfer claims;
- interrupted promotion-authoritative transactions;
- overlapping incompatible work authority.

## Scaling direction

The architecture should scale primarily by stronger artifact contracts and incremental recomputation, not by introducing additional competing control planes. Future performance work should preserve exact dependency/provenance semantics while reducing unnecessary recomputation.

## Version 1.00 architectural bar

The v1 system is complete only when the full governed lifecycle is coherent end to end, stale/change propagation is reliable, real transfer claims are supported, clean packaging is reproducible, documentation matches behavior, and an independent verifier recommends release for the exact candidate.
