# Lessons Registry

## LESSON-0001 — Recursive improvement requires governance

**Origin:** v0.01 → v0.02 design cycle  
**Observation:** Measurement alone is insufficient if a later version can change its own evaluation criteria.  
**Rule adopted:** Success criteria for a candidate are frozen by the parent/governor before candidate implementation.  
**Regression:** REG-0001.

## LESSON-0002 — Improvement must preserve failure memory

**Origin:** v0.01 → v0.02 design cycle  
**Observation:** A self-improving system can regress if fixes are not converted into durable tests/rules.  
**Rule adopted:** Adopted fixes produce regression memory or an explicit justification for manual-only verification.  
**Regression:** REG-0003.

## LESSON-0003 — Rejection rate is not validator quality

**Origin:** v0.03 implementation cycle  
**Observation:** An over-broad duplicate-ID rule rejected a valid workspace and initially made the validator look stricter.  
**Rule adopted:** Every validator/linter release must pair invalid-case detection with preregistered valid-case false-positive guardrails.  
**Regression:** REG-0004.

## LESSON-0004 — Primary IDs and reference IDs require different semantics

**Origin:** v0.03 implementation cycle  
**Observation:** The same identifier shape may represent record identity or a reference to another record.  
**Rule adopted:** Uniqueness applies to primary record IDs; references are checked for format and resolution, not global uniqueness.  
**Regression:** REG-0004.

## LESSON-0005 — Perfect synthetic scores do not prove compatibility coverage

**Origin:** v0.07 Adaptive Discovery shadow evaluation  
**Observation:** The frozen v0.07 corpus scored perfectly on its intended semantics, yet historical real specifications still exposed two inherited ambiguity false positives.  
**Rule adopted:** Keep a non-promotional historical/real-artifact shadow pass in successor releases and move representative historical shapes into pre-freeze benchmark preflight where practical.  
**Regressions:** REG-0015, REG-0016.

## LESSON-0006 — Safe question reduction requires explicit non-question provenance

**Origin:** v0.07 Adaptive Discovery  
**Observation:** Asking fewer questions is only meaningful when every suppressed question is explained as governed, safely inferred, dependency-blocked, or budget-deferred; otherwise question reduction can hide ambiguity.  
**Rule adopted:** Every discovery action must preserve reason/provenance and unresolved deferrals remain unresolved work.  
**Evidence:** MET-007-001, MET-007-G03, MET-007-G05, MET-007-G06.

## LESSON-0007 — Task definitions and execution history should not be the same record

**Origin:** v0.07 retrospective / v0.08 successor design  
**Observation:** Immutable preregistered task definitions remain marked `planned` even after completion evidence appears in events/tests/gates. Rewriting them would weaken historical integrity.  
**Rule adopted:** v0.08 should compile immutable task definitions and represent execution lifecycle through append-only events.  
**Target:** IMP-0013 / v0.08.

## LESSON-0008 — Per-ledger atomicity is not cross-ledger transactionality

**Origin:** DEF-007-004  
**Observation:** Duplicate-ID protection correctly prevented a bad event append, but earlier valid writes to other ledgers had already committed in the same orchestration.  
**Rule adopted:** When multi-ledger transactional orchestration is introduced, preflight all IDs/schemas before the first mutation and add failure-injection regression coverage.  
**Target:** reliability series v0.12–v0.13.

## LESSON-0009 — Derived plans cannot outrank their source evidence

**Origin:** v0.08 Task Compiler shadow evaluation  
**Observation:** A stale/empty supplied v0.07 discovery plan could appear clean while the current source specification still contained a decision-needed ambiguity.  
**Rule adopted:** Consumers of derived governance plans must reconcile or recompute the parent source condition required for authority; absence in a derived plan is not proof of absence in the source.  
**Regression:** REG-0017.

## LESSON-0010 — Reject duplicate evidence before index construction

**Origin:** v0.08 Task Compiler shadow evaluation  
**Observation:** Building a dictionary from task metadata before duplicate checking allowed a later duplicate `source_task_id` to overwrite earlier evidence silently.  
**Rule adopted:** Validate stable identity uniqueness on the sequence before any lossy map/index transformation.  
**Regression:** REG-0018.

## LESSON-0011 — Stable-ID semantics belong to artifact schemas, not field names alone

**Origin:** v0.08 self-build execution integration  
**Observation:** Generic validation treated every `event_id` as `EVT-*` and every `task_id` as `TASK-*`, rejecting valid frozen execution namespaces `TEVT-*` and compiled-task namespaces `CTASK-*`.  
**Rule adopted:** Stable-ID validation must be path/schema/type aware when artifact families intentionally use distinct namespaces.  
**Regression:** REG-0019.
