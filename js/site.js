/* =========================================================
   Digi-games — shared site logic
   Works off data/games.json (client-side only, no backend).
   Every page includes this file and sets:
     window.GC_ROOT = "./"   (pages at site root: index.html, browse.html)
     window.GC_ROOT = "../"  (pages under /games/*.html)
   ========================================================= */

(function () {
  "use strict";

  const ROOT = window.GC_ROOT || "./";
  const DATA_URL = ROOT + "data/games.json";

  const GC = {
    games: [],
    ready: null,
  };
  window.GameCodex = GC;

  GC.ready = fetch(DATA_URL)
    .then((r) => {
      if (!r.ok) throw new Error("Failed to load games.json: " + r.status);
      return r.json();
    })
    .then((games) => {
      GC.games = games;
      document.dispatchEvent(new CustomEvent("gc:data-ready", { detail: games }));
      return games;
    })
    .catch((err) => {
      console.error("[GameCodex] Could not load game data.", err);
      document.dispatchEvent(new CustomEvent("gc:data-error", { detail: err }));
      return [];
    });

  // ---------- helpers ----------
  function gamePath(slug) {
    return ROOT + "games/" + slug + ".html";
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function initials(title) {
    const words = title.replace(/[^A-Za-z0-9 ]/g, "").split(" ").filter(Boolean);
    if (words.length === 0) return "?";
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
    return (words[0][0] + words[1][0]).toUpperCase();
  }

  function formatDate(iso) {
    const d = new Date(iso + "T00:00:00Z");
    return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  }

  function year(iso) { return iso.slice(0, 4); }

  GC.util = { gamePath, escapeHtml, initials, formatDate, year };

  // ---------- poster watermark icons ----------
  // Simple original line-icons, one concept per genre — see scripts/genre_icons.py
  // for the canonical source (mirrored here for client-side rendering).
  const GENRE_ICONS = {
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
  function genreIcon(genre) {
    return GENRE_ICONS[genre] || GENRE_ICONS["Action Adventure"];
  }

  // ---------- tile rendering ----------
  // mode: "grid" (default tiles) — used on home trending + browse
  function posterArtHTML(game) {
    if (game.poster) {
      return `<img class="tile-photo" src="${ROOT}${game.poster}" alt="${escapeHtml(game.title)} cover art" loading="lazy" decoding="async">
          <div class="tile-vignette"></div>
          <div class="tile-shine"></div>`;
    }
    return `<div class="tile-art-bg"></div>
          <span class="poster-icon"><svg viewBox="0 0 64 64">${genreIcon(game.genres[0])}</svg></span>
          <div class="tile-vignette"></div>
          <div class="tile-shine"></div>
          <span class="poster-badge"><span class="tile-initial">${initials(game.title)}</span></span>`;
  }

  function tileHTML(game) {
    const yt = game.youtube;
    return `
    <article class="tile reveal" data-slug="${game.slug}" style="--tile-accent:${game.accent};--tile-accent2:${game.accent2}">
      <a class="tile-media" href="${gamePath(game.slug)}" data-yt="${yt.id}" aria-label="Open ${escapeHtml(game.title)}">
        <span class="tile-genre-badge">${escapeHtml(game.genres[0])}</span>
        <div class="tile-art${game.poster ? " has-photo" : ""}">
          ${posterArtHTML(game)}
        </div>
        <iframe class="tile-preview" tabindex="-1" title="" data-id="${yt.id}"></iframe>
        <span class="play-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </span>
      </a>
      <div class="tile-body">
        <a href="${gamePath(game.slug)}">
          <h3 class="tile-title">${escapeHtml(game.title)}</h3>
        </a>
        <div class="tile-meta">
          <span>${year(game.releaseDate)}</span>
          <span class="dot">&middot;</span>
          <span>${escapeHtml(game.platforms[0])}${game.platforms.length > 1 ? " +" + (game.platforms.length - 1) : ""}</span>
        </div>
      </div>
    </article>`;
  }

  function renderGrid(container, games) {
    if (!container) return;
    if (games.length === 0) {
      container.innerHTML = `<div class="no-results"><strong>No games matched.</strong>Try a different title, genre, or platform.</div>`;
      return;
    }
    container.innerHTML = games.map(tileHTML).join("");
    wireHoverPreviews(container);
    wireTilt(container);
    wireReveal(container);
  }
  GC.renderGrid = renderGrid;
  GC.genreIcon = genreIcon;
  GC.posterArtHTML = posterArtHTML;

  // ---------- pointer-tilt on poster art ----------
  function wireTilt(scope) {
    const medias = (scope || document).querySelectorAll(".tile-media, .game-cover");
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    medias.forEach((media) => {
      media.addEventListener("pointermove", (e) => {
        if (e.pointerType === "touch") return;
        const rect = media.getBoundingClientRect();
        const px = (e.clientX - rect.left) / rect.width - 0.5;
        const py = (e.clientY - rect.top) / rect.height - 0.5;
        media.style.setProperty("--ry", (px * 14).toFixed(2) + "deg");
        media.style.setProperty("--rx", (py * -14).toFixed(2) + "deg");
      });
      media.addEventListener("pointerleave", () => {
        media.style.setProperty("--rx", "0deg");
        media.style.setProperty("--ry", "0deg");
      });
    });
  }
  GC.wireTilt = wireTilt;

  // ---------- scroll-reveal for grid tiles ----------
  function wireReveal(scope) {
    const els = (scope || document).querySelectorAll(".reveal");
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      els.forEach((el) => el.classList.add("in"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        entry.target.classList.add("in");
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    els.forEach((el, i) => {
      el.style.transitionDelay = Math.min(i % 12, 8) * 35 + "ms";
      io.observe(el);
    });
  }
  GC.wireReveal = wireReveal;

  // ---------- hover-preview (muted autoplay YouTube on hover) ----------
  function wireHoverPreviews(scope) {
    const medias = (scope || document).querySelectorAll(".tile-media[data-yt]");
    medias.forEach((media) => {
      const iframe = media.querySelector(".tile-preview");
      let timer = null;
      media.addEventListener("mouseenter", () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          const id = iframe.dataset.id;
          if (!iframe.src) {
            iframe.src = `https://www.youtube.com/embed/${id}?autoplay=1&mute=1&loop=1&playlist=${id}&controls=0&modestbranding=1&playsinline=1&rel=0`;
          }
          iframe.classList.add("active");
        }, 320); // small delay so casual mouse passes don't spin up video
      });
      media.addEventListener("mouseleave", () => {
        clearTimeout(timer);
        iframe.classList.remove("active");
        iframe.src = ""; // stop playback/loading entirely
      });
    });
  }
  GC.wireHoverPreviews = wireHoverPreviews;

  // ---------- main video player (official YouTube IFrame Player API) ----------
  // Loads the real https://www.youtube.com/iframe_api script once, then mounts
  // YT.Player instances on demand. Playback happens fully inside our page via
  // postMessage — nothing here ever navigates the top-level page to youtube.com.
  // (YouTube's own player chrome still shows its small logo/title as a link,
  // per YouTube's platform terms — that one element can't be removed by any
  // embed method, API-driven or not. Everything else — play, pause, the whole
  // watch experience — stays on this page.)
  let ytApiPromise = null;
  function loadYouTubeApi() {
    if (ytApiPromise) return ytApiPromise;
    ytApiPromise = new Promise((resolve) => {
      if (window.YT && window.YT.Player) { resolve(window.YT); return; }
      const prevReady = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function () {
        if (typeof prevReady === "function") prevReady();
        resolve(window.YT);
      };
      if (!document.querySelector('script[src="https://www.youtube.com/iframe_api"]')) {
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        document.head.appendChild(tag);
      }
    });
    return ytApiPromise;
  }

  // mountId: id of an empty element to mount the player into (replaced in place).
  function mountYouTubePlayer(mountId, videoId, opts) {
    const el = document.getElementById(mountId);
    if (!el) return null;
    let player = null;
    loadYouTubeApi().then((YT) => {
      // element may have been removed already (SPA nav away before API loaded)
      if (!document.getElementById(mountId)) return;
      const playerVars = { rel: 0, modestbranding: 1, playsinline: 1, enablejsapi: 1 };
      if (window.location.origin && window.location.origin.indexOf("http") === 0) {
        playerVars.origin = window.location.origin;
      }
      player = new YT.Player(mountId, {
        videoId: videoId,
        playerVars: Object.assign(playerVars, opts || {}),
      });
    });
    return { destroy: () => { if (player && player.destroy) player.destroy(); } };
  }
  GC.mountYouTubePlayer = mountYouTubePlayer;

  // ---------- search (shared logic for nav + hero + browse) ----------
  function searchGames(games, query) {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return games.filter((g) => {
      return (
        g.title.toLowerCase().includes(q) ||
        g.genres.some((x) => x.toLowerCase().includes(q)) ||
        g.platforms.some((x) => x.toLowerCase().includes(q)) ||
        g.developer.toLowerCase().includes(q)
      );
    }).slice(0, 8);
  }
  GC.searchGames = searchGames;

  function resultRowHTML(game) {
    return `<a href="${gamePath(game.slug)}" style="--tile-accent:${game.accent}">
      <span class="swatch" style="background:linear-gradient(135deg, ${game.accent}, ${game.accent2})"></span>
      <span>
        <div>${escapeHtml(game.title)}</div>
        <div class="meta">${year(game.releaseDate)} &middot; ${escapeHtml(game.genres[0])}</div>
      </span>
    </a>`;
  }

  // Wire up any [data-search-input] + [data-search-results] pair once data is ready
  function wireSearchWidget(input, resultsBox, opts) {
    opts = opts || {};
    function run() {
      const q = input.value;
      if (!q.trim()) {
        resultsBox.classList.remove("open");
        resultsBox.innerHTML = "";
        return;
      }
      const matches = searchGames(GC.games, q);
      if (matches.length === 0) {
        resultsBox.innerHTML = `<div class="nav-search-empty">No matches for “${escapeHtml(q)}”.</div>`;
      } else {
        resultsBox.innerHTML = matches.map(resultRowHTML).join("");
      }
      resultsBox.classList.add("open");
    }
    input.addEventListener("input", run);
    input.addEventListener("focus", () => { if (input.value.trim()) resultsBox.classList.add("open"); });
    document.addEventListener("click", (e) => {
      if (!resultsBox.contains(e.target) && e.target !== input) {
        resultsBox.classList.remove("open");
      }
    });
    if (opts.form) {
      opts.form.addEventListener("submit", (e) => {
        e.preventDefault();
        const q = input.value.trim();
        window.location.href = ROOT + "browse.html" + (q ? "?q=" + encodeURIComponent(q) : "");
      });
    }
  }
  GC.wireSearchWidget = wireSearchWidget;

  // ---------- data-backed hero stats (never hand-typed, so they can't go stale) ----------
  function computeStats(games) {
    const studios = new Set(games.map((g) => g.developer)).size;
    const earliestYear = games.reduce((min, g) => Math.min(min, parseInt(g.releaseDate.slice(0, 4), 10)), 9999);
    return { gamesCovered: games.length, studios, earliestYear };
  }
  GC.computeStats = computeStats;

  // No signup mechanism exists yet, so this is a real "0" rather than a
  // computed value -- update it by hand once a subscriber source exists.
  GC.subscriberCount = 0;

  // Generic (non-trademarked) platform-family glyphs: which families a
  // visitor's own platform falls into actually matters; a raw "14 platforms"
  // count does not, so this replaces that with a filtered icon strip instead.
  const PLATFORM_FAMILIES = [
    { key: "pc", label: "PC", test: (s) => s.includes("pc") || s.includes("mac"),
      icon: '<rect x="3" y="5" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 17v3"/>' },
    { key: "playstation", label: "PlayStation", test: (s) => s.startsWith("ps") || s.includes("playstation"),
      icon: '<path d="M6 9c-2 0-3.3 1.6-3.6 4-.3 2.4.5 4.4 2.5 4.4 1.3 0 1.8-1 2.5-2.2.6-1 1-1.3 2-1.3h5c1 0 1.4.3 2 1.3.7 1.2 1.2 2.2 2.5 2.2 2 0 2.8-2 2.5-4.4C21.3 10.6 20 9 18 9Z"/><circle cx="16" cy="8" r=".9" fill="currentColor" stroke="none"/><circle cx="18.3" cy="10" r=".9" fill="currentColor" stroke="none"/>' },
    { key: "xbox", label: "Xbox", test: (s) => s.includes("xbox"),
      icon: '<circle cx="12" cy="9.5" r="4"/><path d="M12 13.5v3M8.2 20h7.6"/>' },
    { key: "nintendo", label: "Nintendo", test: (s) => s.includes("switch") || s.includes("wii"),
      icon: '<rect x="4" y="6" width="16" height="12" rx="3"/><circle cx="8" cy="12" r="1.3"/><circle cx="16" cy="10" r="1" fill="currentColor" stroke="none"/><circle cx="16" cy="14" r="1" fill="currentColor" stroke="none"/>' },
    { key: "mobile", label: "Mobile", test: (s) => s.includes("mobile") || s.includes("ios") || s.includes("android"),
      icon: '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 18h2"/>' },
  ];
  function platformCoverage(games) {
    const all = new Set();
    games.forEach((g) => g.platforms.forEach((p) => all.add(p.toLowerCase())));
    return PLATFORM_FAMILIES.filter((f) => Array.from(all).some((p) => f.test(p)));
  }
  GC.platformCoverage = platformCoverage;

  // ---------- neon-sign dust sparkles for the hero brand lockup ----------
  // Scatters a handful of small twinkling motes across `container` (the
  // .hero-brand wrapper), inspired by the drifting dust around a lit neon
  // sign. Skipped outright under prefers-reduced-motion rather than paused.
  function spawnSparkles(container, count) {
    if (!container) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    count = count || 9;
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const s = document.createElement("span");
      s.className = "brand-sparkle";
      s.setAttribute("aria-hidden", "true");
      s.style.left = (Math.random() * 96 + 2).toFixed(1) + "%";
      s.style.top = (Math.random() * 84 + 8).toFixed(1) + "%";
      s.style.animationDelay = (Math.random() * 2.2).toFixed(2) + "s";
      s.style.animationDuration = (1.8 + Math.random() * 1.6).toFixed(2) + "s";
      frag.appendChild(s);
    }
    container.appendChild(frag);
  }
  GC.spawnSparkles = spawnSparkles;

  // ---------- animated stat counters (+ optional donut-ring sweep) ----------
  // If a [data-count] element sits inside a ".stat-ring", its sibling
  // ".stat-ring-progress" circle sweeps in lockstep with the count-up --
  // full when the target is > 0, left EMPTY when the target is 0 (e.g. an
  // honest "0 subscribers" placeholder) rather than faking a filled ring.
  function animateCounters(scope) {
    const els = (scope || document).querySelectorAll("[data-count]");
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        io.unobserve(el);
        const target = parseFloat(el.dataset.count);
        const decimals = (el.dataset.count.split(".")[1] || "").length;
        const suffix = el.dataset.suffix || "";
        const ring = el.closest(".stat-ring");
        const progress = ring ? ring.querySelector(".stat-ring-progress") : null;
        let circumference = 0;
        if (progress) {
          const r = parseFloat(progress.getAttribute("r")) || 27;
          circumference = 2 * Math.PI * r;
          progress.style.strokeDasharray = String(circumference);
          progress.style.strokeDashoffset = String(circumference);
        }
        const ringFraction = target > 0 ? 1 : 0;
        const dur = 1100;
        const start = performance.now();
        function tick(now) {
          const p = Math.min(1, (now - start) / dur);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (target * eased).toFixed(decimals) + suffix;
          if (progress) progress.style.strokeDashoffset = String(circumference * (1 - eased * ringFraction));
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    els.forEach((el) => io.observe(el));
  }
  GC.animateCounters = animateCounters;

  // ---------- lightweight particle field for hero ----------
  function initParticles(canvasHost) {
    if (!canvasHost) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const canvas = document.createElement("canvas");
    canvasHost.appendChild(canvas);
    const ctx = canvas.getContext("2d");
    let w, h, particles;
    const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#7c8cff";

    function resize() {
      w = canvas.width = canvasHost.clientWidth * devicePixelRatio;
      h = canvas.height = canvasHost.clientHeight * devicePixelRatio;
      canvas.style.width = "100%";
      canvas.style.height = "100%";
    }
    function makeParticles() {
      const count = Math.min(70, Math.floor((w * h) / 46000));
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.6 + 0.4,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
        a: Math.random() * 0.5 + 0.15,
      }));
    }
    function frame() {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = accent;
      particles.forEach((p) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;
        ctx.globalAlpha = p.a;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * devicePixelRatio, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1;
      requestAnimationFrame(frame);
    }
    resize(); makeParticles();
    window.addEventListener("resize", () => { resize(); makeParticles(); });
    requestAnimationFrame(frame);
  }
  GC.initParticles = initParticles;

  // ---------- home hero: coverflow-style featured carousel ----------
  // Renders one absolutely-positioned card per game inside `els.stage`, then
  // animates each card's transform/opacity by its signed distance from the
  // active index (0 = centered/upright, ±1 = tilted side cards, further =
  // hidden just past the edge, ready to slide in). Reuses posterArtHTML so
  // carousel cards look like the same "poster" system as every grid tile.
  function buildCarousel(games, els) {
    if (!els || !els.stage || !games || games.length === 0) return;
    const stage = els.stage, titleEl = els.title, dotsEl = els.dots;
    const root = els.root || stage;
    const N = games.length;
    let current = 0;
    let timer = null;
    let titleSwapTimer = null;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) root.classList.add("motion-ok");

    const cards = games.map((g, i) => {
      const el = document.createElement("div");
      el.className = "carousel-card card-enter";
      el.style.setProperty("--tile-accent", g.accent);
      el.style.setProperty("--tile-accent2", g.accent2);
      el.innerHTML = `<a class="carousel-card-media" href="${gamePath(g.slug)}" aria-label="Open ${escapeHtml(g.title)}" tabindex="-1">
        <div class="tile-art${g.poster ? " has-photo" : ""}">${posterArtHTML(g)}</div>
      </a>`;
      el.addEventListener("click", (e) => {
        if (i !== current) { e.preventDefault(); goTo(i); }
      });
      stage.appendChild(el);
      return el;
    });

    function shortestOffset(i, cur) {
      let d = i - cur;
      if (d > N / 2) d -= N;
      if (d < -N / 2) d += N;
      return d;
    }

    function positionCard(el, i) {
      const off = shortestOffset(i, current);
      const abs = Math.abs(off);
      const dir = off === 0 ? 0 : (off > 0 ? 1 : -1);
      el.style.zIndex = String(10 - abs);
      el.querySelector(".carousel-card-media").tabIndex = abs === 0 ? 0 : -1;
      el.setAttribute("aria-hidden", abs === 0 ? "false" : "true");
      el.classList.toggle("is-active", abs === 0);
      if (abs === 0) {
        el.style.transform = "translateX(-50%) rotateY(0deg) scale(1)";
        el.style.opacity = "1";
      } else if (abs === 1) {
        el.style.transform = `translateX(calc(-50% + ${dir * 68}%)) rotateY(${dir * -32}deg) scale(0.8)`;
        el.style.opacity = "0.55";
      } else {
        el.style.transform = `translateX(calc(-50% + ${dir * 125}%)) rotateY(${dir * -40}deg) scale(0.7)`;
        el.style.opacity = "0";
      }
    }

    function render(animateTitle) {
      cards.forEach(positionCard);
      if (titleEl) {
        if (animateTitle && !reduceMotion) {
          clearTimeout(titleSwapTimer);
          titleEl.classList.add("swap");
          titleSwapTimer = setTimeout(() => {
            titleEl.textContent = games[current].title;
            titleEl.classList.remove("swap");
          }, 200);
        } else {
          titleEl.textContent = games[current].title;
        }
      }
      if (dotsEl) {
        Array.from(dotsEl.children).forEach((d, i) => {
          d.classList.toggle("active", i === current);
          d.setAttribute("aria-current", i === current ? "true" : "false");
        });
      }
    }

    function goTo(i) {
      if (((i % N) + N) % N === current) return;
      current = ((i % N) + N) % N;
      render(true);
      resetAutoplay();
    }
    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    if (dotsEl) {
      dotsEl.innerHTML = games.map((g) => `<button type="button" class="carousel-dot" aria-label="Show ${escapeHtml(g.title)}"></button>`).join("");
      Array.from(dotsEl.children).forEach((d, i) => d.addEventListener("click", () => goTo(i)));
    }
    if (els.prevBtn) els.prevBtn.addEventListener("click", prev);
    if (els.nextBtn) els.nextBtn.addEventListener("click", next);

    stage.setAttribute("tabindex", "0");
    stage.setAttribute("role", "region");
    stage.setAttribute("aria-label", "Featured games carousel");
    stage.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
      if (e.key === "ArrowRight") { e.preventDefault(); next(); }
    });

    function resetAutoplay() {
      clearInterval(timer);
      if (reduceMotion) return;
      timer = setInterval(next, 4800);
    }
    stage.addEventListener("pointerenter", () => clearInterval(timer));
    stage.addEventListener("pointerleave", resetAutoplay);
    stage.addEventListener("focusin", () => clearInterval(timer));
    stage.addEventListener("focusout", resetAutoplay);

    // initial layout while cards are still in their .card-enter (off/faded) state...
    render(false);
    // ...then release the entrance state a frame later so the transition
    // animates from "flown in from below" into its resting coverflow spot,
    // staggered slightly per card for a nicer cascade.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        cards.forEach((el, i) => {
          if (!reduceMotion) {
            el.style.transitionDelay = Math.min(Math.abs(shortestOffset(i, current)), 4) * 60 + "ms";
          }
          el.classList.remove("card-enter");
        });
        setTimeout(() => { cards.forEach((el) => { el.style.transitionDelay = ""; }); }, 900);
      });
    });
    resetAutoplay();
  }
  GC.buildCarousel = buildCarousel;

  // ---------- floating dock nav: sliding indicator + search overlay ----------
  function debounce(fn, wait) {
    let t = null;
    return function () {
      clearTimeout(t);
      const args = arguments;
      t = setTimeout(() => fn.apply(null, args), wait);
    };
  }

  function initDockNav(nav) {
    nav = nav || document.querySelector(".dock-nav");
    if (!nav) return;
    const indicator = nav.querySelector(".dock-indicator");

    function moveIndicator() {
      const active = nav.querySelector(".dock-link.active");
      if (!active || !indicator) return;
      indicator.style.left = active.offsetLeft + "px";
      indicator.style.top = active.offsetTop + "px";
      indicator.style.width = active.offsetWidth + "px";
      indicator.style.height = active.offsetHeight + "px";
      indicator.classList.add("ready");
    }
    moveIndicator();
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(moveIndicator).catch(() => {});
    }
    window.addEventListener("resize", debounce(moveIndicator, 120));
    window.addEventListener("orientationchange", () => setTimeout(moveIndicator, 60));

    const overlay = document.getElementById("search-overlay");
    const overlayBackdrop = document.getElementById("search-overlay-backdrop");
    const overlayClose = document.getElementById("search-overlay-close");
    const overlayInput = document.getElementById("nav-search-input");
    const searchToggle = document.getElementById("dock-search-toggle");

    function openSearch() {
      if (!overlay) return;
      overlay.classList.add("open");
      setTimeout(() => { if (overlayInput) overlayInput.focus(); }, 60);
    }
    function closeSearch() {
      if (!overlay || !overlay.classList.contains("open")) return;
      overlay.classList.remove("open");
      if (searchToggle) searchToggle.focus();
    }
    if (searchToggle) searchToggle.addEventListener("click", openSearch);
    if (overlayBackdrop) overlayBackdrop.addEventListener("click", closeSearch);
    if (overlayClose) overlayClose.addEventListener("click", closeSearch);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && overlay && overlay.classList.contains("open")) closeSearch();
    });

    return { moveIndicator, openSearch, closeSearch };
  }
  GC.initDockNav = initDockNav;
})();
