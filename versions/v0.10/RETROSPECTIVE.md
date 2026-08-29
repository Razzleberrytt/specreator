# Spec Creator v0.10 Retrospective — Protocol MVP

**Release decision:** PROMOTED AS EXPERIMENTAL (DEC-0032)  
**Frozen contract:** REL-0.10-FROZEN-001  
**Parent:** v0.09.2 PROMOTED AS EXPERIMENTAL

## What worked
The Protocol MVP composed the promoted deterministic task and prompt boundaries into a single fail-closed orchestration API/CLI. All three frozen projects completed with zero manual artifact reconstruction. Deterministic rerun, exact resume, artifact provenance, and promoted-stage semantic preservation all measured 1.0. The blocker/recovery project remained blocked until append-only recovery evidence was present. Hash-mismatched continuation failed closed. The three separate-context v0.09.2 transfer trials remained valid and intact.

## Defect and regression memory
DEF-010-001 exposed a post-freeze resume defect: after correctly replaying a completed continuation, the initial implementation attempted to execute terminal `done` tasks again. The implementation was corrected without changing any frozen artifact, and REG-0024 permanently requires exact completed-resume preservation plus fail-closed hash mismatch behavior.

## Evidence limits
The three Protocol MVP evaluation projects are intentionally small synthetic governed fixtures. Role-separated verification occurs in the same runtime. External transfer trials establish portability of the v0.09.2 prompt boundary, not population-level causal benefit of the v0.10 orchestration layer. Promotion therefore remains experimental.

## Iteration-hygiene evidence for v0.11+
The cycle exposed avoidable continuation friction: validation profiles are implicit, release sealing is multi-step, immutable boundaries require reconstruction, and internal release snapshots have not always been independently test-runnable. These observations should feed the next unfrozen discovery cycle rather than modifying v0.10 retroactively. Highest-value candidates are a machine-readable lifecycle state, atomic freeze/seal transactions, automatic evidence ingestion, explicit validation profiles, an immutable-artifact registry, checkpoint self-tests, and a measurable handoff-entropy target.

## Next highest-ROI task
Open v0.11 discovery around **Iteration & Continuation Architecture**. Target the invariant that a fresh receiving context should need only the checkpoint package plus `Continue` to identify and execute the next legal action, with no hidden chat reconstruction. Do not freeze v0.11 until this is translated into measurable preregistered criteria.
