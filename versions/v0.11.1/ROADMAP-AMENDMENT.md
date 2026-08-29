# v0.11.1 Roadmap Amendment — Retry Numbering and Capability Preservation

**Status:** UNFROZEN retry-governance amendment under DEC-0034.

## Decision

v0.11 remains immutable failed-frozen history: its capability target was preregistered and frozen, but implementation was blocked by `DEF-011-POSTFREEZE-001` before implementation began.

v0.11.1 is a **patch-version governed retry of the v0.11 capability**, not a new roadmap capability. It keeps the v0.11 lifecycle/execution-efficiency product target and changes only what is required to make the frozen ownership boundary satisfiable and regression-resistant.

## Numbering rule

- Successful v0.11.1 promotion completes the roadmap's **0.11 — Iteration, Continuation & Efficiency Architecture** capability slot.
- If v0.11.1 itself fails in a way that requires a new frozen candidate, retry as **v0.11.2** (and so on) rather than consuming v0.12.
- **v0.12 remains Crash-Safe Resume & Reuse** exactly as already planned.
- Patch retries may not pull later roadmap capabilities into their promotion criteria merely because work is nearby.

## Forward direction preserved

The v0.21–v0.29 Existing-Solution & Repository Intelligence series, including the Top-5 Repository Prototype Synthesis rule, remains preserved and does not become a v0.11.1 promotion obligation.
