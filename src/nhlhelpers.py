""" YES, oor no? """

import datetime
import logging


def yesorno(team, teamdates, date2=None):

    """
    Input: team/city/etc, teamdates and date
    Returns: True/False
    """

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")

    chosen_team = get_team(
        team
    )  # returns "New York Rangers" on http://URL/NYR or "" on no match

    ### The YES/NO logic:
    # Check if yesterday's date is a key in teamdates, continue on first hit (not ordered..).
    if chosen_team is None and date2 is None:
        for date in teamdates:
            if yesterday == date:
                return True

    if date2 is None:
        # If no date set - set it to yesterday
        date2 = yesterday
    if dateapi(teamdates, chosen_team, date2):
        return True

    return False


def validatedate(date):
    """Return the date in format %Y-%m-%d if it is a valid date otherwise None.
    Not accepting day in the middle"""

    date_formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%d%m%Y",
        "%Y%m%d",
        "%A, %b %-d",
    ]
    dateinnhlformat = None
    if date:
        for date_format in date_formats:
            try:
                dateinnhlformat = datetime.datetime.strptime(
                    date, date_format
                ).strftime("%Y-%m-%d")
            except ValueError:
                pass

    return dateinnhlformat


def dateapi(teamdates, team=None, date=None):
    """Return true if there was a game on the date
    Return false there was not and if date was unparseable
    Take a team and/or a date as arguments"""

    # Try to make the date provided into the NHL format
    dateinnhlformat = validatedate(date)

    if (dateinnhlformat) and (dateinnhlformat in teamdates) and (team is None):
        # OK there is a game on that date!
        logging.debug(f"no team: {team} but on date: {date} there was a game")
        return True
    if (dateinnhlformat) and (dateinnhlformat in teamdates) and (team is not None):
        # OK there was a team and good date provided!
        # if dateinnhlformat exists a date has been chosen
        # for each list (matchup) at the date chosen
        for matchup in teamdates[dateinnhlformat]:
            for combatant in matchup:
                if combatant == team:
                    logging.debug(f"{team} played on {date}")
                    return True
    logging.debug(f"boo - no game found for team {team} or date {date}")
    return False


def get_city_from_team(cityteam):
    """Returns a city and teamname from teamname in lower case.
    It should return the contents of class wide-matchup from the NHL schedule
    For historical reasons:
      This function used to return a city from a team name, citydict1 had entries like:
      "Washington" : "Washington Capitals",

    This function is not named well anymore, but it works ;)
    Something like, get_city_team_from_team? Confusing in any case..
    """

    citydict1 = {
        "ducks": "Anaheim Ducks",
        "coyotes": "Arizona Coyotes",
        "bruins": "Boston Bruins",
        "buffalo": "Buffalo Sabres",
        "hurricanes": "Carolina Hurricanes",
        "bluejackets": "Columbus Blue Jackets",
        "flames": "Calgary Flames",
        "blackhawks": "Chicago Blackhawks",
        "avalanche": "Colorado Avalanche",
        "stars": "Dallas Stars",
        "redwings": "Detroit Red Wings",
        "oilers": "Edmonton Oilers",
        "panthers": "Florida Panthers",
        "kings": "Los Angeles Kings",
        "wild": "Minnesota Wild",
        "canadiens": "Montreal Canadiens",
        "devils": "New Jersey Devils",
        "predators": "Nashville Predators",
        "islanders": "New York Islanders",
        "rangers": "New York Rangers",
        "senators": "Ottawa Senators",
        "flyers": "Philadelphia Flyers",
        "penguins": "Pittsburgh Penguins",
        "sharks": "San Jose Sharks",
        "blues": "St Louis Blues",
        "lightning": "Tampa Bay Lightning",
        "leafs": "Toronto Maple Leafs",
        "canucks": "Vancouver Canucks",
        "goldenknights": "Vegas Golden Knights",
        "jets": "Winnipeg Jets",
        "capitals": "Washington Capitals",
        "kraken": "Seattle Kraken",
    }

    # Flip because I'm lazy
    citydict1flip = {value: key for key, value in citydict1.items()}
    # This means the dict has keys of "Dallas Stars": "dallas"

    try:
        return citydict1flip[cityteam]
    except KeyError:
        return ""


def get_team_from_city(city):
    """Returns a team abbreviation from cityname."""

    citydict = {
        "ANA": "ANAHEIM",
        "ARI": "ARIZONA",
        "BOS": "BOSTON",
        "BUF": "BUFFALO",
        "CAR": "CAROLINA",
        "CBJ": "COLUMBUS",
        "CGY": "CALGARY",
        "CHI": "CHICAGO",
        "COL": "COLORADO",
        "DAL": "DALLAS",
        "DET": "DETROIT",
        "EDM": "EDMONTON",
        "FLA": "FLORIDA",
        "LAK": "LOSANGELES",
        "MIN": "MINNESOTA",
        "MTL": "MONTREAL",
        "NJD": "NEWJERSEY",
        "NSH": "NASHVILLE",
        "NYI": "NYISLANDERS",
        "NYR": "NYRANGERS",
        "OTT": "OTTAWA",
        "PHI": "PHILADELPHIA",
        "PIT": "PITTSBURGH",
        "SJS": "SANJOSE",
        "SEA": "SEATTLE",
        "STL": "STLOUIS",
        "TBL": "TAMPABAY",
        "TOR": "TORONTO",
        "VAN": "VANCOUVER",
        "VGK": "VEGAS",
        "WPG": "WINNIPEG",
        "WSH": "WASHINGTON",
    }

    # Flip because I'm lazy
    citydictflip = {value: key for key, value in citydict.items()}

    try:
        return citydictflip[city]
    except KeyError:
        return "nope"


def get_team(team):
    """Returns a "City Team Name", as in teamdict1.
    Is in that format because the dictionary in get_team_colors wants that.
    """

    if team:
        team = team.upper()
    else:
        return None

    teamdict1 = {
        "ANA": "Anaheim Ducks",
        "ARI": "Arizona Coyotes",
        "BOS": "Boston Bruins",
        "BUF": "Buffalo Sabres",
        "CAR": "Carolina Hurricanes",
        "CBJ": "Columbus Blue Jackets",
        "CGY": "Calgary Flames",
        "CHI": "Chicago Blackhawks",
        "COL": "Colorado Avalanche",
        "DAL": "Dallas Stars",
        "DET": "Detroit Red Wings",
        "EDM": "Edmonton Oilers",
        "FLA": "Florida Panthers",
        "LAK": "Los Angeles Kings",
        "MIN": "Minnesota Wild",
        "MTL": "Montreal Canadiens",
        "NJD": "New Jersey Devils",
        "NSH": "Nashville Predators",
        "NYI": "New York Islanders",
        "NYR": "New York Rangers",
        "OTT": "Ottawa Senators",
        "PHI": "Philadelphia Flyers",
        "PIT": "Pittsburgh Penguins",
        "SEA": "Seattle Kraken",
        "SJS": "San Jose Sharks",
        "STL": "St Louis Blues",
        "TBL": "Tampa Bay Lightning",
        "TOR": "Toronto Maple Leafs",
        "VAN": "Vancouver Canucks",
        "VGK": "Vegas Golden Knights",
        "WPG": "Winnipeg Jets",
        "WSH": "Washington Capitals",
    }

    # To make DETROITREDWINGS return DET
    teamdict1nospaces = {
        key: value.replace(" ", "").upper() for key, value in teamdict1.items()
    }
    teamdict1nospaces = {value: key for key, value in teamdict1nospaces.items()}

    teamnamedict = {
        "ANA": "DUCKS",
        "ARI": "COYOTES",
        "BOS": "BRUINS",
        "BUF": "SABRES",
        "CAR": "HURRICANES",
        "CBJ": "BLUEJACKETS",
        "CGY": "FLAMES",
        "CHI": "BLACKHAWKS",
        "COL": "AVALANCHE",
        "DAL": "STARS",
        "DET": "REDWINGS",
        "EDM": "OILERS",
        "FLA": "PANTHERS",
        "LAK": "KINGS",
        "MIN": "WILD",
        "MTL": "CANADIENS",
        "NJD": "DEVILS",
        "NSH": "PREDATORS",
        "NYI": "ISLANDERS",
        "NYR": "RANGERS",
        "OTT": "SENATORS",
        "PHI": "FLYERS",
        "PIT": "PENGUINS",
        "SEA": "KRAKEN",
        "SJS": "SHARKS",
        "STL": "BLUES",
        "TBL": "LIGHTNING",
        "TOR": "MAPLELEAFS",
        "VAN": "CANUCKS",
        "VGK": "GOLDENKNIGHTS",
        "WPG": "JETS",
        "WSH": "CAPITALS",
    }

    # Flip the values because I'm lazy
    teamnamedict1 = {value: key for key, value in teamnamedict.items()}

    # Some extra "non-standard" ones
    teamnameshortdict = {
        "CANES": "CAR",
        "JACKETS": "CBJ",
        "HAWKS": "CHI",
        "WINGS": "DET",
        "PREDS": "NSH",
        "SENS": "OTT",
        "PENS": "PIT",
        "BOLTS": "TBL",
        "LEAFS": "TOR",
        "CAPS": "WSH",
        "TAMPA": "TBL",
        "LA": "LAK",
        "NJ": "NJD",
        "SJ": "SJS",
        "LV": "VGK",
        "LASVEGAS": "VGK",
        "MONTRÉAL": "MTL",
        "MONTRÉALCANADIENS": "MTL",
        "ST. LOUIS": "STL",
        "ST. LOUIS BLUES": "STL",
    }

    # First check if someone put in the proper abbreviation
    try:
        thisisyourteam = teamdict1[team]
    except KeyError:
        # If not, then try with the name of the team
        try:
            thisisyourteam = teamdict1[teamnamedict1[team]]
        except KeyError:
            # Then one could have one more for half names, like la, leafs, wings, jackets, etc
            try:
                thisisyourteam = teamdict1[teamnameshortdict[team]]
            except KeyError:
                # Perhaps it's a city name?
                try:
                    thisisyourteam = teamdict1[get_team_from_city(team)]
                except KeyError:
                    # Perhaps it's a citynameteamname?1
                    try:
                        thisisyourteam = teamdict1[teamdict1nospaces[team]]
                    except KeyError:
                        # After that no team selected - nothing in title
                        thisisyourteam = None

    return thisisyourteam


def get_team_colors(team):
    """Return a color and True/False if we found a team
    List is from https://github.com/jimniels/teamcolors.github.io"""

    teamname = get_team(team)

    nhl = {
        "Anaheim Ducks": ["000000", "91764B", "EF5225"],
        "Arizona Coyotes": ["841F27", "000000", "EFE1C6"],
        "Boston Bruins": ["000000", "FFC422"],
        "Buffalo Sabres": ["002E62", "FDBB2F", "AEB6B9"],
        "Calgary Flames": ["E03A3E", "FFC758", "000000"],
        "Carolina Hurricanes": ["E03A3E", "000000", "8E8E90"],
        "Chicago Blackhawks": ["E3263A", "000000"],
        "Colorado Avalanche": ["8B2942", "01548A", "000000", "A9B0B8"],
        "Columbus Blue Jackets": ["00285C", "E03A3E", "A9B0B8"],
        "Dallas Stars": ["006A4E", "000000", "C0C0C0"],
        "Detroit Red Wings": ["EC1F26"],
        "Edmonton Oilers": ["003777", "E66A20"],
        "Florida Panthers": ["C8213F", "002E5F", "D59C05"],
        "Los Angeles Kings": ["000000", "AFB7BA"],
        "Minnesota Wild": ["025736", "BF2B37", "EFB410", "EEE3C7"],
        "Montreal Canadiens": ["BF2F38", "213770"],
        "Nashville Predators": ["FDBB2F", "002E62"],
        "New Jersey Devils": ["E03A3E", "000000"],
        "New York Islanders": ["00529B", "F57D31"],
        "New York Rangers": ["0161AB", "E6393F"],
        "Ottawa Senators": ["E4173E", "000000", "D69F0F"],
        "Philadelphia Flyers": ["F47940", "000000"],
        "Pittsburgh Penguins": ["000000", "D1BD80"],
        "San Jose Sharks": ["05535D", "F38F20", "000000"],
        "Seattle Kraken": ["355464", "99D9D9", "001628"],
        "St Louis Blues": ["0546A0", "FFC325", "101F48"],
        "Tampa Bay Lightning": ["013E7D", "000000", "C0C0C0"],
        "Toronto Maple Leafs": ["003777"],
        "Vancouver Canucks": ["07346F", "047A4A", "A8A9AD"],
        "Vegas Golden Knights": ["333F42", "B4975A", "010101"],
        "Washington Capitals": ["CF132B", "00214E", "000000"],
        "Winnipeg Jets": ["002E62", "0168AB", "A8A9AD"],
    }
    try:
        return nhl[teamname]
    except KeyError:
        return ["000000"]


def get_all_teams():
    """Returns all teams"""

    allteams = {
        "ANA": "Anaheim Ducks",
        "ARI": "Arizona Coyotes",
        "BOS": "Boston Bruins",
        "BUF": "Buffalo Sabres",
        "CAR": "Carolina Hurricanes",
        "CBJ": "Columbus Blue Jackets",
        "CGY": "Calgary Flames",
        "CHI": "Chicago Blackhawks",
        "COL": "Colorado Avalanche",
        "DAL": "Dallas Stars",
        "DET": "Detroit Red Wings",
        "EDM": "Edmonton Oilers",
        "FLA": "Florida Panthers",
        "LAK": "Los Angeles Kings",
        "MIN": "Minnesota Wild",
        "MTL": "Montreal Canadiens",
        "NJD": "New Jersey Devils",
        "NSH": "Nashville Predators",
        "NYI": "New York Islanders",
        "NYR": "New York Rangers",
        "OTT": "Ottawa Senators",
        "PHI": "Philadelphia Flyers",
        "PIT": "Pittsburgh Penguins",
        "SEA": "Seattle Kraken",
        "SJS": "San Jose Sharks",
        "STL": "St Louis Blues",
        "TBL": "Tampa Bay Lightning",
        "TOR": "Toronto Maple Leafs",
        "VAN": "Vancouver Canucks",
        "VGK": "Vegas Golden Knights",
        "WPG": "Winnipeg Jets",
        "WSH": "Washington Capitals",
    }
    return allteams
