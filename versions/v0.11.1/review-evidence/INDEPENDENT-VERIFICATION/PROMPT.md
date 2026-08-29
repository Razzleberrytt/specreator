# Prompt — Independent v0.11.1 Post-Implementation Verification

You are a genuinely separate receiving context performing the required independent post-implementation verification for Spec Creator v0.11.1.

Treat the attached VERIFYING checkpoint ZIP as the sole source of truth. Do not repair, implement, promote, freeze, redesign, or begin v0.12.

Read and follow `versions/v0.11.1/review-evidence/INDEPENDENT-VERIFICATION/PROTOCOL.md` exactly. Independently recompute the frozen v0.11.1 obligations rather than trusting authored implementation summaries.

Important sequencing rule: the root `PACKAGE-MANIFEST.json` is not yet the final shipping manifest. Final shipping-manifest generation is intentionally reserved for the authoritative context after this independent verification. This is not permission to ignore package integrity: recompute current package ownership and frozen/parent/history hashes independently, and report any unexpected path or drift.

Return raw evidence plus exactly one recommendation: `READY_FOR_RELEASE_SEAL` or `NOT_READY` with blocking defects. Do not continue development.
