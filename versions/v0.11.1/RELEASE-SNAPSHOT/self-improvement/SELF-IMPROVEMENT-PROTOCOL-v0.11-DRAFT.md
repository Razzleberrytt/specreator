# Controlled Recursive Self-Improvement Protocol — v0.11 Draft

**Status:** UNFROZEN successor protocol amendment. The v0.10-bound shared protocol remains immutable.

## Core Loop

Observe → Diagnose → Propose → Pre-register → Freeze → Implement → Verify → Measure → Adopt/Reject → Add Regressions → Specify Next Version.

## Roles

**Parent Spec Creator:** defines successor spec and freezes release contract.  
**Implementation Agent:** builds the candidate; cannot rewrite frozen criteria.  
**Verifier:** checks correctness against frozen criteria.  
**Evaluator:** reconciles metrics and recommends promotion/rejection.  
**User/Governor:** approves breaking changes, critical risk acceptance, and promotion where required.

## Promotion Rule

A candidate is never promoted merely because it is newer or more elaborate. Promotion requires evidence that it satisfies frozen release criteria and does not violate critical guardrails.

## Learning Rule

Every meaningful failure must end in one of four dispositions:
1. fixed + regression added
2. accepted risk + owner/justification
3. deferred + explicit target
4. rejected as non-actionable/noise

Unclassified failure observations are process debt.

## Recursive Version Rule

Version N may generate Version N+1's candidate specification, but:
- version N+1 cannot rewrite its own frozen contract
- evaluation must use data recorded after freeze under declared rules
- failed experiments remain visible
- prior applicable critical regressions persist
- breaking changes require explicit governance

## Local Optimization Defense

Always pair a primary improvement metric with guardrails. Example:

Primary goal: reduce user clarification requests.  
Guardrails: ambiguity escape must not increase; rework must not increase; critical decision closure remains 100%.

This prevents "improvement" by simply asking fewer questions and allowing more mistakes later.


## Execution Efficiency Rule

Beginning with unfrozen v0.11 discovery, recursive improvement must consider the **cost and wall-clock architecture of the development loop itself**, not only candidate feature quality.

Before freezing a successor where implementation effort is material, identify:

- unnecessary work that can be eliminated;
- reusable/cached valid artifacts;
- true dependency DAG and critical path;
- safely independent workstreams and execution waves;
- context and I/O that can be minimized or batched;
- load imbalance / straggler risk;
- safe preparatory/speculative work;
- failure/retry boundaries;
- integration/merge contracts.

Efficiency claims require paired guardrails. Example:

Primary goal: reduce time-to-verified-implementation.  
Guardrails: no increase in critical ambiguity escape, scope escape, architectural rework, verification failure, unsafe parallelization, hidden reconstruction, or governance violations.

Synthetic graph structure can validate dependency and scheduling correctness, but it cannot by itself prove real wall-clock savings. Provider/runtime-dependent claims require declared empirical execution evidence.


## Existing-Solution Reuse Rule

Recursive improvement must not assume Spec Creator has to invent every mechanism itself. Before proposing a material new architecture or engine, inspect applicable internal history and, when permitted and useful, relevant external implementations, standards, libraries, research, and documented failures.

The process must:
- search for diverse approaches rather than a single fashionable implementation;
- deduplicate near-equivalent sources;
- qualify a broad candidate corpus and then select an exact portfolio of five distinct repositories most relevant and complementary to the active successor specification;
- distinguish claims from demonstrated evidence;
- extract reusable principles/patterns before considering direct code reuse;
- synthesize the prototype/reference design from the strongest compatible parts of the selected five;
- preserve source/version/license/provenance information for every adopted element;
- compare compatibility with Spec Creator's frozen contracts and governance model;
- record why a pattern was adopted or rejected;
- independently verify the composite against blank-slate and strongest-single-repository baselines.

Discovery source count is not an improvement metric. The discovery stopping rule is marginal information gain versus analysis/integration cost; the **five-repository portfolio is a fixed prototype-synthesis contract after discovery**, not a quality metric. If fewer than five qualified repositories exist, emit `TOP5_SOURCE_SHORTFALL` rather than padding. External precedent cannot rewrite frozen criteria or justify bypassing preregistration. Detailed doctrine: `docs/EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md` and `versions/v0.11/ESIS-TOP5-PROTOTYPE-AMENDMENT.md`.
