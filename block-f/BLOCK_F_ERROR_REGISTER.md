# CRD.PI Block F Error Register

Status date: 2026-09-08
Branch: `block-f-final-closure`
Scope: recruiter-facing delivery and QA only. Frozen analytical outputs from Blocks A–E must not be changed.

| ID | Priority | Area | Evidence / root cause | Remediation | Verification | Status |
|---|---|---|---|---|---|---|
| BF-ERR-001 | P0 | Responsive | GitHub Actions run #9: mobile `/monitoring/` document width 414px at 390px viewport. Remaining offender was an evidence table after the governance-flow overflow had already been removed. | Add scoped small-screen table containment/wrapping in `assets/crdpi-monitoring.js`; preserve desktop table behavior. | Multi-width Playwright matrix: 320/360/390/414/768/1440 across all seven pages; document width must not exceed viewport. | FIXED_PENDING_CI |
| BF-ERR-002 | P1 | Social metadata | `architecture/index.html` still points `og:image` to `crdpi-governance.svg` although `assets/og/crdpi-architecture.svg` exists. | Replace Architecture OG reference with Architecture-specific asset. | Static source assertion and browser/source audit. | OPEN |
| BF-ERR-003 | P0 | CI diagnostics | Browser QA failure previously skipped reconciliation, claim, privacy and final bundle checks, hiding downstream errors. | Run independent QA steps with `continue-on-error` / `if: always()` and enforce one aggregate fail-closed gate at the end. | One CI run must report all gate outcomes and still fail if any gate is non-success. | FIXED_PENDING_CI |
| BF-ERR-004 | P1 | Privacy | Public scanner did not include root README/master links and had no negative fixtures proving detection capability. | Scan README + master links; add negative fixtures for IDs, local paths, tokens, secrets and labelled phone data. | Pytest negative fixtures + final bundle scan. | FIXED_PENDING_CI |
| BF-ERR-005 | P2 | Reproducibility | Deterministic build was described but not independently proven across consecutive builds. | Add `check_public_build_determinism.py`; compare SHA-256 across two consecutive builds. | CI determinism step PASS. | FIXED_PENDING_CI |
| BF-ERR-006 | P2 | Responsive coverage | Browser QA only exercised 390px and 1440px. | Expand audit widths to 320, 360, 390, 414, 768, 1440 while retaining 14 canonical screenshots. | 42 route/viewport checks PASS. | FIXED_PENDING_CI |
| BF-ERR-007 | P0 | Formal closure | Block F closure artifacts are incomplete until all pre-deployment QA gates are green. | Generate final QA/status/manifest/artifact index/closure documents only after CI passes. | Required closure files committed and internally consistent. | OPEN |
| BF-ERR-008 | P0 | Delivery state | Page 07 must remain `IN_PROGRESS` while any required gate or deployment smoke is pending. | Derive state from Block F QA artifact; do not hard-code `DELIVERED`. | Page 07/README/status all agree with QA state. | CONTROL_ACTIVE |
| BF-ERR-009 | P0 | Canonical merge/release | Branch has not yet been merged and `block-f-v1.0-final` does not exist. | Merge only after branch CI green; run live smoke; then finalize status and tag/release. | `main` smoke PASS and final release points to intended SHA. | OPEN |
| BF-ERR-010 | P1 | Enforcement | `main` branch is not protected with required status checks. | If connector/account permissions allow, require Block F QA before merge; otherwise disclose limitation and keep manual fail-closed sequence. | Branch/ruleset read confirms enforcement or closure report records limitation. | OPEN |

## Non-negotiable frozen upstream controls

- Block D canonical release: `block-d-v1.0-final`.
- Block E canonical release: `block-e-v1.0.2-final`.
- Scored analytical population: 310,066.
- Frozen feature contract: 79 features.
- Block F must not retune model, target, Block D economics/policy thresholds, or Block E monitoring findings.

## Release rule

```text
ANY REQUIRED GATE FAILS
→ Block F remains IN_PROGRESS
→ no merge to main
→ no DELIVERED state
→ no block-f-v1.0-final release
```
