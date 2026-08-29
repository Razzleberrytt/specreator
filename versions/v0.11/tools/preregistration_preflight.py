from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
V11 = ROOT / "versions" / "v0.11"


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
        V11 / "candidate-schemas" / "execution-architecture-v1.candidate.schema.json",
        V11 / "candidate-schemas" / "lifecycle-checkpoint-v1.candidate.schema.json",
    ]
    schemas = [load_json(p) for p in schema_paths]
    for s in schemas:
        jsonschema.Draft202012Validator.check_schema(s)
    checkpoint = load_json(V11 / "LIFECYCLE-CHECKPOINT-DRAFT.json")
    list(jsonschema.Draft202012Validator(schemas[1]).iter_errors(checkpoint)) or None
    errors = list(jsonschema.Draft202012Validator(schemas[1]).iter_errors(checkpoint))
    if errors: die("lifecycle checkpoint schema errors: " + "; ".join(e.message for e in errors))

    # Execution fixture provenance, DAG, waves, critical paths
    exec_fixtures = load_jsonl(V11 / "candidate-fixtures" / "execution-architecture-corpus.jsonl")
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
    rules = load_json(V11 / "LIFECYCLE-TRANSITION-RULES.candidate.json")
    life = load_jsonl(V11 / "candidate-fixtures" / "lifecycle-continuation-corpus.jsonl")
    for f in life:
        got = resolve_lifecycle(rules, f["state"], f["blockers"])
        if got != f["expected_next_action"]:
            die(f"{f['fixture_id']} lifecycle action {got} != {f['expected_next_action']}")

    open_tokens = [b["transition_token"] for b in checkpoint["blockers"] if b["status"] == "OPEN"]
    checkpoint_action = resolve_lifecycle(rules, checkpoint["release_state"], open_tokens)
    if checkpoint_action != checkpoint["next_legal_action"]["action_token"]:
        die(f"checkpoint lifecycle action {checkpoint_action} != declared {checkpoint['next_legal_action']['action_token']}")

    # Exact evaluation universes
    u = load_json(V11 / "EVALUATION-UNIVERSES.json")["universes"]
    if u["execution_fixtures"]["members"] != [f["fixture_id"] for f in exec_fixtures]: die("execution fixture universe mismatch")
    if u["lifecycle_fixtures"]["members"] != [f["fixture_id"] for f in life]: die("lifecycle fixture universe mismatch")
    if u["critical_path_fixtures"]["members"] != [f["fixture_id"] for f in exec_fixtures]: die("critical-path universe mismatch")
    if u["integration_source_tasks"]["members"] != source_keys: die("integration source-task universe mismatch")
    if len(source_keys) != 23: die("integration source-task count mismatch")
    if u["effective_dependency_edges"]["count"] != 22: die("effective edge universe count mismatch")

    # Evaluation design must reference only declared exact universes.
    eval_design = load_json(V11 / "EVALUATION-DESIGN.json")
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
        "python versions/v0.11/tools/preregistration_preflight.py",
    ]
    if checkpoint["validation_profile"]["commands"] != expected_commands:
        die("validation profile commands drift")

    # Preserve exact first-review source artifacts and verify them against receiver hashes.
    review_root = V11 / "review-evidence" / "INDEPENDENT-PREFREEZE-001"
    review_evidence = load_json(review_root / "review-evidence.json")
    for rel, expected_hash in review_evidence["reviewed_artifact_hashes"].items():
        preserved = review_root / "source-package-artifacts" / rel
        if not preserved.is_file(): die(f"missing preserved reviewed artifact {rel}")
        if hashlib.sha256(preserved.read_bytes()).hexdigest() != expected_hash:
            die(f"preserved reviewed artifact hash mismatch {rel}")

    # Preserve independent re-review 002 evidence exactly as received.
    rereview_root = V11 / "review-evidence" / "INDEPENDENT-PREFREEZE-REREVIEW-002"
    rereview_manifest = load_json(rereview_root / "MANIFEST.json")
    for item in rereview_manifest["files"]:
        evidence_path = rereview_root / item["path"]
        if not evidence_path.is_file(): die(f"missing preserved rereview-002 evidence {item['path']}")
        raw = evidence_path.read_bytes()
        if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
            die(f"preserved rereview-002 evidence mismatch {item['path']}")

    # Parent suite exact collection universe
    parent = load_json(V11 / "PARENT-SUITE-UNIVERSE.json")
    cp = subprocess.run(["python", "-m", "pytest", "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True)
    if cp.returncode != 0: die("pytest collection failed")
    nodeids = [ln.strip() for ln in cp.stdout.splitlines() if "::" in ln and not ln.startswith("=")]
    if nodeids != parent["nodeids"] or len(nodeids) != 155: die("parent suite node-id universe drift")

    # Active regression exact snapshot
    active = []
    for line in (ROOT / "self-improvement" / "regressions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("status") == "active": active.append(rec["regression_id"])
    snap = load_json(V11 / "ACTIVE-REGRESSION-UNIVERSE.json")
    if active != [x["regression_id"] for x in snap["regressions"]] or len(active) != 24:
        die("active regression universe drift")

    # Frozen parent integrity exact all manifest entries
    man = load_json(ROOT / "versions" / "v0.10" / "MANIFEST.json")
    entries = man.get("content_hashes", {})
    if len(entries) != 1120: die(f"v0.10 manifest count {len(entries)} != 1120")
    for rel, expected in entries.items():
        p = ROOT / rel
        if not p.is_file(): die(f"missing frozen parent path {rel}")
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            die(f"frozen parent hash mismatch {rel}")

    # Exact package-wide immutable-boundary classification. Prefix inference is not authority.
    registry = load_json(V11 / "IMMUTABILITY-BOUNDARY-DRAFT.json")
    ownership = load_json(V11 / "SUCCESSOR-OWNERSHIP-UNIVERSE.json")
    protected = set(entries) | set(registry["protected_release_manifests"])
    if len(protected) != registry["protected_parent_selector"]["expected_unique_count"]:
        die(f"protected-parent unique count {len(protected)} != registry expectation")

    transient_dirs = {".pytest_cache", "__pycache__"}
    transient_suffixes = {".pyc"}
    package_paths = set()
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(part in transient_dirs for part in rel.parts) or p.suffix in transient_suffixes:
            continue
        package_paths.add(rel.as_posix())

    successor = set(ownership["members"])
    if len(successor) != ownership["member_count"]:
        die("successor ownership member_count mismatch or duplicate member")
    overlap = protected & successor
    unclassified = package_paths - protected - successor
    stale = successor - package_paths
    if overlap:
        die(f"immutable-boundary overlap: {sorted(overlap)[:10]}")
    if unclassified:
        die(f"immutable-boundary unclassified paths: {sorted(unclassified)[:10]}")
    if stale:
        die(f"immutable-boundary stale successor members: {sorted(stale)[:10]}")
    if package_paths != protected | successor:
        die("immutable-boundary package partition mismatch")
    iu = u["immutable_boundary_assertions"]
    if iu["protected_selector"]["expected_unique_count"] != len(protected):
        die("immutable-boundary protected universe count mismatch")
    if iu["successor_selector"]["count"] != len(successor):
        die("immutable-boundary successor universe count mismatch")
    if iu["expected_unclassified_count"] != 0 or iu["expected_overlap_count"] != 0 or iu["expected_stale_successor_member_count"] != 0:
        die("immutable-boundary zero-tolerance target drift")

    print("PASS: v0.11 preregistration preflight")
    print("candidate schemas: 2 valid")
    print("execution fixtures: 6; explicit provenance edges: 21; derived conflict edges: 1")
    print("lifecycle fixtures: 4 independently derived")
    print("integration source-task universe: 23")
    print("parent suite universe: 155 node IDs")
    print("active regression universe: 24 IDs")
    print("frozen parent integrity: 1120/1120")
    print(f"immutable-boundary classification: protected={len(protected)} successor={len(successor)} unclassified=0 overlap=0 stale=0")


if __name__ == "__main__":
    main()
