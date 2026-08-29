# v0.03 Retrospective

**Release decision:** PROMOTED AS EXPERIMENTAL  
**Frozen contract:** `REL-0.03-FROZEN-001`  
**Contract hash:** `7996697714454684bd324bc368dec7588ebf9443f117e9d27c7dc2bf434c4f47`

## What worked

The recursive protocol prevented goalpost movement: the v0.03 success criteria were frozen before code existed, and the implementation was judged against that exact contract. The valid-fixture guardrail was especially valuable because it caught a validator that was becoming “stricter” in a wrong way.

The split between JSON Schema shape validation and deterministic semantic checks was effective. It kept controlled enums/required fields declarative while handling references, lifecycles, hashes, scorecards, and metric reconciliation in code.

## What failed

The first full test run was **26 passed / 2 failed**. Both failures came from one implementation defect: the duplicate-ID checker treated a metric's `snapshot_id` reference as if it were a new snapshot record.

## Root cause and rework

The first implementation generalized “all ID-shaped fields should be unique” too aggressively. Primary identifiers and reference identifiers need different semantics.

The fix introduced an explicit primary-ID mapping. The original valid fixture was not weakened. A permanent regression, `REG-0004`, now guarantees that shared references do not produce false duplicate errors.

## Where the specification was weak

v0.03 specified stable-ID and duplicate-ID validation but did not explicitly say **duplicate uniqueness applies to primary record IDs, not references**. That omission allowed the false-positive implementation.

This is a useful precursor lesson for v0.04: lint rules must model context and reference semantics rather than blindly matching words or shapes.

## Where the protocol saved work

- Frozen success criteria prevented weakening the valid fixture after it exposed the bug.
- The guardrail against valid-fixture false positives prevented a misleading “higher rejection rate = better validator” outcome.
- Regression memory converted the discovered defect into REG-0004.
- Denominator snapshots made the reported 22/22 and 4/4 fixture metrics auditable rather than impressionistic.
- Separate implementer/verifier actor records made self-certification mechanically testable.

## Overhead that did not pay off yet

The release/evaluation record set is verbose for a small validator. The overhead is justified for this recursive bootstrap, but future versions should compile more of these records automatically rather than hand-authoring them.

## Retained changes

Retain the Python CLI/library, versioned schemas, semantic validator architecture, canonical frozen-contract hashing, metric reconciliation, manifest verification, self-certification check, regression-governance check, and fixture corpus.

## Rejected/deferred changes

No GUI, statistical claims about software-delivery improvement, natural-language linting, repository intelligence, or autonomous promotion were added.

## What v0.04 should learn

v0.04 should build the Spec Linter, but with a **false-positive-first design**:

1. every lint rule needs a precise trigger and counterexample corpus;
2. rule output must identify the exact requirement/text span and reason;
3. context-sensitive rules must distinguish declarations from references and accepted decisions from unresolved ambiguity;
4. seeded clean specs must act as a guardrail, not only seeded defective specs;
5. lint rules should be independently disableable only by governed configuration, never silently weakened to pass a release.

## Metrics

- Automated tests: **30/30 pass**
- Preregistered invalid fixture detection: **22/22 = 100%**
- Preregistered valid fixture acceptance: **4/4 = 100%**
- Frozen critical regression pass rate: **3/3 = 100%**
- Additional new regression REG-0004: **PASS**
- Critical gate bypass count: **0**
- Metric reconciliation failures: **0**
- Candidate self-certification violations in release scorecard: **0**

## Limitation

This release demonstrates **artifact correctness and recursive-governance execution**, not yet real-world reductions in development rework. v0.03 is therefore promoted **as experimental**, not as a validated 1.0-quality system.
