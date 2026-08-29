from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from .task_compiler import compile_project
from .task_execution import replay_task_events


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_v008_corpus(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    contract = json.loads((root / "versions/v0.08/FROZEN-RELEASE-CONTRACT.json").read_text(encoding="utf-8"))
    plan = json.loads((root / "versions/v0.08/EVALUATION-PLAN.json").read_text(encoding="utf-8"))
    corpus = _load_jsonl(root / plan["corpus"]["combined_path"])
    execution = _load_jsonl(root / plan["corpus"]["execution_path"])

    expected_hashes = {
        "evaluation_plan": next(x.split()[-1].rstrip(".") for x in contract["failure_conditions"] if x.startswith("Frozen evaluation-plan SHA-256 differs from")),
        "compiler_corpus": next(x.split()[-1].rstrip(".") for x in contract["failure_conditions"] if x.startswith("Frozen compiler corpus SHA-256 differs from")),
        "heldout": next(x.split()[-1].rstrip(".") for x in contract["failure_conditions"] if x.startswith("Frozen held-out partition SHA-256 differs from")),
        "execution": next(x.split()[-1].rstrip(".") for x in contract["failure_conditions"] if x.startswith("Frozen execution corpus SHA-256 differs from")),
    }
    hash_checks = {
        "evaluation_plan": _sha(root / "versions/v0.08/EVALUATION-PLAN.json") == expected_hashes["evaluation_plan"],
        "compiler_corpus": _sha(root / plan["corpus"]["combined_path"]) == expected_hashes["compiler_corpus"],
        "heldout": _sha(root / plan["corpus"]["heldout_path"]) == expected_hashes["heldout"],
        "execution": _sha(root / plan["corpus"]["execution_path"]) == expected_hashes["execution"],
    }

    rows = []
    accepted_total = accepted_exact = held_acc_total = held_acc_exact = 0
    neg_total = neg_exact = 0
    dep_prov_num = dep_prov_den = 0
    trace_num = trace_den = 0
    parallel_num = parallel_den = 0
    unresolved_escape = unsafe_parallel = oversized_escape = cycle_escape = invented_dep = 0
    repeat_num = repeat_den = 0

    for case in corpus:
        actual = compile_project(case["project"], root=root)
        actual2 = compile_project(case["project"], root=root)
        repeat_den += 1
        if actual == actual2:
            repeat_num += 1
        expected = case["expected"]
        result = {"case_id": case["case_id"], "category": case["category"], "partition": case["partition"], "actual_status": actual["status"], "expected_status": expected["status"]}
        if expected["status"] == "compiled":
            accepted_total += 1
            if case["partition"] == "heldout":
                held_acc_total += 1
            exact = actual == expected
            accepted_exact += int(exact)
            if case["partition"] == "heldout": held_acc_exact += int(exact)
            result["exact"] = exact
            expected_by = {t["task_id"]: t for t in expected["tasks"]}
            actual_by = {t["task_id"]: t for t in actual.get("tasks", [])}
            for tid, et in expected_by.items():
                at = actual_by.get(tid)
                trace_den += 1
                if at and at.get("source_requirement_ids") == et["source_requirement_ids"] and at.get("verification_refs") == et["verification_refs"] and at.get("gate_ids") == et["gate_ids"] and at.get("provenance", {}).get("source_requirement_ids") == et["provenance"]["source_requirement_ids"]:
                    trace_num += 1
                parallel_den += 1
                if at and at.get("parallel_with") == et["parallel_with"]:
                    parallel_num += 1
                for prereq in et["prerequisite_task_ids"]:
                    dep_prov_den += 1
                    if at and prereq in at.get("prerequisite_task_ids", []) and at.get("provenance", {}).get("prerequisite_task_ids") == et["provenance"]["prerequisite_task_ids"]:
                        dep_prov_num += 1
                if at:
                    extra = set(at.get("prerequisite_task_ids", [])) - set(et["prerequisite_task_ids"])
                    invented_dep += len(extra)
            # Unsafe parallel if any shared-write conflict pair appears in parallel list.
            for zone in actual.get("conflict_zones", []):
                tids = zone["task_ids"]
                for a in tids:
                    for b in tids:
                        if a < b and b in actual_by.get(a, {}).get("parallel_with", []):
                            unsafe_parallel += 1
        else:
            neg_total += 1
            actual_codes = sorted({d["code"] for d in actual.get("diagnostics", [])})
            expected_codes = sorted(expected.get("diagnostic_codes", []))
            exact = actual["status"] == expected["status"] and all(c in actual_codes for c in expected_codes)
            if "blocking_action_ids" in expected:
                actual_blocking = sorted({x for d in actual.get("diagnostics", []) for x in d.get("blocking_action_ids", [])})
                exact = exact and actual_blocking == expected["blocking_action_ids"]
            if "cycle_source_task_ids" in expected:
                actual_cycle = sorted({x for d in actual.get("diagnostics", []) if d["code"] == "TC-DEPENDENCY-CYCLE" for x in d.get("source_task_ids", [])})
                exact = exact and actual_cycle == expected["cycle_source_task_ids"]
            neg_exact += int(exact)
            result["exact"] = exact
            if case["category"] == "owner_blocker" and actual["status"] == "compiled": unresolved_escape += 1
            if case["category"] == "atomicity_refinement" and actual["status"] == "compiled": oversized_escape += 1
            if case["category"] == "dependency_cycle" and actual["status"] == "compiled": cycle_escape += 1
        rows.append(result)

    execution_exact = 0
    invalid_exec_escape = 0
    exec_rows = []
    for case in execution:
        result = replay_task_events(graph_hash=case["graph_hash"], task_ids=case["task_ids"], events=case["events"], root=root)
        codes = sorted({d["code"] for d in result["diagnostics"]})
        if case["valid"]:
            exact = result["ok"] and result["final_states"] == case["expected_final_states"] and not codes
        else:
            exact = (not result["ok"]) and all(c in codes for c in case["expected_codes"])
            if result["ok"]:
                invalid_exec_escape += 1
        execution_exact += int(exact)
        exec_rows.append({"case_id": case["case_id"], "valid": case["valid"], "exact": exact, "codes": codes})

    preflight = json.loads((root / "evaluation/v008-preregistration-preflight.json").read_text(encoding="utf-8"))
    metrics = {
        "accepted_task_graph_exact_match_rate": accepted_exact / accepted_total if accepted_total else None,
        "heldout_task_graph_exact_match_rate": held_acc_exact / held_acc_total if held_acc_total else None,
        "negative_case_classification_accuracy": neg_exact / neg_total if neg_total else None,
        "dependency_provenance_accuracy": dep_prov_num / dep_prov_den if dep_prov_den else 1.0,
        "critical_ready_task_trace_completeness_rate": trace_num / trace_den if trace_den else None,
        "parallelization_decision_accuracy": parallel_num / parallel_den if parallel_den else None,
        "unresolved_decision_escape_count": unresolved_escape,
        "unsafe_parallelization_count": unsafe_parallel,
        "oversized_ready_task_count": oversized_escape,
        "dependency_cycle_escape_count": cycle_escape,
        "invented_dependency_count": invented_dep,
        "execution_stream_exact_match_rate": execution_exact / len(execution) if execution else None,
        "invalid_execution_escape_count": invalid_exec_escape,
        "deterministic_repeat_rate": repeat_num / repeat_den if repeat_den else None,
        "parent_preflight_rate": preflight["summary"]["compiler_preflight_rate"],
        "v008_spec_quality_acceptance_rate": 1.0 if preflight["summary"]["v008_spec_lint_ok"] and preflight["summary"]["v008_spec_ambiguity_findings"] == 0 and preflight["summary"]["v008_spec_discovery_question_batches"] == 0 else 0.0,
    }
    return {
        "candidate_version": "0.08",
        "hash_checks": hash_checks,
        "counts": {
            "compiler_cases": len(corpus), "accepted_cases": accepted_total, "heldout_accepted_cases": held_acc_total, "negative_cases": neg_total,
            "execution_cases": len(execution), "dependency_edges_evaluated": dep_prov_den, "compiled_tasks_evaluated": trace_den,
        },
        "metrics": metrics,
        "compiler_results": rows,
        "execution_results": exec_rows,
        "missing_data": [] if all(v is not None for v in metrics.values()) else [k for k, v in metrics.items() if v is None],
    }
