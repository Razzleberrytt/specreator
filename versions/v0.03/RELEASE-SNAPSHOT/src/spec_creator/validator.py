from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import hashlib
import json
import math
import re

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from .models import ValidationReport, canonical_contract_hash
from .schema_registry import JSONL_SCHEMAS, schema_for_json


ID_PATTERNS = {
    "event_id": re.compile(r"^EVT-[A-Za-z0-9._-]+$"),
    "improvement_id": re.compile(r"^IMP-[A-Za-z0-9._-]+$"),
    "regression_id": re.compile(r"^REG-[A-Za-z0-9._-]+$"),
    "experiment_id": re.compile(r"^EXP-[A-Za-z0-9._-]+$"),
    "decision_id": re.compile(r"^DEC-[A-Za-z0-9._-]+$"),
    "contract_id": re.compile(r"^REL-[A-Za-z0-9._-]+$"),
    "metric_record_id": re.compile(r"^MET-[A-Za-z0-9._-]+$"),
    "snapshot_id": re.compile(r"^DEN-[A-Za-z0-9._-]+$"),
    "evaluation_id": re.compile(r"^EVAL-[A-Za-z0-9._-]+$"),
    "requirement_id": re.compile(r"^REQ-[A-Za-z0-9._-]+$"),
    "task_id": re.compile(r"^TASK-[A-Za-z0-9._-]+$"),
    "gate_id": re.compile(r"^GATE-[A-Za-z0-9._-]+$"),
}


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _load_schema(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / "schemas" / name).read_text(encoding="utf-8"))


def _validate_schema(root: Path, schema_name: str, obj: Any, artifact: str, report: ValidationReport, line: int | None = None) -> None:
    try:
        schema = _load_schema(root, schema_name)
    except Exception as exc:
        report.add("SCHEMA_LOAD_ERROR", artifact, f"Cannot load schema {schema_name}: {exc}", line=line)
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path)
        suffix = f" at {loc}" if loc else ""
        report.add("SCHEMA_VALIDATION_ERROR", artifact, f"{schema_name}{suffix}: {err.message}", line=line)


def _read_json(path: Path, root: Path, report: ValidationReport) -> Any | None:
    artifact = _rel(root, path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        report.add("MALFORMED_JSON", artifact, str(exc))
        return None


def _read_jsonl(path: Path, root: Path, report: ValidationReport) -> list[tuple[int, dict[str, Any]]]:
    artifact = _rel(root, path)
    rows: list[tuple[int, dict[str, Any]]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        report.add("READ_ERROR", artifact, str(exc))
        return rows
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            report.add("MALFORMED_JSONL", artifact, str(exc), line=line_no)
            continue
        if not isinstance(obj, dict):
            report.add("JSONL_RECORD_NOT_OBJECT", artifact, "JSONL records must be JSON objects.", line=line_no)
            continue
        rows.append((line_no, obj))
    return rows


def _validate_all_schema_documents(root: Path, report: ValidationReport) -> None:
    for path in sorted((root / "schemas").glob("*.schema.json")):
        artifact = _rel(root, path)
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            report.add("INVALID_SCHEMA_DOCUMENT", artifact, str(exc))


def validate_contract_hash(contract: dict[str, Any]) -> bool:
    declared = contract.get("contract_hash")
    return isinstance(declared, str) and declared == canonical_contract_hash(contract)


PRIMARY_ID_FIELD = {
    "evaluation/events.jsonl": "event_id",
    "evaluation/metric-ledger.jsonl": "metric_record_id",
    "evaluation/denominator-snapshots.jsonl": "snapshot_id",
    "evaluation/release-scorecards.jsonl": "evaluation_id",
    "self-improvement/improvement-ledger.jsonl": "improvement_id",
    "self-improvement/experiment-registry.jsonl": "experiment_id",
    "self-improvement/regressions.jsonl": "regression_id",
    "self-improvement/decisions.jsonl": "decision_id",
    "requirements/requirements.jsonl": "requirement_id",
    "tasks/tasks.jsonl": "task_id",
    "evaluation/gates.jsonl": "gate_id",
}


def _stable_id_check(records: dict[str, list[tuple[int, dict[str, Any]]]], report: ValidationReport) -> None:
    # Validate ID-shaped fields wherever they occur, but only de-duplicate the
    # artifact's primary record ID. Reference IDs (e.g. metric.snapshot_id)
    # may and should repeat.
    seen_primary: dict[tuple[str, str], tuple[str, int]] = {}
    for artifact, rows in records.items():
        primary_field = PRIMARY_ID_FIELD.get(artifact)
        for line_no, obj in rows:
            for field, pattern in ID_PATTERNS.items():
                if field not in obj:
                    continue
                value = obj[field]
                if value is None:
                    continue
                if not isinstance(value, str) or not pattern.fullmatch(value):
                    report.add("INVALID_STABLE_ID", artifact, f"{field} has invalid stable ID: {value!r}", line=line_no)
            if primary_field and isinstance(obj.get(primary_field), str):
                value = obj[primary_field]
                key = (primary_field, value)
                prior = seen_primary.get(key)
                if prior:
                    report.add("DUPLICATE_ID", artifact, f"Duplicate {primary_field} {value}; first seen at {prior[0]}:{prior[1]}", line=line_no)
                else:
                    seen_primary[key] = (artifact, line_no)


def _collect(records: dict[str, list[tuple[int, dict[str, Any]]]], path: str) -> list[dict[str, Any]]:
    return [obj for _, obj in records.get(path, [])]


def _semantic_events(records: dict[str, list[tuple[int, dict[str, Any]]]], report: ValidationReport) -> None:
    path = "evaluation/events.jsonl"
    rows = records.get(path, [])
    by_id = {o.get("event_id"): o for _, o in rows if isinstance(o.get("event_id"), str)}
    for line_no, event in rows:
        parent = event.get("parent_event_id")
        if parent and parent not in by_id:
            report.add("BROKEN_EVENT_REFERENCE", path, f"parent_event_id {parent} does not exist.", line=line_no)
        if event.get("status") == "superseded":
            attrs = event.get("attributes") or {}
            replacement = attrs.get("superseded_by_event_id")
            if not replacement:
                report.add("INVALID_SUPERSESSION", path, "Superseded event must declare attributes.superseded_by_event_id.", line=line_no)
            elif replacement == event.get("event_id") or replacement not in by_id:
                report.add("INVALID_SUPERSESSION", path, f"superseded_by_event_id {replacement!r} must resolve to a distinct event.", line=line_no)


def _semantic_regressions(records: dict[str, list[tuple[int, dict[str, Any]]]], contracts: list[tuple[str, dict[str, Any]]], report: ValidationReport) -> None:
    reg_path = "self-improvement/regressions.jsonl"
    dec_path = "self-improvement/decisions.jsonl"
    regs = _collect(records, reg_path)
    decisions = {d.get("decision_id"): d for d in _collect(records, dec_path)}
    reg_by_id = {r.get("regression_id"): r for r in regs}
    for i, reg in enumerate(regs, 1):
        if reg.get("status") in {"retired", "superseded"}:
            did = reg.get("superseding_decision_id")
            dec = decisions.get(did)
            if not did or not dec or dec.get("status") != "approved":
                report.add("UNGOVERNED_REGRESSION_RETIREMENT", reg_path, f"{reg.get('regression_id')} is {reg.get('status')} without an approved superseding decision.", line=i)
    for artifact, contract in contracts:
        ids = contract.get("applicable_regressions") or contract.get("critical_regressions") or []
        for rid in ids:
            reg = reg_by_id.get(rid)
            if not reg:
                report.add("MISSING_CRITICAL_REGRESSION", artifact, f"Referenced regression {rid} does not exist.")
            elif reg.get("status") != "active":
                report.add("INACTIVE_CRITICAL_REGRESSION", artifact, f"Referenced regression {rid} is not active.")


def _semantic_metrics(records: dict[str, list[tuple[int, dict[str, Any]]]], report: ValidationReport) -> None:
    den_path = "evaluation/denominator-snapshots.jsonl"
    met_path = "evaluation/metric-ledger.jsonl"
    den_rows = records.get(den_path, [])
    met_rows = records.get(met_path, [])
    snapshots = {o.get("snapshot_id"): o for _, o in den_rows}
    events = {o.get("event_id") for _, o in records.get("evaluation/events.jsonl", [])}

    for line_no, snap in den_rows:
        md = snap.get("missing_data") or {}
        if md.get("status") == "complete" and snap.get("denominator_value") is None:
            report.add("MISSING_DENOMINATOR", den_path, "Complete denominator snapshot must have denominator_value.", line=line_no)
        for eid in snap.get("source_event_ids") or []:
            if eid not in events:
                report.add("BROKEN_SOURCE_EVENT_REFERENCE", den_path, f"source_event_id {eid} does not exist.", line=line_no)

    for line_no, metric in met_rows:
        md = metric.get("missing_data") or {}
        sid = metric.get("snapshot_id")
        if not sid:
            if md.get("status") == "complete":
                report.add("MISSING_DENOMINATOR_SNAPSHOT", met_path, "Complete metric record must reference snapshot_id.", line=line_no)
            continue
        snap = snapshots.get(sid)
        if not snap:
            report.add("MISSING_DENOMINATOR_SNAPSHOT", met_path, f"snapshot_id {sid} does not exist.", line=line_no)
            continue
        comparisons = [
            ("cutoff_utc", "METRIC_CUTOFF_MISMATCH"),
            ("scope", "METRIC_SCOPE_MISMATCH"),
            ("denominator_value", "METRIC_DENOMINATOR_MISMATCH"),
            ("denominator_unit", "METRIC_DENOMINATOR_UNIT_MISMATCH"),
        ]
        for field, code in comparisons:
            if metric.get(field) != snap.get(field):
                report.add(code, met_path, f"{field} differs from snapshot {sid}.", line=line_no)
        if metric.get("metric_name") != snap.get("metric_name"):
            report.add("METRIC_NAME_MISMATCH", met_path, f"metric_name differs from snapshot {sid}.", line=line_no)
        if md.get("status") == "complete":
            numerator = metric.get("numerator_value")
            denominator = metric.get("denominator_value")
            value = metric.get("value")
            if numerator is None or denominator is None:
                report.add("INCOMPLETE_COMPLETE_METRIC", met_path, "Complete metric must have numerator and denominator.", line=line_no)
            elif denominator == 0:
                if value is not None:
                    report.add("ZERO_DENOMINATOR_VALUE", met_path, "Zero denominator must produce value=null and explicit missing-data state.", line=line_no)
                if md.get("status") == "complete":
                    report.add("ZERO_DENOMINATOR_COMPLETE", met_path, "Zero denominator cannot be marked complete.", line=line_no)
            else:
                expected = numerator / denominator
                if value is None or not math.isclose(value, expected, rel_tol=1e-12, abs_tol=1e-12):
                    report.add("METRIC_CALCULATION_MISMATCH", met_path, f"value {value!r} does not equal numerator/denominator {expected}.", line=line_no)
        else:
            if metric.get("value") is not None and not (metric.get("denominator_value") not in (None, 0) and metric.get("numerator_value") is not None):
                report.add("MISSING_DATA_MASQUERADES_AS_VALUE", met_path, "Incomplete/unavailable metric must not invent a value.", line=line_no)
        for eid in metric.get("source_event_ids") or []:
            if eid not in events:
                report.add("BROKEN_SOURCE_EVENT_REFERENCE", met_path, f"source_event_id {eid} does not exist.", line=line_no)


def _semantic_scorecards(records: dict[str, list[tuple[int, dict[str, Any]]]], contracts: list[tuple[str, dict[str, Any]]], report: ValidationReport) -> None:
    path = "evaluation/release-scorecards.jsonl"
    contract_by_id = {c.get("contract_id"): c for _, c in contracts}
    for line_no, card in records.get(path, []):
        evaluator = card.get("evaluator_actor_id")
        impls = set(card.get("implementation_actor_ids") or [])
        if evaluator in impls:
            report.add("CANDIDATE_SELF_CERTIFICATION", path, "Evaluator actor is also an implementation actor.", line=line_no)
        contract = contract_by_id.get(card.get("contract_id"))
        if not contract:
            report.add("BROKEN_CONTRACT_REFERENCE", path, f"contract_id {card.get('contract_id')} does not resolve.", line=line_no)
            continue
        gate_ids = {o.get("id") for o in card.get("gate_outcomes") or []}
        for gid in contract.get("mandatory_gates") or []:
            if gid not in gate_ids:
                report.add("MISSING_GATE_OUTCOME", path, f"Mandatory gate {gid} has no scorecard outcome.", line=line_no)
        reg_ids = {o.get("id") for o in card.get("regression_outcomes") or []}
        required_regs = contract.get("applicable_regressions") or contract.get("critical_regressions") or []
        for rid in required_regs:
            if rid not in reg_ids:
                report.add("MISSING_REGRESSION_OUTCOME", path, f"Applicable regression {rid} has no scorecard outcome.", line=line_no)


def _semantic_contracts(contracts: list[tuple[str, dict[str, Any]]], report: ValidationReport) -> None:
    for artifact, contract in contracts:
        if contract.get("schema_version") == "2.0":
            if contract.get("parent_version") == contract.get("candidate_version"):
                report.add("INVALID_VERSION_LINEAGE", artifact, "parent_version and candidate_version must differ.")
            if not validate_contract_hash(contract):
                report.add("FROZEN_CONTRACT_HASH_MISMATCH", artifact, "contract_hash does not match canonical contract content.")


def _semantic_manifests(root: Path, manifests: list[tuple[str, dict[str, Any]]], contracts: list[tuple[str, dict[str, Any]]], records: dict[str, list[tuple[int, dict[str, Any]]]], report: ValidationReport) -> None:
    contract_by_version = {c.get("candidate_version"): c for _, c in contracts}
    decisions = {d.get("decision_id"): d for d in _collect(records, "self-improvement/decisions.jsonl")}
    regs = {r.get("regression_id"): r for r in _collect(records, "self-improvement/regressions.jsonl")}
    for artifact, manifest in manifests:
        for relpath, declared in (manifest.get("content_hashes") or {}).items():
            p = root / relpath
            if not p.exists():
                report.add("MANIFEST_FILE_MISSING", artifact, f"Manifest content file does not exist: {relpath}")
                continue
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            if actual != declared:
                report.add("MANIFEST_HASH_MISMATCH", artifact, f"SHA-256 mismatch for {relpath}")
        if manifest.get("manifest_schema_version") == "2.0":
            contract = contract_by_version.get(manifest.get("version"))
            if not contract:
                report.add("MANIFEST_CONTRACT_MISSING", artifact, "No frozen contract found for manifest version.")
            elif manifest.get("release_contract_hash") != contract.get("contract_hash"):
                report.add("MANIFEST_CONTRACT_HASH_MISMATCH", artifact, "release_contract_hash does not match frozen contract.")
            for rid in manifest.get("retired_regressions") or []:
                reg = regs.get(rid)
                if not reg or reg.get("status") not in {"retired", "superseded"}:
                    report.add("INVALID_RETIRED_REGRESSION_DECLARATION", artifact, f"Manifest declares {rid} retired but registry does not.")
                elif not reg.get("superseding_decision_id") or reg.get("superseding_decision_id") not in decisions:
                    report.add("UNGOVERNED_REGRESSION_RETIREMENT", artifact, f"Retired regression {rid} lacks governed decision.")


def _validate_package_manifest(root: Path, report: ValidationReport) -> None:
    path = root / "PACKAGE-MANIFEST.json"
    if not path.exists():
        return
    obj = _read_json(path, root, report)
    if not isinstance(obj, dict):
        return
    entries = obj.get("files")
    if not isinstance(entries, list):
        report.add("PACKAGE_MANIFEST_INVALID", "PACKAGE-MANIFEST.json", "files must be an array.")
        return
    seen = set()
    for ent in entries:
        if not isinstance(ent, dict) or not all(k in ent for k in ("path", "sha256", "bytes")):
            report.add("PACKAGE_MANIFEST_INVALID", "PACKAGE-MANIFEST.json", "Each file entry requires path, sha256, bytes.")
            continue
        relpath = ent["path"]
        if relpath in seen:
            report.add("PACKAGE_MANIFEST_DUPLICATE", "PACKAGE-MANIFEST.json", f"Duplicate entry {relpath}")
        seen.add(relpath)
        p = root / relpath
        if not p.exists():
            report.add("PACKAGE_MANIFEST_FILE_MISSING", "PACKAGE-MANIFEST.json", f"Missing file {relpath}")
            continue
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != ent["sha256"]:
            report.add("PACKAGE_MANIFEST_HASH_MISMATCH", "PACKAGE-MANIFEST.json", f"Hash mismatch for {relpath}")
        if len(data) != ent["bytes"]:
            report.add("PACKAGE_MANIFEST_SIZE_MISMATCH", "PACKAGE-MANIFEST.json", f"Byte count mismatch for {relpath}")


def validate_workspace(root: str | Path, *, validate_package_manifest: bool = True) -> ValidationReport:
    root = Path(root).resolve()
    report = ValidationReport()
    if not root.exists() or not root.is_dir():
        report.add("WORKSPACE_NOT_FOUND", str(root), "Workspace path does not exist or is not a directory.")
        return report

    _validate_all_schema_documents(root, report)
    records: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    contracts: list[tuple[str, dict[str, Any]]] = []
    manifests: list[tuple[str, dict[str, Any]]] = []

    # Known JSONL production ledgers.
    for relpath, schema_name in JSONL_SCHEMAS.items():
        path = root / relpath
        if not path.exists():
            continue
        rows = _read_jsonl(path, root, report)
        records[relpath] = rows
        for line_no, obj in rows:
            _validate_schema(root, schema_name, obj, relpath, report, line_no)

    # Version JSON artifacts.
    versions = root / "versions"
    if versions.exists():
        for path in sorted(versions.glob("v*/FROZEN-RELEASE-CONTRACT.json")):
            obj = _read_json(path, root, report)
            if isinstance(obj, dict):
                artifact = _rel(root, path)
                schema_name = schema_for_json(artifact, obj)
                if schema_name:
                    _validate_schema(root, schema_name, obj, artifact, report)
                contracts.append((artifact, obj))
        for path in sorted(versions.glob("v*/MANIFEST.json")):
            obj = _read_json(path, root, report)
            if isinstance(obj, dict):
                artifact = _rel(root, path)
                schema_name = schema_for_json(artifact, obj)
                if schema_name:
                    _validate_schema(root, schema_name, obj, artifact, report)
                manifests.append((artifact, obj))

    _stable_id_check(records, report)
    _semantic_events(records, report)
    _semantic_regressions(records, contracts, report)
    _semantic_metrics(records, report)
    _semantic_contracts(contracts, report)
    _semantic_scorecards(records, contracts, report)
    _semantic_manifests(root, manifests, contracts, records, report)
    if validate_package_manifest:
        _validate_package_manifest(root, report)
    return report
