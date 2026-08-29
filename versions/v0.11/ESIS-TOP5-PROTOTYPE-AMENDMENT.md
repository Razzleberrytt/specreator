# ESIS Top-5 Repository Prototype Synthesis Amendment

**Status:** UNFROZEN forward product-direction requirement. This does not alter v0.11 preregistered promotion metrics or authorize v0.11 implementation/freeze.

## Requirement

For an implementation-oriented specification where relevant external repositories exist and ESIS is applicable, Spec Creator must perform broad repository discovery and then select an **exact portfolio of the top 5 distinct qualified repositories related to the specification in progress** before producing the ESIS-informed prototype.

The discovery corpus is not capped at five. Spec Creator searches broadly enough to reach useful capability saturation, deduplicates forks/near-clones, qualifies candidates, and only then chooses the five-repository synthesis portfolio.

## Top-5 portfolio selection

The five repositories are selected as a complementary portfolio, not by stars alone. Selection evidence must consider:

- direct relevance to the active specification;
- demonstrated implementation quality and test evidence;
- maintenance/activity and maturity;
- security posture and dependency risk;
- license/provenance clarity and compatibility;
- architectural compatibility with project constraints;
- uniqueness of useful mechanisms/patterns;
- capability complementarity across the five;
- expected integration cost and rework risk.

Forks, mirrors, and materially equivalent clones do not count as distinct portfolio members.

When enough qualified candidates exist, each selected repository should contribute at least one unique useful pattern, mechanism, interface, test strategy, failure lesson, or license-compatible component to the synthesis. A higher-scoring but redundant source may be replaced by a slightly lower-scoring source that materially improves capability coverage.

## Prototype synthesis rule

The prototype is created from the **best compatible parts of the five selected repositories**, but “combine” means governed synthesis, not blind source-code concatenation.

For every adopted element, Spec Creator must record:

- source repository and stable version/commit;
- capability addressed;
- what is being reused: concept, pattern, interface, test, dependency, or code component;
- why it is preferred over alternatives;
- compatibility assumptions;
- integration contract;
- license/provenance obligations;
- verification requirement.

Unknown or incompatible licensing fails closed for direct code reuse. The system may independently reimplement a documented idea/pattern when legally and technically appropriate.

## Required prototype artifacts

A mature ESIS prototype flow should emit at minimum:

- `repo-candidate-landscape.json`
- `repo-qualification-ledger.json`
- `top-five-repo-portfolio.json`
- `top-five-capability-matrix.json`
- `compatibility-matrix.json`
- `prototype-synthesis-plan.json`
- `prototype-provenance-map.json`
- `prototype-verification-plan.json`

`top-five-repo-portfolio.json` must contain exactly five distinct qualified repository identities for a compliant top-5 synthesis run.

## Insufficient-source behavior

If exhaustive reasonable discovery produces fewer than five qualified distinct repositories, Spec Creator must emit a `TOP5_SOURCE_SHORTFALL` blocker. It must not pad the portfolio with low-quality/duplicate repositories or claim that a top-5 synthesis occurred. The owner may explicitly choose a non-ESIS/limited-source path, but that exception must be visible in the spec and cannot masquerade as the normal top-5 prototype process.

## Validation

Before treating the composite prototype as preferred, compare it against at least:

1. a reasonable blank-slate prototype/design; and
2. the strongest single-repository adaptation.

The composite must not be claimed superior unless verification evidence supports the claim under the project’s quality, security, licensing, maintainability, and time-to-verified-implementation criteria.
