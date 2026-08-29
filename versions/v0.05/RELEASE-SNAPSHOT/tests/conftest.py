from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

import pytest

from spec_creator.models import canonical_contract_hash


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def base_event(event_id: str = "EVT-T-001") -> dict:
    return {
        "event_id": event_id,
        "project_id": "fixture-project",
        "event_time_utc": "2026-08-24T14:20:00Z",
        "recorded_time_utc": "2026-08-24T14:20:00Z",
        "actor_type": "agent",
        "actor_id": "agent:fixture",
        "event_type": "fixture_event",
        "event_version": "1",
        "phase": "verification",
        "classification": "measurement",
        "severity": "none",
        "status": "resolved",
        "included_in_metrics": True,
        "evidence_refs": [],
        "notes": "fixture",
        "attributes": {},
    }


def active_reg(rid: str) -> dict:
    return {
        "regression_id": rid,
        "origin_incident": "fixture",
        "first_fixed_version": "0.02",
        "description": "fixture regression",
        "reproducer_ref": None,
        "expected_behavior": "must pass",
        "severity": "critical",
        "applicable_modes": ["Exhaustive"],
        "automated": True,
        "verification_procedure": "pytest",
        "status": "active",
        "superseding_decision_id": None,
    }


def valid_contract() -> dict:
    c = {
        "contract_id": "REL-T-001",
        "schema_version": "2.0",
        "parent_version": "0.02",
        "candidate_version": "0.03",
        "frozen_at_utc": "2026-08-24T14:20:00Z",
        "goals": [{"goal_id": "G-T-001", "description": "validate", "acceptance": "all tests pass"}],
        "requirements": [{"requirement_id": "REQ-T-001", "description": "validate", "critical": True}],
        "mandatory_gates": ["GATE-T-001"],
        "applicable_regressions": ["REG-0001", "REG-0002", "REG-0003"],
        "primary_metrics": [{"metric_id": "M-T-001", "name": "fixture_rate", "target_operator": "eq", "target_value": 1.0, "unit": "ratio"}],
        "guardrail_metrics": [{"metric_id": "M-T-G01", "name": "guardrail", "target_operator": "eq", "target_value": 0, "unit": "count"}],
        "failure_conditions": ["critical failure"],
        "promotion_conditions": ["all pass"],
        "rollback_expectations": {
            "rollback_target": "0.02",
            "preserve_parent_history": True,
            "parent_contract_sha256": "0" * 64,
            "expectation": "restore parent",
        },
        "evaluator_independence": {
            "implementation_actor_id": "agent:fixture",
            "required_evaluator_actor_id": "verifier:fixture",
            "must_differ": True,
        },
        "hash_algorithm": "sha256",
        "hash_scope": "canonical excluding contract_hash",
        "contract_hash": "",
    }
    c["contract_hash"] = canonical_contract_hash(c)
    return c


@pytest.fixture
def valid_workspace(tmp_path: Path) -> Path:
    root = tmp_path / "ws"
    shutil.copytree(PROJECT_ROOT / "schemas", root / "schemas")

    events = [base_event()]
    dump_jsonl(root / "evaluation/events.jsonl", events)
    dump_jsonl(root / "self-improvement/regressions.jsonl", [active_reg("REG-0001"), active_reg("REG-0002"), active_reg("REG-0003")])
    dump_jsonl(root / "self-improvement/decisions.jsonl", [])
    dump_jsonl(root / "self-improvement/improvement-ledger.jsonl", [])
    dump_jsonl(root / "self-improvement/experiment-registry.jsonl", [])

    snapshot = {
        "snapshot_id": "DEN-T-001",
        "metric_name": "fixture_rate",
        "cutoff_utc": "2026-08-24T14:20:00Z",
        "scope": "fixture",
        "denominator_value": 1,
        "denominator_unit": "fixtures",
        "source_event_ids": ["EVT-T-001"],
        "missing_data": {"status": "complete", "details": ""},
    }
    metric = {
        "metric_record_id": "MET-T-001",
        "metric_name": "fixture_rate",
        "snapshot_id": "DEN-T-001",
        "numerator_value": 1,
        "denominator_value": 1,
        "denominator_unit": "fixtures",
        "value": 1.0,
        "cutoff_utc": "2026-08-24T14:20:00Z",
        "scope": "fixture",
        "source_event_ids": ["EVT-T-001"],
        "missing_data": {"status": "complete", "details": ""},
    }
    dump_jsonl(root / "evaluation/denominator-snapshots.jsonl", [snapshot])
    dump_jsonl(root / "evaluation/metric-ledger.jsonl", [metric])
    dump_jsonl(root / "evaluation/release-scorecards.jsonl", [])

    contract = valid_contract()
    dump_json(root / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json", contract)
    return root


@pytest.fixture
def helpers():
    return {
        "dump_json": dump_json,
        "dump_jsonl": dump_jsonl,
        "base_event": base_event,
        "active_reg": active_reg,
        "valid_contract": valid_contract,
        "project_root": PROJECT_ROOT,
    }
