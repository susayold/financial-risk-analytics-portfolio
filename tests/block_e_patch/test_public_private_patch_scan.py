from ._helpers import PATCH, js

def test_public_private_patch_scan():
    s = js(PATCH / "PUBLIC_PRIVATE_PATCH_SCAN.json")
    assert s["status"] == "PASS" and s["findings"] == []
