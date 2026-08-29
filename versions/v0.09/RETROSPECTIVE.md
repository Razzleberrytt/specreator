# v0.09 Retrospective — Frozen Benchmark Defect

**Decision:** RETRY REQUIRED  
**Frozen contract:** `REL-0.09-FROZEN-001`  
**Contract SHA-256:** `e3759fb602aad1612f3d8048253f6e6b59f5c0c15d7fc6dd04b529115c0d6049`

The first executable evaluation exposed two separate problems. `DEF-009-003` was an ordinary implementation integration error in the evaluator and was corrected without touching frozen artifacts. After that correction, 45/45 accepted envelopes matched exactly and 29/30 negative cases classified correctly.

The remaining case, `DEV-NEG-2-07`, is a frozen evaluation defect. It is labeled `task_contract_mismatch`, but its `task_contract` is exactly the same valid contract used by accepted implementation fixtures for `CTASK-008-SELF-03`. There is no governed input evidence that distinguishes it as invalid. Rejecting it would require fixture-ID overfitting, violating determinism and the no-cherry-picking invariant.

Therefore v0.09 is not promotable and its corpus/plan/contract remain immutable. The retry must add a **semantic contrast preflight** proving each negative mutation is actually distinguishable from accepted controls before freezing. This becomes `REG-0020`.

No failed result is hidden and no frozen success criterion is weakened. The Prompt Compiler implementation may be reused as pre-existing retry code, but v0.09.1 receives a new preregistration package and frozen contract before any retry-specific implementation modification.
