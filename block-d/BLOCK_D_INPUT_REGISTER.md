# Block D Input Register

| Input | Required for | Current state | Authority |
|---|---|---|---|
| C8E frozen model and 79-feature contract | D0/D1 | Available in private C9 closure package | [C9 closure folder](https://drive.google.com/drive/folders/1Z_ORctxmgWkDTMXfw-1SDPMC1IcMg70x) |
| C8E Validation predictions | D1 | Available; 83,664 rows | Private C8E results package |
| C9 OOT predictions | D1 | Available; 44,221 rows | Private C9 closure package |
| Governed Development population | D1 bridge | Referenced by the C8 self-run package, but not currently materialized in D runtime | [C8 self-run package](https://drive.google.com/file/d/1NhAA-gqwjuvzjTcprYft6g4L1g4EpZ57/view?usp=drivesdk) |
| C8E Development predictions | D1 | No persisted Development score mart has been verified; C8 package is runnable input, not score evidence | Must be materialized and checked |
| Pricing enrichment bridge | D3/D7 | Not yet available to D runtime | Figshare enrichment, subject to bridge QA |
| Full accepted source loss/recovery fields | D2/D4 | Source-level full audit complete; exact governed-core ID bridge pending | D2 full-source audit; governed-core bridge must be supplied/materialized |
| Account-grain LGD scenario anchors | D4 fallback | Generated from 260,486 account-grain BAD rows through issue year 2017 after 1,993 exact duplicates removed; 2018 monitor-only | D4 scenario output; not approved empirical C8E LGD |

## D3 execution evidence

The accepted/pricing fallback was sufficient to execute D3 contractual scenarios. The account-level output is stored in the private Drive Block D folder and excluded from GitHub; only sanitized contracts and QA summaries are public.

## Evidence rule

Summary metrics from Block C can freeze the upstream model and its claim boundary, but they cannot substitute for account-level inputs required to calculate D1–D8. No downstream number is published until its population and field-level evidence are present.

See `D1_RISK_SCORE_MART/D1_INPUT_AVAILABILITY_AUDIT.md` for the detailed
Drive evidence distinction and exact D1 opening requirements.
