(() => {
  const $ = (selector) => document.querySelector(selector);
  const pct = (value, digits = 2) => `${(Number(value) * 100).toFixed(digits)}%`;
  const n = (value) => Number(value).toLocaleString("en-US");
  const esc = (value) => String(value ?? "—").replace(/[&<>\"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]));
  const iconFor = (domain) => domain === "Feature Drift" ? "i-trend" : domain === "Calibration" ? "i-shield" : domain === "Policy Capacity" ? "i-clock" : domain === "Loss / Severity" ? "i-target" : "i-bars";

  function renderSnapshot(page) {
    const c = page.governance_counts;
    const cards = [
      ["AMBER", "Current KRI Status", "Latest closure state", "amber"], ["RED", "Historical Highest", "Calibration slope · 2017-10", "red"], [c.kri_count, "KRIs", "Frozen monitoring contract", "blue"], [c.alert_count, "Alerts", "20 AMBER · 1 RED", "blue"], [c.breach_count, "Breaches", "2 persistence · 1 RED", "amber"], [c.investigation_count, "Investigations", "All alert-linked", "blue"], [c.action_count, "Actions", "Controlled taxonomy", "blue"], ["NO", "Auto Retraining", "Governance review first", "neutral"],
    ];
    $("#snapshot").innerHTML = cards.map((card) => `<article class="snapshot-card ${card[3]}"><b class="snap-value">${card[0]}</b><span class="snap-label">${card[1]}</span><small>${card[2]}</small></article>`).join("");
  }

  function renderDomains(page) {
    const domains = [
      ["Data Quality & Coverage", "GREEN", "12 KRIs", "No governed E2 alert · controlled", "green", "i-shield"],
      ["Feature Drift", "AMBER", "18 KRIs", "3 AMBER findings · 0 RED", "amber", "i-trend"],
      ["Score & Risk Mix", "GREEN", "16 KRIs", `Annual PSI ${page.score_drift.annual_psi.toFixed(4)} · stable`, "green", "i-bars"],
      ["Model Performance & Calibration", "AMBER / RED", "16 KRIs", "Annual AMBER · 2017-10 RED", "mixed", "i-shield"],
      ["Loss / Severity", "GREEN", "14 KRIs", "0 non-GREEN E6 alerts", "green", "i-target"],
      ["Policy Capacity & Concentration", "AMBER", "18 KRIs", "Growth / Balanced watch", "amber", "i-clock"],
    ];
    $("#domains").innerHTML = domains.map((row) => `<article class="domain-card ${row[4]}"><span class="domain-icon"><svg><use href="#${row[5]}"></use></svg></span><h3>${row[0]}</h3><p><b>${row[1]}</b> · ${row[2]}</p><small>${row[3]}</small></article>`).join("");
  }

  function renderFeatures(page) {
    $("#feature-cards").innerHTML = page.feature_drift.map((row) => { const value = row.metric === "MISSINGNESS_SHIFT_PP" ? `+${row.value.toFixed(4)}pp` : row.value.toFixed(6); return `<article class="feature-headline"><div><b>${esc(row.feature)}</b><small>${row.metric === "PSI" ? "PSI · AMBER starts at 0.10" : "Missingness Shift · 2–5pp AMBER"}</small></div><div><strong>${value}</strong><span>AMBER · WATCH</span></div></article>`; }).join("");
    $("#feature-bars").innerHTML = page.feature_drift.map((row) => { const isMissing = row.metric !== "PSI"; const width = isMissing ? Math.min(row.value / 5 * 100, 100) : Math.min(row.value / .25 * 100, 100); const value = isMissing ? `+${row.value.toFixed(4)}pp` : row.value.toFixed(6); return `<div class="feature-row ${isMissing ? "missing" : ""}"><label>${esc(row.feature)}</label><span class="feature-track"><span class="feature-fill" style="width:${width}%"></span></span><strong>${value}<small>${row.severity}</small></strong></div>`; }).join("");
    $("#feature-table").innerHTML = `<table><caption>Feature drift findings</caption><thead><tr><th>Feature</th><th>Metric</th><th>Window</th><th>Observed</th><th>Status</th></tr></thead><tbody>${page.feature_drift.map((row) => `<tr><td>${esc(row.feature)}</td><td>${row.metric}</td><td>${row.window}</td><td>${row.metric === "PSI" ? row.value.toFixed(6) : "+" + row.value.toFixed(4) + "pp"}</td><td>${row.severity}</td></tr>`).join("")}</tbody></table>`;
  }

  function renderScore(page) {
    const monthly = page.score_drift.monthly;
    $("#score-chart").innerHTML = `<div class="score-bars">${monthly.map((row) => `<i class="score-bar" style="--h:${Math.max(row.psi / .25 * 100, 3)}%" title="${row.window}: ${row.psi.toFixed(6)} · ${row.severity}"><label>${row.window.slice(5)}</label></i>`).join("")}</div>`;
    $("#score-table").innerHTML = `<table><caption>2017 monthly score PSI</caption><thead><tr><th>Window</th><th>Sample</th><th>PSI</th><th>Status</th></tr></thead><tbody>${monthly.map((row) => `<tr><td>${row.window}</td><td>${n(row.n)}</td><td>${row.psi.toFixed(6)}</td><td>${row.severity}</td></tr>`).join("")}</tbody></table>`;
  }

  function renderPerformance(page) {
    const q = page.discrimination.quarterly;
    $("#auc-chart").innerHTML = q.map((row) => `<i style="--h:${((row.roc_auc - .7) / .2 * 100).toFixed(1)}%" title="${row.window}: ${row.roc_auc.toFixed(4)}"></i>`).join("");
    const cal = page.calibration.monthly;
    $("#calibration-chart").innerHTML = cal.map((row) => { const status = row.slope > 1.35 || row.slope < .65 ? "red" : row.slope > 1.25 || row.slope < .75 ? "amber" : ""; return `<i class="${status}" style="--h:${Math.max((row.slope - .6) / .8 * 100, 5)}%" title="${row.window}: ${row.slope.toFixed(6)}"><label>${row.window} · ${row.slope.toFixed(4)}</label></i>`; }).join("");
  }

  function renderCapacity(page) {
    $("#capacity").innerHTML = page.policy_capacity.map((row) => { const green = row.severity === "GREEN"; const value = green ? "Within capacity" : `+${row.over_capacity_pp.toFixed(3)}pp`; return `<div class="capacity-item ${green ? "green" : ""}"><span>${row.policy}</span><span class="capacity-track"><i class="capacity-fill" style="width:${green ? 4 : Math.min(row.over_capacity_pp / 2 * 100, 100)}%"></i></span><strong>${value}<small>${row.action}</small></strong></div>`; }).join("");
  }

  let alerts = [];
  function renderAlertTable() {
    const filter = $("#alert-filter").value;
    const filtered = alerts.filter((row) => filter === "ALL" || row.severity === filter || (filter === "E3" && row.source_stage === "E3") || (filter === "E5" && row.source_stage === "E5") || (filter === "E7" && row.source_stage === "E7"));
    const sortSeverity = { RED: 0, AMBER: 1 };
    filtered.sort((a, b) => (sortSeverity[a.severity] - sortSeverity[b.severity]) || a.window.localeCompare(b.window));
    $("#alert-table").innerHTML = `<table><thead><tr><th>Severity</th><th>Domain</th><th>Metric</th><th>Window</th><th>Observed</th><th>Threshold</th><th>Action</th><th>Open</th></tr></thead><tbody>${filtered.map((row) => `<tr><td><span class="severity ${row.severity}">${row.severity}</span></td><td>${row.source_stage === "E3" ? "Feature Drift" : row.source_stage === "E5" ? "Calibration" : "Policy Capacity"}</td><td>${esc(row.metric)}</td><td>${esc(row.window)}</td><td>${row.metric.includes("CAPACITY") ? "+" + row.value.toFixed(3) + "pp" : row.metric.includes("PSI") ? row.value.toFixed(6) : row.value.toFixed(6)}</td><td>${esc(row.threshold)}</td><td>${esc(row.action_type)}</td><td><button class="alert-row-button" data-alert="${row.alert_id}">Details ↗</button></td></tr>`).join("")}</tbody></table>`;
    document.querySelectorAll("[data-alert]").forEach((button) => button.addEventListener("click", () => openDrawer(button.dataset.alert)));
  }

  function openDrawer(id) {
    const row = alerts.find((item) => item.alert_id === id); if (!row) return;
    $("#drawer-content").innerHTML = `<span class="status-pill ${row.severity.toLowerCase()}">${row.severity}</span><h2 class="drawer-title">${esc(row.metric)}</h2><p class="drawer-sub">${esc(row.window)} · ${esc(row.alert_id)}</p><div class="drawer-grid"><div><span>Domain</span><b>${row.source_stage === "E3" ? "Feature Drift" : row.source_stage === "E5" ? "Calibration" : "Policy Capacity"}</b></div><div><span>Observed</span><b>${row.value.toFixed(6)}</b></div><div><span>Threshold</span><b>${esc(row.threshold)}</b></div><div><span>Persistence</span><b>${row.persistence_count || "1 / standard"}</b></div><div><span>Investigation</span><b>${row.investigation_id}</b></div><div><span>Action</span><b>${row.action_type}</b></div><div><span>Model change required?</span><b>NO</b></div><div><span>Production change required?</span><b>NO</b></div></div><p class="panel-note">Every non-GREEN signal is retained as governed work. A breach is an escalation state, not a replacement for the investigation/action link.</p>`;
    $("#alert-drawer").showModal();
  }

  function setupUI() {
    $(".menu-toggle").addEventListener("click", () => { const nav = $(".nav-links"); const open = nav.classList.toggle("open"); $(".menu-toggle").setAttribute("aria-expanded", String(open)); });
    $("#alert-filter").addEventListener("change", renderAlertTable);
    $(".drawer-close").addEventListener("click", () => $("#alert-drawer").close());
    $("#alert-drawer").addEventListener("click", (event) => { if (event.target === $("#alert-drawer")) $("#alert-drawer").close(); });
  }

  Promise.all([fetch("../public/data/page-05-monitoring.json").then((response) => response.json()), fetch("../public/data/monitoring-alerts.json").then((response) => response.json())])
    .then(([page, alertPayload]) => { alerts = alertPayload.alerts; renderSnapshot(page); renderDomains(page); renderFeatures(page); renderScore(page); renderPerformance(page); renderCapacity(page); renderAlertTable(); setupUI(); })
    .catch((error) => { console.error(error); document.querySelector("#main").insertAdjacentHTML("afterbegin", "<p class=\"method-note\">The public monitoring contract could not be loaded.</p>"); });
})();
