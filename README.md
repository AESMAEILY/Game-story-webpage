# Digi-games

A static walkthrough &amp; story hub — 50 games, client-side search/filter, hover-preview trending grid, and per-game pages with an embedded top YouTube walkthrough plus a hand-written (not machine-translated) story summary. No backend, no database — everything reads from one JSON file.

## Structure

```
index.html          Home — hero, big search, trending grid
browse.html          Full searchable/filterable grid (title, genre, platform, sort)
games/<slug>.html    One static page per game (generated — see below)
data/games.json      Single source of truth for every game's data
css/styles.css        Shared styles (dark theme, glow accents)
js/site.js            Shared logic: search, filters, hover-preview, particles, counters
scripts/generate_pages.py   Regenerates games/*.html from data/games.json
scripts/_make_data.py       Reference only — how games.json was originally authored
```

## Previewing locally

Because the pages fetch `data/games.json` with `fetch()`, opening `index.html` directly by double-clicking it (`file://…`) will silently fail to load any games — browsers block local-file fetches like that. Run a tiny local server from the project root instead:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

Any static server works the same way (`npx serve`, VS Code's Live Server, etc.).

## Adding, editing, or removing a game

1. Open `data/games.json`. Each entry looks like this:

```json
{
  "slug": "elden-ring",
  "title": "Elden Ring",
  "tagline": "A Tarnished returns to claim the shattered Elden Ring.",
  "releaseDate": "2022-02-25",
  "genres": ["Action RPG"],
  "platforms": ["PC", "PS5", "PS4", "Xbox Series X|S", "Xbox One"],
  "developer": "FromSoftware",
  "publisher": "Bandai Namco",
  "accent": "#a970ff",
  "accent2": "#5b2a9e",
  "youtube": { "id": "WVF4GccrX6E", "title": "ELDEN RING Full Game Walkthrough - No Commentary (4K 60 FPS)" },
  "lore": { "en": "…", "de": "", "es": "", "fr": "" }
}
```

   - `slug` must be unique — it becomes the filename `games/<slug>.html` and the URL.
   - `youtube.id` is the 11-character ID from the video's URL (`youtube.com/watch?v=`**`WVF4GccrX6E`**). Pick the video by searching YouTube for `"<game> full walkthrough no commentary"` and grabbing the best-regarded, most complete result — that's exactly how the current 50 were chosen. No API key needed, it's a plain `<iframe>` embed.
   - `accent` / `accent2` drive that game's glow color on its page and on its tiles everywhere else. Any two hex colors work; picking one from `css/styles.css`'s `GENRE_ACCENT` palette in `scripts/_make_data.py` keeps things consistent.
   - `lore.en` is required. `lore.de` / `lore.es` / `lore.fr` are optional — leave them as `""` and that language's button is automatically greyed out on the game page with a "translation coming soon" note. Fill one in (by hand — not machine translation, so it reads naturally) and the button lights up immediately.
   - There's no cover art file to source or license — every tile and hero banner is a generated gradient + initials, styled from `accent`/`accent2`. That's deliberate: it sidesteps box-art copyright entirely and stays visually consistent. If you'd rather use real key art later, swap `.tile-art` / `.game-cover` in the templates for an `<img>`.

2. Save the file — `index.html` and `browse.html` pick it up immediately on next load, since they fetch the JSON live.
3. Regenerate the static per-game pages:

```bash
python3 scripts/generate_pages.py
```

   This rewrites everything in `games/` from `data/games.json`, including deleting pages for any game you removed. It never touches `index.html`, `browse.html`, `css/`, or `js/`.

### Adding real cover art for a game

By default every tile and hero cover is generated art (a gradient mesh + genre-icon watermark + monogram — see "Notes" below on why). To swap in a real cover image for a specific game:

1. Drop a portrait image (roughly 2:3, e.g. 800×1200) into `assets/posters/`, named after the game's `slug` — e.g. `assets/posters/hades-2.jpg`. A landscape/banner image works too; the site letterboxes it instead of cropping it.
2. Add a `"poster"` field to that game's entry in `data/games.json`, pointing at the file: `"poster": "assets/posters/hades-2.jpg"`.
3. Re-run `python3 scripts/generate_pages.py` — the game's page and every grid tile referencing it now use the real image instead of the generated art. Removing the `poster` field (or the image file) reverts it to generated art automatically.
4. If you also keep `preview/site-preview.html` in sync as a shareable single-file demo, re-run `python3 scripts/build_preview.py` too — it inlines every poster image as base64 so the preview stays a single self-contained file.

Only use images you have the rights to use — official box art is copyrighted by its publisher, so this is best suited to art you've licensed, screenshots you've taken, or a source that explicitly allows fan/reference-site use.

### Adding a new language across the board

Search/filter and the language switcher are already wired for `en` / `de` / `es` / `fr`. To add a fifth language:

- Add the key to every `lore` object in `data/games.json` (empty string is fine to start).
- In `scripts/generate_pages.py`, add it to `LANG_LABELS` and `LANG_NAMES` at the top.
- Re-run the generator.

## Deploying to GitHub Pages

1. Push this folder to a GitHub repo (root of the repo, or a `/docs` folder — either works).
2. In the repo's Settings → Pages, set the source to that branch/folder.
3. That's it — everything is static, no build step required at deploy time. Just remember to run `scripts/generate_pages.py` locally before you push whenever you've edited `data/games.json`.

## License & copyright

This site's design, code, and original written content (story summaries, copy, etc.) are Copyright (c) 2026 Alireza Esmaeily — All Rights Reserved. See [`LICENSE`](./LICENSE) for the full terms. The repository is hosted publicly on GitHub so GitHub Pages can serve it, but public visibility is not permission to reuse: no one may copy, redistribute, or build on this design/code without written permission from the copyright holder.

Game titles, cover art, screenshots, trailer footage, and embedded YouTube videos remain the property of their respective publishers, developers, and creators — this project only references/embeds them for commentary and walkthrough purposes, and claims no ownership over that third-party material.

## Notes

- No real box art is used anywhere by default — every tile/cover is procedurally generated (gradient mesh + genre-icon watermark + monogram badge) so the site ships with zero copyright exposure out of the box. See "Adding real cover art for a game" above if you want to opt specific titles into real images you have the rights to use.
- Hover-preview on grid tiles loads a muted, looping YouTube embed of that game's walkthrough after a short hover delay, and tears it down on mouse-leave — so idle browsing doesn't spin up dozens of background video streams.
- "Trending Now" on the home page is currently just the 12 newest releases by `releaseDate`. If you want real trending logic later (e.g. wired to actual view counts), that's the one spot (`index.html`'s inline script) to change — it's a single `.slice(0, 12)` on the sorted dataset.
- Lore summaries are intentionally spoiler-conscious (setup and stakes, not endings).
