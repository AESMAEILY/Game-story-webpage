#!/usr/bin/env python3
"""Bundles the multi-page GameStoryHub site into ONE self-contained HTML file
(hash-routed SPA) for a live Artifact preview. Not part of the deliverable &mdash;
the real deliverable is the multi-page static site in the project root."""
import base64
import json
import mimetypes
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "css", "styles.css"), encoding="utf-8") as f:
    CSS = f.read()

with open(os.path.join(ROOT, "data", "games.json"), encoding="utf-8") as f:
    GAMES = json.load(f)

# The preview bundle is a single self-contained file (Artifact CSP allows no
# external asset hosts besides Google Fonts), so any real poster image has to
# be inlined as a data: URI rather than referenced by its relative site path.
for _game in GAMES:
    _poster = _game.get("poster")
    if _poster:
        _path = os.path.join(ROOT, _poster)
        _mime = mimetypes.guess_type(_path)[0] or "image/jpeg"
        with open(_path, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode("ascii")
        _game["poster"] = f"data:{_mime};base64,{_b64}"

GAMES_JSON = json.dumps(GAMES, ensure_ascii=False)

HTML = """<title>GameStoryHub</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
__CSS__
:root { --accent: #7c8cff; --accent2: #3ee6c4; }
.preview-badge {
  position: fixed; bottom: 16px; right: 16px; z-index: 200;
  background: var(--bg-elev); border: 1px solid var(--line);
  color: var(--text-faint); font-size: 0.72rem; padding: 8px 14px;
  border-radius: 999px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.preview-badge strong { color: var(--text); }
</style>

<a class="skip-link" href="javascript:void(0)" data-skip="main">Skip to content</a>

<header class="site-nav">
  <a class="brand" href="javascript:void(0)" data-nav="/">
    <span class="brand-mark">&#9889;</span>
    <span>GameStoryHub<small>Walkthroughs &amp; Story</small></span>
  </a>
  <nav class="nav-links" aria-label="Primary">
    <a href="javascript:void(0)" data-route="home" data-nav="/">Home</a>
    <a href="javascript:void(0)" data-route="browse" data-nav="/browse">Browse</a>
  </nav>
  <div class="nav-search">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
    <input type="search" id="nav-search-input" placeholder="Search games&hellip;" aria-label="Search games">
    <div class="nav-search-results" id="nav-search-results"></div>
  </div>
</header>

<main id="main"><div id="app"></div></main>

<footer class="site-footer">
  <div class="container">
    <span>GameStoryHub &mdash; a fan-made walkthrough &amp; story hub. Videos embedded via YouTube; all game titles and art are property of their respective publishers.</span>
    <span>&copy; 2026 Alireza Esmaeily. All rights reserved. Site design and code are proprietary.</span>
    <span><a href="javascript:void(0)" data-nav="/browse">Browse all games</a></span>
  </div>
</footer>

<div class="preview-badge"><strong>Live preview</strong> &middot; single-file bundle of the real multi-page site</div>

<script id="games-data" type="application/json">
__GAMES_JSON__
</script>

<script>
(function () {
  "use strict";
  var GAMES = JSON.parse(document.getElementById("games-data").textContent);
  var app = document.getElementById("app");

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function initials(title) {
    var words = title.replace(/[^A-Za-z0-9 ]/g, "").split(" ").filter(Boolean);
    if (words.length === 0) return "?";
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
    return (words[0][0] + words[1][0]).toUpperCase();
  }
  function formatDate(iso) {
    var d = new Date(iso + "T00:00:00Z");
    return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  }
  function year(iso) { return iso.slice(0, 4); }
  function gameHref(slug) { return "/game/" + slug; }

  var GENRE_ICONS = {
    "Metroidvania": '<circle cx="16" cy="20" r="5"/><circle cx="48" cy="16" r="5"/><circle cx="32" cy="48" r="5"/><path d="M20 23 L44 18 M18 24 L30 45 M46 20 L34 45"/>',
    "Roguelike": '<rect x="14" y="14" width="36" height="36" rx="7"/><circle cx="24" cy="24" r="2.6" fill="currentColor" stroke="none"/><circle cx="40" cy="24" r="2.6" fill="currentColor" stroke="none"/><circle cx="32" cy="32" r="2.6" fill="currentColor" stroke="none"/><circle cx="24" cy="40" r="2.6" fill="currentColor" stroke="none"/><circle cx="40" cy="40" r="2.6" fill="currentColor" stroke="none"/>',
    "Action RPG": '<path d="M32 6 L32 38 M32 6 L27 15 L37 15 Z M20 38 H44 M32 38 V56 M25 47 H39"/>',
    "RPG": '<path d="M32 8 L52 16 V30 C52 45 43 54 32 58 C21 54 12 45 12 30 V16 Z M32 20 V44 M22 32 H42"/>',
    "JRPG": '<path d="M20 24 L32 6 L44 24 L38 54 L26 54 Z M20 24 H44 M32 6 V24"/>',
    "Turn-Based RPG": '<path d="M17 8 H47 M17 56 H47 M19 8 C19 24 45 24 45 8 M19 56 C19 40 45 40 45 56"/>',
    "Action Adventure": '<circle cx="32" cy="32" r="23"/><path d="M32 15 L39 32 L32 49 L25 32 Z"/>',
    "3D Platformer": '<path d="M8 52 H20 V40 H32 V28 H44 V16" /><path d="M12 42 C18 24 32 18 46 14" stroke-dasharray="1 7"/>',
    "Co-op Platformer": '<path d="M8 52 H20 V40 H32 V28 H44 V16" /><path d="M12 42 C18 24 32 18 46 14" stroke-dasharray="1 7"/>',
    "Co-op Action Adventure": '<circle cx="25" cy="32" r="16"/><circle cx="39" cy="32" r="16"/>',
    "Survival Horror": '<path d="M6 32 C15 16 49 16 58 32 C49 48 15 48 6 32 Z"/><circle cx="32" cy="32" r="7.5"/><path d="M33 24 L29 8 M41 26 L54 16"/>',
    "Tactical Shooter": '<circle cx="32" cy="32" r="19"/><circle cx="32" cy="32" r="4" fill="currentColor" stroke="none"/><path d="M32 4 V16 M32 48 V60 M4 32 H16 M48 32 H60"/>',
    "VR Shooter": '<path d="M13 33 C13 17 21 9 32 9 C43 9 51 17 51 33"/><rect x="7" y="29" width="13" height="17" rx="4.5"/><rect x="44" y="29" width="13" height="17" rx="4.5"/>',
    "Puzzle": '<path d="M18 18 H30 C30 11 41 11 41 18 H53 V30 C60 30 60 41 53 41 V53 H41 C41 60 30 60 30 53 H18 V41 C11 41 11 30 18 30 Z"/>',
    "Life Simulation": '<path d="M10 34 L32 14 L54 34"/><path d="M17 31 V53 H47 V31"/><path d="M27 44 C24 40 18 41 18 46 C18 51 27 56 27 56 C27 56 36 51 36 46 C36 41 30 40 27 44"/>',
    "Farming Simulation": '<path d="M32 58 V18 M32 18 L23 9 M32 18 L41 9 M32 29 L23 20 M32 29 L41 20 M32 40 L23 31 M32 40 L41 31"/>',
    "Sandbox Survival": '<path d="M32 6 L54 18 V42 L32 54 L10 42 V18 Z M32 6 V30 M10 18 L32 30 L54 18 M32 30 V54"/>',
    "MMORPG": '<circle cx="32" cy="32" r="23"/><path d="M9 32 H55 M32 9 C19 20 19 44 32 55 C45 44 45 20 32 9 Z"/>',
  };
  function genreIcon(genre) { return GENRE_ICONS[genre] || GENRE_ICONS["Action Adventure"]; }

  function posterArtHTML(game) {
    if (game.poster) {
      return '<img class="tile-photo" src="' + game.poster + '" alt="' + escapeHtml(game.title) + ' cover art" loading="lazy" decoding="async">' +
        '<div class="tile-vignette"></div><div class="tile-shine"></div>';
    }
    return '<div class="tile-art-bg"></div>' +
      '<span class="poster-icon"><svg viewBox="0 0 64 64">' + genreIcon(game.genres[0]) + '</svg></span>' +
      '<div class="tile-vignette"></div><div class="tile-shine"></div>' +
      '<span class="poster-badge"><span class="tile-initial">' + initials(game.title) + '</span></span>';
  }

  function tileHTML(game) {
    var yt = game.youtube;
    return '<article class="tile reveal" data-slug="' + game.slug + '" style="--tile-accent:' + game.accent + ';--tile-accent2:' + game.accent2 + '">' +
      '<a class="tile-media" href="javascript:void(0)" data-nav="' + gameHref(game.slug) + '" data-yt="' + yt.id + '" aria-label="Open ' + escapeHtml(game.title) + '">' +
        '<span class="tile-genre-badge">' + escapeHtml(game.genres[0]) + '</span>' +
        '<div class="tile-art' + (game.poster ? ' has-photo' : '') + '">' + posterArtHTML(game) +
        '</div>' +
        '<iframe class="tile-preview" tabindex="-1" title="" data-id="' + yt.id + '"></iframe>' +
        '<span class="play-badge" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>' +
      '</a>' +
      '<div class="tile-body">' +
        '<a href="javascript:void(0)" data-nav="' + gameHref(game.slug) + '"><h3 class="tile-title">' + escapeHtml(game.title) + '</h3></a>' +
        '<div class="tile-meta"><span>' + year(game.releaseDate) + '</span><span class="dot">&middot;</span><span>' + escapeHtml(game.platforms[0]) + (game.platforms.length > 1 ? " +" + (game.platforms.length - 1) : "") + '</span></div>' +
      '</div></article>';
  }

  function wireTilt(scope) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var medias = (scope || document).querySelectorAll(".tile-media, .game-cover");
    medias.forEach(function (media) {
      media.addEventListener("pointermove", function (e) {
        if (e.pointerType === "touch") return;
        var rect = media.getBoundingClientRect();
        var px = (e.clientX - rect.left) / rect.width - 0.5;
        var py = (e.clientY - rect.top) / rect.height - 0.5;
        media.style.setProperty("--ry", (px * 14).toFixed(2) + "deg");
        media.style.setProperty("--rx", (py * -14).toFixed(2) + "deg");
      });
      media.addEventListener("pointerleave", function () {
        media.style.setProperty("--rx", "0deg");
        media.style.setProperty("--ry", "0deg");
      });
    });
  }

  function wireReveal(scope) {
    var els = (scope || document).querySelectorAll(".reveal");
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        entry.target.classList.add("in");
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    els.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 12, 8) * 35 + "ms";
      io.observe(el);
    });
  }

  function renderGrid(container, games) {
    if (!container) return;
    if (games.length === 0) {
      container.innerHTML = '<div class="no-results"><strong>No games matched.</strong>Try a different title, genre, or platform.</div>';
      return;
    }
    container.innerHTML = games.map(tileHTML).join("");
    wireHoverPreviews(container);
    wireTilt(container);
    wireReveal(container);
  }

  function wireHoverPreviews(scope) {
    var medias = (scope || document).querySelectorAll(".tile-media[data-yt]");
    medias.forEach(function (media) {
      var iframe = media.querySelector(".tile-preview");
      var timer = null;
      media.addEventListener("mouseenter", function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          var id = iframe.dataset.id;
          if (!iframe.src) {
            iframe.src = "https://www.youtube.com/embed/" + id + "?autoplay=1&mute=1&loop=1&playlist=" + id + "&controls=0&modestbranding=1&playsinline=1&rel=0";
          }
          iframe.classList.add("active");
        }, 320);
      });
      media.addEventListener("mouseleave", function () {
        clearTimeout(timer);
        iframe.classList.remove("active");
        iframe.src = "";
      });
    });
  }

  // Official YouTube IFrame Player API for the main "top walkthrough" video —
  // playback happens entirely inside our page via postMessage, no navigation
  // to youtube.com. (YouTube's own player chrome still shows its small
  // logo/title as a link, per YouTube's platform terms — that one element
  // can't be removed by any embed method — everything else stays in-page.)
  var ytApiPromise = null;
  function loadYouTubeApi() {
    if (ytApiPromise) return ytApiPromise;
    ytApiPromise = new Promise(function (resolve) {
      if (window.YT && window.YT.Player) { resolve(window.YT); return; }
      var prevReady = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function () {
        if (typeof prevReady === "function") prevReady();
        resolve(window.YT);
      };
      if (!document.querySelector('script[src="https://www.youtube.com/iframe_api"]')) {
        var tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        document.head.appendChild(tag);
      }
    });
    return ytApiPromise;
  }
  function mountYouTubePlayer(mountId, videoId) {
    loadYouTubeApi().then(function (YT) {
      if (!document.getElementById(mountId)) return; // SPA nav moved on before API loaded
      var playerVars = { rel: 0, modestbranding: 1, playsinline: 1, enablejsapi: 1 };
      if (window.location.origin && window.location.origin.indexOf("http") === 0) {
        playerVars.origin = window.location.origin;
      }
      new YT.Player(mountId, { videoId: videoId, playerVars: playerVars });
    });
  }

  function searchGames(games, query) {
    var q = query.trim().toLowerCase();
    if (!q) return [];
    return games.filter(function (g) {
      return g.title.toLowerCase().indexOf(q) !== -1 ||
        g.genres.some(function (x) { return x.toLowerCase().indexOf(q) !== -1; }) ||
        g.platforms.some(function (x) { return x.toLowerCase().indexOf(q) !== -1; }) ||
        g.developer.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 8);
  }

  function resultRowHTML(game) {
    return '<a href="javascript:void(0)" data-nav="' + gameHref(game.slug) + '">' +
      '<span class="swatch" style="background:linear-gradient(135deg, ' + game.accent + ', ' + game.accent2 + ')"></span>' +
      '<span><div>' + escapeHtml(game.title) + '</div><div class="meta">' + year(game.releaseDate) + ' &middot; ' + escapeHtml(game.genres[0]) + '</div></span></a>';
  }

  function wireSearchWidget(input, resultsBox) {
    function run() {
      var q = input.value;
      if (!q.trim()) { resultsBox.classList.remove("open"); resultsBox.innerHTML = ""; return; }
      var matches = searchGames(GAMES, q);
      resultsBox.innerHTML = matches.length === 0
        ? '<div class="nav-search-empty">No matches for &ldquo;' + escapeHtml(q) + '&rdquo;.</div>'
        : matches.map(resultRowHTML).join("");
      resultsBox.classList.add("open");
    }
    input.addEventListener("input", run);
    input.addEventListener("focus", function () { if (input.value.trim()) resultsBox.classList.add("open"); });
    document.addEventListener("click", function (e) {
      if (!resultsBox.contains(e.target) && e.target !== input) resultsBox.classList.remove("open");
    });
  }

  function animateCounters(scope) {
    var els = (scope || document).querySelectorAll("[data-count]");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);
        var target = parseFloat(el.dataset.count);
        var dur = 1100, start = performance.now();
        function tick(now) {
          var p = Math.min(1, (now - start) / dur);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased);
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  function initParticles(canvasHost) {
    if (!canvasHost || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    canvasHost.innerHTML = "";
    var canvas = document.createElement("canvas");
    canvasHost.appendChild(canvas);
    var ctx = canvas.getContext("2d");
    var w, h, particles;
    function resize() {
      w = canvas.width = canvasHost.clientWidth * devicePixelRatio;
      h = canvas.height = canvasHost.clientHeight * devicePixelRatio;
      canvas.style.width = "100%"; canvas.style.height = "100%";
    }
    function makeParticles() {
      var count = Math.min(70, Math.floor((w * h) / 46000));
      particles = Array.from({ length: count }, function () {
        return { x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.6 + 0.4,
          vx: (Math.random() - 0.5) * 0.15, vy: (Math.random() - 0.5) * 0.15, a: Math.random() * 0.5 + 0.15 };
      });
    }
    function frame() {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#7c8cff";
      particles.forEach(function (p) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;
        ctx.globalAlpha = p.a;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r * devicePixelRatio, 0, Math.PI * 2); ctx.fill();
      });
      ctx.globalAlpha = 1;
      requestAnimationFrame(frame);
    }
    resize(); makeParticles();
    window.addEventListener("resize", function () { resize(); makeParticles(); });
    requestAnimationFrame(frame);
  }

  // ---------- views ----------
  function viewHome() {
    var trending = GAMES.slice(0, 12);
    var genres = Array.from(new Set(GAMES.flatMap(function (g) { return g.genres; }))).sort();
    var platforms = Array.from(new Set(GAMES.flatMap(function (g) { return g.platforms; })));
    var earliest = GAMES.reduce(function (a, b) { return a.releaseDate < b.releaseDate ? a : b; }).releaseDate.slice(0, 4);

    app.innerHTML =
      '<section class="hero">' +
        '<div class="hero-bg" id="particles-host"></div>' +
        '<div class="container">' +
          '<p class="hero-eyebrow">50 games &middot; walkthroughs &amp; story</p>' +
          '<h1>Every walkthrough. <span class="grad">Every story.</span> One codex.</h1>' +
          '<p class="lead">Search top-rated YouTube walkthroughs and hand-written story summaries for 50 of gaming\\'s biggest titles &mdash; from this year\\'s releases back to the classics that defined their genres.</p>' +
          '<div class="search-hero">' +
            '<form id="hero-search-form" role="search">' +
              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>' +
              '<input type="search" id="hero-search-input" placeholder="Search by title, genre, or platform&hellip;" aria-label="Search games" autocomplete="off">' +
              '<button type="submit">Search</button>' +
            '</form>' +
            '<div class="search-hero-results" id="hero-search-results"></div>' +
          '</div>' +
          '<div class="stat-row">' +
            '<div class="stat-item"><div class="stat-num" data-count="' + GAMES.length + '">0</div><div class="stat-label">Games covered</div></div>' +
            '<div class="stat-item"><div class="stat-num" data-count="' + genres.length + '">0</div><div class="stat-label">Genres &amp; sub-genres</div></div>' +
            '<div class="stat-item"><div class="stat-num" data-count="' + platforms.length + '">0</div><div class="stat-label">Platforms indexed</div></div>' +
            '<div class="stat-item"><div class="stat-num" data-count="' + earliest + '">0</div><div class="stat-label">Earliest release year</div></div>' +
          '</div>' +
        '</div>' +
      '</section>' +
      '<section class="section"><div class="container">' +
        '<div class="section-head"><div><h2>Trending now</h2><p>Hover any tile for a muted preview &mdash; click through for the full walkthrough and story.</p></div><a class="see-all" href="javascript:void(0)" data-nav="/browse">Browse all games &rarr;</a></div>' +
        '<div class="grid" id="trending-grid"></div>' +
      '</div></section>' +
      '<section class="section" style="padding-top:0;"><div class="container">' +
        '<div class="section-head"><div><h2>Browse by genre</h2><p>Jump straight into a category.</p></div></div>' +
        '<div class="filter-row" id="genre-chip-row">' + genres.map(function (g) {
          return '<a class="filter-pill" href="javascript:void(0)" data-nav="/browse?genre=' + encodeURIComponent(g) + '">' + g + '</a>';
        }).join("") + '</div>' +
      '</div></section>';

    renderGrid(document.getElementById("trending-grid"), trending);
    initParticles(document.getElementById("particles-host"));
    animateCounters(app);
    wireSearchWidget(document.getElementById("hero-search-input"), document.getElementById("hero-search-results"));
    document.getElementById("hero-search-form").addEventListener("submit", function (e) {
      e.preventDefault();
      var q = document.getElementById("hero-search-input").value.trim();
      window.location.hash = "#/browse" + (q ? "?q=" + encodeURIComponent(q) : "");
    });
  }

  function viewBrowse(qs) {
    var params = new URLSearchParams(qs || "");
    var state = { q: params.get("q") || "", genre: params.get("genre") || "", platform: "", sort: "date-desc" };

    app.innerHTML =
      '<section class="section" style="padding-bottom:0;"><div class="container">' +
        '<div class="section-head"><div><h2>Browse the hub</h2><p>Live search across all 50 titles &mdash; filters apply instantly, no reload.</p></div></div>' +
        '<div class="browse-toolbar">' +
          '<div class="browse-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>' +
            '<input type="search" id="browse-search-input" placeholder="Search by title, genre, developer&hellip;" aria-label="Search games" autocomplete="off"></div>' +
          '<div class="select-wrap"><select id="platform-select" aria-label="Filter by platform"><option value="">All platforms</option></select></div>' +
          '<div class="select-wrap"><select id="sort-select" aria-label="Sort games">' +
            '<option value="date-desc">Newest first</option><option value="date-asc">Oldest first</option>' +
            '<option value="az">Title A&ndash;Z</option><option value="za">Title Z&ndash;A</option></select></div>' +
        '</div>' +
        '<div class="filter-row" id="genre-filter-row"></div>' +
        '<p class="browse-count" id="result-count"></p>' +
      '</div></section>' +
      '<section class="section" style="padding-top:0;"><div class="container"><div class="grid" id="browse-grid"></div></div></section>';

    var searchInput = document.getElementById("browse-search-input");
    var platformSelect = document.getElementById("platform-select");
    var sortSelect = document.getElementById("sort-select");
    var genreRow = document.getElementById("genre-filter-row");
    var grid = document.getElementById("browse-grid");
    var countEl = document.getElementById("result-count");
    searchInput.value = state.q;

    function render() {
      var q = state.q.trim().toLowerCase();
      var filtered = GAMES.filter(function (g) {
        var matchesQ = !q || g.title.toLowerCase().indexOf(q) !== -1 ||
          g.genres.some(function (x) { return x.toLowerCase().indexOf(q) !== -1; }) ||
          g.developer.toLowerCase().indexOf(q) !== -1;
        var matchesGenre = !state.genre || g.genres.indexOf(state.genre) !== -1;
        var matchesPlatform = !state.platform || g.platforms.indexOf(state.platform) !== -1;
        return matchesQ && matchesGenre && matchesPlatform;
      });
      filtered.sort(function (a, b) {
        if (state.sort === "az") return a.title.localeCompare(b.title);
        if (state.sort === "za") return b.title.localeCompare(a.title);
        return state.sort === "date-desc" ? (a.releaseDate < b.releaseDate ? 1 : -1) : (a.releaseDate > b.releaseDate ? 1 : -1);
      });
      countEl.textContent = filtered.length + (filtered.length === 1 ? " game" : " games") +
        (state.q || state.genre || state.platform ? " matching your filters." : " in the hub.");
      renderGrid(grid, filtered);
    }

    var platforms = Array.from(new Set(GAMES.flatMap(function (g) { return g.platforms; }))).sort();
    platforms.forEach(function (p) {
      var opt = document.createElement("option"); opt.value = p; opt.textContent = p; platformSelect.appendChild(opt);
    });
    if (params.get("platform")) { platformSelect.value = params.get("platform"); state.platform = params.get("platform"); }

    var genres = Array.from(new Set(GAMES.flatMap(function (g) { return g.genres; }))).sort();
    function renderGenreRow() {
      genreRow.innerHTML = ['<button class="filter-pill' + (state.genre === "" ? " active" : "") + '" data-genre="">All genres</button>']
        .concat(genres.map(function (g) { return '<button class="filter-pill' + (state.genre === g ? " active" : "") + '" data-genre="' + g + '">' + g + '</button>'; }))
        .join("");
      genreRow.querySelectorAll(".filter-pill").forEach(function (btn) {
        btn.addEventListener("click", function () { state.genre = btn.dataset.genre; renderGenreRow(); render(); });
      });
    }
    renderGenreRow();
    render();

    searchInput.addEventListener("input", function () { state.q = searchInput.value; render(); });
    platformSelect.addEventListener("change", function () { state.platform = platformSelect.value; render(); });
    sortSelect.addEventListener("change", function () { state.sort = sortSelect.value; render(); });
  }

  function viewGame(slug) {
    var game = GAMES.find(function (g) { return g.slug === slug; });
    if (!game) { app.innerHTML = '<div class="section container"><div class="no-results"><strong>Game not found.</strong><a href="javascript:void(0)" data-nav="/browse">Back to browse</a></div></div>'; return; }

    function langButtons(lore) {
      return ["en", "de", "es", "fr"].map(function (code) {
        var labels = { en: "EN", de: "DE", es: "ES", fr: "FR" };
        var has = !!(lore[code] || "").trim();
        var active = code === "en" ? " active" : "";
        var disabled = (has || code === "en") ? "" : " disabled";
        return '<button type="button" data-lang="' + code + '" class="lang-btn' + active + '"' + disabled + '>' + labels[code] + '</button>';
      }).join("");
    }
    function lorePanels(lore) {
      var names = { de: "German", es: "Spanish", fr: "French" };
      return ["en", "de", "es", "fr"].map(function (code) {
        var text = (lore[code] || "").trim();
        var display = code === "en" ? "block" : "none";
        if (text) return '<p class="lore-text" data-lang-panel="' + code + '" style="display:' + display + '">' + escapeHtml(text) + '</p>';
        return '<p class="lore-text" data-lang-panel="' + code + '" style="display:' + display + '"><em>' + names[code] + ' translation coming soon &mdash; this summary is currently only available in English.</em></p>';
      }).join("");
    }
    function fullStoryHTML(game) {
      if (!game.storySections || !game.storySections.length) return "";
      var items = game.storySections.map(function (s) {
        return '<div class="story-section"><h4>' + escapeHtml(s.heading) + '</h4><p>' + escapeHtml(s.text) + '</p></div>';
      }).join("");
      return '<details class="story-card" style="margin-top:20px;">' +
        '<summary><span class="story-card-title">Full story &mdash; major spoilers</span><span class="story-card-hint">Tap to reveal the complete plot</span></summary>' +
        '<div class="story-card-body">' + items + '</div>' +
        '</details>';
    }
    function creatorsHTML(game) {
      if (!game.creators || !game.creators.length) return "";
      var cards = game.creators.map(function (c) {
        return '<div class="creator-card">' +
          '<div class="creator-video"><iframe src="https://www.youtube.com/embed/' + c.youtubeId + '?rel=0&modestbranding=1" title="' + escapeHtml(c.videoTitle) + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>' +
          '<div class="creator-caption">' +
            '<span class="creator-name">' + escapeHtml(c.name) + '</span>' +
            '<span class="creator-video-title">' + escapeHtml(c.videoTitle) + '</span>' +
            '<a href="https://www.youtube.com/watch?v=' + c.youtubeId + '" target="_blank" rel="noopener">Watch on YouTube &#8599;</a>' +
          '</div>' +
        '</div>';
      }).join("");
      return '<div class="creators-card" style="margin-top:20px;"><h2>More from top creators</h2><div class="creators-grid">' + cards + '</div></div>';
    }

    app.innerHTML =
      '<section class="game-hero" style="--accent:' + game.accent + ';--accent2:' + game.accent2 + '">' +
        '<div class="game-hero-bg" style="background:radial-gradient(700px 460px at 20% 0%, ' + game.accent + '55, transparent 65%), radial-gradient(600px 460px at 90% 30%, ' + game.accent2 + '44, transparent 65%), var(--bg);"></div>' +
        '<div class="container">' +
          '<p class="breadcrumb"><a href="javascript:void(0)" data-nav="/">Home</a> / <a href="javascript:void(0)" data-nav="/browse">Browse</a> / ' + escapeHtml(game.title) + '</p>' +
          '<div class="game-hero-grid">' +
            '<div class="game-cover' + (game.poster ? ' has-photo' : '') + '" style="--tile-accent:' + game.accent + ';--tile-accent2:' + game.accent2 + '">' +
              (game.poster
                ? '<img class="tile-photo" src="' + game.poster + '" alt="' + escapeHtml(game.title) + ' cover art">' +
                  '<div class="tile-vignette"></div>'
                : '<div class="tile-art-bg"></div>' +
                  '<span class="poster-icon"><svg viewBox="0 0 64 64">' + genreIcon(game.genres[0]) + '</svg></span>' +
                  '<div class="tile-vignette"></div>' +
                  '<span class="poster-badge"><span class="tile-initial">' + initials(game.title) + '</span></span>') +
              '</div>' +
            '<div class="game-title-block">' +
              '<div class="chips">' + game.genres.map(function (g) { return '<span class="chip">' + escapeHtml(g) + '</span>'; }).join("") + '<span class="chip">' + year(game.releaseDate) + '</span></div>' +
              '<h1>' + escapeHtml(game.title) + '</h1>' +
              '<p class="tagline">' + escapeHtml(game.tagline) + '</p>' +
              '<div class="game-meta-list">' +
                '<div>Release date<strong>' + formatDate(game.releaseDate) + '</strong></div>' +
                '<div>Developer<strong>' + escapeHtml(game.developer) + '</strong></div>' +
                '<div>Publisher<strong>' + escapeHtml(game.publisher) + '</strong></div>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</section>' +
      '<section class="section" style="padding-top:0;"><div class="container">' +
        '<div class="game-body-grid" style="--accent:' + game.accent + ';--accent2:' + game.accent2 + '">' +
          '<div>' +
            '<div class="video-wrap"><div id="yt-player-main"></div></div>' +
            '<div class="video-caption"><span>Top walkthrough: ' + escapeHtml(game.youtube.title) + '</span><a href="https://www.youtube.com/watch?v=' + game.youtube.id + '" target="_blank" rel="noopener">Watch on YouTube &#8599;</a></div>' +
            '<div class="lore-card" style="margin-top:34px;">' +
              '<div class="lore-head"><h2>Story &amp; lore</h2><div class="lang-switch" role="group" aria-label="Language">' + langButtons(game.lore) + '</div></div>' +
              lorePanels(game.lore) +
              '<p class="lore-note" data-lore-note>Translations are written by hand, not machine-translated &mdash; new languages are added over time.</p>' +
            '</div>' +
            fullStoryHTML(game) +
            creatorsHTML(game) +
          '</div>' +
          '<aside>' +
            '<div class="side-card"><h3>Platforms</h3><div class="platform-tags">' + game.platforms.map(function (p) { return '<span>' + escapeHtml(p) + '</span>'; }).join("") + '</div></div>' +
            '<div class="side-card"><h3>Details</h3><ul>' +
              '<li><span>Genre</span><strong>' + escapeHtml(game.genres[0]) + '</strong></li>' +
              '<li><span>Released</span><strong>' + formatDate(game.releaseDate) + '</strong></li>' +
              '<li><span>Developer</span><strong>' + escapeHtml(game.developer) + '</strong></li>' +
              '<li><span>Publisher</span><strong>' + escapeHtml(game.publisher) + '</strong></li>' +
            '</ul></div>' +
          '</aside>' +
        '</div>' +
        '<div class="related-strip"><div class="section-head"><div><h2>More like this</h2><p>Other games in ' + escapeHtml(game.genres[0]) + '.</p></div></div><div class="grid" id="related-grid"></div></div>' +
      '</div></section>';

    document.querySelectorAll(".lang-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (btn.disabled) return;
        document.querySelectorAll(".lang-btn").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        var lang = btn.dataset.lang;
        document.querySelectorAll("[data-lang-panel]").forEach(function (p) { p.style.display = (p.dataset.langPanel === lang) ? "block" : "none"; });
        document.querySelector("[data-lore-note]").classList.toggle("show", lang !== "en");
      });
    });

    var related = GAMES.filter(function (g) { return g.slug !== slug && g.genres.indexOf(game.genres[0]) !== -1; }).slice(0, 4);
    if (related.length < 4) {
      var more = GAMES.filter(function (g) { return g.slug !== slug && related.indexOf(g) === -1; }).slice(0, 4 - related.length);
      related = related.concat(more);
    }
    renderGrid(document.getElementById("related-grid"), related);
    wireTilt(document.querySelector(".game-hero-grid"));
    mountYouTubePlayer("yt-player-main", game.youtube.id);
    window.scrollTo(0, 0);
  }

  // ---------- router ----------
  function route() {
    var hash = window.location.hash.replace(/^#/, "") || "/";
    var qIndex = hash.indexOf("?");
    var path = qIndex === -1 ? hash : hash.slice(0, qIndex);
    var qs = qIndex === -1 ? "" : hash.slice(qIndex + 1);

    document.querySelectorAll(".nav-links a").forEach(function (a) { a.classList.remove("active"); });

    if (path === "/" || path === "") {
      document.querySelector('[data-route="home"]').classList.add("active");
      document.documentElement.style.setProperty("--accent", "#7c8cff");
      document.documentElement.style.setProperty("--accent2", "#3ee6c4");
      viewHome();
    } else if (path === "/browse") {
      document.querySelector('[data-route="browse"]').classList.add("active");
      document.documentElement.style.setProperty("--accent", "#7c8cff");
      document.documentElement.style.setProperty("--accent2", "#3ee6c4");
      viewBrowse(qs);
    } else if (path.indexOf("/game/") === 0) {
      var slug = path.slice("/game/".length);
      var g = GAMES.find(function (x) { return x.slug === slug; });
      document.documentElement.style.setProperty("--accent", g ? g.accent : "#7c8cff");
      document.documentElement.style.setProperty("--accent2", g ? g.accent2 : "#3ee6c4");
      viewGame(slug);
    } else {
      viewHome();
    }
  }

  // Internal navigation (nav links, tiles, breadcrumbs, filter pills, ...) uses
  // href="javascript:void(0)" + a data-nav="/path" attribute instead of a real
  // href="#/path". A bare "#/..." anchor resolves against the DOCUMENT'S BASE
  // URL when clicked -- and when this preview is embedded via an iframe with
  // no explicit <base>, that base can be inherited from the surrounding page,
  // so the click can escape the preview entirely instead of just changing the
  // hash. Routing everything through this delegated click handler sidesteps
  // that: it only ever touches window.location.hash directly, which is always
  // a same-document operation regardless of how the page is embedded.
  document.addEventListener("click", function (e) {
    var skipEl = e.target.closest("[data-skip]");
    if (skipEl) {
      e.preventDefault();
      var target = document.getElementById(skipEl.getAttribute("data-skip"));
      if (target) {
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus();
        target.scrollIntoView();
      }
      return;
    }
    var navEl = e.target.closest("[data-nav]");
    if (navEl) {
      e.preventDefault();
      var path = navEl.getAttribute("data-nav");
      var current = window.location.hash.replace(/^#/, "") || "/";
      if (current === path) { route(); } else { window.location.hash = path; }
    }
  }, true);

  window.addEventListener("hashchange", route);
  wireSearchWidget(document.getElementById("nav-search-input"), document.getElementById("nav-search-results"));
  route();
})();
</script>
"""


def main():
    out = HTML.replace("__CSS__", CSS).replace("__GAMES_JSON__", GAMES_JSON)
    out_path = os.path.join(ROOT, "preview", "site-preview.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print("Wrote", out_path, len(out), "bytes")


if __name__ == "__main__":
    main()
