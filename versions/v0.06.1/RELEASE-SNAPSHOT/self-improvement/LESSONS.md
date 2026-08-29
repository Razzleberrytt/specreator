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
