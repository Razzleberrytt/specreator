# Spec Creator v0.08 Continuation State

## Sealed release target

- Candidate: **v0.08 — Task Compiler**
- Decision: **PROMOTED AS EXPERIMENTAL** under DEC-0025
- Contract: `versions/v0.08/FROZEN-RELEASE-CONTRACT.json`
- Canonical frozen contract SHA-256: `460333b394380c6fbc9633ee86fcbff1e91e0c2105b681e51bb9acf5d1b92ec6`
- Promotion ceiling remains experimental because evidence is same-cycle synthetic/process-separated rather than independent external-project evidence.

## Verified release evidence

- complete suite: **142/142 PASS**
- exact sealed v0.07 inherited suite: **119/119 PASS**
- accepted compiler graphs: **24/24 exact**
- held-out accepted graphs: **12/12 exact**
- negative classifications: **36/36 exact**
- execution streams: **16/16 exact**
- critical self-traceability: **13/13 complete**
- self-build compiler output: **7 tasks**, one conflict zone, six dependency edges
- self-build execution replay: **28 events**, all seven tasks end `done`
- active regressions through **REG-0019** present/passing
- frozen metrics: **20/20 PASS**
- mandatory gates: **21/21 PASS**
- independent verifier: **PASS, 37/37 checks true**
- pre-final package rehearsal: **0 errors / 0 warnings**

## Corrective defects preserved

- DEF-008-001 → REG-0017: stale discovery plan cannot hide current ambiguity.
- DEF-008-002 → REG-0018: duplicate source-task metadata cannot overwrite evidence.
- DEF-008-003 → REG-0019: execution/task stable-ID namespaces are path/schema aware.
- DEF-008-004: package rehearsal redirected stdout into the sealed workspace; existing REG-0009 covers the invariant.
- EVT-SC-0113: successor-draft orchestration path error; reinforces LESSON-0008 without changing frozen v0.08 evidence.

## Successor state

`versions/v0.09/SPEC-CREATOR-v0.09-DRAFT.md` is an **unfrozen, unimplemented** evidence-derived Prompt Compiler draft. Its current inherited quality stack is:

- lint findings: 0
- ambiguity findings/questions: 0
- discovery candidates/questions: 0

No v0.09 implementation is authorized yet.

## Next highest-ROI task

Preregister v0.09 Prompt Compiler before implementation:

1. define versioned prompt-envelope and prompt-compilation-input schemas;
2. define five prompt kinds: bootstrap, implementation, debug, verification, continuation;
3. freeze a generic-prompt baseline for corrective-prompt/context-reconstruction comparison;
4. build development + held-out fixtures covering scope attacks, missing prerequisites, unresolved owner decisions, verifier-role separation, continuation handoffs, and context-closure boundaries;
5. include historical v0.08 task/event shapes in non-promotional shadow preflight;
6. preregister denominators for obligation retention, scope expansion, corrective-prompt proxy, continuation exactness, deterministic rendering, and context over-inclusion;
7. parent-preflight every embedded v0.08 graph/task/execution dependency;
8. freeze `FROZEN-RELEASE-CONTRACT.json` before writing Prompt Compiler implementation code.

Do not race to v0.10. A rigorously preregistered v0.09 is higher ROI than accumulating version numbers.
