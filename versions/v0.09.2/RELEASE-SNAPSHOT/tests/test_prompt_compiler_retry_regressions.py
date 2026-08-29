from __future__ import annotations

from pathlib import Path
import json

import pytest

from spec_creator.release_freeze import (
    FreezePreconditionError,
    FrozenContractValidationError,
    finalize_frozen_contract,
    freeze_contract_fail_closed,
)
from spec_creator.task_compiler import validate_compiled_graph


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "fixtures" / "prompt-compiler" / "v0.09.2" / "corpus.jsonl"
SCHEMA = ROOT / "schemas" / "frozen-release-contract-v2.schema.json"


def _rows():
    return [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]


def _observable_negative(case: dict) -> bool:
    inp = case["input"]
    defect = case["defect_class"]
    graph = inp.get("compiled_task_graph") or {}
    task_id = inp.get("task_id")
    task = next((t for t in graph.get("tasks", []) if t.get("task_id") == task_id), {})
    events = inp.get("execution_events") or []
    state = None
    for event in events:
        if event.get("task_id") == task_id:
            state = event.get("to_state")

    if defect == "scope_expansion":
        return bool(set(inp.get("requested_write_scopes") or []) - set(task.get("write_scopes") or []))
    if defect == "prerequisite_incomplete":
        prereqs = set(task.get("prerequisite_task_ids") or [])
        done = {e.get("task_id") for e in events if e.get("to_state") == "done"}
        return bool(prereqs - done)
    if defect == "owner_decision":
        return bool((inp.get("task_contract") or {}).get("blocking_owner_decision_ids"))
    if defect == "same_actor_verification":
        actor = inp.get("actor_context") or {}
        return inp.get("prompt_kind") == "verification" and actor.get("requested_actor_id") == actor.get("implementation_actor_id")
    if defect == "verification_not_done":
        return inp.get("prompt_kind") == "verification" and state != "done"
    if defect == "debug_missing_evidence":
        return inp.get("prompt_kind") == "debug" and not inp.get("debug_evidence_refs")
    if defect == "task_contract_mismatch":
        return (inp.get("task_contract") or {}).get("task_id") != task_id
    if defect == "duplicate_context":
        records = inp.get("context_records") or []
        ids = [r.get("context_id") for r in records]
        refs = [r.get("ref") for r in records]
        return len(ids) != len(set(ids)) or len(refs) != len(set(refs))
    if defect == "critical_unbound_context":
        for rec in inp.get("context_records") or []:
            selectors = rec.get("selectors") or {}
            if rec.get("critical") is True and not any(selectors.get(k) for k in ("task_ids", "requirement_ids", "verification_refs", "gate_ids", "prompt_kinds")):
                return True
        return False
    if defect == "invalid_graph_hash":
        return bool(validate_compiled_graph(graph))
    return False


def _valid_contract_template() -> dict:
    return {
        "contract_id": "REL-TEST-FROZEN-001",
        "schema_version": "2.0",
        "parent_version": "0.08",
        "candidate_version": "0.09.2",
        "frozen_at_utc": "2026-08-24T17:45:00Z",
        "goals": [{"goal_id": "G-TEST-001", "description": "test", "acceptance": "pass"}],
        "requirements": [{"requirement_id": "REQ-TEST-001", "description": "test", "critical": True}],
        "mandatory_gates": ["GATE-TEST-001"],
        "applicable_regressions": ["REG-0020", "REG-0021", "REG-0022"],
        "primary_metrics": [{"metric_id": "M-TEST-001", "name": "primary", "target_operator": "eq", "target_value": 1, "unit": "count"}],
        "guardrail_metrics": [{"metric_id": "M-TEST-G01", "name": "guard", "target_operator": "eq", "target_value": 0, "unit": "count"}],
        "failure_conditions": ["any failure"],
        "promotion_conditions": ["all pass"],
        "rollback_expectations": {
            "rollback_target": "0.08",
            "preserve_parent_history": True,
            "parent_contract_sha256": "0" * 64,
            "expectation": "preserve parent",
        },
        "evaluator_independence": {
            "implementation_actor_id": "agent:builder",
            "required_evaluator_actor_id": "verifier:independent",
            "must_differ": True,
        },
        "hash_algorithm": "sha256",
        "hash_scope": "canonical JSON excluding contract_hash",
        "contract_hash": "",
    }


def test_reg0020_negative_cases_have_semantic_contrast():
    negative = [case for case in _rows() if case.get("class") == "negative"]
    assert len(negative) == 30
    failures = [case["case_id"] for case in negative if not _observable_negative(case)]
    assert failures == []


def test_reg0021_freeze_preconditions_are_fail_closed(tmp_path):
    destination = tmp_path / "FROZEN-RELEASE-CONTRACT.json"
    preconditions = {"parent": True, "schema": True, "contrast": False, "spec": True, "tests": True}
    with pytest.raises(FreezePreconditionError):
        freeze_contract_fail_closed(_valid_contract_template(), destination=destination, schema_path=SCHEMA, preconditions=preconditions)
    assert not destination.exists()


def test_reg0022_contract_schema_checked_before_write(tmp_path):
    destination = tmp_path / "FROZEN-RELEASE-CONTRACT.json"
    invalid = _valid_contract_template()
    invalid["requirements"][0] = {"requirement_id": "REQ-TEST-001", "text": "wrong field", "critical": True}
    with pytest.raises(FrozenContractValidationError):
        freeze_contract_fail_closed(invalid, destination=destination, schema_path=SCHEMA, preconditions={"all": True})
    assert not destination.exists()

    valid = finalize_frozen_contract(_valid_contract_template(), schema_path=SCHEMA)
    assert valid["contract_hash"]
