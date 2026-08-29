from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import json

from jsonschema import Draft202012Validator


NODE_TYPES = ("goal", "requirement", "feature", "task", "test", "gate")
PRIMARY_RELATIONS: dict[tuple[str, str, str], str] = {
    ("goal", "requires", "requirement"): "requires",
    ("requirement", "realized_by", "feature"): "realized_by",
    ("feature", "decomposed_to", "task"): "decomposed_to",
    ("task", "verified_by", "test"): "verified_by",
    ("test", "gated_by", "gate"): "gated_by",
}
AUXILIARY_RELATIONS: dict[tuple[str, str, str], str] = {
    ("task", "precedes", "task"): "precedes",
    ("feature", "precedes", "feature"): "precedes",
}
ALLOWED_RELATIONS = {**PRIMARY_RELATIONS, **AUXILIARY_RELATIONS}


@dataclass(frozen=True, order=True)
class TraceDiagnostic:
    code: str
    message: str
    node_id: str | None = None
    edge_index: int | None = None
    severity: str = "error"

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }
        if self.node_id is not None:
            out["node_id"] = self.node_id
        if self.edge_index is not None:
            out["edge_index"] = self.edge_index
        return out


@dataclass(frozen=True)
class TraceabilityGraph:
    graph_id: str
    schema_version: str
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, str], ...]

    @property
    def node_by_id(self) -> dict[str, dict[str, Any]]:
        # Duplicate IDs are intentionally collapsed here only after duplicate
        # detection has happened. First declaration wins deterministically.
        out: dict[str, dict[str, Any]] = {}
        for node in self.nodes:
            out.setdefault(node["id"], node)
        return out


@dataclass
class TraceabilityReport:
    graph_id: str | None
    diagnostics: list[TraceDiagnostic] = field(default_factory=list)
    critical_requirements_total: int = 0
    critical_requirements_complete: int = 0
    complete_paths: dict[str, list[list[str]]] = field(default_factory=dict)

    @property
    def errors(self) -> list[TraceDiagnostic]:
        return [d for d in self.diagnostics if d.severity == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def critical_traceability_coverage_rate(self) -> float | None:
        if self.critical_requirements_total == 0:
            return None
        return self.critical_requirements_complete / self.critical_requirements_total

    def as_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "ok": self.ok,
            "summary": {
                "errors": len(self.errors),
                "diagnostics": len(self.diagnostics),
                "critical_requirements_total": self.critical_requirements_total,
                "critical_requirements_complete": self.critical_requirements_complete,
                "critical_traceability_coverage_rate": self.critical_traceability_coverage_rate,
            },
            "diagnostics": [d.as_dict() for d in sorted(self.diagnostics)],
            "complete_paths": {k: v for k, v in sorted(self.complete_paths.items())},
        }


@dataclass(frozen=True)
class ImpactReport:
    graph_id: str
    seed_ids: tuple[str, ...]
    upstream: tuple[str, ...]
    downstream: tuple[str, ...]
    diagnostics: tuple[TraceDiagnostic, ...] = ()

    @property
    def ok(self) -> bool:
        return not any(d.severity == "error" for d in self.diagnostics)

    def as_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "ok": self.ok,
            "seed_ids": list(self.seed_ids),
            "upstream": list(self.upstream),
            "downstream": list(self.downstream),
            "diagnostics": [d.as_dict() for d in sorted(self.diagnostics)],
        }


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "traceability-graph-v1.schema.json"


def _schema_diagnostics(obj: Any) -> list[TraceDiagnostic]:
    try:
        schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    except Exception as exc:
        return [TraceDiagnostic("TRACE-SCHEMA-LOAD", f"Cannot load traceability schema: {exc}")]
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.absolute_path))
    return [
        TraceDiagnostic(
            "TRACE-SCHEMA",
            f"{'.'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}",
        )
        for err in errors
    ]


def parse_graph(obj: dict[str, Any]) -> TraceabilityGraph:
    diagnostics = _schema_diagnostics(obj)
    if diagnostics:
        raise ValueError("; ".join(d.message for d in diagnostics))
    # Preserve declaration order in the stored graph. Derived outputs are
    # explicitly sorted so JSON output is deterministic.
    return TraceabilityGraph(
        graph_id=obj["graph_id"],
        schema_version=obj["schema_version"],
        nodes=tuple(dict(n) for n in obj["nodes"]),
        edges=tuple({"from": e["from"], "relation": e["relation"], "to": e["to"]} for e in obj["edges"]),
    )


def load_graph(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _structural_diagnostics(graph: TraceabilityGraph) -> list[TraceDiagnostic]:
    out: list[TraceDiagnostic] = []
    node_seen: set[str] = set()
    for node in graph.nodes:
        nid = node["id"]
        if nid in node_seen:
            out.append(TraceDiagnostic("TRACE-DUPLICATE-NODE", f"Duplicate node ID: {nid}", node_id=nid))
        node_seen.add(nid)

    edge_seen: set[tuple[str, str, str]] = set()
    for idx, edge in enumerate(graph.edges):
        key = (edge["from"], edge["relation"], edge["to"])
        if key in edge_seen:
            out.append(TraceDiagnostic("TRACE-DUPLICATE-EDGE", f"Duplicate directed edge: {key[0]} -[{key[1]}]-> {key[2]}", edge_index=idx))
        edge_seen.add(key)

    # Stop reference/type reasoning from generating cascades when duplicate
    # identities already make the graph ambiguous.
    if out:
        return sorted(out)

    nodes = graph.node_by_id
    broken = False
    for idx, edge in enumerate(graph.edges):
        missing = [nid for nid in (edge["from"], edge["to"]) if nid not in nodes]
        if missing:
            broken = True
            out.append(TraceDiagnostic(
                "TRACE-BROKEN-REFERENCE",
                f"Edge references missing node(s): {', '.join(sorted(missing))}",
                node_id=sorted(missing)[0],
                edge_index=idx,
            ))
    if broken:
        return sorted(out)

    for idx, edge in enumerate(graph.edges):
        src_t = nodes[edge["from"]]["type"]
        dst_t = nodes[edge["to"]]["type"]
        triple = (src_t, edge["relation"], dst_t)
        if triple not in ALLOWED_RELATIONS:
            out.append(TraceDiagnostic(
                "TRACE-INVALID-TRANSITION",
                f"Invalid transition {src_t} -[{edge['relation']}]-> {dst_t}",
                node_id=edge["from"],
                edge_index=idx,
            ))
    if out:
        return sorted(out)

    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        adjacency[edge["from"]].append(edge["to"])
    for values in adjacency.values():
        values.sort()

    state: dict[str, int] = {nid: 0 for nid in nodes}
    stack: list[str] = []
    cycle_nodes: set[str] = set()

    def dfs(nid: str) -> bool:
        state[nid] = 1
        stack.append(nid)
        for nxt in adjacency.get(nid, []):
            if state[nxt] == 0:
                if dfs(nxt):
                    return True
            elif state[nxt] == 1:
                start = stack.index(nxt)
                cycle_nodes.update(stack[start:])
                cycle_nodes.add(nxt)
                return True
        stack.pop()
        state[nid] = 2
        return False

    for nid in sorted(nodes):
        if state[nid] == 0 and dfs(nid):
            out.append(TraceDiagnostic(
                "TRACE-CYCLE",
                f"Directed cycle detected involving: {', '.join(sorted(cycle_nodes))}",
                node_id=sorted(cycle_nodes)[0] if cycle_nodes else nid,
            ))
            break
    return sorted(out)


def _primary_targets(graph: TraceabilityGraph) -> dict[tuple[str, str], list[str]]:
    nodes = graph.node_by_id
    out: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in graph.edges:
        if edge["from"] not in nodes or edge["to"] not in nodes:
            continue
        triple = (nodes[edge["from"]]["type"], edge["relation"], nodes[edge["to"]]["type"])
        if triple in PRIMARY_RELATIONS:
            out[(edge["from"], edge["relation"])].append(edge["to"])
    for values in out.values():
        values.sort()
    return out


def _complete_paths_for_requirement(graph: TraceabilityGraph, req_id: str) -> tuple[list[list[str]], TraceDiagnostic | None]:
    targets = _primary_targets(graph)
    nodes = graph.node_by_id
    incoming_goals = sorted(
        e["from"] for e in graph.edges
        if e["relation"] == "requires" and e["to"] == req_id and e["from"] in nodes and nodes[e["from"]]["type"] == "goal"
    )
    if not incoming_goals:
        return [], TraceDiagnostic("TRACE-MISSING-UPSTREAM-GOAL", f"Critical requirement {req_id} has no upstream goal.", node_id=req_id)

    stages = [
        ("realized_by", "feature", "TRACE-MISSING-FEATURE"),
        ("decomposed_to", "task", "TRACE-MISSING-TASK"),
        ("verified_by", "test", "TRACE-MISSING-TEST"),
        ("gated_by", "gate", "TRACE-MISSING-GATE"),
    ]
    partials: list[list[str]] = [[req_id]]
    for relation, stage_name, code in stages:
        next_partials: list[list[str]] = []
        for path in partials:
            for target in targets.get((path[-1], relation), []):
                next_partials.append(path + [target])
        if not next_partials:
            return [], TraceDiagnostic(code, f"Critical requirement {req_id} has no complete {stage_name} stage.", node_id=req_id)
        partials = next_partials

    complete: list[list[str]] = []
    for goal in incoming_goals:
        for downstream in partials:
            complete.append([goal] + downstream)
    complete.sort()
    return complete, None


def validate_graph(obj: dict[str, Any] | TraceabilityGraph) -> TraceabilityReport:
    if isinstance(obj, TraceabilityGraph):
        graph = obj
        schema_diags: list[TraceDiagnostic] = []
    else:
        schema_diags = _schema_diagnostics(obj)
        graph_id = obj.get("graph_id") if isinstance(obj, dict) else None
        if schema_diags:
            return TraceabilityReport(graph_id=graph_id, diagnostics=schema_diags)
        graph = parse_graph(obj)

    report = TraceabilityReport(graph_id=graph.graph_id)
    structural = _structural_diagnostics(graph)
    if structural:
        report.diagnostics.extend(structural)
        return report

    critical = sorted(
        n["id"] for n in graph.nodes
        if n.get("type") == "requirement" and n.get("critical") is True
    )
    report.critical_requirements_total = len(critical)
    for req_id in critical:
        paths, diagnostic = _complete_paths_for_requirement(graph, req_id)
        if diagnostic:
            report.diagnostics.append(diagnostic)
        else:
            report.critical_requirements_complete += 1
            report.complete_paths[req_id] = paths
    report.diagnostics.sort()
    return report


def _closure(seed_ids: Iterable[str], adjacency: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set(seed_ids)
    q = deque(sorted(seed_ids))
    result: set[str] = set()
    while q:
        current = q.popleft()
        for nxt in adjacency.get(current, []):
            if nxt in seen:
                continue
            seen.add(nxt)
            result.add(nxt)
            q.append(nxt)
    return result


def analyze_impact(obj: dict[str, Any] | TraceabilityGraph, seed_ids: Iterable[str]) -> ImpactReport:
    graph = obj if isinstance(obj, TraceabilityGraph) else parse_graph(obj)
    validation = validate_graph(graph)
    if not validation.ok:
        return ImpactReport(graph.graph_id, tuple(sorted(set(seed_ids))), (), (), tuple(validation.errors))

    seeds = tuple(sorted(set(seed_ids)))
    nodes = graph.node_by_id
    unknown = sorted(set(seeds) - set(nodes))
    if unknown:
        diagnostics = tuple(
            TraceDiagnostic("TRACE-UNKNOWN-SEED", f"Impact seed node does not exist: {nid}", node_id=nid)
            for nid in unknown
        )
        return ImpactReport(graph.graph_id, seeds, (), (), diagnostics)

    forward: dict[str, list[str]] = defaultdict(list)
    reverse: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        forward[edge["from"]].append(edge["to"])
        reverse[edge["to"]].append(edge["from"])
    for mapping in (forward, reverse):
        for values in mapping.values():
            values.sort()

    rank = {node_type: idx for idx, node_type in enumerate(NODE_TYPES)}
    def impact_order(nid: str) -> tuple[int, str]:
        return (rank[nodes[nid]["type"]], nid)

    downstream = tuple(sorted(_closure(seeds, forward), key=impact_order))
    upstream = tuple(sorted(_closure(seeds, reverse), key=impact_order))
    # A seed is never part of its own impact set, even if multiple seeds reach
    # each other through a valid auxiliary relation. Output order follows the
    # governed Goal→Requirement→Feature→Task→Test→Gate chain, then stable ID.
    downstream = tuple(x for x in downstream if x not in seeds)
    upstream = tuple(x for x in upstream if x not in seeds)
    return ImpactReport(graph.graph_id, seeds, upstream, downstream)
