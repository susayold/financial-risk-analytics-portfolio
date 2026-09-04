(() => {
  const DATA_URL = "../public/data/page-03-model-decisioning.json";
  const FEATURE_URL = "../public/data/model-feature-contract-79f.json";
  const doc = document;
  const $ = (id) => doc.getElementById(id);
  const get = (object, path) => path.split(".").reduce((value, key) => value?.[key], object);
  const icon = (name) => `<svg><use href="#i-${name}"/></svg>`;
  const format = (value, kind = "text") => {
    if (value === undefined || value === null) return "—";
    const n = Number(value);
    if (kind === "integer") return n.toLocaleString("en-US");
    if (kind === "percent") return `${(n * 100).toFixed(2)}%`;
    if (kind === "decimal4") return n.toFixed(4);
    if (kind === "pp") return `${(n * 100).toFixed(2)}pp`;
    return String(value);
  };
  function bind(data) {
    doc.querySelectorAll("[data-bind]").forEach((node) => { node.textContent = format(get(data, node.dataset.bind), node.dataset.format); });
  }
  function renderSplits(data) {
    const target = $("split-grid");
    data.population.splits.forEach((split, index) => {
      const card = doc.createElement("article"); card.className = "split-card";
      card.innerHTML = `<span class="code">${split.split}</span><h3>${format(split.rows, "integer")}<small>accounts</small></h3><div class="split-metrics"><div><b>${format(split.bad, "integer")}</b><span>BAD</span></div><div><b>${format(split.bad_rate, "percent")}</b><span>BAD rate</span></div>${split.roc_auc ? `<div><b>${format(split.roc_auc, "decimal4")}</b><span>ROC-AUC</span></div>` : ""}</div><p>${split.role}</p>`;
      target.append(card);
    });
  }
  function renderMetrics(data) {
    const target = $("metric-grid");
    const cards = [["roc_auc", "ROC-AUC", "Ranking discrimination", "bars"], ["gini", "Gini", "Rank separation", "target"], ["ks", "KS", "Maximum separation", "nodes"], ["pr_auc", "PR-AUC", "Precision-recall", "trend"], ["brier", "Brier", "Probabilistic error", "amount", true], ["log_loss", "Log Loss", "Probabilistic error", "doc", true]];
    cards.forEach(([key, label, note, symbol, error]) => { const card = doc.createElement("article"); card.className = `metric-card${error ? " error" : ""}`; card.innerHTML = `<div class="metric-icon">${icon(symbol)}</div><strong>${format(data.oot[key], "decimal4")}</strong><h3>${label}</h3><p>${note}</p>`; target.append(card); });
  }
  function renderBands(data) {
    const target = $("band-grid");
    data.decisioning.risk_bands.forEach((value) => { const parts = value.split(" "); const card = doc.createElement("article"); card.className = "band-card"; card.innerHTML = `<span>${parts[0]}</span><b>${parts.slice(1).join(" ")}</b><small>Reporting label</small>`; target.append(card); });
  }
  function renderFeatures(data) {
    const target = $("feature-groups");
    data.feature_groups.forEach((group) => { const card = doc.createElement("article"); card.className = "feature-group"; const exception = group.id === "D" ? `<small class="exception">Versioned role exception</small>` : ""; card.innerHTML = `<span class="group-id">${group.id}</span><strong>${group.count}</strong><h3>${group.name}</h3><p>${group.features.join(" · ")} …</p>${exception}`; target.append(card); });
  }
  function renderDrawer(featureData) {
    const target = $("drawer-grid"); target.innerHTML = "";
    featureData.features.forEach((feature) => { const item = doc.createElement("div"); item.className = `drawer-item${feature.role_exception ? " exception" : ""}`; const index = doc.createElement("b"); index.textContent = String(feature.canonical_index).padStart(2, "0"); const name = doc.createElement("span"); name.textContent = feature.name; item.append(index, name); target.append(item); });
  }
  function renderReplay(data) {
    const target = $("replay-grid");
    const values = [["79/79", "Frozen features recovered", "layers"], [format(data.reproducibility.scored_rows, "integer"), "Unique scored accounts reconciled", "database"], [`${format(data.reproducibility.oot_replay_rows, "integer")} / ${format(data.reproducibility.oot_replay_rows, "integer")}`, "OOT rows replay matched", "target"], [format(data.reproducibility.oot_replay_max_abs_diff, "decimal4"), "Max OOT prediction difference", "shield"], [format(data.reproducibility.oot_replay_spearman, "decimal4"), "Replay Spearman", "bars"]];
    values.forEach(([value, label, symbol]) => { const card = doc.createElement("article"); card.className = "replay-card"; card.innerHTML = `${icon(symbol)}<strong>${value}</strong><span>${label}</span>`; target.append(card); });
  }
  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" }); if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json(); bind(data); renderSplits(data); renderMetrics(data); renderBands(data); renderFeatures(data); renderReplay(data);
      const open = $("open-features"); const close = $("close-features"); const drawer = $("feature-drawer"); let featurePromise;
      open.addEventListener("click", async () => { const expanded = open.getAttribute("aria-expanded") === "true"; open.setAttribute("aria-expanded", String(!expanded)); drawer.hidden = expanded; if (!expanded) { featurePromise ||= fetch(FEATURE_URL, { cache: "no-store" }).then((res) => res.json()); renderDrawer(await featurePromise); close.focus(); } });
      close.addEventListener("click", () => { drawer.hidden = true; open.setAttribute("aria-expanded", "false"); open.focus(); });
      doc.addEventListener("keydown", (event) => { if (event.key === "Escape" && !drawer.hidden) { drawer.hidden = true; open.setAttribute("aria-expanded", "false"); open.focus(); } });
    } catch (error) { doc.body.dataset.dataError = "true"; console.error("Page 03 data contract failed to load", error); }
  }
  const menu = doc.querySelector(".menu-toggle"); const nav = doc.querySelector(".nav-links"); menu?.addEventListener("click", () => { const open = menu.getAttribute("aria-expanded") === "true"; menu.setAttribute("aria-expanded", String(!open)); nav.classList.toggle("open", !open); });
  init();
})();
