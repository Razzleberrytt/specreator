from __future__ import annotations
from pathlib import Path
from typing import Any


JSONL_SCHEMAS = {
    "evaluation/events.jsonl": "event-v1.schema.json",
    "evaluation/metric-ledger.jsonl": "metric-ledger-v1.schema.json",
    "evaluation/denominator-snapshots.jsonl": "denominator-snapshot-v1.schema.json",
    "evaluation/release-scorecards.jsonl": "release-scorecard-v1.schema.json",
    "self-improvement/improvement-ledger.jsonl": "improvement-v1.schema.json",
    "self-improvement/experiment-registry.jsonl": "experiment-v1.schema.json",
    "self-improvement/regressions.jsonl": "regression-v1.schema.json",
    "self-improvement/decisions.jsonl": "decision-v1.schema.json",
    "requirements/requirements.jsonl": "requirement-v1.schema.json",
    "tasks/tasks.jsonl": "task-v1.schema.json",
    "evaluation/gates.jsonl": "gate-v1.schema.json",
}


def schema_for_json(relative_path: str, obj: dict[str, Any]) -> str | None:
    p = Path(relative_path)
    if p.name == "FROZEN-RELEASE-CONTRACT.json":
        return "frozen-release-contract-v2.schema.json" if obj.get("schema_version") == "2.0" else "frozen-release-contract-v1.schema.json"
    if p.name == "MANIFEST.json" and "versions" in p.parts:
        return "manifest-v2.schema.json" if obj.get("manifest_schema_version") == "2.0" else "manifest-v1.schema.json"
    return None
