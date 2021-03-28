""" YES, oor no? """

from __future__ import print_function  # python3
import os
import datetime
import json  # data is stored in json

import webapp2  # pylint: disable=import-error
import cloudstorage as gcs  # we fetch the schedule from gcs

import NHLHelpers # a file of our own that has some help functions used by several scripts

from google.appengine.api import app_identity  # pylint: disable=import-error

DEBUG = False


class MainPage(webapp2.RequestHandler):
    """ Main Page Class """

    def get(self):
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        # meaning this function can be split out into more functions/classes
        """Return a <strike>friendly</strike> binary HTTP greeting.
        teamdates dictionary is in JSON, from the update_schedule.py file in a cronjob

        """
        teamdates = json.loads(read_file())["teamdates"]

        # These are the defaults, only used with "CLI" user agents
        yes = "YES\n"
        nope = "NO\n"

        useragent = self.request.headers["User-Agent"].split("/")[0]
        # this sometimes (not for Links..) makes user agent without version, like curl, Safari
        uri = self.request.uri
        arguments = list(set(uri.split("/")))

        for arg in REMOVE_THESE:
            while arg in arguments:
                arguments.remove(arg)

        date1 = None
        # Team variable is the argument is used to call yesorno and get_team_colors functions
        team1 = None

        # Set some tomorrow things for when a date or team has not been specified
        # tomorrow set to today if none is set
        # because today is like tomorrow if you know what I mean (wink wink)
        tomorrow = datetime.datetime.now()
        tomorrow1 = tomorrow.strftime("%Y%m%d")
        tomorrowurl = "/%s" % (tomorrow1)
        # TOOD: How to handle if someone enters multiple dates etc?
        for arg in arguments:
            if NHLHelpers.get_team(arg):
                team1 = arg
                # If we have a team set tomorrowurl like /teamname/date
                tomorrowurl = "/%s/%s" % (team1, tomorrow1)
            elif NHLHelpers.validatedate(arg):
                date1 = NHLHelpers.validatedate(arg)
                # If an argument is a date we set tomorrow to one day after that
                tomorrow = datetime.datetime.strptime(
                    date1, "%Y-%m-%d"
                ) + datetime.timedelta(days=1)
                tomorrow1 = tomorrow.strftime("%Y%m%d")
        # If we have a good team and date we have both in tomorrowurl
        if team1 and date1:
            tomorrowurl = "/%s/%s" % (team1, tomorrow1)

        fgcolor = self.give_me_a_color(team1)
        ## Minimalistic style if from a CLI tool
        if useragent in CLIAGENTS:

            ### The YES/NO logic:
            if NHLHelpers.yesorno(team1, teamdates, date1):
                self.response.write(yes)
            else:
                self.response.write(nope)
            ### End YES/NO logic

        else:
            # YES/NO prettifying..
            yes = """
              <div class="shiny" id="shiny"><a title='Was There An NHL Game Yesterday?'>YES</a></div>
            """
            nope = """
              <div class="shiny" id="shiny"><a title='Was There An NHL Game Yesterday?'>NO</a></div>
            """

            # Headers
            self.response.headers["Content-Type"] = "text/html"
            self.response.write(
                """
            <!DOCTYPE html>
            <html lang ="en">
            <head><title>Was there an NHL game yesterday?
            """
            )
            teamlongtext = NHLHelpers.get_team(team1)
            if teamlongtext is None:
                teamlongtext = ""
                # Can't figure out what team that was, set no team chosen.
                tomorrowurl = "/%s" % (tomorrow1)
            self.response.write("%s</title>\n" % teamlongtext)
            # Write args as js vars for preferences.js. undefined var is now "None"
            self.response.write(
                """
            <script>
            var argteam, argdate, argfgcolor, tomorrow;
            var argteam = %r;
            var argdate = %r;
            var argfgcolor = %r;
            var tomorrow = %r;
            </script>
            """
                % (str(team1), str(date1), str(fgcolor), str(tomorrow))
            )
            self.response.write(COMMON_META)
            self.response.write(
                """
            <meta name="theme-color" content="#%s">
            <script src="/preferences.js"></script>
            <script src="/shiny.umd.js"></script>
            <link type="text/css" href="/stylesheets/shiny.css" rel="stylesheet">
                """
                % fgcolor
            )

            self.response.write(
                """
            <script> loadTeam(); </script>
            <link type="text/css" href="/stylesheets/app.css" rel="stylesheet">
            </head>
            <body style="text-align: center; padding-top: 5px;">
              <div id="content" class="content" style="font-weight: bold; font-size: 220px; font-size: 30vw; font-family: Arial,sans-serif; text-decoration: none; color: #%s;">\n"""  # pylint: disable=line-too-long
                % (fgcolor)
            )

            if NHLHelpers.yesorno(team1, teamdates, date1):
                self.response.write(yes)
                therewasagame = "YES"
            else:
                self.response.write(nope)
                therewasagame = "NO"
            ### End YES/NO logic

            ### Structured Data
            self.response.write(
                """
              <script type="application/ld+json">
              {
                "@context": "http://schema.org/",
                "@type": "Thing",
                "url": "https://wtangy.se",
                "name": "Was There An NHL Game Yesterday?",
                "description": "Did My Team Play Yesterday In NHL?",
                "potentialAction": {
                  "name": "N/A",
                  "result": "%s",
                  "agent": "%s"
                }
              }
              </script>
              </div>
            """
                % (therewasagame, teamlongtext)
            )

            ### The github forkme
            # http://tholman.com/github-corners/
            self.response.write(
                """
              <a href="https://github.com/martbhell/wasthereannhlgamelastnight" class="github-corner" aria-label="View source on Github"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#%s; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a>"""  #  pylint: disable=line-too-long
                % fgcolor
            )
            ### The menu icon to the left
            # https://github.com/google/material-design-icons/blob/master/navigation/svg/production/ic_menu_48px.svg
            # Double %% because unsupported-format-character-0x22-at-in-python-string
            self.response.write(
                """
              <a href="/menu" title="menu">
              <svg xmlns="http://www.w3.org/2000/svg" width="10%%" height="50%%" style="fill:#%s;
              position: absolute; top: 0; border: 0; left: 0">
              <path d="M6 36h36v-4H6v4zm0-10h36v-4H6v4zm0-14v4h36v-4H6z"/></svg></a>"""
                % fgcolor
            )

            ### The right arrow sign bottom right
            # https://css-tricks.com/snippets/css/css-triangle/
            self.response.write(
                """
              <a href="%s" title="what about tomorrow?" class="right-arrow-corner" aria-label="Is there a game tomorrow?"><div class="arrow-right" style="width:0; height:0; border-top: 60px solid transparent; border-bottom: 60px solid transparent; border-left: 60px solid #%s; right: 0px; bottom: 0px; position: absolute;"></div></a>"""  # pylint: disable=line-too-long
                % (tomorrowurl, fgcolor)
            )

            ### End icons
            # self.response.write(now2)

            self.response.write(DISCLAIMER)
            self.response.write(
                """
                <script src="/colorpreferences.js"></script>
                <script> loadBgColor(); </script>
            </body>
            </html>"""
            )

    @classmethod
    def give_me_a_color(cls, team1):
        """ Select a color, take second color if the first is black. """

        color = NHLHelpers.get_team_colors(team1)
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
    bucket_name = os.environ.get(
        "BUCKET_NAME", app_identity.get_default_gcs_bucket_name()
    )

    version = os.environ["CURRENT_VERSION_ID"].split(".")[0]
    bucket = "/" + bucket_name
    # for dev_appserver we get version None
    if version == "None":
        filename = bucket + "/schedule"
    else:
        filename = bucket + "/schedule_" + version

    with gcs.open(filename) as cloudstorage_file:
        jsondata = cloudstorage_file.read()

    return jsondata

# https://developers.google.com/analytics/devguides/collection/gtagjs/ip-anonymization
GOOGLE_ANALYTICS = """<!-- Global site tag (gtag.js) - Google Analytics -->
            <script async src='https://www.googletagmanager.com/gtag/js?id=UA-1265550-3'></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'UA-1265550-3', { 'anonymize_ip': true });
            </script>"""

DISCLAIMER = """<div class="disclaimer" style="font-size:10px; ">
              <!-- wtangy.se is not affiliated with any teams or leagues that have their colors displayed. -->
              <!-- Written by Johan Guldmyr - source is available at https://github.com/martbhell/wasthereannhlgamelastnight -->
              </div>"""
COMMON_META = (
    """<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico"/>
            <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
            <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
            <link rel="manifest" href="/site.webmanifest">
            <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5">
            <meta name="msapplication-TileColor" content="#603cba">
            <meta name="robots" content="index,follow">
            <meta name="application-name" content="Was there an NHL game yesterday?">
            <meta name="description" content="Indicates with a YES/NO if there was an NHL game on yesterday">
            <meta name="keywords" content="YES,NO,NHL,icehockey,hockey,games,match,wasthereannhlgamelastnight,wasthereannhlgameyesterday,wtangy,wtangln">
            <meta name="author" content="Johan Guldmyr">
            %s"""
    % GOOGLE_ANALYTICS
)

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
REMOVE_THESE = [
    "wtangy.se",
    "https:",
    "http:",
    "",
    "localhost:8080",
    "wtangy.se",
    "wasthereannhlgamelastnight.appspot.com",
]

APPLICATION = webapp2.WSGIApplication([("/.*", MainPage)], debug=True)
