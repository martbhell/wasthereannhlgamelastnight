""" YES, oor no? """
import os
import datetime
import json # data is stored in json

import webapp2 # pylint: disable=import-error
import cloudstorage as gcs # we fetch the schedule from gcs pylint: disable=import-error

from google.appengine.api import app_identity # pylint: disable=import-error

DEBUG = False

class MainPage(webapp2.RequestHandler):
    """ Main Page Class """

    def get(self):
        """Return a <strike>friendly</strike> binary HTTP greeting.
        teamdates dictionary is in JSON, from the update_schedule.py file in a cronjob

        """
        teamdates = json.loads(read_file())['teamdates']

        #These are the defaults, only used with "CLI" user agents
        yes = "YES\n"
        nope = "NO\n"

        useragent = self.request.headers['User-Agent'].split('/')[0]
        # this sometimes (not for Links..) makes user agent without version, like curl, Safari
        uri = self.request.uri
        arguments = list(set(uri.split('/')))

        for arg in REMOVE_THESE:
            while arg in arguments:
                arguments.remove(arg)

        date1 = None
        # Team variable is the argument is used to call yesorno and get_team_colors functions
        team1 = None

        # TOOD: How to handle if someone enters multiple dates etc?
        for arg in arguments:
            if get_team(arg):
                team1 = arg
            elif any(char.isdigit() for char in arg):
                date1 = arg

        fgcolor = self.give_me_a_color(team1)
        ## Minimalistic style if from a CLI tool
        if useragent in CLIAGENTS:

            ### The YES/NO logic:
            if yesorno(team1, teamdates, date1):
                self.response.write(yes)
            else:
                self.response.write(nope)
            ### End YES/NO logic

        else:
            # YES/NO prettifying..
            yes = "\
            <a title='Was There An NHL Game Yesterday?'>YES</a>\n"
            nope = "\
            <a title='Was There An NHL Game Yesterday?'>NO</a>\n"

            # Headers
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<!DOCTYPE html>\n\
        <html lang ="en">\n\
        <head><title>Was there an NHL game yesterday?')
            teamlongtext = get_team(team1)
            if teamlongtext is None:
                teamlongtext = ""
                # Can't figure out what team that was, set no team chosen.
            self.response.write('%s</title>\n' % teamlongtext)
            # Write args as js vars for preferences.js. undefined var is now "None"
            self.response.write('<script>\nvar argteam, argdate, argfgcolor;\nvar argteam = %r;\nvar argdate = %r;\nvar argfgcolor = %r;\n</script>\n' % (str(team1), str(date1), str(fgcolor))) # pylint: disable=line-too-long
            self.response.write(COMMON_META)
            self.response.write('<meta name="theme-color" content="#%s">\n\
            <script src="/preferences.js"></script>\n' %fgcolor)
            self.response.write('<script> loadTeam(); </script>\n\
            <link type="text/css" href="/stylesheets/app.css" rel="stylesheet">\n\
        </head>\n\
            <body style="text-align: center; padding-top: 5px;">\n\
            <div class="content" style="font-weight: bold; font-size: 220px; font-size: 30vw; font-family: Arial,sans-serif; text-decoration: none; color: #%s;">\n' % (fgcolor)) # pylint: disable=line-too-long

            ### The YES/NO logic:
            if yesorno(team1, teamdates, date1):
                self.response.write(yes)
                therewasagame = "YES"
            else:
                self.response.write(nope)
                therewasagame = "NO"
            ### End YES/NO logic

            ### Structured Data
            self.response.write(' \
            <script type="application/ld+json">\n\
            { \n\
              "@context": "http://schema.org/", \n\
              "@type": "Thing", \n\
              "url": "https://wtangy.se", \n\
              "name": "Was There An NHL Game Yesterday?", \n\
              "description": "Did My Team Play Yesterday In NHL?", \n\
              "potentialAction": { \n\
                "name": "N/A", \n\
                "result": "%s", \n\
                "agent": "%s" \n\
              } \n\
            } \n\
             </script>\n\t\t\t</div> \n' % (therewasagame, teamlongtext))

            ### The github forkme
            # http://tholman.com/github-corners/
            self.response.write('\t\t\t<a href="https://github.com/martbhell/wasthereannhlgamelastnight" class="github-corner" aria-label="View source on Github"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#') # pylint: disable=line-too-long
            self.response.write(fgcolor)
            self.response.write('; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a>') # pylint: disable=line-too-long
            ### The menu icon to the left
            # https://github.com/google/material-design-icons/blob/master/navigation/svg/production/ic_menu_48px.svg
            self.response.write('<a href="/menu" title="menu"><svg xmlns="http://www.w3.org/2000/svg" width="10%" height="50%" style="fill:#') # pylint: disable=line-too-long
            self.response.write(fgcolor)
            self.response.write('; position: absolute; top: 0; border: 0; left: 0"><path d="M6 36h36v-4H6v4zm0-10h36v-4H6v4zm0-14v4h36v-4H6z"/></svg></a>') # pylint: disable=line-too-long

            ### End icons
            #self.response.write(now2)

            self.response.write(DISCLAIMER)
            self.response.write('</body>\n\
        </html>\n')

    @classmethod
    def give_me_a_color(cls, team1):
        """ Select a color, take second color if the first is black. """

        color = get_team_colors(team1)
        fgcolor = color[0]
        try:
            fgcolor2 = color[1]
        except IndexError:
            fgcolor2 = color[0]
        if fgcolor == "000000":
            fgcolor = fgcolor2

        return fgcolor

def read_file():
    """ Read the schedule from GCS, return JSON """
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())

    version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
    bucket = '/' + bucket_name
    # for dev_appserver we get version None
    if version == "None":
        filename = bucket + '/schedule'
    else:
        filename = bucket + '/schedule_' + version

    with gcs.open(filename) as cloudstorage_file:
        jsondata = cloudstorage_file.read()

    return jsondata

def yesorno(team, teamdates, date2=None):

    """
    Input: team/city/etc, teamdates and date
    Returns: True/False
    """

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")

    chosen_team = get_team(team) # returns "New York Rangers" on http://URL/NYR or "" on no match

    ### The YES/NO logic:
    # Check if yesterday's date is a key in teamdates, continue on first hit (not ordered..).
    if chosen_team is None and date2 is None:
        for date in teamdates:
            if yesterday == date:
                if DEBUG:
                    print "D1"
                return True

    if date2 is None:
        # If no date set - set it to yesterday
        date2 = yesterday
    if dateapi(teamdates, chosen_team, date2):
        return True

    return False

def dateapi(teamdates, team=None, date=None):
    """Return true if there was a game on the date
    Return false there was not and if date was unparseable
    Take a team and/or a date as arguments """
    # Not accepting day in the middle
    dateinnhlformat = None
    date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d', '%d%m%Y', '%Y%m%d', '%A, %b %-d'] # pylint: disable=line-too-long

    # a date was provided
    if date:
        #### Date parsing
        # Try to make the date provided into the NHL format
        for date_format in date_formats:
            try:
                dateinnhlformat = datetime.datetime.strptime(date, date_format).strftime("%Y-%m-%d")
            except ValueError:
                pass

        # First assume it's only the date and no team
        if (dateinnhlformat) and (dateinnhlformat in teamdates) and (team is None):
            if DEBUG:
                print "F1"
                print "datenhl: %s" % dateinnhlformat
                print "chosen: %s" % team
            return True
        elif dateinnhlformat and (dateinnhlformat in teamdates) and team:
            # if dateinnhlformat exists a date has been chosen
            # for each list (matchup) at the date chosen
            for matchup in teamdates[dateinnhlformat]:
                for combatant in matchup:
                    if combatant == team:
                        return True
    else:
        if DEBUG:
            print "datenhl: %s" % dateinnhlformat
            print "chosen: %s" % team
            print "G1"
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
        "ducks" : "Anaheim Ducks",
        "coyotes" : "Arizona Coyotes",
        "bruins" : "Boston Bruins",
        "buffalo" : "Buffalo Sabres",
        "hurricanes" : "Carolina Hurricanes",
        "bluejackets" : "Columbus Blue Jackets",
        "flames" : "Calgary Flames",
        "blackhawks" : "Chicago Blackhawks",
        "avalanche" : "Colorado Avalanche",
        "stars" : "Dallas Stars",
        "redwings" : "Detroit Red Wings",
        "oilers" : "Edmonton Oilers",
        "panthers" : "Florida Panthers",
        "kings" : "Los Angeles Kings",
        "wild" : "Minnesota Wild",
        "canadiens" : "Montreal Canadiens",
        "devils" : "New Jersey Devils",
        "predators" : "Nashville Predators",
        "islanders" : "New York Islanders",
        "rangers" : "New York Rangers",
        "senators" : "Ottawa Senators",
        "flyers" : "Philadelphia Flyers",
        "penguins" : "Pittsburgh Penguins",
        "sharks" : "San Jose Sharks",
        "blues" : "St Louis Blues",
        "lightning" : "Tampa Bay Lightning",
        "leafs" : "Toronto Maple Leafs",
        "canucks" : "Vancouver Canucks",
        "goldenknights" : "Vegas Golden Knights",
        "jets" : "Winnipeg Jets",
        "capitals" : "Washington Capitals",
    }

    # Flip because I'm lazy
    citydict1flip = {value: key for key, value in citydict1.items()}

    try:
        return citydict1flip[cityteam]
    except KeyError:
        return ""


def get_team_from_city(city):
    """Returns a team abbreviation from cityname.
    """

    citydict = {
        "ANA" : "ANAHEIM",
        "ARI" : "ARIZONA",
        "BOS" : "BOSTON",
        "BUF" : "BUFFALO",
        "CAR" : "CAROLINA",
        "CBJ" : "COLUMBUS",
        "CGY" : "CALGARY",
        "CHI" : "CHICAGO",
        "COL" : "COLORADO",
        "DAL" : "DALLAS",
        "DET" : "DETROIT",
        "EDM" : "EDMONTON",
        "FLA" : "FLORIDA",
        "LAK" : "LOSANGELES",
        "MIN" : "MINNESOTA",
        "MTL" : "MONTREAL",
        "NJD" : "NEWJERSEY",
        "NSH" : "NASHVILLE",
        "NYI" : "NYISLANDERS",
        "NYR" : "NYRANGERS",
        "OTT" : "OTTAWA",
        "PHI" : "PHILADELPHIA",
        "PIT" : "PITTSBURGH",
        "SJS" : "SANJOSE",
        "STL" : "STLOUIS",
        "TBL" : "TAMPABAY",
        "TOR" : "TORONTO",
        "VAN" : "VANCOUVER",
        "VGK" : "VEGAS",
        "WPG" : "WINNIPEG",
        "WSH" : "WASHINGTON",
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
        "ANA" : "Anaheim Ducks",
        "ARI" : "Arizona Coyotes",
        "BOS" : "Boston Bruins",
        "BUF" : "Buffalo Sabres",
        "CAR" : "Carolina Hurricanes",
        "CBJ" : "Columbus Blue Jackets",
        "CGY" : "Calgary Flames",
        "CHI" : "Chicago Blackhawks",
        "COL" : "Colorado Avalanche",
        "DAL" : "Dallas Stars",
        "DET" : "Detroit Red Wings",
        "EDM" : "Edmonton Oilers",
        "FLA" : "Florida Panthers",
        "LAK" : "Los Angeles Kings",
        "MIN" : "Minnesota Wild",
        "MTL" : "Montreal Canadiens",
        "NJD" : "New Jersey Devils",
        "NSH" : "Nashville Predators",
        "NYI" : "New York Islanders",
        "NYR" : "New York Rangers",
        "OTT" : "Ottawa Senators",
        "PHI" : "Philadelphia Flyers",
        "PIT" : "Pittsburgh Penguins",
        "SJS" : "San Jose Sharks",
        "STL" : "St Louis Blues",
        "TBL" : "Tampa Bay Lightning",
        "TOR" : "Toronto Maple Leafs",
        "VAN" : "Vancouver Canucks",
        "VGK" : "Vegas Golden Knights",
        "WPG" : "Winnipeg Jets",
        "WSH" : "Washington Capitals",
    }

    # To make DETROITREDWINGS return DET
    teamdict1nospaces = {key:value.replace(" ", "").upper() for key, value in teamdict1.iteritems()}
    teamdict1nospaces = {value: key for key, value in teamdict1nospaces.items()}

    teamnamedict = {
        "ANA" : "DUCKS",
        "ARI" : "COYOTES",
        "BOS" : "BRUINS",
        "BUF" : "SABRES",
        "CAR" : "HURRICANES",
        "CBJ" : "BLUEJACKETS",
        "CGY" : "FLAMES",
        "CHI" : "BLACKHAWKS",
        "COL" : "AVALANCHE",
        "DAL" : "STARS",
        "DET" : "REDWINGS",
        "EDM" : "OILERS",
        "FLA" : "PANTHERS",
        "LAK" : "KINGS",
        "MIN" : "WILD",
        "MTL" : "CANADIENS",
        "NJD" : "DEVILS",
        "NSH" : "PREDATORS",
        "NYI" : "ISLANDERS",
        "NYR" : "RANGERS",
        "OTT" : "SENATORS",
        "PHI" : "FLYERS",
        "PIT" : "PENGUINS",
        "SJS" : "SHARKS",
        "STL" : "BLUES",
        "TBL" : "LIGHTNING",
        "TOR" : "MAPLELEAFS",
        "VAN" : "CANUCKS",
        "VGK" : "GOLDENKNIGHTS",
        "WPG" : "JETS",
        "WSH" : "CAPITALS",
    }

    # Flip the values because I'm lazy
    teamnamedict1 = {value: key for key, value in teamnamedict.items()}

    # Some extra "non-standard" ones
    teamnameshortdict = {
        "CANES" : "CAR",
        "JACKETS" : "CBJ",
        "HAWKS" : "CHI",
        "WINGS" : "DET",
        "PREDS" : "NSH",
        "SENS" : "OTT",
        "PENS" : "PIT",
        "BOLTS" : "TBL",
        "LEAFS" : "TOR",
        "CAPS" : "WSH",
        "TAMPA" : "TBL",
        "LA" : "LAK",
        "NJ" : "NJD",
        "SJ" : "SJS",
        "LV" : "VGK",
        "LASVEGAS" : "VGK",
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
                    #Perhaps it's a citynameteamname?1
                    try:
                        thisisyourteam = teamdict1[teamdict1nospaces[team]]
                    except KeyError:
                        # After that no team selected - nothing in title
                        thisisyourteam = None

    return thisisyourteam

def get_team_colors(team):
    """Return a color and True/False if we found a team
    List is from https://github.com/jimniels/teamcolors.github.io """

    teamname = get_team(team)

    nhl = {
        "Anaheim Ducks" :                   ["000000", "91764B", "EF5225"],
        "Arizona Coyotes" :                 ["841F27", "000000", "EFE1C6"],
        "Boston Bruins" :                   ["000000", "FFC422"],
        "Buffalo Sabres" :                  ["002E62", "FDBB2F", "AEB6B9"],
        "Calgary Flames" :                  ["E03A3E", "FFC758", "000000"],
        "Carolina Hurricanes" :             ["E03A3E", "000000", "8E8E90"],
        "Chicago Blackhawks" :              ["E3263A", "000000"],
        "Colorado Avalanche" :              ["8B2942", "01548A", "000000", "A9B0B8"],
        "Columbus Blue Jackets" :           ["00285C", "E03A3E", "A9B0B8"],
        "Dallas Stars" :                    ["006A4E", "000000", "C0C0C0"],
        "Detroit Red Wings" :               ["EC1F26"],
        "Edmonton Oilers" :                 ["003777", "E66A20"],
        "Florida Panthers" :                ["C8213F", "002E5F", "D59C05"],
        "Los Angeles Kings" :               ["000000", "AFB7BA"],
        "Minnesota Wild" :                  ["025736", "BF2B37", "EFB410", "EEE3C7"],
        "Montreal Canadiens" :              ["BF2F38", "213770"],
        "Nashville Predators" :             ["FDBB2F", "002E62"],
        "New Jersey Devils" :               ["E03A3E", "000000"],
        "New York Islanders" :              ["00529B", "F57D31"],
        "New York Rangers" :                ["0161AB", "E6393F"],
        "Ottawa Senators" :                 ["E4173E", "000000", "D69F0F"],
        "Philadelphia Flyers" :             ["F47940", "000000"],
        "Pittsburgh Penguins" :             ["000000", "D1BD80"],
        "San Jose Sharks" :                 ["05535D", "F38F20", "000000"],
        "St Louis Blues" :                  ["0546A0", "FFC325", "101F48"],
        "Tampa Bay Lightning" :             ["013E7D", "000000", "C0C0C0"],
        "Toronto Maple Leafs" :             ["003777"],
        "Vancouver Canucks" :               ["07346F", "047A4A", "A8A9AD"],
        "Vegas Golden Knights" :            ["333F42", "B4975A", "010101"],
        "Washington Capitals" :             ["CF132B", "00214E", "000000"],
        "Winnipeg Jets" :                   ["002E62", "0168AB", "A8A9AD"]
    }
    try:
        return nhl[teamname]
    except KeyError:
        return ["000000"]

def get_all_teams():
    """Returns all teams"""

    allteams = {
        "ANA" : "Anaheim Ducks",
        "ARI" : "Arizona Coyotes",
        "BOS" : "Boston Bruins",
        "BUF" : "Buffalo Sabres",
        "CAR" : "Carolina Hurricanes",
        "CBJ" : "Columbus Blue Jackets",
        "CGY" : "Calgary Flames",
        "CHI" : "Chicago Blackhawks",
        "COL" : "Colorado Avalanche",
        "DAL" : "Dallas Stars",
        "DET" : "Detroit Red Wings",
        "EDM" : "Edmonton Oilers",
        "FLA" : "Florida Panthers",
        "LAK" : "Los Angeles Kings",
        "MIN" : "Minnesota Wild",
        "MTL" : "Montreal Canadiens",
        "NJD" : "New Jersey Devils",
        "NSH" : "Nashville Predators",
        "NYI" : "New York Islanders",
        "NYR" : "New York Rangers",
        "OTT" : "Ottawa Senators",
        "PHI" : "Philadelphia Flyers",
        "PIT" : "Pittsburgh Penguins",
        "SJS" : "San Jose Sharks",
        "STL" : "St Louis Blues",
        "TBL" : "Tampa Bay Lightning",
        "TOR" : "Toronto Maple Leafs",
        "VAN" : "Vancouver Canucks",
        "VGK" : "Vegas Golden Knights",
        "WPG" : "Winnipeg Jets",
        "WSH" : "Washington Capitals",
    }
    return allteams

GOOGLE_ANALYTICS = "<!-- Global site tag (gtag.js) - Google Analytics -->\n\
                   <script async src='https://www.googletagmanager.com/gtag/js?id=UA-1265550-3'></script>\n\
                   <script>\n\
                     window.dataLayer = window.dataLayer || [];\n\
                     function gtag(){dataLayer.push(arguments);}\n\
                     gtag('js', new Date());\n\n\
                     gtag('config', 'UA-1265550-3');\n\
                   </script>\n"

DISCLAIMER = '<div class="disclaimer" style="font-size:10px; ">\n\
              <!-- wtangy.se is not affiliated with any teams or leagues that have their colors displayed. -->\n\
              <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->\n\
              </div>\n'
COMMON_META = '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
            <meta name="robots" content="index,follow">\n\
            <meta name="application-name" content="Was there an NHL game yesterday?">\n\
            <meta name="description" content="Indicates with a YES/NO if there was an NHL game on yesterday">\n\
            <meta name="keywords" content="YES,NO,NHL,icehockey,hockey,games,match,wasthereannhlgamelastnight,wasthereannhlgameyesterday,wtangy,wtangln">\n\
            <meta name="author" content="Johan Guldmyr">\n\
            %s' % GOOGLE_ANALYTICS

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
REMOVE_THESE = ['wtangy.se', 'https:', 'http:', '', 'localhost:8080', 'wtangy.se', 'wasthereannhlgamelastnight.appspot.com'] # pylint: disable=line-too-long

APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
