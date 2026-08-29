# Spec Creator v0.07 — Adaptive Discovery

**Status:** Approved preregistration specification; implementation not yet started  
**Parent:** v0.06.1 (PROMOTED AS EXPERIMENTAL)

## Objective

Ask fewer, higher-value owner questions without allowing ambiguity to escape into implementation. v0.07 converts the v0.06.1 ambiguity queue into a deterministic discovery plan that can safely apply only explicit, reversible, low-risk profile defaults, defer questions blocked by unresolved prerequisites, batch only explicitly grouped decisions, and preserve provenance for every non-question action.

The release remains deterministic and rule-bounded. It does not infer product intent from an LLM, embeddings, external data, or statistical confidence. A project profile is explicit intake data supplied to the engine; profile membership never silently invents a product choice.

## Controlled discovery model

Each v0.06.1 ambiguity finding receives exactly one v0.07 action:

- `already_governed` — parent ambiguity evidence already resolves the candidate.
- `infer_default` — an exact profile default satisfies all safe-inference gates.
- `ask_now` — the candidate belongs to a selected frontier question batch.
- `defer_dependency` — an unresolved declared prerequisite must be answered first.
- `defer_budget` — a noncritical frontier candidate is preserved but falls outside the bounded question budget.

Every action has a machine-readable reason and provenance. `defer_dependency` and `defer_budget` are not treated as resolved decisions.

## Safe-inference gates

A profile default may become `infer_default` only when all of the following are true:

1. the parent finding is `AMB-001` / unresolved options;
2. the profile targets the exact requirement/task block and ambiguity span;
3. the proposed value is one of the declared options;
4. the default is marked `risk=low`, `reversible=true`, and `auto_apply=true`;
5. provenance is one of `owner_intake`, `approved_policy`, or `existing_spec` and has a non-empty source reference;
6. the owning block is noncritical and the parent finding is not high severity;
7. downstream impact count is at most 3;
8. the selected project type permits automatic defaults (`prototype`, `production`, or `custom`; `regulated` never does).

Failure of any gate preserves an owner decision; it never silently downgrades risk.

## Question frontier and information value

A block may declare `Decision-Depends-On: REQ-*` or `TASK-*`. If the referenced block still contains an unresolved owner decision, dependent candidates are `defer_dependency` until that prerequisite is governed, inferred, or answered.

A block may declare `Decision-Group: <stable-token>`. Only findings with the exact same explicit group token may be batched into one owner question. Ungrouped findings remain one question each.

For every ready batch, information value is deterministic:

`max(member priority_score) + 40 * unresolved_dependent_block_count + 15 * (member_count - 1)`

Critical ready batches always enter `ask_now` regardless of budget. Remaining noncritical batches are selected by descending information value, then ascending group identifier, until the profile question budget is exhausted. Unselected ready candidates become `defer_budget` with provenance and remain visible.

## Project-type intake profiles

Controlled project types are `prototype`, `production`, `regulated`, and `custom`.

Default question budgets when the profile does not provide an explicit positive budget are:

- prototype: 2
- production: 3
- regulated: 4
- custom: 2

These defaults affect interaction pacing only. They do not provide product-value defaults. Product-value defaults must be explicit profile entries satisfying the safe-inference gates above.

## Requirements

### REQ-007-001
Requirement: Transform a v0.06.1 ambiguity report into a deterministic discovery plan with exactly one action per finding.
Critical: true
Acceptance: Every frozen case yields stable action records containing candidate identity, action, reason, provenance, and deterministic ordering.
Verify: tests/test_discovery.py::test_frozen_action_plans

### REQ-007-002
Requirement: Compute deterministic information-value scores for ready question batches using the preregistered formula and stable tie-breaking.
Critical: true
Acceptance: At least 95% of frozen priority cases select the preregistered highest-information ready batch and all tied cases follow the declared stable order.
Verify: tests/test_discovery.py::test_information_value_priority

### REQ-007-003
Requirement: Respect explicit decision dependencies by deferring dependent questions until prerequisite blocks that still require an owner decision are resolved or selected.
Critical: true
Acceptance: Every frozen dependency case matches the preregistered frontier and no critical dependent candidate disappears from the plan.
Verify: tests/test_discovery.py::test_dependency_frontier

### REQ-007-004
Requirement: Batch owner questions only when findings share the same explicit Decision-Group token and enforce the project-profile question budget for noncritical frontier batches.
Critical: true
Acceptance: Frozen batching cases emit the exact preregistered batch membership and question count; unrelated findings are never implicitly merged.
Verify: tests/test_discovery.py::test_explicit_batching_and_budget

### REQ-007-005
Requirement: Apply an automatic profile default only when every preregistered safe-inference gate passes.
Critical: true
Acceptance: All frozen safe-default cases infer the expected value and every action includes profile/default provenance.
Verify: tests/test_discovery.py::test_safe_inference

### REQ-007-006
Requirement: Reject unsafe automatic defaults for critical, high-impact, nonreversible, non-low-risk, untrusted, disabled, mismatched, or regulated-profile cases.
Critical: true
Acceptance: Unsafe-default count is zero across all frozen adversarial cases and the affected decisions remain visible as owner questions or governed deferrals.
Verify: tests/test_discovery.py::test_unsafe_inference_guardrails

### REQ-007-007
Requirement: Support controlled project-type intake profiles without deriving product choices from project type alone.
Critical: true
Acceptance: Project type changes only declared interaction policy; a profile with no explicit product default never resolves an AMB-001 choice automatically.
Verify: tests/test_discovery.py::test_project_profiles_do_not_invent_choices

### REQ-007-008
Requirement: Preserve machine-readable provenance and reason codes for every inferred, governed, asked, or deferred candidate.
Critical: true
Acceptance: Provenance completeness is 100% on the frozen corpus and every suppressed parent question has a reason that explains why it is not asked now.
Verify: tests/test_discovery.py::test_provenance_complete

### REQ-007-009
Requirement: Evaluate adaptive discovery on hash-locked development and held-out partitions without using missing evidence as zero.
Critical: true
Acceptance: Corpus and evaluation-plan hashes match the frozen contract, all denominator counts reconcile, and the held-out exact-action metric uses only preregistered held-out cases.
Verify: tests/test_discovery_evaluator.py::test_frozen_evaluation_and_denominators

### REQ-007-010
Requirement: Expose adaptive discovery through deterministic Python API and CLI JSON output with optional traceability graph and project-profile inputs.
Critical: true
Acceptance: CLI/API outputs are deterministic and malformed profiles or invalid supplied trace graphs fail explicitly with nonzero status.
Verify: tests/test_discovery_cli.py::test_discovery_cli

### REQ-007-011
Requirement: Preserve all promoted-parent validator, linter, traceability, ambiguity, ledger, history, and package-integrity behavior.
Critical: true
Acceptance: The complete inherited suite and all active regressions remain passing; every graph-backed v0.07 corpus case passes parent trace validation before freeze.
Verify: tests/test_discovery_evaluator.py::test_parent_preflight_and_inherited_regressions

### REQ-007-012
Requirement: Seal release evidence only after independent verification and generate the mutable shipping package manifest last.
Critical: true
Acceptance: Final package validation reports zero errors and warnings, release history remains verifiable, and extracted-ZIP verification reproduces the frozen result.
Verify: tests/test_package_manifest.py and evaluation/independent_verifier_v0.07.py

## Primary evaluation interpretation

The parent baseline asks one question for each `decision_needed=true` ambiguity finding. v0.07 may reduce immediate owner questions only through safe explicit defaults, explicit batching, or governed dependency/budget deferral. The primary question-reduction metric therefore measures immediate pre-implementation interaction burden, not guaranteed lifetime question elimination.

The held-out partition is hash-locked before implementation and scored separately. Because the same development agent creates the benchmark and later sees the project package, even perfect held-out synthetic performance is not independent real-world evidence. Synthetic success is capped at `PROMOTED AS EXPERIMENTAL`.

## Non-goals

- no LLM or probabilistic intent guessing;
- no GUI;
- no task compiler;
- no automatic mutation of owner-authored specifications;
- no claim of real-world owner-time or implementation-rework reduction from synthetic results alone.
