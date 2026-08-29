# Spec Creator v0.09 — Prompt Compiler (Unfrozen Draft)

**Status:** Evidence-derived draft only. No v0.09 implementation is authorized until prompt schemas, corpora, held-out evaluation, denominators, parent preflight, and a frozen v0.09 release contract are preregistered.
**Parent:** v0.08 Task Compiler, PROMOTED AS EXPERIMENTAL under DEC-0025.

## Objective

Compile one immutable v0.08 task plus only the governed context required to execute or verify it into deterministic bounded agent prompts. Prompt compilation must preserve task scope, prerequisites, source requirements, acceptance criteria, write scopes, verification references, gate obligations, and compiled-task-graph identity without inventing product or architectural decisions.

The Prompt Compiler should reduce context reconstruction and corrective prompting by producing purpose-specific prompts rather than copying the entire project into every agent context.

## Proposed prompt kinds

1. `bootstrap` — establish task identity, immutable evidence, allowed scope, prerequisites, and required outputs before work starts.
2. `implementation` — authorize only the task's owned write scopes and acceptance criteria.
3. `debug` — constrain diagnosis/correction to observed evidence and preserve frozen requirements/tests.
4. `verification` — give a role-separated verifier the frozen criteria and evidence needed to reproduce claims without implementation-author self-certification.
5. `continuation` — preserve exact task state, evidence refs, unresolved blockers, completed work, and next permitted action across sessions.

## Proposed invariants

### REQ-009-D01
Requirement: Every compiled prompt must bind to candidate version, compiled graph hash, compiled task ID, prompt kind, and source evidence identifiers.
Critical: true
Acceptance: Every accepted prompt fixture contains exact preregistered identity/provenance fields and rejects graph/task hash mismatches.
Failure: Missing or mismatched immutable identity blocks prompt compilation instead of emitting an unbound prompt.
Verify: Planned frozen prompt-schema and identity tests.

### REQ-009-D02
Requirement: An implementation prompt may authorize writes only within the compiled task's declared write scopes and must include its prerequisites, acceptance criteria, verification references, and gates.
Critical: true
Acceptance: Every accepted implementation fixture contains exactly the task-authorized scopes/criteria and no unrelated write scope.
Failure: Missing task evidence or requested scope expansion returns a structured blocking diagnostic rather than silently widening authority.
Verify: Planned scope-preservation corpus tests.

### REQ-009-D03
Requirement: Prompt compilation must refuse implementation/debug prompts when prerequisite execution state is not satisfied or an unresolved owner decision blocks the task.
Critical: true
Acceptance: Every frozen blocked-state case emits the exact preregistered blocker and no executable prompt body.
Failure: A blocked task cannot be converted into executable agent authority.
Verify: Planned prerequisite/decision-block corpus tests.

### REQ-009-D04
Requirement: Verification prompts must identify a verifier role distinct from the implementation actor and include frozen criteria/evidence without implementation-authored success conclusions.
Critical: true
Acceptance: Accepted verification fixtures contain exact objective checks and omit candidate self-certification language.
Failure: Same-actor verification or missing frozen checks blocks verifier-prompt generation.
Verify: Planned independent-verification prompt tests.

### REQ-009-D05
Requirement: Continuation prompts must preserve task state by replayed execution evidence, graph hash, completed evidence, open blockers, and the next permitted action without rewriting historical task definitions.
Critical: true
Acceptance: Repeated continuation compilation over identical event streams is byte-equivalent and every held-out handoff fixture retains all preregistered state facts.
Failure: Incomplete, conflicting, or hash-mismatched execution history blocks continuation compilation.
Verify: Planned continuation/handoff corpus tests.

### REQ-009-D06
Requirement: Context minimization must be deterministic and may omit evidence only when that evidence is outside the task's transitive prerequisites, source requirement/test/gate closure, authorized scopes, or selected prompt-kind obligations.
Critical: true
Acceptance: Frozen fixtures exactly match both included and intentionally excluded context references and preserve every critical obligation.
Failure: If safe context closure cannot be proven, prompt compilation fails closed rather than heuristically dropping context.
Verify: Planned context-closure exact-match tests.

### REQ-009-D07
Requirement: Generated prompts must encode explicit completion evidence requirements and prohibit tests, gates, frozen criteria, or critical regressions from being weakened to obtain a pass.
Critical: true
Acceptance: Every implementation/debug/verification fixture contains the preregistered evidence and non-weakening constraints appropriate to its prompt kind.
Failure: Missing completion or non-weakening constraints makes the prompt invalid.
Verify: Planned constraint-preservation tests.

### REQ-009-D08
Requirement: Expose prompt compilation through deterministic Python API and CLI JSON output with versioned machine-readable prompt envelopes.
Critical: true
Acceptance: Repeated runs over byte-identical inputs produce byte-equivalent normalized envelopes; malformed inputs return nonzero with structured diagnostics.
Failure: Nondeterministic prompt envelopes or unstructured errors fail the release gate.
Verify: Planned CLI/API tests.

### REQ-009-D09
Requirement: Preserve the exact sealed v0.08 parent suite and every active regression, including task-compiler shadow/integration regressions.
Critical: true
Acceptance: Parent baseline and all active regressions pass unchanged before any v0.09 promotion.
Failure: Any missing/failing active regression blocks promotion; tests may not be weakened to make v0.09 pass.
Verify: Planned independent verifier.

### REQ-009-D10
Requirement: Evaluate prompt compilation on hash-locked development and held-out fixtures spanning all five prompt kinds, blocked tasks, scope attacks, context-closure boundaries, continuation handoffs, and verifier-role separation.
Critical: true
Acceptance: Frozen evaluator reports exact envelope/context matches, corrective-prompt proxy, scope escapes, missing obligations, context over-inclusion, and missing-data state with preregistered denominators.
Failure: Missing/invalid parent dependencies, incomplete denominators, or post-result benchmark edits invalidate the candidate rather than being treated as zero/pass.
Verify: Planned frozen corpus evaluator.

## Proposed evaluation emphasis

Primary candidate evidence should compare bounded compiled prompts with a preregistered generic-prompt baseline on corrective-prompt proxy and exact obligation retention. Guardrails should include zero scope expansion, zero missing critical constraints, zero prerequisite/owner-decision escapes, zero self-certification violations, exact continuation-state preservation, deterministic prompt reproduction, and a bounded context-over-inclusion rate.

Held-out fixtures must be hash-locked before implementation. At least one non-promotional shadow pass should use historical v0.08 tasks/events because v0.07 and v0.08 both demonstrated that perfect synthetic benchmarks can miss integration-shaped defects.

## Non-goals

- no LLM-generated rewriting of product intent;
- no automatic task decomposition or architecture invention;
- no code generation;
- no multi-agent scheduler;
- no hidden retrieval heuristics that cannot explain why context was included or excluded;
- no full promotion claim from same-cycle synthetic evidence alone.
