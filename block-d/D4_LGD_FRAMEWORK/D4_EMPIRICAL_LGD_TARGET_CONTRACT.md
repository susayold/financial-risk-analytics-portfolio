# D4 Empirical LGD Target Contract

- Population: `actual_default == 1`, matched scored/origination fields available, issue_year <= 2017.
- Target: frozen D2 `retrospective_lgd_proxy_model`; no silent formula change.
- D2 formula family: `net_economic_loss_proxy / funded_amnt`, with D2 anomaly classification and model clipping retained.
- Validation: rolling-origin folds <=2013 -> 2014, <=2014 -> 2015, <=2015 -> 2016, <=2016 -> 2017; inadequate folds are explicitly recorded as skipped.
- 2018: excluded from primary empirical selection and monitor-only.
- Claim boundary: analytical portfolio LGD evidence only; not regulatory, IFRS 9, Basel, or production LGD.

Rows used in matched challenger population: **49,049**.
