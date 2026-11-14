// GeoCities-style extras: neighborhood switcher, hit counter, sparkle trail.
(function () {
  // Two helpers so nothing here needs a DOM or language feature newer than
  // the browsers this page is meant to survive on. A NodeList only gained
  // .forEach with DOM4, and String.prototype.padStart is ES2017: either one
  // throws on an older engine, and a throw in this file takes the theme
  // switcher and the counter down with it.
  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  function pad(n, width) {
    var out = String(n);
    while (out.length < width) { out = "0" + out; }
    return out;
  }

  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); }
    catch (e) { return null; }
  }

  // --- neighborhood (theme) switcher ---
  // "salinasvalley" is the house theme: PANTONE 13-0324 TCX Lettuce Green
  // (#BED38E). A stored name that is no longer in this list — an older
  // "lettuce", "rainforest" or "siliconvalley" — falls back to the default
  // below rather than leaving the page with no theme class at all.
  var THEMES = ["salinasvalley", "growthchamber"];
  var DEFAULT_THEME = "salinasvalley";
  // --- the guestbook widget follows the neighborhood ---
  // giscus runs in an iframe on its own origin, so it cannot read the body
  // class; it is told instead, by postMessage. The URLs are absolute because
  // the iframe resolves them against giscus.app, not against this site.
  var GISCUS_ORIGIN = "https://giscus.app";
  var GISCUS_THEMES = {
    salinasvalley: "https://www.mfkara.net/assets/geocities/giscus-salinasvalley.css",
    growthchamber: "https://www.mfkara.net/assets/geocities/giscus-growthchamber.css"
  };
  var active = DEFAULT_THEME;

  function syncGiscus(t) {
    var frame = document.querySelector("iframe.giscus-frame");
    if (!frame || !frame.contentWindow || !GISCUS_THEMES[t]) return;
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: GISCUS_THEMES[t] } } }, GISCUS_ORIGIN);
  }

  // The iframe loads lazily and may not exist when the theme is first applied,
  // so the first sync waits for giscus to announce itself. Without this, a
  // visitor whose stored neighborhood is GrowthChamber would get a light
  // comment box on a dark page until they touched the switcher.
  window.addEventListener("message", function (event) {
    if (event.origin !== GISCUS_ORIGIN) return;
    if (!event.data || typeof event.data !== "object" || !event.data.giscus) return;
    syncGiscus(active);
  });

  function setTheme(t) {
    if (THEMES.indexOf(t) < 0) t = DEFAULT_THEME;
    THEMES.forEach(function (x) { document.body.classList.remove("theme-" + x); });
    document.body.classList.add("theme-" + t);
    each(document.querySelectorAll("[data-theme]"), function (b) {
      b.classList.toggle("active", b.getAttribute("data-theme") === t);
    });
    active = t;
    syncGiscus(t);
    store("gc-theme", t);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTheme(store("gc-theme") || DEFAULT_THEME);
    each(document.querySelectorAll("[data-theme]"), function (b) {
      b.addEventListener("click", function () { setTheme(b.getAttribute("data-theme")); });
    });

    // --- per-browser visit counter (honest: it counts YOUR visits) ---
    //
    // Counts visits, not page views. Incrementing on every load made the
    // number a page counter wearing a visitor counter's label: clicking
    // Home -> Publications -> CV -> Guestbook announced four visitors, all of
    // them the same person.
    //
    // A visit is a run of activity with no gap longer than VISIT_WINDOW, the
    // 30 minutes analytics tools conventionally use. The timestamp is written
    // on every page, so moving around the site extends the current visit
    // rather than starting a new one, and coming back tomorrow counts once.
    //
    // The window is kept in localStorage rather than sessionStorage, which is
    // per tab: opening a second tab would otherwise be a second visitor.
    var VISIT_WINDOW = 30 * 60 * 1000;
    var now = Date.now();
    var seen = parseInt(store("gc-seen") || "0", 10);
    var n = parseInt(store("gc-hits") || "0", 10);
    if (!seen || now - seen > VISIT_WINDOW) n += 1;
    store("gc-hits", String(n));
    store("gc-seen", String(now));
    var el = document.getElementById("gc-hits");
    // With storage blocked (a private window, or site data switched off) both
    // reads come back null, so this reads 000001 on every page: the one number
    // that is true for a visitor nothing can be remembered about.
    if (el) el.textContent = pad(n || 1, 6);

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
