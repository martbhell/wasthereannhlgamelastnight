#!/usr/bin/python

# This requires BS4 (findAll vs find_all)

from BeautifulSoup import BeautifulSoup
import urllib2

url= 'http://www.nhl.com/ice/schedulebyseason.htm'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page.read())
debug = True

data = {}
data1 = []
lines = []
# Format2 test: { "Wed Jun 8, 2015" : [ "Tampa Bay", "Chicago" ] }
teamdates = {}
div = soup.find('div', attrs={'class':'card'})
div_body = div.findAll('div', attrs={'class':['day-table-horiz-scrollable-wrapper', 'section-subheader']})

#if debug: print len(div_body)
# every even numbered element including zero is a date, the second one is the games on that date
# put the matchups in each date's key
for col in range(0, len(div_body)):
  teams = []
  if col % 2 == 0:
    matchups_ele = col +1
    #print matchups_ele
    date = div_body[col].contents[0]
    #data1 has a list of all the dates
    data1.append(date)
    #print "############################" + date
    #print div_body[matchups_ele]
    teamdates[date] = []
    data[date] = div_body[matchups_ele]
    matchups = div_body[matchups_ele].findAll('div', attrs={'class':'wide-matchup'})
    for i in range(len(matchups)):
      twoteams = []
      for team in matchups[i].findAll('a', href=True):
        twoteams.append(team['href'][1:])

      # teamdates has a dict of lists with dates as keys and matchups in the lists
      teamdates[date].append(twoteams)

### Making the output (before / after )
# lines = set([u'Sun Oct 25, 2015', u'Fri Feb 12, 2016', u'Sat Dec 12, 2015', u'Tue Feb 9, 2016', u'Thu Nov 12, 2015', u'Mon Mar 14, 2016', u'Tue Feb 23, 2016', u'Fri Apr 8, 2016', u'Sun Mar 20, 2016', u'Fri Dec 1...)
# lines = set([u'Wednesday, Apr 27', u'Monday, Apr 25', u'Monday, Apr 18', u'Wednesday, Apr 20', u'Tuesday, Apr 19', u'Sunday, Apr 24', u'Friday, Apr 22', u'Tuesday, Apr 26', u'Thursday, Apr 21', u'Saturday, Apr 23', u'Sunday, Apr 17'])
####
# teamdates = {u'Sun Oct 25, 2015': [[u'Minnesota', u'Winnipeg'], [u'Calgary', u'NY Rangers'], [u'Los Angeles', u'Edmonton']], u'Fri Feb 12, 2016': [[u'Montr\xe9al', u'Buffalo'], [u'Los Angeles', u'NY Rangers'], [u'Pittsburgh', u'Carolina'] ... }
# teamdates = {u'Wednesday, Apr 27': [[u'flyers', u'capitals'], [u'rangers', u'penguins'], [u'predators', u'ducks']], u'Monday, Apr 25': [[u'penguins', u'rangers'], [u'blackhawks', u'blues'], [u'ducks', u'predators']], u'Monday, Apr 18': [[u'capi ... }
###

# remove all duplicate entries - http://stackoverflow.com/questions/8200342/removing-duplicate-strings-from-a-list-in-python
lines = set(data1)
# printing without unicode - for copy-pasting - not needed if importing
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print "lines = " + str(lines)
#print linestr
teamdatestr = "teamdates = " + str(teamdates).encode('utf8').replace("u'","'")
print "teamdates = " + str(teamdates)
