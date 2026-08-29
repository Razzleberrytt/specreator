from pathlib import Path
import json, pytest
from spec_creator.v0111.lifecycle import derive_next_action, LifecycleResolutionError
ROOT=Path(__file__).resolve().parents[2]
def load_jsonl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def test_all_frozen_lifecycle_fixtures_exact():
 rules=json.loads((ROOT/'versions/v0.11.1/LIFECYCLE-TRANSITION-RULES.candidate.json').read_text())
 fixtures=load_jsonl(ROOT/'versions/v0.11.1/candidate-fixtures/lifecycle-continuation-corpus.jsonl')
 assert [derive_next_action(rules,f['state'],f['blockers']) for f in fixtures]==[f['expected_next_action'] for f in fixtures]
def test_current_frozen_state_derives_implementation():
 rules=json.loads((ROOT/'versions/v0.11.1/LIFECYCLE-TRANSITION-RULES.candidate.json').read_text())
 assert derive_next_action(rules,'FROZEN',[])=='implement_frozen_candidate'
def test_unknown_state_fails_closed():
 rules=json.loads((ROOT/'versions/v0.11.1/LIFECYCLE-TRANSITION-RULES.candidate.json').read_text())
 with pytest.raises(LifecycleResolutionError): derive_next_action(rules,'BOGUS',[])
