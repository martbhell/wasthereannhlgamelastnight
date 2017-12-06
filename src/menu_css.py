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

        self.response.headers['Content-Type'] = 'text/css'
        # Loop through and write all the teams:
        allteams = sorted(list(wasthereannhlgamelastnight.get_all_teams().keys()))
        # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
        colordict = {}
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
            }\n' % (ateam,colordict[ateam]))


MENU_CSS = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
