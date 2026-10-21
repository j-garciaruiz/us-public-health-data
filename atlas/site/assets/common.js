/* Shared helpers: data loading, color scales, formatting, county map. */
(function () {
  "use strict";

  const loaded = {};
  // Load a data file as a <script> so the pages also work when opened from disk.
  function loadScript(src) {
    if (!loaded[src]) {
      loaded[src] = new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = src;
        s.onload = resolve;
        s.onerror = () => reject(new Error("Could not load " + src));
        document.head.appendChild(s);
      });
    }
    return loaded[src];
  }

  async function loadOutcome(id) {
    // Single-file builds embed every outcome up front; use it when present.
    if (window.ATLAS_DATA && window.ATLAS_DATA[id]) return window.ATLAS_DATA[id];
    await loadScript("data/atlas_" + id + ".js");
    return window.ATLAS_DATA[id];
  }

  const dark = () => window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Sequential blue (dataviz reference ramp, steps 100-700); flips anchor in dark mode.
  const BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
  // Diverging: blue arm (lower than expected) and red arm (higher), equal steps,
  // neutral warm grey midpoint.
  const DIV_LIGHT = ["#104281", "#2a78d6", "#86b6ef", "#f0efec", "#f1a99f", "#d9584d", "#9c2520"];
  const DIV_DARK = ["#5598e7", "#2f6db8", "#1f4672", "#383835", "#7a2d27", "#c4473c", "#f08a7e"];

  function quantile(values, q) {
    const v = values.filter((x) => x !== null && Number.isFinite(x)).sort((a, b) => a - b);
    if (!v.length) return 0;
    const i = (v.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i);
    return v[lo] + (v[hi] - v[lo]) * (i - lo);
  }

  function sequentialScale(values) {
    const lo = quantile(values, 0.02), hi = quantile(values, 0.98);
    const ramp = dark() ? BLUE.slice().reverse() : BLUE;
    return d3.scaleSequential(d3.interpolateRgbBasis(ramp)).domain([lo, hi]).clamp(true);
  }

  function divergingScale(values) {
    const m = Math.max(quantile(values.map((x) => (x === null ? null : Math.abs(x))), 0.98), 1e-6);
    const ramp = dark() ? DIV_DARK : DIV_LIGHT;
    return d3.scaleDiverging(d3.interpolateRgbBasis(ramp)).domain([-m, 0, m]).clamp(true);
  }

  function fmt(v, units, signed) {
    if (v === null || v === undefined || !Number.isFinite(v)) return "n/a";
    const s = signed && v > 0 ? "+" : "";
    if (units === "SMR x 100") return s + d3.format(".0f")(v);
    return s + d3.format(".1f")(v) + (signed ? " pts" : "%");
  }

  // Draw the county map into an <svg>; returns {paths, path, svg} for recoloring.
  function drawMap(svg, opts) {
    const topo = window.US_TOPO;
    const counties = topojson.feature(topo, topo.objects.counties);
    const states = topojson.mesh(topo, topo.objects.states, (a, b) => a !== b);
    const W = 975, H = 610;
    const proj = d3.geoIdentity().reflectY(true).fitSize([W, H], counties);
    const path = d3.geoPath(proj);
    svg.attr("viewBox", `0 0 ${W} ${H}`).attr("preserveAspectRatio", "xMidYMid meet");
    const g = svg.append("g");
    const paths = g.selectAll("path.county").data(counties.features).join("path")
      .attr("class", "county").attr("d", path).attr("data-fips", (d) => d.id);
    g.append("path").attr("class", "state-lines").datum(states).attr("d", path)
      .attr("fill", "none").attr("stroke", "var(--state-line)").attr("stroke-width", 1.1)
      .attr("stroke-linejoin", "round").attr("pointer-events", "none");
    if (opts && opts.patternId) {
      const defs = svg.append("defs");
      const p = defs.append("pattern").attr("id", opts.patternId).attr("patternUnits", "userSpaceOnUse")
        .attr("width", 5).attr("height", 5).attr("patternTransform", "rotate(45)");
      p.append("rect").attr("width", 5).attr("height", 5).attr("fill", "var(--missing)");
      p.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 5)
        .attr("stroke", "var(--missing-hatch)").attr("stroke-width", 1.4);
    }
    return { paths, path, svg, g };
  }

  window.EVO = { loadScript, loadOutcome, sequentialScale, divergingScale, quantile, fmt, drawMap, dark };
})();
