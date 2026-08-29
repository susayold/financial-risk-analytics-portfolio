# CRD.PI — Block B White Slide Website

Recruiter-facing static HTML presentation for **Block B — Data Engineering & Quality Control**.

## Scope

This page covers the reviewed B0–B4 engineering foundation:

- governed Zenodo ingestion;
- one granted-loan/account canonical staging grain;
- executable DQ01–DQ07 controls;
- exact Block A champion-feature contract enforcement;
- chronological reconciliation and sanitized audit evidence;
- runtime cleanup and handoff from B0–B3 to the B4 `mart_credit_application_core` analytical mart;
- B4 one-account grain, exact reconciliation, schema contract and safe handoff to B5.

It does not claim a production pipeline, verified 12-month PD, calibrated model, LGD/EAD, ECL, pricing policy or portfolio-risk findings.

## Files

- `index.html` — nine-slide semantic page.
- `../assets/crdpi-block-b.css` — white slide design system and responsive layout.
- `../assets/crdpi-block-b.js` — scroll/keyboard navigation, rail state and reveal behavior.
- `../assets/images/block-b/` — optimized visual assets only; no raw LendingClub data.
- `../sql/marts/05_mart_credit_application_core.sql` — reproducible B4 mart projection.
- `../sql/tests/` and `../src/run_b4_tests.py` — B4 reconciliation and boundary tests.
- `../docs/B4_RUN_REPORT.md` and `../evidence/block-b/b4-*.md` — sanitized B4 handoff evidence.

## Local preview

From the repository root, serve the static files with any simple HTTP server and open `/block-b/`. GitHub Pages serves the same route without a build step.
