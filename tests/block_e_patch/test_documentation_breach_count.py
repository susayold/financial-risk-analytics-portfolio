import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_documentation_breach_count():
    e8 = json.loads((ROOT / "block-e/E8_KRI_GOVERNANCE/E8_TEST_RESULTS_PATCHED.json").read_text(encoding="utf-8"))
    expected = e8["breach_count"]
    assert expected == 3
    for rel in ["block-e/BLOCK_E_STATUS.md", "block-e/BLOCK_E_EXECUTION_TRACKER.md"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert f"{expected} breaches" in text
        assert "4 breaches" not in text
