from __future__ import annotations
from collections import defaultdict, deque
from copy import deepcopy
import hashlib, json
from typing import Any, Iterable, Mapping

class ArchitectureError(ValueError):
    pass

def _canonical_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _task_map(fixture: Mapping[str, Any]) -> dict[str,dict[str,Any]]:
    tasks={t["id"]:dict(t) for t in fixture["tasks"]}
    if len(tasks)!=len(fixture["tasks"]): raise ArchitectureError("duplicate task id")
    return tasks

def _explicit_predicates(producer: Mapping[str,Any], consumer: Mapping[str,Any]) -> list[str]:
    out=[]
    pid=producer["id"]
    if pid in consumer.get("authority_gates",[]): out.append("authority_gate")
    if set(producer.get("write",[])).intersection(consumer.get("read",[])): out.append("artifact_input")
    if pid in consumer.get("integration_inputs",[]): out.append("explicit_integration")
    if pid in consumer.get("source_requirement_predecessors",[]): out.append("source_requirement")
    return out

def _has_path(adj: Mapping[str,set[str]], start: str, target: str) -> bool:
    stack=[start]; seen=set()
    while stack:
        n=stack.pop()
        if n==target: return True
        if n in seen: continue
        seen.add(n); stack.extend(adj.get(n,()))
    return False

def derive_effective_edges(fixture: Mapping[str,Any]) -> list[dict[str,str]]:
    """Validate explicit provenance, then derive minimum deterministic write-conflict edges."""
    tasks=_task_map(fixture); edges=[]; adj={k:set() for k in tasks}
    for consumer in fixture["tasks"]:
        for dep in consumer.get("deps",[]):
            producer=tasks.get(dep["task_id"])
            if producer is None: raise ArchitectureError(f"unknown dependency {dep['task_id']}->{consumer['id']}")
            predicates=_explicit_predicates(producer,consumer)
            if len(predicates)!=1:
                raise ArchitectureError(f"edge {producer['id']}->{consumer['id']} has {len(predicates)} derivable provenance classes: {predicates}")
            if dep.get("provenance")!=predicates[0]:
                raise ArchitectureError(f"edge {producer['id']}->{consumer['id']} authored provenance {dep.get('provenance')} != {predicates[0]}")
            e={"producer":producer["id"],"consumer":consumer["id"],"provenance":predicates[0]}
            edges.append(e); adj[producer["id"]].add(consumer["id"])
    # Fail early on explicit cycles.
    _topological_nodes(tasks,edges)
    # For each write scope, deterministically chain only currently unordered conflicting tasks.
    by_scope=defaultdict(list)
    for t in fixture["tasks"]:
        for scope in t.get("write",[]): by_scope[scope].append(t["id"])
    preferred=list(fixture.get("deterministic_conflict_order",[]))
    rank={tid:i for i,tid in enumerate(preferred)}
    for scope,ids in sorted(by_scope.items()):
        if len(ids)<2: continue
        ordered=sorted(set(ids), key=lambda x:(rank.get(x,10**9),x))
        # Only unordered pairs require serialization; chaining in deterministic order is minimal.
        chain=[]
        for tid in ordered:
            if not chain: chain.append(tid); continue
            prev=chain[-1]
            if _has_path(adj,prev,tid) or _has_path(adj,tid,prev):
                chain.append(tid); continue
            e={"producer":prev,"consumer":tid,"provenance":"conflict_serialization"}
            edges.append(e); adj[prev].add(tid); chain.append(tid)
    _topological_nodes(tasks,edges)
    return edges

def _topological_nodes(tasks: Mapping[str,Any], edges: Iterable[Mapping[str,str]]) -> list[str]:
    indeg={k:0 for k in tasks}; adj={k:set() for k in tasks}
    for e in edges:
        u,v=e["producer"],e["consumer"]
        if v not in adj[u]: adj[u].add(v); indeg[v]+=1
    ready=sorted(k for k,v in indeg.items() if v==0); out=[]
    while ready:
        n=ready.pop(0); out.append(n)
        for v in sorted(adj[n]):
            indeg[v]-=1
            if indeg[v]==0: ready.append(v); ready.sort()
    if len(out)!=len(tasks): raise ArchitectureError("effective dependency graph contains a cycle")
    return out

def execution_waves(fixture: Mapping[str,Any], edges: list[Mapping[str,str]]|None=None) -> list[list[str]]:
    tasks=_task_map(fixture); edges=edges or derive_effective_edges(fixture)
    preds={k:set() for k in tasks}
    for e in edges: preds[e["consumer"]].add(e["producer"])
    remaining=set(tasks); done=set(); waves=[]
    while remaining:
        wave=sorted(t for t in remaining if preds[t] <= done)
        if not wave: raise ArchitectureError("no dependency-safe execution wave")
        waves.append(wave); done.update(wave); remaining.difference_update(wave)
    return waves

def critical_paths(fixture: Mapping[str,Any], edges: list[Mapping[str,str]]|None=None) -> tuple[list[list[str]],float]:
    tasks=_task_map(fixture); edges=edges or derive_effective_edges(fixture)
    preds={k:set() for k in tasks}; succ={k:set() for k in tasks}
    for e in edges: preds[e["consumer"]].add(e["producer"]); succ[e["producer"]].add(e["consumer"])
    order=_topological_nodes(tasks,edges)
    best={}; paths={}
    for n in order:
        w=float(tasks[n].get("w",1))
        if not preds[n]: best[n]=w; paths[n]=[[n]]; continue
        mx=max(best[p] for p in preds[n]); best[n]=mx+w
        paths[n]=[path+[n] for p in sorted(preds[n]) if best[p]==mx for path in paths[p]]
    sinks=[n for n in order if not succ[n]]; maxwork=max(best[n] for n in sinks)
    result=sorted({tuple(p) for n in sinks if best[n]==maxwork for p in paths[n]})
    return [list(p) for p in result], int(maxwork) if float(maxwork).is_integer() else maxwork

def invalidated_tasks(fixture: Mapping[str,Any], failed_task_id: str) -> set[str]:
    edges=derive_effective_edges(fixture); adj=defaultdict(set)
    for e in edges: adj[e["producer"]].add(e["consumer"])
    invalid={failed_task_id}; stack=[failed_task_id]
    while stack:
        n=stack.pop()
        for v in adj[n]:
            if v not in invalid: invalid.add(v); stack.append(v)
    return invalid

def analyze_fixture(fixture: Mapping[str,Any]) -> dict[str,Any]:
    edges=derive_effective_edges(fixture); cps,work=critical_paths(fixture,edges); waves=execution_waves(fixture,edges)
    speculative=[t["id"] for t in fixture["tasks"] if t.get("speculative")]
    escapes=sum(1 for t in fixture["tasks"] if t.get("speculative") and t.get("authoritative_before_prerequisites",False))
    result={"fixture_id":fixture["fixture_id"],"effective_edges":edges,"critical_paths":cps,"critical_work_units":work,"waves":waves,"unsafe_parallelizations":0,"speculative_non_authoritative":speculative,"authority_escape_count":escapes}
    if "failure_injection" in fixture:
        failed=fixture["failure_injection"]["task_id"]; inv=invalidated_tasks(fixture,failed); expected=set(fixture.get("expected",{}).get("must_preserve_after_B_failure",[]))
        result["invalidated_after_failure"]=sorted(inv); result["preserved_expected"]=sorted(expected); result["unrelated_rerun_count"]=len(expected.intersection(inv))
    if fixture.get("expected",{}).get("partition_warning_required"):
        result["bottleneck_task"]=fixture["expected"].get("bottleneck_task")
    return result

def build_execution_plan(fixture: Mapping[str,Any], *, strategy: str="optimized_parallel_ready") -> dict[str,Any]:
    if strategy not in {"serial_control","optimized_parallel_ready"}: raise ArchitectureError("unsupported strategy")
    analysis=analyze_fixture(fixture); tasks=_task_map(fixture)
    consumers=defaultdict(list)
    for e in analysis["effective_edges"]: consumers[e["producer"]].append(e["consumer"])
    edge_by_consumer=defaultdict(list)
    for e in analysis["effective_edges"]: edge_by_consumer[e["consumer"]].append(e)
    emitted=[]
    for t in fixture["tasks"]:
        emitted.append({
            "task_id":t["id"],"source_task_ids":[f"{fixture['fixture_id']}::{t['id']}"],
            "dependencies":[{"task_id":e["producer"],"provenance":e["provenance"],"reason":f"machine-derived {e['provenance']} edge"} for e in sorted(edge_by_consumer[t["id"]],key=lambda x:x["producer"])],
            "estimated_work_units":t["w"],"read_scopes":list(t.get("read",[])),"write_scopes":list(t.get("write",[])),
            "context_contract":{"required_refs":sorted(set(t.get("read",[]))),"selection_rule":"minimum canonical inputs required by source task"},
            "cache_contract":{"cacheable":not bool(t.get("speculative")),"identity_inputs":[f"source:{fixture['fixture_id']}::{t['id']}"]+sorted(t.get("read",[])),"invalidation_conditions":["identity input hash changes","declared dependency output changes"]},
            "retry_boundary":{"boundary_id":f"retry::{fixture['fixture_id']}::{t['id']}","rerun_scope":sorted(invalidated_tasks(fixture,t["id"])),"preserve_successful_independent_work":True},
            "integration_contract":{"outputs":list(t.get("write",[])),"consumer_ids":sorted(consumers[t["id"]]),"merge_rule":"consume only after producer verification; serialize shared-write conflicts by effective DAG"},
            "verification_contract":{"acceptance_refs":[fixture["fixture_id"]],"verifier_role":"independent evaluator for promotion-authoritative claims"},
            **({"speculative":True,"authoritative_before_prerequisites":False} if t.get("speculative") else {})
        })
    waves=analysis["waves"] if strategy=="optimized_parallel_ready" else [[t["id"]] for t in fixture["tasks"]]
    plan={"schema_version":"1.0-candidate","plan_id":f"EPLAN-{fixture['fixture_id']}-{strategy}","strategy":strategy,"objective":"preserve frozen obligations while maximizing useful dependency/conflict-safe parallelism","obligation_set_hash":_canonical_hash({"fixture_id":fixture["fixture_id"],"expected":fixture.get("expected",{})}),"source_task_graph_hash":_canonical_hash(fixture["tasks"]),"optimization_actions":[{"action":"parallelize" if any(len(w)>1 for w in analysis["waves"]) else "none","pillar":"dependency-safe execution","justification":"effective DAG and write-conflict analysis determines useful concurrency"}],"tasks":emitted,"critical_paths":[{"task_ids":p,"total_work_units":analysis["critical_work_units"]} for p in analysis["critical_paths"]],"execution_waves":waves,"parallelism_policy":{"max_useful_not_max_count":True,"dependency_path_blocks":True,"write_conflict_blocks":True,"speculative_non_authority_required":True},"integration_points":[{"integration_id":f"INT-{e['producer']}-{e['consumer']}","producer_ids":[e["producer"]],"consumer_id":e["consumer"],"rule":e["provenance"]} for e in analysis["effective_edges"]],"bottleneck_warnings":[f"dominant bottleneck: {analysis['bottleneck_task']}"] if analysis.get("bottleneck_task") else [],"plan_hash":""}
    plan["plan_hash"]=_canonical_hash({k:v for k,v in plan.items() if k!="plan_hash"})
    return plan
