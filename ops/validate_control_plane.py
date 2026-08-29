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
            "current_sealed_release",
            "active_candidate",
            "phase",
            "lane_ownership",
            "blockers",
            "live_claims",
            "latest_handoff_receipt_ids",
            "verification_receipt",
            "next_legal_transition",
            "successor_cycle_count_since_convergence_review",
            "convergence_mode",
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
            "restoration_integrity_verified",
            "baseline_reconciled",
        },
        "repository observation",
    )

    for key in ("observation_basis_main_sha", "observation_basis_tree_sha"):
        value = repo[key]
        if not isinstance(value, str) or len(value) != 40:
            fail(f"repository {key} must be a 40-character git SHA")

    if repo["restoration_integrity_verified"] and not repo["baseline_bytes_present"]:
        fail("restoration integrity cannot be verified when baseline bytes are absent")
    if repo["baseline_reconciled"] and not repo["restoration_integrity_verified"]:
        fail("baseline cannot be reconciled before restoration integrity is verified")

    contract_path = ROOT / "versions/v0.11.1/FROZEN-RELEASE-CONTRACT.json"
    manifest_path = ROOT / "PACKAGE-MANIFEST.json"
    if repo["baseline_bytes_present"]:
        if not contract_path.is_file():
            fail("baseline_bytes_present requires the v0.11.1 frozen contract to exist")
        if not manifest_path.is_file():
            fail("baseline_bytes_present requires the restored package manifest to exist")
    elif contract_path.exists() or manifest_path.exists():
        fail("restored-looking baseline artifacts exist but baseline_bytes_present is false")

    contract = load_json("versions/v0.11.1/FROZEN-RELEASE-CONTRACT.json") if repo["baseline_bytes_present"] else None
    contract_hash = contract.get("contract_hash") if contract else None

    candidate = state["active_candidate"]
    sealed = state["current_sealed_release"]

    if not repo["baseline_reconciled"]:
        if sealed is not None:
            fail("current sealed release must remain null before baseline reconciliation")
        if not isinstance(candidate, dict) or candidate.get("version") != "0.11.1":
            fail("active candidate must remain v0.11.1 before baseline reconciliation")
        if candidate.get("exact_candidate_sha") is not None:
            fail("exact candidate SHA cannot become release authority before lane-5 reconciliation")
        if contract_hash and candidate.get("frozen_contract_hash") != contract_hash:
            fail("candidate frozen_contract_hash must match the restored frozen contract")
    else:
        if candidate is not None:
            fail("no active successor candidate may exist immediately after baseline reconciliation")
        if not isinstance(sealed, dict):
            fail("reconciled baseline requires current_sealed_release")
        if sealed.get("version") != "0.11.1":
            fail("reconciled baseline sealed release must be v0.11.1")
        if sealed.get("frozen_contract_hash") != contract_hash:
            fail("sealed release frozen contract hash must match restored contract")
        if sealed.get("new_seal_created") is not False:
            fail("baseline reconciliation must not create a new v0.11.1 seal")
        receipt_id = sealed.get("reconciliation_receipt_id")
        if not receipt_id:
            fail("reconciled sealed release requires a reconciliation receipt id")
        receipt_path = ROOT / "ops/reconciliation-receipts" / f"{receipt_id}.json"
        if not receipt_path.is_file():
            fail("sealed release reconciliation receipt file is missing")

    blocker_ids = [item["id"] for item in state["blockers"]]
    if len(blocker_ids) != len(set(blocker_ids)):
        fail("duplicate blocker id")
    if repo["baseline_reconciled"] and any(item.get("status") == "OPEN" for item in state["blockers"]):
        fail("baseline-reconciled state cannot retain an open baseline blocker")

    receipt = state["verification_receipt"]
    if repo["baseline_reconciled"]:
        if receipt.get("freshness") != "VALID_FOR_HISTORICAL_SEALED_PACKAGE_BY_EXACT_BYTE_IDENTITY":
            fail("reconciled historical seal requires exact-byte-identity freshness status")
        if not receipt.get("identity"):
            fail("reconciled historical seal must reference verifier evidence identity")
    elif receipt.get("freshness") in {"FRESH", "VALID", "CURRENT"}:
        fail("generic fresh verification cannot authorize unreconciled baseline state")

    if not repo["baseline_bytes_present"]:
        expected_action = "RECOVER_CANONICAL_V0_11_1_BASELINE"
    elif not repo["restoration_integrity_verified"]:
        expected_action = "VERIFY_RESTORED_V0_11_1_BASELINE_INTEGRITY"
    elif not repo["baseline_reconciled"]:
        expected_action = "RECONCILE_RESTORED_V0_11_1_BASELINE"
    else:
        expected_action = "RECONCILE_V1_MUST_EVIDENCE_AGAINST_SEALED_V0_11_1"

    next_action = state["next_legal_transition"]["action"]
    if next_action != expected_action:
        fail(f"next legal action must be {expected_action}")

    claim_ids = []
    live_claim_ids = []
    for claim in claims["claims"]:
        claim_ids.append(claim["task_id"])
        if claim["status"] == "ACTIVE":
            if parse_ts(claim["expires_at"]) <= parse_ts(claim["updated_at"]):
                fail(f"claim {claim['task_id']} expires_at must be after updated_at")
            live_claim_ids.append(claim["task_id"])
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate work-claim task id")
    if sorted(state["live_claims"]) != sorted(live_claim_ids):
        fail("canonical state live_claims disagrees with work-claims ledger")

    if not repo["baseline_reconciled"] and trajectory["prospective_successors"]:
        fail("successor admission is prohibited before v0.11.1 baseline reconciliation")

    trajectory_blockers = trajectory["objective_v1_must_blockers"]
    trajectory_ids = [item["id"] for item in trajectory_blockers]
    if len(trajectory_ids) != len(set(trajectory_ids)):
        fail("duplicate v1 trajectory blocker id")
    declared_count = trajectory["convergence_review"]["must_blocker_count"]
    if declared_count != len(trajectory_blockers):
        fail("v1 convergence blocker count mismatch")
    if state["v1_convergence"]["must_blocker_count"] != declared_count:
        fail("canonical state and trajectory disagree on v1 MUST blocker count")
    if sorted(state["v1_convergence"]["must_blockers"]) != sorted(trajectory_ids):
        fail("canonical state and trajectory disagree on v1 MUST blocker identities")

    if state["successor_cycle_count_since_convergence_review"] < 0:
        fail("successor cycle count cannot be negative")
    if not state["convergence_mode"]:
        fail("convergence_mode must be explicit")

    print("PASS: control-plane metadata internally consistent and fail-closed")


if __name__ == "__main__":
    main()
