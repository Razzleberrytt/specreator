from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import re

from .ambiguity import AmbiguityFinding, analyze_ambiguity
from .linter import _blocks, _field, _scan_lines, Block

PROJECT_TYPES = {"prototype", "production", "regulated", "custom"}
DEFAULT_BUDGETS = {"prototype": 2, "production": 3, "regulated": 4, "custom": 2}
TRUSTED_PROVENANCE = {"owner_intake", "approved_policy", "existing_spec"}
SAFE_RISK = "low"
MAX_SAFE_DOWNSTREAM_IMPACT = 3
OPTIONS_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_.-]*)\s*=\s*(.+?)\s*$")


@dataclass(frozen=True)
class ProfileDefault:
    block_id: str
    ambiguity_code: str
    span: str
    value: str
    risk: str
    reversible: bool
    auto_apply: bool
    provenance: str
    source_ref: str

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "ProfileDefault":
        required = {
            "block_id", "ambiguity_code", "span", "value", "risk",
            "reversible", "auto_apply", "provenance", "source_ref",
        }
        missing = sorted(required - set(obj))
        extra = sorted(set(obj) - required)
        if missing:
            raise ValueError(f"profile default missing field(s): {', '.join(missing)}")
        if extra:
            raise ValueError(f"profile default has unknown field(s): {', '.join(extra)}")
        for name in ("block_id", "ambiguity_code", "span", "value", "risk", "provenance", "source_ref"):
            if not isinstance(obj[name], str) or not obj[name].strip():
                raise ValueError(f"profile default {name} must be a non-empty string")
        if not isinstance(obj["reversible"], bool) or not isinstance(obj["auto_apply"], bool):
            raise ValueError("profile default reversible/auto_apply must be boolean")
        return cls(**obj)


@dataclass(frozen=True)
class DiscoveryProfile:
    profile_id: str
    project_type: str
    question_budget: int
    defaults: tuple[ProfileDefault, ...] = ()

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> "DiscoveryProfile":
        if obj is None:
            obj = {"profile_id": "PROF-DEFAULT", "project_type": "custom", "defaults": []}
        if not isinstance(obj, dict):
            raise ValueError("profile must be a JSON object")
        allowed = {"profile_id", "project_type", "question_budget", "defaults"}
        extra = sorted(set(obj) - allowed)
        if extra:
            raise ValueError(f"profile has unknown field(s): {', '.join(extra)}")
        profile_id = obj.get("profile_id")
        project_type = obj.get("project_type")
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")
        if project_type not in PROJECT_TYPES:
            raise ValueError(f"project_type must be one of {sorted(PROJECT_TYPES)}")
        budget = obj.get("question_budget", DEFAULT_BUDGETS[project_type])
        if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
            raise ValueError("question_budget must be a positive integer")
        defaults_raw = obj.get("defaults", [])
        if not isinstance(defaults_raw, list):
            raise ValueError("defaults must be an array")
        defaults = tuple(ProfileDefault.from_dict(x) for x in defaults_raw)
        seen: set[tuple[str, str, str]] = set()
        for d in defaults:
            key = (d.block_id, d.ambiguity_code, d.span)
            if key in seen:
                raise ValueError(f"duplicate profile default target {key}")
            seen.add(key)
        return cls(profile_id=profile_id, project_type=project_type, question_budget=budget, defaults=defaults)


@dataclass(frozen=True)
class CandidateAction:
    candidate_id: str
    block_id: str
    code: str
    span: str
    critical: bool
    action: str
    reason: str
    provenance: dict[str, Any]
    value: str | None = None
    dependencies: tuple[str, ...] = ()
    batch_group: str | None = None
    information_value: int | None = None
    inference_rejection_reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "candidate_id": self.candidate_id,
            "block_id": self.block_id,
            "code": self.code,
            "span": self.span,
            "critical": self.critical,
            "action": self.action,
            "reason": self.reason,
            "provenance": self.provenance,
            "dependencies": list(self.dependencies),
        }
        if self.value is not None:
            out["value"] = self.value
        if self.batch_group is not None:
            out["batch_group"] = self.batch_group
        if self.information_value is not None:
            out["information_value"] = self.information_value
        if self.inference_rejection_reasons:
            out["inference_rejection_reasons"] = list(self.inference_rejection_reasons)
        return out


@dataclass(frozen=True)
class QuestionBatch:
    group_id: str
    information_value: int
    critical: bool
    member_candidate_ids: tuple[str, ...]
    member_block_ids: tuple[str, ...]
    question: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "group_id": self.group_id,
            "information_value": self.information_value,
            "critical": self.critical,
            "member_candidate_ids": list(self.member_candidate_ids),
            "member_block_ids": list(self.member_block_ids),
            "question": self.question,
        }


@dataclass
class DiscoveryPlan:
    profile: DiscoveryProfile
    actions: list[CandidateAction] = field(default_factory=list)
    questions: list[QuestionBatch] = field(default_factory=list)
    baseline_question_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        actions = sorted(self.actions, key=lambda a: (a.block_id, a.code, a.candidate_id))
        questions = sorted(self.questions, key=lambda q: (-q.information_value, q.group_id))
        return {
            "ok": True,
            "profile": {
                "profile_id": self.profile.profile_id,
                "project_type": self.profile.project_type,
                "question_budget": self.profile.question_budget,
            },
            "summary": {
                "candidates": len(actions),
                "baseline_questions": self.baseline_question_count,
                "question_batches": len(questions),
                "infer_default": sum(a.action == "infer_default" for a in actions),
                "already_governed": sum(a.action == "already_governed" for a in actions),
                "ask_now": sum(a.action == "ask_now" for a in actions),
                "defer_dependency": sum(a.action == "defer_dependency" for a in actions),
                "defer_budget": sum(a.action == "defer_budget" for a in actions),
            },
            "actions": [a.as_dict() for a in actions],
            "questions": [q.as_dict() for q in questions],
        }


def _block_metadata(text: str) -> dict[str, dict[str, Any]]:
    lines = _scan_lines(text)
    blocks = [b for b in _blocks(lines) if b.kind in {"requirement", "task"}]
    out: dict[str, dict[str, Any]] = {}
    for b in blocks:
        deps: tuple[str, ...] = ()
        dep = _field(b, "Decision-Depends-On")
        if dep and dep[0].strip():
            deps = tuple(x.strip() for x in re.split(r"[,;]", dep[0]) if x.strip())
        grp = _field(b, "Decision-Group")
        group = grp[0].strip() if grp and grp[0].strip() else None
        options: dict[str, tuple[str, ...]] = {}
        default_values: dict[str, str] = {}
        for li in b.lines:
            if not li.active:
                continue
            m = re.match(r"^\s*Options:\s*(.*?)\s*$", li.text, re.I)
            if m:
                kv = OPTIONS_RE.match(m.group(1))
                if kv and "|" in kv.group(2):
                    options[kv.group(1)] = tuple(x.strip() for x in kv.group(2).split("|") if x.strip())
            m = re.match(r"^\s*Default:\s*(.*?)\s*$", li.text, re.I)
            if m:
                kv = OPTIONS_RE.match(m.group(1))
                if kv:
                    default_values[kv.group(1)] = kv.group(2).strip()
        out[b.identifier] = {"block": b, "dependencies": deps, "group": group, "options": options, "defaults": default_values}
    return out


def _matching_profile_default(profile: DiscoveryProfile, finding: AmbiguityFinding) -> ProfileDefault | None:
    matches = [d for d in profile.defaults if d.block_id == finding.block_id and d.ambiguity_code == finding.code and d.span == finding.span]
    return matches[0] if matches else None


def _safe_default_rejection_reasons(
    profile: DiscoveryProfile,
    finding: AmbiguityFinding,
    profile_default: ProfileDefault,
    metadata: dict[str, dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if finding.code != "AMB-001":
        reasons.append("unsupported_ambiguity_code")
    block = metadata.get(finding.block_id, {})
    options = block.get("options", {}).get(finding.span, ())
    if not options or profile_default.value not in options:
        reasons.append("value_not_declared_option")
    if profile_default.risk != SAFE_RISK:
        reasons.append("risk_not_low")
    if not profile_default.reversible:
        reasons.append("not_reversible")
    if not profile_default.auto_apply:
        reasons.append("auto_apply_disabled")
    if profile_default.provenance not in TRUSTED_PROVENANCE:
        reasons.append("untrusted_provenance")
    if finding.critical:
        reasons.append("critical_block")
    if finding.severity == "high":
        reasons.append("high_severity")
    if finding.downstream_impact_count > MAX_SAFE_DOWNSTREAM_IMPACT:
        reasons.append("downstream_impact_too_high")
    if profile.project_type == "regulated":
        reasons.append("regulated_profile_forbids_auto_default")
    return reasons


def _candidate_id(f: AmbiguityFinding) -> str:
    return f"{f.block_id}:{f.code}:{f.line}"


def plan_discovery(
    text: str,
    *,
    profile: dict[str, Any] | DiscoveryProfile | None = None,
    trace_graph: dict[str, Any] | None = None,
) -> DiscoveryPlan:
    prof = profile if isinstance(profile, DiscoveryProfile) else DiscoveryProfile.from_dict(profile)
    report = analyze_ambiguity(text, trace_graph=trace_graph)
    metadata = _block_metadata(text)
    findings = sorted(report.findings, key=lambda f: (f.block_id, f.code, f.line, f.span))
    baseline = sum(f.decision_needed for f in findings)

    actions_by_id: dict[str, CandidateAction] = {}
    unresolved_owner: dict[str, AmbiguityFinding] = {}
    rejected_defaults: dict[str, tuple[str, ...]] = {}

    # Phase 1: preserve parent governance and apply only fully safe explicit profile defaults.
    for f in findings:
        cid = _candidate_id(f)
        block_meta = metadata.get(f.block_id, {})
        deps = tuple(block_meta.get("dependencies", ()))
        group = block_meta.get("group")
        if not f.decision_needed:
            value = block_meta.get("defaults", {}).get(f.span) if f.code == "AMB-001" else None
            actions_by_id[cid] = CandidateAction(
                candidate_id=cid, block_id=f.block_id, code=f.code, span=f.span, critical=f.critical,
                action="already_governed", reason="parent_governance_resolved",
                provenance={"source": "parent_ambiguity", "ref": f"{f.block_id}:{f.line}", "disposition": f.disposition},
                value=value, dependencies=deps, batch_group=group,
            )
            continue
        pd = _matching_profile_default(prof, f)
        if pd is not None:
            rejection = _safe_default_rejection_reasons(prof, f, pd, metadata)
            if not rejection:
                actions_by_id[cid] = CandidateAction(
                    candidate_id=cid, block_id=f.block_id, code=f.code, span=f.span, critical=f.critical,
                    action="infer_default", reason="safe_profile_default",
                    provenance={"source": pd.provenance, "ref": pd.source_ref, "profile_id": prof.profile_id},
                    value=pd.value, dependencies=deps, batch_group=group,
                )
                continue
            rejected_defaults[cid] = tuple(rejection)
        unresolved_owner[cid] = f

    # Blocks still needing owner resolution after governed/safe defaults.
    unresolved_blocks = {f.block_id for f in unresolved_owner.values()}

    # Phase 2: dependency frontier.
    ready: dict[str, AmbiguityFinding] = {}
    for cid, f in unresolved_owner.items():
        block_meta = metadata.get(f.block_id, {})
        deps = tuple(block_meta.get("dependencies", ()))
        blocking = tuple(sorted(d for d in deps if d in unresolved_blocks))
        if blocking:
            actions_by_id[cid] = CandidateAction(
                candidate_id=cid, block_id=f.block_id, code=f.code, span=f.span, critical=f.critical,
                action="defer_dependency", reason="prerequisite_owner_decision_pending",
                provenance={"source": "spec_dependency", "ref": f.block_id, "blocking_dependencies": list(blocking)},
                dependencies=deps, batch_group=block_meta.get("group"),
                inference_rejection_reasons=rejected_defaults.get(cid, ()),
            )
        else:
            ready[cid] = f

    # Count unresolved dependent blocks for information-value scoring.
    dependents_by_block: dict[str, set[str]] = {}
    for block_id, meta in metadata.items():
        for dep in meta.get("dependencies", ()):
            if block_id in unresolved_blocks:
                dependents_by_block.setdefault(dep, set()).add(block_id)

    # Explicit groups only; otherwise one group per candidate.
    groups: dict[str, list[tuple[str, AmbiguityFinding]]] = {}
    for cid, f in ready.items():
        grp = metadata.get(f.block_id, {}).get("group") or f"{f.block_id}:{f.code}"
        groups.setdefault(grp, []).append((cid, f))

    group_rows: list[tuple[str, int, bool, list[tuple[str, AmbiguityFinding]]]] = []
    for grp, members in groups.items():
        member_blocks = {f.block_id for _, f in members}
        dependent_blocks: set[str] = set()
        for b in member_blocks:
            dependent_blocks.update(dependents_by_block.get(b, set()))
        score = max(f.priority_score for _, f in members) + 40 * len(dependent_blocks) + 15 * (len(members) - 1)
        critical = any(f.critical for _, f in members)
        group_rows.append((grp, score, critical, sorted(members, key=lambda x: (x[1].block_id, x[1].code, x[1].line))))

    critical_groups = sorted([g for g in group_rows if g[2]], key=lambda x: (-x[1], x[0]))
    noncritical_groups = sorted([g for g in group_rows if not g[2]], key=lambda x: (-x[1], x[0]))
    selected_ids = {g[0] for g in critical_groups}
    remaining_slots = max(prof.question_budget - len(critical_groups), 0)
    for g in noncritical_groups[:remaining_slots]:
        selected_ids.add(g[0])

    questions: list[QuestionBatch] = []
    for grp, score, critical, members in group_rows:
        selected = grp in selected_ids
        if selected:
            qs = [f.question or f"What decision is required for {f.block_id}?" for _, f in members]
            question = qs[0] if len(qs) == 1 else f"Resolve group {grp}: " + " | ".join(qs)
            questions.append(QuestionBatch(
                group_id=grp, information_value=score, critical=critical,
                member_candidate_ids=tuple(cid for cid, _ in members),
                member_block_ids=tuple(f.block_id for _, f in members), question=question,
            ))
        for cid, f in members:
            meta = metadata.get(f.block_id, {})
            actions_by_id[cid] = CandidateAction(
                candidate_id=cid, block_id=f.block_id, code=f.code, span=f.span, critical=f.critical,
                action="ask_now" if selected else "defer_budget",
                reason="selected_information_frontier" if selected else "question_budget_deferred",
                provenance={"source": "adaptive_discovery_policy", "ref": "REL-0.07-FROZEN-001", "profile_id": prof.profile_id},
                dependencies=tuple(meta.get("dependencies", ())), batch_group=grp, information_value=score,
                inference_rejection_reasons=rejected_defaults.get(cid, ()),
            )

    return DiscoveryPlan(profile=prof, actions=list(actions_by_id.values()), questions=questions, baseline_question_count=baseline)


def plan_discovery_file(
    path: str | Path,
    *,
    profile_path: str | Path | None = None,
    trace_graph_path: str | Path | None = None,
) -> DiscoveryPlan:
    text = Path(path).read_text(encoding="utf-8")
    profile_obj = None
    if profile_path is not None:
        profile_obj = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    graph = None
    if trace_graph_path is not None:
        graph = json.loads(Path(trace_graph_path).read_text(encoding="utf-8"))
    return plan_discovery(text, profile=profile_obj, trace_graph=graph)
