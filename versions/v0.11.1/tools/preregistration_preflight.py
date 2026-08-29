from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / "versions" / "v0.11.1"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def die(msg: str):
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def derive_explicit_provenance(fix, tasks, consumer, dep_id):
    producer = tasks[dep_id]
    matches = []
    if dep_id in consumer.get("authority_gates", []):
        matches.append("authority_gate")
    if set(producer.get("write", [])) & set(consumer.get("read", [])):
        matches.append("artifact_input")
    if dep_id in consumer.get("integration_inputs", []):
        matches.append("explicit_integration")
    if dep_id in consumer.get("source_requirement_predecessors", []):
        matches.append("source_requirement")
    if len(matches) != 1:
        die(f"{fix['fixture_id']} {dep_id}->{consumer['id']} provenance oracle matched {matches}, expected exactly one")
    return matches[0]


def effective_edges(fix):
    tasks = {t["id"]: t for t in fix["tasks"]}
    edges = []
    for t in fix["tasks"]:
        for d in t.get("deps", []):
            if d["task_id"] not in tasks:
                die(f"{fix['fixture_id']} unknown dependency {d['task_id']}")
            derived = derive_explicit_provenance(fix, tasks, t, d["task_id"])
            if derived != d["provenance"]:
                die(f"{fix['fixture_id']} {d['task_id']}->{t['id']} declared {d['provenance']} but oracle derives {derived}")
            edges.append((d["task_id"], t["id"], derived))

    order = fix.get("deterministic_conflict_order", [])
    if order:
        for a, b in zip(order, order[1:]):
            if a not in tasks or b not in tasks:
                die(f"{fix['fixture_id']} conflict order references unknown task")
            if not (set(tasks[a].get("write", [])) & set(tasks[b].get("write", []))):
                die(f"{fix['fixture_id']} conflict order {a}->{b} has no shared write scope")
            edges.append((a, b, "conflict_serialization"))
    return edges


def topo_and_waves(fix, edges):
    ids = [t["id"] for t in fix["tasks"]]
    indeg = {x: 0 for x in ids}
    succ = defaultdict(list)
    for a, b, _ in edges:
        succ[a].append(b)
        indeg[b] += 1
    remaining = set(ids)
    waves = []
    while remaining:
        ready = sorted(x for x in remaining if indeg[x] == 0)
        if not ready:
            die(f"{fix['fixture_id']} effective DAG contains cycle")
        waves.append(ready)
        for x in ready:
            remaining.remove(x)
            for y in succ[x]:
                indeg[y] -= 1
    return waves, succ


def critical_paths(fix, edges):
    tasks = {t["id"]: t for t in fix["tasks"]}
    preds = defaultdict(list)
    succ = defaultdict(list)
    indeg = {x: 0 for x in tasks}
    for a, b, _ in edges:
        preds[b].append(a)
        succ[a].append(b)
        indeg[b] += 1
    q = deque(sorted([x for x, d in indeg.items() if d == 0]))
    order = []
    while q:
        x = q.popleft(); order.append(x)
        for y in sorted(succ[x]):
            indeg[y] -= 1
            if indeg[y] == 0: q.append(y)
    if len(order) != len(tasks): die(f"{fix['fixture_id']} cycle")
    best = {}
    paths = {}
    for x in order:
        w = tasks[x]["w"]
        if not preds[x]:
            best[x] = w; paths[x] = [[x]]
        else:
            mx = max(best[p] for p in preds[x])
            best[x] = mx + w
            paths[x] = [p + [x] for pr in sorted(preds[x]) if best[pr] == mx for p in paths[pr]]
    mx = max(best.values())
    all_paths = sorted({tuple(p) for x in tasks if best[x] == mx for p in paths[x]})
    return [list(p) for p in all_paths], mx


def matches_pred(pred, blockers):
    kind = pred["kind"]
    if kind == "empty": return len(blockers) == 0
    if kind == "nonempty": return len(blockers) > 0
    if kind == "contains_any": return any(x in blockers for x in pred.get("tokens", []))
    die(f"unknown blocker predicate {kind}")


def resolve_lifecycle(rules, state, blockers):
    hits = [r for r in rules["rules"] if r["state"] == state and matches_pred(r["blocker_predicate"], blockers)]
    if not hits: die(f"lifecycle {state}/{blockers} has no rule")
    pri = min(r["priority"] for r in hits)
    winners = [r for r in hits if r["priority"] == pri]
    if len(winners) != 1: die(f"lifecycle {state}/{blockers} has priority tie")
    return winners[0]["action"]


def main():
    # Schema validity + checkpoint validation
    schema_paths = [
        V / "candidate-schemas" / "execution-architecture-v1.candidate.schema.json",
        V / "candidate-schemas" / "lifecycle-checkpoint-v1.candidate.schema.json",
    ]
    schemas = [load_json(p) for p in schema_paths]
    for s in schemas:
        jsonschema.Draft202012Validator.check_schema(s)
    checkpoint = load_json(V / "LIFECYCLE-CHECKPOINT-DRAFT.json")
    list(jsonschema.Draft202012Validator(schemas[1]).iter_errors(checkpoint)) or None
    errors = list(jsonschema.Draft202012Validator(schemas[1]).iter_errors(checkpoint))
    if errors: die("lifecycle checkpoint schema errors: " + "; ".join(e.message for e in errors))

    # Execution fixture provenance, DAG, waves, critical paths
    exec_fixtures = load_jsonl(V / "candidate-fixtures" / "execution-architecture-corpus.jsonl")
    explicit_count = derived_conflict_count = 0
    source_keys = []
    for f in exec_fixtures:
        edges = effective_edges(f)
        explicit_count += sum(1 for e in edges if e[2] != "conflict_serialization")
        derived_conflict_count += sum(1 for e in edges if e[2] == "conflict_serialization")
        source_keys.extend(f"{f['fixture_id']}::{t['id']}" for t in f["tasks"])
        waves, _ = topo_and_waves(f, edges)
        if waves != f["expected"]["waves"]:
            die(f"{f['fixture_id']} waves {waves} != expected {f['expected']['waves']}")
        cps, work = critical_paths(f, edges)
        if sorted(cps) != sorted(f["expected"]["critical_paths"]):
            die(f"{f['fixture_id']} critical paths {cps} != expected {f['expected']['critical_paths']}")
        if work != f["expected"]["critical_work_units"]:
            die(f"{f['fixture_id']} critical work {work} != expected {f['expected']['critical_work_units']}")
    if (explicit_count, derived_conflict_count) != (21, 1):
        die(f"dependency edge counts {(explicit_count, derived_conflict_count)} != (21, 1)")

    # Lifecycle rule derivation independent of answer key
    rules = load_json(V / "LIFECYCLE-TRANSITION-RULES.candidate.json")
    life = load_jsonl(V / "candidate-fixtures" / "lifecycle-continuation-corpus.jsonl")
    for f in life:
        got = resolve_lifecycle(rules, f["state"], f["blockers"])
        if got != f["expected_next_action"]:
            die(f"{f['fixture_id']} lifecycle action {got} != {f['expected_next_action']}")

    open_tokens = [b["transition_token"] for b in checkpoint["blockers"] if b["status"] == "OPEN"]
    checkpoint_action = resolve_lifecycle(rules, checkpoint["release_state"], open_tokens)
    if checkpoint_action != checkpoint["next_legal_action"]["action_token"]:
        die(f"checkpoint lifecycle action {checkpoint_action} != declared {checkpoint['next_legal_action']['action_token']}")

    # Exact evaluation universes
    u = load_json(V / "EVALUATION-UNIVERSES.json")["universes"]
    if u["execution_fixtures"]["members"] != [f["fixture_id"] for f in exec_fixtures]: die("execution fixture universe mismatch")
    if u["lifecycle_fixtures"]["members"] != [f["fixture_id"] for f in life]: die("lifecycle fixture universe mismatch")
    if u["critical_path_fixtures"]["members"] != [f["fixture_id"] for f in exec_fixtures]: die("critical-path universe mismatch")
    if u["integration_source_tasks"]["members"] != source_keys: die("integration source-task universe mismatch")
    if len(source_keys) != 23: die("integration source-task count mismatch")
    if u["effective_dependency_edges"]["count"] != 22: die("effective edge universe count mismatch")

    # Evaluation design must reference only declared exact universes.
    eval_design = load_json(V / "EVALUATION-DESIGN.json")
    for metric in eval_design["primary_metrics"] + eval_design["guardrail_metrics"]:
        name = metric["metric"]
        universe = metric.get("universe")
        if universe not in u:
            die(f"metric {name} references undeclared universe {universe}")
        if "denominator_count" in metric and "count" in u[universe] and metric["denominator_count"] != u[universe]["count"]:
            die(f"metric {name} denominator_count does not match universe count")
    # Anti-omission integration contract must be schema-enforced.
    exec_task_schema = schemas[0]["properties"]["tasks"]["items"]
    if "source_task_ids" not in exec_task_schema["required"] or "integration_contract" not in exec_task_schema["required"]:
        die("execution schema does not require source_task_ids + integration_contract")
    blocker_schema = schemas[1]["properties"]["blockers"]["items"]
    action_schema = schemas[1]["properties"]["next_legal_action"]
    if "transition_token" not in blocker_schema["required"] or "action_token" not in action_schema["required"]:
        die("lifecycle schema does not require transition/action tokens")
    expected_commands = [
        "python -m pytest -q",
        "PYTHONPATH=src python -m spec_creator.cli validate . --no-package-manifest",
        "python versions/v0.11.1/tools/preregistration_preflight.py",
    ]
    if checkpoint["validation_profile"]["commands"] != expected_commands:
        die("validation profile commands drift")

    # Candidate preregistration inventory must exactly cover all current retry-version artifacts except itself.
    inv = load_json(V / "PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json")
    expected_inv_paths=[]
    for p in sorted(V.rglob("*")):
        if not p.is_file() or p.name == "PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json" or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        expected_inv_paths.append(p.relative_to(ROOT).as_posix())
    listed=[x["path"] for x in inv["artifacts"]]
    if listed != expected_inv_paths or inv["artifact_count"] != len(expected_inv_paths):
        die("preregistration artifact inventory path/count drift")
    for item in inv["artifacts"]:
        q=ROOT/item["path"]; raw=q.read_bytes()
        if len(raw)!=item["bytes"] or hashlib.sha256(raw).hexdigest()!=item["sha256"]:
            die(f"preregistration artifact inventory hash mismatch {item['path']}")

    # Inherited semantic schemas/fixtures are byte-identical to the failed v0.11 target.
    for rel in [
        "candidate-schemas/execution-architecture-v1.candidate.schema.json",
        "candidate-schemas/lifecycle-checkpoint-v1.candidate.schema.json",
        "candidate-fixtures/execution-architecture-corpus.jsonl",
        "candidate-fixtures/lifecycle-continuation-corpus.jsonl",
    ]:
        if hashlib.sha256((V/rel).read_bytes()).hexdigest() != hashlib.sha256((ROOT/"versions"/"v0.11"/rel).read_bytes()).hexdigest():
            die(f"inherited semantic asset drift {rel}")

    # Parent suite exact inherited collection universe
    parent = load_json(V / "PARENT-SUITE-UNIVERSE.json")
    cp = subprocess.run(["python", "-m", "pytest", "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True)
    if cp.returncode != 0: die("pytest collection failed")
    nodeids = [ln.strip() for ln in cp.stdout.splitlines() if "::" in ln and not ln.startswith("=")]
    if nodeids != parent["nodeids"] or len(nodeids) != 155: die(f"parent suite node-id universe drift: {len(nodeids)}")

    # Exact inherited regressions plus retry-local REG-0025.
    active = []
    for line in (ROOT / "self-improvement" / "regressions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("status") == "active": active.append(rec["regression_id"])
    snap = load_json(V / "ACTIVE-REGRESSION-UNIVERSE.json")
    snap_ids = [x["regression_id"] for x in snap["regressions"]]
    if len(active) != 24 or snap_ids[:24] != active or snap_ids[24:] != ["REG-0025"] or snap["expected_count"] != 25:
        die("active regression universe drift or REG-0025 missing")

    # Frozen executable-parent integrity.
    man = load_json(ROOT / "versions" / "v0.10" / "MANIFEST.json")
    entries = man.get("content_hashes", {})
    if len(entries) != 1120: die(f"v0.10 manifest count {len(entries)} != 1120")
    for rel, expected in entries.items():
        p = ROOT / rel
        if not p.is_file(): die(f"missing frozen parent path {rel}")
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected: die(f"frozen parent hash mismatch {rel}")

    # Failed v0.11 predecessor is now a hash-exact retry parent.
    failed = load_json(V / "FAILED-PREDECESSOR-v0.11-BASELINE.json")
    if failed["entry_count"] != 154 or len(failed["entries"]) != 154: die("failed predecessor baseline count drift")
    failed_paths = set()
    for item in failed["entries"]:
        rel=item["path"]
        if rel in failed_paths: die(f"duplicate failed baseline path {rel}")
        failed_paths.add(rel)
        p=ROOT/rel
        if not p.is_file(): die(f"missing failed predecessor path {rel}")
        raw=p.read_bytes()
        if len(raw)!=item["bytes"] or hashlib.sha256(raw).hexdigest()!=item["sha256"]: die(f"failed predecessor hash mismatch {rel}")

    registry = load_json(V / "IMMUTABILITY-BOUNDARY-DRAFT.json")
    ownership = load_json(V / "SUCCESSOR-OWNERSHIP-UNIVERSE.json")
    protected = set(entries) | set(registry["protected_release_manifests"])
    if len(protected) != 1121 or len(protected) != registry["protected_parent_selector"]["expected_unique_count"]: die("protected-parent unique count drift")
    if protected & failed_paths: die("failed predecessor baseline overlaps protected parent")

    def selector_matches(rel, s):
        kind=s["kind"]
        if kind=="exact": return rel==s["value"]
        if kind=="prefix": return rel.startswith(s["value"])
        if kind=="directory_filename_prefix":
            if not rel.startswith(s["directory"]): return False
            tail=rel[len(s["directory"]):]
            return "/" not in tail and tail.startswith(s["value"])
        if kind=="directory_filename_in":
            if not rel.startswith(s["directory"]): return False
            tail=rel[len(s["directory"]):]
            return "/" not in tail and tail in set(s["values"])
        die(f"unknown successor selector kind {kind}")

    transient_dirs={".pytest_cache","__pycache__"}; transient_suffixes={".pyc"}
    package_paths=set()
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(part in transient_dirs for part in rel.parts) or p.suffix in transient_suffixes: continue
        package_paths.add(rel.as_posix())

    unclassified=[]; immutable_successor_overlap=[]; successor_multimatch=[]; successor=set()
    for rel in sorted(package_paths):
        matches=[s["selector_id"] for s in ownership["selectors"] if selector_matches(rel,s)]
        if rel in protected or rel in failed_paths:
            if matches: immutable_successor_overlap.append((rel,matches))
            continue
        if len(matches)==0: unclassified.append(rel)
        elif len(matches)>1: successor_multimatch.append((rel,matches))
        else: successor.add(rel)
    if unclassified: die(f"immutable-boundary unclassified paths: {unclassified[:10]}")
    if immutable_successor_overlap: die(f"immutable/successor overlap: {immutable_successor_overlap[:5]}")
    if successor_multimatch: die(f"successor selector multi-match: {successor_multimatch[:5]}")

    snapshot=set(ownership["current_snapshot_members"])
    if ownership["current_snapshot_member_count"] != len(snapshot): die("ownership snapshot count/duplicate drift")
    stale=snapshot-package_paths
    if stale: die(f"stale successor snapshot members: {sorted(stale)[:10]}")
    if ownership.get("current_snapshot_generated_after_all_preregistration_artifacts") and snapshot != successor:
        die("current successor snapshot does not equal mechanically classified retry-successor paths")

    prospective=load_json(V / "candidate-fixtures" / "ownership-prospective-paths.json")
    prospect_errors=[]
    for rel in prospective["members"]:
        matches=[s["selector_id"] for s in ownership["selectors"] if selector_matches(rel,s)]
        if rel in protected or rel in failed_paths or len(matches)!=1: prospect_errors.append((rel,matches))
    if prospect_errors: die(f"prospective output classification errors: {prospect_errors[:10]}")
    forbidden_errors=[]
    for rel in prospective.get("forbidden_members", []):
        matches=[s["selector_id"] for s in ownership["selectors"] if selector_matches(rel,s)]
        if matches: forbidden_errors.append((rel,matches))
    if forbidden_errors: die(f"forbidden path unexpectedly admitted: {forbidden_errors[:10]}")
    if prospective.get("forbidden_count") != len(prospective.get("forbidden_members", [])): die("forbidden fixture count drift")

    iu=u["immutable_boundary_assertions"]
    if iu["protected_parent_expected_count"]!=1121 or iu["failed_predecessor_expected_count"]!=154: die("immutable universe count target drift")
    for key in ["expected_unclassified_count","expected_immutable_successor_overlap_count","expected_successor_selector_multi_match_count","expected_stale_snapshot_member_count"]:
        if iu[key] != 0: die(f"zero-tolerance target drift {key}")

    # Retry target is non-weaker than failed v0.11 and adds one guardrail.
    old=load_json(ROOT/"versions"/"v0.11"/"EVALUATION-PLAN.json")
    new=load_json(V/"EVALUATION-PLAN.json")
    def sig(m): return (m["metric"],m.get("universe"),m.get("denominator_count"),m.get("numerator_rule"),m.get("target"))
    old_metrics=[sig(m) for m in old["primary_metrics"]+old["guardrail_metrics"]]
    new_by_name={m["metric"]:m for m in new["primary_metrics"]+new["guardrail_metrics"]}
    for om in old["primary_metrics"]+old["guardrail_metrics"]:
        nm=new_by_name.get(om["metric"])
        if not nm: die(f"retry dropped v0.11 metric {om['metric']}")
        # Retry-specific denominators may only strengthen active regression / missing data / gates.
        if om["metric"] not in {"active_regression_pass_rate","missing_data_count","critical_gate_bypass_count"}:
            if sig(om)[1:] != sig(nm)[1:]: die(f"retry weakened/changed inherited metric {om['metric']}")
        if nm.get("target") != om.get("target"): die(f"retry target drift {om['metric']}")
    if "prospective_output_classification_error_count" not in new_by_name or new_by_name["prospective_output_classification_error_count"]["target"] != 0:
        die("retry prospective ownership metric missing")
    if new["promotion_authoritative_metric_count"] != 16: die("retry promotion metric count != 16")

    print("PASS: v0.11.1 governed-retry preregistration preflight")
    print("candidate schemas: 2 valid; execution fixtures: 6; lifecycle fixtures: 4")
    print("parent suite universe: 155 node IDs; regressions: 24 inherited + REG-0025")
    print("immutable integrity: v0.10=1120/1120; failed-v0.11=154/154")
    print(f"classification: protected={len(protected)} failed_predecessor={len(failed_paths)} retry_successor={len(successor)} unclassified=0 overlap=0 multimatch=0 stale=0")
    print(f"prospective output closure: {prospective['count']}/{prospective['count']} legal paths classify exactly once; {prospective.get('forbidden_count',0)}/{prospective.get('forbidden_count',0)} forbidden paths rejected")
    print("promotion-authoritative metrics: 16 (15 inherited + 1 stricter retry guardrail)")


if __name__ == "__main__":
    main()
