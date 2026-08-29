from __future__ import annotations

from pathlib import Path
import copy
import json

import pytest

from spec_creator.traceability import analyze_impact, parse_graph, validate_graph
from spec_creator.trace_evaluator import evaluate_v005_corpus


ROOT = Path(__file__).resolve().parents[1]
CORPUS = [json.loads(x) for x in (ROOT / "fixtures/traceability/v0.05/corpus.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]


def cases(kind: str):
    return [c for c in CORPUS if c["case_kind"] == kind]


def by_code(code: str):
    return [c for c in cases("invalid") if code in c["expected_codes"]]


def test_valid_graph_parses():
    graph = parse_graph(cases("valid")[0]["graph"])
    assert graph.graph_id.startswith("TG-")
    assert [n["id"] for n in graph.nodes] == [n["id"] for n in cases("valid")[0]["graph"]["nodes"]]


@pytest.mark.parametrize("case", by_code("TRACE-DUPLICATE-NODE") + by_code("TRACE-DUPLICATE-EDGE"), ids=lambda c: c["case_id"])
def test_duplicate_node_and_edge_detection(case):
    emitted = {d.code for d in validate_graph(case["graph"]).errors}
    assert set(case["expected_codes"]).issubset(emitted)


@pytest.mark.parametrize("case", by_code("TRACE-BROKEN-REFERENCE"), ids=lambda c: c["case_id"])
def test_broken_edge_reference_detection(case):
    report = validate_graph(case["graph"])
    assert {d.code for d in report.errors} == {"TRACE-BROKEN-REFERENCE"}
    assert any("MISSING" in (d.node_id or "") for d in report.errors)


@pytest.mark.parametrize("case", by_code("TRACE-INVALID-TRANSITION"), ids=lambda c: c["case_id"])
def test_invalid_relation_transition_detection(case):
    assert {d.code for d in validate_graph(case["graph"]).errors} == {"TRACE-INVALID-TRANSITION"}


@pytest.mark.parametrize("case", by_code("TRACE-CYCLE"), ids=lambda c: c["case_id"])
def test_cycle_detection(case):
    report = validate_graph(case["graph"])
    assert {d.code for d in report.errors} == {"TRACE-CYCLE"}
    assert report.errors[0].node_id is not None


def test_critical_traceability_coverage():
    for case in cases("valid") + cases("impact"):
        report = validate_graph(case["graph"])
        assert report.ok
        assert report.critical_traceability_coverage_rate == 1.0
        assert report.critical_requirements_total == report.critical_requirements_complete


@pytest.mark.parametrize("case", [c for c in cases("invalid") if c["expected_codes"][0].startswith("TRACE-MISSING-")], ids=lambda c: c["case_id"])
def test_orphan_critical_requirement_detection(case):
    report = validate_graph(case["graph"])
    assert [d.code for d in report.errors] == case["expected_codes"]


@pytest.mark.parametrize("case", cases("impact"), ids=lambda c: c["case_id"])
def test_impact_analysis(case):
    report = analyze_impact(case["graph"], case["impact_seed_ids"])
    assert report.ok
    assert list(report.upstream) == case["expected_upstream"]
    assert list(report.downstream) == case["expected_downstream"]


def test_impact_unknown_seed_is_error():
    report = analyze_impact(cases("valid")[0]["graph"], ["NO-SUCH-NODE"])
    assert not report.ok
    assert [d.code for d in report.diagnostics] == ["TRACE-UNKNOWN-SEED"]


def test_traceability_schema_rejects_malformed_graph():
    graph = copy.deepcopy(cases("valid")[0]["graph"])
    del graph["graph_id"]
    report = validate_graph(graph)
    assert not report.ok
    assert {d.code for d in report.errors} == {"TRACE-SCHEMA"}


def test_frozen_v005_corpus_evaluation_is_perfect():
    result = evaluate_v005_corpus(ROOT)
    assert result["counts"]["case_count"] == 30
    assert result["metrics"] == {
        "invalid_graph_detection_rate": 1.0,
        "valid_graph_acceptance_rate": 1.0,
        "critical_traceability_coverage_rate": 1.0,
        "impact_analysis_exact_match_rate": 1.0,
        "diagnostic_code_precision": 1.0,
        "valid_graph_false_positive_count": 0,
    }


def test_impact_order_follows_traceability_chain_regression():
    """REG-0007: impact members are ordered by governed chain, not lexical ID."""
    case = cases("impact")[0]
    report = analyze_impact(case["graph"], case["impact_seed_ids"])
    assert list(report.upstream) == case["expected_upstream"]
    assert list(report.downstream) == case["expected_downstream"]
