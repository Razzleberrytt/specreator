# Continuation State — after v0.03

## Current release state
- v0.03: PROMOTED AS EXPERIMENTAL
- Frozen contract: REL-0.03-FROZEN-001
- Contract SHA-256: 7996697714454684bd324bc368dec7588ebf9443f117e9d27c7dc2bf434c4f47
- Full automated suite: 30/30 passing
- Workspace validator: 0 errors / 0 warnings before packaging
- New permanent regression: REG-0004

## Do not change retrospectively
- `versions/v0.03/FROZEN-RELEASE-CONTRACT.json`
- historical v0.01/v0.02 source artifacts
- raw evaluation failure events
- failed initial test-run evidence
- inherited critical regressions

## v0.04 state
`versions/v0.04/SPEC-CREATOR-v0.04-DRAFT.md` exists as a draft only. No v0.04 frozen contract exists and no v0.04 implementation has begun.

## Next highest-ROI task
Design the v0.04 Spec Linter's seeded defective-spec corpus **and seeded clean-spec counterexample corpus**, define per-rule precision/false-positive metrics and inherited regressions REG-0001–REG-0004, then freeze v0.04 before writing linter code.

## Recommended first command next session
`PYTHONPATH=src python -m spec_creator.cli validate .`

Then inspect `versions/v0.04/SPEC-CREATOR-v0.04-DRAFT.md`, the v0.03 retrospective, REG-0004, and DEC-0004 before freezing v0.04.
