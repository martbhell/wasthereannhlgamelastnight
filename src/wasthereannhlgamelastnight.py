import os
import datetime

# grep "VISITING TEAM" -B 20 -m 1 NHL.2014-2015.Playoffs.txt
# today's and yesterday's date in the same format as in the schedule from NHL.
# dates looks like this: Sat Jun 6, 2015
now = datetime.datetime.now().strftime("%a %b %-d, %Y")
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.strftime("%a %b %-d, %Y")

#from subprocess import PIPE, Popen
#dates={}
#
#def cmdline(command):
#    process = Popen(
#        args=command,
#        stdout=PIPE,
#        shell=True
#    )
#    return process.communicate()[0]

#data = cmdline("grep 'VISITING TEAM' -B 20 -m 1 NHL.2014-2015.Playoffs.txt|grep 2015|grep -v PLAYOFF")

#lines = data.split('\n')

lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']

### What to print?

print 'Content-Type: text/html'
print ''
print '<!DOCTYPE html>\
        <html lang ="en">\
        <head><title>Was there an NHL game last night?</title></head>\
        <body style="text-align: center; padding-top: 200px;">\
            <div class="content" style="font-weight: bold; font-size: 220px; font-family: Arial,sans-serif; text-decoration: none; color: black;">'

for game in lines:
    if yesterday == game:
        print "YES"
        break
    else:
        print "NO"
        break

print '<div class="disclaimer" style="font-size:10px; ">All times are in UTC</div>'
print '<!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->'
print '</div></body></html>'
