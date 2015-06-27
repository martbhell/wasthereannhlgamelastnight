#!/usr/bin/python

# This requires BS4 (findAll vs find_all)

from BeautifulSoup import BeautifulSoup
import urllib2

url= 'http://www.nhl.com/ice/schedulebyseason.htm'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page.read())

data = []
data1 = []
lines = []
# Format2 test: { "Wed Jun 8, 2015" : [ "Tampa Bay", "Chicago" ] }
teamdates = {}
table = soup.find('table', attrs={'class':'data schedTbl'})
table_body = table.find('tbody')


# Just get dates and put them in a list:
rows = table_body.findAll('tr')
for row in rows:

### dates where there are games
    # http://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
    # This finds them, but the dates are listed twice each row so problem.
    cols = row.findAll('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

    # This finds one specific div in the row
    date = row.find("div", {"class": "skedStartDateSite"})
    date = [ele1.strip() for ele1 in date]
    data1.append([ele for ele in date if ele]) # Get rid of empty values

### teamdates
    # date and teams playing that date:  first a <div class=teamName"> <a ..>Detroit</a></div>
    # data2 = [u'Chicago', u'Tampa Bay']
    tivs = row.findAll("div", {"class": "teamName"})
    data2 = []
    for a in tivs:
        data2.append(a.find('a').contents[0])
    # first try to add append the list (of two teams) to the date (list and key) in teamdates dict
    try:
      teamdates[date[0]].append(data2)
    except:
    # If that date(list and key) does not exist, create it first
      teamdates[date[0]] = []
      teamdates[date[0]].append(data2)

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
# printing without unicode - for copy-pasting
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print linestr
teamdatestr = "teamdates = " + str(teamdates).encode('utf8').replace("u'","'")
print teamdatestr
