(() => {
  const DATA_URL = "../public/data/page-02-portfolio-risk.json";
  const root = document;
  const byId = (id) => root.getElementById(id);
  const valueAt = (obj, path) => path.split(".").reduce((value, key) => value?.[key], obj);
  const fmt = (value, format = "text") => {
    if (value === null || value === undefined) return "—";
    if (format === "integer") return Number(value).toLocaleString("en-US");
    if (format === "compact") {
      const n = Number(value);
      if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
      if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
      if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
      return n.toLocaleString("en-US");
    }
    if (format === "currencyCompact") {
      const n = Number(value);
      if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
      if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
      return `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
    }
    if (format === "percent") return `${(Number(value) * 100).toFixed(2)}%`;
    if (format === "multiple") return `${Number(value).toFixed(2)}×`;
    return String(value);
  };
  const clean = (label) => String(label).replaceAll("_", " ").replace(/\b\w/g, (m) => m.toUpperCase());
  const setText = (node, text) => { node.textContent = text; };

  function bindData(data) {
    root.querySelectorAll("[data-bind]").forEach((node) => {
      setText(node, fmt(valueAt(data, node.dataset.bind), node.dataset.format));
    });
    root.querySelectorAll("[data-width]").forEach((node) => {
      const share = Number(valueAt(data, node.dataset.width));
      node.style.width = `${Math.max(4, Math.min(96, share * 100))}%`;
    });
  }

  function renderFico(data) {
    const rows = data.segment_explorer.rows.filter((row) => row.dimension === "fico_band").sort((a, b) => a.segment.localeCompare(b.segment));
    const chart = byId("fico-bars");
    chart.innerHTML = "";
    const labels = document.createElement("div");
    labels.className = "bar-labels";
    const maxAccounts = Math.max(...rows.map((row) => row.accounts));
    rows.forEach((row) => {
      const pair = document.createElement("div"); pair.className = "bar-pair";
      const good = document.createElement("i"); good.className = "good-bar";
      const bad = document.createElement("i"); bad.className = "bad-bar";
      good.style.setProperty("--good", `${(row.accounts * (1 - row.bad_rate) / maxAccounts) * 100}%`);
      bad.style.setProperty("--bad", `${(row.accounts * row.bad_rate / maxAccounts) * 100}%`);
      pair.append(good, bad); chart.append(pair);
      const label = document.createElement("span"); label.textContent = row.segment.replace("–", "-"); labels.append(label);
    });
    chart.after(labels);
  }

  const segmentValue = (row, metric) => metric === "bad_rate" ? row.bad_rate : row[metric];
  function renderSegmentExplorer(data) {
    const select = byId("dimension-select");
    data.segment_explorer.dimensions.forEach((dimension) => {
      const option = document.createElement("option"); option.value = dimension; option.textContent = clean(dimension); select.append(option);
    });
    const render = () => {
      const dimension = select.value;
      const metric = byId("metric-select").value;
      const headlineOnly = byId("headline-only").checked;
      let rows = data.segment_explorer.rows.filter((row) => dimension === "All Dimensions" || row.dimension === dimension);
      if (headlineOnly) rows = rows.filter((row) => row.headline_eligible);
      rows.sort((a, b) => segmentValue(b, metric) - segmentValue(a, metric));
      rows = rows.slice(0, 8);
      const max = Math.max(...rows.map((row) => segmentValue(row, metric)), 0.01);
      const target = byId("segment-rows"); target.innerHTML = "";
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        const segment = document.createElement("td"); segment.textContent = `${clean(row.dimension)} · ${row.segment}`;
        const rate = document.createElement("td"); rate.className = "rate-cell";
        const rateValue = document.createElement("span"); rateValue.className = "rate-value"; rateValue.textContent = fmt(row.bad_rate, "percent");
        const rateBar = document.createElement("span"); rateBar.className = "rate-bar"; const fill = document.createElement("i"); fill.style.width = `${Math.max(6, segmentValue(row, metric) / max * 100)}%`; rateBar.append(fill); rate.append(rateValue, rateBar);
        const accounts = document.createElement("td"); accounts.textContent = fmt(row.accounts, "integer");
        const relative = document.createElement("td"); relative.textContent = fmt(row.relative_bad_rate, "multiple");
        const share = document.createElement("td"); share.textContent = fmt(row.bad_associated_share, "percent");
        tr.append(segment, rate, accounts, relative, share); target.append(tr);
      });
      const insights = byId("insight-cards"); insights.innerHTML = "";
      data.headline_segment_risk.forEach((row) => {
        const card = document.createElement("div"); card.className = "insight-card";
        const title = document.createElement("b"); title.textContent = `${clean(row.dimension)} · ${row.segment}`;
        const copy = document.createElement("span"); copy.textContent = `${fmt(row.relative_bad_rate, "multiple")} baseline · ${fmt(row.bad_associated_share, "percent")} BAD-associated share`;
        const value = document.createElement("strong"); value.textContent = fmt(row.bad_rate, "percent"); card.append(title, copy, value); insights.append(card);
      });
    };
    [select, byId("metric-select"), byId("headline-only")].forEach((control) => control.addEventListener("change", render));
    render();
  }

  function renderMateriality(data) {
    const field = byId("bubble-field");
    data.materiality.top_segments.slice(0, 8).forEach((row, index) => {
      const bubble = document.createElement("span"); bubble.className = "bubble";
      const x = Math.min(88, Math.max(8, row.bad_associated_share * 100));
      const y = Math.min(82, Math.max(10, (row.relative_bad_rate - .75) / .55 * 100));
      bubble.style.left = `${x}%`; bubble.style.bottom = `${y}%`; bubble.style.setProperty("--size", `${index < 3 ? 25 : 19}px`);
      bubble.title = `${row.segment}: ${fmt(row.bad_rate, "percent")} BAD rate; ${fmt(row.bad_associated_share, "percent")} BAD-associated share`;
      bubble.textContent = index < 4 ? row.segment.split(" ")[0] : ""; field.append(bubble);
    });
  }

  function renderConcentration(data) {
    const rows = data.materiality.top_segments.slice(); let sortKey = "rank"; let ascending = true;
    const render = () => {
      rows.sort((a, b) => {
        const av = sortKey === "rank" ? a.materiality_rank : a[sortKey]; const bv = sortKey === "rank" ? b.materiality_rank : b[sortKey];
        return (typeof av === "string" ? av.localeCompare(bv) : av - bv) * (ascending ? 1 : -1);
      });
      const target = byId("concentration-rows"); target.innerHTML = "";
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        [row.materiality_rank, row.segment, `${clean(row.dimension)}`, fmt(row.accounts, "integer"), fmt(row.bad_rate, "percent"), fmt(row.bad_associated_share, "percent")].forEach((value) => { const td = document.createElement("td"); td.textContent = value; tr.append(td); }); target.append(tr);
      });
    };
    root.querySelectorAll(".concentration-table th[data-sort]").forEach((header) => header.addEventListener("click", () => { const key = header.dataset.sort; ascending = key === sortKey ? !ascending : key !== "bad_rate" && key !== "bad_associated_share"; sortKey = key; render(); }));
    render();
    const contrast = byId("contrast-cards");
    data.materiality.contrast.forEach((row) => { const card = document.createElement("div"); card.className = "contrast-card"; card.innerHTML = `<div><b>${clean(row.dimension)} · ${row.segment}</b><strong>${fmt(row.bad_rate, "percent")}</strong></div><small>BAD rate &nbsp;·&nbsp; <b>${fmt(row.bad_associated_share, "percent")}</b> BAD-associated share</small>`; contrast.append(card); });
  }

  function renderVintage(data) {
    const target = byId("split-cards");
    data.splits.forEach((row) => { const card = document.createElement("article"); card.className = `split-card${row.label === "Historical Shadow" ? " shadow" : ""}`; card.innerHTML = `<span class="split-code">${row.label}</span><strong>${fmt(row.accounts, "integer")}</strong><b>${fmt(row.bad_rate, "percent")}</b><p>${row.min_issue_d} → ${row.max_issue_d}</p><small>${fmt(row.issue_cohorts, "integer")} issue cohorts</small>`; target.append(card); });
    const chart = byId("annual-bars"); const max = Math.max(...data.annual.map((row) => row.accounts));
    data.annual.forEach((row) => { const wrapper = document.createElement("div"); wrapper.className = "annual-year"; const bar = document.createElement("i"); bar.style.height = `${Math.max(3, row.accounts / max * 100)}%`; const year = document.createElement("span"); year.textContent = row.issue_year; wrapper.append(bar, year); chart.append(wrapper); });
    const svg = byId("annual-line"); const maxRate = Math.max(...data.annual.map((row) => row.bad_rate)); const points = data.annual.map((row, index) => `${(index / (data.annual.length - 1)) * 900},${210 - (row.bad_rate / maxRate) * 180}`).join(" "); svg.querySelector("path").setAttribute("d", `M ${points.replaceAll(" ", " L ")}`);
  }

  function renderGovernance(data) {
    const flow = byId("governance-flow");
    data.governance.flow.forEach((label, index) => { const node = document.createElement("div"); node.className = "flow-node"; const icon = document.createElement("span"); icon.className = "flow-icon"; icon.innerHTML = `<svg><use href="#${index === 0 ? "i-database" : index === 1 ? "i-layers" : index >= 2 && index <= 6 ? "i-bars" : "i-shield"}"/></svg>`; const name = document.createElement("b"); name.textContent = label; const small = document.createElement("small"); small.textContent = index === 2 ? "1 account / row" : index > 2 ? "aggregate evidence" : "governed source"; node.append(icon, name, small); flow.append(node); });
  }

  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      bindData(data); renderFico(data); renderSegmentExplorer(data); renderMateriality(data); renderConcentration(data); renderVintage(data); renderGovernance(data);
    } catch (error) {
      root.body.dataset.dataError = "true";
      console.error("Page 02 data contract failed to load", error);
    }
  }
  const menu = document.querySelector(".menu-toggle"); const nav = document.querySelector(".nav-links");
  menu?.addEventListener("click", () => { const open = menu.getAttribute("aria-expanded") === "true"; menu.setAttribute("aria-expanded", String(!open)); nav.classList.toggle("open", !open); });
  init();
})();
