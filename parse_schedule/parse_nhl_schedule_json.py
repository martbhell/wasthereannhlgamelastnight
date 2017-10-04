#!/usr/bin/python

# goal is to read json and write output in a format that the app can use as input

import json # for parsing
import urllib2 # for fetching data
import sys # for return codes

#url= 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2018-04-09'
#page = urllib2.urlopen(url)
debug = True

#jsondata = json.loads(page.read())

fileread = open("testdata.json", "r")
jsondata = json.loads(fileread.read())

#if debug: print jsondata

data = {}
data1 = []
lines = []
# Format2 test: { "Wed Jun 8, 2015" : [ "Tampa Bay", "Chicago" ] }
teamdates = {}

######## JSON

# "schema":

# { "dates" : [
#   { "date":"2017-10-05", 
#     "games": [ 
#     { "gamePK": 2017020005, "gameDate": "2017-10-05T23:00:00Z", "status": {}, "teams": 
#       { "away": 
#         { "team": { "id": 18, "name": "Nashvile Predators", "link": "/api/v1/teams/18" } }
#       }, { "home":
#         { "team": { "id": 6, "name": "Boston Bruins", "link": "/api/v1/teams/6" } }
#       } 
#     },
#     { "gamePK": 2017020006, "gameDate": "2017-10-05T23:00:00Z", "status": {}, "teams": 
#       { "away": 
#         { "team": { "id": 8, "name": "Montreal Canadiens", "link": "/api/v1/teams/8" } }
#       }, { "home":
#         { "team": { "id": 7, "name": "Buffalo Sabres", "link": "/api/v1/teams/7" } }
#       } 
#     } ]
#    }, 
#   { "date":"2017-10-06",
#     "games": [ ]
#   } 
# }
#     

if jsondata['totalGames'] == 0:
  print "totalGames found, adjust start and enddate"
  sys.exit(31)

dates = jsondata['dates']
for key in dates:
  date = key['date']
  teamdates[date] = []
  # convert date
  data1.append(date)
  games = key['games']
  for game in games:
    twoteams = []
    teams = game['teams']
    # remove city name (keep only last word?)
    # lowercase?
    twoteams.append(teams['away']['team']['name'])
    twoteams.append(teams['home']['team']['name'])
    teamdates[date].append(twoteams)

# End result at some point needed to look like:
#lines = set([u'Wednesday, Jun 15', u'Sunday, Jun 12'])
#teamdates = {u'Wednesday, Jun 15': [[u'sharks', u'penguins']], u'Sunday, Jun 12': [[u'penguins', u'sharks']]}

# remove all duplicate entries - http://stackoverflow.com/questions/8200342/removing-duplicate-strings-from-a-list-in-python
lines = set(data1)
# printing without unicode - for copy-pasting - not needed if importing
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print "lines = " + str(lines)
#print linestr
teamdatestr = "teamdates = " + str(teamdates).encode('utf8').replace("u'","'")
print "teamdates = " + str(teamdates)
