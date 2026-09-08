(() => {
  const dataUrl = "../public/data/page-07-architecture.json";
  const $ = (selector) => document.querySelector(selector);
  const make = (tag, className, text) => { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; };
  const question = [
    "What is CRD.PI and what does it demonstrate?", "Where is observed portfolio risk concentrated?", "Can the frozen model rank historical OOT risk credibly?", "What does risk ranking mean for loss, policy and stress?", "What changed and what requires attention?", "Can a reviewer trace signal → action → release?", "How is governed evidence delivered safely?",
  ];
  const projectBase = new URL("../", window.location.href);
  const resolveProjectRoute = (route) => route === "/" ? projectBase.href : new URL(route.replace(/^\/+/, ""), projectBase).href;
  const renderPages = (pages, deliveryStatus) => {
    const root = $("#page-cards");
    pages.forEach((page, index) => {
      const current = page.number === 7;
      const delivered = deliveryStatus === "DELIVERED";
      const card = make("article", `page-card ${current ? "current" : ""}`);
      card.append(make("div", "number", String(page.number).padStart(2, "0")));
      card.append(make("h3", "", page.name));
      card.append(make("p", "", question[index]));
      card.append(make("small", "", page.route + " · " + page.data_contract));
      const statusClass = current && !delivered ? "in-progress" : "live";
      const statusText = current && !delivered ? "IN PROGRESS" : "LIVE";
      card.append(make("span", statusClass, statusText));
      const link = make("a", "card-link", current ? "Current page" : "Open page ↗");
      link.href = resolveProjectRoute(page.route);
      card.append(link);
      root.append(card);
    });
  };
  const renderTech = (items) => { const root = $("#tech-stack"); items.forEach((item) => { const row = make("div", "tech-item"); row.append(make("b", "", item.layer)); row.append(make("span", "", item.technology)); row.append(make("em", item.status === "IMPLEMENTED" ? "impl" : "", item.status)); root.append(row); }); };
  const renderQa = (qa) => { const root = $("#qa-gates"); Object.entries(qa).forEach(([name, status]) => { const row = make("div", "qa-item"); row.append(make("i", "", status === "PASS" ? "✓" : "·")); row.append(make("span", "", name.replace(/_/g, " "))); row.append(make("em", "", status)); root.append(row); }); };
  const bindMenu = () => { const toggle = $(".menu-toggle"); const nav = $(".nav-links"); toggle.addEventListener("click", () => { const open = nav.classList.toggle("open"); toggle.setAttribute("aria-expanded", String(open)); toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation"); }); };
  fetch(dataUrl).then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then((page) => {
    renderPages(page.pages, page.meta.status);
    renderTech(page.technology_stack);
    renderQa(page.block_f_qa);
    bindMenu();
    $("#scorecard").querySelector(".featured strong").textContent = page.meta.status.replace(/_/g, " ");
    $("#scorecard").querySelector(".featured small").textContent = "Page 07 · delivery state";
  }).catch((error) => { console.error("Architecture data unavailable", error); document.body.dataset.dataError = "true"; const root = $("#page-cards"); root.replaceChildren(make("p", "static-contract", "Architecture data is not available in this build.")); bindMenu(); });
})();
