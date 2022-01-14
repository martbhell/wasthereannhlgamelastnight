import datetime
import NHLHelpers
import json
from urllib.request import urlopen

NOW = datetime.datetime.now()
FOR_UPDATED = str(NOW.isoformat())
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
START_DATE = "%s-08-01" % LAST_YEAR
END_DATE = "%s-07-01" % CURRENT_YEAR
URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s" % (
  START_DATE,
  END_DATE,
)

def fetch_upstream_url(url):

    with urlopen(url) as page:
        jsondata = json.loads(page.read())
    totalgames = jsondata["totalGames"]

    if totalgames == 0:
        #TODO: Set 500 status code
        #self.response.set_status(500)
        return (totalgames, False)
    return (totalgames, jsondata)

def parse_schedule(jsondata):

    dict_of_keys_and_matchups = {}
    dict_of_keys_and_matchups_s = {}

# json data looks like this under "dates":
# {'date': '2022-04-28', 'totalItems': 9, 'totalEvents': 0, 'totalGames': 9, 'totalMatches': 0, 'games': [{'gamePk': 2021021290, 'link': '/api/v1/game/2021021290/feed/live', 'gameType': 'R', 'season': '20212022', 'gameDate': '2022-04-28T23:00:00Z', 'status': {'abstractGameState': 'Preview', 'codedGameState': '1', 'detailedState': 'Scheduled', 'statusCode': '1', 'startTimeTBD': False}, 'teams': {'away': {'leagueRecord': {'wins': 10, 'losses': 19, 'ot': 6, 'type': 'league'}, 'score': 0, 'team': {'id': 7, 'name': 'Buffalo Sabres', 'link': '/api/v1/teams/7'}}, 'home': {'leagueRecord': {'wins': 19, 'losses': 11, 'ot': 2, 'type': 'league'}, 'score': 0, 'team': {'id': 6, 'name': 'Boston Bruins', 'link': '/api/v1/teams/6'}}}, 'venue': {'id': 5085, 'name': 'TD Garden', 'link': '/api/v1/venues/5085'}, 'content': {'link': '/api/v1/game/2021021290/content'}}, {'gamePk':

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
            # Attempting to fix
            # OK these work without .encode
            #twoteams.append(teams["away"]["team"]["name"].replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            #twoteams.append(teams["home"]["team"]["name"].replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            # What about replacing Montreal
            twoteams.append(teams["away"]["team"]["name"].replace('Montréal', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            twoteams.append(teams["home"]["team"]["name"].replace('Montréal', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
            twoteams_sorted = sorted(twoteams)
            dict_of_keys_and_matchups[date].append(twoteams_sorted)
            dict_of_keys_and_matchups_s[date] = sorted(
                dict_of_keys_and_matchups[date]
            )

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

    return json_data


# Below gets the data, so fetching works
[totalgames, jsondata] = fetch_upstream_url(URL)

# Then our parsing begins
[teamdates] = parse_schedule(jsondata)
# Parse Schedule does not work
# Output is like: 

# {'2021-09-25': [[], []], '2021-09-26': [[], [

#print(teamdates)
content = make_data_json(teamdates)
#print(content)
