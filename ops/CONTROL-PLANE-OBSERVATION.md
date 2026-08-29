# Control-plane repository observation semantics

`ops/spec-creator-state.json` records a **snapshot observation**, not a self-referential assertion that the file somehow contains the SHA of the commit that contains itself.

The repository observation is therefore bound to `repository.observation_basis_main_sha` and `repository.observation_basis_tree_sha`: the exact `main` state inspected immediately before the control-plane reconciliation commit was created. Later commits make that snapshot older, but not invalid; automation must refresh the observation when repository reality materially changes.

`baseline_bytes_present` means the historical v0.11.1 artifact family is visible in the repository. It does **not** mean the baseline has been reconciled, independently reverified for the exact GitHub state, sealed, or adopted. Those are separate authority-bearing transitions.

`baseline_reconciled` is the fail-closed gate. While false, successor implementation and release promotion remain prohibited even when restored-looking files are present.

The bootstrap validator validates repository **shape and control-plane semantics**, not a fixed historical file count. It must never infer restoration success merely from the number of files in the working tree.
