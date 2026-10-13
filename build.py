#!/usr/bin/env python3
"""WTANGY Static Site Generator and Dev Server"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
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


def build_atom_feed(dist_dir):
    """Generate dist/atom.xml feed based on atom_bootstrap.xml or existing feed."""
    atom_dist_path = os.path.join(dist_dir, "atom.xml")
    bootstrap_path = os.path.join(SRC_PATH, "atom_bootstrap.xml")

    source_file = atom_dist_path if os.path.exists(atom_dist_path) else bootstrap_path

    if os.path.exists(source_file):
        try:
            tree = ET.parse(source_file)
        except Exception as err:
            logging.warning("Could not parse %s: %s", source_file, err)
            tree = None
    else:
        tree = None

    if not os.path.exists(atom_dist_path) and os.path.exists(bootstrap_path):
        with open(bootstrap_path, "r", encoding="utf-8") as src, open(
            atom_dist_path, "w", encoding="utf-8"
        ) as dst:
            dst.write(src.read())
        logging.info("Generated %s from bootstrap feed", atom_dist_path)
    elif tree is not None:
        tree.write(atom_dist_path, encoding="utf-8", xml_declaration=True)
        logging.info("Generated %s", atom_dist_path)


def build_team_css(dist_dir):
    """Generate dynamic team color CSS at dist/css/menu_team.css."""
    css_dir = os.path.join(dist_dir, "css")
    os.makedirs(css_dir, exist_ok=True)
    css_path = os.path.join(css_dir, "menu_team.css")

    allteams = sorted(list(nhlhelpers.get_all_teams().keys()))
    whitetext = [
        "ARI",
        "BUF",
        "CBJ",
        "DET",
        "EDM",
        "NSH",
        "NYI",
        "NYR",
        "TBL",
        "TOR",
        "VAN",
        "WPG",
    ]
    yellowtext = ["STL"]

    css_lines = []
    for ateam in allteams:
        colors = nhlhelpers.get_team_colors(ateam)
        bg = colors[0]
        if bg == "000000" and len(colors) > 1:
            bg = colors[1]
        css_lines.append(f".wrapper > a.{ateam} {{")
        css_lines.append(f"    background-color: #{bg};")
        css_lines.append("    font-family: NHL;")
        if ateam in whitetext:
            css_lines.append("    color: white;")
        elif ateam in yellowtext:
            css_lines.append("    color: yellow;")
        css_lines.append("}")

    css_content = "\n".join(css_lines) + "\n"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)

    logging.info("Generated %s", css_path)


def build_openapi_and_docs(dist_dir):
    """Generate dist/openapi.json and Swagger UI at dist/docs/index.html."""
    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Was There An NHL Game Yesterday? (WTANGY) API",
            "description": "API documentation for WTANGY schedule endpoints and team/date query parameters.",
            "version": "1.0.0",
        },
        "servers": [
            {"url": "https://wtangy.se", "description": "Production Server"},
            {"url": "http://localhost:8080", "description": "Local Development Server"},
        ],
        "paths": {
            "/": {
                "get": {
                    "summary": "Root Yesterday Query",
                    "description": "Returns YES or NO depending on whether an NHL game was played yesterday.",
                    "parameters": [
                        {
                            "name": "JSON",
                            "in": "query",
                            "required": False,
                            "description": "Returns JSON response if present",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "YES/NO response"}},
                }
            },
            "/{team}": {
                "get": {
                    "summary": "Team Schedule Query",
                    "description": "Returns YES or NO depending on whether specified team played yesterday.",
                    "parameters": [
                        {
                            "name": "team",
                            "in": "path",
                            "required": True,
                            "description": "Team abbreviation or name (e.g. DET, NYR, RedWings)",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "JSON",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"200": {"description": "YES/NO response"}},
                }
            },
            "/{date}": {
                "get": {
                    "summary": "Date Query",
                    "description": "Returns YES or NO depending on whether an NHL game was played on specified date.",
                    "parameters": [
                        {
                            "name": "date",
                            "in": "path",
                            "required": True,
                            "description": "Date in YYYYMMDD or YYYY-MM-DD format",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "YES/NO response"}},
                }
            },
            "/{team}/{date}": {
                "get": {
                    "summary": "Team and Date Query",
                    "description": "Returns YES or NO depending on whether specified team played on specified date.",
                    "parameters": [
                        {
                            "name": "team",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "date",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"200": {"description": "YES/NO response"}},
                }
            },
            "/get_schedule": {
                "get": {
                    "summary": "Get Schedule JSON",
                    "description": "Returns the complete schedule dictionary mapping dates to matchups.",
                    "responses": {
                        "200": {
                            "description": "JSON schedule object",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"teamdates": {"type": "object"}},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/version": {
                "get": {
                    "summary": "Get Schedule Version",
                    "description": "Returns JSON with build timestamp ISO date.",
                    "responses": {
                        "200": {
                            "description": "Version JSON object",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "version": {"type": "string"},
                                            "instance": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/atom.xml": {
                "get": {
                    "summary": "Atom RSS Feed",
                    "description": "Returns Atom 1.0 XML feed of schedule updates.",
                    "responses": {
                        "200": {
                            "description": "Atom XML feed",
                            "content": {"application/xml": {}},
                        }
                    },
                }
            },
            "/menu": {
                "get": {
                    "summary": "Interactive Team Selector",
                    "responses": {"200": {"description": "HTML team menu"}},
                }
            },
        },
    }

    openapi_path = os.path.join(dist_dir, "openapi.json")
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2)
    logging.info("Generated %s", openapi_path)

    docs_dir = os.path.join(dist_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    docs_html_path = os.path.join(docs_dir, "index.html")

    swagger_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WTANGY API Documentation</title>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
  <style>
    html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
    *, *:before, *:after { box-sizing: inherit; }
    body { margin: 0; background: #fafafa; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" charset="UTF-8"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
  <script>
    window.onload = function() {
      window.ui = SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
      });
    };
  </script>
</body>
</html>
"""

    with open(docs_html_path, "w", encoding="utf-8") as f:
        f.write(swagger_html)
    logging.info("Generated %s", docs_html_path)


def copy_static_assets(dist_dir):
    """Copy all static files from src/static to dist/ and dist/static/."""
    static_src_dir = os.path.join(SRC_PATH, "static")
    if not os.path.exists(static_src_dir):
        logging.warning("Static assets directory %s does not exist", static_src_dir)
        return

    static_dist_sub_dir = os.path.join(dist_dir, "static")
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(static_dist_sub_dir, exist_ok=True)

    copied_count = 0
    for filename in os.listdir(static_src_dir):
        src_file = os.path.join(static_src_dir, filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, os.path.join(dist_dir, filename))
            shutil.copy2(src_file, os.path.join(static_dist_sub_dir, filename))
            copied_count += 1

    logging.info(
        "Copied %d static asset files to %s and %s",
        copied_count,
        dist_dir,
        static_dist_sub_dir,
    )


def give_me_a_color(team):
    """Select a color, take second color if the first is black."""
    color = nhlhelpers.get_team_colors(team)
    fgcolor = color[0]
    try:
        fgcolor2 = color[1]
    except IndexError:
        fgcolor2 = color[0]
    if fgcolor == "000000":
        fgcolor = fgcolor2
    return fgcolor


def render_index_html(
    yesorno="NO",
    team=None,
    teamlongtext=None,
    date=None,
    fgcolor="000000",
    tomorrow=None,
    tomorrowurl="/",
):
    """Render index.html template with variables."""
    index_template_path = os.path.join(SRC_PATH, "templates", "index.html")
    with open(index_template_path, "r", encoding="utf-8") as f:
        content = f.read()

    team_str = str(team) if team else "None"
    date_str = str(date) if date else "None"
    fgcolor_str = str(fgcolor).lstrip("#") if fgcolor else "000000"
    teamlongtext_str = str(teamlongtext) if teamlongtext else ""
    tomorrow_str = str(tomorrow) if tomorrow else ""

    content = content.replace("{{ yesorno }}", yesorno)
    content = content.replace("{{ team }}", team_str)
    content = content.replace("{{ date }}", date_str)
    content = content.replace("{{ fgcolor }}", fgcolor_str)
    content = content.replace("{{ tomorrow }}", tomorrow_str)
    content = content.replace("{{ tomorrowurl }}", tomorrowurl)

    if teamlongtext:
        content = re.sub(
            r"\{%\s*if teamlongtext is not none\s*%\}\s*\{\{\s*teamlongtext\s*\}\}\s*\{%\s*endif\s*%\}",
            teamlongtext_str,
            content,
        )
    else:
        content = re.sub(
            r"\{%\s*if teamlongtext is not none\s*%\}\s*\{\{\s*teamlongtext\s*\}\}\s*\{%\s*endif\s*%\}",
            "",
            content,
        )

    content = content.replace("{{ teamlongtext }}", teamlongtext_str)
    return content


def render_menu_html():
    """Render menu.html template with team boxes."""
    menu_template_path = os.path.join(SRC_PATH, "templates", "menu.html")
    allteams = sorted(list(nhlhelpers.get_all_teams().keys()))
    reallyallteams = nhlhelpers.get_all_teams()
    with open(menu_template_path, "r", encoding="utf-8") as f:
        template = f.read()

    team_links = []
    for team in allteams:
        title = reallyallteams.get(team, team)
        link = f'<a href="/{team}" class="{team}" title="{title}" onClick="saveTeam(\'{team}\')"><div>{team}</div></a>'
        team_links.append(link)

    loop_pattern = r"\{%\s*for team in allteams\s*-?%\}(.*?)\{%\s*endfor\s*%\}"
    rendered = re.sub(loop_pattern, "\n".join(team_links), template, flags=re.DOTALL)
    return rendered


def build_html_pages(dist_dir, schedule_data):
    """Pre-render root index.html, menu/index.html, and static team pages."""
    teamdates = schedule_data.get("teamdates", {})
    now = datetime.now()
    tomorrow1 = now.strftime("%Y%m%d")

    # 1. Root page
    root_yesorno = "YES" if nhlhelpers.yesorno(None, teamdates, None) else "NO"
    root_html = render_index_html(
        yesorno=root_yesorno,
        team=None,
        teamlongtext=None,
        date=None,
        fgcolor="000000",
        tomorrow=tomorrow1,
        tomorrowurl=f"/{tomorrow1}",
    )
    with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_html)
    logging.info("Generated %s", os.path.join(dist_dir, "index.html"))

    # 2. Menu page
    menu_dir = os.path.join(dist_dir, "menu")
    os.makedirs(menu_dir, exist_ok=True)
    menu_html = render_menu_html()
    with open(os.path.join(menu_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(menu_html)
    logging.info("Generated %s", os.path.join(menu_dir, "index.html"))

    # 3. Team pages
    keys = set()
    allteams = nhlhelpers.get_all_teams()
    for abbrev, full_name in allteams.items():
        keys.add(abbrev)
        keys.add(abbrev.lower())
        keys.add(full_name.replace(" ", ""))
        keys.add(full_name.replace(" ", "").lower())

    extra_names = [
        "ducks", "coyotes", "bruins", "buffalo", "hurricanes", "bluejackets", "flames", "blackhawks",
        "avalanche", "stars", "redwings", "oilers", "panthers", "kings", "wild", "canadiens", "devils",
        "predators", "islanders", "rangers", "senators", "flyers", "penguins", "sharks", "blues",
        "lightning", "leafs", "canucks", "goldenknights", "jets", "capitals", "kraken", "utah",
        "canes", "jackets", "hawks", "wings", "preds", "sens", "pens", "bolts", "caps", "tampa",
        "la", "nj", "sj", "lv", "lasvegas", "montréal", "stlouis", "detroit", "boston", "chicago",
        "dallas", "edmonton", "florida", "minnesota", "montreal", "nashville", "ottawa", "philadelphia",
        "pittsburgh", "seattle", "vancouver", "vegas", "winnipeg", "washington"
    ]
    for name in extra_names:
        if nhlhelpers.get_team(name):
            keys.add(name)
            keys.add(name.upper())
            keys.add(name.capitalize())

    team_page_count = 0
    for team_key in keys:
        clean_team = team_key.upper().replace(" ", "").replace("%20", "")
        teamlongtext = nhlhelpers.get_team(clean_team)
        if not teamlongtext:
            continue

        fgcolor = give_me_a_color(clean_team)
        yesorno = "YES" if nhlhelpers.yesorno(clean_team, teamdates, None) else "NO"
        tomorrowurl = f"/{clean_team}/{tomorrow1}"

        team_html = render_index_html(
            yesorno=yesorno,
            team=clean_team,
            teamlongtext=teamlongtext,
            date=None,
            fgcolor=fgcolor,
            tomorrow=tomorrow1,
            tomorrowurl=tomorrowurl,
        )

        team_dir = os.path.join(dist_dir, team_key)
        os.makedirs(team_dir, exist_ok=True)
        with open(os.path.join(team_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(team_html)
        team_page_count += 1

    logging.info("Generated %d static team pages in %s", team_page_count, dist_dir)


def run_dev_server(dist_dir, port=8080):
    """Run local HTTP dev server serving dist_dir."""

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dist_dir, **kwargs)

        def do_GET(self):
            clean_path = self.path.split("?")[0].rstrip("/")
            if clean_path in ("/get_schedule", "/get_schedule.json"):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                file_path = os.path.join(dist_dir, "get_schedule.json")
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            if clean_path in ("/version", "/version.json"):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                file_path = os.path.join(dist_dir, "version.json")
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

            requested_file = os.path.join(dist_dir, self.path.lstrip("/"))
            if not os.path.exists(requested_file) and not os.path.exists(
                requested_file + ".html"
            ):
                parts = [p for p in clean_path.split("/") if p]
                if parts:
                    first_part = parts[0]
                    team_folder = os.path.join(dist_dir, first_part)
                    if os.path.isdir(team_folder):
                        self.path = f"/{first_part}/index.html"
                    else:
                        self.path = "/index.html"

            super().do_GET()

        def guess_type(self, path):
            basename = os.path.basename(path)
            if basename in ("get_schedule", "version"):
                return "application/json"
            if basename == "atom.xml":
                return "application/xml"
            return super().guess_type(path)

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
    schedule_data = build_schedule_and_version(dist_dir)
    build_atom_feed(dist_dir)
    build_team_css(dist_dir)
    build_openapi_and_docs(dist_dir)
    copy_static_assets(dist_dir)
    build_html_pages(dist_dir, schedule_data)
    logging.info("Build complete!")

    if args.serve:
        run_dev_server(dist_dir, args.port)


if __name__ == "__main__":
    main()
