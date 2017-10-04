#!/usr/bin/python

# read json and write output in a format that the app can use as input

import json # for parsing
import urllib2 # for fetching data
import sys # for return codes

#TODO: put in dates in URL automagically
#TODO: Run in a cronjob to update automagically daily?

url= 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2018-04-09'
page = urllib2.urlopen(url)
debug = True

jsondata = json.loads(page.read())

# want to use a file rather than fetch from the URL above?
#fileread = open("testdata.json", "r")
#jsondata = json.loads(fileread.read())
#if debug: print jsondata

data = {}
data1 = []
lines = []
teamdates = {}

######## JSON "schema"

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
  print "totalGames not found in data, adjust start and enddate"
  sys.exit(31)

dates = jsondata['dates']
for key in dates:
  date = key['date']
  teamdates[date] = []
  data1.append(date)
  games = key['games']
  for game in games:
    twoteams = []
    teams = game['teams']
    twoteams.append(teams['away']['team']['name'])
    twoteams.append(teams['home']['team']['name'])
    teamdates[date].append(twoteams)

# End result at some point needed to look like:
#        lines = set([u'2017-11-14', u'2018-04-04', u'2017-11-01'])
#        teamdates = {u'2017-11-14': [[u'Buffalo Sabres', u'Pittsburgh Penguins'], [u'Columbus Blue Jackets', u'Montr\xe9al Canadiens'] ], u'2018-04-04': [[u'Ottawa Senators', u'Buffalo Sabres'], [u'Chicago Blackhawks', u'St. Louis Blues']] }

# remove all duplicate entries - http://stackoverflow.com/questions/8200342/removing-duplicate-strings-from-a-list-in-python
lines = set(data1)
# printing without unicode - for copy-pasting - not needed if importing
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print "lines = " + str(lines)
#print linestr
#teamdatestr = "teamdates = " + str(teamdates).encode('utf8').replace("u'","'")
print "teamdates = " + str(teamdates)
