from pathlib import Path
import json, hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]

def _matches(rel,s):
 k=s['kind']
 if k=='exact': return rel==s['value']
 if k=='prefix': return rel.startswith(s['value'])
 if k=='directory_filename_prefix':
  if not rel.startswith(s['directory']): return False
  tail=rel[len(s['directory']):]; return '/' not in tail and tail.startswith(s['value'])
 if k=='directory_filename_in':
  if not rel.startswith(s['directory']): return False
  tail=rel[len(s['directory']):]; return '/' not in tail and tail in set(s['values'])
 raise AssertionError(k)

def test_reg0025_prospective_ownership_25_legal_and_7_forbidden():
 fixture=json.loads((ROOT/'versions/v0.11.1/candidate-fixtures/ownership-prospective-paths.json').read_text())
 own=json.loads((ROOT/'versions/v0.11.1/SUCCESSOR-OWNERSHIP-UNIVERSE.json').read_text())
 assert fixture['count']==25 and len(fixture['members'])==25
 assert fixture['forbidden_count']==7 and len(fixture['forbidden_members'])==7
 for rel in fixture['members']:
  matches=[s['selector_id'] for s in own['selectors'] if _matches(rel,s)]
  assert len(matches)==1, (rel,matches)
 for rel in fixture['forbidden_members']:
  matches=[s['selector_id'] for s in own['selectors'] if _matches(rel,s)]
  assert matches==[], (rel,matches)

def test_frozen_registry_still_exact_after_implementation():
 p=subprocess.run([sys.executable,str(ROOT/'versions/v0.11.1/tools/frozen_contract_preflight.py')],cwd=ROOT,capture_output=True,text=True)
 assert p.returncode==0, p.stdout+p.stderr

def test_failed_v011_baseline_hashes_remain_exact():
 x=json.loads((ROOT/'versions/v0.11.1/FAILED-PREDECESSOR-v0.11-BASELINE.json').read_text()); assert len(x['entries'])==154
 for item in x['entries']:
  p=ROOT/item['path']; assert p.stat().st_size==item['bytes']; assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
