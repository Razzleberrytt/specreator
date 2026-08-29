from __future__ import annotations
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[3]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    errors=[]
    reg_path=ROOT/'versions/v0.11/FROZEN-ARTIFACT-REGISTRY.json'
    contract_path=ROOT/'versions/v0.11/FROZEN-RELEASE-CONTRACT.json'
    if not reg_path.exists(): errors.append('missing FROZEN-ARTIFACT-REGISTRY.json')
    if not contract_path.exists(): errors.append('missing FROZEN-RELEASE-CONTRACT.json')
    if errors:
        print('FAIL:', '; '.join(errors)); return 1
    reg=json.loads(reg_path.read_text())
    for item in reg['artifacts']:
        p=ROOT/item['path']
        if not p.exists(): errors.append(f"missing frozen artifact: {item['path']}"); continue
        got=sha256(p)
        if got!=item['sha256']: errors.append(f"hash mismatch: {item['path']} expected={item['sha256']} got={got}")
    # Validate contract hash using the project's canonical function.
    sys.path.insert(0,str(ROOT/'src'))
    from spec_creator.models import canonical_contract_hash
    contract=json.loads(contract_path.read_text())
    if contract.get('contract_hash') != canonical_contract_hash(contract): errors.append('contract_hash mismatch')
    # Verify all parent manifest hashes exactly.
    pm=json.loads((ROOT/'versions/v0.10/MANIFEST.json').read_text())
    for rel,expected in pm['content_hashes'].items():
        p=ROOT/rel
        if not p.exists() or sha256(p)!=expected: errors.append(f'v0.10 parent drift: {rel}')
    if errors:
        print(f'FAIL: {len(errors)} error(s)')
        for e in errors[:50]: print('-',e)
        return 1
    print(f"PASS: {len(reg['artifacts'])}/{len(reg['artifacts'])} frozen registry artifacts; v0.10 {len(pm['content_hashes'])}/{len(pm['content_hashes'])}; contract hash valid")
    return 0

if __name__=='__main__': raise SystemExit(main())
