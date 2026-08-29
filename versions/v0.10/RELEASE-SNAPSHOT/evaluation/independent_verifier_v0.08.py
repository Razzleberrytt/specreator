from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from spec_creator.ambiguity import analyze_ambiguity_file
from spec_creator.discovery import plan_discovery_file
from spec_creator.linter import lint_file
from spec_creator.models import canonical_contract_hash
from spec_creator.task_compiler import compile_project, validate_compiled_graph
from spec_creator.task_compiler_evaluator import evaluate_v008_corpus
from spec_creator.task_execution import replay_task_events_file
from spec_creator.traceability import load_graph, validate_graph
from spec_creator.validator import validate_workspace

ACTOR='verifier:independent-pass-008'
IMPLEMENTATION_ACTOR='agent:spec-creator-builder'
EXPECTED={
 'contract':'460333b394380c6fbc9633ee86fcbff1e91e0c2105b681e51bb9acf5d1b92ec6',
 'spec':'8b078db7dfb566cf83ac563d5ce7ef60c1f456145c2a8bc6077bdcb7698c4ddd',
 'plan':'93917ef51cd4ca06db01bbbbe89ec8e448ec8c44cc0ea0ae79f419c474d423b5',
 'corpus':'abec3d8c23f2eec3a4a721dc254ea72fbbedafe1f4ea6e9f19722eda733e61ef',
 'heldout':'da9ee47f5fadf77911d512e43a0ac17dd20404283130e2be513f7744d06fcae1',
 'execution':'8ffa30d23ed346a1e4c5ebb0e458babd9e2b997cdcd2284bfbdbb67bf71710eb',
 'preflight':'40a46aaec5c098b144e90be5b428a595c23b440d0410a314f7d97a02d05fee33',
 'project_schema':'88b54a4415a829d1c8ee55a29e5ddf9de470e227b18185506a8531d173244bcf',
 'compiled_schema':'c5678475b219c29fc383ae789410448188144874e73b1c309798dfafe36dcde0',
 'execution_schema':'c00c68c6c10561471ccc1d132fa597c477a185a6ce07f7a3b4a763cdeb256173',
}
INHERITED_FILES=[
 'tests/test_ambiguity.py','tests/test_ambiguity_cli.py','tests/test_ambiguity_evaluator.py','tests/test_cli.py',
 'tests/test_discovery.py','tests/test_discovery_cli.py','tests/test_discovery_evaluator.py','tests/test_ledger.py',
 'tests/test_linter.py','tests/test_package_manifest.py','tests/test_traceability.py','tests/test_traceability_cli.py','tests/test_validator.py'
]

def sha(path: Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def run_pytest(args):
 p=subprocess.run([sys.executable,'-m','pytest','-q',*args],cwd=ROOT,text=True,capture_output=True)
 return {'returncode':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
def active_regs():
 out=set()
 for line in (ROOT/'self-improvement/regressions.jsonl').read_text().splitlines():
  if line.strip():
   r=json.loads(line)
   if r.get('status')=='active': out.add(r['regression_id'])
 return out

contract=json.loads((ROOT/'versions/v0.08/FROZEN-RELEASE-CONTRACT.json').read_text())
contract_hash=canonical_contract_hash(contract)
eval_result=evaluate_v008_corpus(ROOT)
preflight=json.loads((ROOT/'evaluation/v008-preregistration-preflight.json').read_text())
spec_lint=lint_file(ROOT/'versions/v0.08/SPEC-CREATOR-v0.08.md').as_dict()
spec_amb=analyze_ambiguity_file(ROOT/'versions/v0.08/SPEC-CREATOR-v0.08.md').as_dict()
spec_disc=plan_discovery_file(ROOT/'versions/v0.08/SPEC-CREATOR-v0.08.md').as_dict()
trace=validate_graph(load_graph(ROOT/'versions/v0.08/TRACEABILITY-GRAPH.json')).as_dict()
project=json.loads((ROOT/'versions/v0.08/SELF-TASK-COMPILATION-PROJECT.json').read_text())
saved_compiled=json.loads((ROOT/'versions/v0.08/SELF-COMPILED-TASK-GRAPH.json').read_text())
recompiled=compile_project(project,root=ROOT)
compiled_schema=validate_compiled_graph(saved_compiled,root=ROOT)
replay=replay_task_events_file(ROOT/'versions/v0.08/SELF-COMPILED-TASK-GRAPH.json',ROOT/'execution/task-events.jsonl',root=ROOT)
shadow=json.loads((ROOT/'evaluation/shadow-task-compiler-v0.08-final.json').read_text())
workspace=validate_workspace(ROOT,validate_package_manifest=False).as_dict()
full=run_pytest([])
inherited=run_pytest([*INHERITED_FILES,'-k','not execution_ledger_uses_compiled_stable_id_namespace_regression'])
newregs=run_pytest([
 'tests/test_task_compiler.py::test_stale_discovery_plan_cannot_hide_owner_decision_regression',
 'tests/test_task_compiler.py::test_duplicate_task_metadata_is_rejected_before_dict_overwrite_regression',
 'tests/test_validator.py::test_execution_ledger_uses_compiled_stable_id_namespace_regression'])
active=active_regs(); frozen=set(contract['applicable_regressions']); corrective={'REG-0017','REG-0018','REG-0019'}
m=eval_result['metrics']
checks={
 'actor_independence':ACTOR!=IMPLEMENTATION_ACTOR,
 'contract_hash':contract_hash==EXPECTED['contract']==contract.get('contract_hash'),
 'spec_hash':sha(ROOT/'versions/v0.08/SPEC-CREATOR-v0.08.md')==EXPECTED['spec'],
 'plan_hash':sha(ROOT/'versions/v0.08/EVALUATION-PLAN.json')==EXPECTED['plan'],
 'corpus_hash':sha(ROOT/'fixtures/task-compiler/v0.08/corpus.jsonl')==EXPECTED['corpus'],
 'heldout_hash':sha(ROOT/'fixtures/task-compiler/v0.08/heldout.jsonl')==EXPECTED['heldout'],
 'execution_corpus_hash':sha(ROOT/'fixtures/task-compiler/v0.08/execution-corpus.jsonl')==EXPECTED['execution'],
 'preflight_hash':sha(ROOT/'evaluation/v008-preregistration-preflight.json')==EXPECTED['preflight'],
 'project_schema_hash':sha(ROOT/'schemas/task-compilation-project-v1.schema.json')==EXPECTED['project_schema'],
 'compiled_schema_hash':sha(ROOT/'schemas/compiled-task-graph-v1.schema.json')==EXPECTED['compiled_schema'],
 'execution_schema_hash':sha(ROOT/'schemas/task-execution-event-v1.schema.json')==EXPECTED['execution_schema'],
 'parent_preflight':preflight['summary']['all_ok'] and preflight['summary']['compiler_preflight_rate']==1.0,
 'spec_quality':spec_lint['summary']['unsuppressed']==0 and spec_amb['summary']['findings']==0 and spec_disc['summary']['question_batches']==0,
 'accepted_exact':m['accepted_task_graph_exact_match_rate']>=0.95,
 'heldout_exact':m['heldout_task_graph_exact_match_rate']>=0.95,
 'negative_exact':m['negative_case_classification_accuracy']==1.0,
 'dependency_provenance':m['dependency_provenance_accuracy']==1.0,
 'critical_trace':m['critical_ready_task_trace_completeness_rate']==1.0,
 'parallelization':m['parallelization_decision_accuracy']==1.0,
 'unresolved_escape':m['unresolved_decision_escape_count']==0,
 'unsafe_parallel':m['unsafe_parallelization_count']==0,
 'oversized_escape':m['oversized_ready_task_count']==0,
 'cycle_escape':m['dependency_cycle_escape_count']==0,
 'invented_dependency':m['invented_dependency_count']==0,
 'execution_exact':m['execution_stream_exact_match_rate']==1.0,
 'invalid_execution_escape':m['invalid_execution_escape_count']==0,
 'deterministic_repeat':m['deterministic_repeat_rate']==1.0,
 'self_traceability':trace['ok'] and trace['summary']['critical_requirements_total']==13 and trace['summary']['critical_requirements_complete']==13,
 'self_compile_reproduces':recompiled==saved_compiled and saved_compiled['status']=='compiled' and not compiled_schema,
 'self_execution_replay':replay['ok'] and len(replay['final_states'])==7 and all(v=='done' for v in replay['final_states'].values()),
 'shadow_corrective_clean':shadow['use_for_promotion'] is False and shadow['summary']['passed']==shadow['summary']['cases']==2,
 'full_tests':full['returncode']==0 and '142 passed' in full['stdout'],
 'inherited_tests':inherited['returncode']==0 and '119 passed' in inherited['stdout'],
 'new_corrective_regressions':newregs['returncode']==0 and '3 passed' in newregs['stdout'],
 'frozen_regressions_present':frozen<=active,
 'corrective_regressions_present':corrective<=active,
 'workspace_without_shipping_manifest':workspace['ok'] and workspace['summary']['errors']==0 and workspace['summary']['warnings']==0,
}
result={
 'candidate_version':'0.08','actor_id':ACTOR,'implementation_actor_id':IMPLEMENTATION_ACTOR,
 'checks':checks,'result':'PASS' if all(checks.values()) else 'FAIL','recommendation':'PROMOTED AS EXPERIMENTAL' if all(checks.values()) else 'RETRY REQUIRED',
 'hashes':{k:(contract_hash if k=='contract' else sha(ROOT/{'spec':'versions/v0.08/SPEC-CREATOR-v0.08.md','plan':'versions/v0.08/EVALUATION-PLAN.json','corpus':'fixtures/task-compiler/v0.08/corpus.jsonl','heldout':'fixtures/task-compiler/v0.08/heldout.jsonl','execution':'fixtures/task-compiler/v0.08/execution-corpus.jsonl','preflight':'evaluation/v008-preregistration-preflight.json','project_schema':'schemas/task-compilation-project-v1.schema.json','compiled_schema':'schemas/compiled-task-graph-v1.schema.json','execution_schema':'schemas/task-execution-event-v1.schema.json'}[k])) for k in EXPECTED},
 'corpus_counts':eval_result['counts'],'corpus_metrics':m,'preflight_summary':preflight['summary'],'spec_lint_summary':spec_lint['summary'],'spec_ambiguity_summary':spec_amb['summary'],'spec_discovery_summary':spec_disc['summary'],'traceability_summary':trace['summary'],'self_compiled_summary':saved_compiled['summary'],'self_execution_summary':{'event_count':replay['event_count'],'final_states':replay['final_states']},'shadow_summary':shadow['summary'],
 'full_test_run':full,'inherited_test_run':inherited,'new_corrective_regression_test_run':newregs,'workspace_validation':workspace['summary'],'active_regression_count':len(active),
 'limitations':['Independent role separation occurs within the same runtime/session.','Frozen compiler and execution corpora are same-cycle synthetic evidence; held-out labels are hash-locked but not externally independent.','Shadow cases are corrective/non-promotional and cannot raise classification above the frozen experimental ceiling.','The normalized task IR assumes source task boundaries already exist; automatic architecture/task decomposition remains a non-goal.','Final root package manifest is intentionally generated only after release accounting is complete.']
}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result['result']=='PASS' else 1)
