import webapp2
import os
import datetime
import NHL_schedule
import re

debug = False

class MainPage(webapp2.RequestHandler):
    def get(self):
        """Return a <strike>friendly</strike> binary HTTP greeting.
        lines and teamdates dictionaries come from the NHL_schedule.py file, it is created manually
        with ../parser/parse_nhl_schedule.py

        TODO: Update examples
        Examples:
        #lines = set([u'Wednesday, Apr 27', u'Monday, Apr 25', u'Monday, Apr 18', u'Wednesday, Apr 20'])
        #teamdates = {u'Wednesday, Apr 27': [[u'flyers', u'capitals'], [u'rangers', u'penguins'], [u'predators', u'ducks']], u'Monday, Apr 25': [[u'p .. )
        """
        lines = NHL_schedule.lines
        teamdates = NHL_schedule.teamdates

        #These are the defaults, only used with "CLI" user agents
        YES = "YES\n"
        NO = "NO\n"

        # Date format: 2017-10-08
	# These are only used while debugging
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        now2 = datetime.datetime.now()

        useragent = self.request.headers['User-Agent'].split('/')[0]
        cliagents = [ "curl", "Wget"]
        # this sometimes (not for Links..) makes user agent without version, like curl, Safari
        uri = self.request.uri
        # Team variable is the argument is used to call yesorno and get_team_colors functions
        team = uri.split('/')[3].upper()

        # Select a color, take second color if the first is black.
        color = get_team_colors(team)
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
            if yesorno(team):
              self.response.write(YES)
            else:
              self.response.write(NO)
            ### End YES/NO logic

        else:
            # YES/NO prettifying..
            YES = "\
            YES\n"
            NO = "\
            NO\n"

            # Headers
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<!DOCTYPE html>\n\
            <html lang ="en">\n\
            <head><title>Was there an NHL game last night?')
            try:
              self.response.write(chosen_team)
            except:
              self.response.write(get_team("DET"))
            self.response.write('</title>\n\
            <meta charset="UTF-8">\n\
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
            <meta name="robots" content="index,follow">\n\
            <meta name="application-name" content="Was there an NHL game last night?">\n\
            <meta name="description" content="Indicates with a YES/NO if there was an NHL game on last night">\n\
            <meta name="keywords" content="YES,NO,NHL,icehockey,hockey,games,match,wasthereannhlgamelastnight">\n\
            <meta name="author" content="Johan Guldmyr">\n\
            </head>\n\
            <body style="text-align: center; padding-top: 5px;">\n\
                <div class="content" style="font-weight: bold; font-size: 220px; font-size: 30vw; font-family: Arial,sans-serif; text-decoration: none; color: #')
            self.response.write(fgcolor)
            self.response.write(';">\n')

            ### The YES/NO logic:
            if yesorno(team):
              self.response.write(YES)
            else:
              self.response.write(NO)
            ### End YES/NO logic

            self.response.write('\
                </div>\n')

            ### The github forkme
            self.response.write('\n\
                <link rel="stylesheet" href="/stylesheets/gh-fork-ribbon.css" property="stylesheet"/>\n\
                <!--[if lt IE 9]>\n\
                  <link rel="stylesheet" href="/stylesheets/gh-fork-ribbon.ie.css" property="stylesheet" />\n\
                  <![endif]-->\n\
                  <div class="github-fork-ribbon-wrapper right-bottom">\n\
                    <div class="github-fork-ribbon">\n\
                        <a href="https://github.com/martbhell/wasthereannhlgamelastnight">Fork me on GitHub</a>\n\
                    </div>\n\
                  </div>\n')
            ### End github forkme
            #self.response.write(now2)

            self.response.write('\n\
                <div class="disclaimer" style="font-size:10px; ">')
            self.response.write('<!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->')
            self.response.write('\n\
                <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->')
            self.response.write('\n\
                </div>\n\
            </body>\n\
            </html>\n')


def yesorno(team):

    """
    Input: team/city/etc
    Returns: True/False
    """

    # lines has dates 
    # teamdates has dates in dict with lists of games
    lines = NHL_schedule.lines
    teamdates = NHL_schedule.teamdates
    requestcontainsanumber = None
    requesthasteamarg = None

## Debug
    if debug:
      yesterday = "2017-10-01"
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
    # Start counter at zero
    yes = 0

    # Date chosen if there is a number in the URI
    try:
      parse = re.search('\d', team)
      if parse != None:
        requestcontainsanumber = True
    except:
      requestcontainsanumber = False

    # Should the arguments be parsed here?
    # Team also chosen if there is a ?t= in the URI
    try:
      parseteam = re.search('\?', team)
      if debug:
        print "parseteam: " + parseteam
      if parseteam != None:
        requesthasteamarg = True
    except:
      requesthasteamarg = False

    # Check in lines list if yesterday's date is in the list, continue on first hit (list is not ordered..).
    if team == "FAVICON.ICO":
      nothing = 0
    elif team == "":
      for date in lines:
          if yesterday == date:
              yes += 1
              continue
      if yes != 0:
              return(True)
      else:
              if debug:
                print "D"
              return(False)

    # Number in the request
    elif requestcontainsanumber:
      if dateapi(team,requesthasteamarg):
        return(True)

    else:
      # A-Team has been chosen!
      # TODO: update format
      # Format of teamdates dict: {'Sun Oct 25, 2015': [['Minnesota', 'Winnipeg'], ['Calgary', 'NY Rangers'], ['Los Angeles', 'Edmonton']], 'Fri Feb 12, 2016': [
      # Check if the team selected is in any of yesterday's lists
      try:
        for list in teamdates[yesterday]:
          for t in list:
            if t == chosen_city:
              yes += 1
              continue
        if yes != 0:
          if debug:
            print "A"
          return(True)
        else:
          if debug:
            print "B"
          return(False)
      # keyerror comes if yesterday's date is not in the list - no games at all
      except KeyError:
          if debug:
            print "C"
          return(False)

def dateapi(team,requesthasteamarg):
    """Return true if there was a game on the date
    Return false there was not and if date was unparseable
    Takes URI requst and requesthasteamarg(true/false) as arguments"""
    # Not accepting day in the middle
    dateNHLformat = None
    DATE_FORMATS = ['%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d', '%d%m%Y', '%Y%m%d', '%A, %b %-d']
    teamdates = NHL_schedule.teamdates
    chosen_team = None
    chosen_city = None

    # a ?team= argument was provided. 
    if requesthasteamarg:
      try:
        findteamarg = team.split("=")
        if debug:
          print findteamarg
        if findteamarg[1]:
          # remove last 5 characters before the first = - assume /DATE?team=TEAM
          chosen_date = findteamarg[0][:-5]
          chosen_team = get_team(findteamarg[1])
          chosen_city = get_city_from_team(chosen_team)
          if debug:
            print chosen_date
      except IndexError:
        # /20151222?team=
        nothing = 0

    #### Date parsing
    # Try to make the date provided into the NHL format
    for date_format in DATE_FORMATS:
        try:
            dateNHLformat = datetime.datetime.strptime(team, date_format).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # First assume it's only the date
    if dateNHLformat and dateNHLformat in teamdates:
      return(True)

    # If arguments are provided, check if chosen_date has a date
    if requesthasteamarg:
      for date_format in DATE_FORMATS:
          try:
              dateNHLformat = datetime.datetime.strptime(chosen_date, date_format).strftime("%Y-%m-%d")
          except ValueError:
              pass
          except UnboundLocalError:
              pass

      # if dateNHLformat exists a date has been chosen
      if chosen_city and dateNHLformat:
      # for each list (matchup) at the date chosen
        for list in teamdates[dateNHLformat]:
          for t in list:
            if t == chosen_city:
              return(True)
    else:
      return(False)

def handle_404(request, response, exception):
    """Return a custom 404 error. Currently unused"""
    response.write('Sorry, nothing at this URL.')
    response.set_status(404)

def get_city_from_team(cityteam):
    """Returns a city and teamname from teamname in lower case. It should return the contents of class wide-matchup from the NHL schedule
    For historical reasons:
      This function used to return a city from a team name, citydict1 had entries like:
      "Washington" : "Washington Capitals",

    This function is not named well anymore, but it works ;) Something like, get_city_team_from_team? Confusing in any case..
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
    "jets" : "Winnipeg Jets",
    "capitals" : "Washington Capitals",
    }

    # Flip because I'm lazy
    citydict1flip = {value: key for key, value in citydict1.items()}

    try:
      return(citydict1flip[cityteam])
    except KeyError:
      return("")


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
    "WPG" : "WINNIPEG",
    "WSH" : "WASHINGTON",
    }

    # Flip because I'm lazy
    citydictflip = {value: key for key, value in citydict.items()}

    try:
      return(citydictflip[city])
    except KeyError:
      return("nope")

def get_team(team):
    """Returns a "City Team Name", as in teamdict1.
    Is in that format because the dictionary in get_team_colors wants that.
    """

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
    "WPG" : "Winnipeg Jets",
    "WSH" : "Washington Capitals",
    }

    # To make DETROITREDWINGS return DET
    teamdict1nospaces = { key:value.replace(" ", "").upper() for key, value in teamdict1.iteritems()}
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
    "WPG" : "JETS",
    "WSH" : "CAPITALS",
    }

    # Flip the values because I'm lazy
    teamnamedict1 = {value: key for key, value in teamnamedict.items()}

    # The rest in this one:
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
    }

    # First check if someone put in the proper abbreviation
    try:
      return(teamdict1[team])
    except KeyError:
    # If not, then try with the name of the team
      try:
        return(teamdict1[teamnamedict1[team]])
      except:
      # Then one could have one more for half names, like la, leafs, wings, jackets, etc
        try:
          return(teamdict1[teamnameshortdict[team]])
        except:
        # Perhaps it's a city name?
          try:
            return(teamdict1[get_team_from_city(team)])
          except:
          #Perhaps it's a citynameteamname?1
            try:
              return(teamdict1[teamdict1nospaces[team]])
            except:
            # After that no team selected - nothing in title
              return("")

def get_team_colors(team):
    """Return a color"""
    """ List is from https://github.com/jimniels/teamcolors.github.io """

    teamname = get_team(team)

    NHL = {
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
        "Vegas Golden Knights" :            ["010101", "B4975A", "333F42"],
        "Washington Capitals" :             ["CF132B", "00214E", "000000"],
        "Winnipeg Jets" :                   ["002E62", "0168AB", "A8A9AD" ]
    }
    try:
      return(NHL[teamname])
    except:
      return(["000000"])


application = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
application.error_handlers[404] = handle_404
