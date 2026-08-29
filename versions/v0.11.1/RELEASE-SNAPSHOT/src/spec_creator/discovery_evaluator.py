from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import re

from .ambiguity import analyze_ambiguity
from .discovery import plan_discovery
from .linter import lint_text
from .models import canonical_contract_hash
from .traceability import validate_graph


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            raise ValueError(f"{path}:{line_no}: malformed JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{line_no}: record must be object")
        out.append(obj)
    return out


def _canonical_jsonl(records: list[dict[str, Any]]) -> bytes:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for r in records).encode("utf-8")


def _condition_hash(contract: dict[str, Any], label: str) -> str:
    for cond in contract.get("failure_conditions", []):
        if label.lower() in cond.lower():
            m = re.search(r"\b[0-9a-f]{64}\b", cond)
            if m:
                return m.group(0)
    raise ValueError(f"frozen contract missing hash condition for {label}")


def preflight_discovery_corpus(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    cases = _load_jsonl(path)
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    ok_count = 0
    graph_count = 0
    for case in cases:
        cid = case.get("case_id")
        if not isinstance(cid, str) or not cid:
            raise ValueError("case missing case_id")
        duplicate = cid in seen
        seen.add(cid)
        doc = case.get("document")
        if not isinstance(doc, str):
            raise ValueError(f"{cid}: document must be string")
        lint = lint_text(doc)
        graph = case.get("trace_graph")
        graph_ok = True
        if graph is not None:
            graph_count += 1
            graph_ok = validate_graph(graph).ok
        amb = analyze_ambiguity(doc, trace_graph=graph)
        baseline = sum(f.decision_needed for f in amb.findings)
        expected = ((case.get("expected") or {}).get("baseline_question_count"))
        baseline_ok = isinstance(expected, int) and baseline == expected
        row_ok = (not duplicate) and lint.ok and graph_ok and baseline_ok
        ok_count += int(row_ok)
        rows.append({
            "case_id": cid,
            "duplicate_case_id": duplicate,
            "lint_ok": lint.ok,
            "trace_graph_ok": graph_ok,
            "baseline_question_count": baseline,
            "expected_baseline_question_count": expected,
            "ok": row_ok,
        })
    return {
        "ok": ok_count == len(cases),
        "case_count": len(cases),
        "parent_valid_case_count": ok_count,
        "parent_preflight_rate": (ok_count / len(cases)) if cases else None,
        "graph_backed_case_count": graph_count,
        "cases": rows,
    }


def _action_lookup(plan: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(a["block_id"], a["code"]): a for a in plan.get("actions", [])}


def _match_expected_action(expected: dict[str, Any], actual: dict[str, Any] | None) -> bool:
    if actual is None:
        return False
    for key in ("block_id", "code", "action"):
        if actual.get(key) != expected.get(key):
            return False
    if "value" in expected and actual.get("value") != expected.get("value"):
        return False
    return True


def evaluate_v007_corpus(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    contract_path = root / "versions/v0.07/FROZEN-RELEASE-CONTRACT.json"
    plan_path = root / "versions/v0.07/EVALUATION-PLAN.json"
    corpus_path = root / "fixtures/discovery/v0.07/corpus.jsonl"
    heldout_path = root / "fixtures/discovery/v0.07/heldout.jsonl"

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    eval_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if canonical_contract_hash(contract) != contract.get("contract_hash"):
        raise ValueError("frozen v0.07 contract hash mismatch")
    frozen_plan_sha = _condition_hash(contract, "evaluation-plan")
    frozen_corpus_sha = _condition_hash(contract, "combined discovery corpus")
    frozen_heldout_sha = _condition_hash(contract, "held-out partition")
    if _sha(plan_path) != frozen_plan_sha:
        raise ValueError("frozen v0.07 evaluation plan hash mismatch")
    if _sha(corpus_path) != frozen_corpus_sha:
        raise ValueError("frozen v0.07 corpus hash mismatch")
    if _sha(heldout_path) != frozen_heldout_sha:
        raise ValueError("frozen v0.07 heldout hash mismatch")

    cases = _load_jsonl(corpus_path)
    heldout_records = _load_jsonl(heldout_path)
    filtered_heldout = [c for c in cases if c.get("partition") == "heldout"]
    if _canonical_jsonl(filtered_heldout) != heldout_path.read_bytes():
        raise ValueError("heldout partition is not an exact frozen subset of combined corpus")

    preflight = preflight_discovery_corpus(corpus_path)
    case_results: list[dict[str, Any]] = []

    baseline_questions = 0
    adaptive_question_batches = 0
    priority_total = priority_correct = 0
    heldout_action_total = heldout_action_correct = 0
    safe_total = safe_correct = 0
    unsafe_default_count = 0
    critical_escape_count = 0
    dependency_total = dependency_correct = 0
    provenance_total = provenance_complete = 0
    zero_question_case_total = unnecessary_question_batches = 0
    rework_proxy_error_count = 0

    for case in cases:
        cid = case["case_id"]
        result = plan_discovery(case["document"], profile=case.get("profile"), trace_graph=case.get("trace_graph")).as_dict()
        expected = case["expected"]
        baseline_questions += expected["baseline_question_count"]
        adaptive_question_batches += result["summary"]["question_batches"]
        actual_lookup = _action_lookup(result)
        expected_actions = expected.get("actions", [])
        matched = 0
        action_exact = len(result.get("actions", [])) == len(expected_actions)
        for ea in expected_actions:
            aa = actual_lookup.get((ea["block_id"], ea["code"]))
            good = _match_expected_action(ea, aa)
            matched += int(good)
            action_exact = action_exact and good
            if case.get("partition") == "heldout":
                heldout_action_total += 1
                heldout_action_correct += int(good)
        actual_groups = sorted(q["group_id"] for q in result.get("questions", []))
        expected_groups = sorted(expected.get("selected_batch_groups", []))
        group_exact = actual_groups == expected_groups

        if case.get("category") in {"dependency", "batch_budget"}:
            priority_total += 1
            priority_correct += int(group_exact)
        if case.get("category") == "safe_default":
            safe_total += 1
            safe_correct += int(action_exact and any(a.get("action") == "infer_default" for a in result.get("actions", [])))
        if case.get("category") == "unsafe_default":
            unsafe_default_count += sum(a.get("action") == "infer_default" for a in result.get("actions", []))
        if case.get("category") == "dependency":
            dependency_total += 1
            dependency_correct += int(action_exact and group_exact)
        if expected["baseline_question_count"] == 0:
            zero_question_case_total += 1
            unnecessary_question_batches += result["summary"]["question_batches"]

        # Critical owner decisions may be asked now or explicitly dependency-deferred, but never budget-hidden/defaulted.
        amb = analyze_ambiguity(case["document"], trace_graph=case.get("trace_graph"))
        for f in amb.findings:
            if f.critical and f.decision_needed:
                aa = actual_lookup.get((f.block_id, f.code))
                if aa is None or aa.get("action") not in {"ask_now", "defer_dependency"}:
                    critical_escape_count += 1

        for a in result.get("actions", []):
            provenance_total += 1
            prov = a.get("provenance")
            if a.get("reason") and isinstance(prov, dict) and prov.get("source") and prov.get("ref"):
                provenance_complete += 1

        case_exact = action_exact and group_exact and result["summary"]["baseline_questions"] == expected["baseline_question_count"] and result["summary"]["question_batches"] == expected["question_batch_count"]
        if not case_exact:
            rework_proxy_error_count += 1
        case_results.append({
            "case_id": cid,
            "partition": case.get("partition"),
            "category": case.get("category"),
            "action_exact": action_exact,
            "question_groups_exact": group_exact,
            "expected_question_batches": expected["question_batch_count"],
            "actual_question_batches": result["summary"]["question_batches"],
            "expected_action_count": len(expected_actions),
            "matched_action_count": matched,
            "ok": case_exact,
        })

    metrics = {
        "owner_question_reduction_rate": ((baseline_questions - adaptive_question_batches) / baseline_questions) if baseline_questions else None,
        "information_value_top_selection_accuracy": (priority_correct / priority_total) if priority_total else None,
        "heldout_action_exact_match_rate": (heldout_action_correct / heldout_action_total) if heldout_action_total else None,
        "safe_inference_exact_match_rate": (safe_correct / safe_total) if safe_total else None,
        "unsafe_default_count": unsafe_default_count,
        "critical_ambiguity_escape_count": critical_escape_count,
        "dependency_frontier_accuracy": (dependency_correct / dependency_total) if dependency_total else None,
        "provenance_completeness_rate": (provenance_complete / provenance_total) if provenance_total else None,
        "unnecessary_question_rate": (unnecessary_question_batches / zero_question_case_total) if zero_question_case_total else None,
        "rework_proxy_error_count": rework_proxy_error_count,
        "parent_preflight_rate": preflight["parent_preflight_rate"],
    }
    counts = {
        "case_count": len(cases),
        "heldout_case_count": len(heldout_records),
        "baseline_question_count": baseline_questions,
        "adaptive_question_batch_count": adaptive_question_batches,
        "priority_case_count": priority_total,
        "heldout_action_count": heldout_action_total,
        "safe_default_case_count": safe_total,
        "unsafe_default_case_count": sum(c.get("category") == "unsafe_default" for c in cases),
        "dependency_case_count": dependency_total,
        "provenance_action_count": provenance_total,
        "zero_question_case_count": zero_question_case_total,
    }
    return {
        "evaluation_id": "CORPUS-EVAL-007-001",
        "candidate_version": "0.07",
        "hashes": {
            "contract_canonical_sha256": contract["contract_hash"],
            "evaluation_plan_sha256": _sha(plan_path),
            "corpus_sha256": _sha(corpus_path),
            "heldout_sha256": _sha(heldout_path),
        },
        "counts": counts,
        "metrics": metrics,
        "parent_preflight": {k: v for k, v in preflight.items() if k != "cases"},
        "case_results": case_results,
    }
