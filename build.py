#!/usr/bin/env python3
"""WTANGY Static Site Generator and Dev Server"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add src/ to path so we can import nhlhelpers
SYS_PATH = os.path.abspath(os.path.dirname(__file__))
SRC_PATH = os.path.join(SYS_PATH, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import nhlhelpers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def fetch_upstream_schedule(fetch_url):
    """Fetch schedule JSON from upstream URL."""
    req = urllib.request.Request(fetch_url, headers={"User-Agent": "WTANGY-Build/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        content = response.read().decode("utf-8")
        dest_url = response.geturl()
        schedule_date_str = dest_url.split("/")[-1]
        try:
            date_obj = datetime.strptime(schedule_date_str, "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.now()
        jsondata = json.loads(content)
        return jsondata, date_obj


def parse_schedule(jsondata):
    """Parse raw NHL API json data into teamdates matchup structure."""
    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

    dates = jsondata.get("gameWeek", [])
    for key in dates:
        date = key["date"]
        dict_of_keys_and_matchups[date] = []
        games = key.get("games", [])
        for game in games:
            twoteams = []
            awayabbrev = game["awayTeam"]["abbrev"]
            homeabbrev = game["homeTeam"]["abbrev"]
            twoteams.append(nhlhelpers.get_team(awayabbrev))
            twoteams.append(nhlhelpers.get_team(homeabbrev))
            if None in twoteams:
                logging.info(
                    "Unknown team (%s or %s) on %s. Skipping.",
                    awayabbrev,
                    homeabbrev,
                    date,
                )
                continue
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

    return dict_of_keys_and_matchups_s


def fetch_full_schedule(extra_weeks=4):
    """Fetch current week + extra_weeks ahead from NHL API."""
    base_url = "https://api-web.nhle.com/v1/schedule"
    url_now = f"{base_url}/now"

    logging.info("Fetching initial schedule from %s", url_now)
    try:
        jsondata, schedule_date = fetch_upstream_schedule(url_now)
    except Exception as err:
        logging.error("Failed to fetch schedule from NHL API: %s", err)
        # Fallback empty schedule dictionary if API fails
        return {"teamdates": {}}

    teamdates = parse_schedule(jsondata)
    content = {"teamdates": teamdates}

    for week in range(1, extra_weeks):
        next_week = schedule_date + timedelta(days=7 * week)
        next_date_str = str(next_week).split(" ", maxsplit=1)[0]
        extra_url = f"{base_url}/{next_date_str}"
        try:
            extra_jsondata, _ = fetch_upstream_schedule(extra_url)
            extra_teamdates = parse_schedule(extra_jsondata)
            content["teamdates"].update(extra_teamdates)
        except Exception as err:
            logging.warning("Could not fetch extra week %s: %s", extra_url, err)

    return content


def build_schedule_and_version(dist_dir, schedule_data=None):
    """Write get_schedule and version JSON static endpoints into dist/."""
    os.makedirs(dist_dir, exist_ok=True)

    if schedule_data is None:
        schedule_data = fetch_full_schedule()

    schedule_json_str = json.dumps(schedule_data, indent=2, sort_keys=True)

    # Output get_schedule and get_schedule.json
    get_schedule_path = os.path.join(dist_dir, "get_schedule")
    get_schedule_json_path = os.path.join(dist_dir, "get_schedule.json")
    with open(get_schedule_path, "w", encoding="utf-8") as f:
        f.write(schedule_json_str)
    with open(get_schedule_json_path, "w", encoding="utf-8") as f:
        f.write(schedule_json_str)

    logging.info("Generated %s and %s", get_schedule_path, get_schedule_json_path)

    # Output version and version.json
    now = datetime.now()
    version_data = {"version": now.isoformat(), "instance": "static"}
    version_json_str = json.dumps(version_data, indent=2)

    version_path = os.path.join(dist_dir, "version")
    version_json_path = os.path.join(dist_dir, "version.json")
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(version_json_str)
    with open(version_json_path, "w", encoding="utf-8") as f:
        f.write(version_json_str)

    logging.info("Generated %s and %s", version_path, version_json_path)
    return schedule_data


def run_dev_server(dist_dir, port=8080):
    """Run local HTTP dev server serving dist_dir."""

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dist_dir, **kwargs)

    server_address = ("", port)
    httpd = HTTPServer(server_address, Handler)
    logging.info("--------------------------------------------------")
    logging.info("[DX Dev Server] Running at http://localhost:%d/", port)
    logging.info("Serving directory: %s", os.path.abspath(dist_dir))
    logging.info("Press Ctrl+C to stop.")
    logging.info("--------------------------------------------------")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("\nShutting down dev server.")
        httpd.server_close()


def main():
    parser = argparse.ArgumentParser(description="WTANGY Static Site Generator")
    parser.add_argument(
        "--dist",
        default="dist",
        help="Target output directory for static files (default: dist)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch local developer HTTP server after building",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for local developer HTTP server (default: 8080)",
    )
    args = parser.parse_args()

    dist_dir = os.path.abspath(args.dist)
    logging.info("Starting WTANGY static site build into %s", dist_dir)
    build_schedule_and_version(dist_dir)
    logging.info("Build complete!")

    if args.serve:
        run_dev_server(dist_dir, args.port)


if __name__ == "__main__":
    main()
