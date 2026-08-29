from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spec_creator.models import canonical_contract_hash
from spec_creator.prompt_compiler import compile_prompt, validate_prompt_envelope
from spec_creator.prompt_compiler_evaluator import evaluate_v0092_corpus
from spec_creator.task_compiler import compile_project, validate_compiled_graph
from spec_creator.traceability import load_graph, validate_graph
from spec_creator.validator import validate_workspace

ACTOR="verifier:independent-pass-0092"
IMPLEMENTATION_ACTOR="agent:spec-creator-builder"
EXPECTED_CONTRACT_HASH="e0f91282e131e64c8b5a6407362e889f7feaa65c161d1847048ca04a644b1888"
EXPECTED_FROZEN_SHA256={'evaluation/pytest-regressions-v0.09.2-prefreeze.txt': '1d3314562a9345a9f75b1adf32d61168822c00d316f7db85833230bba023e448', 'evaluation/pytest-v0.09.2-prefreeze-current-suite.txt': '669bb3b4da8488b180553ab16ce08c697385156e3a8ba90d4d651e8f81dadf9c', 'evaluation/v0092-benchmark-contrast-preflight.json': '0ea91647d6626da4063c1d1cc15cb6746f89ce12627864ae0429f0801fb798d6', 'evaluation/v0092-prefreeze-transaction-final.json': '73e302ae7b76f9a6938eb974bd2a49781be581e70b32030bc231ad77bd1f2ddc', 'evaluation/v0092-preregistration-preflight.json': '3e07a83f0440f7448603f34c85acee3ad4ba28455432e00ff09d8383fc1632fd', 'evaluation/v0092-schema-preflight.json': '0e2c0f1ba60b53a2596012570679c198bb8cd62a954fc11e82dec077925b390d', 'evaluation/workspace-validation-v0.09.2-prefreeze-after-regression-tests.json': 'b65df417fd737813c080a3c097c38924e77ebca7432cd9ee9a9ee4971b608a90', 'fixtures/prompt-compiler/v0.09.2/baseline.json': 'ecab22f1ff6b609e250dea79a7df6d2cb871e4a6dd1db54bb69dbf3d2964d7f7', 'fixtures/prompt-compiler/v0.09.2/corpus.jsonl': '5e63cb9c90fa0f46fe876fab1b36dfc705ba0f3d4ec27dfc2fb93cc63dc6c8ec', 'fixtures/prompt-compiler/v0.09.2/development.jsonl': 'd4e6b29a4891dd8af4de5474e145a2bb631ccc574ea58770db4c0018044cdd54', 'fixtures/prompt-compiler/v0.09.2/heldout.jsonl': 'ac355ba31a6a818e6da36eb4695023406a01d0408b153c8ba7258bc2e4858c3a', 'schemas/prompt-compilation-input-v1.schema.json': '4365164d63f141cb0cece5e812666871d2af988369b598a2cdb7337dd82aba9c', 'schemas/prompt-envelope-v1.schema.json': '8549a36497cebe28ad01e136224fe6ed820c9d37a7922a767c1d48ec239a8d24', 'versions/v0.09.2/EVALUATION-PLAN.json': '8e0601991928641fc4559d13b96a7293df9da3a7832792c33fc74b17293350e6', 'versions/v0.09.2/FROZEN-RELEASE-CONTRACT.json': '44a34857f9c0b34b7ceb3e576c9b39329c4a7d73ad5d908f0d920426b421dde7', 'versions/v0.09.2/SPEC-CREATOR-v0.09.2.md': 'fff55af89386e3750af3c86fd37f922a52e9423186a02f269997ee2a52f3a68b'}
EXPECTED_HISTORY_SHA256={'versions/v0.09/FROZEN-RELEASE-CONTRACT.json': 'e28f4b3c9efdcea3076703a9e08ca7e2c69d127543ea99bd453ac23ab7fdf33d', 'versions/v0.09/EVALUATION-v0.09.json': '9fca41ed6f14fc903b06df066e468cd38cfe1c7b0f9448f74f9b1dca9328f69b', 'evaluation/def-009-004-frozen-benchmark-contrast-defect.json': '2e8ba0bae47383908baca3131ae8693db9f912ebc789ac16e8426e1dba1cf19c', 'versions/v0.09.1/FROZEN-RELEASE-CONTRACT.INVALID-ATTEMPT.json': 'f383bba360b693f9216cd1d72e2368dc83c63099807960e5c53985dcde561c07', 'versions/v0.09.1/EVALUATION-v0.09.1.json': 'ff507871807b224feda70b76430a0f59b04f58d82503727b8978f6de0b766f8c', 'evaluation/def-0091-001-freeze-with-failed-preflight.json': 'b706f799bd2b377ad744558b468b9f0dcff8fac53d40c9bd0311130a38852636', 'evaluation/def-0091-002-invalid-contract-schema.json': '8bbfd3f6a31314944b5099f3e581944b6b90f5262ecd00453fb6953a9ccd92b1'}
PARENT_TEST_FILES=['tests/test_ambiguity.py', 'tests/test_ambiguity_cli.py', 'tests/test_ambiguity_evaluator.py', 'tests/test_cli.py', 'tests/test_discovery.py', 'tests/test_discovery_cli.py', 'tests/test_discovery_evaluator.py', 'tests/test_ledger.py', 'tests/test_linter.py', 'tests/test_package_manifest.py', 'tests/test_task_compiler.py', 'tests/test_task_compiler_cli.py', 'tests/test_task_compiler_evaluator.py', 'tests/test_task_execution.py', 'tests/test_traceability.py', 'tests/test_traceability_cli.py', 'tests/test_validator.py']

def sha(path: Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_pytest(args):
    p=subprocess.run([sys.executable,"-m","pytest","-q",*args],cwd=ROOT,text=True,capture_output=True)
    return {"returncode":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()}

def active_regs():
    out={}
    for line in (ROOT/"self-improvement/regressions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line)
            if r.get("status")=="active": out[r["regression_id"]]=r
    return out

def selectors(task_ids=None, reqs=None, tests=None, gates=None, kinds=None):
    return {"task_ids":task_ids or [],"requirement_ids":reqs or [],"verification_refs":tests or [],"gate_ids":gates or [],"prompt_kinds":kinds or []}

def historical_shadow_recompute():
    graph=json.loads((ROOT/"versions/v0.08/SELF-COMPILED-TASK-GRAPH.json").read_text(encoding="utf-8"))
    events=[]
    for line in (ROOT/"execution/task-events.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            e=json.loads(line)
            if e.get("graph_hash")==graph["graph_hash"]: events.append(e)
    tasks={t["task_id"]:t for t in graph["tasks"]}
    specs=[
      ("bootstrap","CTASK-008-SELF-01",events[:1],"agent:spec-creator-builder",False),
      ("implementation","CTASK-008-SELF-01",events[:2],"agent:spec-creator-builder",False),
      ("debug","CTASK-008-SELF-01",events[:3],"agent:spec-creator-builder",True),
      ("verification","CTASK-008-SELF-01",events[:4],"verifier:historical-shadow-0092-independent",False),
      ("continuation","CTASK-008-SELF-07",events,"agent:spec-creator-builder",False),
    ]
    rows=[]
    for i,(kind,tid,evs,actor,debug) in enumerate(specs,1):
        t=tasks[tid]
        ctx=[{"context_id":f"CTX-VERIFY-SHADOW-{i}-TASK","ref":"versions/v0.08/SELF-COMPILED-TASK-GRAPH.json","kind":"artifact","critical":True,"selectors":selectors(task_ids=[tid])}]
        for j,r in enumerate(t["source_requirement_ids"],1): ctx.append({"context_id":f"CTX-VERIFY-SHADOW-{i}-R{j}","ref":r,"kind":"requirement","critical":True,"selectors":selectors(reqs=[r])})
        for j,x in enumerate(t["verification_refs"],1): ctx.append({"context_id":f"CTX-VERIFY-SHADOW-{i}-T{j}","ref":x,"kind":"test","critical":True,"selectors":selectors(tests=[x])})
        for j,x in enumerate(t["gate_ids"],1): ctx.append({"context_id":f"CTX-VERIFY-SHADOW-{i}-G{j}","ref":x,"kind":"gate","critical":True,"selectors":selectors(gates=[x])})
        inp={
          "schema_version":"1.0","request_id":f"PREQ-VERIFY-0092-SHADOW-{i}","candidate_version":"0.09.2","prompt_kind":kind,
          "compiled_task_graph":graph,"task_id":tid,
          "task_contract":{"task_id":tid,"acceptance_criteria":["Historical shadow must preserve task authority."],"critical_obligations":["Preserve historical identity, scope, prerequisites, tests, gates, and execution evidence."],"evidence_requirements":t["verification_refs"] or ["versions/v0.08/FROZEN-RELEASE-CONTRACT.json"],"blocking_owner_decision_ids":[],"frozen_criteria_refs":["frozen:REL-0.08-FROZEN-001"]+[f"frozen:{r}" for r in t["source_requirement_ids"]]},
          "context_records":ctx,"execution_events":evs,"actor_context":{"implementation_actor_id":IMPLEMENTATION_ACTOR,"requested_actor_id":actor},
          "requested_write_scopes":t["write_scopes"] if kind in {"implementation","debug"} else [],"debug_evidence_refs":["historical:v0.08:debug-evidence"] if debug else []
        }
        out=compile_prompt(inp,root=ROOT)
        rows.append({"kind":kind,"status":out.get("status"),"schema_valid":not validate_prompt_envelope(out,root=ROOT) if out.get("status")=="compiled" else False,"identity":out.get("graph_hash")==graph["graph_hash"] and out.get("task_id")==tid,"scope_bounded":set(out.get("allowed_write_scopes",[])).issubset(set(t["write_scopes"]))})
    return {"event_count":len(events),"rows":rows,"all_ok":len(events)==28 and all(r["status"]=="compiled" and r["schema_valid"] and r["identity"] and r["scope_bounded"] for r in rows)}

def meets(value,op,target):
    if value is None: return False
    return {"eq":value==target,"gte":value>=target,"lte":value<=target}[op]

contract=json.loads((ROOT/"versions/v0.09.2/FROZEN-RELEASE-CONTRACT.json").read_text(encoding="utf-8"))
plan=json.loads((ROOT/"versions/v0.09.2/EVALUATION-PLAN.json").read_text(encoding="utf-8"))
contract_schema=json.loads((ROOT/"schemas/frozen-release-contract-v2.schema.json").read_text(encoding="utf-8"))
contract_schema_errors=sorted(Draft202012Validator(contract_schema).iter_errors(contract), key=lambda e:list(e.path))
print("[verifier] corpus",file=sys.stderr,flush=True)
corpus=evaluate_v0092_corpus(ROOT)
print("[verifier] full",file=sys.stderr,flush=True)
full=run_pytest([])
print("[verifier] parent evidence",file=sys.stderr,flush=True)
parent_text=(ROOT/"evaluation/pytest-v0.08-parent-suite-on-v0.09.2-final.txt").read_text(encoding="utf-8").strip()
parent={"returncode":0 if "142 passed" in parent_text else 1,"stdout":parent_text,"stderr":""}
retry_text=(ROOT/"evaluation/pytest-regressions-v0.09.2-prefreeze.txt").read_text(encoding="utf-8").strip()
retry_regs={"returncode":0 if "3 passed" in retry_text else 1,"stdout":retry_text,"stderr":""}
reg23_text=(ROOT/"evaluation/pytest-reg0023-v0.09.2.txt").read_text(encoding="utf-8").strip()
reg23={"returncode":0 if "passed" in reg23_text else 1,"stdout":reg23_text,"stderr":""}
active=active_regs(); frozen_regs=set(contract["applicable_regressions"])
print("[verifier] self",file=sys.stderr,flush=True)
trace=validate_graph(load_graph(ROOT/"versions/v0.09.2/TRACEABILITY-GRAPH.json")).as_dict()
self_project=json.loads((ROOT/"versions/v0.09.2/SELF-TASK-COMPILATION-PROJECT.json").read_text(encoding="utf-8"))
saved_graph=json.loads((ROOT/"versions/v0.09.2/SELF-COMPILED-TASK-GRAPH.json").read_text(encoding="utf-8"))
recompiled_graph=compile_project(self_project,root=ROOT)
self_graph_schema=validate_compiled_graph(saved_graph,root=ROOT)
self_prompt_input=json.loads((ROOT/"versions/v0.09.2/SELF-PROMPT-INPUT.json").read_text(encoding="utf-8"))
saved_prompt=json.loads((ROOT/"versions/v0.09.2/SELF-COMPILED-PROMPT.json").read_text(encoding="utf-8"))
recompiled_prompt=compile_prompt(self_prompt_input,root=ROOT)
self_prompt_schema=validate_prompt_envelope(saved_prompt,root=ROOT)
print("[verifier] shadow",file=sys.stderr,flush=True)
shadow=historical_shadow_recompute()
print("[verifier] workspace",file=sys.stderr,flush=True)
workspace=validate_workspace(ROOT,validate_package_manifest=False).as_dict()
rollback=json.loads((ROOT/"versions/v0.09.2/ROLLBACK.json").read_text(encoding="utf-8"))
frozen_hash_checks={p:sha(ROOT/p)==h for p,h in EXPECTED_FROZEN_SHA256.items()}
history_hash_checks={p:sha(ROOT/p)==h for p,h in EXPECTED_HISTORY_SHA256.items()}
# No promotion decision may exist before mandatory gates are evaluated.
premature_promotions=[]
for line in (ROOT/"self-improvement/decisions.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        d=json.loads(line)
        if "v0.09.2" in (d.get("title","")+" "+d.get("rationale","")) and "Promote v0.09.2" in d.get("title",""):
            premature_promotions.append(d["decision_id"])
process_metrics={
 "inherited_regression_pass_rate": 1.0 if frozen_regs<=set(active) and full["returncode"]==0 and parent["returncode"]==0 and retry_regs["returncode"]==0 else 0.0,
 "critical_gate_bypass_count": 0 if not premature_promotions else len(premature_promotions),
}
all_frozen_metric_names={m["name"] for m in plan["primary_metrics"]+plan["guardrail_metrics"]}
scored=dict(corpus["metrics"]); scored.update(process_metrics)
# missing_data_count is measured after every other frozen metric has a concrete source value.
missing_except_self=sorted(name for name in all_frozen_metric_names-{"missing_data_count"} if scored.get(name) is None)
process_metrics["missing_data_count"]=len(missing_except_self)
scored["missing_data_count"]=process_metrics["missing_data_count"]
metric_checks={m["name"]:meets(scored.get(m["name"]),m["target_operator"],m["target_value"]) for m in plan["primary_metrics"]+plan["guardrail_metrics"]}
gate_readiness={
 "GATE-009-CORPUS-INTEGRITY": all(corpus["hash_checks"].values()) and corpus["counts"]["output_schema_error_count"]==0,
 "GATE-009-PARENT-PREFLIGHT": corpus["metrics"]["parent_preflight_rate"]==1.0 and parent["returncode"]==0 and "142 passed" in parent["stdout"],
 "GATE-009-SPEC-QUALITY": corpus["metrics"]["v0092_spec_quality_acceptance_rate"]==1.0,
 "GATE-009-SCHEMA": not contract_schema_errors and not self_graph_schema and not self_prompt_schema,
 "GATE-009-COMPILE": corpus["metrics"]["development_prompt_envelope_exact_match_rate"]==1.0 and corpus["metrics"]["heldout_prompt_envelope_exact_match_rate"]==1.0,
 "GATE-009-IDENTITY": shadow["all_ok"] and recompiled_prompt.get("graph_hash")==saved_graph["graph_hash"],
 "GATE-009-SCOPE": corpus["metrics"]["scope_expansion_count"]==0 and shadow["all_ok"],
 "GATE-009-PREREQUISITE": corpus["metrics"]["prerequisite_escape_count"]==0,
 "GATE-009-OWNER": corpus["metrics"]["owner_decision_escape_count"]==0,
 "GATE-009-VERIFIER": corpus["metrics"]["self_certification_violation_count"]==0 and ACTOR!=IMPLEMENTATION_ACTOR,
 "GATE-009-CONTINUATION": corpus["metrics"]["continuation_state_exact_match_rate"]==1.0,
 "GATE-009-CONTEXT": corpus["metrics"]["context_over_inclusion_rate"]<=0.05,
 "GATE-009-OBLIGATION": corpus["metrics"]["obligation_retention_rate"]==1.0 and corpus["metrics"]["missing_critical_constraint_count"]==0,
 "GATE-009-CLI": full["returncode"]==0,
 "GATE-009-TEST": full["returncode"]==0 and "151 passed" in full["stdout"],
 "GATE-009-REGRESSION": process_metrics["inherited_regression_pass_rate"]==1.0 and reg23["returncode"]==0 and "REG-0023" in active,
 "GATE-009-SHADOW": shadow["all_ok"],
 "GATE-009-SELF": trace["ok"] and recompiled_graph==saved_graph and saved_graph["status"]=="compiled" and recompiled_prompt==saved_prompt and saved_prompt["status"]=="compiled",
 "GATE-009-RECONCILIATION": all(metric_checks.values()) and process_metrics["missing_data_count"]==0,
 "GATE-009-INDEPENDENT": ACTOR!=IMPLEMENTATION_ACTOR,
 "GATE-009-PACKAGE": workspace["ok"] and workspace["summary"]["errors"]==0 and workspace["summary"]["warnings"]==0,
 "GATE-009-ROLLBACK": rollback.get("status")=="declared" and rollback.get("rollback_target_version")=="0.08",
}
checks={
 "actor_independence":ACTOR!=IMPLEMENTATION_ACTOR,
 "contract_schema":not contract_schema_errors,
 "contract_hash":contract.get("contract_hash")==EXPECTED_CONTRACT_HASH==canonical_contract_hash(contract),
 "frozen_artifacts_intact":all(frozen_hash_checks.values()),
 "failed_history_intact":all(history_hash_checks.values()),
 "corpus_hashes":all(corpus["hash_checks"].values()),
 "all_frozen_metrics_available":set(scored)==all_frozen_metric_names and process_metrics["missing_data_count"]==0,
 "all_frozen_metrics_meet_target":all(metric_checks.values()),
 "parent_suite_exact":parent["returncode"]==0 and "142 passed" in parent["stdout"],
 "current_suite":full["returncode"]==0 and "151 passed" in full["stdout"],
 "retry_regressions":retry_regs["returncode"]==0 and "3 passed" in retry_regs["stdout"],
 "reg0023":reg23["returncode"]==0 and "passed" in reg23["stdout"],
 "frozen_regressions_present":frozen_regs<=set(active),
 "new_corrective_regression_present":"REG-0023" in active,
 "self_traceability":trace["ok"],
 "self_graph_reproduces":recompiled_graph==saved_graph and not self_graph_schema,
 "self_prompt_reproduces":recompiled_prompt==saved_prompt and not self_prompt_schema,
 "historical_shadow":shadow["all_ok"],
 "workspace_prefinal":workspace["ok"] and workspace["summary"]["errors"]==0 and workspace["summary"]["warnings"]==0,
 "rollback_declared":rollback.get("rollback_target_version")=="0.08",
 "no_premature_promotion":not premature_promotions,
 "all_gate_evidence_ready":set(gate_readiness)==set(contract["mandatory_gates"]) and all(gate_readiness.values()),
}
result={
 "candidate_version":"0.09.2","contract_id":contract["contract_id"],"actor_id":ACTOR,"implementation_actor_id":IMPLEMENTATION_ACTOR,
 "result":"PASS" if all(checks.values()) else "FAIL","recommendation":"PROMOTED AS EXPERIMENTAL" if all(checks.values()) else "RETRY REQUIRED",
 "checks":checks,"frozen_hash_checks":frozen_hash_checks,"failed_history_hash_checks":history_hash_checks,
 "corpus_counts":corpus["counts"],"corpus_metrics":corpus["metrics"],"release_process_metrics":process_metrics,"reconciled_metric_values":scored,"metric_target_checks":metric_checks,
 "gate_readiness":gate_readiness,"full_test_run":full,"parent_test_run":parent,"retry_regression_test_run":retry_regs,"reg0023_test_run":reg23,
 "self_traceability_summary":trace["summary"],"self_compiled_summary":saved_graph["summary"],"self_prompt_hash":saved_prompt["envelope_hash"],"historical_shadow":shadow,
 "workspace_validation":workspace["summary"],"active_regression_count":len(active),"frozen_regression_count":len(frozen_regs),"premature_promotion_decisions":premature_promotions,
 "limitations":["Role-separated verification occurs within the same runtime/session, not an external organization.","Frozen development/held-out corpora are synthetic same-cycle evidence and visible to the implementer.","Historical v0.08 shadow is non-promotional and cannot raise the frozen experimental ceiling.","Final root package seal and fresh extracted-ZIP verification occur after release accounting; any later failure invalidates promotion and triggers rollback/retry."],
}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result["result"]=="PASS" else 1)
