# D6 — Decision Policy Gate

## Status

`CONTROLLED_HOLD` — proposed analytical policy pack exists; no production
decision policy is approved.

## Purpose

D6 converts a validated risk/economics view into transparent action bands,
review rules and exception handling. Risk bands remain reporting labels until
the D1 cutpoints are fitted on the declared reference population.

## Required inputs

- D1 frozen score mart with reusable cutpoints, `risk_band` and split-level
  diagnostics.
- D5 approved expected-loss proxy or an explicitly documented policy that does
  not use EL.
- D0 claim boundary and post-outcome field restrictions.
- Owner approval for action thresholds, override rules and monitoring limits.

## Required acceptance tests

1. Every eligible account maps to exactly one policy action or explicit manual
   review state.
2. No action threshold is fitted from OOT outcomes.
3. Overrides are reason-coded, bounded and auditable.
4. Policy labels do not imply approval authority beyond the evidence.
5. Policy performance can be reproduced by split and risk band.

## Current decision

D6 has a proposed non-production mapping for review. Any accept/refer/decline
recommendation remains premature until owner thresholds and overrides are
approved.
