# CRD.PI — Block B White Slide Website

Recruiter-facing static HTML presentation for **Block B — Data Engineering & Quality Control**.

## Scope

This page covers the reviewed and locked B0–B9 engineering and portfolio-risk foundation:

- governed Zenodo ingestion;
- one granted-loan/account canonical staging grain;
- executable DQ01–DQ07 controls;
- exact Block A champion-feature contract enforcement;
- chronological reconciliation and sanitized audit evidence;
- runtime cleanup and handoff from B0–B3 to the B4 `mart_credit_application_core` analytical mart;
- B4 one-account grain, exact reconciliation, schema contract and safe handoff to B5;
- B5 controlled pricing enrichment and rejected-context boundary;
- B6 portfolio overview and descriptive baseline;
- B7 single-variable segment risk;
- B8 material risk concentration screening;
- B9 vintage/temporal analysis with right-truncation caveat.

It does not claim a production pipeline, verified 12-month PD, calibrated model, ROC-AUC/KS/Gini, LGD/EAD, ECL, optimized approval policy, causal reject inference or live monitoring.

## Files

- `index.html` — fourteen-section semantic page.
- `../assets/crdpi-block-b.css` — white slide design system and responsive layout.
- `../assets/crdpi-block-b.js` — scroll/keyboard navigation, rail state and reveal behavior.
- `../assets/images/block-b/` — optimized visual assets only; no raw LendingClub data.
- `../sql/marts/05_mart_credit_application_core.sql` — reproducible B4 mart projection.
- `../sql/tests/` and `../src/run_b4_tests.py` — B4 reconciliation and boundary tests.
- `../docs/B4_RUN_REPORT.md` and `../evidence/block-b/b4-*.md` — sanitized B4 handoff evidence.
- `../docs/B6_RUN_REPORT.md` through `../docs/B9_RUN_REPORT.md` — aggregate analytical reports.
- `../docs/BLOCK_B_ANALYTICAL_FINDINGS.md` and `../docs/BLOCK_B_FINAL_LOCK.md` — findings and final lock.
- `../evidence/block-b/b6-*.md` through `../evidence/block-b/block-b-final-lock.md` — public aggregate evidence.

## Local preview

From the repository root, serve the static files with any simple HTTP server and open `/block-b/`. GitHub Pages serves the same route without a build step.
