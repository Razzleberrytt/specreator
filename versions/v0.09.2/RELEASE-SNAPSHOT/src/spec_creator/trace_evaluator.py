from __future__ import annotations

from pathlib import Path
import hashlib
import json

from .traceability import analyze_impact, validate_graph


V005_CORPUS_SHA256 = "f80475f84faad0afeb57da0d4db385274debe0760f87e2687fec0457d7ba3c21"
V005_PLAN_SHA256 = "3f97c63e65b6d3d9a3c217a8bed60b5129c2ade80a9f34c636852e645205a881"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ratio(n: int, d: int) -> float | None:
    return None if d == 0 else n / d


def evaluate_v005_corpus(root: str | Path) -> dict:
    root = Path(root)
    corpus_path = root / "fixtures/traceability/v0.05/corpus.jsonl"
    plan_path = root / "versions/v0.05/EVALUATION-PLAN.json"
    actual_corpus = _sha(corpus_path)
    actual_plan = _sha(plan_path)
    if actual_corpus != V005_CORPUS_SHA256:
        raise ValueError(f"frozen traceability corpus hash mismatch: {actual_corpus}")
    if actual_plan != V005_PLAN_SHA256:
        raise ValueError(f"frozen v0.05 evaluation-plan hash mismatch: {actual_plan}")

    cases = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results: list[dict] = []
    invalid_total = invalid_detected = 0
    accepted_total = accepted_count = 0
    expected_diag_hits = emitted_diag_total = 0
    critical_total = critical_complete = 0
    impact_total = impact_exact = 0

    for case in cases:
        report = validate_graph(case["graph"])
        emitted_codes = [d.code for d in report.errors]
        expected_codes = list(case.get("expected_codes", []))
        expected_set = set(expected_codes)
        kind = case["case_kind"]
        row: dict = {
            "case_id": case["case_id"],
            "case_kind": kind,
            "expected_codes": expected_codes,
            "emitted_codes": emitted_codes,
            "validation_ok": report.ok,
            "critical_requirements_total": report.critical_requirements_total,
            "critical_requirements_complete": report.critical_requirements_complete,
        }

        if kind == "invalid":
            invalid_total += 1
            detected = expected_set.issubset(set(emitted_codes))
            if detected:
                invalid_detected += 1
            for code in emitted_codes:
                emitted_diag_total += 1
                if code in expected_set:
                    expected_diag_hits += 1
            row["pass"] = detected and all(code in expected_set for code in emitted_codes)
        else:
            accepted_total += 1
            if report.ok:
                accepted_count += 1
            # Frozen denominator includes all critical requirements in every
            # valid/impact benchmark graph, whether or not the implementation
            # accepts it. This prevents acceptance failures shrinking coverage.
            critical_in_graph = sum(1 for n in case["graph"]["nodes"] if n.get("type") == "requirement" and n.get("critical") is True)
            critical_total += critical_in_graph
            if report.ok:
                critical_complete += report.critical_requirements_complete
            row["pass"] = report.ok

            if kind == "impact":
                impact_total += 1
                impact = analyze_impact(case["graph"], case["impact_seed_ids"])
                actual_up = list(impact.upstream)
                actual_down = list(impact.downstream)
                exact = impact.ok and actual_up == case["expected_upstream"] and actual_down == case["expected_downstream"]
                if exact:
                    impact_exact += 1
                row["impact"] = {
                    "seed_ids": list(impact.seed_ids),
                    "actual_upstream": actual_up,
                    "actual_downstream": actual_down,
                    "expected_upstream": case["expected_upstream"],
                    "expected_downstream": case["expected_downstream"],
                    "exact_match": exact,
                }
                row["pass"] = row["pass"] and exact
        results.append(row)

    metrics = {
        "invalid_graph_detection_rate": _ratio(invalid_detected, invalid_total),
        "valid_graph_acceptance_rate": _ratio(accepted_count, accepted_total),
        "critical_traceability_coverage_rate": _ratio(critical_complete, critical_total),
        "impact_analysis_exact_match_rate": _ratio(impact_exact, impact_total),
        "diagnostic_code_precision": _ratio(expected_diag_hits, emitted_diag_total),
        "valid_graph_false_positive_count": accepted_total - accepted_count,
    }
    counts = {
        "case_count": len(cases),
        "invalid_total": invalid_total,
        "invalid_detected": invalid_detected,
        "accepted_graph_total": accepted_total,
        "accepted_graph_count": accepted_count,
        "critical_requirement_total": critical_total,
        "critical_requirement_complete": critical_complete,
        "impact_total": impact_total,
        "impact_exact": impact_exact,
        "emitted_invalid_diagnostic_count": emitted_diag_total,
        "expected_invalid_diagnostic_hits": expected_diag_hits,
    }
    return {
        "corpus_sha256": actual_corpus,
        "evaluation_plan_sha256": actual_plan,
        "counts": counts,
        "metrics": metrics,
        "cases": results,
    }
