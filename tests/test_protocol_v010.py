import json
from pathlib import Path
from spec_creator.protocol import run_protocol, validate_run
from spec_creator.protocol_evaluator import evaluate_v010
ROOT=Path(__file__).resolve().parents[1]
def cases(): return [json.loads(x) for x in (ROOT/'fixtures/protocol/v0.10/corpus.jsonl').read_text().splitlines() if x.strip()]
def test_all_frozen_protocol_cases_complete_and_validate():
    for c in cases():
        x=run_protocol(c,root=ROOT); assert x['run']['status']=='completed'; assert validate_run(x['run'],root=ROOT)==[]
def test_blocker_recovery_is_observed_without_gate_bypass():
    c=next(x for x in cases() if x['scenario']=='blocker_recovery'); r=run_protocol(c,root=ROOT)['run']; assert r['metrics']['blocked_then_recovered']; assert r['metrics']['critical_gate_bypass_count']==0
def test_resume_exact_and_hash_mismatch_fails_closed():
    c=next(x for x in cases() if x['scenario']=='resume'); a=run_protocol(c,root=ROOT); b=run_protocol(c,root=ROOT,resume=a['continuation']); assert b['run']['status']=='completed'; assert b['run']['artifact_hashes']['execution_events']==a['run']['artifact_hashes']['execution_events']; bad=run_protocol(c,root=ROOT,resume=a['continuation'],tamper_resume_hash=True); assert bad['run']['status']=='blocked'
def test_v010_frozen_metrics_hit_targets():
    m=evaluate_v010(ROOT)['metrics']; assert m['end_to_end_project_completion_rate']==1; assert m['manual_artifact_reconstruction_count']==0; assert m['deterministic_rerun_rate']==1; assert m['resume_exact_match_rate']==1; assert m['artifact_provenance_completeness_rate']==1; assert m['promoted_stage_semantic_preservation_rate']==1; assert m['critical_gate_bypass_count']==0; assert m['invalid_or_hash_mismatched_resume_escape_count']==0
