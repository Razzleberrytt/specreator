from __future__ import annotations
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]; V=ROOT/'versions/v0.11.1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def matches(rel,s):
 k=s['kind']
 if k=='exact': return rel==s['value']
 if k=='prefix': return rel.startswith(s['value'])
 if k=='directory_filename_prefix':
  if not rel.startswith(s['directory']): return False
  tail=rel[len(s['directory']):]; return '/' not in tail and tail.startswith(s['value'])
 if k=='directory_filename_in':
  if not rel.startswith(s['directory']): return False
  tail=rel[len(s['directory']):]; return '/' not in tail and tail in set(s['values'])
 raise ValueError(k)
def main():
 errs=[]
 reg=load(V/'FROZEN-ARTIFACT-REGISTRY.json'); contract=load(V/'FROZEN-RELEASE-CONTRACT.json')
 for x in reg['artifacts']:
  p=ROOT/x['path']
  if not p.is_file() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']: errs.append('frozen artifact drift: '+x['path'])
 sys.path.insert(0,str(ROOT/'src')); from spec_creator.models import canonical_contract_hash
 if contract.get('contract_hash')!=canonical_contract_hash(contract): errs.append('contract_hash mismatch')
 pm=load(ROOT/'versions/v0.10/MANIFEST.json')
 for rel,h in pm['content_hashes'].items():
  if not (ROOT/rel).is_file() or sha(ROOT/rel)!=h: errs.append('v0.10 drift: '+rel)
 failed=load(V/'FAILED-PREDECESSOR-v0.11-BASELINE.json')
 for x in failed['entries']:
  p=ROOT/x['path']
  if not p.is_file() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']: errs.append('failed-v0.11 drift: '+x['path'])
 own=load(V/'SUCCESSOR-OWNERSHIP-UNIVERSE.json'); imm=load(V/'IMMUTABILITY-BOUNDARY-DRAFT.json')
 protected=set(pm['content_hashes'])|set(imm['protected_release_manifests']); fp={x['path'] for x in failed['entries']}
 transient={'.pytest_cache','__pycache__'}; un=[]; ov=[]; mm=[]
 for p in ROOT.rglob('*'):
  if not p.is_file() or any(q in transient for q in p.relative_to(ROOT).parts) or p.suffix=='.pyc': continue
  rel=p.relative_to(ROOT).as_posix(); ms=[s['selector_id'] for s in own['selectors'] if matches(rel,s)]
  if rel in protected or rel in fp:
   if ms: ov.append((rel,ms))
  elif len(ms)==0: un.append(rel)
  elif len(ms)>1: mm.append((rel,ms))
 if un: errs.append(f'unclassified={len(un)} first={un[:5]}')
 if ov: errs.append(f'immutable/successor overlap={len(ov)} first={ov[:3]}')
 if mm: errs.append(f'successor multimatch={len(mm)} first={mm[:3]}')
 prospective=load(V/'candidate-fixtures/ownership-prospective-paths.json')
 legal=prospective.get('legal_paths',prospective.get('paths',[])); legal=[x['path'] if isinstance(x,dict) else x for x in legal]
 for rel in legal:
  if len([s for s in own['selectors'] if matches(rel,s)])!=1 or rel in protected or rel in fp: errs.append('prospective classification failure: '+rel)
 if len(contract['primary_metrics'])+len(contract['guardrail_metrics'])!=16: errs.append('frozen metric count != 16')
 rev=load(V/'review-evidence/INDEPENDENT-PREFREEZE-001/review-evidence.json')
 if rev['final_recommendation']!='READY_FOR_FREEZE_PREPARATION' or any(x['verdict']!='PASS' for x in rev['obligations']) or rev['new_blocking_defects']: errs.append('independent prefreeze review not ready')
 if errs:
  print(f'FAIL: {len(errs)} error(s)'); [print('-',e) for e in errs[:50]]; return 1
 print(f"PASS: frozen registry {len(reg['artifacts'])}/{len(reg['artifacts'])}; v0.10 {len(pm['content_hashes'])}/{len(pm['content_hashes'])}; failed-v0.11 {len(failed['entries'])}/{len(failed['entries'])}; ownership/prospective closure exact; contract hash valid")
 return 0
if __name__=='__main__': raise SystemExit(main())
