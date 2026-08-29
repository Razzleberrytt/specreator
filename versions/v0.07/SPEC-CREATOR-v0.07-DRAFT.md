# Spec Creator v0.07 DRAFT — Adaptive Discovery

**Status:** Unfrozen evidence-derived draft only  
**Parent if pursued:** v0.06.1 PROMOTED AS EXPERIMENTAL

## Goal

Reduce owner-question burden by selecting the highest-information unresolved decisions first and proposing safe, reversible defaults where governance permits, without increasing ambiguity escape or downstream rework.

## Evidence from v0.06.1

The Ambiguity Engine can deterministically identify and rank decision-needed findings on a frozen synthetic corpus, but it currently asks one bounded question for every decision-needed finding. Perfect synthetic interception does not show that every question is worth asking immediately. v0.06.1 also demonstrated that false positives and evidence-pipeline defects can erase apparent efficiency gains.

## Candidate capability scope

- information-value scoring over decision-needed ambiguity candidates;
- dependency-aware question batching and stopping rules;
- explicit safe-inference policy with reversible proposed defaults;
- provenance for every inferred/defaulted value;
- project-type intake profiles that alter question relevance without silently changing owner intent;
- escalation when confidence/impact crosses a preregistered threshold;
- deterministic API/CLI output suitable for later task/prompt compilers.

## Candidate guardrails

- no critical ambiguity escape increase versus v0.06.1 baseline;
- unnecessary-question rate does not worsen;
- unsafe-default rate is zero on preregistered adversarial cases;
- every suppressed question has a machine-readable reason and provenance;
- parent validators/linter/traceability/ambiguity engine remain passing;
- missing outcome evidence is unavailable, never zero.

## Evaluation requirement before freeze

Create and hash-lock a corpus **before implementation** with ambiguous, clean, governed-default, adversarial-safe-inference, and multi-question dependency scenarios. Include a held-out partition not used to tune rule thresholds. Parent-validate every embedded spec/trace artifact before freezing the contract. Where practical, add a small shadow evaluation on real project specifications without using the result to rewrite frozen synthetic criteria.

## Non-goals

- no probabilistic LLM-based guessing presented as governed inference;
- no GUI;
- no task compiler yet;
- no claim of real-world owner-time reduction from synthetic results alone.
