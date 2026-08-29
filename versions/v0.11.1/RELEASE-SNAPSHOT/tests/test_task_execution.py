import json
from pathlib import Path

from spec_creator.task_execution import replay_task_events

ROOT=Path(__file__).resolve().parents[1]
CASES=[json.loads(x) for x in (ROOT/'fixtures/task-compiler/v0.08/execution-corpus.jsonl').read_text().splitlines() if x.strip()]

def run(c):
    return replay_task_events(graph_hash=c['graph_hash'], task_ids=c['task_ids'], events=c['events'], root=ROOT)

def test_frozen_execution_corpus():
    for c in CASES:
        r=run(c)
        codes={d['code'] for d in r['diagnostics']}
        if c['valid']:
            assert r['ok'], c['case_id']
            assert r['final_states']==c['expected_final_states']
        else:
            assert not r['ok'], c['case_id']
            assert set(c['expected_codes']).issubset(codes)

def test_duplicate_execution_event_rejected():
    c=next(c for c in CASES if c['case_id']=='TE-INVALID-01')
    assert 'TE-DUPLICATE-EVENT' in {d['code'] for d in run(c)['diagnostics']}

def test_execution_graph_hash_drift_rejected():
    c=next(c for c in CASES if c['case_id']=='TE-INVALID-02')
    assert 'TE-GRAPH-HASH-MISMATCH' in {d['code'] for d in run(c)['diagnostics']}

def test_execution_state_is_replayed_not_stored_in_task_definition():
    c=next(c for c in CASES if c['case_id']=='TE-VALID-02')
    r=run(c)
    assert r['final_states']['CTASK-EXEC-A']=='done'

def test_invalid_transition_and_time_reversal_rejected():
    for cid,code in [('TE-INVALID-05','TE-INVALID-TRANSITION'),('TE-INVALID-06','TE-TIME-REVERSAL')]:
        c=next(c for c in CASES if c['case_id']==cid)
        assert code in {d['code'] for d in run(c)['diagnostics']}
