# Spec Creator

Spec Creator is a controlled, evidence-driven specification system for AI software development. The project is intentionally bootstrapping itself under the same release rules it is designed to impose on future projects.

## Current state

- **v0.01** — measured specification protocol; historical experimental baseline.
- **v0.02** — controlled recursive-improvement protocol; structurally useful but **not retroactively promoted** because its supplied frozen release evidence was incomplete.
- **v0.03** — **PROMOTED AS EXPERIMENTAL** after a frozen, measured recursive cycle.
- **v0.04** — draft only; not frozen and not implemented.

## What v0.03 adds

v0.03 is the first executable Spec Creator layer:

```bash
pip install -e .
spec-creator validate .
spec-creator hash-contract versions/v0.03/FROZEN-RELEASE-CONTRACT.json
```

It provides:

- JSON and JSONL validation
- JSON Schema Draft 2020-12 validation
- stable primary-ID and duplicate detection
- cross-reference checks
- event supersession/lifecycle checks
- regression-retirement governance
- denominator snapshot / metric reconciliation
- missing-data enforcement
- frozen-contract canonical SHA-256 verification
- version-manifest hash verification
- candidate self-certification detection where actor records expose it
- automated fixture/regression tests

## v0.03 evidence

The frozen v0.03 contract was created before implementation and was never weakened.

- 30/30 automated tests pass
- 22/22 preregistered invalid fixture classes are rejected
- 4/4 preregistered valid fixture classes are accepted
- REG-0001 through REG-0003 pass
- newly discovered REG-0004 passes
- zero critical gate bypasses
- zero metric reconciliation failures
- role-separated verifier pass reports zero workspace errors/warnings

See:

- `versions/v0.03/FROZEN-RELEASE-CONTRACT.json`
- `evaluation/release-scorecards.jsonl`
- `versions/v0.03/RETROSPECTIVE.md`
- `evaluation/verifier-pass-v0.03.txt`

## Recursive invariant

`observe → diagnose → propose → preregister → freeze → implement → verify → measure → adopt/reject → preserve regression memory → specify next version`

A candidate may not rewrite its own frozen criteria, silently erase failures, treat missing data as zero, or promote itself merely because it is newer.

## Next highest-ROI task

Use the v0.03 validator to design the **v0.04 Spec Linter rule corpus**, especially its clean-spec false-positive guardrails, then freeze v0.04 before implementation.
