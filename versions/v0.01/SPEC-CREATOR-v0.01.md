# Spec Creator v0.01

**Version:** 0.01  
**Status:** Experimental / usable prototype  
**Purpose:** Convert an incomplete project idea into an implementation-ready specification that an AI coding agent can understand, execute, verify, and continue without unnecessary redesign.

## 1. Mission and Principles

Spec Creator reduces development waste caused by unclear requirements, missing decisions, architectural drift, inconsistent implementations, forgotten constraints, weak testing, and unclear completion criteria.

It transforms:

> “I want to build something that does X.”

into:

> “Here is what to build, why it exists, how it behaves, how it is structured, what depends on what, how it will be tested, and how an agent determines completion.”

The system optimizes for implementation clarity. Every specification element must clarify at least one of:

- project purpose and scope
- required or prohibited behavior
- architecture and interfaces
- dependencies and implementation order
- verification criteria
- next agent task
- completion status

Spec Creator must also produce evidence that it is improving the development process. It must measure whether the specification reduces unresolved ambiguity, implementation rework, corrective user prompting, architectural drift, repeated clarification requests, and incomplete or unverifiable work.

All evaluation evidence must be recorded as structured events with stable identifiers, explicit timestamps, consistent classifications, and raw denominators. Derived metrics must never be recorded without the underlying counts needed to reproduce them.

## 2. Workflow

Idea → Discovery → Requirements and scope → Decisions, assumptions, and constraints → Architecture and data model → Flows and feature specifications → Interfaces and edge cases → Tests and acceptance criteria → Quality gates and failure checks → Milestones and tasks → Agent prompts → Implementation and completion audit → Event capture and metric calculation → Evaluation metrics and retrospective.

The system must resolve high-impact ambiguity before implementation rather than immediately generating code.

Each transition between stages must pass the applicable quality gate. A failed gate blocks progression unless the failure is explicitly accepted as a documented risk by the user.

Every material action in the workflow must produce an event record when it affects a task, prompt, clarification, corrective intervention, rework, defect, quality gate, or denominator used in evaluation.

## 3. Project Discovery

Extract the minimum information needed to define the project: project name and type, one-sentence description, target users, problem being solved, primary outcome, success and failure conditions, version-1 requirements, desirable but deferred features, and explicit exclusions.

Infer obvious information when safe. Record unknowns instead of silently guessing.

### Discovery Quality Gate
Pass only when the project has a testable one-sentence description, primary actor, explicit outcome, separated v1/deferred scope, success and failure conditions, and all high-impact unknowns recorded.

### Discovery Failure Conditions
Fail when the objective has materially different interpretations, no primary actor is identifiable, v1 cannot be separated from future ideas, a critical external dependency is unknown, success cannot be evaluated, or the system would need to invent a product decision.

## 4. Requirements, Constraints, and Decisions

Functional requirements use stable IDs and define description, trigger, inputs, expected behavior, outputs, failure behavior, dependencies, and acceptance criteria.

Nonfunctional requirements define measurable properties such as performance, reliability, accessibility, security, privacy, maintainability, scalability, compatibility, and cost.

Constraints are classified Hard, Preferred, or Open.

Maintain explicit Assumptions, Unknowns, and Decisions. Unresolved decisions must not be presented as settled requirements.

### Requirements Quality Gate
Pass only when every in-scope capability is identified, observable, testable, traceable, dependency-aware, and not critically blocked by unresolved decisions.

### Requirements Failure Conditions
Fail on vague or conflicting requirements, untestable behavior, implied critical behavior, silent assumption conversion, unapproved scope expansion, weak acceptance criteria, or missing ownership/dependency/verification paths where needed.

## 5. Architecture and Data Model

Define major components, responsibilities, inputs/outputs, dependencies, interfaces, owned data, and failure modes before tasks.

When relevant, define entities with fields/types, required/optional values, identifiers, relationships, validation, and lifecycle.

### Architecture Quality Gate
Pass when component responsibilities and boundaries are explicit, interfaces and data ownership are defined, dependencies are understandable, hard constraints are satisfied, and at least one feasible implementation path exists.

### Architecture Failure Conditions
Fail on conflicting state ownership, informal-only interfaces, unbounded responsibilities, violated hard constraints, unsupported workflows, blocking unresolved choices, unnecessary infrastructure, or boundaries that permit incompatible implementations.

## 6. Flows and Features

User flows define actor, starting state, ordered behavior, failure paths, and completion state.

Feature specifications define purpose, user story, behavior, UI, edge cases/errors, dependencies, binary acceptance criteria, and tests.

### Flow and Feature Quality Gate
Pass when primary workflows have start/end states, normal/failure paths, requirement mappings, acceptance criteria, explicit state transitions, risk-appropriate edge cases, dependencies, and user-visible states where applicable.

## 7. Interfaces and UX

Define contracts for APIs, functions, events, database interactions, and external services. APIs specify method/route, auth, request/response schemas, errors/status codes, and rate limits where relevant.

UI specifications define navigation, page hierarchy, screen purpose, controls/interactions, loading/empty/success/error states, responsive behavior, and accessibility requirements.

## 8. Edge Cases, Security, and Safety

Attempt to break the design before implementation. Consider malformed/empty input, duplicates, dependency/network failures, interruptions, large data, concurrency, inconsistent state, unauthorized access, secrets, injection/validation risks, abuse, financial/privacy/safety risks, third-party failure, logging, and rate limiting.

High-risk items require mitigation or explicit risk acceptance.

## 9. Testing and Definition of Done

Use appropriate unit, integration, end-to-end, regression, performance, accessibility, security, and manual acceptance verification.

Every important requirement maps to verification.

A feature is complete only when its requirements and acceptance criteria pass, required tests pass, build/lint/type checks pass where applicable, no blocking regressions remain, interfaces stay compatible, and documentation/task status are updated.

## 10. Dependencies, Milestones, and Tasks

Order work by dependency. Milestones represent functioning states, not elapsed time.

Default milestone model:
- M0 Foundation
- M1 Core System
- M2 Usable Product
- M3 Reliability
- M4 Release Candidate
- M5 Production Release

Atomic tasks define objective, affected files/components, requirements, dependencies, implementation notes, acceptance criteria, tests, prohibited scope, and completion output.

## 11. Agent Prompts and Behavior

Generate Bootstrap, Implementation, Verification, Debugging, and Continuation prompts from the specification.

Agents read the overview/current milestone/current task, inspect relevant code, follow approved architecture, stay within scope, run tests, verify acceptance criteria, record significant decisions, update status, and identify the next dependency-safe task.

Agents must not redesign architecture without approval, introduce unjustified frameworks, duplicate functionality, weaken tests, remove difficult requirements, mark incomplete work complete, or broadly refactor without measurable benefit.

## 12. Traceability and Change Control

Maintain Goal → Requirement → Feature → Task → Test.

Requirement changes are recorded, impact-analyzed, reflected in the specification, implemented, and reverified.

## 13. Specification Package

Typical files:
- /spec/00-PROJECT-OVERVIEW.md
- /spec/01-REQUIREMENTS.md
- /spec/02-ARCHITECTURE.md
- /spec/03-DATA-MODEL.md
- /spec/04-USER-FLOWS.md
- /spec/05-FEATURE-SPECS.md
- /spec/06-INTERFACES.md
- /spec/07-UX-UI.md
- /spec/08-SECURITY.md
- /spec/09-TEST-PLAN.md
- /spec/10-MILESTONES.md
- /spec/11-TASKS.md
- /spec/12-TRACEABILITY.md
- /spec/13-DECISIONS.md
- /spec/14-ASSUMPTIONS-AND-UNKNOWNS.md
- /spec/15-QUALITY-GATES.md
- /spec/16-EVALUATION-LOG.md
- /spec/17-EVENT-SCHEMA.md
- /spec/18-METRIC-LEDGER.md
- /agent/AGENT-INSTRUCTIONS.md
- /agent/BOOTSTRAP-PROMPT.md
- /agent/CURRENT-MILESTONE.md
- /agent/CURRENT-TASK.md
- /agent/VERIFICATION-PROMPT.md
- /agent/CONTINUATION-PROMPT.md

Source-of-truth hierarchy:
1. explicit user decision
2. current approved specification
3. architecture decisions
4. feature specifications
5. current implementation task
6. existing implementation
7. agent assumptions

## 14. Quality and Completion Audits

Implementation-readiness requires explicit requirements/exclusions, architecture/dependencies, interfaces, acceptance criteria/tests, implementation order, zero unresolved critical decisions, passed mandatory gates, cleared/accepted critical failures, and evaluation/event/denominator readiness.

Completion requires all requirements/tests/decisions/bugs/deferred features/security/docs/deployment/gates/evaluation records to reconcile.

## 15. Explicit Quality Gates and Failure Policy

Gate statuses: PASS, PASS WITH ACCEPTED RISK, BLOCKED, FAIL, NOT APPLICABLE.

Critical failures are those capable of materially different implementations, data loss/corruption, security/privacy/financial/safety harm, unverifiability, major architectural rework, or inability to determine completion. Critical failures block implementation or release.

Failed gates are recorded, classified, assigned corrective action/owner, rerun, and recorded again. Failed gates cannot be silently downgraded.

## 16. Event Logging and Counting Procedure

Use a common append-only event log as the authoritative process-evaluation source.

Canonical event records require stable IDs, project ID, UTC event/recorded timestamps, actor, controlled event type/version, phase, classification, severity, status, inclusion flag, evidence, and links to relevant artifacts.

Controlled classifications include normal, specification_clarification, implementation_defect, specification_defect, agent_execution_error, user_scope_change, external_dependency_failure, environment_failure, intentional_architectural_change, unrelated_maintenance, measurement, and administrative.

Canonical event families include project/baseline, task, prompt, rework, defect, gate, and measurement events.

Lifecycle events use opening events as counts; closing events update status rather than incrementing the count again.

Corrections append a new correction/superseding event rather than mutating history.

At evaluation checkpoints: load events to cutoff, validate, remove superseded from active counts, deduplicate, classify, construct entity sets, create denominator snapshot, calculate raw numerators, derive metrics, reconcile lifecycle totals, record metric calculation, record missing data, and review risk/scope/incomplete-data impacts.

A metric is invalid if numerator and denominator use different cutoffs, scopes, baselines, or effort units.

## 17. Measurable Evaluation Framework

Evaluate against a comparable baseline whenever practical.

Core metric families:
- ambiguity reduction
- rework
- corrective prompting
- agent autonomy
- specification quality
- efficiency
- user experience

Representative targets:
- zero unresolved critical ambiguity at implementation start
- ambiguity density ≤ 0.25/task Standard
- clarification request rate ≤ 0.30/task
- ambiguity escape ≤ 10% Standard / ≤ 5% Exhaustive
- rework task rate ≤ 15% Standard / ≤ 10% Exhaustive
- rework effort ≥ 30% lower than baseline
- architectural rework ≤ 10% Standard / ≤ 5% Exhaustive
- corrective prompts ≥ 30% lower than baseline
- repeated clarification ≤ 5%
- first-pass task success ≥ 70% Standard / ≥ 85% Exhaustive
- independent verification ≥ 90%
- continuation success ≥ 90%
- scope compliance ≥ 95%
- critical traceability/verification/decision closure = 100%
- overall traceability/verification ≥ 95%
- total delivery effort ≥ 20% lower after protocol maturation

Every reported metric includes raw numerator, denominator, cutoff/scope, missing-data status, and source snapshot.

## 18. Evaluation Protocol

Maintain project type/complexity, operating mode, agent model/version, baseline details, initial idea, spec duration, user questions, gate results, tasks, clarifications, corrective prompts, rework, architecture changes, defects, tests, completion, metrics, evaluator notes, limitations, schema version, denominator snapshots, ledger records, missing data, and reconciliation.

Evaluation is invalid when metrics lack raw counts, baseline differences are hidden, later-session rework is omitted, corrective prompts are counted inconsistently, failed tests are hidden, criteria change after results, missing data is treated favorably, critical gates are bypassed, snapshots cannot be reproduced, or different effort units are compared as equivalent.

## 19. Minimum Acceptance Threshold for v0.01

Initial validation requires at least three different projects: small utility/script, standard application/website, and high-complexity/integration-heavy project.

Pass only if zero critical ambiguities remain at implementation start, traceability ≥ 95%, critical verification = 100%, corrective prompts and rework effort are each ≥ 20% lower than baseline/prior workflow, first-pass task success ≥ 70%, scope compliance ≥ 90%, no critical gate bypass occurs, and evaluation logs/denominators reconcile.

## 20. Operating Modes

Quick: lightweight spec with discovery, requirements, scope, task acceptance criteria, verification, and minimum evaluation logging.

Standard: full workflow, all mandatory quality gates and core metrics.

Exhaustive: alternatives/risk analysis, detailed interfaces, threat modeling, expanded edge cases/task graphs, adversarial review, independent verification, and full baseline comparison where practical.

## 21. v0.01 Interaction Model

AI-conversation protocol:
User idea → ambiguity/requirements → preliminary gates → high-impact questions → decisions/scope → generated/audited spec → mandatory gates → tasks/prompts → implementation → event capture → denominator snapshots → metric calculation → reconciliation/review.

No graphical application is required.

## 22. v0.01 Master Prompt

Role: requirements-engineering and software-planning system for autonomous AI coding agents.

Objective: provide enough structured context to build, test, verify, continue, and measure the project while minimizing guessing, drift, rework, corrective prompting, and ambiguity escape.

Method:
1. determine objective
2. extract explicit requirements
3. infer conservatively
4. separate facts/assumptions/unknowns/decisions
5. define scope/constraints
6. resolve high-impact ambiguity
7. define architecture/data/interfaces/flows
8. define features
9. define acceptance criteria/tests
10. analyze edge cases/failures/security/safety
11. build dependency-aware milestones/tasks
12. generate agent prompts
13. apply quality gates
14. record gate outcomes
15. audit traceability/evaluation readiness
16. record implementation events append-only
17. use stable identifiers/classifications
18. snapshot denominators
19. calculate metrics from raw events
20. reconcile metrics
21. compare with baseline or disclose limitation

Interaction: ask only high-value questions; infer safe defaults; never guess through material financial/security/privacy/safety ambiguity.

Completion: do not call a spec implementation-ready, an implementation complete, or Spec Creator validated until its corresponding mandatory conditions are actually met.

## 23. Success Criterion

Spec Creator v0.01 succeeds when an AI coding agent can understand constraints, identify the next task, implement consistently, verify work, require less correction, avoid unnecessary refactoring, resume across sessions, pass gates with less intervention, measurably reduce ambiguity/rework/corrective prompting, and generate an auditable event history from which metrics can be reproduced.

## 24. Future Development

Potential future capabilities include protocol testing, automatic requirement extraction, ambiguity detection, dependency graphs, prompt generation, linting, drift detection, repository-aware updates, interactive UI, synchronized state, automated event classification/baseline comparison, statistical analysis, rework prediction, agent gate enforcement, schema validation, denominator reconciliation, cross-project aggregation, evaluator agreement analysis, and tamper-evident event storage.

## Current Status

Spec Creator v0.01 exists as an unproven protocol. Its next job is to run against real projects, preserve complete raw events and denominators, compare with baselines where possible, measure failures, and use those findings to specify v0.02.
