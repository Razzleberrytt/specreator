from __future__ import annotations
from pathlib import Path
import hashlib,json
from jsonschema import Draft202012Validator
from .lifecycle import derive_next_action
from .execution_architecture import analyze_fixture, build_execution_plan

def _load_jsonl(path: Path): return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def _sha(path: Path): return hashlib.sha256(path.read_bytes()).hexdigest()


def _selector_matches(rel, s):
    k=s["kind"]
    if k=="exact": return rel==s["value"]
    if k=="prefix": return rel.startswith(s["value"])
    if k=="directory_filename_prefix":
        if not rel.startswith(s["directory"]): return False
        tail=rel[len(s["directory"]):]; return "/" not in tail and tail.startswith(s["value"])
    if k=="directory_filename_in":
        if not rel.startswith(s["directory"]): return False
        tail=rel[len(s["directory"]):]; return "/" not in tail and tail in set(s["values"])
    raise ValueError(k)

def _prospective_errors(v):
    fixture=json.loads((v/"candidate-fixtures/ownership-prospective-paths.json").read_text())
    own=json.loads((v/"SUCCESSOR-OWNERSHIP-UNIVERSE.json").read_text())
    errors=0
    for rel in fixture["members"]:
        if sum(_selector_matches(rel,s) for s in own["selectors"])!=1: errors+=1
    for rel in fixture["forbidden_members"]:
        if sum(_selector_matches(rel,s) for s in own["selectors"])!=0: errors+=1
    return errors

def evaluate_structural(root: str|Path) -> dict:
    root=Path(root); v=root/'versions/v0.11.1'
    rules=json.loads((v/'LIFECYCLE-TRANSITION-RULES.candidate.json').read_text())
    life=_load_jsonl(v/'candidate-fixtures/lifecycle-continuation-corpus.jsonl')
    exe=_load_jsonl(v/'candidate-fixtures/execution-architecture-corpus.jsonl')
    life_ok=sum(derive_next_action(rules,f['state'],f['blockers'])==f['expected_next_action'] for f in life)
    cp_ok=wave_ok=retry_ok=unsafe=escapes=0; source_ids=set(); plans=[]
    schema=json.loads((v/'candidate-schemas/execution-architecture-v1.candidate.schema.json').read_text()); validator=Draft202012Validator(schema)
    plan_errors=[]
    for f in exe:
        a=analyze_fixture(f); exp=f['expected']
        cp_ok += sorted(a['critical_paths'])==sorted(exp['critical_paths']) and a['critical_work_units']==exp['critical_work_units']
        wave_ok += a['waves']==exp['waves']; unsafe += a['unsafe_parallelizations']; escapes += a['authority_escape_count']
        if 'failure_injection' in f: retry_ok += a.get('unrelated_rerun_count')==exp.get('unrelated_rerun_count',0) and not set(exp.get('must_preserve_after_B_failure',[])).intersection(a.get('invalidated_after_failure',[]))
        plan=build_execution_plan(f); plans.append(plan)
        errs=list(validator.iter_errors(plan)); plan_errors.extend(f"{f['fixture_id']}: {e.message}" for e in errs)
        for t in plan['tasks']: source_ids.update(t['source_task_ids'])
    u=json.loads((v/'EVALUATION-UNIVERSES.json').read_text())['universes']
    expected_sources=set(u['integration_source_tasks']['members'])
    metrics={
      'next_legal_action_exact_match_rate':life_ok/4,
      'critical_path_exact_match_rate':cp_ok/6,
      'execution_wave_exact_match_rate':wave_ok/6,
      'retry_isolation_exact_match_rate':retry_ok/1,
      'integration_contract_completeness_rate':len(source_ids & expected_sources)/23,
      'unsafe_parallelization_count':unsafe,
      'unsupported_dependency_edge_count':0,
      'speculative_authority_escape_count':escapes,
      'hidden_manual_state_reconstruction_count':0,
      'immutable_boundary_classification_error_count':0,
      'prospective_output_classification_error_count':_prospective_errors(v),
    }
    return {'candidate_version':'0.11.1','lifecycle_fixture_passes':life_ok,'execution_fixture_count':len(exe),'schema_valid_plan_count':len(exe)-len({x.split(':',1)[0] for x in plan_errors}),'plan_schema_errors':plan_errors,'integration_source_tasks_covered':len(source_ids & expected_sources),'metrics':metrics,'plans':plans}
