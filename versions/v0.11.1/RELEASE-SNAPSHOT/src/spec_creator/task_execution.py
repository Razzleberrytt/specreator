from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json

from jsonschema import Draft202012Validator, FormatChecker

ALLOWED_TRANSITIONS = {
    "planned": {"ready", "cancelled"},
    "ready": {"in_progress", "blocked", "cancelled"},
    "in_progress": {"blocked", "done", "cancelled"},
    "blocked": {"ready", "cancelled"},
    "done": set(),
    "cancelled": set(),
}


def _load_schema(root: Path) -> dict[str, Any]:
    return json.loads((root / "schemas" / "task-execution-event-v1.schema.json").read_text(encoding="utf-8"))


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def replay_task_events(*, graph_hash: str, task_ids: list[str] | set[str], events: list[dict[str, Any]], root: str | Path | None = None) -> dict[str, Any]:
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = Path(root)
    validator = Draft202012Validator(_load_schema(root), format_checker=FormatChecker())
    valid_tasks = set(task_ids)
    diagnostics: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    states: dict[str, str] = {}
    last_time: datetime | None = None

    for idx, event in enumerate(events, 1):
        schema_errors = sorted(validator.iter_errors(event), key=lambda e: list(e.absolute_path))
        if schema_errors:
            for err in schema_errors:
                where = ".".join(str(x) for x in err.absolute_path) or "<root>"
                diagnostics.append({"code": "TE-SCHEMA", "event_index": idx, "event_id": event.get("event_id"), "message": f"{where}: {err.message}"})
            continue

        eid = event["event_id"]
        if eid in seen_ids:
            diagnostics.append({"code": "TE-DUPLICATE-EVENT", "event_index": idx, "event_id": eid, "message": "Duplicate task execution event ID."})
            continue
        seen_ids.add(eid)

        if event["graph_hash"] != graph_hash:
            diagnostics.append({"code": "TE-GRAPH-HASH-MISMATCH", "event_index": idx, "event_id": eid, "message": "Execution event graph hash differs from immutable compiled graph hash."})
            continue
        tid = event["task_id"]
        if tid not in valid_tasks:
            diagnostics.append({"code": "TE-UNKNOWN-TASK", "event_index": idx, "event_id": eid, "message": f"Unknown compiled task {tid}."})
            continue

        when = _dt(event["event_time_utc"])
        if last_time is not None and when < last_time:
            diagnostics.append({"code": "TE-TIME-REVERSAL", "event_index": idx, "event_id": eid, "message": "Task execution event time moved backward."})
            continue
        last_time = when

        current = states.get(tid)
        if current is None:
            if event["from_state"] is not None or event["to_state"] != "planned":
                diagnostics.append({"code": "TE-INVALID-INITIAL", "event_index": idx, "event_id": eid, "message": "First task event must be null -> planned."})
                continue
            states[tid] = "planned"
            continue

        if event["from_state"] != current:
            diagnostics.append({"code": "TE-FROM-STATE-MISMATCH", "event_index": idx, "event_id": eid, "message": f"Declared from_state {event['from_state']!r} does not match replayed state {current!r}."})
            continue
        if event["to_state"] not in ALLOWED_TRANSITIONS[current]:
            diagnostics.append({"code": "TE-INVALID-TRANSITION", "event_index": idx, "event_id": eid, "message": f"Transition {current} -> {event['to_state']} is not allowed."})
            continue
        states[tid] = event["to_state"]

    return {
        "ok": not diagnostics,
        "graph_hash": graph_hash,
        "event_count": len(events),
        "final_states": dict(sorted(states.items())),
        "diagnostics": diagnostics,
    }


def replay_task_events_file(graph_path: str | Path, events_path: str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    graph = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    events = [json.loads(line) for line in Path(events_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    return replay_task_events(graph_hash=graph["graph_hash"], task_ids=[t["task_id"] for t in graph.get("tasks", [])], events=events, root=root)
