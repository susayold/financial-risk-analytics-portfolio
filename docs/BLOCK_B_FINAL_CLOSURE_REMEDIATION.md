# Block B — Final Closure Remediation

## Pre-closure snapshot

- `pre_closure_commit: e325d7f`
- `baseline_change: false`
- `target_state: BLOCK B = FINAL REVIEWED / LOCKED`

Commit `e325d7f` established the B6–B9 analytical outputs and reconciled population baselines. This closure sprint corrects analytical metric naming/denominators, concentration eligibility, test executability, temporal composition completeness and the final lock mechanism without redefining the governed population or outcome.

## Change-control boundary

B0–B5 source/staging governance, B4 core mart design, B5 bridge/pricing/rejected-context logic, target definition, split definition, `issue_d` authority, champion whitelist and source authority remain frozen. No predictive modeling, PD, model performance, calibration, LGD/EAD/ECL, approval cutoff, pricing optimization or reject inference is added.

## Closure changes

1. Split BAD amount metrics into `bad_amount_to_total_exposure` and `bad_associated_share` with explicit denominators.
2. Use the stricter `accounts >= 1000 AND account_share >= 0.001` primary-segment rule.
3. Implement Wilson 95% confidence intervals instead of retaining placeholder columns.
4. Add target-independent B8 dimension informativeness and exclude quasi-constant dimensions from headline ranking while retaining them for audit.
5. Harden B6–B9 tests so PASS is derived from SQL, file content, schema, reconciliation or repository inspection.
6. Add annual purpose/home-ownership composition, final QA and final-lock evidence.

The governed core baseline must remain 1,347,681 accounts, 269,249 BAD, 1,078,432 GOOD, 139 issue cohorts, $19,417,698,475 total `loan_amnt` and $4,186,020,700 BAD-associated amount.

## Closure result

- B6: 8/8 PASS.
- B7: 12/12 PASS.
- B8: 9/9 PASS.
- B9: 9/9 PASS.
- Final QA: 15/15 PASS.
- `baseline_change: false`.
- Final state: `BLOCK B = FINAL REVIEWED / LOCKED`.
