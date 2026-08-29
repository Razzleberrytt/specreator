# Version 1.00 Capability Map

## Purpose

This map turns the prospective Version 1.00 contract into a planning view that connects capability, evidence, dependency, and lane responsibility. It does **not** admit successor versions or declare any MUST complete. Current machine-readable trajectory and exact evidence remain authoritative.

## Capability map

| ID | Capability | Primary lane(s) | Required evidence family | Depends on |
| --- | --- | --- | --- | --- |
| V1-01 | Governed specification lifecycle | 2, 3, 5 | End-to-end fixtures + real-project examples + negative owner-intent cases | Restored canonical baseline |
| V1-02 | Discovery and clarification | 2 | Frozen ambiguity/discovery corpora, held-out cases, provenance metrics | Specification model |
| V1-03 | Typed traceability | 2, 3 | Valid/invalid graph corpora, completeness and exact impact results | Stable identities |
| V1-04 | Deterministic task compilation | 2, 3 | Compiler corpus, dependency provenance, conflict/parallelism negatives | Traceability |
| V1-05 | Prompt/context compilation | 2, 3 | Context-closure corpus, authority/prerequisite/owner/verifier negatives | Task + trace authority |
| V1-06 | Execution planning and resume | 3 | Interrupted/resumed streams, append-only replay, exact reconstructed state | Task/prompt compilation |
| V1-07 | Change propagation and freshness | 2, 3, 5 | Mutation matrix, stale invalidation, safe-reuse proofs | Provenance + dependency graph |
| V1-08 | Determinism and provenance | 1, 2, 3 | Repeat-build comparisons, canonical hashes, provenance completeness | Artifact contracts |
| V1-09 | Real-project transfer | 3, 4 | Preregistered separate-context trials with exact denominators | Stable end-to-end workflow |
| V1-10 | Package/install/clean extraction | 1 | Shipping manifest, ownership, clean install/extraction | Release candidate |
| V1-11 | Security and data integrity | 1, 2, 4 | Threat model, adversarial tests, interrupted transaction tests | Stable storage/execution model |
| V1-12 | Regression memory | 1, 2, 4 | Active regression ledger and exact PASS evidence | All adopted defect history |
| V1-13 | Documentation and examples | 3, 5 | Behavior-matched docs, reproducible example project | Stable public workflow |
| V1-14 | CLI/API/workflow usability | 2, 3 | Contract/help tests, structured diagnostics, representative trials | Stable capabilities |
| V1-15 | Independent verification | 4 | Exact-state verifier receipt with freshness basis | Frozen v1 candidate |
| V1-16 | Release lineage and seal | 1, 5 | Reconciled lineage, final manifest/seal/completion receipt | All v1 MUSTs + fresh verification |

Lane numbers indicate primary responsibility, not unilateral phase authority.

## Dependency spine

The highest-level dependency chain is expected to be:

```text
baseline identity
   ↓
canonical governance / artifact contracts
   ↓
specification + discovery
   ↓
traceability
   ↓
task compilation
   ↓
prompt/context compilation
   ↓
execution/resume
   ↓
change propagation + transfer evidence
   ↓
security/usability/docs hardening
   ↓
release candidate
   ↓
independent v1 verification
   ↓
seal + v1.0.0
```

This is a dependency model, not a requirement to create one release per box. Related gaps should be closed with the smallest justified number of successor transactions.

## Evidence classes

### Structural evidence

Schemas, static validation, exact IDs, graph validity, package membership and canonical hashing.

### Behavioral evidence

Deterministic accepted/negative fixtures, replay behavior, change propagation and failure-mode tests.

### Transfer evidence

Preregistered observations from genuinely separate contexts. Transfer claims must preserve exact denominators and uncertainty.

### Operational evidence

Clean installation, extraction, resumability, interrupted transaction recovery and automation behavior.

### Independent evidence

Recomputation by Lane 4 against the exact candidate and freshness basis.

## Prioritization after baseline restoration

Lane 5 should rank remaining objective v1 MUST gaps using evidence, dependency leverage, risk reduction and information value. The default ordering principle is:

1. blockers that prevent trustworthy measurement or promotion;
2. correctness/provenance/freshness gaps that could invalidate later evidence;
3. missing end-to-end lifecycle capabilities;
4. real-project uncertainty needed to establish transfer;
5. packaging/security/usability/documentation hardening;
6. optional performance or presentation work only after MUST completion.

A lower-level capability with many downstream dependents may outrank a user-visible feature because repairing it first prevents invalid evidence and rework.

## Completion semantics

Each row can eventually be tracked as one of:

- `UNASSESSED` — no fresh evidence-based determination yet;
- `GAP_CONFIRMED` — objective missing capability exists;
- `EVIDENCE_REQUIRED` — capability may exist but required proof is insufficient;
- `IN_PROGRESS` — legally admitted work is active;
- `VERIFICATION_REQUIRED` — implementation evidence exists but independent verification is pending/stale;
- `SATISFIED` — objective evidence satisfies the frozen applicable v1 criterion;
- `NOT_APPLICABLE` — only if the frozen v1 contract explicitly excludes it with rationale.

Do not mark a capability SATISFIED from roadmap prose, historical similarity, or unverified implementation.

## Current gate

Until the canonical v0.11.1 baseline is faithfully restored and reconciled, this map remains prospective. It must not be used to justify successor implementation that contaminates the restoration transaction.
