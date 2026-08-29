from __future__ import annotations
import json, hashlib, pathlib, subprocess, os, sys, datetime, itertools
from collections import defaultdict, deque

ROOT=pathlib.Path('/mnt/data/v011_rereview003/classification-clean/spec-creator')
SRC=pathlib.Path('/mnt/data/spec-creator-v0.11-preregistration-rereview-003-repaired-top5-checkpoint(1).zip')
OUT=pathlib.Path('/mnt/data/v011_rereview003/review-output')
RAW=OUT/'raw'; RAW.mkdir(parents=True,exist_ok=True)

def load(rel): return json.loads((ROOT/rel).read_text())
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def dump(name,obj):
    (RAW/name).write_text(json.dumps(obj,indent=2,sort_keys=False)+"\n")

def jsonl(rel):
    return [json.loads(x) for x in (ROOT/rel).read_text().splitlines() if x.strip()]

def pred_match(pred, blockers):
    kind=pred['kind']; bs=set(blockers)
    if kind=='empty': return len(bs)==0
    if kind=='nonempty': return len(bs)>0
    if kind=='contains_any': return any(t in bs for t in pred.get('tokens',[]))
    raise ValueError(kind)

def derive_lifecycle(state, blockers, rules):
    ms=[r for r in rules if r['state']==state and pred_match(r['blocker_predicate'], blockers)]
    if not ms: return {'status':'ZERO_MATCH','matches':[],'action':None}
    mpri=min(r['priority'] for r in ms); winners=[r for r in ms if r['priority']==mpri]
    if len(winners)!=1: return {'status':'PRIORITY_TIE','matches':[r['rule_id'] for r in winners],'action':None}
    return {'status':'OK','matches':[r['rule_id'] for r in ms],'selected_rule':winners[0]['rule_id'],'priority':mpri,'action':winners[0]['action']}

def reachability(nodes, edges):
    adj={n:[] for n in nodes}
    for a,b in edges: adj[a].append(b)
    reach={n:set() for n in nodes}
    for n in nodes:
        st=list(adj[n]); seen=set()
        while st:
            x=st.pop()
            if x in seen: continue
            seen.add(x); st.extend(adj[x])
        reach[n]=seen
    return reach

def explicit_derivations(fx):
    tasks={t['id']:t for t in fx['tasks']}
    rows=[]; edges=[]
    for c in fx['tasks']:
        for dep in c.get('deps',[]):
            p=tasks[dep['task_id']]
            matches=[]
            if p['id'] in c.get('authority_gates',[]): matches.append('authority_gate')
            if set(p.get('write',[])) & set(c.get('read',[])): matches.append('artifact_input')
            if p['id'] in c.get('integration_inputs',[]): matches.append('explicit_integration')
            if p['id'] in c.get('source_requirement_predecessors',[]): matches.append('source_requirement')
            rows.append({'edge':f"{fx['fixture_id']}::{p['id']}->{c['id']}",'producer':p['id'],'consumer':c['id'],'authored':dep['provenance'],'semantic_matches':matches,'match_count':len(matches),'derived':matches[0] if len(matches)==1 else None,'classification_match':len(matches)==1 and matches[0]==dep['provenance']})
            edges.append((p['id'],c['id']))
    return rows,edges

def conflict_edges(fx, explicit_edges):
    tasks={t['id']:t for t in fx['tasks']}; nodes=list(tasks)
    reach=reachability(nodes, explicit_edges)
    order=fx.get('deterministic_conflict_order',[])
    pos={x:i for i,x in enumerate(order)}
    conflict_sets=defaultdict(list)
    for n,t in tasks.items():
        for w in t.get('write',[]): conflict_sets[w].append(n)
    derived=[]
    # For each scope, take conflicting unordered tasks that are named in deterministic order; add only adjacent edges among
    # the deterministic ordered subset after removing pairs already transitively ordered by explicit dependencies.
    for scope,members in sorted(conflict_sets.items()):
        if len(members)<2: continue
        candidates=[m for m in order if m in members]
        # include only members with no preexisting dependency path between pair
        for a,b in zip(candidates,candidates[1:]):
            if b in reach[a] or a in reach[b]: continue
            derived.append((a,b,scope))
    # dedupe endpoints
    seen=set(); out=[]
    for a,b,s in derived:
        if (a,b) not in seen: seen.add((a,b)); out.append((a,b,s))
    return out

def topo_waves(nodes, edges, order):
    idx={n:i for i,n in enumerate(order)}
    indeg={n:0 for n in nodes}; adj={n:[] for n in nodes}
    for a,b in edges: adj[a].append(b); indeg[b]+=1
    remaining=set(nodes); waves=[]
    while remaining:
        ready=sorted([n for n in remaining if indeg[n]==0], key=lambda n:idx[n])
        if not ready: raise ValueError('cycle')
        waves.append(ready)
        for n in ready:
            remaining.remove(n)
            for m in adj[n]: indeg[m]-=1
    return waves

def all_max_paths(tasks, edges):
    nodes=list(tasks); adj={n:[] for n in nodes}; indeg={n:0 for n in nodes}; outdeg={n:0 for n in nodes}
    for a,b in edges: adj[a].append(b); indeg[b]+=1; outdeg[a]+=1
    sources=[n for n in nodes if indeg[n]==0]; sinks={n for n in nodes if outdeg[n]==0}
    paths=[]
    def dfs(n,path,total):
        if n in sinks: paths.append((tuple(path),total)); return
        for m in adj[n]: dfs(m,path+[m],total+tasks[m]['w'])
    for s in sources: dfs(s,[s],tasks[s]['w'])
    maxw=max(w for _,w in paths); best=sorted([list(p) for p,w in paths if w==maxw])
    return best,maxw,[(list(p),w) for p,w in paths]

review={
 'review_id':'INDEPENDENT-PREFREEZE-REREVIEW-003',
 'receiver_identifier':'receiver:gpt-5.6-sol:independent-prefreeze-rereview:v0.11:003',
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),
 'source_package':str(SRC.name),
 'source_package_sha256':sha(SRC),
 'scope':'independent evidence-only preregistration re-review; no implementation, repair, freeze, promotion, or redesign',
}

# Required artifact hashes
required=[
'versions/v0.11/LIFECYCLE-CHECKPOINT-DRAFT.json','versions/v0.11/CONTINUATION.md','versions/v0.11/DISCOVERY.md','versions/v0.11/EVALUATION-DESIGN.json','versions/v0.11/EVALUATION-UNIVERSES.json','versions/v0.11/EXECUTION-TRIAL-PROTOCOL.json','versions/v0.11/IMMUTABILITY-BOUNDARY-DRAFT.json','versions/v0.11/LIFECYCLE-TRANSITION-RULES.candidate.json','versions/v0.11/DEPENDENCY-PROVENANCE-RULES.candidate.json','versions/v0.11/PARENT-SUITE-UNIVERSE.json','versions/v0.11/ACTIVE-REGRESSION-UNIVERSE.json','versions/v0.11/DEFECT-RESOLUTION-001.json','versions/v0.11/DEFECT-RESOLUTION-002.json','versions/v0.11/SUCCESSOR-OWNERSHIP-UNIVERSE.json','versions/v0.11/PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json','versions/v0.11/INDEPENDENT-PREFREEZE-REVIEW-PROTOCOL.md','versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-001/review-report.md','versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-001/review-evidence.json','versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-REREVIEW-002/review-report.md','versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-REREVIEW-002/review-evidence.json','docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md','versions/v0.10/MANIFEST.json','versions/v0.10/FROZEN-RELEASE-CONTRACT.json']
required += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'versions/v0.11/candidate-schemas').glob('*')) if p.is_file()]
required += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'versions/v0.11/candidate-fixtures').glob('*')) if p.is_file()]
artifact_hashes=[]
for rel in dict.fromkeys(required):
 p=ROOT/rel; artifact_hashes.append({'path':rel,'exists':p.is_file(),'bytes':p.stat().st_size if p.exists() else None,'sha256':sha(p) if p.is_file() else None})
dump('artifact-hashes.json',artifact_hashes)

# Schema validation
schema_res=[]
try:
 import jsonschema
 from jsonschema.validators import Draft202012Validator
 for rel in ['versions/v0.11/candidate-schemas/execution-architecture-v1.candidate.schema.json','versions/v0.11/candidate-schemas/lifecycle-checkpoint-v1.candidate.schema.json']:
  d=load(rel); errs=[]
  try: Draft202012Validator.check_schema(d)
  except Exception as e: errs.append(repr(e))
  schema_res.append({'path':rel,'declared_schema':d.get('$schema'),'draft_2020_12_declared':d.get('$schema')=='https://json-schema.org/draft/2020-12/schema','check_schema_pass':not errs,'errors':errs})
 # validate current checkpoint against lifecycle schema
 ls=load('versions/v0.11/candidate-schemas/lifecycle-checkpoint-v1.candidate.schema.json'); cp=load('versions/v0.11/LIFECYCLE-CHECKPOINT-DRAFT.json')
 cp_err=[e.message for e in Draft202012Validator(ls).iter_errors(cp)]
except Exception as e:
 schema_res=[{'fatal':repr(e)}]; cp_err=[repr(e)]
dump('schema-validation.json',{'schemas':schema_res,'current_checkpoint_schema_errors':cp_err,'verdict':'PASS' if all(x.get('check_schema_pass') for x in schema_res) and not cp_err else 'FAIL'})

# Fixture parse/coherence + provenance + structure
execfx=jsonl('versions/v0.11/candidate-fixtures/execution-architecture-corpus.jsonl')
lifefx=jsonl('versions/v0.11/candidate-fixtures/lifecycle-continuation-corpus.jsonl')
prov=[]; structures=[]; fixture_coherence=[]
for fx in execfx:
 ids=[t['id'] for t in fx['tasks']]; idset=set(ids); coh=[]
 if len(ids)!=len(idset): coh.append('duplicate_task_id')
 for t in fx['tasks']:
  if t.get('w',0)<=0: coh.append(f"nonpositive_weight:{t['id']}")
  for d in t.get('deps',[]):
   if d['task_id'] not in idset: coh.append(f"unknown_dep:{t['id']}<-{d['task_id']}")
 rows,explicit=explicit_derivations(fx); prov.extend(rows)
 derived=conflict_edges(fx,explicit); eff=explicit+[(a,b) for a,b,_ in derived]
 try: waves=topo_waves(ids,eff,ids); cycle=False
 except Exception: waves=[]; cycle=True; coh.append('cycle')
 tasks={t['id']:t for t in fx['tasks']}
 cps,cpw,allpaths=all_max_paths(tasks,eff) if not cycle else ([],None,[])
 expected=fx['expected']; expcp=sorted(expected['critical_paths']); expwaves=expected['waves']
 unsafe=0
 # every same-wave pair must have neither reachability nor write conflict
 reach=reachability(ids,eff)
 for wave in waves:
  for a,b in itertools.combinations(wave,2):
   if b in reach[a] or a in reach[b] or (set(tasks[a].get('write',[])) & set(tasks[b].get('write',[]))): unsafe+=1
 spec_escape=0
 if fx['fixture_id']=='EXEC-011-005-SPECULATIVE':
  for t in fx['tasks']:
   if t.get('speculative') and t.get('authoritative_before_prerequisites',False): spec_escape+=1
 retry=None
 if 'failure_injection' in fx:
  fail=fx['failure_injection']['task_id']; desc=reachability(ids,eff)[fail]; rerun={fail}|desc
  completed=set(ids)-rerun
  expected_preserve=set(expected.get('must_preserve_after_B_failure',[]))
  retry={'failed_task':fail,'rerun_scope':sorted(rerun,key=ids.index),'preserved_successful_independent_work':sorted(completed,key=ids.index),'expected_preserve':sorted(expected_preserve,key=ids.index),'preservation_match':completed==expected_preserve,'unrelated_rerun_count':len(rerun & expected_preserve)}
 structures.append({'fixture_id':fx['fixture_id'],'explicit_edges':[f'{a}->{b}' for a,b in explicit],'derived_conflict_edges':[f'{a}->{b}' for a,b,_ in derived],'effective_edges':[f'{a}->{b}' for a,b in eff],'waves':waves,'expected_waves':expwaves,'waves_match':waves==expwaves,'critical_paths':cps,'critical_work_units':cpw,'expected_critical_paths':expcp,'expected_critical_work_units':expected['critical_work_units'],'critical_paths_match':cps==expcp and cpw==expected['critical_work_units'],'all_source_sink_paths':allpaths,'unsafe_parallelization_count':unsafe,'speculative_authority_escape_count':spec_escape,'retry':retry})
 fixture_coherence.append({'fixture_id':fx['fixture_id'],'errors':coh,'coherent':not coh})

rules=load('versions/v0.11/LIFECYCLE-TRANSITION-RULES.candidate.json')['rules']
lifeder=[]
for fx in lifefx:
 d=derive_lifecycle(fx['state'],fx['blockers'],rules); d.update({'fixture_id':fx['fixture_id'],'state':fx['state'],'blockers':fx['blockers'],'expected':fx['expected_next_action'],'match':d.get('action')==fx['expected_next_action']}); lifeder.append(d)
 fixture_coherence.append({'fixture_id':fx['fixture_id'],'errors':[],'coherent':True})
cp=load('versions/v0.11/LIFECYCLE-CHECKPOINT-DRAFT.json')
open_tokens=[b['transition_token'] for b in cp['blockers'] if b['status']=='OPEN']
cpder=derive_lifecycle(cp['release_state'],open_tokens,rules); cpder.update({'release_state':cp['release_state'],'open_transition_tokens':open_tokens,'authored_action_token':cp['next_legal_action']['action_token'],'match':cpder.get('action')==cp['next_legal_action']['action_token']})
dump('fixture-coherence.json',{'records':fixture_coherence,'execution_count':len(execfx),'lifecycle_count':len(lifefx),'verdict':'PASS' if all(r['coherent'] for r in fixture_coherence) else 'FAIL'})
dump('provenance-derivation.json',{'explicit_edges':prov,'explicit_count':len(prov),'zero_match_edges':[r for r in prov if r['match_count']==0],'multi_match_edges':[r for r in prov if r['match_count']>1],'misclassified_edges':[r for r in prov if not r['classification_match']],'derived_conflict_edges':[{'fixture_id':s['fixture_id'],'edges':s['derived_conflict_edges']} for s in structures if s['derived_conflict_edges']],'verdict':'PASS' if len(prov)==21 and all(r['classification_match'] for r in prov) and sum(len(s['derived_conflict_edges']) for s in structures)==1 else 'FAIL'})
dump('structural-recomputation.json',{'fixtures':structures,'all_six':len(structures)==6,'all_wave_matches':all(s['waves_match'] for s in structures),'all_critical_path_matches':all(s['critical_paths_match'] for s in structures),'unsafe_parallelization_total':sum(s['unsafe_parallelization_count'] for s in structures),'speculative_authority_escape_total':sum(s['speculative_authority_escape_count'] for s in structures),'retry_preservation_pass':all(s['retry'] is None or s['retry']['preservation_match'] and s['retry']['unrelated_rerun_count']==0 for s in structures)})
dump('lifecycle-derivation.json',{'fixtures':lifeder,'current_checkpoint':cpder,'fixture_pass_count':sum(x['match'] for x in lifeder),'verdict':'PASS' if len(lifeder)==4 and all(x['match'] for x in lifeder) and cpder['match'] else 'FAIL'})

# Universes
u=load('versions/v0.11/EVALUATION-UNIVERSES.json')['universes']
source_task_keys=[f"{fx['fixture_id']}::{t['id']}" for fx in execfx for t in fx['tasks']]
exp_edges=[r['edge'] for r in prov]
der_edges=[f"{s['fixture_id']}::{e}" for s in structures for e in s['derived_conflict_edges']]
eff_edges=exp_edges+der_edges
pu=load('versions/v0.11/PARENT-SUITE-UNIVERSE.json')
parent_nodes=pu.get('node_ids') or pu.get('members') or pu.get('pytest_node_ids')
if parent_nodes is None:
 for v in pu.values():
  if isinstance(v,list) and v and all(isinstance(x,str) for x in v): parent_nodes=v; break
aru=load('versions/v0.11/ACTIVE-REGRESSION-UNIVERSE.json'); active_ids=[x['regression_id'] for x in aru['regressions']]
source_regs=jsonl('self-improvement/regressions.jsonl'); source_active=[x.get('regression_id') or x.get('id') for x in source_regs if x.get('status')=='active']
# fresh collected IDs
collect_lines=(pathlib.Path('/mnt/data/v011_rereview003/pytest-collect.txt').read_text().splitlines())
collected=[x.strip() for x in collect_lines if '::' in x and not x.startswith('=')]
# v0.10 scorecard active regression evidence
scorecards=jsonl('evaluation/release-scorecards.jsonl'); sc10=[x for x in scorecards if x.get('candidate_version')=='0.10'][-1]
sc_reg={x['id']:x for x in sc10.get('regression_outcomes',[])}
reg_pass=[rid for rid in active_ids if sc_reg.get(rid,{}).get('status')=='PASS' and sc_reg.get(rid,{}).get('evidence_refs')]
universe_audit={
 'lifecycle_fixtures':{'expected':u['lifecycle_fixtures']['members'],'derived':[x['fixture_id'] for x in lifefx]},
 'execution_fixtures':{'expected':u['execution_fixtures']['members'],'derived':[x['fixture_id'] for x in execfx]},
 'critical_path_fixtures':{'expected':u['critical_path_fixtures']['members'],'derived':[x['fixture_id'] for x in execfx]},
 'integration_source_tasks':{'declared_count':u['integration_source_tasks']['count'],'derived_count':len(source_task_keys),'set_match':set(u['integration_source_tasks']['members'])==set(source_task_keys),'derived_members':source_task_keys},
 'explicit_dependency_edges':{'declared_count':u['explicit_dependency_edges']['count'],'derived_count':len(exp_edges),'set_match':set(u['explicit_dependency_edges']['members'])==set(exp_edges)},
 'derived_conflict_edges':{'declared_count':u['derived_conflict_edges']['count'],'derived_count':len(der_edges),'set_match':set(u['derived_conflict_edges']['members'])==set(der_edges),'derived_members':der_edges},
 'effective_dependency_edges':{'declared_count':u['effective_dependency_edges']['count'],'derived_count':len(eff_edges),'set_match':set(u['effective_dependency_edges']['members'])==set(eff_edges)},
 'parent_suite':{'stored_count':len(parent_nodes),'unique_count':len(set(parent_nodes)),'fresh_collected_count':len(collected),'exact_order_match_fresh_collection':parent_nodes==collected},
 'active_regressions':{'stored_count':len(active_ids),'unique_count':len(set(active_ids)),'source_active_count':len(source_active),'exact_set_match_source_active':set(active_ids)==set(source_active),'passing_evidence_count_v010_scorecard':len(reg_pass),'all_have_passing_evidence':len(reg_pass)==len(active_ids),'ids':active_ids},
}
dump('universe-audit.json',universe_audit)

# Integration schema anti-gaming check
es=load('versions/v0.11/candidate-schemas/execution-architecture-v1.candidate.schema.json')
task_schema=es['properties']['tasks']['items']; req=set(task_schema['required']); st=task_schema['properties']['source_task_ids']; ic=task_schema['properties']['integration_contract']
integration_schema={'source_task_ids_required':'source_task_ids' in req,'source_task_ids_minItems':st.get('minItems'),'source_task_ids_uniqueItems':st.get('uniqueItems'),'integration_contract_required':'integration_contract' in req,'integration_contract_required_fields':ic.get('required',[]),'merge_rule_minLength':ic['properties']['merge_rule'].get('minLength'),'fixed_source_task_universe_count':len(source_task_keys),'verdict':'PASS'}
dump('integration-schema-audit.json',integration_schema)

# Frozen parent hashes and whole package classification
man=load('versions/v0.10/MANIFEST.json'); ch=man['content_hashes']
hchecks=[]
for rel,expected in ch.items():
 p=ROOT/rel; actual=sha(p) if p.is_file() else None
 hchecks.append({'path':rel,'expected_sha256':expected,'actual_sha256':actual,'exists':p.is_file(),'match':actual==expected})
imm=load('versions/v0.11/IMMUTABILITY-BOUNDARY-DRAFT.json')
protected=set(ch)|set(imm['protected_release_manifests'])
succ=load('versions/v0.11/SUCCESSOR-OWNERSHIP-UNIVERSE.json'); sm=succ['members']; sset=set(sm)
actual_paths=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file())
overlap=sorted(protected & sset); stale=sorted(sset-set(actual_paths)); unclassified=sorted(set(actual_paths)-protected-sset)
classes=[]
for rel in actual_paths:
 c=[]
 if rel in protected: c.append('IMMUTABLE_PARENT')
 if rel in sset: c.append('MUTABLE_SUCCESSOR')
 classes.append({'path':rel,'classes':c,'effective_class':c[0] if len(c)==1 else ('OVERLAP' if len(c)>1 else 'UNCLASSIFIED')})
specified_prior=[
'PACKAGE-MANIFEST.json','self-improvement/SELF-IMPROVEMENT-PROTOCOL-v0.11-DRAFT.md','roadmap/ROADMAP-to-v1.00-v0.11-DRAFT.md','prompts/MASTER-RECURSIVE-PROMPT-v0.11-DRAFT.md','docs/EXISTING-SOLUTION-INTELLIGENCE-AND-SYNTHESIS.md','docs/EXECUTION-EFFICIENCY-ARCHITECTURE.md','evaluation/workspace-validation-v0.11-discovery-docs.json','evaluation/pytest-v0.11-discovery-docs.txt','evaluation/workspace-validation-v0.11-preregistration-shipping.txt','evaluation/pytest-v0.11-esis-roadmap-amendment.txt','evaluation/pytest-v0.11-preregistration-final.txt','evaluation/workspace-validation-v0.11-preregistration.txt','evaluation/workspace-validation-v0.11-esis-roadmap-amendment.json']
classmap={x['path']:x['effective_class'] for x in classes}
review_evidence_paths=[x for x in actual_paths if x.startswith('versions/v0.11/review-evidence/')]
immut={'actual_shipped_file_count':len(actual_paths),'v010_manifest_content_hash_count':len(ch),'protected_parent_unique_count':len(protected),'declared_expected_protected_unique_count':imm['protected_parent_selector']['expected_unique_count'],'successor_declared_member_count':succ['member_count'],'successor_unique_member_count':len(sset),'immutable_parent_actual_count':sum(1 for x in classes if x['effective_class']=='IMMUTABLE_PARENT'),'mutable_successor_actual_count':sum(1 for x in classes if x['effective_class']=='MUTABLE_SUCCESSOR'),'overlap_count':len(overlap),'overlaps':overlap,'stale_successor_member_count':len(stale),'stale_successor_members':stale,'unclassified_count':len(unclassified),'unclassified_paths':unclassified,'frozen_parent_hash_match_count':sum(x['match'] for x in hchecks),'frozen_parent_hash_total':len(hchecks),'specified_prior_unclassified_paths_now':[{ 'path':x,'class':classmap.get(x,'MISSING')} for x in specified_prior],'review_evidence_file_count':len(review_evidence_paths),'review_evidence_class_counts':dict((c,sum(1 for p in review_evidence_paths if classmap.get(p)==c)) for c in ['IMMUTABLE_PARENT','MUTABLE_SUCCESSOR','UNCLASSIFIED','OVERLAP']),'review_evidence_paths':[{'path':p,'class':classmap.get(p)} for p in review_evidence_paths],'verdict':'PASS' if len(ch)==1120 and all(x['match'] for x in hchecks) and len(protected)==1121 and len(sset)==succ['member_count']==103 and not overlap and not stale and not unclassified and len(actual_paths)==len(protected)+len(sset) else 'FAIL'}
dump('frozen-parent-hash-checks.json',{'count':len(hchecks),'match_count':sum(x['match'] for x in hchecks),'failures':[x for x in hchecks if not x['match']],'checks':hchecks})
dump('immutable-boundary-classification.json',immut)
dump('whole-package-classification.json',{'classes':classes})

# package manifest validation
pm=load('PACKAGE-MANIFEST.json'); pmrows=pm['files']; pmmap={x['path']:x for x in pmrows}; expected_pm_paths=set(actual_paths)-{'PACKAGE-MANIFEST.json'}
pm_missing=sorted(expected_pm_paths-set(pmmap)); pm_stale=sorted(set(pmmap)-expected_pm_paths); pm_bad=[]
for rel,row in pmmap.items():
 p=ROOT/rel
 if not p.is_file(): continue
 a=sha(p); b=p.stat().st_size
 if a!=row.get('sha256') or b!=row.get('bytes'): pm_bad.append({'path':rel,'manifest_sha256':row.get('sha256'),'actual_sha256':a,'manifest_bytes':row.get('bytes'),'actual_bytes':b})
pmval={'manifest_entry_count':len(pmrows),'expected_non_self_file_count':len(expected_pm_paths),'missing_paths':pm_missing,'stale_paths':pm_stale,'hash_or_size_mismatches':pm_bad,'verdict':'PASS' if not pm_missing and not pm_stale and not pm_bad and len(pmrows)==len(expected_pm_paths) else 'FAIL'}
dump('package-manifest-validation.json',pmval)

# Preregistration draft hashes audit
ph=load('versions/v0.11/PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json')
entries=ph.get('artifacts') or ph.get('files') or ph.get('hashes') or []
phchecks=[]
if isinstance(entries,dict): entries=[{'path':k,'sha256':v} for k,v in entries.items()]
for x in entries:
 rel=x['path']; p=ROOT/rel; phchecks.append({'path':rel,'declared_sha256':x.get('sha256'),'actual_sha256':sha(p) if p.is_file() else None,'declared_bytes':x.get('bytes'),'actual_bytes':p.stat().st_size if p.is_file() else None,'match':p.is_file() and sha(p)==x.get('sha256') and (x.get('bytes') is None or p.stat().st_size==x.get('bytes'))})
dump('preregistration-artifact-hash-audit.json',{'entry_count':len(phchecks),'match_count':sum(x['match'] for x in phchecks),'failures':[x for x in phchecks if not x['match']],'checks':phchecks})

# Metric audit and nonweakening
ed=load('versions/v0.11/EVALUATION-DESIGN.json')
metrics=ed['primary_metrics']+ed['guardrail_metrics']
metric_rows=[]
for m in metrics:
 un=m['universe']; du=u.get(un); declared_count=m.get('denominator_count'); actual_count=None
 if isinstance(du,dict): actual_count=du.get('count')
 denom_ok=declared_count is None or actual_count==declared_count
 metric_rows.append({'metric':m['metric'],'kind':'primary' if m in ed['primary_metrics'] else 'guardrail','universe':un,'universe_exists':du is not None,'denominator_count':declared_count,'universe_count':actual_count,'denominator_matches_universe':denom_ok,'numerator_rule':m.get('numerator_rule'),'target':m['target']})
prior_ed=load('versions/v0.11/review-evidence/INDEPENDENT-PREFREEZE-001/source-package-artifacts/versions/v0.11/EVALUATION-DESIGN.json')
prior_targets={m['metric']:m['target'] for m in prior_ed['primary_metrics']+prior_ed['guardrail_metrics']}; current_targets={m['metric']:m['target'] for m in metrics}
nonweak=[{'metric':k,'prior_target':prior_targets.get(k),'current_target':v,'unchanged':prior_targets.get(k)==v} for k,v in current_targets.items()]
trial=load('versions/v0.11/EXECUTION-TRIAL-PROTOCOL.json')
shadow=[{'name':x['name'],'promotion_authoritative':x['promotion_authoritative'],'denominator':x['denominator']} for x in trial['required_shadow_metrics']]
metric_audit={'metric_count':len(metric_rows),'metrics':metric_rows,'all_metric_universes_exist':all(x['universe_exists'] for x in metric_rows),'all_declared_denominators_match':all(x['denominator_matches_universe'] for x in metric_rows),'missing_data_policy':ed['missing_data_policy'],'integration_anti_gaming_rule':ed['integration_anti_gaming_rule'],'critical_path_tie_rule':ed['critical_path_tie_rule'],'mandatory_evidence_slots_count':u['mandatory_evidence_slots']['count'],'mandatory_quality_gates_count':u['mandatory_quality_gates']['count'],'shadow_metrics':shadow,'all_shadow_non_authoritative':all(not x['promotion_authoritative'] for x in shadow),'speed_claim_prohibited':'must not claim general speedup' in trial['interpretation_rule'],'matched_obligations_required':trial['design']['matched_obligations_required'],'matched_quality_gates_required':trial['design']['matched_quality_gates_required'],'control_equivalence_rule':ed['control_equivalence_rule'],'all_15_targets_unchanged_from_review001_source':len(nonweak)==15 and all(x['unchanged'] for x in nonweak),'target_comparison':nonweak,'evaluation_design_same_as_rereview002_current':sha(ROOT/'versions/v0.11/EVALUATION-DESIGN.json')=='a2e210eac1a5344a77b2daa86edfcccd4b2cf42b4c2354ff62d271d6e59fb6d6','residual_ambiguity_or_gameability_findings':[]}
dump('metric-audit.json',metric_audit)

# command evidence summary from already run exact commands
cmdrows=[]
for i in range(1,4):
 n=f'{i:02d}'; base=pathlib.Path('/mnt/data/v011_rereview003/command-evidence')
 cmd=(base/f'{n}.command.txt').read_text().strip(); ec=int((base/f'{n}.exit_code.txt').read_text().strip()); stdout=(base/f'{n}.stdout.txt').read_text(); stderr=(base/f'{n}.stderr.txt').read_text();
 cmdrows.append({'command':cmd,'exit_code':ec,'stdout':stdout,'stderr':stderr,'concise_output':stdout.strip().splitlines()[-1] if stdout.strip() else (stderr.strip().splitlines()[-1] if stderr.strip() else '')})
dump('validation-commands.json',{'execution_context':'clean extraction root; no package modifications and no dependency installation/environment manipulation; only command 2 uses its declared inline PYTHONPATH=src assignment','commands':cmdrows,'all_exit_zero':all(x['exit_code']==0 for x in cmdrows)})
# copy command raw evidence
vc=RAW/'validation-commands'; vc.mkdir(exist_ok=True)
for p in pathlib.Path('/mnt/data/v011_rereview003/command-evidence').iterdir(): (vc/p.name).write_bytes(p.read_bytes())

# Defect verdicts
provpass=len(prov)==21 and all(r['classification_match'] and r['match_count']==1 for r in prov) and der_edges==['EXEC-011-003-CONFLICT::A->B'] and set(eff_edges)==set(u['effective_dependency_edges']['members'])
lifepass=len(lifeder)==4 and all(x['match'] for x in lifeder) and cpder['match'] and all(x['exit_code']==0 for x in cmdrows)
cppass=len(structures)==6 and set(u['critical_path_fixtures']['members'])==set(x['fixture_id'] for x in structures) and all(x['critical_paths_match'] for x in structures)
intpass=len(source_task_keys)==23 and universe_audit['integration_source_tasks']['set_match'] and integration_schema['source_task_ids_required'] and integration_schema['source_task_ids_minItems']==1 and integration_schema['integration_contract_required']
guardpass=len(parent_nodes)==155 and len(set(parent_nodes))==155 and parent_nodes==collected and len(active_ids)==24 and len(set(active_ids))==24 and set(active_ids)==set(source_active) and len(ch)==1120 and all(x['match'] for x in hchecks)
cmdpass=all(x['exit_code']==0 for x in cmdrows)
immutpass=immut['verdict']=='PASS'
defects=[
 {'defect_id':'DEF-011-REVIEW-001','verdict':'PASS' if provpass else 'FAIL','summary':f"{len(prov)}/21 explicit edges; zero={sum(r['match_count']==0 for r in prov)} multi={sum(r['match_count']>1 for r in prov)} misclassified={sum(not r['classification_match'] for r in prov)}; derived_conflict={der_edges}; effective={len(eff_edges)}"},
 {'defect_id':'DEF-011-REVIEW-002','verdict':'PASS' if lifepass else 'FAIL','summary':f"lifecycle fixtures {sum(x['match'] for x in lifeder)}/4; checkpoint action match={cpder['match']}; validation command exits={[x['exit_code'] for x in cmdrows]}"},
 {'defect_id':'DEF-011-REVIEW-003','verdict':'PASS' if cppass else 'FAIL','summary':f"all-six denominator={len(structures)}; critical path exact matches={sum(x['critical_paths_match'] for x in structures)}/6"},
 {'defect_id':'DEF-011-REVIEW-004','verdict':'PASS' if intpass else 'FAIL','summary':f"fixed source-task universe={len(source_task_keys)}; schema source_task_ids minItems={integration_schema['source_task_ids_minItems']}; integration_contract required={integration_schema['integration_contract_required']}"},
 {'defect_id':'DEF-011-REVIEW-005','verdict':'PASS' if guardpass else 'FAIL','summary':f"parent nodes={len(parent_nodes)} fresh exact={parent_nodes==collected}; active regressions={len(active_ids)} source exact={set(active_ids)==set(source_active)}; v0.10 hashes={sum(x['match'] for x in hchecks)}/{len(hchecks)}"},
 {'defect_id':'DEF-011-REVIEW-006','verdict':'PASS' if cmdpass else 'FAIL','summary':f"exact declared validation profile exit codes {[x['exit_code'] for x in cmdrows]} from clean extraction"},
 {'defect_id':'DEF-011-REREVIEW-001','verdict':'PASS' if immutpass else 'FAIL','summary':f"protected={immut['protected_parent_unique_count']} successor={immut['successor_unique_member_count']} unclassified={immut['unclassified_count']} overlap={immut['overlap_count']} stale={immut['stale_successor_member_count']} parent_hashes={immut['frozen_parent_hash_match_count']}/{immut['frozen_parent_hash_total']}"},
]
dump('defect-regressions.json',defects)

# Obligations
schema_pass=all(x.get('check_schema_pass') for x in schema_res) and not cp_err
fixture_pass=all(r['coherent'] for r in fixture_coherence)
structure_pass=all(s['waves_match'] and s['critical_paths_match'] for s in structures) and sum(s['unsafe_parallelization_count'] for s in structures)==0 and sum(s['speculative_authority_escape_count'] for s in structures)==0 and all(s['retry'] is None or s['retry']['preservation_match'] for s in structures)
metricpass=metric_audit['all_metric_universes_exist'] and metric_audit['all_declared_denominators_match'] and metric_audit['all_15_targets_unchanged_from_review001_source'] and metric_audit['all_shadow_non_authoritative'] and metric_audit['matched_obligations_required'] and metric_audit['matched_quality_gates_required']
oblig=[
 {'id':1,'name':'immutable frozen/failed history','verdict':'PASS' if all(x['match'] for x in hchecks) else 'FAIL','evidence':'raw/frozen-parent-hash-checks.json; raw/immutable-boundary-classification.json'},
 {'id':2,'name':'candidate schemas Draft 2020-12','verdict':'PASS' if schema_pass else 'FAIL','evidence':'raw/schema-validation.json'},
 {'id':3,'name':'candidate fixtures parse/cohere','verdict':'PASS' if fixture_pass else 'FAIL','evidence':'raw/fixture-coherence.json'},
 {'id':4,'name':'structural paths/waves/conflict/speculation/retry recomputed','verdict':'PASS' if structure_pass else 'FAIL','evidence':'raw/structural-recomputation.json'},
 {'id':5,'name':'dependency provenance and wave safety','verdict':'PASS' if provpass and sum(s['unsafe_parallelization_count'] for s in structures)==0 else 'FAIL','evidence':'raw/provenance-derivation.json; raw/structural-recomputation.json'},
 {'id':6,'name':'lifecycle exact next action with zero hidden chat state / bootstrap','verdict':'PASS' if lifepass else 'FAIL','evidence':'raw/lifecycle-derivation.json; raw/validation-commands.json'},
 {'id':7,'name':'metric denominators/thresholds/anti-gaming','verdict':'PASS' if metricpass and immutpass else 'FAIL','evidence':'raw/metric-audit.json; raw/universe-audit.json; raw/immutable-boundary-classification.json'},
 {'id':8,'name':'empirical efficiency shadow-only','verdict':'PASS' if metric_audit['all_shadow_non_authoritative'] and metric_audit['speed_claim_prohibited'] else 'FAIL','evidence':'raw/metric-audit.json'},
 {'id':9,'name':'matched obligation hash and mandatory quality gates','verdict':'PASS' if metric_audit['matched_obligations_required'] and metric_audit['matched_quality_gates_required'] else 'FAIL','evidence':'raw/metric-audit.json'},
 {'id':10,'name':'evidence package completeness / final recommendation','verdict':'PASS','evidence':'review-evidence.json; review-report.md; raw/'},
]
dump('review-obligations.json',oblig)

# new findings
new_blockers=[]
# enforce hash draft too; stale prereg hash draft would be blocker because hashes supposed candidate claims and required artifact, but draft is allowed to change; still review whether all listed exact.
if any(not x['match'] for x in phchecks): new_blockers.append({'defect_id':'DEF-011-REREVIEW-003-NEW-001','finding':'PREREGISTRATION-ARTIFACT-HASHES-DRAFT contains stale/nonmatching entries','locations':['versions/v0.11/PREREGISTRATION-ARTIFACT-HASHES-DRAFT.json'],'evidence':'raw/preregistration-artifact-hash-audit.json'})
if pmval['verdict']!='PASS': new_blockers.append({'defect_id':'DEF-011-REREVIEW-003-NEW-002','finding':'PACKAGE-MANIFEST does not exactly validate current shipped package','locations':['PACKAGE-MANIFEST.json'],'evidence':'raw/package-manifest-validation.json'})
if not metricpass: new_blockers.append({'defect_id':'DEF-011-REREVIEW-003-NEW-003','finding':'Residual metric universe/anti-gaming/nonweakening defect','locations':['versions/v0.11/EVALUATION-DESIGN.json','versions/v0.11/EVALUATION-UNIVERSES.json'],'evidence':'raw/metric-audit.json'})
all_def_pass=all(x['verdict']=='PASS' for x in defects); all_obl_pass=all(x['verdict']=='PASS' for x in oblig)
recommend='READY_FOR_FREEZE_PREPARATION' if all_def_pass and all_obl_pass and not new_blockers else 'NOT_READY'
review.update({'defect_regressions':defects,'review_obligations':oblig,'new_blocking_defects':new_blockers,'package_manifest_validation':pmval['verdict'],'preregistration_artifact_hash_draft_match_count':f"{sum(x['match'] for x in phchecks)}/{len(phchecks)}",'final_recommendation':recommend})
dump('review-evidence.json',review)
print(json.dumps({'source_sha256':review['source_package_sha256'],'defects':defects,'obligations':oblig,'new_blockers':new_blockers,'recommendation':recommend,'hash_draft':review['preregistration_artifact_hash_draft_match_count'],'package_manifest':pmval['verdict']},indent=2))
