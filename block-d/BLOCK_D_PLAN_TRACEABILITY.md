# CRD.PI Block D — Plan Traceability

Updated: 2026-09-03  
Execution scope: controlled analytical review, not production approval

This matrix records what was executed for the Block D plan, where the
evidence lives, and which decisions are still required before a gate can open.
It deliberately separates a completed analytical pack from an approved
production or regulatory result.

## Requirement-to-evidence matrix

| Plan stage | Required outcome | Evidence produced | Current result | Remaining condition |
|---|---|---|---|---|
| D0 Governance | Freeze upstream versions, model, population lanes, roles, assumptions and claim boundary | `D0_GOVERNANCE_CONTRACT/`, `src/run_block_d_d0_qa.py` | PASS; 10/10 QA gates | None for the D0 contract |
| D1 Risk score mart | Replay frozen C8E model, create scored decision mart, reconcile score/pricing fields and splits | `D1_RISK_SCORE_MART/` including materialized `risk_band_contract.json`; private D1 mart and diagnostics | PASS_WITH_LIMITATIONS; 310,066 scored rows; 100% pricing bridge in matched subset; Validation cutpoints materialized and reused | No full-governed-population score coverage claim |
| D2 Loss evidence | Reconcile accepted source to governed population, preserve target semantics, deduplicate loss evidence and document recovery role | `D2_LOSS_RECOVERY_EVIDENCE/`; private governed bridge and BAD evidence | PASS_WITH_LIMITATIONS; 1,347,681/1,347,681 governed IDs and 269,249/269,249 governed BAD rows reconciled | Retrospective BAD-only evidence; no regulatory LGD or GOOD-row recovery claim |
| D3 EAD | Define contractual EAD proxy and timing scenarios with anomaly treatment | `D3_EAD_FRAMEWORK/`; `D3_CONTRACT_AUDIT.json`; private D3 evidence | PASS_WITH_LIMITATIONS; 331,865-row declared pricing-source scope; 104 schedule anomalies excluded | `loan_amnt` remains an origination proxy, not approved regulatory EAD |
| D4 LGD | Produce governed BAD-only LGD scenario anchors and protect the 2018 shadow cohort | `D4_LGD_FRAMEWORK/`; D2 bridge audit; private D4 outputs | BRIDGE_RECONCILED_APPROVAL_PENDING; Q25/Q50/Q75/Q90 anchors generated; 10 pass, 0 fail, 0 pending; descriptive linkage also materialized | Approve one main-case LGD and timing boundary; descriptive linkage is not an empirical LGD model |
| D5 Expected loss | Combine score, LGD and EAD under an explicit formula for review | `D5_EXPECTED_LOSS/`; private D5 scenario pack | CONTROLLED_HOLD; 1,240,264 scenario rows and 60 summaries executed | Accept analytical proxy and D4 input; no approved EL/regulatory claim |
| D6 Decision policy | Map risk/economics bands to proposed actions and document governance | `D6_DECISION_POLICY/`; private D6 pack | CONTROLLED_HOLD; 310,066 proposed assignments | Owner approval of thresholds, overrides and action authority |
| D7 Pricing | Reconcile score-to-pricing fields and assess pricing adequacy only when cost/fee evidence exists | `D7_PRICING/`; private D7 pack | CONTROLLED_HOLD; 310,066 descriptive diagnostics; required bridge fields complete | Cost, fee and timing evidence if profitability or adequacy is required |
| D8 Stress | Run explicit PD/LGD/EAD sensitivity scenarios without presenting them as forecasts | `D8_STRESS/`; private D8 pack | CONTROLLED_HOLD; 720 sensitivity cells executed | Approve baseline and shock policy; D5 approved baseline required |
| D9 Closure | Assemble closure manifest, reconcile gates and record owner sign-off | `D9_CLOSURE/`; `D9_APPROVAL_REGISTER.md`; `D9_APPROVAL_REGISTER.json`; `BLOCK_D_APPROVAL_DECISION_PACK.md`; `BLOCK_D_VALIDATION_REPORT.md`; `D5_D9_DOWNSTREAM_GATE_REGISTER.md`; `D5_D9_GATE_QA.json` | CONTROLLED_HOLD; `NOT_LOCKED_REVIEW_REQUIRED`; downstream QA 5/5 | D4–D8 approvals plus data/model/risk owner sign-off, then rerun D9 |

## Verified population and bridge invariants

- Full governed population: **1,347,681** = **1,291,521** modeling core +
  **56,160** Historical Shadow monitor-only rows.
- Matched scored subset: **310,066** = **182,181** Development + **83,664**
  Validation + **44,221** OOT.
- Accepted bridge source scanned: **2,260,701** rows; no duplicate-ID groups,
  target conflicts or loan-amount mismatches in the exact governed bridge.
- Governed BAD loss evidence: **269,249 / 269,249** rows matched at
  account-grain.

## Claim boundary

The project may show the controlled analytical packs and their diagnostics. It
must not describe them as regulatory PD/LGD/EAD/ECL, IFRS 9, Basel, capital
adequacy, realized loss/profitability, or a production approve/decline policy.
`actual_default` remains an observed final-resolution outcome, not a verified
12-month PD. Post-outcome recovery fields remain evidence-only and are not
underwriting predictors.

## Reproducibility and storage

- Public repository: contracts, sanitized audits, reproducible scripts and
  bounded summaries only.
- Private Drive: derived evidence packs and review artifacts.
- Raw accepted CSV, DuckDB files, private model binaries and temporary runtime
  data are excluded from both public GitHub and Drive.
- Final deterministic checks from the repository root:

```text
python src/run_block_d_d0_qa.py
python src/run_block_d_downstream_gate_qa.py
```

## Final decision path

1. Record the D4 main-case LGD/timing decision.
2. Confirm D5 analytical proxy acceptance.
3. Approve D6 thresholds/overrides and D8 baseline/shocks.
4. Provide D7 cost/fee inputs if profitability is in scope.
5. Record data, model and risk owner sign-off.
6. Rerun D9 and update the closure decision only if every upstream gate passes.

The structured register can be checked with
`python src/validate_block_d_owner_decisions.py`; the final manifest evidence
paths and SHA-256 entries can be checked with
`python src/validate_block_d_d9_checksums.py`.
