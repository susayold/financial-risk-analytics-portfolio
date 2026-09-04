from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
E0 = ROOT / "block-e/E0_MONITORING_CONTRACT"
E5 = ROOT / "block-e/E5_PERFORMANCE_CALIBRATION"
E7 = ROOT / "block-e/E7_POLICY_CONCENTRATION"
E8 = ROOT / "block-e/E8_KRI_GOVERNANCE"
E9 = ROOT / "block-e/E9_FINAL"
PATCH = ROOT / "block-e/GOVERNANCE_PATCH"

def csv(path):
    return pd.read_csv(path)

def js(path):
    return json.loads(path.read_text(encoding="utf-8"))
