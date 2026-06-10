#!/usr/bin/env python3
"""
Extract the Graspop Metal Meeting 2026 lineup from the saved website HTML.

Parses 'Line-up-Lijst_Graspop_Metal_Meeting_2026.html' (the artist list page
with embedded schedule info) and writes a structured lineup.json.
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup

YEAR = 2026
DATA_DIR = f"data/{YEAR}"

DAY_MAP = {
    "donderdag": "Thursday",
    "vrijdag": "Friday",
    "zaterdag": "Saturday",
    "zondag": "Sunday",
}
DAY_ORDER = ["Thursday", "Friday", "Saturday", "Sunday"]

# Sets that start before this hour belong to the previous festival day's night
# programme (e.g. a 0:50 tribute set in the Metal Dome is Thursday night).
NIGHT_CUTOFF_HOUR = 6

BASE_URL = "https://www.graspop.be"


@dataclass
class Act:
    id: str
    artist: str
    day: str
    start: str
    end: str
    stage: str
    url: str | None
    image: str | None


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "unknown"


def parse_time(raw: str) -> str:
    """Normalize '16.35' / '0.00' to zero-padded 'HH:MM'."""
    h, m = raw.strip().replace(".", ":").split(":")
    return f"{int(h):02d}:{int(m):02d}"


def sort_minutes(hhmm: str) -> int:
    """Minutes since the festival day's start, late-night sets counted as 24h+."""
    h, m = map(int, hhmm.split(":"))
    if h < NIGHT_CUTOFF_HOUR:
        h += 24
    return h * 60 + m


def extract_from_html(html_path: str) -> list[Act]:
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    acts = []
    seen_ids = set()
    skipped = 0

    for item in soup.select(".artists-list__item"):
        name_el = item.select_one(".artist__name")
        timing_el = item.select_one(".artist__timing")
        if not name_el or not timing_el:
            skipped += 1
            continue

        artist = name_el.get_text(strip=True)
        parts = [p.strip() for p in timing_el.get_text(strip=True).split("•")]
        if len(parts) != 3:
            print(f"  ! Unparseable timing for {artist!r}: {parts}")
            skipped += 1
            continue

        day_nl, time_range, stage = parts
        day = DAY_MAP.get(day_nl.lower())
        if day is None:
            print(f"  ! Unknown day for {artist!r}: {day_nl!r}")
            skipped += 1
            continue

        m = re.match(r"^(\d{1,2}[.:]\d{2})\s*-\s*(\d{1,2}[.:]\d{2})$", time_range)
        if not m:
            print(f"  ! Unparseable time range for {artist!r}: {time_range!r}")
            skipped += 1
            continue
        start, end = parse_time(m.group(1)), parse_time(m.group(2))

        link_el = item.select_one("a.artist__link[href]")
        url = BASE_URL + link_el["href"] if link_el else None
        img_el = item.select_one("img.artist__image[src]")
        image = img_el["src"] if img_el else None

        # Stable id from the band page slug, falling back to the name.
        slug = link_el["href"].rstrip("/").rsplit("/", 1)[-1] if link_el else slugify(artist)
        act_id = slug
        n = 2
        while act_id in seen_ids:
            act_id = f"{slug}-{n}"
            n += 1
        seen_ids.add(act_id)

        acts.append(Act(act_id, artist, day, start, end, stage, url, image))

    if skipped:
        print(f"Skipped {skipped} items without full schedule info")

    acts.sort(key=lambda a: (DAY_ORDER.index(a.day), sort_minutes(a.start), a.stage))
    return acts


def save_json(acts: list[Act], output_path: str) -> None:
    stages = []
    for a in acts:  # keep first-appearance order of the main stages
        if a.stage not in stages:
            stages.append(a.stage)
    data = {
        "festival": "Graspop Metal Meeting",
        "year": YEAR,
        "days": [d for d in DAY_ORDER if any(a.day == d for a in acts)],
        "stages": stages,
        "acts": [asdict(a) for a in acts],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(acts)} acts to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract the GMM lineup from the saved HTML")
    parser.add_argument("--input", default=f"{DATA_DIR}/Line-up-Lijst_Graspop_Metal_Meeting_{YEAR}.html")
    parser.add_argument("--json", default=f"{DATA_DIR}/lineup.json")
    args = parser.parse_args()

    acts = extract_from_html(args.input)
    save_json(acts, args.json)

    per_day = {d: sum(1 for a in acts if a.day == d) for d in DAY_ORDER}
    print(f"Summary: {len(acts)} acts — " + ", ".join(f"{d} {n}" for d, n in per_day.items()))


if __name__ == "__main__":
    main()
