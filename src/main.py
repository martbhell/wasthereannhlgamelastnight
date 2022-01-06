import datetime
from flask import request
from flask import Flask, render_template, make_response
import NHLHelpers

app = Flask(__name__)

#http://exploreflask.com/en/latest/views.html
@app.route('/')
def view_root():
    return the_root()

@app.route('/<string:var1>/')
def view_team(var1):
    return the_root(var1, var2=False)

@app.route('/<string:var1>/<string:var2>/')
def view_teamdate(var1, var2):
    return the_root(var1, var2)

# Use the_root for both /DETROIT and /DETROIT/20220122
def the_root(var1=False, var2=False):

    # Set some tomorrow things for when a date or team has not been specified
    # tomorrow set to today if none is set
    # because today is like tomorrow if you know what I mean (wink wink)
    tomorrow = datetime.datetime.now()
    tomorrow1 = tomorrow.strftime("%Y%m%d")
    tomorrowurl = "/%s" % (tomorrow1)

    ########

    team1 = None
    date1 = None

    arguments = [ var1, var2 ]
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

    ########

    fgcolor = give_me_a_color(team1)

    ########

    ########

    agent=request.headers.get('User-Agent')
    try:
        short_agent=agent.split("/")[0]
    except:
        short_agent=agent
    yesorno="YES"

    if short_agent in CLIAGENTS:
        return render_template('cli.html', yesorno=yesorno, agent=agent)
    return render_template('index.html', yesorno=yesorno, agent=agent, team=team1, date=date1, fgcolor=fgcolor, tomorrow=tomorrow, tomorrowurl=tomorrowurl)

@app.route('/update_schedule')
def update_schedule():

    return render_template('update_schedule.html')

@app.route('/menu')
def menu():

    allteams = sorted(list(NHLHelpers.get_all_teams().keys()))

    return render_template('menu.html', allteams=allteams)

@app.route('/css/menu_team.css')
def menu_css():

    allteams = sorted(list(NHLHelpers.get_all_teams().keys()))
    # Recreate give_me_a_color classmethod because I couldn't figure out how to call it
    colordict = {}
    # If we use
    # https://raw.githubusercontent.com/jimniels/teamcolors/master/static/data/teams.json
    # we would need to pick which of the colors to show. Sometimes it's 3rd, 2nd, first...
    for ateam in allteams:
        # Loop through colors and don't pick black as background for the box
        colors = NHLHelpers.get_team_colors(ateam)
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

    # https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Auto-placement_in_CSS_Grid_Layout
    # TODO: Why isn't it css if we grab file directly? Looks OK in dev console..
    # TODO: Put meta/disclaimer/google analytics in some variable.
   
    resp = make_response(render_template('menu_team.css', allteams=allteams, colordict=colordict, whitetext=whitetext, yellowtext=yellowtext, mimetype="text/css"))
    resp.headers['Content-Type'] = 'text/css'
    return resp 


def give_me_a_color(team):
    """ Select a color, take second color if the first is black. """

    color = NHLHelpers.get_team_colors(team)
    fgcolor = color[0]
    try:
        fgcolor2 = color[1]
    except IndexError:
        fgcolor2 = color[0]
    if fgcolor == "000000":
        fgcolor = fgcolor2

    return fgcolor



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
