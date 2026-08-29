from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import hashlib
import json

from jsonschema import Draft202012Validator, FormatChecker

from .task_compiler import validate_compiled_graph
from .task_execution import replay_task_events

ROLE = {
    "bootstrap": "bootstrap_agent",
    "implementation": "implementation_agent",
    "debug": "debug_agent",
    "verification": "verification_agent",
    "continuation": "continuation_agent",
}
NEXT_ACTION = {
    None: "initialize_task_execution",
    "planned": "advance_to_ready_when_prerequisites_satisfied",
    "ready": "begin_implementation",
    "in_progress": "continue_current_task",
    "blocked": "resolve_recorded_blocker",
    "done": "verification_or_next_task",
    "cancelled": "no_further_action",
}
BASE_CONSTRAINTS = [
    "Do not weaken or remove tests, gates, frozen criteria, or critical regressions to obtain a pass.",
    "Do not expand write scope beyond allowed_write_scopes.",
    "Report missing information explicitly; do not treat missing data as zero.",
]
KIND_CONSTRAINT = {
    "bootstrap": "Do not implement until prerequisites and an execution-authorizing prompt kind permit work.",
    "implementation": "Produce completion evidence for every evidence requirement before claiming done.",
    "debug": "Diagnose from observed evidence and preserve frozen requirements/tests while correcting the defect.",
    "verification": "Reproduce objective checks independently; do not rely on implementation-authored success conclusions.",
    "continuation": "Do not rewrite immutable task definitions or historical execution events.",
}
KIND_INSTRUCTION = {
    "bootstrap": "Establish bounded task context and readiness only; do not modify implementation artifacts.",
    "implementation": "Implement only this authorized task within allowed write scopes and satisfy every acceptance/evidence obligation.",
    "debug": "Diagnose and correct only the observed defect within allowed write scopes without weakening frozen checks.",
    "verification": "Independently verify the task against frozen criteria, tests, gates, and evidence; do not self-certify implementation work.",
    "continuation": "Resume from replayed execution state using only preserved evidence and the next permitted action.",
}


def _root(root: str | Path | None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[2]


def _canonical_hash(obj: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    data = copy.deepcopy(obj)
    for key in exclude or set():
        data.pop(key, None)
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _diag(code: str, message: str, refs: list[str] | None = None) -> dict[str, Any]:
    return {"code": code, "message": message, "refs": sorted(set(refs or []))}


def _load_schema(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / "schemas" / name).read_text(encoding="utf-8"))


def validate_prompt_input(obj: dict[str, Any], *, root: str | Path | None = None) -> list[dict[str, Any]]:
    r = _root(root)
    validator = Draft202012Validator(_load_schema(r, "prompt-compilation-input-v1.schema.json"), format_checker=FormatChecker())
    out: list[dict[str, Any]] = []
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(x) for x in err.absolute_path) or "<root>"
        out.append(_diag("PC-INPUT-SCHEMA", f"{where}: {err.message}"))
    return out


def validate_prompt_envelope(obj: dict[str, Any], *, root: str | Path | None = None) -> list[dict[str, Any]]:
    r = _root(root)
    validator = Draft202012Validator(_load_schema(r, "prompt-envelope-v1.schema.json"), format_checker=FormatChecker())
    out: list[dict[str, Any]] = []
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(x) for x in err.absolute_path) or "<root>"
        out.append(_diag("PC-OUTPUT-SCHEMA", f"{where}: {err.message}"))
    if not out and obj.get("envelope_hash") != _canonical_hash(obj, exclude={"envelope_hash"}):
        out.append(_diag("PC-ENVELOPE-HASH", "Prompt envelope hash does not match canonical content."))
    return out


def _empty_envelope(inp: Any, status: str, diagnostic: dict[str, Any]) -> dict[str, Any]:
    request_id = inp.get("request_id") if isinstance(inp, dict) else None
    candidate_version = inp.get("candidate_version") if isinstance(inp, dict) else None
    prompt_kind = inp.get("prompt_kind") if isinstance(inp, dict) else None
    task_id = inp.get("task_id") if isinstance(inp, dict) else None
    graph = inp.get("compiled_task_graph") if isinstance(inp, dict) else None
    graph_hash = graph.get("graph_hash") if isinstance(graph, dict) and isinstance(graph.get("graph_hash"), str) and len(graph.get("graph_hash")) == 64 else None
    actor_role = ROLE.get(prompt_kind) if isinstance(prompt_kind, str) else None
    env: dict[str, Any] = {
        "schema_version": "1.0",
        "request_id": request_id,
        "status": status,
        "candidate_version": candidate_version,
        "graph_hash": graph_hash,
        "task_id": task_id,
        "prompt_kind": prompt_kind,
        "actor_role": actor_role,
        "declared_write_scopes": [],
        "allowed_write_scopes": [],
        "prerequisite_states": [],
        "source_requirement_ids": [],
        "acceptance_criteria": [],
        "verification_refs": [],
        "gate_ids": [],
        "frozen_criteria_refs": [],
        "critical_obligations": [],
        "evidence_requirements": [],
        "source_evidence_refs": [],
        "included_context_refs": [],
        "excluded_context_refs": [],
        "task_state": None,
        "completed_evidence_refs": [],
        "open_blockers": [],
        "next_permitted_action": None,
        "completion_constraints": [],
        "diagnostics": [diagnostic],
        "prompt_text": None,
        "envelope_hash": "",
    }
    env["envelope_hash"] = _canonical_hash(env, exclude={"envelope_hash"})
    return env


def _task_indexes(graph: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    order = [t["task_id"] for t in graph.get("tasks", [])]
    return {t["task_id"]: t for t in graph.get("tasks", [])}, order


def _transitive_prereqs(task_id: str, tasks: dict[str, dict[str, Any]], order: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []

    def walk(tid: str) -> None:
        for pid in tasks[tid].get("prerequisite_task_ids", []):
            if pid not in seen:
                seen.add(pid)
                walk(pid)
                out.append(pid)

    walk(task_id)
    return sorted(out, key=order.index)


def _context_closure(inp: dict[str, Any], task: dict[str, Any], tasks: dict[str, dict[str, Any]], order: list[str]) -> tuple[list[str], list[str], list[str]]:
    tid = task["task_id"]
    prereqs = _transitive_prereqs(tid, tasks, order)
    closure_tasks = {tid, *prereqs}
    closure_reqs = set(task.get("source_requirement_ids", []))
    closure_tests = set(task.get("verification_refs", []))
    closure_gates = set(task.get("gate_ids", []))
    for pid in prereqs:
        closure_reqs.update(tasks[pid].get("source_requirement_ids", []))
        closure_tests.update(tasks[pid].get("verification_refs", []))
        closure_gates.update(tasks[pid].get("gate_ids", []))

    included: list[str] = []
    excluded: list[str] = []
    unbound_critical: list[str] = []
    for record in inp["context_records"]:
        selectors = record["selectors"]
        kind_ok = not selectors["prompt_kinds"] or inp["prompt_kind"] in selectors["prompt_kinds"]
        selector_hit = (
            bool(set(selectors["task_ids"]) & closure_tasks)
            or bool(set(selectors["requirement_ids"]) & closure_reqs)
            or bool(set(selectors["verification_refs"]) & closure_tests)
            or bool(set(selectors["gate_ids"]) & closure_gates)
            or bool(selectors["prompt_kinds"])
        )
        no_selector = not any(selectors.values())
        if no_selector and record["critical"]:
            unbound_critical.append(record["ref"])
        if kind_ok and selector_hit:
            included.append(record["ref"])
        else:
            excluded.append(record["ref"])
    return sorted(set(included)), sorted(set(excluded)), sorted(set(unbound_critical))


def _render_prompt(env: dict[str, Any]) -> str:
    def section(name: str, values: list[str]) -> str:
        if not values:
            return f"{name}:\n- <none>"
        return name + ":\n" + "\n".join(f"- {value}" for value in values)

    lines = [
        f"PROMPT_KIND: {env['prompt_kind']}",
        f"REQUEST_ID: {env['request_id']}",
        f"CANDIDATE_VERSION: {env['candidate_version']}",
        f"GRAPH_HASH: {env['graph_hash']}",
        f"TASK_ID: {env['task_id']}",
        f"ACTOR_ROLE: {env['actor_role']}",
        f"TASK_STATE: {env['task_state'] if env['task_state'] is not None else '<uninitialized>'}",
        f"NEXT_PERMITTED_ACTION: {env['next_permitted_action']}",
        section("DECLARED_WRITE_SCOPES", env["declared_write_scopes"]),
        section("ALLOWED_WRITE_SCOPES", env["allowed_write_scopes"]),
        section("PREREQUISITES", [f"{x['task_id']}={x['state']}" for x in env["prerequisite_states"]]),
        section("SOURCE_REQUIREMENTS", env["source_requirement_ids"]),
        section("ACCEPTANCE_CRITERIA", env["acceptance_criteria"]),
        section("VERIFICATION_REFS", env["verification_refs"]),
        section("GATES", env["gate_ids"]),
        section("FROZEN_CRITERIA", env["frozen_criteria_refs"]),
        section("CRITICAL_OBLIGATIONS", env["critical_obligations"]),
        section("EVIDENCE_REQUIREMENTS", env["evidence_requirements"]),
        section("INCLUDED_CONTEXT", env["included_context_refs"]),
        section("COMPLETED_EVIDENCE", env["completed_evidence_refs"]),
        section("OPEN_BLOCKERS", env["open_blockers"]),
        section("COMPLETION_CONSTRAINTS", env["completion_constraints"]),
        f"INSTRUCTION:\n{KIND_INSTRUCTION[env['prompt_kind']]}",
    ]
    return "\n\n".join(lines) + "\n"


def compile_prompt(inp: Any, *, root: str | Path | None = None) -> dict[str, Any]:
    r = _root(root)
    if not isinstance(inp, dict):
        return _empty_envelope(inp, "invalid", _diag("PC-INPUT-SCHEMA", "Input must be a JSON object."))
    schema_errors = validate_prompt_input(inp, root=r)
    if schema_errors:
        return _empty_envelope(inp, "invalid", schema_errors[0])

    graph = inp["compiled_task_graph"]
    graph_diagnostics = validate_compiled_graph(graph, root=r)
    if graph_diagnostics:
        refs = [d["code"] for d in graph_diagnostics]
        return _empty_envelope(inp, "invalid", _diag("PC-GRAPH-INVALID", "Parent v0.08 compiled task graph validation failed.", refs))

    tasks, order = _task_indexes(graph)
    tid = inp["task_id"]
    if tid not in tasks:
        return _empty_envelope(inp, "invalid", _diag("PC-TASK-NOT-FOUND", f"Compiled task {tid} does not exist in the graph.", [tid]))
    task = tasks[tid]
    if inp["task_contract"]["task_id"] != tid:
        return _empty_envelope(inp, "invalid", _diag("PC-TASK-CONTRACT-MISMATCH", "task_contract.task_id does not match requested compiled task.", [inp["task_contract"]["task_id"], tid]))

    context_ids = [x["context_id"] for x in inp["context_records"]]
    duplicates = sorted({x for x in context_ids if context_ids.count(x) > 1})
    if duplicates:
        return _empty_envelope(inp, "invalid", _diag("PC-CONTEXT-DUPLICATE", "Duplicate context_id values are not permitted.", duplicates))

    replay = replay_task_events(graph_hash=graph["graph_hash"], task_ids=list(tasks), events=inp["execution_events"], root=r)
    if not replay["ok"]:
        refs = [d["code"] for d in replay["diagnostics"]]
        return _empty_envelope(inp, "invalid", _diag("PC-EXECUTION-INVALID", "Task execution history failed parent replay validation.", refs))

    included, excluded, unbound = _context_closure(inp, task, tasks, order)
    if unbound:
        return _empty_envelope(inp, "blocked", _diag("PC-CONTEXT-CLOSURE-UNPROVEN", "Critical context lacks selectors proving safe inclusion or exclusion.", unbound))

    kind = inp["prompt_kind"]
    contract = inp["task_contract"]
    prereqs = _transitive_prereqs(tid, tasks, order)
    states = replay["final_states"]
    prereq_states = [{"task_id": pid, "state": states.get(pid)} for pid in prereqs]
    task_state = states.get(tid)

    if kind in {"implementation", "debug"} and contract["blocking_owner_decision_ids"]:
        return _empty_envelope(inp, "blocked", _diag("PC-OWNER-DECISION", "Unresolved owner decisions block executable task authority.", contract["blocking_owner_decision_ids"]))

    if kind in {"implementation", "debug"}:
        incomplete = [x["task_id"] for x in prereq_states if x["state"] != "done"]
        if incomplete:
            return _empty_envelope(inp, "blocked", _diag("PC-PREREQUISITE-INCOMPLETE", "Every transitive prerequisite must be done before executable task authority is emitted.", incomplete))
        if any(scope not in task["write_scopes"] for scope in inp["requested_write_scopes"]):
            extra = [scope for scope in inp["requested_write_scopes"] if scope not in task["write_scopes"]]
            return _empty_envelope(inp, "blocked", _diag("PC-SCOPE-EXPANSION", "Requested write scope exceeds the compiled task declaration.", extra))

    if kind == "implementation" and task_state not in {"ready", "in_progress"}:
        return _empty_envelope(inp, "blocked", _diag("PC-TASK-NOT-READY", "Implementation prompt requires task state ready or in_progress.", [str(task_state)]))
    if kind == "debug":
        if task_state not in {"in_progress", "blocked"}:
            return _empty_envelope(inp, "blocked", _diag("PC-TASK-NOT-DEBUGGABLE", "Debug prompt requires task state in_progress or blocked.", [str(task_state)]))
        if not inp["debug_evidence_refs"]:
            return _empty_envelope(inp, "blocked", _diag("PC-DEBUG-EVIDENCE-MISSING", "Debug prompt requires observed defect evidence."))
    if kind == "verification":
        if inp["actor_context"]["requested_actor_id"] == inp["actor_context"]["implementation_actor_id"]:
            return _empty_envelope(inp, "blocked", _diag("PC-VERIFIER-SELF-CERTIFICATION", "Verification actor must differ from implementation actor.", [inp["actor_context"]["requested_actor_id"]]))
        if task_state != "done":
            return _empty_envelope(inp, "blocked", _diag("PC-TASK-NOT-DONE", "Verification prompt requires replayed task state done.", [str(task_state)]))

    allowed = sorted(inp["requested_write_scopes"] or task["write_scopes"]) if kind in {"implementation", "debug"} else []
    completed = sorted({ref for event in inp["execution_events"] if event.get("task_id") == tid and event.get("to_state") == "done" for ref in event.get("evidence_refs", [])})
    blockers: list[str] = []
    if task_state == "blocked":
        blockers = sorted({event["reason"] for event in inp["execution_events"] if event.get("task_id") == tid and event.get("to_state") == "blocked" and event.get("reason")})
    frozen = sorted(contract["frozen_criteria_refs"])
    source_evidence = sorted(set(included) | set(task["source_requirement_ids"]) | set(task["verification_refs"]) | set(task["gate_ids"]) | set(frozen))

    env: dict[str, Any] = {
        "schema_version": "1.0",
        "request_id": inp["request_id"],
        "status": "compiled",
        "candidate_version": inp["candidate_version"],
        "graph_hash": graph["graph_hash"],
        "task_id": tid,
        "prompt_kind": kind,
        "actor_role": ROLE[kind],
        "declared_write_scopes": sorted(task["write_scopes"]),
        "allowed_write_scopes": allowed,
        "prerequisite_states": prereq_states,
        "source_requirement_ids": sorted(task["source_requirement_ids"]),
        "acceptance_criteria": sorted(contract["acceptance_criteria"]),
        "verification_refs": sorted(task["verification_refs"]),
        "gate_ids": sorted(task["gate_ids"]),
        "frozen_criteria_refs": frozen,
        "critical_obligations": sorted(contract["critical_obligations"]),
        "evidence_requirements": sorted(contract["evidence_requirements"]),
        "source_evidence_refs": source_evidence,
        "included_context_refs": included,
        "excluded_context_refs": excluded,
        "task_state": task_state,
        "completed_evidence_refs": completed,
        "open_blockers": blockers,
        "next_permitted_action": NEXT_ACTION[task_state],
        "completion_constraints": sorted(BASE_CONSTRAINTS + [KIND_CONSTRAINT[kind]]),
        "diagnostics": [],
        "prompt_text": None,
        "envelope_hash": "",
    }
    env["prompt_text"] = _render_prompt(env)
    env["envelope_hash"] = _canonical_hash(env, exclude={"envelope_hash"})
    return env


def compile_prompt_file(path: str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return _empty_envelope({}, "invalid", _diag("PC-INPUT-JSON", f"Cannot parse prompt compilation input JSON: {exc}"))
    return compile_prompt(obj, root=root)
