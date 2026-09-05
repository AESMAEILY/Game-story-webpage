#!/usr/bin/env python3
"""
Digi-games — static page generator.

Regenerates games/<slug>.html for every entry in data/games.json.

USAGE
  1. Edit data/games.json — add, remove, or update a game entry (see
     README.md for the field reference and how to add a new title).
  2. From the project root, run:  python3 scripts/generate_pages.py
  3. The games/ folder is fully rewritten from the JSON. Nothing else
     (index.html, browse.html, css/, js/) is touched by this script.

This keeps data/games.json as the single source of truth: the JSON is
also fetched client-side by index.html and browse.html, so editing it
once updates the home page, the browse grid, AND regenerates the
per-game static pages together.
"""
import json
import os
import re
import html
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "games.json")
OUT_DIR = os.path.join(ROOT, "games")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genre_icons import icon_for  # noqa: E402

LANG_LABELS = {"en": "EN", "de": "DE", "es": "ES", "fr": "FR"}
LANG_NAMES = {"en": "English", "de": "German", "es": "Spanish", "fr": "French"}

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Crect width='100' height='100' rx='26' fill='%23{accent}'/%3E"
           "%3Ctext x='50' y='65' font-size='42' font-weight='700' text-anchor='middle' font-family='Arial' fill='%2306060a'%3E"
           "DG%3C/text%3E%3C/svg%3E")


def esc(s):
    return html.escape(str(s), quote=True)


def initials(title):
    words = re.sub(r"[^A-Za-z0-9 ]", "", title).split()
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def format_date(iso):
    from datetime import datetime
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%B %-d, %Y") if os.name != "nt" else d.strftime("%B %d, %Y")


def lang_buttons(lore):
    btns = []
    for code in ["en", "de", "es", "fr"]:
        has_text = bool(lore.get(code, "").strip())
        active = " active" if code == "en" else ""
        disabled = "" if has_text or code == "en" else " disabled"
        btns.append(
            f'<button type="button" data-lang="{code}" class="lang-btn{active}"{disabled}>{LANG_LABELS[code]}</button>'
        )
    return "\n          ".join(btns)


def lore_panels(lore):
    panels = []
    for code in ["en", "de", "es", "fr"]:
        text = lore.get(code, "").strip()
        display = "block" if code == "en" else "none"
        if text:
            panels.append(f'<p class="lore-text" data-lang-panel="{code}" style="display:{display}">{esc(text)}</p>')
        else:
            panels.append(
                f'<p class="lore-text" data-lang-panel="{code}" style="display:{display}">'
                f'<em>{LANG_NAMES[code]} translation coming soon — this summary is currently only available in English.</em></p>'
            )
    return "\n          ".join(panels)


def platform_tags(platforms):
    return "".join(f"<span>{esc(p)}</span>" for p in platforms)


def full_story_html(game):
    sections = game.get("storySections")
    if not sections:
        return ""
    items = "\n            ".join(
        f'<div class="story-section"><h4>{esc(s["heading"])}</h4><p>{esc(s["text"])}</p></div>'
        for s in sections
    )
    return (
        '\n        <details class="story-card">\n'
        '          <summary>\n'
        '            <span class="story-card-title">Full story — major spoilers</span>\n'
        '            <span class="story-card-hint">Tap to reveal the complete plot</span>\n'
        '          </summary>\n'
        '          <div class="story-card-body">\n'
        f'            {items}\n'
        '          </div>\n'
        '        </details>'
    )


def creators_html(game):
    creators = game.get("creators")
    if not creators:
        return ""
    cards = "".join(
        '\n          <div class="creator-card">\n'
        '            <div class="creator-video">\n'
        f'              <iframe src="https://www.youtube.com/embed/{c["youtubeId"]}?rel=0&modestbranding=1" '
        f'title="{esc(c["videoTitle"])}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
        'gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>\n'
        '            </div>\n'
        '            <div class="creator-caption">\n'
        f'              <span class="creator-name">{esc(c["name"])}</span>\n'
        f'              <span class="creator-video-title">{esc(c["videoTitle"])}</span>\n'
        f'              <a href="https://www.youtube.com/watch?v={c["youtubeId"]}" target="_blank" rel="noopener">Watch on YouTube ↗</a>\n'
        '            </div>\n'
        '          </div>'
        for c in creators
    )
    return (
        '\n        <div class="creators-card">\n'
        '          <h2>More from top creators</h2>\n'
        f'          <div class="creators-grid">{cards}\n'
        '          </div>\n'
        '        </div>'
    )


def genre_chips(genres):
    return "".join(f'<span class="chip">{esc(g)}</span>' for g in genres)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Walkthrough &amp; Story | Digi-games</title>
<meta name="description" content="{tagline} Top YouTube walkthrough, release info, and story for {title} on Digi-games.">
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/styles.css">
<style>:root {{ --accent: {accent}; --accent2: {accent2}; }}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<nav class="dock-nav" id="dock-nav" aria-label="Primary">
  <a class="dock-brand" href="../index.html" aria-label="Digi-games home">DG</a>
  <div class="dock-links">
    <div class="dock-indicator" id="dock-indicator"></div>
    <a href="../index.html" class="dock-link" data-route="home">
      <svg class="dock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10.5L12 4l9 6.5"/><path d="M5 9.5V20h14V9.5"/><path d="M9 20v-6h6v6"/></svg>
      <span class="dock-label">Home</span>
    </a>
    <a href="../browse.html" class="dock-link" data-route="browse">
      <svg class="dock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>
      <span class="dock-label">Browse</span>
    </a>
    <button type="button" class="dock-link dock-search-toggle" id="dock-search-toggle" aria-label="Search games" aria-haspopup="dialog">
      <svg class="dock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
      <span class="dock-label">Search</span>
    </button>
  </div>
</nav>

<div class="search-overlay" id="search-overlay" role="dialog" aria-modal="true" aria-label="Search games">
  <div class="search-overlay-backdrop" id="search-overlay-backdrop"></div>
  <div class="search-overlay-panel">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
    <input type="search" id="nav-search-input" placeholder="Search games…" aria-label="Search games">
    <button type="button" class="search-overlay-close" id="search-overlay-close" aria-label="Close search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
    <div class="nav-search-results" id="nav-search-results"></div>
  </div>
</div>

<main id="main">
<section class="game-hero">
  <div class="game-hero-bg"></div>
  <div class="container">
    <p class="breadcrumb"><a href="../index.html">Home</a> / <a href="../browse.html">Browse</a> / {title}</p>
    <div class="game-hero-grid">
      <div class="game-cover{cover_class}" style="--tile-accent:{accent};--tile-accent2:{accent2}">
        {cover_html}
      </div>
      <div class="game-title-block">
        <div class="chips">{genre_chips}<span class="chip">{year}</span></div>
        <h1>{title}</h1>
        <p class="tagline">{tagline}</p>
        <div class="game-meta-list">
          <div>Release date<strong>{release_full}</strong></div>
          <div>Developer<strong>{developer}</strong></div>
          <div>Publisher<strong>{publisher}</strong></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0;">
  <div class="container">
    <div class="game-body-grid">
      <div>
        <div class="video-wrap">
          <div id="yt-player-main"></div>
          <noscript><iframe src="https://www.youtube.com/embed/{yt_id}?rel=0&modestbranding=1" title="{yt_title_esc}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></noscript>
        </div>
        <div class="video-caption">
          <span>Top walkthrough: {yt_title_esc}</span>
          <a href="https://www.youtube.com/watch?v={yt_id}" target="_blank" rel="noopener">Watch on YouTube ↗</a>
        </div>

        <div class="lore-card" style="margin-top:34px;">
          <div class="lore-head">
            <h2>Story &amp; lore</h2>
            <div class="lang-switch" role="group" aria-label="Language">
              {lang_buttons}
            </div>
          </div>
          {lore_panels}
          <p class="lore-note" data-lore-note>Translations are written by hand, not machine-translated — new languages are added over time.</p>
        </div>
        {full_story_html}
        {creators_html}
      </div>

      <aside>
        <div class="side-card">
          <h3>Platforms</h3>
          <div class="platform-tags">{platform_tags}</div>
        </div>
        <div class="side-card">
          <h3>Details</h3>
          <ul>
            <li><span>Genre</span><strong>{genre_primary}</strong></li>
            <li><span>Released</span><strong>{release_full}</strong></li>
            <li><span>Developer</span><strong>{developer}</strong></li>
            <li><span>Publisher</span><strong>{publisher}</strong></li>
          </ul>
        </div>
      </aside>
    </div>

    <div class="related-strip">
      <div class="section-head">
        <div>
          <h2>More like this</h2>
          <p>Other games in {genre_primary}.</p>
        </div>
      </div>
      <div class="grid" id="related-grid"><div class="no-results">Loading…</div></div>
    </div>
  </div>
</section>
</main>

<footer class="site-footer">
  <div class="container">
    <span>Digi-games — a fan-made hub for walkthroughs, story, and everything you need to play. Videos embedded via YouTube; all game titles and art are property of their respective publishers.</span>
    <span>&copy; 2026 Alireza Esmaeily. All rights reserved. This site's design and code are proprietary — see <a href="https://github.com/AESMAEILY/GameStoryHub/blob/main/LICENSE" target="_blank" rel="noopener">LICENSE</a>.</span>
    <span><a href="../browse.html">Browse all games</a></span>
  </div>
</footer>

<script>window.GC_ROOT = "../";</script>
<script src="../js/site.js"></script>
<script>
(function () {{
  var SLUG = "{slug}";
  var PRIMARY_GENRE = "{genre_primary_js}";

  GameCodex.initDockNav();

  document.querySelectorAll(".lang-btn").forEach(function (btn) {{
    btn.addEventListener("click", function () {{
      if (btn.disabled) return;
      document.querySelectorAll(".lang-btn").forEach(function (b) {{ b.classList.remove("active"); }});
      btn.classList.add("active");
      var lang = btn.dataset.lang;
      document.querySelectorAll("[data-lang-panel]").forEach(function (p) {{
        p.style.display = (p.dataset.langPanel === lang) ? "block" : "none";
      }});
      var note = document.querySelector("[data-lore-note]");
      note.classList.toggle("show", lang !== "en");
    }});
  }});

  GameCodex.ready.then(function (games) {{
    var related = games.filter(function (g) {{ return g.slug !== SLUG && g.genres.indexOf(PRIMARY_GENRE) !== -1; }}).slice(0, 4);
    if (related.length < 4) {{
      var more = games.filter(function (g) {{ return g.slug !== SLUG && related.indexOf(g) === -1; }}).slice(0, 4 - related.length);
      related = related.concat(more);
    }}
    GameCodex.renderGrid(document.getElementById("related-grid"), related);

    GameCodex.wireSearchWidget(
      document.getElementById("nav-search-input"),
      document.getElementById("nav-search-results")
    );
  }});

  GameCodex.wireTilt(document.querySelector(".game-hero-grid"));
  GameCodex.mountYouTubePlayer("yt-player-main", "{yt_id}");
}})();
</script>
</body>
</html>
"""


def cover_html(game):
    poster = game.get("poster")
    if poster:
        return (
            f'<img class="tile-photo" src="../{poster}" alt="{esc(game["title"])} cover art" loading="lazy" decoding="async">\n'
            f'        <div class="tile-vignette"></div>'
        )
    return (
        f'<div class="tile-art-bg"></div>\n'
        f'        <span class="poster-icon"><svg viewBox="0 0 64 64">{icon_for(game["genres"][0])}</svg></span>\n'
        f'        <div class="tile-vignette"></div>\n'
        f'        <span class="poster-badge"><span class="tile-initial">{initials(game["title"])}</span></span>'
    )


def build_page(game):
    accent = game["accent"].lstrip("#")
    return PAGE_TEMPLATE.format(
        title=esc(game["title"]),
        tagline=esc(game["tagline"]),
        favicon=FAVICON.format(accent=accent),
        accent=game["accent"],
        accent2=game["accent2"],
        initials=initials(game["title"]),
        cover_class=" has-photo" if game.get("poster") else "",
        cover_html=cover_html(game),
        genre_chips=genre_chips(game["genres"]),
        year=game["releaseDate"][:4],
        release_full=format_date(game["releaseDate"]),
        developer=esc(game["developer"]),
        publisher=esc(game["publisher"]),
        yt_id=game["youtube"]["id"],
        yt_title_esc=esc(game["youtube"]["title"]),
        lang_buttons=lang_buttons(game["lore"]),
        lore_panels=lore_panels(game["lore"]),
        full_story_html=full_story_html(game),
        creators_html=creators_html(game),
        platform_tags=platform_tags(game["platforms"]),
        genre_primary=esc(game["genres"][0]),
        genre_primary_js=game["genres"][0].replace('"', '\\"'),
        slug=game["slug"],
    )


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        games = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)
    # clear stale generated pages (anything not in the current dataset)
    valid_files = {g["slug"] + ".html" for g in games}
    for existing in os.listdir(OUT_DIR):
        if existing.endswith(".html") and existing not in valid_files and not existing.startswith("_"):
            os.remove(os.path.join(OUT_DIR, existing))

    for game in games:
        out_path = os.path.join(OUT_DIR, game["slug"] + ".html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(build_page(game))

    print(f"Generated {len(games)} game pages in {OUT_DIR}/")


if __name__ == "__main__":
    main()
