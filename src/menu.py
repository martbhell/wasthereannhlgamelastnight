""" YES, oor no? """

import webapp2 # pylint: disable=import-error

DEBUG = False

class MainPage(webapp2.RequestHandler):
    """ Main Page Class """

    def get(self):
        """Return a <strike>friendly</strike> binary HTTP greeting.
        teamdates dictionary is in JSON, from the update_schedule.py file in a cronjob

        """

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!DOCTYPE html>\n\
    <html lang ="en">\n\
    <head><title>Which NHL team do you choose?</title>\n\
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
        <meta name="robots" content="index,follow">\n\
        <meta name="application-name" content="Was there an NHL game yesterday?">\n\
        <meta name="description" content="Indicates with a YES/NO if there was an NHL game on yesterday">\n\
        <meta name="keywords" content="YES,NO,NHL,icehockey,hockey,games,match,wasthereannhlgamelastnight,wasthereannhlgameyesterday,wtangy,wtangln">\n\
        <meta name="author" content="Johan Guldmyr">\n\
        <link href="stylesheets/menu.css" rel="stylesheet">\n\
    </head>\n\
        <body style="text-align: center; padding-top: 5px;">\n\
        <div class="wrapper">')
        # Loop through and write all the teams like:
        allteams = sorted(list(get_all_teams().keys()))
        for ateam in allteams:
            print str(ateam)
            # https://css-tricks.com/snippets/jquery/make-entire-div-clickable/
            self.response.write('<div><a href="%s">%s</a></div>' % (ateam,ateam))

        self.response.write('</div>\n\
        <div class="disclaimer" style="font-size:10px; ">\n\
        <!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->\n\
        <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->\n\
        </div>\n\
    </body>\n\
    </html>\n')

## how to import stuff from wasthereannhlgamelastnight.py ?

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
    return allteams

APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
