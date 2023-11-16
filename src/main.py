""" YES, oor no? """

import datetime
import os
import json
import logging
from urllib.request import urlopen
from device_detector import DeviceDetector
from jsondiff import diff
from flask import request
from flask import Flask, render_template, make_response
from google.cloud import storage
import feedparser
from feedgen.feed import FeedGenerator
import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import NotFound

# start opentelemetry
from opentelemetry import metrics, trace
from opentelemetry.exporter.cloud_monitoring import (
    CloudMonitoringMetricsExporter,
)
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

#
import nhlhelpers

#

set_global_textmap(CloudTraceFormatPropagator())

resource = Resource.create(
    {
        "service.name": "wtangy",
        "service.namespace": "wtangy_main",
        "service.instance.id": "wtangy_1",
    }
)

tracer_provider = TracerProvider(resource=resource)
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
    # BatchSpanProcessor buffers spans and sends them in batches in a
    # background thread. The default parameters are sensible, but can be
    # tweaked to optimize your performance
    BatchSpanProcessor(cloud_trace_exporter)
)

meter_provider = MeterProvider(
    metric_readers=[
        PeriodicExportingMetricReader(
            CloudMonitoringMetricsExporter(), export_interval_millis=5000
        )
    ],
    resource=resource,
)

trace.set_tracer_provider(tracer_provider)
metrics.set_meter_provider(meter_provider)

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# end opentelemetry

# https://cloud.google.com/datastore/docs/reference/libraries#client-libraries-usage-python

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

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
            tomorrow = datetime.datetime.strptime(
                date1, "%Y-%m-%d"
            ) + datetime.timedelta(days=1)
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

    useragent = request.headers.get("User-Agent")
    logging.debug(f"User-Agent: {useragent}")
    if useragent:
        device = DeviceDetector(useragent).parse()

    ### The YES/NO logic:
    yesorno = "NO"
    if nhlhelpers.yesorno(team1, teamdates, date1):
        yesorno = "YES"

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
                atom_feed_manager(diff(json.loads(old_content), json.loads(content)))
            else:
                logging.info(
                    "Would have sent an update notification, but it might be playoff folks!"
                )
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

    # Step 2: Modify the feed entries and metadata
    modified_entries = []
    for entry in parsed_feed.entries:
        # Modify entry attributes as needed
        #  except we are not modifying them..
        modified_entries.append(entry)

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

    # Here we add a new entry
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
        f"It's available on https://wtangy.se/get_schedule. <br /> <br /> {message}"
    )
    new_update.link(href="https://wtangy.se/get_schedule", rel="alternate")
    new_update.category([{"term": veri}])
    author = {"name": "cron"}
    new_update.author(author)

    # Step 9: Save the new Atom feed as a string and write to GCS
    new_atom_feed_xml = new_feed.atom_str(pretty=True)
    create_file(filename, new_atom_feed_xml)

    return True


def fetch_upstream_schedule(url):
    """geturl a file and do some health checking"""

    jsondata = None

    with urlopen(url) as page:
        jsondata = import_lazily("json").loads(page.read())

    totalgames = 0
    if jsondata:
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
