#!/usr/bin/env python3
"""
Enrich lineup.json with Spotify/YouTube links scraped from each act's
graspop.be band page. Results are cached in band_links.json so re-runs
only fetch what's missing.
"""

import argparse
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup

YEAR = 2026
DATA_DIR = f"data/{YEAR}"
PLATFORMS = ("spotify", "youtube")
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) gmm2026-lineup-planning"}


def fetch_links(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        soup = BeautifulSoup(resp.read(), "html.parser")
    links = {}
    # The band's own socials live in the artist header; the page footer
    # holds Graspop's socials, which we must not pick up.
    for a in soup.select(".artist-head__socials a.social__link[href]"):
        platform = (a.get("title") or "").lower()
        if platform in PLATFORMS and platform not in links:
            links[platform] = a["href"]
    return links


def main():
    parser = argparse.ArgumentParser(description="Fetch listen links for the lineup")
    parser.add_argument("--lineup", default=f"{DATA_DIR}/lineup.json")
    parser.add_argument("--cache", default=f"{DATA_DIR}/band_links.json")
    parser.add_argument("--refresh", action="store_true", help="refetch everything")
    args = parser.parse_args()

    with open(args.lineup, encoding="utf-8") as f:
        lineup = json.load(f)

    try:
        with open(args.cache, encoding="utf-8") as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}
    if args.refresh:
        cache = {}

    todo = [a for a in lineup["acts"] if a.get("url") and a["id"] not in cache]
    print(f"Fetching {len(todo)} band pages ({len(cache)} cached)")

    def worker(act):
        try:
            return act["id"], fetch_links(act["url"])
        except Exception as e:
            print(f"  ! {act['artist']}: {e}")
            return act["id"], None

    with ThreadPoolExecutor(max_workers=6) as pool:
        for act_id, links in pool.map(worker, todo):
            if links is not None:
                cache[act_id] = links

    with open(args.cache, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False, sort_keys=True)

    for act in lineup["acts"]:
        for platform in PLATFORMS:
            link = cache.get(act["id"], {}).get(platform)
            if link:
                act[platform] = link
            else:
                act.pop(platform, None)

    with open(args.lineup, "w", encoding="utf-8") as f:
        json.dump(lineup, f, indent=2, ensure_ascii=False)

    counts = {p: sum(1 for a in lineup["acts"] if a.get(p)) for p in PLATFORMS}
    total = len(lineup["acts"])
    print("Coverage: " + ", ".join(f"{p} {n}/{total}" for p, n in counts.items()))


if __name__ == "__main__":
    main()
