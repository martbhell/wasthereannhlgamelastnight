""" YES, oor no? """
import os
import datetime
import json # data is stored in json

import webapp2
import cloudstorage as gcs # we fetch the schedule from gcs

from google.appengine.api import app_identity

DEBUG = False

class MainPage(webapp2.RequestHandler):
    """ Main Page Class """
    def get(self):
        """Return a <strike>friendly</strike> binary HTTP greeting.
        teamdates dictionary is in JSON, from the update_schedule.py file in a cronjob

        """

        theschedule = json.loads(self.read_file())
        global teamdates
        teamdates = theschedule['teamdates']

        #These are the defaults, only used with "CLI" user agents
        yes = "YES\n"
        nope = "NO\n"

        useragent = self.request.headers['User-Agent'].split('/')[0]
        cliagents = ["curl", "Wget", 'Python']
        # this sometimes (not for Links..) makes user agent without version, like curl, Safari
        uri = self.request.uri
        arguments = uri.split('/')
        remove_these = ['wtangy.se', 'https:', 'http:', '', 'localhost:8080', 'wtangy.se', 'wasthereannhlgamelastnight.appspot.com'] # pylint: disable=line-too-long
        for arg in arguments:
            if arg in remove_these:
                arguments.remove(arg)
        arguments = filter(None, arguments) # remove empty strings
        if DEBUG:
            print arguments

        json1 = False
        date1 = None
        # Team variable is the argument is used to call yesorno and get_team_colors functions
        team1 = None
        argcounter = 0

        # TOOD: How to handle if someone enters multiple dates etc?
        for arg in arguments:
            if get_team(arg):
                argcounter = argcounter + 1
                team1 = arg
            elif "json" in arg or "JSON" in arg:
                argcounter = argcounter + 1
                json1 = True
            elif any(char.isdigit() for char in arg):
                argcounter = argcounter + 1
                date1 = arg

        # Select a color, take second color if the first is black.
        [color, foundateam] = get_team_colors(team1)
        fgcolor = color[0]
        try:
            fgcolor2 = color[1]
        except:
            fgcolor2 = color[0]
        if fgcolor == "000000":
            fgcolor = fgcolor2

        ## Minimalistic style if from a CLI tool
        if useragent in cliagents:

            ### The YES/NO logic:
            if yesorno(team1, date1):
                self.response.write(yes)
            else:
                self.response.write(nope)
            ### End YES/NO logic

        else:
            # YES/NO prettifying..
            yes = "\
            YES\n"
            nope = "\
            NO\n"

            # Headers
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<!DOCTYPE html>\n\
            <html lang ="en">\n\
            <head><title>Was there an NHL game yesterday?')
            try:
                teamlongtext = get_team(team1)
            except:
                # Can't figure out what team that was, set no team chosen.
                teamlongtext = ""
            self.response.write(teamlongtext)
            self.response.write('</title>\n\
            <meta charset="UTF-8">\n\
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
            <meta name="robots" content="index,follow">\n\
            <meta name="application-name" content="Was there an NHL game yesterday?">\n\
            <meta name="description" content="Indicates with a YES/NO if there was an NHL game on yesterday">\n\
            <meta name="keywords" content="YES,NO,NHL,icehockey,hockey,games,match,wasthereannhlgamelastnight,wasthereannhlgameyesterday,wtangy,wtangln">\n\
            <meta name="author" content="Johan Guldmyr">\n\
            <meta name="theme-color" content="#')
            self.response.write(fgcolor)
            self.response.write('">\n\
            </head>\n\
            <body style="text-align: center; padding-top: 5px;">\n\
            <div class="content" style="font-weight: bold; font-size: 220px; font-size: 30vw; font-family: Arial,sans-serif; text-decoration: none; color: #') # pylint: disable=line-too-long
            self.response.write(fgcolor)
            self.response.write(';">\n')

            ### The YES/NO logic:
            if yesorno(team1, date1):
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
            </script> \n' % (therewasagame, teamlongtext))

            self.response.write('\
                </div>\n')

            ### The github forkme
            # http://tholman.com/github-corners/
            self.response.write('<a href="https://github.com/martbhell/wasthereannhlgamelastnight" class="github-corner" aria-label="View source on Github"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#') # pylint: disable=line-too-long
            self.response.write(fgcolor)
            self.response.write('; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a><style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>') # pylint: disable=line-too-long

            ### End github forkme
            #self.response.write(now2)

            self.response.write('\n\
                <div class="disclaimer" style="font-size:10px; ">')
            self.response.write('<!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->') # pylint: disable=line-too-long
            self.response.write('\n\
                <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->') # pylint: disable=line-too-long
            self.response.write('\n\
                </div>\n\
            </body>\n\
            </html>\n')

    def read_file(self):
        """ Read the schedule from GCS, return JSON """
        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        bucket = '/' + bucket_name
        filename = bucket + '/schedule'

        with gcs.open(filename) as cloudstorage_file:
            jsondata = cloudstorage_file.read()

        return jsondata


def yesorno(team, date2=None):

    """
    Input: team/city/etc and date
    Returns: True/False
    """

## Debug
    if DEBUG:
        yesterday = "2017-10-14"
        print "yesterday:" + yesterday
        yesterday4 = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday4 = yesterday4.strftime("%Y-%m-%d")
        print "yesterday4:" + yesterday4
    else:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime("%Y-%m-%d")
##

    chosen_team = get_team(team) # returns "New York Rangers" on http://URL/NYR or "" on no match
    chosen_city = get_city_from_team(chosen_team) # outputs "NY Rangers" on http://URL/NYR or "".

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
    if dateapi(chosen_team, date2):
        return True

    return False

def dateapi(team=None, date=None):
    """Return true if there was a game on the date
    Return false there was not and if date was unparseable
    Take a team and/or a date as arguments """
    # Not accepting day in the middle
    dateinnhlformat = None
    date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d', '%d%m%Y', '%Y%m%d', '%A, %b %-d'] # pylint: disable=line-too-long
    chosen_team = team
    chosen_city = None

    # a date was provided
    if date:
        #### Date parsing
        # Try to make the date provided into the NHL format
        for date_format in date_formats:
            try:
                dateinnhlformat = datetime.datetime.strptime(date, date_format).strftime("%Y-%m-%d")
            except ValueError:
                pass

        # First assume it's only the date
        if DEBUG:
            print "datenhl: %s" % dateinnhlformat
        if DEBUG:
            print "chosen: %s" % chosen_team
        if (dateinnhlformat) and (dateinnhlformat in teamdates) and (chosen_team is None):
            if DEBUG:
                print "F1"
            return True
        elif dateinnhlformat and (dateinnhlformat in teamdates) and chosen_team:
            # if dateinnhlformat exists a date has been chosen
            if chosen_team and dateinnhlformat and (dateinnhlformat in teamdates):
                # for each list (matchup) at the date chosen
                for matchup in teamdates[dateinnhlformat]:
                    for combatant in matchup:
                        if combatant == chosen_team:
                            if DEBUG:
                                print "E1"
                            return True
    else:
        if DEBUG:
            print "G1"
        return False

def handle_404(request, response, exception):
    """Return a custom 404 error. Currently unused"""
    response.write('Sorry, nothing at this URL.')
    response.set_status(404)

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
        "blackhawks" : "Chicago Black Hawks",
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
        "CHI" : "Chicago Black Hawks",
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
        return teamdict1[team]
    except KeyError:
        # If not, then try with the name of the team
        try:
            return teamdict1[teamnamedict1[team]]
        except:
            # Then one could have one more for half names, like la, leafs, wings, jackets, etc
            try:
                return teamdict1[teamnameshortdict[team]]
            except:
                # Perhaps it's a city name?
                try:
                    return teamdict1[get_team_from_city(team)]
                except:
                    #Perhaps it's a citynameteamname?1
                    try:
                        return teamdict1[teamdict1nospaces[team]]
                    except:
                        # After that no team selected - nothing in title
                        return None

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
        return(nhl[teamname], True)
    except:
        return(["000000"], False)


APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
APPLICATION.error_handlers[404] = handle_404
