/* Project page: hero map, two charts and the atlas examples.
   Every number comes from window.FINDINGS or the atlas data files. */
(function () {
  "use strict";
  const F = window.FINDINGS;
  const pct = (x, d = 0) => d3.format(`.${d}%`)(x);
  const tip = document.getElementById("tooltip");
  const CAT = { blue: "var(--accent)", orange: "#d95926", ink: "var(--ink)" };

  function showTip(event, html) {
    tip.innerHTML = html;
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let left = event.clientX + 14, top = event.clientY + 14;
    if (left + w > innerWidth - 8) left = event.clientX - w - 14;
    if (top + h > innerHeight - 8) top = event.clientY - h - 14;
    tip.style.left = left + "px"; tip.style.top = top + "px"; tip.classList.add("on");
  }
  const hideTip = () => tip.classList.remove("on");

  // ---- bound numbers --------------------------------------------------
  const r2 = F.r2_crude_cv.map((d) => d.inputs_plus_state_cv);
  const r2Median = d3.median(r2);
  const bind = {
    r2_median_pct: pct(r2Median),
    r2_median_pct1: pct(r2Median, 1),
    max_gain_pts: d3.format(".1f")(F.pvo_max_gain_larger * 100),
    max_gain_all_pts: d3.format(".1f")(F.pvo_max_gain_all * 100),
  };
  document.querySelectorAll("[data-bind]").forEach((el) => { el.textContent = bind[el.dataset.bind]; });

  // ---- hero map -------------------------------------------------------
  async function heroMap() {
    const id = "mortality_diabetes_deaths";
    const data = await EVO.loadOutcome(id);
    const pos = Object.fromEntries(window.ATLAS_INDEX.counties.map((c, i) => [c.fips, i]));
    const map = EVO.drawMap(d3.select("#hero-map"), { patternId: "hatch-hero" });
    const vals = data.nat.shr;
    const scale = EVO.divergingScale(vals);
    map.paths
      .attr("fill", (d) => { const v = vals[pos[d.id]]; return v === null || v === undefined ? "url(#hatch-hero)" : scale(v); })
      .attr("fill-opacity", (d) => (data.nat.tier[pos[d.id]] === 3 ? 0.28 : 1));
    const m = scale.domain()[2];
    const stops = d3.range(0, 1.0001, 0.1).map((t) => scale(-m + 2 * m * t)).join(",");
    document.getElementById("hero-legend").innerHTML =
      `<span>lower</span><i style="background:linear-gradient(90deg,${stops})"></i><span>higher</span>`;
  }

  // ---- chart 1: how much of each PLACES measure is reproduced ----------
  function chartR2() {
    const el = document.getElementById("chart-r2");
    el.innerHTML = "";
    const bench = F.benchmark;
    const all = bench.find((b) => b.sample === "all counties");
    const big = bench.find((b) => b.sample === ">=20k adults");
    const W = Math.max(320, el.clientWidth), narrow = W < 560;
    const H = narrow ? 250 : 230, M = { l: 10, r: 20, t: narrow ? 90 : 70, b: 34 };
    const x = d3.scaleLinear().domain([0.6, 1]).range([M.l, W - M.r]);
    const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    svg.append("g").attr("class", "axis").attr("transform", `translate(0,${H - M.b})`)
      .call(d3.axisBottom(x).ticks(narrow ? 4 : 5).tickFormat(d3.format(".0%")).tickSize(-(H - M.t - M.b)))
      .call((g) => g.select(".domain").remove());
    // beeswarm of the 40 PLACES measures
    const nodes = F.r2_crude_cv.map((d) => ({ ...d, x: x(d.inputs_plus_state_cv), y: 0 }));
    const sim = d3.forceSimulation(nodes).force("x", d3.forceX((d) => x(d.inputs_plus_state_cv)).strength(1))
      .force("y", d3.forceY(0)).force("c", d3.forceCollide(narrow ? 4.4 : 5.6)).stop();
    for (let i = 0; i < 200; i++) sim.tick();
    const cy = M.t + 40;
    svg.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("cx", (d) => d.x).attr("cy", (d) => cy + d.y).attr("r", narrow ? 3.6 : 4.6)
      .attr("fill", CAT.blue).attr("stroke", "var(--surface)").attr("stroke-width", 1)
      .on("mousemove", (e, d) => showTip(e, `<div class="t-name">PLACES: ${d.label}</div><dl><dt>Reproduced</dt><dd>${pct(d.inputs_plus_state_cv, 1)}</dd><dt>Counties</dt><dd>${d.n_counties.toLocaleString("en-US")}</dd></dl>`))
      .on("mouseleave", hideTip);
    // benchmark: directly measured uninsurance
    [[all.cv_r2_acs_direct, "Census, full available sample"], [big.cv_r2_acs_direct, "Census, 20,000+ adults"]].forEach(([v, label], k) => {
      const g = svg.append("g").attr("transform", `translate(${x(v)},${cy})`);
      g.append("path").attr("d", d3.symbol(d3.symbolDiamond, 90)).attr("fill", CAT.orange)
        .on("mousemove", (e) => showTip(e, `<div class="t-name">Uninsured 19-64, measured by the Census</div><dl><dt>Sample</dt><dd>${label}</dd><dt>Reproduced</dt><dd>${pct(v, 1)}</dd></dl>`))
        .on("mouseleave", hideTip);
    });
    const placesUnins = F.r2_crude_cv.find((d) => d.measure === "access2").inputs_plus_state_cv;
    svg.append("text").attr("x", x(placesUnins)).attr("y", M.t - 52).attr("text-anchor", "end").attr("class", "label-strong")
      .text(`PLACES uninsurance: ${pct(placesUnins)}`);
    svg.append("line").attr("x1", x(placesUnins)).attr("x2", x(placesUnins)).attr("y1", M.t - 46).attr("y2", cy - 8)
      .attr("stroke", "var(--axis)");
    const census = svg.append("text").attr("x", x(all.cv_r2_acs_direct)).attr("y", M.t - 30).attr("class", "label-strong");
    if (narrow) {
      census.append("tspan").attr("x", x(all.cv_r2_acs_direct)).attr("dy", "-1.1em").text(`Census-measured uninsurance: ${pct(all.cv_r2_acs_direct)}`);
      census.append("tspan").attr("x", x(all.cv_r2_acs_direct)).attr("dy", "1.2em").text(`(${pct(big.cv_r2_acs_direct)} in larger counties)`);
    } else census.text(`Census-measured uninsurance: ${pct(all.cv_r2_acs_direct)} (${pct(big.cv_r2_acs_direct)} in larger counties)`);
    svg.append("line").attr("x1", x(all.cv_r2_acs_direct)).attr("x2", x(all.cv_r2_acs_direct)).attr("y1", M.t - 24).attr("y2", cy - 8)
      .attr("stroke", "var(--axis)");
    svg.append("text").attr("x", M.l).attr("y", H - 4).text(narrow ? "Share reproduced. Blue: 40 PLACES measures (crude)." : "Share of county-to-county variation reproduced on counties the model did not see. Blue: the 40 PLACES measures (crude prevalence).");
    // data table
    document.getElementById("table-r2").innerHTML = `<table><thead><tr><th>PLACES measure</th><th class="num">Reproduced</th><th class="num">Counties</th></tr></thead><tbody>` +
      F.r2_crude_cv.slice().sort((a, b) => b.inputs_plus_state_cv - a.inputs_plus_state_cv)
        .map((d) => `<tr><td>${d.label}</td><td class="num">${pct(d.inputs_plus_state_cv, 1)}</td><td class="num">${d.n_counties.toLocaleString("en-US")}</td></tr>`).join("") +
      `<tr><td>Census-measured uninsurance, full available sample</td><td class="num">${pct(all.cv_r2_acs_direct, 1)}</td><td class="num">${all.n.toLocaleString("en-US")}</td></tr>` +
      `<tr><td>Census-measured uninsurance, 20,000+ adults</td><td class="num">${pct(big.cv_r2_acs_direct, 1)}</td><td class="num">${big.n.toLocaleString("en-US")}</td></tr></tbody></table>`;
  }

  // ---- chart 2: PLACES vs measured outcomes ----------------------------
  function chartPvo() {
    const el = document.getElementById("chart-pvo");
    el.innerHTML = "";
    const SRC = { medicare: "Medicare", acs: "Census", wonder: "deaths" };
    const rows = F.places_vs_observed.filter((d) => d.sample === "all")
      .map((d) => ({ ...d, label: d.source === "wonder" ? d.outcome.replace(" (SMR)", "") : `${d.outcome} (${SRC[d.source]})` }))
      .sort((a, b) => b.cv_r2_demo - a.cv_r2_demo);
    const W = Math.max(320, el.clientWidth), narrow = W < 640;
    const rowH = narrow ? 40 : 24, M = { l: narrow ? 8 : 300, r: 16, t: 12, b: 40 };
    const H = M.t + rows.length * rowH + M.b;
    const x = d3.scaleLinear().domain([0, 0.9]).range([M.l, W - M.r]);
    const y = (i) => M.t + i * rowH + rowH / 2;
    const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    svg.append("g").attr("class", "axis").attr("transform", `translate(0,${H - M.b})`)
      .call(d3.axisBottom(x).ticks(narrow ? 3 : 9).tickFormat(d3.format(".0%")).tickSize(-(H - M.t - M.b)))
      .call((g) => g.select(".domain").remove());
    const g = svg.append("g").selectAll("g").data(rows).join("g").attr("transform", (d, i) => `translate(0,${y(i)})`);
    if (narrow) g.append("text").attr("x", 0).attr("y", -10).text((d) => d.label);
    else g.append("text").attr("x", M.l - 12).attr("dy", "0.35em").attr("text-anchor", "end").text((d) => d.label);
    if (narrow) g.attr("transform", (d, i) => `translate(0,${y(i) + 6})`);
    g.append("line").attr("x1", (d) => x(Math.min(d.cv_r2_places, d.cv_r2_demo))).attr("x2", (d) => x(Math.max(d.cv_r2_demo_places, d.cv_r2_demo)))
      .attr("stroke", "var(--axis)").attr("stroke-width", 2);
    g.append("circle").attr("cx", (d) => x(d.cv_r2_places)).attr("r", 5).attr("fill", CAT.orange).attr("stroke", "var(--surface)");
    g.append("circle").attr("cx", (d) => x(d.cv_r2_demo)).attr("r", 5.5).attr("fill", CAT.blue).attr("stroke", "var(--surface)");
    g.append("circle").attr("cx", (d) => x(d.cv_r2_demo_places)).attr("r", 8).attr("fill", "none").attr("stroke", CAT.ink).attr("stroke-width", 1.5);
    g.append("rect").attr("x", 0).attr("y", -rowH / 2).attr("width", W).attr("height", rowH).attr("fill", "transparent")
      .on("mousemove", (e, d) => showTip(e, `<div class="t-name">${d.label}</div><dl>
        <dt>PLACES alone</dt><dd>${pct(d.cv_r2_places, 1)}</dd>
        <dt>Demographics and state</dt><dd>${pct(d.cv_r2_demo, 1)}</dd>
        <dt>Both together</dt><dd>${pct(d.cv_r2_demo_places, 1)}</dd>
        <dt>Counties</dt><dd>${d.n.toLocaleString("en-US")}</dd></dl>`))
      .on("mouseleave", hideTip);
    // legend: three series, so a legend is always present (dataviz rule)
    el.insertAdjacentHTML("afterbegin", `<div class="chart-legend">
      <span><i style="background:${CAT.orange}"></i>PLACES alone</span>
      <span><i style="background:${CAT.blue}"></i>Demographics and state (plus Medicare Advantage share for Medicare)</span>
      <span><i class="ring"></i>Both together</span></div>`);
    svg.append("text").attr("x", narrow ? 0 : M.l).attr("y", H - 6).text(narrow ? "Share of county variation predicted (R²)" : "Share of county variation predicted in held-out counties (cross-validated R²; full available samples)");
    document.getElementById("table-pvo").innerHTML = `<table><thead><tr><th>Measured outcome</th><th class="num">PLACES alone</th><th class="num">Demographics and state</th><th class="num">Both</th><th class="num">Counties</th></tr></thead><tbody>` +
      rows.map((d) => `<tr><td>${d.label}</td><td class="num">${pct(d.cv_r2_places, 1)}</td><td class="num">${pct(d.cv_r2_demo, 1)}</td><td class="num">${pct(d.cv_r2_demo_places, 1)}</td><td class="num">${d.n.toLocaleString("en-US")}</td></tr>`).join("") + "</tbody></table>";
  }

  // ---- examples ---------------------------------------------------------
  function examples() {
    const ex = Object.fromEntries(F.examples.map((e) => [e.fips + e.layer, e]));
    const caddo = ex["22017mortality"], iberia = ex["22045mortality"];
    const rich = ex["36085medicare_actual"], kings = ex["36047medicare_actual"];
    const link = (e, extra) => `atlas.html#o=${e.id}&v=diff&m=nat&s=1&f=1&c=${e.fips}${extra || ""}`;
    const f0 = d3.format(".0f"), f1 = d3.format(".1f");
    document.getElementById("examples").innerHTML = `
      <article class="ex">
        <p class="ex-num">${f0(caddo.observed)} vs ${f0(caddo.expected)}</p>
        <h3>Diabetes deaths:<br>Caddo&nbsp;Parish, Louisiana</h3>
        <p>Diabetes deaths run at ${f1(caddo.observed / 100)} times the national rate for Caddo's age mix (an index of ${f0(caddo.observed)}, where 100 is the national rate), against ${f0(caddo.expected)} expected from its demographics. Iberia Parish, elsewhere in Louisiana, has an index of ${f0(iberia.observed)} against ${f0(iberia.expected)} expected. The contrast could reflect differences in disease, care, how deaths are certified or other factors; this analysis does not distinguish&nbsp;them.</p>
        <a href="${link(caddo)}">See Louisiana in the atlas</a>
      </article>
      <article class="ex">
        <p class="ex-num">${f0(rich.observed)}% vs ${f0(rich.expected)}%</p>
        <h3>Recorded diabetes in Staten&nbsp;Island</h3>
        <p>Share of Original Medicare beneficiaries with a recorded diabetes diagnosis, against the share expected from county demographics and Medicare Advantage enrollment. Brooklyn: ${f0(kings.observed)}% against ${f0(kings.expected)}%. Disease, access to care, who is in Original Medicare, and diagnosis or coding practices may all contribute; this analysis does not separate&nbsp;them.</p>
        <a href="${link(rich)}">See New York City in the atlas</a>
      </article>
      <article class="ex">
        <p class="ex-num">${F.atlas_outcomes} layers</p>
        <h3>Deaths, diagnoses and&nbsp;disability</h3>
        <p>${F.atlas_min_coverage.toLocaleString("en-US")} to ${F.atlas_max_coverage.toLocaleString("en-US")} counties per layer, depending on the source, with measured and expected values. Predictions use county demographics, plus Medicare Advantage share for Medicare, with or without state indicators. Reliability is shown where it can be estimated; age-standardized Medicare has none.</p>
        <a href="atlas.html">Browse all outcomes</a>
      </article>`;
  }

  heroMap(); chartR2(); chartPvo(); examples();
  // Redraw the charts at the new width (labels stay legible on phones).
  let lastW = innerWidth;
  new ResizeObserver(() => {
    if (Math.abs(innerWidth - lastW) < 40) return;
    lastW = innerWidth; chartR2(); chartPvo();
  }).observe(document.body);
})();
