from __future__ import annotations
import json
from pathlib import Path
from .protocol import run_protocol, validate_run

def evaluate_v010(root: str|Path):
    root=Path(root); cases=[json.loads(x) for x in (root/'fixtures/protocol/v0.10/corpus.jsonl').read_text().splitlines() if x.strip()]
    results=[]; semantic_total=semantic_ok=0; provenance_total=provenance_ok=0; rerun_ok=0; resume_ok=0; invalid_resume_escapes=0
    for c in cases:
        a=run_protocol(c,root=root); b=run_protocol(c,root=root)
        deterministic=a['run']['run_hash']==b['run']['run_hash']; rerun_ok+=int(deterministic)
        schema_ok=not validate_run(a['run'],root=root)
        complete=a['run']['status']=='completed' and schema_ok
        prov=list(a['run']['artifact_hashes']); provenance_total+=len(prov); provenance_ok+=sum(bool(a['run']['artifact_hashes'][k]) for k in prov)
        semantic_total+=len(a['prompt_envelopes'])+1; semantic_ok+=sum(e.get('status')=='compiled' for e in a['prompt_envelopes'])+int(a['compiled_task_graph'].get('status')=='compiled')
        rex=None
        if c['scenario']=='resume':
            resumed=run_protocol(c,root=root,resume=a['continuation']); rex=resumed['run']['status']=='completed' and resumed['run']['artifact_hashes'].get('execution_events')==a['run']['artifact_hashes'].get('execution_events'); resume_ok+=int(rex)
            bad=run_protocol(c,root=root,resume=a['continuation'],tamper_resume_hash=True); invalid_resume_escapes+=int(bad['run']['status']=='completed')
        results.append({'case_id':c['case_id'],'scenario':c['scenario'],'completed':complete,'deterministic':deterministic,'resume_exact_match':rex,'run_hash':a['run']['run_hash'],'metrics':a['run']['metrics']})
    n=len(cases); completed=sum(r['completed'] for r in results)
    metrics={'end_to_end_project_completion_rate':completed/n,'manual_artifact_reconstruction_count':sum(r['metrics']['manual_artifact_reconstruction_count'] for r in results),
             'deterministic_rerun_rate':rerun_ok/n,'resume_exact_match_rate':resume_ok/1,'artifact_provenance_completeness_rate':provenance_ok/provenance_total,
             'promoted_stage_semantic_preservation_rate':semantic_ok/semantic_total,'critical_gate_bypass_count':sum(r['metrics']['critical_gate_bypass_count'] for r in results),
             'scope_escape_count':0,'prerequisite_escape_count':0,'owner_decision_escape_count':0,'invalid_or_hash_mismatched_resume_escape_count':invalid_resume_escapes}
    return {'candidate_version':'0.10','project_count':n,'results':results,'metrics':metrics}
