# Spec Creator v0.04 — Spec Linter (Draft)

**Status:** Draft successor specification; **not frozen and not implemented**  
**Parent:** v0.03 (promoted as experimental)

## Evidence-derived objective

Detect specification defects before implementation while keeping false-positive burden low enough that agents do not learn to ignore the linter.

The v0.03 cycle added one important design constraint: rule engines must distinguish context and references from primary declarations. REG-0004 showed that a broad syntactic rule can look rigorous while rejecting valid input.

## Candidate scope

Initial linter rule families:

- vague or non-testable requirement language
- missing acceptance criteria
- missing failure behavior for critical operations
- unresolved critical decisions
- undefined referenced interfaces/entities
- orphan requirements with no verification path
- contradictory requirement pairs
- task descriptions too broad for bounded implementation
- unbounded component responsibilities
- implementation assumptions not approved or explicitly marked exploratory

## Required v0.04 evaluation design

Before implementation, create a frozen contract with:

- seeded defective-spec corpus
- seeded clean-spec corpus
- per-rule precision/false-positive metrics
- severity calibration
- exact-span/rationale output requirements
- rule suppression governance
- inherited REG-0001 through REG-0004
- rollback to v0.03
- independent verifier pass

## Non-goals for the first v0.04 candidate

No semantic embeddings, model-dependent scoring, GUI, automatic rewriting of specs, or repository-aware code analysis unless evidence shows a deterministic rule cannot reasonably cover the required behavior.

## Next highest-ROI task

Design and preregister the **v0.04 lint rule corpus and clean-spec counterexample corpus**, then freeze the v0.04 release contract before writing linter code.
