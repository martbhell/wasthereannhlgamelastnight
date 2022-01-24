""" YES, oor no? """

import datetime
import os
import sys
import json
import logging
from urllib.request import urlopen
import tweepy
from device_detector import DeviceDetector
from jsondiff import diff
from flask import request
from flask import Flask, render_template, make_response
from google.cloud import storage
import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import NotFound
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
    tomorrow = datetime.datetime.now()
    tomorrow1 = tomorrow.strftime("%Y%m%d")
    tomorrowurl = f"/{tomorrow1}"

    ########

    team1 = None
    date1 = None

    for arg in [var1, var2]:
        if nhlhelpers.get_team(arg):
            team1 = arg
            # If we have a team set tomorrowurl like /teamname/date
            tomorrowurl = f"/{team1}/{tomorrow1}"
        elif nhlhelpers.validatedate(arg):
            date1 = nhlhelpers.validatedate(arg)
            # If an argument is a date we set tomorrow to one day after that
            tomorrow = datetime.datetime.strptime(
                date1, "%Y-%m-%d"
            ) + datetime.timedelta(days=1)
            tomorrow1 = tomorrow.strftime("%Y%m%d")
    # If we have a good team and date we have both in tomorrowurl
    if team1 and date1:
        tomorrowurl = f"/{team1}/{tomorrow1}"

    teamlongtext = None
    if team1:
        teamlongtext = nhlhelpers.get_team(team1)

    ########

    fgcolor = give_me_a_color(team1)

    ########

    filename = "py3_schedule"
    if VERSION != "None":
        filename = "py3_schedule_" + VERSION

    try:
        teamdates = json.loads(read_file(filename))["teamdates"]
    except NotFound:
        # In case there is no schedule stored for the backend, try to make it
        logging.info(
            "Viewing Root but no schedule found, let's try to parse and store it"
        )
        update_schedule()
        teamdates = json.loads(read_file(filename))["teamdates"]

    ### Returning something cheap for evil

    useragent = request.headers.get("User-Agent")
    logging.debug(f"User-Agent: {useragent}")
    if useragent:
        device = DeviceDetector(useragent).parse()
    else:
        return render_template("cli.html", yesorno="HMM")
    if device.is_bot():
        return render_template("cli.html", yesorno="NO"), 500

    ### The YES/NO logic:
    yesorno = "NO"
    if nhlhelpers.yesorno(team1, teamdates, date1):
        yesorno = "YES"

    if device.client_type() == "library":
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
def update_schedule():
    """fetches schedule from upstream, parses it, uploads it, sets a version, outputs html for debug"""

    # default bucket is in this format: project-id.appspot.com
    # https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
    filename = "py3_schedule_" + VERSION
    updated_filename = "py3_updated_schedule_" + VERSION

    logging.info(f"Using filename {filename} and updated_filename {updated_filename}")

    ####

    [totalgames, jsondata] = fetch_upstream_schedule(URL)

    if not jsondata:
        return (
            render_template(
                "update_schedule.html",
                version=VERSION,
                filename=filename,
                totalgames=totalgames,
                last_updated=False,
                changes=False,
            ),
            500,
        )

    changes = False

    if totalgames == 0:
        pass
    else:
        [teamdates] = parse_schedule(jsondata)
        content = make_data_json(teamdates)
        try:
            old_content = read_file(filename)
        except NotFound:
            create_file(filename, content)
            changes = "just created"
            logging.info("No schedule found, created it")
            return (
                render_template(
                    "update_schedule.html",
                    version=VERSION,
                    filename=filename,
                    totalgames=totalgames,
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
            changes = diff(json.loads(old_content), json.loads(content))
            logging.info(f"Changes: {changes}")
            create_file(filename, content)
            create_file(updated_filename, FOR_UPDATED)
            last_updated = read_file(updated_filename)
            # Only send notifications outside playoffs
            #  (potential spoilers - games are removed from the schedule)
            if CURRENT_MONTH < 4 or CURRENT_MONTH > 6:
                logging.info("Sending an update notification")
                send_an_email(diff(json.loads(old_content), json.loads(content)), True)
            return (
                render_template(
                    "update_schedule.html",
                    version=VERSION,
                    filename=filename,
                    totalgames=totalgames,
                    last_updated=last_updated,
                    changes=changes,
                ),
                202,
            )

    return render_template(
        "update_schedule.html",
        version=VERSION,
        filename=filename,
        totalgames=totalgames,
        last_updated=last_updated,
        changes=changes,
    )


@app.route("/get_schedule")
def get_schedule():
    """Get schedule from GCS and return it as JSON"""

    if VERSION == "None":
        filename = "py3_schedule"
    else:
        filename = "py3_schedule_" + VERSION

    logging.info(f"Using filename {filename}")

    content = json.loads(read_file(filename))
    resp = make_response(json.dumps(content, indent=2))
    resp.headers["Content-Type"] = "application/json"
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

    # We set_version in update_schedule.py


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

    mybucket = storage_client.bucket(bucket_name)
    blob = mybucket.blob(filename)
    logging.debug(f"Trying to read filename {filename} in bucket_name {bucket_name}")
    downloaded_blob = blob.download_as_text(encoding="utf-8")

    return downloaded_blob


def get_size(obj, seen=None):
    """Recursively finds size of objects
    https://goshippo.com/blog/measure-real-size-any-python-object/

    >>> get_size({ "hello": [2,3,[1,2,[2,3]]] })
    674
    >>> get_size({ "hello": [2,3,[1,2,[2,3]]], "hello2": [2,3,4,5] })
    869
    >>> get_size({})
    280
    """
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def send_an_email(message, twitter=False):
    """send an e-mail, optionally to the admin"""

    # Mail is not available in python3 -- only twitter!
    # Also no implemented way to send the whole change to the Admin

    logging.info("Inside send an e-mail")

    real_message = message
    msgsize = get_size(real_message)
    # size of 2019-2020 schedule was 530016, unclear how large the jsondiff was 2018->2019
    #  50000 is less than 65490 which was in the log of the update
    #  if we change all "Rangers" to "Freeezers" the changes to restore 2019-2020 was 106288
    if msgsize > 150000:
        real_message = f"Msgsize is {msgsize}, see /get_schedule - Hello new season?"
        logging.info(f" big message: {real_message}")

    if twitter:
        # Files uploaded manually, content unquoted
        # These are strings
        # Beware of newlines
        testfile = read_file("FOO.TXT")
        logging.info(testfile)
        logging.info(type(testfile))
        api_key = read_file("API_KEY.TXT")
        if "\n" in api_key:
            logging.error(
                "There's a newline in your twitter API_KEY, doubt that should be in there"
            )
        api_secret_key = read_file("API_SECRET_KEY.TXT")
        access_token = read_file("ACCESS_TOKEN.TXT")
        access_token_secret = read_file("ACCESS_TOKEN_SECRET.TXT")

        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        # msgsize: 1577
        #  changes: {u'teamdates': {u'2019-09-29': {delete: [2]}}}
        # if msgsize > 1600:
        #    api.update_status(real_message)
        # else:
        api.update_status(
            "#NHL {{ VERSION }} schedule updated on https://wtangy.se - did your team play last night? Try out https://wtangy.se/DETROIT"
        )
        logging.info("Tweeted and message size was %s", msgsize)

        return True
    return False


def fetch_upstream_schedule(url):
    """geturl a file and do some health checking"""

    with urlopen(url) as page:
        jsondata = json.loads(page.read())
    totalgames = jsondata["totalGames"]

    if totalgames == 0:
        logging.error("parsing data, 0 games found.")
        logging.info(f"URL: {url}")
        return (totalgames, False)
    return (totalgames, jsondata)


def parse_schedule(jsondata):
    """parse the json data into a dict the app is used to.
    as a bonus we also sort things

    The JSON data looks something like this under "dates":

    {'date': '2022-04-28',
      'games': ['teams': {'away': {'team': {'id': 7, 'name': 'Buffalo Sabres'}},
                          'home': {'team': {'id': 6, 'name': 'Boston Bruins'}}}}
    """

    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

    dates = jsondata["dates"]
    for key in dates:
        date = key["date"]
        dict_of_keys_and_matchups[date] = []
        games = key["games"]
        for game in games:
            twoteams = []
            teams = game["teams"]
            # Montréal and St. Louis Blues are added into the get_team() function
            #  So if someone enters it, it works
            # But the lookups are then later done with "MTL" or "STL" respectively,
            #  and in some places with "Montreal Canadiens".
            twoteams.append(
                teams["away"]["team"]["name"]
                .replace("Montréal", "Montreal")
                .replace("St. Louis Blues", "St Louis Blues")
            )
            twoteams.append(
                teams["home"]["team"]["name"]
                .replace("Montréal", "Montreal")
                .replace("St. Louis Blues", "St Louis Blues")
            )
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

    logging.info("parsed schedule")
    return [dict_of_keys_and_matchups_s]


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

# Variables

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
VERSION = os.environ.get("GAE_VERSION", "no_GAE_VERSION_env_found")

NOW = datetime.datetime.now()
FOR_UPDATED = str({"version": str(NOW.isoformat())})
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
# if now is before August we get last year from September until July
if CURRENT_MONTH < 8:
    START_DATE = f"{LAST_YEAR}-08-01"
    END_DATE = f"{CURRENT_YEAR}-07-01"
# if now is in or after August we get this year from September until July
else:
    START_DATE = f"{CURRENT_YEAR}-08-01"
    END_DATE = f"{NEXT_YEAR}-07-01"

URL = f"https://statsapi.web.nhl.com/api/v1/schedule?startDate={START_DATE}&endDate={END_DATE}"
