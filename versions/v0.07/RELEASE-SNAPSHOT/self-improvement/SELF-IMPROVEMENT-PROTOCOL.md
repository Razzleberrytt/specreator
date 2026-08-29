# Controlled Recursive Self-Improvement Protocol

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
