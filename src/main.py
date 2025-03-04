"""YES, oor no?"""

import json
import logging
import os
from datetime import datetime, timedelta

import feedparser
import google.cloud.logging
import requests
from device_detector import DeviceDetector
from feedgen.feed import FeedGenerator
from flask import Flask, jsonify, make_response, render_template, request
from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage
from jsondiff import diff

#
import nhlhelpers

# https://cloud.google.com/datastore/docs/reference/libraries#client-libraries-usage-python

app = Flask(__name__)

# /menu is now also /menu/
app.url_map.strict_slashes = False

# Setup logging https://cloud.google.com/logging/docs/setup/python
CLIENT = google.cloud.logging.Client()
CLIENT.setup_logging()


# http://exploreflask.com/en/latest/views.html
@app.route("/")
def view_root():
    """No arguments"""
    return the_root()


@app.route("/<string:var1>/")
def view_team(var1):
    """1 argument, team or date"""
    return the_root(var1, var2=False)


@app.route("/<string:var1>/<string:var2>/")
def view_teamdate(var1, var2):
    """2 arguments, hopefully one team and one date"""
    return the_root(var1, var2)


def the_root(var1=False, var2=False):
    """We use the_root for both /DETROIT and /DETROIT/20220122"""

    # Set some tomorrow things for when a date or team has not been specified
    # tomorrow set to today if none is set
    # because today is like tomorrow if you know what I mean (wink wink)
    tomorrow = datetime.now()
    tomorrow1 = tomorrow.strftime("%Y%m%d")
    tomorrowurl = f"/{tomorrow1}"

    ########

    team1, date1 = None, None

    for arg in [var1, var2]:
        # NHLHelpers we in some dicts replace spaces (%20) with "" .. hmm.
        if arg and nhlhelpers.get_team(arg.upper().replace(" ", "").replace("%20", "")):
            team1 = arg.upper().replace(" ", "").replace("%20", "")
            # If we have a team set tomorrowurl like /teamname/date
            tomorrowurl = f"/{team1}/{tomorrow1}"
        elif arg and nhlhelpers.validatedate(arg):
            date1 = nhlhelpers.validatedate(arg)
            # If an argument is a date we set tomorrow to one day after that
            tomorrow = datetime.strptime(date1, "%Y-%m-%d") + timedelta(days=1)
            tomorrow1 = tomorrow.strftime("%Y%m%d")
            tomorrowurl = f"/{tomorrow1}"  # Used by the right-arrow on index.html

    logging.debug(f"var1: {var1} var2: {var2} team1: {team1} date1: {date1}")
    # If we have a good team and date we have both in tomorrowurl
    if team1 and date1:
        tomorrowurl = f"/{team1}/{tomorrow1}"

    teamlongtext = None
    if team1:
        teamlongtext = nhlhelpers.get_team(team1)

    ########

    fgcolor = give_me_a_color(team1)

    ########

    teamdates = THESCHEDULE

    useragent = request.headers.get("User-Agent")
    logging.debug(f"User-Agent: {useragent}")
    device = ""
    if useragent:
        device = DeviceDetector(useragent).parse()

    ### The YES/NO logic:
    yesorno = "NO"
    if nhlhelpers.yesorno(team1, teamdates, date1):
        yesorno = "YES"

    if "JSON" in request.args:
        return jsonify({"wtangy": yesorno, "team": str(team1), "date": str(date1)})

    if useragent and device.client_type() == "library":
        return render_template("cli.html", yesorno=yesorno)

    return render_template(
        "index.html",
        yesorno=yesorno,
        team=team1,
        teamlongtext=teamlongtext,
        date=date1,
        fgcolor=fgcolor,
        tomorrow=tomorrow,
        tomorrowurl=tomorrowurl,
    )


@app.route("/update_schedule")
@app.route("/update_schedule_6fd74614-9bdd-45a5-a96d-a19b597bc604")
def update_schedule():
    """fetches schedule from upstream, parses it, uploads it, sets a version, outputs html for debug"""

    # default bucket is in this format: project-id.appspot.com
    # https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
    filename = "py3_nhle_new_schedule_" + VERSION
    updated_filename = "py3_updated_schedule_" + VERSION

    logging.info(f"Using filename {filename} and updated_filename {updated_filename}")

    ####

    url = "https://api-web.nhle.com/v1/schedule"  #
    url_now = f"{url}/now"  # gets update of today for this week

    jsondata, schedule_date = fetch_upstream_schedule(url_now)
    content = fetch_schedule_ahead(jsondata, url, schedule_date)

    if not jsondata:
        return (
            render_template(
                "update_schedule.html",
                version=VERSION,
                filename=filename,
                last_updated=False,
                changes=False,
            ),
            500,
        )

    changes = False

    try:
        old_content = json.loads(str(read_file(filename)).replace("'", '"'))
    except NotFound:
        create_file(filename, str(content))
        changes = "just created"
        logging.info("No schedule found, created it")
        return (
            render_template(
                "update_schedule.html",
                version=VERSION,
                filename=filename,
                last_updated=FOR_UPDATED,
                changes=changes,
            ),
            202,
        )
    if old_content == content:
        changes = "No changes needed"
        try:
            last_updated = read_file(updated_filename)
            _msg = "Not updating schedule - it is current."
            logging.info(_msg)
        except NotFound:
            create_file(updated_filename, FOR_UPDATED)
            last_updated = read_file(updated_filename)
        logging.info(f"Last updated: {last_updated}")
    else:
        changes = diff(old_content, content)
        logging.info(f"Changes: {changes}")
        create_file(filename, str(content))
        create_file(updated_filename, FOR_UPDATED)
        last_updated = read_file(updated_filename)
        # Only send notifications outside playoffs
        #  (potential spoilers - games are removed from the schedule)
        if CURRENT_MONTH < 4 or CURRENT_MONTH > 6:
            logging.info("Sending an update notification")
            atom_feed_manager(diff(old_content, content))
        else:
            logging.info(
                "Would have sent an update notification, but it might be playoff folks!"
            )
        return (
            render_template(
                "update_schedule.html",
                version=VERSION,
                filename=filename,
                last_updated=last_updated,
                changes=changes,
            ),
            202,
        )

    return render_template(
        "update_schedule.html",
        version=VERSION,
        filename=filename,
        last_updated=last_updated,
        changes=changes,
    )


@app.route("/get_schedule")
def get_schedule():
    """Get schedule from GCS and return it as JSON"""

    if VERSION == "None":
        filename = "py3_nhle_new_schedule"
    else:
        filename = "py3_nhle_new_schedule_" + VERSION

    logging.info(f"Using filename {filename}")

    content = json.loads(str(read_file(filename)).replace("'", '"'))
    resp = make_response(json.dumps(content, indent=2))
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/atom.xml")
def atom_feed():
    """Get atom feed from GCS and return"""

    if VERSION == "None":
        filename = "atom_feed.xml"
    else:
        filename = "atom_feed_" + VERSION + ".xml"

    logging.info(f"Using filename {filename}")

    # No need to pretty print the XML?
    content = read_file(filename)
    resp = make_response(content)
    resp.headers["Content-Type"] = "application/xml"
    return resp


@app.route("/menu")
def menu():
    """Return a menu, where one can choose team and some other settings"""

    allteams = sorted(list(nhlhelpers.get_all_teams().keys()))
    reallyallteams = nhlhelpers.get_all_teams()

    return render_template(
        "menu.html", allteams=allteams, reallyallteams=reallyallteams
    )


@app.route("/css/menu_team.css")
def menu_css():
    """Programmatically creates CSS based on the defined teams and their colors"""

    allteams = sorted(list(nhlhelpers.get_all_teams().keys()))
    # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
    colordict = {}
    # If we use
    # https://raw.githubusercontent.com/jimniels/teamcolors/master/static/data/teams.json
    # we would need to pick which of the colors to show. Sometimes it's 3rd, 2nd, first...
    for ateam in allteams:
        # Loop through colors and don't pick black as background for the box
        colors = nhlhelpers.get_team_colors(ateam)
        backgroundcolor = colors[0]
        try:
            backgroundcolor2 = colors[1]
        except IndexError:
            backgroundcolor2 = colors[0]
        if backgroundcolor == "000000":
            backgroundcolor = backgroundcolor2
        colordict[ateam] = backgroundcolor
    # Make CSS
    # Default font color is black.
    # With some backgrounds black is not so readable so we change it to white.
    # https://en.wikipedia.org/wiki/Template:NHL_team_color might be good, it talks about contrast at least..
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

    # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
    resp = make_response(
        render_template(
            "menu_team.css",
            allteams=allteams,
            colordict=colordict,
            whitetext=whitetext,
            yellowtext=yellowtext,
            mimetype="text/css",
        )
    )
    resp.headers["Content-Type"] = "text/css"
    return resp


@app.route("/version")
def version():
    """Fetch a file and render it"""

    return get_version()

    # We set_version in update_schedule


def get_version():
    """Fetch a file and return JSON"""

    # https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
    if VERSION == "None":
        filename = "py3_updated_schedule"
    else:
        filename = "py3_updated_schedule_" + VERSION

    # If we always store json no need to make it more json
    jsondata = str(read_file(filename)).replace("'", '"')

    resp = make_response(jsondata)
    resp.headers["Content-Type"] = "application/json"

    return resp


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


def create_file(filename, content):
    """Create a file."""

    try:
        storage_client = storage.Client()
    except DefaultCredentialsError:
        logging.error("Could not setup storage client for create_file")
        return False

    project_name = os.environ.get(
        "GOOGLE_CLOUD_PROJECT", "no_GOOGLE_CLOUD_PROJECT_found"
    )

    bucket_name = project_name + ".appspot.com"

    mybucket = storage_client.bucket(bucket_name)
    blob = mybucket.blob(filename)
    logging.info(
        f"Trying to create filename {filename} in bucket_name {bucket_name}, content size is {get_size(content)}"
    )

    blob.upload_from_string(content, content_type="application/json")

    return True


def stat_file(filename):
    """stat a file
    This returns a CLASS, fetch properties in the results with var.id, not var['id'] ???
    https://cloud.google.com/storage/docs/viewing-editing-metadata#code-samples
    """
    try:
        storage_client = storage.Client()
    except DefaultCredentialsError:
        logging.error("Could not setup storage client for stat_file")
        return False

    project_name = os.environ.get(
        "GOOGLE_CLOUD_PROJECT", "no_GOOGLE_CLOUD_PROJECT_found"
    )

    bucket_name = project_name + ".appspot.com"

    mybucket = storage_client.bucket(bucket_name)
    logging.info(f"Trying to stat filename {filename} in bucket_name {bucket_name}")

    return mybucket.get_blob(filename)


def read_file(filename):
    """read and return a file!"""

    try:
        storage_client = storage.Client()
    except DefaultCredentialsError:
        logging.error("Could not setup storage client for read_file")
        return False

    project_name = os.environ.get(
        "GOOGLE_CLOUD_PROJECT", "no_GOOGLE_CLOUD_PROJECT_found"
    )

    bucket_name = project_name + ".appspot.com"
    now_before = datetime.now()

    mybucket = storage_client.bucket(bucket_name)
    blob = mybucket.blob(filename)
    logging.debug(f"Trying to read filename {filename} in bucket_name {bucket_name}")
    now_after = datetime.now()
    time_spent = now_after - now_before
    logging.info(f"Read blob {bucket_name}:{filename} in {time_spent}")
    downloaded_blob = blob.download_as_text(encoding="utf-8")

    return downloaded_blob


def get_size(obj):
    """It's just characters baby

    >>> get_size({ "hello": [2,3,[1,2,[2,3]]] })
    33
    >>> get_size({ "hello": [2,3,[1,2,[2,3]]], "hello2": [2,3,4,5] })
    57
    >>> get_size({})
    2
    """
    size = len(str(obj))
    return size


def atom_feed_manager(message):
    """Manage the Atom Feed"""

    veri = "testing"
    if VERSION == "master":
        veri = "main"

    filename = "atom_feed_" + VERSION + ".xml"
    logging.info(f"ATOM: For veri {veri} using filename {filename}")

    parsed_feed = feedparser.parse("https://wtangy.se/atom.xml")
    if parsed_feed.entries == []:
        logging.error("ATOM ERROR: We found no entries")
        return False

    sorted_entries = sorted(
        parsed_feed.entries, key=lambda x: x["updated"], reverse=True
    )

    # Step 2: Modify the feed entries and metadata
    max_entries = 64
    modified_entries = []
    for entry in sorted_entries:
        # Modify entry attributes as needed
        #  except we are not modifying them..
        modified_entries.append(entry)
        max_entries = max_entries - 1
        # But we do only keep the last 64 updates
        #  Trying to be nice to RSS readers - no need for them to after a few
        #  years download megabytes. .. Is that how RSS readers work?
        if not max_entries:
            break

    # Step 3: Create a new Atom feed using feedgenerator
    #  Here we "override" the General Feed attributes
    new_feed = FeedGenerator()
    new_feed.title("WTANGY Schedule Updates")
    new_feed.description("Was There An NHL Game Yesterday?")
    new_feed.link(href="https://wtangy.se/", rel="alternate")
    new_feed.link(href="https://wtangy.se/atom.xml", rel="self")
    new_feed.language("en")
    new_feed.id("https://wtangy.se/")

    # Add modified entries to the new feed
    #  Here we are also not modifying anything..
    for modified_entry in modified_entries:
        entry = new_feed.add_entry()
        entry.id(modified_entry.id)
        entry.title(modified_entry.title)
        entry.description(modified_entry.description)
        entry.link(href=modified_entry.link, rel="alternate")
        entry.updated(modified_entry.updated)
        entry.category([{"term": modified_entry.category}])
        entry.author({"name": modified_entry.author})

    # Here we add a new entry _at the bottom_of the file_
    #  All entries in this section need to be in the above too or they are lost
    #  in space and time.
    #    Except the updated attribute?
    #  Changes are in the description field.
    #    Maybe content with type=html would be better?
    new_update = new_feed.add_entry()
    new_update_date = str(new_update.updated()).replace(" ", "")
    new_update.id(f"https://wtangy.se/schedule/{new_update_date}")
    new_update.title(f"NHL Schedule ({veri}) Has Been Updated")
    new_update.description(
        f"It's available on <a href='https://wtangy.se/get_schedule'>wtangy.se</a>. \n\n {message}"
    )
    new_update.link(href="https://wtangy.se/get_schedule", rel="alternate")
    new_update.category([{"term": veri}])
    author = {"name": "cron"}
    new_update.author(author)

    # Step 9: Save the new Atom feed as a string and write to GCS
    new_atom_feed_xml = new_feed.atom_str(pretty=True)
    create_file(filename, new_atom_feed_xml)

    return True


def fetch_schedule_ahead(now_initial_jsondata, base_url, now_initial_schedule_date):
    """return parsed 4 weeks ahead of now"""

    extra_weeks = 4
    teamdates = parse_schedule(now_initial_jsondata)
    content = json.loads(make_data_json(teamdates))
    for week in range(1, extra_weeks):
        next_week = now_initial_schedule_date + timedelta(days=7 * week)
        next_date_str = str(next_week).split(" ", maxsplit=1)[0]
        extra_url = f"{base_url}/{next_date_str}"
        extra_jsondata, _ = fetch_upstream_schedule(extra_url)  # could verify here
        extra_teamdates = parse_schedule(extra_jsondata)
        extra_content = json.loads(make_data_json(extra_teamdates))
        content["teamdates"].update(extra_content["teamdates"])

    return content


def fetch_upstream_schedule(fetch_this_url):
    """geturl a file and do some health checking"""

    jsondata = None

    geturl = requests.get(fetch_this_url, timeout=5)
    content = geturl.content
    destination_url = geturl.url
    schedule_date = destination_url.split("/")[-1]
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(schedule_date, date_format)

    jsondata = import_lazily("json").loads(content)

    logging.info(f"URL: {fetch_this_url}")
    return (jsondata, date_obj)


def parse_schedule(jsondata):
    """parse the json data into a dict the app is used to.
    as a bonus we also sort things

    The JSON data looks something like this under "dates":

    # URL.gameWeek is a list of dicts
    # {
    #  date: "2023-11-26"
    #  games: [ list of dicts
    #    {
    #      id: 2023020321 # running number
    #      season: 20232024
    #      awayTeam:
    #        {
    #          abbrev: MIN
    #          placeName: { default: "Montréal" } # see the accent
    #      homeTeam: { abbrev: DET, placeName: { default: "St. Louis" }
    #    },
    #    { }
    #  date: "2023-11-27"
    #  games: [] ...
    """

    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

    dates = jsondata["gameWeek"]
    for key in dates:
        date = key["date"]
        dict_of_keys_and_matchups[date] = []
        games = key["games"]
        for game in games:
            twoteams = []
            awayabbrev = game["awayTeam"]["abbrev"]
            homeabbrev = game["homeTeam"]["abbrev"]
            twoteams.append(nhlhelpers.get_team(awayabbrev))
            twoteams.append(nhlhelpers.get_team(homeabbrev))
            if None in twoteams:
                logging.info(
                    f"Unknown team ({awayabbrev} or {homeabbrev}) on {date}. Not adding this to our schedule"
                )
                continue
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

    logging.info("parsed schedule")
    return dict_of_keys_and_matchups_s


def make_data_json(teamdates):
    """turn parsed data into json, end result in JSON should look like:
    {
     "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], }
    }
    """
    data = {}
    data["teamdates"] = teamdates
    json_data = json.dumps(data, sort_keys=True)

    logging.info("made json")
    return json_data


def import_lazily(module_name):
    """only import some modules when needed"""
    try:
        return __import__(module_name)
    except ImportError:
        return None


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)


# Variables

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
VERSION = os.environ.get("GAE_VERSION", "no_GAE_VERSION_env_found")

# Loading schedule on startup instead of on every request to reduce latency
# Expecting dynamic instances to restart often enough to figure out schedule
#   changes.
FILENAME = "py3_nhle_new_schedule"
if VERSION != "None":
    FILENAME = "py3_nhle_new_schedule_" + VERSION

try:
    THESCHEDULE = json.loads(read_file(FILENAME).replace("'", '"'))["teamdates"]
except NotFound:
    # In case there is no schedule stored for the backend, try to make it
    logging.info("Viewing Root but no schedule found, let's try to parse and store it")
    update_schedule()
    THESCHEDULE = json.loads(str(read_file(FILENAME)).replace("'", '"'))["teamdates"]
##

NOW = datetime.now()
FOR_UPDATED = str({"version": str(NOW.isoformat()), "instance": VERSION})
[CURRENT_MONTH, CURRENT_YEAR] = (
    NOW.month,
    NOW.year,
)  # used to silence updates during playoffs
