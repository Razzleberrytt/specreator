# v0.05 Retrospective — Traceability Engine

**Release decision:** PROMOTED AS EXPERIMENTAL  
**Frozen contract:** `REL-0.05-FROZEN-001`  
**Contract canonical SHA-256:** `c3d9588520221b8b8440d296bf3da5f2cbf7b43751b1725299b576f16efb3ca5`

## What worked

v0.05 converted identifier-level references into an executable typed delivery graph. The new engine can parse and validate Goal → Requirement → Feature → Task → Test → Gate chains, reject invalid transitions and broken references, detect cycles and incomplete critical chains, and compute deterministic upstream/downstream impact.

The strongest improvement over v0.04 is that **traceability is now semantic rather than nominal**. A requirement string appearing in a task or test is not enough. For a critical requirement to count as complete, an actual governed ordered path must exist.

The frozen benchmark also worked as intended. The corpus and evaluation plan were created and hash-locked before implementation. Final verification reproduced both hashes exactly and obtained perfect frozen metrics without modifying the benchmark.

The system was dogfooded on v0.05 itself. `TRACEABILITY-GRAPH.json` contains all ten critical v0.05 requirements, and the executable validator reports 10/10 complete critical paths with zero diagnostics.

## What failed

### DEF-005-001 — impact result ordering mismatch

The first full implementation test run was **74 passed / 8 failed**. Graph validation itself was correct, but impact analysis returned the correct members in lexical ID order rather than in the preregistered delivery-chain order.

All five frozen impact cases therefore failed exact-match evaluation. The dependent corpus and CLI tests failed with them.

The contract and corpus were not modified. The implementation was changed so impact outputs are ordered by governed node type:

`Goal → Requirement → Feature → Task → Test → Gate`

with stable-ID ordering only as a tie-breaker inside the same node type.

The correction became **REG-0007**.

## Why the protocol mattered

This failure is small in code but important procedurally. A looser workflow could have declared the output an unordered mathematical set and changed the expected fixtures after seeing the result. The frozen benchmark prevented that reinterpretation.

The process forced a clearer API contract: deterministic impact output includes both membership and order. That gives downstream tools reproducible JSON rather than semantically equivalent but unstable output.

## Final frozen evidence

- frozen corpus: **30 cases**
- invalid cases: **20/20 detected**
- valid + impact graphs: **10/10 accepted**
- critical requirements in frozen accepted graphs: **10/10 complete**
- exact impact cases: **5/5**
- invalid-case diagnostic precision: **20/20 = 100%**
- valid graph false positives: **0**
- v0.05 specification linter findings: **0**
- inherited v0.04 automated suite: **49/49 PASS**
- complete v0.05 automated suite: **83/83 PASS**
- applicable inherited regressions REG-0001–REG-0006: **PASS**
- new REG-0007: **PASS**
- v0.05 self-trace graph: **10/10 critical requirements complete**
- pre-release workspace validation: **0 errors / 0 warnings**
- mandatory release gates: **12/12 PASS**
- independent-role verifier: **PASS**
- critical gate bypasses: **0**

## What the engine now does

The executable v0.05 layer provides:

- versioned traceability graph JSON schema;
- typed node and relation validation;
- duplicate node detection;
- duplicate directed-edge detection;
- broken-edge reference detection;
- governed relation/type transition validation;
- cycle detection across primary and preregistered auxiliary relations;
- first-missing-stage diagnostics for critical requirements;
- complete ordered critical traceability paths;
- deterministic upstream/downstream impact analysis;
- importable Python API;
- CLI validation, impact, and frozen-corpus evaluation commands;
- exact frozen evaluation metrics with denominator preservation.

## Where the specification was weak

The v0.05 spec said impact analysis should compute upstream and downstream "sets", while the frozen corpus encoded deterministic ordered arrays. The benchmark made the intended behavior executable, but the prose specification should have stated that canonical serialization order is part of the interface contract.

That is not severe enough to invalidate the frozen contract because the preregistered corpus unambiguously defined the expected output before implementation. It should nevertheless inform future specs: where deterministic machine output matters, ordering rules should be explicit in prose and machine fixtures.

## Where the protocol still creates overhead

Release evidence remains partly hand-assembled. Events, denominator snapshots, metric records, gates, scorecards, experiment results, manifests, snapshots, and retrospectives are individually useful, but manually producing all of them is repetitive and introduces clerical risk.

The evidence from v0.03 through v0.05 increasingly supports a future **evidence compiler / release compiler** that derives higher-level records from raw immutable events instead of requiring repeated manual transcription. This should not displace the roadmap's next capability unless it becomes a blocking reliability issue.

## Limitation and release classification

The traceability benchmark is synthetic and visible to the implementation actor. The verifier is role-separated from implementation but runs in the same local session/runtime. No independent software project has yet demonstrated reduced implementation rework, clarification, or defect escape because of the traceability engine.

Therefore the frozen contract's promotion ceiling applies: **PROMOTED AS EXPERIMENTAL**.

## What v0.06 should learn

The roadmap's **Ambiguity Engine** remains the correct next product capability.

v0.05 suggests three requirements for it:

1. ambiguity findings must link to concrete requirement/task nodes rather than float as untraceable prose comments;
2. false-positive and "unnecessary question" rates must be explicit guardrails, because over-detecting ambiguity can create more work than it saves; and
3. v0.06 should evaluate not only classification accuracy but whether ambiguity resolution reduces downstream clarification or rework on a preregistered evaluation set.

A strong v0.06 should distinguish ambiguity that requires an owner decision from ambiguity that can safely use a governed default.
