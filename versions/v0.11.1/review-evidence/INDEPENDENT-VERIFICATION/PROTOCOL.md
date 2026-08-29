# Spec Creator v0.11.1 Independent Post-Implementation Verification Protocol

Status: REQUIRED INDEPENDENT GATE. Evidence-only; do not repair, modify frozen artifacts, promote, or begin v0.12.

## Role
Act as `verifier:independent-pass-0111`, genuinely separate from `agent:spec-creator-builder-v0.11.1`.

## Authority
Treat the supplied VERIFYING checkpoint ZIP as the sole source of truth. The root `PACKAGE-MANIFEST.json` is intentionally not the final shipping manifest yet; final manifest generation is reserved for the authoritative release-seal step after this independent verification.

## Required independent checks
1. Validate `REL-0.11.1-FROZEN-001` canonical contract hash and every `FROZEN-ARTIFACT-REGISTRY.json` member.
2. Recompute all 1120 v0.10 manifest hashes and all 154 failed-v0.11 baseline hashes.
3. Run the exact frozen 155-node parent universe and the full current test suite; no frozen parent node may disappear or fail.
4. Independently recompute all 25 active regression outcomes. REG-0025 must test all 25 legal prospective paths and all 7 forbidden paths from the frozen fixture; do not trust a helper's summary if its lookup is incomplete.
5. Independently derive all four lifecycle fixture actions from state+blockers using the frozen rules.
6. Independently validate all 21 explicit dependency edges have exactly one semantic provenance, derive the one conflict-serialization edge, and verify 22 effective edges total.
7. Independently recompute all six critical-path sets and all six execution-wave plans exactly.
8. Verify retry isolation preserves unrelated successful work and speculative work never obtains authority early.
9. Validate all emitted execution plans against the frozen candidate schema and confirm the fixed 23-source-task integration denominator is covered 23/23.
10. Recompute current whole-package ownership after immutable precedence: zero unclassified, zero immutable/successor overlap, zero successor-selector multimatch. Separately recompute the 25 legal prospective + 7 forbidden selector cases.
11. Verify the five primary metrics meet 1.0 targets and all measurable zero-tolerance guardrails meet 0; parent and active-regression pass rates must be 1.0. Do not treat missing final package-manifest evidence as a pre-verification defect because the final shipping manifest is intentionally generated after independent verification.
12. Confirm shadow execution evidence is matched-obligation calibration only and is not used for a general speedup claim.
13. Run `PYTHONPATH=src python -m spec_creator.cli validate . --no-package-manifest`; require 0 errors / 0 warnings.
14. Run `python versions/v0.11.1/tools/frozen_contract_preflight.py`, but independently inspect REG-0025 rather than relying solely on the helper's printed prospective-closure claim.
15. Inspect `src/spec_creator/v0111/` and `tests/v0111/` for implementation/spec mismatches, hidden authority, unsupported assumptions, or new blocking defects.

## Required output
Return an evidence ZIP containing raw commands/output, machine-readable recomputation, hashes, defects (if any), and one exact recommendation:

- `READY_FOR_RELEASE_SEAL` — implementation satisfies frozen criteria and may proceed to authoritative final release sealing/package-manifest generation; or
- `NOT_READY` — include blocking defect IDs and reproducible evidence.

Do not modify or freeze anything and do not start v0.12.
