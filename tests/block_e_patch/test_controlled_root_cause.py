from ._helpers import E8, csv

def test_controlled_root_cause():
    allowed = {"DATA_QUALITY","DATA_COVERAGE","MISSINGNESS","POPULATION_SHIFT","PRODUCT_MIX_SHIFT","PRICING_CONTRACT_SHIFT","MODEL_PERFORMANCE","CALIBRATION","OUTCOME_MATURITY","CONCENTRATION","POLICY_CAPACITY","ECONOMIC_STRESS","UNKNOWN"}
    assert set(csv(E8 / "investigation_register.csv").root_cause) <= allowed
