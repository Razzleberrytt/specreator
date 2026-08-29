#!/usr/bin/env python3
"""Dependency-free validation for Spec Creator shared control-plane metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(relative: str):
    path = ROOT / relative
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require_keys(mapping: dict, required: set[str], label: str) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        fail(f"{label} missing required keys: {missing}")


def main() -> None:
    state = load_json("ops/spec-creator-state.json")
    claims = load_json("ops/work-claims.json")
    trajectory = load_json("ops/V1-TRAJECTORY.json")

    require_keys(
        state,
        {
            "schema_version",
            "state_id",
            "repository",
            "active_candidate",
            "phase",
            "lane_ownership",
            "blockers",
            "verification_receipt",
            "next_legal_transition",
            "v1_convergence",
        },
        "state",
    )

    repo = state["repository"]
    require_keys(
        repo,
        {
            "full_name",
            "default_branch",
            "observation_basis_main_sha",
            "observation_basis_tree_sha",
            "baseline_bytes_present",
            "baseline_reconciled",
        },
        "repository observation",
    )

    # A control-plane commit cannot contain its own commit SHA. The two
    # observation-basis fields intentionally bind to the exact main/tree state
    # inspected immediately before the reconciliation commit was written.
    for key in ("observation_basis_main_sha", "observation_basis_tree_sha"):
        value = repo[key]
        if not isinstance(value, str) or len(value) != 40:
            fail(f"repository {key} must be a 40-character git SHA")

    if state["phase"] == "BASELINE_RECONSTRUCTION_BLOCKED" and repo["baseline_reconciled"]:
        fail("blocked baseline phase cannot claim a reconciled baseline")

    contract_path = ROOT / "versions/v0.11.1/FROZEN-RELEASE-CONTRACT.json"
    manifest_path = ROOT / "PACKAGE-MANIFEST.json"
    if repo["baseline_bytes_present"]:
        if not contract_path.is_file():
            fail("baseline_bytes_present requires the v0.11.1 frozen contract to exist")
        if not manifest_path.is_file():
            fail("baseline_bytes_present requires the restored package manifest to exist")
    elif contract_path.exists() or manifest_path.exists():
        fail("restored-looking baseline artifacts exist but baseline_bytes_present is false")

    candidate = state["active_candidate"]
    if candidate["version"] != "0.11.1":
        fail("active candidate must remain v0.11.1 until baseline reconciliation")
    if not repo["baseline_reconciled"] and candidate["exact_candidate_sha"] is not None:
        fail("exact candidate SHA cannot be authoritative before baseline reconciliation")

    if repo["baseline_bytes_present"]:
        contract = load_json("versions/v0.11.1/FROZEN-RELEASE-CONTRACT.json")
        actual_contract_hash = contract.get("contract_hash")
        if candidate.get("frozen_contract_hash") != actual_contract_hash:
            fail("candidate frozen_contract_hash must match the restored frozen contract")

    blockers = state["blockers"]
    blocker_ids = [item["id"] for item in blockers]
    if len(blocker_ids) != len(set(blocker_ids)):
        fail("duplicate blocker id")
    if not repo["baseline_reconciled"] and "BLK-BASELINE-001" not in blocker_ids:
        fail("baseline blocker must remain explicit until reconciliation completes")

    receipt = state["verification_receipt"]
    if not repo["baseline_reconciled"] and receipt.get("freshness") in {"FRESH", "VALID", "CURRENT"}:
        fail("verification cannot be fresh/current before baseline reconciliation")

    next_action = state["next_legal_transition"]["action"]
    expected_action = (
        "RECONCILE_CANONICAL_V0_11_1_BASELINE"
        if repo["baseline_bytes_present"]
        else "RECOVER_CANONICAL_V0_11_1_BASELINE"
    )
    if next_action != expected_action:
        fail(f"next legal action must be {expected_action}")

    claim_ids = []
    for claim in claims["claims"]:
        claim_ids.append(claim["task_id"])
        # Follow the ledger's stated staleness policy: only ACTIVE claims are
        # live mutation authority. ACTIVE_BLOCKED records ownership context but
        # do not authorize mutation while blocked.
        if claim["status"] == "ACTIVE":
            if parse_ts(claim["expires_at"]) <= parse_ts(claim["updated_at"]):
                fail(f"claim {claim['task_id']} expires_at must be after updated_at")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate work-claim task id")

    if not repo["baseline_reconciled"] and trajectory["prospective_successors"]:
        fail("successor admission is prohibited before v0.11.1 baseline reconciliation/seal")

    trajectory_blockers = trajectory["objective_v1_must_blockers"]
    declared_count = trajectory["convergence_review"]["must_blocker_count"]
    if declared_count != len(trajectory_blockers):
        fail("v1 convergence blocker count mismatch")
    if state["v1_convergence"]["must_blocker_count"] != declared_count:
        fail("canonical state and trajectory disagree on v1 MUST blocker count")

    print(
        "PASS: control-plane metadata internally consistent; "
        "baseline reconciliation remains fail-closed"
    )


if __name__ == "__main__":
    main()
