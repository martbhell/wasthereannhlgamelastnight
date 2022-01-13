import datetime
import os
import sys
import json
import logging
import tweepy
from jsondiff import diff
from urllib.request import urlopen
from flask import request
from flask import Flask, render_template, make_response, jsonify
import NHLHelpers
from google.cloud import storage
import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import NotFound

# https://cloud.google.com/datastore/docs/reference/libraries#client-libraries-usage-python

app = Flask(__name__)

# Setup logging https://cloud.google.com/logging/docs/setup/python
CLIENT = google.cloud.logging.Client()
CLIENT.setup_logging()

#http://exploreflask.com/en/latest/views.html
@app.route('/')
def view_root():
    return the_root()

@app.route('/<string:var1>/')
def view_team(var1):
    return the_root(var1, var2=False)

@app.route('/<string:var1>/<string:var2>/')
def view_teamdate(var1, var2):
    return the_root(var1, var2)

# Use the_root for both /DETROIT and /DETROIT/20220122
def the_root(var1=False, var2=False):

    # Set some tomorrow things for when a date or team has not been specified
    # tomorrow set to today if none is set
    # because today is like tomorrow if you know what I mean (wink wink)
    tomorrow = datetime.datetime.now()
    tomorrow1 = tomorrow.strftime("%Y%m%d")
    tomorrowurl = "/%s" % (tomorrow1)

    ########

    team1 = None
    date1 = None

    arguments = [ var1, var2 ]
    for arg in arguments:
        if NHLHelpers.get_team(arg):
            team1 = arg
            # If we have a team set tomorrowurl like /teamname/date
            tomorrowurl = "/%s/%s" % (team1, tomorrow1)
        elif NHLHelpers.validatedate(arg):
            date1 = NHLHelpers.validatedate(arg)
            # If an argument is a date we set tomorrow to one day after that
            tomorrow = datetime.datetime.strptime(
                date1, "%Y-%m-%d"
            ) + datetime.timedelta(days=1)
            tomorrow1 = tomorrow.strftime("%Y%m%d")
    # If we have a good team and date we have both in tomorrowurl
    if team1 and date1:
        tomorrowurl = "/%s/%s" % (team1, tomorrow1)

    teamlongtext = None
    if team1:
        teamlongtext = NHLHelpers.get_team(team1)

    ########

    fgcolor = give_me_a_color(team1)

    ########

    ########

    agent=request.headers.get('User-Agent')
    try:
        short_agent=agent.split("/")[0]
    except:
        short_agent=agent
    yesorno="YES"

    if short_agent in CLIAGENTS:
        return render_template('cli.html', yesorno=yesorno, agent=agent)
    return render_template('index.html', yesorno=yesorno, agent=agent, team=team1, teamlongtext=teamlongtext, date=date1, fgcolor=fgcolor, tomorrow=tomorrow, tomorrowurl=tomorrowurl)

@app.route('/update_schedule')
def update_schedule():

    # default bucket is in this format: project-id.appspot.com
    # https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
    version = os.environ.get(
            "GAE_VERSION", "no_GAE_VERSION_env_found"
            )
    if version == "None":
        filename = "py3_schedule"
        updated_filename = "py3_updated_schedule"
    else:
        filename = "py3_schedule_" + version
        updated_filename = "py3_updated_schedule_" + version

    logging.info("Using filename %s and updated_filename %s" % (filename, updated_filename))

    ####

    [totalgames, jsondata] = fetch_upstream_schedule(URL)

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
            old_content = read_file(filename)
        if old_content == content:
            try:
                last_updated = read_file(updated_filename)
                _msg = "Not updating schedule - it is current."
                logging.info(_msg)
            except NotFound:
                create_file(updated_filename, FOR_UPDATED)
                last_updated = read_file(updated_filename)
            logging.info("Last updated: %s" % last_updated)
        else:
            changes = diff(json.loads(old_content), json.loads(content))
            logging.info("Changes: %s", changes)
            create_file(filename, content)
            create_file(updated_filename, FOR_UPDATED)
            # Only send e-mails outside playoffs
            #  (potential spoilers - games are removed from the schedule)
            if CURRENT_MONTH < 4 or CURRENT_MONTH > 6:
                send_an_email(
                    diff(json.loads(old_content), json.loads(content)), True, False # False - without twitter
                )
            return render_template('update_schedule.html', version=version, filename=filename, totalgames=totalgames, last_updated=last_updated, changes=changes), 202

    #return jsonify(jsondata)

    return render_template('update_schedule.html', version=version, filename=filename, totalgames=totalgames, last_updated=last_updated, changes=changes)


@app.route('/get_schedule')
def get_schedule():

    version = os.environ.get(
            "GAE_VERSION", "no_GAE_VERSION_env_found"
            )
    if version == "None":
        filename = "py3_schedule"
    else:
        filename = "py3_schedule_" + version

    logging.info("Using filename %s and updated_filename %s" % (filename, updated_filename))

    content = read_file(filename)
    parsed = json.loads(content)
    return jsonify(parsed)

@app.route('/menu')
def menu():

    allteams = sorted(list(NHLHelpers.get_all_teams().keys()))
    reallyallteams = NHLHelpers.get_all_teams()

    return render_template('menu.html', allteams=allteams, reallyallteams=reallyallteams)

@app.route('/css/menu_team.css')
def menu_css():

    allteams = sorted(list(NHLHelpers.get_all_teams().keys()))
    # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
    colordict = {}
    # If we use
    # https://raw.githubusercontent.com/jimniels/teamcolors/master/static/data/teams.json
    # we would need to pick which of the colors to show. Sometimes it's 3rd, 2nd, first...
    for ateam in allteams:
        # Loop through colors and don't pick black as background for the box
        colors = NHLHelpers.get_team_colors(ateam)
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
    # TODO: Why isn't it css if we grab file directly? Looks OK in dev console..
    # TODO: Put meta/disclaimer/google analytics in some variable.
   
    resp = make_response(render_template('menu_team.css', allteams=allteams, colordict=colordict, whitetext=whitetext, yellowtext=yellowtext, mimetype="text/css"))
    resp.headers['Content-Type'] = 'text/css'
    return resp 

@app.route('/version')
def version():
    """ Fetch a file and render it """

    return get_version()

# We set_version in update_schedule.py

def get_version():
    """ Fetch a file and return JSON """

    # https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
    version = os.environ.get(
            "GAE_VERSION", "no_GAE_VERSION_env_found"
            )
    if version == "None":
        filename = "py3_updated_schedule"
    else:
        filename = "py3_updated_schedule_" + version

    jsondata = read_file(filename)

    return jsonify(jsondata)

def give_me_a_color(team):
    """ Select a color, take second color if the first is black. """

    color = NHLHelpers.get_team_colors(team)
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
        client = storage.Client()
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
    logging.info("Trying to create filename %s in bucket_name %s, content size is %s" % (filename, bucket_name, get_size(content)))
    blob.upload_from_string(content, content_type='application/json')
    # TODO How to retry / add backoff
    # TODO How to add acl ?     https://cloud.google.com/storage/docs/access-control/create-manage-lists#json-api says default is project-private..


def stat_file(filename):
    """ stat a file
    This returns a CLASS, fetch properties in the results with var.id, not var['id'] ???
    https://cloud.google.com/storage/docs/viewing-editing-metadata#code-samples
    """
    try:
        client = storage.Client()
        storage_client = storage.Client()
    except DefaultCredentialsError:
        logging.error("Could not setup storage client for stat_file")
        return False

    project_name = os.environ.get(
        "GOOGLE_CLOUD_PROJECT", "no_GOOGLE_CLOUD_PROJECT_found"
    )

    bucket_name = project_name + ".appspot.com"

    mybucket = storage_client.bucket(bucket_name)
    logging.info("Trying to stat filename %s in bucket_name %s" % (filename, bucket_name))
    return mybucket.get_blob(filename)

def read_file(filename):
    """ read and return a file! """

    try:
        client = storage.Client()
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
    logging.info("Trying to read filename %s in bucket_name %s" % (filename, bucket_name))
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
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def send_an_email(message, admin=False, twitter=False):
    """ send an e-mail, optionally to the admin """
    # https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.mail
    # TODO: Mail is not available in python3 -- only twitter!

    # https://cloud.google.com/appengine/docs/standard/python3/runtime#environment_variables
    sender_address = "{}@appspot.gserviceaccount.com".format(
       os.environ['GAE_APPLICATION']
    )

    to_email = os.environ["USER_EMAIL"]
    to_name = to_email

    real_message = message
    msgsize = get_size(real_message)
    # size of 2019-2020 schedule was 530016, unclear how large the jsondiff was 2018->2019
    #  50000 is less than 65490 which was in the log of the update
    #  if we change all "Rangers" to "Freeezers" the changes to restore 2019-2020 was 106288
    if msgsize > 150000:
        real_message = "Msgsize is %s, see /get_schedule - Hello new season?" % msgsize
        logging.info(real_message)

# TODO: No e-mail In Python 3 GAE ?
# https://cloud.google.com/appengine/docs/standard/python/migrate-to-python3#mail
###
#    if admin or to_email is None or to_email == "":
#        mail.send_mail_to_admins(
#            sender=sender_address,
#            subject="NHL schedule changed A",
#            body="msgsize: %s \n changes: %s" % (msgsize, real_message),
#        )
#    else:
#        mail.send_mail(
#            sender=sender_address,
#            to="%s <%s>" % (to_name, to_email),
#            subject="NHL schedule changed",
#            body="msgsize: %s \n changes: %s" % (msgsize, real_message),
#        )
    if twitter:
        api_key = os.environ['API_KEY']
        api_secret_key = os.environ['API_SECRET_KEY']
        access_token = os.environ['ACCESS_TOKEN']
        access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        # msgsize: 1577
        #  changes: {u'teamdates': {u'2019-09-29': {delete: [2]}}}
        #if msgsize > 1600:
        #    api.update_status(real_message)
        #else:
        api.update_status("#NHL schedule updated on https://wtangy.se - did your team play last night? Try out https://wtangy.se/DETROIT")
        logging.info("Tweeted and message size was %s", msgsize)

def fetch_upstream_schedule(url):
    """ geturl a file and do some health checking
    """

    with urlopen(url) as page:
        jsondata = json.loads(page.read())
    totalgames = jsondata["totalGames"]

    if totalgames == 0:
        logging.error("parsing data, 0 games found.")
        logging.info("URL: %s" % url)
        #TODO: Set 500 status code
        #self.response.set_status(500)
        return (totalgames, False)
    return (totalgames, jsondata)


def parse_schedule(jsondata):
    """ parse the json data into a dict the app is used to.
        as a bonus we also sort things
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
            # sorry, you can't query montre(withaccent)alcanadiens, all the hard coded bits in the main parser
            #  wasthereannhlgamelastnight.py has MTL without the acute accent
            # without the encode('utf-8') the replace of a unicode gives a unicode error
            # Silmarillionly, mainparser has St Louis Blues, not St. Louis Blues as in the NHL schema
            # TODO: Fix TypeError
            #twoteams.append(teams["away"]["team"]["name"].encode('utf-8').replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            #twoteams.append(teams["home"]["team"]["name"].encode('utf-8').replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(
                dict_of_keys_and_matchups[date]
            )
 
    logging.info("parsed schedule")
    return [dict_of_keys_and_matchups_s]

def make_data_json(teamdates):
    """ turn parsed data into json, end result in JSON should look like:
    {
     "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], }
    }
    """
    data = {}
    data["teamdates"] = teamdates
    json_data = json.dumps(data, sort_keys=True)

    logging.info("made json")
    return json_data


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

# Variables

CLIAGENTS = ["curl", "Wget", "Python-urllib"]

NOW = datetime.datetime.now()
FOR_UPDATED = str(NOW.isoformat())
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
# if now is before August we get last year from September until July
if CURRENT_MONTH < 8:
    START_DATE = "%s-08-01" % LAST_YEAR
    END_DATE = "%s-07-01" % CURRENT_YEAR
# if now is in or after August we get this year from September until July
else:
    START_DATE = "%s-08-01" % CURRENT_YEAR
    END_DATE = "%s-07-01" % NEXT_YEAR

URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s" % (
    START_DATE,
    END_DATE,
)
