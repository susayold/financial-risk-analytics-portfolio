# B8 Status — Risk Concentration

- **Gate:** `B8 = FINAL REVIEWED / PASS`
- **Materiality rule:** `relative_bad_rate > 1.0 AND account_share >= 0.001`
- **Material segments:** 44
- **Ranking key:** BAD-associated loan amount share descending, with deterministic dimension/segment tie-breakers
- **Tests:** 7/7 PASS

The primary business measure is BAD-associated exposure share. The project-defined concentration index (`relative_bad_rate × loan_amount_share`) is descriptive only.
