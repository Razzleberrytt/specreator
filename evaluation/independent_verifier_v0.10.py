from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spec_creator.protocol_evaluator import evaluate_v010
from spec_creator.models import canonical_contract_hash

def main():
 c=json.load(open(ROOT/'versions/v0.10/FROZEN-RELEASE-CONTRACT.json')); ev=evaluate_v010(ROOT)
 frozen=[]
 for x in c['failure_conditions']:
  m=re.match(r'Frozen artifact SHA-256 differs for (.*): expected ([0-9a-f]{64})\.',x)
  if m:
   p,h=m.groups(); a=hashlib.sha256((ROOT/p).read_bytes()).hexdigest(); frozen.append({'path':p,'ok':a==h})
 hist=json.load(open(ROOT/'evaluation/historical-integrity-baseline-v0.10.json')); hist_bad=[]
 for p,h in hist['sha256'].items():
  q=ROOT/p
  if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest()!=h: hist_bad.append(p)
 tr=json.load(open(ROOT/'evaluation/transfer-v0.10/trial-index.json'))
 test=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,env={**__import__('os').environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True)
 m=ev['metrics']; ok=(test.returncode==0 and all(x['ok'] for x in frozen) and not hist_bad and canonical_contract_hash(c)==c['contract_hash'] and tr['prefreeze_acceptance_met'] and m['end_to_end_project_completion_rate']==1 and m['deterministic_rerun_rate']==1 and m['resume_exact_match_rate']==1 and m['artifact_provenance_completeness_rate']==1 and m['promoted_stage_semantic_preservation_rate']==1 and m['manual_artifact_reconstruction_count']==0 and m['critical_gate_bypass_count']==0 and m['invalid_or_hash_mismatched_resume_escape_count']==0)
 out={'verifier_actor':'verifier:independent-pass-010','ok':ok,'pytest_returncode':test.returncode,'pytest_tail':test.stdout.strip().splitlines()[-2:],'frozen_artifact_count':len(frozen),'frozen_drift_count':sum(not x['ok'] for x in frozen),'historical_baseline_count':hist['count'],'historical_drift_count':len(hist_bad),'historical_drift':hist_bad,'contract_hash_ok':canonical_contract_hash(c)==c['contract_hash'],'transfer_3_of_3':tr['validated_trials']==3,'protocol_metrics':m,'recommendation':'PROMOTED AS EXPERIMENTAL' if ok else 'RETRY REQUIRED'}
 print(json.dumps(out,indent=2,sort_keys=True)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
