# CLAIM_TRACEABILITY_MATRIX.md

**Built from direct verification against the actual evidence register, not from this task's example table.** The example illustrated format using approximate ID assignments that don't match the real register in two places (EV-003 and EV-005) — noted explicitly below rather than silently corrected, since propagating an unverified mapping would risk exactly the kind of status error this task's rules exist to prevent.

| Manuscript Claim | Evidence ID | Status |
|---|---|---|
| Deterministic execution (within-environment) | EV-001 | **Verified** |
| ForecastBench reconciliation tooling (mechanism) | EV-002 | Mechanism only — not executed |
| Statistical significance methodology (mechanism) | EV-003 | Mechanism only — not executed against real data |
| Cross-platform / cross-environment reproducibility | EV-004 | **Blocked** |
| Artifact integrity / checksumming | EV-005 | **Verified** (real, scope-limited — this program's own repository files, not ForecastBench's experimental outputs) |
| Targeted test coverage | EV-006 | **Verified** (real, scope-limited — one test file, not the manuscript's cited 132-test suite) |
| ForecastBench metric discrepancy resolution | EV-010 | **Blocked** |

## Discrepancies From This Task's Example Table, Stated Precisely

| This task's example said | What's actually true | Why it matters |
|---|---|---|
| "artifact integrity — EV-003 — Verified" | Artifact integrity is **EV-005**, Verified. EV-003 is statistical methodology, still Pending/mechanism-only | Using the example as given would have mislabeled Pending evidence as Verified under the wrong ID |
| "statistical significance — EV-005 — Pending" | Statistical significance is **EV-003**, Pending. EV-005 is the real, completed checksum execution | Using the example as given would have mislabeled completed, executed evidence as Pending — the opposite error, still a factual mismatch |
| "cross-platform reproducibility — EV-004 — Pending" | Status is **Blocked**, not Pending — the CI mechanism exists and is specified but has never been triggered, which is a more specific, more accurate description than generic "Pending" | Small but real precision difference — "Pending" implies work is queued; "Blocked" states why it hasn't started |

Everything else in the example (EV-001, EV-006, EV-010 IDs and their general status direction) matched the real register and is carried through unchanged.
