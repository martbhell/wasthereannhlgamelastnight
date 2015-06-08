import webapp2
import os
import datetime

class MainPage(webapp2.RequestHandler):
    def get(self):
        """Return a friendly HTTP greeting."""
        #data = cmdline("grep 'VISITING TEAM' -B 20 -m 1 NHL.2014-2015.Playoffs.txt|grep 2015|grep -v PLAYOFF")
        #lines = data.split('\n')
        lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']
        now = datetime.datetime.now().strftime("%a %b %-d, %Y")
        now2 = datetime.datetime.now()
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime("%a %b %-d, %Y")
        uri = self.request.uri
        team = uri.split('/')[3].upper()
        color = get_team_colors(team)
        fgcolor = color[0]

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!DOCTYPE html>\n\
        <html lang ="en">\n\
        <head><title>Was there an NHL game last night?')
        try:
          self.response.write(get_team(team))
        except:
          self.response.write(get_team("DET"))
        self.response.write('</title></head>\n\
        <body style="text-align: center; padding-top: 200px;">\n\
            <div class="content" style="font-weight: bold; font-size: 220px; font-family: Arial,sans-serif; text-decoration: none; color: #')
        self.response.write(fgcolor)
        self.response.write(';">\n')

        for game in lines:
            if yesterday == game:
                self.response.write("YES")
                break
            else:
                self.response.write("NO")
                break

        self.response.write('<div class="disclaimer" style="font-size:10px; ">')
        self.response.write(now2)
        self.response.write('</div>\n')
        self.response.write('<!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->\n')
        self.response.write('</div></body></html>')



def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Sorry, nothing at this URL.')
    response.set_status(404)

def get_team(team):
    """Returns a team name
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

    try:
      return(teamdict1[team])
    except KeyError:
      return("")

def get_team_colors(team):
    """Return a color"""
    """ List is from https://github.com/teamcolors/teamcolors.github.io """

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
