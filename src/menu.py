""" Menu, oor no? """

# pylint: disable=too-few-public-methods,line-too-long

import webapp2 # pylint: disable=import-error
import json
import wasthereannhlgamelastnight

class MainPage(webapp2.RequestHandler):
    """ Menu Page Class"""

    def get(self):
        """Return a menu where one can choose a team

        """

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!DOCTYPE html>\n\
    <html lang ="en">\n\
    <head><title>Which NHL team do you choose?</title>\n')
        self.response.write(wasthereannhlgamelastnight.COMMON_META)
        self.response.write('<link href="stylesheets/menu.css" rel="stylesheet">\n\
        <link href="menu_team.css" rel="stylesheet">\n\
    </head>\n\
        <body style="text-align: center; padding-top: 5px;">\n\
        <div class="wrapper">')
        # Loop through and write all the teams like:
        allteams = self.get_teams()
        darkteams = ["BUF", "CBJ", "EDM", "NYI", "NYR", "STL", "TBL", "TOR", "VAN", "WPG"]
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            # https://css-tricks.com/snippets/jquery/make-entire-div-clickable/
            if ateam in darkteams:
                self.response.write('<a href="%s" class="%s"><div><font color=white>%s</font></div></a>' % (ateam, ateam, ateam))
            else:
                self.response.write('<a href="%s" class="%s"><div>%s</div></a>' % (ateam, ateam, ateam))

        self.response.write('</div>\n')
        self.response.write(wasthereannhlgamelastnight.DISCLAIMER)

        self.response.write('</body>\n\
        </html>\n')
    @staticmethod
    def get_teams():
        """ Return a sorted list of teams """
        allteams = sorted(list(wasthereannhlgamelastnight.get_all_teams().keys()))
        return allteams

APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)

########

class CSSPage(webapp2.RequestHandler):
    """ CSS Page Class """

    def get(self):
        """Return CSS used to color boxes """

        self.response.headers['Content-Type'] = 'text/css'
        # Loop through and write all the teams:
        allteams = sorted(list(wasthereannhlgamelastnight.get_all_teams().keys()))
        # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
        colordict = {}
        # If we use
        # https://raw.githubusercontent.com/jimniels/teamcolors/master/static/data/teams.json
        # we would need to pick which of the colors to show. Sometimes it's 3rd, 2nd, first...
        #longteamname = wasthereannhlgamelastnight.get_team(ateam)
        for ateam in allteams:
            colors = wasthereannhlgamelastnight.get_team_colors(ateam)
            backgroundcolor = colors[0]
            try:
                backgroundcolor2 = colors[1]
            except IndexError:
                backgroundcolor2 = colors[0]
            if backgroundcolor == "000000":
                backgroundcolor = backgroundcolor2
            colordict[ateam] = backgroundcolor
        # Make CSS
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            self.response.write('.wrapper > a.%s { \n\
                background-color: #%s; \n\
            }\n' % (ateam, colordict[ateam]))


MENU_CSS = webapp2.WSGIApplication([
    ('/.*', CSSPage),
], debug=True)
