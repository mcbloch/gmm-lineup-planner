#!/usr/bin/env python3
"""Download the Graspop Metal Meeting lineup page (the artist list with
embedded schedule info) into the year's data folder."""

import argparse
import os
import urllib.request

YEAR = 2026
DATA_DIR = f"data/{YEAR}"
LINEUP_URL = "https://www.graspop.be/nl/line-up/"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) gmm2026-lineup-planning"}


def main():
    parser = argparse.ArgumentParser(description="Download the GMM lineup page")
    parser.add_argument("--url", default=LINEUP_URL)
    parser.add_argument("--output", default=f"{DATA_DIR}/Line-up-Lijst_Graspop_Metal_Meeting_{YEAR}.html")
    args = parser.parse_args()

    print(f"Downloading {args.url}")
    req = urllib.request.Request(args.url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "wb") as f:
        f.write(html)
    print(f"Saved {len(html)} bytes to {args.output}")


if __name__ == "__main__":
    main()
