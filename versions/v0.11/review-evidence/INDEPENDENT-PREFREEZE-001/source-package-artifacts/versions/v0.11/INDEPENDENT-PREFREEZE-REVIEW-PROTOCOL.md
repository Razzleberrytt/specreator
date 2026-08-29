# v0.11 Independent Prefreeze Review Protocol

**Purpose:** obtain genuinely separate-context review evidence before any v0.11 freeze.

The receiving context must not implement, freeze, promote, repair, or redesign v0.11. It reviews the preregistration draft and returns evidence only.

## Review obligations

1. Confirm v0.10 and earlier frozen/failed history is treated as immutable.
2. Validate both candidate JSON Schemas as Draft 2020-12 schemas.
3. Validate every candidate fixture parses and is internally coherent.
4. Recompute expected critical paths/waves/conflict behavior for the structural fixtures without trusting the authored expectations.
5. Check that every sequential dependency has a permitted provenance class and every declared parallel wave is dependency/conflict safe.
6. Check lifecycle fixtures can recover one exact next legal action with zero hidden chat state.
7. Audit every denominator and threshold in `EVALUATION-DESIGN.json` for ambiguity or gameability.
8. Confirm empirical wall-clock/context/rework evidence is shadow-only for v0.11 and cannot authorize a speed claim.
9. Confirm serial/control and optimized comparisons require identical obligation hashes and mandatory quality gates.
10. Return PASS/FAIL per obligation, defects with exact artifact locations, and a final recommendation: `READY_FOR_FREEZE_PREPARATION` or `NOT_READY`.

## Evidence package minimum

Return machine-readable JSON plus a concise Markdown report. Include receiver identifier, UTC time, source package SHA-256, reviewed artifact hashes, computations performed, findings, and recommendation. Missing evidence is not PASS.
