from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from spec_creator.ambiguity_evaluator import evaluate_v0061_corpus, preflight_ambiguity_corpus
from spec_creator.linter import lint_file
from spec_creator.models import canonical_contract_hash
from spec_creator.traceability import load_graph, validate_graph
from spec_creator.validator import validate_workspace

ACTOR='verifier:independent-pass-006'
IMPLEMENTATION_ACTOR='agent:spec-creator-builder'
EXPECTED_CONTRACT='2ae4073dc197c73386d07b9746d38d807a1d9c038b56aae6a68c7c16a53fbf27'
EXPECTED_CORPUS='3d147717ff2501061f72a0c5f384403751297eb91b6d916fd4fbb48e9edf5f9e'
EXPECTED_PLAN='70e3f6c5017fc2a6aef312065ec7f705cbc055f9cec46aec6144c1a1ee6a0bc5'

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def run_pytest(args):
    p=subprocess.run([sys.executable,'-m','pytest','-q',*args],cwd=ROOT,text=True,capture_output=True)
    return {'returncode':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

contract=json.loads((ROOT/'versions/v0.06.1/FROZEN-RELEASE-CONTRACT.json').read_text())
corpus=ROOT/'fixtures/ambiguity/v0.06.1/corpus.jsonl'
plan=ROOT/'versions/v0.06.1/EVALUATION-PLAN.json'
contract_hash=canonical_contract_hash(contract)
corpus_hash=sha(corpus); plan_hash=sha(plan)
retry_preflight=preflight_ambiguity_corpus(corpus)
failed_preflight=preflight_ambiguity_corpus(ROOT/'fixtures/ambiguity/v0.06/corpus.jsonl')
evaluation=evaluate_v0061_corpus(ROOT)
lint=lint_file(ROOT/'versions/v0.06.1/SPEC-CREATOR-v0.06.1.md').as_dict()
trace=validate_graph(load_graph(ROOT/'versions/v0.06.1/TRACEABILITY-GRAPH.json')).as_dict()
workspace=validate_workspace(ROOT,validate_package_manifest=False).as_dict()
full=run_pytest([])
inherited=run_pytest(['tests/test_validator.py','tests/test_linter.py','tests/test_traceability.py','tests/test_traceability_cli.py','tests/test_cli.py'])
regs=[]
for line in (ROOT/'self-improvement/regressions.jsonl').read_text().splitlines():
    if line.strip(): regs.append(json.loads(line))
active={r['regression_id'] for r in regs if r.get('status')=='active'}
applicable=set(contract['applicable_regressions'])
new_required={'REG-0010','REG-0011','REG-0012','REG-0013'}

m=evaluation['metrics']
checks={
 'actor_independence': ACTOR != IMPLEMENTATION_ACTOR,
 'contract_hash': contract_hash == EXPECTED_CONTRACT == contract.get('contract_hash'),
 'corpus_hash': corpus_hash == EXPECTED_CORPUS,
 'plan_hash': plan_hash == EXPECTED_PLAN,
 'retry_dependency_preflight': retry_preflight['ok'] and retry_preflight['trace_graph_valid_count']==16,
 'failed_candidate_regression': (not failed_preflight['ok']) and failed_preflight['trace_graph_invalid_count']==16,
 'spec_lint': lint['summary']['unsuppressed']==0,
 'defect_detection': m['defect_case_detection_rate']>=0.95,
 'clean_acceptance': m['clean_case_acceptance_rate']>=0.95,
 'classification': m['decision_needed_classification_accuracy']>=0.95,
 'governed_default_questions': m['governed_default_question_count']==0,
 'priority': m['priority_top_question_accuracy']>=0.90,
 'clarification_proxy': m['implementation_time_clarification_reduction_proxy_rate']>=0.80,
 'unnecessary_questions': m['unnecessary_question_rate']<=0.05,
 'critical_escapes': m['critical_ambiguity_escape_count']==0,
 'self_traceability': trace['ok'] and trace['summary']['critical_requirements_complete']==12 and trace['summary']['critical_requirements_total']==12,
 'full_tests': full['returncode']==0,
 'inherited_tests': inherited['returncode']==0,
 'frozen_regressions_present': applicable <= active,
 'new_regressions_present': (new_required | {'REG-0014'}) <= active,
 'workspace_without_shipping_manifest': workspace['ok'] and workspace['summary']['errors']==0 and workspace['summary']['warnings']==0,
}
result={
 'candidate_version':'0.06.1','actor_id':ACTOR,'implementation_actor_id':IMPLEMENTATION_ACTOR,
 'checks':checks,'result':'PASS' if all(checks.values()) else 'FAIL',
 'hashes':{'contract_canonical_sha256':contract_hash,'corpus_sha256':corpus_hash,'evaluation_plan_sha256':plan_hash},
 'corpus_metrics':m,'corpus_counts':evaluation['counts'],
 'retry_preflight':{k:v for k,v in retry_preflight.items() if k!='trace_cases'},
 'failed_v006_preflight':{k:v for k,v in failed_preflight.items() if k!='trace_cases'},
 'spec_lint_summary':lint['summary'],'traceability_summary':trace['summary'],
 'full_test_run':full,'inherited_test_run':inherited,'workspace_validation':workspace['summary'],
 'limitations':['Role separation is within the same runtime/session, not an external organization.','Clarification reduction is a synthetic interception proxy; no real-project causal reduction is claimed.','Final root package manifest is intentionally sealed only after all release evidence files are complete.']
}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result['result']=='PASS' else 1)
