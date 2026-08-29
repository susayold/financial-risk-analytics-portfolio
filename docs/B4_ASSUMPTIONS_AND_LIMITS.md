# B4 ASSUMPTIONS AND LIMITS

1. The mart represents resolved granted loans only.
2. `actual_default` remains a final-resolution outcome.
3. The mart is not a verified 12-month Probability of Default dataset.
4. `loan_amnt` is not observed EAD; it is a governed exposure proxy.
5. No LGD is observed in the primary source.
6. No model preprocessing is applied in B4.
7. Geography remains analysis-only.
8. Supplemental pricing variables are intentionally absent.
9. RejectStats remains outside the granted-loan mart.
10. Historical Shadow remains a resolved-sample simulation, not live monitoring.

`dq_status` reflects reviewed structural/source controls, not model-preprocessing quality. The mart is a reproducible analytical core and does not claim production deployment, model scores, PD calibration, cutoffs, pricing, LGD, EAD estimates or ECL.
