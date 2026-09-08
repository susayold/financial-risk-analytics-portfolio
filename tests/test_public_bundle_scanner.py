import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_public_bundle import scan_text


def test_privacy_scanner_detects_row_level_and_secret_fixtures():
    fixtures = {
        'account': '"account_id": 12345',
        'borrower': '"borrower_id": "abc"',
        'customer': '"customer_id": 99',
        'row_level': '"row_level_prediction": 0.42',
        'kaggle': '/kaggle/input/private-data/file.csv',
        'windows': r'C:\\Users\\analyst\\private.csv',
        'bearer': 'Authorization: Bearer abc.def-123',
        'secret': 'api_key="abcdefghijk"',
        'phone': 'Phone: +84 912 345 678',
    }
    for name, payload in fixtures.items():
        assert scan_text(payload, name), f"scanner missed negative fixture: {name}"


def test_privacy_scanner_allows_boundary_language():
    text = (
        'Browser row-level data is false. '
        'Raw row-level predictions remain private. '
        'Production authorization remains false and regulatory compliance is not claimed.'
    )
    assert scan_text(text) == []
