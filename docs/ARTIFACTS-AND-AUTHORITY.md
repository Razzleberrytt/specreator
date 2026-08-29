# Artifact and Authority Reference

## Purpose

Spec Creator relies on many files, but not every file has the same authority. This reference defines how to reason about them without turning documentation into a competing control plane.

## Artifact classes

### Historical immutable evidence

Examples: frozen contracts, preserved failed experiments, historical release snapshots, historical regression records, sealed package evidence, prior verifier receipts.

Rule: never rewrite these to make later work appear successful. Corrections happen through additive successor/retry evidence.

### Active candidate authority

Examples: the currently frozen candidate contract, exact candidate commit, authoritative candidate artifacts, candidate test definitions, dependency/lock identity.

Rule: implementation must remain within the frozen scope. Changes to promotion-authoritative identity invalidate handoffs or verification as defined by freshness rules.

### Derived execution artifacts

Examples: trace graphs, compiled task graphs, prompt/context packages, execution plans, validation plans, impact reports.

Rule: derived artifacts must preserve provenance to their authoritative inputs and become stale when relevant source authority changes.

### Runtime/execution history

Examples: append-only task/execution events, checkpoints, transfer observations.

Rule: execution history records what happened; it must not retroactively rewrite immutable task/spec meaning.

### Verification evidence

Examples: independent recomputation results, verifier receipts, freshness basis, release recommendation.

Rule: verification applies only to the exact identity it covers. Historical PASS remains historical evidence, but stale PASS cannot authorize a changed state.

### Release/package evidence

Examples: package ownership classifications, authoritative shipping manifest, clean-extraction evidence, package hashes, completion receipts, changelog/release notes.

Rule: authoritative shipping evidence is produced only in the correct release context and must reflect exact shipping membership.

### Orchestration/control-plane state

Examples: `ops/spec-creator-state.json`, `ops/work-claims.json`, `ops/V1-TRAJECTORY.json`, handoff/freshness registries when present.

Rule: these coordinate current legal work. They may reference historical/product evidence but may not rewrite it. Major phase advancement belongs to the canonical orchestration authority.

### Explanatory documentation

Examples: README, architecture docs, roadmap prose, tutorials.

Rule: documentation explains the system. It does not authorize release or override exact machine evidence.

## Authority resolution

When artifacts disagree, first identify the exact claim in dispute. Authority is claim-scoped rather than globally assigned to whichever file is newest.

Use this resolution process:

1. **Historical claim?** Use the immutable frozen/sealed evidence that governed that historical transaction.
2. **What bytes are actually in GitHub now?** Use exact repository tree/commit content.
3. **What phase is legally active now?** Use canonical machine-readable orchestration state after checking whether that state itself is stale against repository reality.
4. **Who owns current work?** Use live claims plus exact owner activity and staleness policy.
5. **Can a candidate be promoted?** Use its frozen contract, exact candidate identity, required evidence, regressions, and fresh independent verifier receipt.
6. **What ships?** Use the authoritative shipping manifest created in the release/seal context, not a convenient root manifest or prose list.
7. **What should happen next?** Use the current legal transition and v1 trajectory after reconciliation.

Never resolve a contradiction by choosing the newer artifact merely because it is newer.

## Freshness matrix

A prior verifier recommendation should be considered stale for promotion when any verifier-required input changes, including:

| Input | Why it matters |
| --- | --- |
| Candidate SHA | Candidate bytes changed |
| Frozen contract hash | Acceptance authority changed |
| Required tests/test definitions | Evidence instrument changed |
| Package membership/manifest | Shipping identity changed |
| Dependency lock/identity | Executed environment changed |
| Promotion-authoritative artifact set | Scope of verified evidence changed |
| Verifier-required criteria | Verification obligation changed |

Additional inputs may be included by a frozen contract. Freshness must fail closed rather than assuming equivalence.

## Handoff receipt minimums

A machine-readable phase-boundary receipt should bind at minimum:

- receipt ID/hash;
- exact candidate SHA;
- frozen contract hash;
- authoritative artifact set;
- changed artifact set;
- validation/test evidence;
- metric definitions and denominators when applicable;
- producing lane/actor;
- timestamp;
- intended consumer;
- receipt type/phase boundary.

Receipts are append-only evidence. They do not themselves authorize a phase transition.

## Work claim minimums

A work claim should include:

- unique task ID;
- owner lane;
- scope;
- candidate/release identity;
- conflict key or incompatible scopes;
- claimed/updated/heartbeat time;
- status;
- expiry/staleness policy.

Claims prevent duplicate incompatible work. They are not locks for stealing active work and they are not release authority.

## Documentation staleness procedure

If prose disagrees with authoritative evidence:

1. do not mutate product/release state to match prose;
2. identify the exact stale statement;
3. update documentation in a focused change;
4. preserve historical wording only where needed to document historical context;
5. link prose to the canonical source of truth instead of duplicating volatile values where practical;
6. if machine-readable state itself disagrees with exact repository reality, record that as a control-plane defect and reconcile it through the correct owner/authority.

## Prohibited authority shortcuts

Do not:

- use README status text to promote a release;
- treat an issue checkbox as evidence that a frozen criterion passed;
- reuse verification after candidate identity changes;
- infer shipping membership from directory contents when an authoritative manifest is required;
- rewrite a failed experiment into success;
- silently remove a regression;
- alter a denominator after freeze;
- treat absence of evidence as zero defects;
- treat a generated summary as more authoritative than the exact artifacts it summarizes.

## Design principle

The system should make the legal source of authority discoverable and mechanically checkable. Whenever humans or agents must guess which artifact is authoritative, that is a governance design smell worth eliminating.
