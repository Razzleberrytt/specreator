from pathlib import Path
import json
from jsonschema import Draft202012Validator
from spec_creator.v0111.execution_architecture import analyze_fixture, build_execution_plan, derive_effective_edges
ROOT=Path(__file__).resolve().parents[2]
def fixtures(): return [json.loads(x) for x in (ROOT/'versions/v0.11.1/candidate-fixtures/execution-architecture-corpus.jsonl').read_text().splitlines() if x.strip()]
def test_all_structural_oracles_exact():
 for f in fixtures():
  a=analyze_fixture(f); e=f['expected']
  assert sorted(a['critical_paths'])==sorted(e['critical_paths']); assert a['critical_work_units']==e['critical_work_units']; assert a['waves']==e['waves']
def test_dependency_counts_and_conflict_provenance():
 all_edges=[e for f in fixtures() for e in derive_effective_edges(f)]
 assert sum(e['provenance']!='conflict_serialization' for e in all_edges)==21
 assert sum(e['provenance']=='conflict_serialization' for e in all_edges)==1
def test_generated_plans_validate_schema_and_cover_23_sources():
 schema=json.loads((ROOT/'versions/v0.11.1/candidate-schemas/execution-architecture-v1.candidate.schema.json').read_text()); v=Draft202012Validator(schema); src=set()
 for f in fixtures():
  p=build_execution_plan(f); assert list(v.iter_errors(p))==[]
  for t in p['tasks']: src.update(t['source_task_ids'])
 expected=set(json.loads((ROOT/'versions/v0.11.1/EVALUATION-UNIVERSES.json').read_text())['universes']['integration_source_tasks']['members'])
 assert src==expected and len(src)==23
def test_speculation_never_authoritative_early():
 f=next(x for x in fixtures() if x['fixture_id'].endswith('SPECULATIVE')); a=analyze_fixture(f)
 assert a['authority_escape_count']==0 and a['speculative_non_authoritative']==['PREP']
def test_retry_isolation_preserves_unrelated_branch():
 f=next(x for x in fixtures() if x['fixture_id'].endswith('RETRY-ISOLATION')); a=analyze_fixture(f)
 assert a['unrelated_rerun_count']==0 and set(a['preserved_expected'])=={'A','C'}
