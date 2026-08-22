/* =========================================================
   GameStoryHub — shared site logic
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

  // ---------- animated stat counters ----------
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
        const dur = 1100;
        const start = performance.now();
        function tick(now) {
          const p = Math.min(1, (now - start) / dur);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (target * eased).toFixed(decimals) + suffix;
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

  // ---------- mobile nav toggle ----------
  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    const links = document.querySelector(".nav-links");
    if (toggle && links) {
      toggle.addEventListener("click", () => links.classList.toggle("open"));
    }
  });
})();
