"""One-time source remediation for Block F responsive debt and claim wording.

Safe to re-run: CSS blocks are appended only once and already-negated claim
wording is preserved. This script changes delivery/source presentation only;
it does not alter upstream analytical data or model outputs.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "/* BLOCK_F_RESPONSIVE_HARDENING_V1 */"

PATCHES = {
    "assets/crdpi-overview.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .decision-pipeline{width:100%!important;max-width:100%!important;min-width:0!important;overflow-x:auto!important;overflow-y:hidden!important}
  .decision-pipeline .flow-track{width:100%!important;max-width:100%!important;min-width:0!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:8px!important}
  .decision-pipeline .flow-track>*{max-width:100%!important;min-width:0!important}
}
""",
    "assets/crdpi-portfolio.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .segment-table,.allocation{width:100%!important;max-width:100%!important;min-width:0!important;overflow-x:auto!important;overflow-y:hidden!important}
  .segment-table>*{min-width:0!important;overflow-wrap:anywhere}
  .allocation-row{width:100%!important;max-width:100%!important;min-width:0!important}
}
""",
    "assets/crdpi-loss.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .policy-grid{width:100%!important;max-width:100%!important;min-width:0!important;grid-template-columns:minmax(0,1fr)!important;margin-left:0!important;margin-right:0!important;overflow:hidden!important}
  .policy-card{width:100%!important;max-width:100%!important;min-width:0!important}
}
""",
    "assets/crdpi-monitoring.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .feature-row,.capacity-item{width:100%!important;max-width:100%!important;min-width:0!important;grid-template-columns:minmax(0,1fr)!important;gap:8px!important}
  .feature-track,.capacity-track{width:100%!important;max-width:100%!important;min-width:0!important}
}
""",
    "assets/crdpi-governance.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .wide-table{width:100%!important;max-width:100%!important;min-width:0!important;overflow-x:auto!important;overflow-y:hidden!important}
  .process-flow{width:100%!important;max-width:100%!important;min-width:0!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:8px!important;overflow:hidden!important}
  .process-node{width:100%!important;max-width:100%!important;min-width:0!important}
  .process-flow>i{align-self:center!important;transform:rotate(90deg)}
}
""",
    "assets/crdpi-architecture.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V1 */
@media (max-width: 800px){
  .handoff-flow{width:100%!important;max-width:100%!important;min-width:0!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:8px!important;overflow:hidden!important}
  .handoff-flow>*{width:100%!important;max-width:100%!important;min-width:0!important}
  .handoff-flow>i{width:auto!important;align-self:center!important;transform:rotate(90deg)}
  .repo-tree{width:100%!important;max-width:100%!important;min-width:0!important;overflow-wrap:anywhere!important;word-break:break-word!important}
}
""",
}

PRIMARY_PAGES = [
    "index.html",
    "portfolio-risk/index.html",
    "model-decisioning/index.html",
    "loss-policy-stress/index.html",
    "monitoring/index.html",
    "governance/index.html",
    "architecture/index.html",
]


def patch_css() -> int:
    changed = 0
    for rel, block in PATCHES.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        path.write_text(text.rstrip() + "\n" + block.strip() + "\n", encoding="utf-8")
        print(f"patched responsive containment: {rel}")
        changed += 1
    return changed


def patch_claims() -> int:
    # Only rewrite an unqualified positive phrase. Existing "not a ..." text is retained.
    pattern = re.compile(r"(?<!not a )verified regulatory 12-month PD", re.I)
    changed = 0
    for rel in PRIMARY_PAGES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        new, count = pattern.subn("Not a verified regulatory 12-month PD", text)
        if count:
            path.write_text(new, encoding="utf-8")
            print(f"strengthened regulatory-PD boundary: {rel} ({count})")
            changed += count
    return changed


def main() -> None:
    css = patch_css()
    claims = patch_claims()
    print(f"Block F remediation complete: css_files={css}, claim_replacements={claims}")


if __name__ == "__main__":
    main()
