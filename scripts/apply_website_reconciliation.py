from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count == 0:
        if new in text:
            return
        raise RuntimeError(f"Expected text not found in {path}: {old[:100]!r}")
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    text = read(path)
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count == 0:
        if replacement in text:
            return
        raise RuntimeError(f"Pattern not found in {path}: {pattern[:100]!r}")
    write(path, updated)


def patch_overview() -> None:
    replace_once(
        "index.html",
        '<span class="hero-badge badge-progress"><i></i>Block F · Delivery in progress</span>',
        '<span class="hero-badge badge-blue"><i></i>Block F · Delivered</span>',
    )
    replace_once(
        "index.html",
        '<b>Better decisions</b><small>Higher quality approvals</small>',
        '<b>Decision trade-offs</b><small>Historical policy simulation</small>',
    )


def patch_portfolio() -> None:
    path = ROOT / "public/data/page-02-portfolio-risk.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["meta"]["as_of"] = payload["portfolio"]["max_issue_d"]
    payload["meta"]["oot_cutoff"] = "2017-12-01"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    replace_once(
        "portfolio-risk/index.html",
        'As of Block F (v1.0.2-final) &nbsp;·&nbsp; Latest data: <b data-bind="meta.as_of"></b> (LendingClub)',
        'Block F delivery · <b>block-f-v1.0-final</b> &nbsp;·&nbsp; Full resolved-loan portfolio through <b data-bind="meta.as_of"></b> &nbsp;·&nbsp; OOT cutoff 2017-12',
    )

    replace_once(
        "scripts/build_page02_public_data.py",
        '    check(payload["meta"]["public_safe"] is True, "Page 02 must remain public-safe")\n',
        '    check(payload["meta"]["public_safe"] is True, "Page 02 must remain public-safe")\n'
        '    check(payload["meta"]["as_of"] == portfolio["max_issue_d"] == "2018-12-01", "Page 02 full-core latest date must be 2018-12-01")\n'
        '    check(payload["meta"]["oot_cutoff"] == "2017-12-01", "Page 02 OOT cutoff must remain 2017-12-01")\n',
    )


def patch_model() -> None:
    replace_once(
        "scripts/build_page03_public_data.py",
        '    quarterly = read_csv(ROOT / "block-e" / "E5_PERFORMANCE_CALIBRATION" / "quarterly_performance.csv")\n',
        '    quarterly = read_csv(ROOT / "block-e" / "E5_PERFORMANCE_CALIBRATION" / "quarterly_performance.csv")\n'
        '    score_psi = read_csv(ROOT / "block-e" / "E4_SCORE_RISK_MIX" / "score_psi.csv")\n',
    )
    replace_once(
        "scripts/build_page03_public_data.py",
        '    quarterly_auc_range = max(number(row, "roc_auc") for row in oot_quarters) - min(number(row, "roc_auc") for row in oot_quarters)\n',
        '    quarterly_auc_range = max(number(row, "roc_auc") for row in oot_quarters) - min(number(row, "roc_auc") for row in oot_quarters)\n'
        '    annual_score_psi = row_for(score_psi, "window_id", "OOT")\n',
    )
    replace_once(
        "scripts/build_page03_public_data.py",
        '            "prediction_psi": 0.003663365,\n',
        '            "prediction_psi": number(annual_score_psi, "psi"),\n',
    )


def patch_loss_pricing() -> None:
    replace_once(
        "scripts/build_page04_public_data.py",
        '                "mean_rate": number(row["mean_int_rate"]),\n',
        '                "mean_rate": number(row["mean_int_rate"]) / 100.0,\n',
    )
    replace_once(
        "scripts/build_page04_public_data.py",
        '    pricing.sort(key=lambda item: item["decile"])\n',
        '    pricing.sort(key=lambda item: item["decile"])\n'
        '    if not all(0.0 <= item["mean_rate"] <= 1.0 for item in pricing):\n'
        '        raise ValueError("Pricing mean_rate must be stored as a decimal fraction in the public contract")\n'
        '    if not all(abs((item["mean_rate"] - item["mean_el_rate"]) - item["diagnostic_spread"]) < 1e-12 for item in pricing):\n'
        '        raise ValueError("Pricing diagnostic spread does not reconcile after interest-rate normalization")\n',
    )


def patch_monitoring() -> None:
    replace_once(
        "scripts/build_page05_public_data.py",
        '    decision = read_json(E / "E9_FINAL" / "BLOCK_E_DECISION_PATCHED.json")\n',
        '    decision = read_json(E / "E9_FINAL" / "BLOCK_E_DECISION_PATCHED.json")\n'
        '    kri_register = read_csv(E / "E8_KRI_GOVERNANCE" / "kri_register_PATCHED.csv")\n',
    )
    replace_once(
        "scripts/build_page05_public_data.py",
        '    assert counts == {\n        "kri_count": 92, "alert_count": 21, "amber_alert_count": 20,\n        "red_alert_count": 1, "breach_count": 3, "investigation_count": 21,\n        "action_count": 21, "green_alert_count": 0,\n    }\n',
        '    assert counts == {\n        "kri_count": 92, "alert_count": 21, "amber_alert_count": 20,\n        "red_alert_count": 1, "breach_count": 3, "investigation_count": 21,\n        "action_count": 21, "green_alert_count": 0,\n    }\n'
        '    kri_stage_counts = {stage: sum(1 for row in kri_register if row["source_stage"] == stage) for stage in ("E3", "E4", "E5", "E6", "E7")}\n'
        '    if kri_stage_counts != {"E3": 3, "E4": 17, "E5": 68, "E6": 1, "E7": 3}:\n'
        '        raise ValueError(f"Unexpected canonical KRI stage counts: {kri_stage_counts}")\n'
        '    if sum(kri_stage_counts.values()) != counts["kri_count"]:\n'
        '        raise ValueError("KRI domain counts do not reconcile to the canonical total")\n',
    )
    replace_once(
        "scripts/build_page05_public_data.py",
        '        "governance_counts": counts,\n',
        '        "governance_counts": counts,\n'
        '        "kri_domain_counts": {\n'
        '            "feature_drift": kri_stage_counts["E3"],\n'
        '            "score_risk_mix": kri_stage_counts["E4"],\n'
        '            "performance_calibration": kri_stage_counts["E5"],\n'
        '            "loss_severity": kri_stage_counts["E6"],\n'
        '            "policy_capacity_concentration": kri_stage_counts["E7"],\n'
        '            "total": sum(kri_stage_counts.values()),\n'
        '        },\n'
        '        "data_quality_control": {"registry": "E2", "kri_count": 0, "note": "Governed DQ control layer outside the E8 KRI registry"},\n',
    )

    regex_once(
        "assets/crdpi-monitoring.js",
        r'  function renderDomains\(page\) \{.*?\n  \}\n\n  function renderFeatures',
        '''  function renderDomains(page) {
    const k = page.kri_domain_counts;
    const domains = [
      ["Data Quality & Coverage", "GREEN", "CONTROL LAYER", "E2 governed DQ checks · outside the 92-KRI registry", "green", "i-shield"],
      ["Feature Drift", "AMBER", `${k.feature_drift} KRIs`, "3 AMBER findings · 0 RED", "amber", "i-trend"],
      ["Score & Risk Mix", "GREEN", `${k.score_risk_mix} KRIs`, `Annual PSI ${page.score_drift.annual_psi.toFixed(4)} · stable`, "green", "i-bars"],
      ["Model Performance & Calibration", "AMBER / RED", `${k.performance_calibration} KRIs`, "Annual AMBER · 2017-10 RED", "mixed", "i-shield"],
      ["Loss / Severity", "GREEN", `${k.loss_severity} KRI`, "0 non-GREEN E6 alerts", "green", "i-target"],
      ["Policy Capacity & Concentration", "AMBER", `${k.policy_capacity_concentration} KRIs`, "Growth / Balanced watch", "amber", "i-clock"],
    ];
    $("#domains").innerHTML = domains.map((row) => `<article class="domain-card ${row[4]}"><span class="domain-icon"><svg><use href="#${row[5]}"></use></svg></span><h3>${row[0]}</h3><p><b>${row[1]}</b> · ${row[2]}</p><small>${row[3]}</small></article>`).join("");
  }

  function renderFeatures''',
    )
    replace_once(
        "monitoring/index.html",
        '<p>One frozen population monitored across six risk domains.</p>',
        '<p>One frozen population monitored across five canonical KRI domains plus the upstream E2 data-quality control layer.</p>',
    )


def patch_governance_and_architecture() -> None:
    replace_once("governance/index.html", "<h2>Release History</h2>", "<h2>Analytical Release History — Blocks D/E</h2>")
    for old, new in [
        ("BLOCK F · IN PROGRESS", "BLOCK F · DELIVERED"),
        ("<strong>IN PROGRESS</strong>", "<strong>DELIVERED</strong>"),
        ("Current state: IN PROGRESS", "Current state: DELIVERED"),
    ]:
        replace_once("architecture/index.html", old, new)


def patch_public_docs() -> None:
    replace_once(
        "README.md",
        '- Block F: **final closure in progress** on the recruiter-facing delivery layer.\n\nBlock F must not change the model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.',
        '- Block F: [`block-f-v1.0-final`](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-f-v1.0-final) — **DELIVERED** recruiter-facing delivery layer.\n\nBlock F did not change the model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.',
    )
    replace_once("README.md", "Block F closure adds:", "Block F delivery includes:")

    old = '''## Block F delivery state

Block F is being closed through a dedicated delivery QA sprint. It must not change the frozen model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.

Target closure artifacts:

```text
block-f/BLOCK_F_STATUS.md
block-f/BLOCK_F_FINAL_QA.json
block-f/BLOCK_F_RELEASE_MANIFEST.json
block-f/BLOCK_F_PUBLIC_ARTIFACT_INDEX.csv
block-f/BLOCK_F_CLOSURE.md
```

Target final tag after all delivery gates pass:

```text
block-f-v1.0-final
```
'''
    new = '''## Block F delivery state

Block F is **DELIVERED**. The recruiter-facing seven-page website passed delivery QA and deployment smoke without changing the frozen model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.

Final closure artifacts:

```text
block-f/BLOCK_F_STATUS.md
block-f/BLOCK_F_FINAL_QA.json
block-f/BLOCK_F_RELEASE_MANIFEST.json
block-f/BLOCK_F_PUBLIC_ARTIFACT_INDEX.csv
block-f/BLOCK_F_CLOSURE.md
```

Final release: [`block-f-v1.0-final`](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-f-v1.0-final)
'''
    replace_once("PROJECT_MASTER_LINKS.md", old, new)


def write_regression_tests() -> None:
    test = r'''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_portfolio_dates_and_release_language_are_unambiguous():
    page = load("page-02-portfolio-risk.json")
    assert page["meta"]["as_of"] == page["portfolio"]["max_issue_d"] == "2018-12-01"
    assert page["meta"]["oot_cutoff"] == "2017-12-01"
    html = (ROOT / "portfolio-risk" / "index.html").read_text(encoding="utf-8")
    assert "block-f-v1.0-final" in html
    assert "Latest data:" not in html
    assert "As of Block F (v1.0.2-final)" not in html


def test_model_prediction_psi_uses_monitoring_canonical_value():
    model = load("page-03-model-decisioning.json")
    monitoring = load("page-05-monitoring.json")
    assert model["ranking"]["prediction_psi"] == monitoring["score_drift"]["annual_psi"]


def test_pricing_contract_uses_decimal_rate_units_and_reconciles_spread():
    page = load("page-04-loss-policy-stress.json")
    for row in page["pricing"]["diagnostics"]:
        assert 0 <= row["mean_rate"] <= 1
        assert abs((row["mean_rate"] - row["mean_el_rate"]) - row["diagnostic_spread"]) < 1e-12
    assert abs(page["pricing"]["diagnostics"][0]["mean_rate"] - 0.06923217335266634) < 1e-15


def test_monitoring_kri_domain_counts_reconcile_to_92():
    page = load("page-05-monitoring.json")
    counts = page["kri_domain_counts"]
    assert counts == {
        "feature_drift": 3,
        "score_risk_mix": 17,
        "performance_calibration": 68,
        "loss_severity": 1,
        "policy_capacity_concentration": 3,
        "total": 92,
    }
    assert page["data_quality_control"]["kri_count"] == 0
    assert page["governance_counts"]["kri_count"] == counts["total"]


def test_final_delivery_status_is_not_stale_in_public_pages_or_docs():
    overview = (ROOT / "index.html").read_text(encoding="utf-8")
    architecture = (ROOT / "architecture" / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    master = (ROOT / "PROJECT_MASTER_LINKS.md").read_text(encoding="utf-8")
    assert "Block F · Delivery in progress" not in overview
    assert "BLOCK F · IN PROGRESS" not in architecture
    assert "Current state: IN PROGRESS" not in architecture
    assert "final closure in progress" not in readme
    assert "Block F is being closed" not in master
    assert "block-f-v1.0-final" in readme
    assert "block-f-v1.0-final" in master


def test_overview_does_not_claim_proven_approval_improvement():
    overview = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "Higher quality approvals" not in overview
    assert "Historical policy simulation" in overview
'''
    write("tests/test_website_reconciliation.py", test)


def main() -> None:
    patch_overview()
    patch_portfolio()
    patch_model()
    patch_loss_pricing()
    patch_monitoring()
    patch_governance_and_architecture()
    patch_public_docs()
    write_regression_tests()
    print("Website reconciliation patch applied")


if __name__ == "__main__":
    main()
