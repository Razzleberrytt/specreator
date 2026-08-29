# v0.09.1 Retrospective — Invalid Freeze Transaction

**Decision:** RETRY REQUIRED

The retry correctly repaired the contradictory `task_contract_mismatch` fixture and its semantic-contrast preflight passed 30/30. However, the preregistration helper then created a frozen contract even though its own parent preflight reported 72/75 rather than 75/75.

The three apparent parent failures were themselves a preflight implementation mistake: the helper treated intentionally invalid graph-hash cases as execution-invalid without independently replaying their otherwise valid empty execution streams. Regardless, `all_ok=false` was visible before the contract write. A correct freeze transaction must fail closed at that point.

Because `REL-0.09.1-FROZEN-001` exists and binds the failed preflight artifact, it is preserved rather than regenerated. `REG-0021` now requires preregistration helpers to assert every precondition before contract creation. v0.09.2 retries from the same product direction with corrected parent preflight semantics and an explicit fail-closed freeze transaction.
