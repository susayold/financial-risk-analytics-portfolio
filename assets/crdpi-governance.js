(() => {
  const pagePath = "../public/data/page-06-governance.json";
  const taxonomyPath = "../public/data/governance-taxonomy.json";
  const evidencePath = "../public/data/governance-evidence-index.json";
  const $ = (selector) => document.querySelector(selector);
  const make = (tag, className, text) => { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; };
  const titleCase = (value) => value.toLowerCase().replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  const renderStatus = (page) => {
    const s = page.status || page.meta;
    const m = page.monitoring_state;
    const q = page.qa;
    const cards = [
      ["PASS WITH MONITORING", "Block E Closure", "pass"],
      [`${q.e9_passed} / ${q.e9_passed + q.e9_failed}`, "Final QA", "pass"],
      [`${q.e8_passed} / ${q.e8_passed + q.e8_failed}`, "E8 Governance QA", "pass"],
      [q.checksum_integrity, "Checksum Integrity", "pass"],
      [q.public_private_scan, "Public / Private Scan", "pass"],
      [m.current_highest_kri, "Current Highest KRI", "amber"],
      [m.historical_highest_kri, "Historical Highest KRI", "red"],
      [page.change_control.automatic_retraining ? "YES" : "NO", "Automatic Retraining", "neutral"],
    ];
    const root = $("#status-grid");
    cards.forEach(([value, label, tone]) => { const card = make("article", `status-card ${tone}`); card.append(make("span", "label", label)); card.append(make("strong", "", value)); card.append(make("small", "", label === "Block E Closure" ? page.meta.canonical_block_e_release : "Governance contract")); root.append(card); });
  };

  const renderTags = (taxonomy) => {
    const roots = $("#root-causes");
    taxonomy.root_causes.forEach((item) => roots.append(make("span", "tag", titleCase(item))));
    const actions = $("#actions");
    taxonomy.actions.forEach((item) => actions.append(make("span", "tag action", titleCase(item))));
  };

  const renderReleases = (page) => {
    const root = $("#release-lineage");
    page.release_lineage.forEach((release) => {
      const card = make("article", `release-card ${release.current ? "current" : ""}`);
      card.append(make("div", "release-dot", release.tag.replace("block-", "").replace("-v", "\nv")));
      card.append(make("h3", "", release.tag));
      card.append(make("small", "", release.date || "Historical predecessor · date not asserted"));
      card.append(make("em", "", release.current ? "CURRENT" : titleCase(release.type)));
      root.append(card);
    });
  };

  const openDrawer = (row) => {
    const dialog = $("#evidence-drawer");
    const content = $("#drawer-content"); content.replaceChildren();
    const body = make("div", "drawer-body"); body.append(make("h3", "", row.artifact_name));
    const dl = make("dl");
    [["Purpose", row.purpose], ["Stage", row.stage], ["Release", row.release], ["Class", row.public_private_class], ["Status", row.status]].forEach(([label, value]) => { dl.append(make("dt", "", label)); dl.append(make("dd", "", value)); });
    body.append(dl);
    const link = make("a", "drawer-source", "Open canonical source ↗"); link.href = row.public_source; link.target = "_blank"; link.rel = "noreferrer"; body.append(link);
    content.append(body); if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
  };

  const renderEvidence = (rows) => {
    const body = $("#evidence-body");
    rows.forEach((row) => {
      const tr = document.createElement("tr"); tr.tabIndex = 0; tr.setAttribute("aria-label", `Open ${row.artifact_name} evidence details`);
      const cells = [["Evidence", row.artifact_name], ["Purpose", row.purpose], ["Stage", row.stage], ["State", row.status], ["Class", row.public_private_class]];
      cells.forEach(([label, value], index) => { const td = document.createElement("td"); td.dataset.label = label; if (index === 0) { const button = make("button", "", value); button.type = "button"; button.addEventListener("click", () => openDrawer(row)); td.append(button); } else if (index === 4) { td.append(make("span", `class-badge ${row.public_private_class.includes("PRIVATE") ? "private" : ""}`, value)); } else td.textContent = value; tr.append(td); });
      tr.addEventListener("click", (event) => { if (event.target.tagName !== "BUTTON") openDrawer(row); }); tr.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openDrawer(row); } }); body.append(tr);
    });
  };

  const bind = (page) => {
    $("#snapshot-sha").textContent = page.snapshot.sha256;
    $("#copy-hash").addEventListener("click", async () => { const status = $("#copy-status"); try { await navigator.clipboard.writeText(page.snapshot.sha256); status.textContent = "Copied"; } catch { status.textContent = "Select the hash to copy"; } });
    const close = () => { const dialog = $("#evidence-drawer"); if (dialog.open) dialog.close(); else dialog.removeAttribute("open"); };
    $(".drawer-close").addEventListener("click", close); $("#evidence-drawer").addEventListener("click", (event) => { if (event.target === event.currentTarget) close(); });
    const toggle = $(".menu-toggle"); const nav = $(".nav-links"); toggle.addEventListener("click", () => { const open = nav.classList.toggle("open"); toggle.setAttribute("aria-expanded", String(open)); toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation"); });
    renderStatus(page); renderReleases(page);
  };

  Promise.all([fetch(pagePath).then((r) => r.json()), fetch(taxonomyPath).then((r) => r.json()), fetch(evidencePath).then((r) => r.json())]).then(([page, taxonomy, evidence]) => { bind(page); renderTags(taxonomy); renderEvidence(evidence); }).catch((error) => { console.error("Governance data unavailable", error); document.body.dataset.dataError = "true"; });
})();
