from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from spec_creator.lint_evaluator import evaluate_v004_corpus
from spec_creator.linter import lint_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def rules(report):
    return [f.rule_id for f in report.findings if not f.suppressed]


def test_frozen_v004_corpus_meets_all_preregistered_targets():
    result = evaluate_v004_corpus(PROJECT_ROOT)
    assert result["counts"]["case_count"] == 100
    assert result["counts"]["defect_total"] == 50
    assert result["counts"]["clean_total"] == 50
    assert result["metrics"] == {
        "defect_case_detection_rate": 1.0,
        "clean_case_acceptance_rate": 1.0,
        "finding_precision": 1.0,
        "diagnostic_completeness_rate": 1.0,
        "minimum_per_rule_precision": 1.0,
        "clean_false_positive_count": 0,
    }
    assert set(result["per_rule_precision"].values()) == {1.0}


def test_diagnostics_have_exact_source_spans():
    text = "The service must be fast and user-friendly.\n"
    report = lint_text(text)
    assert report.findings
    source = text.splitlines()[0]
    for finding in report.findings:
        start = finding.column - 1
        assert source[start:start + len(finding.span)] == finding.span
        assert finding.rationale


def test_constraint_contradiction_has_related_line():
    report = lint_text("Constraint: mode = json\nConstraint: mode = text\n")
    finding = next(f for f in report.findings if f.rule_id == "LINT-007")
    assert finding.related_line == 1
    assert finding.line == 2


def test_approved_local_suppression_is_honored():
    text = "Lint-Suppress: LINT-001 decision=DEC-9001\nThe service must be fast.\n"
    report = lint_text(text, approved_decisions={"DEC-9001"})
    vague = next(f for f in report.findings if f.rule_id == "LINT-001")
    assert vague.suppressed is True
    assert vague.suppression_decision_id == "DEC-9001"
    assert report.ok is True


def test_unapproved_suppression_cannot_hide_finding():
    text = "Lint-Suppress: LINT-001 decision=DEC-9001\nThe service must be fast.\n"
    report = lint_text(text)
    assert "LINT-001" in rules(report)
    assert "LINT-SUPPRESS-001" in rules(report)
    assert report.ok is False


def test_invalid_blanket_suppression_is_rejected():
    text = "Lint-Suppress: ALL decision=DEC-9001\nThe service must be fast.\n"
    report = lint_text(text, approved_decisions={"DEC-9001"})
    assert "LINT-SUPPRESS-001" in rules(report)
    assert "LINT-001" in rules(report)


def test_frozen_corpus_hash_drift_fails(tmp_path):
    import shutil
    ws = tmp_path / "ws"
    shutil.copytree(PROJECT_ROOT / "fixtures", ws / "fixtures")
    (ws / "versions/v0.04").mkdir(parents=True)
    shutil.copy2(PROJECT_ROOT / "versions/v0.04/EVALUATION-PLAN.json", ws / "versions/v0.04/EVALUATION-PLAN.json")
    corpus = ws / "fixtures/linter/v0.04/corpus.jsonl"
    corpus.write_text(corpus.read_text() + "{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="corpus hash mismatch"):
        evaluate_v004_corpus(ws)


def test_frozen_plan_hash_drift_fails(tmp_path):
    import shutil
    ws = tmp_path / "ws"
    shutil.copytree(PROJECT_ROOT / "fixtures", ws / "fixtures")
    (ws / "versions/v0.04").mkdir(parents=True)
    plan = ws / "versions/v0.04/EVALUATION-PLAN.json"
    shutil.copy2(PROJECT_ROOT / "versions/v0.04/EVALUATION-PLAN.json", plan)
    plan.write_text(plan.read_text().replace("preregistered-pre-freeze", "changed"), encoding="utf-8")
    with pytest.raises(ValueError, match="evaluation-plan hash mismatch"):
        evaluate_v004_corpus(ws)
