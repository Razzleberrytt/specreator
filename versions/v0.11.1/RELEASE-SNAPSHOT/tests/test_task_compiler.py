import json
from pathlib import Path

from spec_creator.task_compiler import compile_project, validate_compiled_graph

ROOT = Path(__file__).resolve().parents[1]
CORPUS = [json.loads(x) for x in (ROOT/'fixtures/task-compiler/v0.08/corpus.jsonl').read_text().splitlines() if x.strip()]

def cases(category):
    return [c for c in CORPUS if c['category']==category]

def test_frozen_task_graphs():
    for c in CORPUS:
        if c['expected']['status']=='compiled':
            assert compile_project(c['project'], root=ROOT) == c['expected'], c['case_id']

def test_owner_decisions_block_compilation():
    for c in cases('owner_blocker'):
        r=compile_project(c['project'], root=ROOT)
        assert r['status']=='blocked'
        assert {d['code'] for d in r['diagnostics']} == {'TC-OWNER-DECISION'}
        assert sorted(r['diagnostics'][0]['blocking_action_ids']) == c['expected']['blocking_action_ids']

def test_dependency_provenance():
    for c in cases('accepted_dependency'):
        r=compile_project(c['project'], root=ROOT)
        assert r==c['expected']
        for t in r['tasks']:
            if t['prerequisite_task_ids']:
                assert t['provenance']['prerequisite_task_ids']
                assert all(x.startswith(('trace:','order:','artifact:')) for x in t['provenance']['prerequisite_task_ids'])

def test_cycle_rejection():
    for c in cases('dependency_cycle'):
        r=compile_project(c['project'], root=ROOT)
        assert r['status']=='invalid'
        d=next(d for d in r['diagnostics'] if d['code']=='TC-DEPENDENCY-CYCLE')
        assert d['source_task_ids']==c['expected']['cycle_source_task_ids']

def test_atomicity_bounds():
    for c in cases('atomicity_refinement'):
        r=compile_project(c['project'], root=ROOT)
        assert r['status']=='needs_spec_refinement'
        assert sorted({d['code'] for d in r['diagnostics']})==c['expected']['diagnostic_codes']
        assert r['tasks']==[]

def test_conflict_zones():
    for c in cases('accepted_conflict'):
        r=compile_project(c['project'], root=ROOT)
        assert r==c['expected']
        assert len(r['conflict_zones'])==1
        tids=r['conflict_zones'][0]['task_ids']
        by={t['task_id']:t for t in r['tasks']}
        assert tids[1] not in by[tids[0]]['parallel_with']
        assert tids[0] not in by[tids[1]]['parallel_with']

def test_parallelization_rules():
    for c in CORPUS:
        if c['expected']['status']=='compiled':
            r=compile_project(c['project'], root=ROOT)
            assert [t['parallel_with'] for t in r['tasks']] == [t['parallel_with'] for t in c['expected']['tasks']]

def test_critical_coverage():
    for c in cases('parent_invalid'):
        r=compile_project(c['project'], root=ROOT)
        assert r['status']=='invalid'
        assert all(code in {d['code'] for d in r['diagnostics']} for code in c['expected']['diagnostic_codes'])

def test_compiled_graph_schema_and_hash():
    for c in CORPUS[:12]:
        r=compile_project(c['project'], root=ROOT)
        if r['status']=='compiled':
            assert validate_compiled_graph(r, root=ROOT)==[]

def test_stale_discovery_plan_cannot_hide_owner_decision_regression():
    import copy
    c=copy.deepcopy(next(c for c in CORPUS if c['category']=='owner_blocker'))
    c['project']['project_id']='TCP-REG-0017'
    c['project']['discovery_plan']={'actions':[]}
    r=compile_project(c['project'], root=ROOT)
    assert r['status']=='blocked'
    assert 'TC-DISCOVERY-PLAN-INCOMPLETE' in {d['code'] for d in r['diagnostics']}


def test_duplicate_task_metadata_is_rejected_before_dict_overwrite_regression():
    import copy
    c=copy.deepcopy(next(c for c in CORPUS if c['expected']['status']=='compiled'))
    c['project']['project_id']='TCP-REG-0018'
    duplicate=copy.deepcopy(c['project']['task_metadata'][0])
    duplicate['write_scopes']=['src/overwritten']
    c['project']['task_metadata'].append(duplicate)
    r=compile_project(c['project'], root=ROOT)
    assert r['status']=='invalid'
    assert 'TC-METADATA-DUPLICATE' in {d['code'] for d in r['diagnostics']}
