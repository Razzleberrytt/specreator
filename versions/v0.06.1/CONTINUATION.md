# Continuation State — after v0.06.1

## Current release state

- v0.06.1: **PROMOTED AS EXPERIMENTAL**
- v0.06: **RETRY REQUIRED** and preserved unchanged
- parent: v0.05 **PROMOTED AS EXPERIMENTAL**
- frozen contract: `REL-0.06.1-FROZEN-001`
- canonical contract hash: `2ae4073dc197c73386d07b9746d38d807a1d9c038b56aae6a68c7c16a53fbf27`
- retry corpus SHA-256: `3d147717ff2501061f72a0c5f384403751297eb91b6d916fd4fbb48e9edf5f9e`
- evaluation-plan SHA-256: `70e3f6c5017fc2a6aef312065ec7f705cbc055f9cec46aec6144c1a1ee6a0bc5`
- complete suite: **100/100 PASS**
- inherited v0.05 test modules: **84/84 PASS**
- frozen corpus metrics: all targets met
- self-traceability: **12/12 critical requirements complete**
- mandatory gates: **16/16 PASS**
- active regression memory: REG-0001 through REG-0014

## Executable commands

```bash
spec-creator validate .
spec-creator lint path/to/spec.md --json
spec-creator trace-validate graph.json --json
spec-creator ambiguity path/to/spec.md --json
spec-creator preflight-ambiguity-corpus fixtures/ambiguity/v0.06.1/corpus.jsonl --json
spec-creator evaluate-ambiguity-corpus . --json
spec-creator seal-package . --release-version 0.06.1 --release-status "PROMOTED AS EXPERIMENTAL" --generated-at-utc <UTC>
```

## Do not change retrospectively

- failed `versions/v0.06/FROZEN-RELEASE-CONTRACT.json`, v0.06 evaluation plan/corpus, and failure evidence
- `versions/v0.06.1/FROZEN-RELEASE-CONTRACT.json`
- `versions/v0.06.1/EVALUATION-PLAN.json`
- `fixtures/ambiguity/v0.06.1/corpus.jsonl`
- defect evidence DEF-0061-001 through DEF-0061-005
- REG-0001 through REG-0014 without governed retirement
- historical JSONL prefixes / release snapshots

## Known limitation

v0.06.1 proves deterministic behavior on a visible synthetic corpus. It does **not** prove that real users ask fewer questions, that implementation rework falls, or that the rules generalize to arbitrary specification styles.

## Next highest-ROI task

Use v0.06.1 to preregister **v0.07 — Adaptive Discovery** around information value per owner question. Build the evaluation corpus first, including held-out clean cases and cases where an apparently safe inference would be wrong. Guardrails must include ambiguity escape, unnecessary-question burden, unsafe-default rate, and rework proxy. Do not freeze v0.07 until its benchmark itself passes all promoted-parent validators.
