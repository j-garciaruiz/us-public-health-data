/* County atlas: measured vs expected, with reliability-aware smoothing. */
(function () {
  "use strict";
  const IDX = window.ATLAS_INDEX;
  const OUT = Object.fromEntries(IDX.outcomes.map((o) => [o.id, o]));
  const COUNTY = IDX.counties;
  const POS = Object.fromEntries(COUNTY.map((c, i) => [c.fips, i]));
  const LAYER_ORDER = ["mortality", "medicare_actual", "acs", "medicare_std"];
  const LAYER_LABEL = {
    mortality: "Deaths (CDC WONDER, 2018-2024)",
    medicare_actual: "Medicare claims (2023)",
    acs: "Disability, Census survey (2019-2023)",
    medicare_std: "Medicare claims, age-standardized (2023)",
  };
  const CAVEAT = {
    mortality: "Underlying cause from death certificates, which differ in how causes are recorded. An index of 100 means national age-specific death rates applied to the county's age mix; a difference of zero means the measured and predicted indices match. Values exist only for counties with 10 or more deaths (NCHS rule).",
    medicare_actual: "Recorded diagnoses reflect access to care and coding as well as disease. Covers Original Medicare only; the model adjusts for each county's Medicare Advantage share.",
    medicare_std: "Recorded diagnoses, age-standardized by CMS. The extract used here lacks the age-specific inputs needed to estimate uncertainty, so reliability is not estimated and differences are not smoothed. The prediction model includes Medicare Advantage share.",
    acs: "Self-reported difficulty from the Census survey. Small counties have wide margins of error, which the smoothing takes into account.",
  };
  const TIER = { 1: "High", 2: "Moderate", 3: "Low", 0: "Not estimated" };

  const state = { o: "mortality_diabetes_deaths", v: "diff", m: "nat", s: true, f: true, c: null };
  let data = null, map = null, scale = null, shown = [];

  // ---- URL state ------------------------------------------------------
  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    if (p.get("o") && OUT[p.get("o")]) state.o = p.get("o");
    if (["obs", "exp", "diff"].includes(p.get("v"))) state.v = p.get("v");
    if (["nat", "ws"].includes(p.get("m"))) state.m = p.get("m");
    if (p.get("s") !== null) state.s = p.get("s") !== "0";
    if (p.get("f") !== null) state.f = p.get("f") !== "0";
    if (p.get("c") && POS[p.get("c")] !== undefined) state.c = p.get("c");
  }
  function writeHash() {
    const p = new URLSearchParams({ o: state.o, v: state.v, m: state.m, s: state.s ? "1" : "0", f: state.f ? "1" : "0" });
    if (state.c) p.set("c", state.c);
    history.replaceState(null, "", "#" + p.toString());
  }

  // ---- values ---------------------------------------------------------
  const outcome = () => OUT[state.o];
  function val(i) {
    const o = outcome(), m = data[state.m];
    const obs = data.obs[i], exp = m.exp[i];
    const raw = m.raw[i];  // exported at full precision, not recomputed from rounded values
    const smooth = o.shrinkage ? m.shr[i] : null;
    const diff = state.s && o.shrinkage ? smooth : raw;
    return { obs, exp, raw, smooth, diff, tier: m.tier[i], rel: m.rel[i], peers: m.peers ? m.peers[i] : null };
  }
  function current(i) {
    const x = val(i);
    return state.v === "obs" ? x.obs : state.v === "exp" ? x.exp : x.diff;
  }

  // ---- controls -------------------------------------------------------
  function buildControls() {
    const sel = document.getElementById("outcome");
    for (const layer of LAYER_ORDER) {
      const g = document.createElement("optgroup");
      g.label = LAYER_LABEL[layer];
      IDX.outcomes.filter((o) => o.layer === layer).forEach((o) => {
        const opt = document.createElement("option");
        opt.value = o.id; opt.textContent = o.label;
        g.appendChild(opt);
      });
      sel.appendChild(g);
    }
    sel.addEventListener("change", () => { state.o = sel.value; load(); });
    document.querySelectorAll("#view button").forEach((b) => b.addEventListener("click", () => { state.v = b.dataset.v; render(); }));
    document.querySelectorAll("#mode button").forEach((b) => b.addEventListener("click", () => { state.m = b.dataset.m; render(); }));
    document.getElementById("smooth").addEventListener("change", (e) => { state.s = e.target.checked; render(); });
    document.getElementById("fade").addEventListener("change", (e) => { state.f = e.target.checked; render(); });
    const dl = document.getElementById("county-list");
    const byLabel = {};
    COUNTY.forEach((c) => {
      const label = `${c.name}, ${c.st}`;
      byLabel[label.toLowerCase()] = c.fips;
      const opt = document.createElement("option"); opt.value = label; dl.appendChild(opt);
    });
    const search = document.getElementById("search");
    search.addEventListener("change", () => {
      const f = byLabel[search.value.trim().toLowerCase()];
      if (f) pin(f);
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") pin(null); });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  }

  function syncControls() {
    document.getElementById("outcome").value = state.o;
    document.querySelectorAll("#view button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === state.v)));
    document.querySelectorAll("#mode button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.m === state.m)));
    const sm = document.getElementById("smooth");
    sm.checked = state.s; sm.disabled = !outcome().shrinkage || state.v !== "diff";
    const fd = document.getElementById("fade");
    fd.checked = state.f; fd.disabled = !outcome().shrinkage || state.v !== "diff";
  }

  // ---- rendering ------------------------------------------------------
  function render() {
    if (!data) return;
    syncControls();
    const o = outcome();
    const n = COUNTY.length;
    shown = Array.from({ length: n }, (_, i) => current(i));
    if (state.v === "diff") scale = EVO.divergingScale(shown);
    else scale = EVO.sequentialScale(data.obs);
    map.paths
      .attr("fill", (d) => {
        const i = POS[d.id];
        const v = i === undefined ? null : shown[i];
        return v === null || v === undefined ? "url(#hatch)" : scale(v);
      })
      .attr("fill-opacity", (d) => {
        const i = POS[d.id];
        if (i === undefined || state.v !== "diff" || !state.f || !o.shrinkage) return 1;
        return data[state.m].tier[i] === 3 ? 0.28 : 1;
      })
      .classed("pinned", (d) => d.id === state.c);
    titles(); legend(); about(); extremes(); details(state.c); table(); writeHash();
  }

  function modeText() {
    const o = outcome();
    const base = "county age, sex, race and ethnicity, education and poverty" + (o.layer.startsWith("medicare") ? ", plus Medicare Advantage share" : "");
    return state.m === "nat" ? `Expected from ${base}, using models fit on other available counties without state indicators.` : `Expected from ${base}, plus state indicators, using models fit on other available counties.`;
  }

  function titles() {
    const o = outcome();
    const smoothOn = o.shrinkage && state.s;
    const view = { obs: "measured", exp: "expected", diff: smoothOn ? "smoothed difference from expected" : "measured minus expected" }[state.v];
    document.getElementById("map-title").textContent = `${o.label}: ${view}`;
    let sub;
    if (state.v === "obs") sub = `${o.measure}. Source: ${o.source}.`;
    else if (state.v === "exp") sub = modeText() + " Same color scale as the measured view.";
    else sub = `${o.units === "SMR x 100" ? "Mortality-index points (SMR x 100)" : "Percentage points"}. ${modeText()}` +
      (o.shrinkage && state.s ? " Small-county noise is pulled toward zero according to each county's reliability." : "");
    document.getElementById("map-sub").textContent = sub;
  }

  function legend() {
    const o = outcome(), el = document.getElementById("legend");
    const dom = scale.domain(), lo = dom[0], hi = dom[dom.length - 1];
    const stops = d3.range(0, 1.0001, 0.1).map((t) => scale(lo + (hi - lo) * t)).join(",");
    const signed = state.v === "diff";
    const ticks = signed
      ? `<span>${EVO.fmt(lo, o.units, true)}<br>lower</span><span>0</span><span>${EVO.fmt(hi, o.units, true)}<br>higher</span>`
      : `<span>${EVO.fmt(lo, o.units)}</span><span>${EVO.fmt(hi, o.units)}</span>`;
    let sw = `<span class="sw"><i style="background:repeating-linear-gradient(45deg,var(--missing) 0 3px,var(--missing-hatch) 3px 4.5px)"></i>No data or suppressed</span>`;
    if (signed && state.f && o.shrinkage) sw += `<span class="sw"><i style="background:${scale(hi)};opacity:.28"></i>Low reliability</span>`;
    el.innerHTML = `<div class="ramp" style="background:linear-gradient(90deg,${stops})" role="img" aria-label="Color scale from ${EVO.fmt(lo, o.units, signed)} to ${EVO.fmt(hi, o.units, signed)}"></div>
      <div class="ticks">${ticks}</div><div class="swatches">${sw}</div>`;
  }

  function about() {
    const o = outcome();
    document.getElementById("about").innerHTML = `<h3>About this outcome</h3>
      <p>${o.measure}.</p><p>Source: ${o.source}. Counties with data: ${o.counties.toLocaleString("en-US")}.</p>
      <p class="caveat">${CAVEAT[o.layer]}</p>
      ${o.places_label ? `<p>County details also show the ${o.places_label} (${o.places_note}) for comparison.</p>` : ""}`;
  }

  function details(fips) {
    const el = document.getElementById("details");
    if (!data) return;
    if (!fips) { el.innerHTML = `<p class="hint">Hover a county for values; click to keep it here. Press Escape to clear.</p>`; return; }
    const i = POS[fips], c = COUNTY[i], o = outcome(), x = val(i);
    const ratio = o.units === "SMR x 100" ? " (100 = national)" : "";
    const rows = [
      ["Measured" + ratio, EVO.fmt(x.obs, o.units)],
      ["Expected" + ratio, EVO.fmt(x.exp, o.units)],
      ["Raw difference", EVO.fmt(x.raw, o.units, true)],
    ];
    if (o.shrinkage) rows.push(["Smoothed difference", EVO.fmt(x.smooth, o.units, true)]);
    rows.push(["Reliability", x.tier === null ? "n/a" : `${TIER[x.tier]}${x.rel !== null ? ` (${d3.format(".2f")(x.rel)})` : ""}`]);
    const pl = data.places[i];
    if (o.places_label) rows.push([o.places_label, pl === null ? "n/a" : d3.format(".1f")(pl) + "%"]);
    let notes = data.note[i] ? `<p class="note">${data.note[i]}.</p>` : "";
    if (x.obs === null) notes += `<p class="note">No value: not reported, suppressed or not matched for this county.</p>`;
    if (state.m === "ws" && x.peers === 0) notes += `<p class="note">No other counties in this state, so its expected value uses the average state effect.</p>`;
    if (data.disc[i]) notes += `<p class="note">Flagged: CMS size band disagrees with Medicare enrollment counts for this county. Treat with caution.</p>`;
    el.innerHTML = `<h3>${c.name}, ${c.st}</h3><dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>${notes}`;
  }

  function extremes() {
    const o = outcome(), m = data[state.m];
    document.getElementById("ext-title").textContent = o.shrinkage
      ? "Largest differences, high or moderate reliability"
      : "Largest raw differences (reliability not estimated)";
    const items = [];
    COUNTY.forEach((c, i) => {
      const x = val(i);
      if (x.diff === null) return;
      if (o.shrinkage && !(m.tier[i] === 1 || m.tier[i] === 2)) return;
      items.push({ i, v: x.diff });
    });
    items.sort((a, b) => b.v - a.v);
    const li = (it) => `<li><button type="button" data-fips="${COUNTY[it.i].fips}"><span>${COUNTY[it.i].name}, ${COUNTY[it.i].st}</span><span class="v">${EVO.fmt(it.v, o.units, true)}</span></button></li>`;
    document.getElementById("top-high").innerHTML = items.slice(0, 8).map(li).join("");
    document.getElementById("top-low").innerHTML = items.slice(-8).reverse().map(li).join("");
    document.querySelectorAll(".extremes button").forEach((b) => b.addEventListener("click", () => pin(b.dataset.fips)));
  }

  let sortKey = "diff", sortDir = -1;
  function table() {
    const det = document.getElementById("table-details");
    if (!det.open) return;
    if (!data) {
      document.querySelector("#county-table thead").innerHTML = "";
      document.querySelector("#county-table tbody").innerHTML =
        `<tr><td>Loading the selected outcome. The table will appear when it is ready.</td></tr>`;
      return;
    }
    const o = outcome();
    const cols = [["name", "County"], ["st", "State"], ["obs", "Measured"], ["exp", "Expected"], ["diff", o.shrinkage && state.s ? "Smoothed difference" : "Raw difference"], ["tier", "Reliability"]];
    const rows = COUNTY.map((c, i) => { const x = val(i); return { fips: c.fips, name: c.name, st: c.st, obs: x.obs, exp: x.exp, diff: x.diff, tier: x.tier }; })
      .filter((r) => r.obs !== null);
    rows.sort((a, b) => {
      const A = a[sortKey], B = b[sortKey];
      if (A === null) return 1; if (B === null) return -1;
      return (A > B ? 1 : A < B ? -1 : 0) * sortDir;
    });
    const thead = document.querySelector("#county-table thead");
    thead.innerHTML = "<tr>" + cols.map(([k, l]) => `<th scope="col" class="${["obs", "exp", "diff", "tier"].includes(k) ? "num" : ""}" aria-sort="${k === sortKey ? (sortDir > 0 ? "ascending" : "descending") : "none"}"><button type="button" data-k="${k}">${l}</button></th>`).join("") + "</tr>";
    thead.querySelectorAll("th button").forEach((b) => b.addEventListener("click", () => {
      sortDir = sortKey === b.dataset.k ? -sortDir : (["name", "st"].includes(b.dataset.k) ? 1 : -1);
      sortKey = b.dataset.k; table();
      const again = document.querySelector(`#county-table th button[data-k="${sortKey}"]`);
      if (again) again.focus();
    }));
    document.querySelector("#county-table tbody").innerHTML = rows.map((r) =>
      `<tr><td>${r.name}</td><td>${r.st}</td><td class="num">${EVO.fmt(r.obs, o.units)}</td><td class="num">${EVO.fmt(r.exp, o.units)}</td><td class="num">${EVO.fmt(r.diff, o.units, true)}</td><td class="num">${r.tier === null ? "n/a" : TIER[r.tier]}</td></tr>`).join("");
  }

  // ---- interaction ----------------------------------------------------
  const tip = document.getElementById("tooltip");
  function showTip(event, fips) {
    const i = POS[fips];
    if (i === undefined || !data) return;
    const c = COUNTY[i], o = outcome(), x = val(i);
    tip.innerHTML = `<div class="t-name">${c.name}, ${c.st}</div><dl>
      <dt>Measured</dt><dd>${EVO.fmt(x.obs, o.units)}</dd>
      <dt>Expected</dt><dd>${EVO.fmt(x.exp, o.units)}</dd>
      <dt>${o.shrinkage && state.s ? "Smoothed difference" : "Raw difference"}</dt><dd>${EVO.fmt(x.diff, o.units, true)}</dd>
      <dt>Reliability</dt><dd>${x.tier === null ? "n/a" : TIER[x.tier]}</dd></dl>`;
    const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
    let left = event.clientX + pad, top = event.clientY + pad;
    if (left + w > innerWidth - 8) left = event.clientX - w - pad;
    if (top + h > innerHeight - 8) top = event.clientY - h - pad;
    tip.style.left = left + "px"; tip.style.top = top + "px";
    tip.classList.add("on");
  }
  function pin(fips) {
    state.c = fips;
    map.paths.classed("pinned", (d) => d.id === fips);
    if (fips) map.paths.filter((d) => d.id === fips).raise();
    map.g.select(".state-lines").raise();
    details(fips); writeHash();
  }

  // Each load gets a token; only the latest request may commit its data, so a
  // slow earlier request can never paint over the current selection (Codex
  // site review, finding 1).
  let loadToken = 0;
  async function load() {
    const token = ++loadToken, wanted = state.o;
    const status = document.getElementById("status");
    status.hidden = false; status.textContent = "Loading " + OUT[wanted].label.toLowerCase();
    tip.classList.remove("on");
    data = null;
    try {
      const d = await EVO.loadOutcome(wanted);
      if (token !== loadToken || wanted !== state.o) return;
      data = d;
      status.hidden = true;
      render();
    } catch (err) {
      if (token !== loadToken) return;
      status.textContent = "This outcome could not be loaded. Reload the page or pick another outcome.";
    }
  }

  function init() {
    readHash();
    buildControls();
    map = EVO.drawMap(d3.select("#map"), { patternId: "hatch" });
    map.paths
      .on("mousemove", (e, d) => showTip(e, d.id))
      .on("mouseleave", () => tip.classList.remove("on"))
      .on("click", (e, d) => pin(state.c === d.id ? null : d.id));
    document.getElementById("table-details").addEventListener("toggle", table);
    // Links that change only the #state (e.g. from the project page) do not reload.
    window.addEventListener("hashchange", () => {
      const before = state.o;
      state.c = null;
      readHash();
      if (state.o !== before) load(); else render();
    });
    load();
  }
  init();
})();
