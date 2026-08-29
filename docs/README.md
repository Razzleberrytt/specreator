# Spec Creator Documentation

This directory contains explanatory and prospective design documentation. Exact release authority lives in machine-readable state, frozen contracts, repository history, manifests, receipts, tests and verifier evidence.

## Start here

- [`ROADMAP.md`](ROADMAP.md) — governed path from the mature v0.11.1 baseline to Version 1.00, including convergence and post-v1 boundaries.
- [`VERSION-1.00-CONTRACT.md`](VERSION-1.00-CONTRACT.md) — prospective additive v1 completion criteria. It is intentionally not a retroactive historical contract.
- [`V1-CAPABILITY-MAP.md`](V1-CAPABILITY-MAP.md) — maps v1 capability families to evidence, dependencies, and primary lane responsibility without pre-admitting successors.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — end-to-end system architecture, authority boundaries, failure model, and product/control-plane separation.
- [`ARTIFACTS-AND-AUTHORITY.md`](ARTIFACTS-AND-AUTHORITY.md) — artifact classes, freshness rules, handoff/claim minimums, and authority-conflict resolution.
- [`AUTONOMOUS-DEVELOPMENT.md`](AUTONOMOUS-DEVELOPMENT.md) — five-lane ownership, claims, receipts, freshness, reconciliation and no-churn behavior.

## Architecture research

- [`EXECUTION-EFFICIENCY-ARCHITECTURE.md`](EXECUTION-EFFICIENCY-ARCHITECTURE.md) — execution-efficiency architecture and opportunities.
- [`EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md`](EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md) — existing-solution intelligence and synthesis work.

## Reading paths

For **product architecture**, read `ARCHITECTURE.md` → `ROADMAP.md` → `VERSION-1.00-CONTRACT.md`.

For **autonomous development/governance**, read `AUTONOMOUS-DEVELOPMENT.md` → `ARTIFACTS-AND-AUTHORITY.md` → the live machine-readable files under `ops/`.

For **v1 planning**, read `ROADMAP.md` → `V1-CAPABILITY-MAP.md` → `VERSION-1.00-CONTRACT.md`. The map is prospective; the machine-readable V1 trajectory determines what work has actually been admitted.

## Authority hierarchy

When documentation disagrees with promotion-authoritative evidence, do not guess. Resolve the exact disputed claim against its governing artifacts. In broad order:

1. immutable historical release/frozen evidence for the historical claim it governs;
2. exact repository bytes and hashes;
3. canonical machine-readable orchestration state for current phase authority, after checking that it is fresh against repository reality;
4. exact claims/handoff/verifier receipts and freshness inputs;
5. frozen active candidate contract;
6. prospective trajectory/checklists;
7. explanatory prose documentation.

See [`ARTIFACTS-AND-AUTHORITY.md`](ARTIFACTS-AND-AUTHORITY.md) for the full conflict-resolution and documentation-staleness procedure.

Prose is designed to make the system understandable; it is not a second control plane.
