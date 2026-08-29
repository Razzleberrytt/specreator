# v0.11.1 Retry Discovery

v0.11.1 exists for one reason: `DEF-011-POSTFREEZE-001` proved that freezing an exact list of the *current* successor files cannot serve as authority for files that necessarily appear later during freeze, implementation, verification, and sealing.

The retry does not reopen the v0.11 product question. Its semantic behavior target is intentionally unchanged. The design change is governance-mechanical:

1. seal all pre-retry failed-v0.11 bytes into a hash-exact immutable predecessor baseline;
2. preserve v0.10 as executable parent authority;
3. reserve isolated v0.11.1 namespaces for implementation, tests, evidence, and release artifacts;
4. freeze deterministic, disjoint path selectors over those namespaces;
5. independently test a prospective-output fixture before freeze;
6. carry the defect as REG-0025 through final package validation.

This converts ownership from a brittle closed enumeration into a frozen rule over bounded namespaces while retaining a current snapshot for auditability.
