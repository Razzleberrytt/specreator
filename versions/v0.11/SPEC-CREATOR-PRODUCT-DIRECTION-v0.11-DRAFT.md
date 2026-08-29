# Spec Creator — Product Direction Specification (v0.11 Draft)

**Status:** UNFROZEN PRODUCT-DIRECTION DRAFT. This document describes the forward product target and does **not** alter the current v0.11 preregistration or grant implementation/freeze authority.

## 1. Mission

Spec Creator converts incomplete software objectives into implementation-ready, machine-checkable, verifiable plans that AI coding agents can execute with minimal reconstruction, unnecessary redesign, or wasted wall-clock time.

The long-term product should behave less like a document generator and more like a **specification compiler + execution architect + solution-intelligence system**.

## 2. Primary optimization target

Optimize **time-to-verified-implementation**, subject to hard constraints for:
- correctness;
- safety;
- traceability;
- reproducibility;
- governance;
- provenance/licensing;
- bounded scope;
- independent verification.

Raw task count, source count, token count, apparent concurrency, and implementation speed are not sufficient success metrics by themselves.

## 3. Core product capability families

### 3.1 Discovery and ambiguity resolution
- infer project type and objective;
- identify unknowns, assumptions, and irreversible decisions;
- ask high-information questions;
- distinguish safe defaults from decisions requiring explicit authority.

### 3.2 Specification compilation
- requirements;
- architecture;
- data models;
- interfaces;
- user/system flows;
- risk controls;
- acceptance criteria;
- tests and verification obligations.

### 3.3 Existing-Solution Intelligence & Synthesis (ESIS)
When relevant, Spec Creator should search for existing implementations and knowledge before inventing a solution from scratch.

It should:
1. discover a broad and diverse candidate repository landscape;
2. deduplicate forks/near-clones;
3. qualify sources by relevance, evidence, maturity, activity, test quality, security, license, and provenance;
4. select an **exact top-5 portfolio of distinct qualified repositories related to the specification in progress**;
5. decompose the selected repositories and qualified alternates into comparable capabilities;
6. extract patterns, mechanisms, interfaces, tests, and failure lessons;
7. identify compatibility/conflict constraints;
8. synthesize one or more coherent prototype/reference architectures from the best compatible parts of the five selected repositories;
9. select or combine ideas based on explicit evidence and tradeoffs;
10. distinguish conceptual inspiration from code/component reuse;
11. preserve source/license provenance;
12. independently validate the composite design against blank-slate and strongest-single-repo baselines.

The discovery corpus optimizes for **capability coverage and uniqueness** rather than a fixed size; the prototype-synthesis portfolio is exactly five qualified distinct repositories. If five cannot be found, the system emits `TOP5_SOURCE_SHORTFALL` rather than padding the portfolio.

Detailed doctrine: `docs/EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md`.

### 3.4 Execution architecture
Every implementation-ready output should, where material, derive:
- dependency provenance;
- critical path;
- safely parallelizable workstreams;
- deterministic execution waves;
- minimum-context contracts;
- caching/reuse opportunities;
- latency-overlap opportunities;
- load-balance warnings;
- failure/retry boundaries;
- write/conflict scopes;
- integration contracts.

Detailed doctrine: `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md`.

### 3.5 Agent work-package compilation
Compile the specification and execution architecture into bounded agent prompts/work packages containing only the authority, context, inputs, outputs, constraints, and verification criteria necessary for each task.

### 3.6 Repository intelligence
For brownfield projects, understand the actual repository before specifying changes:
- structure and ownership map;
- architecture extraction;
- interfaces;
- tests;
- dependency graph;
- code/spec drift;
- impact analysis;
- patch planning.

### 3.7 Verification and evaluation science
- preregister success criteria before candidate implementation;
- preserve frozen criteria;
- run independent verification;
- compare matched baselines;
- measure rework, continuation, scope compliance, correctness, and efficiency;
- prevent metric gaming.

### 3.8 Recursive self-improvement
Use the currently promoted version to help specify its successor, while keeping the successor unable to rewrite its own frozen contract or self-certify promotion.

### 3.9 Learning and reusable intelligence
Capture validated lessons as reusable assets:
- regression memory;
- architecture patterns;
- source-quality history;
- integration lessons;
- performance evidence;
- reusable specification modules;
- cacheable project artifacts.

## 4. ESIS reference workflow

`Objective → broad repo landscape discovery → qualification/deduplication → exact top-5 portfolio → capability matrix → pattern extraction → compatibility analysis → top-5 prototype synthesis → selected architecture → execution architecture → implementation packages → verification → learning`

This stage may run partially in parallel with ordinary discovery where dependencies permit.

## 5. Synthesis rules

A synthesized design must be internally coherent. The system must not create a "Frankenstein" implementation by concatenating unrelated codebases.

For every adopted external idea, record:
- what was adopted;
- where it came from;
- why it was selected;
- what alternatives were rejected;
- what assumptions make it compatible;
- how it will be verified;
- whether the reuse is conceptual, interface-level, dependency-level, test-level, or code-level;
- any license/provenance obligations.

Unknown license/provenance fails closed for code reuse.

## 6. Breadth policy

Spec Creator should use as many sources as are **reasonably useful**, where "useful" is governed by marginal information gain.

Discovery expands until:
- key capability areas have adequate coverage;
- major architecture families are represented;
- new sources are predominantly duplicative;
- marginal insight is lower than analysis/integration cost;
- explicit time/resource limits are reached.

The goal is not to stop discovery at two or three sources merely for convenience, and not to ingest hundreds merely because they exist. After discovery saturates, exactly five distinct qualified repositories form the normal ESIS prototype-synthesis portfolio.

## 7. Future evaluation candidates for ESIS

Before ESIS can authorize product claims, preregister matched evaluations for metrics such as:
- capability-coverage improvement versus blank-slate planning;
- unique-pattern recall on governed source corpora;
- source deduplication precision;
- license/provenance classification accuracy;
- architecture incompatibility detection;
- reduction in implementation rework;
- reduction in corrective prompts;
- time-to-verified-implementation;
- security/quality regression rate;
- source-attribution completeness;
- synthesis determinism under identical evidence.

## 8. Governance boundary for current v0.11

ESIS is recorded now because it materially changes the long-term product direction, but **it is not being inserted into the already-prepared v0.11 preregistration gates**.

v0.11 remains focused on iteration/continuation state and execution-efficiency architecture. ESIS implementation is scheduled in the post-alpha existing-solution/repository-intelligence series. This prevents goalpost movement while preserving the idea in the authoritative forward plan.

The normative forward contract for the five-repository prototype portfolio is `versions/v0.11/ESIS-TOP5-PROTOTYPE-AMENDMENT.md`.
