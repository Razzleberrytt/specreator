from pathlib import Path
import hashlib
import json

from spec_creator.ambiguity_evaluator import (
    evaluate_v0061_corpus, preflight_ambiguity_corpus, V0061_CORPUS_SHA256, V0061_PLAN_SHA256,
)

ROOT = Path(__file__).resolve().parents[1]


def test_original_v006_corpus_preflight_detects_invalid_trace_graphs():
    result = preflight_ambiguity_corpus(ROOT / "fixtures/ambiguity/v0.06/corpus.jsonl")
    assert result["ok"] is False
    assert result["trace_graph_case_count"] == 16
    assert result["trace_graph_invalid_count"] == 16


def test_retry_corpus_parent_preflight_passes():
    result = preflight_ambiguity_corpus(ROOT / "fixtures/ambiguity/v0.06.1/corpus.jsonl")
    assert result["ok"] is True
    assert result["trace_graph_valid_count"] == 16


def test_clarification_interception_proxy():
    result = evaluate_v0061_corpus(ROOT)
    m = result["metrics"]
    assert m["defect_case_detection_rate"] >= 0.95
    assert m["clean_case_acceptance_rate"] >= 0.95
    assert m["decision_needed_classification_accuracy"] >= 0.95
    assert m["governed_default_question_count"] == 0
    assert m["priority_top_question_accuracy"] >= 0.90
    assert m["implementation_time_clarification_reduction_proxy_rate"] >= 0.80
    assert m["unnecessary_question_rate"] <= 0.05
    assert m["critical_ambiguity_escape_count"] == 0


def test_retry_evaluator_hash_constants_match_frozen_contract():
    corpus = ROOT / "fixtures/ambiguity/v0.06.1/corpus.jsonl"
    plan = ROOT / "versions/v0.06.1/EVALUATION-PLAN.json"
    contract = json.loads((ROOT / "versions/v0.06.1/FROZEN-RELEASE-CONTRACT.json").read_text())
    corpus_sha = hashlib.sha256(corpus.read_bytes()).hexdigest()
    plan_sha = hashlib.sha256(plan.read_bytes()).hexdigest()
    assert corpus_sha == V0061_CORPUS_SHA256
    assert plan_sha == V0061_PLAN_SHA256
    failures = "\n".join(contract["failure_conditions"])
    assert corpus_sha in failures
    assert plan_sha in failures
