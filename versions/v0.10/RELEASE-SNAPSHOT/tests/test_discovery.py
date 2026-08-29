from __future__ import annotations

import json
from pathlib import Path
import pytest

from spec_creator.discovery import DiscoveryProfile, plan_discovery

ROOT = Path(__file__).resolve().parents[1]


def _cases(name="development.jsonl"):
    return [json.loads(x) for x in (ROOT / "fixtures/discovery/v0.07" / name).read_text().splitlines() if x.strip()]


def _action_map(payload):
    return {(a["block_id"], a["code"]): a for a in payload["actions"]}


def _expected_exact(case, payload):
    actual = _action_map(payload)
    expected = case["expected"]["actions"]
    assert len(payload["actions"]) == len(expected)
    for e in expected:
        a = actual[(e["block_id"], e["code"])]
        assert a["action"] == e["action"]
        if "value" in e:
            assert a.get("value") == e["value"]
    assert sorted(q["group_id"] for q in payload["questions"]) == sorted(case["expected"]["selected_batch_groups"])
    assert payload["summary"]["question_batches"] == case["expected"]["question_batch_count"]


def test_frozen_action_plans():
    for case in _cases():
        payload = plan_discovery(case["document"], profile=case["profile"], trace_graph=case.get("trace_graph")).as_dict()
        _expected_exact(case, payload)


def test_information_value_priority():
    for case in [c for c in _cases() if c["category"] in {"dependency", "batch_budget"}]:
        payload = plan_discovery(case["document"], profile=case["profile"], trace_graph=case.get("trace_graph")).as_dict()
        assert sorted(q["group_id"] for q in payload["questions"]) == sorted(case["expected"]["selected_batch_groups"])


def test_dependency_frontier():
    for case in [c for c in _cases() if c["category"] == "dependency"]:
        _expected_exact(case, plan_discovery(case["document"], profile=case["profile"]).as_dict())


def test_explicit_batching_and_budget():
    for case in [c for c in _cases() if c["category"] == "batch_budget"]:
        payload = plan_discovery(case["document"], profile=case["profile"]).as_dict()
        _expected_exact(case, payload)
        assert len(payload["questions"][0]["member_candidate_ids"]) == 2


def test_safe_inference():
    for case in [c for c in _cases() if c["category"] == "safe_default"]:
        payload = plan_discovery(case["document"], profile=case["profile"]).as_dict()
        action = payload["actions"][0]
        assert action["action"] == "infer_default"
        assert action["value"] == case["expected"]["actions"][0]["value"]
        assert action["provenance"]["ref"]


def test_unsafe_inference_guardrails():
    for case in [c for c in _cases() if c["category"] == "unsafe_default"]:
        payload = plan_discovery(case["document"], profile=case["profile"], trace_graph=case.get("trace_graph")).as_dict()
        assert all(a["action"] != "infer_default" for a in payload["actions"])
        assert payload["summary"]["question_batches"] == 1
        if case["variant"] != "critical":
            assert payload["actions"][0].get("inference_rejection_reasons")


def test_project_profiles_do_not_invent_choices():
    doc = """### REQ-PROFILE-001
Requirement: Select the persistence choice.
Critical: false
Options: storage = SQLite | PostgreSQL
Acceptance: A choice is explicit.
Verify: unit
"""
    for project_type in ("prototype", "production", "regulated", "custom"):
        payload = plan_discovery(doc, profile={"profile_id": f"P-{project_type}", "project_type": project_type, "defaults": []}).as_dict()
        assert payload["actions"][0]["action"] == "ask_now"


def test_provenance_complete():
    for case in _cases():
        payload = plan_discovery(case["document"], profile=case["profile"], trace_graph=case.get("trace_graph")).as_dict()
        for action in payload["actions"]:
            assert action["reason"]
            assert action["provenance"]["source"]
            assert action["provenance"]["ref"]


def test_critical_ready_question_bypasses_budget():
    doc = """### REQ-CRIT-1
Requirement: Select critical persistence.
Critical: true
Options: persistence = A | B
Acceptance: selected
Verify: unit

### REQ-NONCRIT-1
Requirement: Select noncritical theme.
Critical: false
Options: theme = light | dark
Acceptance: selected
Verify: unit
"""
    payload = plan_discovery(doc, profile={"profile_id": "P", "project_type": "custom", "question_budget": 1, "defaults": []}).as_dict()
    assert payload["questions"][0]["member_block_ids"] == ["REQ-CRIT-1"]
    amap = _action_map(payload)
    assert amap[("REQ-CRIT-1", "AMB-001")]["action"] == "ask_now"
    assert amap[("REQ-NONCRIT-1", "AMB-001")]["action"] == "defer_budget"


def test_malformed_profile_rejected():
    with pytest.raises(ValueError, match="question_budget"):
        DiscoveryProfile.from_dict({"profile_id": "P", "project_type": "custom", "question_budget": 0, "defaults": []})
    with pytest.raises(ValueError, match="project_type"):
        DiscoveryProfile.from_dict({"profile_id": "P", "project_type": "mystery", "defaults": []})


def test_duplicate_profile_default_target_rejected():
    d = {"block_id": "REQ-X", "ambiguity_code": "AMB-001", "span": "x", "value": "a", "risk": "low", "reversible": True, "auto_apply": True, "provenance": "owner_intake", "source_ref": "I"}
    with pytest.raises(ValueError, match="duplicate profile default"):
        DiscoveryProfile.from_dict({"profile_id": "P", "project_type": "custom", "defaults": [d, dict(d, value="b")]})
