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


def main() -> None:
    state = load_json("ops/spec-creator-state.json")
    claims = load_json("ops/work-claims.json")
    trajectory = load_json("ops/V1-TRAJECTORY.json")

    required_state = {
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
    }
    missing = sorted(required_state - set(state))
    if missing:
        fail(f"state missing required keys: {missing}")

    repo = state["repository"]
    if repo["baseline_present"] is not False:
        fail("bootstrap validator is only valid while canonical baseline is absent")
    if repo["observed_shipped_files"] != 1:
        fail("observed shipped-file count must match the inspected one-file GitHub tree")

    candidate = state["active_candidate"]
    if candidate["version"] != "0.11.1":
        fail("active candidate must remain v0.11.1 until baseline reconstruction")
    if candidate["exact_candidate_sha"] is not None:
        fail("candidate SHA must remain unknown until canonical bytes are recovered")
    if candidate["frozen_contract_hash"] is not None:
        fail("frozen contract hash must not be invented during reconstruction")

    blockers = state["blockers"]
    blocker_ids = [item["id"] for item in blockers]
    if len(blocker_ids) != len(set(blocker_ids)):
        fail("duplicate blocker id")
    if "BLK-BASELINE-001" not in blocker_ids:
        fail("baseline reconstruction blocker must remain explicit")

    receipt = state["verification_receipt"]
    if receipt["freshness"] != "STALE_FOR_GITHUB_REPOSITORY_STATE":
        fail("external verification cannot be fresh for the empty GitHub tree")

    if state["next_legal_transition"]["action"] != "RECOVER_CANONICAL_V0_11_1_BASELINE":
        fail("next legal action must remain canonical baseline recovery")

    claim_ids = []
    for claim in claims["claims"]:
        claim_ids.append(claim["task_id"])
        if claim["status"] in {"ACTIVE", "ACTIVE_BLOCKED"}:
            if parse_ts(claim["expires_at"]) <= parse_ts(claim["updated_at"]):
                fail(f"claim {claim['task_id']} expires_at must be after updated_at")
            if claim["candidate_version"] == "0.11.1" and claim["exact_candidate_sha"] is not None:
                fail("v0.11.1 claim must not invent an exact candidate SHA")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate work-claim task id")

    if trajectory["prospective_successors"]:
        fail("successor admission is prohibited before v0.11.1 baseline restoration/seal")
    trajectory_blockers = trajectory["objective_v1_must_blockers"]
    declared_count = trajectory["convergence_review"]["must_blocker_count"]
    if declared_count != len(trajectory_blockers):
        fail("v1 convergence blocker count mismatch")
    if state["v1_convergence"]["must_blocker_count"] != declared_count:
        fail("canonical state and trajectory disagree on v1 MUST blocker count")

    print("PASS: control-plane metadata internally consistent; baseline recovery remains fail-closed")


if __name__ == "__main__":
    main()
