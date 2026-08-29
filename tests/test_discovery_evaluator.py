from __future__ import annotations

import json
from pathlib import Path

from spec_creator.discovery_evaluator import evaluate_v007_corpus, preflight_discovery_corpus

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_evaluation_and_denominators():
    result = evaluate_v007_corpus(ROOT)
    assert result["counts"]["case_count"] == 72
    assert result["counts"]["heldout_case_count"] == 34
    assert result["counts"]["baseline_question_count"] == 92
    assert result["metrics"]["owner_question_reduction_rate"] >= 0.40
    assert result["metrics"]["information_value_top_selection_accuracy"] >= 0.95
    assert result["metrics"]["heldout_action_exact_match_rate"] >= 0.95
    assert result["metrics"]["safe_inference_exact_match_rate"] == 1.0
    assert result["metrics"]["unsafe_default_count"] == 0
    assert result["metrics"]["critical_ambiguity_escape_count"] == 0
    assert result["metrics"]["dependency_frontier_accuracy"] == 1.0
    assert result["metrics"]["provenance_completeness_rate"] == 1.0
    assert result["metrics"]["unnecessary_question_rate"] <= 0.05
    assert result["metrics"]["rework_proxy_error_count"] == 0


def test_parent_preflight_and_inherited_regressions():
    result = preflight_discovery_corpus(ROOT / "fixtures/discovery/v0.07/corpus.jsonl")
    assert result["ok"]
    assert result["case_count"] == 72
    assert result["parent_preflight_rate"] == 1.0
    frozen = json.loads((ROOT / "evaluation/v007-preregistration-preflight.json").read_text())
    assert frozen["parent_valid_case_count"] == 72
    assert frozen["heldout_case_count"] == 34


def test_v007_self_traceability_complete():
    from spec_creator.traceability import validate_graph
    graph = json.loads((ROOT / "versions/v0.07/TRACEABILITY-GRAPH.json").read_text())
    report = validate_graph(graph)
    assert report.ok
    assert report.critical_requirements_total == 12
    assert report.critical_requirements_complete == 12
    assert report.critical_traceability_coverage_rate == 1.0
