# Continuation State — after v0.04

## Current release state

- v0.04: **PROMOTED AS EXPERIMENTAL**
- Frozen contract: `REL-0.04-FROZEN-001`
- Contract hash: `2e512511159fd20d432b143f2093e84001eb8857f5b3db151c0654a89eea3010`
- Frozen lint corpus: 100 cases; SHA-256 `cc23a138f8a8c4b8d1985a8cde6e4177d9185d7c01f1f777eced3a462d729b7d`
- Frozen evaluation plan SHA-256: `d397f59d72cf83df246beb41a59931b67d8d15d3bd850dce8fc2e2be4925fbc4`
- Full automated suite: 49/49 PASS
- Inherited v0.03 suite: 30/30 PASS
- Workspace validation before release packaging: 0 errors / 0 warnings
- New regressions: REG-0005 and REG-0006

## Executable commands

```bash
spec-creator validate .
spec-creator lint path/to/spec.md
spec-creator lint path/to/spec.md --json
spec-creator evaluate-lint-corpus .
```

## Do not change retrospectively

- `versions/v0.04/FROZEN-RELEASE-CONTRACT.json`
- `versions/v0.04/EVALUATION-PLAN.json`
- `fixtures/linter/v0.04/corpus.jsonl`
- v0.01–v0.03 frozen/version source artifacts
- historical append-only event prefixes
- failed/recovery events EVT-SC-0033 and EVT-SC-0035
- active regressions REG-0001–REG-0006

## Next highest-ROI task

Use promoted-experimental v0.04 to draft and lint the v0.05 Traceability Engine specification. Before implementation, preregister a graph corpus containing valid complete chains plus broken references, orphan critical requirements, missing tests/gates, duplicate edges, and change-impact cases; then freeze v0.05.
