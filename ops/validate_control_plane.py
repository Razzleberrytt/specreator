#!/usr/bin/env python3
"""Dependency-free validation for Spec Creator shared control-plane metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(relative: str):
    with (ROOT / relative).open("r", encoding="utf-8") as handle:
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

    require_keys(state, {"schema_version","state_id","repository","current_sealed_release","active_candidate","phase","lane_ownership","blockers","live_claims","latest_handoff_receipt_ids","verification_receipt","next_legal_transition","successor_cycle_count_since_convergence_review","convergence_mode","v1_convergence"}, "state")
    repo = state["repository"]
    require_keys(repo, {"full_name","default_branch","observation_basis_main_sha","observation_basis_tree_sha","baseline_bytes_present","restoration_integrity_verified","baseline_reconciled"}, "repository observation")

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
    if repo["baseline_bytes_present"] and (not contract_path.is_file() or not manifest_path.is_file()):
        fail("baseline bytes present requires restored frozen contract and package manifest")
    contract_hash = load_json("versions/v0.11.1/FROZEN-RELEASE-CONTRACT.json").get("contract_hash") if repo["baseline_bytes_present"] else None

    candidate = state["active_candidate"]
    sealed = state["current_sealed_release"]
    if repo["baseline_reconciled"]:
        if candidate is not None:
            fail("no active successor candidate may exist before a valid preregistration freeze is reconciled")
        if not isinstance(sealed, dict) or sealed.get("version") != "0.11.1":
            fail("reconciled baseline requires current sealed v0.11.1 release")
        if sealed.get("frozen_contract_hash") != contract_hash:
            fail("sealed release frozen contract hash must match restored contract")
        if sealed.get("new_seal_created") is not False:
            fail("baseline reconciliation must not create a new v0.11.1 seal")
        receipt_id = sealed.get("reconciliation_receipt_id")
        if not receipt_id or not (ROOT / "ops/reconciliation-receipts" / f"{receipt_id}.json").is_file():
            fail("sealed release reconciliation receipt is missing")
    else:
        if sealed is not None:
            fail("current sealed release must remain null before baseline reconciliation")

    receipt = state["verification_receipt"]
    if repo["baseline_reconciled"]:
        if receipt.get("freshness") != "VALID_FOR_HISTORICAL_SEALED_PACKAGE_BY_EXACT_BYTE_IDENTITY" or not receipt.get("identity"):
            fail("historical sealed baseline requires exact-byte-identity verifier freshness")

    claim_ids, live_claim_ids = [], []
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

    trajectory_blockers = trajectory["objective_v1_must_blockers"]
    trajectory_ids = [item["id"] for item in trajectory_blockers]
    if len(trajectory_ids) != len(set(trajectory_ids)):
        fail("duplicate v1 trajectory blocker id")
    declared_count = trajectory["convergence_review"]["must_blocker_count"]
    if declared_count != len(trajectory_blockers):
        fail("v1 convergence blocker count mismatch")
    if state["v1_convergence"]["must_blocker_count"] != declared_count or sorted(state["v1_convergence"]["must_blockers"]) != sorted(trajectory_ids):
        fail("canonical state and trajectory disagree on v1 MUST blockers")

    failed = state.get("failed_preregistrations", [])
    failed_ids = [item.get("freeze_id") for item in failed]
    if len(failed_ids) != len(set(failed_ids)):
        fail("duplicate failed preregistration freeze identity")
    for item in failed:
        receipt_id = item.get("reconciliation_receipt_id")
        if not receipt_id or not (ROOT / "ops/reconciliation-receipts" / f"{receipt_id}.json").is_file():
            fail("failed preregistration must have an immutable reconciliation receipt")
        if item.get("disposition") != "REJECTED_FOR_IMPLEMENTATION_AUTHORITY_PRESERVE_HISTORY":
            fail("failed preregistration disposition must preserve history and deny implementation authority")

    next_action = state["next_legal_transition"]["action"]
    if not repo["baseline_bytes_present"]:
        expected_action = "RECOVER_CANONICAL_V0_11_1_BASELINE"
    elif not repo["restoration_integrity_verified"]:
        expected_action = "VERIFY_RESTORED_V0_11_1_BASELINE_INTEGRITY"
    elif not repo["baseline_reconciled"]:
        expected_action = "RECONCILE_RESTORED_V0_11_1_BASELINE"
    elif failed and state["v1_convergence"].get("selected_next_blocker") == "V1-MUST-FRESHNESS-001":
        expected_action = "PREREGISTER_V1_FRESHNESS_MUTATION_MATRIX_RETRY"
    elif state["phase"] == "V1_GAP_PREREGISTRATION":
        expected_action = "PREREGISTER_V1_FRESHNESS_MUTATION_MATRIX"
    else:
        expected_action = "RECONCILE_V1_MUST_EVIDENCE_AGAINST_SEALED_V0_11_1"
    if next_action != expected_action:
        fail(f"next legal action must be {expected_action}")

    if failed and candidate is not None:
        fail("rejected preregistration cannot coexist with an active successor candidate")
    if failed and trajectory.get("next_priority", {}).get("implementation_authorized") is not False:
        fail("rejected preregistration must keep successor implementation unauthorized")

    if state["successor_cycle_count_since_convergence_review"] < 0 or not state["convergence_mode"]:
        fail("convergence state must be explicit and nonnegative")

    print("PASS: control-plane metadata internally consistent and fail-closed")


if __name__ == "__main__":
    main()
