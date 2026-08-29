# Spec Creator v0.05 — Traceability Engine (Draft)

**Status:** Draft successor specification; not frozen and not implemented  
**Parent:** v0.04 (PROMOTED AS EXPERIMENTAL)

## Objective

Build and verify a machine-readable Goal → Requirement → Feature → Task → Test → Gate graph so critical delivery claims are supported by an explicit path rather than identifier presence alone.

The v0.04 cycle established two constraints for v0.05:

- current mutable project state and immutable historical release evidence must remain distinct; and
- a reference string is not evidence of valid traceability unless the referenced node exists and the relationship is semantically allowed.

## Graph model

A traceability graph contains typed nodes and typed directed edges.

Node types:

- goal
- requirement
- feature
- task
- test
- gate

Allowed primary chain:

`goal → requirement → feature → task → test → gate`

A critical requirement is complete only when it is reachable from at least one goal and reaches at least one gate through the full ordered chain.

The engine also reports upstream and downstream impact for selected changed nodes.

### REQ-005-001
Requirement: Parse a versioned JSON traceability graph with typed nodes and edges.
Critical: true
Acceptance: Valid graph fixtures produce a deterministic in-memory graph with stable node and edge ordering.
Verify: tests/test_traceability.py::test_valid_graph_parses

### REQ-005-002
Requirement: Reject duplicate node IDs and duplicate directed edges.
Critical: true
Acceptance: Frozen duplicate-node and duplicate-edge fixtures are rejected with stable diagnostic codes.
Verify: tests/test_traceability.py::test_duplicate_node_and_edge_detection

### REQ-005-003
Requirement: Reject edges whose source or target node does not exist.
Critical: true
Acceptance: Every frozen broken-reference fixture is rejected and names the missing node ID.
Verify: tests/test_traceability.py::test_broken_edge_reference_detection

### REQ-005-004
Requirement: Enforce allowed edge type transitions for the primary traceability chain.
Critical: true
Acceptance: Edges that skip or reverse the declared chain are rejected unless a future version explicitly adds a governed relation type.
Verify: tests/test_traceability.py::test_invalid_relation_transition_detection

### REQ-005-005
Requirement: Detect directed cycles in the primary delivery graph.
Critical: true
Acceptance: Every frozen cyclic graph is rejected and reports at least one involved node.
Verify: tests/test_traceability.py::test_cycle_detection

### REQ-005-006
Requirement: Compute complete critical traceability from goal through requirement, feature, task, test, and gate.
Critical: true
Acceptance: Every critical requirement in a valid frozen graph has at least one complete ordered path and the engine reports coverage deterministically.
Verify: tests/test_traceability.py::test_critical_traceability_coverage

### REQ-005-007
Requirement: Detect orphan critical requirements that lack an upstream goal or any required downstream chain segment.
Critical: true
Acceptance: Frozen orphan and missing-segment fixtures are rejected with the first missing traceability stage identified.
Verify: tests/test_traceability.py::test_orphan_critical_requirement_detection

### REQ-005-008
Requirement: Compute upstream and downstream impact sets for one or more changed node IDs.
Critical: true
Acceptance: Frozen impact fixtures match the exact preregistered upstream and downstream node sets.
Verify: tests/test_traceability.py::test_impact_analysis

### REQ-005-009
Requirement: Expose traceability validation and impact analysis through an importable API and CLI JSON output.
Critical: true
Acceptance: CLI and API outputs are deterministic and return nonzero for invalid graphs or unknown impact seed IDs.
Verify: tests/test_traceability_cli.py::test_traceability_cli

### REQ-005-010
Requirement: Preserve v0.04 validator, linter, historical-release, and append-only regression behavior.
Critical: true
Acceptance: The inherited suite and active regressions REG-0001 through REG-0006 remain passing.
Verify: tests/test_validator.py and tests/test_linter.py

## Architecture

Use a small deterministic Python module. Do not add a database, GUI, network dependency, graph-embedding model, or repository source-code analysis in v0.05.

The traceability engine may use adjacency maps and breadth/depth traversal. Graph ordering and diagnostics must remain reproducible.

## Evaluation design requirement

Before implementation, create and hash-lock a traceability corpus containing valid complete graphs, duplicate IDs/edges, broken references, invalid transitions, cycles, orphan critical requirements, missing downstream stages, and exact impact-analysis expectations.

## Promotion limit

Synthetic graph-corpus success can justify PROMOTED AS EXPERIMENTAL. It does not prove that traceability improves delivery outcomes on independent software projects.
