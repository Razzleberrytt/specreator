# Spec Creator Roadmap — v0.01 to v1.00

## Roadmap Philosophy

The roadmap is **capability-gated, not calendar-gated**. A version advances only when its exit criteria are met. Versions may be skipped, merged, or split only through a recorded roadmap decision.

Every version N is, where practical, used to specify version N+1. The parent version freezes the successor's release contract before implementation.

## v0.01 — Measured Specification Protocol
**Theme:** Make specification quality observable.  
**Core:** requirements, architecture, flows, interfaces, gates, tasks, prompts, traceability, event logging, metrics.  
**Exit:** complete unproven protocol exists.

## v0.02 — Controlled Recursive Improvement
**Theme:** Make improvement itself spec-driven.  
**Adds:** improvement ledger, experiment registry, frozen successor contracts, regression corpus, independent evaluation, anti-gaming rules, release manifests.  
**Exit:** complete successor spec and recursive governance model exist.

## v0.03 — Executable Schemas and Validator
**Theme:** Make protocol artifacts machine-checkable.  
**Build:** JSON Schemas for events, requirements, tasks, gates, metrics, release contracts; schema validator CLI/library.  
**Exit:** invalid core artifacts are automatically rejected; schema migration strategy exists.

## v0.04 — Spec Linter
**Theme:** Detect weak specifications automatically.  
**Build:** rules for vague language, missing acceptance criteria, orphan requirements, undefined interfaces, unresolved critical decisions, test gaps.  
**Exit:** seeded defect corpus demonstrates useful precision/recall and low false-positive burden.

## v0.05 — Traceability Engine
**Theme:** Build and verify Goal → Requirement → Feature → Task → Test graph.  
**Build:** machine-readable graph, orphan detection, impact analysis, change propagation warnings.  
**Exit:** 100% critical traceability enforcement in test corpus.

## v0.06 — Ambiguity Engine
**Theme:** Identify ambiguity before agents encounter it.  
**Build:** ambiguity taxonomy, severity scoring, conflict detection, decision-needed classifier, question prioritizer.  
**Exit:** measurable reduction in implementation-time clarification on evaluation projects.

### v0.06 execution note — 2026-08-24

The first frozen v0.06 candidate was **RETRY REQUIRED** before implementation because 16/16 graph-backed benchmark fixtures were invalid under the promoted v0.05 traceability schema. Under DEC-0015 the semantic benchmark and thresholds were preserved, only parent-schema-invalid graph fields were repaired in a separately frozen **v0.06.1** retry, and the failed v0.06 artifacts remain immutable. v0.06.1 subsequently met its frozen criteria and was **PROMOTED AS EXPERIMENTAL**. REG-0008 permanently requires parent-validator preflight before successor freeze; REG-0009 requires shipping-manifest-last release sequencing.

## v0.07 — Adaptive Discovery
**Theme:** Ask fewer, better questions.  
**Build:** information-value question selection, safe inference, default proposals, project-type intake profiles.  
**Exit:** question efficiency improves without worsening ambiguity escape.

## v0.08 — Task Compiler
**Theme:** Compile specs into dependency-safe atomic work.  
**Build:** task decomposition, dependency DAG, conflict zones, parallelization rules, task-complexity bounds.  
**Exit:** task graph is executable with no critical circular dependencies or unresolved product decisions.

## v0.09 — Prompt Compiler
**Theme:** Generate bounded agent prompts directly from task context.  
**Build:** bootstrap/implementation/debug/verification/continuation prompt generation with context minimization.  
**Exit:** prompts preserve scope/criteria/constraints and beat generic prompts on corrective-prompt rate.

## v0.10 — Protocol MVP
**Theme:** End-to-end CLI/library prototype.  
**Build:** intake → spec → validate → tasks → prompts → events → metrics.  
**Exit:** three evaluation projects complete end-to-end without manual artifact reconstruction.

## v0.11–v0.19 — Reliability Series
**Theme:** Harden the MVP.
- 0.11 deterministic IDs and artifact references
- 0.12 crash-safe state/resume
- 0.13 event reconciliation engine
- 0.14 migration/version compatibility
- 0.15 change-impact engine
- 0.16 merge/conflict awareness
- 0.17 reproducible evaluation runner
- 0.18 independent verifier workflows
- 0.19 reliability audit and consolidation

**Exit for 0.19:** no critical integrity failures across the validation corpus.

## v0.20 — Alpha
**Theme:** First coherent productized system.  
**Adds:** stable CLI, project workspace, validator/linter/traceability/task/prompt/evaluation commands.  
**Exit:** external-style user can operate from docs without the original designer reconstructing context.

## v0.21–v0.29 — Repository Intelligence
- repo ingestion and structure map
- existing-architecture extraction
- interface discovery
- test discovery
- code/spec drift signals
- repository-aware change impact
- safe patch planning
- continuation-state generation
- consolidation

**v0.29 exit:** Spec Creator can reliably understand an existing medium repo before specifying changes.

## v0.30 — Repository-Aware Beta Foundation
**Theme:** Specs become synchronized with real code state.  
**Exit:** detected drift is evidence-backed, traceable, and reviewable.

## v0.31–v0.39 — Evaluation Science
- matched baseline runner
- project complexity normalization
- effort-unit normalization
- confidence intervals where sample size allows
- evaluator agreement
- metric sensitivity analysis
- anti-gaming audit
- cross-project aggregation
- consolidation

**v0.39 exit:** claims of improvement are statistically and procedurally defensible for the available corpus.

## v0.40 — Closed-Loop Improvement Beta
**Theme:** Automatically propose evidence-backed protocol improvements.  
**Constraint:** proposals only; no autonomous promotion.  
**Exit:** proposals link to raw evidence, predicted metrics, risks, and preregistered experiments.

## v0.41–v0.49 — Regression Intelligence
- automatic regression proposal from failures
- reproducer capture
- regression deduplication
- severity/applicability inference
- regression retirement governance
- historical replay
- cross-version compatibility suite
- failure-cluster analysis
- consolidation

## v0.50 — Midpoint Release
**Theme:** Measured recursive system.  
**Exit:** at least three successful recursive version cycles, no critical recurrence of adopted regression fixes, and full auditability.

## v0.51–v0.59 — Multi-Agent Coordination
- planner/implementer/verifier role contracts
- shared contract ownership
- parallel task conflict prediction
- merge sequencing
- disagreement resolution
- scoped handoffs
- agent performance attribution
- multi-agent evaluation
- consolidation

## v0.60 — Multi-Agent Beta
**Theme:** Spec Creator coordinates multiple coding agents without contract drift.  
**Exit:** parallel evaluation demonstrates lower wall-clock effort without increased architectural rework.

## v0.61–v0.69 — UX and Productization
- interactive project setup
- visual gates/status
- traceability browser
- decision inbox
- evaluation dashboard
- diff/review UI
- regression explorer
- export/import bundles
- consolidation

## v0.70 — Product Beta
**Theme:** Usable beyond protocol enthusiasts.  
**Exit:** non-expert user can create an implementation-ready package with bounded assistance.

## v0.71–v0.79 — Extensibility
- project-type profiles
- custom gate plugins
- custom metric plugins
- agent/provider adapters
- schema extensions
- organization policies
- reusable spec modules
- template marketplace format (local/open format)
- consolidation

## v0.80 — Extensible Release Candidate Foundation
**Theme:** Stable extension contracts.  
**Exit:** core remains deterministic under third-party profiles/plugins.

## v0.81–v0.89 — Security, Governance, and Provenance
- signed/fingerprinted release contracts
- tamper-evident event chains
- permission boundaries
- sensitive-data policies
- audit export
- policy-as-code gates
- supply-chain checks
- adversarial self-improvement tests
- consolidation

## v0.90 — Release Candidate
**Theme:** Feature freeze for 1.0.  
**Exit:** all intended 1.0 capabilities present; only defects, evidence gaps, and usability blockers remain.

## v0.91–v0.99 — Validation and Hardening
- 0.91 broad project corpus
- 0.92 high-complexity integrations
- 0.93 brownfield repositories
- 0.94 multi-agent stress testing
- 0.95 failure/recovery drills
- 0.96 security/provenance audit
- 0.97 docs/onboarding audit
- 0.98 final metric reconciliation
- 0.99 1.0 readiness audit and frozen release contract

## v1.00 — Validated Spec Compiler
**Definition:** A stable, auditable system that converts incomplete software ideas or change requests into machine-checkable specifications, dependency-safe tasks, bounded agent prompts, verification plans, synchronized state, and evidence-backed improvement proposals.

### v1.00 Mandatory Exit Criteria
- zero unresolved critical ambiguities at implementation start across release validation corpus
- 100% critical requirement traceability and verification coverage
- ≥95% overall traceability and verification coverage
- ≥90% independent verification success
- ≥95% scope compliance
- ≥90% continuation success
- statistically/operationally defensible improvement over baseline on rework and corrective prompting
- all critical regressions pass
- no critical quality gate bypass
- reproducible release metrics from raw event logs
- documented rollback/migration strategy
- stable public schemas/CLI/API contracts
- complete security/provenance review
- successful recursive self-specification cycle for v1.00 from v0.99 without evaluator reconstruction of missing context

## What 1.00 Does NOT Mean

v1.00 does not mean Spec Creator is finished forever. It means the protocol and product contracts are stable enough that future 1.x improvements preserve compatibility and are governed by the same evidence-driven recursive loop.

### v0.07 execution note — 2026-08-24

v0.07 Adaptive Discovery was **PROMOTED AS EXPERIMENTAL** under DEC-0022. The frozen 72-case benchmark reduced 92 immediate parent questions to 40 governed question batches (56.52% reduction), achieved 24/24 exact information-value selections and 47/47 held-out action matches, and recorded zero unsafe defaults or critical ambiguity escapes. The exact v0.06.1 parent baseline remained 100/100 tests passing; the final v0.07 suite is 119/119. A required non-promotional real-spec shadow evaluation exposed two inherited false positives not represented in the synthetic corpus; the fixes became REG-0015 and REG-0016 without changing frozen v0.07 evidence. v0.08 remains Task Compiler, with added evidence-derived constraints for unresolved-discovery blockers, event-sourced task execution state, historical-shape preflight, conflict zones, and deterministic task-complexity bounds.

### v0.08 execution note — 2026-08-24

v0.08 **Task Compiler** met REL-0.08-FROZEN-001 and was **PROMOTED AS EXPERIMENTAL** under DEC-0025. It adds deterministic normalized task compilation, trace-derived dependency provenance, owner-decision blocking, atomicity/refinement bounds, conflict zones, conservative parallelization, critical coverage, immutable graph hashing, and append-only execution replay. The complete suite is 142/142 PASS and the exact v0.07 baseline is 119/119 PASS. Three post-freeze shadow/self-integration defects became REG-0017 through REG-0019 without modifying frozen targets. The evidence-derived v0.09 Prompt Compiler draft remains unfrozen and unimplemented pending baseline/schema/corpus preregistration.

### v0.10 discovery checkpoint — 2026-08-24

v0.10 Protocol MVP discovery is open under DEC-0031, but freeze and implementation are deliberately blocked until three genuinely separate-context v0.09.2 prompt-transfer trials satisfy `versions/v0.10/TRANSFER-EVIDENCE-PROTOCOL.json`. This preserves the v0.09.2 retrospective's evidence limit instead of substituting same-session synthetic success. After transfer evidence is complete, v0.10 must still preregister its exact orchestration schemas, three-project evaluation corpus, denominators, thresholds, parent preflight, and frozen contract before implementation.
