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
# Thought experiment:
# Format1 test: { "CHI" : [ "Mon Jun 8, 2015", "Wed Jun 10, 2015" ], "TBL" : [ "Mon Jun 8, 2015", "Wed Jun 10, 2015" ] }
# Format2 test: { "Wed Jun 8, 2015" : [ "CHI", "TBL" ] }
teamdates = {}
table = soup.find('table', attrs={'class':'data schedTbl'})
table_body = table.find('tbody')

#print table_body

rows = table_body.findAll('tr')
for row in rows:
    # http://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
    # This finds them, but the dates are listed twice each row so problem.
    cols = row.findAll('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

    # This finds one specific div in the row
    divs = row.find("div", {"class": "skedStartDateSite"})
    divs = [ele1.strip() for ele1 in divs]
    data1.append([ele for ele in divs if ele]) # Get rid of empty values

# We want this in a list, like:
# lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']

for tr in data1:
    date = tr[0]
    date.encode("UTF8")
    lines.append(date)

# Using the list as it is:
print lines[0]
# printing without unicode - for copy-pasting
linestr = "lines = " + str(lines).encode('utf8').replace("u'","'")
print linestr
