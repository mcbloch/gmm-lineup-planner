#!/usr/bin/env python3
"""Generate index.html by embedding lineup.json into template.html."""

import argparse
import json

YEAR = 2026
DATA_DIR = f"data/{YEAR}"


def main():
    parser = argparse.ArgumentParser(description="Build the GMM planner page")
    parser.add_argument("--lineup", default=f"{DATA_DIR}/lineup.json")
    parser.add_argument("--template", default="template.html")
    parser.add_argument("--output", default="index.html")
    args = parser.parse_args()

    with open(args.lineup, encoding="utf-8") as f:
        lineup = json.load(f)
    with open(args.template, encoding="utf-8") as f:
        template = f.read()

    if "__LINEUP_JSON__" not in template:
        raise SystemExit("template is missing the __LINEUP_JSON__ placeholder")

    # Escape '</' so the JSON can never terminate the <script> block early.
    payload = json.dumps(lineup, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("__LINEUP_JSON__", payload)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {args.output} with {len(lineup['acts'])} acts")


if __name__ == "__main__":
    main()
