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
    # http://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
    # This finds them, but the dates are listed twice each row so problem.
    cols = row.findAll('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

    # This finds one specific div in the row
    date = row.find("div", {"class": "skedStartDateSite"})
    date = [ele1.strip() for ele1 in date]
    data1.append([ele for ele in date if ele]) # Get rid of empty values

    # date and teams playing that date:  first a <div class=teamName"> <a ..>Detroit</a></div>
    tivs = row.findAll("div", {"class": "teamName"})
    data2 = []
    for a in tivs:
        data2.append(a.find('a').contents[0])
    teamdates[date[0]] = data2

print teamdates

# We want this in a list, like:
# lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']

for tr in data1:
    d8 = tr[0]
    d8.encode("UTF8")
    lines.append(d8)

# Using the list as it is:
print lines[0]
# printing without unicode - for copy-pasting
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print linestr
