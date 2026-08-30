# B8 Status — Risk Concentration

- **Gate:** `B8 = FINAL REVIEWED / PASS`
- **Materiality rule:** `headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0`
- **Material segments:** 43
- **Ranking key:** BAD-associated loan amount share descending, with deterministic dimension/segment tie-breakers
- **Dimension filter:** dominant segment share > 99.5% → `QUASI_CONSTANT`, audit-visible but excluded from headline ranking
- **Tests:** 9/9 PASS

The primary measure is BAD-associated loan amount share. The project-defined concentration index (`relative_bad_rate × loan_amount_share`) is descriptive only.
