from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable
import re


@dataclass(frozen=True, order=True)
class Finding:
    line: int
    column: int
    rule_id: str
    severity: str
    span: str
    rationale: str
    related_line: int | None = None
    suppressed: bool = False
    suppression_decision_id: str | None = None

    def as_dict(self) -> dict:
        data = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "line": self.line,
            "column": self.column,
            "span": self.span,
            "rationale": self.rationale,
            "suppressed": self.suppressed,
        }
        if self.related_line is not None:
            data["related_line"] = self.related_line
        if self.suppression_decision_id is not None:
            data["suppression_decision_id"] = self.suppression_decision_id
        return data


@dataclass
class LintReport:
    findings: list[Finding]

    @property
    def unsuppressed(self) -> list[Finding]:
        return [f for f in self.findings if not f.suppressed]

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" and not f.suppressed for f in self.findings)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "summary": {
                "findings": len(self.findings),
                "unsuppressed": len(self.unsuppressed),
                "suppressed": sum(1 for f in self.findings if f.suppressed),
            },
            "findings": [f.as_dict() for f in self.findings],
        }


@dataclass(frozen=True)
class LineInfo:
    number: int
    text: str
    active: bool


@dataclass(frozen=True)
class Block:
    kind: str
    identifier: str
    start_line: int
    end_line: int
    lines: tuple[LineInfo, ...]


VAGUE_TERMS = (
    "user-friendly",
    "reasonably",
    "reasonable",
    "appropriately",
    "as needed",
    "common formats",
    "similar inputs",
    "robust",
    "simple",
    "good",
    "most users",
    "fast",
)

MUTATING_OPERATIONS = (
    "delete",
    "deploy",
    "write",
    "migrate",
    "send",
    "update",
    "upload",
    "charge",
    "publish",
    "remove",
    "overwrite",
)

TASK_ACTION_PATTERNS = (
    r"\bdesign(?:ing)?\b",
    r"\bimplement(?:ing)?\b",
    r"\btest(?:ing)?\b",
    r"\bdocument(?:ing)?\b",
    r"\bpackage|packaging\b",
    r"\brelease|releasing\b",
    r"\bparse|parsing\b",
    r"\bbuild|building\b",
    r"\bcreate|creating\b",
    r"\bupdate|updating\b",
    r"\brefactor|refactoring\b",
    r"\brewrite|rewriting\b",
    r"\bfix|fixing\b",
    r"\bverify|verifying\b",
    r"\bpublish|publishing\b",
    r"\badd|adding\b",
    r"\bmigrate|migrating\b",
    r"\bdeploy|deploying\b",
    r"\bintegrate|integrating\b",
    r"\blint|linting\b",
    r"\bsuppress|suppression\b",
    r"\breport|reporting\b",
)

UNRESOLVED_DECISION = re.compile(r"\b(?:TBD|TODO|pending|unresolved|undecided)\b", re.I)
DECISION_ID = re.compile(r"\bDEC-[A-Za-z0-9._-]+\b")
SUPPRESSION_RE = re.compile(r"^\s*Lint-Suppress:\s*(LINT-\d{3})\s+decision=(DEC-[A-Za-z0-9._-]+)\s*$", re.I)


def _scan_lines(text: str) -> list[LineInfo]:
    lines = text.splitlines()
    result: list[LineInfo] = []
    in_fence = False
    fence_token: str | None = None
    for idx, line in enumerate(lines, 1):
        stripped = line.lstrip()
        is_fence = stripped.startswith("```") or stripped.startswith("~~~")
        if is_fence:
            token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_token = token
            elif token == fence_token:
                in_fence = False
                fence_token = None
            result.append(LineInfo(idx, line, False))
            continue
        active = not in_fence
        if active and stripped.startswith(">"):
            active = False
        if active and re.match(r"^(?:Notes|Rationale):", stripped, re.I):
            active = False
        result.append(LineInfo(idx, line, active))
    return result


def _blocks(lines: list[LineInfo]) -> list[Block]:
    starts: list[tuple[int, str, str]] = []
    for i, li in enumerate(lines):
        s = li.text.strip()
        m = re.match(r"^###\s+(REQ-[A-Za-z0-9._-]+)\s*$", s)
        if m:
            starts.append((i, "requirement", m.group(1)))
            continue
        m = re.match(r"^###\s+(TASK-[A-Za-z0-9._-]+)\s*$", s)
        if m:
            starts.append((i, "task", m.group(1)))
            continue
        m = re.match(r"^###\s+Component:\s*(.+?)\s*$", s, re.I)
        if m:
            starts.append((i, "component", m.group(1).strip()))
    out: list[Block] = []
    for n, (start_idx, kind, ident) in enumerate(starts):
        next_start = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        # A ### requirement/task/component block ends at any later heading at
        # the same or a higher Markdown level. This prevents a following ##
        # section from leaking explanatory prose into the normative block,
        # while preserving deeper #### substructure inside the block.
        end_idx = next_start
        for j in range(start_idx + 1, next_start):
            if re.match(r"^#{1,3}\s+", lines[j].text.strip()):
                end_idx = j
                break
        block_lines = tuple(lines[start_idx:end_idx])
        out.append(Block(kind, ident, lines[start_idx].number, block_lines[-1].number if block_lines else lines[start_idx].number, block_lines))
    return out


def _field(block: Block, name: str) -> tuple[str, LineInfo] | None:
    pat = re.compile(rf"^\s*{re.escape(name)}:\s*(.*?)\s*$", re.I)
    for li in block.lines:
        if not li.active:
            continue
        m = pat.match(li.text)
        if m:
            return m.group(1), li
    return None


def _column(line: str, span: str) -> int:
    idx = line.lower().find(span.lower())
    return (idx + 1) if idx >= 0 else 1


def _finding(rule_id: str, li: LineInfo, span: str, rationale: str, *, related_line: int | None = None, severity: str = "error") -> Finding:
    return Finding(
        line=li.number,
        column=_column(li.text, span),
        rule_id=rule_id,
        severity=severity,
        span=span,
        rationale=rationale,
        related_line=related_line,
    )


def _lint_vague(lines: list[LineInfo]) -> list[Finding]:
    findings: list[Finding] = []
    for li in lines:
        if not li.active or not li.text.strip() or li.text.lstrip().startswith("#"):
            continue
        # Suppression directives are metadata, not normative prose.
        if li.text.lstrip().lower().startswith("lint-suppress:"):
            continue
        low = li.text.lower()
        for term in VAGUE_TERMS:
            # Guard short adjective terms with word boundaries.
            if " " not in term and "-" not in term:
                match = re.search(rf"\b{re.escape(term)}\b", low)
            else:
                match = re.search(re.escape(term), low)
            if match:
                span = li.text[match.start():match.end()]
                findings.append(_finding("LINT-001", li, span, f"'{span}' is vague or non-testable without a measurable bound or explicit acceptance criterion."))
    return findings


def _lint_requirements(blocks: list[Block]) -> list[Finding]:
    findings: list[Finding] = []
    for b in blocks:
        if b.kind != "requirement":
            continue
        heading = b.lines[0]
        acceptance = _field(b, "Acceptance")
        verify = _field(b, "Verify")
        if not acceptance or not acceptance[0].strip():
            findings.append(_finding("LINT-002", heading, b.identifier, "Requirement block has no non-empty Acceptance: criterion."))
        if not verify or not verify[0].strip():
            findings.append(_finding("LINT-006", heading, b.identifier, "Requirement block has no non-empty Verify: path."))
        crit = _field(b, "Critical")
        req = _field(b, "Requirement")
        failure = _field(b, "Failure")
        is_critical = bool(crit and crit[0].strip().lower() == "true")
        if is_critical and req:
            low = req[0].lower()
            operation = next((op for op in MUTATING_OPERATIONS if re.search(rf"\b{re.escape(op)}\b", low)), None)
            if operation and (not failure or not failure[0].strip()):
                findings.append(_finding("LINT-003", req[1], operation, f"Critical mutating operation '{operation}' lacks explicit Failure: behavior."))
    return findings


def _lint_decisions(lines: list[LineInfo]) -> list[Finding]:
    findings: list[Finding] = []
    for li in lines:
        if not li.active:
            continue
        s = li.text.strip()
        if not re.match(r"^(?:Decision|Critical Decision):", s, re.I):
            continue
        critical = s.lower().startswith("critical decision:") or "[critical]" in s.lower()
        if critical:
            m = UNRESOLVED_DECISION.search(s)
            if m:
                findings.append(_finding("LINT-004", li, m.group(0), "Critical decision remains unresolved and can block deterministic implementation."))
    return findings


def _lint_references(lines: list[LineInfo]) -> list[Finding]:
    declarations: set[str] = set()
    refs: list[tuple[LineInfo, str]] = []
    for li in lines:
        if not li.active:
            continue
        m = re.match(r"^\s*(?:Interface|Entity):\s*([A-Za-z0-9._-]+)\s*$", li.text, re.I)
        if m:
            declarations.add(m.group(1))
            continue
        m = re.match(r"^\s*Refs:\s*(.*?)\s*$", li.text, re.I)
        if m:
            for token in [x.strip() for x in m.group(1).split(",") if x.strip()]:
                refs.append((li, token))
    findings: list[Finding] = []
    for li, token in refs:
        if token not in declarations:
            findings.append(_finding("LINT-005", li, token, f"Reference '{token}' has no matching Interface: or Entity: declaration in this document."))
    return findings


def _lint_constraints(lines: list[LineInfo]) -> list[Finding]:
    seen: dict[str, tuple[str, LineInfo]] = {}
    findings: list[Finding] = []
    for li in lines:
        if not li.active:
            continue
        m = re.match(r"^\s*Constraint:\s*([A-Za-z0-9._-]+)\s*=\s*(.*?)\s*$", li.text, re.I)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        prior = seen.get(key)
        if prior and prior[0] != value:
            findings.append(_finding("LINT-007", li, li.text.strip(), f"Constraint '{key}' conflicts with value '{prior[0]}' declared on line {prior[1].number}.", related_line=prior[1].number))
        elif not prior:
            seen[key] = (value, li)
    return findings


def _lint_tasks(blocks: list[Block]) -> list[Finding]:
    findings: list[Finding] = []
    for b in blocks:
        if b.kind != "task":
            continue
        task = _field(b, "Task")
        if not task or _field(b, "Bounded By"):
            continue
        text = task[0]
        count = sum(1 for pat in TASK_ACTION_PATTERNS if re.search(pat, text, re.I))
        if count >= 4:
            findings.append(_finding("LINT-008", task[1], text, f"Task combines {count} major action domains without an explicit Bounded By: constraint."))
    return findings


def _lint_components(blocks: list[Block]) -> list[Finding]:
    findings: list[Finding] = []
    for b in blocks:
        if b.kind != "component":
            continue
        resp = _field(b, "Responsibilities")
        if not resp or _field(b, "Out of Scope"):
            continue
        text = resp[0]
        broad = bool(re.search(r"\b(?:everything|all|any)\b", text, re.I))
        domains = len([x for x in text.split(",") if x.strip()])
        if broad or domains > 4:
            findings.append(_finding("LINT-009", resp[1], text, "Component responsibilities are broad or multi-domain without an explicit Out of Scope: boundary."))
    return findings


def _lint_assumptions(lines: list[LineInfo]) -> list[Finding]:
    findings: list[Finding] = []
    governed = re.compile(r"\[(?:approved|rejected)\s+DEC-[A-Za-z0-9._-]+\]", re.I)
    for li in lines:
        if not li.active:
            continue
        m = re.match(r"^\s*Assumption:\s*(.*?)\s*$", li.text, re.I)
        if not m:
            continue
        if not governed.search(li.text):
            span = m.group(1) or li.text.strip()
            findings.append(_finding("LINT-010", li, span, "Active implementation assumption lacks an approved or rejected DEC-* governance marker."))
    return findings


def _apply_suppressions(lines: list[LineInfo], findings: list[Finding], approved_decisions: set[str]) -> list[Finding]:
    directives: list[tuple[LineInfo, str, str, int | None]] = []
    governance: list[Finding] = []
    for idx, li in enumerate(lines):
        if not li.active or not li.text.lstrip().lower().startswith("lint-suppress:"):
            continue
        m = SUPPRESSION_RE.match(li.text)
        if not m:
            governance.append(_finding("LINT-SUPPRESS-001", li, li.text.strip(), "Suppression directive is invalid; expected 'Lint-Suppress: LINT-### decision=DEC-*'."))
            continue
        rule_id, decision_id = m.group(1).upper(), m.group(2)
        target: int | None = None
        for nxt in lines[idx + 1:]:
            if nxt.active and nxt.text.strip():
                target = nxt.number
                break
        directives.append((li, rule_id, decision_id, target))
        if decision_id not in approved_decisions:
            governance.append(_finding("LINT-SUPPRESS-001", li, decision_id, f"Suppression decision {decision_id} is not in the caller-supplied approved decision set."))

    out = list(findings)
    for directive, rule_id, decision_id, target in directives:
        if decision_id not in approved_decisions or target is None:
            continue
        updated: list[Finding] = []
        used = False
        for f in out:
            if not used and f.rule_id == rule_id and f.line == target and not f.suppressed:
                updated.append(replace(f, suppressed=True, suppression_decision_id=decision_id))
                used = True
            else:
                updated.append(f)
        out = updated
    out.extend(governance)
    return out


def lint_text(text: str, *, approved_decisions: Iterable[str] = ()) -> LintReport:
    lines = _scan_lines(text)
    blocks = _blocks(lines)
    findings: list[Finding] = []
    findings.extend(_lint_vague(lines))
    findings.extend(_lint_requirements(blocks))
    findings.extend(_lint_decisions(lines))
    findings.extend(_lint_references(lines))
    findings.extend(_lint_constraints(lines))
    findings.extend(_lint_tasks(blocks))
    findings.extend(_lint_components(blocks))
    findings.extend(_lint_assumptions(lines))
    findings = _apply_suppressions(lines, findings, set(approved_decisions))
    findings.sort(key=lambda f: (f.line, f.column, f.rule_id, f.span))
    return LintReport(findings)


def lint_file(path: str | Path, *, approved_decisions: Iterable[str] = ()) -> LintReport:
    return lint_text(Path(path).read_text(encoding="utf-8"), approved_decisions=approved_decisions)
