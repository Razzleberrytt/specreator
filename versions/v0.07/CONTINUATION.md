# v0.07 Continuation State

## Sealed candidate

- Version: **v0.07 — Adaptive Discovery**
- Decision: **PROMOTED AS EXPERIMENTAL** under `DEC-0022`
- Frozen contract: `versions/v0.07/FROZEN-RELEASE-CONTRACT.json`
- Canonical contract SHA-256: `981c1415040c986d031f528ce10a12456a0e594bbb9551f95cbec4bf8c3dac38`
- Combined frozen corpus SHA-256: `31e13b98991543208e453faa89d2277282646f8110483fab1ea9a8d9b3c272ad`
- Held-out partition SHA-256: `064d0b1a78e708cb071fa9c28db8b7b0f1b98cb5e70f0c9f81e14e0282f3848e`
- Evaluation-plan SHA-256: `539e75dca5af5067188417b27ed405719b9b3e4d78a61739178c0db0a9cebe3d`

Do not modify those frozen v0.07 artifacts in a successor cycle. Failed/corrective evidence and REG-0015/REG-0016 must remain visible.

## Reproduced release evidence

- full current suite: **119/119 PASS**
- exact inherited v0.06.1 baseline: **100/100 PASS**
- owner-question reduction: **52/92 = 56.52%**
- information-value top selection: **24/24 exact**
- held-out action exact match: **47/47 exact**
- safe inference: **20/20 exact**
- unsafe defaults: **0**
- critical ambiguity escapes: **0**
- dependency frontier: **16/16 exact**
- provenance completeness: **98/98**
- unnecessary question batches: **0/40**
- critical self-traceability: **12/12 complete**
- mandatory gates: **19/19 PASS**
- preregistered metrics: **16/16 PASS**
- independent verifier: **PASS**
- active regressions through **REG-0016**: preserved/passing

## Highest-ROI successor direction

Proceed to **v0.08 — Task Compiler** only through a new preregistration/freeze cycle. Use the v0.08 draft if present, but treat it as unfrozen design input rather than an approved contract.

The next benchmark should prove at minimum:

- unresolved discovery decisions block dependent compilation;
- critical requirements compile into complete atomic task paths;
- dependency DAGs are acyclic and deterministic;
- explicit conflict zones prevent unsafe parallelization;
- task-complexity/granularity bounds reject oversized tasks;
- compiled tasks preserve requirement/test/gate/source provenance;
- historical task execution state is event-sourced rather than rewritten;
- held-out task graphs score exactly without hiding missing tasks;
- parent validator/linter/traceability/ambiguity/discovery behavior remains passing.

## Release-order invariant

Before ending a successor release:

1. finish all release and successor-draft artifacts intended for the package;
2. run role-separated verification;
3. reconcile metrics/gates and record the decision;
4. generate version-local release manifest/snapshot;
5. generate root `PACKAGE-MANIFEST.json` **last**;
6. validate the sealed workspace;
7. ZIP it;
8. extract the ZIP into a fresh directory and rerun validation/tests plus file-set/hash comparison.
