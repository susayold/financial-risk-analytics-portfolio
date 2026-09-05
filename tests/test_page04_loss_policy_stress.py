import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "data" / "page-04-loss-policy-stress.json"
HTML = ROOT / "loss-policy-stress" / "index.html"


def load_page():
    return json.loads(PAGE.read_text(encoding="utf-8"))


def test_central_and_sensitivities_reconcile():
    page = load_page()
    central = page["central_case"]
    assert central["accounts"] == 310066
    assert abs(central["ead_proxy"] - 4469158350.0) < 1e-6
    assert abs(central["expected_loss_proxy"] - 526752273.6678772) < 1e-6
    assert abs(central["el_rate"] - 0.11786386438240148) < 1e-12
    assert [row["scenario"] for row in page["lgd_sensitivity"]] == [
        "Q25_LOW_SEVERITY", "Q50_CENTRAL", "Q75_ADVERSE", "Q90_SEVERE"
    ]
    assert abs(page["lgd_sensitivity"][1]["el_proxy"] - central["expected_loss_proxy"]) < 1e-6
    assert [row["timing"] for row in page["ead_timing"]] == ["0M", "6M", "12M", "18M", "24M"]


def test_policies_and_stress_are_frozen_and_monotonic():
    page = load_page()
    assert {row["scenario"] for row in page["policies"]} == {"GROWTH", "BALANCED", "CONSERVATIVE"}
    for policy in page["policies"]:
        oot = policy["oot"]
        route_sum = oot["approval_rate"] + oot["review_rate"] + oot["decline_rate"]
        assert abs(route_sum - 1.0) < 1e-9
    assert page["controls"]["policy_selection_basis"] == "Validation-2016"
    assert page["controls"]["oot_threshold_tuning"] is False
    stress = page["stress"]
    assert [row["scenario"] for row in stress] == ["BASE", "MILD", "ADVERSE", "SEVERE"]
    assert [row["el_rate"] for row in stress] == sorted(row["el_rate"] for row in stress)
    assert [row["lgd"] for row in stress] == sorted(row["lgd"] for row in stress)
    assert page["meta"]["production_authorized"] is False
    assert page["meta"]["regulatory_compliance_claimed"] is False


def test_pricing_boundary_and_page_claims():
    page = load_page()
    assert page["pricing"]["scope"] == "DESCRIPTIVE_ONLY"
    assert page["pricing"]["profitability_claim_allowed"] is False
    assert page["pricing"]["int_rate_recursion_caveat"] is True
    html = HTML.read_text(encoding="utf-8").lower()
    assert "not profitability" in html
    assert "not forecast" in html
    assert "not regulatory" in html
    assert "ifrs 9" in html
    assert "basel" in html
    assert "production" in html
    assert "range" not in html
    assert "type=\"range\"" not in html
    assert "pricing optimization" not in html
    assert "profit-maximizing" not in html
    assert "page 03" in html or "risk model" in html


if __name__ == "__main__":
    test_central_and_sensitivities_reconcile()
    test_policies_and_stress_are_frozen_and_monotonic()
    test_pricing_boundary_and_page_claims()
    print("page04 tests: PASS 3/3")
