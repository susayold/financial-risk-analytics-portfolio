# Block D Results Summary

Updated: 2026-09-02

## Executive result

The executable evidence work for D0–D9 is complete at review scope. Block D
is **not locked** because the remaining approvals are governance decisions,
not missing calculations.

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 PASS_WITH_LIMITATIONS` · `D3 PASS_WITH_LIMITATIONS` · `D4 BRIDGE_RECONCILED_APPROVAL_PENDING` · `D5–D9 CONTROLLED_HOLD`

Execution coverage is **100% (10/10 stages)**, while closure readiness toward
`LOCKED` is **73.5%** under the documented scorecard conversion. See
`BLOCK_D_PLAN_COMPLETION_SCORECARD.md` for the stage-by-stage basis.

## Verified results

| Stage | Verified output |
|---|---|
| D1 | 310,066 unique scored accounts: Development 182,181; Validation 83,664; OOT 44,221. Pricing bridge complete for all scored rows. Validation risk-band cutpoints are materialized and reused across the matched mart. Full governed population reconciliation: 1,347,681 = 1,291,521 modeling core + 56,160 Historical Shadow. |
| D2 | 1,347,681/1,347,681 governed IDs matched the accepted bridge artifact; target concordance 100%; loan amount concordance 100%; zero duplicate-ID groups/conflicts; 269,249/269,249 governed BAD rows matched loss evidence. The legacy source audit is tracked separately by source checksum. |
| D4 | Q25 LGD 48.9670%; Q50 66.7385%; Q75 79.0297%; Q90 86.5786%. Anchors use issue years through 2017; 2018 Shadow is monitor-only (8,846 BAD rows in the governed evidence). The separate descriptive score-to-loss linkage covers 49,049/49,049 scored-BAD rows; D4 remains approval-pending. |
| D5 | 1,240,264 account-scenario rows and 60 split/band summaries. At 12-month EAD scenario, EL proxy rates are Q25 9.2663%, Q50 12.6292%, Q75 14.9552%, Q90 16.3837%. These are analytical scenario values, not approved EL. |
| D6 | 310,066 proposed policy assignments across five D1 risk bands. Labels are proposed/non-production and do not grant approve/decline authority. |
| D7 | 310,066 pricing diagnostics; required `term`, `int_rate`, `installment`, `sub_grade`, `grade_derived`, `loan_amnt` and `p_bad_final` bridge fields are complete. Profitability is not evaluated because costs/fees are not evidenced. |
| D8 | 720 explicit sensitivity cells across four LGD scenarios, three PD shock levels, two LGD shocks and two EAD shocks, split and risk band. Illustrative only. |
| D9 | Closure review manifest created with `NOT_LOCKED_REVIEW_REQUIRED`. |

## Remaining decisions

1. Approve one D4 main-case LGD and timing boundary.
2. Approve D5 use as an analytical proxy, if desired.
3. Approve D6 action thresholds and override rules.
4. Supply/approve D7 cost, fee and timing assumptions if profitability is required.
5. Approve D8 baseline and stress policy.
6. Record data/model/risk owner sign-off, then rerun the final D9 gate.

## Non-claims

`actual_default` remains an observed final-resolution outcome, not a verified
12-month PD. No result here is a regulatory PD/LGD/EAD/ECL, IFRS 9, Basel,
capital adequacy, realized loss or realized profitability claim. Raw accepted
source data and private model binaries are not in GitHub or Drive.

## Evidence locations

- [Block D Drive folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-)
- [Block D execution tracker](https://drive.google.com/file/d/1jFgmmxySbCMObhsznxsMKBYk1q439sw4/view?usp=drivesdk)
- [D1 full pack](https://drive.google.com/file/d/1A2laFU3d9e5UHAegKfIzKaAegLNpBlRy/view?usp=drivesdk)
- [D2 governed bridge pack](https://drive.google.com/file/d/1503zJkDmksZwx7AkIEg3-OHdCxk6TYq8/view?usp=drivesdk)
- [D5 scenario pack](https://drive.google.com/file/d/1i4TjiREQAzutHrEU3iYBK3sOk5woMpDm/view?usp=drivesdk)
- [D6 policy pack](https://drive.google.com/file/d/1G5OLPz-NAvO1KLUynJc1DEJxnJrdYU2T/view?usp=drivesdk)
- [D7 pricing pack](https://drive.google.com/file/d/1umRSK8tUFUscH4bLZi8hyhIOKhfqwvPl/view?usp=drivesdk)
- [GitHub Block D](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-d)
