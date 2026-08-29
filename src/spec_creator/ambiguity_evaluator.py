from __future__ import annotations

from pathlib import Path
import hashlib
import json

from .ambiguity import analyze_ambiguity
from .traceability import validate_graph

V0061_CORPUS_SHA256 = "3d147717ff2501061f72a0c5f384403751297eb91b6d916fd4fbb48e9edf5f9e"
V0061_PLAN_SHA256 = "70e3f6c5017fc2a6aef312065ec7f705cbc055f9cec46aec6144c1a1ee6a0bc5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ratio(n: int, d: int) -> float | None:
    return None if d == 0 else n / d


def preflight_ambiguity_corpus(path: str | Path) -> dict:
    path = Path(path)
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    trace_cases = []
    for row in rows:
        if "trace_graph" not in row:
            continue
        report = validate_graph(row["trace_graph"])
        trace_cases.append({
            "case_id": row.get("case_id"),
            "valid": report.ok,
            "diagnostics": [d.as_dict() for d in report.errors],
        })
    return {
        "case_count": len(rows),
        "trace_graph_case_count": len(trace_cases),
        "trace_graph_valid_count": sum(x["valid"] for x in trace_cases),
        "trace_graph_invalid_count": sum(not x["valid"] for x in trace_cases),
        "ok": all(x["valid"] for x in trace_cases),
        "trace_cases": trace_cases,
    }


def evaluate_v0061_corpus(root: str | Path) -> dict:
    root = Path(root)
    corpus_path = root / "fixtures/ambiguity/v0.06.1/corpus.jsonl"
    plan_path = root / "versions/v0.06.1/EVALUATION-PLAN.json"
    actual_corpus = _sha(corpus_path)
    actual_plan = _sha(plan_path)
    if actual_corpus != V0061_CORPUS_SHA256:
        raise ValueError(f"frozen ambiguity retry corpus hash mismatch: {actual_corpus}")
    if actual_plan != V0061_PLAN_SHA256:
        raise ValueError(f"frozen v0.06.1 evaluation-plan hash mismatch: {actual_plan}")

    preflight = preflight_ambiguity_corpus(corpus_path)
    if not preflight["ok"]:
        raise ValueError("frozen ambiguity retry corpus contains invalid embedded traceability graph(s)")

    cases = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    defect_total = defect_detected = 0
    clean_total = clean_accepted = 0
    expected_candidate_total = expected_candidate_exact = 0
    governed_default_questions = 0
    priority_total = priority_exact = 0
    workflow_trigger_total = workflow_intercepted = 0
    critical_trigger_total = critical_intercepted = 0
    emitted_questions = unnecessary_questions = 0

    for case in cases:
        report = analyze_ambiguity(case["document"], trace_graph=case.get("trace_graph"))
        actual = {(f.block_id, f.code): f for f in report.findings}
        expected = {(f["block_id"], f["code"]): f for f in case.get("expected_findings", [])}
        expected_decision = {k for k, v in expected.items() if v.get("decision_needed") is True}
        question_pairs = {(f.block_id, f.code) for f in report.questions}

        exact_candidates = 0
        for key, exp in expected.items():
            expected_candidate_total += 1
            got = actual.get(key)
            exact = bool(got and got.decision_needed == exp["decision_needed"] and got.disposition == exp["disposition"])
            if exact:
                expected_candidate_exact += 1
                exact_candidates += 1

        kind = case["case_kind"]
        if kind == "defect":
            defect_total += 1
            if all(k in actual for k in expected):
                defect_detected += 1
        if kind == "clean":
            clean_total += 1
            if not report.findings:
                clean_accepted += 1
        if kind == "resolved":
            governed_default_questions += len(report.questions)
        if kind == "priority":
            priority_total += 1
            top = report.questions[0] if report.questions else None
            exp_top = case["expected_top_question"]
            if top and (top.block_id, top.code) == (exp_top["block_id"], exp_top["code"]):
                priority_exact += 1
        if kind == "workflow":
            triggers = int(case["true_implementation_clarification_triggers"])
            critical = int(case.get("critical_trigger_count", triggers))
            matched = len(expected_decision & question_pairs)
            workflow_trigger_total += triggers
            workflow_intercepted += min(matched, triggers)
            critical_trigger_total += critical
            critical_intercepted += min(matched, critical)

        emitted_questions += len(report.questions)
        unnecessary_questions += len(question_pairs - expected_decision)
        results.append({
            "case_id": case["case_id"],
            "case_kind": kind,
            "expected_candidate_count": len(expected),
            "exact_classification_count": exact_candidates,
            "finding_pairs": sorted([list(k) for k in actual]),
            "question_pairs": sorted([list(k) for k in question_pairs]),
            "top_question": None if not report.questions else {"block_id": report.questions[0].block_id, "code": report.questions[0].code},
        })

    metrics = {
        "defect_case_detection_rate": _ratio(defect_detected, defect_total),
        "clean_case_acceptance_rate": _ratio(clean_accepted, clean_total),
        "decision_needed_classification_accuracy": _ratio(expected_candidate_exact, expected_candidate_total),
        "governed_default_question_count": governed_default_questions,
        "priority_top_question_accuracy": _ratio(priority_exact, priority_total),
        "implementation_time_clarification_reduction_proxy_rate": _ratio(workflow_intercepted, workflow_trigger_total),
        "unnecessary_question_rate": _ratio(unnecessary_questions, emitted_questions),
        "critical_ambiguity_escape_count": critical_trigger_total - critical_intercepted,
    }
    counts = {
        "case_count": len(cases),
        "defect_total": defect_total,
        "defect_detected": defect_detected,
        "clean_total": clean_total,
        "clean_accepted": clean_accepted,
        "expected_candidate_total": expected_candidate_total,
        "expected_candidate_exact": expected_candidate_exact,
        "governed_default_questions": governed_default_questions,
        "priority_total": priority_total,
        "priority_exact": priority_exact,
        "workflow_trigger_total": workflow_trigger_total,
        "workflow_intercepted": workflow_intercepted,
        "critical_trigger_total": critical_trigger_total,
        "critical_intercepted": critical_intercepted,
        "emitted_questions": emitted_questions,
        "unnecessary_questions": unnecessary_questions,
    }
    return {
        "corpus_sha256": actual_corpus,
        "evaluation_plan_sha256": actual_plan,
        "preflight": preflight,
        "counts": counts,
        "metrics": metrics,
        "cases": results,
    }
