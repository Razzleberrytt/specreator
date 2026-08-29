from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spec_creator.linter import lint_file
from spec_creator.models import canonical_contract_hash
from spec_creator.trace_evaluator import evaluate_v005_corpus
from spec_creator.traceability import load_graph, validate_graph
from spec_creator.validator import validate_workspace

EXPECTED_CONTRACT = "c3d9588520221b8b8440d296bf3da5f2cbf7b43751b1725299b576f16efb3ca5"
EXPECTED_CORPUS = "f80475f84faad0afeb57da0d4db385274debe0760f87e2687fec0457d7ba3c21"
EXPECTED_PLAN = "3f97c63e65b6d3d9a3c217a8bed60b5129c2ade80a9f34c636852e645205a881"
ACTOR = "verifier:independent-pass-004"
IMPLEMENTATION_ACTOR = "agent:spec-creator-builder"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(args: list[str]) -> dict:
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", *args], cwd=ROOT, text=True, capture_output=True)
    return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}


contract = json.loads((ROOT / "versions/v0.05/FROZEN-RELEASE-CONTRACT.json").read_text())
corpus_eval = evaluate_v005_corpus(ROOT)
lint = lint_file(ROOT / "versions/v0.05/SPEC-CREATOR-v0.05.md")
self_trace = validate_graph(load_graph(ROOT / "versions/v0.05/TRACEABILITY-GRAPH.json"))
workspace = validate_workspace(ROOT, validate_package_manifest=False)
full_tests = run_pytest([])
regression_tests = run_pytest([
    "tests/test_validator.py::test_frozen_contract_mutation_detected",
    "tests/test_validator.py::test_candidate_self_certification_detected",
    "tests/test_validator.py::test_critical_regression_cannot_disappear",
    "tests/test_validator.py::test_shared_reference_ids_are_not_false_duplicates",
    "tests/test_validator.py::test_historical_append_only_manifest_prefix_survives_successor_append",
    "tests/test_validator.py::test_historical_append_only_manifest_detects_prefix_mutation",
    "tests/test_validator.py::test_historical_mutable_source_uses_release_snapshot",
    "tests/test_validator.py::test_historical_release_snapshot_mutation_detected",
    "tests/test_validator.py::test_append_jsonl_helper_preserves_existing_prefix",
    "tests/test_validator.py::test_append_jsonl_helper_rejects_duplicate_primary_id",
])
regs = [json.loads(x) for x in (ROOT / "self-improvement/regressions.jsonl").read_text().splitlines() if x.strip()]
reg_by_id = {r["regression_id"]: r for r in regs}
required_regs = [f"REG-{i:04d}" for i in range(1, 7)]

checks = {
    "actor_separation": ACTOR != IMPLEMENTATION_ACTOR,
    "contract_canonical_hash": canonical_contract_hash(contract) == EXPECTED_CONTRACT == contract.get("contract_hash"),
    "corpus_file_hash": sha(ROOT / "fixtures/traceability/v0.05/corpus.jsonl") == EXPECTED_CORPUS,
    "evaluation_plan_file_hash": sha(ROOT / "versions/v0.05/EVALUATION-PLAN.json") == EXPECTED_PLAN,
    "invalid_graph_detection_rate": corpus_eval["metrics"]["invalid_graph_detection_rate"] == 1.0,
    "valid_graph_acceptance_rate": corpus_eval["metrics"]["valid_graph_acceptance_rate"] == 1.0,
    "critical_traceability_coverage_rate": corpus_eval["metrics"]["critical_traceability_coverage_rate"] == 1.0,
    "impact_analysis_exact_match_rate": corpus_eval["metrics"]["impact_analysis_exact_match_rate"] == 1.0,
    "diagnostic_code_precision": corpus_eval["metrics"]["diagnostic_code_precision"] == 1.0,
    "valid_graph_false_positive_count": corpus_eval["metrics"]["valid_graph_false_positive_count"] == 0,
    "v005_spec_lint_clean": lint.ok and len(lint.unsuppressed) == 0,
    "self_traceability_graph_clean": self_trace.ok and self_trace.critical_requirements_total == 10 and self_trace.critical_requirements_complete == 10,
    "workspace_validation_clean": workspace.ok and not workspace.warnings,
    "full_test_suite_pass": full_tests["returncode"] == 0,
    "applicable_regression_tests_pass": regression_tests["returncode"] == 0,
    "applicable_regression_registry_intact": all(rid in reg_by_id and reg_by_id[rid].get("status") == "active" for rid in required_regs),
}

result = {
    "actor_id": ACTOR,
    "implementation_actor_id": IMPLEMENTATION_ACTOR,
    "candidate_version": "0.05",
    "checks": checks,
    "all_checks_pass": all(checks.values()),
    "corpus_counts": corpus_eval["counts"],
    "corpus_metrics": corpus_eval["metrics"],
    "lint_summary": lint.as_dict()["summary"],
    "self_trace_summary": self_trace.as_dict()["summary"],
    "workspace_summary": workspace.as_dict()["summary"],
    "full_tests": full_tests,
    "applicable_regression_tests": regression_tests,
    "recommendation": "PROMOTED AS EXPERIMENTAL" if all(checks.values()) else "RETRY REQUIRED",
    "limitations": [
        "Verifier role is process-separated from the implementation actor but runs in the same local session/runtime.",
        "Frozen traceability benchmark is synthetic and visible to the implementer; no independent real-project outcome evidence is claimed."
    ]
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["all_checks_pass"] else 1)
