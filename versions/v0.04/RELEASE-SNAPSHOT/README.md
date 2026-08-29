# Spec Creator

Spec Creator is a controlled, evidence-driven specification system for AI software development. It is bootstrapping itself under the same release rules it is intended to impose on future projects.

## Current state

- **v0.01** — measured specification protocol; historical experimental baseline.
- **v0.02** — controlled recursive-improvement protocol; structurally useful but not retroactively promoted because its supplied release evidence was incomplete.
- **v0.03** — **PROMOTED AS EXPERIMENTAL**; executable schemas and structural validator.
- **v0.04** — **PROMOTED AS EXPERIMENTAL**; deterministic Spec Linter plus recursion-safe historical release verification.

## Install and run

```bash
pip install -e .

spec-creator validate .
spec-creator hash-contract versions/v0.04/FROZEN-RELEASE-CONTRACT.json
spec-creator lint path/to/spec.md
spec-creator lint path/to/spec.md --json
spec-creator evaluate-lint-corpus .
```

Use `--approved-decision DEC-...` on `lint` only when a local lint suppression has an explicitly approved governance decision.

## Executable capabilities

### Structural validator — v0.03+

- JSON / JSONL syntax validation
- JSON Schema Draft 2020-12 validation
- stable primary-ID / duplicate checks
- cross-reference checks
- event supersession consistency
- regression-retirement governance
- denominator snapshot / metric reconciliation
- missing-data enforcement
- frozen-contract canonical SHA-256 verification
- release-manifest verification
- candidate self-certification detection where actor records expose it

### Deterministic Spec Linter — v0.04

The bounded Markdown lint profile detects:

- vague/non-testable normative wording
- missing requirement acceptance criteria
- missing failure behavior on critical mutating operations
- unresolved critical decisions
- undefined interface/entity references
- requirements without verification paths
- contradictory deterministic constraints
- overly broad tasks
- unbounded component responsibilities
- ungoverned implementation assumptions

Every finding carries a stable rule ID, line, column, exact span, severity, and rationale.

### Recursive-history integrity — v0.04

- append-only ledgers preserve historical byte prefixes;
- mutable shared source can evolve while prior release content is preserved under version-local `RELEASE-SNAPSHOT` evidence;
- historical prefix/snapshot mutation remains detectable;
- `append_jsonl_records` prevents accidental whole-ledger rewrites when adding historical records.

## v0.04 frozen evidence

- 49/49 full automated tests PASS
- 30/30 inherited v0.03 tests PASS
- 50/50 frozen defect cases detected
- 50/50 frozen clean counterexamples accepted
- 56/56 emitted findings expected
- 56/56 diagnostics complete
- minimum per-rule precision 100%
- frozen REG-0001–REG-0004: 4/4 PASS
- new REG-0005/REG-0006 scenarios: 6/6 PASS
- suppression-governance scenarios: 3/3 PASS
- 12/12 mandatory gates PASS
- independent-role verifier: PASS

The release remains experimental because the benchmark is synthetic and there is not yet independent real-project evidence of reduced implementation rework.

## Recursive invariant

`observe → evidence → root cause → hypothesis → preregister → freeze → implement → independently verify → reconcile → adopt/reject → preserve regression memory → specify successor`

A candidate may not rewrite its frozen criteria, silently edit historical evidence, hide failed experiments, treat missing data as zero, remove critical regressions for convenience, or promote itself merely because it is newer.

## Next capability

v0.05 is planned as the **Traceability Engine**: a machine-readable and verifiable Goal → Requirement → Task → Test → Gate graph with orphan detection and change-impact analysis.
