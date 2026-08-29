# Spec Creator v0.10 — Protocol MVP (Unfrozen Discovery Draft)

**Status:** DISCOVERY / PREFREEZE BLOCKED ON EXTERNAL-TRANSFER EVIDENCE. No v0.10 implementation is authorized.
**Parent:** v0.09.2 Prompt Compiler, PROMOTED AS EXPERIMENTAL under DEC-0030.

## Objective

Integrate the promoted deterministic capabilities into one end-to-end protocol boundary: intake → governed specification → validation → traceability → ambiguity/discovery → task compilation → bounded prompts → append-only execution evidence → metrics/reconciliation. The MVP must compose existing contracts rather than bypass or reinterpret them.

v0.10 must also address the principal evidence limitation inherited from v0.09.2: same-cycle synthetic prompt fixtures do not establish that compiled prompts reduce reconstruction or corrective rework when handed to a genuinely separate execution context.

## Prefreeze evidence blocker

Before a v0.10 frozen release contract may be created, at least three transfer trials must be completed outside the v0.09.2 implementation context. Each trial must use a sealed v0.09.2 compiled prompt plus its declared evidence only. The receiving context must not receive hidden reconstruction help from the v0.09.2 implementation session.

The transfer protocol is preregistered in `versions/v0.10/TRANSFER-EVIDENCE-PROTOCOL.json`. Missing transfer trials remain missing evidence; synthetic substitutes may not satisfy this blocker.

## Proposed requirements

### REQ-010-D01 — End-to-end composition
Provide a deterministic API/CLI orchestration path that composes existing promoted stages without weakening their validation, blockers, identities, or hashes.

### REQ-010-D02 — Artifact contract
Every stage transition must consume a versioned machine-readable artifact or an explicitly governed source input. No stage may reconstruct required upstream state from prose when a promoted artifact exists.

### REQ-010-D03 — Fail-closed stage boundaries
A failed/missing prerequisite stage must block downstream executable authority. Partial output may be diagnostic evidence but may not be treated as a successful pipeline result.

### REQ-010-D04 — Resume and continuation
The MVP must resume from persisted artifacts/events without manual artifact reconstruction and must reject incompatible or hash-mismatched continuation state.

### REQ-010-D05 — End-to-end provenance
The final run record must identify the exact spec, trace graph, discovery state, compiled task graph, prompt envelopes, event streams, metric evidence, and version/schema identities used.

### REQ-010-D06 — Existing capability preservation
The orchestrator must call or faithfully compose the promoted validator/linter/traceability/ambiguity/discovery/task/prompt/event/metric semantics. It may not create a second weaker implementation path solely to make end-to-end fixtures pass.

### REQ-010-D07 — Three-project evaluation
At least three preregistered evaluation projects must complete end-to-end without manual artifact reconstruction. Projects must exercise materially different paths, including one blocker/failure-recovery path and one continuation/resume path.

### REQ-010-D08 — External transfer evidence
At least three separate-context v0.09.2 prompt-transfer trials must be completed before freeze. Report reconstruction requests, corrective prompts attributable to missing/incorrect compiled context, scope escapes, obligation loss, and completion status. Missing trials block freeze.

### REQ-010-D09 — Historical integrity
Exact v0.09.2 sealed-parent behavior and every active regression through REG-0023 must remain passing. v0.09/v0.09.1 failed history and all frozen historical artifacts remain immutable.

### REQ-010-D10 — Release governance
Before implementation, freeze exact schemas, evaluation projects, transfer evidence, denominators, thresholds, parent preflight, success criteria, and contract hashes. Post-freeze defects become regression memory; criteria may not be weakened.

## Proposed evaluation emphasis

Primary MVP evidence should measure end-to-end completion without manual reconstruction, exact artifact provenance, deterministic rerun/resume, and preservation of promoted stage semantics. Safety guardrails include zero critical gate bypasses, zero scope/owner/prerequisite escapes, zero hidden manual artifact reconstruction, zero historical mutation, and exact parent/regression preservation.

Transfer evidence is a **prefreeze dependency**, not a metric that can be fabricated from same-session synthetic fixtures. It exists to determine whether v0.09.2 prompts are portable enough to serve as the orchestration boundary for v0.10.

## Non-goals

- no replacement of promoted component algorithms merely for orchestration convenience;
- no autonomous architecture/product decisions;
- no multi-agent scheduler;
- no repository intelligence beyond existing explicit inputs;
- no claim of external causal benefit from same-session synthetic evidence;
- no implementation before the transfer blocker and normal preregistration gates are green.
