# B5 Assumptions and Limits

1. Zenodo remains target, population, chronology and champion-feature authority.
2. Figshare is supplemental only; its population is not the full core portfolio.
3. Pricing mart covers 325,255 matched accounts, approximately 24.13% of the core.
4. Matched pricing coverage is not automatically representative of the full portfolio.
5. Supplemental conflicts never overwrite core fields; core wins.
6. `grade_derived` is derived from `sub_grade` and is benchmark-only.
7. `int_rate`, `installment` and `term` are economics-only.
8. RejectStats has no observed repayment outcome for rejected applications.
9. No reject inference, rejected BAD rate, PD, loss rate or causal approval claim is made.
10. B5 performs no model preprocessing, fitting, PD/LGD/EAD/ECL estimation or champion-model promotion.
11. Public evidence is aggregate and sanitized; row-level raw/supplemental data stays out of GitHub.
12. RejectStats `risk_score` remains generic; the project does not assume one credit-score methodology across the full rejected-source period.
13. RejectStats DTI parsing removes `%` and stores percentage-point units; parse failures are separately audited and are not imputed.

