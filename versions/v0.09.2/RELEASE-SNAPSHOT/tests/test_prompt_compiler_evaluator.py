from pathlib import Path
from spec_creator.prompt_compiler_evaluator import evaluate_v0092_corpus

ROOT = Path(__file__).resolve().parents[1]


def test_v0092_frozen_corpus_metrics_are_exact_where_corpus_scored():
    result = evaluate_v0092_corpus(ROOT)
    m = result["metrics"]
    assert m["development_prompt_envelope_exact_match_rate"] == 1.0
    assert m["heldout_prompt_envelope_exact_match_rate"] == 1.0
    assert m["negative_case_classification_accuracy"] == 1.0
    assert m["obligation_retention_rate"] == 1.0
    assert m["benchmark_contrast_preflight_rate"] == 1.0
    assert m["preregistration_precondition_pass_rate"] == 1.0
    assert result["missing_data"] == ["inherited_regression_pass_rate", "critical_gate_bypass_count", "missing_data_count"]


def test_reg0023_v0092_evaluator_metric_names_match_frozen_plan():
    import json
    result = evaluate_v0092_corpus(ROOT)
    plan = json.loads((ROOT / "versions/v0.09.2/EVALUATION-PLAN.json").read_text(encoding="utf-8"))
    frozen_names = {m["name"] for m in plan["primary_metrics"] + plan["guardrail_metrics"]}
    corpus_scored = {name for name, value in result["metrics"].items() if value is not None}
    assert "v0092_spec_quality_acceptance_rate" in corpus_scored
    assert "v009_spec_quality_acceptance_rate" not in result["metrics"]
    assert corpus_scored <= frozen_names
