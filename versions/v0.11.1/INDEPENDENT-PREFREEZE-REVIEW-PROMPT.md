# Prompt — Independent v0.11.1 Governed Retry Prefreeze Review

You are a genuinely separate receiving context performing one independent prefreeze review for Spec Creator v0.11.1.

Treat the attached v0.11.1 retry checkpoint ZIP as the sole source of truth. Extract and inspect it. Do not continue development, implement, freeze, promote, repair, or redesign the candidate.

v0.11 froze successfully but was blocked before implementation by `DEF-011-POSTFREEZE-001`: its exact 103-member successor ownership enumeration omitted 52 freeze-time shipped paths and could not legally admit later implementation/evidence paths. The authoritative context claims v0.11.1 repairs this without weakening the product target. Do not trust that claim. Recompute it independently.

Read at minimum all files under `versions/v0.11.1/` relevant to the spec, evaluation design/universes/plan, immutable boundary, successor ownership, failed-v0.11 baseline, regression/parent universes, lifecycle/dependency rules, schemas, fixtures, review protocol, preregistration hashes, and continuation. Also inspect the preserved v0.11 frozen contract/checkpoint and v0.10 manifest.

Perform every obligation in `INDEPENDENT-PREFREEZE-REVIEW-PROTOCOL.md`, especially:

- recompute 1120/1120 v0.10 hashes;
- recompute 154/154 failed-v0.11 baseline hashes;
- recompute actual whole-package path classification from selectors, not the snapshot;
- classify every prospective output path exactly once;
- verify REG-0025 is a real regression against the failed mechanism;
- verify the original 15 v0.11 metrics are not weakened and the retry guardrail is additive;
- independently derive lifecycle/provenance/critical paths/waves rather than trusting authored answers;
- run clean-extraction validation.

Return raw evidence plus a concise report with `READY_FOR_FREEZE_PREPARATION` or `NOT_READY`. If NOT_READY, assign stable defect IDs and precise reproductions. Do not freeze or implement.
