# v0.09.1 Failed Contract Attempt — Quarantine Notice

The exact bytes originally written to `FROZEN-RELEASE-CONTRACT.json` are preserved as `FROZEN-RELEASE-CONTRACT.INVALID-ATTEMPT.json` with file SHA-256 `f383bba360b693f9216cd1d72e2368dc83c63099807960e5c53985dcde561c07` (its internal canonical contract hash field was `ece6c01cf6e4ab5813d53c72685328b7fb106bd6adeb20b861cf96e30f39310f`).

This attempted freeze was already invalid under `DEF-0091-001` because its own preregistration preflight was red. `DEF-0091-002` additionally established that the attempted contract was schema-invalid. It therefore never became an eligible frozen release contract. The recognized filename is intentionally absent so workspace validation does not misrepresent an invalid attempted freeze as a valid historical contract. No bytes from the attempt were edited or discarded.
