(() => {
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) => String(value).replace(/[&<>\"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]));
  const pct = (value, digits = 2) => `${(Number(value) * 100).toFixed(digits)}%`;
  const money = (value, digits = 2) => {
    const n = Number(value);
    if (Math.abs(n) >= 1e9) return `$${(n / 1e9).toFixed(digits)}B`;
    if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(digits)}M`;
    return `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
  };
  const pp = (value) => `${value >= 0 ? "+" : ""}${(Number(value) * 100).toFixed(2)}pp`;
  const short = (value) => Number(value).toLocaleString("en-US");

  function renderCentral(page) {
    const c = page.central_case;
    const cards = [
      ["i-people", short(c.accounts), "Scored Accounts", "Matched scored analytical population"],
      ["i-bars", pct(c.mean_p_bad_final), "Mean Risk Score", "Mean p_bad_final"],
      ["i-shield", pct(c.lgd), "Central LGD Proxy", "LGD_CENTRAL_Q50"],
      ["i-database", money(c.ead_proxy), "Origination EAD Proxy", "EAD_0M"],
      ["i-target", money(c.expected_loss_proxy), "Expected-Loss Proxy", "Analytical expected loss"],
      ["i-trend", pct(c.el_rate), "Portfolio EL Rate", "Central Q50 severity case"],
    ];
    $("#central-kpis").innerHTML = cards.map((card) => `<article class="kpi"><span class="kpi-icon"><svg><use href="#${card[0]}"></use></svg></span><b class="kpi-value">${card[1]}</b><span class="kpi-label">${card[2]}</span><small class="kpi-note">${card[3]}</small></article>`).join("");
  }

  function renderSensitivity(page) {
    const labels = { Q25_LOW_SEVERITY: "Q25", Q50_CENTRAL: "Q50", Q75_ADVERSE: "Q75", Q90_SEVERE: "Q90" };
    const lgd = page.lgd_sensitivity;
    const maxRate = Math.max(...lgd.map((row) => row.el_rate));
    $("#lgd-bars").innerHTML = lgd.map((row) => `<div class="h-bar"><span class="h-label">${labels[row.scenario]}</span><span class="bar-track"><span class="bar-fill" style="width:${(row.el_rate / maxRate * 100).toFixed(1)}%"></span></span><span class="bar-value">${pct(row.el_rate)}<small>${pct(row.lgd)} LGD · ${money(row.el_proxy)}</small></span></div>`).join("");
    $("#lgd-table").innerHTML = `<table><caption>LGD sensitivity values</caption><thead><tr><th>Scenario</th><th>LGD</th><th>EL Proxy</th><th>EL Rate</th></tr></thead><tbody>${lgd.map((row) => `<tr><td>${labels[row.scenario]}</td><td>${pct(row.lgd, 2)}</td><td>${money(row.el_proxy)}</td><td>${pct(row.el_rate, 2)}</td></tr>`).join("")}</tbody></table>`;
    const ead = page.ead_timing;
    const maxEad = Math.max(...ead.map((row) => row.ead_proxy));
    $("#ead-bars").innerHTML = ead.map((row) => `<div class="ead-bar"><span class="ead-label">${row.timing}</span><span class="bar-track"><span class="bar-fill" style="width:${(row.ead_proxy / maxEad * 100).toFixed(1)}%"></span></span><span class="bar-value">${money(row.ead_proxy)}<small>EL ${money(row.el_proxy_q50)} · ${pct(row.el_rate_q50)}</small></span></div>`).join("");
    $("#ead-table").innerHTML = `<table><caption>EAD timing sensitivity values</caption><thead><tr><th>Timing</th><th>EAD Proxy</th><th>EL Proxy</th><th>EL Rate</th></tr></thead><tbody>${ead.map((row) => `<tr><td>${row.timing}</td><td>${money(row.ead_proxy)}</td><td>${money(row.el_proxy_q50)}</td><td>${pct(row.el_rate_q50)}</td></tr>`).join("")}</tbody></table>`;
  }

  function routeBar(policy, source, mode) {
    const values = mode === "accounts" ? [source.approved_accounts, source.review_accounts, source.declined_accounts] : [source.approved_ead, source.review_ead, source.declined_ead];
    const total = values.reduce((sum, value) => sum + Number(value), 0);
    const labels = mode === "accounts" ? values.map(short) : values.map(money);
    return `<div class="route-row"><span class="route-name">${policy.scenario}</span><span class="route-stack"><span class="approve" style="width:${source.approval_rate * 100}%">Approve ${pct(source.approval_rate)}</span><span class="review" style="width:${source.review_rate * 100}%">Review ${pct(source.review_rate)}</span><span class="decline" style="width:${source.decline_rate * 100}%">Decline ${pct(source.decline_rate)}</span></span><span class="route-total">${labels[0]} / ${labels[1]} / ${labels[2]}<br>${mode === "accounts" ? short(total) + " accounts" : money(total)}</span></div>`;
  }

  let policyData;
  let routeMode = "accounts";
  function renderPolicy(page, selected = "BALANCED") {
    policyData = page.policies.find((row) => row.scenario === selected) || page.policies[1];
    document.querySelectorAll("[data-policy]").forEach((button) => button.setAttribute("aria-selected", String(button.dataset.policy === policyData.scenario)));
    const v = policyData.validation;
    const o = policyData.oot;
    const metric = (value, label) => `<div class="policy-metric"><b>${value}</b><span>${label}</span></div>`;
    $("#policy-detail").innerHTML = `<article class="policy-card"><h3>Validation Contract</h3><p>${esc(v.basis)} · ${esc(v.selection_rule)}</p><div class="policy-metrics">${metric(pct(v.approval_rate), "Approve")}${metric(pct(v.review_rate), "Review")}${metric(pct(v.decline_rate), "Decline")}${metric(pct(v.approved_el_rate), "Approved EL rate")}${metric(pct(v.bad_capture_rate), "BAD capture")}</div><div class="route-mini"><span class="approve" style="width:${v.approval_rate * 100}%">Approve</span><span class="review" style="width:${v.review_rate * 100}%">Review</span><span class="decline" style="width:${v.decline_rate * 100}%">Decline</span></div><div class="cutoff-note">Frozen approve cutoff <b>${Number(v.approve_cutoff).toFixed(4)}</b> · decline cutoff <b>${Number(v.decline_cutoff).toFixed(4)}</b></div></article><article class="policy-card oot"><h3>OOT Replay · 2017</h3><p>Historical policy simulation · unchanged thresholds</p><div class="policy-metrics">${metric(pct(o.approval_rate), "Approve")}${metric(pct(o.review_rate), "Review")}${metric(pct(o.decline_rate), "Decline")}${metric(pct(o.approved_bad_rate), "Approved BAD")}${metric(pct(o.bad_capture_rate), "BAD capture")}${metric(pct(o.good_route_out_rate), "GOOD route-out")}</div><div class="route-mini"><span class="approve" style="width:${o.approval_rate * 100}%">Approve</span><span class="review" style="width:${o.review_rate * 100}%">Review</span><span class="decline" style="width:${o.decline_rate * 100}%">Decline</span></div><div class="cutoff-note"><b>${money(o.approved_ead)}</b> approved EAD · <b>${money(o.approved_el_proxy)}</b> approved EL · ${pct(o.approved_el_rate)} approved EL rate</div></article>`;
  }

  function renderRoutes(page) {
    $("#route-bars").innerHTML = page.policies.map((policy) => routeBar(policy, policy.oot, routeMode)).join("");
    const rows = page.policies.map((policy) => { const o = policy.oot; return `<tr><td>${policy.scenario}</td><td>${pct(o.approval_rate)}</td><td>${pct(o.review_rate)}</td><td>${pct(o.decline_rate)}</td><td>${pct(o.bad_capture_rate)}</td><td>${pct(o.good_route_out_rate)}</td></tr>`; }).join("");
    $("#replay-table").innerHTML = `<table><caption>OOT policy replay route metrics</caption><thead><tr><th>Policy</th><th>Approve</th><th>Review</th><th>Decline</th><th>BAD capture</th><th>GOOD route-out</th></tr></thead><tbody>${rows}</tbody></table>`;
  }

  function renderFrontier(page) {
    const colors = { GROWTH: "#2166f3", BALANCED: "#6d3cff", CONSERVATIVE: "#0b9b70" };
    const maxEad = Math.max(...page.policies.map((p) => p.oot.approved_ead));
    $("#frontier-points").innerHTML = page.policies.map((policy) => { const o = policy.oot; const size = 18 + Math.sqrt(o.approved_ead / maxEad) * 20; const x = 11 + o.approval_rate * 78; const y = 17 + o.bad_capture_rate * 68; return `<span class="frontier-point" style="left:${x}%;bottom:${y}%;--size:${size}px;--point:${colors[policy.scenario]}"><b>${policy.scenario}</b></span>`; }).join("");
    $("#frontier-legend").innerHTML = page.policies.map((policy) => `<div class="legend-item"><i class="legend-dot" style="--point:${colors[policy.scenario]}"></i>${policy.scenario} · ${pct(policy.oot.good_route_out_rate)} GOOD route-out</div>`).join("");
  }

  function renderPricing(page) {
    const pricing = page.pricing.diagnostics;
    const maxRate = Math.max(...pricing.map((row) => row.mean_rate));
    $("#pricing-bars").innerHTML = `<div class="pricing-bars">${pricing.map((row) => `<div class="price-row"><span class="price-label">${esc(row.label.split(" ")[0])}</span><span class="price-track"><i class="price-line rate" style="height:${row.mean_rate / maxRate * 92}%"></i><i class="price-line el" style="height:${row.mean_el_rate / maxRate * 92}%"></i></span><span class="price-values"><b>Rate ${pct(row.mean_rate)}</b>EL ${pct(row.mean_el_rate)}<br>${pp(row.diagnostic_spread)}</span></div>`).join("")}<div class="price-legend"><span><i class="rate-key"></i>Observed Interest Rate</span><span><i class="el-key"></i>Analytical EL Rate</span></div></div>`;
    $("#pricing-table").innerHTML = `<table><caption>Descriptive pricing diagnostics</caption><thead><tr><th>Risk</th><th>Accounts</th><th>Observed rate</th><th>Analytical EL</th><th>Spread</th></tr></thead><tbody>${pricing.map((row) => `<tr><td>${esc(row.label)}</td><td>${short(row.accounts)}</td><td>${pct(row.mean_rate)}</td><td>${pct(row.mean_el_rate)}</td><td>${pp(row.diagnostic_spread)}</td></tr>`).join("")}</tbody></table>`;
  }

  function renderStress(page) {
    const classes = { BASE: "base", MILD: "mild", ADVERSE: "adverse", SEVERE: "severe" };
    $("#stress-cards").innerHTML = page.stress.map((row) => `<article class="stress-card ${classes[row.scenario]}"><h3>${row.scenario}</h3><b>${pct(row.el_rate)}</b><span>Portfolio EL Rate</span><small>Risk ${pct(row.mean_p_bad)} · LGD ${pct(row.lgd)}<br><strong>${money(row.el_proxy)}</strong> EL proxy${row.delta_vs_base_el_rate ? ` · ${pp(row.delta_vs_base_el_rate)} vs Base` : ""}</small></article>`).join("");
    const max = Math.max(...page.stress.map((row) => row.el_rate));
    $("#stress-bars").innerHTML = page.stress.map((row) => `<div class="stress-row"><span class="stress-name">${row.scenario}</span><span class="stress-track"><span class="stress-fill" style="width:${row.el_rate / max * 100}%"></span></span><span class="stress-value"><b>${pct(row.el_rate)}</b><br>${money(row.el_proxy)}</span></div>`).join("");
    $("#stress-table").innerHTML = `<table><caption>Stress scenario values</caption><thead><tr><th>Scenario</th><th>Mean risk</th><th>LGD</th><th>EL Proxy</th><th>EL Rate</th></tr></thead><tbody>${page.stress.map((row) => `<tr><td>${row.scenario}</td><td>${pct(row.mean_p_bad)}</td><td>${pct(row.lgd)}</td><td>${money(row.el_proxy)}</td><td>${pct(row.el_rate)}</td></tr>`).join("")}</tbody></table>`;
  }

  function renderReverse(page) {
    const labels = { A: "ADVERSE EL equivalent", B: "SEVERE EL equivalent" };
    $("#reverse-cards").innerHTML = page.reverse_stress.map((row) => `<article class="reverse-card"><h3>${labels[row.id]}</h3><p>${esc(row.question)}</p><div class="reverse-metrics"><div><b>${pct(row.required_mean_p_bad)}</b><span>Required mean risk score</span></div><div><b>${pct(row.relative_mean_p_increase)}</b><span>Relative increase vs Base</span></div><div><b>${pct(row.target_el_rate)}</b><span>Target EL rate</span></div></div></article>`).join("");
  }

  function setupNav() {
    const toggle = $(".menu-toggle");
    toggle.addEventListener("click", () => { const nav = $(".nav-links"); const open = nav.classList.toggle("open"); toggle.setAttribute("aria-expanded", String(open)); });
  }

  fetch("../public/data/page-04-loss-policy-stress.json")
    .then((response) => { if (!response.ok) throw new Error("Page 04 public contract unavailable"); return response.json(); })
    .then((page) => {
      renderCentral(page); renderSensitivity(page); renderPolicy(page); renderRoutes(page); renderFrontier(page); renderPricing(page); renderStress(page); renderReverse(page); setupNav();
      document.querySelectorAll("[data-policy]").forEach((button) => button.addEventListener("click", () => { renderPolicy(page, button.dataset.policy); }));
      document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => { routeMode = button.dataset.view; document.querySelectorAll("[data-view]").forEach((item) => item.classList.toggle("active", item === button)); renderRoutes(page); }));
    })
    .catch((error) => { document.querySelectorAll("[id$='-kpis'],[id$='-bars'],[id$='-cards'],#policy-detail,#route-bars,#frontier-points,#pricing-bars,#stress-bars,#reverse-cards").forEach((node) => { node.innerHTML = `<p class="trust-note">Unable to load the public analytical contract.</p>`; }); console.error(error); });
})();
