from __future__ import annotations

from pathlib import Path
import hashlib
import json

from .linter import lint_text


V004_CORPUS_SHA256 = "cc23a138f8a8c4b8d1985a8cde6e4177d9185d7c01f1f777eced3a462d729b7d"
V004_PLAN_SHA256 = "d397f59d72cf83df246beb41a59931b67d8d15d3bd850dce8fc2e2be4925fbc4"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_v004_corpus(root: str | Path) -> dict:
    root = Path(root)
    corpus_path = root / "fixtures/linter/v0.04/corpus.jsonl"
    plan_path = root / "versions/v0.04/EVALUATION-PLAN.json"
    actual_corpus = _sha(corpus_path)
    actual_plan = _sha(plan_path)
    if actual_corpus != V004_CORPUS_SHA256:
        raise ValueError(f"frozen corpus hash mismatch: {actual_corpus}")
    if actual_plan != V004_PLAN_SHA256:
        raise ValueError(f"frozen evaluation-plan hash mismatch: {actual_plan}")

    cases = [json.loads(x) for x in corpus_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    results = []
    defect_total = defect_detected = 0
    clean_total = clean_accepted = 0
    expected_finding_count = emitted_finding_count = 0
    complete_diagnostics = 0
    per_rule = {f"LINT-{i:03d}": {"tp": 0, "fp": 0} for i in range(1, 11)}

    for case in cases:
        report = lint_text(case["document"])
        emitted = [f for f in report.findings if not f.suppressed]
        emitted_rules = [f.rule_id for f in emitted]
        expected = set(case["expected_rules"])
        if case["case_kind"] == "defect":
            defect_total += 1
            if expected.issubset(set(emitted_rules)):
                defect_detected += 1
        else:
            clean_total += 1
            if not emitted:
                clean_accepted += 1

        for f in emitted:
            emitted_finding_count += 1
            if f.rule_id in expected:
                expected_finding_count += 1
                if f.rule_id in per_rule:
                    per_rule[f.rule_id]["tp"] += 1
            elif f.rule_id in per_rule:
                per_rule[f.rule_id]["fp"] += 1
            if f.rule_id and f.rationale and f.span and f.line >= 1 and f.column >= 1:
                complete_diagnostics += 1

        results.append({
            "case_id": case["case_id"],
            "case_kind": case["case_kind"],
            "expected_rules": case["expected_rules"],
            "emitted_rules": emitted_rules,
            "pass": (expected.issubset(set(emitted_rules)) if case["case_kind"] == "defect" else not emitted),
            "findings": [f.as_dict() for f in emitted],
        })

    def ratio(n: int, d: int) -> float | None:
        return None if d == 0 else n / d

    rule_precision = {}
    for rid, counts in per_rule.items():
        denom = counts["tp"] + counts["fp"]
        rule_precision[rid] = ratio(counts["tp"], denom) if denom else 0.0

    metrics = {
        "defect_case_detection_rate": ratio(defect_detected, defect_total),
        "clean_case_acceptance_rate": ratio(clean_accepted, clean_total),
        "finding_precision": ratio(expected_finding_count, emitted_finding_count),
        "diagnostic_completeness_rate": ratio(complete_diagnostics, emitted_finding_count),
        "minimum_per_rule_precision": min(rule_precision.values()) if rule_precision else None,
        "clean_false_positive_count": clean_total - clean_accepted,
    }
    counts = {
        "case_count": len(cases),
        "defect_total": defect_total,
        "defect_detected": defect_detected,
        "clean_total": clean_total,
        "clean_accepted": clean_accepted,
        "emitted_finding_count": emitted_finding_count,
        "expected_finding_count": expected_finding_count,
        "complete_diagnostics": complete_diagnostics,
    }
    return {
        "corpus_sha256": actual_corpus,
        "evaluation_plan_sha256": actual_plan,
        "counts": counts,
        "metrics": metrics,
        "per_rule_precision": rule_precision,
        "cases": results,
    }
