# v0.06.1 Retrospective — Ambiguity Engine Governed Retry

**Release decision:** PROMOTED AS EXPERIMENTAL  
**Parent:** v0.05  
**Failed predecessor candidate:** v0.06 — RETRY REQUIRED  
**Frozen contract:** `REL-0.06.1-FROZEN-001`  
**Contract canonical SHA-256:** `2ae4073dc197c73386d07b9746d38d807a1d9c038b56aae6a68c7c16a53fbf27`

## What worked

v0.06.1 turns ambiguity handling from informal prompting into deterministic pre-implementation analysis. It classifies six preregistered ambiguity families, separates owner decisions from governed defaults, links findings to v0.05 traceability impact, ranks bounded questions deterministically, and evaluates a clarification-interception proxy without treating missing evidence as success.

The retry process itself was at least as important as the feature. The original frozen v0.06 corpus could not satisfy its own parent-traceability gate. Instead of repairing frozen fixtures in place, the system preserved v0.06 as RETRY REQUIRED, recorded REG-0008, created a separate semantically equivalent retry corpus, parent-validated all 16 embedded graphs, and froze a new v0.06.1 contract.

Final frozen synthetic results are perfect: 24/24 defect cases detected, 20/20 clean cases accepted, 76/76 expected classifications exact, 8/8 priority choices exact, 16/16 synthetic workflow clarification triggers intercepted, zero governed-default questions, zero unnecessary questions, and zero critical ambiguity escapes. All 12 critical v0.06.1 requirements have complete Goal → Requirement → Feature → Task → Test → Gate paths.

## What failed during the cycle

### DEF-006-001 — invalid frozen v0.06 benchmark dependencies
All 16 graph-backed cases violated the promoted parent traceability schema. v0.06 was failed rather than rewritten. **REG-0008** now requires successor benchmark dependencies to pass promoted-parent executable validators before freeze.

### DEF-006-002 — stale live shipping manifest
The top-level manifest still represented an earlier release after legitimate successor work. **REG-0009** moves mutable package sealing to the final release step.

### DEF-0061-001 — malformed preregistration ledger append
A helper proposed requirement/task records with the wrong schema fields. Exact malformed evidence was preserved. **REG-0010** requires schema validation before append and byte-identical failure behavior.

### DEF-0061-002 — duplicate stable IDs from overlapping interrupted passes
The resumed workspace contained two different v0.06.1 preregistration sequences under the same event/requirement/task/decision/experiment/improvement IDs. Exact pre-repair bytes were preserved in defect evidence; the active ledger retained the occurrences matching the immutable frozen contract. **REG-0011** rejects duplicate existing IDs before append.

### DEF-0061-003 — “pending” false positive
The initial implementation treated `zero pending records` as an unresolved specification state. The clean frozen fixture caught it. The implementation now distinguishes unresolved status (`mode is pending`) from ordinary domain adjective usage. **REG-0012** preserves both sides of the distinction.

### DEF-0061-004 — evaluator pointed to obsolete transient plan hash
The evaluator initially carried a transient preregistration hash rather than the hash embedded in the final immutable retry contract. The contract was not changed; evaluator configuration was corrected. **REG-0013** cross-checks evaluator constants, artifact bytes, and frozen contract failure conditions.

### DEF-0061-005 — corrupted v0.05 release-snapshot README
Final historical verification exposed a 267-byte explanatory file where v0.05's immutable snapshot required the release-time root README. The exact displaced bytes were preserved. The historical README was recovered without guessing by reversing only known successor README edits; the recovered 4,974-byte content exactly matched the SHA-256 already declared by the frozen v0.05 manifest. **REG-0014** now requires historical snapshot content to match its declared release hash instead of allowing a damaged snapshot to mask history.

## Why the recursive protocol saved work

The strongest result is procedural: two tempting shortcuts were blocked. First, v0.06 could not silently repair an invalid frozen benchmark. Second, the `pending records` false positive could not be dismissed by weakening a clean-case fixture. In both cases the frozen evidence forced the implementation/process to change instead of the target.

The protocol also exposed a new class of recursive-system risk: **the evidence machinery itself can become the source of defects**. Duplicate event IDs, malformed ledger writes, obsolete evaluator hashes, and stale package manifests are not product-domain ambiguity bugs, but they can make evidence untrustworthy. Those failures now have executable regression memory.

## Where the protocol created overhead

Release accounting remains manually repetitive. Raw events are translated into denominator snapshots, metric records, gates, scorecards, experiment results, manifests, snapshots, and retrospectives. This cycle produced multiple clerical/process defects around exactly that boundary. A future evidence/release compiler remains high-value, but it should be introduced under its own frozen contract rather than bypassing the roadmap opportunistically.

## Final evidence

- 72 frozen retry cases; hashes unchanged after freeze
- 16/16 graph-backed retry fixtures pass v0.05 parent preflight
- 24/24 defect cases detected
- 20/20 clean cases accepted
- 76/76 candidate classifications exact
- 8/8 priority cases exact
- 16/16 synthetic workflow triggers intercepted
- 0/64 unnecessary questions
- 0 critical ambiguity escapes
- 12/12 critical self-traceability paths complete
- 84/84 inherited v0.05 test modules PASS
- 100/100 complete v0.06.1 tests PASS
- REG-0001–REG-0009 frozen applicable set PASS
- REG-0010–REG-0014 new regression memory PASS
- 14/14 frozen primary + guardrail metrics PASS
- 16/16 mandatory gates PASS
- independent-role verification PASS
- final workspace validation before shipping seal: 0 errors / 0 warnings

## Limitation and classification

The benchmark is synthetic and visible to the implementer. The clarification metric measures interception of preregistered synthetic triggers, not observed reduction in real implementation conversations. The verifier is role-separated but in the same runtime/session. Therefore the frozen ceiling applies: **PROMOTED AS EXPERIMENTAL**, not fully promoted.

## What v0.07 should learn

The roadmap's Adaptive Discovery direction remains correct, but v0.06.1 changes its emphasis. v0.07 should optimize **information value per question**, not raw question count. Safe inference must be explicit and reversible; defaults need traceable provenance; question suppression must be penalized when it causes ambiguity escape. Evaluation should include held-out clean/ambiguous project scenarios and, if possible, a small real-project shadow evaluation before any claim of reduced owner burden.
