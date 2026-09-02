# Block D Execution Tracker

Updated: 2026-09-02

## Current position

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 PASS_WITH_LIMITATIONS` · `D3 PASS_WITH_LIMITATIONS` · `D4 BRIDGE_RECONCILED_APPROVAL_PENDING` · `D5–D9 CONTROLLED_HOLD`

The evidence bridges are complete. The block is not locked because D4
main-case LGD/timing approval, D6 owner policy approval and D7/D8 governance
decisions are not recorded.

## Work completed in this execution

| Stage | Result | What was done | Evidence |
|---|---|---|---|
| D0 | PASS | Preserved frozen model, population lanes, target semantics and claim boundary | `D0_GOVERNANCE_CONTRACT/` |
| D1 | PASS_WITH_LIMITATIONS | Replayed frozen C8E 79-feature model for 182,181 Development rows; built 310,066-row Development/Validation/OOT score mart; matched pricing fields 100%; reconciled core + Shadow population | `D1_RISK_SCORE_MART/`, Drive `D1_full_20260902.zip` |
| D2 | PASS_WITH_LIMITATIONS | Scanned 2,260,701 accepted-source rows; bridged 1,347,681/1,347,681 governed IDs; target and loan amount concordance 100%; filtered 269,249 governed BAD loss rows | `D2_LOSS_RECOVERY_EVIDENCE/`, Drive `D2_governed_core_bridge_20260902.zip` |
| D3 | PASS_WITH_LIMITATIONS | Retained contractual EAD proxy and timing scope on accepted/pricing source | `D3_EAD_FRAMEWORK/` and private D3 evidence |
| D4 | BRIDGE_RECONCILED_APPROVAL_PENDING | Generated Q25/Q50/Q75/Q90 governed BAD-only LGD anchors; 2018 Shadow monitor-only; explicit approval boundary retained | `D4_LGD_FRAMEWORK/`, Drive D4 files |
| D5 | CONTROLLED HOLD | Executed 1,240,264 account-scenario rows and 60 split/band summaries using `p_bad_final × LGD scenario × declared EAD`; not approved EL | Drive `D5_scenario_pack_20260902.zip` |
| D6 | CONTROLLED HOLD | Generated 310,066 proposed policy assignments across five reporting bands; no production cutoff or override authority claimed | Drive `D6_policy_pack_20260902.zip` |
| D7 | CONTROLLED HOLD | Generated 310,066 pricing diagnostics; required bridge fields complete; no cost/fee profitability claim | Drive `D7_pricing_pack_20260902.zip` |
| D8 | CONTROLLED HOLD | Generated 720 explicit PD/LGD/EAD sensitivity cells by split and band; illustrative only | Drive D8 summary files |
| D9 | CONTROLLED HOLD | Created closure manifest and listed remaining approvals; closure remains `NOT_LOCKED_REVIEW_REQUIRED` with no false lock | `D9_CLOSURE/D9_CLOSURE_REVIEW_MANIFEST.json`, `D9_CLOSURE/D9_GATE_RESULTS.json` |

## Population reconciliation

- Full governed population: **1,347,681** = modeling core **1,291,521** + Historical Shadow **56,160**.
- D1 scored matched subset: **310,066** = Development **182,181** + Validation **83,664** + OOT **44,221**.
- D2 governed BAD loss evidence: **269,249 / 269,249** BAD rows matched.
- No source duplicate-ID groups, target conflicts or loan-amount mismatches were found in the exact bridge.

## Claim boundary

- `actual_default` remains an observed final-resolution BAD/GOOD flag, not a verified 12-month PD.
- D5 and D8 outputs are analytical scenario values, not regulatory PD/LGD/EAD/ECL or realized loss.
- D6 is a proposed reporting/action mapping, not an approval policy.
- D7 is descriptive pricing context, not margin or profitability.
- Raw accepted CSV, private model binaries and temporary runtime data remain outside GitHub and were not uploaded to Drive.

## Drive delivery

- [Block D main folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-)
- [D1 full evidence ZIP](https://drive.google.com/file/d/1A2laFU3d9e5UHAegKfIzKaAegLNpBlRy/view?usp=drivesdk)
- [D2 governed bridge ZIP](https://drive.google.com/file/d/1503zJkDmksZwx7AkIEg3-OHdCxk6TYq8/view?usp=drivesdk)
- [D5 scenario pack ZIP](https://drive.google.com/file/d/1i4TjiREQAzutHrEU3iYBK3sOk5woMpDm/view?usp=drivesdk)
- [D6 policy pack ZIP](https://drive.google.com/file/d/1G5OLPz-NAvO1KLUynJc1DEJxnJrdYU2T/view?usp=drivesdk)
- [D7 pricing pack ZIP](https://drive.google.com/file/d/1umRSK8tUFUscH4bLZi8hyhIOKhfqwvPl/view?usp=drivesdk)
