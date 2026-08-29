from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import copy
import hashlib
import json

from jsonschema import Draft202012Validator, FormatChecker

from .linter import lint_text
from .ambiguity import analyze_ambiguity
from .traceability import validate_graph

BLOCKING_DISCOVERY_ACTIONS = {"ask_now", "defer_dependency", "defer_budget"}


def _canonical_hash(obj: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    data = copy.deepcopy(obj)
    for key in exclude or set():
        data.pop(key, None)
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _compiled_id(source_task_id: str) -> str:
    return "CTASK-" + source_task_id[5:]


def _empty_result(project_id: str, status: str, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    out = {
        "schema_version": "1.0",
        "project_id": project_id,
        "status": status,
        "tasks": [],
        "conflict_zones": [],
        "diagnostics": diagnostics,
        "summary": {
            "task_count": 0,
            "dependency_edge_count": 0,
            "conflict_zone_count": 0,
            "blocking_diagnostic_count": len(diagnostics),
        },
        "graph_hash": "",
    }
    out["graph_hash"] = _canonical_hash(out, exclude={"graph_hash"})
    return out


def _diag(code: str, message: str, *, source_task_ids: list[str] | None = None, source_refs: list[str] | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"code": code, "message": message}
    if source_task_ids is not None:
        d["source_task_ids"] = sorted(source_task_ids)
    if source_refs is not None:
        d["source_refs"] = sorted(source_refs)
    return d


def _load_schema(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / "schemas" / name).read_text(encoding="utf-8"))


def validate_compilation_project(project: dict[str, Any], *, root: str | Path | None = None) -> list[dict[str, Any]]:
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = Path(root)
    schema = _load_schema(root, "task-compilation-project-v1.schema.json")
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    out = []
    for err in sorted(v.iter_errors(project), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(x) for x in err.absolute_path) or "<root>"
        out.append(_diag("TC-INPUT-SCHEMA", f"{where}: {err.message}"))
    return out


def validate_compiled_graph(graph: dict[str, Any], *, root: str | Path | None = None) -> list[dict[str, Any]]:
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = Path(root)
    schema = _load_schema(root, "compiled-task-graph-v1.schema.json")
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    out = []
    for err in sorted(v.iter_errors(graph), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(x) for x in err.absolute_path) or "<root>"
        out.append(_diag("TC-OUTPUT-SCHEMA", f"{where}: {err.message}"))
    if not out and graph.get("graph_hash") != _canonical_hash(graph, exclude={"graph_hash"}):
        out.append(_diag("TC-GRAPH-HASH", "Compiled task graph hash does not match canonical content."))
    return out


def _graph_indexes(graph: dict[str, Any]):
    types = {n["id"]: n["type"] for n in graph["nodes"]}
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in graph["edges"]:
        outgoing[e["from"]].append(e)
        incoming[e["to"]].append(e)
    return types, incoming, outgoing


def _cycle_nodes(nodes: list[str], deps: set[tuple[str, str]]) -> list[str]:
    adjacency = {n: [] for n in nodes}
    for a, b in deps:
        if a in adjacency and b in adjacency:
            adjacency[a].append(b)
    for values in adjacency.values():
        values.sort()

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    cyclic: set[str] = set()

    def visit(v: str) -> None:
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in adjacency[v]:
            if w not in indices:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)
                if w == v:
                    break
            if len(component) > 1 or (len(component) == 1 and component[0] in adjacency[component[0]]):
                cyclic.update(component)

    for n in sorted(nodes):
        if n not in indices:
            visit(n)
    return sorted(cyclic)


def _topological(nodes: list[str], deps: set[tuple[str, str]]) -> list[str]:
    indegree = {n: 0 for n in nodes}
    adjacency: dict[str, set[str]] = defaultdict(set)
    for a, b in deps:
        if b not in adjacency[a]:
            adjacency[a].add(b)
            indegree[b] += 1
    ready = sorted(n for n in nodes if indegree[n] == 0)
    out: list[str] = []
    while ready:
        n = ready.pop(0)
        out.append(n)
        for child in sorted(adjacency[n]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
                ready.sort()
    return out


def _reachability(nodes: list[str], deps: set[tuple[str, str]]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for a, b in deps:
        adjacency[a].add(b)
    out: dict[str, set[str]] = {}
    for n in nodes:
        stack = list(adjacency[n])
        seen: set[str] = set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adjacency[x])
        out[n] = seen
    return out


def compile_project(project: dict[str, Any], *, root: str | Path | None = None) -> dict[str, Any]:
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = Path(root)
    project_id = project.get("project_id", "TCP-INVALID") if isinstance(project, dict) else "TCP-INVALID"
    if not isinstance(project, dict):
        return _empty_result(project_id, "invalid", [_diag("TC-INPUT-SCHEMA", "Input must be a JSON object.")])

    schema_diagnostics = validate_compilation_project(project, root=root)
    if schema_diagnostics:
        return _empty_result(project_id, "invalid", schema_diagnostics)

    lint = lint_text(project["spec_text"])
    if not lint.ok:
        refs = [f"LINT:{f.rule_id}:{f.line}" for f in lint.unsuppressed]
        return _empty_result(project_id, "invalid", [_diag("TC-SPEC-LINT", "Active specification linter rejected the source specification.", source_refs=refs)])

    trace_report = validate_graph(project["traceability_graph"])
    if not trace_report.ok:
        refs = [d.code for d in trace_report.errors]
        return _empty_result(project_id, "invalid", [_diag("TC-TRACE-INVALID", "Parent traceability validator rejected the supplied graph.", source_refs=refs)])

    actions = project["discovery_plan"].get("actions", [])
    action_ids = [a.get("candidate_id") for a in actions]
    duplicate_action_ids = sorted({x for x in action_ids if isinstance(x, str) and action_ids.count(x) > 1})
    if duplicate_action_ids:
        return _empty_result(project_id, "invalid", [_diag("TC-DISCOVERY-ACTION-DUPLICATE", "Discovery plan contains duplicate candidate actions.", source_refs=duplicate_action_ids)])

    # Reconcile the supplied plan against the parent ambiguity engine so a stale
    # or truncated plan cannot hide a real owner decision. Safe inferred defaults
    # may resolve a candidate, but every decision-needed parent finding must still
    # be represented by its stable candidate ID in the supplied plan.
    ambiguity = analyze_ambiguity(project["spec_text"])
    by_candidate = {a.get("candidate_id"): a for a in actions if isinstance(a.get("candidate_id"), str)}
    missing_candidates: list[str] = []
    invalid_resolutions: list[str] = []
    for finding in ambiguity.findings:
        if not finding.decision_needed:
            continue
        candidate_id = f"{finding.block_id}:{finding.code}:{finding.line}"
        action = by_candidate.get(candidate_id)
        if action is None:
            missing_candidates.append(candidate_id)
        elif action.get("action") == "already_governed":
            invalid_resolutions.append(candidate_id)
    if missing_candidates or invalid_resolutions:
        refs = sorted(set(missing_candidates + invalid_resolutions))
        return _empty_result(project_id, "blocked", [_diag("TC-DISCOVERY-PLAN-INCOMPLETE", "Supplied discovery plan does not account for every decision-needed parent ambiguity finding.", source_refs=refs)])

    blocking = sorted(
        a["candidate_id"]
        for a in actions
        if a.get("action") in BLOCKING_DISCOVERY_ACTIONS
    )
    if blocking:
        d = _diag("TC-OWNER-DECISION", "Unresolved discovery actions block implementation-ready compilation.", source_refs=blocking)
        d["blocking_action_ids"] = blocking
        return _empty_result(project_id, "blocked", [d])

    graph = project["traceability_graph"]
    types, incoming, outgoing = _graph_indexes(graph)
    source_tasks = sorted(n["id"] for n in graph["nodes"] if n["type"] == "task")
    metadata_ids = [m["source_task_id"] for m in project["task_metadata"]]
    duplicate_metadata_ids = sorted({x for x in metadata_ids if metadata_ids.count(x) > 1})
    if duplicate_metadata_ids:
        return _empty_result(project_id, "invalid", [_diag("TC-METADATA-DUPLICATE", "Task metadata contains duplicate source_task_id records; no record may silently overwrite another.", source_task_ids=duplicate_metadata_ids)])
    metadata = {m["source_task_id"]: m for m in project["task_metadata"]}

    missing_meta = sorted(set(source_tasks) - set(metadata))
    extra_meta = sorted(set(metadata) - set(source_tasks))
    if missing_meta or extra_meta:
        refs = [f"missing:{x}" for x in missing_meta] + [f"extra:{x}" for x in extra_meta]
        return _empty_result(project_id, "invalid", [_diag("TC-METADATA-MISSING", "Task metadata must correspond exactly to trace task nodes.", source_task_ids=missing_meta + extra_meta, source_refs=refs)])

    reqs_by_task: dict[str, list[str]] = {}
    tests_by_task: dict[str, list[str]] = {}
    gates_by_task: dict[str, list[str]] = {}
    for tid in source_tasks:
        features = sorted(e["from"] for e in incoming[tid] if e["relation"] == "decomposed_to" and types.get(e["from"]) == "feature")
        reqs = sorted({e["from"] for f in features for e in incoming[f] if e["relation"] == "realized_by" and types.get(e["from"]) == "requirement"})
        tests = sorted({e["to"] for e in outgoing[tid] if e["relation"] == "verified_by" and types.get(e["to"]) == "test"})
        gates = sorted({e["to"] for test in tests for e in outgoing[test] if e["relation"] == "gated_by" and types.get(e["to"]) == "gate"})
        reqs_by_task[tid] = reqs
        tests_by_task[tid] = tests
        gates_by_task[tid] = gates

    critical_reqs = sorted(n["id"] for n in graph["nodes"] if n["type"] == "requirement" and n.get("critical"))
    covered = {r for rs in reqs_by_task.values() for r in rs}
    missing_critical = sorted(set(critical_reqs) - covered)
    tasks_without_verification = sorted(t for t in source_tasks if not tests_by_task[t] or not gates_by_task[t])
    if missing_critical or tasks_without_verification:
        refs = [f"uncovered:{r}" for r in missing_critical] + [f"missing_test_or_gate:{t}" for t in tasks_without_verification]
        return _empty_result(project_id, "invalid", [_diag("TC-CRITICAL-COVERAGE", "Critical requirement-to-task-test-gate coverage is incomplete.", source_task_ids=tasks_without_verification, source_refs=refs)])

    dep_reasons: dict[tuple[str, str], set[str]] = defaultdict(set)
    for e in graph["edges"]:
        if e["relation"] == "precedes" and types.get(e["from"]) == "task" and types.get(e["to"]) == "task":
            dep_reasons[(e["from"], e["to"])].add(f"trace:{e['from']}:precedes:{e['to']}")
    for o in project["ordering_constraints"]:
        a, b = o["before_task_id"], o["after_task_id"]
        if a not in metadata or b not in metadata:
            return _empty_result(project_id, "invalid", [_diag("TC-ORDER-REFERENCE", "Ordering constraint references a task outside the validated task set.", source_task_ids=[a, b], source_refs=[o["source_ref"]])])
        dep_reasons[(a, b)].add("order:" + o["source_ref"])

    producers: dict[str, list[str]] = defaultdict(list)
    for tid, meta in metadata.items():
        for artifact in meta["produces_artifacts"]:
            producers[artifact].append(tid)
    ambiguous_artifacts = sorted(a for a, tids in producers.items() if len(tids) > 1)
    if ambiguous_artifacts:
        refs = [f"artifact:{a}:producers={','.join(sorted(producers[a]))}" for a in ambiguous_artifacts]
        return _empty_result(project_id, "invalid", [_diag("TC-ARTIFACT-PRODUCER-AMBIGUOUS", "Consumed artifact producer must be unique.", source_refs=refs)])
    for tid, meta in metadata.items():
        for artifact in meta["consumes_artifacts"]:
            prod = producers.get(artifact, [])
            if len(prod) == 1 and prod[0] != tid:
                dep_reasons[(prod[0], tid)].add(f"artifact:{artifact}:producer={prod[0]}:consumer={tid}")

    deps = set(dep_reasons)
    cycles = _cycle_nodes(source_tasks, deps)
    if cycles:
        return _empty_result(project_id, "invalid", [_diag("TC-DEPENDENCY-CYCLE", "Combined task dependency graph contains a cycle.", source_task_ids=cycles)])

    prereqs: dict[str, set[str]] = defaultdict(set)
    for a, b in deps:
        prereqs[b].add(a)

    atomic_codes: set[str] = set()
    atomic_task_refs: dict[str, list[str]] = defaultdict(list)
    for tid in source_tasks:
        meta = metadata[tid]
        req_count = len(reqs_by_task[tid])
        write_count = len(meta["write_scopes"])
        prereq_count = len(prereqs[tid])
        verify_count = len(tests_by_task[tid])
        score = 3 * req_count + 2 * write_count + prereq_count + verify_count
        if req_count > 3:
            atomic_codes.add("TC-ATOMIC-REQUIREMENT-LIMIT")
            atomic_task_refs["TC-ATOMIC-REQUIREMENT-LIMIT"].append(tid)
        if write_count > 2 and not meta.get("wide_scope_authorization_ref"):
            atomic_codes.add("TC-ATOMIC-WRITE-LIMIT")
            atomic_task_refs["TC-ATOMIC-WRITE-LIMIT"].append(tid)
        if verify_count == 0:
            atomic_codes.add("TC-ATOMIC-NO-VERIFICATION")
            atomic_task_refs["TC-ATOMIC-NO-VERIFICATION"].append(tid)
        if score > 10:
            atomic_codes.add("TC-ATOMIC-COMPLEXITY")
            atomic_task_refs["TC-ATOMIC-COMPLEXITY"].append(tid)
    if atomic_codes:
        diagnostics = [_diag(code, "Source task violates frozen v0.08 atomicity bounds; specification refinement is required.", source_task_ids=atomic_task_refs[code]) for code in sorted(atomic_codes)]
        return _empty_result(project_id, "needs_spec_refinement", diagnostics)

    topo = _topological(source_tasks, deps)
    reach = _reachability(source_tasks, deps)

    scope_tasks: dict[str, list[str]] = defaultdict(list)
    for tid in source_tasks:
        for scope in metadata[tid]["write_scopes"]:
            scope_tasks[scope].append(tid)
    shared_scopes = sorted((scope, sorted(tids)) for scope, tids in scope_tasks.items() if len(tids) >= 2)
    zone_by_scope = {scope: f"CZ-{i:03d}" for i, (scope, _) in enumerate(shared_scopes, 1)}
    zones = [
        {"conflict_zone_id": zone_by_scope[scope], "write_scope": scope, "task_ids": [_compiled_id(t) for t in tids]}
        for scope, tids in shared_scopes
    ]

    tasks: list[dict[str, Any]] = []
    for tid in topo:
        meta = metadata[tid]
        reqs = reqs_by_task[tid]
        tests = tests_by_task[tid]
        gates = gates_by_task[tid]
        conflict_ids = sorted(zone_by_scope[s] for s in meta["write_scopes"] if s in zone_by_scope)
        parallel_with: list[str] = []
        for other in source_tasks:
            if other == tid:
                continue
            dependency_path = other in reach[tid] or tid in reach[other]
            write_conflict = bool(set(meta["write_scopes"]) & set(metadata[other]["write_scopes"]))
            if not dependency_path and not write_conflict:
                parallel_with.append(_compiled_id(other))

        req_prov: list[str] = []
        for req in reqs:
            features = sorted(
                e["to"] for e in outgoing[req]
                if e["relation"] == "realized_by"
                and any(x["relation"] == "decomposed_to" and x["to"] == tid for x in outgoing[e["to"]])
            )
            for feature in features:
                req_prov.append(f"trace:{req}:realized_by:{feature}:decomposed_to:{tid}")
        dep_prov: list[str] = []
        for p in sorted(prereqs[tid]):
            dep_prov.extend(sorted(dep_reasons[(p, tid)]))
        gate_prov = sorted(
            f"trace:{test}:gated_by:{gate}"
            for test in tests for gate in gates
            if any(e["relation"] == "gated_by" and e["to"] == gate for e in outgoing[test])
        )
        factors = {
            "source_requirement_count": len(reqs),
            "write_scope_count": len(meta["write_scopes"]),
            "prerequisite_count": len(prereqs[tid]),
            "verification_reference_count": len(tests),
        }
        score = 3 * factors["source_requirement_count"] + 2 * factors["write_scope_count"] + factors["prerequisite_count"] + factors["verification_reference_count"]
        tasks.append({
            "task_id": _compiled_id(tid),
            "source_task_id": tid,
            "source_requirement_ids": reqs,
            "write_scopes": sorted(meta["write_scopes"]),
            "read_scopes": sorted(meta["read_scopes"]),
            "produced_artifacts": sorted(meta["produces_artifacts"]),
            "consumed_artifacts": sorted(meta["consumes_artifacts"]),
            "prerequisite_task_ids": [_compiled_id(x) for x in sorted(prereqs[tid])],
            "verification_refs": tests,
            "gate_ids": gates,
            "conflict_zone_ids": conflict_ids,
            "parallel_with": sorted(parallel_with),
            "complexity_score": score,
            "complexity_factors": factors,
            "provenance": {
                "source_requirement_ids": sorted(req_prov),
                "write_scopes": [f"task_metadata:{tid}.write_scopes"],
                "read_scopes": [f"task_metadata:{tid}.read_scopes"],
                "produced_artifacts": [f"task_metadata:{tid}.produces_artifacts"],
                "consumed_artifacts": [f"task_metadata:{tid}.consumes_artifacts"],
                "prerequisite_task_ids": sorted(dep_prov),
                "verification_refs": [f"trace:{tid}:verified_by:{x}" for x in tests],
                "gate_ids": gate_prov,
                "conflict_zone_ids": sorted(f"write_scope:{s}" for s in meta["write_scopes"] if s in zone_by_scope),
                "parallel_with": ["rule:no_dependency_path_and_no_shared_write_scope"],
                "complexity_score": ["formula:v0.08"],
            },
        })

    result = {
        "schema_version": "1.0",
        "project_id": project_id,
        "status": "compiled",
        "tasks": tasks,
        "conflict_zones": zones,
        "diagnostics": [],
        "summary": {
            "task_count": len(tasks),
            "dependency_edge_count": len(deps),
            "conflict_zone_count": len(zones),
            "blocking_diagnostic_count": 0,
        },
        "graph_hash": "",
    }
    result["graph_hash"] = _canonical_hash(result, exclude={"graph_hash"})
    output_errors = validate_compiled_graph(result, root=root)
    if output_errors:
        return _empty_result(project_id, "invalid", output_errors)
    return result


def compile_project_file(path: str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return _empty_result("TCP-INVALID", "invalid", [_diag("TC-INPUT-JSON", f"Cannot parse compilation project: {exc}")])
    return compile_project(obj, root=root)
