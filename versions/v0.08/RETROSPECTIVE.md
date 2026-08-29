# Spec Creator v0.08 Retrospective — Task Compiler

**Release decision:** PROMOTED AS EXPERIMENTAL (DEC-0025)  
**Frozen contract:** REL-0.08-FROZEN-001  
**Parent:** v0.07 PROMOTED AS EXPERIMENTAL

## What worked

v0.08 crossed an important boundary from *describing work* to compiling governed work. The normalized Task Compiler deterministically converts already-approved source-task and traceability evidence into immutable atomic task records, dependency edges, conflict zones, parallel-safety decisions, verification/gate provenance, and a stable topological execution order. Execution state is kept outside those definitions in append-only graph-hash-bound events.

The preregistration discipline worked well. The approved v0.08 specification failed its inherited linter before freeze because three write-scope requirements lacked explicit failure behavior. Those defects were corrected before REL-0.08-FROZEN-001 existed, then the exact spec, schemas, 60-case compiler corpus, 30-case held-out partition, 16 execution streams, evaluation plan, and parent preflight were hash-locked. No frozen target was edited after implementation began.

The frozen evaluator is strong on its intended semantics: 24/24 accepted graphs, 12/12 held-out accepted graphs, 36/36 negative classifications, all dependency/provenance/parallel/atomicity guardrails, and 16/16 execution streams match exactly. The release also dogfoods its compiler on a real 13-requirement v0.08 trace graph, producing seven atomic tasks and replaying 28 execution events against an immutable graph hash.

Independent verification reproduced all frozen hashes, 142/142 current tests, the exact 119/119 sealed-parent baseline, 13/13 critical self-traceability, exact self-compilation, and execution replay.

## What failed

Three meaningful implementation/integration defects escaped the perfect synthetic benchmark:

1. **DEF-008-001 / REG-0017:** a stale or empty supplied discovery plan could hide ambiguity present in the source specification. The compiler now recomputes parent ambiguity state and requires decision-needed candidates to be represented instead of trusting a derived plan as authority.
2. **DEF-008-002 / REG-0018:** duplicate `source_task_id` metadata could be silently overwritten during dictionary construction. Duplicate metadata IDs are now rejected before indexing.
3. **DEF-008-003 / REG-0019:** the generic validator coupled stable-ID formats to field names and rejected the frozen `TEVT-*` / `CTASK-*` execution namespaces. Stable-ID rules are now path/schema aware.

A fourth release-engineering mistake, **DEF-008-004**, occurred when the first package-rehearsal command redirected its own stdout into the workspace being sealed. That changed a file immediately after hashing it and produced two manifest mismatches. The failure was preserved and rerun correctly with output outside the workspace. Existing REG-0009 already covers the underlying manifest-last/no-post-seal-mutation invariant, so a duplicate regression was not added.

The combined promotion/successor helper also committed valid release records before failing because `versions/v0.09/` did not yet exist. No records were retried or rewritten; v0.09 creation was split into a separate step. This reinforces LESSON-0008: per-file append safety is not orchestration transactionality.

## What caused rework

Most rework did **not** come from ambiguous product intent. It came from integration boundaries that synthetic fixtures abstracted away: freshness/authority of derived discovery artifacts, duplicate metadata before map construction, namespace assumptions in shared validation, and release-orchestration sequencing. That is useful evidence that the next gains are increasingly about artifact authority and end-to-end integration rather than adding more prose requirements.

## Where the specification was weak

The frozen specification correctly required unresolved discovery actions to block compilation, but it did not explicitly say that a supplied discovery plan must be proven fresh/reconciled to the current source spec. REG-0017 now captures the stronger rule.

The specification required stable deterministic IDs but did not explicitly state that different artifact types may own different valid namespaces for semantically similar fields. REG-0019 captures that compatibility requirement.

The specification intentionally did not solve natural-language task decomposition. v0.08 therefore assumes source task boundaries already exist in the normalized input. That is a conscious non-goal, not evidence that automatic decomposition works.

## Where the protocol saved work

- Parent preflight caught spec-quality defects before freeze.
- Frozen corpora prevented post-result benchmark editing.
- Non-promotional shadow evaluation found two bugs that perfect frozen scores missed.
- Self-dogfood exposed a shared-validator integration bug before release.
- Regression memory converted all three product defects into permanent checks.
- Role-separated verification prevented the implementation pass from being the sole release authority.
- Manifest rehearsal caught a release-sequencing mistake before the immutable shipping seal.

## Where the protocol created overhead

The release has many evidence artifacts and repeated validations. Some are redundant at human-reading level, but they currently provide machine-reconcilable proof that hashes, denominators, tests, gates, and package state agree. The highest-value future reduction is not deleting evidence; it is compiling these release operations into a transactional/reproducible runner during the reliability series.

## Retain

- normalized deterministic task IR;
- trace-derived dependencies rather than inferred architecture;
- owner-decision fail-closed behavior;
- explicit atomicity bounds and `needs_spec_refinement` rather than automatic splitting;
- conflict-zone and conservative parallelization rules;
- immutable task definitions plus append-only execution events;
- held-out + shadow evaluation separation;
- exact sealed-parent regression baseline;
- manifest-last shipping discipline.

## Reject / defer

- automatic architectural task splitting;
- probabilistic dependency invention;
- treating derived discovery state as more authoritative than source specification;
- mutable status fields inside compiled task definitions;
- claims that perfect same-cycle synthetic scores prove real-project rework reduction.

## What v0.09 should learn

The Prompt Compiler should compile bounded role-specific context from v0.08 task/execution evidence rather than rebuilding context manually. It must bind every prompt to graph/task identity, preserve exact write scope and critical obligations, refuse blocked/prerequisite-incomplete tasks, separate verifier authority from implementation authority, make continuation state reproducible, and minimize context only through explainable deterministic closure. A generic-prompt baseline and held-out/historical shadow corpus should be frozen before implementation so “shorter prompts” cannot be mistaken for better prompts when they silently omit constraints.
