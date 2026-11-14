// GeoCities-style extras: neighborhood switcher, hit counter, sparkle trail.
(function () {
  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); }
    catch (e) { return null; }
  }

  // --- neighborhood (theme) switcher ---
  // "lettuce" is the house theme: PANTONE 13-0324 TCX Lettuce Green (#BED38E).
  var THEMES = ["lettuce", "rainforest", "area51", "siliconvalley"];
  var DEFAULT_THEME = "lettuce";
  function setTheme(t) {
    if (THEMES.indexOf(t) < 0) t = DEFAULT_THEME;
    THEMES.forEach(function (x) { document.body.classList.remove("theme-" + x); });
    document.body.classList.add("theme-" + t);
    document.querySelectorAll("[data-theme]").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-theme") === t);
    });
    store("gc-theme", t);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTheme(store("gc-theme") || DEFAULT_THEME);
    document.querySelectorAll("[data-theme]").forEach(function (b) {
      b.addEventListener("click", function () { setTheme(b.getAttribute("data-theme")); });
    });

    // --- per-browser hit counter (honest: counts your own visits) ---
    var n = parseInt(store("gc-hits") || "0", 10) + 1;
    store("gc-hits", String(n));
    var el = document.getElementById("gc-hits");
    if (el) el.textContent = String(n).padStart(6, "0");

    var up = document.getElementById("gc-updated");
    if (up) up.textContent = new Date(document.lastModified).toLocaleDateString("en-GB");
  });

  // --- sparkle cursor trail (skipped when the visitor asks for less motion) ---
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  var last = 0, GLYPHS = ["✨", "🌱", "✦", "🥬"];
  document.addEventListener("mousemove", function (e) {
    if (calm && calm.matches) return;
    var now = Date.now();
    if (now - last < 60) return;
    last = now;
    var s = document.createElement("span");
    s.className = "gc-sparkle";
    s.textContent = GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
    s.style.left = e.clientX + 8 + "px";
    s.style.top = e.clientY + 8 + "px";
    document.body.appendChild(s);
    setTimeout(function () { s.remove(); }, 800);
  });
})();
