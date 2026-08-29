from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker
from .task_compiler import compile_project, validate_compiled_graph
from .prompt_compiler import compile_prompt, validate_prompt_envelope
from .task_execution import replay_task_events
from .linter import lint_text
from .traceability import validate_graph


def canonical_hash(obj: dict[str, Any], exclude: set[str] | None = None) -> str:
    data=copy.deepcopy(obj)
    for k in exclude or set(): data.pop(k,None)
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _hash(obj: Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _event(graph_hash, task_id, idx, frm, to, reason=None, evidence=None):
    e={"event_id":f"TEVT-P010-{idx:04d}","graph_hash":graph_hash,"task_id":task_id,
       "event_time_utc":f"2026-01-01T00:{idx//60:02d}:{idx%60:02d}Z","actor_id":"protocol:v0.10",
       "from_state":frm,"to_state":to,"evidence_refs":evidence or []}
    if reason is not None: e["reason"]=reason
    return e

def _contract(task):
    return {"task_id":task["task_id"],"acceptance_criteria":[f"Complete {r}" for r in task["source_requirement_ids"]],
            "critical_obligations":[f"Preserve {r}" for r in task["source_requirement_ids"]],
            "evidence_requirements":list(task["verification_refs"]),"frozen_criteria_refs":list(task["gate_ids"]),
            "blocking_owner_decision_ids":[]}

def _prompt(graph, task, kind, events, seq, root):
    actor="verifier:v0.10" if kind=="verification" else "implementer:v0.10"
    inp={"schema_version":"1.0","request_id":f"PREQ-P010-{seq:04d}","candidate_version":"0.10",
         "compiled_task_graph":graph,"task_id":task["task_id"],"prompt_kind":kind,"task_contract":_contract(task),
         "context_records":[],"execution_events":events,"requested_write_scopes":task["write_scopes"] if kind in {"implementation","debug"} else [],
         "debug_evidence_refs":["evidence:blocker"] if kind=="debug" else [],
         "actor_context":{"requested_actor_id":actor,"implementation_actor_id":"implementer:v0.10"}}
    return compile_prompt(inp,root=root)

def validate_run(run: dict[str,Any], root=None):
    root=Path(root or Path(__file__).resolve().parents[2])
    schema=json.loads((root/'schemas/protocol-run-v1.schema.json').read_text())
    errs=[]
    for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(run): errs.append(e.message)
    if not errs and run.get('run_hash') != canonical_hash(run,{'run_hash'}): errs.append('run_hash mismatch')
    return errs

def run_protocol(case: dict[str,Any], *, root=None, resume: dict[str,Any]|None=None, tamper_resume_hash: bool=False):
    root=Path(root or Path(__file__).resolve().parents[2]); project=case['project']; pid=project['project_id']; rid=f"PRUN-{case['case_id']}"
    records=[]; artifacts={}; diagnostics=[]
    lint=lint_text(project['spec_text']); records.append({'stage':'spec_lint','status':'pass' if lint.ok else 'invalid','artifact_refs':['spec_text'],'diagnostics':[]})
    trace=validate_graph(project['traceability_graph']); records.append({'stage':'traceability','status':'pass' if trace.ok else 'invalid','artifact_refs':['traceability_graph'],'diagnostics':[]})
    if not lint.ok or not trace.ok: status='invalid'; graph=None
    else:
        graph=compile_project(project,root=root); gs='pass' if graph['status']=='compiled' else graph['status']; records.append({'stage':'task_compile','status':gs,'artifact_refs':['compiled_task_graph'],'diagnostics':graph.get('diagnostics',[])})
        status='completed' if gs=='pass' else gs
    prompt_envs=[]; events=[]; blocked_observed=False; recovered=False
    if graph and graph.get('status')=='compiled':
        artifacts['compiled_task_graph']=_hash(graph)
        tasks={t['task_id']:t for t in graph['tasks']}; order=[t['task_id'] for t in graph['tasks']]
        if resume is not None:
            expected=resume.get('graph_hash'); actual=graph['graph_hash']
            if tamper_resume_hash or expected != actual:
                records.append({'stage':'resume','status':'blocked','artifact_refs':['compiled_task_graph'],'diagnostics':[{'code':'P010-RESUME-HASH','message':'Resume graph hash mismatch.'}]})
                status='blocked'
            else:
                events=copy.deepcopy(resume.get('execution_events',[])); rep=replay_task_events(graph_hash=actual,task_ids=order,events=events,root=root)
                if not rep['ok']:
                    records.append({'stage':'resume','status':'invalid','artifact_refs':['execution_events'],'diagnostics':rep['diagnostics']}); status='invalid'
                else: records.append({'stage':'resume','status':'pass','artifact_refs':['compiled_task_graph','execution_events'],'diagnostics':[]})
        idx=len(events)+1; seq=1
        if status=='completed':
            states=replay_task_events(graph_hash=graph['graph_hash'],task_ids=order,events=events,root=root)['final_states']
            for tid in order:
                task=tasks[tid]; st=states.get(tid)
                if st is None:
                    events.append(_event(graph['graph_hash'],tid,idx,None,'planned')); idx+=1; st='planned'
                if st == 'done':
                    continue
                if 'bootstrap' in case['prompt_kinds']:
                    env=_prompt(graph,task,'bootstrap',events,seq,root); seq+=1; prompt_envs.append(env)
                if st=='planned': events.append(_event(graph['graph_hash'],tid,idx,'planned','ready')); idx+=1; st='ready'
                if case['scenario']=='blocker_recovery' and not blocked_observed:
                    events.append(_event(graph['graph_hash'],tid,idx,'ready','blocked','preregistered blocker')); idx+=1; blocked_observed=True; st='blocked'
                    if 'debug' in case['prompt_kinds']:
                        env=_prompt(graph,task,'debug',events,seq,root); seq+=1; prompt_envs.append(env)
                    events.append(_event(graph['graph_hash'],tid,idx,'blocked','ready',evidence=['evidence:recovery'])); idx+=1; recovered=True; st='ready'
                if 'implementation' in case['prompt_kinds']:
                    env=_prompt(graph,task,'implementation',events,seq,root); seq+=1; prompt_envs.append(env)
                events.append(_event(graph['graph_hash'],tid,idx,'ready','in_progress')); idx+=1
                events.append(_event(graph['graph_hash'],tid,idx,'in_progress','done',evidence=[f'evidence:{tid}:done'])); idx+=1
                if 'continuation' in case['prompt_kinds']:
                    env=_prompt(graph,task,'continuation',events,seq,root); seq+=1; prompt_envs.append(env)
                if 'verification' in case['prompt_kinds']:
                    env=_prompt(graph,task,'verification',events,seq,root); seq+=1; prompt_envs.append(env)
            rep=replay_task_events(graph_hash=graph['graph_hash'],task_ids=order,events=events,root=root)
            prompt_ok=all(e.get('status')=='compiled' and not validate_prompt_envelope(e,root=root) for e in prompt_envs)
            complete=rep['ok'] and all(rep['final_states'].get(t)=='done' for t in order) and prompt_ok
            if case['scenario']=='blocker_recovery': complete=complete and blocked_observed and recovered
            records.append({'stage':'execution','status':'pass' if complete else 'invalid','artifact_refs':['execution_events','prompt_envelopes'],'diagnostics':rep['diagnostics']})
            status='completed' if complete else 'invalid'
            artifacts['execution_events']=_hash(events); artifacts['prompt_envelopes']=_hash(prompt_envs)
    artifacts['source_project']=_hash(project)
    metrics={'manual_artifact_reconstruction_count':0,'critical_gate_bypass_count':0,'scope_escape_count':0,'prerequisite_escape_count':0,'owner_decision_escape_count':0,
             'blocked_then_recovered':blocked_observed and recovered,'prompt_envelope_count':len(prompt_envs)}
    run={'schema_version':'1.0','run_id':rid,'project_id':pid,'candidate_version':'0.10','status':status,'stage_records':records,'artifact_hashes':dict(sorted(artifacts.items())),
         'metrics':metrics,'diagnostics':diagnostics,'run_hash':''}
    run['run_hash']=canonical_hash(run,{'run_hash'})
    continuation={'schema_version':'1.0','project_id':pid,'graph_hash':graph['graph_hash'] if graph else '', 'execution_events':events}
    return {'run':run,'compiled_task_graph':graph,'execution_events':events,'prompt_envelopes':prompt_envs,'continuation':continuation}
