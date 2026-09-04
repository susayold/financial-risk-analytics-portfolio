from ._helpers import E9, js

def test_patch_checksum_integrity():
    m = js(E9 / "BLOCK_E_FINAL_CHECKSUM_MANIFEST_PATCHED.json")
    assert m["checksum_status"] == "PASS"
    assert m["snapshot_sha256_unchanged"] == "fe2ae600c9913ccfe827509f439c2f14108260e0e237f3fa78715b145123cd42"
