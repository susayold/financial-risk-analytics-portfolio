# CRD.PI Block D — Validation Report

Validated: 2026-09-03  
Assessment: **SHARE WITH CAVEATS — NOT READY TO LOCK**  
Scope: controlled analytical review; no production or regulatory claim

## 1. Purpose and audience

This report validates whether the current Block D evidence is accurate,
traceable and safe to share with internal reviewers before owner approval. It
does not approve any LGD, expected-loss, pricing, policy or stress assumption.

The intended audience is the data owner, model owner, risk owner and the
reviewer responsible for the final D9 closure decision.

## 2. Evidence inventory

The review covers the governed artifacts for D0–D9, including:

- D0 governance contract, upstream snapshot, assumptions, roles and QA.
- D1 frozen C8E score mart audit, validation cutpoints and test results.
- D2 governed-core bridge, target/amount concordance and retrospective BAD-only
  loss evidence.
- D3 public EAD contract audit and declared schedule-scope controls.
- D4 governed BAD-only LGD anchors, bridge reconciliation and score-to-loss
  linkage audit.
- D5–D8 scenario, policy, pricing and stress gate artifacts.
- D9 closure manifest, approval register, owner-intake validator and full-review
  QA output.

Raw accepted CSV, DuckDB files, private model binaries and temporary runtime
data are intentionally excluded from the public repository and are not needed
for this controlled artifact-level validation.

## 3. Methodology and scope checks

| Area | Validated definition | Result |
|---|---|---|
| Governed population | 1,347,681 rows = 1,291,521 modeling core + 56,160 Historical Shadow monitor-only rows | Consistent across bridge and traceability |
| Scored population | 310,066 matched rows = 182,181 Development + 83,664 Validation + 44,221 OOT | Explicitly limited; no full-population score claim |
| Loss evidence | 269,249 governed BAD rows at account grain | Retrospective BAD-only evidence; not regulatory LGD |
| EAD scope | 331,865 accepted/pricing-source rows; 104 schedule anomalies excluded | `loan_amnt` remains an origination proxy |
| Time and shadow treatment | D4 reference `issue_year <= 2017`; 2018 remains monitor-only | Approval still pending |
| Claim boundary | D5–D8 remain analytical, descriptive or illustrative | No production/regulatory claim |

## 4. Calculation and control spot-checks

| Check | Evidence | Result |
|---|---|---|
| Planned stage coverage | Completion scorecard | 10/10 stages executed = 100% execution coverage |
| Full-review QA | `BLOCK_D_FULL_REVIEW_QA.json` | 53/53 checks pass, 0 fail |
| D0 governance | `D0_TEST_RESULTS.json` | 10/10 governance gates pass |
| D2 population bridge | `D2_GOVERNED_CORE_BRIDGE_AUDIT.json` | 1,347,681/1,347,681 IDs reconcile; target and loan amount concordance pass |
| D3 contract audit | `D3_CONTRACT_AUDIT.json` | 8/8 public contract checks pass; numeric output claim remains false |
| D4 LGD evidence | `D4_RUN_AUDIT.json` and tests | 269,249 usable BAD rows; 10 pass, 0 fail, 0 pending; approval remains open |
| D9 evidence integrity | `D9_CLOSURE_REVIEW_MANIFEST.json` | 15/15 SHA-256 entries pass |
| Owner decision schema | `D9_APPROVAL_VALIDATION.json` and self-test | Valid pending register; 3/3 validator self-tests pass; not ready for rerun |

The scorecard's 73.5% figure is a documented management readiness conversion,
not a model metric. It is the average of the ten stage conversion values and
must not be presented as approval probability, model performance or regulatory
readiness.

## 5. Issues and limitations

### High — D9 closure blocker

The owner register remains `PENDING_OWNER_INPUT`. D4 main-case LGD/timing,
D5 analytical-proxy acceptance, D6 thresholds/overrides, D7 pricing scope and
D8 stress policy have not been explicitly approved. Data, model and risk
owner sign-offs are also pending. The block must remain
`NOT_LOCKED_REVIEW_REQUIRED`.

### Medium — evidence boundaries

- D1 covers the 310,066-row matched scored subset, not all governed accounts.
- D2 is retrospective BAD-only evidence and does not establish GOOD-row
  recovery or regulatory LGD.
- D3 uses `loan_amnt` as an origination EAD proxy within a declared scope.
- D4 anchors are scenario assumptions, not an empirical LGD model.
- D5 expected loss, D6 policy, D7 pricing and D8 stress outputs remain
  controlled review packs rather than approved production results.

### Data access limitation

The raw source and private model packages are intentionally not stored in the
public repository. Therefore this report validates the available deterministic
audits, contracts, bridges, manifests and claim boundaries; it does not claim
to independently recompute private raw-data schedules from the public repo.

## 6. Conclusion and required caveats

The controlled analytical evidence is **safe to share with caveats** for owner
review. The technical controls are passing, but the project is **not ready to
be called locked, production-ready, regulatory, realized-loss or profitability
approved**.

Before D9 can be rerun, an authorized owner must complete the structured
register, provide the three sign-offs and preserve the stated claim boundary.
Then rerun:

```text
python src/validate_block_d_owner_decisions.py --require-ready
python src/run_block_d_full_review_qa.py
python src/build_block_d_completion_scorecard.py
python src/build_block_d_d9_closure_manifest.py --output-dir block-d/D9_CLOSURE --d1-audit block-d/D1_RISK_SCORE_MART/D1_RUN_AUDIT.json --d2-audit block-d/D2_LOSS_RECOVERY_EVIDENCE/D2_GOVERNED_CORE_BRIDGE_AUDIT.json --d3-audit block-d/D3_EAD_FRAMEWORK/D3_CONTRACT_AUDIT.json --d4-audit block-d/D4_LGD_FRAMEWORK/D4_RUN_AUDIT.json --d5-audit block-d/D5_EXPECTED_LOSS/D5_ANALYTICAL_SCENARIO_AUDIT.json --d6-audit block-d/D6_DECISION_POLICY/D6_ANALYTICAL_PACK_AUDIT.json --d7-audit block-d/D7_PRICING/D7_DIAGNOSTIC_AUDIT.json --d8-audit block-d/D8_STRESS/D8_ILLUSTRATIVE_SENSITIVITY_AUDIT.json
python src/validate_block_d_d9_checksums.py
```

The final D9 decision must still be made by the authorized owner; no approval
is inferred by this validation report.
