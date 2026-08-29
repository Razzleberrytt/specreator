from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from spec_creator.validator import validate_workspace, validate_contract_hash
from spec_creator.models import canonical_contract_hash


def codes(report):
    return {i.code for i in report.errors}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def test_valid_workspace_passes(valid_workspace):
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert report.ok, report.as_dict()


def test_frozen_contract_hash_is_valid(valid_workspace):
    c = read_json(valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json")
    assert validate_contract_hash(c)


def test_frozen_contract_mutation_detected(valid_workspace, helpers):
    p = valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json"
    c = read_json(p)
    c["goals"][0]["acceptance"] = "changed after freeze"
    helpers["dump_json"](p, c)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "FROZEN_CONTRACT_HASH_MISMATCH" in codes(report)


def test_malformed_json_detected(valid_workspace, helpers):
    p = valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json"
    p.write_text((helpers["project_root"] / "fixtures/invalid/malformed.json").read_text(), encoding="utf-8")
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MALFORMED_JSON" in codes(report)


def test_malformed_jsonl_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    p.write_text((helpers["project_root"] / "fixtures/invalid/malformed.jsonl").read_text(), encoding="utf-8")
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MALFORMED_JSONL" in codes(report)


def test_missing_mandatory_field_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]()
    del event["actor_id"]
    helpers["dump_jsonl"](p, [event])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "SCHEMA_VALIDATION_ERROR" in codes(report)


def test_invalid_controlled_value_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]()
    event["phase"] = "magical"
    helpers["dump_jsonl"](p, [event])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "SCHEMA_VALIDATION_ERROR" in codes(report)


def test_invalid_stable_id_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]("bad-id")
    helpers["dump_jsonl"](p, [event])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "INVALID_STABLE_ID" in codes(report)


def test_duplicate_ids_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]()
    helpers["dump_jsonl"](p, [event, copy.deepcopy(event)])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "DUPLICATE_ID" in codes(report)


def test_broken_event_reference_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]()
    event["parent_event_id"] = "EVT-NOT-THERE"
    helpers["dump_jsonl"](p, [event])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "BROKEN_EVENT_REFERENCE" in codes(report)


def test_invalid_supersession_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    event = helpers["base_event"]()
    event["status"] = "superseded"
    helpers["dump_jsonl"](p, [event])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "INVALID_SUPERSESSION" in codes(report)


def test_valid_supersession_passes(valid_workspace, helpers):
    p = valid_workspace / "evaluation/events.jsonl"
    old = helpers["base_event"]("EVT-T-OLD")
    new = helpers["base_event"]("EVT-T-NEW")
    old["status"] = "superseded"
    old["attributes"] = {"superseded_by_event_id": "EVT-T-NEW"}
    helpers["dump_jsonl"](p, [old, new])
    # update metric/snapshot sources to existing event
    for rel in ["evaluation/denominator-snapshots.jsonl", "evaluation/metric-ledger.jsonl"]:
        rows = read_jsonl(valid_workspace / rel)
        rows[0]["source_event_ids"] = ["EVT-T-NEW"]
        helpers["dump_jsonl"](valid_workspace / rel, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "INVALID_SUPERSESSION" not in codes(report)
    assert "BROKEN_SOURCE_EVENT_REFERENCE" not in codes(report)


def test_missing_denominator_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/denominator-snapshots.jsonl"
    rows = read_jsonl(p)
    rows[0]["denominator_value"] = None
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MISSING_DENOMINATOR" in codes(report)


def test_missing_snapshot_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["snapshot_id"] = "DEN-MISSING"
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MISSING_DENOMINATOR_SNAPSHOT" in codes(report)


def test_metric_cutoff_mismatch_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["cutoff_utc"] = "2026-08-24T15:20:00Z"
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "METRIC_CUTOFF_MISMATCH" in codes(report)


def test_metric_scope_mismatch_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["scope"] = "different"
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "METRIC_SCOPE_MISMATCH" in codes(report)


def test_metric_denominator_mismatch_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["denominator_value"] = 2
    rows[0]["value"] = 0.5
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "METRIC_DENOMINATOR_MISMATCH" in codes(report)


def test_metric_calculation_mismatch_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["value"] = 0.25
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "METRIC_CALCULATION_MISMATCH" in codes(report)


def test_source_event_reference_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    rows[0]["source_event_ids"] = ["EVT-MISSING"]
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "BROKEN_SOURCE_EVENT_REFERENCE" in codes(report)


def test_regression_retirement_requires_governance(valid_workspace, helpers):
    p = valid_workspace / "self-improvement/regressions.jsonl"
    rows = read_jsonl(p)
    rows[0]["status"] = "retired"
    rows[0]["superseding_decision_id"] = None
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "UNGOVERNED_REGRESSION_RETIREMENT" in codes(report)


def test_candidate_self_certification_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/release-scorecards.jsonl"
    card = {
        "evaluation_id": "EVAL-T-001",
        "contract_id": "REL-T-001",
        "candidate_version": "0.03",
        "evaluated_at_utc": "2026-08-24T14:20:00Z",
        "implementation_actor_ids": ["agent:fixture"],
        "evaluator_actor_id": "agent:fixture",
        "gate_outcomes": [{"id": "GATE-T-001", "status": "PASS", "evidence_refs": []}],
        "regression_outcomes": [
            {"id": "REG-0001", "status": "PASS", "evidence_refs": []},
            {"id": "REG-0002", "status": "PASS", "evidence_refs": []},
            {"id": "REG-0003", "status": "PASS", "evidence_refs": []},
        ],
        "primary_metric_outcomes": [{"metric_name": "fixture_rate", "status": "PASS", "metric_record_id": "MET-T-001"}],
        "guardrail_metric_outcomes": [{"metric_name": "guardrail", "status": "PASS", "metric_record_id": "MET-T-001"}],
        "open_critical_defects": [],
        "recommendation": "PROMOTED AS EXPERIMENTAL",
        "rationale": "fixture",
    }
    helpers["dump_jsonl"](p, [card])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "CANDIDATE_SELF_CERTIFICATION" in codes(report)


def test_missing_gate_outcome_detected(valid_workspace, helpers):
    p = valid_workspace / "evaluation/release-scorecards.jsonl"
    card = {
        "evaluation_id": "EVAL-T-001",
        "contract_id": "REL-T-001",
        "candidate_version": "0.03",
        "evaluated_at_utc": "2026-08-24T14:20:00Z",
        "implementation_actor_ids": ["agent:fixture"],
        "evaluator_actor_id": "verifier:fixture",
        "gate_outcomes": [],
        "regression_outcomes": [
            {"id": "REG-0001", "status": "PASS", "evidence_refs": []},
            {"id": "REG-0002", "status": "PASS", "evidence_refs": []},
            {"id": "REG-0003", "status": "PASS", "evidence_refs": []},
        ],
        "primary_metric_outcomes": [],
        "guardrail_metric_outcomes": [],
        "open_critical_defects": [],
        "recommendation": "BLOCKED",
        "rationale": "fixture",
    }
    helpers["dump_jsonl"](p, [card])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MISSING_GATE_OUTCOME" in codes(report)


def test_manifest_hash_mismatch_detected(valid_workspace, helpers):
    artifact = valid_workspace / "artifact.txt"
    artifact.write_text("actual", encoding="utf-8")
    contract = read_json(valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json")
    manifest = {
        "manifest_schema_version": "2.0",
        "version": "0.03",
        "parent_version": "0.02",
        "status": "experimental",
        "protocol_schema_version": "2.0",
        "added_capabilities": ["validator"],
        "removed_or_deprecated_capabilities": [],
        "breaking_changes": [],
        "required_migrations": [],
        "new_regressions": [],
        "retired_regressions": [],
        "preregistered_goals": ["G-T-001"],
        "evaluation_result": "fixture",
        "promotion_decision": "BLOCKED",
        "release_contract_hash": contract["contract_hash"],
        "content_hashes": {"artifact.txt": "0" * 64},
        "rollback_ref": "versions/v0.03/ROLLBACK.json",
    }
    helpers["dump_json"](valid_workspace / "versions/v0.03/MANIFEST.json", manifest)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_HASH_MISMATCH" in codes(report)


def test_manifest_contract_hash_mismatch_detected(valid_workspace, helpers):
    contract = read_json(valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json")
    manifest = {
        "manifest_schema_version": "2.0",
        "version": "0.03",
        "parent_version": "0.02",
        "status": "experimental",
        "protocol_schema_version": "2.0",
        "added_capabilities": ["validator"],
        "removed_or_deprecated_capabilities": [],
        "breaking_changes": [],
        "required_migrations": [],
        "new_regressions": [],
        "retired_regressions": [],
        "preregistered_goals": ["G-T-001"],
        "evaluation_result": "fixture",
        "promotion_decision": "BLOCKED",
        "release_contract_hash": "1" * 64,
        "content_hashes": {},
        "rollback_ref": "versions/v0.03/ROLLBACK.json",
    }
    helpers["dump_json"](valid_workspace / "versions/v0.03/MANIFEST.json", manifest)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_CONTRACT_HASH_MISMATCH" in codes(report)


def test_all_schema_documents_are_valid(valid_workspace):
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "INVALID_SCHEMA_DOCUMENT" not in codes(report)


def test_shared_reference_ids_are_not_false_duplicates(valid_workspace, helpers):
    """REG-0004: repeated references are not duplicate primary record IDs."""
    p = valid_workspace / "evaluation/metric-ledger.jsonl"
    rows = read_jsonl(p)
    second = copy.deepcopy(rows[0])
    second["metric_record_id"] = "MET-T-002"
    helpers["dump_jsonl"](p, [rows[0], second])
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "DUPLICATE_ID" not in codes(report)
    assert report.ok, report.as_dict()


def test_critical_regression_cannot_disappear(valid_workspace, helpers):
    """REG-0003: a frozen critical regression reference must resolve."""
    p = valid_workspace / "self-improvement/regressions.jsonl"
    rows = [r for r in read_jsonl(p) if r["regression_id"] != "REG-0003"]
    helpers["dump_jsonl"](p, rows)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MISSING_CRITICAL_REGRESSION" in codes(report)


def _write_historical_snapshot(ws, relpath, data, helpers):
    import hashlib
    snap = {
        "files": [{"path": relpath, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}]
    }
    helpers["dump_json"](ws / "versions/v0.03/PACKAGE-MANIFEST-SNAPSHOT.json", snap)
    return snap["files"][0]["sha256"]


def _write_manifest_for_artifact(ws, relpath, sha, helpers):
    contract = read_json(ws / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json")
    manifest = {
        "manifest_schema_version": "2.0",
        "version": "0.03",
        "parent_version": "0.02",
        "status": "experimental",
        "protocol_schema_version": "2.0",
        "added_capabilities": ["validator"],
        "removed_or_deprecated_capabilities": [],
        "breaking_changes": [],
        "required_migrations": [],
        "new_regressions": [],
        "retired_regressions": [],
        "preregistered_goals": ["G-T-001"],
        "evaluation_result": "fixture",
        "promotion_decision": "BLOCKED",
        "release_contract_hash": contract["contract_hash"],
        "content_hashes": {relpath: sha},
        "rollback_ref": "versions/v0.03/ROLLBACK.json",
    }
    helpers["dump_json"](ws / "versions/v0.03/MANIFEST.json", manifest)


def test_historical_append_only_manifest_prefix_survives_successor_append(valid_workspace, helpers):
    """REG-0005: legitimate append must not invalidate a historical release prefix."""
    rel = "evaluation/events.jsonl"
    p = valid_workspace / rel
    frozen = p.read_bytes()
    sha = _write_historical_snapshot(valid_workspace, rel, frozen, helpers)
    _write_manifest_for_artifact(valid_workspace, rel, sha, helpers)
    with p.open("ab") as f:
        f.write((json.dumps(helpers["base_event"]("EVT-T-APPENDED")) + "\n").encode())
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_HASH_MISMATCH" not in codes(report)
    assert "MANIFEST_HISTORICAL_PREFIX_MISMATCH" not in codes(report)


def test_historical_append_only_manifest_detects_prefix_mutation(valid_workspace, helpers):
    rel = "evaluation/events.jsonl"
    p = valid_workspace / rel
    frozen = p.read_bytes()
    sha = _write_historical_snapshot(valid_workspace, rel, frozen, helpers)
    _write_manifest_for_artifact(valid_workspace, rel, sha, helpers)
    mutated = bytearray(frozen)
    mutated[0] = ord("X")
    p.write_bytes(bytes(mutated) + b'\n')
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_HISTORICAL_PREFIX_MISMATCH" in codes(report)


def test_historical_manifest_keeps_immutable_files_exact(valid_workspace, helpers):
    rel = "artifact.txt"
    p = valid_workspace / rel
    p.write_text("frozen", encoding="utf-8")
    import hashlib
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    _write_historical_snapshot(valid_workspace, rel, p.read_bytes(), helpers)
    _write_manifest_for_artifact(valid_workspace, rel, sha, helpers)
    p.write_text("changed", encoding="utf-8")
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_HASH_MISMATCH" in codes(report)


def test_historical_mutable_source_uses_release_snapshot(valid_workspace, helpers):
    rel = "src/shared.py"
    current = valid_workspace / rel
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text("version two", encoding="utf-8")
    frozen = b"version one"
    import hashlib
    sha = hashlib.sha256(frozen).hexdigest()
    snap = valid_workspace / "versions/v0.03/RELEASE-SNAPSHOT" / rel
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_bytes(frozen)
    _write_manifest_for_artifact(valid_workspace, rel, sha, helpers)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_HASH_MISMATCH" not in codes(report)
    assert "MANIFEST_RELEASE_SNAPSHOT_MISMATCH" not in codes(report)


def test_historical_release_snapshot_mutation_detected(valid_workspace, helpers):
    rel = "src/shared.py"
    current = valid_workspace / rel
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text("version two", encoding="utf-8")
    frozen = b"version one"
    import hashlib
    sha = hashlib.sha256(frozen).hexdigest()
    snap = valid_workspace / "versions/v0.03/RELEASE-SNAPSHOT" / rel
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_bytes(b"tampered")
    _write_manifest_for_artifact(valid_workspace, rel, sha, helpers)
    report = validate_workspace(valid_workspace, validate_package_manifest=False)
    assert "MANIFEST_RELEASE_SNAPSHOT_MISMATCH" in codes(report)


def test_append_jsonl_helper_preserves_existing_prefix(tmp_path):
    """REG-0006: append-only writes must not rewrite historical bytes."""
    from spec_creator.ledger import append_jsonl_records
    p = tmp_path / "events.jsonl"
    frozen = b'{"event_id":"EVT-OLD","z":1,"a":2}\n'
    p.write_bytes(frozen)
    append_jsonl_records(p, [{"event_id": "EVT-NEW", "a": 3}], primary_id_field="event_id")
    assert p.read_bytes()[:len(frozen)] == frozen


def test_append_jsonl_helper_rejects_duplicate_primary_id(tmp_path):
    from spec_creator.ledger import append_jsonl_records
    p = tmp_path / "events.jsonl"
    append_jsonl_records(p, [{"event_id": "EVT-ONE"}], primary_id_field="event_id")
    import pytest
    with pytest.raises(ValueError, match="duplicate event_id"):
        append_jsonl_records(p, [{"event_id": "EVT-ONE"}], primary_id_field="event_id")


def test_v005_release_snapshot_readme_matches_manifest_declared_bytes():
    root = Path(__file__).resolve().parents[1]
    manifest = read_json(root / "versions/v0.05/MANIFEST.json")
    snapshot = root / "versions/v0.05/RELEASE-SNAPSHOT/README.md"
    raw = snapshot.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest["content_hashes"]["README.md"]
    entry = next(x for x in read_json(root / "versions/v0.05/PACKAGE-MANIFEST-SNAPSHOT.json")["files"] if x["path"] == "README.md")
    assert len(raw) == entry["bytes"]
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
