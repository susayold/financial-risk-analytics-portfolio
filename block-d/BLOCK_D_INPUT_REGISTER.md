# Block D Input Register

| Input | Required for | Current state | Authority |
|---|---|---|---|
| C8E frozen model and 79-feature contract | D0/D1 | Available in private C9 closure package | [C9 closure folder](https://drive.google.com/drive/folders/1Z_ORctxmgWkDTMXfw-1SDPMC1IcMg70x) |
| C8E Validation predictions | D1 | Available; 83,664 rows | Private C8E results package |
| C9 OOT predictions | D1 | Available; 44,221 rows | Private C9 closure package |
| Governed Development population | D1 bridge | Materialized in C7 cumulative package; 829,347 rows | [C7/C9 private package](https://drive.google.com/drive/folders/1Z_ORctxmgWkDTMXfw-1SDPMC1IcMg70x) |
| C8E Development predictions | D1 | Replayed from frozen C8E 79-feature model for 182,181 matched Development rows; no refit | D1 development score audit |
| Pricing enrichment bridge | D1/D3/D7 | 310,066/310,066 scored rows matched required pricing fields | D1 pricing bridge in private D evidence |
| Full accepted source loss/recovery fields | D2/D4 | Exact governed-core bridge PASS: 1,347,681 IDs, targets and loan amounts reconcile | D2 governed bridge audit |
| Account-grain LGD scenario anchors | D4 | Generated from 269,249 governed BAD rows; 2018 shadow monitor-only | D4 scenario output; approval still pending |

## D3 execution evidence

The accepted/pricing fallback was sufficient to execute D3 contractual scenarios. The account-level output is stored in the private Drive Block D folder and excluded from GitHub; only sanitized contracts and QA summaries are public.

## Evidence rule

Summary metrics from Block C can freeze the upstream model and its claim boundary, but they cannot substitute for account-level inputs required to calculate D1–D8. No downstream number is published until its population and field-level evidence are present.

See `D1_RISK_SCORE_MART/D1_INPUT_AVAILABILITY_AUDIT.md` for the detailed
Drive evidence distinction and exact D1 opening requirements.
