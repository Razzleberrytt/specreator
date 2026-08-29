# v0.11.1 Independent Prefreeze Review Protocol

The reviewer must be a genuinely separate receiving context from the context that constructed the retry candidate. Treat the received ZIP as the sole source of truth. Do not freeze, implement, promote, or repair it.

## Required independent recomputation

1. Validate both candidate schemas and both inherited semantic corpora without trusting authored expected results as derivation oracles.
2. Recompute lifecycle actions from transition rules and blockers.
3. Recompute explicit dependency provenance, conflict serialization, effective DAGs, all maximum-work critical paths, deterministic waves, retry preservation, speculative-authority behavior, and the fixed 23-source-task integration denominator.
4. Recompute the exact 155-node parent suite collection and test outcomes.
5. Recompute the exact 24 inherited active regressions plus retry-local REG-0025.
6. Recompute all 1120 v0.10 manifest hashes and every one of the 154 failed-v0.11 predecessor baseline hashes.
7. Recompute whole-package ownership using immutable precedence and the retry selector rules. Report counts for protected parent, failed predecessor, retry successor, unclassified, immutable/successor overlap, successor selector multi-match, and stale snapshot members.
8. Independently classify every path in `candidate-fixtures/ownership-prospective-paths.json`. Every one must classify exactly once as retry successor.
9. Compare the 15 original v0.11 promotion-authoritative metrics against the v0.11.1 plan. No target, denominator semantics, numerator rule, missing-data rule, or anti-gaming rule may be weakened. Confirm the retry guardrail is additive.
10. Validate from a clean extraction and return raw command evidence.

## Decision rule

Return `READY_FOR_FREEZE_PREPARATION` only if all obligations pass and no new blocking defect is found. Any missing, malformed, skipped, unreconciled, or non-reproducible evidence is `NOT_READY`.
