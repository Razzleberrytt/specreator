# Existing-Solution Intelligence & Synthesis Architecture

**Status:** UNFROZEN forward-looking product architecture captured during v0.11 discovery. It does not alter v0.11 preregistered promotion obligations.

## Purpose

Spec Creator should not assume every implementation begins from a blank sheet. For many software objectives, mature open-source projects, libraries, reference implementations, standards, papers, vendor examples, and prior internal work already contain useful solutions to parts of the problem.

The target capability is **Existing-Solution Intelligence & Synthesis (ESIS)**: discover relevant existing solutions, compare them systematically, extract reusable architectural knowledge, and synthesize a stronger implementation blueprint without blindly copying or mechanically merging sources.

ESIS is an efficiency and quality multiplier. It can reduce unnecessary invention, expose known failure modes, improve architecture selection, surface proven interfaces, and generate better implementation hypotheses before expensive coding begins.

## Core principle

> Search broadly, select deliberately, extract patterns, preserve provenance, synthesize cleanly, and validate the result independently.

The objective is **maximum useful solution coverage during discovery**, followed by an **exact top-5 qualified repository portfolio for prototype synthesis**.

A larger discovery corpus is beneficial only while additional sources contribute unique capabilities, architectures, performance techniques, failure lessons, tests, interfaces, or evidence. Near-duplicate forks and low-information sources increase context, I/O, legal review, and integration cost without increasing useful coverage. The fixed count applies to the final prototype-synthesis portfolio, not to discovery.

## ESIS pipeline

### Stage 0 — Relevance decision

Before discovery, determine whether external or prior-solution intelligence is useful for the current objective.

Skip or narrow ESIS when:
- the task is trivial;
- the design is intentionally novel and precedent would bias discovery;
- privacy or policy constraints prohibit external lookup;
- the problem is already bounded by an authoritative internal implementation;
- discovery cost clearly exceeds expected reuse value.

### Stage 1 — Solution landscape discovery

Search across appropriate source classes, which may include:
- open-source repositories;
- package/library ecosystems;
- official SDKs and reference implementations;
- standards/specifications;
- academic or engineering papers;
- benchmark projects;
- prior internal repositories/specifications;
- issue trackers, postmortems, and documented failure cases.

Discovery should favor diversity across:
- architecture;
- language/runtime;
- maturity;
- execution model;
- performance strategy;
- dependency profile;
- deployment model;
- maintenance model.

### Stage 2 — Deduplication and source qualification

Detect forks, mirrors, abandoned copies, generated clones, and materially equivalent sources.

For each retained source, record at minimum where available:
- stable source identifier and version/commit;
- license and reuse constraints;
- activity/maintenance signals;
- documentation quality;
- test coverage/evidence;
- security posture or known advisories;
- architectural scope;
- claimed versus demonstrated performance;
- relevant strengths;
- known limitations;
- confidence in extracted conclusions.

Source popularity is evidence, not authority.

### Stage 3 — Top-5 portfolio selection and capability decomposition

After broad discovery, deduplication, and qualification, select exactly five distinct qualified repositories that together best cover the active specification. Optimize portfolio complementarity and unique useful contribution, not stars or five independent scalar ranks. If fewer than five qualified distinct repositories exist after reasonable exhaustive discovery, emit `TOP5_SOURCE_SHORTFALL` and do not claim a compliant top-5 synthesis.

Normalize the selected sources—and enough qualified alternates to justify selection—into a comparable capability model. Do not compare entire repositories as indivisible units.

Example capability dimensions:
- data ingestion;
- scheduling;
- execution;
- state management;
- retry/recovery;
- caching;
- concurrency;
- observability;
- security;
- validation/testing;
- configuration;
- interface design;
- deployment;
- performance optimization.

This creates a **capability matrix** showing which source is strongest, weakest, or distinctive in each dimension.

### Stage 4 — Pattern and mechanism extraction

Extract reusable knowledge at multiple levels:
1. **Principles** — broad design lessons.
2. **Patterns** — recurring architecture or workflow structures.
3. **Mechanisms** — algorithms, protocols, state machines, retry rules, queues, caching strategies, etc.
4. **Interfaces/contracts** — useful boundaries and schemas.
5. **Tests/benchmarks** — ways to verify the behavior.
6. **Failure lessons** — defects, limitations, and anti-patterns to avoid.
7. **Components** — code-level candidates only when reuse is appropriate and license-compatible.

Patterns should be preferred over direct code reuse when the same benefit can be obtained more safely through independent implementation.

### Stage 5 — Compatibility and conflict analysis

Before combining ideas, identify incompatibilities such as:
- conflicting state models;
- incompatible concurrency assumptions;
- different trust boundaries;
- inconsistent data models;
- mutually exclusive dependencies;
- incompatible licenses;
- runtime/platform mismatch;
- contradictory performance tradeoffs;
- incompatible security models.

A feature that works well in one source is not automatically composable with another.

### Stage 6 — Top-5 prototype synthesis candidate generation

Generate one or more candidate prototype/reference architectures from the strongest compatible ideas across the exact five-repository portfolio. The compliant prototype path must preserve all five repository identities and show what each contributed or why a selected source's candidate contribution was rejected during compatibility analysis.

Each adopted idea should carry:
- source/provenance reference;
- capability addressed;
- reason for selection;
- alternatives considered;
- compatibility assumptions;
- integration contract;
- verification requirement;
- reuse mode: concept, pattern, interface, test, dependency, or code component.

The synthesis should be a coherent architecture, not a pile of favorite parts.

### Stage 7 — Clean-room / license-aware implementation plan

Before implementation, classify every reused element:
- **idea/pattern only** — independently implement from documented behavior;
- **permissively reusable component** — preserve required notices and obligations;
- **dependency** — consume through its public contract;
- **restricted/incompatible** — use only as a behavioral reference or exclude;
- **unknown license/provenance** — fail closed for code reuse.

Spec Creator must never infer that public source code is automatically unrestricted for copying.

### Stage 8 — Composite blueprint validation

Validate the synthesized design independently against:
- project requirements;
- architecture consistency;
- dependency correctness;
- security constraints;
- license/provenance constraints;
- integration complexity;
- expected performance;
- testability;
- maintainability;
- time-to-verified-implementation.

Where practical, compare the composite blueprint against:
- a blank-slate baseline;
- the strongest single-source adaptation;
- alternate synthesis candidates.

### Stage 9 — Evidence and learning capture

After implementation, record which borrowed patterns actually helped and which caused rework. Feed this evidence back into future source scoring and synthesis decisions.

## Corpus breadth and top-5 stopping/selection rule

ESIS should search broadly enough to reach **capability saturation**, then choose an exact five-repository prototype portfolio.

A practical policy is:
1. discover a diverse initial corpus;
2. score, qualify, and deduplicate it;
3. map unique capabilities/patterns;
4. expand discovery toward uncovered or weakly supported dimensions;
5. stop discovery when new sources add negligible unique information relative to analysis/integration cost;
6. from the qualified non-duplicate corpus, choose exactly five repositories whose combined utility and complementarity best cover the active specification;
7. synthesize the prototype from the best compatible parts of that five-repository portfolio.

The fixed number **five** is therefore a prototype-synthesis contract, not a discovery cap.

## Source scoring model

A future implementation may score sources using a weighted model such as:

`utility = relevance × evidence_quality × uniqueness × compatibility × maintainability × provenance_confidence - analysis_cost - integration_risk`

No single scalar score should suppress important outliers. A lower-ranked source may remain valuable if it contains a unique mechanism or failure lesson.

## Relationship to execution efficiency

ESIS extends the existing efficiency doctrine in `docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md`.

It can improve:
- **algorithm optimization** by exposing better known approaches;
- **parallelism** by revealing proven decomposition patterns;
- **latency** by surfacing established batching/async designs;
- **partitioning** through known sharding/domain boundaries;
- **context/I/O efficiency** by reusing validated abstractions rather than rediscovering them;
- **caching/reuse** by extending reuse beyond current-project artifacts;
- **failure isolation** by learning from mature recovery designs;
- **integration efficiency** by borrowing proven contracts and adapters.

ESIS should itself use parallel discovery and analysis where safe: independent sources can be inspected concurrently, then normalized through a shared comparison contract.

## Required machine-readable outputs (future)

A mature implementation should emit:
- `solution-landscape.json`
- `source-provenance.json`
- `repo-qualification-ledger.json`
- `top-five-repo-portfolio.json`
- `capability-matrix.json`
- `pattern-catalog.json`
- `compatibility-matrix.json`
- `synthesis-candidates.json`
- `selected-reference-architecture.json`
- `prototype-provenance-map.json`
- `reuse-and-license-plan.json`
- `synthesis-verification-plan.json`

## Anti-patterns

Never:
- choose sources solely by stars/popularity;
- assume newer means better;
- treat README claims as benchmark evidence;
- combine components without interface/conflict analysis;
- copy code before checking license/provenance;
- keep adding discovery sources after useful coverage saturates;
- confuse the exact top-5 prototype portfolio requirement with a claim that source count itself measures quality;
- let external precedents override explicit user requirements;
- adopt a pattern without a verification obligation;
- claim a composite design is superior before testing it.

## Success condition

ESIS succeeds when Spec Creator can demonstrate that its synthesized blueprint is more complete, compatible, traceable, and/or efficient to implement than a reasonable blank-slate or single-reference baseline **without increasing legal/provenance risk, architectural rework, or verification failure**.

Detailed top-5 prototype contract: `versions/v0.11/ESIS-TOP5-PROTOTYPE-AMENDMENT.md`.
