"""Idempotent source remediation for Block F responsive debt and claim wording.

Safe to re-run: each CSS hardening block is appended only once and already-negated
claim wording is preserved. This changes presentation/delivery only; it does not
alter upstream analytical data, model outputs, policy thresholds, or monitoring findings.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER_V1 = "/* BLOCK_F_RESPONSIVE_HARDENING_V1 */"
MARKER_V2 = "/* BLOCK_F_RESPONSIVE_HARDENING_V2 */"
MARKER_V3 = "/* BLOCK_F_RESPONSIVE_HARDENING_V3 */"
MARKER_V4 = "/* BLOCK_F_RESPONSIVE_HARDENING_V4 */"

PATCHES_V1 = {
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

PATCHES_V2 = {
    "assets/crdpi-overview.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 340px){
  .hero-visual,.visual-grid,.trust-strip,.trust-strip .page-width{width:100%!important;max-width:100%!important;min-width:0!important}
  .hero-visual,.visual-grid{overflow:hidden!important}
  .visual-grid{inset:auto!important;transform:none!important}
  .trust-strip .page-width{grid-template-columns:minmax(0,1fr)!important}
  .trust-item{width:100%!important;max-width:100%!important;min-width:0!important}
}
""",
    "assets/crdpi-portfolio.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 340px){
  #governance-flow.flow{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;min-width:0!important;overflow:visible!important;gap:8px!important}
  #governance-flow .flow-node{width:100%!important;max-width:100%!important;min-width:0!important}
  #governance-flow>span,#governance-flow>i{align-self:center!important;transform:rotate(90deg)}
}
""",
    "assets/crdpi-loss.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 340px){
  .chain{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;min-width:0!important;overflow:visible!important;gap:8px!important}
  .chain-node{width:100%!important;max-width:100%!important;min-width:0!important}
  .chain-op{align-self:center!important;transform:rotate(90deg)}
}
""",
    "assets/crdpi-monitoring.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 340px){
  .feature-headlines{display:grid!important;grid-template-columns:minmax(0,1fr)!important;width:100%!important;max-width:100%!important;min-width:0!important}
  .feature-headline{display:grid!important;grid-template-columns:minmax(0,1fr)!important;width:100%!important;max-width:100%!important;min-width:0!important}
  .feature-headline>*{max-width:100%!important;min-width:0!important;overflow-wrap:anywhere!important}
}
""",
    "assets/crdpi-governance.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 800px){
  .evidence-table{width:100%!important;max-width:100%!important;min-width:0!important;table-layout:fixed!important}
  .evidence-table th,.evidence-table td{min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important}
}
@media (max-width: 380px){
  .trail-graph{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;min-width:0!important;overflow:visible!important;gap:8px!important}
  .trail-graph>*{position:static!important;inset:auto!important;transform:none!important;width:100%!important;max-width:100%!important;min-width:0!important}
  .trail-end{width:100%!important;max-width:100%!important;min-width:0!important}
  .release-message{display:block!important;width:100%!important;max-width:100%!important;min-width:0!important}
  .release-message strong{white-space:normal!important;max-width:100%!important;overflow-wrap:anywhere!important;word-break:break-word!important}
}
""",
    "assets/crdpi-architecture.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V2 */
@media (max-width: 800px){
  .arch-hero .hero-grid,.architecture-grid{grid-template-columns:minmax(0,1fr)!important;width:100%!important;max-width:100%!important;min-width:0!important}
  .browser-visual,.component-panel,.component-grid{max-width:100%!important;min-width:0!important}
  .component-panel{width:100%!important}
  .component-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media (max-width: 420px){
  .component-grid{grid-template-columns:minmax(0,1fr)!important}
}
""",
}

PATCHES_V3 = {
    "assets/crdpi-portfolio.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V3 */
@media (max-width: 340px){
  .concentration-table{width:100%!important;max-width:100%!important;min-width:0!important;table-layout:fixed!important}
  .concentration-table th,.concentration-table td{min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important}
}
""",
    "assets/crdpi-loss.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V3 */
@media (max-width: 340px){
  main button{min-width:0!important;max-width:100%!important;white-space:normal!important}
  main table{width:100%!important;max-width:100%!important;min-width:0!important;table-layout:fixed!important}
  main th,main td{min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important}
}
""",
    "assets/crdpi-governance.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V3 */
@media (max-width: 800px){
  .site-nav .top-cta{display:none!important}
  .site-nav .nav-shell{width:calc(100% - 32px)!important;max-width:100%!important;min-width:0!important;gap:12px!important}
}
""",
    "assets/crdpi-architecture.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V3 */
@media (max-width: 800px){
  .site-nav .top-cta{display:none!important}
  .site-nav .nav-shell{width:calc(100% - 32px)!important;max-width:100%!important;min-width:0!important;gap:12px!important}
  .arch-hero .hero-grid{overflow:hidden!important}
  .browser-visual{width:100%!important;max-width:100%!important;min-width:0!important;margin-left:0!important;margin-right:0!important;left:auto!important;right:auto!important;transform:none!important}
}
""",
}

PATCHES_V4 = {
    "assets/crdpi-portfolio.css": r"""
/* BLOCK_F_RESPONSIVE_HARDENING_V4 */
@media (max-width: 340px){
  .risk-table{width:100%!important;max-width:100%!important;min-width:0!important;table-layout:fixed!important}
  .risk-table th,.risk-table td{min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important}
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


def append_patches(patches: dict[str, str], marker: str, label: str) -> int:
    changed = 0
    for rel, block in patches.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if marker in text:
            continue
        path.write_text(text.rstrip() + "\n" + block.strip() + "\n", encoding="utf-8")
        print(f"patched {label}: {rel}")
        changed += 1
    return changed


def patch_claims() -> int:
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
    v1 = append_patches(PATCHES_V1, MARKER_V1, "responsive containment V1")
    v2 = append_patches(PATCHES_V2, MARKER_V2, "responsive containment V2")
    v3 = append_patches(PATCHES_V3, MARKER_V3, "responsive containment V3")
    v4 = append_patches(PATCHES_V4, MARKER_V4, "responsive containment V4")
    claims = patch_claims()
    print(f"Block F remediation complete: v1_files={v1}, v2_files={v2}, v3_files={v3}, v4_files={v4}, claim_replacements={claims}")


if __name__ == "__main__":
    main()
