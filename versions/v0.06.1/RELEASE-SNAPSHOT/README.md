# Spec Creator

Spec Creator is a controlled, evidence-driven specification system for AI software development. It is recursively developing itself under the same preregistration, frozen-contract, verification, regression-memory, and release rules it is intended to impose on future projects.

## Current state

- **v0.01** — measured specification protocol; historical experimental baseline.
- **v0.02** — controlled recursive-improvement protocol; structurally useful but not retroactively promoted because supplied release evidence was incomplete.
- **v0.03** — **PROMOTED AS EXPERIMENTAL**; executable schemas and structural validator.
- **v0.04** — **PROMOTED AS EXPERIMENTAL**; deterministic Spec Linter plus recursion-safe historical release verification.
- **v0.05** — **PROMOTED AS EXPERIMENTAL**; typed Traceability Engine with critical-path enforcement and deterministic change-impact analysis.
- **v0.06** — **RETRY REQUIRED**; frozen Ambiguity Engine candidate rejected before implementation because all 16 graph-backed benchmark dependencies violated the promoted v0.05 traceability schema.
- **v0.06.1** — **PROMOTED AS EXPERIMENTAL**; governed retry with deterministic ambiguity detection/classification, trace-aware question priority, clarification-interception proxy, parent-artifact preflight, schema-aware ledger append, and manifest-last package sealing.

## Install and run

```bash
pip install -e .

spec-creator validate .
spec-creator hash-contract versions/v0.05/FROZEN-RELEASE-CONTRACT.json
spec-creator lint path/to/spec.md
spec-creator lint path/to/spec.md --json
spec-creator evaluate-lint-corpus .
spec-creator trace-validate graph.json
spec-creator trace-impact graph.json NODE-ID [NODE-ID ...]
spec-creator evaluate-trace-corpus .
spec-creator ambiguity path/to/spec.md --json
spec-creator preflight-ambiguity-corpus fixtures/ambiguity/v0.06.1/corpus.jsonl --json
spec-creator evaluate-ambiguity-corpus . --json
spec-creator seal-package . --release-version 0.06.1 --release-status "PROMOTED AS EXPERIMENTAL" --generated-at-utc <UTC>
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

### Deterministic Spec Linter — v0.04+

The bounded Markdown profile detects vague/non-testable normative wording, missing acceptance or failure behavior, unresolved critical decisions, undefined references, missing verification, deterministic contradictions, overly broad tasks, unbounded components, and ungoverned assumptions.

Findings carry stable rule IDs, line/column, exact source span, severity, and rationale. Local suppression requires an approved governance decision.

### Recursive-history integrity — v0.04+

- append-only ledgers preserve historical byte prefixes;
- mutable shared source can evolve while prior release content is preserved in version-local release snapshots;
- historical prefix/snapshot mutation remains detectable;
- `append_jsonl_records` prevents accidental whole-ledger rewrites when appending historical records.

### Traceability Engine — v0.05

The typed graph model supports:

`Goal → Requirement → Feature → Task → Test → Gate`

It adds:

- versioned traceability graph schema;
- duplicate-node and duplicate-edge detection;
- broken-reference validation;
- governed relation/type transitions;
- cycle detection;
- critical-chain completeness and first-missing-stage diagnostics;
- deterministic complete-path output;
- upstream/downstream change-impact analysis;
- CLI/API access and frozen-corpus evaluation.

The v0.05 release dogfoods its own engine: all ten critical v0.05 requirements have complete ordered paths in `versions/v0.05/TRACEABILITY-GRAPH.json`.

## v0.05 frozen evidence

- **83/83** complete automated tests PASS
- **49/49** inherited v0.04 tests PASS
- **20/20** frozen invalid graphs detected
- **10/10** frozen valid + impact graphs accepted
- **10/10** frozen critical requirements complete
- **5/5** impact cases exact
- diagnostic precision **100%**
- valid graph false positives **0**
- v0.05 spec lint findings **0**
- applicable inherited REG-0001–REG-0006 PASS
- new REG-0007 PASS
- **12/12** mandatory gates PASS
- independent-role verifier PASS

The first implementation run failed 8 tests because impact output used lexical ID ordering. The frozen benchmark was not changed; the implementation was corrected and the defect became REG-0007.

### Ambiguity Engine — v0.06.1

The governed retry adds a deterministic six-family ambiguity layer over active Markdown requirement/task blocks:

- unresolved/defaulted options;
- missing measurable bounds;
- undefined referents;
- conflicting constraints;
- assumption governance;
- unresolved status markers.

Each finding includes source location, owning block, severity, disposition (`owner_decision`, `governed_default`, or `spec_correction`), decision-needed state, traceability downstream impact, priority score, and an optional bounded owner question. A supplied trace graph must pass the promoted v0.05 validator before it can influence ranking.

The release also hardens recursive operation itself: embedded successor benchmark artifacts are parent-validated before freeze, schema-aware JSONL append rejects malformed/duplicate records before writing bytes, and the live shipping package manifest is regenerated only after all release artifacts are complete.

## v0.06.1 frozen evidence

- frozen retry corpus: **72 cases**
- defect detection: **24/24 = 100%**
- clean acceptance: **20/20 = 100%**
- exact decision/disposition classifications: **76/76 = 100%**
- governed-default questions: **0**
- priority top-question accuracy: **8/8 = 100%**
- synthetic clarification triggers intercepted: **16/16 = 100%**
- unnecessary questions: **0/64 = 0%**
- critical ambiguity escapes: **0**
- parent-valid graph-backed retry cases: **16/16**
- release self-traceability: **12/12 critical requirements complete**
- inherited v0.05 test modules: **84/84 PASS**
- complete v0.06.1 suite: **100/100 PASS**
- frozen applicable regressions REG-0001–REG-0009: **PASS**
- new REG-0010–REG-0014: **PASS**
- mandatory v0.06.1 gates: **16/16 PASS**
- independent-role verifier: **PASS**

The first frozen v0.06 candidate is intentionally retained as a failed experiment. v0.06.1 fixes benchmark dependency validity through a governed retry rather than rewriting v0.06 history.

## Recursive invariant

`observe → evidence → root cause → hypothesis → preregister → freeze → implement → independently verify → reconcile → adopt/reject → preserve regression memory → specify successor`

A candidate may not rewrite its frozen criteria, silently edit historical events, hide failed experiments, treat missing data as zero, manipulate denominators, remove regressions for convenience, weaken tests for a pass, or promote itself merely because it is newer.

## Next capability

v0.07 is planned as **Adaptive Discovery**. The highest-ROI next experiment is not “ask more questions”; it is to measure **information gained per owner question** while preserving ambiguity-escape and rework guardrails. v0.07 should add safe-inference/default proposals and project-type intake profiles, but should not claim real-world efficiency improvement until evaluated on held-out or independent project scenarios.
