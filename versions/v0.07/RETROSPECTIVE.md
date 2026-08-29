# v0.07 Retrospective — Adaptive Discovery

**Release decision:** PROMOTED AS EXPERIMENTAL  
**Parent:** v0.06.1 — PROMOTED AS EXPERIMENTAL  
**Frozen contract:** `REL-0.07-FROZEN-001`  
**Contract canonical SHA-256:** `981c1415040c986d031f528ce10a12456a0e594bbb9551f95cbec4bf8c3dac38`

## What worked

v0.07 turns the parent ambiguity queue into a deterministic discovery plan. Every ambiguity candidate receives exactly one governed action: already governed, infer a narrowly safe explicit default, ask now, defer on an unresolved dependency, or defer under a bounded question budget. The planner adds explicit project profiles, exact safe-inference gates, dependency-aware frontiering, explicit decision batching, deterministic information-value ranking, and machine-readable provenance.

The frozen synthetic benchmark passes every preregistered target. The parent baseline contains 92 immediate owner questions; v0.07 emits 40 question batches, a reduction of 52/92 = **56.52%**, above the frozen 40% minimum. Information-value top selection is 24/24 exact, the hash-locked held-out partition is 47/47 exact at the action-record level, safe inference is 20/20 exact, dependency frontiering is 16/16 exact, all 98 expected actions have complete provenance, and there are zero unsafe defaults, zero critical ambiguity escapes, zero unnecessary question batches, and zero rework-proxy mismatches.

The promoted parent is preserved: the exact preimplementation v0.06.1 baseline remains 100/100 tests passing. The complete v0.07 suite finishes at 119/119. All 12 critical v0.07 requirements have complete Goal → Requirement → Feature → Task → Test → Gate paths. Independent verification recomputes all four frozen hashes, all frozen metrics, the exact parent suite, new regression tests, shadow status, self-traceability, and workspace validation with every check passing.

## What failed or required correction

### DEF-007-001 — higher-level heading leakage

The required non-promotional shadow run over real Spec Creator specifications found false ambiguity questions in the historical v0.06.1 spec. The shared Markdown block parser ended a `###` requirement block only at another `###` heading, so a later `##` explanatory section leaked into the previous normative block. That explanatory prose contained ambiguity-marker examples and was incorrectly treated as active requirement text.

The frozen v0.07 corpus, plan, held-out partition, and contract were not changed. The parser was corrected so level 1–3 headings terminate the active requirement/task/component block while deeper headings remain local. **REG-0015** permanently covers the boundary behavior.

### DEF-007-002 — descriptive “unresolved” language treated as status

After the heading-boundary fix, the shadow run exposed one remaining inherited false positive: the phrase `unresolved alternatives` described the ambiguity taxonomy but was interpreted as an unresolved decision state. The matcher now distinguishes descriptive taxonomy language from actual status forms such as `is unresolved`. **REG-0016** preserves both sides of that distinction.

These fixes are corrective maintenance discovered after freeze. Under DEC-0021 they are deliberately excluded from the preregistered IMP-0012 effectiveness claim.

## What caused rework

The frozen discovery implementation itself did not require benchmark-driven corrective rework: the initial 115-test run and first frozen-corpus evaluation already met all preregistered v0.07 effectiveness targets. Rework came from the required shadow evaluation, which exercised historical real specifications outside the synthetic benchmark distribution and exposed two inherited ambiguity-parser weaknesses.

This is an important distinction. Synthetic benchmark success measured the intended new behavior well, but it did not fully cover interactions with historical prose structure. Keeping the shadow gate separate from promotion metrics prevented the cycle from silently converting post-result fixes into evidence that the preregistered experiment had succeeded.

## Where the specification was strong

- Safe inference is defined as an exact conjunction of gates rather than a confidence score.
- Project type changes interaction policy but cannot invent product values.
- Dependency and budget deferral remain visible unresolved work rather than being treated as completion.
- Held-out labels and denominators were hash-locked before implementation.
- Missing evidence is explicitly incomplete rather than zero.
- The synthetic-evidence ceiling prevented overclaiming real-world efficiency improvement.
- The mandatory shadow pass caught defects that the frozen benchmark did not.

## Where the specification was weak

The v0.07 frozen benchmark did not include enough historical prose-layout diversity to catch inherited parser interactions. More generally, the benchmark focused on discovery decision semantics and less on cross-version document-shape robustness. The mandatory shadow gate compensated for this, but future benchmark design should preflight representative historical artifacts as adversarial compatibility inputs before freeze rather than relying on a postimplementation shadow pass alone.

The task ledger also still represents preregistered task definitions rather than event-sourced execution state. Completed implementation is demonstrated by events/tests/gates, while the original task records remain `planned`. This is auditable but awkward and becomes increasingly costly as the system approaches a real Task Compiler.

## Where the protocol saved work

- Frozen hashes prevented changing the held-out labels or thresholds after seeing perfect results.
- The parent preflight prevented another v0.06-style invalid-benchmark dependency failure.
- Independent verification caught configuration/integrity drift before promotion could be declared.
- The shadow gate found two real inherited false positives without contaminating the frozen experiment metrics.
- Regression memory converted both defects into permanent executable checks.
- Manifest-last release sequencing prevents release accounting from invalidating its own shipping integrity evidence.

## Where the protocol created overhead

The release requires separate preregistration, hash locking, parent preflight, synthetic evaluation, shadow evaluation, self-traceability, independent verification, denominator snapshots, metric records, gates, scorecard, rollback, retrospective, release manifest, historical snapshot, shipping manifest, and extracted-package verification. This is intentionally conservative, but several artifacts repeat the same facts in different schemas.

A later reliability version should compile release accounting from raw events and frozen contracts rather than manually constructing overlapping ledgers. Until that compiler exists, duplication is accepted because it makes disagreement detectable.

## Changes retained

- Adaptive discovery action model and deterministic information-value selection.
- Explicit safe-inference gates and unsafe-default rejection.
- Explicit dependency frontier, batching, and question budget semantics.
- Project profiles that alter interaction policy without inventing product decisions.
- Full provenance on every action.
- Hash-locked development/held-out evaluation.
- REG-0015 heading-boundary protection.
- REG-0016 unresolved-context protection.
- Mandatory real-spec shadow evaluation as a compatibility guardrail.

## Changes rejected

- No probabilistic or LLM-based intent inference.
- No automatic product-value defaults derived only from project type.
- No rewriting of frozen synthetic labels after seeing results.
- No use of shadow corrective fixes as retroactive IMP-0012 effectiveness evidence.
- No claim that a 56.5% synthetic question reduction proves a 56.5% real-world owner-time reduction.

## What v0.08 should learn

The next roadmap capability remains **v0.08 — Task Compiler**, but v0.07 adds several constraints that should become first-class compiler invariants:

1. unresolved `ask_now`, `defer_dependency`, or `defer_budget` owner decisions must block any task whose correctness depends on them;
2. a compiled task must trace to bounded requirements, tests, gates, and affected files/interfaces rather than merely restating prose;
3. task dependencies must form an acyclic executable DAG with deterministic ordering and explicit conflict zones;
4. task granularity must be bounded so tasks are atomic enough for independent verification and safe parallelization;
5. task execution state should be event-sourced rather than requiring historical task-definition rewrites;
6. benchmark preflight should include historical real-spec/task shapes before freeze, not only synthetic cases;
7. success must measure executable task-graph correctness and rework/merge-conflict guardrails, not simply the number of tasks produced.

## Final interpretation

v0.07 provides strong evidence that the deterministic adaptive-discovery mechanism behaves exactly as preregistered on its synthetic development and held-out corpus while preserving the parent release. It does **not** establish causal real-project productivity improvement. `PROMOTED AS EXPERIMENTAL` is therefore the strongest classification justified by the frozen contract and available evidence.

## Late release-engineering observations

Two ordinary caller/API mistakes during resumed release bookkeeping were preserved as **DEF-007-003**. Both failed closed before producing release evidence or mutating frozen artifacts, so no new regression was justified beyond the existing CLI/import failure behavior.

A later successor-draft helper exposed **DEF-007-004**: per-ledger validated append correctly rejected a duplicate event ID, but two earlier writes to different ledgers had already committed. The intended decision/improvement records were valid and preserved, the duplicate event ledger write made no byte change, and the successor event was appended under the next free ID. REG-0011 already protects duplicate IDs within a ledger; true cross-ledger transactional orchestration is deferred to the roadmap reliability series (v0.12–v0.13) and should receive dedicated regression coverage when introduced.
