from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import re

from .linter import _blocks, _field, _scan_lines, Block, LineInfo
from .traceability import analyze_impact, validate_graph

UNBOUNDED_TERMS = ("quickly", "soon", "large", "small", "recent", "significant", "substantial", "minimal")
UNRESOLVED_MARKERS = ("TBD", "TODO", "pending", "unresolved", "undecided")


def _unresolved_marker_match(text: str, marker: str):
    """Return a semantic unresolved-marker match, avoiding ordinary adjective uses.

    ``pending`` is overloaded in implementation prose (for example, "zero pending
    records"). Treat it as an ambiguity marker only when it functions as unresolved
    status or modifies a decision-like noun. Other preregistered markers remain
    unambiguous status tokens.
    """
    m = re.search(rf"\b{re.escape(marker)}\b", text, re.I)
    if not m or marker.lower() != "pending":
        return m
    before = text[:m.start()]
    after = text[m.end():]
    status_before = re.search(r"\b(?:is|remains|still|status\s*[:=]?)\s*$", before, re.I)
    terminal = re.match(r"\s*(?:[.,;:]|$)", after)
    decision_noun = re.match(r"\s+(?:decision|choice|approval|resolution|determination|selection)\b", after, re.I)
    return m if (status_before or terminal or decision_noun) else None
REFERENT_PREFIX = re.compile(r"^\s*(It|This|They|Those)\b", re.I)
APPROVED_DEC = re.compile(r"\[approved\s+(DEC-[A-Za-z0-9._-]+)\]", re.I)
KEY_VALUE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_.-]*)\s*=\s*(.+?)\s*$")
INTERFACE = re.compile(r"^\s*Interface:\s*([A-Za-z][A-Za-z0-9_.-]*)\s*$", re.I)

SEVERITY_WEIGHT = {"high": 300, "medium": 200, "low": 100}


@dataclass(frozen=True)
class AmbiguityFinding:
    code: str
    block_id: str
    block_kind: str
    line: int
    column: int
    span: str
    category: str
    severity: str
    disposition: str
    decision_needed: bool
    critical: bool
    downstream_impact_count: int = 0
    priority_score: int = 0
    question: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {
            "code": self.code,
            "block_id": self.block_id,
            "block_kind": self.block_kind,
            "line": self.line,
            "column": self.column,
            "span": self.span,
            "category": self.category,
            "severity": self.severity,
            "disposition": self.disposition,
            "decision_needed": self.decision_needed,
            "critical": self.critical,
            "downstream_impact_count": self.downstream_impact_count,
            "priority_score": self.priority_score,
        }
        if self.question is not None:
            out["question"] = self.question
        return out


@dataclass
class AmbiguityReport:
    findings: list[AmbiguityFinding] = field(default_factory=list)

    @property
    def questions(self) -> list[AmbiguityFinding]:
        return sorted(
            [f for f in self.findings if f.decision_needed and f.question],
            key=lambda f: (-f.priority_score, f.block_id, f.code, f.line),
        )

    def as_dict(self) -> dict[str, Any]:
        findings = sorted(self.findings, key=lambda f: (f.block_id, f.line, f.code, f.span))
        questions = self.questions
        return {
            "ok": True,
            "summary": {
                "findings": len(findings),
                "decision_needed": sum(f.decision_needed for f in findings),
                "questions": len(questions),
            },
            "findings": [f.as_dict() for f in findings],
            "questions": [f.as_dict() for f in questions],
        }


def _critical(block: Block) -> bool:
    value = _field(block, "Critical")
    return bool(value and value[0].strip().lower() == "true")


def _active_fields(block: Block, name: str) -> list[tuple[str, LineInfo]]:
    pat = re.compile(rf"^\s*{re.escape(name)}:\s*(.*?)\s*$", re.I)
    out: list[tuple[str, LineInfo]] = []
    for li in block.lines:
        if not li.active:
            continue
        m = pat.match(li.text)
        if m:
            out.append((m.group(1), li))
    return out


def _column(text: str, span: str) -> int:
    idx = text.lower().find(span.lower())
    return idx + 1 if idx >= 0 else 1


def _severity(code: str, critical: bool, governed: bool = False) -> str:
    if governed:
        return "low"
    if code == "AMB-004":
        return "high"
    if code in {"AMB-001", "AMB-003", "AMB-006"}:
        return "high" if critical else "medium"
    if code in {"AMB-002", "AMB-005"}:
        return "medium" if critical else "low"
    return "medium"


def _question(code: str, block_id: str, span: str) -> str:
    if code == "AMB-001":
        return f"Which option should govern {block_id} for {span}?"
    if code == "AMB-002":
        return f"What measurable bound should replace '{span}' in {block_id}?"
    if code == "AMB-003":
        return f"What explicit referent does '{span}' identify in {block_id}?"
    if code == "AMB-004":
        return f"Which conflicting value for {span} should govern {block_id}?"
    if code == "AMB-005":
        return f"Should this assumption be approved, rejected, or replaced for {block_id}?"
    if code == "AMB-006":
        return f"What decision resolves '{span}' in {block_id}?"
    return f"What decision is required for {block_id}?"


def _declared_interfaces(lines: list[LineInfo]) -> set[str]:
    out: set[str] = set()
    for li in lines:
        if not li.active:
            continue
        m = INTERFACE.match(li.text)
        if m:
            out.add(m.group(1))
    return out


def _impact_counts(trace_graph: dict[str, Any] | None, block_ids: set[str]) -> dict[str, int]:
    if trace_graph is None:
        return {bid: 0 for bid in block_ids}
    validation = validate_graph(trace_graph)
    if not validation.ok:
        details = "; ".join(f"{d.code}: {d.message}" for d in validation.errors)
        raise ValueError(f"invalid traceability graph: {details}")
    counts: dict[str, int] = {}
    nodes = {n.get("id") for n in trace_graph.get("nodes", [])}
    for bid in block_ids:
        if bid not in nodes:
            counts[bid] = 0
            continue
        impact = analyze_impact(trace_graph, [bid])
        if not impact.ok:
            raise ValueError(f"impact analysis failed for {bid}")
        counts[bid] = len(impact.downstream)
    return counts


def analyze_ambiguity(text: str, *, trace_graph: dict[str, Any] | None = None) -> AmbiguityReport:
    lines = _scan_lines(text)
    blocks = [b for b in _blocks(lines) if b.kind in {"requirement", "task"}]
    interfaces = _declared_interfaces(lines)
    impact = _impact_counts(trace_graph, {b.identifier for b in blocks})
    findings: list[AmbiguityFinding] = []

    def add(code: str, block: Block, li: LineInfo, span: str, category: str, disposition: str, decision_needed: bool) -> None:
        crit = _critical(block)
        governed = disposition == "governed_default"
        sev = _severity(code, crit, governed)
        count = impact.get(block.identifier, 0)
        score = SEVERITY_WEIGHT[sev] + (50 if crit else 0) + min(count, 99)
        q = _question(code, block.identifier, span) if decision_needed else None
        findings.append(AmbiguityFinding(
            code=code, block_id=block.identifier, block_kind=block.kind,
            line=li.number, column=_column(li.text, span), span=span,
            category=category, severity=sev, disposition=disposition,
            decision_needed=decision_needed, critical=crit,
            downstream_impact_count=count, priority_score=score, question=q,
        ))

    for block in blocks:
        # AMB-001: unresolved/defaulted Options: key = A | B
        for value, li in _active_fields(block, "Options"):
            m = KEY_VALUE.match(value)
            if not m or "|" not in m.group(2):
                continue
            key = m.group(1)
            options = [x.strip() for x in m.group(2).split("|") if x.strip()]
            default = _field(block, "Default")
            governed = False
            if default:
                dm = KEY_VALUE.match(default[0])
                governed = bool(dm and dm.group(1) == key and dm.group(2).strip() in options)
            add("AMB-001", block, li, key, "unresolved_options", "governed_default" if governed else "owner_decision", not governed)

        # AMB-002/003 are requirement-field semantics.
        requirement = _field(block, "Requirement")
        if requirement:
            req_text, req_li = requirement
            if not _field(block, "Bound"):
                for term in UNBOUNDED_TERMS:
                    m = re.search(rf"\b{re.escape(term)}\b", req_text, re.I)
                    if m:
                        add("AMB-002", block, req_li, req_text[m.start():m.end()], "missing_measurable_bound", "owner_decision", True)
                        break
            rm = REFERENT_PREFIX.match(req_text)
            if rm:
                refs = _field(block, "Refs")
                declared = False
                if refs:
                    targets = [x.strip() for x in re.split(r"[,;]", refs[0]) if x.strip()]
                    declared = bool(targets) and all(t in interfaces for t in targets)
                if not declared:
                    add("AMB-003", block, req_li, rm.group(1), "undefined_referent", "owner_decision", True)

        # AMB-004: conflicting same-key constraints.
        by_key: dict[str, list[tuple[str, LineInfo]]] = {}
        for value, li in _active_fields(block, "Constraint"):
            m = KEY_VALUE.match(value)
            if m:
                by_key.setdefault(m.group(1), []).append((m.group(2).strip(), li))
        for key, values in sorted(by_key.items()):
            distinct = {v for v, _ in values}
            if len(distinct) > 1:
                add("AMB-004", block, values[-1][1], key, "conflicting_constraint", "owner_decision", True)

        # AMB-005: assumption governance.
        for value, li in _active_fields(block, "Assumption"):
            governed = bool(APPROVED_DEC.search(value))
            span = value if len(value) <= 120 else value[:117] + "..."
            add("AMB-005", block, li, span, "assumption_governance", "governed_default" if governed else "owner_decision", not governed)

        # AMB-006: unresolved active normative markers. Avoid duplicate scanning of
        # Notes/Rationale/fences because _scan_lines marks them inactive.
        for li in block.lines:
            if not li.active:
                continue
            if li.text.strip().startswith("#"):
                continue
            for marker in UNRESOLVED_MARKERS:
                m = _unresolved_marker_match(li.text, marker)
                if m:
                    add("AMB-006", block, li, li.text[m.start():m.end()], "unresolved_marker", "owner_decision", True)
                    break

    # Remove exact duplicate semantic candidates deterministically. This can
    # happen only if duplicated equivalent normative lines are present.
    unique: dict[tuple[Any, ...], AmbiguityFinding] = {}
    for f in findings:
        key = (f.block_id, f.code, f.line, f.span, f.disposition, f.decision_needed)
        unique.setdefault(key, f)
    return AmbiguityReport(list(unique.values()))


def analyze_ambiguity_file(path: str | Path, *, trace_graph_path: str | Path | None = None) -> AmbiguityReport:
    text = Path(path).read_text(encoding="utf-8")
    graph = None
    if trace_graph_path is not None:
        graph = json.loads(Path(trace_graph_path).read_text(encoding="utf-8"))
    return analyze_ambiguity(text, trace_graph=graph)
