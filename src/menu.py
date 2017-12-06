""" YES, oor no? """

import webapp2 # pylint: disable=import-error
import wasthereannhlgamelastnight

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
        <link href="menu_team.css" rel="stylesheet">\n\
    </head>\n\
        <body style="text-align: center; padding-top: 5px;">\n\
        <div class="wrapper">')
        # Loop through and write all the teams like:
        allteams = sorted(list(wasthereannhlgamelastnight.get_all_teams().keys()))
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            # https://css-tricks.com/snippets/jquery/make-entire-div-clickable/
            self.response.write('<a href="%s" class="%s"><div>%s</div></a>' % (ateam,ateam,ateam))

        self.response.write('</div>\n\
        <div class="disclaimer" style="font-size:10px; ">\n\
        <!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->\n\
        <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->\n\
        </div>\n\
    </body>\n\
    </html>\n')

APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
