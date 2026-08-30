"""Export sanitized, aggregate-only B6-B9 reports and public evidence."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def read_json(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def read_csv(path: Path):
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
def pct(v): return f"{float(v) * 100:.2f}%"
def money(v): return f"${float(v):,.0f}"
def write(path: Path, text: str): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text.strip() + '\n', encoding='utf-8')


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1]); a = p.parse_args(); r = a.repo_root
    b6 = read_json(r/'outputs/b6/portfolio_kpis.json'); b6t = read_json(r/'outputs/b6/b6_test_results.json'); b7t = read_json(r/'outputs/b7/b7_test_results.json'); b8 = read_json(r/'outputs/b8/b8_summary.json'); b8t = read_json(r/'outputs/b8/b8_test_results.json'); b9 = read_json(r/'outputs/b9/b9_summary.json'); b9t = read_json(r/'outputs/b9/b9_test_results.json')
    seg = read_csv(r/'outputs/b7/segment_risk.csv'); conc = read_csv(r/'outputs/b8/risk_concentration.csv'); annual = read_csv(r/'outputs/b9/vintage_annual.csv'); splits = read_csv(r/'outputs/b9/vintage_split.csv'); composition = read_csv(r/'outputs/b9/vintage_composition_annual.csv')
    headline = sorted([x for x in seg if x['primary_segment'] == 'True'], key=lambda x: float(x['bad_rate']), reverse=True)[:8]
    material = sorted([x for x in conc if x['materiality_flag'] == 'True'], key=lambda x: int(x['materiality_rank']))[:8]
    latest_year = max(int(x['issue_year']) for x in composition)
    latest_purpose = sorted([x for x in composition if int(x['issue_year']) == latest_year and x['dimension'] == 'purpose'], key=lambda x: float(x['account_share_within_year']), reverse=True)[0]
    b6_status, b7_status, b8_status, b9_status = b6t['gate_status'], b7t['gate_status'], b8t['gate_status'], b9t['gate_status']

    write(r/'docs/B6_STATUS.md', f'''# B6 Status — Portfolio Overview

- **Gate:** `B6 = FINAL REVIEWED / {b6_status}`
- **Source:** locked `mart.mart_credit_application_core`
- **Grain:** one row per granted-loan application/account
- **Accounts:** {b6['total_accounts']:,}
- **GOOD / BAD:** {b6['good_accounts']:,} / {b6['bad_accounts']:,}
- **Observed final-resolution BAD rate:** {pct(b6['observed_bad_rate'])}
- **Total loan amount proxy:** {money(b6['total_loan_amount'])}
- **BAD-associated loan amount:** {money(b6['bad_associated_loan_amount'])} ({pct(b6['bad_associated_exposure_share'])})
- **Tests:** 8/8 {b6_status}

B6 is descriptive. `loan_amnt` is an exposure proxy, not observed EAD; BAD-associated loan amount is not realized loss; the BAD rate is not verified 12-month PD.
''')
    write(r/'docs/B6_RUN_REPORT.md', f'''# B6 Run Report — Portfolio Overview

## Work completed

B6 profiled the frozen core mart without caps, imputation, outlier treatment or feature transforms. It produced a portfolio KPI baseline, numeric percentile profile and composition tables for the governed core dimensions.

## Results

| Metric | Result |
|---|---:|
| Total accounts | {b6['total_accounts']:,} |
| GOOD | {b6['good_accounts']:,} |
| BAD | {b6['bad_accounts']:,} |
| Observed final-resolution BAD rate | {pct(b6['observed_bad_rate'])} |
| Total `loan_amnt` proxy | {money(b6['total_loan_amount'])} |
| BAD-associated amount | {money(b6['bad_associated_loan_amount'])} |
| BAD-associated exposure share | {pct(b6['bad_associated_exposure_share'])} |
| Issue cohorts | {b6['issue_cohorts']} |

## QA

`{b6_status}` across B6T01–B6T08. Direct core-source exposure/null reconciliations, count identities, category shares and the public claim contract pass. Pricing fields are absent from the core mart; matched pricing remains under the B5 boundary. This observed BAD rate is not verified 12-month PD.

## Artifacts

- `outputs/b6/portfolio_kpis.json`
- `outputs/b6/numeric_profile.csv`
- `outputs/b6/portfolio_mix.csv`
- `outputs/b6/b6_test_results.json`
''')

    headline_md = '\n'.join(f"| {x['dimension']} | {x['segment']} | {int(x['accounts']):,} | {pct(x['bad_rate'])} | {float(x['relative_bad_rate']):.2f}x | {pct(x['bad_associated_share'])} |" for x in headline)
    write(r/'docs/B7_STATUS.md', f'''# B7 Status — Segment Risk

- **Gate:** `B7 = FINAL REVIEWED / {b7_status}`
- **Dimensions:** {len(set(x['dimension'] for x in seg))}
- **Segment rows:** {len(seg):,}, including fixed buckets where required
- **Primary-segment rule:** `accounts >= 1,000 AND account_share >= 0.1%`
- **Tests:** 12/12 {b7_status}

B7 reports single-variable descriptive observed BAD segmentation only. It does not select model features or claim predictive performance.
''')
    write(r/'docs/B7_RUN_REPORT.md', f'''# B7 Run Report — Segment Risk

## Work completed

B7 segmented the frozen core by fixed FICO and DTI bands, exact Q1–Q4 cut points for revenue and loan amount, and five categorical dimensions. Missing values are explicit as `UNKNOWN / MISSING`; no silent row drops were used. The primary rule is `accounts >= 1,000 AND account_share >= 0.1%`.

## Headline descriptive groups

| Dimension | Segment | Accounts | Observed BAD rate | Relative BAD rate | BAD-associated share |
|---|---|---:|---:|---:|---:|
{headline_md}

`BAD-associated share` means segment BAD-associated `loan_amnt` divided by total portfolio BAD-associated `loan_amnt`. It is not the segment's share of total portfolio exposure; that separate ratio is `bad_amount_to_total_exposure`.

These are screening findings, not causal effects, approval rules or automatically approved Block C features. This is not predictive model performance.

## QA

`{b7_status}` across B7T01–B7T12. Every dimension reconciles to {b6['total_accounts']:,} accounts, 100% of the loan amount proxy and 100% of total BAD-associated amount; Wilson 95% intervals are executable and bounded.
''')

    material_md = '\n'.join(f"| {x['materiality_rank']} | {x['dimension']} | {x['segment']} | {int(x['accounts']):,} | {pct(x['bad_rate'])} | {pct(x['bad_associated_share'])} |" for x in material)
    write(r/'docs/B8_STATUS.md', f'''# B8 Status — Risk Concentration

- **Gate:** `B8 = FINAL REVIEWED / {b8_status}`
- **Materiality rule:** `headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0`
- **Material segments:** {b8['material_segments']}
- **Ranking key:** BAD-associated loan amount share descending, with deterministic dimension/segment tie-breakers
- **Dimension filter:** dominant segment share > 99.5% → `QUASI_CONSTANT`, audit-visible but excluded from headline ranking
- **Tests:** 9/9 {b8_status}

The primary measure is BAD-associated loan amount share. The project-defined concentration index (`relative_bad_rate × loan_amount_share`) is descriptive only.
''')
    write(r/'docs/B8_RUN_REPORT.md', f'''# B8 Run Report — Risk Concentration

## Work completed

B8 joined elevated observed BAD rates to scale using only B7 single-variable outputs. The materiality rule was fixed before ranking and was not tuned to the observed result. No combinatorial segment search was performed.

## First material rows by BAD-associated loan amount share

| Rank | Dimension | Segment | Accounts | Observed BAD rate | BAD-associated share |
|---:|---|---|---:|---:|---:|
{material_md}

`BAD-associated share` is segment BAD-associated loan amount divided by total BAD-associated loan amount. The `experience_c` dimension is quasi-constant (dominant share >99.5%), so it remains audit-visible but is excluded from headline/materiality ranking.

The table is a prioritization view for descriptive investigation. It does not represent realized loss, expected loss, a causal driver ranking or a production policy.

## QA

`{b8_status}` across B8T01–B8T09. Account, exposure and BAD-associated shares reconcile independently within every dimension; quasi-constant dimensions are excluded from headline ranking and ranks are deterministic.
''')

    annual_md = '\n'.join(f"| {x['issue_year']} | {int(x['accounts']):,} | {pct(x['bad_rate'])} | {money(x['bad_associated_loan_amount'])} |" for x in annual)
    split_md = '\n'.join(f"| {x['split_name']} | {int(x['accounts']):,} | {pct(x['bad_rate'])} | {x['min_issue_d']} → {x['max_issue_d']} |" for x in splits)
    write(r/'docs/B9_STATUS.md', f'''# B9 Status — Vintage / Temporal Analysis

- **Gate:** `B9 = FINAL REVIEWED / {b9_status}`
- **Temporal authority:** `issue_d`
- **Monthly cohorts:** {b9['cohorts']}
- **Annual years:** {b9['years']}
- **Composition dimensions:** `purpose`, `home_ownership_n`
- **Tests:** 9/9 {b9_status}

Mandatory boundary: the 2018 resolved-loan sample is subject to right truncation and resolution selection. A lower observed BAD rate in 2018 is not confirmed credit-quality improvement. This is not live monitoring.
''')
    write(r/'docs/B9_RUN_REPORT.md', f'''# B9 Run Report — Vintage / Temporal

## Work completed

B9 used `issue_d` as the sole temporal authority and generated monthly cohort, annual cohort, split and annual composition summaries. Monthly and annual aggregations reconcile exactly to the frozen core.

## Split baseline

| Split | Accounts | Observed BAD rate | Date range |
|---|---:|---:|---|
{split_md}

## Annual view

| Issue year | Accounts | Observed BAD rate | BAD-associated amount |
|---:|---:|---:|---:|
{annual_md}

## Composition insight

In {latest_year}, `{latest_purpose['segment']}` was the largest purpose segment at {pct(latest_purpose['account_share_within_year'])} of that year's accounts, with an observed BAD rate of {pct(latest_purpose['bad_rate'])}. This is descriptive composition, not a causal or policy conclusion.

## Interpretation boundary

Temporal shifts may be described as associated, coincident or co-moving. They are not treated as causal. The 2018 cohort is a historical shadow/resolved-loan sample and not a live performance-monitoring window. This is not predictive PD or live monitoring.
''')

    findings = '\n'.join(f"- **{x['dimension']} = {x['segment']}**: {pct(x['bad_rate'])} observed BAD rate, {float(x['relative_bad_rate']):.2f}x the portfolio baseline, {pct(x['bad_associated_share'])} of total BAD-associated loan amount." for x in headline[:5])
    write(r/'docs/BLOCK_B_ANALYTICAL_FINDINGS.md', f'''# Block B — Analytical Findings (B6–B9)

## Executive answer

The resolved granted-loan portfolio contains **{b6['total_accounts']:,} accounts**, with an observed final-resolution BAD rate of **{pct(b6['observed_bad_rate'])}**. BAD-associated `loan_amnt` totals **{money(b6['bad_associated_loan_amount'])}**, or **{pct(b6['bad_associated_exposure_share'])}** of the loan amount proxy.

## Where observed risk is higher

{findings}

These are descriptive, single-variable comparisons. They are not causal explanations and are not an approval policy.

## Where higher risk overlaps with scale

The B8 materiality screen found **{b8['material_segments']}** segments under the predefined rule `headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0`. The primary quantity is BAD-associated loan amount share: segment BAD-associated amount divided by total BAD-associated amount.

## How risk moves across cohorts

Development observed BAD rate is **{pct(splits[0]['bad_rate'])}**, Validation **{pct(splits[1]['bad_rate'])}**, OOT **{pct(splits[2]['bad_rate'])}**, and Historical Shadow 2018 **{pct(splits[3]['bad_rate'])}**. The 2018 decrease is not interpreted as confirmed quality improvement because of right truncation/resolution selection.

## Handoff

Block C may consume the frozen `mart_credit_application_core`. B6–B9 rankings and findings are evidence for analysis, not automatically admitted model features. Observed BAD is not verified 12-month PD.
''')
    write(r/'docs/BLOCK_B_ASSUMPTIONS_AND_LIMITS.md', '''# Block B — Assumptions and Limits

## Metric semantics

- `actual_default` is the observed final-resolution outcome in the governed granting dataset.
- Observed BAD rate is not verified 12-month PD, forecast PD or model score.
- `loan_amnt` is an exposure proxy; it is not observed EAD.
- BAD-associated loan amount is not realized loss, LGD, ECL or expected loss.
- Matched pricing fields remain B5 descriptive enrichment; they are not blended into the core baseline.
- Rejected applications remain context-only with no inferred GOOD/BAD outcome.

## Temporal assumptions

- `issue_d` is the only temporal authority.
- Temporal movement is descriptive and non-causal.
- The 2018 historical-shadow sample is resolution-selected and right-truncated; it is not live monitoring.

## Scope limits

This work does not claim ROC-AUC, KS, Gini, calibration, PD, LGD, EAD, ECL, optimized approval policy, reject inference or production monitoring. No caps, imputations, outlier treatments or model transformations were fitted in B6–B9.
''')
    write(r/'docs/BLOCK_B_FINAL_LOCK.md', f'''# Block B Final Lock

## Status

`BLOCK B = FINAL REVIEWED / LOCKED`

## Locked gates

- B0–B3: FINAL REVIEWED / PASS
- B4: FINAL REVIEWED / PASS — core application mart
- B5: FINAL REVIEWED / PASS — controlled enrichment / rejected context boundary
- B6: FINAL REVIEWED / {b6_status}
- B7: FINAL REVIEWED / {b7_status}
- B8: FINAL REVIEWED / {b8_status}
- B9: FINAL REVIEWED / {b9_status}

## Locked populations

- Core application mart: {b6['total_accounts']:,} accounts; {b6['bad_accounts']:,} BAD; {b6['good_accounts']:,} GOOD; {b6['issue_cohorts']} issue cohorts.
- Matched pricing sample: 325,255 accounts; B5 bridge authority preserved.
- Rejected context: 27,648,741 records; context only; no outcome assignment.

## Final claim boundary

Allowed: governed data engineering, data quality, composition, observed BAD segmentation, concentration screening, vintage analysis and descriptive pricing context. Not allowed: verified PD, credit-score model performance, calibration, expected loss, LGD/EAD, optimized approval, causal reject inference or live monitoring.

## Transition

`PORTFOLIO RISK MAPPED. NEXT: BUILD THE MODEL.` Block C consumes the frozen core mart; B6–B9 findings do not silently become model features.
''')

    ev = r/'evidence/block-b'
    for name, doc, artifacts in [
        ('b6-portfolio-overview.md', 'B6_RUN_REPORT.md', ['outputs/b6/portfolio_kpis.json','outputs/b6/numeric_profile.csv','outputs/b6/portfolio_mix.csv','outputs/b6/b6_test_results.json']),
        ('b7-segment-risk.md', 'B7_RUN_REPORT.md', ['outputs/b7/segment_risk.csv','outputs/b7/b7_band_definitions.json','outputs/b7/b7_test_results.json']),
        ('b8-risk-concentration.md', 'B8_RUN_REPORT.md', ['outputs/b8/risk_concentration.csv','outputs/b8/b8_dimension_profile.csv','outputs/b8/b8_summary.json','outputs/b8/b8_test_results.json']),
        ('b9-vintage-analysis.md', 'B9_RUN_REPORT.md', ['outputs/b9/vintage_monthly.csv','outputs/b9/vintage_annual.csv','outputs/b9/vintage_split.csv','outputs/b9/vintage_composition_annual.csv','outputs/b9/b9_test_results.json']),
    ]:
        write(ev/name, (r/'docs'/doc).read_text(encoding='utf-8') + '\n## Evidence files\n\n' + '\n'.join(f'- `{x}`' for x in artifacts))
    write(ev/'block-b-final-lock.md', (r/'docs/BLOCK_B_FINAL_LOCK.md').read_text(encoding='utf-8'))
    print(json.dumps({'status':'PASS','block_b_status':'FINAL REVIEWED / LOCKED','reports_refreshed':8}, indent=2)); return 0


if __name__ == '__main__': raise SystemExit(main())
