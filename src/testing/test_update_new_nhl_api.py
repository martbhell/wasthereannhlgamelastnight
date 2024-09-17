""" Bits of main.py to test the parsing """

import json
from datetime import datetime, timedelta

import requests
from jsondiff import diff

from nhlhelpers import get_team

###


def fetch_upstream_url(fetch_this_url):
    """Fetch Upstream Schedule
    returns json and a string of the date of the schedule
    that we got redirected to
    """

    geturl = requests.get(fetch_this_url, timeout=5)
    content = geturl.content
    destination_url = geturl.url
    schedule_date = destination_url.split("/")[-1]
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(schedule_date, date_format)

    jsondata = json.loads(content)

    if jsondata["gameWeek"] == []:
        print("Oh no")

    return (jsondata, date_obj)


def parse_schedule(jsondata):
    """Parse it"""

    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

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

    dates = jsondata["gameWeek"]
    for key in dates:
        date = key["date"]
        # print(date)
        dict_of_keys_and_matchups[date] = []
        games = key["games"]
        for game in games:
            twoteams = []
            # teams = game["teams"]
            # sorry, you can't query montre(withaccent)alcanadiens, hard coded bits in main parser
            #  wasthereannhlgamelastnight.py has MTL without the acute accent
            # Silmarillionly, mainparser has St Louis Blues, not St. Louis Blues as in the NHLschema
            awayabbrev = game["awayTeam"]["abbrev"]
            homeabbrev = game["homeTeam"]["abbrev"]
            twoteams.append(
                get_team(awayabbrev)
                #                .replace("Montréal", "Montreal")
                #                .replace("St. Louis Blues", "St Louis Blues")
            )
            twoteams.append(
                get_team(homeabbrev)
                #                .replace("Montréal", "Montreal")
                #                .replace("St. Louis Blues", "St Louis Blues")
            )
            if None in twoteams:
                continue
            print(twoteams)
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

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

    return json_data


# Below gets the data, so fetching works
URL = "https://api-web.nhle.com/v1/schedule"  #
URL_NOW = f"{URL}/now"  # gets update of today for this week

DATE_FORMAT = "%Y-%m-%d"
JSONDATA, SCHEDULE_DATE = fetch_upstream_url(URL_NOW)
EXTRA_WEEKS = 3
TEAMDATES = parse_schedule(JSONDATA)
CONTENT = json.loads(make_data_json(TEAMDATES))
for WEEK in range(1, EXTRA_WEEKS):
    NEXT_WEEK = SCHEDULE_DATE + timedelta(days=7 * WEEK)
    NEXT = str(NEXT_WEEK).split(" ", maxsplit=1)[0]
    EXTRA_URL = f"{URL}/{NEXT}"
    EXTRA_JSONDATA, EXTRA_SCHEDULE_DATE = fetch_upstream_url(EXTRA_URL)
    EXTRA_TEAMDATES = parse_schedule(EXTRA_JSONDATA)
    EXTRA_CONTENT = json.loads(make_data_json(EXTRA_TEAMDATES))
    # print(EXTRA_CONTENT)
    CONTENT["teamdates"].update(
        EXTRA_CONTENT["teamdates"]
    )  # .update updates the dictionary
    print(EXTRA_CONTENT)
    # print(CONTENT)
    # print(type(CONTENT))
    # print(type(CONTENT["teamdates"]))
    # print(type(json.loads(CONTENT["teamdates"])))
    # print(diff(json.dumps(CONTENT), json.dumps(EXTRA_CONTENT)))
    print(diff(CONTENT, EXTRA_CONTENT))
    # print(json.dumps(EXTRA_CONTENT))

# Now content contains next ~4 (possibly off by one :D ?) weeks of games
# CONTENT["teamdates"] = CONTENT["teamdates"]
# print(CONTENT)
# print(json.dumps(CONTENT, indent=2))

NOW = datetime.now()
FOR_UPDATED = str({"version": str(NOW.isoformat())})
[CURRENT_MONTH, CURRENT_YEAR] = (
    NOW.month,
    NOW.year,
)  # used to silence updates during playoffs
