""" Menu, oor no? """

import webapp2 # pylint: disable=import-error
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
        allteams = sorted(list(wasthereannhlgamelastnight.get_all_teams().keys()))
        for ateam in allteams:
            # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
            # https://css-tricks.com/snippets/jquery/make-entire-div-clickable/
            self.response.write('<a href="%s" class="%s"><div>%s</div></a>' % (ateam, ateam, ateam))

        self.response.write('</div>\n')
        self.response.write(wasthereannhlgamelastnight.DISCLAIMER)

        self.response.write('</body>\n\
        </html>\n')

APPLICATION = webapp2.WSGIApplication([
    ('/.*', MainPage),
], debug=True)
