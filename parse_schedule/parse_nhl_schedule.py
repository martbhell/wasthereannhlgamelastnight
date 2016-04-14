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
  teams = {}
  if col % 2 == 0:
    matchups_ele = col +1
    #print matchups_ele
    print "############################" + div_body[col].contents[0]
    date = div_body[col].contents[0]
    #print div_body[matchups_ele]
    data[date] = div_body[matchups_ele]
    matchups = div_body[matchups_ele].findAll('div', attrs={'class':'wide-matchup'})
    for i in range(len(matchups)):
      teams[i] = []
      for team in matchups[i].findAll('a', href=True):
        teams[i].append(team['href'][1:])
    print teams

### teamdates
    # date and teams playing that date:  first a <div class=teamName"> <a ..>Detroit</a></div>
    # data2 = [u'Chicago', u'Tampa Bay']
#    tivs = row.findAll("div", {"class": "teamName"})
#    data2 = []
#    for a in tivs:
#        data2.append(a.find('a').contents[0])
#    # first try to add append the list (of two teams) to the date (list and key) in teamdates dict
#    try:
#      teamdates[date[0]].append(data2)
#    except:
#    # If that date(list and key) does not exist, create it first
#      teamdates[date[0]] = []
#      teamdates[date[0]].append(data2)

# team dates look like: {u'Mon Jun 15, 2015': [u'Tampa Bay', u'Chicago'], u'Sat Jun 13, 2015': [u'Chicago', u'Tampa Bay'], u'Wed Jun 17, 2015': [u'Chicago', u'Tampa Bay']}
# without utf8: 'Fri Oct 9, 2015': [['Winnipeg', 'New Jersey'], ['NY Rangers', 'Columbus'], ['Toronto', 'Detroit'], ['Chicago', 'NY Islanders'], ['Arizona', 'Los Angeles']],
#print teamdates
### end teamdates

# We want this in a list, like:
# lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']

for tr in data1:
    d8 = tr[0]
    d8.encode("UTF8")
    lines.append(d8)

# Using the list as it is:
#print lines[0]
# remove all duplicate entries - http://stackoverflow.com/questions/8200342/removing-duplicate-strings-from-a-list-in-python
lines = set(lines)
# printing without unicode - for copy-pasting - not needed if importing
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print "lines = " + str(lines)
#print linestr
teamdatestr = "teamdates = " + str(teamdates).encode('utf8').replace("u'","'")
print "teamdates = " + str(teamdates)
#print teamdatestr
