""" Bits of main.py to test the parsing """

import datetime
import json
import requests

from nhlhelpers import get_team

NOW = datetime.datetime.now()
FOR_UPDATED = str(NOW.isoformat())
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
START_DATE = f"{LAST_YEAR}-08-01"
END_DATE = f"{CURRENT_YEAR}-07-01"
URL = "https://api-web.nhle.com/v1/schedule/now"  # gets update of today for this week
# Do I want to fetch more than just one week?
# What's the likelihood of this breaking and me not having time to fix it asap?


def fetch_upstream_url():
    """Fetch Upstream Schedule"""

    content = requests.get(URL, timeout=5).content

    jsondata = json.loads(content)

    if jsondata["gameWeek"] == []:
        print("Oh no")

    return jsondata


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
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

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

    return json_data


# Below gets the data, so fetching works
JSONDATA = fetch_upstream_url()
# print(json.dumps(JSONDATA, indent=2))

# Then our parsing begins
TEAMDATES = parse_schedule(JSONDATA)
# print(TEAMDATES)
CONTENT = json.loads(make_data_json(TEAMDATES))
print(json.dumps(CONTENT, indent=2))

# print(json.dumps(TEAMDATES, indent=2))
