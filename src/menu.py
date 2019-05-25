""" Menu, oor no? """

# pylint: disable=too-few-public-methods,line-too-long

import webapp2  # pylint: disable=import-error
import wasthereannhlgamelastnight
import Helpers


class MainPage(webapp2.RequestHandler):
    """ Menu Page Class"""

    def get(self):
        """Return a menu where one can choose a team

        """

        self.response.headers["Content-Type"] = "text/html"
        self.response.write(
            '<!DOCTYPE html>\n\
    <html lang ="en">\n\
    <head><title>Which NHL team do you choose?</title>\n'
        )
        self.response.write(wasthereannhlgamelastnight.COMMON_META)
        self.response.write(
            '<link href="/stylesheets/menu.css" rel="stylesheet">\n\
        <link type="text/css" href="/menu_team.css" rel="stylesheet">\n\
        <script src="/preferences.js"></script>\n\
        <script src="/colorpreferences.js"></script>\n\
    </head>\n\
        <body style="text-align: center; padding-top: 5px;">\n\
        <div id="wrapper" class="wrapper">'
        )
        # Loop through and write all the teams like:
        allteams = self.get_teams()
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            # https://css-tricks.com/snippets/jquery/make-entire-div-clickable/
            longteamname = Helpers.get_team(ateam)
            # https://davidwalsh.name/html5-storage
            # Note the use of %r instead of %s in the onClick to have it print 'DET' instead of " det" ..
            # Used to store the chosen team in a local browser variable
            self.response.write(
                '<a href="/%s" class="%s" title="%s" onClick="saveTeam(%r)"><div>%s</div></a>'
                % (longteamname.replace(" ", ""), ateam, longteamname, ateam, ateam)
            )
        self.response.write(
            """<a href="/" title="Black Background Color" onClick="saveBgColor('#1e1e1e')"><div>Black BG Color</div></a>"""
        )
        self.response.write(
            """<a href="/" title="CLEAR Team&Color Selection" onClick="localStorage.clear()"><div>Clear Team <br />& Color Selection</div></a>"""
        )
        self.response.write("</div>\n")
        self.response.write(wasthereannhlgamelastnight.DISCLAIMER)

        self.response.write(
            """
                <script src="/colorpreferences.js"></script>
                <script> loadBgColor(); </script>
            </body>
        </html>"""
        )

    @staticmethod
    def get_teams():
        """ Return a sorted list of teams """
        allteams = sorted(list(Helpers.get_all_teams().keys()))
        return allteams


APPLICATION = webapp2.WSGIApplication([("/.*", MainPage)], debug=True)

########


class CSSPage(webapp2.RequestHandler):
    """ CSS Page Class """

    def get(self):
        """Return CSS used to color boxes """

        self.response.headers["Content-Type"] = "text/css"
        # Loop through and write all the teams:
        allteams = sorted(list(Helpers.get_all_teams().keys()))
        # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
        colordict = {}
        # If we use
        # https://raw.githubusercontent.com/jimniels/teamcolors/master/static/data/teams.json
        # we would need to pick which of the colors to show. Sometimes it's 3rd, 2nd, first...
        for ateam in allteams:
            # Loop through colors and don't pick black as background for the box
            colors = Helpers.get_team_colors(ateam)
            backgroundcolor = colors[0]
            try:
                backgroundcolor2 = colors[1]
            except IndexError:
                backgroundcolor2 = colors[0]
            if backgroundcolor == "000000":
                backgroundcolor = backgroundcolor2
            colordict[ateam] = backgroundcolor
        # Make CSS
        # Default font color is black.
        # With some backgrounds black is not so readable so we change it to white.
        # https://en.wikipedia.org/wiki/Template:NHL_team_color might be good, it talks about contrast at least..
        whitetext = [
            "ARI",
            "BUF",
            "CBJ",
            "DET",
            "EDM",
            "NSH",
            "NYI",
            "NYR",
            "TBL",
            "TOR",
            "VAN",
            "WPG",
        ]
        yellowtext = ["STL"]
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            self.response.write(
                ".wrapper > a.%s { \n\
                background-color: #%s; \n"
                % (ateam, colordict[ateam])
            )
            if ateam in whitetext:
                self.response.write("\t\tcolor: white \n }\n")
            elif ateam in yellowtext:
                self.response.write("\t\tcolor: yellow \n }\n")
            else:
                self.response.write("}\n")


########

MENU_CSS = webapp2.WSGIApplication([("/.*", CSSPage)], debug=True)
