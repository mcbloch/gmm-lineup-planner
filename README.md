# GMM 2026 Lineup Planning

Plan which bands to see at Graspop Metal Meeting 2026.

## Workflow

```sh
uv run download_lineup.py  # graspop.be artist-list page -> data/2026/*.html
uv run extract_lineup.py   # HTML -> data/2026/lineup.json
uv run fetch_links.py      # scrape Spotify/YouTube links from graspop.be into lineup.json
uv run build_site.py       # lineup.json + template.html -> index.html
```

Then open `index.html` in any browser (works from `file://`, no server needed).

Downloaded and generated data lives in `data/<year>/` (gitignored); each script's
defaults point there via its `YEAR`/`DATA_DIR` constants.

## Files

- `download_lineup.py` — downloads the graspop.be artist-list page (the data source) into `data/2026/`
- `extract_lineup.py` — parses the HTML into `data/2026/lineup.json`
- `data/2026/lineup.json` — structured lineup: per act an `id` (slug), `artist`, `day`, `start`/`end`, `stage`, `url`, `image`. Acts are sorted chronologically per day; sets starting before 06:00 count as the previous day's night programme.
- `fetch_links.py` — fetches each act's graspop.be band page and adds `spotify`/`youtube` links to `lineup.json`; results cached in `data/2026/band_links.json` (delete it or pass `--refresh` to refetch)
- `template.html` — the planner app, with a `__LINEUP_JSON__` placeholder
- `build_site.py` — embeds the JSON into the template and writes `index.html`
- `index.html` — the generated, self-contained planner (only the band thumbnails need network)

## The planner

Mobile-first single page:

- Day tabs (Thu–Sun), filter chips per rating + unrated, stage filter
- Spotify and YouTube buttons on every card — direct artist link where graspop.be lists one (134/147 on Spotify), otherwise a search link (shown dimmed)
- Six rating tiers per act: **🤘 Must / Want / Good / Filler / Skip / Nope** — tap again to unset
- Acts rated Must/Want that overlap in time get a ⚠ conflict warning
- Ratings persist in `localStorage` (`gmm2026-ratings`)
- Export downloads `gmm2026-ratings.json`; Import reads it back (also accepts a bare `{id: rating}` object)

Five acts with "Meerdere performances" (roaming DJs, no fixed slot) are skipped during extraction.
