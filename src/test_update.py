""" Bits of main.py to test the parsing """

import datetime
import json
from urllib.request import urlopen

NOW = datetime.datetime.now()
FOR_UPDATED = str(NOW.isoformat())
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
START_DATE = f"{LAST_YEAR}-08-01"
END_DATE = f"{CURRENT_YEAR}-07-01"
URL = f"https://statsapi.web.nhl.com/api/v1/schedule?startDate={START_DATE}&endDate={END_DATE}"


def fetch_upstream_url(url):
    """Fetch Upstream Schedule"""

    with urlopen(url) as page:
        jsondata = json.loads(page.read())
    totalgames = jsondata["totalGames"]

    if totalgames == 0:
        return (totalgames, False)
    return (totalgames, jsondata)


def parse_schedule(jsondata):
    """Parse it"""

    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

    # json data looks something like this under "dates":
    # {'date': '2022-04-28',
    #   'games': ['teams': {'away': {'team': {'id': 7, 'name': 'Buffalo Sabres'}},
    #                       'home': {'team': {'id': 6, 'name': 'Boston Bruins'}}}}

    dates = jsondata["dates"]
    for key in dates:
        date = key["date"]
        dict_of_keys_and_matchups[date] = []
        games = key["games"]
        for game in games:
            twoteams = []
            teams = game["teams"]
            # sorry, you can't query montre(withaccent)alcanadiens, hard coded bits in main parser
            #  wasthereannhlgamelastnight.py has MTL without the acute accent
            # Silmarillionly, mainparser has St Louis Blues, not St. Louis Blues as in the NHLschema
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
[TOTALGAMES, JSONDATA] = fetch_upstream_url(URL)

# Then our parsing begins
[TEAMDATES] = parse_schedule(JSONDATA)
# Parse Schedule does not work
# Output is like:

# {'2021-09-25': [[], []], '2021-09-26': [[], [

# print(teamdates)
content = json.loads(make_data_json(TEAMDATES))
print(json.dumps(content, indent=2))
