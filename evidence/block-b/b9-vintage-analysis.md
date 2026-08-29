# B9 Run Report — Vintage / Temporal

## Work completed

B9 used `issue_d` as the sole temporal authority and generated monthly cohort, annual cohort and split summaries. Monthly and annual aggregations reconcile exactly to the frozen core.

## Split baseline

| Split | Accounts | Observed BAD rate | Date range |
|---|---:|---:|---|
| Development | 829,347 | 18.46% | 2007-06-01 → 2015-12-01 |
| Validation | 293,057 | 23.28% | 2016-01-01 → 2016-12-01 |
| OOT | 169,117 | 23.13% | 2017-01-01 → 2017-12-01 |
| Historical Shadow | 56,160 | 15.75% | 2018-01-01 → 2018-12-01 |

## Annual view

| Issue year | Accounts | Observed BAD rate | BAD-associated amount |
|---:|---:|---:|---:|
| 2007 | 599 | 26.38% | $1,552,225 |
| 2008 | 2,393 | 20.73% | $4,984,450 |
| 2009 | 5,281 | 13.69% | $7,628,075 |
| 2010 | 12,537 | 14.01% | $18,601,150 |
| 2011 | 21,721 | 15.18% | $43,360,600 |
| 2012 | 53,367 | 16.20% | $127,242,925 |
| 2013 | 134,804 | 15.60% | $329,869,625 |
| 2014 | 223,102 | 18.45% | $640,993,375 |
| 2015 | 375,543 | 20.18% | $1,192,093,600 |
| 2016 | 293,057 | 23.28% | $1,051,046,600 |
| 2017 | 169,117 | 23.13% | $618,130,600 |
| 2018 | 56,160 | 15.75% | $150,517,475 |

## Interpretation boundary

Temporal shifts may be described as associated, coincident or co-moving. They are not treated as causal. The 2018 cohort is a historical shadow/resolved-loan sample and not a live performance-monitoring window.

## Evidence files

- `outputs/b9/vintage_monthly.csv`
- `outputs/b9/vintage_annual.csv`
- `outputs/b9/vintage_split.csv`
- `outputs/b9/b9_test_results.json`
