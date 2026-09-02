# Block D — Approval Register (D4–D9)

Updated: 2026-09-03  
Purpose: record explicit owner decisions without fabricating approval. Use
`BLOCK_D_APPROVAL_DECISION_PACK.md` for the quantitative option comparison and
`D9_APPROVAL_REGISTER.json` for the structured input record.

All rows below are currently **PENDING**. The proposed values are review
options derived from the executed analytical packs; they are not approved
assumptions, production policy or regulatory parameters.

## Decision register

| Decision | Evidence to review | Current proposal/options | Status | Owner / date |
|---|---|---|---|---|
| D4 main-case LGD | D4 scenario anchors, score-to-loss linkage and approval decision pack | Select Q25 48.9670%, Q50 66.7385%, Q75 79.0297% or Q90 86.5786%; timing reference `issue_year <= 2017`; 2018 remains monitor-only | PENDING | — |
| D4 timing boundary | D4 contract and 2018 truncation guard | Approve the reference cohort and whether any timing adjustment is required | PENDING | — |
| D5 analytical proxy | D5 scenario audit | Accept only as `p_bad_final × LGD assumption × declared EAD scenario`; 12-month EAD view remains analytical proxy only | PENDING | — |
| D6 action thresholds | D6 proposed policy assignments | Approve or revise the five-band mapping and action thresholds; define reason-coded overrides and monitoring limits | PENDING | — |
| D7 pricing scope | D7 diagnostic audit | Keep descriptive-only, or supply/approve cost, fee and timing evidence before any adequacy/profitability analysis | PENDING | — |
| D8 stress policy | D8 sensitivity audit | Approve baseline and shocks: PD 0/+10%/+25%, LGD 0/+10 percentage points, EAD 0/+5%, or document alternatives | PENDING | — |
| D9 owner sign-off | Full QA, status and artifact index | Confirm data owner, model owner and risk owner have reviewed the claim boundary and evidence | PENDING | — |

## Sign-off fields

| Role | Name | Decision / conditions | Date | Signature or recorded approval reference |
|---|---|---|---|---|
| Data owner | — | — | — | — |
| Model owner | — | — | — | — |
| Risk owner | — | — | — | — |

## Conditions for unlocking D9

1. D4 main-case LGD and timing are explicitly approved.
2. D5 analytical-proxy use and claim boundary are accepted.
3. D6 thresholds/overrides and D8 baseline/shocks are approved.
4. D7 cost/fee inputs are supplied if profitability or price adequacy is in scope.
5. All three owner sign-offs are recorded.
6. The final QA and D9 closure manifest are rerun against the approved inputs.

Until all conditions are met, the only valid Block D status is
`NOT_LOCKED_REVIEW_REQUIRED`.
