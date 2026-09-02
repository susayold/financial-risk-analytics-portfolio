# D9 Decision Gap Register

Updated: 2026-09-03  
Purpose: convert the remaining Block D closure conditions into explicit,
reviewable owner inputs without inferring approval.

## Open decision register

| Gap ID | Owner input required | Valid completion evidence | Downstream effect |
|---|---|---|---|
| D4-LGD-01 | Select exactly one main-case anchor: Q25, Q50, Q75 or Q90 | `D9_APPROVAL_REGISTER.json` has `status=APPROVED`, selected option and owner/date/reference | Opens the D4 main-case assumption gate |
| D4-TIME-01 | Approve `issue_year <= 2017` and 2018 monitor-only treatment, or document an alternative | Register records `approved=true` plus decision owner/date/reference and conditions | Establishes the accepted LGD timing boundary |
| D5-EL-01 | Accept `p_bad_final × LGD assumption × declared EAD scenario` as analytical proxy only | Register records `approved=true` and preserves the non-regulatory claim boundary | Permits D5 review gate evaluation; does not create a regulatory EL claim |
| D6-POL-01 | Approve or revise five-band thresholds and action mapping | Both `thresholds_approved=true` and `overrides_approved=true`, with owner trail | Permits D6 policy gate evaluation; does not authorize production action by itself |
| D7-PRICE-01 | Select `DESCRIPTIVE_ONLY`, or provide approved cost/fee/timing inputs | Register selection plus evidence reference; no profitability claim without inputs | Keeps D7 safely descriptive or enables a separately approved adequacy analysis |
| D8-STRESS-01 | Approve existing PD/LGD/EAD shocks or document alternatives | Register records `approved=true` with policy reference and conditions | Permits D8 sensitivity gate evaluation; does not make a forecast |
| D9-SIGN-01 | Data owner sign-off | Name, date, status and approval reference in owner register | Required before final D9 rerun |
| D9-SIGN-02 | Model owner sign-off | Name, date, status and approval reference in owner register | Required before final D9 rerun |
| D9-SIGN-03 | Risk owner sign-off | Name, date, status and approval reference in owner register | Required before final D9 rerun |

## Current state

All nine gaps are currently open. The structured register remains
`PENDING_OWNER_INPUT`; this file is a handoff aid and does not change any gate
status. A decision is not valid merely because a scenario or report exists.

## Acceptance sequence after inputs arrive

1. Record each decision in `D9_APPROVAL_REGISTER.json` and preserve the owner,
   date, reference and conditions fields.
2. Run `python src/validate_block_d_owner_decisions.py` and inspect errors.
3. Run it again with `--require-ready`; it must return
   `READY_FOR_D9_RERUN`.
4. Run full-review QA and regenerate the completion scorecard and D9 manifest.
5. Run the checksum validator. Only then may the authorized reviewer decide
   whether D9 can move to `LOCKED`.

## Claim boundary

Until all gaps are explicitly accepted and the final D9 gate passes, Block D
must remain `NOT_LOCKED_REVIEW_REQUIRED`. No value in this register is a
production, regulatory, profitability or approve/decline authorization.
