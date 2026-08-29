# B5 Handoff

`B5 = FINAL REVIEWED / PASS`. The next governed stage is `B6 — Portfolio Overview`.

Use three visibly separate populations in B6:

- Full core: `mart_credit_application_core` — 1,347,681 accounts.
- Matched pricing sample: `mart_credit_pricing_enriched` — 325,255 accounts.
- Rejected context: `mart_rejected_context` — context only, not target eligible.

Safe public claim: Built an exact account-ID bridge between the governed LendingClub core and a supplemental pricing dataset, matching 325,255 accounts while preserving Zenodo as the authoritative source for target and overlapping risk fields. Rejected applicants are isolated as context evidence without a fabricated repayment outcome.

