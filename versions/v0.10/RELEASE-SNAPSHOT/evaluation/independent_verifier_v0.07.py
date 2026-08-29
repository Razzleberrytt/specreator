from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from spec_creator.ambiguity import analyze_ambiguity_file
from spec_creator.discovery_evaluator import evaluate_v007_corpus, preflight_discovery_corpus
from spec_creator.linter import lint_file
from spec_creator.models import canonical_contract_hash
from spec_creator.traceability import load_graph, validate_graph
from spec_creator.validator import validate_workspace

ACTOR='verifier:independent-pass-007'
IMPLEMENTATION_ACTOR='agent:spec-creator-builder'
EXPECTED_CONTRACT='981c1415040c986d031f528ce10a12456a0e594bbb9551f95cbec4bf8c3dac38'
EXPECTED_PLAN='539e75dca5af5067188417b27ed405719b9b3e4d78a61739178c0db0a9cebe3d'
EXPECTED_CORPUS='31e13b98991543208e453faa89d2277282646f8110483fab1ea9a8d9b3c272ad'
EXPECTED_HELDOUT='064d0b1a78e708cb071fa9c28db8b7b0f1b98cb5e70f0c9f81e14e0282f3848e'
INHERITED_TESTS=[
 'tests/test_ambiguity.py','tests/test_ambiguity_cli.py','tests/test_ambiguity_evaluator.py',
 'tests/test_cli.py','tests/test_ledger.py','tests/test_linter.py','tests/test_package_manifest.py',
 'tests/test_traceability.py','tests/test_traceability_cli.py','tests/test_validator.py'
]

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def run_pytest(args):
    p=subprocess.run([sys.executable,'-m','pytest','-q',*args],cwd=ROOT,text=True,capture_output=True)
    return {'returncode':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

def load_active_regs():
    rows=[]
    for line in (ROOT/'self-improvement/regressions.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip(): rows.append(json.loads(line))
    return {r['regression_id'] for r in rows if r.get('status')=='active'}

contract_path=ROOT/'versions/v0.07/FROZEN-RELEASE-CONTRACT.json'
plan_path=ROOT/'versions/v0.07/EVALUATION-PLAN.json'
corpus_path=ROOT/'fixtures/discovery/v0.07/corpus.jsonl'
heldout_path=ROOT/'fixtures/discovery/v0.07/heldout.jsonl'
spec_path=ROOT/'versions/v0.07/SPEC-CREATOR-v0.07.md'
contract=json.loads(contract_path.read_text(encoding='utf-8'))
contract_hash=canonical_contract_hash(contract)
evaluation=evaluate_v007_corpus(ROOT)
preflight=preflight_discovery_corpus(corpus_path)
lint=lint_file(spec_path).as_dict()
amb=analyze_ambiguity_file(spec_path).as_dict()
trace=validate_graph(load_graph(ROOT/'versions/v0.07/TRACEABILITY-GRAPH.json')).as_dict()
shadow=json.loads((ROOT/'evaluation/shadow-real-specs-v0.07-final.json').read_text(encoding='utf-8'))
workspace=validate_workspace(ROOT,validate_package_manifest=False).as_dict()
full=run_pytest([])
inherited=run_pytest([*INHERITED_TESTS, '-k', 'not test_requirement_block_stops_at_higher_level_heading_regression and not test_unresolved_taxonomy_description_is_not_status_marker_regression and not test_unresolved_status_still_detected_after_context_fix'])
new_regressions=run_pytest(['tests/test_ambiguity.py::test_requirement_block_stops_at_higher_level_heading_regression','tests/test_ambiguity.py::test_unresolved_taxonomy_description_is_not_status_marker_regression','tests/test_ambiguity.py::test_unresolved_status_still_detected_after_context_fix'])
active=load_active_regs(); applicable=set(contract['applicable_regressions'])
new_required={'REG-0015','REG-0016'}
metrics=evaluation['metrics']
shadow_clean=all(r.get('summary',{}).get('candidates')==0 and r.get('summary',{}).get('question_batches')==0 for r in shadow.get('results',[]))
checks={
 'actor_independence': ACTOR != IMPLEMENTATION_ACTOR,
 'contract_hash': contract_hash == EXPECTED_CONTRACT == contract.get('contract_hash'),
 'evaluation_plan_hash': sha(plan_path) == EXPECTED_PLAN,
 'corpus_hash': sha(corpus_path) == EXPECTED_CORPUS,
 'heldout_hash': sha(heldout_path) == EXPECTED_HELDOUT,
 'parent_preflight': preflight['ok'] and preflight['case_count']==72 and preflight['parent_preflight_rate']==1.0,
 'spec_lint': lint['summary']['unsuppressed']==0,
 'spec_ambiguity': len(amb.get('questions',[]))==0,
 'question_reduction': metrics['owner_question_reduction_rate']>=0.40,
 'information_value': metrics['information_value_top_selection_accuracy']>=0.95,
 'heldout_actions': metrics['heldout_action_exact_match_rate']>=0.95,
 'safe_inference': metrics['safe_inference_exact_match_rate']==1.0,
 'unsafe_defaults': metrics['unsafe_default_count']==0,
 'critical_escapes': metrics['critical_ambiguity_escape_count']==0,
 'dependency_frontier': metrics['dependency_frontier_accuracy']==1.0,
 'provenance': metrics['provenance_completeness_rate']==1.0,
 'unnecessary_questions': metrics['unnecessary_question_rate']<=0.05,
 'rework_proxy': metrics['rework_proxy_error_count']==0,
 'self_traceability': trace['ok'] and trace['summary']['critical_requirements_complete']==12 and trace['summary']['critical_requirements_total']==12,
 'shadow_nonpromotional_clean': shadow.get('use_for_promotion') is False and shadow_clean,
 'full_tests': full['returncode']==0,
 'inherited_tests': inherited['returncode']==0 and '100 passed' in inherited['stdout'],
 'new_corrective_regression_tests': new_regressions['returncode']==0 and '3 passed' in new_regressions['stdout'],
 'frozen_regressions_present': applicable <= active,
 'new_corrective_regressions_present': new_required <= active,
 'workspace_without_shipping_manifest': workspace['ok'] and workspace['summary']['errors']==0 and workspace['summary']['warnings']==0,
}
result={
 'candidate_version':'0.07','actor_id':ACTOR,'implementation_actor_id':IMPLEMENTATION_ACTOR,
 'checks':checks,'result':'PASS' if all(checks.values()) else 'FAIL',
 'recommendation':'PROMOTED AS EXPERIMENTAL' if all(checks.values()) else 'RETRY REQUIRED',
 'hashes':{'contract_canonical_sha256':contract_hash,'evaluation_plan_sha256':sha(plan_path),'corpus_sha256':sha(corpus_path),'heldout_sha256':sha(heldout_path)},
 'corpus_metrics':metrics,'corpus_counts':evaluation['counts'],'preflight_summary':{k:v for k,v in preflight.items() if k!='cases'},
 'spec_lint_summary':lint['summary'],'spec_ambiguity_summary':amb.get('summary',{}),'traceability_summary':trace['summary'],
 'shadow_summary':[{'file':r['file'],'summary':r['summary']} for r in shadow['results']],
 'full_test_run':full,'inherited_test_run':inherited,'new_corrective_regression_test_run':new_regressions,'workspace_validation':workspace['summary'],
 'active_regression_count':len(active),
 'limitations':['Role separation is within the same runtime/session, not an external organization.','The frozen held-out set is same-cycle synthetic evidence and does not establish real-project causal rework reduction.','Shadow internal-spec evaluation is corrective/non-promotional and cannot raise the release classification.','Final root package manifest is intentionally generated only after release accounting is complete.']
}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result['result']=='PASS' else 1)
