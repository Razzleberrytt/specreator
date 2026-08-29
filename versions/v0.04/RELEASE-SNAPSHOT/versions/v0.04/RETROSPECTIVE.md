# v0.04 Retrospective

**Release decision:** PROMOTED AS EXPERIMENTAL  
**Frozen contract:** `REL-0.04-FROZEN-001`  
**Contract hash:** `2e512511159fd20d432b143f2093e84001eb8857f5b3db151c0654a89eea3010`

## What worked

v0.04 turned the first natural-language quality controls into executable code without introducing model-dependent scoring. The deterministic Markdown profile made the rules reproducible, and the frozen matched corpus forced each rule to prove both defect detection and clean-case precision.

The strongest design choice was treating false positives as a first-class guardrail. The frozen corpus contained five defect cases and five clean counterexamples for each of LINT-001 through LINT-010. Final results were 50/50 defect cases detected, 50/50 clean cases accepted, 56/56 emitted findings expected, and 56/56 findings with complete source spans and rationales.

The frozen hash lock on the corpus and evaluation plan also worked: implementation could not alter the benchmark after seeing results.

## What failed

Two failures occurred outside the lint rules themselves.

### DEF-004-001 — historical manifest self-invalidation

As soon as legitimate v0.04 records were added, the v0.03 manifest began failing because it had hashed shared files that successors are expected to change. The original validator implicitly assumed current shared paths must remain identical to the prior release forever.

The repair distinguishes two historical integrity modes:

- append-only ledgers must retain the exact historical byte prefix in the live ledger; and
- mutable shared source is verified against an immutable version-local `RELEASE-SNAPSHOT` captured from the prior release package.

This became **REG-0005**.

### DEF-004-002 — accidental JSONL historical-byte rewrite

The first preregistration helper scripts parsed entire JSONL ledgers and rewrote them while adding new records. The logical historical records were unchanged, but their JSON serialization/order changed, violating the append-only history invariant.

The untouched v0.03 parent ZIP allowed exact byte-for-byte restoration of every affected prefix. v0.04 records were then appended after the restored prefix. A dedicated `append_jsonl_records` helper now appends bytes without rewriting prior content and rejects duplicate primary IDs before writing.

This became **REG-0006**.

## Why the protocol mattered

Both defects are examples that a conventional “tests green” workflow could easily miss. The historical-manifest defect appeared because the recursive cycle immediately exercised the system across a version boundary. The byte-rewrite defect was caught because the manifest prefix check cared about historical bytes, not merely equivalent parsed JSON.

Neither failure was hidden, and neither caused the frozen release contract or corpus to be weakened.

## Linter capability delivered

v0.04 adds deterministic detection for:

1. vague/non-testable wording;
2. missing acceptance criteria;
3. missing failure behavior on critical mutating operations;
4. unresolved critical decisions;
5. undefined referenced interfaces/entities;
6. requirements without verification paths;
7. contradictory deterministic constraints;
8. overly broad tasks;
9. unbounded component responsibilities; and
10. ungoverned implementation assumptions.

Diagnostics include source line, column, exact span, severity, and rationale. Constraint contradictions include the related prior line.

Local suppression is governance-bound: an explicitly supplied approved `DEC-*` can suppress one local rule finding. Unknown/unapproved or invalid blanket suppressions cannot hide the defect.

## Evidence

- Full automated suite: **49/49 PASS**
- Inherited v0.03 tests: **30/30 PASS**
- Frozen inherited regressions REG-0001–REG-0004: **4/4 PASS**
- New history-regression scenarios for REG-0005/REG-0006: **6/6 PASS**
- Suppression governance scenarios: **3/3 PASS**
- Frozen defect cases: **50/50 detected**
- Frozen clean cases: **50/50 accepted**
- Finding precision: **56/56 = 100%**
- Diagnostic completeness: **56/56 = 100%**
- Minimum per-rule precision: **100%**
- Workspace validator before release packaging: **0 errors / 0 warnings**
- Mandatory gates: **12/12 PASS**

## Where the specification was weak

The initial v0.04 draft assumed the v0.03 historical manifest model was already recursion-safe. The pre-freeze cycle disproved that assumption. Because the defect was found before the v0.04 contract existed, the dependency repair could be added without goalpost movement.

The linter itself deliberately supports a bounded deterministic Markdown profile. It does not prove robust understanding of arbitrary prose, subtle semantic contradictions, or repository context.

## Overhead

Hand-authored release ledgers, denominator records, gates, scorecards, and snapshots remain verbose. This is increasingly strong evidence that later roadmap versions should compile these artifacts from lower-level events rather than rely on repeated manual record construction.

## Retained changes

Retain:

- deterministic rule architecture;
- clean-counterexample requirement per rule;
- exact-span/rationale diagnostics;
- governed local suppressions;
- frozen corpus hash locking;
- historical release snapshots;
- live-prefix enforcement for append-only history;
- byte-preserving JSONL append helper;
- REG-0005 and REG-0006.

## What v0.05 should learn

The roadmap's Traceability Engine remains the correct next capability. v0.04 also shows that traceability must distinguish **current mutable state** from **historical immutable evidence** and must never infer coverage simply because an identifier string exists.

v0.05 should build a machine-readable Goal → Requirement → Task → Test → Gate graph, identify broken/orphan relationships, enforce complete critical traceability in a frozen graph corpus, and provide impact analysis. The v0.04 linter should be used to lint the v0.05 specification itself before v0.05 is frozen.

## Limitation and release classification

The frozen benchmark is synthetic and visible to the implementer. There is no measured independent-project reduction in rework, clarification, or implementation defects yet. For that reason the frozen contract explicitly caps v0.04 at **PROMOTED AS EXPERIMENTAL**.
